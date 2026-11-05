import React, { useMemo, useState, useCallback, useEffect } from "react";
import {
  Table2,
  Trash2,
  Edit3,
  Link2,
  ZoomIn,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Sparkles,
  Inbox,
  Image as ImageIcon,
  X,
} from "lucide-react";
import { toast } from "sonner";
import { useReportStore } from "../store/useReportStore";
import { getConcessionTheme } from "../utils/concessionTheme";
import { ConfirmDeleteModal } from "./Modals";

interface RegistrosCadastradosPanelProps {
  onOpenEditModal: (tab?: "fisc" | "nc") => void;
}

export const RegistrosCadastradosPanel: React.FC<RegistrosCadastradosPanelProps> = ({
  onOpenEditModal,
}) => {
  const {
    tipoRelatorio,
    categoriaRelatorio,
    getActiveWorkspace,
    deleteRegistrosNcBulk,
    deleteFiscalizacoesBulk,
    limparRegistrosAtuais,
  } = useReportStore();

  const ws = getActiveWorkspace();
  const regs = ws.registrosNc;
  const fiscs = ws.fiscalizacoes;
  const fotos = ws.photos;
  const isMonitoring = categoriaRelatorio === "Monitoramento";
  const theme = getConcessionTheme(tipoRelatorio, categoriaRelatorio);

  const [selFisc, setSelFisc] = useState<string[]>([]);
  const [selNc, setSelNc] = useState<string[]>([]);
  const [confirmMode, setConfirmMode] = useState<"fisc" | "nc" | "clear_all" | null>(null);
  const [zoomUrl, setZoomUrl] = useState<string | null>(null);

  // Fechamento de zoom/confirmação com ESC
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        if (zoomUrl) {
          setZoomUrl(null);
        } else if (confirmMode) {
          setConfirmMode(null);
        }
      }
    },
    [zoomUrl, confirmMode]
  );

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

  // Contabiliza ocorrências-base (desconsidera 2ª foto relacionada como registro duplo)
  const baseRegs = useMemo(() => regs.filter((r) => !r.is_relacionado), [regs]);

  const kpiData = useMemo(() => {
    if (isMonitoring) {
      const sanadas = baseRegs.filter((r) => r.Situação === "Sanada").length;
      const parciais = baseRegs.filter((r) => r.Situação === "Parcialmente Sanada").length;
      const pendentes = baseRegs.filter((r) => !r.Situação || r.Situação === "Pendente").length;
      return [
        {
          label: "Total Auditadas",
          value: baseRegs.length,
          icon: Table2,
          color: "",
          iconBg: "",
          customColor: theme.primary,
          customBg: theme.lightBg,
          customBorder: theme.lightBorder,
          border: "border-slate-200/80",
        },
        {
          label: "Saneadas",
          value: sanadas,
          icon: CheckCircle2,
          color: "text-[#008763]",
          iconBg: "bg-[#e6fbf4] border border-[#a7f3d0]",
          border: "border-[#a7f3d0]/60",
        },
        {
          label: "Parcialmente Saneadas",
          value: parciais,
          icon: Clock,
          color: "text-[#4338ca]",
          iconBg: "bg-[#eff2fe] border border-[#c7d2fe]",
          border: "border-[#c7d2fe]/60",
        },
        {
          label: "Pendentes",
          value: pendentes,
          icon: AlertTriangle,
          color: "text-[#b45309]",
          iconBg: "bg-[#fffbeb] border border-[#fde68a]",
          border: "border-[#fde68a]/60",
        },
      ];
    }

    if (tipoRelatorio === "CRA") {
      const ncCount = baseRegs.filter((r) => (r["Não Conformidade"] || "").trim() !== "").length;
      const paCount = baseRegs.length - ncCount;
      const relPhotosCount = regs.filter((r) => Boolean(r.Foto)).length;
      return [
        {
          label: "Total de Achados",
          value: baseRegs.length,
          icon: Table2,
          color: "",
          iconBg: "",
          customColor: theme.primary,
          customBg: theme.lightBg,
          customBorder: theme.lightBorder,
          border: "border-slate-200/80",
        },
        {
          label: "Não Conformidades (NC)",
          value: ncCount,
          icon: AlertTriangle,
          color: "text-rose-600",
          iconBg: "bg-rose-50 border border-rose-200",
          border: "border-rose-200/70",
        },
        {
          label: "Pontos de Atenção (PA)",
          value: paCount,
          icon: Sparkles,
          color: "text-amber-600",
          iconBg: "bg-amber-50 border border-amber-200",
          border: "border-amber-200/70",
        },
        {
          label: "Fotos Vinculadas",
          value: relPhotosCount,
          icon: ImageIcon,
          color: "text-[#008763]",
          iconBg: "bg-[#e6fbf4] border border-[#a7f3d0]",
          border: "border-[#a7f3d0]/70",
        },
      ];
    }

    const relPhotosCount = regs.filter((r) => Boolean(r.Foto)).length;
    return [
      {
        label: "Total de Ocorrências",
        value: baseRegs.length,
        icon: Table2,
        color: "",
        iconBg: "",
        customColor: theme.primary,
        customBg: theme.lightBg,
        customBorder: theme.lightBorder,
        border: "border-slate-200/80",
      },
      {
        label: "Irregularidades (NC)",
        value: baseRegs.length,
        icon: AlertTriangle,
        color: "text-rose-600",
        iconBg: "bg-rose-50 border border-rose-200",
        border: "border-rose-200/70",
      },
      {
        label: "Registros Fotográficos",
        value: relPhotosCount,
        icon: ImageIcon,
        color: "text-[#008763]",
        iconBg: "bg-[#e6fbf4] border border-[#a7f3d0]",
        border: "border-[#a7f3d0]/70",
      },
    ];
  }, [isMonitoring, tipoRelatorio, baseRegs, regs]);

  const allNcKeys = regs.map((r) => `${r["ID da Fiscalização"]}__${r["Nº"]}`);
  const allNcSelected = allNcKeys.length > 0 && allNcKeys.every((k) => selNc.includes(k));

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
      toast.success("Todos os registros de ocorrências foram limpos.");
    }
    setConfirmMode(null);
  };

  const ncHeaders = useMemo(() => {
    if (isMonitoring) {
      return [
        "Nº",
        "Foto",
        "Codificação / NC",
        tipoRelatorio === "SOCICAM" ? "Terminal" : "Pista / Trecho",
        "Situação",
        tipoRelatorio === "SOCICAM" ? "Informação SOCICAM" : `Posicionamento ${tipoRelatorio}`,
        "Constatação",
        "Análise ARPE",
        "Ações",
      ];
    }
    if (tipoRelatorio === "SOCICAM") {
      return [
        "Nº",
        "Foto",
        "Terminal",
        "Irregularidade",
        "Codificação",
        "Observações (Legenda)",
        "Determinação",
        "Ações",
      ];
    }
    if (tipoRelatorio === "CRC") {
      return [
        "Nº",
        "Foto",
        "Codificação",
        "Pista",
        "Trecho",
        "Patologia",
        "Observações (Legenda)",
        "Ações",
      ];
    }
    return [
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
  }, [isMonitoring, tipoRelatorio]);

  return (
    <div className="mt-0 flex flex-col gap-4 rounded-b-2xl rounded-t-none border-x border-b border-slate-300 bg-[#f1f5f9] p-4 sm:p-6 shadow-xl shadow-slate-900/5 animate-in slide-in-from-top-1 duration-200">
      {/* ========================================================================= */}
      {/* BARRA DE AÇÕES DO PAINEL EXPANSÍVEL (SEM TÍTULO REDUNDANTE, COR DINÂMICA) */}
      {/* ========================================================================= */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-300/80 pb-3.5">
        <div className="flex items-center gap-2.5">
          <div
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl border shadow-xs"
            style={{
              backgroundColor: theme.lightBg,
              borderColor: theme.lightBorder,
              color: theme.primary,
            }}
          >
            <Table2 className="h-4 w-4" />
          </div>
          <span
            className="rounded-full border px-3 py-1 font-mono text-xs font-bold shadow-xs"
            style={{
              backgroundColor: theme.lightBg,
              borderColor: theme.lightBorder,
              color: theme.primary,
            }}
          >
            {baseRegs.length} {baseRegs.length === 1 ? "achado registrado" : "achados registrados"}
          </span>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {regs.length > 0 && (
            <button
              type="button"
              onClick={() => onOpenEditModal("nc")}
              className="inline-flex items-center gap-1.5 rounded-xl border border-slate-300 bg-white px-3 py-1.5 text-[11px] font-bold text-slate-700 hover:bg-slate-50 hover:text-slate-900 transition-all shadow-xs"
              title="Editar todas as ocorrências em lote"
            >
              <Edit3 className="h-3.5 w-3.5" style={{ color: theme.primary }} /> Editar em Lote
            </button>
          )}

          {fiscs.length > 0 && (
            <button
              type="button"
              onClick={() => onOpenEditModal("fisc")}
              className="inline-flex items-center gap-1.5 rounded-xl border border-slate-300 bg-white px-3 py-1.5 text-[11px] font-bold text-slate-700 hover:bg-slate-50 hover:text-slate-900 transition-all shadow-xs"
              title="Editar cabeçalhos da fiscalização"
            >
              <Edit3 className="h-3.5 w-3.5" style={{ color: theme.primary }} /> Cabeçalhos ({fiscs.length})
            </button>
          )}

          {regs.length > 0 && (
            <button
              type="button"
              onClick={() => setConfirmMode("clear_all")}
              className="inline-flex items-center gap-1.5 rounded-xl border border-rose-300 bg-rose-50 px-2.5 py-1.5 text-[11px] font-bold text-rose-600 hover:bg-rose-100 transition-all shadow-xs"
              title="Limpar todos os registros cadastrados"
            >
              <Trash2 className="h-3.5 w-3.5" /> Limpar
            </button>
          )}
        </div>
      </div>

      {/* ========================================================================= */}
      {/* KPIS DE RESUMO (CARDS MODERNOS DA REFERÊNCIA)                             */}
      {/* ========================================================================= */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {kpiData.map((kpi, idx) => {
          const Icon = kpi.icon;
          return (
            <div
              key={idx}
              className={`flex items-center gap-3 rounded-2xl bg-white border ${kpi.border} p-3.5 shadow-sm transition-all hover:shadow-md`}
            >
              <div
                className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${
                  kpi.customColor ? "border" : `${kpi.iconBg} ${kpi.color}`
                }`}
                style={
                  kpi.customColor
                    ? {
                        color: kpi.customColor,
                        backgroundColor: kpi.customBg,
                        borderColor: kpi.customBorder,
                      }
                    : undefined
                }
              >
                <Icon className="h-5 w-5 stroke-[2.2]" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="text-[10px] font-bold uppercase tracking-wider text-slate-500 truncate">
                  {kpi.label}
                </div>
                <div className="text-xl font-extrabold text-slate-900 tracking-tight">
                  {kpi.value}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* ========================================================================= */}
      {/* BARRA DE AÇÕES EM LOTE (ESTILO ÍNDIGO DA REF)                              */}
      {/* ========================================================================= */}
      {selNc.length > 0 && (
        <div
          className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border px-4 py-2.5 text-xs shadow-sm animate-in slide-in-from-top-2 duration-150"
          style={{
            backgroundColor: theme.lightBg,
            borderColor: theme.lightBorder,
          }}
        >
          <div className="flex items-center gap-2">
            <span
              className="flex h-5 w-5 items-center justify-center rounded-full text-white font-bold text-[10px] shadow-xs"
              style={{ backgroundColor: theme.primary }}
            >
              {selNc.length}
            </span>
            <span className="font-bold text-slate-900">
              {selNc.length} {selNc.length === 1 ? "registro selecionado" : "registros selecionados"}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setConfirmMode("nc")}
              className="inline-flex items-center gap-1.5 rounded-xl bg-rose-600 px-3 py-1.5 text-xs font-bold text-white shadow-sm hover:bg-rose-500 active:scale-95 transition-all"
            >
              <Trash2 className="h-3.5 w-3.5" /> Excluir ({selNc.length})
            </button>
            <button
              type="button"
              onClick={() => setSelNc([])}
              className="rounded-xl border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-all shadow-xs"
            >
              Desmarcar
            </button>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TABELA DE OCORRÊNCIAS (ESTILO WHITE / ENTERPRISE DASHBOARD DA REF)        */}
      {/* ========================================================================= */}
      <div className="overflow-auto max-h-[460px] rounded-2xl border border-slate-300/90 bg-white shadow-xs">
        <table className="w-full text-left text-xs border-collapse">
          <thead className="sticky top-0 z-20 bg-[#f8fafc] text-slate-500 border-b border-slate-200 select-none">
            <tr>
              <th className="w-10 px-3.5 py-3">
                <input
                  type="checkbox"
                  checked={allNcSelected}
                  onChange={(e) => setSelNc(e.target.checked ? allNcKeys : [])}
                  className="h-4 w-4 rounded border-slate-300 cursor-pointer" style={{ accentColor: theme.primary }}
                  title="Selecionar todos os registros"
                />
              </th>
              {ncHeaders.map((h, idx) => (
                <th
                  key={`${h}_${idx}`}
                  className="px-3.5 py-3 text-[10px] font-bold uppercase tracking-wider text-slate-500"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 font-normal">
            {regs.length === 0 ? (
              <tr>
                <td colSpan={ncHeaders.length + 1} className="py-14 text-center">
                  <div className="flex flex-col items-center justify-center gap-2.5">
                    <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 text-slate-400">
                      <Inbox className="h-6 w-6" />
                    </div>
                    <div className="text-sm font-bold text-slate-800">
                      Nenhuma ocorrência registrada ainda
                    </div>
                    <p className="max-w-md text-xs text-slate-500">
                      Preencha os dados e salve a ocorrência acima para visualizar e auditar nesta tabela.
                    </p>
                  </div>
                </td>
              </tr>
            ) : (
              regs.map((r, i) => {
                const rowKey = `${r["ID da Fiscalização"]}__${r["Nº"]}`;
                const fi = fotos.findIndex((f) => f.name === r.Foto);
                const isNc = Boolean((r["Não Conformidade"] || "").trim());
                const sit = r.Situação || "Pendente";
                const isChecked = selNc.includes(rowKey);

                return (
                  <tr
                    key={rowKey}
                    className={`group transition-colors duration-150 ${
                      isChecked
                        ? "bg-[#eff2fe]/70 hover:bg-[#eff2fe]"
                        : r.is_relacionado
                        ? "bg-slate-50/60 hover:bg-slate-50"
                        : "hover:bg-slate-50/80"
                    }`}
                  >
                    {/* Checkbox */}
                    <td className="px-3.5 py-2.5">
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={() =>
                          setSelNc((s) =>
                            s.includes(rowKey) ? s.filter((x) => x !== rowKey) : [...s, rowKey]
                          )
                        }
                        className="h-4 w-4 rounded border-slate-300 cursor-pointer" style={{ accentColor: theme.primary }}
                      />
                    </td>

                    {/* Nº Sequencial */}
                    <td className="px-3.5 py-2.5 font-bold text-slate-900 whitespace-nowrap">
                      <div className="flex items-center gap-1.5">
                        <span className="font-mono text-xs">{r["Nº"] || i + 1}</span>
                        {r.is_relacionado && (
                          <span
                            className="inline-flex items-center gap-0.5 rounded-md border px-1.5 py-0.5 text-[9px] font-bold"
                            style={{
                              backgroundColor: theme.lightBg,
                              borderColor: theme.lightBorder,
                              color: theme.primary,
                            }}
                            title="2ª foto relacionada à ocorrência anterior"
                          >
                            <Link2 className="h-2.5 w-2.5" /> 2ª Foto
                          </span>
                        )}
                      </div>
                    </td>

                    {/* Foto com Zoom Lightbox */}
                    <td className="px-3.5 py-2 whitespace-nowrap">
                      {fi >= 0 ? (
                        <div
                          className="group/img relative h-9 w-12 cursor-pointer overflow-hidden rounded-lg border border-slate-200 bg-slate-100 shadow-xs transition-transform duration-200 hover:scale-110 hover:border-indigo-400"
                          onClick={() => setZoomUrl(fotos[fi].previewUrl)}
                          title={`Ampliar ${r.Foto}`}
                        >
                          <img
                            src={fotos[fi].previewUrl}
                            alt={r.Foto}
                            className="h-full w-full object-cover"
                          />
                          <div className="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 group-hover/img:opacity-100 transition-opacity">
                            <ZoomIn className="h-3.5 w-3.5 text-white" />
                          </div>
                        </div>
                      ) : (
                        <span className="font-mono text-[11px] text-slate-400" title={r.Foto}>
                          {r.Foto || "—"}
                        </span>
                      )}
                    </td>

                    {/* Colunas Específicas por Modalidade e Concessão */}
                    {isMonitoring ? (
                      <>
                        <td className="px-3.5 py-2.5 font-mono text-xs font-bold text-slate-900 whitespace-nowrap">
                          {r.Identificação || "—"}
                        </td>
                        <td className="px-3.5 py-2.5 text-slate-700 whitespace-nowrap">
                          {tipoRelatorio === "SOCICAM"
                            ? r.Terminal || "—"
                            : [r.Pista, r.Trecho].filter(Boolean).join(" · ") || "—"}
                        </td>
                        <td className="px-3.5 py-2.5 whitespace-nowrap">
                          <span
                            className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[11px] font-bold border ${
                              sit === "Sanada"
                                ? "bg-[#e6fbf4] border-[#a7f3d0] text-[#008763]"
                                : sit === "Parcialmente Sanada"
                                ? "bg-[#eff2fe] border-[#c7d2fe] text-[#4338ca]"
                                : "bg-[#fffbeb] border-[#fde68a] text-[#b45309]"
                            }`}
                          >
                            <span
                              className={`h-1.5 w-1.5 rounded-full ${
                                sit === "Sanada"
                                  ? "bg-[#008763]"
                                  : sit === "Parcialmente Sanada"
                                  ? "bg-[#4338ca]"
                                  : "bg-[#b45309]"
                              }`}
                            />
                            {sit}
                          </span>
                        </td>
                        <td className="max-w-[170px] truncate px-3.5 py-2.5 text-slate-600" title={r.Determinação}>
                          {r.Determinação || "—"}
                        </td>
                        <td className="max-w-[170px] truncate px-3.5 py-2.5 text-slate-600" title={r.Observações}>
                          {r.Observações || "—"}
                        </td>
                        <td className="max-w-[170px] truncate px-3.5 py-2.5 text-slate-600" title={r["Análise ARPE"]}>
                          {r["Análise ARPE"] || "—"}
                        </td>
                      </>
                    ) : tipoRelatorio === "SOCICAM" ? (
                      <>
                        <td className="px-3.5 py-2.5 text-slate-700 whitespace-nowrap">{r.Terminal || "—"}</td>
                        <td className="px-3.5 py-2.5 font-bold text-slate-900 max-w-[170px] truncate" title={r["Não Conformidade"]}>
                          {r["Não Conformidade"] || "—"}
                        </td>
                        <td className="px-3.5 py-2.5 font-mono text-xs text-slate-700 whitespace-nowrap">
                          {r.Identificação || "—"}
                        </td>
                        <td className="max-w-[180px] truncate px-3.5 py-2.5 text-slate-600" title={r.Observações}>
                          {r.Observações || "—"}
                        </td>
                        <td className="max-w-[150px] truncate px-3.5 py-2.5 text-slate-600" title={r.Determinação}>
                          {r.Determinação || "—"}
                        </td>
                      </>
                    ) : tipoRelatorio === "CRC" ? (
                      <>
                        <td className="px-3.5 py-2.5 font-mono text-xs font-bold text-slate-900 whitespace-nowrap">
                          {r.Identificação || "—"}
                        </td>
                        <td className="px-3.5 py-2.5 text-slate-700 whitespace-nowrap">{r.Pista || "—"}</td>
                        <td className="px-3.5 py-2.5 text-slate-700 whitespace-nowrap">{r.Trecho || "—"}</td>
                        <td className="px-3.5 py-2.5 font-bold text-slate-900 max-w-[180px] truncate" title={r["Não Conformidade"]}>
                          {r["Não Conformidade"] || "—"}
                        </td>
                        <td className="max-w-[180px] truncate px-3.5 py-2.5 text-slate-600" title={r.Observações}>
                          {r.Observações || "—"}
                        </td>
                      </>
                    ) : (
                      /* CRA Fiscalização */
                      <>
                        <td className="px-3.5 py-2.5 whitespace-nowrap">
                          <span
                            className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-[11px] font-bold border ${
                              isNc
                                ? "bg-rose-50 border-rose-200 text-rose-700"
                                : "bg-amber-50 border-amber-200 text-amber-700"
                            }`}
                          >
                            {isNc ? "NC" : "PA"}
                          </span>
                        </td>
                        <td className="px-3.5 py-2.5 text-slate-700 whitespace-nowrap">{r.Pista || "—"}</td>
                        <td className="px-3.5 py-2.5 text-slate-700 whitespace-nowrap">{r.Trecho || "—"}</td>
                        <td className="px-3.5 py-2.5 text-slate-700 whitespace-nowrap">{r.Direção || r.Faixa || "—"}</td>
                        <td className="px-3.5 py-2.5 font-mono text-xs font-bold text-indigo-700 whitespace-nowrap">
                          {r.Identificação || "—"}
                        </td>
                        <td className="max-w-[200px] truncate px-3.5 py-2.5 text-slate-600" title={r.Observações || r["Não Conformidade"] || r["Ponto de Atenção"]}>
                          {r.Observações || r["Não Conformidade"] || r["Ponto de Atenção"] || "—"}
                        </td>
                      </>
                    )}

                    {/* Ações */}
                    <td className="px-3.5 py-2.5 whitespace-nowrap">
                      <button
                        type="button"
                        onClick={() => {
                          setSelNc([rowKey]);
                          setConfirmMode("nc");
                        }}
                        className="rounded-lg p-1.5 text-slate-400 hover:bg-rose-50 hover:text-rose-600 transition-colors"
                        title="Excluir ocorrência"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Modal de Zoom Lightbox */}
      {zoomUrl && (
        <div
          className="fixed inset-0 z-60 flex items-center justify-center bg-black/90 p-4 backdrop-blur-md"
          onClick={() => setZoomUrl(null)}
        >
          <div className="relative max-h-[90vh] max-w-4xl animate-in fade-in zoom-in-95 duration-200">
            <button
              type="button"
              aria-label="Fechar ampliação"
              onClick={() => setZoomUrl(null)}
              className="absolute -right-3 -top-3 rounded-full bg-white p-2 text-slate-900 shadow-xl hover:scale-110 active:scale-95 transition-all"
            >
              <X className="h-5 w-5" />
            </button>
            <img
              src={zoomUrl}
              alt="Zoom"
              className="max-h-[85vh] rounded-2xl object-contain shadow-2xl ring-1 ring-white/20"
            />
          </div>
        </div>
      )}

      {/* Confirmação de Exclusão */}
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
              ? "Confirma a exclusão das ocorrências selecionadas e a renumeração sequencial?"
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
    </div>
  );
};
