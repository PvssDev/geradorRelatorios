// -*- coding: utf-8 -*-
/**
 * Serviço de Persistência Local por Pasta (geradorBD).
 * 
 * Organiza a persistência das 6 modalidades na pasta local "geradorBD"
 * de forma modular e estruturada:
 * 
 * geradorBD/
 * └── <modalidade>/               (ex: cra_fiscalizacao, cra_monitoramento, etc.)
 *     ├── estado/
 *     │   └── estado.json
 *     └── midia/
 *         ├── fotos/
 *         │   └── foto_01.jpg
 *         └── arquivos/
 *             ├── documento_anterior.docx (ou .pdf)
 *             └── planilha_elegibilidade.xlsx
 */

import {
  CategoriaRelatorio,
  FiscalizacaoItem,
  RegistroNcItem,
  TipoRelatorio,
  UploadedPhotoItem,
} from "../types/report.types";
import { ModalityWorkspaceState } from "../store/useReportStore";

export class PastaNaoEncontradaError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "PastaNaoEncontradaError";
  }
}

const IDB_NAME = "arpe_gerador_relatorios_db";
const IDB_STORE = "diretorio_handles";
const IDB_KEY = "geradorBD_dir_handle";

/**
 * Abre o banco IndexedDB nativo do navegador.
 */
function abrirBancoIndexedDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    if (typeof indexedDB === "undefined") {
      reject(new Error("IndexedDB não disponível no navegador"));
      return;
    }
    const request = indexedDB.open(IDB_NAME, 1);
    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(IDB_STORE)) {
        db.createObjectStore(IDB_STORE);
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error);
  });
}

/**
 * Salva o FileSystemDirectoryHandle no IndexedDB para uso em sessões futuras.
 */
export async function salvarHandleIndexedDB(
  handle: FileSystemDirectoryHandle
): Promise<void> {
  try {
    const db = await abrirBancoIndexedDB();
    await new Promise<void>((resolve, reject) => {
      const tx = db.transaction(IDB_STORE, "readwrite");
      const store = tx.objectStore(IDB_STORE);
      const req = store.put(handle, IDB_KEY);
      req.onsuccess = () => resolve();
      req.onerror = () => reject(req.error);
    });
  } catch (err) {
    console.warn("Aviso: Falha ao persistir handle no IndexedDB:", err);
  }
}

/**
 * Recupera o FileSystemDirectoryHandle previamente salvo no IndexedDB.
 */
export async function obterHandleSalvoIndexedDB(): Promise<FileSystemDirectoryHandle | null> {
  try {
    const db = await abrirBancoIndexedDB();
    return await new Promise<FileSystemDirectoryHandle | null>((resolve) => {
      const tx = db.transaction(IDB_STORE, "readonly");
      const store = tx.objectStore(IDB_STORE);
      const req = store.get(IDB_KEY);
      req.onsuccess = () => resolve((req.result as FileSystemDirectoryHandle) || null);
      req.onerror = () => resolve(null);
    });
  } catch {
    return null;
  }
}

/**
 * Limpa o handle salvo no IndexedDB (desconectar).
 */
export async function limparHandleSalvoIndexedDB(): Promise<void> {
  try {
    const db = await abrirBancoIndexedDB();
    await new Promise<void>((resolve) => {
      const tx = db.transaction(IDB_STORE, "readwrite");
      const store = tx.objectStore(IDB_STORE);
      const req = store.delete(IDB_KEY);
      req.onsuccess = () => resolve();
      req.onerror = () => resolve();
    });
  } catch {
    // Ignora
  }
}

/**
 * Verifica o status de conexão da pasta geradorBD de forma automática.
 * Executada no boot da página ou ao revalidar.
 */
export async function verificarStatusConexaoPasta(): Promise<{
  conectado: boolean;
  handle: FileSystemDirectoryHandle | null;
  nomePasta?: string;
}> {
  if (typeof window === "undefined" || !("showDirectoryPicker" in window)) {
    return { conectado: false, handle: null };
  }

  const handle = await obterHandleSalvoIndexedDB();
  if (!handle) {
    return { conectado: false, handle: null };
  }

  try {
    const perm = await (handle as any).queryPermission({ mode: "readwrite" });
    if (perm === "granted") {
      return { conectado: true, handle, nomePasta: handle.name };
    }
  } catch (err) {
    console.warn("Erro ao checar permissão da pasta:", err);
  }

  return { conectado: false, handle: null, nomePasta: handle.name };
}

