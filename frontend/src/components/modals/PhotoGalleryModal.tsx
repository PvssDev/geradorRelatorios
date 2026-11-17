import React, { useMemo } from "react";
import { useReportStore } from "../../store/useReportStore";
import { UploadedPhotoItem } from "../../types/report.types";
import { DarkGalleryModal, DarkGalleryItem } from "./DarkGalleryModal";

export const PhotoGalleryModal: React.FC<{ onClose: () => void }> = ({
  onClose,
}) => {
  const {
    categoriaRelatorio,
    getActiveWorkspace,
    setCarouselIndex,
    monitoringNewPhotoName,
    setMonitoringNewPhotoName,
  } = useReportStore();
  const ws = getActiveWorkspace();
  const isMonitoring = categoriaRelatorio === "Monitoramento";

  const fotosEmNc = useMemo(() => {
    const set = new Set<string>();
    for (const nc of ws.registrosNc) {
      if (nc.Foto) set.add(nc.Foto.trim().toLowerCase());
    }
    return set;
  }, [ws.registrosNc]);

  const items: DarkGalleryItem[] = useMemo(
    () =>
      ws.photos.map((photo: UploadedPhotoItem, index: number) => {
        const numLabel = `#${String(index + 1).padStart(2, "0")}`;
        const isCurrent = isMonitoring
          ? photo.name === (monitoringNewPhotoName || ws.photos[0]?.name)
          : index === ws.carouselIndex;
        const inNc = fotosEmNc.has(photo.name.trim().toLowerCase());
        const statusLabel = inNc ? "Vinculada NC" : "Disponível";

        return {
          key: photo.id,
          imageUrl: photo.previewUrl,
          imageAlt: photo.name,
          title: photo.name,
          subtitle: isCurrent ? "Selecionada no carrossel" : "Clique para selecionar",
          searchText: `${numLabel} ${photo.name} ${statusLabel}`,
          topLeftBadge: {
            label: numLabel,
          },
          topRightBadge: inNc
            ? {
                label: "✓ NC",
                className: "bg-ok text-white",
              }
            : {
                label: "Disponível",
                className: "bg-slate-900/85 text-slate-300 border border-white/15",
              },
          isSelected: isCurrent,
          onSelect: () => {
            if (isMonitoring) {
              setMonitoringNewPhotoName(photo.name);
            } else {
              setCarouselIndex(index);
            }
            onClose();
          },
        };
      }),
    [
      ws.photos,
      ws.carouselIndex,
      isMonitoring,
      monitoringNewPhotoName,
      fotosEmNc,
      setMonitoringNewPhotoName,
      setCarouselIndex,
      onClose,
    ]
  );

  return (
    <DarkGalleryModal
      title="Galeria de Fotos do Levantamento"
      totalCount={ws.photos.length}
      items={items}
      searchPlaceholder="Pesquisar por nome da foto, número (#01) ou status (NC, Disponível)..."
      infoBanner={
        <>
          <strong>Como usar a galeria:</strong> clique em qualquer foto para
          defini-la como a foto ativa do carrossel. Fotos com selo{" "}
          <strong className="text-emerald-300">✓ NC</strong> já foram
          adicionadas ao relatório; fotos marcadas como{" "}
          <strong className="text-slate-200">Disponível</strong> ainda não
          possuem vínculo.
        </>
      }
      onClose={onClose}
    />
  );
};
