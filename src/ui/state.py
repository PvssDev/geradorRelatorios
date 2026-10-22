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
from services.session_cache_service import carregar_sessao_local, salvar_sessao_local

BASE_NC_OPTIONS = [
    "FI", "TTC", "TTL", "TLC", "TLL", "TRR", "J", "TB",
    "JE", "TBE", "ALP", "ATP", "O", "P", "EX", "D", "R",
    "ALC", "ATC", "E"
]

__all__ = [
    "BASE_NC_OPTIONS",
    "obter_termos_ui",
    "inicializar_estado_sessao",
    "carregar_estado_relatorio_ativo",
    "salvar_estado_relatorio_ativo",
    "enfileirar_acao_fs",
    "verificar_e_alternar_relatorio",
    "sincronizar_opcoes_nc"
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
        "codificacao_persistida": "",
        "fundamento_persistido": "",
        "determinacao_persistida": "",
        "faixa_persistida": "",
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
        "manual_relacao_map": {},
        "otimizar_fotos_relatorio": True
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

    # Carrega o cache inicial do relatório ativo (apenas na inicialização ou se ainda não carregado)
    if not st.session_state.get("_cache_inicial_carregado", False):
        carregar_estado_relatorio_ativo()
        st.session_state._cache_inicial_carregado = True
        st.session_state._ultimo_par_relatorio = (
            st.session_state.tipo_relatorio,
            st.session_state.categoria_relatorio
        )


def carregar_estado_relatorio_ativo() -> None:
    """Carrega dados salvos em disco (geradorRelatorios/) para o tipo e categoria atuais."""
    tipo = st.session_state.get("tipo_relatorio", "CRA")
    cat = st.session_state.get("categoria_relatorio", "Fiscalização")
    dados = carregar_sessao_local(tipo, cat)
    if dados and isinstance(dados, dict):
        st.session_state.temp_fiscalizacoes = dados.get("temp_fiscalizacoes", [])
        st.session_state.temp_nc = dados.get("temp_nc", [])
        st.session_state.manual_relacao_map = dados.get("manual_relacao_map", {})
        if "pista_persistida" in dados:
            st.session_state.pista_persistida = dados.get("pista_persistida", "")
        if "trecho_persistido" in dados:
            st.session_state.trecho_persistido = dados.get("trecho_persistido", "")
        if "codificacao_persistida" in dados:
            st.session_state.codificacao_persistida = dados.get("codificacao_persistida", "")
        if "fundamento_persistido" in dados:
            st.session_state.fundamento_persistido = dados.get("fundamento_persistido", "")
        if "determinacao_persistida" in dados:
            st.session_state.determinacao_persistida = dados.get("determinacao_persistida", "")
        if "faixa_persistida" in dados:
            st.session_state.faixa_persistida = dados.get("faixa_persistida", "")


def salvar_estado_relatorio_ativo(media_to_save: list = None) -> None:
    """
    Salva os dados atuais de st.session_state no arquivo JSON correspondente ao relatório ativo
    e enfileira sincronização com o sistema de arquivos local da máquina do usuário.
    """
    tipo = st.session_state.get("tipo_relatorio", "CRA")
    cat = st.session_state.get("categoria_relatorio", "Fiscalização")
    dados = {
        "temp_fiscalizacoes": st.session_state.get("temp_fiscalizacoes", []),
        "temp_nc": st.session_state.get("temp_nc", []),
        "manual_relacao_map": st.session_state.get("manual_relacao_map", {}),
        "pista_persistida": st.session_state.get("pista_persistida", ""),
        "trecho_persistido": st.session_state.get("trecho_persistido", ""),
        "codificacao_persistida": st.session_state.get("codificacao_persistida", ""),
        "fundamento_persistido": st.session_state.get("fundamento_persistido", ""),
        "determinacao_persistida": st.session_state.get("determinacao_persistida", ""),
        "faixa_persistida": st.session_state.get("faixa_persistida", "")
    }
    salvar_sessao_local(tipo, cat, dados)

    # Enfileira ação de salvamento para a pasta física do usuário via File System Access API
    enfileirar_acao_fs({
        "action": "SAVE",
        "tipo": tipo,
        "cat": cat,
        "state_data": dados,
    })


def enfileirar_acao_fs(acao: dict) -> None:
    """
    Adiciona uma ação à fila de sincronização com a pasta local (File System Access API).
    A ação permanece na fila até o componente confirmar (ACK) que a executou.
    """
    versao = st.session_state.get("_fs_sync_version", 0) + 1
    st.session_state._fs_sync_version = versao
    item = dict(acao)
    item["version"] = versao
    fila = list(st.session_state.get("_fs_action_queue", []))
    fila.append(item)
    st.session_state._fs_action_queue = fila


def verificar_e_alternar_relatorio(novo_tipo: str, nova_categoria: str) -> None:
    """
    Ao alternar entre uma das 6 possibilidades de relatório, salva o relatório atual
    e carrega os dados do novo relatório selecionado a partir do seu cache local.
    """
    par_atual = (st.session_state.get("tipo_relatorio"), st.session_state.get("categoria_relatorio"))
    novo_par = (novo_tipo, nova_categoria)

    if par_atual != novo_par:
        # Salva o estado atual antes de alternar
        salvar_estado_relatorio_ativo()

        # Atualiza para o novo par
        st.session_state.tipo_relatorio = novo_tipo
        st.session_state.categoria_relatorio = nova_categoria
        st.session_state.widget_menu_tipo = novo_tipo
        st.session_state.widget_menu_categoria = nova_categoria
        st.session_state._ultimo_par_relatorio = novo_par

        # Carrega o cache do novo par selecionado
        carregar_estado_relatorio_ativo()
        st.session_state.nc_form_step = 1
        st.session_state.carousel_index = 0

        # Enfileira leitura da pasta física do usuário para o novo par
        enfileirar_acao_fs({
            "action": "LOAD",
            "tipo": novo_tipo,
            "cat": nova_categoria,
        })


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
