# -*- coding: utf-8 -*-
import streamlit as st
from sections.quadros.quadros import MAP_SIGLAS, expandir_siglas
from ui.state import sincronizar_opcoes_nc, BASE_NC_OPTIONS, salvar_estado_relatorio_ativo
from utils import (
    calcular_codificacao_cra,
    obter_proximo_numero_sequencial_cra,
)
from ui.dialogs.management_dialogs import adicionar_nc_personalizada_modal

@st.dialog("Confirmar Exclusão de Itens", icon=":material/delete:")
def confirmar_exclusao_nc_modal(nc_keys):
    st.write("Você tem certeza que deseja excluir os seguintes itens selecionados?")
    for id_fisc, num in nc_keys:
        st.write(f"- **ID {id_fisc} - Item nº {num}**")
    st.warning("Esta ação não pode ser desfeita.")
    
    col_sim, col_nao = st.columns(2)
    with col_sim:
        if st.button("Sim, Excluir", icon=":material/delete:", type="primary", use_container_width=True, key="btn_confirm_nc_del"):
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
            salvar_estado_relatorio_ativo()
            st.session_state.pending_toast = ":green[:material/check_circle:] Não Conformidades selecionadas excluídas com sucesso!"
            st.rerun()
    with col_nao:
        if st.button("Cancelar", icon=":material/close:", use_container_width=True, key="btn_cancel_nc_del"):
            st.rerun()




@st.dialog("Atenção: Limpar Registros", icon=":material/warning:")
def confirmar_limpar_registros_modal(tipo_relatorio: str, categoria_relatorio: str):
    """
    Modal de confirmação para limpar apenas os registros do tipo e categoria ativos.
    Exige tempo de segurança de 5 segundos para leitura antes de habilitar o botão vermelho de exclusão.
    """
    import time
    from services.session_cache_service import limpar_sessao_local
    from services.media_storage_service import limpar_estado_completo_relatorio_disco

    st.markdown(
        f"Você está prestes a resetar e **apagar todos os registros** de:<br/>"
        f"<h3 style='color: #b91c1c; margin: 4px 0;'>{tipo_relatorio} — {categoria_relatorio}</h3>"
        f"Ao confirmar, todos os dados salvos deste relatório específico serão **perdidos definitivamente**.",
        unsafe_allow_html=True
    )
    st.write("")

    # Gerenciamento do temporizador de 5 segundos
    now = time.time()
    if "_clear_modal_start_time" not in st.session_state:
        st.session_state._clear_modal_start_time = now

    elapsed = now - st.session_state._clear_modal_start_time
    tempo_restante = max(0, int(5 - elapsed))

    placeholder_info = st.empty()
    placeholder_botoes = st.empty()

    if tempo_restante > 0:
        placeholder_info.warning(
            f":material/timer: Por segurança, leia as instruções acima. "
            f"O botão de exclusão será liberado em **{tempo_restante}s**..."
        )
        with placeholder_botoes.container():
            col_del, col_canc = st.columns(2)
            with col_del:
                st.button(
                    f"Excluir Tudo ({tempo_restante}s)",
                    icon=":material/delete_forever:",
                    disabled=True,
                    use_container_width=True,
                    key="btn_clear_confirm_disabled"
                )
            with col_canc:
                if st.button("Cancelar", icon=":material/close:", use_container_width=True, key="btn_clear_cancel_wait"):
                    if "_clear_modal_start_time" in st.session_state:
                        del st.session_state._clear_modal_start_time
                    st.session_state.show_confirm_limpar_registros = False
                    st.rerun()

        # Aguarda 1 segundo e força o rerun para atualizar o contador
        time.sleep(1)
        st.rerun()
    else:
        placeholder_info.error(
            ":material/report: **Tempo de segurança concluído.** "
            "A exclusão afetará única e exclusivamente este relatório."
        )
        with placeholder_botoes.container():
            col_del, col_canc = st.columns(2)
            with col_del:
                with st.container(key="btn_container_perigo_excluir"):
                    if st.button(
                        "Sim, Excluir Definitivamente",
                        icon=":material/delete_forever:",
                        type="primary",
                        use_container_width=True,
                        key="btn_clear_confirm_action"
                    ):
                        # Reseta as listas do relatório ativo
                        st.session_state.temp_nc = []
                        st.session_state.temp_fiscalizacoes = []
                        st.session_state.relatorios_preenchimento_data = []
                        if "planilha_download_bytes" in st.session_state:
                            del st.session_state.planilha_download_bytes
                        st.session_state.photos_uploader_version += 1
                        st.session_state.fill_photos = []
                        if "carousel_index" in st.session_state:
                            st.session_state.carousel_index = 0
                        st.session_state.pista_persistida = ""
                        st.session_state.trecho_persistido = ""
                        st.session_state.codificacao_persistida = ""
                        st.session_state.fundamento_persistido = ""
                        st.session_state.determinacao_persistida = ""
                        st.session_state.faixa_persistida = ""
                        st.session_state.manual_relacao_map = {}
                        st.session_state._fotos_restauradas = []
                        st.session_state._uploader_fotos_anteriores = []
                        st.session_state._planilha_salva_local = None
                        st.session_state._mon_doc_salvo_local = None
                        if "uploaded_planilha_elegibilidade" in st.session_state:
                            st.session_state.uploaded_planilha_elegibilidade = None
                        if "uploaded_mon_anterior" in st.session_state:
                            st.session_state.uploaded_mon_anterior = None
                        st.session_state.old_photos_to_match = []

                        # Apaga o arquivo de cache e mídias correspondentes no disco local do usuário
                        limpar_estado_completo_relatorio_disco(tipo_relatorio, categoria_relatorio)

                        # Enfileira remoção das subpastas midia e estado na máquina física do usuário
                        from ui.state import enfileirar_acao_fs
                        enfileirar_acao_fs({
                            "action": "CLEAR",
                            "tipo": tipo_relatorio,
                            "cat": categoria_relatorio,
                        })

                        if "_clear_modal_start_time" in st.session_state:
                            del st.session_state._clear_modal_start_time
                        st.session_state.show_confirm_limpar_registros = False
                        st.session_state.pending_toast = f":green[:material/check_circle:] Registros de {tipo_relatorio} ({categoria_relatorio}) resetados com sucesso!"
                        st.rerun()
            with col_canc:
                if st.button("Cancelar", icon=":material/close:", use_container_width=True, key="btn_clear_cancel_done"):
                    if "_clear_modal_start_time" in st.session_state:
                        del st.session_state._clear_modal_start_time
                    st.session_state.show_confirm_limpar_registros = False
                    st.rerun()





