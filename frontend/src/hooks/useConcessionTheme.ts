import { useReportStore } from "../store/useReportStore";
import { ConcessionTheme, getConcessionTheme } from "../utils/concessionTheme";

/**
 * Hook centralizado para obter o tema dinâmico do relatório ativo (CRA, CRC, SOCICAM x Fiscalização, Monitoramento).
 */
export function useConcessionTheme(): ConcessionTheme {
  const tipoRelatorio = useReportStore((s) => s.tipoRelatorio);
  const categoriaRelatorio = useReportStore((s) => s.categoriaRelatorio);
  return getConcessionTheme(tipoRelatorio, categoriaRelatorio);
}