/**
 * Retorna o identificador normalizado da pasta para cada uma das 6 modalidades.
 */
export function obterPastaModalidade(
  tipo: TipoRelatorio,
  categoria: CategoriaRelatorio
): string {
  const t = tipo.toLowerCase();
  const c = categoria.toLowerCase().replace(/ç/g, "c").replace(/ã/g, "a");
  return `${t}_${c}`;
}

/**
 * Solicita ou reaproveita a pasta "geradorBD".
 */
export async function solicitarPastaGeradorBD(
  forcePicker: boolean = false
): Promise<FileSystemDirectoryHandle> {
  if (!("showDirectoryPicker" in window)) {
    throw new Error(
      "Seu navegador não suporta a File System Access API nativa. Recomendamos Google Chrome ou Microsoft Edge no Windows."
    );
  }

  if (!forcePicker) {
    const handleSalvo = await obterHandleSalvoIndexedDB();
    if (handleSalvo) {
      try {
        let perm = await (handleSalvo as any).queryPermission({ mode: "readwrite" });
        if (perm !== "granted") {
          perm = await (handleSalvo as any).requestPermission({ mode: "readwrite" });
        }
        if (perm === "granted") {
          return handleSalvo;
        }
      } catch (err) {
        console.warn("Handle existente inválido, abrindo seletor:", err);
      }
    }
  }

  const pickedHandle = await (window as any).showDirectoryPicker({
    mode: "readwrite",
    startIn: "documents",
  });

  let targetHandle: FileSystemDirectoryHandle;

  if (pickedHandle.name.toLowerCase() === "geradorbd") {
    targetHandle = pickedHandle;
  } else {
    try {
      targetHandle = await pickedHandle.getDirectoryHandle("geradorBD", {
        create: false,
      });
    } catch {
      throw new PastaNaoEncontradaError(
        `A pasta selecionada foi "${pickedHandle.name}". Para salvar ou carregar, selecione uma pasta chamada exatamente "geradorBD".`
      );
    }
  }

  await salvarHandleIndexedDB(targetHandle);
  return targetHandle;
}

/**
 * Salva o estado atual, fotos e arquivos anexos na estrutura padronizada da modalidade:
 * geradorBD/<modalidade>/estado/estado.json
 * geradorBD/<modalidade>/midia/fotos/
 * geradorBD/<modalidade>/midia/arquivos/
 */
