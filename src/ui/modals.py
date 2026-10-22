# -*- coding: utf-8 -*-
import streamlit as st
from database.manager import (
    salvar_responsaveis,
    salvar_coordenadores,
    salvar_contratos,
    salvar_custom_ncs,
    salvar_custom_ncs_socicam
)
from sections.quadros.quadros import MAP_SIGLAS, expandir_siglas
from ui.state import sincronizar_opcoes_nc, BASE_NC_OPTIONS, salvar_estado_relatorio_ativo
from utils import (
    calcular_codificacao_cra,
    obter_proximo_numero_sequencial_cra,
    formatar_legenda_foto,
    converter_faixa_para_sigla,
    combinar_faixas_relacionadas
)
from services.image_service import extrair_data_original_foto


@st.dialog("Visualização Completa da Imagem", width="large", icon=":material/zoom_in:")
def mostrar_foto_modal(uploaded_file):
    from services.image_service import obter_foto_base64
    import os
    caption = getattr(uploaded_file, "name", None)
    if not caption and isinstance(uploaded_file, str):
        caption = os.path.basename(uploaded_file)
    if not caption:
        caption = "Visualização da Imagem"

    b64_src = obter_foto_base64(uploaded_file, max_size=(1600, 1200))
    if b64_src:
        st.html(
            f'<div style="text-align: center; margin: 4px 0;">'
            f'<img src="{b64_src}" style="max-width: 100%; max-height: 75vh; border-radius: 8px; object-fit: contain; box-shadow: 0 4px 20px rgba(0,0,0,0.15); display: inline-block;" alt="{caption}" />'
            f'<p style="color: #64748b; font-size: 13.5px; margin-top: 10px; font-weight: 500;">{caption}</p>'
            f'</div>'
        )
    else:
        st.info(f"Imagem indisponível: {caption}")


@st.dialog("Galeria de Fotos do Levantamento", width="large", icon=":material/photo_library:")
def galeria_fotos_modal(fotos=None, target_index_key="carousel_index"):
    from services.image_service import obter_foto_base64, obter_nomes_fotos_em_nc, foto_esta_em_nc
    import os
    
    if fotos is None:
        fotos = st.session_state.get("fill_photos", [])
    if not fotos:
        st.info("Nenhuma foto disponível no momento.")
        return

    nomes_em_nc = obter_nomes_fotos_em_nc(st.session_state.get("temp_nc", []))

    st.markdown(f"Clique diretamente em qualquer foto para defini-la como a foto central do carrossel (**{len(fotos)} fotos disponíveis**). As fotos **apagadas** já foram adicionadas a uma Não Conformidade.")
    
    filtro = st.text_input("Filtrar fotos por nome:", placeholder="Digite parte do nome da foto...", key="input_filtro_galeria")
    
    fotos_enumeradas = list(enumerate(fotos))
    if filtro.strip():
        filtro_lower = filtro.strip().lower()
        fotos_enumeradas = [item for item in fotos_enumeradas if filtro_lower in (getattr(item[1], "name", os.path.basename(item[1]) if isinstance(item[1], str) else "")).lower()]

    if not fotos_enumeradas:
        st.warning("Nenhuma foto encontrada com o filtro informado.")
        return

    cols_per_row = 4
    for row_start in range(0, len(fotos_enumeradas), cols_per_row):
        cols = st.columns(cols_per_row)
        for c_idx in range(cols_per_row):
            item_idx = row_start + c_idx
            if item_idx < len(fotos_enumeradas):
                orig_idx, photo = fotos_enumeradas[item_idx]
                with cols[c_idx]:
                    is_current = (orig_idx == st.session_state.get(target_index_key, 0))
                    in_nc = foto_esta_em_nc(photo, nomes_em_nc)
                    
                    if is_current and in_nc:
                        card_key = f"gal_card_curr_nc_{orig_idx}"
                    elif in_nc:
                        card_key = f"gal_card_nc_{orig_idx}"
                    elif is_current:
                        card_key = f"gal_card_curr_{orig_idx}"
                    else:
                        card_key = f"gal_card_{orig_idx}"

                    with st.container(key=card_key):
                        b64_src = obter_foto_base64(photo, max_size=(220, 165))
                        if b64_src:
                            st.html(f'<img src="{b64_src}" style="width: 100%; height: auto; border-radius: 6px; display: block;" alt="Foto {orig_idx + 1}" />')
                        else:
                            st.info("Imagem indisponível")
                        
                        nome = getattr(photo, "name", None)
                        if not nome and isinstance(photo, str):
                            nome = os.path.basename(photo)
                        if not nome:
                            nome = f"Foto {orig_idx + 1}"
                            
                        nome_curto = nome[:16] + "..." if len(nome) > 19 else nome
                        
                        badges = []
                        if is_current and in_nc:
                            badges.append(":material/warning:")
                        elif is_current:
                            badges.append(":material/push_pin:")
                        if in_nc:
                            badges.append(f"**[{in_nc}]**")
                        badge_str = f" {' '.join(badges)}" if badges else ""

                        st.caption(f"**#{orig_idx + 1}** {nome_curto}{badge_str}")
                        
                        if st.button("", key=f"btn_gal_pick_{orig_idx}_{target_index_key}"):
                            st.session_state[target_index_key] = orig_idx
                            st.rerun()


