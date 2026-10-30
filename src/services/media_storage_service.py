# -*- coding: utf-8 -*-
"""Serviço de Armazenamento Local de Mídia e Documentos Auxiliares.

Gerencia o salvamento físico, carregamento e exclusão de fotos e documentos
(planilhas de elegibilidade e relatórios anteriores) na estrutura padronizada
de diretórios do projeto:
    geradorRelatorios/{subpasta_relatorio}/midia/fotos/
    geradorRelatorios/{subpasta_relatorio}/midia/arquivos/
"""

import os
import io
import mimetypes
import logging
from typing import List, Optional, Tuple, Any

logger = logging.getLogger(__name__)

# Pasta local de cache e mídias na máquina do usuário (fora do código do projeto)
USER_HOME = os.path.expanduser("~")
CACHE_DIR = os.path.join(USER_HOME, "geradorRelatorios")

# Extensões válidas de imagem
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}

# Mapeamento padronizado de subpastas para as 6 modalidades
MAPA_SUBPASTAS = {
    ("CRA", "Fiscalização"): "cra_fiscalizacao",
    ("CRA", "Monitoramento"): "cra_monitoramento",
    ("CRC", "Fiscalização"): "crc_fiscalizacao",
    ("CRC", "Monitoramento"): "crc_monitoramento",
    ("SOCICAM", "Fiscalização"): "socicam_fiscalizacao",
    ("SOCICAM", "Monitoramento"): "socicam_monitoramento",
}


def normalizar_termo(texto: str) -> str:
    """Remove acentos e caracteres especiais para nomes de pastas seguros."""
    substituicoes = {
        "ã": "a", "á": "a", "à": "a", "â": "a",
        "é": "e", "ê": "e",
        "í": "i",
        "ó": "o", "ô": "o", "õ": "o",
        "ú": "u",
        "ç": "c",
    }
    limpo = str(texto).strip().lower()
    for k, v in substituicoes.items():
        limpo = limpo.replace(k, v)
    return limpo


def obter_subpasta_relatorio(tipo_relatorio: str, categoria_relatorio: str) -> str:
    """Retorna o nome da subpasta padronizada para o tipo e categoria de relatório."""
    tipo_key = str(tipo_relatorio).strip().upper()
    cat_key = "Monitoramento" if "mon" in str(categoria_relatorio).lower() else "Fiscalização"

    if (tipo_key, cat_key) in MAPA_SUBPASTAS:
        return MAPA_SUBPASTAS[(tipo_key, cat_key)]

    return f"{normalizar_termo(tipo_relatorio)}_{normalizar_termo(categoria_relatorio)}"


def obter_diretorios_midia(tipo_relatorio: str, categoria_relatorio: str) -> Tuple[str, str]:
    """Retorna os caminhos absolutos das pastas (fotos_dir, arquivos_dir)."""
    subpasta = obter_subpasta_relatorio(tipo_relatorio, categoria_relatorio)
    base_relatorio = os.path.join(CACHE_DIR, subpasta, "midia")
    fotos_dir = os.path.join(base_relatorio, "fotos")
    arquivos_dir = os.path.join(base_relatorio, "arquivos")
    return fotos_dir, arquivos_dir


