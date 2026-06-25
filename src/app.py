import streamlit as st
import os
import tempfile
import pandas as pd
import io
from datetime import datetime
from report import gerar_relatorio
st.set_page_config(page_title="Gerador de Relatórios ARPE", layout="wide")

@st.dialog("Visualização Completa da Imagem", width="large")
def mostrar_foto_modal(uploaded_file):
    st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

st.title("📄 Gerador de Relatórios de Fiscalização")

# Layout principal da aplicação
with st.container():

    # 1. Upload de Fotos do Levantamento no início
    st.subheader("📸 Upload de Fotos do Levantamento")
    
    if "fill_photos_sort_option" not in st.session_state:
        st.session_state.fill_photos_sort_option = "Ordem de Upload"

    col_uploader, col_sort = st.columns([3, 1])
    with col_uploader:
        uploaded_nc_photos = st.file_uploader(
            "Faça o upload de todas as fotos da fiscalização para usá-las no carrossel de Não Conformidades", 
            type=["jpg", "jpeg", "png"], 
            accept_multiple_files=True,
            key="fill_photos_uploader"
        )
    with col_sort:
        st.write("") # Alinhamento vertical discreto
        st.write("**Ordenar Fotos por:**")
        with st.popover(f"↕️ {st.session_state.fill_photos_sort_option}", use_container_width=True):
            if st.button("Ordem de Upload", use_container_width=True, key="btn_sort_upload"):
                st.session_state.fill_photos_sort_option = "Ordem de Upload"
                st.rerun()
            if st.button("Nome (A-Z / 0-9)", use_container_width=True, key="btn_sort_asc"):
                st.session_state.fill_photos_sort_option = "Nome (A-Z / 0-9)"
                st.rerun()
            if st.button("Nome (Z-A / 9-0)", use_container_width=True, key="btn_sort_desc"):
                st.session_state.fill_photos_sort_option = "Nome (Z-A / 9-0)"
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

    with st.form("form_fiscalizacao"):
        col1, col2 = st.columns(2)
        with col1:
            id_fisc = st.text_input("ID da Fiscalização (ex: 2026-001)", help="Identificador único para vincular as abas")
            data_fisc = st.text_input("Data (ex: 15/06/2026)", placeholder="dd/mm/aaaa")
            hora = st.text_input("Hora (ex: 10:00)", placeholder="Opcional")
            cidade = st.text_input("Cidade (ex: Recife)", placeholder="Cidade do Terminal")
            local = st.text_input("Local (ex: TIP (RECIFE))", placeholder="Nome do Terminal")
        with col2:
            responsaveis = st.text_input("Pessoal Responsável (ex: Nome 1, Nome 2)", placeholder="Investigadores")
            coordenador = st.text_input("Coordenador", placeholder="Nome do Coordenador")
            contrato = st.text_input("Número do Contrato", value="1.041.080/08")
            periodo = st.text_input("Período (ex: 15 a 18/06/2026)", placeholder="Opcional")

        submit_fisc = st.form_submit_button("➕ Adicionar Fiscalização")
        if submit_fisc:
            if not id_fisc:
                st.error("O ID da Fiscalização é obrigatório.")
            else:
                # Preenche as assinaturas automaticamente a partir do Pessoal Responsável
                assinaturas_auto = responsaveis.replace(",", ";") if responsaveis else ""
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
                    "Assinatura": assinaturas_auto,
                    "Relatório Gerado": False
                })
                st.success(f"Fiscalização {id_fisc} adicionada!")

    st.divider()
    st.subheader("🚩 Não Conformidades (NC)")
    
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
                help="Avança para a próxima foto do carrossel ao adicionar a Não Conformidade"
            )
            
            foto_default = current_photo.name
        else:
            st.info("💡 Faça o upload de fotos no início da página para visualizá-las aqui no carrossel de Não Conformidades.")
            foto_default = ""

    with col_inputs:
        id_vinculo = st.selectbox("Vincular ao ID da Fiscalização", [f["ID da Fiscalização"] for f in st.session_state.temp_fiscalizacoes] if st.session_state.temp_fiscalizacoes else ["Nenhum ID cadastrado"])
        
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
            
        nc_options = ["FI", "TTC", "TTL", "TLC", "TLL", "TRR", "J", "TB", "JE", "TBE", "ALP", "ATP", "O", "P", "EX", "D", "R", "ALC", "ATC", "E"]
        nc_descricao = st.pills("Não Conformidade", nc_options, key=f"nc_desc_{st.session_state.nc_form_counter}")
        nc_legenda = st.text_area("Observações", key=f"nc_obs_{st.session_state.nc_form_counter}", placeholder="Escreva as observações/legenda correspondente...")
        
        if st.button("➕ Adicionar Não Conformidade", type="primary"):
            if id_vinculo == "Nenhum ID cadastrado":
                st.error("Adicione uma fiscalização primeiro.")
            elif not nc_descricao:
                st.error("O campo 'Não Conformidade' é obrigatório.")
            else:
                st.session_state.temp_nc.append({
                    "ID da Fiscalização": id_vinculo,
                    "Nº": nc_num,
                    "Terminal": terminal_nc,
                    "Não Conformidade": nc_descricao,
                    "Foto": foto_default,
                    "Observações": nc_legenda
                })
                # Avançar carrossel automaticamente se houver próxima foto e a opção estiver ativada
                if st.session_state.get("auto_advance_active", True) and st.session_state.fill_photos and st.session_state.carousel_index < len(st.session_state.fill_photos) - 1:
                    st.session_state.carousel_index += 1
                
                st.session_state.nc_form_counter += 1
                st.success(f"NC {nc_num} adicionada ao ID {id_vinculo}!")
                st.rerun()

    st.divider()
    if st.session_state.temp_fiscalizacoes:
        st.subheader("📋 Resumo do Preenchimento")
        st.write("**Fiscalizações:**", pd.DataFrame(st.session_state.temp_fiscalizacoes))
        st.write("**Não Conformidades:**", pd.DataFrame(st.session_state.temp_nc))
        
        if st.button("💾 Gerar Planilha Completa"):
            # Vincular Não Conformidades e Observações à planilha Fiscalizações logo após a coluna Período
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
                        "Assinatura": fisc["Assinatura"],
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
                            "Assinatura": fisc["Assinatura"],
                            "Relatório Gerado": fisc["Relatório Gerado"]
                        })

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                pd.DataFrame(flat_fiscalizacoes).to_excel(writer, sheet_name="Fiscalizações", index=False)
                pd.DataFrame(st.session_state.temp_nc).to_excel(writer, sheet_name="Não-conformidades ", index=False)
                pd.DataFrame().to_excel(writer, sheet_name="Observações Importantes", index=False)
                pd.DataFrame().to_excel(writer, sheet_name="Recomendações", index=False)

            st.download_button(
                label="📥 Baixar Planilha Preenchida",
                data=output.getvalue(),
                file_name=f"planilha_gerada_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        # Inicializar estado para persistir os relatórios gerados via aba preenchimento
        if "relatorios_preenchimento_data" not in st.session_state:
            st.session_state.relatorios_preenchimento_data = []

        if st.button("🚀 Gerar Relatório Automático", type="primary"):
            if not st.session_state.temp_fiscalizacoes:
                st.error("Adicione pelo menos uma fiscalização primeiro.")
            else:
                with st.spinner("Gerando relatórios automaticamente..."):
                    st.session_state.relatorios_preenchimento_data = []
                    
                    # 1. Gerar a planilha em memória
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
                                "Assinatura": fisc["Assinatura"],
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
                                    "Assinatura": fisc["Assinatura"],
                                    "Relatório Gerado": fisc["Relatório Gerado"]
                                })

                    excel_buffer = io.BytesIO()
                    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                        pd.DataFrame(flat_fiscalizacoes).to_excel(writer, sheet_name="Fiscalizações", index=False)
                        pd.DataFrame(st.session_state.temp_nc).to_excel(writer, sheet_name="Não-conformidades ", index=False)
                        pd.DataFrame().to_excel(writer, sheet_name="Observações Importantes", index=False)
                        pd.DataFrame().to_excel(writer, sheet_name="Recomendações", index=False)
                    excel_buffer.seek(0)

                    # 2. Criar diretório temporário para as fotos já enviadas (st.session_state.fill_photos)
                    with tempfile.TemporaryDirectory() as temp_dir:
                        fotos_dir = os.path.join(temp_dir, "fotos")
                        reports_dir = os.path.join(temp_dir, "reports")
                        os.makedirs(fotos_dir, exist_ok=True)
                        os.makedirs(reports_dir, exist_ok=True)

                        # Copiar as fotos salvas em st.session_state.fill_photos
                        if "fill_photos" in st.session_state and st.session_state.fill_photos:
                            for photo in st.session_state.fill_photos:
                                with open(os.path.join(fotos_dir, photo.name), "wb") as f:
                                    f.write(photo.getbuffer())

                        # 3. Chamar a função gerar_relatorio
                        try:
                            arquivos_gerados, _ = gerar_relatorio(
                                caminho_planilha=excel_buffer,
                                fotos_dir=fotos_dir,
                                relatorios_dir=reports_dir,
                                gerar_todos=True
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
                                st.success(f"✅ {len(arquivos_gerados) // 2} relatório(s) completo(s) (Word + PDF) gerado(s) com sucesso!")
                        except Exception as e:
                            st.error(f"❌ Erro ao gerar relatórios: {e}")
                            st.exception(e)

        # Exibir botões de download dos relatórios se gerados
        if st.session_state.relatorios_preenchimento_data:
            st.write("### 📥 Baixar Relatórios Gerados")
            col1, col2 = st.columns(2)
            docx_files = [x for x in st.session_state.relatorios_preenchimento_data if x["nome"].endswith(".docx")]
            pdf_files = [x for x in st.session_state.relatorios_preenchimento_data if x["nome"].endswith(".pdf")]
            
            with col1:
                st.write("**Documentos Word (.docx):**")
                for i, item in enumerate(docx_files):
                    st.download_button(
                        label=f"Baixar {item['nome']}",
                        data=item["bytes"],
                        file_name=item["nome"],
                        key=f"dl_fill_docx_{i}_{item['nome']}"
                    )
            with col2:
                st.write("**Documentos PDF (.pdf):**")
                for i, item in enumerate(pdf_files):
                    st.download_button(
                        label=f"Baixar {item['nome']}",
                        data=item["bytes"],
                        file_name=item["nome"],
                        key=f"dl_fill_pdf_{i}_{item['nome']}"
                    )

        if st.button("🗑️ Limpar Tudo", type="secondary"):
            st.session_state.temp_fiscalizacoes = []
            st.session_state.temp_nc = []
            st.session_state.relatorios_preenchimento_data = []
            st.rerun()

st.divider()
st.info("Nota: Use a aba 'Preencher Planilha' para montar seus dados e depois a aba 'Gerador' para processar os documentos.")
