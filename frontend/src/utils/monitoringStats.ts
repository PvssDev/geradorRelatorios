import {
  MonitoramentoAnteriorItem,
  MonitoramentoAnteriorMeta,
  RegistroNcItem,
} from "../types/report.types";

export interface MonitoringStatsSummary {
  /** Total de NCs extraídas do relatório de monitoramento/fiscalização anterior */
  totalAnterior: number;
  /** Base de comparação (maior valor entre totalAnterior e registradas) */
  baseComparacao: number;
  /** Quantidade de NCs únicas avaliadas/registradas na sessão atual */
  registradas: number;
  /** Quantidade de NCs do relatório anterior que ainda não foram registradas */
  naoRegistradas: number;
  /** Quantidade de NCs com Situação === "Sanada" */
  sanadas: number;
  /** Quantidade de NCs com Situação === "Parcialmente Sanada" */
  parcialmenteSanadas: number;
  /** Quantidade de NCs com Situação === "Pendente" */
  pendentes: number;
  /** Soma das que permanecem sem solução definitiva (Pendentes + Parcialmente Sanadas) */
  totalPendentesConclusao: number;
  /** Percentuais em relação à baseComparacao (0 a 100) */
  pctSanadas: number;
  pctParciais: number;
  pctPendentes: number;
  pctNaoRegistradas: number;
  pctCobertura: number;
}

/**
 * Calcula estatísticas reais comparativas entre o relatório anterior e os registros atuais
 * do monitoramento, sem efeitos colaterais (função pura).
 */
export function calcularEstatisticasMonitoramento(
  activeRegs: RegistroNcItem[],
  oldItems: MonitoramentoAnteriorItem[] = [],
  prevMeta: MonitoramentoAnteriorMeta | null = null
): MonitoringStatsSummary {
  // Filtra apenas ocorrências principais (ignora fotos extras vinculadas via is_relacionado)
  const principais = activeRegs.filter(
    (r) => !r.is_relacionado && (r["Não Conformidade"] || "").trim() !== ""
  );

  const registradas = principais.length;
  const metaPendencias = Number(prevMeta?.total_pendencias_extraidas || 0);
  const oldItemsCount = oldItems.length;
  const rawAnterior = oldItemsCount > 0 ? oldItemsCount : metaPendencias;

  const totalAnterior = rawAnterior > 0 ? rawAnterior : registradas;
  const baseComparacao = Math.max(totalAnterior, registradas, 1);

  let sanadas = 0;
  let parcialmenteSanadas = 0;
  let pendentes = 0;

  for (const reg of principais) {
    const sit = (reg.Situação || "Pendente").trim();
    if (sit === "Sanada") {
      sanadas += 1;
    } else if (sit === "Parcialmente Sanada") {
      parcialmenteSanadas += 1;
    } else {
      pendentes += 1;
    }
  }

  const naoRegistradas = Math.max(0, totalAnterior - registradas);
  const totalPendentesConclusao = pendentes + parcialmenteSanadas;

  const hasData = totalAnterior > 0 || registradas > 0;
  const pctSanadas = hasData ? Math.round((sanadas / baseComparacao) * 100) : 0;
  const pctParciais = hasData
    ? Math.round((parcialmenteSanadas / baseComparacao) * 100)
    : 0;
  const pctPendentes = hasData ? Math.round((pendentes / baseComparacao) * 100) : 0;
  const pctNaoRegistradas = hasData
    ? Math.max(0, 100 - pctSanadas - pctParciais - pctPendentes)
    : 0;
  const pctCobertura =
    totalAnterior > 0
      ? Math.min(100, Math.round((registradas / totalAnterior) * 100))
      : registradas > 0
      ? 100
      : 0;

  return {
    totalAnterior,
    baseComparacao: hasData ? Math.max(totalAnterior, registradas) : 0,
    registradas,
    naoRegistradas,
    sanadas,
    parcialmenteSanadas,
    pendentes,
    totalPendentesConclusao,
    pctSanadas,
    pctParciais,
    pctPendentes,
    pctNaoRegistradas,
    pctCobertura,
  };
}

