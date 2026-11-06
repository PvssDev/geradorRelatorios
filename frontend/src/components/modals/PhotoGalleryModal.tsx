import React, { useState, useMemo } from "react";
import { X, Images, Search, CheckCircle2 } from "lucide-react";
import { useReportStore } from "../../store/useReportStore";
import { UploadedPhotoItem } from "../../types/report.types";
import { modalInputCls } from "./modalHelpers";

export const PhotoGalleryModal: React.FC<{ onClose: () => void }> = ({
  onClose,
}) => {
  const { getActiveWorkspace, setCarouselIndex } = useReportStore();
  const ws = getActiveWorkspace();
  const [filtro, setFiltro] = useState("");

  const fotosEmNc = useMemo(() => {
    const set = new Set<string>();
    for (const nc of ws.registrosNc) {
      if (nc.Foto) set.add(nc.Foto.trim().toLowerCase());
    }
    return set;
  }, [ws.registrosNc]);

  const filtradas = useMemo(() => {
    const q = filtro.trim().toLowerCase();
    return ws.photos
      .map((photo: UploadedPhotoItem, index: number) => ({ photo, index }))
      .filter(({ photo }) => !q || photo.name.toLowerCase().includes(q));
  }, [ws.photos, filtro]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-foreground/60 p-4 backdrop-blur-[1px]"
      role="dialog"
      aria-modal="true"
    >
      <div className="flex max-h-[90vh] w-full max-w-4xl flex-col overflow-hidden rounded-2xl border border-border bg-card shadow-card-lg">
        <div className="flex items-center justify-between border-b border-border bg-navy-gradient px-5 py-4 text-primary-foreground">
          <h3 className="flex items-center gap-2 text-base font-bold">
            <Images className="h-5 w-5 text-accent" />
            Galeria de Fotos do Levantamento ({ws.photos.length} fotos)
          </h3>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1.5 text-primary-foreground/80 hover:bg-white/10 hover:text-primary-foreground"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="space-y-4 overflow-y-auto p-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <p className="text-xs text-muted-foreground">
              Clique em qualquer foto para defini-la como a foto central do
              carrossel. Fotos com selo{" "}
              <b className="text-ok">Vinculada [NC]</b> já foram adicionadas ao
              relatório.
            </p>
            <div className="relative w-full sm:w-64">
              <Search className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                value={filtro}
                onChange={(e) => setFiltro(e.target.value)}
                placeholder="Filtrar por nome..."
                className={`${modalInputCls} pl-9`}
              />
            </div>
          </div>

          {filtradas.length === 0 ? (
            <div className="rounded-xl border border-border bg-secondary/40 p-8 text-center text-sm text-muted-foreground">
              Nenhuma foto encontrada.
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
              {filtradas.map(({ photo, index }) => {
                const isCurrent = index === ws.carouselIndex;
                const inNc = fotosEmNc.has(photo.name.trim().toLowerCase());
                return (
                  <button
                    key={photo.id}
                    type="button"
                    onClick={() => {
                      setCarouselIndex(index);
                      onClose();
                    }}
                    className={`group relative overflow-hidden rounded-xl border-2 text-left transition ${
                      isCurrent
                        ? "border-accent ring-2 ring-accent/30"
                        : inNc
                        ? "border-ok/50 opacity-80 hover:opacity-100"
                        : "border-border hover:border-accent/60"
                    }`}
                  >
                    <div className="relative aspect-[4/3] w-full bg-navy-2">
                      <img
                        src={photo.previewUrl}
                        alt={photo.name}
                        className="h-full w-full object-cover"
                      />
                      <span className="absolute left-2 top-2 rounded-md bg-primary/85 px-2 py-0.5 font-mono text-[10px] font-bold text-primary-foreground">
                        #{String(index + 1).padStart(2, "0")}
                      </span>
                      {inNc && (
                        <span className="absolute right-2 top-2 inline-flex items-center gap-1 rounded-md bg-ok px-2 py-0.5 text-[10px] font-bold text-white">
                          <CheckCircle2 className="h-3 w-3" /> NC
                        </span>
                      )}
                    </div>
                    <div className="bg-card p-2">
                      <p
                        className="truncate text-xs font-semibold text-foreground"
                        title={photo.name}
                      >
                        {photo.name}
                      </p>
                      <p className="text-[10px] text-muted-foreground">
                        {isCurrent ? "Selecionada no carrossel" : "Clique para selecionar"}
                      </p>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

/* -------------------------------------------------------------------------- */
/* 5. JANELA MODAL DE RELACIONAR FOTO À OCORRÊNCIA                            */
/* -------------------------------------------------------------------------- */
