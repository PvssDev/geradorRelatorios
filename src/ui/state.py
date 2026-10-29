import os
import base64
import mimetypes
from typing import Optional, List, Dict, Any
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
    "validar_integridade_estado_concessao",
    "BASE_NC_OPTIONS",
    "obter_termos_ui",
    "inicializar_estado_sessao",
    "carregar_estado_relatorio_ativo",
    "salvar_estado_relatorio_ativo",
    "enfileirar_acao_fs",
    "enfileirar_sincronizacao_midia",
    "serializar_arquivo_para_payload_fs",
    "verificar_e_alternar_relatorio",
    "ao_alternar_tipo_menu",
    "ao_alternar_categoria_menu",
    "sincronizar_opcoes_nc",
    "resetar_estado_sessao_relatorio_ativo"
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


def validar_integridade_estado_concessao(tipo: str, dados: dict) -> bool:
    """
    Valida se os dados persistidos correspondem estritamente à concessionária ativa.
    Impede que dados residuais ou contaminações cruzadas (ex: CRA dentro de SOCICAM)
    sejam carregados indevidamente no session_state.
    """
    if not dados or not isinstance(dados, dict):
        return True

    fisc_list = dados.get("temp_fiscalizacoes", [])
    if not fisc_list:
        return True

    tipo_upper = str(tipo or "").upper().strip()
    for f in fisc_list:
        loc = str(f.get("Local", "") or "").lower()
        contrato = str(f.get("Contrato", "") or "").lower()

        if tipo_upper == "SOCICAM":
            # SOCICAM opera exclusivamente terminais rodoviários e contrato 1.041.080/08
            if any(termo in loc for termo in ["rota do atlântico", "rota dos coqueiros", "pe-024"]) or any(termo in contrato for termo in ["043/2011", "cgpe"]):
                return False
        elif tipo_upper == "CRA":
            # CRA opera a Rota do Atlântico
            if any(termo in loc for termo in ["terminal rodoviário", "tip", "rota dos coqueiros"]) or "1.041.080/08" in contrato:
                return False
        elif tipo_upper == "CRC":
            # CRC opera a Rota dos Coqueiros
            if any(termo in loc for termo in ["terminal rodoviário", "tip", "rota do atlântico"]) or "1.041.080/08" in contrato:
                return False

    return True


def carregar_estado_relatorio_ativo() -> None:
    """Carrega dados salvos em disco (geradorRelatorios/) para o tipo e categoria atuais."""
    tipo = st.session_state.get("tipo_relatorio", "CRA")
    cat = st.session_state.get("categoria_relatorio", "Fiscalização")
    dados = carregar_sessao_local(tipo, cat)
    if dados and isinstance(dados, dict):
        if not validar_integridade_estado_concessao(tipo, dados):
            limpar_sessao_local(tipo, cat)
            st.session_state.temp_fiscalizacoes = []
            st.session_state.temp_nc = []
            st.session_state.manual_relacao_map = {}
            st.session_state.pista_persistida = ""
            st.session_state.trecho_persistido = ""
            st.session_state.codificacao_persistida = ""
            st.session_state.fundamento_persistido = ""
            st.session_state.determinacao_persistida = ""
            st.session_state.faixa_persistida = ""
            return

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
    else:
        st.session_state.temp_fiscalizacoes = []
        st.session_state.temp_nc = []
        st.session_state.manual_relacao_map = {}
        st.session_state.pista_persistida = ""
        st.session_state.trecho_persistido = ""
        st.session_state.codificacao_persistida = ""
        st.session_state.fundamento_persistido = ""
        st.session_state.determinacao_persistida = ""
        st.session_state.faixa_persistida = ""


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