@st.dialog("Atenção: Limpar Registros e Estado", icon=":material/warning:")
def confirmar_reset_estado_modal(tipo_relatorio: str, categoria_relatorio: str):
    """
    Modal unificado nativo para resetar permanentemente o estado, fotos e mídias
    do relatório ativo tanto no navegador quanto na máquina física do usuário.
    """
    from ui.state import resetar_estado_sessao_relatorio_ativo

    st.markdown(
        f"Você está prestes a **resetar o estado completo** de:<br/>"
        f"<h3 style='color: #b91c1c; margin: 4px 0;'>{tipo_relatorio} — {categoria_relatorio}</h3>"
        f"Esta ação apagará permanentemente o **arquivo de estado**, todas as **fotos** e **documentos auxiliares** "
        f"salvos desta modalidade, tanto no navegador quanto na pasta local física.",
        unsafe_allow_html=True
    )
    st.write("")

    col_sim, col_nao = st.columns(2)
    with col_sim:
        with st.container(key="btn_container_perigo_excluir"):
            if st.button("Sim, Limpar Tudo", icon=":material/delete_forever:", type="primary", use_container_width=True, key="btn_confirm_reset_estado_action"):
                resetar_estado_sessao_relatorio_ativo(tipo_relatorio, categoria_relatorio)
                st.session_state.show_confirm_reset_estado = False
                st.session_state.pending_toast = {
                    "msg": f"Estado de {tipo_relatorio} ({categoria_relatorio}) resetado com sucesso!",
                    "icon": ":material/check_circle:"
                }
                st.rerun()
    with col_nao:
        if st.button("Cancelar", icon=":material/close:", use_container_width=True, key="btn_cancel_reset_estado"):
            st.session_state.show_confirm_reset_estado = False
            st.rerun()



