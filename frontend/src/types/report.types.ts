export type TipoRelatorio = "CRA" | "CRC" | "SOCICAM";
export type CategoriaRelatorio = "Fiscalização" | "Monitoramento";
export type SituacaoNC = "Pendente" | "Parcialmente Sanada" | "Sanada";
export type SortOption = "Nome (A-Z / 0-9)" | "Nome (Z-A / 9-0)" | "Ordem de Upload";

export type StateKey =
  | "CRA_Fiscalização"
  | "CRA_Monitoramento"
  | "CRC_Fiscalização"
  | "CRC_Monitoramento"
  | "SOCICAM_Fiscalização"
  | "SOCICAM_Monitoramento";

export interface PessoaItem {
  nome: string;
  matricula: string;
  funcao: string;
}

export interface CustomNcItem {
  sigla: string;
  descricao: string;
}

export interface FiscalizacaoItem {
  "ID da Fiscalização": string;
  Data: string;
  Hora: string;
  Cidade: string;
  Local: string;
  "Pessoal Responsável": string;
  Coordenador: string;
  Contrato: string;
  Período: string;
  "Relatório Gerado": boolean;
}

export interface RegistroNcItem {
  "ID da Fiscalização": string;
  "Nº": number;
  Terminal: string;
  Pista: string;
  Trecho: string;
  "Não Conformidade": string;
  "Ponto de Atenção": string;
  Foto: string;
  "Foto Anterior": string;
  "Legenda Anterior": string;
  "Legenda da Foto"?: string;
  Observações: string;
  Identificação: string;
  "Direção (faixa)": string;
  "Fundamento da infração": string;
  Determinação: string;
  Situação: SituacaoNC;
  "Análise ARPE": string;
  is_relacionado?: boolean;
  grupo_relacao?: string;
}

export interface UploadedPhotoItem {
  id: string;
  name: string;
  file: File;
  previewUrl: string;
  uploadOrder: number;
}

export interface MonitoramentoAnteriorItem {
  id_nc: string;
  constatacao: string;
  pista: string;
  trecho: string;
  old_legend: string;
  old_photo_path: string;
  old_photo_b64: string;
  display_label: string;
}

export interface RelatorioGeradoItem {
  nome: string;
  base64: string;
}

export interface BootstrapConfigResponse {
  responsaveis: PessoaItem[];
  coordenadores: PessoaItem[];
  contratos: string[];
  contratos_padrao: Record<TipoRelatorio, string>;
  custom_ncs: CustomNcItem[];
  custom_ncs_socicam: CustomNcItem[];
  base_nc_options: string[];
  map_siglas: Record<string, string>;
  locais_socicam: string[];
}

export interface TermosUI {
  term_fisc: string;
  term_fisc_lower: string;
  term_fisc_plural: string;
  term_fisc_plural_lower: string;
  term_fisc_prep: string;
  term_fisc_prep_f: string;
  term_fisc_pessoal: string;
}

export function obterTermosUI(isMonitoring: boolean): TermosUI {
  return {
    term_fisc: isMonitoring ? "Monitoramento" : "Fiscalização",
    term_fisc_lower: isMonitoring ? "monitoramento" : "fiscalização",
    term_fisc_plural: isMonitoring ? "Monitoramentos" : "Fiscalizações",
    term_fisc_plural_lower: isMonitoring ? "monitoramentos" : "fiscalizações",
    term_fisc_prep: isMonitoring ? "do Monitoramento" : "da Fiscalização",
    term_fisc_prep_f: isMonitoring ? "pelo Monitoramento" : "pela Fiscalização",
    term_fisc_pessoal: isMonitoring ? "Equipe de Monitoramento" : "Equipe de Fiscalização",
  };
}

