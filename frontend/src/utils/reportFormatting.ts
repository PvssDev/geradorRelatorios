/**
 * Utilitários puros de formatação compartilhados entre modais e painéis de resumo.
 */

export function contrairCodificacoes(cod1: string, cod2: string): string {
  const c1 = cod1.trim().replace(/\.$/, "");
  const c2 = cod2.trim().replace(/\.$/, "");
  if (!c1 && !c2) return "";
  if (!c1) return `${c2}.`;
  if (!c2 || c1 === c2) return `${c1}.`;

  const lastDot1 = c1.lastIndexOf(".");
  const lastDot2 = c2.lastIndexOf(".");
  if (
    lastDot1 > 0 &&
    lastDot1 === lastDot2 &&
    c1.slice(0, lastDot1) === c2.slice(0, lastDot2)
  ) {
    const prefix = c1.slice(0, lastDot1 + 1);
    const suf1 = c1.slice(lastDot1 + 1);
    const suf2 = c2.slice(lastDot2 + 1);
    return `${prefix}${suf1} e ${suf2}.`;
  }
  return `${c1} e ${c2}.`;
}

export function resolverSiglaFaixaCombinada(
  faixa1?: string,
  faixa2?: string
): string {
  const combinado = `${faixa1 || ""} ${faixa2 || ""}`.toLowerCase();
  const temEsq = combinado.includes("esq");
  const temDir = combinado.includes("dir");
  if (temEsq && temDir) return "FED";
  if (temEsq) return "FE";
  if (temDir) return "FD";
  return "";
}

export function contarItensAchado(valor?: string): number {
  if (!valor) return 0;
  return valor
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean).length;
}

export function contarAchadosUnicosNoGrupo(
  registros: ReadonlyArray<Record<string, unknown>>,
  campo: "Não Conformidade" | "Ponto de Atenção"
): number {
  const unicos = new Set<string>();
  registros.forEach((r) => {
    const val = String(r[campo] || "");
    val
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean)
      .forEach((s) => unicos.add(s.toLowerCase()));
  });
  return unicos.size;
}

