import React, { useState, useMemo } from "react";
import { createPortal } from "react-dom";
import { Images, X, Search, Info, Image as ImageIcon } from "lucide-react";
import { useLockBodyScroll } from "../../hooks/useLockBodyScroll";
import { useConcessionTheme } from "../../hooks/useConcessionTheme";

export interface DarkGalleryItem {
  key: string;
  imageUrl: string | null;
  imageAlt: string;
  title: string;
  subtitle?: string;
  searchText: string;
  topLeftBadge?: {
    label: string;
    className?: string;
  };
  topRightBadge?: {
    label: string;
    className: string;
  };
  isSelected: boolean;
  onSelect: () => void;
}

interface DarkGalleryModalProps {
  title: string;
  totalCount: number;
  items: DarkGalleryItem[];
  searchPlaceholder: string;
  infoBanner: React.ReactNode;
  emptyLabel?: string;
  onClose: () => void;
}

/**
 * Janela de galeria unificada (layout escuro sem blur) reutilizada tanto pela
 * Galeria Anterior (Monitoramento) quanto pela Galeria de Fotos do Levantamento.
 */
export const DarkGalleryModal: React.FC<DarkGalleryModalProps> = ({
  title,
  totalCount,
  items,
  searchPlaceholder,
  infoBanner,
  emptyLabel = "Nenhuma foto encontrada",
  onClose,
}) => {
  useLockBodyScroll(true);
  const theme = useConcessionTheme();
  const [search, setSearch] = useState("");

  const q = search.trim().toLowerCase();
  const filtered = useMemo(() => {
    if (!q) return items;
    return items.filter((item) => item.searchText.toLowerCase().includes(q));
  }, [items, q]);

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/85 p-4 animate-in fade-in"
      role="dialog"
      aria-modal="true"
      onClick={onClose}
    >
      <div
        className="relative flex max-h-[85vh] w-full max-w-4xl flex-col overflow-hidden rounded-3xl bg-slate-900 shadow-2xl animate-in fade-in zoom-in-95 duration-200"
        onClick={(e) => e.stopPropagation()}
      >
        <div
          className="h-1 w-full shrink-0"
          style={{
            background: `linear-gradient(90deg, ${theme.primary}, ${theme.primary}aa 60%, transparent)`,
          }}
        />
        <div className="flex flex-1 min-h-0 flex-col p-6 pt-5">
        <div className="mb-3 flex shrink-0 items-center justify-between border-b border-white/10 pb-3">
          <div className="flex items-center gap-2 min-w-0">
            <Images className="h-5 w-5 shrink-0" style={{ color: theme.primary }} />
            <h3 className="truncate text-base font-bold text-white">
              {title} ({filtered.length}
              {q ? ` de ${totalCount}` : ""})
            </h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Fechar galeria"
            className="rounded-full bg-white/10 p-2 text-slate-300 hover:bg-white/20 hover:text-white transition-all"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Barra de Pesquisa + Explicação de Status */}
        <div className="mb-4 shrink-0 space-y-2.5">
          <div className="relative">
            <Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={searchPlaceholder}
              className="w-full rounded-xl border border-white/15 bg-slate-950/80 py-2.5 pl-10 pr-10 text-xs text-white placeholder:text-slate-400 focus:border-white/40 focus:outline-none transition"
            />
            {search && (
              <button
                type="button"
                onClick={() => setSearch("")}
                aria-label="Limpar pesquisa"
                className="absolute right-3 top-1/2 -translate-y-1/2 rounded-full p-1 text-slate-400 hover:bg-white/10 hover:text-white transition"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            )}
          </div>

          <div className="flex items-start gap-2 rounded-xl border border-amber-400/25 bg-amber-500/10 px-3 py-2 text-[11px] leading-relaxed text-amber-100/90">
            <Info className="mt-0.5 h-3.5 w-3.5 shrink-0 text-amber-300" />
            <span>{infoBanner}</span>
          </div>
        </div>

        {filtered.length === 0 ? (
          <div className="flex flex-1 flex-col items-center justify-center py-12 text-center text-slate-400">
            <Search className="mb-2 h-8 w-8 opacity-40" />
            <p className="text-sm font-medium text-slate-300">
              {q ? `${emptyLabel} para "${search}".` : `${emptyLabel}.`}
            </p>
            {q && (
              <button
                type="button"
                onClick={() => setSearch("")}
                className="mt-2 text-xs font-semibold text-white underline hover:opacity-80"
              >
                Limpar filtro
              </button>
            )}
          </div>
        ) : (
          <div className="flex-1 min-h-0 overflow-y-auto pr-1">
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 auto-rows-max content-start">
              {filtered.map((item) => (
                <button
                  key={item.key}
                  type="button"
                  onClick={item.onSelect}
                  className={`group relative flex cursor-pointer flex-col overflow-hidden rounded-2xl border-2 bg-slate-800 text-left transition-all hover:scale-[1.02] ${
                    item.isSelected
                      ? "shadow-lg"
                      : "border-white/10 hover:border-white/30"
                  }`}
                  style={
                    item.isSelected
                      ? {
                          borderColor: theme.primary,
                          boxShadow: `0 0 0 2px ${theme.primary}`,
                        }
                      : {}
                  }
                >
                  <div className="relative aspect-[4/3] w-full shrink-0 overflow-hidden bg-slate-950">
                    {item.imageUrl ? (
                      <img
                        src={item.imageUrl}
                        alt={item.imageAlt}
                        className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
                      />
                    ) : (
                      <div className="flex h-full w-full items-center justify-center">
                        <ImageIcon className="h-8 w-8 text-white/30" />
                      </div>
                    )}
                    {item.topLeftBadge && (
                      <span
                        className={
                          item.topLeftBadge.className ||
                          "absolute left-2 top-2 rounded-full bg-slate-950/85 px-2 py-0.5 font-mono text-[10px] font-bold text-white border border-white/15 shadow"
                        }
                      >
                        {item.topLeftBadge.label}
                      </span>
                    )}
                    {item.topRightBadge && (
                      <span
                        className={`absolute top-2 right-2 rounded-full px-2 py-0.5 text-[9px] font-bold shadow ${item.topRightBadge.className}`}
                      >
                        {item.topRightBadge.label}
                      </span>
                    )}
                  </div>
                  <div className="w-full shrink-0 p-2 text-xs">
                    <div
                      className="font-mono font-bold text-white truncate"
                      title={item.title}
                    >
                      {item.title}
                    </div>
                    {item.subtitle && (
                      <div
                        className="text-[11px] text-slate-400 truncate"
                        title={item.subtitle}
                      >
                        {item.subtitle}
                      </div>
                    )}
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}
        </div>
      </div>
    </div>,
    document.body
  );
};

