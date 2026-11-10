import React, { useMemo, useState } from "react";
import {
  Rocket,
  Trash2,
  Sparkles,
  Wand2,
  Download,
  CheckCircle2,
  Files,
  Loader2,
  AlertTriangle,
  ChevronRight,
  RotateCcw,
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
    "inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-amber-500 via-amber-600 to-amber-700 px-5 py-2.5 text-sm font-bold text-white shadow-md shadow-amber-500/20 transition-all duration-150 hover:brightness-105 hover:shadow-lg hover:shadow-amber-500/30 active:scale-[0.98] disabled:opacity-40 disabled:pointer-events-none",
  secondary:
    "inline-flex items-center justify-center gap-2 rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-xs font-semibold text-slate-700 shadow-xs transition-all duration-150 hover:bg-slate-50 hover:text-slate-900 hover:border-slate-400 active:scale-[0.98] disabled:opacity-40 disabled:pointer-events-none",
  danger:
    "inline-flex items-center justify-center gap-2 rounded-xl border border-rose-300 bg-rose-50 px-4 py-2.5 text-xs font-bold text-rose-700 shadow-xs transition-all duration-150 hover:bg-rose-100 hover:border-rose-400 active:scale-[0.98] disabled:opacity-40 disabled:pointer-events-none",
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
    getAllPhotosForBatch,
    executarAutoPreenchimento,
    reiniciarModalidadeAtual,
    setRelatoriosGerados,
  } = useReportStore();

  const ws = getActiveWorkspace();
  const isMonitoring = categoriaRelatorio === "Monitoramento";

  const activeFiscIdx = Math.max(
    0,
    Math.min(ws.activeFiscalizacaoIndex, Math.max(0, ws.fiscalizacoes.length - 1))
  );
  const activeFisc = ws.fiscalizacoes[activeFiscIdx];
  const activeFiscId = (activeFisc?.["ID da Fiscalização"] || "").trim();

  // Ocorrências vinculadas estritamente à fiscalização ativa atual
  const activeRegs = useMemo(() => {
    if (!activeFiscId) return [];
    return ws.registrosNc.filter(
      (r) => (r["ID da Fiscalização"] || "").trim() === activeFiscId
    );
  }, [ws.registrosNc, activeFiscId]);

  // Fiscalizações que possuem ao menos 1 registro de ocorrência cadastrado
  const fiscalizacoesValidas = useMemo(() => {
    return ws.fiscalizacoes.filter((f) => {
      const id = (f["ID da Fiscalização"] || "").trim();
      if (!id) return false;
      return ws.registrosNc.some(
        (r) => (r["ID da Fiscalização"] || "").trim() === id
      );
    });
  }, [ws.fiscalizacoes, ws.registrosNc]);

  const countRelatoriosValidos = fiscalizacoesValidas.length;

  const [confirmReset, setConfirmReset] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [generatingBatch, setGeneratingBatch] = useState(false);
  const [avisos, setAvisos] = useState<string[]>([]);

  const handleGerarIndividual = async () => {
    if (!activeRegs.length || !activeFisc) return;

    if (
      tipoRelatorio === "CRC" &&
      isMonitoring &&
      !ws.documentoAnteriorFile
    ) {
      toast.error(
        "Para CRC Monitoramento, envie primeiro o Relatório Anterior (.docx) no Bloco 02."
      );
      return;
    }

    setGenerating(true);
    setGeneratingBatch(false);
    setAvisos([]);
    try {
      const res = await gerarRelatoriosApi({
        tipo_relatorio: tipoRelatorio,
        categoria_relatorio: categoriaRelatorio,
        fiscalizacoes: [activeFisc],
        registros_nc: activeRegs,
        photos: ws.photos,
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
      toast.success(`Relatório (${activeFisc["ID da Fiscalização"]}) gerado com sucesso!`);
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Falha ao gerar o relatório.";
      toast.error(msg);
    } finally {
      setGenerating(false);
    }
  };

  const handleGerarLote = async () => {
    if (countRelatoriosValidos === 0) return;

    if (
      tipoRelatorio === "CRC" &&
      isMonitoring &&
      !ws.documentoAnteriorFile
    ) {
      toast.error(
        "Para CRC Monitoramento, envie primeiro o Relatório Anterior (.docx) no Bloco 02."
      );
      return;
    }

    setGenerating(true);
    setGeneratingBatch(true);
    setAvisos([]);
    try {
      const validIds = new Set(
        fiscalizacoesValidas.map((f) => (f["ID da Fiscalização"] || "").trim())
      );
      const loteRegs = ws.registrosNc.filter((r) =>
        validIds.has((r["ID da Fiscalização"] || "").trim())
      );
      const allBatchPhotos = getAllPhotosForBatch();

      const res = await gerarRelatoriosApi({
        tipo_relatorio: tipoRelatorio,
        categoria_relatorio: categoriaRelatorio,
        fiscalizacoes: fiscalizacoesValidas,
        registros_nc: loteRegs,
        photos: allBatchPhotos,
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
      toast.success(
        `${res.relatorios?.length || countRelatoriosValidos} relatório(s) gerado(s) em lote com sucesso!`
      );
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Falha ao gerar relatórios em lote.";
      toast.error(msg);
    } finally {
      setGenerating(false);
      setGeneratingBatch(false);
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
            className={btn.primary}
            disabled={!activeRegs.length || generating}
            onClick={handleGerarIndividual}
            title={
              !activeRegs.length
                ? "Adicione ocorrências nesta fiscalização para habilitar a emissão"
                : `Gerar apenas o relatório ${activeFiscId}`
            }
          >
            {generating && !generatingBatch ? (
              <Loader2 className="h-4 w-4 animate-spin text-white" />
            ) : (
              <Sparkles className="h-4 w-4 text-amber-100" />
            )}
            <span>
              {generating && !generatingBatch
                ? "Gerando..."
                : `Gerar Relatório (${activeFiscId || "1"})`}
            </span>
          </button>

          <button
            type="button"
            className={btn.secondary}
            disabled={countRelatoriosValidos === 0 || generating}
            onClick={handleGerarLote}
            title={
              countRelatoriosValidos === 0
                ? "Nenhum relatório possui registros de ocorrências para emissão em lote"
                : `Gerar todos os ${countRelatoriosValidos} relatórios que possuem registros cadastrados`
            }
          >
            {generating && generatingBatch ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Files className="h-4 w-4" />
            )}
            <span>
              {generating && generatingBatch
                ? "Gerando Lote..."
                : `Gerar Relatórios (${countRelatoriosValidos})`}
            </span>
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
            disabled={!ws.fiscalizacoes.length && !ws.registrosNc.length && !ws.photos.length}
            onClick={() => setConfirmReset(true)}
            title={`Reiniciar completamente este relatório (${tipoRelatorio} · ${categoriaRelatorio})`}
          >
            <RotateCcw className="h-4 w-4" /> Reiniciar Relatório
          </button>
        </div>

        {!activeRegs.length && (
          <p className="mt-2 text-xs text-muted-foreground">
            Adicione ao menos uma ocorrência nesta fiscalização no bloco 3 para liberar a geração do documento.
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
                  className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-amber-500 to-amber-600 px-4 py-2 text-xs sm:text-sm font-bold text-white shadow-md shadow-amber-500/25 transition-all duration-150 hover:brightness-105 hover:shadow-lg hover:shadow-amber-500/35 active:scale-[0.98]"
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

      {confirmReset && (() => {
        const totalRelatorios = ws.fiscalizacoes.length;
        const totalRegistros = ws.registrosNc.length;
        const totalFotos =
          ws.photos.length +
          Object.values(ws.photosByFiscalizacao || {}).reduce(
            (acc, list) => acc + (list?.length || 0),
            0
          );

        return (
          <ConfirmDeleteModal
            title={`Reiniciar Relatório (${tipoRelatorio} · ${categoriaRelatorio})`}
            description={`Atenção: Esta ação reiniciará completamente o estado deste tipo de relatório (${tipoRelatorio} · ${categoriaRelatorio}). Todos os dados serão apagados: ${totalRelatorios} relatório(s)/cabeçalho(s), ${totalRegistros} ocorrência(s) e fotos vinculadas. Deseja continuar?`}
            itemsPreview={[
              `Modalidade: ${tipoRelatorio} · ${categoriaRelatorio}`,
              `Relatórios / Cabeçalhos cadastrados: ${totalRelatorios}${ws.fiscalizacoes.length > 0 ? ` (${ws.fiscalizacoes.map((f) => f["ID da Fiscalização"] || "Sem ID").join(", ")})` : ""}`,
              `Total de ocorrências feitas: ${totalRegistros} registro(s)`,
              `Total de fotos vinculadas: ${totalFotos} foto(s)`,
            ]}
            onConfirm={() => {
              reiniciarModalidadeAtual();
              setAvisos([]);
              setConfirmReset(false);
              toast.success(
                `Relatório de ${tipoRelatorio} · ${categoriaRelatorio} foi reiniciado com sucesso.`
              );
            }}
            onClose={() => setConfirmReset(false)}
          />
        );
      })()}
    </>
  );
};