@st.dialog("Atenção: Foto já utilizada", width="small")
def alerta_foto_duplicada_modal(foto_name, acao_nome, fill_photos):
    from services.image_service import obter_foto_base64
    
    st.markdown(
        "<div style='text-align: center; color: #ef4444; font-size: 48px;'>"
        "<span class='material-symbols-rounded'>warning</span></div>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<p style='text-align: center; font-size: 15px;'>Você está tentando <b>{acao_nome.lower()}</b> uma foto que já foi "
        "adicionada ou relacionada a outro item/registro anteriormente.</p>",
        unsafe_allow_html=True
    )
    
    photo_obj = next((p for p in fill_photos if getattr(p, "name", "") == foto_name or p == foto_name), None)
    if photo_obj:
        b64_src = obter_foto_base64(photo_obj, max_size=(320, 240))
        if b64_src:
            st.html(f'<div style="text-align: center; margin: 8px 0;"><img src="{b64_src}" style="max-width: 100%; height: auto; border-radius: 8px; display: inline-block; box-shadow: 0 2px 8px rgba(0,0,0,0.12);" alt="{foto_name}" /></div>')
    
    st.write("")
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"{acao_nome} mesmo", type="primary", use_container_width=True):
            if acao_nome == "Adicionar":
                st.session_state.modal_confirmed_proximo = True
                st.session_state.force_proximo_modal = True
            elif acao_nome == "Relacionar":
                st.session_state.modal_confirmed_relacionar = True
                st.session_state.force_relacionar_modal = True
            st.rerun()
    with col2:
        if st.button("Cancelar", use_container_width=True):
            st.rerun()

@st.dialog("Confirmar Exclusão em Lote", icon=":material/delete:")
def confirmar_exclusao_lote_modal(ids, term_plural_lower="fiscalizações", term_plural="Fiscalizações"):
    st.write(f"Você tem certeza que deseja excluir as seguintes {term_plural_lower}?")
    for id_fisc in ids:
        st.write(f"- **{id_fisc}**")
    st.write("Isso também removerá todas as Não Conformidades vinculadas a estes IDs.")
    st.warning("Esta ação não pode ser desfeita.")
    
    col_sim, col_nao = st.columns(2)
    with col_sim:
        if st.button("Sim, Excluir", icon=":material/delete:", type="primary", use_container_width=True, key="btn_confirm_bulk_del"):
            st.session_state.temp_fiscalizacoes = [f for f in st.session_state.temp_fiscalizacoes if f["ID da Fiscalização"] not in ids]
            st.session_state.temp_nc = [nc for nc in st.session_state.temp_nc if nc["ID da Fiscalização"] not in ids]
            st.session_state.relatorios_preenchimento_data = []
            salvar_estado_relatorio_ativo()
            st.session_state.pending_toast = f":green[:material/check_circle:] {term_plural} selecionadas excluídas com sucesso!"
            st.rerun()
    with col_nao:
        if st.button("Cancelar", icon=":material/close:", use_container_width=True, key="btn_cancel_bulk_del"):
            st.rerun()


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

                        # Apaga o arquivo de cache correspondente em geradorRelatorios/
                        limpar_sessao_local(tipo_relatorio, categoria_relatorio)

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

                            # Recalcular legenda formatada para CRA
                            data_foto = nc_target.get("Data da Foto") or extrair_data_original_foto(nc_target.get("Foto"))
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


