export function formatNomeAbreviado(
  nomeCompleto: string,
  compactar: boolean
): string {
  if (!compactar) return nomeCompleto;
  const partes = nomeCompleto.trim().split(/\s+/);
  if (partes.length <= 1) return nomeCompleto;
  const primeiro = partes[0];
  const ultimo = partes[partes.length - 1];
  return `${primeiro} ${ultimo.charAt(0)}.`;
}

export function getTodayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

export function isoToBr(iso: string): string {
  if (!iso) return "";
  const parts = iso.split("-");
  return parts.length === 3 ? `${parts[2]}/${parts[1]}/${parts[0]}` : iso;
}

export function brToIso(br: string): string {
  if (!br || br.startsWith("=")) return getTodayIso();
  const parts = br.split("/");
  return parts.length === 3 ? `${parts[2]}-${parts[1]}-${parts[0]}` : getTodayIso();
}

export function formatarPeriodoVistoria(
  inicioIso: string,
  fimIso: string
): string {
  if (!inicioIso) return "";
  if (!fimIso || fimIso === inicioIso) {
    return isoToBr(inicioIso);
  }
  const [y1, m1, d1] = inicioIso.split("-");
  const [y2, m2, d2] = fimIso.split("-");
  if (!y1 || !y2) return isoToBr(inicioIso);

  if (y1 !== y2) {
    return `${d1}/${m1}/${y1} a ${d2}/${m2}/${y2}`;
  }
  if (m1 !== m2) {
    return `${d1}/${m1} a ${d2}/${m2}/${y2}`;
  }
  return `${d1} a ${d2}/${m2}/${y2}`;
}

export function desmembrarPeriodoEmDatas(
  periodoStr: string,
  fallbackDataIso: string
): { inicioIso: string; fimIso: string } {
  if (!periodoStr || periodoStr.trim() === "" || periodoStr.startsWith("=")) {
    return { inicioIso: fallbackDataIso, fimIso: fallbackDataIso };
  }
  const s = periodoStr.trim();

  // 1. "DD a DD/MM/AAAA"
  const m1 = s.match(
    /^(\d{1,2})\s*(?:a|à|-|e)\s*(\d{1,2})\/(\d{1,2})\/(\d{4})$/
  );
  if (m1) {
    const [, d1, d2, m, y] = m1;
    return {
      inicioIso: `${y}-${m.padStart(2, "0")}-${d1.padStart(2, "0")}`,
      fimIso: `${y}-${m.padStart(2, "0")}-${d2.padStart(2, "0")}`,
    };
  }

  // 2. "DD/MM a DD/MM/AAAA"
  const m2 = s.match(
    /^(\d{1,2})\/(\d{1,2})\s*(?:a|à|-|e)\s*(\d{1,2})\/(\d{1,2})\/(\d{4})$/
  );
  if (m2) {
    const [, d1, m1Val, d2, m2Val, y] = m2;
    return {
      inicioIso: `${y}-${m1Val.padStart(2, "0")}-${d1.padStart(2, "0")}`,
      fimIso: `${y}-${m2Val.padStart(2, "0")}-${d2.padStart(2, "0")}`,
    };
  }

  // 3. "DD/MM/AAAA a DD/MM/AAAA"
  const m3 = s.match(
    /^(\d{1,2})\/(\d{1,2})\/(\d{4})\s*(?:a|à|-|e)\s*(\d{1,2})\/(\d{1,2})\/(\d{4})$/
  );
  if (m3) {
    const [, d1, m1Val, y1, d2, m2Val, y2] = m3;
    return {
      inicioIso: `${y1}-${m1Val.padStart(2, "0")}-${d1.padStart(2, "0")}`,
      fimIso: `${y2}-${m2Val.padStart(2, "0")}-${d2.padStart(2, "0")}`,
    };
  }

  // 4. "DD/MM/AAAA"
  const m4 = s.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
  if (m4) {
    const [, d, m, y] = m4;
    const iso = `${y}-${m.padStart(2, "0")}-${d.padStart(2, "0")}`;
    return { inicioIso: iso, fimIso: iso };
  }

  return { inicioIso: fallbackDataIso, fimIso: fallbackDataIso };
}