def serializar_arquivo_para_payload_fs(arquivo: Any) -> Optional[Dict[str, Any]]:
    """Converte um arquivo enviado (UploadedFile, LocalMediaFile ou similar) em payload Base64 para Local Storage."""
    if not arquivo:
        return None
    nome = getattr(arquivo, "name", None)
    if not nome and isinstance(arquivo, str):
        nome = os.path.basename(arquivo)
    if not nome:
        return None

    # Se já for um RestoredLocalFile com Data URL prévia
    if hasattr(arquivo, "b64_data") and getattr(arquivo, "b64_data"):
        data_url = str(arquivo.b64_data)
        size = getattr(arquivo, "size", 0)
        mime = getattr(arquivo, "type", "application/octet-stream")
        return {
            "name": nome,
            "size": size,
            "type": mime,
            "base64": data_url
        }

    raw_bytes = b""
    if hasattr(arquivo, "seek"):
        try:
            arquivo.seek(0)
        except Exception:
            pass
    if hasattr(arquivo, "getvalue"):
        raw_bytes = arquivo.getvalue()
    elif hasattr(arquivo, "read"):
        raw_bytes = arquivo.read()
        if hasattr(arquivo, "seek"):
            try:
                arquivo.seek(0)
            except Exception:
                pass
    elif isinstance(arquivo, (bytes, bytearray)):
        raw_bytes = bytes(arquivo)
    elif hasattr(arquivo, "filepath") and os.path.exists(getattr(arquivo, "filepath")):
        with open(getattr(arquivo, "filepath"), "rb") as f:
            raw_bytes = f.read()
    elif isinstance(arquivo, str) and os.path.exists(arquivo):
        with open(arquivo, "rb") as f:
            raw_bytes = f.read()

    if not raw_bytes:
        return None

    mime, _ = mimetypes.guess_type(nome)
    if not mime:
        mime = getattr(arquivo, "type", "application/octet-stream") or "application/octet-stream"

    b64_str = base64.b64encode(raw_bytes).decode("utf-8")
    data_url = f"data:{mime};base64,{b64_str}"

    return {
        "name": nome,
        "size": len(raw_bytes),
        "type": mime,
        "base64": data_url
    }


def enfileirar_sincronizacao_midia(
    tipo: str,
    cat: str,
    photos_to_save: Optional[List[Dict[str, Any]]] = None,
    active_photo_names: Optional[List[str]] = None,
    arquivos_to_save: Optional[List[Dict[str, Any]]] = None,
    active_arquivo_names: Optional[List[str]] = None,
) -> None:
    """Enfileira ação SYNC_MEDIA para sincronizar mídias na pasta física do usuário via File System Access API."""
    acao = {
        "action": "SYNC_MEDIA",
        "tipo": tipo,
        "cat": cat,
    }
    if photos_to_save is not None:
        acao["photos_to_save"] = photos_to_save
    if active_photo_names is not None:
        acao["active_photo_names"] = active_photo_names
    if arquivos_to_save is not None:
        acao["arquivos_to_save"] = arquivos_to_save
    if active_arquivo_names is not None:
        acao["active_arquivo_names"] = active_arquivo_names

    enfileirar_acao_fs(acao)


def verificar_e_alternar_relatorio(novo_tipo: str, nova_categoria: str) -> None:
    """
    Ao alternar entre uma das 6 possibilidades de relatório:
    1. Salva o relatório atual antes de alternar;
    2. Reseta as variáveis transitórias em memória e os uploaders do navegador;
    3. Atualiza o tipo e categoria ativos;
    4. Carrega o estado e as fotos da nova modalidade (se houver, restaura; se vazia, permanece limpa).
    """
    par_atual = (st.session_state.get("tipo_relatorio"), st.session_state.get("categoria_relatorio"))
    novo_par = (novo_tipo, nova_categoria)

    if par_atual != novo_par:
        from services.media_storage_service import carregar_fotos_disco

        # 1. Salva o estado atual antes de alternar
        salvar_estado_relatorio_ativo()

        # 2. Reseta as variáveis transitórias em memória
        st.session_state.temp_fiscalizacoes = []
        st.session_state.temp_nc = []
        st.session_state.manual_relacao_map = {}
        st.session_state.fill_photos = []
        st.session_state._fotos_restauradas = []
        st.session_state._uploader_fotos_anteriores = []
        st.session_state._fotos_excluidas_galeria = set()
        st.session_state.uploaded_mon_anterior = None
        st.session_state.uploaded_planilha_elegibilidade = None
        st.session_state.old_photos_to_match = []
        st.session_state.carousel_index = 0
        st.session_state.nc_form_step = 1

        # Reseta os uploaders (incrementa a versão para o browser descartar os arquivos antigos)
        st.session_state.photos_uploader_version = st.session_state.get("photos_uploader_version", 0) + 1
        st.session_state.mon_uploader_version = st.session_state.get("mon_uploader_version", 0) + 1
        st.session_state.planilha_elegibilidade_version = st.session_state.get("planilha_elegibilidade_version", 0) + 1

        # 3. Atualiza para o novo par
        st.session_state.tipo_relatorio = novo_tipo
        st.session_state.categoria_relatorio = nova_categoria

        # Sincroniza widgets de menu no session_state apenas se divergirem,
        # prevenindo StreamlitAPIException caso o widget já tenha sido instanciado.
        if st.session_state.get("widget_menu_tipo") != novo_tipo:
            try:
                st.session_state.widget_menu_tipo = novo_tipo
            except Exception:
                pass

        if st.session_state.get("widget_menu_categoria") != nova_categoria:
            try:
                st.session_state.widget_menu_categoria = nova_categoria
            except Exception:
                pass

        st.session_state._ultimo_par_relatorio = novo_par

        # 4. Carrega o estado JSON da nova modalidade
        carregar_estado_relatorio_ativo()

        # 5. Carrega as fotos da nova modalidade salvas em disco (se existirem)
        fotos_salvas = carregar_fotos_disco(novo_tipo, nova_categoria)
        if fotos_salvas:
            st.session_state.fill_photos = fotos_salvas
            st.session_state._fotos_restauradas = fotos_salvas
            st.session_state._uploader_fotos_anteriores = []

        # 6. Enfileira leitura da pasta física do usuário para o novo par
        enfileirar_acao_fs({
            "action": "LOAD",
            "tipo": novo_tipo,
            "cat": nova_categoria,
        })


