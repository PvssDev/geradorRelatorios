import React, { useMemo, useState, useEffect, useCallback } from "react";
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
import { getConcessionTheme } from "../utils/concessionTheme";

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
  const isMonitoring = categoriaRelatorio === "Monitoramento";
  const [zoomUrl, setZoomUrl] = useState<string | null>(null);
  const [onlyPendingOld, setOnlyPendingOld] = useState(false);

  // Estados para animação fluida direcional
  const [direction, setDirection] = useState<"next" | "prev">("next");
  const [animKey, setAnimKey] = useState(0);

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

  // Navegação por teclado (Seta Esquerda / Seta Direita com Looping)
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      const activeTag = (document.activeElement?.tagName || "").toLowerCase();
      if (activeTag === "input" || activeTag === "textarea" || activeTag === "select") {
        return;
      }
      if (e.key === "ArrowLeft") {
        handlePrev();
      } else if (e.key === "ArrowRight") {
        handleNext();
      }
    },
    [handlePrev, handleNext]
  );

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

  // =========================================================================
  // MODO MONITORAMENTO: Comparador Anterior x Atual
  // =========================================================================
  if (isMonitoring && ws.oldPhotosToMatch.length > 0) {
    const totalOld = ws.oldPhotosToMatch.length;
    const filteredIndices = ws.oldPhotosToMatch
      .map((it, idx) => ({ it, idx }))
      .filter(({ it }) => !onlyPendingOld || !auditedOldIds.has(it.id_nc));

    const oldIdx = Math.max(0, Math.min(ws.carouselIndex, totalOld - 1));
    const oldItem = ws.oldPhotosToMatch[oldIdx];
    const auditedStatus = oldItem ? auditedOldIds.get(oldItem.id_nc) : undefined;
    const pendingCount = ws.oldPhotosToMatch.filter(
      (it) => !auditedOldIds.has(it.id_nc)
    ).length;

    const matchedNew =
      fotos.find((p) => p.name === selectedNewPhotoName) ||
      fotos[Math.min(oldIdx, Math.max(0, fotos.length - 1))] ||
      null;

    const oldSrc = oldItem?.old_photo_b64
      ? oldItem.old_photo_b64.startsWith("data:")
        ? oldItem.old_photo_b64
        : `data:image/jpeg;base64,${oldItem.old_photo_b64}`
      : null;

    const posInFiltered = filteredIndices.findIndex((x) => x.idx === oldIdx);

    const handleOldPrev = () => {
      if (onlyPendingOld && filteredIndices.length > 0) {
        const nextPos = (posInFiltered - 1 + filteredIndices.length) % filteredIndices.length;
        setCarouselIndex(filteredIndices[nextPos].idx);
      } else if (totalOld > 1) {
        setCarouselIndex((oldIdx - 1 + totalOld) % totalOld);
      }
    };

    const handleOldNext = () => {
      if (onlyPendingOld && filteredIndices.length > 0) {
        const nextPos = (posInFiltered + 1) % filteredIndices.length;
        setCarouselIndex(filteredIndices[nextPos].idx);
      } else if (totalOld > 1) {
        setCarouselIndex((oldIdx + 1) % totalOld);
      }
    };

    return (
      <div className="relative overflow-hidden rounded-3xl border border-slate-700/50 bg-gradient-to-b from-[#0a1a2f] via-[#0d223c] to-[#081526] p-5 sm:p-6 shadow-2xl backdrop-blur-xl">
        {/* Glow sutil no topo */}
        <div
          className="pointer-events-none absolute -top-24 left-1/2 h-48 w-96 -translate-x-1/2 rounded-full blur-3xl opacity-20 transition-all duration-300"
          style={{ backgroundColor: theme.primary }}
        />

        <div className="relative z-10 mb-4 flex flex-wrap items-center justify-between gap-3 text-xs font-semibold uppercase tracking-wider text-slate-200">
          <div className="flex flex-wrap items-center gap-2">
            <span className="flex items-center gap-1.5 text-white">
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
              onClick={() => {
                const nextVal = !onlyPendingOld;
                setOnlyPendingOld(nextVal);
                if (nextVal) {
                  const firstPend = ws.oldPhotosToMatch.findIndex(
                    (it) => !auditedOldIds.has(it.id_nc)
                  );
                  if (firstPend >= 0) setCarouselIndex(firstPend);
                }
              }}
              className={`rounded-xl px-3 py-1.5 text-[11px] font-semibold normal-case shadow-sm transition-all duration-200 ${
                onlyPendingOld
                  ? "bg-primary text-white ring-2 ring-primary/30"
                  : "bg-white/10 text-slate-300 hover:bg-white/20 hover:text-white"
              }`}
              style={onlyPendingOld ? { backgroundColor: theme.primary } : {}}
            >
              {onlyPendingOld
                ? `Apenas não auditadas (${pendingCount})`
                : `Filtrar não auditadas (${pendingCount}/${totalOld})`}
            </button>

            <button
              type="button"
              onClick={() => setAutoAdvanceActive(!autoAdvanceActive)}
              className={`inline-flex items-center gap-1.5 rounded-xl px-3 py-1.5 text-[11px] font-semibold normal-case shadow-sm transition-all duration-200 ${
                autoAdvanceActive
                  ? "text-white ring-2 ring-white/30"
                  : "bg-white/10 text-slate-300 hover:bg-white/20 hover:text-white"
              }`}
              style={autoAdvanceActive ? { backgroundColor: theme.primary } : {}}
              title="Avançar automaticamente para a próxima ocorrência após salvar"
            >
              <FastForward className="h-3 w-3" />
              Auto-avanço
            </button>

            {fotos.length > 0 && onOpenGalleryModal && (
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
              {oldIdx + 1} / {totalOld}
            </span>
          </div>
        </div>

        {/* Contexto Extraído do Relatório Anterior */}
        {oldItem && (
          <div className="relative z-10 mb-4 grid gap-2.5 rounded-2xl border border-white/10 bg-white/5 p-3.5 text-xs text-slate-300 backdrop-blur-md sm:grid-cols-2">
            <div>
              <span className="font-semibold" style={{ color: theme.primary }}>
                Identificação:
              </span>{" "}
              <span className="font-mono text-white">{oldItem.id_nc || "—"}</span>
              {tipoRelatorio !== "SOCICAM" &&
                (oldItem.pista || oldItem.trecho) && (
                  <span className="ml-2 text-slate-400">
                    · {[oldItem.pista, oldItem.trecho].filter(Boolean).join(" / ")}
                  </span>
                )}
            </div>
            {oldItem.old_legend && (
              <div className="truncate text-slate-300" title={oldItem.old_legend}>
                <span className="font-semibold" style={{ color: theme.primary }}>
                  Legenda Ant.:
                </span>{" "}
                {oldItem.old_legend}
              </div>
            )}
            {oldItem.constatacao && (
              <div className="sm:col-span-2 text-slate-300/90">
                <span className="font-semibold" style={{ color: theme.primary }}>
                  Constatação Anterior:
                </span>{" "}
                {oldItem.constatacao}
              </div>
            )}
          </div>
        )}

        {/* Barra de Seleção e Navegação com Looping */}
        <div className="relative z-10 mb-4 flex items-center gap-2">
          <button
            type="button"
            disabled={totalOld <= 1}
            onClick={handleOldPrev}
            className="flex items-center gap-1 rounded-xl bg-white/10 px-3.5 py-2 text-xs font-semibold text-white disabled:opacity-30 hover:bg-white/20 transition-all duration-200"
          >
            <ChevronLeft className="h-4 w-4" /> Anterior
          </button>
          <select
            value={oldIdx}
            onChange={(e) => setCarouselIndex(Number(e.target.value))}
            className="flex-1 rounded-xl border border-white/15 bg-white/10 px-3 py-2 text-xs font-medium text-white outline-none focus:border-primary"
          >
            {(onlyPendingOld && filteredIndices.length > 0
              ? filteredIndices
              : ws.oldPhotosToMatch.map((it, idx) => ({ it, idx }))
            ).map(({ it, idx }) => (
              <option key={`${it.id_nc}_${idx}`} value={idx} className="bg-slate-900 text-white">
                {auditedOldIds.has(it.id_nc) ? "✓ " : ""}
                {it.display_label || it.id_nc}
              </option>
            ))}
          </select>
          <button
            type="button"
            disabled={totalOld <= 1}
            onClick={handleOldNext}
            className="flex items-center gap-1 rounded-xl bg-white/10 px-3.5 py-2 text-xs font-semibold text-white disabled:opacity-30 hover:bg-white/20 transition-all duration-200"
          >
            Posterior <ChevronRight className="h-4 w-4" />
          </button>
        </div>

        {/* Lado a Lado: Anterior x Atual */}
        <div className="relative z-10 grid gap-4 sm:grid-cols-2">
          <button
            type="button"
            disabled={!oldSrc}
            onClick={() => oldSrc && setZoomUrl(oldSrc)}
            className="group relative grid aspect-[4/3] place-items-center overflow-hidden rounded-2xl border-2 border-white/15 bg-slate-900/60 shadow-lg transition-transform duration-200 hover:scale-[1.01]"
          >
            {oldSrc ? (
              <img
                src={oldSrc}
                alt="Foto Anterior"
                className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
              />
            ) : (
              <ImageIcon className="h-10 w-10 text-white/30" />
            )}
            <span className="absolute bottom-3 left-3 rounded-lg bg-black/70 px-2.5 py-1 text-xs font-semibold text-white backdrop-blur-md">
              Foto Anterior (Doc)
            </span>
            {oldSrc && (
              <span className="absolute right-3 top-3 rounded-full bg-black/60 p-1.5 text-white/80 opacity-0 group-hover:opacity-100 transition-opacity">
                <ZoomIn className="h-4 w-4" />
              </span>
            )}
          </button>

          <div className="space-y-2">
            <button
              type="button"
              disabled={!matchedNew}
              onClick={() => matchedNew && setZoomUrl(matchedNew.previewUrl)}
              className="group relative grid w-full aspect-[4/3] place-items-center overflow-hidden rounded-2xl border-2 bg-slate-900/60 shadow-lg transition-transform duration-200 hover:scale-[1.01]"
              style={{
                borderColor: theme.primary,
                boxShadow: `0 0 20px ${theme.primary}40`,
              }}
            >
              {matchedNew ? (
                <img
                  src={matchedNew.previewUrl}
                  alt={matchedNew.name}
                  className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
                />
              ) : (
                <ImageIcon className="h-10 w-10 text-white/30" />
              )}
              <span
                className="absolute bottom-3 left-3 rounded-lg px-2.5 py-1 text-xs font-semibold text-white backdrop-blur-md"
                style={{ backgroundColor: theme.primary }}
              >
                {matchedNew ? matchedNew.name : "Envie fotos no bloco 1"}
              </span>
              {matchedNew && (
                <span className="absolute right-3 top-3 rounded-full bg-black/60 p-1.5 text-white/80 opacity-0 group-hover:opacity-100 transition-opacity">
                  <ZoomIn className="h-4 w-4" />
                </span>
              )}
            </button>
            {fotos.length > 0 && onSelectNewPhotoName && (
              <select
                value={matchedNew?.name || ""}
                onChange={(e) => onSelectNewPhotoName(e.target.value)}
                className="w-full rounded-xl border border-white/15 bg-white/10 px-3 py-2 text-xs font-medium text-white outline-none focus:border-accent"
              >
                {fotos.map((f, idx) => (
                  <option key={f.id} value={f.name} className="bg-slate-900 text-white">
                    {fotosEmNc.has(f.name.trim().toLowerCase()) ? "✓ " : ""}
                    Foto {String(idx + 1).padStart(2, "0")} — {f.name}
                  </option>
                ))}
              </select>
            )}
          </div>
        </div>

        {/* Modal de Zoom */}
        {zoomUrl && (
          <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 p-4 backdrop-blur-sm"
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
          </div>
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

  const currentPhoto = fotos[fotoIdx] || null;
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
    <div className="relative overflow-hidden rounded-3xl border border-slate-700/50 bg-gradient-to-b from-[#0a1a2f] via-[#0d223c] to-[#081526] p-5 sm:p-7 shadow-2xl backdrop-blur-xl">
      {/* Estilos inline para animação fluida física com aceleração elástica */}
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

      {/* Iluminação ambiente no topo (Radial Glow) */}
      <div
        className="pointer-events-none absolute -top-24 left-1/2 h-56 w-[500px] -translate-x-1/2 rounded-full blur-3xl opacity-20 transition-all duration-300"
        style={{ backgroundColor: theme.primary }}
      />

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
          className="absolute left-2 sm:left-4 z-40 flex h-11 w-11 items-center justify-center rounded-full border border-white/30 bg-white/90 text-slate-900 shadow-2xl backdrop-blur-md transition-all duration-300 hover:scale-110 active:scale-95 disabled:pointer-events-none disabled:opacity-20"
        >
          <ChevronLeft className="h-6 w-6 stroke-[2.5]" />
        </button>

        {/* Trilho de Cards em Camadas 3D */}
        <div className="relative flex w-full max-w-2xl items-center justify-center">
          {totalFotos === 0 ? (
            /* Estado Vazio */
            <div className="flex h-64 w-full max-w-md flex-col items-center justify-center gap-3 rounded-3xl border-2 border-dashed border-white/20 bg-white/5 p-6 text-center text-slate-400 backdrop-blur-md">
              <ImageIcon className="h-12 w-12 text-white/30 stroke-1" />
              <div className="text-sm font-semibold text-slate-200">Nenhuma foto adicionada</div>
              <p className="text-xs text-slate-400">
                Faça o upload das fotos no bloco 1 para navegar e cadastrar achados.
              </p>
            </div>
          ) : (
            <div className="relative flex w-full items-center justify-center">
              {/* CARD ANTERIOR (ESQUERDA - SOBREPOSTO ATRÁS COM CLIQUE CIRCULAR) */}
              {prevPhoto && (
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
                  <span className="absolute bottom-3 left-3 rounded-lg bg-black/70 px-2 py-0.5 text-[10px] font-semibold text-white backdrop-blur-md">
                    Foto #{String(prevIdx! + 1).padStart(2, "0")}
                  </span>
                </div>
              )}

              {/* CARD ATIVO (CENTRAL - DESTAQUE 3D COM ANIMAÇÃO FLUIDA DIREÇÃO NEXT/PREV) */}
              {currentPhoto && (
                <div
                  key={`curr_${fotoIdx}_${animKey}`}
                  className={`group relative z-30 w-[78%] sm:w-[72%] overflow-hidden rounded-3xl border-2 bg-slate-900 ${
                    direction === "next" ? "anim-slide-next" : "anim-slide-prev"
                  }`}
                  style={{
                    aspectRatio: "4 / 3",
                    borderColor: theme.primary,
                    boxShadow: "0 20px 50px rgba(0,0,0,0.6)",
                  }}
                >
                  <img
                    src={currentPhoto.previewUrl}
                    alt={currentPhoto.name}
                    className="h-full w-full object-cover cursor-pointer transition-transform duration-500 group-hover:scale-105"
                    onClick={() => setZoomUrl(currentPhoto.previewUrl)}
                  />

                  {/* Degradê superior para contraste de badges */}
                  <div className="pointer-events-none absolute inset-x-0 top-0 h-16 bg-gradient-to-b from-black/60 to-transparent" />

                  {/* Badge de Status "Em NC" */}
                  {currentInNc && (
                    <span className="absolute right-3.5 top-3.5 inline-flex items-center gap-1.5 rounded-full bg-ok px-3 py-1 text-[11px] font-bold text-white shadow-lg backdrop-blur-md animate-in fade-in duration-300">
                      <CheckCircle2 className="h-3.5 w-3.5" /> Em NC
                    </span>
                  )}

                  {/* Botão de Zoom no canto superior */}
                  <button
                    type="button"
                    onClick={() => setZoomUrl(currentPhoto.previewUrl)}
                    aria-label="Ampliar foto"
                    className="absolute left-3.5 top-3.5 rounded-full bg-black/60 p-2 text-white shadow-lg backdrop-blur-md hover:scale-110 active:scale-95 transition-all"
                  >
                    <ZoomIn className="h-4 w-4" />
                  </button>

                  {/* Barra de Informações da Foto Ativa no Rodapé */}
                  <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/85 via-black/50 to-transparent p-3.5 pt-7 text-left text-white backdrop-blur-[2px]">
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

              {/* CARD POSTERIOR (DIREITA - SOBREPOSTO ATRÁS COM CLIQUE CIRCULAR) */}
              {nextPhoto && (
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
                  <span className="absolute bottom-3 right-3 rounded-lg bg-black/70 px-2 py-0.5 text-[10px] font-semibold text-white backdrop-blur-md">
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
          className="absolute right-2 sm:right-4 z-40 flex h-11 w-11 items-center justify-center rounded-full border border-white/30 bg-white/90 text-slate-900 shadow-2xl backdrop-blur-md transition-all duration-300 hover:scale-110 active:scale-95 disabled:pointer-events-none disabled:opacity-20"
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

      {/* Modal de Zoom */}
      {zoomUrl && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 p-4 backdrop-blur-sm"
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
        </div>
      )}
    </div>
  );
};
