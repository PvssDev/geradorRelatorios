import React from "react";
import {
  Image as ImageIcon,
  Images,
  CheckCircle2,
  FastForward,
  ChevronLeft,
  ChevronRight,
  ZoomIn,
} from "lucide-react";
import { UploadedPhotoItem } from "../../types/report.types";
import { PhotoZoomLightbox } from "./PhotoZoomLightbox";

interface FiscalizacaoHorizontalCarouselProps {
  fotos: UploadedPhotoItem[];
  fotoIdx: number;
  direction: "next" | "prev";
  animKey: number;
  fotosEmNc: Set<string>;
  activeLegenda: string;
  autoAdvanceActive: boolean;
  onToggleAutoAdvance: () => void;
  onPrev: () => void;
  onNext: () => void;
  onGoTo: (idx: number) => void;
  onOpenGalleryModal?: () => void;
  zoomUrl: string | null;
  onZoom: (url: string | null) => void;
  themePrimary: string;
  isPerf: boolean;
}

export const FiscalizacaoHorizontalCarousel: React.FC<
  FiscalizacaoHorizontalCarouselProps
> = ({
  fotos,
  fotoIdx,
  direction,
  animKey,
  fotosEmNc,
  activeLegenda,
  autoAdvanceActive,
  onToggleAutoAdvance,
  onPrev,
  onNext,
  onGoTo,
  onOpenGalleryModal,
  zoomUrl,
  onZoom,
  themePrimary,
  isPerf,
}) => {
  const totalFotos = fotos.length;
  const currentPhoto = fotos[fotoIdx] || null;
  const prevIdx = totalFotos > 1 ? (fotoIdx - 1 + totalFotos) % totalFotos : null;
  const nextIdx = totalFotos > 1 ? (fotoIdx + 1) % totalFotos : null;
  const prevPhoto = prevIdx !== null ? fotos[prevIdx] : null;
  const nextPhoto = nextIdx !== null ? fotos[nextIdx] : null;

  const currentInNc = currentPhoto
    ? fotosEmNc.has(currentPhoto.name.trim().toLowerCase())
    : false;

  const maxDots = 7;
  const startDot = Math.max(
    0,
    Math.min(fotoIdx - Math.floor(maxDots / 2), totalFotos - maxDots)
  );
  const endDot = Math.min(totalFotos, startDot + maxDots);

  return (
    <div
      className={`relative overflow-hidden border p-4 sm:p-6 ${
        isPerf
          ? "rounded-2xl bg-slate-900 border-slate-700 shadow-sm"
          : "rounded-3xl border-slate-700/50 bg-gradient-to-b from-[#0a1a2f] via-[#0d223c] to-[#081526] shadow-2xl "
      }`}
    >
      {!isPerf && (
        <div
          className="pointer-events-none absolute -top-24 left-1/2 h-56 w-[500px] -translate-x-1/2 rounded-full blur-xl opacity-15 transition-all duration-300"
          style={{ backgroundColor: themePrimary }}
        />
      )}

      {/* Barra Superior de Informações & Ações */}
      <div className="relative z-10 mb-5 flex flex-wrap items-center justify-between gap-3 text-xs font-semibold uppercase tracking-wider text-slate-200">
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-2 text-white">
            <span
              className="h-2 w-2 rounded-full animate-pulse"
              style={{ backgroundColor: themePrimary }}
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
            onClick={onToggleAutoAdvance}
            className={`inline-flex items-center gap-1.5 rounded-xl px-3 py-1.5 text-[11px] font-semibold normal-case shadow-sm transition-all duration-200 ${
              autoAdvanceActive
                ? "text-white ring-2 ring-white/30"
                : "bg-white/10 text-slate-300 hover:bg-white/20 hover:text-white"
            }`}
            style={
              autoAdvanceActive
                ? {
                    backgroundColor: themePrimary,
                    boxShadow: `0 0 15px ${themePrimary}40`,
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
            style={{ color: themePrimary }}
          >
            {totalFotos ? `${fotoIdx + 1} / ${totalFotos}` : "0 fotos"}
          </span>
        </div>
      </div>

      {/* Palco 3D CoverFlow */}
      <div className="relative z-10 flex min-h-[290px] sm:min-h-[340px] items-center justify-center py-2 select-none">
        <button
          type="button"
          disabled={totalFotos <= 1}
          onClick={onPrev}
          aria-label="Foto anterior (looping)"
          className={`absolute left-2 sm:left-4 z-40 flex h-11 w-11 items-center justify-center rounded-xl border transition-all ${
            isPerf
              ? "border-slate-700 bg-slate-800 text-white hover:bg-slate-700 active:scale-95 disabled:opacity-20 disabled:pointer-events-none shadow-sm"
              : "rounded-full border-white/30 bg-white/90 text-slate-900 shadow-2xl hover:scale-110 active:scale-95 disabled:pointer-events-none disabled:opacity-20"
          }`}
        >
          <ChevronLeft className="h-6 w-6 stroke-[2.5]" />
        </button>

        <div className="relative flex w-full max-w-2xl items-center justify-center">
          {totalFotos === 0 ? (
            <div className="flex h-64 w-full max-w-md flex-col items-center justify-center gap-3 rounded-3xl border-2 border-dashed border-white/20 bg-white/5 p-6 text-center text-slate-400">
              <ImageIcon className="h-12 w-12 text-white/30 stroke-1" />
              <div className="text-sm font-semibold text-slate-200">
                Nenhuma foto adicionada
              </div>
              <p className="text-xs text-slate-400">
                Faça o upload das fotos no bloco 1 para navegar e cadastrar achados.
              </p>
            </div>
          ) : (
            <div className="relative flex w-full items-center justify-center">
              {!isPerf && prevPhoto && (
                <div
                  key={`prev_${prevIdx}`}
                  onClick={onPrev}
                  className="group absolute left-0 sm:left-4 z-10 w-[62%] sm:w-[58%] cursor-pointer overflow-hidden rounded-3xl border-2 border-white/20 bg-slate-900 shadow-xl transition-all duration-500 ease-out hover:opacity-85 -translate-x-4 sm:-translate-x-8 scale-[0.84] opacity-55"
                  style={{ aspectRatio: "4 / 3" }}
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

              {currentPhoto && (
                <div
                  key={`curr_${fotoIdx}_${animKey}`}
                  className={`group relative z-30 w-[78%] sm:w-[72%] overflow-hidden border-2 ${
                    isPerf
                      ? "rounded-2xl bg-slate-950 shadow-md"
                      : `rounded-3xl bg-slate-900 ${
                          direction === "next" ? "anim-slide-next" : "anim-slide-prev"
                        }`
                  }`}
                  style={{
                    aspectRatio: "4 / 3",
                    borderColor: themePrimary,
                    boxShadow: isPerf ? undefined : "0 20px 50px rgba(0,0,0,0.6)",
                  }}
                >
                  <img
                    src={currentPhoto.previewUrl}
                    alt={currentPhoto.name}
                    className={`h-full w-full object-cover cursor-pointer ${
                      isPerf ? "" : "transition-transform duration-500 group-hover:scale-105"
                    }`}
                    onClick={() => onZoom(currentPhoto.previewUrl)}
                  />

                  <div className="pointer-events-none absolute inset-x-0 top-0 h-16 bg-gradient-to-b from-black/60 to-transparent" />

                  {currentInNc && (
                    <span className="absolute right-3.5 top-3.5 inline-flex items-center gap-1.5 rounded-full bg-ok px-3 py-1 text-[11px] font-bold text-white shadow-lg animate-in fade-in duration-300">
                      <CheckCircle2 className="h-3.5 w-3.5" /> Em NC
                    </span>
                  )}

                  <button
                    type="button"
                    onClick={() => onZoom(currentPhoto.previewUrl)}
                    aria-label="Ampliar foto"
                    className="absolute left-3.5 top-3.5 rounded-full bg-black/60 p-2 text-white shadow-lg hover:scale-110 active:scale-95 transition-all"
                  >
                    <ZoomIn className="h-4 w-4" />
                  </button>

                  <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/85 via-black/50 to-transparent p-3.5 pt-7 text-left text-white">
                    <div className="flex items-center justify-between gap-2">
                      <span
                        className="rounded-lg px-2.5 py-0.5 font-mono text-[11px] font-bold text-white shadow"
                        style={{ backgroundColor: themePrimary }}
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

              {!isPerf && nextPhoto && (
                <div
                  key={`next_${nextIdx}`}
                  onClick={onNext}
                  className="group absolute right-0 sm:right-4 z-10 w-[62%] sm:w-[58%] cursor-pointer overflow-hidden rounded-3xl border-2 border-white/20 bg-slate-900 shadow-xl transition-all duration-500 ease-out hover:opacity-85 translate-x-4 sm:translate-x-8 scale-[0.84] opacity-55"
                  style={{ aspectRatio: "4 / 3" }}
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

        <button
          type="button"
          disabled={totalFotos <= 1}
          onClick={onNext}
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

      {/* Paginação por Dots */}
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
                onClick={() => onGoTo(idxReal)}
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
                        backgroundColor: themePrimary,
                        boxShadow: `0 0 12px ${themePrimary}80`,
                      }
                    : {}
                }
                title={`Foto ${idxReal + 1}${isInNcDot ? " (Em NC)" : ""}`}
              />
            );
          })}
        </div>
      )}

      {/* Prévia da Legenda */}
      {currentPhoto && activeLegenda && (
        <div
          className={`relative z-10 mt-4 mx-auto w-full max-w-xl rounded-2xl border px-4 py-2.5 text-center shadow-sm ${
            isPerf
              ? "bg-slate-950 border-slate-800"
              : "border-white/10 bg-black/45 shadow-lg transition-all duration-300"
          }`}
        >
          <div className="flex items-center justify-center gap-2 text-[10px] font-bold uppercase tracking-wider text-slate-300">
            <span
              className="inline-block h-1.5 w-1.5 rounded-full animate-pulse"
              style={{ backgroundColor: themePrimary }}
            />
            Prévia da Legenda no Relatório (.docx)
          </div>
          <p className="mt-1 font-sans text-xs italic text-slate-100 leading-relaxed">
            {activeLegenda}
          </p>
        </div>
      )}

      <PhotoZoomLightbox zoomUrl={zoomUrl} onClose={() => onZoom(null)} />
    </div>
  );
};

