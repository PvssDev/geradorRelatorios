import {
  BootstrapConfigResponse,
  CategoriaRelatorio,
  CustomNcItem,
  FiscalizacaoItem,
  MonitoramentoAnteriorItem,
  PessoaItem,
  RegistroNcItem,
  RelatorioGeradoItem,
  TipoRelatorio,
  UploadedPhotoItem,
} from "../types/report.types";
import { comprimirFotoParaEnvio } from "./imageCompressor";
import { otimizarArquivoOfficeParaEnvio } from "./documentOptimizer";

const API_BASE = import.meta.env.VITE_API_URL || "";

async function parseApiError(res: Response, fallbackMsg: string): Promise<string> {
  if (res.status === 413) {
    return "O arquivo ou lote enviado excede o limite de 4,5 MB do servidor em produção. Reduza o tamanho do documento/planilha ou divida o envio.";
  }
  if (res.status === 504) {
    return "O processamento excedeu o tempo limite do servidor (timeout). Tente novamente com arquivos menores.";
  }
  const err = await res.json().catch(() => null);
  if (err && typeof err.detail === "string" && err.detail.trim()) {
    return err.detail;
  }
  return `${fallbackMsg} (HTTP ${res.status})`;
}

export async function fetchBootstrapConfig(): Promise<BootstrapConfigResponse> {
  const res = await fetch(`${API_BASE}/api/config/bootstrap`);
  if (!res.ok) {
    throw new Error("Falha ao carregar configurações iniciais do servidor.");
  }
  return res.json();
}

export async function saveResponsaveisApi(items: PessoaItem[]): Promise<PessoaItem[]> {
  const res = await fetch(`${API_BASE}/api/config/responsaveis`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(items),
  });
  if (!res.ok) throw new Error("Falha ao salvar responsáveis.");
  const data = await res.json();
  return data.responsaveis;
}

export async function saveCoordenadoresApi(items: PessoaItem[]): Promise<PessoaItem[]> {
  const res = await fetch(`${API_BASE}/api/config/coordenadores`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(items),
  });
  if (!res.ok) throw new Error("Falha ao salvar coordenadores.");
  const data = await res.json();
  return data.coordenadores;
}

export async function saveContratosApi(items: string[]): Promise<string[]> {
  const res = await fetch(`${API_BASE}/api/config/contratos`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(items),
  });
  if (!res.ok) throw new Error("Falha ao salvar contratos.");
  const data = await res.json();
  return data.contratos;
}