@st.dialog("Relacionar Foto ao Registro Anterior", width="large")
def relacionar_foto_modal(foto_atual, last_nc, is_cra_fisc=True, target_fisc_data=""):
    from services.image_service import obter_foto_base64, extrair_nome_foto

    st.markdown(
        "<div style='font-size: 14.5px; color: #334155; margin-bottom: 14px; line-height: 1.45;'>"
        "Você está relacionando a nova foto selecionada ao último registro cadastrado. "
        "Revise as fotos e dados lado a lado e, se desejar, modifique a <b>Codificação</b> e as <b>Siglas (NC / PT)</b> antes de confirmar a relação."
        "</div>",
        unsafe_allow_html=True
    )

    target_id = last_nc.get("ID da Fiscalização")
    ant_grp_id = last_nc.get("grupo_relacao")
    if not ant_grp_id:
        ant_grp_id = f"grp_{target_id}_{last_nc.get('Nº', 1)}_{st.session_state.nc_form_counter}"
        last_nc["grupo_relacao"] = ant_grp_id

    # Busca todos os registros do grupo base
    grupo_recs = [nc for nc in st.session_state.temp_nc if nc.get("grupo_relacao") == ant_grp_id]
    if not grupo_recs:
        grupo_recs = [last_nc]

    # Identificar siglas do grupo base
    ant_siglas_lista = []
    for rec in grupo_recs:
        s_val = rec.get("Não Conformidade") or rec.get("Ponto de Atenção") or ""
        for s in str(s_val).split(","):
            s_clean = s.strip()
            if s_clean and s_clean not in ant_siglas_lista:
                ant_siglas_lista.append(s_clean)

    has_nc = any(bool(str(rec.get("Não Conformidade", "")).strip()) for rec in grupo_recs)
    ant_tipo = "Não Conformidade" if has_nc else "Ponto de Atenção"
    ant_foto = grupo_recs[0].get("Foto")
    ant_num = grupo_recs[0].get("Nº", 1)
    ant_cod = last_nc.get("Codificação", "") or last_nc.get("Trecho", "")
    ant_nome = extrair_nome_foto(ant_foto) or getattr(ant_foto, "name", f"Foto #{ant_num}")

    # Identificar dados da foto atual a relacionar
    if st.session_state.fill_photos:
        idx_curr = min(max(0, st.session_state.get("carousel_index", 0)), len(st.session_state.fill_photos) - 1)
        foto_num_atual = idx_curr + 1
    else:
        foto_num_atual = ant_num + 1
    atual_nome = extrair_nome_foto(foto_atual) or getattr(foto_atual, "name", f"Foto #{foto_num_atual}")

    # Opções de siglas de acordo com o tipo de relatório
    is_socicam = st.session_state.get("tipo_relatorio", "") == "SOCICAM"
    options_nc = st.session_state.socicam_nc_options if is_socicam else st.session_state.nc_options

    col_ant, col_nova = st.columns(2, gap="medium")

    with col_ant:
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%); 
                        padding: 9px 12px; border-radius: 8px 8px 0 0; 
                        border: 1px solid #cbd5e1; border-bottom: none; 
                        display: flex; align-items: center; justify-content: space-between;">
                <span style="font-weight: 600; color: #1e293b; font-size: 13.5px;">
                    📷 Foto Anterior (Registro Base)
                </span>
                <span style="background: #2F5173; color: #fff; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">
                    Item #{ant_num}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
        with st.container(border=True):
            b64_ant = obter_foto_base64(ant_foto, max_size=(380, 260))
            if b64_ant:
                st.html(f'<img src="{b64_ant}" style="width: 100%; height: auto; border-radius: 6px; display: block;" alt="{ant_nome}" />')
            else:
                st.info(f"Foto: {ant_nome}")

            st.caption(f"**Arquivo:** `{ant_nome}`")
            st.divider()

            st.markdown(f"**Codificação Anterior:** `{ant_cod if ant_cod else '-'}`")
            ant_faixa = last_nc.get("Direção (faixa)", "")
            sigla_ant_disp = converter_faixa_para_sigla(ant_faixa)
            disp_ant_faixa = f"{ant_faixa} ({sigla_ant_disp})" if sigla_ant_disp and sigla_ant_disp != ant_faixa else (ant_faixa if ant_faixa else "-")
            st.markdown(f"**Direção (faixa) Anterior:** `{disp_ant_faixa}`")
            st.markdown(f"**Tipo:** *{ant_tipo}*")
            siglas_exibidas = ", ".join(ant_siglas_lista) if ant_siglas_lista else "-"
            st.markdown(f"**Sigla(s):** **{siglas_exibidas}**")
            if is_cra_fisc and ant_siglas_lista:
                exp = expandir_siglas(", ".join(ant_siglas_lista))
                if exp:
                    st.caption(f":material/description: {exp}")

    with col_nova:
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%); 
                        padding: 9px 12px; border-radius: 8px 8px 0 0; 
                        border: 1px solid #7dd3fc; border-bottom: none; 
                        display: flex; align-items: center; justify-content: space-between;">
                <span style="font-weight: 600; color: #0369a1; font-size: 13.5px;">
                    🔗 Nova Foto (A Relacionar)
                </span>
                <span style="background: #0284c7; color: #fff; padding: 2px 8px; border-radius: 12px; font-size: 11px; font-weight: 600;">
                    Item #{foto_num_atual}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
        with st.container(border=True):
            b64_nova = obter_foto_base64(foto_atual, max_size=(380, 260))
            if b64_nova:
                st.html(f'<img src="{b64_nova}" style="width: 100%; height: auto; border-radius: 6px; display: block;" alt="{atual_nome}" />')
            else:
                st.info(f"Foto: {atual_nome}")

            st.caption(f"**Arquivo:** `{atual_nome}`")
            st.divider()

            st.markdown("**Modificar campos relacionados:**")

            tipo_idx = 1 if ant_tipo == "Ponto de Atenção" else 0
            rel_tipo = st.radio(
                "Tipo de Registro:",
                options=["Não Conformidade", "Ponto de Atenção"],
                index=tipo_idx,
                horizontal=True,
                key=f"modal_rel_tipo_{st.session_state.nc_form_counter}"
            )

            default_pills = [s for s in ant_siglas_lista if s in options_nc]
            pills_label = "Siglas de Não Conformidade (NC):" if rel_tipo == "Não Conformidade" else "Siglas de Ponto de Atenção (PT):"
            rel_siglas = st.pills(
                pills_label,
                options=options_nc,
                default=default_pills,
                selection_mode="multi",
                key=f"modal_rel_siglas_{st.session_state.nc_form_counter}"
            )

            if rel_siglas:
                exp_new = expandir_siglas(", ".join(rel_siglas))
                if exp_new:
                    st.caption(f":material/info: {exp_new}")

            # Identificar se as siglas mudaram em relação à foto anterior
            siglas_mudaram = (sorted(rel_siglas or []) != sorted(ant_siglas_lista))

            # Não preenche automaticamente: o usuário preenche se desejar ou deixa em branco para herdar a anterior
            rel_cod = st.text_input(
                "Codificação:",
                key=f"modal_rel_cod_{st.session_state.nc_form_counter}",
                placeholder=f"Em branco = herdar anterior ({ant_cod}) ou digite...",
                help="Deixe em branco para herdar a codificação anterior ou informe a nova codificação desejada."
            )

            sigla_ant = converter_faixa_para_sigla(ant_faixa)
            opts_rel_faixa = ["Direita", "Esquerda"]
            # Recomenda a mesma faixa escolhida na foto anterior
            idx_rel_faixa = 1 if sigla_ant == "FE" else 0

            rel_faixa = st.selectbox(
                "Direção (faixa):",
                options=opts_rel_faixa,
                index=idx_rel_faixa,
                key=f"modal_rel_faixa_{st.session_state.nc_form_counter}",
                help="Escolha se a foto relacionada é na faixa Direita ou Esquerda."
            )

    # Painel Informativo sobre o Quadro Word
    st.write("")
    if is_cra_fisc:
        if not siglas_mudaram:
            cod_exib = rel_cod.strip() if rel_cod.strip() else ant_cod
            st.info(
                f":material/link: **Mesmas Siglas Mantidas:** A nova foto será agrupada sob a mesma codificação (`{cod_exib}`) no Quadro (relação 1:1)."
            )
        else:
            st.success(
                ":material/device_hub: **Siglas Diferentes Detectadas:** No Quadro, será gerada uma codificação para cada sigla (**1 para 1**) e as fotos ficarão relacionadas (**N para 1**) com colunas mescladas."
            )
        
        base_raw_prev = rel_cod.strip() if rel_cod.strip() else ant_cod
        base_limpa_prev = base_raw_prev.split("/")[0] if "/" in base_raw_prev else base_raw_prev
        seq_prev = obter_proximo_numero_sequencial_cra(
            st.session_state.temp_nc,
            id_vinculo=target_id,
            tipo_registro=rel_tipo
        )
        cod_prev_rel = calcular_codificacao_cra(base_limpa_prev, data_fisc=target_fisc_data, seq_idx=seq_prev)
        data_prev_rel = extrair_data_original_foto(foto_atual)
        faixa_combinada_prev = combinar_faixas_relacionadas(ant_faixa, rel_faixa)
        leg_prev = formatar_legenda_foto(
            num=foto_num_atual,
            codificacao=cod_prev_rel,
            siglas_ou_ncs=rel_siglas,
            faixa=faixa_combinada_prev,
            data_foto=data_prev_rel
        )
        st.caption(f":material/subtitles: **Legenda:** {leg_prev}")
        if faixa_combinada_prev == "FED":
            st.caption(":material/sync_alt: **Faixa Combinada:** Como uma foto é da Esquerda e a outra da Direita, a legenda de ambas terá a sigla **FED**.")

    # Botões de Ação
    st.write("")
    col_conf, col_canc = st.columns([2, 1], gap="small")
    with col_conf:
        if st.button("Confirmar Relação", icon=":material/link:", type="primary", use_container_width=True, key=f"btn_modal_confirm_rel_{st.session_state.nc_form_counter}"):
            if not rel_siglas:
                st.error("Selecione ao menos uma sigla para confirmar a relação.")
                return

            foto_para_salvar = extrair_nome_foto(foto_atual) or foto_atual
            faixa_combinada = combinar_faixas_relacionadas(ant_faixa, rel_faixa)
            # No Quadro 2 a faixa deve aparecer por extenso
            faixa_extenso = {"FE": "Esquerda", "FD": "Direita", "FED": "Esquerda e Direita"}.get(faixa_combinada, faixa_combinada)

            # Colocar estado relacionado nas duas fotos que estão relacionadas:
            # atualiza o registro base anterior (e todos os itens do mesmo grupo) para is_relacionado = True
            # e atualiza a faixa e a legenda de ambos para a faixa combinada (ex: FED)
            for rec in st.session_state.temp_nc:
                if (ant_grp_id and rec.get("grupo_relacao") == ant_grp_id) or (ant_nome and extrair_nome_foto(rec.get("Foto")).lower() == ant_nome.lower()):
                    rec["is_relacionado"] = True
                    rec["Direção (faixa)"] = faixa_extenso
                    r_cod = str(rec.get("Codificação") or rec.get("Trecho") or "")
                    r_siglas = rec.get("Não Conformidade") or rec.get("Ponto de Atenção") or ""
                    r_data = rec.get("Data da Foto") or extrair_data_original_foto(rec.get("Foto"))
                    r_leg = formatar_legenda_foto(
                        num=rec.get("Nº", 1),
                        codificacao=r_cod,
                        siglas_ou_ncs=r_siglas,
                        faixa=faixa_combinada,
                        data_foto=r_data
                    )
                    rec["Observações"] = r_leg
                    rec["Legenda da Foto"] = r_leg

            if is_cra_fisc:
                base_raw = rel_cod.strip() if rel_cod.strip() else ant_cod
                if not base_raw:
                    st.error("A codificação é obrigatória! Por favor, preencha o campo Codificação para confirmar a relação.")
                    return

                base_limpa = base_raw.split("/")[0] if "/" in base_raw else base_raw
                data_foto_rel = extrair_data_original_foto(foto_para_salvar)

                seq_primeira = obter_proximo_numero_sequencial_cra(
                    st.session_state.temp_nc,
                    id_vinculo=target_id,
                    tipo_registro=rel_tipo
                )
                cod_legenda_rel = calcular_codificacao_cra(base_limpa, data_fisc=target_fisc_data, seq_idx=seq_primeira)
                legenda_relacionada = formatar_legenda_foto(
                    num=foto_num_atual,
                    codificacao=cod_legenda_rel,
                    siglas_ou_ncs=rel_siglas,
                    faixa=faixa_combinada,
                    data_foto=data_foto_rel
                )

                for sigla in rel_siglas:
                    seq_tipo = obter_proximo_numero_sequencial_cra(
                        st.session_state.temp_nc,
                        id_vinculo=target_id,
                        tipo_registro=rel_tipo
                    )
                    cod_final = calcular_codificacao_cra(base_limpa, data_fisc=target_fisc_data, seq_idx=seq_tipo)
                    identificacao = cod_final if cod_final else sigla
                    new_nc = {
                        "ID da Fiscalização": target_id,
                        "Nº": foto_num_atual,
                        "Terminal": last_nc.get("Terminal", ""),
                        "Pista": last_nc.get("Pista", ""),
                        "Trecho": cod_final,
                        "Codificação": cod_final,
                        "Não Conformidade": sigla if rel_tipo == "Não Conformidade" else "",
                        "Ponto de Atenção": sigla if rel_tipo == "Ponto de Atenção" else "",
                        "Foto": foto_para_salvar,
                        "Foto Anterior": "",
                        "Legenda Anterior": "",
                        "Observações": legenda_relacionada,
                        "Legenda da Foto": legenda_relacionada,
                        "Identificação": identificacao,
                        "Direção (faixa)": faixa_extenso,
                        "Fundamento da infração": last_nc.get("Fundamento da infração", ""),
                        "Determinação": last_nc.get("Determinação", ""),
                        "Situação": last_nc.get("Situação", "Pendente"),
                        "Análise ARPE": "",
                        "is_relacionado": True,
                        "grupo_relacao": ant_grp_id,
                        "Data da Foto": data_foto_rel
                    }
                    st.session_state.temp_nc.append(new_nc)
            else:
                nc_desc_str = ", ".join(rel_siglas) if rel_tipo == "Não Conformidade" else ""
                pa_desc_str = ", ".join(rel_siglas) if rel_tipo == "Ponto de Atenção" else ""
                cod_final = rel_cod.strip() if rel_cod.strip() else ant_cod
                identificacao = cod_final if cod_final else (nc_desc_str or pa_desc_str)
                ncs_existentes = [nc for nc in st.session_state.temp_nc if nc.get("ID da Fiscalização") == target_id]
                new_nc_num = len(ncs_existentes) + 1
                data_foto_rel = extrair_data_original_foto(foto_para_salvar)
                legenda_relacionada = formatar_legenda_foto(
                    num=new_nc_num,
                    codificacao=cod_final,
                    siglas_ou_ncs=rel_siglas,
                    faixa=faixa_combinada,
                    data_foto=data_foto_rel
                )
                new_nc = {
                    "ID da Fiscalização": target_id,
                    "Nº": new_nc_num,
                    "Terminal": last_nc.get("Terminal", ""),
                    "Pista": last_nc.get("Pista", ""),
                    "Trecho": cod_final,
                    "Codificação": cod_final,
                    "Não Conformidade": nc_desc_str,
                    "Ponto de Atenção": pa_desc_str,
                    "Foto": foto_para_salvar,
                    "Foto Anterior": "",
                    "Legenda Anterior": "",
                    "Observações": legenda_relacionada,
                    "Legenda da Foto": legenda_relacionada,
                    "Identificação": identificacao,
                    "Direção (faixa)": faixa_extenso,
                    "Fundamento da infração": last_nc.get("Fundamento da infração", ""),
                    "Determinação": last_nc.get("Determinação", ""),
                    "Situação": last_nc.get("Situação", "Pendente"),
                    "Análise ARPE": "",
                    "is_relacionado": True,
                    "grupo_relacao": ant_grp_id,
                    "Data da Foto": data_foto_rel
                }
                st.session_state.temp_nc.append(new_nc)

            st.session_state.relatorios_preenchimento_data = []
            if "planilha_download_bytes" in st.session_state:
                del st.session_state.planilha_download_bytes

            if st.session_state.get("auto_advance_active", True) and st.session_state.fill_photos and st.session_state.carousel_index < len(st.session_state.fill_photos) - 1:
                st.session_state.carousel_index += 1

            st.session_state.pista_persistida = last_nc.get("Pista", "")
            st.session_state.fundamento_persistido = last_nc.get("Fundamento da infração", "")
            st.session_state.determinacao_persistida = last_nc.get("Determinação", "")
            st.session_state.faixa_persistida = rel_faixa.strip()

            salvar_estado_relatorio_ativo()
            st.session_state.nc_form_counter += 1
            st.session_state.pending_toast = {"msg": "Foto relacionada com sucesso!", "icon": ":material/check_circle:"}
            st.rerun()

    with col_canc:
        if st.button("Cancelar", icon=":material/close:", use_container_width=True, key=f"btn_modal_cancel_rel_{st.session_state.nc_form_counter}"):
            st.rerun()



