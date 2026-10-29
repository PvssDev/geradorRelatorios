import React, { useMemo, useState } from "react";
import {
  Image as ImageIcon,
  X,
  Images,
  CheckCircle2,
  FastForward,
} from "lucide-react";
import { useReportStore } from "../store/useReportStore";

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
  const isMonitoring = categoriaRelatorio === "Monitoramento";
  const [zoomUrl, setZoomUrl] = useState<string | null>(null);
  const [onlyPendingOld, setOnlyPendingOld] = useState(false);

  const fotos = ws.photos;
  const fotoIdx = Math.max(
    0,
    Math.min(ws.carouselIndex, Math.max(0, fotos.length - 1))
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

  // Modo Monitoramento com itens anteriores carregados: Comparador Anterior x Atual
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

    return (
      <div className="rounded-2xl bg-navy-gradient p-5">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2 text-xs font-semibold uppercase tracking-wide text-primary-foreground">
          <div className="flex flex-wrap items-center gap-2">
            <span>
              Comparação Fotográfica · {oldItem?.display_label || oldItem?.id_nc}
            </span>
            {auditedStatus && (
              <span className="inline-flex items-center gap-1 rounded-full bg-ok px-2 py-0.5 text-[10px] font-bold normal-case text-white">
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
              className={`rounded-lg px-2.5 py-1 text-[11px] font-semibold normal-case transition ${
                onlyPendingOld
                  ? "bg-accent text-accent-foreground"
                  : "bg-navy-2 text-primary-foreground/80 hover:text-primary-foreground"
              }`}
            >
              {onlyPendingOld
                ? `Apenas não auditadas (${pendingCount})`
                : `Filtrar não auditadas (${pendingCount}/${totalOld})`}
            </button>

            <button
              type="button"
              onClick={() => setAutoAdvanceActive(!autoAdvanceActive)}
              className={`inline-flex items-center gap-1 rounded-lg px-2.5 py-1 text-[11px] font-semibold normal-case transition ${
                autoAdvanceActive
                  ? "bg-accent text-accent-foreground"
                  : "bg-navy-2 text-primary-foreground/75 hover:text-primary-foreground"
              }`}
              title="Avançar automaticamente para a próxima ocorrência após salvar"
            >
              <FastForward className="h-3 w-3" />
              Auto-avanço
            </button>

            {fotos.length > 0 && onOpenGalleryModal && (
              <button
                type="button"
                onClick={onOpenGalleryModal}
                className="inline-flex items-center gap-1 rounded-lg bg-navy-2 px-2.5 py-1 text-[11px] font-semibold normal-case text-primary-foreground hover:bg-accent transition"
              >
                <Images className="h-3.5 w-3.5" />
                Ver todas as fotos
              </button>
            )}

            <span className="text-accent">
              {oldIdx + 1} / {totalOld}
            </span>
          </div>
        </div>

        {/* Contexto Extraído do Relatório Anterior */}
        {oldItem && (
          <div className="mb-4 grid gap-2 rounded-xl border border-sidebar-border bg-navy-2/90 p-3 text-xs text-primary-foreground/90 sm:grid-cols-2">
            <div>
              <span className="font-semibold text-accent">Identificação:</span>{" "}
              <span className="font-mono">{oldItem.id_nc || "—"}</span>
              {tipoRelatorio !== "SOCICAM" &&
                (oldItem.pista || oldItem.trecho) && (
                  <span className="ml-2 text-primary-foreground/75">
                    · {[oldItem.pista, oldItem.trecho].filter(Boolean).join(" / ")}
                  </span>
                )}
            </div>
            {oldItem.old_legend && (
              <div className="truncate" title={oldItem.old_legend}>
                <span className="font-semibold text-accent">Legenda Ant.:</span>{" "}
                {oldItem.old_legend}
              </div>
            )}
            {oldItem.constatacao && (
              <div className="sm:col-span-2 text-primary-foreground/85">
                <span className="font-semibold text-accent">
                  Constatação Anterior:
                </span>{" "}
                {oldItem.constatacao}
              </div>
            )}
          </div>
        )}

        <div className="mb-4 flex items-center gap-2">
          <button
            type="button"
            disabled={
              onlyPendingOld ? posInFiltered <= 0 : oldIdx <= 0
            }
            onClick={() => {
              if (onlyPendingOld && posInFiltered > 0) {
                setCarouselIndex(filteredIndices[posInFiltered - 1].idx);
              } else {
                setCarouselIndex(oldIdx - 1);
              }
            }}
            className="rounded-lg bg-navy-2 px-3 py-1.5 text-xs font-semibold text-primary-foreground disabled:opacity-40 hover:bg-accent transition"
          >
            ‹ Anterior
          </button>
          <select
            value={oldIdx}
            onChange={(e) => setCarouselIndex(Number(e.target.value))}
            className="flex-1 rounded-lg border border-sidebar-border bg-navy-2 px-3 py-1.5 text-xs font-medium text-primary-foreground outline-none"
          >
            {(onlyPendingOld && filteredIndices.length > 0
              ? filteredIndices
              : ws.oldPhotosToMatch.map((it, idx) => ({ it, idx }))
            ).map(({ it, idx }) => (
              <option key={`${it.id_nc}_${idx}`} value={idx}>
                {auditedOldIds.has(it.id_nc) ? "✓ " : ""}
                {it.display_label || it.id_nc}
              </option>
            ))}
          </select>
          <button
            type="button"
            disabled={
              onlyPendingOld
                ? posInFiltered < 0 || posInFiltered >= filteredIndices.length - 1
                : oldIdx >= totalOld - 1
            }
            onClick={() => {
              if (
                onlyPendingOld &&
                posInFiltered >= 0 &&
                posInFiltered < filteredIndices.length - 1
              ) {
                setCarouselIndex(filteredIndices[posInFiltered + 1].idx);
              } else {
                setCarouselIndex(oldIdx + 1);
              }
            }}
            className="rounded-lg bg-navy-2 px-3 py-1.5 text-xs font-semibold text-primary-foreground disabled:opacity-40 hover:bg-accent transition"
          >
            Posterior ›
          </button>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <button
            type="button"
            disabled={!oldSrc}
            onClick={() => oldSrc && setZoomUrl(oldSrc)}
            className="relative grid aspect-[4/3] place-items-center overflow-hidden rounded-xl border-2 border-sidebar-border bg-navy-2"
          >
            {oldSrc ? (
              <img
                src={oldSrc}
                alt="Anterior"
                className="h-full w-full object-cover"
              />
            ) : (
              <ImageIcon className="h-8 w-8 text-primary-foreground/40" />
            )}
            <span className="absolute bottom-2 left-2 rounded-md bg-primary/80 px-2 py-0.5 text-[11px] font-semibold text-primary-foreground">
              Foto Anterior
            </span>
          </button>

          <div className="space-y-2">
            <button
              type="button"
              disabled={!matchedNew}
              onClick={() => matchedNew && setZoomUrl(matchedNew.previewUrl)}
              className="relative grid w-full aspect-[4/3] place-items-center overflow-hidden rounded-xl border-2 border-accent bg-navy-2"
            >
              {matchedNew ? (
                <img
                  src={matchedNew.previewUrl}
                  alt={matchedNew.name}
                  className="h-full w-full object-cover"
                />
              ) : (
                <ImageIcon className="h-8 w-8 text-primary-foreground/40" />
              )}
              <span className="absolute bottom-2 left-2 rounded-md bg-primary/80 px-2 py-0.5 text-[11px] font-semibold text-primary-foreground">
                {matchedNew ? matchedNew.name : "Envie fotos no bloco 1"}
              </span>
            </button>
            {fotos.length > 0 && onSelectNewPhotoName && (
              <select
                value={matchedNew?.name || ""}
                onChange={(e) => onSelectNewPhotoName(e.target.value)}
                className="w-full rounded-lg border border-sidebar-border bg-navy-2 px-2.5 py-1.5 text-xs text-primary-foreground outline-none"
              >
                {fotos.map((f, idx) => (
                  <option key={f.id} value={f.name}>
                    {fotosEmNc.has(f.name.trim().toLowerCase()) ? "✓ " : ""}
                    Foto {String(idx + 1).padStart(2, "0")} — {f.name}
                  </option>
                ))}
              </select>
            )}
          </div>
        </div>

        {zoomUrl && (
          <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-foreground/80 p-4"
            onClick={() => setZoomUrl(null)}
          >
            <div className="relative max-h-[90vh] max-w-4xl">
              <button
                type="button"
                aria-label="Fechar ampliação"
                onClick={() => setZoomUrl(null)}
                className="absolute right-2 top-2 rounded-full bg-primary p-1.5 text-primary-foreground"
              >
                <X className="h-5 w-5" />
              </button>
              <img
                src={zoomUrl}
                alt="Zoom"
                className="max-h-[85vh] rounded-xl object-contain"
              />
            </div>
          </div>
        )}
      </div>
    );
  }

  // Modo Padrão (3-up em bg-navy-gradient fiel ao Lovable)
  return (
    <div className="rounded-2xl bg-navy-gradient p-5">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2 text-xs font-semibold uppercase tracking-wide text-primary-foreground">
        <div className="flex items-center gap-2">
          <span>Foto vinculada</span>
          {fotos[fotoIdx] && (
            <span className="font-mono text-[11px] font-normal normal-case text-primary-foreground/75">
              ({fotos[fotoIdx].name})
            </span>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => setAutoAdvanceActive(!autoAdvanceActive)}
            className={`inline-flex items-center gap-1 rounded-lg px-2.5 py-1 text-[11px] font-semibold normal-case transition ${
              autoAdvanceActive
                ? "bg-accent text-accent-foreground"
                : "bg-navy-2 text-primary-foreground/75 hover:text-primary-foreground"
            }`}
            title="Avançar para a próxima foto automaticamente ao registrar uma ocorrência"
          >
            <FastForward className="h-3 w-3" />
            Avançar automaticamente
          </button>

          {fotos.length > 0 && onOpenGalleryModal && (
            <button
              type="button"
              onClick={onOpenGalleryModal}
              className="inline-flex items-center gap-1 rounded-lg bg-navy-2 px-2.5 py-1 text-[11px] font-semibold normal-case text-primary-foreground hover:bg-accent transition"
            >
              <Images className="h-3.5 w-3.5" />
              Ver todas as fotos
            </button>
          )}

          <span className="text-accent">
            {fotos.length ? `${fotoIdx + 1} / ${fotos.length}` : "sem fotos"}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-[1fr_2fr_1fr] items-center gap-4">
        {([-1, 0, 1] as const).map((off) => {
          const targetIdx = fotoIdx + off;
          const f =
            targetIdx >= 0 && targetIdx < fotos.length
              ? fotos[targetIdx]
              : undefined;
          const main = off === 0;
          const inNc = f
            ? fotosEmNc.has(f.name.trim().toLowerCase())
            : false;

          return (
            <button
              key={off}
              type="button"
              disabled={!f}
              onClick={() => {
                if (!f) return;
                if (main) {
                  setZoomUrl(f.previewUrl);
                } else {
                  setCarouselIndex(targetIdx);
                }
              }}
              className={`relative grid place-items-center overflow-hidden rounded-xl border-2 bg-navy-2 transition ${
                main
                  ? "aspect-[4/3] border-accent"
                  : "aspect-square border-sidebar-border opacity-60 hover:opacity-100"
              }`}
            >
              {f ? (
                <img
                  src={f.previewUrl}
                  alt={f.name}
                  className="h-full w-full object-cover"
                />
              ) : (
                <ImageIcon className="h-8 w-8 text-primary-foreground/40" />
              )}
              {inNc && (
                <span className="absolute right-2 top-2 inline-flex items-center gap-1 rounded-md bg-ok px-2 py-0.5 text-[10px] font-bold text-white shadow">
                  <CheckCircle2 className="h-3 w-3" /> Em NC
                </span>
              )}
              <span className="absolute bottom-2 left-2 rounded-md bg-primary/80 px-2 py-0.5 text-[11px] font-semibold text-primary-foreground">
                {off === -1
                  ? "‹ Anterior"
                  : off === 1
                  ? "Posterior ›"
                  : f
                  ? `Foto ${String(fotoIdx + 1).padStart(2, "0")}`
                  : "Envie fotos no bloco 1"}
              </span>
            </button>
          );
        })}
      </div>

      {zoomUrl && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-foreground/80 p-4"
          onClick={() => setZoomUrl(null)}
        >
          <div className="relative max-h-[90vh] max-w-4xl">
            <button
              type="button"
              aria-label="Fechar ampliação"
              onClick={() => setZoomUrl(null)}
              className="absolute right-2 top-2 rounded-full bg-primary p-1.5 text-primary-foreground"
            >
              <X className="h-5 w-5" />
            </button>
            <img
              src={zoomUrl}
              alt="Zoom"
              className="max-h-[85vh] rounded-xl object-contain"
            />
          </div>
        </div>
      )}
    </div>
  );
};