class LocalMediaFile:
    """Objeto que emula a interface de um UploadedFile do Streamlit para arquivos em disco.

    Permite interoperabilidade total com widgets, bibliotecas de imagens (PIL, docx)
    e rotinas de leitura de bytes sem manter todos os arquivos permanentemente em memória.
    """

    def __init__(self, filepath: str, name: Optional[str] = None):
        self.filepath = os.path.abspath(filepath)
        self.name = name or os.path.basename(filepath)
        self._size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
        mime, _ = mimetypes.guess_type(self.name)
        self.type = mime or "application/octet-stream"
        self._buffer: Optional[io.BytesIO] = None

    @property
    def size(self) -> int:
        if self._size == 0 and os.path.exists(self.filepath):
            self._size = os.path.getsize(self.filepath)
        return self._size

    def _ensure_buffer(self) -> io.BytesIO:
        if self._buffer is None:
            if os.path.exists(self.filepath):
                with open(self.filepath, "rb") as f:
                    self._buffer = io.BytesIO(f.read())
            else:
                self._buffer = io.BytesIO()
        return self._buffer

    def read(self, *args, **kwargs) -> bytes:
        return self._ensure_buffer().read(*args, **kwargs)

    def seek(self, *args, **kwargs):
        return self._ensure_buffer().seek(*args, **kwargs)

    def tell(self) -> int:
        return self._ensure_buffer().tell()

    def getvalue(self) -> bytes:
        return self._ensure_buffer().getvalue()

    def getbuffer(self):
        return self._ensure_buffer().getbuffer()

    def __len__(self) -> int:
        return self.size or len(self.getvalue())

    def __repr__(self) -> str:
        return f"<LocalMediaFile name='{self.name}' size={self.size}>"


def _extrair_bytes_arquivo(arquivo: Any) -> bytes:
    """Extrai os bytes brutos de um objeto Streamlit UploadedFile ou similar."""
    if hasattr(arquivo, "seek"):
        try:
            arquivo.seek(0)
        except Exception:
            pass

    if hasattr(arquivo, "getvalue"):
        return arquivo.getvalue()
    if hasattr(arquivo, "read"):
        conteudo = arquivo.read()
        if hasattr(arquivo, "seek"):
            try:
                arquivo.seek(0)
            except Exception:
                pass
        return conteudo
    if isinstance(arquivo, (bytes, bytearray)):
        return bytes(arquivo)
    if isinstance(arquivo, str) and os.path.exists(arquivo):
        with open(arquivo, "rb") as f:
            return f.read()
    return b""


def salvar_fotos_disco(
    tipo_relatorio: str,
    categoria_relatorio: str,
    fotos_uploader: List[Any],
    nomes_atuais_uploader: Optional[List[str]] = None,
) -> List[LocalMediaFile]:
    """Copia e cola fisicamente as fotos enviadas pelo uploader no diretório local.

    Args:
        tipo_relatorio: Ex: 'CRA', 'CRC', 'SOCICAM'
        categoria_relatorio: Ex: 'Fiscalização', 'Monitoramento'
        fotos_uploader: Lista de fotos novas a serem gravadas no disco.
        nomes_atuais_uploader: Se fornecido (em caso de remoção), apaga do disco
                               os arquivos que não constem nesta lista.

    Returns:
        Lista com todos os objetos LocalMediaFile ativos no diretório.
    """
    fotos_dir, _ = obter_diretorios_midia(tipo_relatorio, categoria_relatorio)
    os.makedirs(fotos_dir, exist_ok=True)

    # 1. Se houve remoção, sincroniza o disco eliminando órfãos
    if nomes_atuais_uploader is not None:
        nomes_permitidos = set(nomes_atuais_uploader)
        for arquivo_existente in os.listdir(fotos_dir):
            if arquivo_existente not in nomes_permitidos:
                caminho_remover = os.path.join(fotos_dir, arquivo_existente)
                try:
                    if os.path.isfile(caminho_remover):
                        os.remove(caminho_remover)
                except Exception as e:
                    logger.warning(f"Não foi possível remover foto órfã {caminho_remover}: {e}")

    # 2. Salva as novas fotos fisicamente
    for foto in fotos_uploader:
        nome_foto = getattr(foto, "name", None)
        if not nome_foto and isinstance(foto, str):
            nome_foto = os.path.basename(foto)
        if not nome_foto:
            continue

        dados_bytes = _extrair_bytes_arquivo(foto)
        if not dados_bytes:
            continue

        destino_path = os.path.join(fotos_dir, nome_foto)
        try:
            with open(destino_path, "wb") as f:
                f.write(dados_bytes)
        except Exception as e:
            logger.error(f"Erro ao salvar foto {nome_foto} em disco: {e}")

    # 3. Retorna a lista completa atualizada em disco
    return carregar_fotos_disco(tipo_relatorio, categoria_relatorio)


