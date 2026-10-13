# -*- coding: utf-8 -*-
import streamlit as st
from database.manager import (
    carregar_responsaveis,
    carregar_coordenadores,
    carregar_contratos,
    carregar_custom_ncs,
    carregar_custom_ncs_socicam
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
        "term_fisc_prep_f": "pelo Monitoramento" if is_monitoring else "pela Fiscalização",
        "term_fisc_pessoal": "Equipe de Monitoramento" if is_monitoring else "Equipe de Fiscalização"
    }


def inicializar_estado_sessao() -> None:
    """Inicializa as chaves essenciais no st.session_state caso não existam."""
    defaults = {
        "tipo_relatorio": "CRA",
        "categoria_relatorio": "Fiscalização",
        "temp_fiscalizacoes": [],
        "temp_nc": [],
        "nc_form_counter": 0,
        "nc_form_step": 1,
        "fill_photos": [],
        "carousel_index": 0,
        "fill_photos_sort_option": "Nome (A-Z / 0-9)",
        "photos_uploader_version": 0,
        "mon_uploader_version": 0,
        "pista_persistida": "",
        "trecho_persistido": "",
        "show_foto_modal": False,
        "modal_foto_path": None,
        "show_confirm_exclusao_lote": False,
        "show_confirm_exclusao_nc": False,
        "nc_para_excluir_idx": None,
        "show_responsaveis_modal": False,
        "show_coordenadores_modal": False,
        "show_contratos_modal": False,
        "show_add_custom_nc_modal": False,
        "active_pills_key_modal": None,
        "manual_relacao_map": {}
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

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

    if "custom_ncs_socicam" not in st.session_state:
        st.session_state.custom_ncs_socicam = carregar_custom_ncs_socicam()

    sincronizar_opcoes_nc()


def sincronizar_opcoes_nc() -> None:
    """Sincroniza as siglas customizadas no mapa de siglas e na lista de opções de seleção."""
    custom_ncs = st.session_state.get("custom_ncs", [])
    for item in custom_ncs:
        sigla = item.get("sigla", "")
        desc = item.get("descricao", "")
        if sigla:
            MAP_SIGLAS[sigla] = desc

    custom_ncs_socicam = st.session_state.get("custom_ncs_socicam", [])
    for item in custom_ncs_socicam:
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

    socicam_options = []
    for item in custom_ncs_socicam:
        sigla = item.get("sigla", "")
        desc = item.get("descricao", "")
        val_to_add = sigla if sigla else desc
        if val_to_add and val_to_add not in socicam_options:
            socicam_options.append(val_to_add)

    st.session_state.socicam_nc_options = socicam_options
