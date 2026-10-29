import React, { useMemo, useRef, useState } from "react";
import {
  CloudUpload,
  Trash2,
  FileCheck2,
  Loader2,
  Images,
  CheckCircle2,
  X,
} from "lucide-react";
import { toast } from "sonner";
import { Card } from "./Card";
import { useReportStore } from "../store/useReportStore";
import { SortOption } from "../types/report.types";
import { parseMonitoramentoAnteriorApi } from "../services/api";

const SORT_OPTIONS: SortOption[] = [
  "Nome (A-Z / 0-9)",
  "Nome (Z-A / 9-0)",
  "Ordem de Upload",
];

interface UploadPanelProps {
  onOpenGalleryModal: () => void;
}

export const UploadPanel: React.FC<UploadPanelProps> = ({
  onOpenGalleryModal,
}) => {
  const {
    categoriaRelatorio,
    compressImages,
    setCompressImages,
    getActiveWorkspace,
    addUploadedPhotos,
    removePhoto,
    clearPhotos,
    setSortOption,
    setCarouselIndex,
    setMonitoramentoAnteriorData,
  } = useReportStore();

  const ws = getActiveWorkspace();
  const isMonitoring = categoriaRelatorio === "Monitoramento";

  const [parsingDoc, setParsingDoc] = useState(false);
  const docInputRef = useRef<HTMLInputElement | null>(null);

  const fotosEmNc = useMemo(() => {
    const set = new Set<string>();
    ws.registrosNc.forEach((nc) => {
      if (nc.Foto) set.add(nc.Foto.trim().toLowerCase());
    });
    return set;
  }, [ws.registrosNc]);

  const vinculadasCount = useMemo(() => {
    return ws.photos.filter((f) => fotosEmNc.has(f.name.trim().toLowerCase()))
      .length;
  }, [ws.photos, fotosEmNc]);

  const onFiles = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    addUploadedPhotos(files);
    toast.success(`${files.length} foto(s) adicionada(s)!`);
  };

  const handleDocAnteriorChange = async (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setParsingDoc(true);
    try {
      const res = await parseMonitoramentoAnteriorApi(file);
      setMonitoramentoAnteriorData(file, res.itens_pendentes || []);
      toast.success(
        `Relatório anterior processado: ${res.itens_pendentes.length} pendência(s) extraída(s)!`
      );
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : "Erro ao ler o arquivo de monitoramento anterior.";
      toast.error(msg);
    } finally {
      setParsingDoc(false);
      e.target.value = "";
    }
  };

  return (
    <Card
      n={1}
      icon={<CloudUpload className="h-5 w-5" />}
      title="Fotos da Vistoria em Campo"
    >
      {isMonitoring && (
        <div className="mb-6 flex flex-wrap items-center justify-between gap-4 rounded-xl border border-border bg-secondary/60 p-4">
          <div>
            <div className="text-xs font-semibold uppercase tracking-wide text-slate-blue">
              Relatório Anterior de Monitoramento (.docx)
            </div>
            <div className="text-xs text-muted-foreground">
              {ws.documentoAnteriorFile
                ? `${ws.documentoAnteriorFile.name} · ${ws.oldPhotosToMatch.length} pendência(s) extraída(s)`
                : "Envie o documento .docx anterior para auditar as NCs pendentes (obrigatório para CRC Monitoramento)"}
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <input
              type="file"
              ref={docInputRef}
              accept=".docx"
              className="hidden"
              onChange={handleDocAnteriorChange}
            />
            <button
              type="button"
              disabled={parsingDoc}
              onClick={() => docInputRef.current?.click()}
              className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-xs font-semibold text-primary-foreground hover:bg-navy-2 transition disabled:opacity-40"
            >
              {parsingDoc ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <FileCheck2 className="h-4 w-4" />
              )}
              {ws.documentoAnteriorFile
                ? "Substituir .docx"
                : "Enviar Relatório Anterior"}
            </button>
            {ws.documentoAnteriorFile && (
              <button
                type="button"
                onClick={() => {
                  setMonitoramentoAnteriorData(null, []);
                  toast.info("Relatório anterior removido.");
                }}
                className="inline-flex items-center gap-1 rounded-lg border border-nc/30 bg-nc-soft px-3 py-2 text-xs font-semibold text-nc hover:bg-nc hover:text-destructive-foreground transition"
                title="Remover relatório anterior"
              >
                <X className="h-3.5 w-3.5" />
                Remover
              </button>
            )}
          </div>
        </div>
      )}

      <label
        className="flex cursor-pointer flex-col items-center gap-2 rounded-xl border-2 border-dashed border-border bg-muted/50 p-8 text-center hover:border-accent transition"
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          onFiles(e.dataTransfer.files);
        }}
      >
        <CloudUpload className="h-8 w-8 text-slate-blue" />
        <span className="text-sm font-medium">
          Arraste as fotos ou clique para selecionar
        </span>
        <span className="text-xs text-muted-foreground">
          JPG, JPEG, PNG · múltiplos arquivos
        </span>
        <input
          type="file"
          multiple
          accept=".jpg,.jpeg,.png"
          className="hidden"
          onChange={(e) => {
            onFiles(e.target.files);
            e.target.value = "";
          }}
        />
      </label>

      <label className="mt-4 flex items-center gap-3 text-sm cursor-pointer">
        <button
          type="button"
          role="switch"
          aria-checked={compressImages}
          onClick={() => setCompressImages(!compressImages)}
          className={`relative h-6 w-11 shrink-0 rounded-full transition ${
            compressImages ? "bg-accent" : "bg-border"
          }`}
        >
          <span
            className={`absolute top-0.5 h-5 w-5 rounded-full bg-card shadow transition-all ${
              compressImages ? "left-5" : "left-0.5"
            }`}
          />
        </button>
        Otimizar e comprimir imagens automaticamente para o Word (limite de 500 KB)
      </label>

      {ws.photos.length > 0 && (
        <>
          <div className="mt-5 flex flex-wrap items-center justify-between gap-2">
            <div className="text-xs font-semibold text-muted-foreground">
              {ws.photos.length}{" "}
              {ws.photos.length === 1 ? "foto carregada" : "fotos carregadas"}
              {vinculadasCount > 0 && (
                <span className="ml-2 rounded-full bg-ok-soft px-2 py-0.5 text-[11px] font-semibold text-ok">
                  {vinculadasCount} em NC/PA
                </span>
              )}
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <button
                type="button"
                onClick={onOpenGalleryModal}
                className="inline-flex items-center gap-1.5 rounded-lg border border-border bg-card px-2.5 py-1 text-xs font-semibold text-foreground hover:border-accent hover:text-accent transition"
              >
                <Images className="h-3.5 w-3.5" />
                Ver Galeria
              </button>

              <select
                aria-label="Ordenação das fotos"
                value={ws.sortOption}
                onChange={(e) => setSortOption(e.target.value as SortOption)}
                className="rounded-lg border border-input bg-secondary/60 px-2.5 py-1 text-xs font-medium text-foreground outline-none focus:border-ring"
              >
                {SORT_OPTIONS.map((opt) => (
                  <option key={opt} value={opt}>
                    Ordem: {opt}
                  </option>
                ))}
              </select>

              <button
                type="button"
                onClick={() => {
                  clearPhotos();
                  toast.info("Fotos removidas deste workspace.");
                }}
                className="inline-flex items-center gap-1 rounded-lg border border-nc/30 bg-nc-soft px-2.5 py-1 text-xs font-medium text-nc hover:bg-nc hover:text-destructive-foreground transition"
              >
                <Trash2 className="h-3.5 w-3.5" />
                Limpar Fotos
              </button>
            </div>
          </div>

          <div className="mt-2 flex gap-3 overflow-x-auto pb-2">
            {ws.photos.map((f, i) => {
              const isSelected = i === ws.carouselIndex;
              const inNc = fotosEmNc.has(f.name.trim().toLowerCase());
              return (
                <div
                  key={f.id}
                  onClick={() => setCarouselIndex(i)}
                  className={`group relative w-36 shrink-0 cursor-pointer overflow-hidden rounded-xl border bg-card transition ${
                    isSelected
                      ? "border-accent ring-2 ring-accent/25"
                      : "border-border hover:border-accent/50"
                  }`}
                >
                  <img
                    src={f.previewUrl}
                    alt={f.name}
                    className="h-24 w-full object-cover"
                  />
                  {inNc && (
                    <span className="absolute left-1.5 top-1.5 inline-flex items-center gap-0.5 rounded-md bg-ok px-1.5 py-0.5 text-[10px] font-bold text-white shadow">
                      <CheckCircle2 className="h-3 w-3" /> NC
                    </span>
                  )}
                  <div className="p-2 text-[11px]">
                    <div className="flex items-center justify-between font-semibold">
                      <span>Foto {String(i + 1).padStart(2, "0")}</span>
                    </div>
                    <div
                      className="truncate text-muted-foreground"
                      title={f.name}
                    >
                      {f.name}
                    </div>
                  </div>
                  <button
                    type="button"
                    aria-label="Excluir foto"
                    onClick={(e) => {
                      e.stopPropagation();
                      removePhoto(f.id);
                    }}
                    className="absolute right-1.5 top-1.5 rounded-md bg-card/90 p-1 text-nc opacity-0 group-hover:opacity-100 transition"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              );
            })}
          </div>
        </>
      )}
    </Card>
  );
};
