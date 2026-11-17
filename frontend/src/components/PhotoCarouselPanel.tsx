import React, { useMemo, useState, useEffect, useCallback } from "react";
import { useReportStore } from "../store/useReportStore";
import { getConcessionTheme, isPerformanceModeActive } from "../utils/concessionTheme";
import { useLockBodyScroll } from "../hooks/useLockBodyScroll";
import { MonitoringDualCarousel } from "./carousel/MonitoringDualCarousel";
import { FiscalizacaoHorizontalCarousel } from "./carousel/FiscalizacaoHorizontalCarousel";

interface PhotoCarouselPanelProps {
  selectedNewPhotoName?: string;
  onSelectNewPhotoName?: (name: string) => void;
  onOpenGalleryModal?: () => void;
}

export const PhotoCarouselPanel: React.FC<PhotoCarouselPanelProps> = ({
  selectedNewPhotoName,
  onSelectNewPhotoName,
  onOpenGalleryModal,
}) => {
  const {
    tipoRelatorio,
    categoriaRelatorio,
    autoAdvanceActive,
    setAutoAdvanceActive,
    getActiveWorkspace,
    setCarouselIndex,
  } = useReportStore();

  const ws = getActiveWorkspace();
  const theme = getConcessionTheme(tipoRelatorio, categoriaRelatorio);
  const isPerf = isPerformanceModeActive();
  const isMonitoring = categoriaRelatorio === "Monitoramento";
  const [zoomUrl, setZoomUrl] = useState<string | null>(null);
  const [showAllOldModal, setShowAllOldModal] = useState(false);
  useLockBodyScroll(showAllOldModal || !!zoomUrl);

  const [direction, setDirection] = useState<"next" | "prev">("next");
  const [animKey, setAnimKey] = useState(0);
  const [oldDirection, setOldDirection] = useState<"next" | "prev">("next");
  const [oldAnimKey, setOldAnimKey] = useState(0);
  const [newDirection, setNewDirection] = useState<"next" | "prev">("next");
  const [newAnimKey, setNewAnimKey] = useState(0);

  const fotos = ws.photos;
  const totalFotos = fotos.length;
  const fotoIdx = Math.max(0, Math.min(ws.carouselIndex, Math.max(0, totalFotos - 1)));

  const fotosEmNc = useMemo(() => {
    const set = new Set<string>();
    ws.registrosNc.forEach((nc) => {
      if (nc.Foto) set.add(nc.Foto.trim().toLowerCase());
    });
    return set;
  }, [ws.registrosNc]);

  const auditedOldIds = useMemo(() => {
    const map = new Map<string, string>();
    ws.registrosNc.forEach((nc) => {
      if (!nc.is_relacionado && nc.Identificação) {
        map.set(nc.Identificação.trim(), nc.Situação || "Pendente");
      }
    });
    return map;
  }, [ws.registrosNc]);

  const handlePrev = useCallback(() => {
    if (totalFotos <= 1) return;
    setDirection("prev");
    setAnimKey((k) => k + 1);
    setCarouselIndex((fotoIdx - 1 + totalFotos) % totalFotos);
  }, [fotoIdx, totalFotos, setCarouselIndex]);

  const handleNext = useCallback(() => {
    if (totalFotos <= 1) return;
    setDirection("next");
    setAnimKey((k) => k + 1);
    setCarouselIndex((fotoIdx + 1) % totalFotos);
  }, [fotoIdx, totalFotos, setCarouselIndex]);

  const handleGoTo = useCallback(
    (targetIdx: number) => {
      if (targetIdx === fotoIdx) return;
      setDirection(targetIdx > fotoIdx ? "next" : "prev");
      setAnimKey((k) => k + 1);
      setCarouselIndex(targetIdx);
    },
    [fotoIdx, setCarouselIndex]
  );

  const totalOld = ws.oldPhotosToMatch.length;
  const oldIdx = Math.max(0, Math.min(ws.carouselIndex, Math.max(0, totalOld - 1)));

  const handleOldPrev = useCallback(() => {
    if (totalOld <= 1) return;
    setOldDirection("prev");
    setOldAnimKey((k) => k + 1);
    setCarouselIndex((oldIdx - 1 + totalOld) % totalOld);
  }, [oldIdx, totalOld, setCarouselIndex]);

  const handleOldNext = useCallback(() => {
    if (totalOld <= 1) return;
    setOldDirection("next");
    setOldAnimKey((k) => k + 1);
    setCarouselIndex((oldIdx + 1) % totalOld);
  }, [oldIdx, totalOld, setCarouselIndex]);

  const selectedNewIdx = fotos.findIndex((p) => p.name === selectedNewPhotoName);
  const newIdx = selectedNewIdx >= 0 ? selectedNewIdx : 0;

  const handleNewPrev = useCallback(() => {
    if (totalFotos <= 1) return;
    setNewDirection("prev");
    setNewAnimKey((k) => k + 1);
    const target = fotos[(newIdx - 1 + totalFotos) % totalFotos];
    if (target && onSelectNewPhotoName) {
      onSelectNewPhotoName(target.name);
    }
  }, [newIdx, totalFotos, fotos, onSelectNewPhotoName]);

  const handleNewNext = useCallback(() => {
    if (totalFotos <= 1) return;
    setNewDirection("next");
    setNewAnimKey((k) => k + 1);
    const target = fotos[(newIdx + 1) % totalFotos];
    if (target && onSelectNewPhotoName) {
      onSelectNewPhotoName(target.name);
    }
  }, [newIdx, totalFotos, fotos, onSelectNewPhotoName]);

  useEffect(() => {
    if (isMonitoring && totalFotos > 0 && !selectedNewPhotoName && onSelectNewPhotoName) {
      onSelectNewPhotoName(fotos[0].name);
    }
  }, [isMonitoring, totalFotos, selectedNewPhotoName, onSelectNewPhotoName, fotos]);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      const activeTag = (document.activeElement?.tagName || "").toLowerCase();
      if (activeTag === "input" || activeTag === "textarea" || activeTag === "select") {
        return;
      }
      if (isMonitoring && totalOld > 0) {
        if (e.key === "ArrowUp") handleOldPrev();
        else if (e.key === "ArrowDown") handleOldNext();
        else if (e.key === "ArrowLeft") handleNewPrev();
        else if (e.key === "ArrowRight") handleNewNext();
      } else {
        if (e.key === "ArrowLeft") handlePrev();
        else if (e.key === "ArrowRight") handleNext();
      }
    },
    [
      isMonitoring,
      totalOld,
      handlePrev,
      handleNext,
      handleOldPrev,
      handleOldNext,
      handleNewPrev,
      handleNewNext,
    ]
  );

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

  const currentPhoto = fotos[fotoIdx] || null;

  const activeLegenda = useMemo(() => {
    if (!currentPhoto) return "";
    const numFoto = String(fotoIdx + 1).padStart(2, "0");
    const dataFisc = ws.fiscalizacoes?.[0]?.Data || "";
    const dataBr = dataFisc
      ? (() => {
          const parts = dataFisc.split("-");
          return parts.length === 3
            ? `${parts[2]}/${parts[1]}/${parts[0]}`
            : dataFisc;
        })()
      : new Date().toLocaleDateString("pt-BR");

    const existingNc = ws.registrosNc?.find(
      (nc) =>
        nc.Foto?.trim().toLowerCase() === currentPhoto.name.trim().toLowerCase()
    );

    if (existingNc) {
      if (existingNc.Observações?.trim()) {
        const obs = existingNc.Observações.trim();
        if (
          obs.toLowerCase().startsWith("foto ") ||
          obs.toLowerCase().startsWith("foto\xa0")
        ) {
          return obs;
        }
        if (
          tipoRelatorio === "CRA" &&
          (existingNc.Trecho || ws.trechoPersistido)
        ) {
          const trechoVal = existingNc.Trecho || ws.trechoPersistido;
          return `Foto ${numFoto} – Trecho ${trechoVal} apresentando ${obs}, em ${dataBr}.`;
        }
        return `Foto ${numFoto} – ${obs}, em ${dataBr}.`;
      }
      const desc =
        existingNc["Não Conformidade"] ||
        existingNc["Ponto de Atenção"] ||
        existingNc.Identificação ||
        "irregularidade constatada";
      return `Foto ${numFoto} – ${desc}, em ${dataBr}.`;
    }

    if (tipoRelatorio === "CRA" && ws.trechoPersistido?.trim()) {
      return `Foto ${numFoto} – Trecho ${ws.trechoPersistido.trim()} apresentando irregularidades em campo, em ${dataBr}.`;
    }
    if (tipoRelatorio === "CRC" && ws.trechoPersistido?.trim()) {
      return `Foto ${numFoto} – Trecho ${ws.trechoPersistido.trim()}, em ${dataBr}.`;
    }
    if (tipoRelatorio === "SOCICAM") {
      const local = ws.fiscalizacoes?.[0]?.Local || "Terminal Rodoviário";
      return `Foto ${numFoto} – Constatação no ${local}, em ${dataBr}.`;
    }
    return `Foto ${numFoto} – Registro de vistoria em campo, em ${dataBr}.`;
  }, [
    currentPhoto,
    fotoIdx,
    ws.fiscalizacoes,
    ws.registrosNc,
    ws.trechoPersistido,
    tipoRelatorio,
  ]);

  if (isMonitoring && ws.oldPhotosToMatch.length > 0) {
    return (
      <MonitoringDualCarousel
        oldItems={ws.oldPhotosToMatch}
        oldIdx={oldIdx}
        oldDirection={oldDirection}
        oldAnimKey={oldAnimKey}
        auditedOldIds={auditedOldIds}
        onOldPrev={handleOldPrev}
        onOldNext={handleOldNext}
        onSelectOldIdx={setCarouselIndex}
        fotos={fotos}
        newIdx={newIdx}
        newDirection={newDirection}
        newAnimKey={newAnimKey}
        fotosEmNc={fotosEmNc}
        onNewPrev={handleNewPrev}
        onNewNext={handleNewNext}
        onOpenGalleryModal={onOpenGalleryModal}
        autoAdvanceActive={autoAdvanceActive}
        onToggleAutoAdvance={() => setAutoAdvanceActive(!autoAdvanceActive)}
        showAllOldModal={showAllOldModal}
        onOpenAllOldModal={() => setShowAllOldModal(true)}
        onCloseAllOldModal={() => setShowAllOldModal(false)}
        zoomUrl={zoomUrl}
        onZoom={setZoomUrl}
        themePrimary={theme.primary}
        isPerf={isPerf}
      />
    );
  }

  return (
    <FiscalizacaoHorizontalCarousel
      fotos={fotos}
      fotoIdx={fotoIdx}
      direction={direction}
      animKey={animKey}
      fotosEmNc={fotosEmNc}
      activeLegenda={activeLegenda}
      autoAdvanceActive={autoAdvanceActive}
      onToggleAutoAdvance={() => setAutoAdvanceActive(!autoAdvanceActive)}
      onPrev={handlePrev}
      onNext={handleNext}
      onGoTo={handleGoTo}
      onOpenGalleryModal={onOpenGalleryModal}
      zoomUrl={zoomUrl}
      onZoom={setZoomUrl}
      themePrimary={theme.primary}
      isPerf={isPerf}
    />
  );
};