export async function saveCustomNcsApi(
  items: CustomNcItem[],
  isSocicam: boolean
): Promise<{ list: CustomNcItem[]; map_siglas: Record<string, string> }> {
  const endpoint = isSocicam ? "/api/config/custom-ncs-socicam" : "/api/config/custom-ncs";
  const res = await fetch(`${API_BASE}${endpoint}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(items),
  });
  if (!res.ok) throw new Error("Falha ao salvar Não Conformidades personalizadas.");
  const data = await res.json();
  return {
    list: isSocicam ? data.custom_ncs_socicam : data.custom_ncs,
    map_siglas: data.map_siglas,
  };
}

export async function parseMonitoramentoAnteriorApi(
  file: File
): Promise<{ metadados: Record<string, unknown>; itens_pendentes: MonitoramentoAnteriorItem[] }> {
  const optimizedFile = await otimizarArquivoOfficeParaEnvio(file, {
    maxWidth: 960,
    maxHeight: 720,
    quality: 0.7,
  });

  const formData = new FormData();
  formData.append("arquivo", optimizedFile, optimizedFile.name);

  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), 55_000);

  try {
    const res = await fetch(`${API_BASE}/api/monitoramento/parse`, {
      method: "POST",
      body: formData,
      signal: controller.signal,
    });
    if (!res.ok) {
      throw new Error(
        await parseApiError(res, "Erro ao ler arquivo de monitoramento anterior.")
      );
    }
    return res.json();
  } catch (err: unknown) {
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new Error("Tempo limite excedido ao processar o relatório anterior (.docx).");
    }
    throw err;
  } finally {
    window.clearTimeout(timeoutId);
  }
}

export async function downloadPlanilhaExcelApi(
  fiscalizacoes: FiscalizacaoItem[],
  registros_nc: RegistroNcItem[]
): Promise<Blob> {
  const res = await fetch(`${API_BASE}/api/relatorios/planilha`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ fiscalizacoes, registros_nc }),
  });
  if (!res.ok) {
    throw new Error("Erro ao gerar a planilha Excel.");
  }
  return res.blob();
}

export async function gerarRelatoriosApi(params: {
  tipo_relatorio: TipoRelatorio;
  categoria_relatorio: CategoriaRelatorio;
  fiscalizacoes: FiscalizacaoItem[];
  registros_nc: RegistroNcItem[];
  photos: UploadedPhotoItem[];
  oldItems: MonitoramentoAnteriorItem[];
  documentoAnteriorFile: File | null;
  planilhaElegibilidadeFile?: File | null;
  customSiglasMap: Record<string, string>;
  responsaveis: PessoaItem[];
  coordenadores: PessoaItem[];
  compressImages?: boolean;
}): Promise<{ relatorios: RelatorioGeradoItem[]; avisos: string[] }> {
  const formData = new FormData();
  const shouldCompress = params.compressImages !== false;

  // Filtra e comprime apenas as fotos referenciadas nas NCs (ou todas se necessário) para otimizar payload na Vercel
  const nomesReferenciados = new Set(
    params.registros_nc
      .map((nc) => (nc.Foto || "").trim().toLowerCase())
      .filter(Boolean)
  );

  const fotosParaEnviar = params.photos.filter(
    (p) => nomesReferenciados.size === 0 || nomesReferenciados.has(p.name.trim().toLowerCase())
  );

  for (const photoItem of fotosParaEnviar) {
    const fileToSend = shouldCompress
      ? await comprimirFotoParaEnvio(photoItem.file)
      : photoItem.file;
    formData.append("fotos_atuais", fileToSend, photoItem.name);
  }

  // Mapa de fotos anteriores em Base64 (para funcionamento stateless na Vercel)
  const fotosAnterioresB64: Record<string, string> = {};
  for (const oldItem of params.oldItems) {
    if (oldItem.old_photo_path && oldItem.old_photo_b64) {
      fotosAnterioresB64[oldItem.old_photo_path] = oldItem.old_photo_b64;
    }
  }

  const payload = {
    tipo_relatorio: params.tipo_relatorio,
    categoria_relatorio: params.categoria_relatorio,
    fiscalizacoes: params.fiscalizacoes,
    registros_nc: params.registros_nc,
    fotos_anteriores_b64: fotosAnterioresB64,
    custom_siglas_map: params.customSiglasMap,
    responsaveis_override: params.responsaveis,
    coordenadores_override: params.coordenadores,
  };

  formData.append("payload_json", JSON.stringify(payload));

  if (params.documentoAnteriorFile) {
    const docToSend = shouldCompress
      ? await otimizarArquivoOfficeParaEnvio(params.documentoAnteriorFile)
      : params.documentoAnteriorFile;
    formData.append("documento_anterior", docToSend, docToSend.name);
  }

  if (params.planilhaElegibilidadeFile) {
    const sheetToSend = shouldCompress
      ? await otimizarArquivoOfficeParaEnvio(params.planilhaElegibilidadeFile)
      : params.planilhaElegibilidadeFile;
    formData.append("planilha_elegibilidade", sheetToSend, sheetToSend.name);
  }

  const res = await fetch(`${API_BASE}/api/relatorios/gerar`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    throw new Error(await parseApiError(res, "Falha ao gerar relatórios."));
  }

  return res.json();
}

