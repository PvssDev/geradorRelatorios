import React, { useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import {
  BarChart3,
  CheckCircle2,
  Clock,
  AlertTriangle,
  FileCheck2,
  MessageSquareText,
} from "lucide-react";
import { Card } from "./Card";
import { useReportStore } from "../store/useReportStore";
import { calcularEstatisticasMonitoramento } from "../utils/monitoringStats";
import {
  getConcessionTheme,
  isPerformanceModeActive,
} from "../utils/concessionTheme";

type SegmentKey = "sanadas" | "parciais" | "pendentes" | "faltam";

interface ChartSegment {
  key: SegmentKey;
  label: string;
  shortLabel: string;
  count: number;
  pct: number;
  color: string;
  softBg: string;
  length: number;
  offset: number;
}

export const RecomendacaoGeralPanel: React.FC = () => {
  const {
    tipoRelatorio,
    categoriaRelatorio,
    getActiveWorkspace,
    upsertActiveFiscalizacao,
  } = useReportStore();
  const ws = getActiveWorkspace();

  const theme = getConcessionTheme(tipoRelatorio, categoriaRelatorio);
  const isPerf = isPerformanceModeActive();
  const [hoveredStatus, setHoveredStatus] = useState<SegmentKey | null>(null);
  const [textareaFocused, setTextareaFocused] = useState(false);

  const activeFiscIdx = Math.max(
    0,
    Math.min(ws.activeFiscalizacaoIndex, Math.max(0, ws.fiscalizacoes.length - 1))
  );
  const activeFisc = ws.fiscalizacoes[activeFiscIdx];
  const activeFiscId = (activeFisc?.["ID da Fiscalização"] || "").trim();

  const activeRegs = useMemo(() => {
    if (!activeFiscId) return [];
    return ws.registrosNc.filter(
      (r) => (r["ID da Fiscalização"] || "").trim() === activeFiscId
    );
  }, [ws.registrosNc, activeFiscId]);

  const stats = useMemo(
    () =>
      calcularEstatisticasMonitoramento(
        activeRegs,
        ws.oldPhotosToMatch,
        ws.documentoAnteriorMeta
      ),
    [activeRegs, ws.oldPhotosToMatch, ws.documentoAnteriorMeta]
  );

  const recomendacaoText = activeFisc?.["Recomendações à SOCICAM"] || "";

  const handleChangeRecomendacao = (
    e: React.ChangeEvent<HTMLTextAreaElement>
  ) => {
    if (!activeFisc) return;
    upsertActiveFiscalizacao({
      ...activeFisc,
      "Recomendações à SOCICAM": e.target.value,
    });
  };

  // Geometria do gráfico Donut SVG (raio = 38, circunferência ≈ 238.76)
  const radius = 38;
  const circumference = 2 * Math.PI * radius;
  const base = Math.max(stats.baseComparacao, 1);

  const segments = useMemo<ChartSegment[]>(() => {
    const raw: Array<Omit<ChartSegment, "length" | "offset">> = [
      {
        key: "sanadas",
        label: "Sanadas",
        shortLabel: "Sanadas",
        count: stats.sanadas,
        pct: stats.pctSanadas,
        color: "#10b981", // Emerald 500
        softBg: "rgba(16, 185, 129, 0.10)",
      },
      {
        key: "parciais",
        label: "Parcialmente Sanadas",
        shortLabel: "Parciais",
        count: stats.parcialmenteSanadas,
        pct: stats.pctParciais,
        color: "#6366f1", // Indigo 500
        softBg: "rgba(99, 102, 241, 0.10)",
      },
      {
        key: "pendentes",
        label: "Pendentes",
        shortLabel: "Pendentes",
        count: stats.pendentes,
        pct: stats.pctPendentes,
        color: theme.primary,
        softBg: `${theme.primary}18`,
      },
      {
        key: "faltam",
        label: "Aguardando Registro",
        shortLabel: "Faltam",
        count: stats.naoRegistradas,
        pct: stats.pctNaoRegistradas,
        color: "#cbd5e1", // Slate 300
        softBg: "rgba(148, 163, 184, 0.14)",
      },
    ];

    let accLen = 0;
    return raw.map((item) => {
      const length = (item.count / base) * circumference;
      const offset = -accLen;
      accLen += length;
      return { ...item, length, offset };
    });
  }, [
    stats.sanadas,
    stats.pctSanadas,
    stats.parcialmenteSanadas,
    stats.pctParciais,
    stats.pendentes,
    stats.pctPendentes,
    stats.naoRegistradas,
    stats.pctNaoRegistradas,
    base,
    circumference,
    theme.primary,
  ]);

  const activeSegment = hoveredStatus
    ? segments.find((s) => s.key === hoveredStatus) || null
    : null;

  const centerDisplay = activeSegment
    ? {
        key: activeSegment.key,
        pct: activeSegment.pct,
        label: activeSegment.shortLabel,
        sub: `${activeSegment.count} NC${activeSegment.count === 1 ? "" : "s"}`,
        color:
          activeSegment.key === "faltam" ? "#475569" : activeSegment.color,
      }
    : {
        key: "default",
        pct: stats.pctSanadas,
        label: "Sanadas",
        sub: `${stats.sanadas}/${stats.baseComparacao}`,
        color: "#10b981",
      };

  const chartTransition = isPerf
    ? { duration: 0 }
    : { duration: 0.72, ease: [0.22, 1, 0.36, 1] as const };

  return (
    <Card
      n={4}
      icon={<BarChart3 className="h-5 w-5" />}
      title="Recomendação Geral"
    >
      <div className="space-y-6">
        {/* 1. Painel Estatístico e Gráfico Comparativo com o Monitoramento Anterior */}
        <div className="rounded-2xl border border-[#d2e2f3] bg-gradient-to-b from-slate-50/75 to-white p-5 shadow-xs">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-200/80 pb-3.5">
            <div>
              <h3 className="text-sm font-bold text-[#071d36]">
                Panorama Comparativo · Monitoramento Anterior vs. Atual
              </h3>
              <p className="text-xs text-slate-500">
                Evolução real das Não Conformidades auditadas no processo{" "}
                <span className="font-semibold text-[#071d36]">
                  {activeFiscId || "atual"}
                </span>
              </p>
            </div>
            <span
              className="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-bold ring-1 transition-colors"
              style={{
                backgroundColor: theme.lightBg,
                color: "#071d36",
                borderColor: theme.lightBorder,
              }}
            >
              <FileCheck2
                className="h-3.5 w-3.5"
                style={{ color: theme.primary }}
              />
              {stats.registradas} de {stats.baseComparacao} registradas (
              {stats.pctCobertura}%)
            </span>
          </div>

          <div className="mt-4 grid grid-cols-1 gap-5 lg:grid-cols-12 lg:items-center">
            {/* Gráfico Donut SVG Interativo + Legenda Sincronizada */}
            <div className="flex flex-col items-center justify-center gap-4 rounded-2xl border border-slate-200/80 bg-white p-4 shadow-xs sm:flex-row lg:col-span-5">
              <div className="relative h-28 w-28 shrink-0">
                <svg
                  viewBox="0 0 112 112"
                  className="h-full w-full -rotate-90 transform overflow-visible"
                  aria-label="Gráfico interativo de situação das Não Conformidades"
                >
                  {/* Trilha base neutra */}
                  <circle
                    cx="56"
                    cy="56"
                    r={radius}
                    fill="transparent"
                    stroke="#f1f5f9"
                    strokeWidth="12"
                  />

                  {segments.map((seg, idx) => {
                    if (seg.length <= 0) return null;
                    const isHovered = hoveredStatus === seg.key;
                    const isDimmed = hoveredStatus !== null && !isHovered;

                    return (
                      <motion.circle
                        key={seg.key}
                        cx="56"
                        cy="56"
                        r={radius}
                        fill="transparent"
                        stroke={seg.color}
                        strokeLinecap="butt"
                        initial={{
                          strokeDasharray: isPerf
                            ? `${seg.length} ${circumference}`
                            : `0 ${circumference}`,
                          strokeDashoffset: seg.offset,
                          strokeWidth: 12,
                          opacity: 1,
                        }}
                        animate={{
                          strokeDasharray: `${seg.length} ${circumference}`,
                          strokeDashoffset: seg.offset,
                          strokeWidth: isHovered ? 15.5 : 12,
                          opacity: isDimmed ? 0.28 : 1,
                        }}
                        transition={{
                          strokeDasharray: {
                            ...chartTransition,
                            delay: isPerf ? 0 : idx * 0.06,
                          },
                          strokeDashoffset: chartTransition,
                          strokeWidth: { duration: isPerf ? 0 : 0.2 },
                          opacity: { duration: isPerf ? 0 : 0.2 },
                        }}
                        style={{
                          filter: isHovered
                            ? `drop-shadow(0 0 6px ${seg.color}66)`
                            : "none",
                        }}
                      />
                    );
                  })}
                </svg>

                {/* Centro dinâmico do Donut */}
                <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center text-center">
                  <AnimatePresence mode="wait">
                    <motion.div
                      key={centerDisplay.key}
                      initial={isPerf ? false : { opacity: 0, scale: 0.92 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={isPerf ? undefined : { opacity: 0, scale: 0.92 }}
                      transition={{ duration: isPerf ? 0 : 0.16 }}
                      className="flex flex-col items-center"
                    >
                      <span className="text-lg font-extrabold leading-none text-[#071d36]">
                        {centerDisplay.pct}%
                      </span>
                      <span
                        className="mt-0.5 text-[10px] font-bold leading-tight"
                        style={{ color: centerDisplay.color }}
                      >
                        {centerDisplay.label}
                      </span>
                      <span className="text-[9.5px] font-medium text-slate-400">
                        {centerDisplay.sub}
                      </span>
                    </motion.div>
                  </AnimatePresence>
                </div>
              </div>

              {/* Legenda interativa */}
              <div className="w-full space-y-1 text-xs sm:w-auto sm:min-w-[136px]">
                {segments
                  .filter((seg) => seg.key !== "faltam" || seg.count > 0)
                  .map((seg) => {
                    const isHovered = hoveredStatus === seg.key;
                    const isDimmed = hoveredStatus !== null && !isHovered;

                    return (
                      <button
                        key={seg.key}
                        type="button"
                        onMouseEnter={() => setHoveredStatus(seg.key)}
                        onMouseLeave={() => setHoveredStatus(null)}
                        onFocus={() => setHoveredStatus(seg.key)}
                        onBlur={() => setHoveredStatus(null)}
                        className={`flex w-full items-center justify-between gap-2.5 rounded-lg px-2 py-1 text-left transition-all duration-150 ${
                          isHovered
                            ? "bg-slate-100/90 shadow-2xs ring-1 ring-slate-200"
                            : "hover:bg-slate-50"
                        } ${isDimmed ? "opacity-55" : "opacity-100"}`}
                      >
                        <span className="flex items-center gap-2">
                          <span
                            className={`h-2.5 w-2.5 shrink-0 rounded-full transition-transform duration-150 ${
                              isHovered ? "scale-125" : ""
                            }`}
                            style={{ backgroundColor: seg.color }}
                          />
                          <span className="font-medium text-slate-600">
                            {seg.shortLabel}
                          </span>
                        </span>
                        <span className="font-bold text-[#071d36]">
                          {seg.count}
                        </span>
                      </button>
                    );
                  })}
              </div>
            </div>

            {/* KPIs + Barra Horizontal Empilhada Animada */}
            <div className="space-y-3.5 lg:col-span-7">
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                {/* KPI 1: Total Anterior */}
                <div
                  className={`rounded-xl border border-slate-200/80 bg-white p-3 shadow-2xs ${
                    isPerf
                      ? ""
                      : "transition-all duration-200 hover:-translate-y-0.5 hover:border-slate-300 hover:shadow-md"
                  }`}
                >
                  <div className="flex items-center justify-between text-[11px] font-semibold text-slate-500">
                    <span>Anterior</span>
                    <span className="grid h-6 w-6 place-items-center rounded-lg bg-slate-100 text-slate-500">
                      <Clock className="h-3.5 w-3.5" />
                    </span>
                  </div>
                  <div className="mt-1.5 text-xl font-extrabold text-[#071d36]">
                    {stats.baseComparacao}
                  </div>
                  <div className="text-[10.5px] text-slate-400">
                    NCs monitoradas
                  </div>
                </div>

                {/* KPI 2: Parciais (sincroniza hover com o gráfico) */}
                <div
                  onMouseEnter={() => setHoveredStatus("parciais")}
                  onMouseLeave={() => setHoveredStatus(null)}
                  className={`cursor-pointer rounded-xl border bg-white p-3 shadow-2xs ${
                    hoveredStatus === "parciais"
                      ? "border-indigo-400 ring-2 ring-indigo-500/15"
                      : "border-slate-200/80"
                  } ${
                    isPerf
                      ? ""
                      : "transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md"
                  }`}
                >
                  <div className="flex items-center justify-between text-[11px] font-semibold text-slate-500">
                    <span>Parciais</span>
                    <span className="grid h-6 w-6 place-items-center rounded-lg bg-indigo-50 text-indigo-600">
                      <FileCheck2 className="h-3.5 w-3.5" />
                    </span>
                  </div>
                  <div className="mt-1.5 text-xl font-extrabold text-indigo-600">
                    {stats.parcialmenteSanadas}
                  </div>
                  <div className="text-[10.5px] text-slate-400">
                    {stats.pctParciais}% em andamento
                  </div>
                </div>

                {/* KPI 3: Sanadas (sincroniza hover com o gráfico) */}
                <div
                  onMouseEnter={() => setHoveredStatus("sanadas")}
                  onMouseLeave={() => setHoveredStatus(null)}
                  className={`cursor-pointer rounded-xl border bg-white p-3 shadow-2xs ${
                    hoveredStatus === "sanadas"
                      ? "border-emerald-400 ring-2 ring-emerald-500/15"
                      : "border-slate-200/80"
                  } ${
                    isPerf
                      ? ""
                      : "transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md"
                  }`}
                >
                  <div className="flex items-center justify-between text-[11px] font-semibold text-slate-500">
                    <span>Sanadas</span>
                    <span className="grid h-6 w-6 place-items-center rounded-lg bg-emerald-50 text-emerald-600">
                      <CheckCircle2 className="h-3.5 w-3.5" />
                    </span>
                  </div>
                  <div className="mt-1.5 text-xl font-extrabold text-emerald-600">
                    {stats.sanadas}
                  </div>
                  <div className="text-[10.5px] text-slate-400">
                    {stats.pctSanadas}% solucionadas
                  </div>
                </div>

                {/* KPI 4: Pendentes (sincroniza hover com o gráfico e usa cor do tema) */}
                <div
                  onMouseEnter={() => setHoveredStatus("pendentes")}
                  onMouseLeave={() => setHoveredStatus(null)}
                  style={
                    hoveredStatus === "pendentes"
                      ? {
                          borderColor: theme.primary,
                          boxShadow: `0 4px 14px -4px ${theme.primary}33`,
                        }
                      : undefined
                  }
                  className={`cursor-pointer rounded-xl border border-slate-200/80 bg-white p-3 shadow-2xs ${
                    isPerf
                      ? ""
                      : "transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md"
                  }`}
                >
                  <div className="flex items-center justify-between text-[11px] font-semibold text-slate-500">
                    <span>Pendentes</span>
                    <span
                      className="grid h-6 w-6 place-items-center rounded-lg"
                      style={{
                        backgroundColor: `${theme.primary}15`,
                        color: theme.primary,
                      }}
                    >
                      <AlertTriangle className="h-3.5 w-3.5" />
                    </span>
                  </div>
                  <div
                    className="mt-1.5 text-xl font-extrabold"
                    style={{ color: theme.primary }}
                  >
                    {stats.pendentes}
                  </div>
                  <div className="text-[10.5px] text-slate-400">
                    {stats.pctPendentes}% pendentes
                  </div>
                </div>
              </div>

              {/* Barra horizontal empilhada com animação de preenchimento e hover sincronizado */}
              <div className="rounded-xl border border-slate-200/80 bg-white px-4 py-3 shadow-2xs">
                <div className="mb-2 flex items-center justify-between text-[11px] font-semibold text-slate-600">
                  <span>Distribuição sobre o Monitoramento Anterior</span>
                  <span className="text-[#071d36]">
                    {activeSegment
                      ? `${activeSegment.label}: ${activeSegment.count} (${activeSegment.pct}%)`
                      : `${stats.sanadas} sanada(s) · ${stats.totalPendentesConclusao} pendente(s)`}
                  </span>
                </div>
                <div className="flex h-3 w-full overflow-hidden rounded-full bg-slate-100 p-0.5 ring-1 ring-slate-200/70">
                  {segments.map((seg, idx) => {
                    if (seg.pct <= 0) return null;
                    const isHovered = hoveredStatus === seg.key;
                    const isDimmed = hoveredStatus !== null && !isHovered;

                    return (
                      <motion.div
                        key={seg.key}
                        initial={{ width: isPerf ? `${seg.pct}%` : "0%" }}
                        animate={{
                          width: `${seg.pct}%`,
                          opacity: isDimmed ? 0.3 : 1,
                        }}
                        transition={{
                          width: {
                            ...chartTransition,
                            delay: isPerf ? 0 : idx * 0.06,
                          },
                          opacity: { duration: isPerf ? 0 : 0.18 },
                        }}
                        onMouseEnter={() => setHoveredStatus(seg.key)}
                        onMouseLeave={() => setHoveredStatus(null)}
                        style={{ backgroundColor: seg.color }}
                        className={`h-full cursor-pointer first:rounded-l-full last:rounded-r-full transition-transform duration-150 ${
                          isHovered ? "scale-y-110 brightness-105" : ""
                        }`}
                        title={`${seg.label}: ${seg.count} (${seg.pct}%)`}
                      />
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 2. Campo Recomendações à SOCICAM (destinado à Seção 5 - Conclusão) */}
        <div className="space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <label
              htmlFor="campo-recomendacoes-socicam"
              className="flex items-center gap-2 text-sm font-bold text-[#071d36]"
            >
              <MessageSquareText
                className="h-4 w-4"
                style={{ color: theme.primary }}
              />
              <span>Recomendações à SOCICAM</span>
            </label>
            <span
              className="rounded-lg px-2.5 py-0.5 text-[11px] font-semibold ring-1"
              style={{
                backgroundColor: theme.lightBg,
                color: theme.primary,
                borderColor: theme.lightBorder,
              }}
            >
              Inserido na Seção 5 · Conclusões e Recomendações
            </span>
          </div>

          <textarea
            id="campo-recomendacoes-socicam"
            rows={3}
            value={recomendacaoText}
            onChange={handleChangeRecomendacao}
            onFocus={() => setTextareaFocused(true)}
            onBlur={() => setTextareaFocused(false)}
            placeholder="Descreva as recomendações à SOCICAM que complementarão o parágrafo conclusivo (ex.: devendo a Concessionária apresentar cronograma executivo para saneamento imediato das pendências)..."
            style={
              textareaFocused
                ? {
                    borderColor: theme.primary,
                    boxShadow: `0 0 0 3px ${theme.primary}22`,
                  }
                : undefined
            }
            className="w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-800 shadow-xs transition-all duration-150 focus:outline-none"
          />
        </div>
      </div>
    </Card>
  );
};
