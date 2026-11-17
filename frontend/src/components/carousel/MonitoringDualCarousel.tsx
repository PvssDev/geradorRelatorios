import React from "react";
import { CheckCircle2, FastForward } from "lucide-react";
import { MonitoramentoAnteriorItem, UploadedPhotoItem } from "../../types/report.types";
import { DarkGalleryModal } from "../modals/DarkGalleryModal";
import { VerticalMonitorCarousel } from "../VerticalMonitorCarousel";
import { PhotoZoomLightbox } from "./PhotoZoomLightbox";

interface MonitoringDualCarouselProps {
  oldItems: MonitoramentoAnteriorItem[];
  oldIdx: number;
  oldDirection: "next" | "prev";
  oldAnimKey: number;
  auditedOldIds: Map<string, string>;
  onOldPrev: () => void;
  onOldNext: () => void;
  onSelectOldIdx: (idx: number) => void;
  fotos: UploadedPhotoItem[];
  newIdx: number;
  newDirection: "next" | "prev";
  newAnimKey: number;
  fotosEmNc: Set<string>;
  onNewPrev: () => void;
  onNewNext: () => void;
  onOpenGalleryModal?: () => void;
  autoAdvanceActive: boolean;
  onToggleAutoAdvance: () => void;
  showAllOldModal: boolean;
  onOpenAllOldModal: () => void;
  onCloseAllOldModal: () => void;
  zoomUrl: string | null;
  onZoom: (url: string | null) => void;
  themePrimary: string;
  isPerf: boolean;
}

const getOldImgSrc = (it: MonitoramentoAnteriorItem | null | undefined) => {
  if (!it?.old_photo_b64) return null;
  return it.old_photo_b64.startsWith("data:")
    ? it.old_photo_b64
    : `data:image/jpeg;base64,${it.old_photo_b64}`;
};

