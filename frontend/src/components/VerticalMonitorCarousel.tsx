import React from "react";
import {
  Image as ImageIcon,
  Images,
  ChevronUp,
  ChevronDown,
  ZoomIn,
  Lock,
} from "lucide-react";

export interface VerticalCarouselCardData {
  id: string;
  src: string | null;
  alt: string;
  label: string;
  prevTitle?: string;
  nextTitle?: string;
}

interface VerticalMonitorCarouselProps {
  title: string;
  galleryLabel: string;
  galleryTitle: string;
  onOpenGallery?: () => void;
  total: number;
  currentIndex: number;
  direction: "next" | "prev";
  animKey: number;
  prevItem: VerticalCarouselCardData | null;
  currentItem: VerticalCarouselCardData | null;
  nextItem: VerticalCarouselCardData | null;
  onPrev: () => void;
  onNext: () => void;
  onZoom: (src: string) => void;
  themePrimary: string;
  isPerf: boolean;
  emptyText: string;
  prevBtnAriaLabel: string;
  prevBtnTitle: string;
  nextBtnAriaLabel: string;
  nextBtnTitle: string;
  zoomTitle: string;
  accentLabel?: boolean;
  blockedReason?: string | null;
}

/**
 * Carrossel vertical 3D reutilizável para o modo Monitoramento
 * (compartilhado entre Fotos Anteriores e Fotos Novas de Vistoria).
 */
