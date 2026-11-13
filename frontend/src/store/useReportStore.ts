import { create } from "zustand";
import {
  BootstrapConfigResponse,
  CategoriaRelatorio,
  CustomNcItem,
  FiscalizacaoItem,
  MonitoramentoAnteriorItem,
  PessoaItem,
  RegistroNcItem,
  RelatorioGeradoItem,
  SituacaoNC,
  SortOption,
  StateKey,
  TipoRelatorio,
  UploadedPhotoItem,
} from "../types/report.types";
import { compararNomesNatural } from "../services/naturalSort";

export interface ModalityWorkspaceState {
  fiscalizacoes: FiscalizacaoItem[];
  activeFiscalizacaoIndex: number;
  registrosNc: RegistroNcItem[];
  photos: UploadedPhotoItem[];
  photosByFiscalizacao: Record<string, UploadedPhotoItem[]>;
  sortOption: SortOption;
  carouselIndex: number;
  pistaPersistida: string;
  trechoPersistido: string;
  documentoAnteriorFile: File | null;
  planilhaElegibilidadeFile: File | null;
  oldPhotosToMatch: MonitoramentoAnteriorItem[];
  relatoriosGerados: RelatorioGeradoItem[];
}

function createEmptyWorkspace(): ModalityWorkspaceState {
  return {
    fiscalizacoes: [],
    activeFiscalizacaoIndex: 0,
    registrosNc: [],
    photos: [],
    photosByFiscalizacao: {},
    sortOption: "Nome (A-Z / 0-9)",
    carouselIndex: 0,
    pistaPersistida: "",
    trechoPersistido: "",
    documentoAnteriorFile: null,
    planilhaElegibilidadeFile: null,
    oldPhotosToMatch: [],
    relatoriosGerados: [],
  };
}

