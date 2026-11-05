import React, { useState } from "react";
import {
  Rocket,
  Trash2,
  Sparkles,
  Wand2,
  Download,
  CheckCircle2,
  FileSpreadsheet,
  Loader2,
  AlertTriangle,
  ChevronRight,
} from "lucide-react";
import { toast } from "sonner";
import { Card } from "./Card";
import { ConfirmDeleteModal } from "./Modals";
import { useReportStore } from "../store/useReportStore";
import {
  downloadPlanilhaExcelApi,
  gerarRelatoriosApi,
} from "../services/api";
import { RelatorioGeradoItem } from "../types/report.types";

interface SummaryAndActionsPanelProps {
  onOpenEditModal?: (tab?: "fisc" | "nc") => void;
}

const btn = {
  primary:
    "inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 px-5 py-2.5 text-sm font-bold text-white shadow-md shadow-amber-500/25 transition-all duration-150 hover:brightness-105 hover:shadow-lg hover:shadow-amber-500/35 active:translate-y-[1px] disabled:opacity-40 disabled:pointer-events-none",
  secondary:
    "inline-flex items-center justify-center gap-2 rounded-xl border border-border bg-card px-4 py-2.5 text-sm font-medium text-foreground hover:bg-muted hover:border-primary/40 transition-all duration-200 active:translate-y-[1px] disabled:opacity-40 disabled:pointer-events-none",
  danger:
    "inline-flex items-center justify-center gap-2 rounded-xl border border-nc/30 bg-nc-soft px-4 py-2.5 text-sm font-semibold text-nc transition-all duration-200 hover:bg-nc hover:text-white active:translate-y-[1px] disabled:opacity-40 disabled:pointer-events-none",
};