export const VerticalMonitorCarousel: React.FC<VerticalMonitorCarouselProps> = ({
  title,
  galleryLabel,
  galleryTitle,
  onOpenGallery,
  total,
  currentIndex,
  direction,
  animKey,
  prevItem,
  currentItem,
  nextItem,
  onPrev,
  onNext,
  onZoom,
  themePrimary,
  isPerf,
  emptyText,
  prevBtnAriaLabel,
  prevBtnTitle,
  nextBtnAriaLabel,
  nextBtnTitle,
  zoomTitle,
  accentLabel = false,
  blockedReason,
}) => {
  return (
    <div className="flex flex-col">
      <div className="mb-2.5 flex min-h-[32px] items-center justify-between gap-2">
        <span className="flex min-w-0 items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-slate-300">
          <span
            className="h-1.5 w-1.5 shrink-0 rounded-full"
            style={{ backgroundColor: themePrimary }}
          />
          <span className="truncate">{title}</span>
        </span>

        <div className="flex shrink-0 items-center gap-1.5">
          {onOpenGallery && (
            <button
              type="button"
              onClick={onOpenGallery}
              className="inline-flex shrink-0 items-center gap-1.5 whitespace-nowrap rounded-xl bg-white/10 px-2.5 py-1 text-[11px] font-semibold normal-case text-slate-200 hover:bg-white/20 hover:text-white shadow-sm transition-all duration-200"
              title={galleryTitle}
            >
              <Images className="h-3.5 w-3.5 shrink-0" />
              {galleryLabel}
            </button>
          )}
          <span
            className="shrink-0 whitespace-nowrap rounded-lg bg-white/10 px-2 py-0.5 font-mono text-[11px] font-bold"
            style={{ color: themePrimary }}
          >
            {total > 0 ? `${currentIndex + 1} / ${total}` : "0 fotos"}
          </span>
        </div>
      </div>

      {/* Palco Vertical 3D */}
      <div className="relative flex h-[350px] sm:h-[390px] w-full flex-col items-center justify-center select-none overflow-hidden rounded-2xl bg-slate-950/40 border border-white/10 p-2 shadow-inner">
        <button
          type="button"
          disabled={total <= 1}
          onClick={onPrev}
          aria-label={prevBtnAriaLabel}
          className="absolute top-2 z-40 flex h-8 w-8 items-center justify-center rounded-full border border-white/30 bg-white/90 text-slate-900 shadow-md transition-all duration-300 hover:scale-110 active:scale-95 disabled:pointer-events-none disabled:opacity-20"
          title={prevBtnTitle}
        >
          <ChevronUp className="h-5 w-5 stroke-[2.5]" />
        </button>

        {/* Card Superior */}
        {!isPerf && prevItem && (
          <div
            key={`prev_${prevItem.id}`}
            onClick={onPrev}
            className="group absolute top-2 z-10 w-[82%] h-[40%] cursor-pointer overflow-hidden rounded-2xl border-2 border-white/20 bg-slate-900 shadow-xl transition-all duration-500 ease-out hover:opacity-85 -translate-y-2 scale-[0.86] opacity-50"
            title={prevItem.prevTitle || prevItem.label}
          >
            {prevItem.src ? (
              <img
                src={prevItem.src}
                alt={prevItem.alt}
                className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
              />
            ) : (
              <div className="flex h-full w-full items-center justify-center bg-slate-900">
                <ImageIcon className="h-8 w-8 text-white/30" />
              </div>
            )}
            <div className="absolute inset-0 bg-black/40 transition-colors group-hover:bg-black/20" />
            <span className="absolute bottom-2 left-2 rounded-md bg-black/70 px-2 py-0.5 text-[10px] font-semibold text-white truncate max-w-[90%]">
              {prevItem.label}
            </span>
          </div>
        )}

        {/* Card Central Ativo */}
        <div
          key={`curr_${currentIndex}_${animKey}`}
          className={`group relative z-30 flex aspect-[4/3] w-[92%] max-h-[70%] items-center justify-center overflow-hidden rounded-2xl border-2 bg-slate-900 ${
            isPerf
              ? "shadow-md"
              : `shadow-2xl transition-all duration-300 ${
                  direction === "next" ? "anim-v-slide-next" : "anim-v-slide-prev"
                }`
          }`}
          style={{
            borderColor: themePrimary,
            boxShadow: isPerf ? undefined : `0 0 20px ${themePrimary}38`,
          }}
        >
          {currentItem?.src ? (
            <img
              src={currentItem.src}
              alt={currentItem.alt}
              className={`h-full w-full object-cover ${
                isPerf ? "" : "transition-transform duration-300 group-hover:scale-105"
              }`}
            />
          ) : (
            <div className="flex h-full w-full flex-col items-center justify-center gap-2 bg-slate-900">
              <ImageIcon className="h-10 w-10 text-white/30" />
              <span className="text-xs text-slate-400">{emptyText}</span>
            </div>
          )}

          {blockedReason && (
            <span
              className="absolute left-3 top-3 z-40 inline-flex items-center gap-1 rounded-full bg-amber-500/95 px-2.5 py-1 text-[10px] font-bold text-slate-950 shadow-md"
              title={blockedReason}
            >
              <Lock className="h-3 w-3" />
              Já registrada
            </span>
          )}

          <span
            className={`absolute bottom-3 left-3 rounded-lg px-2.5 py-1 text-xs font-semibold text-white max-w-[85%] truncate ${
              accentLabel ? "shadow-md" : "bg-black/75"
            }`}
            style={accentLabel ? { backgroundColor: themePrimary } : undefined}
          >
            {currentItem?.label || "Nenhuma foto"}
          </span>

          {currentItem?.src && (
            <button
              type="button"
              onClick={() => onZoom(currentItem.src!)}
              className="absolute right-3 top-3 z-40 rounded-full bg-black/60 p-2 text-white/80 hover:text-white hover:bg-black/80 transition-all hover:scale-110 active:scale-95"
              title={zoomTitle}
            >
              <ZoomIn className="h-4 w-4" />
            </button>
          )}
        </div>

        {/* Card Inferior */}
        {!isPerf && nextItem && (
          <div
            key={`next_${nextItem.id}`}
            onClick={onNext}
            className="group absolute bottom-2 z-10 w-[82%] h-[40%] cursor-pointer overflow-hidden rounded-2xl border-2 border-white/20 bg-slate-900 shadow-xl transition-all duration-500 ease-out hover:opacity-85 translate-y-2 scale-[0.86] opacity-50"
            title={nextItem.nextTitle || nextItem.label}
          >
            {nextItem.src ? (
              <img
                src={nextItem.src}
                alt={nextItem.alt}
                className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
              />
            ) : (
              <div className="flex h-full w-full items-center justify-center bg-slate-900">
                <ImageIcon className="h-8 w-8 text-white/30" />
              </div>
            )}
            <div className="absolute inset-0 bg-black/40 transition-colors group-hover:bg-black/20" />
            <span className="absolute bottom-2 left-2 rounded-md bg-black/70 px-2 py-0.5 text-[10px] font-semibold text-white truncate max-w-[90%]">
              {nextItem.label}
            </span>
          </div>
        )}

        <button
          type="button"
          disabled={total <= 1}
          onClick={onNext}
          aria-label={nextBtnAriaLabel}
          className="absolute bottom-2 z-40 flex h-8 w-8 items-center justify-center rounded-full border border-white/30 bg-white/90 text-slate-900 shadow-md transition-all duration-300 hover:scale-110 active:scale-95 disabled:pointer-events-none disabled:opacity-20"
          title={nextBtnTitle}
        >
          <ChevronDown className="h-5 w-5 stroke-[2.5]" />
        </button>
      </div>
    </div>
  );
};

