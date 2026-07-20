import streamlit as st
import os
import tempfile
import pandas as pd
import io
from datetime import datetime
from report import gerar_relatorio
from database.manager import (
    carregar_responsaveis, salvar_responsaveis,
    carregar_coordenadores, salvar_coordenadores,
    carregar_contratos, salvar_contratos,
    carregar_custom_ncs, salvar_custom_ncs
)
st.set_page_config(page_title="Gerador de Relatórios", layout="wide")

if "categoria_relatorio" not in st.session_state:
    st.session_state.categoria_relatorio = "Fiscalização"

is_monitoring = st.session_state.categoria_relatorio == "Monitoramento"
term_fisc = "Monitoramento" if is_monitoring else "Fiscalização"
term_fisc_lower = "monitoramento" if is_monitoring else "fiscalização"
term_fisc_plural = "Monitoramentos" if is_monitoring else "Fiscalizações"
term_fisc_plural_lower = "monitoramentos" if is_monitoring else "fiscalizações"
term_fisc_prep = "do Monitoramento" if is_monitoring else "da Fiscalização"
term_fisc_prep_f = "de Monitoramento" if is_monitoring else "de Fiscalização"
term_fisc_pessoal = "pelo monitoramento" if is_monitoring else "pela fiscalização"

@st.dialog("Visualização Completa da Imagem", width="large")
def mostrar_foto_modal(uploaded_file):
    st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

@st.dialog("Confirmar Exclusão em Lote")
def confirmar_exclusao_lote_modal(ids):
    st.write(f"Você tem certeza que deseja excluir as seguintes {term_fisc_plural_lower}?")
    for id_fisc in ids:
        st.write(f"- **{id_fisc}**")
    st.write("Isso também removerá todas as Não Conformidades vinculadas a estes IDs.")
    st.warning("⚠️ Esta ação não pode ser desfeita.")
    
    col_sim, col_nao = st.columns(2)
    with col_sim:
        if st.button("Sim, Excluir", type="primary", use_container_width=True, key="btn_confirm_bulk_del"):
            st.session_state.temp_fiscalizacoes = [f for f in st.session_state.temp_fiscalizacoes if f["ID da Fiscalização"] not in ids]
            st.session_state.temp_nc = [nc for nc in st.session_state.temp_nc if nc["ID da Fiscalização"] not in ids]
            st.session_state.relatorios_preenchimento_data = []
            st.success(f"{term_fisc_plural} selecionadas excluídas com sucesso!")
            st.rerun()
    with col_nao:
        if st.button("Cancelar", use_container_width=True, key="btn_cancel_bulk_del"):
            st.rerun()

@st.dialog("Confirmar Exclusão de Itens")
def confirmar_exclusao_nc_modal(nc_keys):
    st.write("Você tem certeza que deseja excluir os seguintes itens selecionados?")
    for id_fisc, num in nc_keys:
        st.write(f"- **ID {id_fisc} - Item nº {num}**")
    st.warning("⚠️ Esta ação não pode ser desfeita.")
    
    col_sim, col_nao = st.columns(2)
    with col_sim:
        if st.button("Sim, Excluir", type="primary", use_container_width=True, key="btn_confirm_nc_del"):
            # Mantém apenas as NCs que NÃO foram marcadas para exclusão
            st.session_state.temp_nc = [
                nc for nc in st.session_state.temp_nc 
                if (nc["ID da Fiscalização"], nc["Nº"]) not in nc_keys
            ]
            
            # Recalcula a numeração sequencial ("Nº") das NCs restantes por ID de fiscalização
            ncs_por_id = {}
            for nc in st.session_state.temp_nc:
                id_f = nc["ID da Fiscalização"]
                if id_f not in ncs_por_id:
                    ncs_por_id[id_f] = []
                ncs_por_id[id_f].append(nc)
            
            novas_ncs = []
            for id_f, lista in ncs_por_id.items():
                for seq, nc in enumerate(lista, 1):
                    nc["Nº"] = seq
                    novas_ncs.append(nc)
            st.session_state.temp_nc = novas_ncs
            
            st.session_state.relatorios_preenchimento_data = []
            st.success("Não Conformidades selecionadas excluídas com sucesso!")
            st.rerun()
    with col_nao:
        if st.button("Cancelar", use_container_width=True, key="btn_cancel_nc_del"):
            st.rerun()

@st.dialog("Gerenciar Pessoal Responsável")
def gerenciar_responsaveis_modal():
    st.write(f"Adicione, veja ou remova os responsáveis técnicos {term_fisc_pessoal}.")
    
    # 1. Inputs para adicionar novo
    novo_resp = st.text_input("Nome do Novo Responsável")
    nova_matricula = st.text_input("Número de Matrícula (ex: 40672015/01)")
    nova_funcao = st.text_input("Função / Cargo (ex: Analista de Regulação)")
    
    if st.button("➕ Adicionar", use_container_width=True):
        if not novo_resp.strip():
            st.error("O nome do responsável é obrigatório.")
        elif not nova_matricula.strip():
            st.error("O número de matrícula é obrigatório.")
        elif not nova_funcao.strip():
            st.error("A função / cargo é obrigatória.")
        else:
            nomes_existentes = [r["nome"].strip().lower() for r in st.session_state.pessoal_responsaveis]
            if novo_resp.strip().lower() not in nomes_existentes:
                st.session_state.pessoal_responsaveis.append({
                    "nome": novo_resp.strip(),
                    "matricula": nova_matricula.strip(),
                    "funcao": nova_funcao.strip()
                })
                salvar_responsaveis(st.session_state.pessoal_responsaveis)
                st.success(f"'{novo_resp.strip()}' adicionado!")
                st.rerun()
            else:
                st.warning("Este nome já está cadastrado.")
            
    st.divider()
    
    # 2. Lista atual com opção de remover
    st.write("**Responsáveis Cadastrados:**")
    if not st.session_state.pessoal_responsaveis:
        st.info("Nenhum responsável cadastrado.")
    else:
        for idx, resp in enumerate(st.session_state.pessoal_responsaveis):
            col_name, col_del = st.columns([4, 1])
            with col_name:
                st.markdown(f"- **{resp['nome']}**  \n  *{resp['funcao']} - Matrícula: {resp['matricula']}*")
            with col_del:
                if st.button("🗑️", key=f"del_resp_{idx}"):
                    st.session_state.pessoal_responsaveis.pop(idx)
                    salvar_responsaveis(st.session_state.pessoal_responsaveis)
                    st.rerun()

