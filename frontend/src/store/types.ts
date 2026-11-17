import {
  BootstrapConfigResponse,
  CategoriaRelatorio,
  CustomNcItem,
  FiscalizacaoItem,
  MonitoramentoAnteriorItem,
  MonitoramentoAnteriorMeta,
  PessoaItem,
  RegistroNcItem,
  RelatorioGeradoItem,
  SituacaoNC,
  SortOption,
  StateKey,
  TipoRelatorio,
  UploadedPhotoItem,
} from "../types/report.types";

export interface InspectionSessionSnapshot {
  registrosNc: RegistroNcItem[];
  photos: UploadedPhotoItem[];
  sortOption: SortOption;
  carouselIndex: number;
  monitoringNewPhotoName: string;
  pistaPersistida: string;
  trechoPersistido: string;
  documentoAnteriorFile: File | null;
  documentoAnteriorMeta: MonitoramentoAnteriorMeta | null;
  planilhaElegibilidadeFile: File | null;
  oldPhotosToMatch: MonitoramentoAnteriorItem[];
  relatoriosGerados: RelatorioGeradoItem[];
}

export interface ModalityWorkspaceState {
  fiscalizacoes: FiscalizacaoItem[];
  activeFiscalizacaoIndex: number;
  registrosNc: RegistroNcItem[];
  photos: UploadedPhotoItem[];
  photosByFiscalizacao: Record<string, UploadedPhotoItem[]>;
  sessionsById: Record<string, InspectionSessionSnapshot>;
  sortOption: SortOption;
  carouselIndex: number;
  pistaPersistida: string;
  trechoPersistido: string;
  documentoAnteriorFile: File | null;
  documentoAnteriorMeta: MonitoramentoAnteriorMeta | null;
  planilhaElegibilidadeFile: File | null;
  oldPhotosToMatch: MonitoramentoAnteriorItem[];
  relatoriosGerados: RelatorioGeradoItem[];
}

export interface RelacionarFotoParams {
  targetIdFiscalizacao: string;
  targetNumero: number;
  fotoName: string;
  trecho?: string;
  observacoes?: string;
  legendaDaFoto?: string;
  situacao?: SituacaoNC;
  tipoRegistro?: "Não Conformidade" | "Ponto de Atenção";
  siglas?: string[];
  direcaoFaixa?: string;
  codificacao?: string;
}

export interface CatalogSlice {
  responsaveis: PessoaItem[];
  coordenadores: PessoaItem[];
  contratos: string[];
  contratosPadrao: Record<TipoRelatorio, string>;
  customNcs: CustomNcItem[];
  customNcsSocicam: CustomNcItem[];
  baseNcOptions: string[];
  mapSiglas: Record<string, string>;
  locaisSocicam: string[];
  getNcOptionsForCurrent: () => string[];
  hydrateBootstrapConfig: (cfg: BootstrapConfigResponse) => void;
  setResponsaveis: (items: PessoaItem[]) => void;
  setCoordenadores: (items: PessoaItem[]) => void;
  setContratos: (items: string[]) => void;
  setCustomNcs: (items: CustomNcItem[], mapSiglas?: Record<string, string>) => void;
  setCustomNcsSocicam: (items: CustomNcItem[], mapSiglas?: Record<string, string>) => void;
}

export interface NavigationSlice {
  tipoRelatorio: TipoRelatorio;
  categoriaRelatorio: CategoriaRelatorio;
  autoAdvanceActive: boolean;
  compressImages: boolean;
  pastaLocalConectada: boolean;
  nomePastaLocal: string;
  monitoringNewPhotoName: string;
  setPastaLocalStatus: (conectada: boolean, nome?: string) => void;
  setMonitoringNewPhotoName: (name: string) => void;
  setTipoRelatorio: (tipo: TipoRelatorio) => void;
  cycleTipoRelatorio: () => void;
  setCategoriaRelatorio: (cat: CategoriaRelatorio) => void;
  toggleCategoriaRelatorio: () => void;
  setAutoAdvanceActive: (val: boolean) => void;
  setCompressImages: (val: boolean) => void;
}

export interface SessionMediaSlice {
  workspaces: Record<StateKey, ModalityWorkspaceState>;
  getActiveWorkspace: () => ModalityWorkspaceState;
  addUploadedPhotos: (files: FileList | File[]) => void;
  removePhoto: (id: string) => void;
  setSortOption: (option: SortOption) => void;
  clearPhotos: () => void;
  getAllPhotosForBatch: () => UploadedPhotoItem[];
  setCarouselIndex: (idx: number) => void;
  setMonitoramentoAnteriorData: (
    file: File | null,
    items: MonitoramentoAnteriorItem[],
    meta?: MonitoramentoAnteriorMeta | null
  ) => void;
  setPlanilhaElegibilidadeFile: (file: File | null) => void;
  setActiveFiscalizacaoIndex: (idx: number) => void;
  addFiscalizacao: (item: FiscalizacaoItem) => { ok: boolean; error?: string };
  upsertActiveFiscalizacao: (item: FiscalizacaoItem) => void;
  updateFiscalizacao: (
    oldId: string,
    updated: FiscalizacaoItem
  ) => { ok: boolean; error?: string };
  deleteFiscalizacoesBulk: (ids: string[]) => void;
  reiniciarModalidadeAtual: () => void;
  setRelatoriosGerados: (items: RelatorioGeradoItem[]) => void;
  importarEstadoModalidade: (
    tipo: TipoRelatorio,
    categoria: CategoriaRelatorio,
    dados: {
      fiscalizacoes: FiscalizacaoItem[];
      activeFiscalizacaoIndex?: number;
      sessionsById?: Record<string, InspectionSessionSnapshot>;
      registrosNc: RegistroNcItem[];
      photos: UploadedPhotoItem[];
      pistaPersistida?: string;
      trechoPersistido?: string;
      documentoAnteriorFile?: File | null;
      documentoAnteriorMeta?: MonitoramentoAnteriorMeta | null;
      planilhaElegibilidadeFile?: File | null;
      oldPhotosToMatch?: MonitoramentoAnteriorItem[];
    }
  ) => void;
}

export interface RecordsSlice {
  setPistaPersistida: (val: string) => void;
  setTrechoPersistido: (val: string) => void;
  addOrUpdateRegistroNc: (rec: RegistroNcItem, advancePhoto?: boolean) => void;
  relacionarFotoUltimaNc: (fotoName: string, situacao?: SituacaoNC) => boolean;
  relacionarFotoComNc: (params: RelacionarFotoParams) => { ok: boolean; error?: string };
  updateRegistroNcAt: (
    idFiscalizacao: string,
    numero: number,
    updated: Partial<RegistroNcItem>
  ) => void;
  deleteRegistrosNcBulk: (
    keys: Array<{ idFiscalizacao: string; numero: number }>
  ) => void;
  executarAutoPreenchimento: () => void;
  limparRegistrosAtuais: (alsoClearPhotos?: boolean) => void;
}

export type ReportStore = CatalogSlice &
  NavigationSlice &
  SessionMediaSlice &
  RecordsSlice;

