# -*- coding: utf-8 -*-
import streamlit as st
from database.manager import (
    carregar_responsaveis,
    carregar_coordenadores,
    carregar_contratos,
    carregar_custom_ncs
)
from sections.quadros.quadros import MAP_SIGLAS

BASE_NC_OPTIONS = [
    "FI", "TTC", "TTL", "TLC", "TLL", "TRR", "J", "TB",
    "JE", "TBE", "ALP", "ATP", "O", "P", "EX", "D", "R",
    "ALC", "ATC", "E"
]


def obter_termos_ui(is_monitoring: bool) -> dict:
    """Retorna o dicionário com as variações textuais de Fiscalização vs Monitoramento."""
    return {
        "term_fisc": "Monitoramento" if is_monitoring else "Fiscalização",
        "term_fisc_lower": "monitoramento" if is_monitoring else "fiscalização",
        "term_fisc_plural": "Monitoramentos" if is_monitoring else "Fiscalizações",
        "term_fisc_plural_lower": "monitoramentos" if is_monitoring else "fiscalizações",
        "term_fisc_prep": "do Monitoramento" if is_monitoring else "da Fiscalização",
        "term_fisc_prep_f": "de Monitoramento" if is_monitoring else "de Fiscalização",
        "term_fisc_pessoal": "pelo monitoramento" if is_monitoring else "pela fiscalização",
    }


def inicializar_estado_sessao() -> None:
    """Garante que todas as chaves essenciais de st.session_state existam."""
    defaults = {
        "categoria_relatorio": "Fiscalização",
        "tipo_relatorio": "CRA",
        "photos_uploader_version": 0,
        "mon_uploader_version": 0,
        "carousel_index": 0,
        "temp_fiscalizacoes": [],
        "temp_nc": [],
        "nc_form_counter": 0,
        "nc_form_step": 1,
        "step1_id_vinculo": "Nenhum ID cadastrado",
        "step1_pista": "",
        "step1_trecho": "",
        "step1_terminal_nc": "",
        "step1_nc_num": 1,
        "step1_nc_desc_str": "",
        "step1_pa_desc_str": "",
        "step1_foto_default": "",
        "step1_nc_legenda": "",
        "step1_situacao": "Pendente",
        "step1_foto_anterior": "",
        "step1_legenda_anterior": "",
        "step1_identificacao": "",
        "pista_persistida": "",
        "trecho_persistido": "",
        "relatorios_preenchimento_data": [],
        "fill_photos": [],
        "fill_photos_sort_option": "Nome (A-Z / 0-9)",
        "old_photos_to_match": []
    }

    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # Carrega dados do banco local se não existirem ou se estiverem em formato antigo
    if "pessoal_responsaveis" not in st.session_state or (
        st.session_state.pessoal_responsaveis and isinstance(st.session_state.pessoal_responsaveis[0], str)
    ):
        st.session_state.pessoal_responsaveis = carregar_responsaveis()

    if "coordenadores" not in st.session_state or (
        st.session_state.coordenadores and isinstance(st.session_state.coordenadores[0], str)
    ):
        st.session_state.coordenadores = carregar_coordenadores()

    if "contratos" not in st.session_state:
        st.session_state.contratos = carregar_contratos()

    if "custom_ncs" not in st.session_state:
        st.session_state.custom_ncs = carregar_custom_ncs()

    sincronizar_opcoes_nc()


def sincronizar_opcoes_nc() -> None:
    """Sincroniza as siglas customizadas no mapa de siglas e na lista de opções de seleção."""
    custom_ncs = st.session_state.get("custom_ncs", [])
    for item in custom_ncs:
        sigla = item.get("sigla", "")
        desc = item.get("descricao", "")
        if sigla:
            MAP_SIGLAS[sigla] = desc

    current_options = BASE_NC_OPTIONS.copy()
    for item in custom_ncs:
        sigla = item.get("sigla", "")
        desc = item.get("descricao", "")
        val_to_add = sigla if sigla else desc
        if val_to_add and val_to_add not in current_options:
            current_options.append(val_to_add)

    st.session_state.nc_options = current_options