@st.dialog("Gerenciar Coordenadores")
def gerenciar_coordenadores_modal():
    st.write(f"Adicione, veja ou remova os coordenadores {term_fisc_prep_f.lower()}.")
    
    # 1. Inputs para adicionar novo
    novo_coord = st.text_input("Nome do Novo Coordenador")
    nova_matricula = st.text_input("Número de Matrícula (ex: 209640/01)")
    nova_funcao = st.text_input("Função / Cargo (ex: Coordenador(a) de Transportes e Rodovias)")
    
    if st.button("➕ Adicionar Coordenador", use_container_width=True):
        if not novo_coord.strip():
            st.error("O nome do coordenador é obrigatório.")
        elif not nova_matricula.strip():
            st.error("O número de matrícula é obrigatório.")
        elif not nova_funcao.strip():
            st.error("A função / cargo é obrigatória.")
        else:
            nomes_existentes = [c["nome"].strip().lower() for c in st.session_state.coordenadores]
            if novo_coord.strip().lower() not in nomes_existentes:
                st.session_state.coordenadores.append({
                    "nome": novo_coord.strip(),
                    "matricula": nova_matricula.strip(),
                    "funcao": nova_funcao.strip()
                })
                salvar_coordenadores(st.session_state.coordenadores)
                st.success(f"'{novo_coord.strip()}' adicionado!")
                st.rerun()
            else:
                st.warning("Este nome já está cadastrado.")
            
    st.divider()
    
    # 2. Lista atual com opção de remover
    st.write("**Coordenadores Cadastrados:**")
    if not st.session_state.coordenadores:
        st.info("Nenhum coordenador cadastrado.")
    else:
        for idx, coord in enumerate(st.session_state.coordenadores):
            col_name, col_del = st.columns([4, 1])
            with col_name:
                st.markdown(f"- **{coord['nome']}**  \n  *{coord['funcao']} - Matrícula: {coord['matricula']}*")
            with col_del:
                if st.button("🗑️", key=f"del_coord_{idx}"):
                    st.session_state.coordenadores.pop(idx)
                    salvar_coordenadores(st.session_state.coordenadores)
                    st.rerun()

@st.dialog("Gerenciar Contratos")
def gerenciar_contratos_modal():
    st.write("Adicione, veja ou remova os números de contrato cadastrados.")
    
    # 1. Input para adicionar novo
    novo_contrato = st.text_input("Número do Novo Contrato")
    if st.button("➕ Adicionar Contrato", use_container_width=True):
        if novo_contrato.strip():
            if novo_contrato.strip() not in st.session_state.contratos:
                st.session_state.contratos.append(novo_contrato.strip())
                salvar_contratos(st.session_state.contratos)
                st.success(f"'{novo_contrato.strip()}' adicionado!")
                st.rerun()
            else:
                st.warning("Este contrato já está na lista.")
        else:
            st.error("O número do contrato não pode ser vazio.")
            
    st.divider()
    
    # 2. Lista atual com opção de remover
    st.write("**Contratos Cadastrados:**")
    if not st.session_state.contratos:
        st.info("Nenhum contrato cadastrado.")
    else:
        for idx, cont in enumerate(st.session_state.contratos):
            col_name, col_del = st.columns([4, 1])
            with col_name:
                st.write(f"- {cont}")
            with col_del:
                if st.button("🗑️", key=f"del_cont_{idx}"):
                    st.session_state.contratos.pop(idx)
                    salvar_contratos(st.session_state.contratos)
                    st.rerun()

def inject_plus_button_css():
    st.markdown("""
    <style>
    /* Styling specifically for the + button next to pills */
    .green-btn-marker + div div.stButton button {
        background-color: #28a745 !important;
        color: white !important;
        border-color: #28a745 !important;
        font-weight: bold !important;
        font-size: 16px !important;
        border-radius: 4px !important;
        height: 38px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    .green-btn-marker + div div.stButton button:hover {
        background-color: #218838 !important;
        border-color: #1e7e34 !important;
    }
    </style>
    """, unsafe_allow_html=True)

@st.dialog("Adicionar Não Conformidade Personalizada")
def adicionar_nc_personalizada_modal(pills_key):
    st.write("Escolha uma Não Conformidade existente ou cadastre uma nova:")
    
    # 1. Escolher existente
    custom_ncs = st.session_state.custom_ncs
    opcoes_existentes = ["-- Selecionar Existente --"] + [
        f"{item.get('sigla', '')} - {item.get('descricao', '')}" if item.get('sigla') else item.get('descricao')
        for item in custom_ncs
    ]
    
    selected_existente = st.selectbox(
        "Não Conformidades Adicionadas Anteriormente",
        options=opcoes_existentes,
        index=0
    )
    
    st.markdown("---")
    st.write("**Ou cadastre uma nova Não Conformidade:**")
    
    nova_sigla = st.text_input("Sigla (opcional)", placeholder="Ex: ABC")
    nova_desc = st.text_input("Descrição (obrigatório)", placeholder="Ex: Minha descrição personalizada...")
    
    col_salvar, col_cancelar = st.columns(2)
    with col_salvar:
        if st.button("Confirmar", type="primary", use_container_width=True, key="btn_confirm_add_custom_nc"):
            if selected_existente != "-- Selecionar Existente --":
                # Find matching item
                idx = opcoes_existentes.index(selected_existente) - 1
                item = custom_ncs[idx]
                sigla = item.get("sigla", "")
                desc = item.get("descricao", "")
                val_to_select = sigla if sigla else desc
                
                # Make sure it's in options
                if val_to_select not in st.session_state.nc_options:
                    st.session_state.nc_options.append(val_to_select)
                
                # Add to selection
                current_sel = list(st.session_state.get(pills_key, []))
                if val_to_select not in current_sel:
                    st.session_state[pills_key] = current_sel + [val_to_select]
                
                st.success("Não conformidade adicionada!")
                st.rerun()
            else:
                desc_strip = nova_desc.strip()
                sigla_strip = nova_sigla.strip().upper()
                
                if not desc_strip:
                    st.error("O campo 'Descrição' é obrigatório para cadastrar uma nova não conformidade.")
                else:
                    # Save new custom NC
                    new_item = {"sigla": sigla_strip, "descricao": desc_strip}
                    st.session_state.custom_ncs.append(new_item)
                    salvar_custom_ncs(st.session_state.custom_ncs)
                    
                    # Update MAP_SIGLAS and options
                    from sections.quadros.quadros import MAP_SIGLAS
                    val_to_select = sigla_strip if sigla_strip else desc_strip
                    if sigla_strip:
                        MAP_SIGLAS[sigla_strip] = desc_strip
                    
                    if val_to_select not in st.session_state.nc_options:
                        st.session_state.nc_options.append(val_to_select)
                        
                    # Add to selection
                    current_sel = list(st.session_state.get(pills_key, []))
                    if val_to_select not in current_sel:
                        st.session_state[pills_key] = current_sel + [val_to_select]
                        
                    st.success("Nova não conformidade cadastrada e selecionada!")
                    st.rerun()
                    
    with col_cancelar:
        if st.button("Cancelar", use_container_width=True, key="btn_cancel_add_custom_nc"):
            st.rerun()

if "tipo_relatorio" not in st.session_state:
    st.session_state.tipo_relatorio = "CRA"