function getStateKey(tipo: TipoRelatorio, categoria: CategoriaRelatorio): StateKey {
  return `${tipo}_${categoria}`;
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

function sortPhotosList(photos: UploadedPhotoItem[], sortOption: SortOption): UploadedPhotoItem[] {
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

interface ReportStore {
  tipoRelatorio: TipoRelatorio;
  categoriaRelatorio: CategoriaRelatorio;
  autoAdvanceActive: boolean;
  compressImages: boolean;

  // Dados administrativos e opções
  responsaveis: PessoaItem[];
  coordenadores: PessoaItem[];
  contratos: string[];
  contratosPadrao: Record<TipoRelatorio, string>;
  customNcs: CustomNcItem[];
  customNcsSocicam: CustomNcItem[];
  baseNcOptions: string[];
  mapSiglas: Record<string, string>;
  locaisSocicam: string[];

  // Status de conexão da pasta local geradorBD
  pastaLocalConectada: boolean;
  nomePastaLocal: string;
  setPastaLocalStatus: (conectada: boolean, nome?: string) => void;

  // Workspaces isolados para os 6 estados
  workspaces: Record<StateKey, ModalityWorkspaceState>;

  // Getters do workspace ativo
  getActiveWorkspace: () => ModalityWorkspaceState;
  getNcOptionsForCurrent: () => string[];

  // Ações de navegação de modalidade e preferências
  setTipoRelatorio: (tipo: TipoRelatorio) => void;
  cycleTipoRelatorio: () => void;
  setCategoriaRelatorio: (cat: CategoriaRelatorio) => void;
  toggleCategoriaRelatorio: () => void;
  setAutoAdvanceActive: (val: boolean) => void;
  setCompressImages: (val: boolean) => void;

  // Persistência de localização por workspace
  setPistaPersistida: (val: string) => void;
  setTrechoPersistido: (val: string) => void;

  // Hidratação de configuração
  hydrateBootstrapConfig: (cfg: BootstrapConfigResponse) => void;
  setResponsaveis: (items: PessoaItem[]) => void;
  setCoordenadores: (items: PessoaItem[]) => void;
  setContratos: (items: string[]) => void;
  setCustomNcs: (items: CustomNcItem[], mapSiglas?: Record<string, string>) => void;
  setCustomNcsSocicam: (items: CustomNcItem[], mapSiglas?: Record<string, string>) => void;

  // Ações de Fotos e Mídia
  addUploadedPhotos: (files: FileList | File[]) => void;
  removePhoto: (id: string) => void;
  setSortOption: (option: SortOption) => void;
  clearPhotos: () => void;
  getAllPhotosForBatch: () => UploadedPhotoItem[];
  setCarouselIndex: (idx: number) => void;
  setMonitoramentoAnteriorData: (file: File | null, items: MonitoramentoAnteriorItem[]) => void;
  setPlanilhaElegibilidadeFile: (file: File | null) => void;

  // Ações de Fiscalização / Monitoramento
  setActiveFiscalizacaoIndex: (idx: number) => void;
  addFiscalizacao: (item: FiscalizacaoItem) => { ok: boolean; error?: string };
  upsertActiveFiscalizacao: (item: FiscalizacaoItem) => void;
  updateFiscalizacao: (oldId: string, updated: FiscalizacaoItem) => { ok: boolean; error?: string };
  deleteFiscalizacoesBulk: (ids: string[]) => void;

  // Ações de Registros (NC / PA)
  addOrUpdateRegistroNc: (rec: RegistroNcItem, advancePhoto?: boolean) => void;
  relacionarFotoUltimaNc: (fotoName: string, situacao?: SituacaoNC) => boolean;
  relacionarFotoComNc: (params: RelacionarFotoParams) => { ok: boolean; error?: string };
  updateRegistroNcAt: (idFiscalizacao: string, numero: number, updated: Partial<RegistroNcItem>) => void;
  deleteRegistrosNcBulk: (keys: Array<{ idFiscalizacao: string; numero: number }>) => void;
  executarAutoPreenchimento: () => void;
  limparRegistrosAtuais: (alsoClearPhotos?: boolean) => void;
  reiniciarModalidadeAtual: () => void;
  setRelatoriosGerados: (items: RelatorioGeradoItem[]) => void;
  importarEstadoModalidade: (
    tipo: TipoRelatorio,
    categoria: CategoriaRelatorio,
    dados: {
      fiscalizacoes: FiscalizacaoItem[];
      registrosNc: RegistroNcItem[];
      photos: UploadedPhotoItem[];
      pistaPersistida?: string;
      trechoPersistido?: string;
      documentoAnteriorFile?: File | null;
      planilhaElegibilidadeFile?: File | null;
    }
  ) => void;
}

const DEFAULT_BASE_OPTIONS = [
  "FI", "TTC", "TTL", "TLC", "TLL", "TRR", "J", "TB",
  "JE", "TBE", "ALP", "ATP", "O", "P", "EX", "D", "R",
  "ALC", "ATC", "E",
];

// Dicionário oficial DNIT 005/2003 + SOCICAM (idêntico a src/sections/quadros/quadros.py)
const DEFAULT_MAP_SIGLAS: Record<string, string> = {
  FI: "Fissuras",
  TTC: "Trincas isoladas transversais curtas",
  TTL: "Trincas isoladas transversais longas",
  TLC: "Trincas isoladas longitudinais curtas",
  TLL: "Trincas isoladas longitudinais longas",
  J: "Trincas interligadas sem erosão acentuada nas bordas das trincas",
  JE: "Trincas interligadas com erosão acentuada nas bordas das trincas",
  TRR: "Trincas isoladas no revestimento devido à retração térmica ou dissecação da base (solo-cimento) ou do revestimento",
  TB: "Trincas interligadas sem erosão acentuada nas bordas das trincas",
  TBE: "Trincas interligadas com erosão acentuada nas bordas das trincas",
  ALP: "Afundamento local plástico devido à fluência plástica de uma ou mais camadas do pavimento ou do subleito",
  ATP: "Afundamento da trilha plástico devido à fluência plástica de uma ou mais camadas do pavimento ou do subleito",
  ALC: "Afundamento local de consolidação devido à consolidação diferencial ocorrente em camadas do pavimento ou do subleito",
  ATC: "Afundamento da trilha de consolidação devido à consolidação diferencial ocorrente em camadas do pavimento ou do subleito",
  O: "Ondulação/Corrugação, caracterizada por ondulações transversais causadas por instabilidade da mistura betuminosa constituinte do revestimento ou da base",
  E: "Escorregamento do revestimento betuminoso",
  EX: "Exsudação do ligante betuminoso no revestimento",
  D: "Desgaste acentuado na superfície do revestimento",
  P: "Buracos decorrentes da desagregação do revestimento e às vezes de camadas inferiores",
  R: "Remendo",
  PINTURA: "Pintura da tampa da bomba de água faltando pintura",
  QUEBRADO: "Vidraças quebradas",
  "VEGETAÇÃO": "Vegetação no telhado",
  FERRAGENS: "Ferragens expostas na viga do terminal",
  "SINALIZAÇÃO": "Sinalização apagada na entrada do terminal",
  "CONDIÇÕES INADEQUADAS": "Banheiro em condições inadequadas",
  BURACO: "Buraco no teto do terminal",
};

const DEFAULT_RESPONSAVEIS: PessoaItem[] = [
  { nome: "Alcides Vieira de Azevedo Bezerra", matricula: "40672015/01", funcao: "Especialista em Regulação" },
  { nome: "Enildo Manoel da Silva Júnior", matricula: "1796500/02", funcao: "Especialista em Regulação" },
  { nome: "Cícero Ronaldo Mendes de Andrade Júnior", matricula: "3485510/02", funcao: "Especialista em Regulação" },
  { nome: "Maria Fernanda da Silva Novaes", matricula: "18471080/01", funcao: "Especialista em Regulação" },
  { nome: "Eulina Menezes Maciel", matricula: "17127955/04", funcao: "Especialista em Regulação" },
  { nome: "Manuel Lucas Nascimento do Espírito Santo", matricula: "18533051/01", funcao: "Especialista em Regulação" },
];

const DEFAULT_COORDENADORES: PessoaItem[] = [
  { nome: "Maria Ângela Albuquerque de Freitas", matricula: "209640/01", funcao: "Coordenadora de Transportes e Rodovias" },
  { nome: "Enildo Manoel da Silva Júnior", matricula: "1796500/02", funcao: "Coordenador em Exercício" },
];

const DEFAULT_CUSTOM_NCS_SOCICAM: CustomNcItem[] = [
  { sigla: "PINTURA", descricao: "Pintura da tampa da bomba de agua faltando pintura" },
  { sigla: "QUEBRADO", descricao: "Vidraças quebradas" },
  { sigla: "VEGETAÇÃO", descricao: "Vegetação no telhado" },
  { sigla: "FERRAGENS", descricao: "Ferragens expostas na viga do terminal" },
  { sigla: "SINALIZAÇÃO", descricao: "Sinalização apagada na entrada do terminal" },
  { sigla: "CONDIÇÕES INADEQUADAS", descricao: "Banheiro em condições inadequadas" },
  { sigla: "BURACO", descricao: "Buraco no teto do terminal" },
];

export const useReportStore = create<ReportStore>((set, get) => ({
  tipoRelatorio: "CRA",
  categoriaRelatorio: "Fiscalização",
  autoAdvanceActive: true,
  compressImages: true,

  responsaveis: DEFAULT_RESPONSAVEIS,
  coordenadores: DEFAULT_COORDENADORES,
  contratos: ["CT. nº 043/2011", "CGPE-001/2006", "CT. nº 1.041.080/08"],
  contratosPadrao: {
    CRA: "CT. nº 043/2011",
    CRC: "CGPE-001/2006",
    SOCICAM: "CT. nº 1.041.080/08",
  },
  customNcs: [],
  customNcsSocicam: DEFAULT_CUSTOM_NCS_SOCICAM,
  baseNcOptions: DEFAULT_BASE_OPTIONS,
  mapSiglas: DEFAULT_MAP_SIGLAS,
  locaisSocicam: ["Garanhuns", "Arcoverde", "Serra Talhada", "Petrolina", "Caruaru", "TIP Recife"],

  workspaces: {
    CRA_Fiscalização: createEmptyWorkspace(),
    CRA_Monitoramento: createEmptyWorkspace(),
    CRC_Fiscalização: createEmptyWorkspace(),
    CRC_Monitoramento: createEmptyWorkspace(),
    SOCICAM_Fiscalização: createEmptyWorkspace(),
    SOCICAM_Monitoramento: createEmptyWorkspace(),
  },

  pastaLocalConectada: false,
  nomePastaLocal: "",
  setPastaLocalStatus: (conectada, nome = "") =>
    set({ pastaLocalConectada: conectada, nomePastaLocal: nome }),

  getActiveWorkspace: () => {
    const state = get();
    const key = getStateKey(state.tipoRelatorio, state.categoriaRelatorio);
    return state.workspaces[key];
  },

  getNcOptionsForCurrent: () => {
    const state = get();
    if (state.tipoRelatorio === "SOCICAM") {
      const opts: string[] = [];
      for (const item of state.customNcsSocicam) {
        const val = (item.sigla || item.descricao || "").trim();
        if (val && !opts.includes(val)) opts.push(val);
      }
      return opts;
    }
    const opts = [...state.baseNcOptions];
    for (const item of state.customNcs) {
      const val = (item.sigla || item.descricao || "").trim();
      if (val && !opts.includes(val)) opts.push(val);
    }
    return opts;
  },

  setTipoRelatorio: (tipo) => set({ tipoRelatorio: tipo }),

  cycleTipoRelatorio: () =>
    set((state) => {
      const next: TipoRelatorio =
        state.tipoRelatorio === "CRA"
          ? "CRC"
          : state.tipoRelatorio === "CRC"
          ? "SOCICAM"
          : "CRA";
      return { tipoRelatorio: next };
    }),

  setCategoriaRelatorio: (cat) => set({ categoriaRelatorio: cat }),

  toggleCategoriaRelatorio: () =>
    set((state) => ({
      categoriaRelatorio:
        state.categoriaRelatorio === "Fiscalização" ? "Monitoramento" : "Fiscalização",
    })),

  setAutoAdvanceActive: (val) => set({ autoAdvanceActive: val }),

  setCompressImages: (val) => set({ compressImages: val }),

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

  hydrateBootstrapConfig: (cfg) => {
    const localResp = localStorage.getItem("arpe_responsaveis");
    const localCoord = localStorage.getItem("arpe_coordenadores");
    const localContratos = localStorage.getItem("arpe_contratos");
    const localCustomNcs = localStorage.getItem("arpe_custom_ncs");
    const localCustomSoc = localStorage.getItem("arpe_custom_ncs_socicam");

    const responsaveis = localResp
      ? JSON.parse(localResp)
      : cfg.responsaveis?.length
      ? cfg.responsaveis
      : DEFAULT_RESPONSAVEIS;
    const coordenadores = localCoord
      ? JSON.parse(localCoord)
      : cfg.coordenadores?.length
      ? cfg.coordenadores
      : DEFAULT_COORDENADORES;
    const contratos = localContratos
      ? JSON.parse(localContratos)
      : cfg.contratos?.length
      ? cfg.contratos
      : ["CT. nº 043/2011", "CGPE-001/2006", "CT. nº 1.041.080/08"];
    const customNcs: CustomNcItem[] = localCustomNcs ? JSON.parse(localCustomNcs) : cfg.custom_ncs;
    const customNcsSocicam: CustomNcItem[] = localCustomSoc
      ? JSON.parse(localCustomSoc)
      : cfg.custom_ncs_socicam?.length
      ? cfg.custom_ncs_socicam
      : DEFAULT_CUSTOM_NCS_SOCICAM;

    const mergedMap = { ...DEFAULT_MAP_SIGLAS, ...cfg.map_siglas };
    for (const item of [...customNcs, ...customNcsSocicam]) {
      if (item.sigla && item.descricao) {
        mergedMap[item.sigla] = item.descricao;
      }
    }

    set({
      responsaveis,
      coordenadores,
      contratos,
      contratosPadrao: cfg.contratos_padrao,
      customNcs,
      customNcsSocicam,
      baseNcOptions: cfg.base_nc_options || DEFAULT_BASE_OPTIONS,
      mapSiglas: mergedMap,
      locaisSocicam: cfg.locais_socicam || [
        "Garanhuns",
        "Arcoverde",
        "Serra Talhada",
        "Petrolina",
        "Caruaru",
        "TIP Recife",
      ],
    });
  },

  setResponsaveis: (items) => {
    localStorage.setItem("arpe_responsaveis", JSON.stringify(items));
    set({ responsaveis: items });
  },

  setCoordenadores: (items) => {
    localStorage.setItem("arpe_coordenadores", JSON.stringify(items));
    set({ coordenadores: items });
  },

  setContratos: (items) => {
    localStorage.setItem("arpe_contratos", JSON.stringify(items));
    set({ contratos: items });
  },

  setCustomNcs: (items, mapSiglas) => {
    localStorage.setItem("arpe_custom_ncs", JSON.stringify(items));
    set((state) => {
      const nextMap = { ...state.mapSiglas, ...(mapSiglas || {}) };
      for (const it of items) {
        if (it.sigla && it.descricao) nextMap[it.sigla] = it.descricao;
      }
      return { customNcs: items, mapSiglas: nextMap };
    });
  },

  setCustomNcsSocicam: (items, mapSiglas) => {
    localStorage.setItem("arpe_custom_ncs_socicam", JSON.stringify(items));
    set((state) => {
      const nextMap = { ...state.mapSiglas, ...(mapSiglas || {}) };
      for (const it of items) {
        if (it.sigla && it.descricao) nextMap[it.sigla] = it.descricao;
      }
      return { customNcsSocicam: items, mapSiglas: nextMap };
    });
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

      const sorted = sortPhotosList(Array.from(existingByName.values()), ws.sortOption);
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
      const nextIdx = Math.max(0, Math.min(ws.carouselIndex, Math.max(0, nextPhotos.length - 1)));

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

  setMonitoramentoAnteriorData: (file, items) =>
    set((state) => {
      const key = getStateKey(state.tipoRelatorio, state.categoriaRelatorio);
      const ws = state.workspaces[key];
      return {
        workspaces: {
          ...state.workspaces,
          [key]: {
            ...ws,
            documentoAnteriorFile: file,
            oldPhotosToMatch: items,
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
      if (safeIdx === ws.activeFiscalizacaoIndex && ws.photos.length > 0) {
        return state;
      }

      // Salva as fotos da fiscalização atual no cache
      const currentOldFisc = ws.fiscalizacoes[ws.activeFiscalizacaoIndex];
      const currentOldId = currentOldFisc?.["ID da Fiscalização"]?.trim() || "";
      const updatedCache = { ...(ws.photosByFiscalizacao || {}) };
      if (currentOldId) {
        updatedCache[currentOldId] = ws.photos;
      }

      // Restaura as fotos da nova fiscalização
      const newFisc = ws.fiscalizacoes[safeIdx];
      const newId = newFisc?.["ID da Fiscalização"]?.trim() || "";
      const restoredPhotos = newId && updatedCache[newId] ? updatedCache[newId] : [];

      return {
        workspaces: {
          ...state.workspaces,
          [key]: {
            ...ws,
            activeFiscalizacaoIndex: safeIdx,
            photosByFiscalizacao: updatedCache,
            photos: restoredPhotos,
            carouselIndex: 0,
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

    // Salva fotos da fiscalização anterior no cache
    const currentOldFisc = ws.fiscalizacoes[ws.activeFiscalizacaoIndex];
    const currentOldId = currentOldFisc?.["ID da Fiscalização"]?.trim() || "";
    const updatedCache = { ...(ws.photosByFiscalizacao || {}) };
    if (currentOldId) {
      updatedCache[currentOldId] = ws.photos;
    }
    // A nova fiscalização inicia com fotos vazias []
    updatedCache[cleanId] = [];

    const nextFisc = [...ws.fiscalizacoes, { ...item, "ID da Fiscalização": cleanId }];
    set({
      workspaces: {
        ...state.workspaces,
        [key]: {
          ...ws,
          fiscalizacoes: nextFisc,
          activeFiscalizacaoIndex: nextFisc.length - 1,
          photosByFiscalizacao: updatedCache,
          photos: [],
          carouselIndex: 0,
          relatoriosGerados: [],
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
        if (id) updatedCache[id] = ws.photos;
        return {
          workspaces: {
            ...state.workspaces,
            [key]: {
              ...ws,
              fiscalizacoes: [item],
              photosByFiscalizacao: updatedCache,
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

      // Evita colisão de ID com outro cabeçalho diferente
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
      if (oldId && oldId !== newId && updatedCache[oldId]) {
        updatedCache[newId] = updatedCache[oldId];
        delete updatedCache[oldId];
      } else if (newId && !updatedCache[newId]) {
        updatedCache[newId] = ws.photos;
      }

      const nextFisc = ws.fiscalizacoes.map((f, idx) => (idx === targetIdx ? item : f));
      const nextNc = ws.registrosNc.map((nc) =>
        nc["ID da Fiscalização"] === oldId
          ? { ...nc, "ID da Fiscalização": newId, Terminal: item.Local }
          : nc
      );
      return {
        workspaces: {
          ...state.workspaces,
          [key]: {
            ...ws,
            fiscalizacoes: nextFisc,
            registrosNc: nextNc,
            photosByFiscalizacao: updatedCache,
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
    if (oldId && oldId !== newId && updatedCache[oldId]) {
      updatedCache[newId] = updatedCache[oldId];
      delete updatedCache[oldId];
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

      const activeFisc = ws.fiscalizacoes[ws.activeFiscalizacaoIndex];
      const activeFiscId = activeFisc?.["ID da Fiscalização"]?.trim() || "";
      if (activeFiscId && idSet.has(activeFiscId)) {
        ws.photos.forEach((p) => URL.revokeObjectURL(p.previewUrl));
      }

      const updatedCache = { ...(ws.photosByFiscalizacao || {}) };
      ids.forEach((id) => {
        if (updatedCache[id]) {
          updatedCache[id].forEach((p) => URL.revokeObjectURL(p.previewUrl));
          delete updatedCache[id];
        }
      });

      const nextFisc = ws.fiscalizacoes.filter((f) => !idSet.has(f["ID da Fiscalização"]));
      const safeIdx = Math.max(
        0,
        Math.min(ws.activeFiscalizacaoIndex, Math.max(0, nextFisc.length - 1))
      );
      const nextActiveId = nextFisc[safeIdx]?.["ID da Fiscalização"]?.trim() || "";
      const restoredPhotos = nextActiveId && updatedCache[nextActiveId] ? updatedCache[nextActiveId] : [];

      return {
        workspaces: {
          ...state.workspaces,
          [key]: {
            ...ws,
            fiscalizacoes: nextFisc,
            activeFiscalizacaoIndex: safeIdx,
            photosByFiscalizacao: updatedCache,
            photos: restoredPhotos,
            carouselIndex: 0,
            registrosNc: ws.registrosNc.filter((nc) => !idSet.has(nc["ID da Fiscalização"])),
            relatoriosGerados: [],
          },
        },
      };
    }),

  addOrUpdateRegistroNc: (rec, advancePhoto = true) =>
    set((state) => {
      const key = getStateKey(state.tipoRelatorio, state.categoriaRelatorio);
      const ws = state.workspaces[key];
      const isMon = state.categoriaRelatorio === "Monitoramento";
      let nextNcs = [...ws.registrosNc];

      if (isMon && ws.oldPhotosToMatch.length > 0) {
        // 1. Procura registro com mesma Identificação + Foto Anterior + ID Fiscalização
        let targetIdx = nextNcs.findIndex(
          (r) =>
            r.Identificação === rec.Identificação &&
            r["Foto Anterior"] === rec["Foto Anterior"] &&
            r["ID da Fiscalização"] === rec["ID da Fiscalização"] &&
            !r.is_relacionado
        );
        // 2. Se não encontrou, procura com Foto Anterior vazia
        if (targetIdx === -1) {
          targetIdx = nextNcs.findIndex(
            (r) =>
              r.Identificação === rec.Identificação &&
              !r["Foto Anterior"] &&
              r["ID da Fiscalização"] === rec["ID da Fiscalização"] &&
              !r.is_relacionado
          );
        }

        if (targetIdx === -1) {
          const countForId = nextNcs.filter(
            (r) => r["ID da Fiscalização"] === rec["ID da Fiscalização"]
          ).length;
          const novoNum = countForId + 1;
          nextNcs.push({
            ...rec,
            "Nº": novoNum,
            is_relacionado: false,
            grupo_relacao: `grp_${rec["ID da Fiscalização"]}_${novoNum}_${Date.now()}`,
          });
        } else {
          nextNcs[targetIdx] = {
            ...nextNcs[targetIdx],
            ...rec,
          };
        }

        // Sincronizar textos (Determinação, Observações, Análise ARPE, Situação) para a mesma Identificação
        nextNcs = nextNcs.map((r) => {
          if (
            r.Identificação === rec.Identificação &&
            r["ID da Fiscalização"] === rec["ID da Fiscalização"]
          ) {
            return {
              ...r,
              Situação: rec.Situação,
              Determinação: rec.Determinação,
              Observações: rec.Observações,
              "Análise ARPE": rec["Análise ARPE"],
            };
          }
          return r;
        });
      } else {
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
      }

      // Avanço automático do carrossel
      let nextCarouselIdx = ws.carouselIndex;
      if (advancePhoto && state.autoAdvanceActive) {
        if (isMon && ws.oldPhotosToMatch.length > 0) {
          if (nextCarouselIdx < ws.oldPhotosToMatch.length - 1) {
            nextCarouselIdx += 1;
          }
        } else if (ws.photos.length > 0) {
          if (nextCarouselIdx < ws.photos.length - 1) {
            nextCarouselIdx += 1;
          }
        }
      }

      return {
        workspaces: {
          ...state.workspaces,
          [key]: {
            ...ws,
            registrosNc: nextNcs,
            carouselIndex: nextCarouselIdx,
            pistaPersistida: rec.Pista || ws.pistaPersistida,
            trechoPersistido: rec.Trecho || ws.trechoPersistido,
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
        nc["ID da Fiscalização"] === targetIdFiscalizacao && nc["Nº"] === targetNumero
    );
    if (targetIndex === -1) {
      return { ok: false, error: "Ocorrência base não encontrada para relacionar." };
    }

    const baseNc = ws.registrosNc[targetIndex];
    const existingGrp = baseNc.grupo_relacao;
    if (baseNc.is_relacionado) {
      return {
        ok: false,
        error: "Este item já é uma 2ª foto relacionada. Selecione a ocorrência principal.",
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

    const isCraFisc = state.tipoRelatorio === "CRA" && state.categoriaRelatorio === "Fiscalização";
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
      "Direção (faixa)": faixaComb ? faixaComb.extenso : baseNc["Direção (faixa)"],
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
        error:
          "Não é permitido relacionar Não Conformidade com Ponto de Atenção.",
      };
    }

    const isPa = tipoRegistro !== undefined ? tipoRegistro === "Ponto de Atenção" : isBasePa;
    const siglasStr = siglas && siglas.length > 0 ? siglas.join(", ") : undefined;

    let ncField = updatedBase["Não Conformidade"];
    let paField = updatedBase["Ponto de Atenção"];

    if (tipoRegistro !== undefined) {
      if (isPa) {
        paField = siglasStr ?? (updatedBase["Ponto de Atenção"] || updatedBase["Não Conformidade"]);
        ncField = "";
      } else {
        ncField = siglasStr ?? (updatedBase["Não Conformidade"] || updatedBase["Ponto de Atenção"]);
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
      const defaultBase = state.tipoRelatorio === "SOCICAM" ? "SOCICAM" : "CRA.ST601.2794-2834";
      const baseRaw = codificacao?.trim() || baseCod || defaultBase;
      const baseLimpa = baseRaw.split("/")[0].trim() || baseRaw;
      const baseSiglas = (baseNc["Não Conformidade"] || baseNc["Ponto de Atenção"] || "")
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

    // Determina número da foto para exibição e correlação
    const foto2Idx = ws.photos.findIndex((p) => p.name === fotoName);
    const foto2Num = foto2Idx >= 0 ? foto2Idx + 1 : (baseNc["Nº"] || 1) + 1;

    // Insere logo após a ocorrência base
    const newRelatedRaw: RegistroNcItem = {
      ...updatedBase,
      Nº: foto2Num,
      Foto: fotoName,
      "Não Conformidade": ncField,
      "Ponto de Atenção": paField,
      Identificação: codFinal,
      Codificação: codFinal,
      "Direção (faixa)": faixaComb ? faixaComb.extenso : (direcaoFaixa !== undefined ? direcaoFaixa : updatedBase["Direção (faixa)"]),
      Trecho: trecho !== undefined ? trecho : updatedBase.Trecho,
      Observações:
        observacoes !== undefined && observacoes.trim()
          ? observacoes.trim()
          : (obs2Auto || updatedBase.Observações),
      "Legenda da Foto":
        legendaDaFoto !== undefined && legendaDaFoto.trim()
          ? legendaDaFoto.trim()
          : (obs2Auto || updatedBase["Legenda da Foto"]),
      Situação: situacao || updatedBase.Situação,
      is_relacionado: true,
      grupo_relacao: grpId,
    };

    const nextList = [...ws.registrosNc];
    nextList[targetIndex] = updatedBase;
    nextList.splice(targetIndex + 1, 0, newRelatedRaw);

    // Se no mesmo grupo houver outros itens, atualiza também a faixa para a faixa combinada
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

    let nextCarouselIdx = ws.carouselIndex;
    if (state.autoAdvanceActive && ws.photos.length > 0 && nextCarouselIdx < ws.photos.length - 1) {
      nextCarouselIdx += 1;
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
      const removeSet = new Set(keys.map((k) => `${k.idFiscalizacao}__${k.numero}`));

      // Exclui o grupo completo se qualquer membro da relação for removido
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

      // Garante invariante: nenhum registro secundário (is_relacionado) permanece órfão
      const baseGroups = new Set<string>();
      withoutRemoved.forEach((nc) => {
        if (!nc.is_relacionado && nc.grupo_relacao) {
          baseGroups.add(nc.grupo_relacao);
        }
      });
      const remaining = withoutRemoved.filter(
        (nc) => !nc.is_relacionado || (nc.grupo_relacao && baseGroups.has(nc.grupo_relacao))
      );

      // Recalcula a numeração sequencial ("Nº") por ID da Fiscalização
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

  executarAutoPreenchimento: () =>
    set((state) => {
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
        // Fallback quando nenhuma foto foi enviada ainda (permite testar geração imediatamente)
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
    }),

  limparRegistrosAtuais: (alsoClearPhotos = false) =>
    set((state) => {
      const key = getStateKey(state.tipoRelatorio, state.categoriaRelatorio);
      const ws = state.workspaces[key];
      const activeFisc = ws.fiscalizacoes[ws.activeFiscalizacaoIndex];
      const activeFiscId = activeFisc?.["ID da Fiscalização"]?.trim() || "";
      const updatedCache = { ...(ws.photosByFiscalizacao || {}) };
      if (alsoClearPhotos) {
        ws.photos.forEach((p) => URL.revokeObjectURL(p.previewUrl));
        if (activeFiscId) updatedCache[activeFiscId] = [];
      }
      const remainingNcs = activeFiscId
        ? ws.registrosNc.filter((r) => (r["ID da Fiscalização"] || "").trim() !== activeFiscId)
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

  reiniciarModalidadeAtual: () =>
    set((state) => {
      const key = getStateKey(state.tipoRelatorio, state.categoriaRelatorio);
      const ws = state.workspaces[key];

      // Revoga todas as fotos em tela e em cache desta modalidade
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

      return {
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
      return {
        workspaces: {
          ...state.workspaces,
          [key]: {
            ...ws,
            fiscalizacoes: dados.fiscalizacoes,
            activeFiscalizacaoIndex: 0,
            registrosNc: dados.registrosNc,
            photos: dados.photos,
            carouselIndex: 0,
            pistaPersistida: dados.pistaPersistida || "",
            trechoPersistido: dados.trechoPersistido || "",
            documentoAnteriorFile: dados.documentoAnteriorFile ?? ws.documentoAnteriorFile,
            planilhaElegibilidadeFile: dados.planilhaElegibilidadeFile ?? ws.planilhaElegibilidadeFile,
            relatoriosGerados: [],
          },
        },
      };
    }),
}));