export async function salvarEstadoEmGeradorBD(
  dirHandle: FileSystemDirectoryHandle,
  tipo: TipoRelatorio,
  categoria: CategoriaRelatorio,
  workspace: ModalityWorkspaceState
): Promise<{ totalFotos: number; totalNcs: number; totalArquivos: number }> {
  const pastaModalidadeNome = obterPastaModalidade(tipo, categoria);

  // 1. Cria ou acessa a pasta da modalidade (ex: cra_fiscalizacao)
  const modHandle = await dirHandle.getDirectoryHandle(pastaModalidadeNome, {
    create: true,
  });

  // 2. Cria subpastas: estado/ e midia/ (fotos/ e arquivos/)
  const estadoHandle = await modHandle.getDirectoryHandle("estado", { create: true });
  const midiaHandle = await modHandle.getDirectoryHandle("midia", { create: true });
  const fotosHandle = await midiaHandle.getDirectoryHandle("fotos", { create: true });
  const arquivosHandle = await midiaHandle.getDirectoryHandle("arquivos", { create: true });

  let totalArquivosSalvos = 0;
  const metaArquivos: Array<{ slot: string; nome: string; size: number; type: string }> = [];

  // Salva Documento Anterior (se houver)
  if (workspace.documentoAnteriorFile) {
    try {
      const docFile = workspace.documentoAnteriorFile;
      const fileHandle = await arquivosHandle.getFileHandle(docFile.name, { create: true });
      const writable = await (fileHandle as any).createWritable();
      await writable.write(docFile);
      await writable.close();
      totalArquivosSalvos++;
      metaArquivos.push({
        slot: "documentoAnterior",
        nome: docFile.name,
        size: docFile.size,
        type: docFile.type,
      });
    } catch (errDoc) {
      console.warn("Erro ao salvar documento anterior:", errDoc);
    }
  }

  // Salva Planilha de Elegibilidade (se houver)
  if (workspace.planilhaElegibilidadeFile) {
    try {
      const planFile = workspace.planilhaElegibilidadeFile;
      const fileHandle = await arquivosHandle.getFileHandle(planFile.name, { create: true });
      const writable = await (fileHandle as any).createWritable();
      await writable.write(planFile);
      await writable.close();
      totalArquivosSalvos++;
      metaArquivos.push({
        slot: "planilhaElegibilidade",
        nome: planFile.name,
        size: planFile.size,
        type: planFile.type,
      });
    } catch (errPlan) {
      console.warn("Erro ao salvar planilha de elegibilidade:", errPlan);
    }
  }

  // Salva fotos em midia/fotos/
  for (const photo of workspace.photos) {
    try {
      let blob: Blob | null = null;
      if (photo.file) {
        blob = photo.file;
      } else if (photo.previewUrl && photo.previewUrl.startsWith("data:")) {
        const res = await fetch(photo.previewUrl);
        blob = await res.blob();
      }

      if (blob) {
        const photoFileHandle = await fotosHandle.getFileHandle(photo.name, {
          create: true,
        });
        const photoWritable = await (photoFileHandle as any).createWritable();
        await photoWritable.write(blob);
        await photoWritable.close();
      }
    } catch (errFoto) {
      console.warn(`Aviso ao gravar foto local ${photo.name}:`, errFoto);
    }
  }

  // 3. Monta o payload completo e salva em estado/estado.json
  const payload = {
    tipo_relatorio: tipo,
    categoria_relatorio: categoria,
    modalidade: pastaModalidadeNome,
    salvo_em: new Date().toISOString(),
    temp_fiscalizacoes: workspace.fiscalizacoes,
    temp_nc: workspace.registrosNc,
    pista_persistida: workspace.pistaPersistida,
    trecho_persistido: workspace.trechoPersistido,
    sort_option: workspace.sortOption,
    carousel_index: workspace.carouselIndex,
    meta_arquivos: metaArquivos,
    meta_fotos: workspace.photos.map((p) => ({
      id: p.id,
      name: p.name,
      uploadOrder: p.uploadOrder,
      size: p.file?.size || 0,
      type: p.file?.type || "image/jpeg",
    })),
  };

  const estadoFileHandle = await estadoHandle.getFileHandle("estado.json", { create: true });
  const writableStream = await (estadoFileHandle as any).createWritable();
  await writableStream.write(JSON.stringify(payload, null, 2));
  await writableStream.close();

  await salvarHandleIndexedDB(dirHandle);

  return {
    totalFotos: workspace.photos.length,
    totalNcs: workspace.registrosNc.length,
    totalArquivos: totalArquivosSalvos,
  };
}

/**
 * Carrega o estado, fotos e arquivos da modalidade a partir da estrutura padronizada:
 * geradorBD/<modalidade>/estado/estado.json
 * geradorBD/<modalidade>/midia/fotos/
 * geradorBD/<modalidade>/midia/arquivos/
 */
