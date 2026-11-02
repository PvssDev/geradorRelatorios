// -*- coding: utf-8 -*-
/**
 * Serviço de Persistência Local por Pasta (geradorBD).
 * 
 * Permite salvar e carregar atomicamente o estado da modalidade ativa
 * e fotos diretamente no disco do usuário em uma pasta chamada "geradorBD",
 * com memorização do handle no IndexedDB para reconexão automática.
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
    // Consulta a permissão sem abrir prompt invasivo
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
 * Retorna o nome do arquivo JSON correspondente à combinação.
 */
export function obterNomeArquivoJson(
  tipo: TipoRelatorio,
  categoria: CategoriaRelatorio
): string {
  const t = tipo.toLowerCase();
  const c = categoria.toLowerCase().replace(/ç/g, "c").replace(/ã/g, "a");
  return `${t}_${c}.json`;
}

/**
 * Retorna o nome da pasta de mídia correspondente à combinação.
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
 * Se forcePicker for false e houver handle salvo com permissão, reaproveita.
 */
export async function solicitarPastaGeradorBD(
  forcePicker: boolean = false
): Promise<FileSystemDirectoryHandle> {
  if (!("showDirectoryPicker" in window)) {
    throw new Error(
      "Seu navegador não suporta a File System Access API nativa. Recomendamos Google Chrome ou Microsoft Edge no Windows."
    );
  }

  // Tenta reaproveitar o handle salvo no IndexedDB se não for forçado
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

  // Abre o explorador de arquivos nativo do SO
  const pickedHandle = await (window as any).showDirectoryPicker({
    mode: "readwrite",
    startIn: "documents",
  });

  let targetHandle: FileSystemDirectoryHandle;

  // Caso 1: O usuário selecionou a própria pasta geradorBD
  if (pickedHandle.name.toLowerCase() === "geradorbd") {
    targetHandle = pickedHandle;
  } else {
    // Caso 2: O usuário selecionou uma pasta pai que contém geradorBD
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

  // Persiste no IndexedDB para conexões automáticas futuras
  await salvarHandleIndexedDB(targetHandle);
  return targetHandle;
}

/**
 * Salva o estado atual e todas as fotos da modalidade na pasta geradorBD.
 */
export async function salvarEstadoEmGeradorBD(
  dirHandle: FileSystemDirectoryHandle,
  tipo: TipoRelatorio,
  categoria: CategoriaRelatorio,
  workspace: ModalityWorkspaceState
): Promise<{ totalFotos: number; totalNcs: number }> {
  const nomeJson = obterNomeArquivoJson(tipo, categoria);
  const pastaModalidade = obterPastaModalidade(tipo, categoria);

  const payload = {
    tipo_relatorio: tipo,
    categoria_relatorio: categoria,
    salvo_em: new Date().toISOString(),
    temp_fiscalizacoes: workspace.fiscalizacoes,
    temp_nc: workspace.registrosNc,
    pista_persistida: workspace.pistaPersistida,
    trecho_persistido: workspace.trechoPersistido,
    sort_option: workspace.sortOption,
    carousel_index: workspace.carouselIndex,
    meta_fotos: workspace.photos.map((p) => ({
      id: p.id,
      name: p.name,
      uploadOrder: p.uploadOrder,
      size: p.file?.size || 0,
      type: p.file?.type || "image/jpeg",
    })),
  };

  const fileHandle = await dirHandle.getFileHandle(nomeJson, { create: true });
  const writableStream = await (fileHandle as any).createWritable();
  await writableStream.write(JSON.stringify(payload, null, 2));
  await writableStream.close();

  if (workspace.photos.length > 0) {
    const modHandle = await dirHandle.getDirectoryHandle(pastaModalidade, {
      create: true,
    });
    const midiaHandle = await modHandle.getDirectoryHandle("midia", {
      create: true,
    });
    const fotosHandle = await midiaHandle.getDirectoryHandle("fotos", {
      create: true,
    });

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
      } catch (err) {
        console.warn(`Aviso ao gravar foto local ${photo.name}:`, err);
      }
    }
  }

  // Atualiza memorização do handle no IndexedDB
  await salvarHandleIndexedDB(dirHandle);

  return {
    totalFotos: workspace.photos.length,
    totalNcs: workspace.registrosNc.length,
  };
}

/**
 * Carrega o estado e restaura as fotos da pasta geradorBD para a modalidade ativa.
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
}> {
  const nomeJson = obterNomeArquivoJson(tipo, categoria);
  const pastaModalidade = obterPastaModalidade(tipo, categoria);

  let fileHandle: FileSystemFileHandle;
  try {
    fileHandle = await dirHandle.getFileHandle(nomeJson, { create: false });
  } catch {
    throw new Error(
      `Nenhum registro encontrado para "${tipo} - ${categoria}". O arquivo "${nomeJson}" não existe na pasta geradorBD.`
    );
  }

  const file = await fileHandle.getFile();
  const text = await file.text();
  const payload = JSON.parse(text);

  const fiscalizacoes: FiscalizacaoItem[] =
    payload.temp_fiscalizacoes || payload.fiscalizacoes || [];
  const registrosNc: RegistroNcItem[] =
    payload.temp_nc || payload.registrosNc || [];
  const pistaPersistida: string = payload.pista_persistida || "";
  const trechoPersistido: string = payload.trecho_persistido || "";

  const fotosRestauradas: UploadedPhotoItem[] = [];
  try {
    const modHandle = await dirHandle.getDirectoryHandle(pastaModalidade, {
      create: false,
    });
    const midiaHandle = await modHandle.getDirectoryHandle("midia", {
      create: false,
    });
    const fotosHandle = await midiaHandle.getDirectoryHandle("fotos", {
      create: false,
    });

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
    // Pasta de fotos ainda não existia ou vazia
  }

  await salvarHandleIndexedDB(dirHandle);

  return {
    fiscalizacoes,
    registrosNc,
    photos: fotosRestauradas,
    pistaPersistida,
    trechoPersistido,
  };
}
