import {
  CategoriaRelatorio,
  MonitoramentoAnteriorItem,
  RegistroNcItem,
  SortOption,
  StateKey,
  TipoRelatorio,
  UploadedPhotoItem,
} from "../../types/report.types";
import { compararNomesNatural } from "../../services/naturalSort";

export function getStateKey(
  tipo: TipoRelatorio,
  categoria: CategoriaRelatorio
): StateKey {
  return `${tipo}_${categoria}`;
}

/**
 * Busca circularmente o próximo índice disponível a partir de `currentIdx`.
 * Caso todos os itens já estejam utilizados, avança para `(currentIdx + 1) % items.length`.
 */
export function findNextCircularIndex<T>(
  items: T[],
  currentIdx: number,
  isUsed: (item: T) => boolean
): number {
  const total = items.length;
  if (total <= 1) return 0;
  const safeIdx = Math.max(0, Math.min(currentIdx, total - 1));
  for (let offset = 1; offset <= total; offset++) {
    const candidateIdx = (safeIdx + offset) % total;
    if (!isUsed(items[candidateIdx])) {
      return candidateIdx;
    }
  }
  return (safeIdx + 1) % total;
}

export function calcularCodificacaoCra(
  baseInput: string,
  dataFisc?: string,
  seqIdx: number = 1
): string {
  if (!baseInput || !baseInput.trim()) return "";
  const baseLimpa = baseInput.trim();
  const matchAno = dataFisc?.match(/\b(20\d{2})\b/);
  const anoPadrao = matchAno ? matchAno[1] : String(new Date().getFullYear());

  if (baseLimpa.includes("/")) {
    const [base, sufixo] = baseLimpa.split("/", 2);
    const m = sufixo.trim().match(/^(\d{4})\.(\d+)$/);
    if (m) {
      const ano = m[1];
      const offsetInicial = parseInt(m[2], 10);
      const numFinal = offsetInicial + (seqIdx - 1);
      return `${base.trim()}/${ano}.${String(numFinal).padStart(3, "0")}`;
    }
    const mAno = sufixo.trim().match(/^(\d{4})$/);
    if (mAno) {
      return `${base.trim()}/${mAno[1]}.${String(seqIdx).padStart(3, "0")}`;
    }
    return `${base.trim()}/${anoPadrao}.${String(seqIdx).padStart(3, "0")}`;
  }

  return `${baseLimpa}/${anoPadrao}.${String(seqIdx).padStart(3, "0")}`;
}

export function combinarFaixasRelacionadas(
  faixa1?: string,
  faixa2?: string
): { sigla: string; extenso: string } {
  const f1 = (faixa1 || "").trim().toUpperCase();
  const f2 = (faixa2 || "").trim().toUpperCase();

  const temEsq1 = f1.includes("ESQ") || f1 === "FE" || f1 === "E";
  const temDir1 = f1.includes("DIR") || f1 === "FD" || f1 === "D";
  const temEsq2 = f2.includes("ESQ") || f2 === "FE" || f2 === "E";
  const temDir2 = f2.includes("DIR") || f2 === "FD" || f2 === "D";

  const temEsq = temEsq1 || temEsq2;
  const temDir = temDir1 || temDir2;

  if (temEsq && temDir) {
    return { sigla: "FED", extenso: "Esquerda e Direita" };
  }
  if (temEsq) {
    return { sigla: "FE", extenso: "Esquerda" };
  }
  if (temDir) {
    return { sigla: "FD", extenso: "Direita" };
  }
  return { sigla: f1 || f2, extenso: faixa1 || faixa2 || "" };
}

export function obterProximoSequencialCra(
  registros: RegistroNcItem[],
  idVinculo: string,
  tipoRegistro: "Não Conformidade" | "Ponto de Atenção"
): number {
  const campoFiltro =
    tipoRegistro === "Não Conformidade" ? "Não Conformidade" : "Ponto de Atenção";
  const recsTipo = registros.filter(
    (nc) =>
      nc["ID da Fiscalização"] === idVinculo &&
      Boolean(nc[campoFiltro]?.trim())
  );

  let maxNum = 0;
  for (const r of recsTipo) {
    const cod = (r.Codificação || r.Identificação || r.Trecho || "").trim();
    const m = cod.match(/\/(\d{4})\.(\d+)$/);
    if (m) {
      const num = parseInt(m[2], 10);
      if (!isNaN(num) && num > maxNum) maxNum = num;
    }
  }

  return maxNum > 0 ? maxNum + 1 : recsTipo.length + 1;
}

