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


def resolver_objeto_foto(photo_source):
    """
    Se photo_source for string (nome de arquivo), procura o UploadedFile correspondente
    em st.session_state.fill_photos ou st.session_state.monitoring_new_photos.
    Se já for um UploadedFile ou caminho existente no disco, retorna-o diretamente.
    """
    if photo_source is None:
        return None
    if not isinstance(photo_source, str):
        return photo_source

    # Se existe no disco diretamente
    if os.path.exists(photo_source):
        return photo_source

    # Tenta resolver pelo nome em st.session_state
    nome_alvo = os.path.basename(photo_source).strip().lower()

    fill_photos = st.session_state.get("fill_photos", [])
    for p in fill_photos:
        p_name = getattr(p, "name", str(p))
        if os.path.basename(p_name).strip().lower() == nome_alvo:
            return p

    mon_photos = st.session_state.get("monitoring_new_photos", [])
    for p in mon_photos:
        p_name = getattr(p, "name", str(p))
        if os.path.basename(p_name).strip().lower() == nome_alvo:
            return p

    return None


def obter_foto_preview(photo_source, max_size=(400, 300)):
    """
    Função auxiliar que extrai uma chave única estável para a foto e recupera
    ou gera a miniatura em cache. Retorna os bytes leves da miniatura ou a
    fonte original com seek(0) em caso de falha.
    """
    if photo_source is None:
        return None

    # Resolve nomes de arquivo (strings) para objetos UploadedFile reais quando em memória
    source_resolved = resolver_objeto_foto(photo_source)
    if source_resolved is None:
        return None

    # Extrai uma chave estável para indexação no cache
    if isinstance(source_resolved, str):
        if not os.path.exists(source_resolved):
            return None
        mtime = os.path.getmtime(source_resolved)
        file_key = f"disk_{source_resolved}_{mtime}_{max_size}"
    else:
        name = getattr(source_resolved, "name", "unknown")
        size = getattr(source_resolved, "size", 0)
        file_key = f"up_{name}_{size}_{max_size}"

    thumb = obter_thumbnail_cached(file_key, source_resolved, max_size=max_size)
    if thumb:
        return thumb

    # Fallback seguro: garante cursor no início do stream original
    if hasattr(source_resolved, "seek"):
        try:
            source_resolved.seek(0)
        except Exception:
            pass
        return source_resolved

    if isinstance(source_resolved, str) and os.path.exists(source_resolved):
        return source_resolved
    return None


def extrair_nome_foto(photo_source) -> str:
    """
    Retorna o nome base limpo do arquivo de uma foto, suportando tanto UploadedFile
    (acessando .name), Path, str (caminho ou nome simples) quanto objetos em memória.
    Evita retornar representações de objeto padrão como '<streamlit...>'.
    """
    if photo_source is None:
        return ""
    if hasattr(photo_source, "name") and photo_source.name:
        return os.path.basename(str(photo_source.name)).strip()
    s = str(photo_source).strip()
    if s.startswith("<streamlit") or s.startswith("<_io."):
        return ""
    return os.path.basename(s).strip()


def obter_nomes_fotos_em_nc(temp_nc: list) -> dict:
    """
    Retorna um dicionário mapeando os nomes/identificadores normalizados (minúsculos)
    de todas as fotos para o seu tipo (NC ou PA).
    """
    if not temp_nc:
        return {}
    nomes = {}
    for nc in temp_nc:
        # Determina o tipo (PA se tiver Ponto de Atenção preenchido e não NC, caso contrário NC)
        is_pa = bool(nc.get("Ponto de Atenção")) and not bool(nc.get("Não Conformidade"))
        tipo = "PA" if is_pa else "NC"

        def _add_foto(f_val):
            nome = extrair_nome_foto(f_val)
            if nome:
                base = nome.lower()
                nomes[base] = tipo
                root, _ = os.path.splitext(base)
                if root:
                    nomes[root] = tipo

        _add_foto(nc.get("Foto"))
        # No monitoramento, a foto anterior só é considerada "adicionada/concluída" se já tiver recebido uma foto nova
        if nc.get("Foto") or nc.get("is_relacionado"):
            _add_foto(nc.get("Foto Anterior"))
    return nomes