def carregar_fotos_disco(tipo_relatorio: str, categoria_relatorio: str) -> List[LocalMediaFile]:
    """Carrega todas as fotos ativas no diretório local como objetos LocalMediaFile."""
    fotos_dir, _ = obter_diretorios_midia(tipo_relatorio, categoria_relatorio)
    if not os.path.exists(fotos_dir):
        return []

    fotos: List[LocalMediaFile] = []
    try:
        arquivos = os.listdir(fotos_dir)
        for nome_arquivo in arquivos:
            ext = os.path.splitext(nome_arquivo)[1].lower()
            if ext in IMAGE_EXTENSIONS:
                caminho_completo = os.path.join(fotos_dir, nome_arquivo)
                if os.path.isfile(caminho_completo):
                    fotos.append(LocalMediaFile(filepath=caminho_completo, name=nome_arquivo))
    except Exception as e:
        logger.error(f"Erro ao carregar fotos em disco de {fotos_dir}: {e}")

    return fotos


def limpar_fotos_disco(tipo_relatorio: str, categoria_relatorio: str) -> None:
    """Remove fisicamente todas as fotos da pasta local do relatório ativo."""
    fotos_dir, _ = obter_diretorios_midia(tipo_relatorio, categoria_relatorio)
    if not os.path.exists(fotos_dir):
        return

    try:
        for f in os.listdir(fotos_dir):
            caminho = os.path.join(fotos_dir, f)
            if os.path.isfile(caminho):
                os.remove(caminho)
    except Exception as e:
        logger.error(f"Erro ao limpar fotos em disco de {fotos_dir}: {e}")


def remover_foto_disco(
    tipo_relatorio: str,
    categoria_relatorio: str,
    nome_foto: str,
) -> bool:
    """Remove pontualmente uma foto física da subpasta midia/fotos/ do relatório ativo.

    Args:
        tipo_relatorio: Ex: 'CRA', 'CRC', 'SOCICAM'
        categoria_relatorio: Ex: 'Fiscalização', 'Monitoramento'
        nome_foto: Nome do arquivo (ex: 'IMG_001.jpg')

    Returns:
        True se o arquivo existia e foi removido com sucesso, False caso contrário.
    """
    if not nome_foto:
        return False
    fotos_dir, _ = obter_diretorios_midia(tipo_relatorio, categoria_relatorio)
    caminho_foto = os.path.join(fotos_dir, nome_foto)
    try:
        if os.path.isfile(caminho_foto):
            os.remove(caminho_foto)
            logger.info(f"Foto {nome_foto} removida com sucesso de {fotos_dir}")
            return True
        return False
    except Exception as e:
        logger.error(f"Erro ao remover foto {caminho_foto} em disco: {e}")
        return False


def salvar_documento_auxiliar_disco(
    tipo_relatorio: str,
    categoria_relatorio: str,
    arquivo_uploader: Any,
) -> Optional[LocalMediaFile]:
    """Salva fisicamente um documento auxiliar (DOCX anterior, Planilha de Elegibilidade) em midia/arquivos/."""
    if not arquivo_uploader:
        return None

    _, arquivos_dir = obter_diretorios_midia(tipo_relatorio, categoria_relatorio)
    os.makedirs(arquivos_dir, exist_ok=True)

    nome_doc = getattr(arquivo_uploader, "name", None)
    if not nome_doc and isinstance(arquivo_uploader, str):
        nome_doc = os.path.basename(arquivo_uploader)
    if not nome_doc:
        return None

    dados_bytes = _extrair_bytes_arquivo(arquivo_uploader)
    if not dados_bytes:
        return None

    destino_path = os.path.join(arquivos_dir, nome_doc)
    try:
        with open(destino_path, "wb") as f:
            f.write(dados_bytes)
        return LocalMediaFile(filepath=destino_path, name=nome_doc)
    except Exception as e:
        logger.error(f"Erro ao salvar documento auxiliar {nome_doc} em disco: {e}")
        return None


