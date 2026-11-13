import React, { useMemo, useState, useCallback, useEffect } from "react";
import { createPortal } from "react-dom";
import {
  Table2,
  Trash2,
  Link2,
  ZoomIn,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Sparkles,
  Inbox,
  Image as ImageIcon,
  X,
  RotateCcw,
} from "lucide-react";
import { toast } from "sonner";
import { useReportStore } from "../store/useReportStore";
import { RegistroNC } from "../types/report.types";
import { getConcessionTheme } from "../utils/concessionTheme";
import {
  contrairCodificacoes,
  contarAchadosUnicosNoGrupo,
} from "../utils/reportFormatting";
import { ConfirmDeleteModal } from "./Modals";
import { useLockBodyScroll } from "../hooks/useLockBodyScroll";

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
    reiniciarModalidadeAtual,
  } = useReportStore();

  const ws = getActiveWorkspace();
  const currentFisc = ws.fiscalizacoes[ws.activeFiscalizacaoIndex] || ws.fiscalizacoes[0];
  const currentFiscId = currentFisc?.["ID da Fiscalização"]?.trim() || "";
  const regs = useMemo(
    () => ws.registrosNc.filter((r) => !currentFiscId || (r["ID da Fiscalização"] || "").trim() === currentFiscId),
    [ws.registrosNc, currentFiscId]
  );
  const fiscs = ws.fiscalizacoes;
  const fotos = ws.photos;
  const isMonitoring = categoriaRelatorio === "Monitoramento";
  const theme = getConcessionTheme(tipoRelatorio, categoriaRelatorio);

  const [selFisc, setSelFisc] = useState<string[]>([]);
  const [selNc, setSelNc] = useState<string[]>([]);
  const [confirmMode, setConfirmMode] = useState<"fisc" | "nc" | null>(null);
  const [zoomUrl, setZoomUrl] = useState<string | null>(null);

  // Trava scroll do body quando lightbox de zoom estiver aberto
  useLockBodyScroll(Boolean(zoomUrl));

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

  // Agrupa fotos relacionadas (mesmo grupo_relacao) em uma única linha no Sumário
  const groupedRows = useMemo(() => {
    const groups: {
      base: RegistroNC;
      relacionado: RegistroNC | null;
      allRecords: RegistroNC[];
      rowKeys: string[];
    }[] = [];
    const byGroup = new Map<string, number>();

    regs.forEach((r) => {
      const rKey = `${r["ID da Fiscalização"]}__${r["Nº"]}`;
      const grp = r.grupo_relacao;
      if (grp && byGroup.has(grp)) {
        const idx = byGroup.get(grp)!;
        const entry = groups[idx];
        if (
          !entry.relacionado &&
          (r.is_relacionado ||
            (r.Foto || "").trim().toLowerCase() !==
              (entry.base.Foto || "").trim().toLowerCase())
        ) {
          entry.relacionado = r;
        }
        entry.allRecords.push(r);
        entry.rowKeys.push(rKey);
      } else {
        const entry = {
          base: r,
          relacionado: null as RegistroNC | null,
          allRecords: [r],
          rowKeys: [rKey],
        };
        if (grp) byGroup.set(grp, groups.length);
        groups.push(entry);
      }
    });

    return groups;
  }, [regs]);

  const kpiData = useMemo(() => {
    if (isMonitoring) {
      const sanadas = groupedRows.filter((g) => g.base.Situação === "Sanada").length;
      const parciais = groupedRows.filter(
        (g) => g.base.Situação === "Parcialmente Sanada"
      ).length;
      const pendentes = groupedRows.filter(
        (g) => !g.base.Situação || g.base.Situação === "Pendente"
      ).length;
      return [
        {
          label: "Auditadas",
          value: groupedRows.length,
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
          label: "Parciais",
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

    const ncCount = groupedRows.reduce(
      (acc, g) =>
        acc + contarAchadosUnicosNoGrupo(g.allRecords, "Não Conformidade"),
      0
    );
    const paCount = groupedRows.reduce(
      (acc, g) =>
        acc + contarAchadosUnicosNoGrupo(g.allRecords, "Ponto de Atenção"),
      0
    );
    const relPhotosCount = new Set(
      regs.map((r) => (r.Foto || "").trim().toLowerCase()).filter(Boolean)
    ).size;

    return [
      {
        label: "Ocorrências",
        value: groupedRows.length,
        icon: Table2,
        color: "",
        iconBg: "",
        customColor: theme.primary,
        customBg: theme.lightBg,
        customBorder: theme.lightBorder,
        border: "border-slate-200/80",
      },
      {
        label: "Irregularidades",
        value: ncCount,
        icon: AlertTriangle,
        color: "text-rose-600",
        iconBg: "bg-rose-50 border border-rose-200",
        border: "border-rose-200/70",
      },
      {
        label: "Pontos de Atenção",
        value: paCount,
        icon: Sparkles,
        color: "text-amber-600",
        iconBg: "bg-amber-50 border border-amber-200",
        border: "border-amber-200/70",
      },
      {
        label: "Registros",
        value: relPhotosCount,
        icon: ImageIcon,
        color: "text-[#008763]",
        iconBg: "bg-[#e6fbf4] border border-[#a7f3d0]",
        border: "border-[#a7f3d0]/70",
      },
    ];
  }, [isMonitoring, groupedRows, regs, theme]);

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
        "Tipo",
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
    <div className="flex flex-col gap-4 bg-white p-4 sm:p-6 animate-in slide-in-from-top-1 duration-200">
      {/* ========================================================================= */}
      {/* KPIS DE RESUMO (CARDS MODERNOS DA REFERÊNCIA)                             */}
      {/* ========================================================================= */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {kpiData.map((kpi, idx) => {
          const Icon = kpi.icon;
          return (
            <div
              key={idx}
              className={`flex items-center gap-3 rounded-2xl bg-white border ${kpi.border} p-3.5 shadow-sm transition-all duration-200 hover:shadow-md hover:-translate-y-0.5 hover:border-slate-300 cursor-default`}
            >
              <div
                className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${kpi.customColor ? "border" : `${kpi.iconBg} ${kpi.color}`
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
                <div className="text-[10px] font-bold uppercase tracking-tight text-slate-500 whitespace-nowrap">
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
            {groupedRows.length === 0 ? (
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
              groupedRows.map((group, i) => {
                const r = group.base;
                const rel = group.relacionado;
                const rowKey = group.rowKeys[0];
                const fi = fotos.findIndex((f) => f.name === r.Foto);
                const fiRel = rel ? fotos.findIndex((f) => f.name === rel.Foto) : -1;
                const isNc = Boolean((r["Não Conformidade"] || "").trim());
                const sit = r.Situação || "Pendente";
                const isChecked = group.rowKeys.every((k) => selNc.includes(k));

                const codsGrupo = group.allRecords
                  .map((rec) => (rec.Identificação || rec.Codificação || "").trim())
                  .filter((v, idx, arr) => v && arr.indexOf(v) === idx);
                const codDisplay =
                  codsGrupo.length >= 2
                    ? contrairCodificacoes(codsGrupo[0], codsGrupo[codsGrupo.length - 1]) ||
                      codsGrupo[0]
                    : codsGrupo[0] || "—";

                const obsDisplay = rel
                  ? rel.Observações || r.Observações || r["Não Conformidade"] || r["Ponto de Atenção"] || "—"
                  : r.Observações || r["Não Conformidade"] || r["Ponto de Atenção"] || "—";

                const ncSiglasDisplay =
                  group.allRecords
                    .flatMap((rec) => [rec["Não Conformidade"], rec["Ponto de Atenção"]])
                    .filter(Boolean)
                    .flatMap((v) => String(v).split(",").map((s) => s.trim()))
                    .filter((v, idx, arr) => v && arr.indexOf(v) === idx)
                    .join(", ") || "—";

                return (
                  <tr
                    key={rowKey}
                    className={`group transition-colors duration-150 ${isChecked
                        ? "bg-[#eff2fe]/70 hover:bg-[#eff2fe]"
                        : rel
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
                            isChecked
                              ? s.filter((x) => !group.rowKeys.includes(x))
                              : Array.from(new Set([...s, ...group.rowKeys]))
                          )
                        }
                        className="h-4 w-4 rounded border-slate-300 cursor-pointer" style={{ accentColor: theme.primary }}
                      />
                    </td>

                    {/* Nº Sequencial */}
                    <td className="px-3.5 py-2.5 font-bold text-slate-900 whitespace-nowrap">
                      <div className="flex items-center gap-1.5">
                        <span className="font-mono text-xs">{r["Nº"] || i + 1}</span>
                        {rel && (
                          <span
                            className="inline-flex items-center gap-0.5 rounded-md border px-1.5 py-0.5 text-[9px] font-bold"
                            style={{
                              backgroundColor: theme.lightBg,
                              borderColor: theme.lightBorder,
                              color: theme.primary,
                            }}
                            title="Ocorrência com 2 fotos relacionadas lado a lado"
                          >
                            <Link2 className="h-2.5 w-2.5" /> 2 Fotos
                          </span>
                        )}
                      </div>
                    </td>

                    {/* Foto(s) com Zoom Lightbox */}
                    <td className="px-3.5 py-2 whitespace-nowrap">
                      <div className="flex items-center gap-1.5">
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

                        {rel &&
                          (fiRel >= 0 ? (
                            <div
                              className="group/img relative h-9 w-12 cursor-pointer overflow-hidden rounded-lg border border-slate-200 bg-slate-100 shadow-xs transition-transform duration-200 hover:scale-110 hover:border-indigo-400"
                              onClick={() => setZoomUrl(fotos[fiRel].previewUrl)}
                              title={`Ampliar ${rel.Foto}`}
                            >
                              <img
                                src={fotos[fiRel].previewUrl}
                                alt={rel.Foto}
                                className="h-full w-full object-cover"
                              />
                              <div className="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 group-hover/img:opacity-100 transition-opacity">
                                <ZoomIn className="h-3.5 w-3.5 text-white" />
                              </div>
                            </div>
                          ) : (
                            <span className="font-mono text-[11px] text-slate-400" title={rel.Foto}>
                              {rel.Foto || "—"}
                            </span>
                          ))}
                      </div>
                    </td>

                    {/* Colunas Específicas por Modalidade e Concessão */}
                    {isMonitoring ? (
                      <>
                        <td className="px-3.5 py-2.5 font-mono text-xs font-bold text-slate-900 whitespace-nowrap">
                          {codDisplay}
                        </td>
                        <td className="px-3.5 py-2.5 text-slate-700 whitespace-nowrap">
                          {tipoRelatorio === "SOCICAM"
                            ? r.Terminal || "—"
                            : [r.Pista, r.Trecho].filter(Boolean).join(" · ") || "—"}
                        </td>
                        <td className="px-3.5 py-2.5 whitespace-nowrap">
                          <span
                            className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[11px] font-bold border ${sit === "Sanada"
                                ? "bg-[#e6fbf4] border-[#a7f3d0] text-[#008763]"
                                : sit === "Parcialmente Sanada"
                                  ? "bg-[#eff2fe] border-[#c7d2fe] text-[#4338ca]"
                                  : "bg-[#fffbeb] border-[#fde68a] text-[#b45309]"
                              }`}
                          >
                            <span
                              className={`h-1.5 w-1.5 rounded-full ${sit === "Sanada"
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
                        <td className="max-w-[170px] truncate px-3.5 py-2.5 text-slate-600" title={obsDisplay}>
                          {obsDisplay}
                        </td>
                        <td className="max-w-[170px] truncate px-3.5 py-2.5 text-slate-600" title={r["Análise ARPE"]}>
                          {r["Análise ARPE"] || "—"}
                        </td>
                      </>
                    ) : tipoRelatorio === "SOCICAM" ? (
                      <>
                        <td className="px-3.5 py-2.5 whitespace-nowrap">
                          <span
                            className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-[11px] font-bold border ${isNc
                                ? "bg-rose-50 border-rose-200 text-rose-700"
                                : "bg-amber-50 border-amber-200 text-amber-700"
                              }`}
                          >
                            {isNc ? "NC" : "PA"}
                          </span>
                        </td>
                        <td className="px-3.5 py-2.5 text-slate-700 whitespace-nowrap">{r.Terminal || "—"}</td>
                        <td className="px-3.5 py-2.5 font-bold text-slate-900 max-w-[170px] truncate" title={ncSiglasDisplay}>
                          {ncSiglasDisplay}
                        </td>
                        <td className="px-3.5 py-2.5 font-mono text-xs text-slate-700 whitespace-nowrap">
                          {codDisplay}
                        </td>
                        <td className="max-w-[180px] truncate px-3.5 py-2.5 text-slate-600" title={obsDisplay}>
                          {obsDisplay}
                        </td>
                        <td className="max-w-[150px] truncate px-3.5 py-2.5 text-slate-600" title={r.Determinação}>
                          {r.Determinação || "—"}
                        </td>
                      </>
                    ) : tipoRelatorio === "CRC" ? (
                      <>
                        <td className="px-3.5 py-2.5 font-mono text-xs font-bold text-slate-900 whitespace-nowrap">
                          {codDisplay}
                        </td>
                        <td className="px-3.5 py-2.5 text-slate-700 whitespace-nowrap">{r.Pista || "—"}</td>
                        <td className="px-3.5 py-2.5 text-slate-700 whitespace-nowrap">{r.Trecho || "—"}</td>
                        <td className="px-3.5 py-2.5 font-bold text-slate-900 max-w-[180px] truncate" title={ncSiglasDisplay}>
                          {ncSiglasDisplay}
                        </td>
                        <td className="max-w-[180px] truncate px-3.5 py-2.5 text-slate-600" title={obsDisplay}>
                          {obsDisplay}
                        </td>
                      </>
                    ) : (
                      /* CRA Fiscalização */
                      <>
                        <td className="px-3.5 py-2.5 whitespace-nowrap">
                          <span
                            className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-[11px] font-bold border ${isNc
                                ? "bg-rose-50 border-rose-200 text-rose-700"
                                : "bg-amber-50 border-amber-200 text-amber-700"
                              }`}
                          >
                            {isNc ? "NC" : "PA"}
                          </span>
                        </td>
                        <td className="px-3.5 py-2.5 text-slate-700 whitespace-nowrap">{r.Pista || "—"}</td>
                        <td className="px-3.5 py-2.5 text-slate-700 whitespace-nowrap">{r.Trecho || "—"}</td>
                        <td className="px-3.5 py-2.5 text-slate-700 whitespace-nowrap">{r["Direção (faixa)"] || "—"}</td>
                        <td className="px-3.5 py-2.5 font-mono text-xs font-bold text-indigo-700 whitespace-nowrap">
                          {codDisplay}
                        </td>
                        <td className="max-w-[200px] truncate px-3.5 py-2.5 text-slate-600" title={obsDisplay}>
                          {obsDisplay}
                        </td>
                      </>
                    )}

                    {/* Ações */}
                    <td className="px-3.5 py-2.5 whitespace-nowrap">
                      <button
                        type="button"
                        onClick={() => {
                          setSelNc(group.rowKeys);
                          setConfirmMode("nc");
                        }}
                        className="rounded-lg p-1.5 text-slate-400 hover:bg-rose-50 hover:text-rose-600 transition-colors"
                        title={rel ? "Excluir relação (ambas as fotos)" : "Excluir ocorrência"}
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
      {zoomUrl &&
        createPortal(
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
          </div>,
          document.body
        )}

      {/* Confirmação de Exclusão */}
      {confirmMode && (
        <ConfirmDeleteModal
          title={
            confirmMode === "fisc"
              ? "Excluir Cabeçalhos Selecionados"
              : "Excluir Ocorrências Selecionadas"
          }
          description={
            confirmMode === "fisc"
              ? "Os cabeçalhos abaixo e todas as ocorrências vinculadas a eles serão removidos:"
              : "Confirma a exclusão das ocorrências selecionadas e a renumeração sequencial?"
          }
          itemsPreview={
            confirmMode === "fisc"
              ? selFisc
              : selNc.map((k) => {
                  const [idF, n] = k.split("__");
                  return `${idF} — Registro Nº ${n}`;
                })
          }
          onConfirm={executeConfirmedDelete}
          onClose={() => setConfirmMode(null)}
        />
      )}
    </div>
  );
};
