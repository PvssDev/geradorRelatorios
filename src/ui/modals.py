# -*- coding: utf-8 -*-
import streamlit as st
from database.manager import (
    salvar_responsaveis,
    salvar_coordenadores,
    salvar_contratos,
    salvar_custom_ncs
)
from sections.quadros.quadros import MAP_SIGLAS
from ui.state import sincronizar_opcoes_nc, BASE_NC_OPTIONS


@st.dialog("Visualização Completa da Imagem", width="large")
def mostrar_foto_modal(uploaded_file):
    st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)


@st.dialog("Confirmar Exclusão em Lote")
def confirmar_exclusao_lote_modal(ids, term_plural_lower="fiscalizações", term_plural="Fiscalizações"):
    st.write(f"Você tem certeza que deseja excluir as seguintes {term_plural_lower}?")
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
            st.success(f"{term_plural} selecionadas excluídas com sucesso!")
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
def gerenciar_responsaveis_modal(term_pessoal="pela fiscalização"):
    st.write(f"Adicione, veja ou remova os responsáveis técnicos {term_pessoal}.")
    
    # 1. Inputs para adicionar novo
    novo_resp = st.text_input("Nome do Novo Responsável")
    nova_matricula = st.text_input("Número de Matrícula (ex: 40672015/01)")
    nova_funcao = st.text_input("Função / Cargo (ex: Analista de Regulação)")
    
    if st.button("➕ Adicionar Responsável", type="primary", use_container_width=True):
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
            col_name, col_del = st.columns([8.5, 1.5])
            with col_name:
                st.markdown(f"- **{resp['nome']}**  \n  *{resp['funcao']} - Matrícula: {resp['matricula']}*")
            with col_del:
                if st.button("🗑️", key=f"del_resp_{idx}", help="Remover responsável"):
                    st.session_state.pessoal_responsaveis.pop(idx)
                    salvar_responsaveis(st.session_state.pessoal_responsaveis)
                    st.rerun()


@st.dialog("Gerenciar Coordenadores")
def gerenciar_coordenadores_modal(term_prep_f="de fiscalização"):
    st.write(f"Adicione, veja ou remova os coordenadores {term_prep_f.lower()}.")
    
    # 1. Inputs para adicionar novo
    novo_coord = st.text_input("Nome do Novo Coordenador")
    nova_matricula = st.text_input("Número de Matrícula (ex: 209640/01)")
    nova_funcao = st.text_input("Função / Cargo (ex: Coordenador(a) de Transportes e Rodovias)")
    
    if st.button("➕ Adicionar Coordenador", type="primary", use_container_width=True):
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
            col_name, col_del = st.columns([8.5, 1.5])
            with col_name:
                st.markdown(f"- **{coord['nome']}**  \n  *{coord['funcao']} - Matrícula: {coord['matricula']}*")
            with col_del:
                if st.button("🗑️", key=f"del_coord_{idx}", help="Remover coordenador"):
                    st.session_state.coordenadores.pop(idx)
                    salvar_coordenadores(st.session_state.coordenadores)
                    st.rerun()


@st.dialog("Gerenciar Contratos")
def gerenciar_contratos_modal():
    st.write("Adicione, veja ou remova os números de contrato cadastrados.")
    
    # 1. Input para adicionar novo
    novo_contrato = st.text_input("Número do Novo Contrato")
    if st.button("➕ Adicionar Contrato", type="primary", use_container_width=True):
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
            col_name, col_del = st.columns([8.5, 1.5])
            with col_name:
                st.write(f"- {cont}")
            with col_del:
                if st.button("🗑️", key=f"del_cont_{idx}", help="Remover contrato"):
                    st.session_state.contratos.pop(idx)
                    salvar_contratos(st.session_state.contratos)
                    st.rerun()


