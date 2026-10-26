# -*- coding: utf-8 -*-
import os
import streamlit as st
from ui.state import salvar_estado_relatorio_ativo
from utils import (
    formatar_legenda_foto,
    converter_faixa_para_sigla,
    combinar_faixas_relacionadas,
    calcular_codificacao_cra,
    obter_proximo_numero_sequencial_cra,
)
from services.image_service import (
    extrair_data_original_foto,
    obter_foto_base64,
    obter_nomes_fotos_em_nc,
    foto_esta_em_nc,
    extrair_nome_foto,
)

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


