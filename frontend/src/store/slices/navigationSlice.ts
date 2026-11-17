import type { StateCreator } from "zustand";
import { TipoRelatorio } from "../../types/report.types";
import type { NavigationSlice, ReportStore } from "../types";

export const createNavigationSlice: StateCreator<
  ReportStore,
  [],
  [],
  NavigationSlice
> = (set) => ({
  tipoRelatorio: "CRA",
  categoriaRelatorio: "Fiscalização",
  autoAdvanceActive: true,
  compressImages: true,
  pastaLocalConectada: false,
  nomePastaLocal: "",
  monitoringNewPhotoName: "",

  setPastaLocalStatus: (conectada, nome = "") =>
    set({ pastaLocalConectada: conectada, nomePastaLocal: nome }),

  setMonitoringNewPhotoName: (name) => set({ monitoringNewPhotoName: name }),

  setTipoRelatorio: (tipo) => set({ tipoRelatorio: tipo }),

  cycleTipoRelatorio: () =>
    set((state) => {
      const order: TipoRelatorio[] = ["CRA", "CRC", "SOCICAM"];
      const idx = order.indexOf(state.tipoRelatorio);
      return { tipoRelatorio: order[(idx + 1) % order.length] };
    }),

  setCategoriaRelatorio: (cat) => set({ categoriaRelatorio: cat }),

  toggleCategoriaRelatorio: () =>
    set((state) => ({
      categoriaRelatorio:
        state.categoriaRelatorio === "Fiscalização"
          ? "Monitoramento"
          : "Fiscalização",
    })),

  setAutoAdvanceActive: (val) => set({ autoAdvanceActive: val }),

  setCompressImages: (val) => set({ compressImages: val }),
});

