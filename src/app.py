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
from services.data_service import (
    gerar_planilha_excel_buffer,
    salvar_fotos_em_diretorio
)
from ui.state import inicializar_estado_sessao, obter_termos_ui
from ui.modals import (
    mostrar_foto_modal,
    confirmar_exclusao_lote_modal,
    confirmar_exclusao_nc_modal,
    gerenciar_responsaveis_modal,
    gerenciar_coordenadores_modal,
    gerenciar_contratos_modal,
    adicionar_nc_personalizada_modal
)

st.set_page_config(page_title="Gerador de Relatórios", layout="wide")

def inject_custom_theme_css():
    import os
    css_path = os.path.join(os.path.dirname(__file__), "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.html(f"<style>{css_content}</style>")

inject_custom_theme_css()

# Inicialização centralizada do estado e opções da aplicação
inicializar_estado_sessao()

is_monitoring = st.session_state.categoria_relatorio == "Monitoramento"
is_crc_monitoring = (st.session_state.get("tipo_relatorio", "CRA") == "CRC" and is_monitoring)
terms = obter_termos_ui(is_monitoring)
term_fisc = terms["term_fisc"]
term_fisc_lower = terms["term_fisc_lower"]
term_fisc_plural = terms["term_fisc_plural"]
term_fisc_plural_lower = terms["term_fisc_plural_lower"]
term_fisc_prep = terms["term_fisc_prep"]
term_fisc_prep_f = terms["term_fisc_prep_f"]
term_fisc_pessoal = terms["term_fisc_pessoal"]

_, col_center_group, _ = st.columns([1, 12, 1])
with col_center_group:
    c_space_l, c_title, c_b1, c_b2, c_space_r = st.columns([2, 16, 1, 1, 3], gap="small")
    with c_title:
        st.markdown(
            f"<h1 style='text-align: right; margin: 0; padding-right: 6px; font-size: 3.15rem; font-weight: 900; color: #ffffff; -webkit-text-stroke: 6px #6f4b3e; paint-order: stroke fill; white-space: nowrap;'>📄 Gerador {st.session_state.tipo_relatorio} ({st.session_state.categoria_relatorio})</h1>",
            unsafe_allow_html=True
        )
    with c_b1:
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        if st.button("🔄", key="btn_swap_tipo", help="Clique para alternar entre CRA, CRC e SOCICAM"):
            if st.session_state.tipo_relatorio == "CRA":
                st.session_state.tipo_relatorio = "CRC"
            elif st.session_state.tipo_relatorio == "CRC":
                st.session_state.tipo_relatorio = "SOCICAM"
            else:
                st.session_state.tipo_relatorio = "CRA"
            st.rerun()
    with c_b2:
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        if st.button("📋", key="btn_swap_categoria", help="Clique para alternar entre Fiscalização e Monitoramento"):
            if st.session_state.categoria_relatorio == "Fiscalização":
                st.session_state.categoria_relatorio = "Monitoramento"
            else:
                st.session_state.categoria_relatorio = "Fiscalização"
            st.rerun()

# Layout principal da aplicação
with st.container():

    # 1. Upload de Fotos do Levantamento no início
    with st.container(border=True, key="upload_arquivos_container"):
        st.markdown("### 📷 Upload de Arquivos")
        if "photos_uploader_version" not in st.session_state:
            st.session_state.photos_uploader_version = 0
        if "mon_uploader_version" not in st.session_state:
            st.session_state.mon_uploader_version = 0
            
        col_uploader, col_sort, col_clear = st.columns([3, 1, 1])
        with col_uploader:
            uploaded_nc_photos = st.file_uploader(
                f"Faça o upload de todas as fotos {term_fisc_prep_f.lower()} para usá-las no carrossel de Registros", 
                type=["jpg", "jpeg", "png"], 
                accept_multiple_files=True,
                key=f"fill_photos_uploader_{st.session_state.photos_uploader_version}"
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
                st.session_state.photos_uploader_version += 1
                st.session_state.fill_photos = []
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

        # 1.1 Upload de Documentos Auxiliares
        uploaded_mon_anterior = None
        if is_monitoring:
            uploaded_mon_anterior = st.file_uploader(
                "Monitoramento Anterior",
                type=["doc", "docx"],
                help="Selecione o arquivo do monitoramento anterior (.doc, .docx)",
                key=f"mon_anterior_uploader_{st.session_state.mon_uploader_version}"
            )

        if "old_photos_to_match" not in st.session_state:
            st.session_state.old_photos_to_match = []

        if is_monitoring and uploaded_mon_anterior:
            last_parsed_key = f"last_parsed_{uploaded_mon_anterior.name}_{uploaded_mon_anterior.size}"
            if st.session_state.get("last_parsed_file") != last_parsed_key or not st.session_state.get("old_photos_to_match"):
                from monitoramento_utils import extrair_ncs_e_fotos_anterior
                st.session_state.old_photos_to_match = extrair_ncs_e_fotos_anterior(uploaded_mon_anterior)
                
                # Adicionar a label de exibição para cada item ("id_nc - trecho")
                label_counts = {}
                for item in st.session_state.old_photos_to_match:
                    id_nc = str(item.get("id_nc", "")).strip()
                    t = str(item.get("trecho", "")).strip()
                    base_label = f"{id_nc} - {t}"
                    label_counts[base_label] = label_counts.get(base_label, 0) + 1
                    
                label_current_indices = {}
                for item in st.session_state.old_photos_to_match:
                    id_nc = str(item.get("id_nc", "")).strip()
                    t = str(item.get("trecho", "")).strip()
                    base_label = f"{id_nc} - {t}"
                    total = label_counts[base_label]
                    if total > 1:
                        idx_l = label_current_indices.get(base_label, 0) + 1
                        label_current_indices[base_label] = idx_l
                        item["display_label"] = f"{base_label} ({idx_l})"
                    else:
                        item["display_label"] = base_label
                        
                st.session_state.last_parsed_file = last_parsed_key
                st.session_state.carousel_index = 0
        elif is_monitoring and "last_parsed_file" in st.session_state and uploaded_mon_anterior is None:
            # Se o usuário removeu explicitamente o arquivo do uploader, limpa as fotos
            st.session_state.old_photos_to_match = []
            del st.session_state.last_parsed_file
        elif not is_monitoring:
            st.session_state.old_photos_to_match = []
            if "last_parsed_file" in st.session_state:
                del st.session_state.last_parsed_file

    if "carousel_index" not in st.session_state:
        st.session_state.carousel_index = 0
    if is_monitoring and st.session_state.old_photos_to_match:
        st.session_state.carousel_index = min(st.session_state.carousel_index, len(st.session_state.old_photos_to_match) - 1)
        st.session_state.carousel_index = max(0, st.session_state.carousel_index)
    elif st.session_state.fill_photos:
        st.session_state.carousel_index = min(st.session_state.carousel_index, len(st.session_state.fill_photos) - 1)
        st.session_state.carousel_index = max(0, st.session_state.carousel_index)

    with st.container(border=True, key="top_fisc_container"):
        st.markdown(f"### 📍 {term_fisc}")
        if st.session_state.get("last_added_fisc_msg"):
            st.success(st.session_state.last_added_fisc_msg)
            del st.session_state.last_added_fisc_msg
            
        col1, col2 = st.columns(2)
        with col1:
            id_fisc = st.text_input(f"ID {term_fisc_prep} (ex: 2026-001)", key="fisc_input_id", help="Identificador único para vincular as abas")
            data_fisc = st.text_input("Data (ex: 15/06/2026)", key="fisc_input_data", placeholder="dd/mm/aaaa")
            if st.session_state.get("tipo_relatorio", "CRA") == "CRA":
                hora = st.text_input("Hora (ex: 10:00)", key="fisc_input_hora", placeholder="Opcional")
                cidade = st.text_input("Cidade (ex: Recife)", key="fisc_input_cidade", placeholder="Cidade do Terminal")
            else:
                hora = ""
                cidade = ""
                
            if st.session_state.get("tipo_relatorio", "CRA") == "CRC":
                local = "Sistema Viário do Paiva"
                periodo = st.text_input("Período (ex: 15 a 18/06/2026)", key="fisc_input_periodo_crc", placeholder="Opcional")
                submit_fisc = st.button(f"➕ Adicionar {term_fisc}", type="primary")
            elif st.session_state.get("tipo_relatorio", "CRA") == "SOCICAM":
                local = st.text_input("Local (ex: TIP (RECIFE))", key="fisc_input_local_socicam", placeholder="Nome do Terminal")
        with col2:
            if st.session_state.get("tipo_relatorio", "CRA") == "CRA":
                local = st.text_input("Local (ex: TIP (RECIFE))", key="fisc_input_local_cra", placeholder="Nome do Terminal")
                periodo = st.text_input("Período (ex: 15 a 18/06/2026)", key="fisc_input_periodo_cra", placeholder="Opcional")
            elif st.session_state.get("tipo_relatorio", "CRA") == "SOCICAM":
                periodo = st.text_input("Período (ex: 15 a 18/06/2026)", key="fisc_input_periodo_socicam", placeholder="Opcional")
 
            col_resp, col_gear = st.columns([10, 1])
            with col_resp:
                responsaveis_sel = st.multiselect(
                    "Pessoal Responsável",
                    options=st.session_state.pessoal_responsaveis,
                    default=st.session_state.pessoal_responsaveis,
                    format_func=lambda x: x["nome"],
                    key="fisc_input_responsaveis",
                    help=f"Selecione os responsáveis {term_fisc_pessoal}. Use a engrenagem ao lado para gerenciar a lista."
                )
                responsaveis = ", ".join([r["nome"] for r in responsaveis_sel])
            with col_gear:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                if st.button("⚙️", help="Gerenciar Responsáveis", key="btn_manage_responsaveis"):
                    gerenciar_responsaveis_modal(term_fisc_pessoal)
            
            # Coordenador
            col_coord, col_gear_coord = st.columns([10, 1])
            with col_coord:
                coordenador_sel = st.selectbox(
                    "Coordenador",
                    options=st.session_state.coordenadores,
                    format_func=lambda x: x["nome"],
                    key="fisc_input_coordenador",
                    help=f"Selecione o coordenador {term_fisc_prep_f.lower()}. Use a engrenagem ao lado para gerenciar a lista."
                )
                coordenador = coordenador_sel["nome"] if coordenador_sel else ""
            with col_gear_coord:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                if st.button("⚙️", help="Gerenciar Coordenadores", key="btn_manage_coordenadores"):
                    gerenciar_coordenadores_modal(term_fisc_prep_f)
            
            # Número do Contrato definido automaticamente por tipo de relatório
            if st.session_state.get("tipo_relatorio", "CRA") == "CRA":
                contrato = "CT. nº 043/2011"
            elif st.session_state.get("tipo_relatorio", "CRA") == "CRC":
                contrato = "CGPE-001/2006"
            else:
                contrato = "CT. nº 1.041.080/08"
 
        if st.session_state.get("tipo_relatorio", "CRA") in ["CRA", "SOCICAM"]:
            submit_fisc = st.button(f"➕ Adicionar {term_fisc}", type="primary")
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
                
                st.session_state.last_added_fisc_msg = f"✅ {term_fisc} {id_fisc} adicionado(a) com sucesso!"
                st.rerun()

    st.write("")
    
    id_vinculo = "Nenhum ID cadastrado"
    nc_num = 1
    terminal_nc = ""
    
    if st.session_state.get("tipo_relatorio", "CRA") == "CRC" and is_monitoring:
        st.session_state.nc_form_step = 1
    
    uploads_pendentes = False
    mensagem_pendencias = []
    
    if not st.session_state.get("fill_photos"):
        uploads_pendentes = True
        mensagem_pendencias.append("as fotos do levantamento")
        
    if is_monitoring:
        # Só bloqueia se não tiver parseado o arquivo ainda
        if not st.session_state.get("old_photos_to_match") and not st.session_state.get("last_parsed_file"):
            uploads_pendentes = True
            mensagem_pendencias.append("o arquivo do monitoramento anterior")
        
    if uploads_pendentes:
        registros_container = st.container(border=True, key="registros_main_container")
        with registros_container:
            st.markdown("### 📝 Cadastro de Registros")
            st.info(f"⚠️ **Cadastro de Registros Suspenso:** Por favor, faça o upload de pendências no topo da página para liberar este painel: **{', e '.join(mensagem_pendencias)}**.")
    else:
        # Preparar fotos antigas de monitoramento (filtrando as que já foram comparadas)
        if is_monitoring and st.session_state.old_photos_to_match:
            fotos_comparadas = {nc["Foto Anterior"] for nc in st.session_state.temp_nc if nc.get("Foto Anterior")}
            old_photos_disponiveis = [
                item for item in st.session_state.old_photos_to_match
                if item["old_photo_path"] not in fotos_comparadas
            ]
        
            if old_photos_disponiveis:
                options_old = [item.get("display_label", item.get("trecho", "Sem Trecho")) for item in old_photos_disponiveis]
                selected_old_key = f"sel_box_old_photo_{st.session_state.nc_form_counter}"
            
                if selected_old_key not in st.session_state or st.session_state[selected_old_key] not in options_old:
                    st.session_state[selected_old_key] = options_old[0]
                
                selected_old_label = st.session_state[selected_old_key]
                current_item = next(
                    (item for item in old_photos_disponiveis if item.get("display_label", item.get("trecho", "")) == selected_old_label),
                    old_photos_disponiveis[0]
                )
                idx = st.session_state.old_photos_to_match.index(current_item)
                st.session_state.carousel_index = idx
            else:
                current_item = None
                idx = 0
                options_old = []
        else:
            old_photos_disponiveis = []
            current_item = None
            idx = 0
            options_old = []
        
        registros_container = st.container(border=True, key="registros_main_container")
        col_inputs, col_preview = registros_container.columns([1.2, 1.0])
    
        with col_preview:
            st.markdown("### 🖼️ Carrossel de Fotos")
            foto_default = ""
            if is_monitoring and st.session_state.old_photos_to_match:
                if current_item:
                    st.markdown(f"**Trecho de Comparação {idx + 1} de {len(st.session_state.old_photos_to_match)}**")
                    col_old, col_new = st.columns(2)
                    with col_old:
                        st.markdown(f"**Foto Anterior ({current_item['id_nc']} - {current_item['trecho']})**")
                        try:
                            from PIL import Image, ImageOps
                            img_old = Image.open(current_item["old_photo_path"])
                            preview_old = ImageOps.fit(img_old, (320, 240))
                            st.image(preview_old, use_container_width=True)
                            st.button("🔍 Ampliar Foto Anterior", on_click=mostrar_foto_modal, args=(current_item["old_photo_path"],), key=f"btn_zoom_old_{idx}_{st.session_state.nc_form_counter}")
                        except Exception:
                            st.image(current_item["old_photo_path"], use_container_width=True)
                    
                        st.selectbox(
                            "Selecione a foto antiga para comparar",
                            options_old,
                            key=selected_old_key
                        )
                    with col_new:
                        st.markdown("**Nova Foto (Atual)**")
                        if st.session_state.fill_photos:
                            new_photo_names = [f.name for f in st.session_state.fill_photos]
                            selected_key = f"sel_box_photo_{idx}_{st.session_state.nc_form_counter}"
                            if selected_key not in st.session_state:
                                st.session_state[selected_key] = st.session_state.fill_photos[min(idx, len(st.session_state.fill_photos)-1)].name
                        
                            current_sel_name = st.session_state[selected_key]
                            if current_sel_name not in new_photo_names:
                                current_sel_name = new_photo_names[0]
                                st.session_state[selected_key] = current_sel_name
                        
                            img_path = next(f for f in st.session_state.fill_photos if f.name == current_sel_name)
                            try:
                                from PIL import Image, ImageOps
                                img_new = Image.open(img_path)
                                preview_new = ImageOps.fit(img_new, (320, 240))
                                st.image(preview_new, use_container_width=True)
                                st.button("🔍 Ampliar Nova Foto", on_click=mostrar_foto_modal, args=(img_path,), key=f"btn_zoom_new_{idx}_{st.session_state.nc_form_counter}")
                            except Exception:
                                st.image(img_path, use_container_width=True)
                        
                            sel_name = st.selectbox(
                                "Selecione a foto correspondente",
                                new_photo_names,
                                key=selected_key
                            )
                            foto_default = sel_name
                        else:
                            st.info("💡 Faça o upload de novas fotos para selecioná-las.")
                            foto_default = ""

                    nav_col1, nav_col2 = st.columns(2)
                    with nav_col1:
                        if st.button("⬅️ Anterior", disabled=(idx == 0), key="btn_prev_photo_mon"):
                            st.session_state.carousel_index = idx - 1
                            st.rerun()
                    with nav_col2:
                        if st.button("Próxima ➡️", disabled=(idx == len(st.session_state.old_photos_to_match) - 1), key="btn_next_photo_mon"):
                            st.session_state.carousel_index = idx + 1
                            st.rerun()

                    st.checkbox(
                        "Avançar foto automaticamente",
                        value=True,
                        key="auto_advance_active",
                        help="Avança para a próxima foto do carrossel ao adicionar o Registro"
                    )
                else:
                    st.success("🎉 Todas as Não Conformidades do monitoramento anterior foram comparadas!")
                    if st.session_state.fill_photos:
                        idx_single = min(st.session_state.carousel_index, len(st.session_state.fill_photos) - 1)
                        current_photo = st.session_state.fill_photos[idx_single]
                        try:
                            from PIL import Image, ImageOps
                            image = Image.open(current_photo)
                            preview_image = ImageOps.fit(image, (400, 300))
                            st.image(preview_image, caption=f"Foto {idx_single + 1} de {len(st.session_state.fill_photos)}: {current_photo.name}")
                        except Exception:
                            st.image(current_photo, caption=f"Foto {idx_single + 1} de {len(st.session_state.fill_photos)}: {current_photo.name}", use_container_width=True)
                        foto_default = current_photo.name
                    else:
                        foto_default = ""
            elif st.session_state.fill_photos:
                idx = st.session_state.carousel_index
                idx = min(idx, len(st.session_state.fill_photos) - 1)
                idx = max(0, idx)
                current_photo = st.session_state.fill_photos[idx]
            
                try:
                    from PIL import Image, ImageOps
                    image = Image.open(current_photo)
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
                st.info("💡 Faça o upload das fotos do levantamento no topo da página para exibi-las aqui.")
                foto_default = ""

        with col_inputs:
            st.markdown("### 📝 Cadastro de Registros")
            if st.session_state.nc_form_step == 1:
                if is_monitoring:
                    id_vinculo = st.selectbox(f"Vincular ao ID {term_fisc_prep}", [f["ID da Fiscalização"] for f in st.session_state.temp_fiscalizacoes] if st.session_state.temp_fiscalizacoes else ["Nenhum ID cadastrado"])
                
                    if st.session_state.old_photos_to_match:
                        idx = st.session_state.carousel_index
                        if idx < len(st.session_state.old_photos_to_match):
                            current_item = st.session_state.old_photos_to_match[idx]
                            st.info(f"📍 **Trecho:** {current_item['trecho']} | **Pista:** {current_item['pista']}\n\n🏷️ **NC:** {current_item['id_nc']}\n\n📝 **Constatação:** {current_item['constatacao']}\n\n📷 **Legenda Anterior:** {current_item['old_legend']}")
                        
                            pista = current_item["pista"]
                            trecho = current_item["trecho"]
                            nc_descricao = [current_item["constatacao"]]
                        else:
                            st.warning("Nenhum item de monitoramento disponível.")
                            st.stop()
                
                    terminal_nc = ""
                    if id_vinculo != "Nenhum ID cadastrado" and st.session_state.temp_fiscalizacoes:
                        for f in st.session_state.temp_fiscalizacoes:
                            if f["ID da Fiscalização"] == id_vinculo:
                                terminal_nc = f["Local"]
                                break
                
                    nc_num = 1
                    if id_vinculo != "Nenhum ID cadastrado" and st.session_state.temp_nc:
                        ncs_existentes = [nc for nc in st.session_state.temp_nc if nc["ID da Fiscalização"] == id_vinculo]
                        nc_num = len(ncs_existentes) + 1
                
                    situacao = st.pills(
                        "Situação",
                        ["Pendente", "Parcialmente Sanada", "Sanada"],
                        selection_mode="single",
                        key=f"nc_situacao_{st.session_state.nc_form_counter}",
                        default="Pendente"
                    )
                
                    ponto_atencao = []
                    nc_legenda = st.text_area("Legenda da Foto Atual", key=f"nc_obs_{st.session_state.nc_form_counter}", placeholder="Escreva a legenda da foto atual...")
                
                    if st.session_state.get("tipo_relatorio", "CRA") == "CRC" and is_monitoring and current_item:
                        st.markdown("#### 📝 Corpo do Relatório")
                    
                        saved_rec = next(
                            (r for r in st.session_state.temp_nc
                             if r["Identificação"] == current_item["id_nc"] 
                             and r["ID da Fiscalização"] == id_vinculo),
                            None
                        )
                    
                        default_pos_crc = saved_rec.get("Determinação", "") if saved_rec else ""
                        default_constatacao = saved_rec.get("Observações", current_item["constatacao"]) if saved_rec else current_item["constatacao"]
                        default_analise_arpe = saved_rec.get("Análise ARPE", "") if saved_rec else ""
                    
                        col_pos, col_const, col_analise = st.columns(3)
                        with col_pos:
                            pos_crc = st.text_area(
                                "POSICIONAMENTO CRC",
                                value=default_pos_crc,
                                key=f"pos_crc_step1_{st.session_state.nc_form_counter}",
                                placeholder="Digite o posicionamento da CRC...",
                                height=160
                            )
                        with col_const:
                            constatacao = st.text_area(
                                "CONSTATAÇÃO",
                                value=default_constatacao,
                                key=f"constatacao_step1_{st.session_state.nc_form_counter}",
                                placeholder="Digite a constatação...",
                                height=160
                            )
                        with col_analise:
                            analise_arpe = st.text_area(
                                "ANÁLISE ARPE",
                                value=default_analise_arpe,
                                key=f"analise_arpe_step1_{st.session_state.nc_form_counter}",
                                placeholder="Digite a análise da ARPE...",
                                height=160
                            )
                else:
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
                    
                    if st.session_state.get("tipo_relatorio", "CRA") == "CRA" and not is_monitoring:
                        tipo_registro = st.pills(
                            "Tipo de Registro",
                            ["Não Conformidade", "Ponto de Atenção"],
                            selection_mode="single",
                            key=f"nc_tipo_{st.session_state.nc_form_counter}",
                            default="Não Conformidade"
                        )
                    else:
                        tipo_registro = "Não Conformidade"

                    situacao = "Pendente"

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
                            if st.button("+", key=f"btn_add_custom_pa_{st.session_state.nc_form_counter}", help="Adicionar Não Conformidade Personalizada", use_container_width=True):
                                adicionar_nc_personalizada_modal(pa_key)
                        nc_descricao = []
                
                    nc_legenda = st.text_area("Observações", key=f"nc_obs_{st.session_state.nc_form_counter}", placeholder="Escreva as observações/legenda correspondente...")
            
                if is_monitoring and not current_item:
                    # Se for monitoramento e já comparou tudo, não exibe os botões de ação
                    pass
                else:
                    if st.session_state.get("tipo_relatorio", "CRA") == "CRC" and is_monitoring:
                        col_save_direct, _ = st.columns([2.5, 7.5], gap="small")
                        with col_save_direct:
                            if st.button("💾 Salvar e Continuar", type="primary", use_container_width=True, key=f"btn_save_crc_mon_step1_{st.session_state.nc_form_counter}"):
                                if id_vinculo == "Nenhum ID cadastrado":
                                    st.error(f"Adicione uma {term_fisc_lower} primeiro.")
                                elif not foto_default:
                                    st.error("É obrigatório ter uma foto selecionada no carrossel para continuar.")
                                else:
                                    # Validação para CRC Monitoramento
                                    campos_vazios = []
                                    if not pos_crc.strip():
                                        campos_vazios.append("POSICIONAMENTO CRC")
                                    if not constatacao.strip():
                                        campos_vazios.append("CONSTATAÇÃO")
                                    if not analise_arpe.strip():
                                        campos_vazios.append("ANÁLISE ARPE")
                                    
                                    if campos_vazios:
                                        st.error(f"❌ Não foi possível salvar. Os seguintes campos estão em branco: {', '.join(campos_vazios)}")
                                    else:
                                        # 1. Tentar encontrar registro com a mesma foto anterior
                                        rec = next((r for r in st.session_state.temp_nc 
                                                    if r["Identificação"] == current_item["id_nc"] 
                                                    and r["Foto Anterior"] == current_item["old_photo_path"] 
                                                    and r["ID da Fiscalização"] == id_vinculo), None)
                                    
                                        # 2. Se não encontrou, tentar encontrar um registro com foto anterior vazia
                                        if not rec:
                                            rec = next((r for r in st.session_state.temp_nc 
                                                        if r["Identificação"] == current_item["id_nc"] 
                                                        and not r.get("Foto Anterior") 
                                                        and r["ID da Fiscalização"] == id_vinculo), None)
                                    
                                        # 3. Se ainda assim não encontrou, cria um novo
                                        if not rec:
                                            rec = {
                                                "ID da Fiscalização": id_vinculo,
                                                "Nº": nc_num,
                                                "Terminal": terminal_nc,
                                                "Pista": pista,
                                                "Trecho": trecho,
                                                "Não Conformidade": ", ".join(nc_descricao) if nc_descricao else "",
                                                "Ponto de Atenção": "",
                                                "Foto": foto_default,
                                                "Foto Anterior": current_item["old_photo_path"],
                                                "Legenda Anterior": current_item["old_legend"],
                                                "Observações": constatacao,
                                                "Identificação": current_item["id_nc"],
                                                "Direção (faixa)": "",
                                                "Fundamento da infração": "",
                                                "Determinação": pos_crc,
                                                "Situação": situacao,
                                                "Análise ARPE": analise_arpe
                                            }
                                            st.session_state.temp_nc.append(rec)
                                        else:
                                            # Atualiza registro existente
                                            rec["Foto"] = foto_default
                                            rec["Foto Anterior"] = current_item["old_photo_path"]
                                            rec["Legenda Anterior"] = current_item["old_legend"]
                                            rec["Observações"] = constatacao
                                            rec["Determinação"] = pos_crc
                                            rec["Situação"] = situacao
                                            rec["Análise ARPE"] = analise_arpe

                                        # Sincronizar textos para todas as ocorrências de foto para a mesma Identificação (CRC)
                                        recs_same_ident = [r for r in st.session_state.temp_nc 
                                                           if r["Identificação"] == current_item["id_nc"] 
                                                           and r["ID da Fiscalização"] == id_vinculo]
                                        for r_same in recs_same_ident:
                                            r_same["Determinação"] = pos_crc
                                            r_same["Observações"] = constatacao
                                            r_same["Análise ARPE"] = analise_arpe

                                        # Avançar carrossel automaticamente se houver próxima foto e a opção estiver ativada
                                        if st.session_state.carousel_index < len(st.session_state.old_photos_to_match) - 1:
                                            st.session_state.carousel_index += 1
                                        
                                        st.session_state.nc_form_counter += 1
                                        st.success("Registro salvo com sucesso!")
                                        st.rerun()
                    else:
                        # Definir largura das colunas baseadas no tipo de relatório (sem col_rel para monitoramento)
                        if is_monitoring:
                            col_nxt, _ = st.columns([1.7, 8.3], gap="small")
                        else:
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
                                    st.session_state.step1_situacao = situacao
                                    if is_monitoring and st.session_state.old_photos_to_match:
                                        st.session_state.step1_foto_anterior = current_item["old_photo_path"]
                                        st.session_state.step1_legenda_anterior = current_item["old_legend"]
                                        st.session_state.step1_identificacao = current_item["id_nc"]
                                    else:
                                        st.session_state.step1_foto_anterior = ""
                                        st.session_state.step1_legenda_anterior = ""
                                        st.session_state.step1_identificacao = ""
                                
                                    st.session_state.nc_form_step = 2
                                    st.rerun()
                    
                        if not is_monitoring:
                            with col_rel:
                                disable_rel = len(st.session_state.temp_nc) == 0
                                if st.button("🔗 Relacionar", type="secondary", disabled=disable_rel, use_container_width=True):
                                    if not foto_default:
                                        st.error("É obrigatório ter uma foto selecionada no carrossel para relacionar.")
                                    else:
                                        last_nc = st.session_state.temp_nc[-1]
                                        target_id = last_nc["ID da Fiscalização"]
                                        ncs_existentes = [nc for nc in st.session_state.temp_nc if nc["ID da Fiscalização"] == target_id]
                                        new_nc_num = len(ncs_existentes) + 1
                                    
                                        new_nc = last_nc.copy()
                                        new_nc["Foto"] = foto_default
                                        new_nc["Nº"] = new_nc_num
                                        new_nc["Situação"] = situacao
                                    
                                        st.session_state.temp_nc.append(new_nc)
                                    
                                        if st.session_state.get("auto_advance_active", True) and st.session_state.fill_photos and st.session_state.carousel_index < len(st.session_state.fill_photos) - 1:
                                            st.session_state.carousel_index += 1
                                        
                                        st.session_state.pista_persistida = new_nc.get("Pista", "")
                                        st.session_state.trecho_persistido = new_nc.get("Trecho", "")
                                    
                                        st.session_state.nc_form_counter += 1
                                        st.success("Informações da última foto relacionadas com sucesso!")
                                        st.rerun()
            else:
                if is_monitoring and st.session_state.get("step1_identificacao"):
                    identificacao = st.text_input("Identificação", value=st.session_state.step1_identificacao, disabled=True)
                else:
                    identificacao = st.text_input("Identificação", key=f"nc_ident_{st.session_state.nc_form_counter}", placeholder="Identificação da infração...")
                
                if st.session_state.get("tipo_relatorio", "CRA") == "CRA":
                    direcao_faixa = st.text_input("Direção (faixa)", key=f"nc_dir_{st.session_state.nc_form_counter}", placeholder="Direção/faixa...")
                else:
                    direcao_faixa = ""
                fundamento_infracao = st.text_input("Fundamento da infração", key=f"nc_fund_{st.session_state.nc_form_counter}", placeholder="Fundamento legal...")
                determinacao = st.text_input("Determinação", key=f"nc_det_{st.session_state.nc_form_counter}", placeholder="Determinação/Ação recomendada...")
                observacoes_crc = st.session_state.step1_nc_legenda
                analise_arpe = ""
            
                situacao = st.session_state.get("step1_situacao", "Pendente")
            
                col_back, col_add, _ = st.columns([1.1, 1.3, 7.6], gap="small")
                with col_back:
                    if st.button("↩️ Voltar", type="secondary", use_container_width=True):
                        st.session_state.nc_form_step = 1
                        st.rerun()
                with col_add:
                    btn_label = "💾 Salvar e Continuar" if st.session_state.get("tipo_relatorio", "CRA") == "CRC" and is_monitoring else "➕ Adicionar"
                    if st.button(btn_label, type="primary", use_container_width=True):
                        if st.session_state.get("tipo_relatorio", "CRA") == "CRC" and is_monitoring:
                            campos_vazios = []
                            _pos_crc = locals().get("pos_crc", "")
                            _constatacao = locals().get("constatacao", "")
                            _analise_arpe = locals().get("analise_arpe", "")

                            if not _pos_crc.strip():
                                campos_vazios.append("POSICIONAMENTO CRC")
                            if not _constatacao.strip():
                                campos_vazios.append("CONSTATAÇÃO")
                            if not _analise_arpe.strip():
                                campos_vazios.append("ANÁLISE ARPE")
                            
                            if campos_vazios:
                                st.warning(f"⚠️ Atenção: Os seguintes campos de texto da CRC estão vazios: {', '.join(campos_vazios)}.")
                    
                        # 1. Tentar encontrar registro com a mesma foto anterior
                        rec = next((r for r in st.session_state.temp_nc 
                                    if r["Identificação"] == identificacao 
                                    and r["Foto Anterior"] == st.session_state.get("step1_foto_anterior", "") 
                                    and r["ID da Fiscalização"] == st.session_state.step1_id_vinculo), None)
                    
                        # 2. Se não encontrou, tentar encontrar um registro com foto anterior vazia
                        if not rec:
                            rec = next((r for r in st.session_state.temp_nc 
                                        if r["Identificação"] == identificacao 
                                        and not r.get("Foto Anterior") 
                                        and r["ID da Fiscalização"] == st.session_state.step1_id_vinculo), None)
                    
                        # 3. Se ainda assim não encontrou, cria um novo
                        if not rec:
                            rec = {
                                "ID da Fiscalização": st.session_state.step1_id_vinculo,
                                "Nº": st.session_state.step1_nc_num,
                                "Terminal": st.session_state.step1_terminal_nc,
                                "Pista": st.session_state.step1_pista,
                                "Trecho": st.session_state.step1_trecho,
                                "Não Conformidade": st.session_state.step1_nc_desc_str,
                                "Ponto de Atenção": st.session_state.step1_pa_desc_str,
                                "Foto": st.session_state.step1_foto_default,
                                "Foto Anterior": st.session_state.get("step1_foto_anterior", ""),
                                "Legenda Anterior": st.session_state.get("step1_legenda_anterior", ""),
                                "Observações": observacoes_crc,
                                "Identificação": identificacao,
                                "Direção (faixa)": direcao_faixa,
                                "Fundamento da infração": fundamento_infracao,
                                "Determinação": determinacao,
                                "Situação": situacao,
                                "Análise ARPE": analise_arpe
                            }
                            st.session_state.temp_nc.append(rec)
                        else:
                            # Atualiza registro existente
                            rec["Foto"] = st.session_state.step1_foto_default
                            rec["Foto Anterior"] = st.session_state.get("step1_foto_anterior", "")
                            rec["Legenda Anterior"] = st.session_state.get("step1_legenda_anterior", "")
                            rec["Observações"] = observacoes_crc
                            rec["Determinação"] = determinacao
                            rec["Situação"] = situacao
                            rec["Análise ARPE"] = analise_arpe

                        # Sincronizar textos para todas as ocorrências de foto para a mesma Identificação (CRC)
                        if st.session_state.get("tipo_relatorio", "CRA") == "CRC" and is_monitoring:
                            recs_same_ident = [r for r in st.session_state.temp_nc 
                                               if r["Identificação"] == identificacao 
                                               and r["ID da Fiscalização"] == st.session_state.step1_id_vinculo]
                            for r_same in recs_same_ident:
                                r_same["Determinação"] = determinacao
                                r_same["Observações"] = observacoes_crc
                                r_same["Análise ARPE"] = analise_arpe

                        # Avançar carrossel automaticamente se houver próxima foto e a opção estiver ativada
                        if is_monitoring and st.session_state.old_photos_to_match:
                            if st.session_state.carousel_index < len(st.session_state.old_photos_to_match) - 1:
                                st.session_state.carousel_index += 1
                        else:
                            if st.session_state.get("auto_advance_active", True) and st.session_state.fill_photos and st.session_state.carousel_index < len(st.session_state.fill_photos) - 1:
                                st.session_state.carousel_index += 1
                        
                        # Salvar valores atuais de pista e trecho para que persistam no formulário
                        st.session_state.pista_persistida = st.session_state.step1_pista
                        st.session_state.trecho_persistido = st.session_state.step1_trecho
                    
                        st.session_state.nc_form_counter += 1
                        st.session_state.nc_form_step = 1
                        st.success(f"Adicionado com sucesso ao ID {st.session_state.step1_id_vinculo}!")
                        st.rerun()



    
    st.write("")
    acoes_container = st.container(border=True, key="acoes_panel_container")
    with acoes_container:
        st.subheader("🛠️ Painel de Ações do Relatório")
        
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
                    confirmar_exclusao_lote_modal(ids_para_excluir, term_fisc_plural_lower, term_fisc_plural)
                    
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
                        for c in ['Situação', 'Foto', 'Fotos', 'Observações', 'Legenda da Foto', 'Análise ARPE']:
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
                    excel_buffer = gerar_planilha_excel_buffer(
                        st.session_state.temp_fiscalizacoes,
                        st.session_state.temp_nc
                    )

                    # 2. Criar diretório temporário para as fotos já enviadas
                    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
                        fotos_dir = os.path.join(temp_dir, "fotos")
                        reports_dir = os.path.join(temp_dir, "reports")
                        os.makedirs(fotos_dir, exist_ok=True)
                        os.makedirs(reports_dir, exist_ok=True)

                        if "fill_photos" in st.session_state and st.session_state.fill_photos:
                            salvar_fotos_em_diretorio(st.session_state.fill_photos, fotos_dir)

                        try:
                            tipo_key = st.session_state.get("tipo_relatorio", "CRA")
                            if st.session_state.get("categoria_relatorio", "Fiscalização") == "Monitoramento":
                                tipo_key = f"{tipo_key}_MONITORAMENTO"

                            if tipo_key == "CRC_MONITORAMENTO" and not uploaded_mon_anterior:
                                st.error("❌ Por favor, faça o upload do arquivo do monitoramento anterior (.docx) para gerar o relatório CRC Monitoramento.")
                                st.stop()

                            arquivos_gerados, _ = gerar_relatorio(
                                caminho_planilha=excel_buffer,
                                fotos_dir=fotos_dir,
                                relatorios_dir=reports_dir,
                                gerar_todos=True,
                                tipo_relatorio=tipo_key,
                                documento_anterior=uploaded_mon_anterior
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
            if not st.session_state.temp_fiscalizacoes:
                st.error(f"Adicione pelo menos um{'' if is_monitoring else 'a'} {term_fisc_lower} primeiro.")
            else:
                output_buffer = gerar_planilha_excel_buffer(
                    st.session_state.temp_fiscalizacoes,
                    st.session_state.temp_nc
                )
                st.session_state.planilha_download_bytes = output_buffer.getvalue()
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
        if st.button("🗑️ Limpar Registros", type="secondary", use_container_width=True, key="btn_clear_all_data"):
            # Mantém st.session_state.temp_fiscalizacoes e os campos de preenchimento de ID intactos
            st.session_state.temp_nc = []
            st.session_state.relatorios_preenchimento_data = []
            if "planilha_download_bytes" in st.session_state:
                del st.session_state.planilha_download_bytes
            st.session_state.photos_uploader_version += 1
            st.session_state.fill_photos = []
            if "carousel_index" in st.session_state:
                st.session_state.carousel_index = 0
            st.session_state.pista_persistida = ""
            st.session_state.trecho_persistido = ""
            st.rerun()

    # Exibir botões de download dos relatórios se gerados
    if st.session_state.relatorios_preenchimento_data:
        st.write("") # Espaçamento
        st.write("### 📥 Baixar Relatórios Gerados")
        with st.container(border=True, key="downloads_section_container"):
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

st.info("Nota: Use a aba 'Preencher Planilha' para montar seus dados e depois a aba 'Gerador' para processar os documentos.")
