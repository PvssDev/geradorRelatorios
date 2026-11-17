// -*- coding: utf-8 -*-
/**
 * Serviço de Persistência Local por Pasta (geradorBD).
 * 
 * Organiza a persistência das 6 modalidades na pasta local "geradorBD"
 * com reconciliação bidirecional (pruning):
 * - Ao salvar, arquivos e fotos excluídos na UI são apagados fisicamente do disco.
 * - Ao carregar, apenas as mídias salvas ativas são restauradas.
 * 
 * Estrutura:
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
  MonitoramentoAnteriorItem,
  MonitoramentoAnteriorMeta,
  RegistroNcItem,
  TipoRelatorio,
  UploadedPhotoItem,
} from "../types/report.types";
import {
  extractActiveSessionSnapshot,
  InspectionSessionSnapshot,
  ModalityWorkspaceState,
} from "../store/useReportStore";

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

function sanitizarNomePastaId(id: string): string {
  const clean = (id || "").trim().replace(/[/\\:*?"<>|]/g, "_");
  return clean || "SEM_ID";
}

interface SessionSaveEntry {
  id: string;
  pasta: string;
  header: FiscalizacaoItem | null;
  snapshot: InspectionSessionSnapshot;
}

async function salvarSessaoEmPasta(
  sessionDirHandle: FileSystemDirectoryHandle,
  tipo: TipoRelatorio,
  categoria: CategoriaRelatorio,
  pastaModalidadeNome: string,
  entry: SessionSaveEntry
): Promise<{ fotos: number; ncs: number; arquivos: number }> {
  const estadoHandle = await sessionDirHandle.getDirectoryHandle("estado", { create: true });
  const midiaHandle = await sessionDirHandle.getDirectoryHandle("midia", { create: true });
  const fotosHandle = await midiaHandle.getDirectoryHandle("fotos", { create: true });
  const arquivosHandle = await midiaHandle.getDirectoryHandle("arquivos", { create: true });

  const { snapshot } = entry;

  // Pruning de anexos órfãos
  const nomesArquivosAtivos = new Set<string>();
  if (snapshot.documentoAnteriorFile) nomesArquivosAtivos.add(snapshot.documentoAnteriorFile.name);
  if (snapshot.planilhaElegibilidadeFile) {
    nomesArquivosAtivos.add(snapshot.planilhaElegibilidadeFile.name);
  }
  try {
    for await (const [nome, item] of (arquivosHandle as any).entries()) {
      if (item.kind === "file" && !nomesArquivosAtivos.has(nome)) {
        try {
          await (arquivosHandle as any).removeEntry(nome);
        } catch {
          // ignora erro pontual de remoção
        }
      }
    }
  } catch {
    // ignora erro de varredura
  }

  // Pruning de fotos órfãs
  const nomesFotosAtivas = new Set(snapshot.photos.map((p) => p.name));
  try {
    for await (const [nome, item] of (fotosHandle as any).entries()) {
      if (item.kind === "file" && !nomesFotosAtivas.has(nome)) {
        try {
          await (fotosHandle as any).removeEntry(nome);
        } catch {
          // ignora erro pontual de remoção
        }
      }
    }
  } catch {
    // ignora erro de varredura
  }

  // Grava arquivos anexos ativos
  let totalArquivosSalvos = 0;
  const metaArquivos: Array<{ slot: string; nome: string; size: number; type: string }> = [];

  if (snapshot.documentoAnteriorFile) {
    try {
      const docFile = snapshot.documentoAnteriorFile;
      const fh = await arquivosHandle.getFileHandle(docFile.name, { create: true });
      const wr = await (fh as any).createWritable();
      await wr.write(docFile);
      await wr.close();
      totalArquivosSalvos++;
      metaArquivos.push({
        slot: "documentoAnterior",
        nome: docFile.name,
        size: docFile.size,
        type: docFile.type,
      });
    } catch (err) {
      console.warn("Erro ao salvar documento anterior:", err);
    }
  }

  if (snapshot.planilhaElegibilidadeFile) {
    try {
      const planFile = snapshot.planilhaElegibilidadeFile;
      const fh = await arquivosHandle.getFileHandle(planFile.name, { create: true });
      const wr = await (fh as any).createWritable();
      await wr.write(planFile);
      await wr.close();
      totalArquivosSalvos++;
      metaArquivos.push({
        slot: "planilhaElegibilidade",
        nome: planFile.name,
        size: planFile.size,
        type: planFile.type,
      });
    } catch (err) {
      console.warn("Erro ao salvar planilha de elegibilidade:", err);
    }
  }

  // Grava fotos ativas
  for (const photo of snapshot.photos) {
    try {
      let blob: Blob | null = null;
      if (photo.file) {
        blob = photo.file;
      } else if (photo.previewUrl && photo.previewUrl.startsWith("data:")) {
        const res = await fetch(photo.previewUrl);
        blob = await res.blob();
      }
      if (blob) {
        const fh = await fotosHandle.getFileHandle(photo.name, { create: true });
        const wr = await (fh as any).createWritable();
        await wr.write(blob);
        await wr.close();
      }
    } catch (err) {
      console.warn(`Aviso ao gravar foto local ${photo.name}:`, err);
    }
  }

  const payload = {
    versao: 2,
    tipo_relatorio: tipo,
    categoria_relatorio: categoria,
    modalidade: pastaModalidadeNome,
    id_sessao: entry.id,
    salvo_em: new Date().toISOString(),
    cabecalho: entry.header,
    temp_nc: snapshot.registrosNc,
    pista_persistida: snapshot.pistaPersistida,
    trecho_persistido: snapshot.trechoPersistido,
    sort_option: snapshot.sortOption,
    carousel_index: snapshot.carouselIndex,
    monitoring_new_photo_name: snapshot.monitoringNewPhotoName,
    documento_anterior_meta: snapshot.documentoAnteriorMeta,
    old_photos_to_match: snapshot.oldPhotosToMatch,
    meta_arquivos: metaArquivos,
    meta_fotos: snapshot.photos.map((p) => ({
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

  return {
    fotos: snapshot.photos.length,
    ncs: snapshot.registrosNc.length,
    arquivos: totalArquivosSalvos,
  };
}

/**
 * Salva todos os IDs (Fiscalizações ou Monitoramentos) na nova estrutura hierárquica:
 * geradorBD/<modalidade>/index.json
 * geradorBD/<modalidade>/<id_sanitizado>/estado/estado.json
 * geradorBD/<modalidade>/<id_sanitizado>/midia/{fotos,arquivos}
 */
