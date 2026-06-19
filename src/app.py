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

# Abas principais da aplicação
tab_gerador, tab_preenchimento = st.tabs(["🚀 Gerador de Relatórios", "📝 Preencher Planilha"])

with tab_gerador:
    st.write("Faça o upload da planilha e das fotos para gerar os relatórios.")

    # Download do Modelo
    with st.expander("📌 Ajuda e Modelo de Planilha"):
        st.write("""
        A planilha deve conter as seguintes colunas na primeira aba:
        - **ID da Fiscalização**: Identificador único.
        - **Contrato**: Número do contrato.
        - **Data**: Data da fiscalização.
        - **Local**: Cidade ou Terminal.
        - **Relatório Gerado**: (Opcional) Coluna de status.
        """)
        template_path = os.path.join(os.path.dirname(__file__), "planilha_fiscalizacao.xlsx")
        if os.path.exists(template_path):
            with open(template_path, "rb") as f:
                st.download_button(
                    label="📥 Baixar Modelo de Planilha (Base)",
                    data=f,
                    file_name="planilha_fiscalizacao.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.error("⚠️ Arquivo de modelo não encontrado.")

    # Upload da Planilha
    uploaded_excel = st.file_uploader("Selecione a planilha Excel (.xlsx)", type=["xlsx"])

    # Upload das Fotos
    uploaded_photos = st.file_uploader("Selecione as fotos (múltiplos arquivos)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    regenerar_todos = st.checkbox(
        "Regenerar relatórios já marcados como gerados",
        help="Ative se a planilha já foi processada antes e todas as linhas estão com 'Relatório Gerado' = VERDADEIRO.",
    )

    # Inicializar estado da sessão para persistir dados entre cliques
    if "arquivos_gerados_data" not in st.session_state:
        st.session_state.arquivos_gerados_data = []
    if "planilha_atualizada_data" not in st.session_state:
        st.session_state.planilha_atualizada_data = None

    if st.button("🚀 Gerar Relatório"):
        if not uploaded_excel:
            st.error("⚠️ Por favor, faça o upload da planilha Excel.")
        elif not uploaded_photos:
            st.warning("⚠️ Nenhuma foto foi carregada. O relatório será gerado sem imagens.")
        
        with st.spinner("Processando relatórios... Isso pode levar alguns minutos."):
                st.session_state.arquivos_gerados_data = []
                st.session_state.planilha_atualizada_data = None
                
                with tempfile.TemporaryDirectory() as temp_dir:
                    fotos_dir = os.path.join(temp_dir, "fotos")
                    reports_dir = os.path.join(temp_dir, "reports")
                    os.makedirs(fotos_dir, exist_ok=True)
                    os.makedirs(reports_dir, exist_ok=True)

                    for photo in uploaded_photos:
                        with open(os.path.join(fotos_dir, photo.name), "wb") as f:
                            f.write(photo.getbuffer())

                    try:
                        arquivos_gerados, planilha_atualizada = gerar_relatorio(
                            caminho_planilha=uploaded_excel,
                            fotos_dir=fotos_dir,
                            relatorios_dir=reports_dir,
                            gerar_todos=regenerar_todos
                        )

                        if not arquivos_gerados:
                            st.warning("Nenhum relatório pendente encontrado.")
                        else:
                            for arquivo in arquivos_gerados:
                                nome_base = os.path.basename(arquivo)
                                with open(arquivo, "rb") as f:
                                    st.session_state.arquivos_gerados_data.append({
                                        "nome": nome_base,
                                        "bytes": f.read()
                                    })
                            
                            if planilha_atualizada:
                                st.session_state.planilha_atualizada_data = planilha_atualizada.getvalue()
                            
                            st.success(f"✅ {len(arquivos_gerados)} arquivo(s) gerado(s) com sucesso!")
                    
                    except Exception as e:
                        st.error(f"❌ Erro: {e}")
                        st.exception(e)

    if st.session_state.arquivos_gerados_data:
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📥 Relatórios")
            for i, item in enumerate(st.session_state.arquivos_gerados_data):
                st.download_button(
                    label=f"Baixar {item['nome']}",
                    data=item["bytes"],
                    file_name=item["nome"],
                    key=f"dl_{i}_{item['nome']}"
                )
        with col2:
            if st.session_state.planilha_atualizada_data:
                st.subheader("📊 Planilha Atualizada")
                st.download_button(
                    label="Baixar Planilha Atualizada",
                    data=st.session_state.planilha_atualizada_data,
                    file_name="planilha_fiscalizacao_atualizada.xlsx"
                )

with tab_preenchimento:
    st.header("📝 Cadastro de Fiscalização")
    st.write("Preencha os dados abaixo para gerar a planilha formatada.")

    if "temp_fiscalizacoes" not in st.session_state:
        st.session_state.temp_fiscalizacoes = []
    if "temp_nc" not in st.session_state:
        st.session_state.temp_nc = []

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
        st.markdown("### 🖼️ Pré-visualização da Foto")
        uploaded_nc_photo = st.file_uploader(
            "Selecione a foto correspondente para visualizar e preencher automaticamente o nome do arquivo", 
            type=["jpg", "jpeg", "png"],
            key="nc_photo_uploader"
        )
        if uploaded_nc_photo:
            try:
                from PIL import Image, ImageOps
                image = Image.open(uploaded_nc_photo)
                # Ajusta a foto para caber exatamente em um box padrão de 400x300 mantendo a proporção e cortando o excesso
                preview_image = ImageOps.fit(image, (400, 300))
                st.image(preview_image, caption=f"Visualização (Tamanho Padrão): {uploaded_nc_photo.name}")
                st.button("🔍 Clique para ampliar a foto", on_click=mostrar_foto_modal, args=(uploaded_nc_photo,), key="btn_zoom_photo")
            except Exception as e:
                st.image(uploaded_nc_photo, caption=f"Visualização: {uploaded_nc_photo.name}", use_container_width=True)
            foto_default = uploaded_nc_photo.name
        else:
            st.info("💡 Faça o upload de uma foto para visualizá-la aqui em tamanho mediano enquanto descreve a não conformidade.")
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
            
        nc_descricao = st.text_area("Não Conformidade", placeholder="Descreva os problemas encontrados...")
        nc_legenda = st.text_area("Observações", placeholder="Escreva as observações/legenda correspondente...")
        
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
                st.success(f"NC {nc_num} adicionada ao ID {id_vinculo}!")

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
        
        if st.button("🗑️ Limpar Tudo", type="secondary"):
            st.session_state.temp_fiscalizacoes = []
            st.session_state.temp_nc = []
            st.rerun()

st.divider()
st.info("Nota: Use a aba 'Preencher Planilha' para montar seus dados e depois a aba 'Gerador' para processar os documentos.")