function downloadBase64Docx(item: RelatorioGeradoItem) {
  const byteChars = atob(item.base64);
  const byteNumbers = new Array(byteChars.length);
  for (let i = 0; i < byteChars.length; i++) {
    byteNumbers[i] = byteChars.charCodeAt(i);
  }
  const blob = new Blob([new Uint8Array(byteNumbers)], {
    type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = item.nome;
  document.body.appendChild(a);
  a.click();
  URL.revokeObjectURL(url);
  document.body.removeChild(a);
}

export const SummaryAndActionsPanel: React.FC<SummaryAndActionsPanelProps> = () => {
  const {
    tipoRelatorio,
    categoriaRelatorio,
    compressImages,
    responsaveis,
    coordenadores,
    mapSiglas,
    getActiveWorkspace,
    executarAutoPreenchimento,
    limparRegistrosAtuais,
    setRelatoriosGerados,
  } = useReportStore();

  const ws = getActiveWorkspace();
  const regs = ws.registrosNc;
  const fotos = ws.photos;
  const isMonitoring = categoriaRelatorio === "Monitoramento";

  const [confirmClearAll, setConfirmClearAll] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [downloadingExcel, setDownloadingExcel] = useState(false);
  const [avisos, setAvisos] = useState<string[]>([]);

  const executeConfirmedDelete = () => {
    limparRegistrosAtuais(false);
    setAvisos([]);
    toast.success("Todos os registros de ocorrências foram limpos.");
    setConfirmClearAll(false);
  };

  const handleGerar = async () => {
    if (!regs.length) return;

    if (
      tipoRelatorio === "CRC" &&
      isMonitoring &&
      !ws.documentoAnteriorFile
    ) {
      toast.error(
        "Para CRC Monitoramento, envie primeiro o Relatório Anterior (.docx) no Bloco 01."
      );
      return;
    }

    setGenerating(true);
    setAvisos([]);
    try {
      const res = await gerarRelatoriosApi({
        tipo_relatorio: tipoRelatorio,
        categoria_relatorio: categoriaRelatorio,
        fiscalizacoes: ws.fiscalizacoes,
        registros_nc: regs,
        photos: fotos,
        oldItems: ws.oldPhotosToMatch,
        documentoAnteriorFile: ws.documentoAnteriorFile,
        planilhaElegibilidadeFile: ws.planilhaElegibilidadeFile,
        customSiglasMap: mapSiglas,
        responsaveis,
        coordenadores,
        compressImages,
      });
      setRelatoriosGerados(res.relatorios || []);
      setAvisos(res.avisos || []);
      toast.success("Relatório (.docx) compilado com sucesso!");
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Falha ao gerar o relatório.";
      toast.error(msg);
    } finally {
      setGenerating(false);
    }
  };

  const handleExcel = async () => {
    if (!regs.length) return;
    setDownloadingExcel(true);
    try {
      const blob = await downloadPlanilhaExcelApi(ws.fiscalizacoes, regs);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `Planilha_${tipoRelatorio}_${categoriaRelatorio}.xlsx`;
      document.body.appendChild(a);
      a.click();
      URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success("Planilha (.xlsx) exportada!");
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Erro ao exportar planilha.";
      toast.error(msg);
    } finally {
      setDownloadingExcel(false);
    }
  };

  return (
    <>
      <Card
        n={4}
        icon={<Rocket className="h-5 w-5" />}
        title="Emissão e Exportação"
      >
        <p className="text-sm text-muted-foreground">
          O relatório reúne fotos, ocorrências e determinações no padrão ARPE de{" "}
          {categoriaRelatorio.toLowerCase()} ({tipoRelatorio}).
        </p>

        <div className="mt-5 flex flex-wrap items-center gap-3">
          <button
            type="button"
            className="inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-amber-500 via-amber-600 to-amber-700 px-5 py-2.5 text-sm font-bold text-white shadow-md shadow-amber-500/25 transition-all duration-150 hover:brightness-105 hover:shadow-lg hover:shadow-amber-500/35 active:translate-y-[1px] disabled:opacity-40 disabled:pointer-events-none"
            disabled={!regs.length || generating}
            onClick={handleGerar}
          >
            {generating ? (
              <Loader2 className="h-4 w-4 animate-spin text-white" />
            ) : (
              <Sparkles className="h-4 w-4 text-amber-100" />
            )}
            <span>{generating ? "Gerando..." : "Gerar Relatório (.docx)"}</span>
          </button>

          <button
            type="button"
            className={btn.secondary}
            disabled={!regs.length || downloadingExcel}
            onClick={handleExcel}
          >
            {downloadingExcel ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <FileSpreadsheet className="h-4 w-4" />
            )}
            Planilha (.xlsx)
          </button>

          <button
            type="button"
            className={btn.secondary}
            onClick={() => {
              executarAutoPreenchimento();
              toast.success("Auto preenchimento aplicado ao workspace atual!");
            }}
          >
            <Wand2 className="h-4 w-4" /> Auto Preenchimento
          </button>

          <button
            type="button"
            className={btn.danger}
            disabled={!regs.length}
            onClick={() => setConfirmClearAll(true)}
          >
            <Trash2 className="h-4 w-4" /> Limpar Todos os Registros
          </button>
        </div>

        {!regs.length && (
          <p className="mt-2 text-xs text-muted-foreground">
            Adicione ao menos um registro no bloco 3 (ou use Auto Preenchimento)
            para gerar o relatório.
          </p>
        )}

        {ws.relatoriosGerados.length > 0 && (
          <div className="mt-6 space-y-3">
            {ws.relatoriosGerados.map((rel) => (
              <div
                key={rel.nome}
                className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-emerald-200/90 bg-emerald-50/80 p-4 shadow-sm"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-white border border-emerald-200 text-emerald-600 shadow-xs">
                    <CheckCircle2 className="h-5 w-5 stroke-[2.5]" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="text-sm font-bold text-slate-900">Relatório Compilado com Sucesso</div>
                    <div className="font-mono text-xs text-slate-600 truncate">
                      {rel.nome}
                    </div>
                  </div>
                </div>

                <button
                  type="button"
                  className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 px-4 py-2 text-xs sm:text-sm font-bold text-white shadow-md shadow-amber-500/25 transition-all duration-150 hover:brightness-105 hover:shadow-lg hover:shadow-amber-500/35 active:translate-y-[1px]"
                  onClick={() => downloadBase64Docx(rel)}
                >
                  <Download className="h-4 w-4 stroke-[2.5]" />
                  <span>Baixar (.docx)</span>
                </button>
              </div>
            ))}
          </div>
        )}

        {avisos.length > 0 && (
          <div className="mt-4 rounded-xl border border-pa/30 bg-pa-soft p-4 text-xs text-pa">
            <div className="flex items-center gap-2 font-semibold">
              <AlertTriangle className="h-4 w-4" /> Avisos da geração:
            </div>
            <ul className="mt-1 list-disc pl-5 text-foreground">
              {avisos.map((av, idx) => (
                <li key={idx}>{av}</li>
              ))}
            </ul>
          </div>
        )}
      </Card>

      {confirmClearAll && (
        <ConfirmDeleteModal
          title="Limpar Todos os Registros"
          description="Deseja realmente remover todas as ocorrências registradas nesta modalidade? (As fotos enviadas e o cabeçalho serão mantidos)."
          itemsPreview={[`${regs.length} registro(s) de ocorrências em ${tipoRelatorio} · ${categoriaRelatorio}`]}
          onConfirm={executeConfirmedDelete}
          onClose={() => setConfirmClearAll(false)}
        />
      )}
    </>
  );
};