export async function salvarEstadoEmGeradorBD(
  dirHandle: FileSystemDirectoryHandle,
  tipo: TipoRelatorio,
  categoria: CategoriaRelatorio,
  workspace: ModalityWorkspaceState,
  monitoringNewPhotoName = ""
): Promise<{ totalSessoes: number; totalFotos: number; totalNcs: number; totalArquivos: number }> {
  const pastaModalidadeNome = obterPastaModalidade(tipo, categoria);
  const modHandle = await dirHandle.getDirectoryHandle(pastaModalidadeNome, {
    create: true,
  });

  // Monta mapa completo de sessões (sincronizando a sessão ativa atual)
  const activeFisc = workspace.fiscalizacoes[workspace.activeFiscalizacaoIndex];
  const activeId = activeFisc?.["ID da Fiscalização"]?.trim() || "";
  const activeSnapshot = extractActiveSessionSnapshot(workspace, monitoringNewPhotoName);

  const sessionsMap: Record<string, InspectionSessionSnapshot> = {
    ...(workspace.sessionsById || {}),
  };
  if (activeId) {
    sessionsMap[activeId] = activeSnapshot;
  }

  const entries: SessionSaveEntry[] = [];
  const usedFolders = new Set<string>();

  const buildUniqueFolder = (id: string) => {
    const base = sanitizarNomePastaId(id);
    let folder = base;
    let n = 1;
    while (usedFolders.has(folder.toLowerCase())) {
      folder = `${base}(${n++})`;
    }
    usedFolders.add(folder.toLowerCase());
    return folder;
  };

  if (workspace.fiscalizacoes.length > 0) {
    for (let i = 0; i < workspace.fiscalizacoes.length; i++) {
      const f = workspace.fiscalizacoes[i];
      const fid = f["ID da Fiscalização"]?.trim() || `SEM_ID_${i + 1}`;
      const snap =
        (i === workspace.activeFiscalizacaoIndex ? activeSnapshot : sessionsMap[fid]) || {
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
      entries.push({
        id: fid,
        pasta: buildUniqueFolder(fid),
        header: f,
        snapshot: snap,
      });
    }
  } else if (
    activeSnapshot.photos.length > 0 ||
    activeSnapshot.registrosNc.length > 0 ||
    activeSnapshot.documentoAnteriorFile ||
    activeSnapshot.planilhaElegibilidadeFile
  ) {
    entries.push({
      id: "RASCUNHO",
      pasta: buildUniqueFolder("RASCUNHO"),
      header: null,
      snapshot: activeSnapshot,
    });
  }

  // Pruning de pastas antigas / excluídas e pastas legadas raiz (estado/ e midia/)
  const activeFolderNames = new Set(entries.map((e) => e.pasta));
  try {
    for await (const [nome, item] of (modHandle as any).entries()) {
      if (item.kind === "directory" && !activeFolderNames.has(nome)) {
        try {
          await (modHandle as any).removeEntry(nome, { recursive: true });
        } catch (errRem) {
          console.warn(`Aviso ao remover pasta antiga ${nome}:`, errRem);
        }
      }
    }
  } catch (errScan) {
    console.warn("Aviso ao limpar subpastas da modalidade:", errScan);
  }

  let totalFotos = 0;
  let totalNcs = 0;
  let totalArquivos = 0;

  for (const entry of entries) {
    const sessDirHandle = await modHandle.getDirectoryHandle(entry.pasta, { create: true });
    const res = await salvarSessaoEmPasta(
      sessDirHandle,
      tipo,
      categoria,
      pastaModalidadeNome,
      entry
    );
    totalFotos += res.fotos;
    totalNcs += res.ncs;
    totalArquivos += res.arquivos;
  }

  // Grava index.json na raiz da modalidade
  const indexPayload = {
    versao: 2,
    tipo_relatorio: tipo,
    categoria_relatorio: categoria,
    modalidade: pastaModalidadeNome,
    salvo_em: new Date().toISOString(),
    active_fiscalizacao_index: workspace.activeFiscalizacaoIndex,
    sessoes: entries.map((e) => ({ id: e.id, pasta: e.pasta })),
  };
  const indexHandle = await modHandle.getFileHandle("index.json", { create: true });
  const indexStream = await (indexHandle as any).createWritable();
  await indexStream.write(JSON.stringify(indexPayload, null, 2));
  await indexStream.close();

  await salvarHandleIndexedDB(dirHandle);

  return {
    totalSessoes: entries.length,
    totalFotos,
    totalNcs,
    totalArquivos,
  };
}

async function lerMidiasDePasta(
  rootHandle: FileSystemDirectoryHandle,
  payload: any
): Promise<{
  photos: UploadedPhotoItem[];
  documentoAnteriorFile: File | null;
  planilhaElegibilidadeFile: File | null;
}> {
  const fotosRestauradas: UploadedPhotoItem[] = [];
  try {
    const midiaHandle = await rootHandle.getDirectoryHandle("midia", { create: false });
    const fotosHandle = await midiaHandle.getDirectoryHandle("fotos", { create: false });

    if (Array.isArray(payload.meta_fotos) && payload.meta_fotos.length > 0) {
      for (const meta of payload.meta_fotos) {
        if (!meta.name) continue;
        try {
          const entryFileHandle = await fotosHandle.getFileHandle(meta.name, { create: false });
          const entryFile = await entryFileHandle.getFile();
          fotosRestauradas.push({
            id: meta.id || `foto-${Date.now()}-${meta.uploadOrder || 0}`,
            name: entryFile.name,
            file: entryFile,
            previewUrl: URL.createObjectURL(entryFile),
            uploadOrder:
              typeof meta.uploadOrder === "number" ? meta.uploadOrder : fotosRestauradas.length,
          });
        } catch {
          console.warn(`Foto salva no metadado não encontrada fisicamente: ${meta.name}`);
        }
      }
    } else {
      let order = 0;
      for await (const [, entry] of (fotosHandle as any).entries()) {
        if (entry.kind === "file") {
          try {
            const entryFile = await (entry as FileSystemFileHandle).getFile();
            fotosRestauradas.push({
              id: `foto-${Date.now()}-${order}`,
              name: entryFile.name,
              file: entryFile,
              previewUrl: URL.createObjectURL(entryFile),
              uploadOrder: order++,
            });
          } catch {
            // ignora erro pontual
          }
        }
      }
    }
  } catch {
    // midia/fotos vazia
  }

  let documentoAnteriorFile: File | null = null;
  let planilhaElegibilidadeFile: File | null = null;
  try {
    const midiaHandle = await rootHandle.getDirectoryHandle("midia", { create: false });
    const arquivosHandle = await midiaHandle.getDirectoryHandle("arquivos", { create: false });
    const metaArquivos: Array<{ slot: string; nome: string }> = payload.meta_arquivos || [];

    if (metaArquivos.length > 0) {
      for (const meta of metaArquivos) {
        if (!meta.nome) continue;
        try {
          const arqFileHandle = await arquivosHandle.getFileHandle(meta.nome, { create: false });
          const arqFile = await arqFileHandle.getFile();
          if (meta.slot === "documentoAnterior") documentoAnteriorFile = arqFile;
          else if (meta.slot === "planilhaElegibilidade") planilhaElegibilidadeFile = arqFile;
        } catch {
          console.warn(`Anexo declarado não encontrado fisicamente: ${meta.nome}`);
        }
      }
    } else {
      for await (const [name, entry] of (arquivosHandle as any).entries()) {
        if (entry.kind === "file") {
          try {
            const arqFile = await (entry as FileSystemFileHandle).getFile();
            if (name.endsWith(".docx") || name.endsWith(".pdf")) {
              if (!documentoAnteriorFile) documentoAnteriorFile = arqFile;
            } else if (name.endsWith(".xlsx") || name.endsWith(".xls")) {
              if (!planilhaElegibilidadeFile) planilhaElegibilidadeFile = arqFile;
            }
          } catch {
            // ignora
          }
        }
      }
    }
  } catch {
    // midia/arquivos vazia
  }

  return {
    photos: fotosRestauradas,
    documentoAnteriorFile,
    planilhaElegibilidadeFile,
  };
}

/**
 * Carrega o estado da modalidade a partir da nova estrutura por ID
 * (geradorBD/<modalidade>/index.json + <id_sanitizado>/{estado,midia}),
 * com fallback automático para o formato legado (geradorBD/<modalidade>/estado/estado.json).
 */
export async function carregarEstadoDeGeradorBD(
  dirHandle: FileSystemDirectoryHandle,
  tipo: TipoRelatorio,
  categoria: CategoriaRelatorio
): Promise<{
  fiscalizacoes: FiscalizacaoItem[];
  activeFiscalizacaoIndex: number;
  sessionsById?: Record<string, InspectionSessionSnapshot>;
  registrosNc: RegistroNcItem[];
  photos: UploadedPhotoItem[];
  pistaPersistida: string;
  trechoPersistido: string;
  documentoAnteriorFile: File | null;
  documentoAnteriorMeta?: MonitoramentoAnteriorMeta | null;
  planilhaElegibilidadeFile: File | null;
  oldPhotosToMatch?: MonitoramentoAnteriorItem[];
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

  // 1. Tenta carregar formato v2 (index.json + subpastas por ID)
  try {
    const indexHandle = await modHandle.getFileHandle("index.json", { create: false });
    const indexFile = await indexHandle.getFile();
    const indexData = JSON.parse(await indexFile.text());
    const sessList: Array<{ id: string; pasta: string }> = Array.isArray(indexData.sessoes)
      ? indexData.sessoes
      : [];

    const fiscalizacoes: FiscalizacaoItem[] = [];
    const sessionsById: Record<string, InspectionSessionSnapshot> = {};

    for (const item of sessList) {
      if (!item.pasta) continue;
      try {
        const sessHandle = await modHandle.getDirectoryHandle(item.pasta, { create: false });
        const estadoHandle = await sessHandle.getDirectoryHandle("estado", { create: false });
        const estadoFile = await (
          await estadoHandle.getFileHandle("estado.json", { create: false })
        ).getFile();
        const payload = JSON.parse(await estadoFile.text());
        const midias = await lerMidiasDePasta(sessHandle, payload);

        if (payload.cabecalho) {
          fiscalizacoes.push(payload.cabecalho);
        }

        const sessId = (payload.id_sessao || item.id || "").trim();
        if (sessId) {
          sessionsById[sessId] = {
            registrosNc: payload.temp_nc || [],
            photos: midias.photos,
            sortOption: payload.sort_option || "Nome (A-Z / 0-9)",
            carouselIndex: typeof payload.carousel_index === "number" ? payload.carousel_index : 0,
            monitoringNewPhotoName: payload.monitoring_new_photo_name || "",
            pistaPersistida: payload.pista_persistida || "",
            trechoPersistido: payload.trecho_persistido || "",
            documentoAnteriorFile: midias.documentoAnteriorFile,
            documentoAnteriorMeta: payload.documento_anterior_meta || null,
            planilhaElegibilidadeFile: midias.planilhaElegibilidadeFile,
            oldPhotosToMatch: payload.old_photos_to_match || [],
            relatoriosGerados: [],
          };
        }
      } catch (errSess) {
        console.warn(`Aviso ao carregar sessão ${item.pasta}:`, errSess);
      }
    }

    const activeIdx = Math.max(
      0,
      Math.min(
        typeof indexData.active_fiscalizacao_index === "number"
          ? indexData.active_fiscalizacao_index
          : 0,
        Math.max(0, fiscalizacoes.length - 1)
      )
    );
    const activeId = fiscalizacoes[activeIdx]?.["ID da Fiscalização"]?.trim() || "RASCUNHO";
    const activeSnap = sessionsById[activeId];

    await salvarHandleIndexedDB(dirHandle);

    return {
      fiscalizacoes,
      activeFiscalizacaoIndex: activeIdx,
      sessionsById,
      registrosNc: activeSnap?.registrosNc || [],
      photos: activeSnap?.photos || [],
      pistaPersistida: activeSnap?.pistaPersistida || "",
      trechoPersistido: activeSnap?.trechoPersistido || "",
      documentoAnteriorFile: activeSnap?.documentoAnteriorFile || null,
      documentoAnteriorMeta: activeSnap?.documentoAnteriorMeta || null,
      planilhaElegibilidadeFile: activeSnap?.planilhaElegibilidadeFile || null,
      oldPhotosToMatch: activeSnap?.oldPhotosToMatch || [],
    };
  } catch {
    // Segue para fallback legado
  }

  // 2. Fallback legado: geradorBD/<modalidade>/estado/estado.json
  let payload: any = null;
  try {
    const estadoHandle = await modHandle.getDirectoryHandle("estado", { create: false });
    const fileHandle = await estadoHandle.getFileHandle("estado.json", { create: false });
    const file = await fileHandle.getFile();
    payload = JSON.parse(await file.text());
  } catch {
    try {
      const legacyJsonName = `${pastaModalidadeNome}.json`;
      const legacyHandle = await dirHandle.getFileHandle(legacyJsonName, { create: false });
      const legacyFile = await legacyHandle.getFile();
      payload = JSON.parse(await legacyFile.text());
    } catch {
      throw new Error(
        `O arquivo "index.json" ou "estado/estado.json" não foi localizado dentro de "${pastaModalidadeNome}".`
      );
    }
  }

  const fiscalizacoes: FiscalizacaoItem[] =
    payload.temp_fiscalizacoes || payload.fiscalizacoes || [];
  const registrosNc: RegistroNcItem[] = payload.temp_nc || payload.registrosNc || [];
  const pistaPersistida: string = payload.pista_persistida || "";
  const trechoPersistido: string = payload.trecho_persistido || "";
  const midiasLegado = await lerMidiasDePasta(modHandle, payload);

  await salvarHandleIndexedDB(dirHandle);

  return {
    fiscalizacoes,
    activeFiscalizacaoIndex: 0,
    registrosNc,
    photos: midiasLegado.photos,
    pistaPersistida,
    trechoPersistido,
    documentoAnteriorFile: midiasLegado.documentoAnteriorFile,
    planilhaElegibilidadeFile: midiasLegado.planilhaElegibilidadeFile,
  };
}
