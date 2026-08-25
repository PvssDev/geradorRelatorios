# -*- coding: utf-8 -*-
import streamlit as st
from database.manager import (
    salvar_responsaveis,
    salvar_coordenadores,
    salvar_contratos,
    salvar_custom_ncs,
    salvar_custom_ncs_socicam
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
                st.rerun()


@st.dialog("Adicionar Não Conformidade Personalizada")
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
                if st.button("🗑️", key=f"del_custom_nc_{prefix_key}{idx}", help="Apagar esta não conformidade permanentemente"):
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
        if st.button("Cadastrar e Selecionar", type="primary", use_container_width=True, key=f"btn_confirm_add_custom_nc_{prefix_key}"):
            desc_strip = nova_desc.strip()
            sigla_strip = nova_sigla.strip().upper()
            
            if not desc_strip:
                st.error("O campo 'Descrição' é obrigatório para cadastrar uma nova não conformidade.")
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
                    
                st.success("Nova não conformidade cadastrada e selecionada!")
                st.rerun()
                    
    with col_cancelar:
        if st.button("Cancelar", use_container_width=True, key=f"btn_cancel_add_custom_nc_{prefix_key}"):
            st.rerun()


@st.dialog("Editar Dados Registrados", width="large")
def editar_registros_relatorio_modal(aba_inicial="fisc", is_monitoring=False, term_fisc="Fiscalização", term_fisc_prep="da Fiscalização", term_fisc_plural="Fiscalizações"):
    if not st.session_state.temp_fiscalizacoes and not st.session_state.temp_nc:
        st.info("Nenhum dado cadastrado para edição.")
        if st.button("Fechar", use_container_width=True, key="btn_close_edit_modal_empty"):
            st.rerun()
        return

    tipo = st.session_state.get("tipo_relatorio", "CRA")
    is_mon = is_monitoring or st.session_state.get("categoria_relatorio", "") == "Monitoramento"

    st.write(f"Edite as informações registradas para **{tipo} ({'Monitoramento' if is_mon else 'Fiscalização'})**.")

    label_nc_tab = "⚠️ Não Conformidades" if tipo in ["CRC", "SOCICAM"] or is_mon else "⚠️ Não Conformidades e Pontos de Atenção"
    tab_fisc, tab_nc = st.tabs([f"📌 {term_fisc_plural}", label_nc_tab])

    # -------------------------------------------------------------
    # TAB 1: EDITAR FISCALIZAÇÃO / MONITORAMENTO
    # -------------------------------------------------------------
    with tab_fisc:
        if not st.session_state.temp_fiscalizacoes:
            st.info(f"Nenhum{'' if is_mon else 'a'} {term_fisc.lower()} cadastrado(a).")
        else:
            options_fisc = [f["ID da Fiscalização"] for f in st.session_state.temp_fiscalizacoes]
            sel_id_fisc = st.selectbox(
                f"Selecione o ID {term_fisc_prep} para editar",
                options_fisc,
                key="edit_modal_sel_fisc_id"
            )
            
            fisc_data = next((f for f in st.session_state.temp_fiscalizacoes if f["ID da Fiscalização"] == sel_id_fisc), None)
            
            if fisc_data:
                st.markdown("---")
                col_id, col_data = st.columns(2)
                with col_id:
                    novo_id = st.text_input(f"ID {term_fisc_prep}", value=str(fisc_data.get("ID da Fiscalização", "")), key="edit_fisc_id_input")
                with col_data:
                    nova_data = st.text_input("Data", value=str(fisc_data.get("Data", "")), key="edit_fisc_data_input")
                
                # Campos específicos por tipo
                if tipo == "CRA":
                    col_h, col_c, col_l = st.columns(3)
                    with col_h:
                        nova_hora = st.text_input("Hora", value=str(fisc_data.get("Hora", "")), key="edit_fisc_hora_input")
                    with col_c:
                        nova_cidade = st.text_input("Cidade", value=str(fisc_data.get("Cidade", "")), key="edit_fisc_cidade_input")
                    with col_l:
                        novo_local = st.text_input("Local", value=str(fisc_data.get("Local", "")), key="edit_fisc_local_input")
                elif tipo == "SOCICAM":
                    novo_local = st.text_input("Local", value=str(fisc_data.get("Local", "")), key="edit_fisc_local_input")
                    nova_hora = ""
                    nova_cidade = ""
                else:  # CRC
                    novo_local = "Sistema Viário do Paiva"
                    nova_hora = ""
                    nova_cidade = ""
                
                col_resp, col_coord = st.columns(2)
                with col_resp:
                    novos_responsaveis = st.text_input("Pessoal Responsável", value=str(fisc_data.get("Pessoal Responsável", "")), key="edit_fisc_resp_input")
                with col_coord:
                    novo_coordenador = st.text_input("Coordenador", value=str(fisc_data.get("Coordenador", "")), key="edit_fisc_coord_input")
                
                novo_periodo = st.text_input("Período", value=str(fisc_data.get("Período", "")), key="edit_fisc_periodo_input")

                if st.button("💾 Salvar Alterações na Fiscalização", type="primary", use_container_width=True, key="btn_save_fisc_edit"):
                    old_id = fisc_data["ID da Fiscalização"]
                    novo_id_clean = novo_id.strip()
                    
                    if not novo_id_clean:
                        st.error(f"O ID {term_fisc_prep} não pode ser vazio.")
                    elif tipo in ["CRA", "SOCICAM"] and not novo_local.strip():
                        st.error("O campo 'Local' é obrigatório.")
                    else:
                        outros_ids = [f["ID da Fiscalização"].strip() for f in st.session_state.temp_fiscalizacoes if f["ID da Fiscalização"] != old_id]
                        if novo_id_clean in outros_ids:
                            st.error(f"O ID '{novo_id_clean}' já existe em outro registro. Escolha um ID único.")
                        else:
                            fisc_data["ID da Fiscalização"] = novo_id_clean
                            fisc_data["Data"] = nova_data
                            fisc_data["Hora"] = nova_hora
                            fisc_data["Cidade"] = nova_cidade
                            fisc_data["Local"] = novo_local.strip() if isinstance(novo_local, str) else novo_local
                            fisc_data["Pessoal Responsável"] = novos_responsaveis
                            fisc_data["Coordenador"] = novo_coordenador
                            fisc_data["Período"] = novo_periodo
                            
                            if novo_id_clean != old_id:
                                for nc in st.session_state.temp_nc:
                                    if nc.get("ID da Fiscalização") == old_id:
                                        nc["ID da Fiscalização"] = novo_id_clean
                            
                            st.session_state.relatorios_preenchimento_data = []
                            if "planilha_download_bytes" in st.session_state:
                                del st.session_state.planilha_download_bytes
                                
                            st.success(f"Alterações salvas com sucesso para o ID '{novo_id_clean}'!")
                            st.rerun()

    # -------------------------------------------------------------
    # TAB 2: EDITAR NÃO CONFORMIDADE / PONTO DE ATENÇÃO
    # -------------------------------------------------------------
    with tab_nc:
        if not st.session_state.temp_nc:
            st.info("Nenhum registro cadastrado.")
        else:
            ids_com_nc = sorted(list(set(nc["ID da Fiscalização"] for nc in st.session_state.temp_nc if "ID da Fiscalização" in nc)))
            if not ids_com_nc:
                st.info("Nenhum registro encontrado.")
            else:
                sel_fisc_for_nc = st.selectbox(
                    f"Filtrar por ID {term_fisc_prep}",
                    ids_com_nc,
                    key="edit_modal_sel_id_for_nc"
                )
                
                ncs_filtradas = [nc for nc in st.session_state.temp_nc if nc.get("ID da Fiscalização") == sel_fisc_for_nc]
                
                if not ncs_filtradas:
                    st.info(f"Nenhum item vinculado ao ID '{sel_fisc_for_nc}'.")
                else:
                    def nc_label(nc_item):
                        desc = nc_item.get("Não Conformidade") or nc_item.get("Ponto de Atenção") or nc_item.get("Identificação") or "Sem Descrição"
                        if isinstance(desc, list):
                            desc = ", ".join(desc)
                        desc_trunc = str(desc)[:50] + ("..." if len(str(desc)) > 50 else "")
                        tipo_label = "PA" if nc_item.get("Ponto de Atenção") and not nc_item.get("Não Conformidade") else "NC"
                        return f"Item nº {nc_item.get('Nº', 1)} [{tipo_label}] - {desc_trunc}"
                    
                    idx_nc_sel = st.selectbox(
                        "Selecione o item para editar",
                        range(len(ncs_filtradas)),
                        format_func=lambda i: nc_label(ncs_filtradas[i]),
                        key="edit_modal_sel_nc_item"
                    )
                    
                    nc_target = ncs_filtradas[idx_nc_sel]
                    
                    st.markdown("---")
                    
                    # 1. CRC ou SOCICAM em Monitoramento:
                    if tipo in ["CRC", "SOCICAM"] and is_mon:
                        situacoes_opts = ["Pendente", "Parcialmente Sanada", "Sanada"]
                        sit_atual = str(nc_target.get("Situação", "Pendente"))
                        sit_idx = situacoes_opts.index(sit_atual) if sit_atual in situacoes_opts else 0
                        edit_situacao = st.selectbox("Situação", situacoes_opts, index=sit_idx, key="edit_nc_situacao")
                        
                        pos_label = "INFORMAÇÃO SOCICAM" if tipo == "SOCICAM" else "POSICIONAMENTO CRC"
                        edit_determinacao = st.text_area(pos_label, value=str(nc_target.get("Determinação", "")), height=110, key="edit_nc_determinacao")
                        edit_observacoes = st.text_area("CONSTATAÇÃO", value=str(nc_target.get("Observações", "")), height=110, key="edit_nc_observacoes")
                        edit_analise_arpe = st.text_area("ANÁLISE ARPE", value=str(nc_target.get("Análise ARPE", "")), height=110, key="edit_nc_analise_arpe")

                        if st.button("💾 Salvar Alterações", type="primary", use_container_width=True, key="btn_save_nc_edit"):
                            nc_target["Situação"] = edit_situacao
                            nc_target["Determinação"] = edit_determinacao
                            nc_target["Observações"] = edit_observacoes
                            nc_target["Análise ARPE"] = edit_analise_arpe
                            st.session_state.relatorios_preenchimento_data = []
                            if "planilha_download_bytes" in st.session_state:
                                del st.session_state.planilha_download_bytes
                            st.success(f"Alterações salvas para o item nº {nc_target.get('Nº', 1)}!")
                            st.rerun()

                    # 2. CRA em Monitoramento:
                    elif tipo == "CRA" and is_mon:
                        c_pista, c_trecho = st.columns(2)
                        with c_pista:
                            edit_pista = st.text_input("Pista", value=str(nc_target.get("Pista", "")), key="edit_nc_pista")
                        with c_trecho:
                            edit_trecho = st.text_input("Trecho", value=str(nc_target.get("Trecho", "")), key="edit_nc_trecho")
                        
                        situacoes_opts = ["Pendente", "Parcialmente Sanada", "Sanada"]
                        sit_atual = str(nc_target.get("Situação", "Pendente"))
                        sit_idx = situacoes_opts.index(sit_atual) if sit_atual in situacoes_opts else 0
                        edit_situacao = st.selectbox("Situação", situacoes_opts, index=sit_idx, key="edit_nc_situacao")
                        
                        obs_atual = nc_target.get("Observações", nc_target.get("Legenda da Foto", ""))
                        edit_observacoes = st.text_area("Legenda da Foto Atual", value=str(obs_atual), height=80, key="edit_nc_observacoes")

                        c_ident, c_dir = st.columns(2)
                        with c_ident:
                            edit_ident = st.text_input("Identificação", value=str(nc_target.get("Identificação", "")), key="edit_nc_ident")
                        with c_dir:
                            edit_direcao = st.text_input("Direção (faixa)", value=str(nc_target.get("Direção (faixa)", "")), key="edit_nc_direcao")

                        edit_fundamento = st.text_area("Fundamento da Infração", value=str(nc_target.get("Fundamento da infração", "")), height=80, key="edit_nc_fundamento")
                        edit_determinacao = st.text_area("Determinação", value=str(nc_target.get("Determinação", "")), height=80, key="edit_nc_determinacao")

                        if st.button("💾 Salvar Alterações", type="primary", use_container_width=True, key="btn_save_nc_edit"):
                            nc_target["Pista"] = edit_pista
                            nc_target["Trecho"] = edit_trecho
                            nc_target["Situação"] = edit_situacao
                            nc_target["Observações"] = edit_observacoes
                            if "Legenda da Foto" in nc_target:
                                nc_target["Legenda da Foto"] = edit_observacoes
                            nc_target["Identificação"] = edit_ident
                            nc_target["Direção (faixa)"] = edit_direcao
                            nc_target["Fundamento da infração"] = edit_fundamento
                            nc_target["Determinação"] = edit_determinacao
                            st.session_state.relatorios_preenchimento_data = []
                            if "planilha_download_bytes" in st.session_state:
                                del st.session_state.planilha_download_bytes
                            st.success(f"Alterações salvas para o item nº {nc_target.get('Nº', 1)}!")
                            st.rerun()

                    # 3. CRA em Fiscalização:
                    elif tipo == "CRA" and not is_mon:
                        c_pista, c_trecho = st.columns(2)
                        with c_pista:
                            edit_pista = st.text_input("Pista", value=str(nc_target.get("Pista", "")), key="edit_nc_pista")
                        with c_trecho:
                            edit_trecho = st.text_input("Trecho", value=str(nc_target.get("Trecho", "")), key="edit_nc_trecho")

                        is_pa = bool(nc_target.get("Ponto de Atenção")) and not bool(nc_target.get("Não Conformidade"))
                        if is_pa:
                            pa_val_str = nc_target.get("Ponto de Atenção", "")
                            if isinstance(pa_val_str, list):
                                pa_val_str = ", ".join(pa_val_str)
                            edit_pa_desc = st.text_area("Ponto de Atenção", value=str(pa_val_str), height=90, key="edit_pa_desc_input")
                            edit_nc_desc = ""
                        else:
                            nc_val_str = nc_target.get("Não Conformidade", "")
                            if isinstance(nc_val_str, list):
                                nc_val_str = ", ".join(nc_val_str)
                            edit_nc_desc = st.text_area("Não Conformidade", value=str(nc_val_str), height=90, key="edit_nc_desc_input")
                            edit_pa_desc = ""

                        obs_atual = nc_target.get("Observações", nc_target.get("Legenda da Foto", ""))
                        edit_observacoes = st.text_area("Observações", value=str(obs_atual), height=80, key="edit_nc_observacoes")

                        c_ident, c_dir = st.columns(2)
                        with c_ident:
                            edit_ident = st.text_input("Identificação", value=str(nc_target.get("Identificação", "")), key="edit_nc_ident")
                        with c_dir:
                            edit_direcao = st.text_input("Direção (faixa)", value=str(nc_target.get("Direção (faixa)", "")), key="edit_nc_direcao")

                        edit_fundamento = st.text_area("Fundamento da Infração", value=str(nc_target.get("Fundamento da infração", "")), height=80, key="edit_nc_fundamento")
                        edit_determinacao = st.text_area("Determinação", value=str(nc_target.get("Determinação", "")), height=80, key="edit_nc_determinacao")

                        if st.button("💾 Salvar Alterações", type="primary", use_container_width=True, key="btn_save_nc_edit"):
                            nc_target["Pista"] = edit_pista
                            nc_target["Trecho"] = edit_trecho
                            if is_pa:
                                nc_target["Ponto de Atenção"] = edit_pa_desc
                            else:
                                nc_target["Não Conformidade"] = edit_nc_desc
                            nc_target["Observações"] = edit_observacoes
                            if "Legenda da Foto" in nc_target:
                                nc_target["Legenda da Foto"] = edit_observacoes
                            nc_target["Identificação"] = edit_ident
                            nc_target["Direção (faixa)"] = edit_direcao
                            nc_target["Fundamento da infração"] = edit_fundamento
                            nc_target["Determinação"] = edit_determinacao
                            st.session_state.relatorios_preenchimento_data = []
                            if "planilha_download_bytes" in st.session_state:
                                del st.session_state.planilha_download_bytes
                            st.success(f"Alterações salvas para o item nº {nc_target.get('Nº', 1)}!")
                            st.rerun()

                    # 4. CRC ou SOCICAM em Fiscalização:
                    else:
                        nc_val_str = nc_target.get("Não Conformidade", "")
                        if isinstance(nc_val_str, list):
                            nc_val_str = ", ".join(nc_val_str)
                        edit_nc_desc = st.text_area("Não Conformidade", value=str(nc_val_str), height=90, key="edit_nc_desc_input")

                        obs_atual = nc_target.get("Observações", nc_target.get("Legenda da Foto", ""))
                        edit_observacoes = st.text_area("Observações", value=str(obs_atual), height=80, key="edit_nc_observacoes")

                        edit_ident = st.text_input("Identificação", value=str(nc_target.get("Identificação", "")), key="edit_nc_ident")
                        edit_fundamento = st.text_area("Fundamento da Infração", value=str(nc_target.get("Fundamento da infração", "")), height=80, key="edit_nc_fundamento")
                        edit_determinacao = st.text_area("Determinação", value=str(nc_target.get("Determinação", "")), height=80, key="edit_nc_determinacao")

                        if st.button("💾 Salvar Alterações", type="primary", use_container_width=True, key="btn_save_nc_edit"):
                            nc_target["Não Conformidade"] = edit_nc_desc
                            nc_target["Observações"] = edit_observacoes
                            if "Legenda da Foto" in nc_target:
                                nc_target["Legenda da Foto"] = edit_observacoes
                            nc_target["Identificação"] = edit_ident
                            nc_target["Fundamento da infração"] = edit_fundamento
                            nc_target["Determinação"] = edit_determinacao
                            st.session_state.relatorios_preenchimento_data = []
                            if "planilha_download_bytes" in st.session_state:
                                del st.session_state.planilha_download_bytes
                            st.success(f"Alterações salvas para o item nº {nc_target.get('Nº', 1)}!")
                            st.rerun()