def foto_esta_em_nc(photo, nomes_em_nc: dict):
    """
    Verifica se um objeto de foto (UploadedFile, caminho ou string)
    corresponde a alguma foto presente no dicionário de fotos em NC/PA.
    Retorna a string 'NC', 'PA' se encontrado, caso contrário False.
    """
    if not photo or not nomes_em_nc:
        return False
    nome = extrair_nome_foto(photo)
    if not nome:
        return False
    base = nome.lower()
    root, _ = os.path.splitext(base)
    
    if base in nomes_em_nc:
        return nomes_em_nc[base]
    if root in nomes_em_nc:
        return nomes_em_nc[root]
    return False


def verificar_foto_elegivel_relacionar(current_photo, temp_nc: list) -> tuple[bool, str]:
    """
    Verifica se a foto atual selecionada no carrossel pode ter a opção de relacionar habilitada.
    Regras estritas de negócio:
    - Deve haver ao menos um registro anterior adicionado em temp_nc.
    - O registro base anterior (last_nc) NÃO pode já ter estado relacionado (is_relacionado).
    - A foto selecionada NÃO pode ser a mesma foto do registro anterior.
    - Apenas as fotos que NÃO foram adicionadas em nenhuma NC ou PT e que NÃO foram
      relacionadas podem ter a opção de relacionar.
    
    Retorna: (pode_relacionar: bool, help_text: str)
    """
    if not temp_nc:
        return False, "Adicione um registro primeiro para habilitar o relacionamento de fotos."

    last_nc = temp_nc[-1]
    if last_nc.get("is_relacionado", False):
        return False, "O registro anterior já faz parte de um relacionamento e não pode receber outro relacionamento."

    if not current_photo:
        return False, "Selecione uma foto no carrossel para relacionar."

    curr_nome = extrair_nome_foto(current_photo).lower()
    if not curr_nome:
        return False, "Foto selecionada inválida."

    curr_root, _ = os.path.splitext(curr_nome)

    ant_foto = last_nc.get("Foto")
    ant_nome = extrair_nome_foto(ant_foto).lower()
    ant_root, _ = os.path.splitext(ant_nome)

    if (curr_nome and curr_nome == ant_nome) or (curr_root and curr_root == ant_root):
        return False, "Esta foto já é a foto do registro anterior."

    for nc in temp_nc:
        for campo in ("Foto", "Foto Anterior"):
            f_val = nc.get(campo)
            if f_val:
                f_nome = extrair_nome_foto(f_val).lower()
                f_root, _ = os.path.splitext(f_nome)
                if (curr_nome and curr_nome == f_nome) or (curr_root and curr_root == f_root):
                    if nc.get("is_relacionado", False):
                        return False, "Esta foto já foi relacionada e não pode ser relacionada novamente."
                    return False, "Esta foto já foi adicionada a uma ocorrência e não pode ser relacionada."

    return True, "Relacionar a foto selecionada ao último registro cadastrado."


def foto_anterior_ja_adicionada(old_photo_ref, temp_nc: list) -> bool:
    """
    Verifica se uma foto anterior específica já foi adicionada/vinculada em temp_nc.
    Regra estrita de negócio: considera APENAS a foto anterior (não seletiva por NC, ID ou foto nova).
    Uma foto anterior é considerada adicionada/concluída se já existir um registro em temp_nc
    com essa mesma foto anterior e com uma foto nova associada.
    """
    if not old_photo_ref or not temp_nc:
        return False

    ref_str = extrair_nome_foto(old_photo_ref).lower()
    ref_root, _ = os.path.splitext(ref_str)

    for r in temp_nc:
        rec_old = r.get("Foto Anterior")
        # No monitoramento, só é adicionada se tiver recebido uma foto nova vinculada
        if rec_old and r.get("Foto"):
            old_str = extrair_nome_foto(rec_old).lower()
            old_root, _ = os.path.splitext(old_str)

            if ref_str == old_str or (ref_root and ref_root == old_root):
                return True
    return False


def obter_nomes_fotos_anteriores_concluidas(temp_nc: list) -> dict:
    """
    Retorna um dicionário mapeando os identificadores normalizados
    exclusivamente das fotos anteriores que já foram concluídas (vinculadas a uma foto nova) para 'NC'.
    Usado para exibir o check de conclusão verde no carrossel de fotos antigas sem interferência de novas fotos.
    """
    if not temp_nc:
        return {}
    nomes = {}
    for r in temp_nc:
        rec_old = r.get("Foto Anterior")
        if rec_old and r.get("Foto"):
            old_str = extrair_nome_foto(rec_old).lower()
            old_root, _ = os.path.splitext(old_str)
            if old_str:
                nomes[old_str] = "NC"
            if old_root:
                nomes[old_root] = "NC"
    return nomes

