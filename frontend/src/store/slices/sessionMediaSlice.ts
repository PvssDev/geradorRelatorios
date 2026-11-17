import type { StateCreator } from "zustand";
import { UploadedPhotoItem } from "../../types/report.types";
import {
  deduplicarItensExtraidosMonitoramento,
  getStateKey,
  sortPhotosList,
} from "../domain/reportCodingRules";
import type {
  InspectionSessionSnapshot,
  ReportStore,
  SessionMediaSlice,
} from "../types";
import {
  applySessionSnapshot,
  createEmptySessionSnapshot,
  createEmptyWorkspace,
  extractActiveSessionSnapshot,
  syncCurrentSessionIntoMap,
} from "./sessionHelpers";

export const createSessionMediaSlice: StateCreator<
  ReportStore,
  [],
  [],
  SessionMediaSlice
> = (set, get) => ({
  workspaces: {
    CRA_Fiscalização: createEmptyWorkspace(),
    CRA_Monitoramento: createEmptyWorkspace(),
    CRC_Fiscalização: createEmptyWorkspace(),
    CRC_Monitoramento: createEmptyWorkspace(),
    SOCICAM_Fiscalização: createEmptyWorkspace(),
    SOCICAM_Monitoramento: createEmptyWorkspace(),
  },

  getActiveWorkspace: () => {
    const state = get();
    const key = getStateKey(state.tipoRelatorio, state.categoriaRelatorio);
    return state.workspaces[key];
  },

  addUploadedPhotos: (fileList) =>
    set((state) => {
      const key = getStateKey(state.tipoRelatorio, state.categoriaRelatorio);
      const ws = state.workspaces[key];
      const activePhotoName = ws.photos[ws.carouselIndex]?.name || null;

      const existingByName = new Map(ws.photos.map((p) => [p.name, p]));
      let nextOrder = ws.photos.length;

      for (const file of Array.from(fileList)) {
        if (!existingByName.has(file.name)) {
          existingByName.set(file.name, {
            id: `${file.name}_${file.size}_${Date.now()}_${nextOrder}`,
            name: file.name,
            file,
            previewUrl: URL.createObjectURL(file),
            uploadOrder: nextOrder++,
          });
        }
      }

      const sorted = sortPhotosList(
        Array.from(existingByName.values()),
        ws.sortOption
      );
      let newIdx = ws.carouselIndex;
      if (activePhotoName) {
        const foundIdx = sorted.findIndex((p) => p.name === activePhotoName);
        if (foundIdx >= 0) newIdx = foundIdx;
      }
      newIdx = Math.max(0, Math.min(newIdx, Math.max(0, sorted.length - 1)));

      const activeFisc = ws.fiscalizacoes[ws.activeFiscalizacaoIndex];
      const activeFiscId = activeFisc?.["ID da Fiscalização"]?.trim() || "";
      const updatedCache = { ...(ws.photosByFiscalizacao || {}) };
      if (activeFiscId) {
        updatedCache[activeFiscId] = sorted;
      }

      return {
        workspaces: {
          ...state.workspaces,
          [key]: {
            ...ws,
            photos: sorted,
            photosByFiscalizacao: updatedCache,
            carouselIndex: newIdx,
          },
        },
      };
    }),

  setSortOption: (option) =>
    set((state) => {
      const key = getStateKey(state.tipoRelatorio, state.categoriaRelatorio);
      const ws = state.workspaces[key];
      const activePhotoName = ws.photos[ws.carouselIndex]?.name || null;
      const sorted = sortPhotosList(ws.photos, option);
      let newIdx = ws.carouselIndex;
      if (activePhotoName) {
        const foundIdx = sorted.findIndex((p) => p.name === activePhotoName);
        if (foundIdx >= 0) newIdx = foundIdx;
      }
      const activeFisc = ws.fiscalizacoes[ws.activeFiscalizacaoIndex];
      const activeFiscId = activeFisc?.["ID da Fiscalização"]?.trim() || "";
      const updatedCache = { ...(ws.photosByFiscalizacao || {}) };
      if (activeFiscId) {
        updatedCache[activeFiscId] = sorted;
      }

      return {
        workspaces: {
          ...state.workspaces,
          [key]: {
            ...ws,
            sortOption: option,
            photos: sorted,
            photosByFiscalizacao: updatedCache,
            carouselIndex: newIdx,
          },
        },
      };
    }),

  removePhoto: (id) =>
    set((state) => {
      const key = getStateKey(state.tipoRelatorio, state.categoriaRelatorio);
      const ws = state.workspaces[key];
      const target = ws.photos.find((p) => p.id === id);
      if (target) {
        URL.revokeObjectURL(target.previewUrl);
      }
      const nextPhotos = ws.photos.filter((p) => p.id !== id);
      const nextIdx = Math.max(
        0,
        Math.min(ws.carouselIndex, Math.max(0, nextPhotos.length - 1))
      );

      const activeFisc = ws.fiscalizacoes[ws.activeFiscalizacaoIndex];
      const activeFiscId = activeFisc?.["ID da Fiscalização"]?.trim() || "";
      const updatedCache = { ...(ws.photosByFiscalizacao || {}) };
      if (activeFiscId) {
        updatedCache[activeFiscId] = nextPhotos;
      }

      return {
        workspaces: {
          ...state.workspaces,
          [key]: {
            ...ws,
            photos: nextPhotos,
            photosByFiscalizacao: updatedCache,
            carouselIndex: nextIdx,
          },
        },
      };
    }),

  clearPhotos: () =>
    set((state) => {
      const key = getStateKey(state.tipoRelatorio, state.categoriaRelatorio);
      const ws = state.workspaces[key];
      ws.photos.forEach((p) => URL.revokeObjectURL(p.previewUrl));

      const activeFisc = ws.fiscalizacoes[ws.activeFiscalizacaoIndex];
      const activeFiscId = activeFisc?.["ID da Fiscalização"]?.trim() || "";
      const updatedCache = { ...(ws.photosByFiscalizacao || {}) };
      if (activeFiscId) {
        updatedCache[activeFiscId] = [];
      }

      return {
        workspaces: {
          ...state.workspaces,
          [key]: {
            ...ws,
            photos: [],
            photosByFiscalizacao: updatedCache,
            carouselIndex: 0,
          },
        },
      };
    }),

  getAllPhotosForBatch: () => {
    const state = get();
    const key = getStateKey(state.tipoRelatorio, state.categoriaRelatorio);
    const ws = state.workspaces[key];
    const photoMap = new Map<string, UploadedPhotoItem>();

    (ws.photos || []).forEach((p) => photoMap.set(p.name, p));

    if (ws.photosByFiscalizacao) {
      Object.values(ws.photosByFiscalizacao).forEach((list) => {
        (list || []).forEach((p) => photoMap.set(p.name, p));
      });
    }

    return Array.from(photoMap.values());
  },

  setCarouselIndex: (idx) =>
    set((state) => {
      const key = getStateKey(state.tipoRelatorio, state.categoriaRelatorio);
      const ws = state.workspaces[key];
      const maxLen =
        state.categoriaRelatorio === "Monitoramento" && ws.oldPhotosToMatch.length > 0
          ? ws.oldPhotosToMatch.length
          : ws.photos.length;
      const safeIdx = Math.max(0, Math.min(idx, Math.max(0, maxLen - 1)));
      return {
        workspaces: {
          ...state.workspaces,
          [key]: {
            ...ws,
            carouselIndex: safeIdx,
          },
        },
      };
    }),

  setMonitoramentoAnteriorData: (file, items, meta = null) =>
    set((state) => {
      const key = getStateKey(state.tipoRelatorio, state.categoriaRelatorio);
      const ws = state.workspaces[key];
      const deduplicatedItems = deduplicarItensExtraidosMonitoramento(items);

      return {
        workspaces: {
          ...state.workspaces,
          [key]: {
            ...ws,
            documentoAnteriorFile: file,
            documentoAnteriorMeta: meta,
            oldPhotosToMatch: deduplicatedItems,
            carouselIndex: 0,
          },
        },
      };
    }),

  setPlanilhaElegibilidadeFile: (file) =>
    set((state) => {
      const key = getStateKey(state.tipoRelatorio, state.categoriaRelatorio);
      const ws = state.workspaces[key];
      return {
        workspaces: {
          ...state.workspaces,
          [key]: {
            ...ws,
            planilhaElegibilidadeFile: file,
          },
        },
      };
    }),

  setActiveFiscalizacaoIndex: (idx) =>
    set((state) => {
      const key = getStateKey(state.tipoRelatorio, state.categoriaRelatorio);
      const ws = state.workspaces[key];
      const safeIdx = Math.max(0, Math.min(idx, Math.max(0, ws.fiscalizacoes.length - 1)));
      if (safeIdx === ws.activeFiscalizacaoIndex) {
        return state;
      }

      const { sessionsById, photosByFiscalizacao } = syncCurrentSessionIntoMap(
        ws,
        state.monitoringNewPhotoName
      );

      const newFisc = ws.fiscalizacoes[safeIdx];
      const newId = newFisc?.["ID da Fiscalização"]?.trim() || "";
      const targetSnapshot =
        (newId && sessionsById[newId]) || createEmptySessionSnapshot();

      return {
        monitoringNewPhotoName: targetSnapshot.monitoringNewPhotoName || "",
        workspaces: {
          ...state.workspaces,
          [key]: {
            ...ws,
            activeFiscalizacaoIndex: safeIdx,
            photosByFiscalizacao,
            sessionsById,
            ...applySessionSnapshot(targetSnapshot),
          },
        },
      };
    }),

  addFiscalizacao: (item) => {
    const state = get();
    const key = getStateKey(state.tipoRelatorio, state.categoriaRelatorio);
    const ws = state.workspaces[key];
    const cleanId = item["ID da Fiscalização"].trim();
    if (!cleanId) {
      return { ok: false, error: "O ID não pode estar vazio." };
    }
    const exists = ws.fiscalizacoes.some(
      (f) => f["ID da Fiscalização"].trim().toLowerCase() === cleanId.toLowerCase()
    );
    if (exists) {
      return {
        ok: false,
        error: `O ID '${cleanId}' já existe! Utilize um identificador único.`,
      };
    }

    const { sessionsById, photosByFiscalizacao } = syncCurrentSessionIntoMap(
      ws,
      state.monitoringNewPhotoName
    );
    const emptySnapshot = createEmptySessionSnapshot();
    sessionsById[cleanId] = emptySnapshot;
    photosByFiscalizacao[cleanId] = [];

    const nextFisc = [
      ...ws.fiscalizacoes,
      { ...item, "ID da Fiscalização": cleanId },
    ];
    set({
      monitoringNewPhotoName: "",
      workspaces: {
        ...state.workspaces,
        [key]: {
          ...ws,
          fiscalizacoes: nextFisc,
          activeFiscalizacaoIndex: nextFisc.length - 1,
          photosByFiscalizacao,
          sessionsById,
          ...applySessionSnapshot(emptySnapshot),
        },
      },
    });
    return { ok: true };
  },

  upsertActiveFiscalizacao: (item) =>
    set((state) => {
      const key = getStateKey(state.tipoRelatorio, state.categoriaRelatorio);
      const ws = state.workspaces[key];
      if (ws.fiscalizacoes.length === 0) {
        const id = item["ID da Fiscalização"]?.trim() || "";
        const updatedCache = { ...(ws.photosByFiscalizacao || {}) };
        const updatedSessions = { ...(ws.sessionsById || {}) };
        if (id) {
          updatedCache[id] = ws.photos;
          updatedSessions[id] = extractActiveSessionSnapshot(
            ws,
            state.monitoringNewPhotoName
          );
        }
        return {
          workspaces: {
            ...state.workspaces,
            [key]: {
              ...ws,
              fiscalizacoes: [item],
              photosByFiscalizacao: updatedCache,
              sessionsById: updatedSessions,
              activeFiscalizacaoIndex: 0,
            },
          },
        };
      }

      const targetIdx = Math.max(
        0,
        Math.min(ws.activeFiscalizacaoIndex, ws.fiscalizacoes.length - 1)
      );
      const oldId = ws.fiscalizacoes[targetIdx]["ID da Fiscalização"];
      const newId = item["ID da Fiscalização"];

      const collision = ws.fiscalizacoes.some(
        (f, idx) =>
          idx !== targetIdx &&
          newId.trim() !== "" &&
          f["ID da Fiscalização"].trim().toLowerCase() === newId.trim().toLowerCase()
      );
      if (collision) {
        return state;
      }

      const updatedCache = { ...(ws.photosByFiscalizacao || {}) };
      const updatedSessions = { ...(ws.sessionsById || {}) };
      if (oldId && oldId !== newId) {
        if (updatedCache[oldId]) {
          updatedCache[newId] = updatedCache[oldId];
          delete updatedCache[oldId];
        }
        if (updatedSessions[oldId]) {
          updatedSessions[newId] = updatedSessions[oldId];
          delete updatedSessions[oldId];
        }
      } else if (newId) {
        if (!updatedCache[newId]) updatedCache[newId] = ws.photos;
        if (!updatedSessions[newId]) {
          updatedSessions[newId] = extractActiveSessionSnapshot(
            ws,
            state.monitoringNewPhotoName
          );
        }
      }

      const nextFisc = ws.fiscalizacoes.map((f, idx) =>
        idx === targetIdx ? item : f
      );
      const nextNc = ws.registrosNc.map((nc) =>
        nc["ID da Fiscalização"] === oldId
          ? { ...nc, "ID da Fiscalização": newId, Terminal: item.Local }
          : nc
      );
      if (newId && updatedSessions[newId]) {
        updatedSessions[newId] = {
          ...updatedSessions[newId],
          registrosNc: nextNc,
        };
      }
      return {
        workspaces: {
          ...state.workspaces,
          [key]: {
            ...ws,
            fiscalizacoes: nextFisc,
            registrosNc: nextNc,
            photosByFiscalizacao: updatedCache,
            sessionsById: updatedSessions,
          },
        },
      };
    }),

  updateFiscalizacao: (oldId, updated) => {
    const state = get();
    const key = getStateKey(state.tipoRelatorio, state.categoriaRelatorio);
    const ws = state.workspaces[key];
    const newId = updated["ID da Fiscalização"].trim();
    if (!newId) {
      return { ok: false, error: "O ID não pode ficar vazio." };
    }
    const collision = ws.fiscalizacoes.some(
      (f) =>
        f["ID da Fiscalização"] !== oldId &&
        f["ID da Fiscalização"].trim().toLowerCase() === newId.toLowerCase()
    );
    if (collision) {
      return {
        ok: false,
        error: `O ID '${newId}' já existe em outro registro. Escolha um ID único.`,
      };
    }

    const updatedCache = { ...(ws.photosByFiscalizacao || {}) };
    const updatedSessions = { ...(ws.sessionsById || {}) };
    if (oldId && oldId !== newId) {
      if (updatedCache[oldId]) {
        updatedCache[newId] = updatedCache[oldId];
        delete updatedCache[oldId];
      }
      if (updatedSessions[oldId]) {
        updatedSessions[newId] = {
          ...updatedSessions[oldId],
          registrosNc: updatedSessions[oldId].registrosNc.map((nc) =>
            nc["ID da Fiscalização"] === oldId
              ? { ...nc, "ID da Fiscalização": newId, Terminal: updated.Local }
              : nc
          ),
        };
        delete updatedSessions[oldId];
      }
    }

    const cleanUpdated = { ...updated, "ID da Fiscalização": newId };
    const nextFisc = ws.fiscalizacoes.map((f) =>
      f["ID da Fiscalização"] === oldId ? cleanUpdated : f
    );
    const nextNc = ws.registrosNc.map((nc) =>
      nc["ID da Fiscalização"] === oldId
        ? { ...nc, "ID da Fiscalização": newId, Terminal: cleanUpdated.Local }
        : nc
    );

    set({
      workspaces: {
        ...state.workspaces,
        [key]: {
          ...ws,
          fiscalizacoes: nextFisc,
          registrosNc: nextNc,
          photosByFiscalizacao: updatedCache,
          sessionsById: updatedSessions,
          relatoriosGerados: [],
        },
      },
    });
    return { ok: true };
  },

  deleteFiscalizacoesBulk: (ids) =>
    set((state) => {
      const key = getStateKey(state.tipoRelatorio, state.categoriaRelatorio);
      const ws = state.workspaces[key];
      const idSet = new Set(ids);

      const { sessionsById, photosByFiscalizacao } = syncCurrentSessionIntoMap(
        ws,
        state.monitoringNewPhotoName
      );

      const activeFisc = ws.fiscalizacoes[ws.activeFiscalizacaoIndex];
      const activeFiscId = activeFisc?.["ID da Fiscalização"]?.trim() || "";
      const deletingActive = Boolean(activeFiscId && idSet.has(activeFiscId));

      ids.forEach((id) => {
        if (photosByFiscalizacao[id]) {
          photosByFiscalizacao[id].forEach((p) => {
            if (p.previewUrl?.startsWith("blob:")) URL.revokeObjectURL(p.previewUrl);
          });
          delete photosByFiscalizacao[id];
        }
        if (sessionsById[id]) {
          sessionsById[id].photos.forEach((p) => {
            if (p.previewUrl?.startsWith("blob:")) URL.revokeObjectURL(p.previewUrl);
          });
          delete sessionsById[id];
        }
      });

      const nextFisc = ws.fiscalizacoes.filter(
        (f) => !idSet.has(f["ID da Fiscalização"])
      );
      const safeIdx = Math.max(
        0,
        Math.min(ws.activeFiscalizacaoIndex, Math.max(0, nextFisc.length - 1))
      );
      const nextActiveId = nextFisc[safeIdx]?.["ID da Fiscalização"]?.trim() || "";
      const restoredSnapshot =
        (nextActiveId && sessionsById[nextActiveId]) ||
        createEmptySessionSnapshot();

      return {
        monitoringNewPhotoName: deletingActive
          ? restoredSnapshot.monitoringNewPhotoName || ""
          : state.monitoringNewPhotoName,
        workspaces: {
          ...state.workspaces,
          [key]: {
            ...ws,
            fiscalizacoes: nextFisc,
            activeFiscalizacaoIndex: safeIdx,
            photosByFiscalizacao,
            sessionsById,
            ...(deletingActive ? applySessionSnapshot(restoredSnapshot) : {}),
            relatoriosGerados: [],
          },
        },
      };
    }),

  reiniciarModalidadeAtual: () =>
    set((state) => {
      const key = getStateKey(state.tipoRelatorio, state.categoriaRelatorio);
      const ws = state.workspaces[key];

      ws.photos.forEach((p) => {
        if (p.previewUrl?.startsWith("blob:")) URL.revokeObjectURL(p.previewUrl);
      });
      if (ws.photosByFiscalizacao) {
        Object.values(ws.photosByFiscalizacao).forEach((list) => {
          list.forEach((p) => {
            if (p.previewUrl?.startsWith("blob:")) URL.revokeObjectURL(p.previewUrl);
          });
        });
      }
      if (ws.sessionsById) {
        Object.values(ws.sessionsById).forEach((sess) => {
          sess.photos.forEach((p) => {
            if (p.previewUrl?.startsWith("blob:")) URL.revokeObjectURL(p.previewUrl);
          });
        });
      }

      return {
        monitoringNewPhotoName: "",
        workspaces: {
          ...state.workspaces,
          [key]: createEmptyWorkspace(),
        },
      };
    }),

  setRelatoriosGerados: (items) =>
    set((state) => {
      const key = getStateKey(state.tipoRelatorio, state.categoriaRelatorio);
      const ws = state.workspaces[key];
      return {
        workspaces: {
          ...state.workspaces,
          [key]: {
            ...ws,
            relatoriosGerados: items,
          },
        },
      };
    }),

  importarEstadoModalidade: (tipo, categoria, dados) =>
    set((state) => {
      const key = getStateKey(tipo, categoria);
      const ws = state.workspaces[key];
      ws.photos.forEach((p) => {
        if (p.previewUrl && p.previewUrl.startsWith("blob:")) {
          URL.revokeObjectURL(p.previewUrl);
        }
      });

      const nextSessions: Record<string, InspectionSessionSnapshot> = {
        ...(dados.sessionsById || {}),
      };
      const nextPhotosCache: Record<string, UploadedPhotoItem[]> = {};

      if (dados.sessionsById) {
        for (const [id, sess] of Object.entries(dados.sessionsById)) {
          nextPhotosCache[id] = sess.photos || [];
        }
      } else if (dados.fiscalizacoes.length > 0) {
        for (const f of dados.fiscalizacoes) {
          const fid = f["ID da Fiscalização"]?.trim() || "";
          if (!fid) continue;
          const isFirst = fid === dados.fiscalizacoes[0]["ID da Fiscalização"]?.trim();
          nextSessions[fid] = {
            ...createEmptySessionSnapshot(),
            registrosNc: dados.registrosNc.filter(
              (nc) => (nc["ID da Fiscalização"] || "").trim() === fid
            ),
            photos: isFirst ? dados.photos : [],
            pistaPersistida: dados.pistaPersistida || "",
            trechoPersistido: dados.trechoPersistido || "",
            documentoAnteriorFile: isFirst ? dados.documentoAnteriorFile ?? null : null,
            documentoAnteriorMeta: isFirst ? dados.documentoAnteriorMeta ?? null : null,
            planilhaElegibilidadeFile: isFirst
              ? dados.planilhaElegibilidadeFile ?? null
              : null,
            oldPhotosToMatch: isFirst ? dados.oldPhotosToMatch || [] : [],
          };
          nextPhotosCache[fid] = nextSessions[fid].photos;
        }
      }

      const activeIdx = Math.max(
        0,
        Math.min(
          dados.activeFiscalizacaoIndex ?? 0,
          Math.max(0, dados.fiscalizacoes.length - 1)
        )
      );
      const activeId =
        dados.fiscalizacoes[activeIdx]?.["ID da Fiscalização"]?.trim() || "";
      const activeSnapshot: InspectionSessionSnapshot =
        (activeId && nextSessions[activeId]) || {
          ...createEmptySessionSnapshot(),
          registrosNc: dados.registrosNc,
          photos: dados.photos,
          pistaPersistida: dados.pistaPersistida || "",
          trechoPersistido: dados.trechoPersistido || "",
          documentoAnteriorFile: dados.documentoAnteriorFile ?? null,
          documentoAnteriorMeta: dados.documentoAnteriorMeta ?? null,
          planilhaElegibilidadeFile: dados.planilhaElegibilidadeFile ?? null,
          oldPhotosToMatch: dados.oldPhotosToMatch || [],
        };

      return {
        monitoringNewPhotoName: activeSnapshot.monitoringNewPhotoName || "",
        workspaces: {
          ...state.workspaces,
          [key]: {
            ...ws,
            fiscalizacoes: dados.fiscalizacoes,
            activeFiscalizacaoIndex: activeIdx,
            photosByFiscalizacao: nextPhotosCache,
            sessionsById: nextSessions,
            ...applySessionSnapshot(activeSnapshot),
          },
        },
      };
    }),
});

