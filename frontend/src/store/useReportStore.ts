import { create } from "zustand";
import type { ReportStore } from "./types";
import { createCatalogSlice } from "./slices/catalogSlice";
import { createNavigationSlice } from "./slices/navigationSlice";
import { createSessionMediaSlice } from "./slices/sessionMediaSlice";
import { createRecordsSlice } from "./slices/recordsSlice";

export type {
  InspectionSessionSnapshot,
  ModalityWorkspaceState,
  RelacionarFotoParams,
  ReportStore,
} from "./types";

export {
  calcularCodificacaoCra,
  combinarFaixasRelacionadas,
  derivarProximaCodificacao,
  obterProximoSequencialCra,
} from "./domain/reportCodingRules";

export { extractActiveSessionSnapshot } from "./slices/sessionHelpers";

export const useReportStore = create<ReportStore>()((...args) => ({
  ...createCatalogSlice(...args),
  ...createNavigationSlice(...args),
  ...createSessionMediaSlice(...args),
  ...createRecordsSlice(...args),
}));