def formatar_sigla_nc(sigla: str) -> str:
    """Retorna a sigla formatada com a sua descrição completa para exibição no seletor."""
    if not sigla:
        return ""
    sigla_clean = str(sigla).strip()
    desc = MAP_SIGLAS.get(sigla_clean)
    if not desc:
        for item in st.session_state.get("custom_ncs", []) + st.session_state.get("custom_ncs_socicam", []):
            if item.get("sigla") == sigla_clean and item.get("descricao"):
                desc = item.get("descricao")
                break
    if desc and desc.lower() != sigla_clean.lower():
        return f"{sigla_clean} — {desc}"
    return sigla_clean




def obter_lista_siglas_atuais(val) -> list:
    """Converte o valor salvo (string ou lista) em uma lista limpa de siglas/opções."""
    if not val:
        return []
    if isinstance(val, list):
        return [str(x).strip() for x in val if str(x).strip()]
    return [str(x).strip() for x in str(val).split(",") if str(x).strip()]




@st.dialog("Editar Dados Registrados", width="large", icon=":material/edit:")
def editar_registros_relatorio_modal(aba_inicial="fisc", is_monitoring=False, term_fisc="Fiscalização", term_fisc_prep="da Fiscalização", term_fisc_plural="Fiscalizações"):
    if not st.session_state.temp_fiscalizacoes and not st.session_state.temp_nc:
        st.info("Nenhum dado cadastrado para edição.")
        if st.button("Fechar", icon=":material/close:", use_container_width=True, key="btn_close_edit_modal_empty"):
            st.rerun()
        return

    tipo = st.session_state.get("tipo_relatorio", "CRA")
    is_mon = is_monitoring or st.session_state.get("categoria_relatorio", "") == "Monitoramento"

    st.write(f"Edite as informações registradas para **{tipo} ({'Monitoramento' if is_mon else 'Fiscalização'})**.")

    label_nc_tab = "Não Conformidades" if tipo in ["CRC", "SOCICAM"] or is_mon else "Não Conformidades e Pontos de Atenção"
    tab_fisc, tab_nc = st.tabs([f":material/location_on: {term_fisc_plural}", f":material/warning: {label_nc_tab}"])

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
                fisc_version = st.session_state.get("fisc_edit_version", 0)
                f_key = f"fisc_edit_{sel_id_fisc}_{fisc_version}"

                col_id, col_data = st.columns(2)
                with col_id:
                    novo_id = st.text_input(f"ID {term_fisc_prep}", value=str(fisc_data.get("ID da Fiscalização", "")), key=f"{f_key}_id")
                with col_data:
                    from datetime import datetime
                    data_str = str(fisc_data.get("Data", ""))
                    try:
                        data_val = datetime.strptime(data_str, "%d/%m/%Y").date() if data_str else None
                    except ValueError:
                        data_val = None
                    if data_val is None:
                        data_val = "today"
                    nova_data_obj = st.date_input("Data", value=data_val, format="DD/MM/YYYY", key=f"{f_key}_data")
                    nova_data = nova_data_obj.strftime("%d/%m/%Y") if nova_data_obj else ""
                
                # Campos específicos por tipo
                if tipo == "CRA":
                    col_h, col_c, col_l = st.columns(3)
                    with col_h:
                        nova_hora = st.text_input("Hora", value=str(fisc_data.get("Hora", "")), key=f"{f_key}_hora")
                    with col_c:
                        nova_cidade = st.text_input("Cidade", value=str(fisc_data.get("Cidade", "")), key=f"{f_key}_cidade")
                    with col_l:
                        val_cra = str(fisc_data.get("Local", ""))
                        if not val_cra:
                            val_cra = "Rota do Atlântico"
                        novo_local = st.text_input("Local", value=val_cra, key=f"{f_key}_local")
                elif tipo == "SOCICAM":
                    opts = ["Garanhuns", "Arcoverde", "Serra Talhada", "Petrolina", "Caruaru", "TIP Recife"]
                    val_socicam = str(fisc_data.get("Local", ""))
                    if val_socicam not in opts:
                        val_socicam = opts[0] if not val_socicam else val_socicam
                        if val_socicam not in opts:
                            opts.append(val_socicam)
                    novo_local = st.selectbox("Local", options=opts, index=opts.index(val_socicam), key=f"{f_key}_local")
                    nova_hora = ""
                    nova_cidade = ""
                else:  # CRC
                    novo_local = "Sistema Viário do Paiva"
                    nova_hora = ""
                    nova_cidade = ""
                
                col_resp, col_coord = st.columns(2)
                with col_resp:
                    novos_responsaveis = st.text_input("Pessoal Responsável", value=str(fisc_data.get("Pessoal Responsável", "")), key=f"{f_key}_resp")
                with col_coord:
                    novo_coordenador = st.text_input("Coordenador", value=str(fisc_data.get("Coordenador", "")), key=f"{f_key}_coord")
                
                novo_periodo = st.text_input("Período", value=str(fisc_data.get("Período", "")), key=f"{f_key}_periodo")

                if st.button("Salvar Alterações na Fiscalização", icon=":material/save:", type="primary", use_container_width=True, key=f"{f_key}_btn_save"):
                    old_id = fisc_data["ID da Fiscalização"]
                    novo_id_clean = novo_id.strip()
                    novo_local_clean = str(novo_local).strip() if novo_local else ""
                    if tipo == "CRA" and not novo_local_clean:
                        novo_local_clean = "Rota do Atlântico"
                    
                    if not novo_id_clean:
                        st.toast(f":red[:material/error:] O ID {term_fisc_prep} não pode ser vazio.")
                    elif tipo == "SOCICAM" and not novo_local_clean:
                        st.toast(":red[:material/error:] O campo 'Local' é obrigatório.")
                    else:
                        outros_ids = [f["ID da Fiscalização"].strip() for f in st.session_state.temp_fiscalizacoes if f["ID da Fiscalização"] != old_id]
                        if novo_id_clean in outros_ids:
                            st.toast(f":red[:material/error:] O ID '{novo_id_clean}' já existe em outro registro. Escolha um ID único.")
                        else:
                            fisc_data["ID da Fiscalização"] = novo_id_clean
                            fisc_data["Data"] = nova_data
                            fisc_data["Hora"] = nova_hora
                            fisc_data["Cidade"] = nova_cidade
                            fisc_data["Local"] = novo_local_clean
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
                            
                            salvar_estado_relatorio_ativo()
                            st.session_state["fisc_edit_version"] = fisc_version + 1
                            st.session_state.pending_toast = f":green[:material/check_circle:] Alterações salvas com sucesso para o ID '{novo_id_clean}'!"
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
                        key=f"edit_modal_sel_nc_item_{sel_fisc_for_nc}"
                    )
                    
                    nc_target = ncs_filtradas[idx_nc_sel]
                    nc_version = st.session_state.get("nc_edit_version", 0)
                    nc_num_val = nc_target.get("Nº", idx_nc_sel + 1)
                    nc_key_prefix = f"nc_edit_{sel_fisc_for_nc}_{nc_num_val}_{idx_nc_sel}_{nc_version}"
                    
                    st.markdown("---")
                    
                    # 1. CRC ou SOCICAM em Monitoramento:
                    if tipo in ["CRC", "SOCICAM"] and is_mon:
                        situacoes_opts = ["Pendente", "Parcialmente Sanada", "Sanada"]
                        sit_atual = str(nc_target.get("Situação", "Pendente"))
                        sit_idx = situacoes_opts.index(sit_atual) if sit_atual in situacoes_opts else 0
                        edit_situacao = st.selectbox("Situação", situacoes_opts, index=sit_idx, key=f"{nc_key_prefix}_situacao")
                        
                        pos_label = "INFORMAÇÃO SOCICAM" if tipo == "SOCICAM" else "POSICIONAMENTO CRC"
                        edit_determinacao = st.text_area(pos_label, value=str(nc_target.get("Determinação", "")), height=110, key=f"{nc_key_prefix}_determinacao")
                        edit_observacoes = st.text_area("CONSTATAÇÃO", value=str(nc_target.get("Observações", "")), height=110, key=f"{nc_key_prefix}_observacoes")
                        edit_analise_arpe = st.text_area("ANÁLISE ARPE", value=str(nc_target.get("Análise ARPE", "")), height=110, key=f"{nc_key_prefix}_analise_arpe")

                        if st.button("Salvar Alterações", icon=":material/save:", type="primary", use_container_width=True, key=f"{nc_key_prefix}_btn_save"):
                            nc_target["Situação"] = edit_situacao
                            nc_target["Determinação"] = edit_determinacao
                            nc_target["Observações"] = edit_observacoes
                            nc_target["Análise ARPE"] = edit_analise_arpe
                            st.session_state.relatorios_preenchimento_data = []
                            if "planilha_download_bytes" in st.session_state:
                                del st.session_state.planilha_download_bytes
                            salvar_estado_relatorio_ativo()
                            st.session_state["nc_edit_version"] = nc_version + 1
                            st.session_state.pending_toast = f":green[:material/check_circle:] Alterações salvas para o item nº {nc_target.get('Nº', 1)}!"
                            st.rerun()

                    # 2. CRA em Monitoramento:
                    elif tipo == "CRA" and is_mon:
                        c_pista, c_trecho = st.columns(2)
                        with c_pista:
                            edit_pista = st.text_input("Pista", value=str(nc_target.get("Pista", "")), key=f"{nc_key_prefix}_pista")
                        with c_trecho:
                            edit_trecho = st.text_input("Trecho", value=str(nc_target.get("Trecho", "")), key=f"{nc_key_prefix}_trecho")
                        
                        situacoes_opts = ["Pendente", "Parcialmente Sanada", "Sanada"]
                        sit_atual = str(nc_target.get("Situação", "Pendente"))
                        sit_idx = situacoes_opts.index(sit_atual) if sit_atual in situacoes_opts else 0
                        edit_situacao = st.selectbox("Situação", situacoes_opts, index=sit_idx, key=f"{nc_key_prefix}_situacao")

                        options_base = list(st.session_state.nc_options)
                        raw_nc = nc_target.get("Não Conformidade", "")
                        curr_selected = obter_lista_siglas_atuais(raw_nc)
                        for s in curr_selected:
                            if s and s not in options_base:
                                options_base.append(s)

                        col_sel, col_add = st.columns([10.5, 1.5])
                        with col_sel:
                            edit_selected_siglas = st.multiselect(
                                "Não Conformidade (clique para abrir e selecionar)",
                                options=options_base,
                                default=curr_selected,
                                format_func=formatar_sigla_nc,
                                placeholder="Clique para abrir e marcar/desmarcar...",
                                key=f"{nc_key_prefix}_nc_multiselect"
                            )
                        with col_add:
                            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                            if st.button("", icon=":material/add:", key=f"{nc_key_prefix}_btn_custom_nc", help="Adicionar Não Conformidade Personalizada"):
                                adicionar_nc_personalizada_modal(f"{nc_key_prefix}_nc_multiselect", is_socicam=False)

                        edit_nc_desc = ", ".join(edit_selected_siglas)
                        
                        obs_atual = nc_target.get("Observações", nc_target.get("Legenda da Foto", ""))
                        edit_observacoes = st.text_area("Legenda da Foto Atual", value=str(obs_atual), height=80, key=f"{nc_key_prefix}_observacoes")

                        if st.session_state.get("tipo_relatorio", "CRA") == "CRA":
                            dir_val = nc_target.get("Direção (faixa)", "")
                            dir_val_str = "" if (dir_val is None or str(dir_val).strip().lower() in ["nan", "none", "null"]) else str(dir_val).strip()
                            sigla_curr = converter_faixa_para_sigla(dir_val_str)
                            if sigla_curr == "FED" or dir_val_str.upper() == "FED":
                                opts_dir = ["FED", "Direita", "Esquerda"]
                                idx_dir = 0
                            elif sigla_curr == "FE":
                                opts_dir = ["Direita", "Esquerda"]
                                idx_dir = 1
                            else:
                                opts_dir = ["Direita", "Esquerda"]
                                idx_dir = 0
                            edit_direcao = st.selectbox(
                                "Direção (faixa)",
                                options=opts_dir,
                                index=idx_dir,
                                key=f"{nc_key_prefix}_direcao"
                            )
                        else:
                            edit_direcao = ""

                        edit_fundamento = st.text_area("Fundamento da Infração", value=str(nc_target.get("Fundamento da infração", "")), height=80, key=f"{nc_key_prefix}_fundamento")
                        edit_determinacao = st.text_area("Determinação", value=str(nc_target.get("Determinação", "")), height=80, key=f"{nc_key_prefix}_determinacao")

                        if st.button("Salvar Alterações", icon=":material/save:", type="primary", use_container_width=True, key=f"{nc_key_prefix}_btn_save"):
                            nc_target["Pista"] = edit_pista
                            nc_target["Trecho"] = edit_trecho
                            nc_target["Situação"] = edit_situacao
                            if edit_nc_desc:
                                nc_target["Não Conformidade"] = edit_nc_desc
                            nc_target["Observações"] = edit_observacoes
                            if "Legenda da Foto" in nc_target:
                                nc_target["Legenda da Foto"] = edit_observacoes
                            nc_target["Identificação"] = str(nc_target.get("Identificação", "")).strip() or edit_nc_desc
                            nc_target["Direção (faixa)"] = edit_direcao
                            nc_target["Fundamento da infração"] = edit_fundamento
                            nc_target["Determinação"] = edit_determinacao
                            st.session_state.relatorios_preenchimento_data = []
                            if "planilha_download_bytes" in st.session_state:
                                del st.session_state.planilha_download_bytes
                            salvar_estado_relatorio_ativo()
                            st.session_state["nc_edit_version"] = nc_version + 1
                            st.session_state.pending_toast = f":green[:material/check_circle:] Alterações salvas para o item nº {nc_target.get('Nº', 1)}!"
                            st.rerun()

                    # 3. CRA em Fiscalização:
                    elif tipo == "CRA" and not is_mon:
                        c_pista, c_cod = st.columns(2)
                        with c_pista:
                            edit_pista = st.text_input("Pista", value=str(nc_target.get("Pista", "")), key=f"{nc_key_prefix}_pista")
                        with c_cod:
                            edit_codificacao = st.text_input("Codificação", value=str(nc_target.get("Codificação") or nc_target.get("Trecho", "")), key=f"{nc_key_prefix}_codificacao")

                        init_is_pa = bool(nc_target.get("Ponto de Atenção")) and not bool(nc_target.get("Não Conformidade"))
                        tipo_reg_edit = st.radio(
                            "Tipo de Registro",
                            ["Não Conformidade", "Ponto de Atenção"],
                            index=1 if init_is_pa else 0,
                            horizontal=True,
                            key=f"{nc_key_prefix}_tipo_reg"
                        )
                        edit_is_pa = (tipo_reg_edit == "Ponto de Atenção")

                        options_base = list(st.session_state.nc_options)

                        if edit_is_pa:
                            raw_val = nc_target.get("Ponto de Atenção") or nc_target.get("Não Conformidade", "")
                            curr_selected = obter_lista_siglas_atuais(raw_val)
                            for s in curr_selected:
                                if s and s not in options_base:
                                    options_base.append(s)

                            col_sel, col_add = st.columns([10.5, 1.5])
                            with col_sel:
                                edit_selected_siglas = st.multiselect(
                                    "Siglas de Ponto de Atenção (clique para abrir e selecionar)",
                                    options=options_base,
                                    default=curr_selected,
                                    format_func=formatar_sigla_nc,
                                    placeholder="Clique para abrir e marcar/desmarcar...",
                                    key=f"{nc_key_prefix}_pa_multiselect"
                                )
                            with col_add:
                                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                                if st.button("", icon=":material/add:", key=f"{nc_key_prefix}_btn_custom_pa", help="Adicionar Não Conformidade Personalizada"):
                                    adicionar_nc_personalizada_modal(f"{nc_key_prefix}_pa_multiselect", is_socicam=False)

                            edit_pa_desc = ", ".join(edit_selected_siglas)
                            edit_nc_desc = ""
                        else:
                            raw_val = nc_target.get("Não Conformidade") or nc_target.get("Ponto de Atenção", "")
                            curr_selected = obter_lista_siglas_atuais(raw_val)
                            for s in curr_selected:
                                if s and s not in options_base:
                                    options_base.append(s)

                            col_sel, col_add = st.columns([10.5, 1.5])
                            with col_sel:
                                edit_selected_siglas = st.multiselect(
                                    "Siglas de Não Conformidade (clique para abrir e selecionar)",
                                    options=options_base,
                                    default=curr_selected,
                                    format_func=formatar_sigla_nc,
                                    placeholder="Clique para abrir e marcar/desmarcar...",
                                    key=f"{nc_key_prefix}_nc_multiselect"
                                )
                            with col_add:
                                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                                if st.button("", icon=":material/add:", key=f"{nc_key_prefix}_btn_custom_nc", help="Adicionar Não Conformidade Personalizada"):
                                    adicionar_nc_personalizada_modal(f"{nc_key_prefix}_nc_multiselect", is_socicam=False)

                            edit_nc_desc = ", ".join(edit_selected_siglas)
                            edit_pa_desc = ""

                        edit_observacoes = ""

                        if st.session_state.get("tipo_relatorio", "CRA") == "CRA":
                            dir_val = nc_target.get("Direção (faixa)", "")
                            dir_val_str = "" if (dir_val is None or str(dir_val).strip().lower() in ["nan", "none", "null"]) else str(dir_val).strip()
                            sigla_curr = converter_faixa_para_sigla(dir_val_str)
                            if sigla_curr == "FED" or dir_val_str.upper() == "FED":
                                opts_dir = ["FED", "Direita", "Esquerda"]
                                idx_dir = 0
                            elif sigla_curr == "FE":
                                opts_dir = ["Direita", "Esquerda"]
                                idx_dir = 1
                            else:
                                opts_dir = ["Direita", "Esquerda"]
                                idx_dir = 0
                            edit_direcao = st.selectbox(
                                "Direção (faixa)",
                                options=opts_dir,
                                index=idx_dir,
                                key=f"{nc_key_prefix}_direcao"
                            )
                        else:
                            edit_direcao = ""

                        edit_fundamento = st.text_area("Fundamento da Infração", value=str(nc_target.get("Fundamento da infração", "")), height=80, key=f"{nc_key_prefix}_fundamento")
                        edit_determinacao = st.text_area("Determinação", value=str(nc_target.get("Determinação", "")), height=80, key=f"{nc_key_prefix}_determinacao")

                        if st.button("Salvar Alterações", icon=":material/save:", type="primary", use_container_width=True, key=f"{nc_key_prefix}_btn_save"):
                            nc_target["Pista"] = edit_pista
                            nc_target["Trecho"] = edit_codificacao
                            nc_target["Codificação"] = edit_codificacao
                            if edit_is_pa:
                                nc_target["Ponto de Atenção"] = edit_pa_desc
                                nc_target["Não Conformidade"] = ""
                            else:
                                nc_target["Não Conformidade"] = edit_nc_desc
                                nc_target["Ponto de Atenção"] = ""
                            
                            ident = edit_codificacao if edit_codificacao else (edit_pa_desc if edit_is_pa else edit_nc_desc)
                            nc_target["Identificação"] = ident
                            nc_target["Direção (faixa)"] = edit_direcao

                            # Recalcular legenda formatada para CRA (sincronizando grupo relacionado se existir)
                            from utils import carregar_mapa_siglas_completo
                            from core.rules.cra_rules import sincronizar_legendas_grupo_cra
                            data_foto = nc_target.get("Data da Foto") or extrair_data_original_foto(nc_target.get("Foto"))
                            nc_target["Data da Foto"] = data_foto
                            grp_edit = str(nc_target.get("grupo_relacao") or "").strip()
                            if grp_edit:
                                sincronizar_legendas_grupo_cra(
                                    st.session_state.temp_nc,
                                    grp_edit,
                                    mapa_siglas=carregar_mapa_siglas_completo(),
                                )
                            else:
                                nova_legenda = formatar_legenda_foto(
                                    num=nc_target.get("Nº", 1),
                                    codificacao=edit_codificacao or nc_target.get("Codificação", ""),
                                    siglas_ou_ncs=edit_pa_desc if edit_is_pa else edit_nc_desc,
                                    faixa=edit_direcao,
                                    data_foto=data_foto
                                )
                                nc_target["Observações"] = nova_legenda
                                if "Legenda da Foto" in nc_target:
                                    nc_target["Legenda da Foto"] = nova_legenda
                            nc_target["Fundamento da infração"] = edit_fundamento
                            nc_target["Determinação"] = edit_determinacao
                            st.session_state.relatorios_preenchimento_data = []
                            if "planilha_download_bytes" in st.session_state:
                                del st.session_state.planilha_download_bytes
                            salvar_estado_relatorio_ativo()
                            st.session_state["nc_edit_version"] = nc_version + 1
                            st.session_state.pending_toast = f":green[:material/check_circle:] Alterações salvas para o item nº {nc_target.get('Nº', 1)}!"
                            st.rerun()

                    # 4. CRC ou SOCICAM em Fiscalização:
                    else:
                        is_soc = (tipo == "SOCICAM")
                        options_base = list(st.session_state.socicam_nc_options if is_soc else st.session_state.nc_options)
                        raw_val = nc_target.get("Não Conformidade", "")
                        curr_selected = obter_lista_siglas_atuais(raw_val)
                        for s in curr_selected:
                            if s and s not in options_base:
                                options_base.append(s)

                        col_sel, col_add = st.columns([10.5, 1.5])
                        with col_sel:
                            edit_selected_siglas = st.multiselect(
                                "Não Conformidade (clique para abrir e selecionar)",
                                options=options_base,
                                default=curr_selected,
                                format_func=formatar_sigla_nc,
                                placeholder="Clique para abrir e marcar/desmarcar...",
                                key=f"{nc_key_prefix}_nc_multiselect"
                            )
                        with col_add:
                            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                            if st.button("", icon=":material/add:", key=f"{nc_key_prefix}_btn_custom_nc", help="Adicionar Não Conformidade Personalizada"):
                                adicionar_nc_personalizada_modal(f"{nc_key_prefix}_nc_multiselect", is_socicam=is_soc)

                        edit_nc_desc = ", ".join(edit_selected_siglas)

                        obs_atual = nc_target.get("Observações", nc_target.get("Legenda da Foto", ""))
                        edit_observacoes = st.text_area("Legenda", value=str(obs_atual), height=80, key=f"{nc_key_prefix}_observacoes")

                        edit_fundamento = st.text_area("Fundamento da Infração", value=str(nc_target.get("Fundamento da infração", "")), height=80, key=f"{nc_key_prefix}_fundamento")
                        edit_determinacao = st.text_area("Determinação", value=str(nc_target.get("Determinação", "")), height=80, key=f"{nc_key_prefix}_determinacao")

                        if st.button("Salvar Alterações", icon=":material/save:", type="primary", use_container_width=True, key=f"{nc_key_prefix}_btn_save"):
                            nc_target["Não Conformidade"] = edit_nc_desc
                            nc_target["Observações"] = edit_observacoes
                            if "Legenda da Foto" in nc_target:
                                nc_target["Legenda da Foto"] = edit_observacoes
                            nc_target["Identificação"] = edit_nc_desc
                            nc_target["Fundamento da infração"] = edit_fundamento
                            nc_target["Determinação"] = edit_determinacao
                            st.session_state.relatorios_preenchimento_data = []
                            if "planilha_download_bytes" in st.session_state:
                                del st.session_state.planilha_download_bytes
                            salvar_estado_relatorio_ativo()
                            st.session_state["nc_edit_version"] = nc_version + 1
                            st.session_state.pending_toast = f":green[:material/check_circle:] Alterações salvas para o item nº {nc_target.get('Nº', 1)}!"
                            st.rerun()




@st.dialog("Atenção: Codificação Obrigatória", icon=":material/warning:")
def alerta_codificacao_obrigatoria_modal():
    st.markdown(
        """
        <div style="background-color: #fff1f2; border: 1px solid #fecdd3; border-left: 4px solid #e11d48; border-radius: 6px; padding: 14px 16px; margin-bottom: 16px;">
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                <span style="font-weight: 700; color: #9f1239; font-size: 15px;">
                    Codificação Obrigatória
                </span>
            </div>
            <p style="margin: 0; color: #475569; font-size: 13.5px; line-height: 1.5;">
                O preenchimento do campo <b>Codificação</b> é obrigatório para cadastrar ou relacionar a ocorrência.
            </p>
            <p style="margin: 6px 0 0 0; color: #64748b; font-size: 12.5px;">
                Por favor, informe a codificação da ocorrência (ex: <code>CRA.ST601.2790-2794</code>) antes de prosseguir.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("Entendido", type="primary", use_container_width=True, key="btn_fechar_aviso_cod_obrigatoria"):
        st.rerun()

