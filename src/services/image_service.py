# -*- coding: utf-8 -*-
import base64
import io
import os
import re
import unicodedata
import streamlit as st
from PIL import Image, ImageOps, ExifTags


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

    # Procura em old_photos_to_match (fotos do monitoramento anterior)
    old_match = st.session_state.get("old_photos_to_match", [])
    for item in old_match:
        p_path = item.get("old_photo_path")
        if p_path:
            p_base = os.path.basename(p_path).strip().lower()
            id_nc = str(item.get("id_nc", "")).strip().lower()
            if p_base == nome_alvo or id_nc == nome_alvo:
                if os.path.exists(p_path):
                    return p_path

    # Normalização de caminhos Windows / Linux
    clean_path = photo_source.replace("\\", os.sep).replace("/", os.sep)
    if os.path.exists(clean_path):
        return clean_path

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


def obter_foto_base64(photo_source, max_size=(400, 300)) -> str:
    """
    Retorna uma Data URL Base64 pronta ('data:image/jpeg;base64,...') para exibição direta
    em tags HTML (<img src="...">) ou componentes web.
    Elimina 100% das requisições HTTP ao endpoint virtual de mídia do Streamlit (/_stcore/media/),
    prevenindo erros de 'Client Error: Image source error' (404) no Streamlit Cloud.
    """
    if photo_source is None:
        return ""

    if hasattr(photo_source, "b64_data") and photo_source.b64_data:
        return photo_source.b64_data

    thumb = obter_foto_preview(photo_source, max_size=max_size)
    if isinstance(thumb, bytes) and len(thumb) > 0:
        b64 = base64.b64encode(thumb).decode("ascii")
        return f"data:image/jpeg;base64,{b64}"
    elif isinstance(thumb, str) and os.path.exists(thumb):
        try:
            with open(thumb, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("ascii")
                return f"data:image/jpeg;base64,{b64}"
        except Exception:
            return ""
    elif hasattr(thumb, "read"):
        try:
            if hasattr(thumb, "seek"):
                thumb.seek(0)
            raw = thumb.read()
            if hasattr(thumb, "seek"):
                thumb.seek(0)
            if raw:
                b64 = base64.b64encode(raw).decode("ascii")
                return f"data:image/jpeg;base64,{b64}"
        except Exception:
            return ""
    return ""


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


def extrair_data_original_foto(photo_source) -> str:
    """
    Extrai a data original (DateTimeOriginal) dos metadados EXIF da foto enviada.
    - Retorna a data formatada em 'DD/MM/YYYY'.
    - Busca estritamente a data original de criação/captura (tag 36867 / 0x9003)
      e NÃO utiliza a data de modificação da imagem (tag 306).
    - Em caso de ausência de metadados, erro de leitura, foto corrompida ou inexistente,
      retorna 'xx/xx/xxxx'.
    """
    if not photo_source:
        return "xx/xx/xxxx"

    source_resolved = resolver_objeto_foto(photo_source)
    if not source_resolved:
        source_resolved = photo_source

    raw_date = None
    try:
        if isinstance(source_resolved, str):
            if not os.path.exists(source_resolved):
                return "xx/xx/xxxx"
            img = Image.open(source_resolved)
        elif hasattr(source_resolved, "seek"):
            try:
                source_resolved.seek(0)
            except Exception:
                pass
            img = Image.open(source_resolved)
        else:
            return "xx/xx/xxxx"

        try:
            exif = img.getexif()
            if exif:
                try:
                    if hasattr(ExifTags, "IFD") and hasattr(ExifTags.IFD, "Exif"):
                        exif_ifd = exif.get_ifd(ExifTags.IFD.Exif)
                    else:
                        exif_ifd = exif.get_ifd(0x8769)
                    if exif_ifd:
                        raw_date = exif_ifd.get(36867) or exif_ifd.get(0x9003)
                except Exception:
                    pass

            if not raw_date and hasattr(img, "_getexif"):
                legacy_exif = img._getexif()
                if isinstance(legacy_exif, dict):
                    raw_date = legacy_exif.get(36867) or legacy_exif.get(0x9003)
        finally:
            try:
                img.close()
            except Exception:
                pass
            if hasattr(source_resolved, "seek"):
                try:
                    source_resolved.seek(0)
                except Exception:
                    pass

        if raw_date:
            match = re.search(r"(\d{4})[:/-](\d{2})[:/-](\d{2})", str(raw_date))
            if match:
                ano, mes, dia = match.groups()
                return f"{dia}/{mes}/{ano}"

    except Exception:
        pass

    return "xx/xx/xxxx"


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


def comprimir_imagem(
    photo_source,
    target_size_kb: int = 500,
    max_dimension: int = 1920,
    qualidade_inicial: int = 82
) -> bytes:
    """
    Comprime e redimensiona uma imagem para aproximadamente target_size_kb (padrão 500 KB)
    mantendo alta resolução e qualidade visual nítida para documentos e impressão.

    Garante:
    - Correção da orientação do sensor via ImageOps.exif_transpose (evita fotos viradas).
    - Preservação estrita dos metadados EXIF (incluindo DateTimeOriginal para extrair_data_original_foto).
    - Conversão segura para RGB com fundo branco caso possua transparência (PNG/RGBA).
    - Redimensionamento proporcional se max(largura, altura) > max_dimension usando Lanczos.
    - Loop adaptativo de qualidade JPEG para convergir próximo a ~500 KB.
    - Retorno estritamente em memória (bytes), sem arquivos temporários no disco (LGPD).
    - Fallback resiliente: em caso de erro, retorna os bytes originais com seek(0) preservado.
    """
    if not photo_source:
        return b""

    source_resolved = resolver_objeto_foto(photo_source)
    if source_resolved is None:
        source_resolved = photo_source

    def _obter_bytes_originais(fonte) -> bytes:
        try:
            if hasattr(fonte, "seek"):
                try:
                    fonte.seek(0)
                except Exception:
                    pass
            if hasattr(fonte, "getbuffer"):
                return bytes(fonte.getbuffer())
            elif hasattr(fonte, "read"):
                return fonte.read()
            elif isinstance(fonte, (bytes, bytearray)):
                return bytes(fonte)
            elif isinstance(fonte, str) and os.path.exists(fonte):
                with open(fonte, "rb") as f:
                    return f.read()
        except Exception:
            pass
        return b""

    try:
        if hasattr(source_resolved, "seek"):
            try:
                source_resolved.seek(0)
            except Exception:
                pass

        if isinstance(source_resolved, str):
            if not os.path.exists(source_resolved):
                return b""
            img = Image.open(source_resolved)
        elif hasattr(source_resolved, "read"):
            img = Image.open(source_resolved)
        elif isinstance(source_resolved, (bytes, bytearray)):
            img = Image.open(io.BytesIO(source_resolved))
        else:
            return _obter_bytes_originais(source_resolved)

        try:
            # 1. Correção de orientação EXIF (modo retrato de smartphone)
            img = ImageOps.exif_transpose(img)

            # 2. Preservação dos metadados EXIF
            raw_exif = img.info.get("exif")
            if not raw_exif:
                try:
                    exif_obj = img.getexif()
                    if exif_obj:
                        raw_exif = exif_obj.tobytes()
                except Exception:
                    raw_exif = None

            # 3. Tratamento de modo e transparência
            if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                bg = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode != "RGBA":
                    img = img.convert("RGBA")
                bg.paste(img, mask=img.split()[-1])
                img = bg
            elif img.mode != "RGB":
                img = img.convert("RGB")

            # 4. Redimensionamento proporcional se maior que max_dimension
            w, h = img.size
            max_side = max(w, h)
            if max_side > max_dimension:
                scale = max_dimension / float(max_side)
                new_w = max(1, int(w * scale))
                new_h = max(1, int(h * scale))
                img = img.resize((new_w, new_h), resample=Image.Resampling.LANCZOS)

            # 5. Compressão adaptativa em JPEG visando ~target_size_kb
            target_bytes = target_size_kb * 1024
            qualities = [qualidade_inicial, 78, 72, 65]
            best_bytes = None

            for q in qualities:
                buf = io.BytesIO()
                save_kwargs = {"format": "JPEG", "quality": q, "optimize": True}
                if raw_exif:
                    save_kwargs["exif"] = raw_exif
                img.save(buf, **save_kwargs)
                data = buf.getvalue()

                if best_bytes is None or len(data) < len(best_bytes):
                    best_bytes = data

                if len(data) <= target_bytes:
                    best_bytes = data
                    break

            # Se ainda estiver acima de target_bytes no piso 65 (fotos com textura/ruído extremo)
            if best_bytes and len(best_bytes) > target_bytes:
                scale_sec = 1440 / float(max(img.size))
                if scale_sec < 1.0:
                    w2 = max(1, int(img.width * scale_sec))
                    h2 = max(1, int(img.height * scale_sec))
                    img_sec = img.resize((w2, h2), resample=Image.Resampling.LANCZOS)
                    buf_sec = io.BytesIO()
                    save_kwargs = {"format": "JPEG", "quality": 75, "optimize": True}
                    if raw_exif:
                        save_kwargs["exif"] = raw_exif
                    img_sec.save(buf_sec, **save_kwargs)
                    data_sec = buf_sec.getvalue()
                    if len(data_sec) < len(best_bytes):
                        best_bytes = data_sec

            return best_bytes or _obter_bytes_originais(source_resolved)

        finally:
            try:
                img.close()
            except Exception:
                pass
            if hasattr(source_resolved, "seek"):
                try:
                    source_resolved.seek(0)
                except Exception:
                    pass

    except Exception:
        return _obter_bytes_originais(source_resolved)