@st.dialog("Adicionar Não Conformidade Personalizada")
def adicionar_nc_personalizada_modal(pills_key):
    st.write("Selecione uma Não Conformidade criada anteriormente ou cadastre uma nova:")
    
    # 1. Escolher existente e permitir apagar
    custom_ncs = st.session_state.custom_ncs
    
    st.markdown("**Não Conformidades Adicionadas Anteriormente:**")
    if not custom_ncs:
        st.info("Nenhuma não conformidade personalizada cadastrada ainda.")
    else:
        for idx, item in enumerate(custom_ncs):
            sigla = item.get("sigla", "")
            desc = item.get("descricao", "")
            label = f"{sigla} - {desc}" if sigla else desc
            val_to_select = sigla if sigla else desc
            
            col_sel, col_del = st.columns([8.5, 1.5])
            with col_sel:
                # Ao clicar, seleciona diretamente a NC e adiciona ao pills_key
                if st.button(label, key=f"sel_custom_nc_{idx}", use_container_width=True):
                    if val_to_select not in st.session_state.nc_options:
                        st.session_state.nc_options.append(val_to_select)
                    
                    current_sel = list(st.session_state.get(pills_key, []))
                    if val_to_select not in current_sel:
                        st.session_state[pills_key] = current_sel + [val_to_select]
                    st.rerun()
            with col_del:
                if st.button("🗑️", key=f"del_custom_nc_{idx}", help="Apagar esta não conformidade permanentemente"):
                    del_item = st.session_state.custom_ncs.pop(idx)
                    salvar_custom_ncs(st.session_state.custom_ncs)
                    
                    del_sigla = del_item.get("sigla", "")
                    del_desc = del_item.get("descricao", "")
                    del_val = del_sigla if del_sigla else del_desc
                    
                    # Remover do MAP_SIGLAS
                    if del_sigla and del_sigla in MAP_SIGLAS:
                        del MAP_SIGLAS[del_sigla]
                    
                    # Reconstruir st.session_state.nc_options
                    sincronizar_opcoes_nc()
                    
                    # Remover da seleção ativa se estiver selecionado
                    current_sel = list(st.session_state.get(pills_key, []))
                    if del_val in current_sel:
                        st.session_state[pills_key] = [x for x in current_sel if x != del_val]
                        
                    st.rerun()
                    
    st.markdown("---")
    st.write("**Cadastrar uma nova Não Conformidade:**")
    
    nova_sigla = st.text_input("Sigla (opcional)", placeholder="Ex: ABC")
    nova_desc = st.text_input("Descrição (obrigatório)", placeholder="Ex: Minha descrição personalizada...")
    
    col_salvar, col_cancelar = st.columns(2)
    with col_salvar:
        if st.button("Cadastrar e Selecionar", type="primary", use_container_width=True, key="btn_confirm_add_custom_nc"):
            desc_strip = nova_desc.strip()
            sigla_strip = nova_sigla.strip().upper()
            
            if not desc_strip:
                st.error("O campo 'Descrição' é obrigatório para cadastrar uma nova não conformidade.")
            else:
                # Salva nova NC
                new_item = {"sigla": sigla_strip, "descricao": desc_strip}
                st.session_state.custom_ncs.append(new_item)
                salvar_custom_ncs(st.session_state.custom_ncs)
                
                # Atualiza MAP_SIGLAS e options
                val_to_select = sigla_strip if sigla_strip else desc_strip
                if sigla_strip:
                    MAP_SIGLAS[sigla_strip] = desc_strip
                
                sincronizar_opcoes_nc()
                    
                # Adiciona à seleção
                current_sel = list(st.session_state.get(pills_key, []))
                if val_to_select not in current_sel:
                    st.session_state[pills_key] = current_sel + [val_to_select]
                    
                st.success("Nova não conformidade cadastrada e selecionada!")
                st.rerun()
                    
    with col_cancelar:
        if st.button("Cancelar", use_container_width=True, key="btn_cancel_add_custom_nc"):
            st.rerun()