def ao_alternar_tipo_menu() -> None:
    """Callback do widget st.pills de tipo de relatório."""
    novo_tipo = st.session_state.get("widget_menu_tipo")
    if not novo_tipo:
        st.session_state.widget_menu_tipo = st.session_state.get("tipo_relatorio", "CRA")
        return
    if novo_tipo != st.session_state.get("tipo_relatorio"):
        verificar_e_alternar_relatorio(novo_tipo, st.session_state.get("categoria_relatorio", "Fiscalização"))


def ao_alternar_categoria_menu() -> None:
    """Callback do widget st.pills de categoria de relatório."""
    nova_cat = st.session_state.get("widget_menu_categoria")
    if not nova_cat:
        st.session_state.widget_menu_categoria = st.session_state.get("categoria_relatorio", "Fiscalização")
        return
    if nova_cat != st.session_state.get("categoria_relatorio"):
        verificar_e_alternar_relatorio(st.session_state.get("tipo_relatorio", "CRA"), nova_cat)


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


def resetar_estado_sessao_relatorio_ativo(tipo_relatorio: str, categoria_relatorio: str) -> None:
    """
    Limpa todos os arquivos físicos no disco (JSON de estado, fotos e documentos auxiliares)
    e reseta as variáveis do session_state correspondentes ao relatório selecionado.
    """
    from services.media_storage_service import limpar_estado_completo_relatorio_disco

    # 1. Limpeza física no disco (JSON de estado, fotos e arquivos)
    limpar_estado_completo_relatorio_disco(tipo_relatorio, categoria_relatorio)

    # 2. Reset em memória no Streamlit
    st.session_state.temp_fiscalizacoes = []
    st.session_state.temp_nc = []
    st.session_state.manual_relacao_map = {}
    st.session_state.fill_photos = []
    st.session_state._fotos_restauradas = []
    st.session_state._uploader_fotos_anteriores = []
    st.session_state._fotos_excluidas_galeria = set()
    st.session_state.old_photos_to_match = []
    st.session_state.uploaded_mon_anterior = None
    st.session_state.uploaded_planilha_elegibilidade = None
    st.session_state._mon_doc_salvo_nome = None
    st.session_state._planilha_salva_nome = None

    st.session_state.pista_persistida = ""
    st.session_state.trecho_persistido = ""
    st.session_state.codificacao_persistida = ""
    st.session_state.fundamento_persistido = ""
    st.session_state.determinacao_persistida = ""
    st.session_state.faixa_persistida = ""

    st.session_state.photos_uploader_version = st.session_state.get("photos_uploader_version", 0) + 1
    st.session_state.mon_uploader_version = st.session_state.get("mon_uploader_version", 0) + 1
    st.session_state.planilha_elegibilidade_version = st.session_state.get("planilha_elegibilidade_version", 0) + 1
    st.session_state.carousel_index = 0
    st.session_state.nc_form_step = 1
    st.session_state.nc_form_counter = st.session_state.get("nc_form_counter", 0) + 1

    # 3. Notifica sincronização de sistema de arquivos local se ativa
    enfileirar_acao_fs({
        "action": "CLEAR",
        "tipo": tipo_relatorio,
        "cat": categoria_relatorio,
    })

