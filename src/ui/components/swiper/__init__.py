import os
import base64
import streamlit as st
import streamlit.components.v1 as components
from services.image_service import obter_foto_preview

_COMPONENT_DIR = os.path.dirname(os.path.abspath(__file__))
_swiper_component = components.declare_component("swiper_carousel", path=_COMPONENT_DIR)


@st.cache_data(show_spinner=False, max_entries=500)
def _obter_foto_src_cached(f_key: str, _photo_source) -> str:
    """
    Gera e armazena em cache o Data URL Base64 da miniatura.
    Executa a compressão/redimensionamento apenas uma vez por foto.
    """
    thumb_bytes = obter_foto_preview(_photo_source, max_size=(420, 290))
    if isinstance(thumb_bytes, bytes) and len(thumb_bytes) > 0:
        b64 = base64.b64encode(thumb_bytes).decode("ascii")
        return f"data:image/jpeg;base64,{b64}"
    elif isinstance(thumb_bytes, str) and os.path.exists(thumb_bytes):
        try:
            with open(thumb_bytes, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("ascii")
                return f"data:image/jpeg;base64,{b64}"
        except Exception:
            return ""
    return ""


def _obter_payload_fotos(photos: list, nomes_em_nc_set: set) -> list:
    """
    Retorna a lista serializada de fotos para o Swiper com cache em memória
    instantâneo (sub-milissegundo). Se as fotos e os NCs não mudaram,
    reutiliza o mesmo objeto da sessão sem qualquer reprocessamento.
    """
    if not photos:
        return []

    # Cria uma assinatura de verificação ultra leve
    nc_sig = tuple(sorted(nomes_em_nc_set)) if nomes_em_nc_set else ()
    photo_sig = []
    for p in photos:
        if isinstance(p, str):
            photo_sig.append(p)
        else:
            photo_sig.append((getattr(p, "name", ""), getattr(p, "size", 0)))
    current_sig = (tuple(photo_sig), nc_sig)

    cached_sig = st.session_state.get("_swiper_cache_sig")
    if cached_sig == current_sig and "_swiper_cached_photos" in st.session_state:
        return st.session_state._swiper_cached_photos

    # Se a lista de fotos ou marcações de NC mudaram, gera o payload
    payload = []
    for p in photos:
        if isinstance(p, str):
            name = os.path.basename(p)
            mtime = os.path.getmtime(p) if os.path.exists(p) else 0
            f_key = f"disk_{p}_{mtime}"
        else:
            name = getattr(p, "name", "foto.jpg")
            size = getattr(p, "size", 0)
            f_key = f"up_{name}_{size}"

        src = _obter_foto_src_cached(f_key, p)
        is_nc = (name in nomes_em_nc_set) if nomes_em_nc_set else False
        payload.append({
            "name": name,
            "is_nc": is_nc,
            "src": src,
        })

    st.session_state._swiper_cache_sig = current_sig
    st.session_state._swiper_cached_photos = payload
    return payload


def render_swiper_carousel(
    photos: list,
    current_index: int,
    nomes_em_nc: set = None,
    key: str = "swiper_carousel"
) -> int:
    """
    Renderiza o carrossel moderno baseado em Swiper.js com sincronismo bidirecional
    perfeito e troca de fotos instantânea.
    """
    if not photos:
        return 0

    total = len(photos)
    current_index = max(0, min(current_index, total - 1))
    nomes_em_nc_set = set(nomes_em_nc) if nomes_em_nc else set()

    # Rastreamento de sincronismo para evitar saltos indesejados
    last_synced_key = f"{key}_last_synced"
    last_synced = st.session_state.get(last_synced_key, None)
    comp_val = st.session_state.get(key, None)

    # Se o componente acabou de disparar um novo valor pelo arraste do usuário
    if isinstance(comp_val, int) and 0 <= comp_val < total:
        if last_synced is not None and comp_val != last_synced:
            # O usuário arrastou no frontend: adota imediatamente o índice do frontend
            current_index = comp_val

    # Mantém o rastreamento atualizado
    st.session_state[last_synced_key] = current_index

    # Recupera o payload de fotos instantâneo (com cache O(1))
    serialized_photos = _obter_payload_fotos(photos, nomes_em_nc_set)

    # Executa o componente Streamlit Custom
    result = _swiper_component(
        photos=serialized_photos,
        currentIndex=current_index,
        default=current_index,
        key=key
    )

    if isinstance(result, int) and 0 <= result < total:
        st.session_state[last_synced_key] = result
        return result

    return current_index
