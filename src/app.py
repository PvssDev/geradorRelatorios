import streamlit as st
import os
import tempfile
from report import gerar_relatorio

st.set_page_config(page_title="Gerador de Relatórios ARPE", layout="centered")

st.title("📄 Gerador de Relatórios de Fiscalização")
st.write("Faça o upload da planilha e das fotos para gerar os relatórios.")

# Download do Modelo
with st.expander("📌 Ajuda e Modelo de Planilha"):
    st.write("""
    A planilha deve conter as seguintes colunas na primeira aba:
    - **ID da Fiscalização**: Identificador único.
    - **Contrato**: Número do contrato.
    - **Data**: Data da fiscalização.
    - **Local**: Cidade ou Terminal.
    - **Relatório Gerado**: (Opcional) Coluna de status — deixe em branco ou **FALSO** para gerar; **VERDADEIRO** indica que já foi gerado.
    """)
    template_path = os.path.join(os.path.dirname(__file__), "modelo_base.xlsx")
    if os.path.exists(template_path):
        with open(template_path, "rb") as f:
            st.download_button(
                label="📥 Baixar Modelo de Planilha (Limpo)",
                data=f,
                file_name="modelo_planilha_fiscalizacao.xlsx",
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
    
    if uploaded_excel:
        with st.spinner("Processando relatórios... Isso pode levar alguns minutos."):
            # Limpar resultados anteriores
            st.session_state.arquivos_gerados_data = []
            st.session_state.planilha_atualizada_data = None
            
            # Criar diretório temporário para as fotos
            with tempfile.TemporaryDirectory() as temp_dir:
                fotos_dir = os.path.join(temp_dir, "fotos")
                reports_dir = os.path.join(temp_dir, "reports")
                os.makedirs(fotos_dir, exist_ok=True)
                os.makedirs(reports_dir, exist_ok=True)

                # Salvar fotos enviadas no diretório temporário
                for photo in uploaded_photos:
                    with open(os.path.join(fotos_dir, photo.name), "wb") as f:
                        f.write(photo.getbuffer())

                try:
                    # Chamar a lógica de geração de relatório
                    arquivos_gerados, planilha_atualizada = gerar_relatorio(
                        caminho_planilha=uploaded_excel,
                        fotos_dir=fotos_dir,
                        relatorios_dir=reports_dir,
                        gerar_todos=regenerar_todos
                    )

                    if not arquivos_gerados:
                        st.warning(
                            "Nenhum relatório pendente foi encontrado. "
                            "Verifique se a coluna **Relatório Gerado** está vazia ou com **FALSO**, "
                            "ou marque a opção acima para regenerar relatórios já processados."
                        )
                    else:
                        # Guardar os bytes em memória (session_state) para persistir após o rerun
                        for arquivo in arquivos_gerados:
                            nome_base = os.path.basename(arquivo)
                            with open(arquivo, "rb") as f:
                                conteudo = f.read()
                                st.session_state.arquivos_gerados_data.append({
                                    "nome": nome_base,
                                    "bytes": conteudo
                                })
                        
                        if planilha_atualizada:
                            st.session_state.planilha_atualizada_data = planilha_atualizada.getvalue()
                        
                        st.success(f"✅ {len(arquivos_gerados)} arquivo(s) gerado(s) com sucesso!")
                
                except Exception as e:
                    st.error(f"❌ Ocorreu um erro ao gerar o relatório: {e}")
                    st.exception(e)

# Exibir resultados (fora do bloco do botão para persistir entre reruns)
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
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document" if item["nome"].endswith(".docx") else "application/pdf",
                key=f"dl_{i}_{item['nome']}"
            )
    
    with col2:
        if st.session_state.planilha_atualizada_data:
            st.subheader("📊 Planilha Atualizada")
            st.write("Baixe a planilha com o status atualizado.")
            st.download_button(
                label="Baixar Planilha Atualizada",
                data=st.session_state.planilha_atualizada_data,
                file_name="planilha_fiscalizacao_atualizada.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )


st.divider()
st.info("Nota: Para a conversão de PDF funcionar localmente, é necessário ter o Microsoft Word instalado no sistema.")
