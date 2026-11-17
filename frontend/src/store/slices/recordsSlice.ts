import type { StateCreator } from "zustand";
import { RegistroNcItem } from "../../types/report.types";
import { buildAutoFillPatch } from "../demo/autoFillFixtures";
import {
  calcularCodificacaoCra,
  combinarFaixasRelacionadas,
  derivarProximaCodificacao,
  findNextCircularIndex,
  getStateKey,
  obterProximoSequencialCra,
} from "../domain/reportCodingRules";
import type { RecordsSlice, ReportStore } from "../types";

export const createRecordsSlice: StateCreator<
  ReportStore,
  [],
  [],
  RecordsSlice
> = (set, get) => ({
  setPistaPersistida: (val) =>
    set((state) => {
      const key = getStateKey(state.tipoRelatorio, state.categoriaRelatorio);
      const ws = state.workspaces[key];
      return {
        workspaces: {
          ...state.workspaces,
          [key]: { ...ws, pistaPersistida: val },
        },
      };
    }),

  setTrechoPersistido: (val) =>
    set((state) => {
      const key = getStateKey(state.tipoRelatorio, state.categoriaRelatorio);
      const ws = state.workspaces[key];
      return {
        workspaces: {
          ...state.workspaces,
          [key]: { ...ws, trechoPersistido: val },
        },
      };
    }),

  addOrUpdateRegistroNc: (rec, advancePhoto = true) =>
    set((state) => {
      const key = getStateKey(state.tipoRelatorio, state.categoriaRelatorio);
      const ws = state.workspaces[key];
      const isMon = state.categoriaRelatorio === "Monitoramento";
      const nextNcs = [...ws.registrosNc];

      const recFotoLower = (rec.Foto || "").trim().toLowerCase();
      if (
        recFotoLower &&
        nextNcs.some((r) => (r.Foto || "").trim().toLowerCase() === recFotoLower)
      ) {
        return state;
      }

      if (isMon && ws.oldPhotosToMatch.length > 0) {
        const alreadyAudited = nextNcs.some(
          (r) =>
            !r.is_relacionado &&
            (r.Identificação === rec.Identificação ||
              (Boolean(rec["Foto Anterior"]) &&
                r["Foto Anterior"] === rec["Foto Anterior"])) &&
            r["ID da Fiscalização"] === rec["ID da Fiscalização"]
        );
        if (alreadyAudited) {
          return state;
        }
      }

      const countForId = nextNcs.filter(
        (r) => r["ID da Fiscalização"] === rec["ID da Fiscalização"]
      ).length;
      const novoNum = countForId + 1;
      nextNcs.push({
        ...rec,
        "Nº": novoNum,
        is_relacionado: false,
        grupo_relacao:
          rec.grupo_relacao ||
          `grp_${rec["ID da Fiscalização"]}_${novoNum}_${Date.now()}`,
      });

      // Avanço automático circular do carrossel
      let nextCarouselIdx = ws.carouselIndex;
      let nextMonitoringNewPhotoName = state.monitoringNewPhotoName;
      if (advancePhoto && state.autoAdvanceActive) {
        const usedNewPhotos = new Set(
          nextNcs
            .map((r) => (r.Foto || "").trim().toLowerCase())
            .filter(Boolean)
        );

        if (isMon) {
          if (ws.oldPhotosToMatch.length > 0) {
            const auditedOldIds = new Set(
              nextNcs
                .filter((r) => !r.is_relacionado && r.Identificação)
                .map((r) => r.Identificação)
            );
            nextCarouselIdx = findNextCircularIndex(
              ws.oldPhotosToMatch,
              nextCarouselIdx,
              (item) => auditedOldIds.has(item.id_nc)
            );
          }
          if (ws.photos.length > 0) {
            const currentPhotoName =
              state.monitoringNewPhotoName || rec.Foto || ws.photos[0].name;
            const currNewIdx = ws.photos.findIndex(
              (p) => p.name === currentPhotoName
            );
            const resolvedIdx = currNewIdx >= 0 ? currNewIdx : 0;
            const nextNewIdx = findNextCircularIndex(
              ws.photos,
              resolvedIdx,
              (p) => usedNewPhotos.has(p.name.trim().toLowerCase())
            );
            nextMonitoringNewPhotoName = ws.photos[nextNewIdx].name;
          }
        } else if (ws.photos.length > 0) {
          nextCarouselIdx = findNextCircularIndex(
            ws.photos,
            nextCarouselIdx,
            (p) => usedNewPhotos.has(p.name.trim().toLowerCase())
          );
        }
      }

      return {
        monitoringNewPhotoName: nextMonitoringNewPhotoName,
        workspaces: {
          ...state.workspaces,
          [key]: {
            ...ws,
            registrosNc: nextNcs,
            carouselIndex: nextCarouselIdx,
            relatoriosGerados: [],
          },
        },
      };
    }),

  relacionarFotoUltimaNc: (fotoName, situacao = "Pendente") => {
    const state = get();
    const ws = state.getActiveWorkspace();
    if (ws.registrosNc.length === 0) return false;
    const lastNc = ws.registrosNc[ws.registrosNc.length - 1];
    if (lastNc.is_relacionado) return false;
    const res = state.relacionarFotoComNc({
      targetIdFiscalizacao: lastNc["ID da Fiscalização"],
      targetNumero: lastNc["Nº"],
      fotoName,
      situacao,
    });
    return res.ok;
  },

  relacionarFotoComNc: ({
    targetIdFiscalizacao,
    targetNumero,
    fotoName,
    trecho,
    observacoes,
    legendaDaFoto,
    situacao,
    tipoRegistro,
    siglas,
    direcaoFaixa,
    codificacao,
  }) => {
    const state = get();
    const key = getStateKey(state.tipoRelatorio, state.categoriaRelatorio);
    const ws = state.workspaces[key];

    const targetIndex = ws.registrosNc.findIndex(
      (nc) =>
        nc["ID da Fiscalização"] === targetIdFiscalizacao &&
        nc["Nº"] === targetNumero
    );
    if (targetIndex === -1) {
      return { ok: false, error: "Ocorrência base não encontrada para relacionar." };
    }

    const baseNc = ws.registrosNc[targetIndex];
    const existingGrp = baseNc.grupo_relacao;
    if (baseNc.is_relacionado) {
      return {
        ok: false,
        error:
          "Este item já é uma 2ª foto relacionada. Selecione a ocorrência principal.",
      };
    }

    if (existingGrp) {
      const groupCount = ws.registrosNc.filter(
        (nc) => nc.grupo_relacao === existingGrp
      ).length;
      if (groupCount >= 2) {
        return {
          ok: false,
          error:
            "Esta ocorrência já possui o limite máximo de 2 fotos relacionadas lado a lado.",
        };
      }
    }

    const isFotoJaCadastrada = ws.registrosNc.some(
      (nc) => (nc.Foto || "").trim().toLowerCase() === fotoName.trim().toLowerCase()
    );
    if (isFotoJaCadastrada) {
      return {
        ok: false,
        error:
          "Esta foto já está cadastrada em uma ocorrência e não pode ser relacionada como 2ª foto.",
      };
    }

    const grpId =
      existingGrp || `grp_${targetIdFiscalizacao}_${baseNc["Nº"]}_${Date.now()}`;
    const baseCod = (baseNc.Codificação || baseNc.Identificação || "").trim();

    const isCraFisc =
      state.tipoRelatorio === "CRA" && state.categoriaRelatorio === "Fiscalização";
    const isCraOrSocicamFisc =
      (state.tipoRelatorio === "CRA" || state.tipoRelatorio === "SOCICAM") &&
      state.categoriaRelatorio === "Fiscalização";
    const activeFisc = ws.fiscalizacoes.find(
      (f) => f["ID da Fiscalização"] === targetIdFiscalizacao
    );
    const dataFisc = activeFisc?.Data || "";

    const faixaComb = isCraFisc
      ? combinarFaixasRelacionadas(baseNc["Direção (faixa)"], direcaoFaixa)
      : null;

    const updatedBase: RegistroNcItem = {
      ...baseNc,
      Identificação: baseNc.Identificação || baseCod,
      Codificação: baseNc.Codificação || baseCod,
      grupo_relacao: grpId,
      is_relacionado: Boolean(baseNc.is_relacionado),
      "Direção (faixa)": faixaComb
        ? faixaComb.extenso
        : baseNc["Direção (faixa)"],
    };

    const isBasePa = Boolean(
      baseNc["Ponto de Atenção"] && !baseNc["Não Conformidade"]
    );
    if (
      tipoRegistro !== undefined &&
      ((isBasePa && tipoRegistro === "Não Conformidade") ||
        (!isBasePa && tipoRegistro === "Ponto de Atenção"))
    ) {
      return {
        ok: false,
        error: "Não é permitido relacionar Não Conformidade com Ponto de Atenção.",
      };
    }

    const isPa =
      tipoRegistro !== undefined
        ? tipoRegistro === "Ponto de Atenção"
        : isBasePa;
    const siglasStr = siglas && siglas.length > 0 ? siglas.join(", ") : undefined;

    let ncField = updatedBase["Não Conformidade"];
    let paField = updatedBase["Ponto de Atenção"];

    if (tipoRegistro !== undefined) {
      if (isPa) {
        paField =
          siglasStr ??
          (updatedBase["Ponto de Atenção"] || updatedBase["Não Conformidade"]);
        ncField = "";
      } else {
        ncField =
          siglasStr ??
          (updatedBase["Não Conformidade"] || updatedBase["Ponto de Atenção"]);
        paField = "";
      }
    } else if (siglasStr !== undefined) {
      if (paField && !ncField) {
        paField = siglasStr;
      } else {
        ncField = siglasStr;
      }
    }

    let codFinal = "";
    if (isCraOrSocicamFisc) {
      const defaultBase =
        state.tipoRelatorio === "SOCICAM"
          ? "SOCICAM"
          : "CRA.ST601.2794-2834";
      const baseRaw = codificacao?.trim() || baseCod || defaultBase;
      const baseLimpa = baseRaw.split("/")[0].trim() || baseRaw;
      const baseSiglas = (
        baseNc["Não Conformidade"] ||
        baseNc["Ponto de Atenção"] ||
        ""
      )
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
      const novasSiglas = (siglasStr || "")
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
      const siglasIguais =
        baseSiglas.length > 0 &&
        baseSiglas.slice().sort().join(",") === novasSiglas.slice().sort().join(",");

      if (!codificacao?.trim() && siglasIguais && baseCod) {
        codFinal = baseCod;
      } else {
        const seqIdx = obterProximoSequencialCra(
          ws.registrosNc,
          targetIdFiscalizacao,
          isPa ? "Ponto de Atenção" : "Não Conformidade"
        );
        codFinal = calcularCodificacaoCra(baseLimpa, dataFisc, seqIdx);
      }
    } else {
      codFinal = codificacao?.trim()
        ? codificacao.trim()
        : derivarProximaCodificacao(baseCod);
    }

    const obs2Auto =
      siglas && siglas.length > 0
        ? siglas.map((s) => (state.mapSiglas[s] || s).toLowerCase()).join(", ")
        : "";

    const foto2Idx = ws.photos.findIndex((p) => p.name === fotoName);
    const foto2Num = foto2Idx >= 0 ? foto2Idx + 1 : (baseNc["Nº"] || 1) + 1;

    const newRelatedRaw: RegistroNcItem = {
      ...updatedBase,
      Nº: foto2Num,
      Foto: fotoName,
      "Não Conformidade": ncField,
      "Ponto de Atenção": paField,
      Identificação: codFinal,
      Codificação: codFinal,
      "Direção (faixa)": faixaComb
        ? faixaComb.extenso
        : direcaoFaixa !== undefined
        ? direcaoFaixa
        : updatedBase["Direção (faixa)"],
      Trecho: trecho !== undefined ? trecho : updatedBase.Trecho,
      Observações:
        observacoes !== undefined && observacoes.trim()
          ? observacoes.trim()
          : obs2Auto || updatedBase.Observações,
      "Legenda da Foto":
        legendaDaFoto !== undefined && legendaDaFoto.trim()
          ? legendaDaFoto.trim()
          : obs2Auto || updatedBase["Legenda da Foto"],
      Situação: situacao || updatedBase.Situação,
      is_relacionado: true,
      grupo_relacao: grpId,
    };

    const nextList = [...ws.registrosNc];
    nextList[targetIndex] = updatedBase;
    nextList.splice(targetIndex + 1, 0, newRelatedRaw);

    if (faixaComb) {
      for (let i = 0; i < nextList.length; i++) {
        if (nextList[i].grupo_relacao === grpId) {
          nextList[i] = {
            ...nextList[i],
            "Direção (faixa)": faixaComb.extenso,
          };
        }
      }
    }

    const counters: Record<string, number> = {};
    const renumbered = nextList.map((nc) => {
      if (isCraFisc) {
        const pIdx = ws.photos.findIndex((p) => p.name === nc.Foto);
        if (pIdx >= 0) {
          return { ...nc, "Nº": pIdx + 1 };
        }
      }
      const idF = nc["ID da Fiscalização"];
      counters[idF] = (counters[idF] || 0) + 1;
      return { ...nc, "Nº": counters[idF] };
    });

    const isMon = state.categoriaRelatorio === "Monitoramento";
    let nextCarouselIdx = ws.carouselIndex;
    if (state.autoAdvanceActive) {
      if (isMon && ws.oldPhotosToMatch.length > 0) {
        const auditedOldIds = new Set(
          renumbered
            .filter((r) => !r.is_relacionado && r.Identificação)
            .map((r) => r.Identificação)
        );
        nextCarouselIdx = findNextCircularIndex(
          ws.oldPhotosToMatch,
          nextCarouselIdx,
          (item) => auditedOldIds.has(item.id_nc)
        );
      } else if (!isMon && ws.photos.length > 0) {
        const usedNewPhotos = new Set(
          renumbered
            .map((r) => (r.Foto || "").trim().toLowerCase())
            .filter(Boolean)
        );
        nextCarouselIdx = findNextCircularIndex(
          ws.photos,
          nextCarouselIdx,
          (p) => usedNewPhotos.has(p.name.trim().toLowerCase())
        );
      }
    }

    set({
      workspaces: {
        ...state.workspaces,
        [key]: {
          ...ws,
          registrosNc: renumbered,
          carouselIndex: nextCarouselIdx,
          relatoriosGerados: [],
        },
      },
    });

    return { ok: true };
  },

  updateRegistroNcAt: (idFiscalizacao, numero, updated) =>
    set((state) => {
      const key = getStateKey(state.tipoRelatorio, state.categoriaRelatorio);
      const ws = state.workspaces[key];
      const nextNcs = ws.registrosNc.map((nc) =>
        nc["ID da Fiscalização"] === idFiscalizacao && nc["Nº"] === numero
          ? { ...nc, ...updated }
          : nc
      );
      return {
        workspaces: {
          ...state.workspaces,
          [key]: {
            ...ws,
            registrosNc: nextNcs,
            relatoriosGerados: [],
          },
        },
      };
    }),

  deleteRegistrosNcBulk: (keys) =>
    set((state) => {
      const key = getStateKey(state.tipoRelatorio, state.categoriaRelatorio);
      const ws = state.workspaces[key];
      const removeSet = new Set(
        keys.map((k) => `${k.idFiscalizacao}__${k.numero}`)
      );

      const removedGroups = new Set<string>();
      ws.registrosNc.forEach((nc) => {
        const ncKey = `${nc["ID da Fiscalização"]}__${nc["Nº"]}`;
        if (removeSet.has(ncKey) && nc.grupo_relacao) {
          removedGroups.add(nc.grupo_relacao);
        }
      });

      const withoutRemoved = ws.registrosNc.filter((nc) => {
        const ncKey = `${nc["ID da Fiscalização"]}__${nc["Nº"]}`;
        if (removeSet.has(ncKey)) return false;
        if (nc.grupo_relacao && removedGroups.has(nc.grupo_relacao)) return false;
        return true;
      });

      const baseGroups = new Set<string>();
      withoutRemoved.forEach((nc) => {
        if (!nc.is_relacionado && nc.grupo_relacao) {
          baseGroups.add(nc.grupo_relacao);
        }
      });
      const remaining = withoutRemoved.filter(
        (nc) =>
          !nc.is_relacionado ||
          (nc.grupo_relacao && baseGroups.has(nc.grupo_relacao))
      );

      const counters: Record<string, number> = {};
      const renumbered = remaining.map((nc) => {
        const idF = nc["ID da Fiscalização"];
        counters[idF] = (counters[idF] || 0) + 1;
        return { ...nc, "Nº": counters[idF] };
      });

      return {
        workspaces: {
          ...state.workspaces,
          [key]: {
            ...ws,
            registrosNc: renumbered,
            relatoriosGerados: [],
          },
        },
      };
    }),

  executarAutoPreenchimento: () => set((state) => buildAutoFillPatch(state)),

  limparRegistrosAtuais: (alsoClearPhotos = false) =>
    set((state) => {
      const key = getStateKey(state.tipoRelatorio, state.categoriaRelatorio);
      const ws = state.workspaces[key];
      const activeFisc = ws.fiscalizacoes[ws.activeFiscalizacaoIndex];
      const activeFiscId = activeFisc?.["ID da Fiscalização"]?.trim() || "";
      const updatedCache = { ...(ws.photosByFiscalizacao || {}) };

      if (alsoClearPhotos) {
        ws.photos.forEach((p) => {
          if (p.previewUrl?.startsWith("blob:")) URL.revokeObjectURL(p.previewUrl);
        });
        if (activeFiscId) updatedCache[activeFiscId] = [];
      }
      const remainingNcs = activeFiscId
        ? ws.registrosNc.filter(
            (r) => (r["ID da Fiscalização"] || "").trim() !== activeFiscId
          )
        : [];
      return {
        workspaces: {
          ...state.workspaces,
          [key]: {
            ...ws,
            registrosNc: remainingNcs,
            photos: alsoClearPhotos ? [] : ws.photos,
            photosByFiscalizacao: updatedCache,
            carouselIndex: 0,
            pistaPersistida: "",
            trechoPersistido: "",
            relatoriosGerados: [],
          },
        },
      };
    }),
});

