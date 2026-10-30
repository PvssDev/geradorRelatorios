import React, { useMemo, useState } from "react";
import {
  Table2,
  Rocket,
  Trash2,
  Sparkles,
  Wand2,
  Download,
  CheckCircle2,
  FileSpreadsheet,
  Loader2,
  Edit3,
  AlertTriangle,
  Link2,
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
  onOpenEditModal: (tab?: "fisc" | "nc") => void;
}

const btn = {
  primary:
    "inline-flex items-center justify-center gap-2 rounded-xl bg-amber-500 px-5 py-2.5 text-sm font-bold text-stone-950 shadow-[0_3px_0_0_#b45309] transition-all duration-150 hover:bg-amber-400 active:translate-y-[2px] active:shadow-[0_1px_0_0_#b45309] disabled:opacity-40 disabled:pointer-events-none",
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

export const SummaryAndActionsPanel: React.FC<SummaryAndActionsPanelProps> = ({
  onOpenEditModal,
}) => {
  const {
    tipoRelatorio,
    categoriaRelatorio,
    compressImages,
    responsaveis,
    coordenadores,
    mapSiglas,
    getActiveWorkspace,
    deleteFiscalizacoesBulk,
    deleteRegistrosNcBulk,
    executarAutoPreenchimento,
    limparRegistrosAtuais,
    setRelatoriosGerados,
  } = useReportStore();

  const ws = getActiveWorkspace();
  const fiscs = ws.fiscalizacoes;
  const regs = ws.registrosNc;
  const fotos = ws.photos;
  const isMonitoring = categoriaRelatorio === "Monitoramento";

  const [selFisc, setSelFisc] = useState<string[]>([]);
  const [selNc, setSelNc] = useState<string[]>([]);
  const [confirmMode, setConfirmMode] = useState<
    "fisc" | "nc" | "clear_all" | null
  >(null);
  const [generating, setGenerating] = useState(false);
  const [downloadingExcel, setDownloadingExcel] = useState(false);
  const [avisos, setAvisos] = useState<string[]>([]);

  // Contabiliza apenas ocorrências-base (não conta a 2ª foto relacionada como nova NC)
  const baseRegs = useMemo(
    () => regs.filter((r) => !r.is_relacionado),
    [regs]
  );

  const kpis = useMemo(() => {
    if (isMonitoring) {
      const sanadas = baseRegs.filter((r) => r.Situação === "Sanada").length;
      const pendentes = baseRegs.length - sanadas;
      return [
        ["Ocorrências Auditadas", baseRegs.length, "bg-secondary text-slate-blue"],
        ["Pendentes / Parc. Sanadas", pendentes, "bg-nc-soft text-nc"],
        ["Sanadas", sanadas, "bg-ok-soft text-ok"],
      ] as const;
    }
    if (tipoRelatorio === "CRA") {
      const ncCount = baseRegs.filter(
        (r) => (r["Não Conformidade"] || "").trim() !== ""
      ).length;
      const paCount = baseRegs.length - ncCount;
      return [
        ["Total de Achados", baseRegs.length, "bg-secondary text-slate-blue"],
        ["Não Conformidades (NC)", ncCount, "bg-nc-soft text-nc"],
        ["Pontos de Atenção (PA)", paCount, "bg-pa-soft text-pa"],
      ] as const;
    }
    const relPhotosCount = regs.filter((r) => Boolean(r.Foto)).length;
    return [
      ["Total de Ocorrências", baseRegs.length, "bg-secondary text-slate-blue"],
      ["Não Conformidades (NC)", baseRegs.length, "bg-nc-soft text-nc"],
      ["Registros Fotográficos", relPhotosCount, "bg-pa-soft text-pa"],
    ] as const;
  }, [isMonitoring, tipoRelatorio, baseRegs, regs]);

  const executeConfirmedDelete = () => {
    if (confirmMode === "fisc") {
      deleteFiscalizacoesBulk(selFisc);
      setSelFisc([]);
      toast.success("Cabeçalhos selecionados excluídos!");
    } else if (confirmMode === "nc") {
      const keys = selNc.map((k) => {
        const [idFiscalizacao, numStr] = k.split("__");
        return { idFiscalizacao, numero: Number(numStr) };
      });
      deleteRegistrosNcBulk(keys);
      setSelNc([]);
      toast.success("Registros selecionados excluídos!");
    } else if (confirmMode === "clear_all") {
      limparRegistrosAtuais(false);
      setSelNc([]);
      setAvisos([]);
      toast.success("Todos os registros de ocorrências foram limpos.");
    }
    setConfirmMode(null);
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

  const allNcKeys = regs.map((r) => `${r["ID da Fiscalização"]}__${r["Nº"]}`);
  const allNcSelected =
    allNcKeys.length > 0 && allNcKeys.every((k) => selNc.includes(k));

  const ncHeaders = isMonitoring
    ? [
        "Nº",
        "Foto",
        "Codificação / NC",
        tipoRelatorio === "SOCICAM" ? "Terminal" : "Pista / Trecho",
        "Situação",
        tipoRelatorio === "SOCICAM"
          ? "Informação SOCICAM"
          : `Posicionamento ${tipoRelatorio}`,
        "Constatação",
        "Análise ARPE",
        "Ações",
      ]
    : tipoRelatorio === "SOCICAM"
    ? [
        "Nº",
        "Foto",
        "Terminal",
        "Irregularidade",
        "Codificação",
        "Observações (Legenda)",
        "Determinação",
        "Ações",
      ]
    : tipoRelatorio === "CRC"
    ? [
        "Nº",
        "Foto",
        "Codificação",
        "Pista",
        "Trecho",
        "Patologia",
        "Observações (Legenda)",
        "Ações",
      ]
    : [
        "Nº",
        "Foto",
        "Tipo",
        "Pista",
        "Trecho",
        "Direção / Faixa",
        "Codificação",
        "Patologia / Obs.",
        "Ações",
      ];

  return (
    <>
      <Card
        n={4}
        icon={<Table2 className="h-5 w-5" />}
        title="Registros Cadastrados para o Relatório"
      >
        {/* KPIs por Modalidade */}
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          {kpis.map(([l, v, c]) => (
            <div key={String(l)} className={`rounded-xl p-4 ${c}`}>
              <div className="text-xs font-medium">{l}</div>
              <div className="text-2xl font-bold">{v}</div>
            </div>
          ))}
        </div>

        {/* Tabela Compacta de Cabeçalhos (Fiscalizações / Monitoramentos) */}
        {fiscs.length > 0 && (
          <div className="mt-5">
            <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
              <span className="text-xs font-semibold uppercase tracking-wide text-slate-blue">
                {isMonitoring
                  ? `Cabeçalhos de Monitoramento (${fiscs.length})`
                  : `Cabeçalhos de Fiscalização (${fiscs.length})`}
              </span>
              <div className="flex items-center gap-2">
                {selFisc.length > 0 && (
                  <button
                    type="button"
                    onClick={() => setConfirmMode("fisc")}
                    className="inline-flex items-center gap-1 rounded-lg border border-nc/30 bg-nc-soft px-2.5 py-1 text-xs font-semibold text-nc hover:bg-nc hover:text-destructive-foreground transition"
                  >
                    <Trash2 className="h-3.5 w-3.5" /> Excluir IDs (
                    {selFisc.length})
                  </button>
                )}
                <button
                  type="button"
                  onClick={() => onOpenEditModal("fisc")}
                  className="inline-flex items-center gap-1 rounded-lg border border-border bg-card px-2.5 py-1 text-xs font-medium hover:bg-muted transition"
                >
                  <Edit3 className="h-3.5 w-3.5" /> Editar Cabeçalhos
                </button>
              </div>
            </div>

            <div className="overflow-x-auto rounded-xl border border-border">
              <table className="w-full text-left text-xs">
                <thead className="bg-muted text-muted-foreground">
                  <tr>
                    <th className="w-8 px-3 py-2">
                      <input
                        type="checkbox"
                        checked={
                          fiscs.length > 0 &&
                          fiscs.every((f) =>
                            selFisc.includes(f["ID da Fiscalização"])
                          )
                        }
                        onChange={(e) =>
                          setSelFisc(
                            e.target.checked
                              ? fiscs.map((f) => f["ID da Fiscalização"])
                              : []
                          )
                        }
                      />
                    </th>
                    <th className="px-3 py-2 font-semibold">ID</th>
                    <th className="px-3 py-2 font-semibold">Data / Período</th>
                    <th className="px-3 py-2 font-semibold">Local</th>
                    <th className="px-3 py-2 font-semibold">Contrato</th>
                    <th className="px-3 py-2 font-semibold">Coordenador(a)</th>
                  </tr>
                </thead>
                <tbody>
                  {fiscs.map((f, idx) => {
                    const fId = f["ID da Fiscalização"];
                    return (
                      <tr
                        key={`${fId}_${idx}`}
                        className="border-t border-border"
                      >
                        <td className="px-3 py-2">
                          <input
                            type="checkbox"
                            checked={selFisc.includes(fId)}
                            onChange={() =>
                              setSelFisc((prev) =>
                                prev.includes(fId)
                                  ? prev.filter((x) => x !== fId)
                                  : [...prev, fId]
                              )
                            }
                          />
                        </td>
                        <td className="px-3 py-2 font-mono font-semibold text-foreground">
                          {fId || "—"}
                        </td>
                        <td className="px-3 py-2">
                          {f.Data}
                          {f.Período && f.Período !== f.Data
                            ? ` (${f.Período})`
                            : ""}
                        </td>
                        <td className="px-3 py-2">{f.Local || "—"}</td>
                        <td className="px-3 py-2 font-mono">
                          {f.Contrato || "—"}
                        </td>
                        <td className="px-3 py-2">{f.Coordenador || "—"}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Tabela Principal de Ocorrências / Auditorias */}
        <div className="mt-5 overflow-x-auto rounded-xl border border-border">
          <table className="w-full text-left text-xs">
            <thead className="bg-muted text-muted-foreground">
              <tr>
                <th className="w-8 px-3 py-2">
                  <input
                    type="checkbox"
                    checked={allNcSelected}
                    onChange={(e) =>
                      setSelNc(e.target.checked ? allNcKeys : [])
                    }
                  />
                </th>
                {ncHeaders.map((h, idx) => (
                  <th key={`${h}_${idx}`} className="px-3 py-2 font-semibold">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {regs.length === 0 && (
                <tr>
                  <td
                    colSpan={ncHeaders.length + 1}
                    className="px-3 py-8 text-center text-muted-foreground"
                  >
                    Nenhum registro adicionado ainda.
                  </td>
                </tr>
              )}
              {regs.map((r, i) => {
                const rowKey = `${r["ID da Fiscalização"]}__${r["Nº"]}`;
                const fi = fotos.findIndex((f) => f.name === r.Foto);
                const isNc = Boolean((r["Não Conformidade"] || "").trim());
                const sit = r.Situação || "Pendente";

                return (
                  <tr
                    key={rowKey}
                    className={`border-t border-border ${
                      r.is_relacionado ? "bg-secondary/30" : ""
                    }`}
                  >
                    <td className="px-3 py-2">
                      <input
                        type="checkbox"
                        checked={selNc.includes(rowKey)}
                        onChange={() =>
                          setSelNc((s) =>
                            s.includes(rowKey)
                              ? s.filter((x) => x !== rowKey)
                              : [...s, rowKey]
                          )
                        }
                      />
                    </td>
                    <td className="px-3 py-2 font-semibold">
                      <div className="flex items-center gap-1">
                        <span>{r["Nº"] || i + 1}</span>
                        {r.is_relacionado && (
                          <span
                            className="inline-flex items-center gap-0.5 rounded bg-accent/15 px-1.5 py-0.5 text-[10px] font-bold text-accent"
                            title="2ª foto relacionada à ocorrência anterior"
                          >
                            <Link2 className="h-2.5 w-2.5" /> 2ª
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-3 py-2">
                      {fi >= 0 ? (
                        <img
                          src={fotos[fi].previewUrl}
                          alt={r.Foto}
                          title={r.Foto}
                          className="h-8 w-10 rounded object-cover"
                        />
                      ) : (
                        <span className="font-mono text-[10px] text-muted-foreground">
                          {r.Foto || "—"}
                        </span>
                      )}
                    </td>

                    {isMonitoring ? (
                      <>
                        <td className="px-3 py-2 font-mono">
                          {r.Identificação || "—"}
                        </td>
                        <td className="px-3 py-2">
                          {tipoRelatorio === "SOCICAM"
                            ? r.Terminal || "—"
                            : [r.Pista, r.Trecho].filter(Boolean).join(" · ") ||
                              "—"}
                        </td>
                        <td className="px-3 py-2">
                          <span
                            className={`rounded-full px-2 py-0.5 font-semibold ${
                              sit === "Sanada"
                                ? "bg-ok-soft text-ok"
                                : sit === "Parcialmente Sanada"
                                ? "bg-pa-soft text-pa"
                                : "bg-nc-soft text-nc"
                            }`}
                          >
                            {sit}
                          </span>
                        </td>
                        <td
                          className="max-w-[160px] truncate px-3 py-2"
                          title={r.Determinação}
                        >
                          {r.Determinação || "—"}
                        </td>
                        <td
                          className="max-w-[160px] truncate px-3 py-2"
                          title={r.Observações}
                        >
                          {r.Observações || "—"}
                        </td>
                        <td
                          className="max-w-[160px] truncate px-3 py-2"
                          title={r["Análise ARPE"]}
                        >
                          {r["Análise ARPE"] || "—"}
                        </td>
                      </>
                    ) : tipoRelatorio === "SOCICAM" ? (
                      <>
                        <td className="px-3 py-2">{r.Terminal || "—"}</td>
                        <td className="px-3 py-2 font-semibold">
                          {r["Não Conformidade"] || "—"}
                        </td>
                        <td className="px-3 py-2 font-mono">
                          {r.Identificação || "—"}
                        </td>
                        <td
                          className="max-w-[200px] truncate px-3 py-2"
                          title={r.Observações}
                        >
                          {r.Observações || "—"}
                        </td>
                        <td
                          className="max-w-[160px] truncate px-3 py-2"
                          title={r.Determinação}
                        >
                          {r.Determinação || "—"}
                        </td>
                      </>
                    ) : tipoRelatorio === "CRC" ? (
                      <>
                        <td className="px-3 py-2 font-mono">
                          {r.Identificação || "—"}
                        </td>
                        <td className="px-3 py-2">{r.Pista || "—"}</td>
                        <td className="px-3 py-2">{r.Trecho || "—"}</td>
                        <td className="px-3 py-2 font-semibold">
                          {r["Não Conformidade"] || "—"}
                        </td>
                        <td
                          className="max-w-[200px] truncate px-3 py-2"
                          title={r.Observações}
                        >
                          {r.Observações || "—"}
                        </td>
                      </>
                    ) : (
                      /* CRA Fiscalização */
                      <>
                        <td className="px-3 py-2">
                          <span
                            className={`rounded-full px-2 py-0.5 font-semibold ${
                              isNc
                                ? "bg-nc-soft text-nc"
                                : "bg-pa-soft text-pa"
                            }`}
                          >
                            {isNc ? "NC" : "PA"}
                          </span>
                        </td>
                        <td className="px-3 py-2">{r.Pista || "—"}</td>
                        <td className="px-3 py-2">{r.Trecho || "—"}</td>
                        <td className="px-3 py-2 font-medium">
                          {r["Direção (faixa)"] || "—"}
                        </td>
                        <td className="px-3 py-2 font-mono">
                          {r.Identificação || "—"}
                        </td>
                        <td
                          className="max-w-[180px] truncate px-3 py-2"
                          title={`${
                            r["Não Conformidade"] || r["Ponto de Atenção"]
                          } — ${r.Observações}`}
                        >
                          <span className="font-semibold">
                            {r["Não Conformidade"] ||
                              r["Ponto de Atenção"] ||
                              "—"}
                          </span>
                          {r.Observações ? ` · ${r.Observações}` : ""}
                        </td>
                      </>
                    )}

                    <td className="px-3 py-2">
                      <button
                        type="button"
                        aria-label="Excluir"
                        className="text-nc hover:opacity-75"
                        onClick={() =>
                          deleteRegistrosNcBulk([
                            {
                              idFiscalizacao: r["ID da Fiscalização"],
                              numero: r["Nº"],
                            },
                          ])
                        }
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        <div className="mt-3 flex flex-wrap items-center gap-3">
          <button
            type="button"
            className={btn.danger}
            disabled={!selNc.length}
            onClick={() => setConfirmMode("nc")}
          >
            <Trash2 className="h-4 w-4" /> Excluir Selecionadas ({selNc.length})
          </button>

          {(regs.length > 0 || fiscs.length > 0) && (
            <button
              type="button"
              className={btn.secondary}
              onClick={() => onOpenEditModal("nc")}
            >
              <Edit3 className="h-4 w-4" /> Editar Registros
            </button>
          )}
        </div>
      </Card>

      <Card
        n={5}
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
            className="group relative inline-flex items-center justify-between gap-4 overflow-hidden rounded-2xl bg-gradient-to-r from-amber-500 via-amber-600 to-amber-700 px-6 py-3.5 text-sm font-bold text-white shadow-lg shadow-amber-500/25 transition-all duration-200 hover:brightness-105 hover:shadow-xl hover:shadow-amber-500/40 active:translate-y-[2px] active:scale-[0.99] disabled:opacity-40 disabled:pointer-events-none"
            disabled={!regs.length || generating}
            onClick={handleGerar}
          >
            <div className="flex items-center gap-2.5">
              {generating ? (
                <Loader2 className="h-5 w-5 animate-spin text-white" />
              ) : (
                <Sparkles className="h-5 w-5 text-amber-100" />
              )}
              <span>{generating ? "Gerando Relatório..." : "Gerar Relatório (.docx)"}</span>
            </div>
            <span className="flex h-7 w-7 items-center justify-center rounded-full bg-black/25 text-white backdrop-blur-sm transition-transform duration-200 group-hover:translate-x-0.5">
              <ChevronRight className="h-4 w-4 stroke-[2.5]" />
            </span>
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
            onClick={() => setConfirmMode("clear_all")}
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
                className="flex flex-wrap items-center gap-4 rounded-xl border border-ok/40 bg-ok-soft p-4"
              >
                <CheckCircle2 className="h-6 w-6 text-ok" />
                <div className="flex-1">
                  <div className="text-sm font-semibold">Relatório pronto</div>
                  <div className="font-mono text-xs text-muted-foreground">
                    {rel.nome}
                  </div>
                </div>
                <button
                  type="button"
                  className={btn.primary}
                  onClick={() => downloadBase64Docx(rel)}
                >
                  <Download className="h-4 w-4" /> Baixar
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

      {confirmMode && (
        <ConfirmDeleteModal
          title={
            confirmMode === "fisc"
              ? "Excluir Cabeçalhos Selecionados"
              : confirmMode === "nc"
              ? "Excluir Ocorrências Selecionadas"
              : "Limpar Todos os Registros"
          }
          description={
            confirmMode === "fisc"
              ? "Os cabeçalhos abaixo e todas as ocorrências vinculadas a eles serão removidos:"
              : confirmMode === "nc"
              ? "Confirma a exclusão das ocorrências selecionadas e renumeração sequencial?"
              : "Deseja realmente remover todas as ocorrências registradas nesta modalidade? (As fotos enviadas e o cabeçalho serão mantidos)."
          }
          itemsPreview={
            confirmMode === "fisc"
              ? selFisc
              : confirmMode === "nc"
              ? selNc.map((k) => {
                  const [idF, n] = k.split("__");
                  return `${idF} — Registro Nº ${n}`;
                })
              : [`${regs.length} registro(s) de ocorrências em ${tipoRelatorio} · ${categoriaRelatorio}`]
          }
          onConfirm={executeConfirmedDelete}
          onClose={() => setConfirmMode(null)}
        />
      )}
    </>
  );
};
