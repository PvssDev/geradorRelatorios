import type { StateCreator } from "zustand";
import { CustomNcItem, PessoaItem } from "../../types/report.types";
import type { CatalogSlice, ReportStore } from "../types";

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
  VEGETAÇÃO: "Vegetação no telhado",
  FERRAGENS: "Ferragens expostas na viga do terminal",
  SINALIZAÇÃO: "Sinalização apagada na entrada do terminal",
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

export const createCatalogSlice: StateCreator<ReportStore, [], [], CatalogSlice> = (
  set,
  get
) => ({
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
  locaisSocicam: [
    "Garanhuns",
    "Arcoverde",
    "Serra Talhada",
    "Petrolina",
    "Caruaru",
    "TIP Recife",
  ],

  getNcOptionsForCurrent: () => {
    const state = get();
    if (state.tipoRelatorio === "SOCICAM") {
      return state.customNcsSocicam.map((i) => i.sigla);
    }
    const base = [...state.baseNcOptions];
    for (const item of state.customNcs) {
      if (item.sigla && !base.includes(item.sigla)) {
        base.push(item.sigla);
      }
    }
    return base;
  },

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
    const customNcs: CustomNcItem[] = localCustomNcs
      ? JSON.parse(localCustomNcs)
      : cfg.custom_ncs;
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
});

