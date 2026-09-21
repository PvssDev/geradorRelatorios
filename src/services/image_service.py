# -*- coding: utf-8 -*-
import io
import os
import re
import unicodedata
import streamlit as st
from PIL import Image, ImageOps


def chave_ordenacao_natural(item):
    """
    Retorna uma chave para ordenação natural (humana) de arquivos/fotos.
    Garante que 'Foto 2' venha antes de 'Foto 10', tratando acentuação,
    maiúsculas/minúsculas e sequências numéricas de qualquer tamanho.
    Funciona tanto com objetos que possuem atributo 'name' (como UploadedFile)
    quanto com strings e caminhos de arquivo.
    """
    if item is None:
        return []
    name = getattr(item, "name", str(item))
    # Normaliza unicode para remover variações de acentuação na comparação
    normalized = unicodedata.normalize("NFKD", name)
    # Divide em blocos de dígitos e não-dígitos
    parts = re.split(r"(\d+)", normalized)
    key = []
    for part in parts:
        if part.isdigit():
            # Tupla: (0, int_value, length) para ordenação numérica prioritária
            key.append((0, int(part), len(part)))
        else:
            key.append((1, part.lower()))
    return key



@st.cache_data(show_spinner=False, max_entries=2000)
def obter_thumbnail_cached(file_key: str, _file_source, max_size=(400, 300)) -> bytes:
    """
    Gera e armazena em cache (Streamlit) uma miniatura em JPEG comprimida (~30-60 KB)
    a partir de um objeto de imagem (UploadedFile, BytesIO ou caminho no disco).

    O Streamlit calcula o hash apenas a partir de 'file_key' e 'max_size' (pois _file_source
    possui prefixo underline), garantindo acesso ultra rápido em O(1).
    """
    if not _file_source:
        return b""

    try:
        # Se for um stream com suporte a seek, reposiciona no início
        if hasattr(_file_source, "seek"):
            try:
                _file_source.seek(0)
            except Exception:
                pass

        # Abre a imagem
        img = Image.open(_file_source)

        # Converte para RGB para compatibilidade universal com JPEG
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        # Redimensiona mantendo proporção e preenchendo as dimensões indicadas
        thumb = ImageOps.fit(img, max_size, method=Image.Resampling.LANCZOS)

        # Salva em buffer JPEG comprimido leve
        buffer = io.BytesIO()
        thumb.save(buffer, format="JPEG", quality=80, optimize=True)
        thumb_bytes = buffer.getvalue()

        # Restaura o ponteiro do stream original para não afetar outras leituras ou downloads
        if hasattr(_file_source, "seek"):
            try:
                _file_source.seek(0)
            except Exception:
                pass

        return thumb_bytes
    except Exception:
        # Se falhar, garante o seek e retorna None
        if hasattr(_file_source, "seek"):
            try:
                _file_source.seek(0)
            except Exception:
                pass
        return None


def obter_foto_preview(photo_source, max_size=(400, 300)):
    """
    Função auxiliar que extrai uma chave única estável para a foto e recupera
    ou gera a miniatura em cache. Retorna os bytes leves da miniatura ou a
    fonte original com seek(0) em caso de falha.
    """
    if photo_source is None:
        return None

    # Extrai uma chave estável para indexação no cache
    if isinstance(photo_source, str):
        mtime = os.path.getmtime(photo_source) if os.path.exists(photo_source) else 0
        file_key = f"disk_{photo_source}_{mtime}_{max_size}"
    else:
        name = getattr(photo_source, "name", "unknown")
        size = getattr(photo_source, "size", 0)
        file_key = f"up_{name}_{size}_{max_size}"

    thumb = obter_thumbnail_cached(file_key, photo_source, max_size=max_size)
    if thumb:
        return thumb

    # Fallback seguro: garante cursor no início do stream original
    if hasattr(photo_source, "seek"):
        try:
            photo_source.seek(0)
        except Exception:
            pass
    return photo_source


def obter_nomes_fotos_em_nc(temp_nc: list) -> set:
    """
    Retorna o conjunto de nomes/identificadores normalizados (minúsculos)
    de todas as fotos que foram adicionadas aos registros de Não Conformidade.
    """
    if not temp_nc:
        return set()
    nomes = set()
    for nc in temp_nc:
        f = nc.get("Foto")
        if f:
            base = os.path.basename(str(f)).strip().lower()
            if base:
                nomes.add(base)
                root, _ = os.path.splitext(base)
                if root:
                    nomes.add(root)
    return nomes


def foto_esta_em_nc(photo, nomes_em_nc: set) -> bool:
    """
    Verifica se um objeto de foto (UploadedFile, caminho ou string)
    corresponde a alguma foto presente no conjunto de fotos em NC.
    """
    if not photo or not nomes_em_nc:
        return False
    name = getattr(photo, "name", str(photo))
    base = os.path.basename(name).strip().lower()
    root, _ = os.path.splitext(base)
    return base in nomes_em_nc or root in nomes_em_nc