export function derivarProximaCodificacao(codBase: string): string {
  if (!codBase || !codBase.trim()) return "";
  const trimmed = codBase.trim();

  // Caso 1: Padrão CRA / CRC com barra e ano: ex. CRA.ST601.2794-2834/2026.001 -> .../2026.002
  const matchAnoSeq = trimmed.match(/^(.*?[\/.])(\d{4})\.(\d+)$/);
  if (matchAnoSeq) {
    const prefix = matchAnoSeq[1];
    const ano = matchAnoSeq[2];
    const seqStr = matchAnoSeq[3];
    const nextSeq = Number(seqStr) + 1;
    return `${prefix}${ano}.${String(nextSeq).padStart(seqStr.length, "0")}`;
  }

  // Caso 2: Padrão SOCICAM ou geral com ponto e sequência final: ex. SOCICAM.2026.001 ou NC.001
  const matchPontoSeq = trimmed.match(/^(.*[\/.])(\d+)$/);
  if (matchPontoSeq) {
    const prefix = matchPontoSeq[1];
    const seqStr = matchPontoSeq[2];
    const nextSeq = Number(seqStr) + 1;
    return `${prefix}${String(nextSeq).padStart(seqStr.length, "0")}`;
  }

  // Caso 3: Padrão textual com espaço ou traço no final: ex. "NC 01" -> "NC 02"
  const matchEspacoSeq = trimmed.match(/^(.*\D)(\d+)$/);
  if (matchEspacoSeq) {
    const prefix = matchEspacoSeq[1];
    const seqStr = matchEspacoSeq[2];
    const nextSeq = Number(seqStr) + 1;
    return `${prefix}${String(nextSeq).padStart(seqStr.length, "0")}`;
  }

  return trimmed;
}

export function sortPhotosList(
  photos: UploadedPhotoItem[],
  sortOption: SortOption
): UploadedPhotoItem[] {
  const copy = [...photos];
  if (sortOption === "Nome (A-Z / 0-9)") {
    copy.sort((a, b) => compararNomesNatural(a.name, b.name));
  } else if (sortOption === "Nome (Z-A / 9-0)") {
    copy.sort((a, b) => compararNomesNatural(b.name, a.name));
  } else {
    copy.sort((a, b) => a.uploadOrder - b.uploadOrder);
  }
  return copy;
}

export function deduplicarItensExtraidosMonitoramento(
  items: MonitoramentoAnteriorItem[]
): MonitoramentoAnteriorItem[] {
  const usedIds = new Set<string>();
  const usedPhotoNames = new Set<string>();

  return items.map((item) => {
    const rawId = (item.id_nc || "FOTO").trim();
    let uniqueId = rawId;
    if (usedIds.has(uniqueId.toLowerCase())) {
      let n = 1;
      while (usedIds.has(`${rawId}(${n})`.toLowerCase())) {
        n += 1;
      }
      uniqueId = `${rawId}(${n})`;
    }
    usedIds.add(uniqueId.toLowerCase());

    let uniquePhotoPath = item.old_photo_path || "";
    if (uniquePhotoPath) {
      const dotIdx = uniquePhotoPath.lastIndexOf(".");
      const base = dotIdx > 0 ? uniquePhotoPath.slice(0, dotIdx) : uniquePhotoPath;
      const ext = dotIdx > 0 ? uniquePhotoPath.slice(dotIdx) : "";
      let candidate = uniquePhotoPath;
      if (usedPhotoNames.has(candidate.toLowerCase())) {
        let n = 1;
        while (usedPhotoNames.has(`${base}(${n})${ext}`.toLowerCase())) {
          n += 1;
        }
        candidate = `${base}(${n})${ext}`;
      }
      usedPhotoNames.add(candidate.toLowerCase());
      uniquePhotoPath = candidate;
    }

    return {
      ...item,
      id_nc: uniqueId,
      old_photo_path: uniquePhotoPath,
      display_label:
        item.display_label && uniqueId !== rawId
          ? item.display_label === rawId
            ? uniqueId
            : `${item.display_label} (${uniqueId.slice(rawId.length + 1, -1)})`
          : item.display_label,
    };
  });
}

