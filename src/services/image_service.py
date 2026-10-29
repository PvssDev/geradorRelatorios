# -*- coding: utf-8 -*-
import io
import os
import re
import unicodedata
from PIL import Image, ImageOps


_THUMBNAIL_CACHE: dict[str, bytes] = {}
_MAX_CACHE_ENTRIES = 2000


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


def obter_thumbnail_cached(file_key: str, _file_source, max_size=(400, 300)) -> bytes:
    """
    Gera e armazena em cache em memória uma miniatura em JPEG comprimida (~30-60 KB)
    a partir de um objeto de imagem (UploadedFile, BytesIO ou caminho no disco).
    Agnóstico de framework web (sem dependência de Streamlit).
    """
    if not _file_source:
        return b""

    cache_key = f"{file_key}_{max_size}"
    if cache_key in _THUMBNAIL_CACHE:
        return _THUMBNAIL_CACHE[cache_key]

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

        if len(_THUMBNAIL_CACHE) >= _MAX_CACHE_ENTRIES:
            _THUMBNAIL_CACHE.pop(next(iter(_THUMBNAIL_CACHE)), None)
        _THUMBNAIL_CACHE[cache_key] = thumb_bytes
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


def comprimir_imagem_para_word(image_bytes: bytes, max_kb: int = 500) -> bytes:
    """
    Otimiza e comprime imagens acima de `max_kb` KB para inserção leve no Word (.docx),
    respeitando orientação EXIF de celulares e mantendo nitidez regulatória.
    """
    if not image_bytes or len(image_bytes) <= max_kb * 1024:
        return image_bytes

    try:
        img = Image.open(io.BytesIO(image_bytes))
        img = ImageOps.exif_transpose(img)
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        max_dim = 1600
        if max(img.size) > max_dim:
            img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

        for quality in (82, 72, 62, 50):
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=quality, optimize=True)
            data = buf.getvalue()
            if len(data) <= max_kb * 1024 or quality == 50:
                return data
    except Exception:
        return image_bytes

    return image_bytes