if "categoria_relatorio" not in st.session_state:
    st.session_state.categoria_relatorio = "Fiscalização"

col_title, col_switch, col_cat, _ = st.columns([0.46, 0.03, 0.03, 0.48], gap="small")
with col_title:
    st.title(f"📄 Gerador {st.session_state.tipo_relatorio} ({st.session_state.categoria_relatorio})")
with col_switch:
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    if st.button("🔄", key="btn_swap_tipo", help="Clique para alternar entre CRA, CRC e SOCICAM"):
        if st.session_state.tipo_relatorio == "CRA":
            st.session_state.tipo_relatorio = "CRC"
        elif st.session_state.tipo_relatorio == "CRC":
            st.session_state.tipo_relatorio = "SOCICAM"
        else:
            st.session_state.tipo_relatorio = "CRA"
        st.rerun()
with col_cat:
    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    if st.button("📋", key="btn_swap_categoria", help="Clique para alternar entre Fiscalização e Monitoramento"):
        if st.session_state.categoria_relatorio == "Fiscalização":
            st.session_state.categoria_relatorio = "Monitoramento"
        else:
            st.session_state.categoria_relatorio = "Fiscalização"
        st.rerun()

# Layout principal da aplicação
with st.container():

    # 1. Upload de Fotos do Levantamento no início
    if "fill_photos_sort_option" not in st.session_state:
        st.session_state.fill_photos_sort_option = "Nome (A-Z / 0-9)"
    if "uploader_version" not in st.session_state:
        st.session_state.uploader_version = 0
        
    col_uploader, col_sort, col_clear = st.columns([3, 1, 1])
    with col_uploader:
        uploaded_nc_photos = st.file_uploader(
            f"Faça o upload de todas as fotos {term_fisc_prep_f.lower()} para usá-las no carrossel de Registros", 
            type=["jpg", "jpeg", "png"], 
            accept_multiple_files=True,
            key=f"fill_photos_uploader_{st.session_state.uploader_version}"
        )
    with col_sort:
        st.write("") # Alinhamento vertical discreto
        st.write("**Ordenar Fotos por:**")
        with st.popover(f"↕️ {st.session_state.fill_photos_sort_option}", use_container_width=True):
            if st.button("Nome (A-Z / 0-9)", use_container_width=True, key="btn_sort_asc"):
                st.session_state.fill_photos_sort_option = "Nome (A-Z / 0-9)"
                st.rerun()
            if st.button("Nome (Z-A / 9-0)", use_container_width=True, key="btn_sort_desc"):
                st.session_state.fill_photos_sort_option = "Nome (Z-A / 9-0)"
                st.rerun()
            if st.button("Ordem de Upload", use_container_width=True, key="btn_sort_upload"):
                st.session_state.fill_photos_sort_option = "Ordem de Upload"
                st.rerun()
    with col_clear:
        st.write("") # Alinhamento vertical discreto
        st.write("**Limpar Fotos:**")
        has_photos = len(uploaded_nc_photos) > 0 if uploaded_nc_photos else False
        if st.button("🗑️ Limpar", disabled=not has_photos, key="btn_clear_uploads", use_container_width=True):
            st.session_state.uploader_version += 1
            if "carousel_index" in st.session_state:
                st.session_state.carousel_index = 0
            st.rerun()

    sort_option = st.session_state.fill_photos_sort_option
    if uploaded_nc_photos:
        photos_to_sort = list(uploaded_nc_photos)
        if sort_option == "Nome (A-Z / 0-9)":
            photos_to_sort.sort(key=lambda x: x.name.lower())
        elif sort_option == "Nome (Z-A / 9-0)":
            photos_to_sort.sort(key=lambda x: x.name.lower(), reverse=True)
        st.session_state.fill_photos = photos_to_sort
    else:
        st.session_state.fill_photos = []

    if "carousel_index" not in st.session_state:
        st.session_state.carousel_index = 0
    if st.session_state.fill_photos:
        st.session_state.carousel_index = min(st.session_state.carousel_index, len(st.session_state.fill_photos) - 1)
        st.session_state.carousel_index = max(0, st.session_state.carousel_index)
    if "temp_fiscalizacoes" not in st.session_state:
        st.session_state.temp_fiscalizacoes = []
    if "temp_nc" not in st.session_state:
        st.session_state.temp_nc = []
    if "nc_form_counter" not in st.session_state:
        st.session_state.nc_form_counter = 0
    if "nc_form_step" not in st.session_state:
        st.session_state.nc_form_step = 1
    if "pista_persistida" not in st.session_state:
        st.session_state.pista_persistida = ""
    if "trecho_persistido" not in st.session_state:
        st.session_state.trecho_persistido = ""
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
        
    from sections.quadros.quadros import MAP_SIGLAS
    for item in st.session_state.custom_ncs:
        sigla = item.get("sigla", "")
        desc = item.get("descricao", "")
        if sigla:
            MAP_SIGLAS[sigla] = desc
            
    if "nc_options" not in st.session_state:
        base_options = ["FI", "TTC", "TTL", "TLC", "TLL", "TRR", "J", "TB", "JE", "TBE", "ALP", "ATP", "O", "P", "EX", "D", "R", "ALC", "ATC", "E"]
        for item in st.session_state.custom_ncs:
            sigla = item.get("sigla", "")
            desc = item.get("descricao", "")
            val_to_add = sigla if sigla else desc
            if val_to_add not in base_options:
                base_options.append(val_to_add)
        st.session_state.nc_options = base_options

    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            id_fisc = st.text_input(f"ID {term_fisc_prep} (ex: 2026-001)", help="Identificador único para vincular as abas")
            data_fisc = st.text_input("Data (ex: 15/06/2026)", placeholder="dd/mm/aaaa")
            if st.session_state.get("tipo_relatorio", "CRA") == "CRA":
                hora = st.text_input("Hora (ex: 10:00)", placeholder="Opcional")
                cidade = st.text_input("Cidade (ex: Recife)", placeholder="Cidade do Terminal")
            else:
                hora = ""
                cidade = ""
                
            if st.session_state.get("tipo_relatorio", "CRA") == "CRC":
                local = "Sistema Viário do Paiva"
                periodo = st.text_input("Período (ex: 15 a 18/06/2026)", placeholder="Opcional")
                submit_fisc = st.button(f"➕ Adicionar {term_fisc}")
            elif st.session_state.get("tipo_relatorio", "CRA") == "SOCICAM":
                local = st.text_input("Local (ex: TIP (RECIFE))", placeholder="Nome do Terminal")
        with col2:
            if st.session_state.get("tipo_relatorio", "CRA") == "CRA":
                local = st.text_input("Local (ex: TIP (RECIFE))", placeholder="Nome do Terminal")
                periodo = st.text_input("Período (ex: 15 a 18/06/2026)", placeholder="Opcional")
            elif st.session_state.get("tipo_relatorio", "CRA") == "SOCICAM":
                periodo = st.text_input("Período (ex: 15 a 18/06/2026)", placeholder="Opcional")
 
            col_resp, col_gear = st.columns([5, 1])
            with col_resp:
                responsaveis_sel = st.multiselect(
                    "Pessoal Responsável",
                    options=st.session_state.pessoal_responsaveis,
                    default=st.session_state.pessoal_responsaveis,
                    format_func=lambda x: x["nome"],
                    help=f"Selecione os responsáveis {term_fisc_pessoal}. Use a engrenagem ao lado para gerenciar a lista."
                )
                responsaveis = ", ".join([r["nome"] for r in responsaveis_sel])
            with col_gear:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                if st.button("⚙️", help="Gerenciar Responsáveis", key="btn_manage_responsaveis"):
                    gerenciar_responsaveis_modal()
            
            # Coordenador
            col_coord, col_gear_coord = st.columns([5, 1])
            with col_coord:
                coordenador_sel = st.selectbox(
                    "Coordenador",
                    options=st.session_state.coordenadores,
                    format_func=lambda x: x["nome"],
                    help=f"Selecione o coordenador {term_fisc_prep_f.lower()}. Use a engrenagem ao lado para gerenciar a lista."
                )
                coordenador = coordenador_sel["nome"] if coordenador_sel else ""
            with col_gear_coord:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                if st.button("⚙️", help="Gerenciar Coordenadores", key="btn_manage_coordenadores"):
                    gerenciar_coordenadores_modal()
            
            # Número do Contrato definido automaticamente por tipo de relatório
            if st.session_state.get("tipo_relatorio", "CRA") == "CRA":
                contrato = "CT. nº 043/2011"
            elif st.session_state.get("tipo_relatorio", "CRA") == "CRC":
                contrato = "CGPE-001/2006"
            else:
                contrato = "CT. nº 1.041.080/08"
 
        if st.session_state.get("tipo_relatorio", "CRA") in ["CRA", "SOCICAM"]:
            submit_fisc = st.button(f"➕ Adicionar {term_fisc}")
        if submit_fisc:
            ids_existentes = [f["ID da Fiscalização"].strip() for f in st.session_state.temp_fiscalizacoes]
            if not id_fisc:
                st.error(f"O ID {term_fisc_prep} é obrigatório.")
            elif not local.strip():
                st.error("O campo 'Local' é obrigatório.")
            elif id_fisc.strip() in ids_existentes:
                st.error(f"O ID {term_fisc_prep} '{id_fisc}' já está cadastrado. Por favor, utilize um ID único.")
            else:
                st.session_state.temp_fiscalizacoes.append({
                    "ID da Fiscalização": id_fisc,
                    "Data": data_fisc,
                    "Hora": hora,
                    "Cidade": cidade,
                    "Local": local,
                    "Pessoal Responsável": responsaveis,
                    "Coordenador": coordenador,
                    "Contrato": contrato,
                    "Período": periodo,
                    "Relatório Gerado": False
                })
                
                # Exibe um aviso listando quais campos adicionais ficaram em branco
                campos_verificar = {
                    "Data": data_fisc,
                    "Hora": hora,
                    "Cidade": cidade,
                    "Pessoal Responsável": responsaveis,
                    "Coordenador": coordenador,
                    "Número do Contrato": contrato,
                    "Período": periodo
                }
                campos_em_branco = [nome for nome, valor in campos_verificar.items() if not str(valor).strip()]
                if campos_em_branco:
                    st.warning(f"⚠️ Atenção: Os seguintes campos opcionais de preenchimento ficaram em branco: {', '.join(campos_em_branco)}.")
                
                st.success(f"{term_fisc} {id_fisc} adicionada!")
                st.rerun()

    st.divider()
    st.subheader("🚩 Registros")
    
    col_inputs, col_preview = st.columns([1.2, 1.0])
    
    with col_preview:
        st.markdown("### 🖼️ Carrossel de Fotos")
        if st.session_state.fill_photos:
            idx = st.session_state.carousel_index
            current_photo = st.session_state.fill_photos[idx]
            
            try:
                from PIL import Image, ImageOps
                image = Image.open(current_photo)
                # Ajusta a foto para caber exatamente em um box padrão de 400x300 mantendo a proporção e cortando o excesso
                preview_image = ImageOps.fit(image, (400, 300))
                st.image(preview_image, caption=f"Foto {idx + 1} de {len(st.session_state.fill_photos)}: {current_photo.name}")
                st.button("🔍 Clique para ampliar a foto", on_click=mostrar_foto_modal, args=(current_photo,), key="btn_zoom_photo_carousel")
            except Exception as e:
                st.image(current_photo, caption=f"Foto {idx + 1} de {len(st.session_state.fill_photos)}: {current_photo.name}", use_container_width=True)
            
            # Controles de Navegação (Voltar e Avançar)
            nav_col1, nav_col2 = st.columns(2)
            with nav_col1:
                if st.button("⬅️ Anterior", disabled=(idx == 0), key="btn_prev_photo"):
                    st.session_state.carousel_index = idx - 1
                    st.rerun()
            with nav_col2:
                if st.button("Próxima ➡️", disabled=(idx == len(st.session_state.fill_photos) - 1), key="btn_next_photo"):
                    st.session_state.carousel_index = idx + 1
                    st.rerun()
            
            st.checkbox(
                "Avançar foto automaticamente",
                value=True,
                key="auto_advance_active",
                help="Avança para a próxima foto do carrossel ao adicionar o Registro"
            )
            
            foto_default = current_photo.name
        else:
            st.info("💡 Faça o upload de fotos no início da página para visualizá-las aqui no carrossel de Registros.")
            foto_default = ""

    with col_inputs:
        if st.session_state.nc_form_step == 1:
            id_vinculo = st.selectbox(f"Vincular ao ID {term_fisc_prep}", [f["ID da Fiscalização"] for f in st.session_state.temp_fiscalizacoes] if st.session_state.temp_fiscalizacoes else ["Nenhum ID cadastrado"])
            
            # Novas variáveis de Pista e Trecho inseridas de forma compacta (lado a lado)
            if st.session_state.get("tipo_relatorio", "CRA") == "CRA":
                col_pista, col_trecho = st.columns(2)
                with col_pista:
                    pista = st.text_input("Pista", value=st.session_state.pista_persistida, key=f"nc_pista_{st.session_state.nc_form_counter}", placeholder="Sul, Norte, Única, Táxi...")
                with col_trecho:
                    trecho = st.text_input("Trecho", value=st.session_state.trecho_persistido, key=f"nc_trecho_{st.session_state.nc_form_counter}", placeholder="Contorno do Cabo, VPE-034...")
            else:
                pista = ""
                trecho = ""

            # Obtém o terminal associado automaticamente a partir do ID da Fiscalização
            terminal_nc = ""
            if id_vinculo != "Nenhum ID cadastrado" and st.session_state.temp_fiscalizacoes:
                for f in st.session_state.temp_fiscalizacoes:
                    if f["ID da Fiscalização"] == id_vinculo:
                        terminal_nc = f["Local"]
                        break
            
            # Calcula o próximo número sequencial de NC para este ID da Fiscalização automaticamente
            nc_num = 1
            if id_vinculo != "Nenhum ID cadastrado" and st.session_state.temp_nc:
                ncs_existentes = [nc for nc in st.session_state.temp_nc if nc["ID da Fiscalização"] == id_vinculo]
                nc_num = len(ncs_existentes) + 1
                
            if st.session_state.get("tipo_relatorio", "CRA") == "CRA":
                tipo_registro = st.pills(
                    "Tipo de Registro",
                    ["Não Conformidade", "Ponto de Atenção"],
                    selection_mode="single",
                    key=f"nc_tipo_{st.session_state.nc_form_counter}",
                    default="Não Conformidade"
                )
            else:
                tipo_registro = "Não Conformidade"
            
            nc_key = f"nc_desc_{st.session_state.nc_form_counter}"
            pa_key = f"pa_desc_{st.session_state.nc_form_counter}"
            
            if tipo_registro == "Não Conformidade":
                col_pills, col_plus = st.columns([11, 1])
                with col_pills:
                    nc_descricao = st.pills(
                        "Siglas de Não Conformidade",
                        st.session_state.nc_options,
                        selection_mode="multi",
                        key=nc_key
                    )
                with col_plus:
                    st.markdown("<div style='height: 28px;' class='green-btn-marker'></div>", unsafe_allow_html=True)
                    inject_plus_button_css()
                    if st.button("+", key=f"btn_add_custom_nc_{st.session_state.nc_form_counter}", help="Adicionar Não Conformidade Personalizada", use_container_width=True):
                        adicionar_nc_personalizada_modal(nc_key)
                ponto_atencao = []
            else:
                col_pills, col_plus = st.columns([11, 1])
                with col_pills:
                    ponto_atencao = st.pills(
                        "Siglas de Ponto de Atenção",
                        st.session_state.nc_options,
                        selection_mode="multi",
                        key=pa_key
                    )
                with col_plus:
                    st.markdown("<div style='height: 28px;' class='green-btn-marker'></div>", unsafe_allow_html=True)
                    inject_plus_button_css()
                    if st.button("+", key=f"btn_add_custom_pa_{st.session_state.nc_form_counter}", help="Adicionar Não Conformidade Personalizada", use_container_width=True):
                        adicionar_nc_personalizada_modal(pa_key)
                nc_descricao = []
            
            nc_legenda = st.text_area("Observações", key=f"nc_obs_{st.session_state.nc_form_counter}", placeholder="Escreva as observações/legenda correspondente...")
            
            col_nxt, col_rel, _ = st.columns([1.7, 2.0, 6.3], gap="small")
            with col_nxt:
                if st.button("➡️ Próximo", type="primary", use_container_width=True):
                    if id_vinculo == "Nenhum ID cadastrado":
                        st.error(f"Adicione um{'' if is_monitoring else 'a'} {term_fisc_lower} primeiro.")
                    elif not nc_descricao and not ponto_atencao:
                        msg_erro = "O campo 'Não Conformidade' é obrigatório." if st.session_state.get("tipo_relatorio", "CRA") in ["CRC", "SOCICAM"] else "O campo 'Não Conformidade' ou 'Ponto de Atenção' é obrigatório."
                        st.error(msg_erro)
                    elif not foto_default:
                        st.error("É obrigatório ter uma foto selecionada no carrossel para continuar.")
                    else:
                        st.session_state.step1_id_vinculo = id_vinculo
                        st.session_state.step1_pista = pista
                        st.session_state.step1_trecho = trecho
                        st.session_state.step1_terminal_nc = terminal_nc
                        st.session_state.step1_nc_num = nc_num
                        st.session_state.step1_nc_desc_str = ", ".join(nc_descricao) if nc_descricao else ""
                        st.session_state.step1_pa_desc_str = ", ".join(ponto_atencao) if ponto_atencao else ""
                        st.session_state.step1_foto_default = foto_default
                        st.session_state.step1_nc_legenda = nc_legenda
                        
                        st.session_state.nc_form_step = 2
                        st.rerun()
            with col_rel:
                disable_rel = len(st.session_state.temp_nc) == 0
                if st.button("🔗 Relacionar", type="secondary", disabled=disable_rel, use_container_width=True):
                    if not foto_default:
                        st.error("É obrigatório ter uma foto selecionada no carrossel para relacionar.")
                    else:
                        last_nc = st.session_state.temp_nc[-1]
                        
                        # Calcula o próximo Nº sequencial dinamicamente para o ID associado
                        target_id = last_nc["ID da Fiscalização"]
                        ncs_existentes = [nc for nc in st.session_state.temp_nc if nc["ID da Fiscalização"] == target_id]
                        new_nc_num = len(ncs_existentes) + 1
                        
                        # Copia todos os campos e atribui a nova foto e número sequencial
                        new_nc = last_nc.copy()
                        new_nc["Foto"] = foto_default
                        new_nc["Nº"] = new_nc_num
                        
                        st.session_state.temp_nc.append(new_nc)
                        
                        # Avançar carrossel automaticamente se houver próxima foto e a opção estiver ativada
                        if st.session_state.get("auto_advance_active", True) and st.session_state.fill_photos and st.session_state.carousel_index < len(st.session_state.fill_photos) - 1:
                            st.session_state.carousel_index += 1
                            
                        # Atualiza valores de persistência
                        st.session_state.pista_persistida = new_nc.get("Pista", "")
                        st.session_state.trecho_persistido = new_nc.get("Trecho", "")
                        
                        st.session_state.nc_form_counter += 1
                        st.success("Informações da última foto relacionadas com sucesso!")
                        st.rerun()
        else:
            # Formulário Etapa 2
            st.markdown(f"### Detalhes do Registro (Foto: `{st.session_state.step1_foto_default}`) - Etapa 2")
            
            identificacao = st.text_input("Identificação", key=f"nc_ident_{st.session_state.nc_form_counter}", placeholder="Identificação da infração...")
            if st.session_state.get("tipo_relatorio", "CRA") == "CRA":
                direcao_faixa = st.text_input("Direção (faixa)", key=f"nc_dir_{st.session_state.nc_form_counter}", placeholder="Direção/faixa...")
            else:
                direcao_faixa = ""
            fundamento_infracao = st.text_input("Fundamento da infração", key=f"nc_fund_{st.session_state.nc_form_counter}", placeholder="Fundamento legal...")
            determinacao = st.text_input("Determinação", key=f"nc_det_{st.session_state.nc_form_counter}", placeholder="Determinação/Ação recomendada...")
            
            col_back, col_add, _ = st.columns([1.1, 1.3, 7.6], gap="small")
            with col_back:
                if st.button("↩️ Voltar", type="secondary", use_container_width=True):
                    st.session_state.nc_form_step = 1
                    st.rerun()
            with col_add:
                if st.button("➕ Adicionar", type="primary", use_container_width=True):
                    st.session_state.temp_nc.append({
                        "ID da Fiscalização": st.session_state.step1_id_vinculo,
                        "Nº": st.session_state.step1_nc_num,
                        "Terminal": st.session_state.step1_terminal_nc,
                        "Pista": st.session_state.step1_pista,
                        "Trecho": st.session_state.step1_trecho,
                        "Não Conformidade": st.session_state.step1_nc_desc_str,
                        "Ponto de Atenção": st.session_state.step1_pa_desc_str,
                        "Foto": st.session_state.step1_foto_default,
                        "Observações": st.session_state.step1_nc_legenda,
                        "Identificação": identificacao,
                        "Direção (faixa)": direcao_faixa,
                        "Fundamento da infração": fundamento_infracao,
                        "Determinação": determinacao
                    })
                    
                    # Avançar carrossel automaticamente se houver próxima foto e a opção estiver ativada
                    if st.session_state.get("auto_advance_active", True) and st.session_state.fill_photos and st.session_state.carousel_index < len(st.session_state.fill_photos) - 1:
                        st.session_state.carousel_index += 1
                        
                    # Salvar valores atuais de pista e trecho para que persistam no formulário
                    st.session_state.pista_persistida = st.session_state.step1_pista
                    st.session_state.trecho_persistido = st.session_state.step1_trecho
                    
                    st.session_state.nc_form_counter += 1
                    st.session_state.nc_form_step = 1
                    st.success(f"Adicionado com sucesso ao ID {st.session_state.step1_id_vinculo}!")
                    st.rerun()

    st.divider()
    if st.session_state.temp_fiscalizacoes:
        with st.expander("📋 Resumo do Preenchimento", expanded=False):
            df_fisc = pd.DataFrame(st.session_state.temp_fiscalizacoes)
            if "Relatório Gerado" in df_fisc.columns:
                df_fisc = df_fisc.drop(columns=["Relatório Gerado"])
            if "Contrato" in df_fisc.columns:
                df_fisc = df_fisc.drop(columns=["Contrato"])
            if st.session_state.get("tipo_relatorio", "CRA") == "CRC":
                for col in ["Hora", "Cidade", "Local"]:
                    if col in df_fisc.columns:
                        df_fisc = df_fisc.drop(columns=[col])
            elif st.session_state.get("tipo_relatorio", "CRA") == "SOCICAM":
                for col in ["Hora", "Cidade"]:
                    if col in df_fisc.columns:
                        df_fisc = df_fisc.drop(columns=[col])
            df_fisc.insert(0, "Excluir", False)
            
            # Apenas para a visualização, encurta o nome dos responsáveis para exibir apenas o primeiro nome
            if "Pessoal Responsável" in df_fisc.columns:
                df_fisc["Pessoal Responsável"] = df_fisc["Pessoal Responsável"].apply(
                    lambda x: ", ".join([name.strip().split()[0] for name in str(x).split(",") if name.strip()])
                )
            
            st.write(f"**{term_fisc_plural}:**")
            edited_df = st.data_editor(
                df_fisc,
                column_config={
                    "Excluir": st.column_config.CheckboxColumn(
                        "Excluir",
                        help=f"Selecione as {term_fisc_plural_lower} que deseja excluir",
                        default=False,
                    ),
                    "ID da Fiscalização": st.column_config.TextColumn(
                        f"ID {term_fisc_prep}",
                        width="medium"
                    ),
                    "Pessoal Responsável": st.column_config.TextColumn(
                        "Pessoal Responsável",
                        width="small"
                    )
                },
                disabled=[col for col in df_fisc.columns if col != "Excluir"],
                use_container_width=True,
                hide_index=True,
                key="fisc_data_editor"
            )
            
            # Identifica as linhas marcadas para exclusão
            selected_rows = edited_df[edited_df["Excluir"] == True] if "Excluir" in edited_df.columns else pd.DataFrame()
            ids_para_excluir = selected_rows["ID da Fiscalização"].tolist() if not selected_rows.empty else []
            
            # Botão que fica habilitado se houver itens selecionados
            disable_btn = len(ids_para_excluir) == 0
            if st.button("🗑️ Excluir Selecionadas", type="secondary", disabled=disable_btn, key="btn_bulk_delete"):
                confirmar_exclusao_lote_modal(ids_para_excluir)
                
            ncs_para_excluir = []
            df_nc = pd.DataFrame(st.session_state.temp_nc)
            
            # 1. Tabela de Não Conformidades (apenas com coluna Não Conformidade)
            st.write("**Não Conformidades:**")
            if not df_nc.empty and "Não Conformidade" in df_nc.columns:
                df_nc_only = df_nc[df_nc["Não Conformidade"].fillna("").astype(str).str.strip() != ""].copy()
                if not df_nc_only.empty:
                    if "Ponto de Atenção" in df_nc_only.columns:
                        df_nc_only = df_nc_only.drop(columns=["Ponto de Atenção"])
                    if st.session_state.get("tipo_relatorio", "CRA") in ["CRC", "SOCICAM"]:
                        for col in ["Terminal", "Trecho", "Pista", "Direção (faixa)"]:
                            if col in df_nc_only.columns:
                                df_nc_only = df_nc_only.drop(columns=[col])
                    df_nc_only.insert(0, "Excluir", False)
                    
                    # Garante ordenação exata das colunas
                    cols_order = ['Excluir', 'ID da Fiscalização', 'Nº', 'Terminal', 'Trecho', 'Pista', 'Não Conformidade', 'Identificação', 'Direção (faixa)', 'Fundamento da infração', 'Determinação']
                    for c in ['Foto', 'Fotos', 'Observações', 'Legenda da Foto']:
                        if c in df_nc_only.columns:
                            cols_order.append(c)
                    cols_order = [c for c in cols_order if c in df_nc_only.columns]
                    df_nc_only = df_nc_only[cols_order]
                    
                    edited_nc_df = st.data_editor(
                        df_nc_only,
                        column_config={
                            "Excluir": st.column_config.CheckboxColumn(
                                "Excluir",
                                help="Selecione as não conformidades que deseja excluir",
                                default=False,
                            ),
                            "ID da Fiscalização": st.column_config.TextColumn(
                                f"ID {term_fisc_prep}"
                            )
                        },
                        disabled=[col for col in df_nc_only.columns if col != "Excluir"],
                        use_container_width=True,
                        hide_index=True,
                        key="nc_data_editor"
                    )
                    
                    # Identifica as linhas marcadas para exclusão
                    selected_ncs = edited_nc_df[edited_nc_df["Excluir"] == True] if "Excluir" in edited_nc_df.columns else pd.DataFrame()
                    ncs_para_excluir = list(zip(selected_ncs["ID da Fiscalização"], selected_ncs["Nº"])) if not selected_ncs.empty else []
                else:
                    st.info("Nenhuma não conformidade registrada.")
            else:
                st.info("Nenhuma não conformidade registrada.")
                
            # 2. Tabela de Pontos de Atenção (apenas com coluna Ponto de Atenção)
            pas_para_excluir = []
            if st.session_state.get("tipo_relatorio", "CRA") == "CRA":
                st.write("") # Espaçamento
                st.write("**Pontos de Atenção:**")
                if not df_nc.empty and "Ponto de Atenção" in df_nc.columns:
                    df_pa_only = df_nc[df_nc["Ponto de Atenção"].fillna("").astype(str).str.strip() != ""].copy()
                    if not df_pa_only.empty:
                        if "Não Conformidade" in df_pa_only.columns:
                            df_pa_only = df_pa_only.drop(columns=["Não Conformidade"])
                        df_pa_only.insert(0, "Excluir", False)
                        
                        # Garante ordenação exata das colunas (Ponto de Atenção após Terminal e antes de Foto)
                        cols_order = ['Excluir', 'ID da Fiscalização', 'Nº', 'Terminal', 'Trecho', 'Pista', 'Ponto de Atenção', 'Identificação', 'Direção (faixa)', 'Fundamento da infração', 'Determinação']
                        for c in ['Foto', 'Fotos', 'Observações', 'Legenda da Foto']:
                            if c in df_pa_only.columns:
                                cols_order.append(c)
                        cols_order = [c for c in cols_order if c in df_pa_only.columns]
                        df_pa_only = df_pa_only[cols_order]
                        
                        edited_pa_df = st.data_editor(
                            df_pa_only,
                            column_config={
                                "Excluir": st.column_config.CheckboxColumn(
                                    "Excluir",
                                    help="Selecione os pontos de atenção que deseja excluir",
                                    default=False,
                                ),
                                "ID da Fiscalização": st.column_config.TextColumn(
                                    f"ID {term_fisc_prep}"
                                )
                            },
                            disabled=[col for col in df_pa_only.columns if col != "Excluir"],
                            use_container_width=True,
                            hide_index=True,
                            key="pa_data_editor"
                        )
                        
                        # Identifica as linhas marcadas para exclusão
                        selected_pas = edited_pa_df[edited_pa_df["Excluir"] == True] if "Excluir" in edited_pa_df.columns else pd.DataFrame()
                        pas_para_excluir = list(zip(selected_pas["ID da Fiscalização"], selected_pas["Nº"])) if not selected_pas.empty else []
                    else:
                        st.info("Nenhum ponto de atenção registrado.")
                else:
                    st.info("Nenhum ponto de atenção registrado.")
                
            # Botão unificado para excluir as selecionadas
            ncs_totais_para_excluir = ncs_para_excluir + pas_para_excluir
            disable_nc_btn = len(ncs_totais_para_excluir) == 0
            label_excluir = "🗑️ Excluir Selecionadas (Não Conformidades)" if st.session_state.get("tipo_relatorio", "CRA") == "CRC" else "🗑️ Excluir Selecionadas (Não Conformidades / Pontos de Atenção)"
            if st.button(label_excluir, type="secondary", disabled=disable_nc_btn, key="btn_nc_bulk_delete"):
                confirmar_exclusao_nc_modal(ncs_totais_para_excluir)
                
            st.write("") # Espaçamento
        st.divider()
        st.subheader("🛠️ Painel de Ações do Relatório")
        
        # Organização dos botões finais em 3 colunas
        col_relatorio, col_planilha, col_limpar = st.columns(3)
        
        # Inicializar estado para persistir os relatórios gerados via aba preenchimento
        if "relatorios_preenchimento_data" not in st.session_state:
            st.session_state.relatorios_preenchimento_data = []
            
        with col_relatorio:
            if st.button("🚀 Gerar Relatório Automático", type="primary", use_container_width=True, key="btn_run_report_main"):
                if not st.session_state.temp_fiscalizacoes:
                    st.error(f"Adicione pelo menos um{'' if is_monitoring else 'a'} {term_fisc_lower} primeiro.")
                else:
                    with st.spinner("Gerando relatórios automaticamente..."):
                        st.session_state.relatorios_preenchimento_data = []
                        flat_fiscalizacoes = []
                        for fisc in st.session_state.temp_fiscalizacoes:
                            id_fisc = fisc["ID da Fiscalização"]
                            ncs = [nc for nc in st.session_state.temp_nc if nc["ID da Fiscalização"] == id_fisc]
                            if not ncs:
                                flat_fiscalizacoes.append({
                                    "ID da Fiscalização": fisc["ID da Fiscalização"],
                                    "Data": fisc["Data"],
                                    "Hora": fisc["Hora"],
                                    "Cidade": fisc["Cidade"],
                                    "Local": fisc["Local"],
                                    "Pessoal Responsável": fisc["Pessoal Responsável"],
                                    "Coordenador": fisc["Coordenador"],
                                    "Contrato": fisc["Contrato"],
                                    "Período": fisc["Período"],
                                    "Observações": "",
                                    "Fotos": "",
                                    "Não conformidade": "",
                                    "Ponto de Atenção": "",
                                    "Pista": "",
                                    "Trecho": "",
                                    "Identificação": "",
                                    "Direção (faixa)": "",
                                    "Fundamento da infração": "",
                                    "Determinação": "",
                                    "Relatório Gerado": fisc["Relatório Gerado"]
                                })
                            else:
                                for nc in ncs:
                                    flat_fiscalizacoes.append({
                                        "ID da Fiscalização": fisc["ID da Fiscalização"],
                                        "Data": fisc["Data"],
                                        "Hora": fisc["Hora"],
                                        "Cidade": fisc["Cidade"],
                                        "Local": fisc["Local"],
                                        "Pessoal Responsável": fisc["Pessoal Responsável"],
                                        "Coordenador": fisc["Coordenador"],
                                        "Contrato": fisc["Contrato"],
                                        "Período": fisc["Período"],
                                        "Observações": nc.get("Observações", nc.get("Legenda da Foto", "")),
                                        "Fotos": nc.get("Foto", nc.get("Fotos", "")),
                                        "Não conformidade": nc.get("Não Conformidade", nc.get("Não conformidade", "")),
                                        "Ponto de Atenção": nc.get("Ponto de Atenção", ""),
                                        "Pista": nc.get("Pista", ""),
                                        "Trecho": nc.get("Trecho", ""),
                                        "Identificação": nc.get("Identificação", ""),
                                        "Direção (faixa)": nc.get("Direção (faixa)", ""),
                                        "Fundamento da infração": nc.get("Fundamento da infração", ""),
                                        "Determinação": nc.get("Determinação", ""),
                                        "Relatório Gerado": fisc["Relatório Gerado"]
                                    })

                        excel_buffer = io.BytesIO()
                        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                            pd.DataFrame(flat_fiscalizacoes).to_excel(writer, sheet_name="Fiscalizações", index=False)
                            pd.DataFrame(st.session_state.temp_nc).to_excel(writer, sheet_name="Não-conformidades ", index=False)
                            pd.DataFrame().to_excel(writer, sheet_name="Observações Importantes", index=False)
                            pd.DataFrame().to_excel(writer, sheet_name="Recomendações", index=False)
                        excel_buffer.seek(0)

                        # 2. Criar diretório temporário para as fotos já enviadas
                        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
                            fotos_dir = os.path.join(temp_dir, "fotos")
                            reports_dir = os.path.join(temp_dir, "reports")
                            os.makedirs(fotos_dir, exist_ok=True)
                            os.makedirs(reports_dir, exist_ok=True)

                            if "fill_photos" in st.session_state and st.session_state.fill_photos:
                                for photo in st.session_state.fill_photos:
                                    with open(os.path.join(fotos_dir, photo.name), "wb") as f:
                                        f.write(photo.getbuffer())

                            try:
                                tipo_key = st.session_state.get("tipo_relatorio", "CRA")
                                if st.session_state.get("categoria_relatorio", "Fiscalização") == "Monitoramento":
                                    tipo_key = f"{tipo_key}_MONITORAMENTO"

                                arquivos_gerados, _ = gerar_relatorio(
                                    caminho_planilha=excel_buffer,
                                    fotos_dir=fotos_dir,
                                    relatorios_dir=reports_dir,
                                    gerar_todos=True,
                                    tipo_relatorio=tipo_key
                                )

                                if not arquivos_gerados:
                                    st.warning("Nenhum relatório gerado.")
                                else:
                                    for arquivo in arquivos_gerados:
                                        nome_base = os.path.basename(arquivo)
                                        with open(arquivo, "rb") as f:
                                            st.session_state.relatorios_preenchimento_data.append({
                                                "nome": nome_base,
                                                "bytes": f.read()
                                            })
                                    st.success(f"✅ {len(arquivos_gerados)} relatório(s) gerado(s) com sucesso!")
                            except Exception as e:
                                st.error(f"❌ Erro ao gerar relatórios: {e}")
                                st.exception(e)
                            finally:
                                import gc
                                gc.collect()
        with col_planilha:
            if st.button("💾 Gerar Planilha Completa", use_container_width=True, key="btn_generate_spreadsheet"):
                flat_fiscalizacoes = []
                for fisc in st.session_state.temp_fiscalizacoes:
                    id_fisc = fisc["ID da Fiscalização"]
                    ncs = [nc for nc in st.session_state.temp_nc if nc["ID da Fiscalização"] == id_fisc]
                    if not ncs:
                        flat_fiscalizacoes.append({
                            "ID da Fiscalização": fisc["ID da Fiscalização"],
                            "Data": fisc["Data"],
                            "Hora": fisc["Hora"],
                            "Cidade": fisc["Cidade"],
                            "Local": fisc["Local"],
                            "Pessoal Responsável": fisc["Pessoal Responsável"],
                            "Coordenador": fisc["Coordenador"],
                            "Contrato": fisc["Contrato"],
                            "Período": fisc["Período"],
                            "Observações": "",
                            "Fotos": "",
                            "Não conformidade": "",
                            "Ponto de Atenção": "",
                            "Pista": "",
                            "Trecho": "",
                            "Identificação": "",
                            "Direção (faixa)": "",
                            "Fundamento da infração": "",
                            "Determinação": "",
                            "Relatório Gerado": fisc["Relatório Gerado"]
                        })
                    else:
                        for nc in ncs:
                            flat_fiscalizacoes.append({
                                "ID da Fiscalização": fisc["ID da Fiscalização"],
                                "Data": fisc["Data"],
                                "Hora": fisc["Hora"],
                                "Cidade": fisc["Cidade"],
                                "Local": fisc["Local"],
                                "Pessoal Responsável": fisc["Pessoal Responsável"],
                                "Coordenador": fisc["Coordenador"],
                                "Contrato": fisc["Contrato"],
                                "Período": fisc["Período"],
                                "Observações": nc.get("Observações", nc.get("Legenda da Foto", "")),
                                "Fotos": nc.get("Foto", nc.get("Fotos", "")),
                                "Não conformidade": nc.get("Não Conformidade", nc.get("Não conformidade", "")),
                                "Ponto de Atenção": nc.get("Ponto de Atenção", ""),
                                "Pista": nc.get("Pista", ""),
                                "Trecho": nc.get("Trecho", ""),
                                "Identificação": nc.get("Identificação", ""),
                                "Direção (faixa)": nc.get("Direção (faixa)", ""),
                                "Fundamento da infração": nc.get("Fundamento da infração", ""),
                                "Determinação": nc.get("Determinação", ""),
                                "Relatório Gerado": fisc["Relatório Gerado"]
                            })

                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    pd.DataFrame(flat_fiscalizacoes).to_excel(writer, sheet_name="Fiscalizações", index=False)
                    pd.DataFrame(st.session_state.temp_nc).to_excel(writer, sheet_name="Não-conformidades ", index=False)
                    pd.DataFrame().to_excel(writer, sheet_name="Observações Importantes", index=False)
                    pd.DataFrame().to_excel(writer, sheet_name="Recomendações", index=False)

                st.session_state.planilha_download_bytes = output.getvalue()
                st.success("Planilha gerada!")
                
            if "planilha_download_bytes" in st.session_state and st.session_state.planilha_download_bytes:
                st.write("") # Pequeno espaçamento
                st.download_button(
                    label="📥 Baixar Planilha",
                    data=st.session_state.planilha_download_bytes,
                    file_name=f"planilha_gerada_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key="dl_btn_planilha"
                )
                
        with col_limpar:
            if st.button("🗑️ Limpar Todos os Dados", type="secondary", use_container_width=True, key="btn_clear_all_data"):
                st.session_state.temp_fiscalizacoes = []
                st.session_state.temp_nc = []
                st.session_state.relatorios_preenchimento_data = []
                if "planilha_download_bytes" in st.session_state:
                    del st.session_state.planilha_download_bytes
                st.rerun()

        # Exibir botões de download dos relatórios se gerados
        if st.session_state.relatorios_preenchimento_data:
            st.write("") # Espaçamento
            st.markdown("---")
            st.write("### 📥 Baixar Relatórios Gerados")
            docx_files = [x for x in st.session_state.relatorios_preenchimento_data if x["nome"].endswith(".docx")]
            
            st.write("**Documentos Word (.docx):**")
            for i, item in enumerate(docx_files):
                st.download_button(
                    label=f"Baixar {item['nome']}",
                    data=item["bytes"],
                    file_name=item["nome"],
                    key=f"dl_fill_docx_{i}_{item['nome']}",
                    use_container_width=True
                )

st.divider()
st.info("Nota: Use a aba 'Preencher Planilha' para montar seus dados e depois a aba 'Gerador' para processar os documentos.")