def carregar_documento_auxiliar_disco(
    tipo_relatorio: str,
    categoria_relatorio: str,
    extensoes: Tuple[str, ...],
) -> Optional[LocalMediaFile]:
    """Carrega o documento auxiliar correspondente mais recente salvo em midia/arquivos/."""
    _, arquivos_dir = obter_diretorios_midia(tipo_relatorio, categoria_relatorio)
    if not os.path.exists(arquivos_dir):
        return None

    exts_norm = {e.lower() for e in extensoes}
    candidatos: List[Tuple[float, str]] = []

    try:
        for nome_arq in os.listdir(arquivos_dir):
            ext = os.path.splitext(nome_arq)[1].lower()
            if ext in exts_norm:
                caminho = os.path.join(arquivos_dir, nome_arq)
                if os.path.isfile(caminho):
                    candidatos.append((os.path.getmtime(caminho), caminho))

        if candidatos:
            # Retorna o arquivo modificado mais recentemente
            candidatos.sort(key=lambda x: x[0], reverse=True)
            mais_recente = candidatos[0][1]
            return LocalMediaFile(filepath=mais_recente)
    except Exception as e:
        logger.error(f"Erro ao carregar documento auxiliar de {arquivos_dir}: {e}")

    return None


def limpar_documentos_auxiliares_disco(
    tipo_relatorio: str,
    categoria_relatorio: str,
    extensoes: Optional[Tuple[str, ...]] = None
) -> None:
    """
    Remove documentos auxiliares salvos em midia/arquivos/ do relatório ativo.
    Se 'extensoes' for fornecido (ex: ('.xlsx', '.xls') ou ('.docx', '.doc')),
    apaga apenas os arquivos que terminem com essas extensões.
    """
    _, arquivos_dir = obter_diretorios_midia(tipo_relatorio, categoria_relatorio)
    if not os.path.exists(arquivos_dir):
        return

    try:
        for f in os.listdir(arquivos_dir):
            if extensoes and not f.lower().endswith(tuple(ext.lower() for ext in extensoes)):
                continue
            caminho = os.path.join(arquivos_dir, f)
            if os.path.isfile(caminho):
                os.remove(caminho)
    except Exception as e:
        logger.error(f"Erro ao limpar documentos auxiliares de {arquivos_dir}: {e}")


def limpar_estado_completo_relatorio_disco(tipo_relatorio: str, categoria_relatorio: str) -> bool:
    """
    Remove todos os arquivos físicos do relatório ativo (CRA, CRC ou SOCICAM):
    1. Arquivo de estado JSON (geradorRelatorios/{subpasta}.json)
    2. Arquivos de mídia (geradorRelatorios/{subpasta}/midia/arquivos/*)
    3. Fotos de mídia (geradorRelatorios/{subpasta}/midia/fotos/*)
    4. Subpasta de estado se existir (geradorRelatorios/{subpasta}/estado/*)
    """
    try:
        # 1. Apaga o JSON de estado da sessão
        from services.session_cache_service import limpar_sessao_local
        limpar_sessao_local(tipo_relatorio, categoria_relatorio)

        # 2. Apaga fotos da pasta midia/fotos/
        limpar_fotos_disco(tipo_relatorio, categoria_relatorio)

        # 3. Apaga arquivos da pasta midia/arquivos/
        limpar_documentos_auxiliares_disco(tipo_relatorio, categoria_relatorio)

        # 4. Apaga arquivos dentro de geradorRelatorios/{subpasta}/estado/ se existir
        subpasta = obter_subpasta_relatorio(tipo_relatorio, categoria_relatorio)
        estado_dir = os.path.join(CACHE_DIR, subpasta, "estado")
        if os.path.exists(estado_dir) and os.path.isdir(estado_dir):
            for f in os.listdir(estado_dir):
                caminho = os.path.join(estado_dir, f)
                if os.path.isfile(caminho):
                    os.remove(caminho)

        return True
    except Exception as e:
        logger.error(f"Erro ao limpar estado completo de {tipo_relatorio} {categoria_relatorio}: {e}")
        return False

