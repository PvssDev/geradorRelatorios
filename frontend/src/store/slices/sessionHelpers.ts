import { UploadedPhotoItem } from "../../types/report.types";
import { InspectionSessionSnapshot, ModalityWorkspaceState } from "../types";

export function createEmptySessionSnapshot(): InspectionSessionSnapshot {
  return {
    registrosNc: [],
    photos: [],
    sortOption: "Nome (A-Z / 0-9)",
    carouselIndex: 0,
    monitoringNewPhotoName: "",
    pistaPersistida: "",
    trechoPersistido: "",
    documentoAnteriorFile: null,
    documentoAnteriorMeta: null,
    planilhaElegibilidadeFile: null,
    oldPhotosToMatch: [],
    relatoriosGerados: [],
  };
}

export function extractActiveSessionSnapshot(
  ws: ModalityWorkspaceState,
  monitoringNewPhotoName = ""
): InspectionSessionSnapshot {
  return {
    registrosNc: ws.registrosNc,
    photos: ws.photos,
    sortOption: ws.sortOption,
    carouselIndex: ws.carouselIndex,
    monitoringNewPhotoName,
    pistaPersistida: ws.pistaPersistida,
    trechoPersistido: ws.trechoPersistido,
    documentoAnteriorFile: ws.documentoAnteriorFile,
    documentoAnteriorMeta: ws.documentoAnteriorMeta,
    planilhaElegibilidadeFile: ws.planilhaElegibilidadeFile,
    oldPhotosToMatch: ws.oldPhotosToMatch,
    relatoriosGerados: ws.relatoriosGerados,
  };
}

export function syncCurrentSessionIntoMap(
  ws: ModalityWorkspaceState,
  monitoringNewPhotoName: string
): {
  sessionsById: Record<string, InspectionSessionSnapshot>;
  photosByFiscalizacao: Record<string, UploadedPhotoItem[]>;
} {
  const nextSessions = { ...(ws.sessionsById || {}) };
  const nextPhotosCache = { ...(ws.photosByFiscalizacao || {}) };
  const currentFisc = ws.fiscalizacoes[ws.activeFiscalizacaoIndex];
  const currentId = currentFisc?.["ID da Fiscalização"]?.trim() || "";
  if (currentId) {
    nextSessions[currentId] = extractActiveSessionSnapshot(ws, monitoringNewPhotoName);
    nextPhotosCache[currentId] = ws.photos;
  }
  return { sessionsById: nextSessions, photosByFiscalizacao: nextPhotosCache };
}

export function applySessionSnapshot(
  snapshot?: InspectionSessionSnapshot
): Omit<
  ModalityWorkspaceState,
  "fiscalizacoes" | "activeFiscalizacaoIndex" | "photosByFiscalizacao" | "sessionsById"
> {
  const s = snapshot || createEmptySessionSnapshot();
  return {
    registrosNc: s.registrosNc,
    photos: s.photos,
    sortOption: s.sortOption,
    carouselIndex: s.carouselIndex,
    pistaPersistida: s.pistaPersistida,
    trechoPersistido: s.trechoPersistido,
    documentoAnteriorFile: s.documentoAnteriorFile,
    documentoAnteriorMeta: s.documentoAnteriorMeta,
    planilhaElegibilidadeFile: s.planilhaElegibilidadeFile,
    oldPhotosToMatch: s.oldPhotosToMatch,
    relatoriosGerados: s.relatoriosGerados,
  };
}

export function createEmptyWorkspace(): ModalityWorkspaceState {
  return {
    fiscalizacoes: [],
    activeFiscalizacaoIndex: 0,
    photosByFiscalizacao: {},
    sessionsById: {},
    ...createEmptySessionSnapshot(),
  };
}

