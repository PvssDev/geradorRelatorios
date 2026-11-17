import React, { useMemo, useState, useEffect, useCallback } from "react";
import { createPortal } from "react-dom";
import {
  Image as ImageIcon,
  X,
  Images,
  CheckCircle2,
  FastForward,
  ChevronLeft,
  ChevronRight,
  ZoomIn,
} from "lucide-react";
import { useReportStore } from "../store/useReportStore";
import { MonitoramentoAnteriorItem } from "../types/report.types";
import { getConcessionTheme, isPerformanceModeActive } from "../utils/concessionTheme";
import { useLockBodyScroll } from "../hooks/useLockBodyScroll";
import { DarkGalleryModal } from "./modals/DarkGalleryModal";
import { VerticalMonitorCarousel } from "./VerticalMonitorCarousel";

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

  // Estados para animação fluida direcional
  const [direction, setDirection] = useState<"next" | "prev">("next");
  const [animKey, setAnimKey] = useState(0);

  // Estados para animação vertical no Monitoramento
  const [oldDirection, setOldDirection] = useState<"next" | "prev">("next");
  const [oldAnimKey, setOldAnimKey] = useState(0);
  const [newDirection, setNewDirection] = useState<"next" | "prev">("next");
  const [newAnimKey, setNewAnimKey] = useState(0);

  const fotos = ws.photos;
  const totalFotos = fotos.length;

  const fotoIdx = Math.max(
    0,
    Math.min(ws.carouselIndex, Math.max(0, totalFotos - 1))
  );

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

  // Navegação com Looping Infinito Circular (360°)
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
      if (targetIdx === fotoIdx || totalFotos <= 1) return;
      setDirection(targetIdx > fotoIdx ? "next" : "prev");
      setAnimKey((k) => k + 1);
      setCarouselIndex(targetIdx);
    },
    [fotoIdx, totalFotos, setCarouselIndex]
  );

  // Handlers para os carrosséis verticais do Monitoramento
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

  // Sincroniza foto nova inicial se nenhuma foi selecionada
  useEffect(() => {
    if (isMonitoring && totalFotos > 0 && !selectedNewPhotoName && onSelectNewPhotoName) {
      onSelectNewPhotoName(fotos[0].name);
    }
  }, [isMonitoring, totalFotos, selectedNewPhotoName, onSelectNewPhotoName, fotos]);

  // Navegação por teclado com suporte vertical no Monitoramento
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      const activeTag = (document.activeElement?.tagName || "").toLowerCase();
      if (activeTag === "input" || activeTag === "textarea" || activeTag === "select") {
        return;
      }
      if (isMonitoring && totalOld > 0) {
        if (e.key === "ArrowUp") {
          handleOldPrev();
        } else if (e.key === "ArrowDown") {
          handleOldNext();
        } else if (e.key === "ArrowLeft") {
          handleNewPrev();
        } else if (e.key === "ArrowRight") {
          handleNewNext();
        }
      } else {
        if (e.key === "ArrowLeft") {
          handlePrev();
        } else if (e.key === "ArrowRight") {
          handleNext();
        }
      }
    },
    [isMonitoring, totalOld, handlePrev, handleNext, handleOldPrev, handleOldNext, handleNewPrev, handleNewNext]
  );

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

  const currentPhoto = fotos[fotoIdx] || null;

  // Legenda automática calculada para a foto ativa
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

    // Verifica se esta foto já possui ocorrência cadastrada
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

    // Caso não vinculada ainda: prévia padrão automática da concessão
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

  // =========================================================================
  // MODO MONITORAMENTO: Dois Carrosséis Verticais 3D Lado a Lado (CoverFlow Vertical)
  // =========================================================================
  if (isMonitoring && ws.oldPhotosToMatch.length > 0) {
    const oldItem = ws.oldPhotosToMatch[oldIdx];
    const auditedStatus = oldItem ? auditedOldIds.get(oldItem.id_nc) : undefined;

    // Trio circular de ocorrências anteriores
    const prevOldIdx = totalOld > 1 ? (oldIdx - 1 + totalOld) % totalOld : null;
    const nextOldIdx = totalOld > 1 ? (oldIdx + 1) % totalOld : null;
    const prevOldItem = prevOldIdx !== null ? ws.oldPhotosToMatch[prevOldIdx] : null;
    const nextOldItem = nextOldIdx !== null ? ws.oldPhotosToMatch[nextOldIdx] : null;

    // Trio circular de fotos novas
    const currentNewPhoto = fotos[newIdx] || null;
    const prevNewIdx = totalFotos > 1 ? (newIdx - 1 + totalFotos) % totalFotos : null;
    const nextNewIdx = totalFotos > 1 ? (newIdx + 1) % totalFotos : null;
    const prevNewPhoto = prevNewIdx !== null ? fotos[prevNewIdx] : null;
    const nextNewPhoto = nextNewIdx !== null ? fotos[nextNewIdx] : null;

    const isCurrentNewInNc = currentNewPhoto
      ? fotosEmNc.has(currentNewPhoto.name.trim().toLowerCase())
      : false;

    const getOldImgSrc = (it: MonitoramentoAnteriorItem | null | undefined) => {
      if (!it?.old_photo_b64) return null;
      return it.old_photo_b64.startsWith("data:")
        ? it.old_photo_b64
        : `data:image/jpeg;base64,${it.old_photo_b64}`;
    };

    const oldSrc = getOldImgSrc(oldItem);
    const prevOldSrc = getOldImgSrc(prevOldItem);
    const nextOldSrc = getOldImgSrc(nextOldItem);

    return (
      <div className={`relative overflow-hidden border p-4 sm:p-6 ${isPerf ? "rounded-2xl bg-slate-900 border-slate-700 shadow-sm" : "rounded-3xl border-slate-700/50 bg-gradient-to-b from-[#0a1a2f] via-[#0d223c] to-[#081526] shadow-2xl "}`}>
        {/* Glow de iluminação no topo (Desativado no modo desempenho) */}
        {!isPerf && (
          <div
            className="pointer-events-none absolute -top-24 left-1/2 h-56 w-[550px] -translate-x-1/2 rounded-full blur-xl opacity-15 transition-all duration-300"
            style={{ backgroundColor: theme.primary }}
          />
        )}

        {/* Barra Superior Global */}
        <div className="relative z-10 mb-5 flex flex-wrap items-center justify-between gap-3 text-xs font-semibold uppercase tracking-wider text-slate-200">
          <div className="flex flex-wrap items-center gap-2">
            <span className="flex items-center gap-2 text-white">
              <span
                className="h-2 w-2 rounded-full animate-pulse"
                style={{ backgroundColor: theme.primary }}
              />
              Comparação Fotográfica · {oldItem?.display_label || oldItem?.id_nc}
            </span>
            {auditedStatus && (
              <span className="inline-flex items-center gap-1 rounded-full bg-ok px-2.5 py-0.5 text-[10px] font-bold normal-case text-white shadow-sm">
                <CheckCircle2 className="h-3 w-3" /> Auditada ({auditedStatus})
              </span>
            )}
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={() => setAutoAdvanceActive(!autoAdvanceActive)}
              className={`inline-flex items-center gap-1.5 rounded-xl px-3 py-1.5 text-[11px] font-semibold normal-case shadow-sm transition-all duration-200 ${
                autoAdvanceActive
                  ? "text-white ring-2 ring-white/30"
                  : "bg-white/10 text-slate-300 hover:bg-white/20 hover:text-white"
              }`}
              style={
                autoAdvanceActive
                  ? {
                      backgroundColor: theme.primary,
                      boxShadow: `0 0 15px ${theme.primary}40`,
                    }
                  : {}
              }
              title="Avançar para a próxima ocorrência automaticamente ao salvar"
            >
              <FastForward className="h-3 w-3" />
              Auto-avanço
            </button>
          </div>
        </div>

        {/* Grade de 2 Carrosséis Verticais Lado a Lado */}
        <div className="relative z-10 grid gap-6 md:grid-cols-2">
          {/* COLUNA 1: CARROSSEL VERTICAL DE FOTOS ANTERIORES */}
          <div className="flex flex-col">
            <VerticalMonitorCarousel
              title="Foto Anterior (Doc)"
              galleryLabel="Galeria anterior"
              galleryTitle="Abrir grade com todas as fotos do documento anterior"
              onOpenGallery={() => setShowAllOldModal(true)}
              total={totalOld}
              currentIndex={oldIdx}
              direction={oldDirection}
              animKey={oldAnimKey}
              prevItem={
                prevOldItem
                  ? {
                      id: `old_${prevOldIdx}`,
                      src: prevOldSrc,
                      alt: prevOldItem.id_nc,
                      label: prevOldItem.id_nc,
                      prevTitle: `Anterior: ${prevOldItem.id_nc}`,
                    }
                  : null
              }
              currentItem={
                oldItem
                  ? {
                      id: `old_${oldIdx}`,
                      src: oldSrc,
                      alt: oldItem.id_nc,
                      label: oldItem.id_nc || "Doc Anterior",
                    }
                  : null
              }
              nextItem={
                nextOldItem
                  ? {
                      id: `old_${nextOldIdx}`,
                      src: nextOldSrc,
                      alt: nextOldItem.id_nc,
                      label: nextOldItem.id_nc,
                      nextTitle: `Próximo: ${nextOldItem.id_nc}`,
                    }
                  : null
              }
              onPrev={handleOldPrev}
              onNext={handleOldNext}
              onZoom={(src) => setZoomUrl(src)}
              themePrimary={theme.primary}
              isPerf={isPerf}
              emptyText="Sem foto anterior"
              prevBtnAriaLabel="Ocorrência anterior (sobe)"
              prevBtnTitle="Foto anterior (para cima)"
              nextBtnAriaLabel="Próxima ocorrência (desce)"
              nextBtnTitle="Próxima foto (para baixo)"
              zoomTitle="Ampliar foto anterior"
              blockedReason={
                auditedStatus
                  ? `Ocorrência anterior já registrada (${auditedStatus})`
                  : null
              }
            />

            {/* Metadados: Legenda Antiga (Lado Esquerdo) */}
            {oldItem && (
              <div className="mt-4 flex flex-1 flex-col gap-1.5 rounded-2xl border border-white/10 bg-white/5 p-4 text-xs text-slate-300 shadow-sm">
                <span className="block text-[10px] font-bold uppercase tracking-wider text-slate-400" style={{ color: theme.primary }}>
                  Legenda Antiga
                </span>
                <p className="mt-0.5 text-xs italic leading-relaxed text-slate-200">
                  {oldItem.old_legend || "—"}
                </p>
              </div>
            )}
          </div>

          {/* COLUNA 2: CARROSSEL VERTICAL DE FOTOS NOVAS (CAMPO) */}
          <div className="flex flex-col">
            <VerticalMonitorCarousel
              title="Foto Nova (Vistoria)"
              galleryLabel="Galeria atual"
              galleryTitle="Abrir galeria de fotos de campo"
              onOpenGallery={totalFotos > 0 ? onOpenGalleryModal : undefined}
              total={totalFotos}
              currentIndex={newIdx}
              direction={newDirection}
              animKey={newAnimKey}
              prevItem={
                prevNewPhoto
                  ? {
                      id: `new_${prevNewIdx}`,
                      src: prevNewPhoto.previewUrl,
                      alt: prevNewPhoto.name,
                      label: prevNewPhoto.name,
                      prevTitle: `Foto anterior ${prevNewIdx! + 1}: ${prevNewPhoto.name}`,
                    }
                  : null
              }
              currentItem={
                currentNewPhoto
                  ? {
                      id: `new_${newIdx}`,
                      src: currentNewPhoto.previewUrl,
                      alt: currentNewPhoto.name,
                      label: currentNewPhoto.name,
                    }
                  : null
              }
              nextItem={
                nextNewPhoto
                  ? {
                      id: `new_${nextNewIdx}`,
                      src: nextNewPhoto.previewUrl,
                      alt: nextNewPhoto.name,
                      label: nextNewPhoto.name,
                      nextTitle: `Próxima foto ${nextNewIdx! + 1}: ${nextNewPhoto.name}`,
                    }
                  : null
              }
              onPrev={handleNewPrev}
              onNext={handleNewNext}
              onZoom={(src) => setZoomUrl(src)}
              themePrimary={theme.primary}
              isPerf={isPerf}
              emptyText="Envie fotos no bloco 1"
              prevBtnAriaLabel="Foto anterior (sobe)"
              prevBtnTitle="Foto nova anterior (para cima)"
              nextBtnAriaLabel="Próxima foto nova (desce)"
              nextBtnTitle="Próxima foto (para baixo)"
              zoomTitle="Ampliar foto nova"
              accentLabel
              blockedReason={
                isCurrentNewInNc
                  ? "Foto atual já vinculada a um registro"
                  : null
              }
            />

            {/* Metadados: Constatação Antiga (Lado Direito) */}
            {oldItem && (
              <div className="mt-4 flex flex-1 flex-col gap-1.5 rounded-2xl border border-white/10 bg-white/5 p-4 text-xs text-slate-300 shadow-sm">
                <span className="block text-[10px] font-bold uppercase tracking-wider text-slate-400" style={{ color: theme.primary }}>
                  Constatação Antiga
                </span>
                <p className="mt-0.5 text-xs leading-relaxed text-slate-200">
                  {oldItem.constatacao || "—"}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Modal de Todas as Fotos Anteriores */}
        {showAllOldModal && (
          <DarkGalleryModal
            title="Fotos do Relatório Anterior"
            totalCount={totalOld}
            searchPlaceholder="Pesquisar por código (ID), constatação ou situação (ex: Pendente, Saneada)..."
            emptyLabel="Nenhuma foto anterior encontrada"
            infoBanner={
              <>
                <strong>Como funciona o status:</strong> quando uma foto anterior
                já foi registrada na auditoria atual, ela exibe a situação
                escolhida — se registrada como{" "}
                <strong className="text-amber-300">Pendente</strong>, permanece
                marcada como pendente para acompanhamento. Fotos sem registro
                exibem{" "}
                <strong className="text-slate-200">Aguardando registro</strong>.
              </>
            }
            items={ws.oldPhotosToMatch.map((it, idx) => {
              const status = auditedOldIds.get(it.id_nc);
              const statusText = status
                ? `registrada ${status}`
                : "aguardando registro nao auditada";

              let topRightBadge = {
                label: "Aguardando registro",
                className:
                  "bg-slate-900/85 text-slate-300 border border-white/15",
              };
              if (status) {
                const norm = status.toLowerCase();
                if (norm.includes("parcial")) {
                  topRightBadge = {
                    label: `Registrada · ${status}`,
                    className: "bg-sky-600 text-white",
                  };
                } else if (norm.includes("pendente")) {
                  topRightBadge = {
                    label: "Registrada · Pendente",
                    className: "bg-amber-500 text-slate-950",
                  };
                } else {
                  topRightBadge = {
                    label: `✓ ${status}`,
                    className: "bg-ok text-white",
                  };
                }
              }

              return {
                key: `${it.id_nc}_${idx}`,
                imageUrl: getOldImgSrc(it),
                imageAlt: it.id_nc,
                title: it.id_nc,
                subtitle: it.constatacao || undefined,
                searchText: `${it.id_nc || ""} ${it.constatacao || ""} ${statusText}`,
                topRightBadge,
                isSelected: idx === oldIdx,
                onSelect: () => {
                  setCarouselIndex(idx);
                  setShowAllOldModal(false);
                },
              };
            })}
            onClose={() => setShowAllOldModal(false)}
          />
        )}

        {/* Modal de Zoom */}
        {zoomUrl &&
          createPortal(
            <div
              className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 p-4 animate-in fade-in"
              onClick={() => setZoomUrl(null)}
            >
            <div className="relative max-h-[90vh] max-w-4xl animate-in fade-in zoom-in-95 duration-200">
              <button
                type="button"
                aria-label="Fechar ampliação"
                onClick={() => setZoomUrl(null)}
                className="absolute -right-3 -top-3 rounded-full bg-white p-2 text-slate-900 shadow-xl hover:scale-110 active:scale-95 transition-all"
              >
                <X className="h-5 w-5" />
              </button>
              <img
                src={zoomUrl}
                alt="Zoom"
                className="max-h-[85vh] rounded-2xl object-contain shadow-2xl ring-1 ring-white/20"
              />
            </div>
          </div>,
          document.body
        )}
      </div>
    );
  }

  // =========================================================================
  // MODO FISCALIZAÇÃO (PADRÃO): CoverFlow 3D com Loop Infinito & Animação Fluida
  // =========================================================================

  // Cálculo Circular 360° para looping infinito
  const prevIdx = totalFotos > 1 ? (fotoIdx - 1 + totalFotos) % totalFotos : null;
  const nextIdx = totalFotos > 1 ? (fotoIdx + 1) % totalFotos : null;

  const prevPhoto = prevIdx !== null ? fotos[prevIdx] : null;
  const nextPhoto = nextIdx !== null ? fotos[nextIdx] : null;

  const currentInNc = currentPhoto
    ? fotosEmNc.has(currentPhoto.name.trim().toLowerCase())
    : false;

  // Janela visível de dots para manter a elegância
  const maxDots = 7;
  const startDot = Math.max(0, Math.min(fotoIdx - Math.floor(maxDots / 2), totalFotos - maxDots));
  const endDot = Math.min(totalFotos, startDot + maxDots);

  return (
    <div className={`relative overflow-hidden border p-4 sm:p-6 ${isPerf ? "rounded-2xl bg-slate-900 border-slate-700 shadow-sm" : "rounded-3xl border-slate-700/50 bg-gradient-to-b from-[#0a1a2f] via-[#0d223c] to-[#081526] shadow-2xl "}`}>

      {/* Estilos inline para animação fluida (Desativado no modo desempenho) */}
      {!isPerf && (
        <style>{`
          @keyframes carouselSlideRight {
          0% {
            opacity: 0.35;
            transform: translateX(45px) scale(0.94);
          }
          100% {
            opacity: 1;
            transform: translateX(0) scale(1);
          }
        }
        @keyframes carouselSlideLeft {
          0% {
            opacity: 0.35;
            transform: translateX(-45px) scale(0.94);
          }
          100% {
            opacity: 1;
            transform: translateX(0) scale(1);
          }
        }
        .anim-slide-next {
          animation: carouselSlideRight 400ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
        .anim-slide-prev {
          animation: carouselSlideLeft 400ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
      `}</style>
      )}

      {/* Iluminação ambiente no topo (Radial Glow - Desativado no modo desempenho) */}
      {!isPerf && (
        <div
          className="pointer-events-none absolute -top-24 left-1/2 h-56 w-[500px] -translate-x-1/2 rounded-full blur-xl opacity-15 transition-all duration-300"
          style={{ backgroundColor: theme.primary }}
        />
      )}

      {/* Barra Superior de Informações & Ações */}
      <div className="relative z-10 mb-5 flex flex-wrap items-center justify-between gap-3 text-xs font-semibold uppercase tracking-wider text-slate-200">
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-2 text-white">
            <span
              className="h-2 w-2 rounded-full animate-pulse"
              style={{ backgroundColor: theme.primary }}
            />
            Foto Selecionada
          </span>
          {currentPhoto && (
            <span className="rounded-md bg-white/10 px-2 py-0.5 font-mono text-[11px] font-normal normal-case text-slate-300">
              {currentPhoto.name}
            </span>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => setAutoAdvanceActive(!autoAdvanceActive)}
            className={`inline-flex items-center gap-1.5 rounded-xl px-3 py-1.5 text-[11px] font-semibold normal-case shadow-sm transition-all duration-200 ${
              autoAdvanceActive
                ? "text-white ring-2 ring-white/30"
                : "bg-white/10 text-slate-300 hover:bg-white/20 hover:text-white"
            }`}
            style={
              autoAdvanceActive
                ? {
                    backgroundColor: theme.primary,
                    boxShadow: `0 0 15px ${theme.primary}40`,
                  }
                : {}
            }
            title="Avançar para a próxima foto automaticamente ao registrar uma ocorrência"
          >
            <FastForward className="h-3 w-3" />
            Avanço automático
          </button>

          {totalFotos > 0 && onOpenGalleryModal && (
            <button
              type="button"
              onClick={onOpenGalleryModal}
              className="inline-flex items-center gap-1.5 rounded-xl bg-white/10 px-3 py-1.5 text-[11px] font-semibold normal-case text-slate-200 hover:bg-white/20 hover:text-white shadow-sm transition-all duration-200"
            >
              <Images className="h-3.5 w-3.5" />
              Ver todas as fotos
            </button>
          )}

          <span
            className="rounded-lg bg-white/10 px-2.5 py-1 font-mono text-[11px] font-bold"
            style={{ color: theme.primary }}
          >
            {totalFotos ? `${fotoIdx + 1} / ${totalFotos}` : "0 fotos"}
          </span>
        </div>
      </div>

      {/* Palco 3D CoverFlow (Layered Stacking com Looping Infinito) */}
      <div className="relative z-10 flex min-h-[290px] sm:min-h-[340px] items-center justify-center py-2 select-none">
        {/* Botão Flutuante Esquerdo (<) - Sempre ativo em Looping quando N > 1 */}
        <button
          type="button"
          disabled={totalFotos <= 1}
          onClick={handlePrev}
          aria-label="Foto anterior (looping)"
          className={`absolute left-2 sm:left-4 z-40 flex h-11 w-11 items-center justify-center rounded-xl border transition-all ${
            isPerf
              ? "border-slate-700 bg-slate-800 text-white hover:bg-slate-700 active:scale-95 disabled:opacity-20 disabled:pointer-events-none shadow-sm"
              : "rounded-full border-white/30 bg-white/90 text-slate-900 shadow-2xl hover:scale-110 active:scale-95 disabled:pointer-events-none disabled:opacity-20"
          }`}
        >
          <ChevronLeft className="h-6 w-6 stroke-[2.5]" />
        </button>

        {/* Trilho de Cards em Camadas 3D */}
        <div className="relative flex w-full max-w-2xl items-center justify-center">
          {totalFotos === 0 ? (
            /* Estado Vazio */
            <div className="flex h-64 w-full max-w-md flex-col items-center justify-center gap-3 rounded-3xl border-2 border-dashed border-white/20 bg-white/5 p-6 text-center text-slate-400">
              <ImageIcon className="h-12 w-12 text-white/30 stroke-1" />
              <div className="text-sm font-semibold text-slate-200">Nenhuma foto adicionada</div>
              <p className="text-xs text-slate-400">
                Faça o upload das fotos no bloco 1 para navegar e cadastrar achados.
              </p>
            </div>
          ) : (
            <div className="relative flex w-full items-center justify-center">
              {/* CARD ANTERIOR (Desativado no modo desempenho para corte de 70% de carga de renderização) */}
              {!isPerf && prevPhoto && (
                <div
                  key={`prev_${prevIdx}`}
                  onClick={handlePrev}
                  className="group absolute left-0 sm:left-4 z-10 w-[62%] sm:w-[58%] cursor-pointer overflow-hidden rounded-3xl border-2 border-white/20 bg-slate-900 shadow-xl transition-all duration-500 ease-out hover:opacity-85 -translate-x-4 sm:-translate-x-8 scale-[0.84] opacity-55"
                  style={{
                    aspectRatio: "4 / 3",
                  }}
                  title={`Foto anterior ${prevIdx! + 1}: ${prevPhoto.name}`}
                >
                  <img
                    src={prevPhoto.previewUrl}
                    alt={prevPhoto.name}
                    className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                  />
                  <div className="absolute inset-0 bg-black/40 transition-colors group-hover:bg-black/20" />
                  <span className="absolute bottom-3 left-3 rounded-lg bg-black/70 px-2 py-0.5 text-[10px] font-semibold text-white">
                    Foto #{String(prevIdx! + 1).padStart(2, "0")}
                  </span>
                </div>
              )}

              {/* CARD ATIVO (CENTRAL - DESTAQUE 3D COM ANIMAÇÃO FLUIDA DIREÇÃO NEXT/PREV) */}
              {currentPhoto && (
                <div
                  key={`curr_${fotoIdx}_${animKey}`}
                  className={`group relative z-30 w-[78%] sm:w-[72%] overflow-hidden border-2 ${isPerf ? "rounded-2xl bg-slate-950 shadow-md" : `rounded-3xl bg-slate-900 ${direction === "next" ? "anim-slide-next" : "anim-slide-prev"}`}`}
                  style={{
                    aspectRatio: "4 / 3",
                    borderColor: theme.primary,
                    boxShadow: isPerf ? undefined : "0 20px 50px rgba(0,0,0,0.6)",
                  }}
                >
                  <img
                    src={currentPhoto.previewUrl}
                    alt={currentPhoto.name}
                    className={`h-full w-full object-cover cursor-pointer ${isPerf ? "" : "transition-transform duration-500 group-hover:scale-105"}`}
                    onClick={() => setZoomUrl(currentPhoto.previewUrl)}
                  />

                  {/* Degradê superior para contraste de badges */}
                  <div className="pointer-events-none absolute inset-x-0 top-0 h-16 bg-gradient-to-b from-black/60 to-transparent" />

                  {/* Badge de Status "Em NC" */}
                  {currentInNc && (
                    <span className="absolute right-3.5 top-3.5 inline-flex items-center gap-1.5 rounded-full bg-ok px-3 py-1 text-[11px] font-bold text-white shadow-lg animate-in fade-in duration-300">
                      <CheckCircle2 className="h-3.5 w-3.5" /> Em NC
                    </span>
                  )}

                  {/* Botão de Zoom no canto superior */}
                  <button
                    type="button"
                    onClick={() => setZoomUrl(currentPhoto.previewUrl)}
                    aria-label="Ampliar foto"
                    className="absolute left-3.5 top-3.5 rounded-full bg-black/60 p-2 text-white shadow-lg hover:scale-110 active:scale-95 transition-all"
                  >
                    <ZoomIn className="h-4 w-4" />
                  </button>

                  {/* Barra de Informações da Foto Ativa no Rodapé */}
                  <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/85 via-black/50 to-transparent p-3.5 pt-7 text-left text-white">
                    <div className="flex items-center justify-between gap-2">
                      <span
                        className="rounded-lg px-2.5 py-0.5 font-mono text-[11px] font-bold text-white shadow"
                        style={{ backgroundColor: theme.primary }}
                      >
                        Foto {String(fotoIdx + 1).padStart(2, "0")}
                      </span>
                      <span className="truncate font-mono text-xs text-slate-200">
                        {currentPhoto.name}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* CARD POSTERIOR (Desativado no modo desempenho) */}
              {!isPerf && nextPhoto && (
                <div
                  key={`next_${nextIdx}`}
                  onClick={handleNext}
                  className="group absolute right-0 sm:right-4 z-10 w-[62%] sm:w-[58%] cursor-pointer overflow-hidden rounded-3xl border-2 border-white/20 bg-slate-900 shadow-xl transition-all duration-500 ease-out hover:opacity-85 translate-x-4 sm:translate-x-8 scale-[0.84] opacity-55"
                  style={{
                    aspectRatio: "4 / 3",
                  }}
                  title={`Próxima foto ${nextIdx! + 1}: ${nextPhoto.name}`}
                >
                  <img
                    src={nextPhoto.previewUrl}
                    alt={nextPhoto.name}
                    className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                  />
                  <div className="absolute inset-0 bg-black/40 transition-colors group-hover:bg-black/20" />
                  <span className="absolute bottom-3 right-3 rounded-lg bg-black/70 px-2 py-0.5 text-[10px] font-semibold text-white">
                    Foto #{String(nextIdx! + 1).padStart(2, "0")}
                  </span>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Botão Flutuante Direito (>) - Sempre ativo em Looping quando N > 1 */}
        <button
          type="button"
          disabled={totalFotos <= 1}
          onClick={handleNext}
          aria-label="Próxima foto (looping)"
          className={`absolute right-2 sm:right-4 z-40 flex h-11 w-11 items-center justify-center rounded-xl border transition-all ${
            isPerf
              ? "border-slate-700 bg-slate-800 text-white hover:bg-slate-700 active:scale-95 disabled:opacity-20 disabled:pointer-events-none shadow-sm"
              : "rounded-full border-white/30 bg-white/90 text-slate-900 shadow-2xl hover:scale-110 active:scale-95 disabled:pointer-events-none disabled:opacity-20"
          }`}
        >
          <ChevronRight className="h-6 w-6 stroke-[2.5]" />
        </button>
      </div>

      {/* Paginação por Dots (Bullets) Interativos com Looping */}
      {totalFotos > 1 && (
        <div className="relative z-10 mt-4 flex items-center justify-center gap-2">
          {Array.from({ length: endDot - startDot }).map((_, i) => {
            const idxReal = startDot + i;
            const isAct = idxReal === fotoIdx;
            const isInNcDot = fotos[idxReal]
              ? fotosEmNc.has(fotos[idxReal].name.trim().toLowerCase())
              : false;

            return (
              <button
                key={idxReal}
                type="button"
                onClick={() => handleGoTo(idxReal)}
                aria-label={`Ir para foto ${idxReal + 1}`}
                className={`transition-all duration-300 focus:outline-none ${
                  isAct
                    ? "h-2.5 w-7 rounded-full shadow-md"
                    : isInNcDot
                    ? "h-2.5 w-2.5 rounded-full bg-ok/80 hover:bg-ok"
                    : "h-2.5 w-2.5 rounded-full bg-white/30 hover:bg-white/60"
                }`}
                style={
                  isAct
                    ? {
                        backgroundColor: theme.primary,
                        boxShadow: `0 0 12px ${theme.primary}80`,
                      }
                    : {}
                }
                title={`Foto ${idxReal + 1}${isInNcDot ? " (Em NC)" : ""}`}
              />
            );
          })}
        </div>
      )}

      {/* Prévia Automática da Legenda do Memorial Fotográfico (.docx) */}
      {currentPhoto && activeLegenda && (
        <div className={`relative z-10 mt-4 mx-auto w-full max-w-xl rounded-2xl border px-4 py-2.5 text-center shadow-sm ${isPerf ? "bg-slate-950 border-slate-800" : "border-white/10 bg-black/45 shadow-lg transition-all duration-300"}`}>
          <div className="flex items-center justify-center gap-2 text-[10px] font-bold uppercase tracking-wider text-slate-300">
            <span
              className="inline-block h-1.5 w-1.5 rounded-full animate-pulse"
              style={{ backgroundColor: theme.primary }}
            />
            Prévia da Legenda no Relatório (.docx)
          </div>
          <p className="mt-1 font-sans text-xs italic text-slate-100 leading-relaxed">
            {activeLegenda}
          </p>
        </div>
      )}

      {/* Modal de Zoom */}
      {zoomUrl &&
        createPortal(
          <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 p-4 animate-in fade-in"
            onClick={() => setZoomUrl(null)}
          >
            <div className="relative max-h-[90vh] max-w-4xl animate-in fade-in zoom-in-95 duration-200">
              <button
                type="button"
                aria-label="Fechar ampliação"
                onClick={() => setZoomUrl(null)}
                className="absolute -right-3 -top-3 rounded-full bg-white p-2 text-slate-900 shadow-xl hover:scale-110 active:scale-95 transition-all"
              >
                <X className="h-5 w-5" />
              </button>
              <img
                src={zoomUrl}
                alt="Zoom"
                className="max-h-[85vh] rounded-2xl object-contain shadow-2xl ring-1 ring-white/20"
              />
            </div>
          </div>,
          document.body
        )}
    </div>
  );
};