export async function carregarEstadoDeGeradorBD(
  dirHandle: FileSystemDirectoryHandle,
  tipo: TipoRelatorio,
  categoria: CategoriaRelatorio
): Promise<{
  fiscalizacoes: FiscalizacaoItem[];
  registrosNc: RegistroNcItem[];
  photos: UploadedPhotoItem[];
  pistaPersistida: string;
  trechoPersistido: string;
  documentoAnteriorFile: File | null;
  planilhaElegibilidadeFile: File | null;
}> {
  const pastaModalidadeNome = obterPastaModalidade(tipo, categoria);

  let modHandle: FileSystemDirectoryHandle;
  try {
    modHandle = await dirHandle.getDirectoryHandle(pastaModalidadeNome, { create: false });
  } catch {
    throw new Error(
      `Nenhum dado salvo encontrado para "${tipo} - ${categoria}". A pasta "${pastaModalidadeNome}" não existe em geradorBD.`
    );
  }

  // 1. Tenta carregar estado/estado.json (ou fallback para formato legado da raiz)
  let payload: any = null;
  try {
    const estadoHandle = await modHandle.getDirectoryHandle("estado", { create: false });
    const fileHandle = await estadoHandle.getFileHandle("estado.json", { create: false });
    const file = await fileHandle.getFile();
    const text = await file.text();
    payload = JSON.parse(text);
  } catch {
    // Tenta formato de migração caso exista na raiz do modHandle
    try {
      const legacyJsonName = `${pastaModalidadeNome}.json`;
      const legacyHandle = await dirHandle.getFileHandle(legacyJsonName, { create: false });
      const legacyFile = await legacyHandle.getFile();
      payload = JSON.parse(await legacyFile.text());
    } catch {
      throw new Error(
        `O arquivo "estado/estado.json" não foi localizado dentro de "${pastaModalidadeNome}".`
      );
    }
  }

  const fiscalizacoes: FiscalizacaoItem[] =
    payload.temp_fiscalizacoes || payload.fiscalizacoes || [];
  const registrosNc: RegistroNcItem[] =
    payload.temp_nc || payload.registrosNc || [];
  const pistaPersistida: string = payload.pista_persistida || "";
  const trechoPersistido: string = payload.trecho_persistido || "";

  // 2. Restaura Fotos de midia/fotos/
  const fotosRestauradas: UploadedPhotoItem[] = [];
  try {
    const midiaHandle = await modHandle.getDirectoryHandle("midia", { create: false });
    const fotosHandle = await midiaHandle.getDirectoryHandle("fotos", { create: false });

    const metaMap = new Map<string, any>();
    if (Array.isArray(payload.meta_fotos)) {
      for (const m of payload.meta_fotos) {
        if (m.name) metaMap.set(m.name, m);
      }
    }

    let order = 0;
    for await (const [name, entry] of (fotosHandle as any).entries()) {
      if (entry.kind === "file") {
        try {
          const entryFile = await (entry as FileSystemFileHandle).getFile();
          const meta = metaMap.get(name);
          const photoId = meta?.id || `foto-${Date.now()}-${order}`;
          const uploadOrder =
            typeof meta?.uploadOrder === "number" ? meta.uploadOrder : order++;
          const previewUrl = URL.createObjectURL(entryFile);

          fotosRestauradas.push({
            id: photoId,
            name: entryFile.name,
            file: entryFile,
            previewUrl,
            uploadOrder,
          });
        } catch (errFoto) {
          console.warn(`Erro ao ler arquivo de foto ${name}:`, errFoto);
        }
      }
    }
  } catch {
    // Midia/fotos ainda não existe ou vazia
  }

  // 3. Restaura Arquivos Anexos de midia/arquivos/
  let documentoAnteriorFile: File | null = null;
  let planilhaElegibilidadeFile: File | null = null;

  try {
    const midiaHandle = await modHandle.getDirectoryHandle("midia", { create: false });
    const arquivosHandle = await midiaHandle.getDirectoryHandle("arquivos", { create: false });

    const metaArquivos: Array<{ slot: string; nome: string }> = payload.meta_arquivos || [];

    for await (const [name, entry] of (arquivosHandle as any).entries()) {
      if (entry.kind === "file") {
        try {
          const arqFile = await (entry as FileSystemFileHandle).getFile();
          const meta = metaArquivos.find((m) => m.nome === name);

          if (meta?.slot === "documentoAnterior" || name.endsWith(".docx") || name.endsWith(".pdf")) {
            if (!documentoAnteriorFile) documentoAnteriorFile = arqFile;
          } else if (meta?.slot === "planilhaElegibilidade" || name.endsWith(".xlsx") || name.endsWith(".xls")) {
            if (!planilhaElegibilidadeFile) planilhaElegibilidadeFile = arqFile;
          }
        } catch (errArq) {
          console.warn(`Erro ao ler anexo ${name}:`, errArq);
        }
      }
    }
  } catch {
    // Midia/arquivos ainda não existe ou vazia
  }

  await salvarHandleIndexedDB(dirHandle);

  return {
    fiscalizacoes,
    registrosNc,
    photos: fotosRestauradas,
    pistaPersistida,
    trechoPersistido,
    documentoAnteriorFile,
    planilhaElegibilidadeFile,
  };
}
