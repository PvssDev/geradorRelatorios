# -*- coding: utf-8 -*-
import streamlit as st
from database.manager import (
    salvar_responsaveis,
    salvar_coordenadores,
    salvar_contratos,
    salvar_custom_ncs,
    salvar_custom_ncs_socicam,
)
from sections.quadros.quadros import MAP_SIGLAS, expandir_siglas
from ui.state import sincronizar_opcoes_nc, BASE_NC_OPTIONS, salvar_estado_relatorio_ativo

@st.dialog("Gerenciar Pessoal Responsável", icon=":material/group:")
def gerenciar_responsaveis_modal(term_pessoal="pela fiscalização"):
    st.write(f"Adicione, veja ou remova os responsáveis técnicos {term_pessoal}.")
    
    # 1. Inputs para adicionar novo
    novo_resp = st.text_input("Nome do Novo Responsável")
    nova_matricula = st.text_input("Número de Matrícula (ex: 40672015/01)")
    nova_funcao = st.text_input("Função / Cargo (ex: Analista de Regulação)")
    
    if st.button("Adicionar Responsável", icon=":material/add:", type="primary", use_container_width=True):
        if not novo_resp.strip():
            st.toast(":red[:material/error:] O nome do responsável é obrigatório.")
        elif not nova_matricula.strip():
            st.toast(":red[:material/error:] O número de matrícula é obrigatório.")
        elif not nova_funcao.strip():
            st.toast(":red[:material/error:] A função / cargo é obrigatória.")
        else:
            nomes_existentes = [r["nome"].strip().lower() for r in st.session_state.pessoal_responsaveis]
            if novo_resp.strip().lower() not in nomes_existentes:
                st.session_state.pessoal_responsaveis.append({
                    "nome": novo_resp.strip(),
                    "matricula": nova_matricula.strip(),
                    "funcao": nova_funcao.strip()
                })
                salvar_responsaveis(st.session_state.pessoal_responsaveis)
                st.session_state.pending_toast = f":green[:material/check_circle:] '{novo_resp.strip()}' adicionado!"
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
                if st.button("", icon=":material/delete:", key=f"del_resp_{idx}", help="Remover responsável"):
                    st.session_state.pessoal_responsaveis.pop(idx)
                    salvar_responsaveis(st.session_state.pessoal_responsaveis)
                    st.rerun()




@st.dialog("Gerenciar Coordenadores", icon=":material/manage_accounts:")
def gerenciar_coordenadores_modal(term_prep_f="de fiscalização"):
    st.write(f"Adicione, veja ou remova os coordenadores {term_prep_f.lower()}.")
    
    # 1. Inputs para adicionar novo
    novo_coord = st.text_input("Nome do Novo Coordenador")
    nova_matricula = st.text_input("Número de Matrícula (ex: 209640/01)")
    nova_funcao = st.text_input("Função / Cargo (ex: Coordenador(a) de Transportes e Rodovias)")
    
    if st.button("Adicionar Coordenador", icon=":material/add:", type="primary", use_container_width=True):
        if not novo_coord.strip():
            st.toast(":red[:material/error:] O nome do coordenador é obrigatório.")
        elif not nova_matricula.strip():
            st.toast(":red[:material/error:] O número de matrícula é obrigatório.")
        elif not nova_funcao.strip():
            st.toast(":red[:material/error:] A função / cargo é obrigatória.")
        else:
            nomes_existentes = [c["nome"].strip().lower() for c in st.session_state.coordenadores]
            if novo_coord.strip().lower() not in nomes_existentes:
                st.session_state.coordenadores.append({
                    "nome": novo_coord.strip(),
                    "matricula": nova_matricula.strip(),
                    "funcao": nova_funcao.strip()
                })
                salvar_coordenadores(st.session_state.coordenadores)
                st.session_state.pending_toast = f":green[:material/check_circle:] '{novo_coord.strip()}' adicionado!"
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
                if st.button("", icon=":material/delete:", key=f"del_coord_{idx}", help="Remover coordenador"):
                    st.session_state.coordenadores.pop(idx)
                    salvar_coordenadores(st.session_state.coordenadores)
                    st.rerun()