export const MonitoringDualCarousel: React.FC<MonitoringDualCarouselProps> = ({
  oldItems,
  oldIdx,
  oldDirection,
  oldAnimKey,
  auditedOldIds,
  onOldPrev,
  onOldNext,
  onSelectOldIdx,
  fotos,
  newIdx,
  newDirection,
  newAnimKey,
  fotosEmNc,
  onNewPrev,
  onNewNext,
  onOpenGalleryModal,
  autoAdvanceActive,
  onToggleAutoAdvance,
  showAllOldModal,
  onOpenAllOldModal,
  onCloseAllOldModal,
  zoomUrl,
  onZoom,
  themePrimary,
  isPerf,
}) => {
  const totalOld = oldItems.length;
  const totalFotos = fotos.length;
  const oldItem = oldItems[oldIdx];
  const auditedStatus = oldItem ? auditedOldIds.get(oldItem.id_nc) : undefined;

  const prevOldIdx = totalOld > 1 ? (oldIdx - 1 + totalOld) % totalOld : null;
  const nextOldIdx = totalOld > 1 ? (oldIdx + 1) % totalOld : null;
  const prevOldItem = prevOldIdx !== null ? oldItems[prevOldIdx] : null;
  const nextOldItem = nextOldIdx !== null ? oldItems[nextOldIdx] : null;

  const currentNewPhoto = fotos[newIdx] || null;
  const prevNewIdx = totalFotos > 1 ? (newIdx - 1 + totalFotos) % totalFotos : null;
  const nextNewIdx = totalFotos > 1 ? (newIdx + 1) % totalFotos : null;
  const prevNewPhoto = prevNewIdx !== null ? fotos[prevNewIdx] : null;
  const nextNewPhoto = nextNewIdx !== null ? fotos[nextNewIdx] : null;

  const isCurrentNewInNc = currentNewPhoto
    ? fotosEmNc.has(currentNewPhoto.name.trim().toLowerCase())
    : false;

  const oldSrc = getOldImgSrc(oldItem);
  const prevOldSrc = getOldImgSrc(prevOldItem);
  const nextOldSrc = getOldImgSrc(nextOldItem);

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
          className="pointer-events-none absolute -top-24 left-1/2 h-56 w-[550px] -translate-x-1/2 rounded-full blur-xl opacity-15 transition-all duration-300"
          style={{ backgroundColor: themePrimary }}
        />
      )}

      {/* Barra Superior Global */}
      <div className="relative z-10 mb-5 flex flex-wrap items-center justify-between gap-3 text-xs font-semibold uppercase tracking-wider text-slate-200">
        <div className="flex flex-wrap items-center gap-2">
          <span className="flex items-center gap-2 text-white">
            <span
              className="h-2 w-2 rounded-full animate-pulse"
              style={{ backgroundColor: themePrimary }}
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
            title="Avançar para a próxima ocorrência automaticamente ao salvar"
          >
            <FastForward className="h-3 w-3" />
            Auto-avanço
          </button>
        </div>
      </div>

      {/* Grade de 2 Carrosséis Verticais Lado a Lado */}
      <div className="relative z-10 grid gap-6 md:grid-cols-2">
        <div className="flex flex-col">
          <VerticalMonitorCarousel
            title="Foto Anterior (Doc)"
            galleryLabel="Galeria anterior"
            galleryTitle="Abrir grade com todas as fotos do documento anterior"
            onOpenGallery={onOpenAllOldModal}
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
            onPrev={onOldPrev}
            onNext={onOldNext}
            onZoom={(src) => onZoom(src)}
            themePrimary={themePrimary}
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

          {oldItem && (
            <div className="mt-4 flex flex-1 flex-col gap-1.5 rounded-2xl border border-white/10 bg-white/5 p-4 text-xs text-slate-300 shadow-sm">
              <span
                className="block text-[10px] font-bold uppercase tracking-wider text-slate-400"
                style={{ color: themePrimary }}
              >
                Legenda Antiga
              </span>
              <p className="mt-0.5 text-xs italic leading-relaxed text-slate-200">
                {oldItem.old_legend || "—"}
              </p>
            </div>
          )}
        </div>

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
            onPrev={onNewPrev}
            onNext={onNewNext}
            onZoom={(src) => onZoom(src)}
            themePrimary={themePrimary}
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

          {oldItem && (
            <div className="mt-4 flex flex-1 flex-col gap-1.5 rounded-2xl border border-white/10 bg-white/5 p-4 text-xs text-slate-300 shadow-sm">
              <span
                className="block text-[10px] font-bold uppercase tracking-wider text-slate-400"
                style={{ color: themePrimary }}
              >
                Constatação Antiga
              </span>
              <p className="mt-0.5 text-xs leading-relaxed text-slate-200">
                {oldItem.constatacao || "—"}
              </p>
            </div>
          )}
        </div>
      </div>

      {showAllOldModal && (
        <DarkGalleryModal
          title="Fotos do Relatório Anterior"
          totalCount={totalOld}
          searchPlaceholder="Pesquisar por código (ID), constatação ou situação (ex: Pendente, Saneada)..."
          emptyLabel="Nenhuma foto anterior encontrada"
          infoBanner={
            <>
              <strong>Como funciona o status:</strong> quando uma foto anterior já
              foi registrada na auditoria atual, ela exibe a situação escolhida —
              se registrada como <strong className="text-amber-300">Pendente</strong>,
              permanece marcada como pendente para acompanhamento. Fotos sem
              registro exibem{" "}
              <strong className="text-slate-200">Aguardando registro</strong>.
            </>
          }
          items={oldItems.map((it, idx) => {
            const status = auditedOldIds.get(it.id_nc);
            const statusText = status
              ? `registrada ${status}`
              : "aguardando registro nao auditada";

            let topRightBadge = {
              label: "Aguardando registro",
              className: "bg-slate-900/85 text-slate-300 border border-white/15",
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
                onSelectOldIdx(idx);
                onCloseAllOldModal();
              },
            };
          })}
          onClose={onCloseAllOldModal}
        />
      )}

      <PhotoZoomLightbox zoomUrl={zoomUrl} onClose={() => onZoom(null)} />
    </div>
  );
};

