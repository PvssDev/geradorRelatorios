import { FiscalizacaoItem, RegistroNcItem } from "../../types/report.types";
import { getStateKey } from "../domain/reportCodingRules";
import type { ReportStore } from "../types";

/**
 * Gera massa de dados de teste/demonstração para a modalidade ativa.
 */
export function buildAutoFillPatch(state: ReportStore) {
  const key = getStateKey(state.tipoRelatorio, state.categoriaRelatorio);
  const ws = state.workspaces[key];
  const tipoRel = state.tipoRelatorio;
  const isMon = state.categoriaRelatorio === "Monitoramento";

  const contrato = state.contratosPadrao[tipoRel];
  const respNomes =
    state.responsaveis.length > 0
      ? state.responsaveis.map((r) => r.nome).join(", ")
      : "=Pessoal Responsável=";
  const coordNome =
    state.coordenadores.length > 0 ? state.coordenadores[0].nome : "=Coordenador=";

  const todayBr = new Date().toLocaleDateString("pt-BR");
  const year = new Date().getFullYear();
  const idPadrao = `${isMon ? "MON" : "FISC"}-${tipoRel}-${year}-001`;
  const cidadePadrao =
    tipoRel === "CRA"
      ? "Cabo de Santo Agostinho / Ipojuca"
      : tipoRel === "CRC"
      ? "Cabo de Santo Agostinho (Reserva do Paiva)"
      : "Recife";
  const localReal =
    tipoRel === "CRA"
      ? "Rota do Atlântico"
      : tipoRel === "CRC"
      ? "Sistema Viário do Paiva"
      : state.locaisSocicam[5] || "TIP Recife";

  const nextFisc = [...ws.fiscalizacoes];
  let idVinculo = "";
  let terminalNc = localReal;

  if (nextFisc.length === 0 || !nextFisc[0]["ID da Fiscalização"].trim()) {
    idVinculo = idPadrao;
    const headerObj: FiscalizacaoItem = {
      "ID da Fiscalização": idVinculo,
      Data: todayBr,
      Hora: tipoRel === "CRA" ? "09:30" : "",
      Cidade: tipoRel === "CRA" ? cidadePadrao : "",
      Local: localReal,
      "Pessoal Responsável": respNomes,
      Coordenador: coordNome,
      Contrato: contrato,
      Período: todayBr,
      "Relatório Gerado": false,
    };
    if (nextFisc.length === 0) {
      nextFisc.push(headerObj);
    } else {
      nextFisc[0] = headerObj;
    }
  } else {
    const activeIdx = Math.max(
      0,
      Math.min(ws.activeFiscalizacaoIndex, nextFisc.length - 1)
    );
    idVinculo = nextFisc[activeIdx]["ID da Fiscalização"];
    terminalNc = nextFisc[activeIdx].Local || localReal;
  }

  const nextNcs: RegistroNcItem[] = [];

  if (isMon && ws.oldPhotosToMatch.length > 0) {
    ws.oldPhotosToMatch.forEach((item, idx) => {
      const fotoNova =
        ws.photos.length > 0 ? ws.photos[idx % ws.photos.length].name : "";
      const posLabel =
        tipoRel === "SOCICAM"
          ? "=INFORMAÇÃO SOCICAM="
          : tipoRel === "CRA"
          ? "=POSICIONAMENTO CRA="
          : "=POSICIONAMENTO CRC=";

      nextNcs.push({
        "ID da Fiscalização": idVinculo,
        "Nº": idx + 1,
        Terminal: terminalNc,
        Pista: item.pista || (tipoRel === "SOCICAM" ? "" : "=Pista="),
        Trecho: item.trecho || (tipoRel === "SOCICAM" ? "" : "=Trecho="),
        "Não Conformidade": item.id_nc || `=Identificação ${idx + 1}=`,
        "Ponto de Atenção": "",
        Foto: fotoNova,
        "Foto Anterior": item.old_photo_path || "",
        "Legenda Anterior": item.old_legend || "",
        "Legenda da Foto": "=legenda da foto atual=",
        Observações: item.constatacao || "=CONSTATAÇÃO=",
        Identificação: item.id_nc || `=Identificação ${idx + 1}=`,
        "Direção (faixa)": "",
        "Fundamento da infração": "",
        Determinação: posLabel,
        Situação: "Pendente",
        "Análise ARPE": "=ANÁLISE ARPE=",
        is_relacionado: false,
        grupo_relacao: `grp_auto_${idx + 1}`,
      });
    });
  } else if (ws.photos.length > 0) {
    ws.photos.forEach((photo, idx) => {
      const seqStr = String(idx + 1).padStart(3, "0");
      const codPadrao =
        tipoRel === "CRA"
          ? `CRA.ST601.2794-2834/${year}.${seqStr}`
          : tipoRel === "CRC"
          ? `CRC.SH015.0646+0648/${year}.${seqStr}`
          : "=Identificação=";
      nextNcs.push({
        "ID da Fiscalização": idVinculo,
        "Nº": idx + 1,
        Terminal: terminalNc,
        Pista: tipoRel === "CRA" ? "Sul" : "",
        Trecho: tipoRel === "CRA" ? "KM 29,08 - 29,14" : "",
        "Não Conformidade": tipoRel === "SOCICAM" ? "SINALIZAÇÃO" : "FI",
        "Ponto de Atenção": "",
        Foto: photo.name,
        "Foto Anterior": "",
        "Legenda Anterior": "",
        "Legenda da Foto": isMon ? "=legenda da foto atual=" : undefined,
        Observações: isMon ? "=CONSTATAÇÃO=" : "=Observações=",
        Identificação: codPadrao,
        "Direção (faixa)":
          tipoRel === "CRA" ? (idx % 2 === 0 ? "Direita" : "Esquerda") : "",
        "Fundamento da infração": "=Fundamento da infração=",
        Determinação: isMon
          ? tipoRel === "SOCICAM"
            ? "=INFORMAÇÃO SOCICAM="
            : `=POSICIONAMENTO ${tipoRel}=`
          : "=Determinação=",
        Situação: "Pendente",
        "Análise ARPE": isMon ? "=ANÁLISE ARPE=" : "",
        is_relacionado: false,
        grupo_relacao: `grp_auto_${idx + 1}`,
      });
    });
  } else {
    const codPadrao =
      tipoRel === "CRA"
        ? `CRA.ST601.2794-2834/${year}.001`
        : tipoRel === "CRC"
        ? `CRC.SH015.0646+0648/${year}.001`
        : "=Identificação=";
    nextNcs.push({
      "ID da Fiscalização": idVinculo,
      "Nº": 1,
      Terminal: terminalNc,
      Pista: tipoRel === "CRA" ? "Sul" : "",
      Trecho: tipoRel === "CRA" ? "KM 29,08 - 29,14" : "",
      "Não Conformidade": tipoRel === "SOCICAM" ? "SINALIZAÇÃO" : "FI",
      "Ponto de Atenção": "",
      Foto: "",
      "Foto Anterior": "",
      "Legenda Anterior": "",
      "Legenda da Foto": isMon ? "=legenda da foto atual=" : undefined,
      Observações: isMon ? "=CONSTATAÇÃO=" : "=Observações=",
      Identificação: codPadrao,
      "Direção (faixa)": tipoRel === "CRA" ? "Direita" : "",
      "Fundamento da infração": "=Fundamento da infração=",
      Determinação: isMon
        ? tipoRel === "SOCICAM"
          ? "=INFORMAÇÃO SOCICAM="
          : `=POSICIONAMENTO ${tipoRel}=`
        : "=Determinação=",
      Situação: "Pendente",
      "Análise ARPE": isMon ? "=ANÁLISE ARPE=" : "",
      is_relacionado: false,
      grupo_relacao: "grp_auto_1",
    });
  }

  return {
    workspaces: {
      ...state.workspaces,
      [key]: {
        ...ws,
        fiscalizacoes: nextFisc,
        registrosNc: nextNcs,
        relatoriosGerados: [],
      },
    },
  };
}