@st.dialog("Gerenciar Contratos", icon=":material/assignment:")
def gerenciar_contratos_modal():
    st.write("Adicione, veja ou remova os números de contrato cadastrados.")
    
    # 1. Input para adicionar novo
    novo_contrato = st.text_input("Número do Novo Contrato")
    if st.button("Adicionar Contrato", icon=":material/add:", type="primary", use_container_width=True):
        if novo_contrato.strip():
            if novo_contrato.strip() not in st.session_state.contratos:
                st.session_state.contratos.append(novo_contrato.strip())
                salvar_contratos(st.session_state.contratos)
                st.session_state.pending_toast = f":green[:material/check_circle:] '{novo_contrato.strip()}' adicionado!"
                st.rerun()
            else:
                st.warning("Este contrato já está na lista.")
                st.rerun()




@st.dialog("Adicionar Não Conformidade Personalizada", icon=":material/add_circle:")
def adicionar_nc_personalizada_modal(pills_key, is_socicam=False):
    prefix_key = "socicam_" if is_socicam else "norm_"
    st.write("Selecione uma Não Conformidade criada anteriormente ou cadastre uma nova:")
    
    custom_ncs = st.session_state.custom_ncs_socicam if is_socicam else st.session_state.custom_ncs
    
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
                if st.button(label, key=f"sel_custom_nc_{prefix_key}{idx}", use_container_width=True):
                    target_options = st.session_state.socicam_nc_options if is_socicam else st.session_state.nc_options
                    if val_to_select not in target_options:
                        target_options.append(val_to_select)
                    
                    current_sel = list(st.session_state.get(pills_key, []))
                    if val_to_select not in current_sel:
                        st.session_state[pills_key] = current_sel + [val_to_select]
                    st.rerun()
            with col_del:
                if st.button("", icon=":material/delete:", key=f"del_custom_nc_{prefix_key}{idx}", help="Apagar esta não conformidade permanentemente"):
                    del_item = custom_ncs.pop(idx)
                    if is_socicam:
                        salvar_custom_ncs_socicam(st.session_state.custom_ncs_socicam)
                    else:
                        salvar_custom_ncs(st.session_state.custom_ncs)
                    
                    del_sigla = del_item.get("sigla", "")
                    del_desc = del_item.get("descricao", "")
                    del_val = del_sigla if del_sigla else del_desc
                    
                    if del_sigla and del_sigla in MAP_SIGLAS:
                        del MAP_SIGLAS[del_sigla]
                    
                    sincronizar_opcoes_nc()
                    
                    current_sel = list(st.session_state.get(pills_key, []))
                    if del_val in current_sel:
                        st.session_state[pills_key] = [x for x in current_sel if x != del_val]
                        
                    st.rerun()
                    
    st.markdown("---")
    st.write("**Cadastrar uma nova Não Conformidade:**")
    
    nova_sigla = st.text_input("Sigla (opcional)", placeholder="Ex: NC01" if is_socicam else "Ex: ABC")
    nova_desc = st.text_input("Descrição (obrigatório)", placeholder="Ex: Minha descrição personalizada...")
    
    col_salvar, col_cancelar = st.columns(2)
    with col_salvar:
        if st.button("Cadastrar e Selecionar", icon=":material/check:", type="primary", use_container_width=True, key=f"btn_confirm_add_custom_nc_{prefix_key}"):
            desc_strip = nova_desc.strip()
            sigla_strip = nova_sigla.strip().upper()
            
            if not desc_strip:
                st.toast(":red[:material/error:] O campo 'Descrição' é obrigatório para cadastrar uma nova não conformidade.")
            else:
                new_item = {"sigla": sigla_strip, "descricao": desc_strip}
                if is_socicam:
                    st.session_state.custom_ncs_socicam.append(new_item)
                    salvar_custom_ncs_socicam(st.session_state.custom_ncs_socicam)
                else:
                    st.session_state.custom_ncs.append(new_item)
                    salvar_custom_ncs(st.session_state.custom_ncs)
                
                val_to_select = sigla_strip if sigla_strip else desc_strip
                if sigla_strip:
                    MAP_SIGLAS[sigla_strip] = desc_strip
                
                sincronizar_opcoes_nc()
                    
                current_sel = list(st.session_state.get(pills_key, []))
                if val_to_select not in current_sel:
                    st.session_state[pills_key] = current_sel + [val_to_select]
                    
                st.session_state.pending_toast = ":green[:material/check_circle:] Nova não conformidade cadastrada e selecionada!"
                st.rerun()
                    
    with col_cancelar:
        if st.button("Cancelar", icon=":material/close:", use_container_width=True, key=f"btn_cancel_add_custom_nc_{prefix_key}"):
            st.rerun()

