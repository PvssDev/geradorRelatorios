import streamlit as st
import os
import tempfile
import shutil
from report import gerar_relatorio

st.set_page_config(page_title="Gerador de Relatórios ARPE", layout="centered")

st.title("📄 Gerador de Relatórios de Fiscalização")
st.write("Faça o upload da planilha e das fotos para gerar os relatórios.")

# Upload da Planilha
uploaded_excel = st.file_uploader("Selecione a planilha Excel (.xlsx)", type=["xlsx"])

# Upload das Fotos
uploaded_photos = st.file_uploader("Selecione as fotos (múltiplos arquivos)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if st.button("🚀 Gerar Relatório"):
    if not uploaded_excel:
        st.error("⚠️ Por favor, faça o upload da planilha Excel.")
    elif not uploaded_photos:
        st.warning("⚠️ Nenhuma foto foi carregada. O relatório será gerado sem imagens.")
        # Mesmo sem fotos, podemos prosseguir se o usuário desejar, ou podemos exigir. 
        # No caso, vou permitir prosseguir mas avisar.
    
    if uploaded_excel:
        with st.spinner("Processando relatórios... Isso pode levar alguns minutos."):
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
                    # Passamos o buffer do excel diretamente
                    arquivos_gerados = gerar_relatorio(
                        caminho_planilha=uploaded_excel,
                        fotos_dir=fotos_dir,
                        relatorios_dir=reports_dir
                    )

                    if not arquivos_gerados:
                        st.info("ℹ️ Nenhum relatório pendente foi encontrado na planilha.")
                    else:
                        st.success(f"✅ {len(arquivos_gerados)} arquivo(s) gerado(s) com sucesso!")
                        
                        st.divider()
                        st.subheader("📥 Download dos Relatórios")
                        
                        for arquivo in arquivos_gerados:
                            nome_base = os.path.basename(arquivo)
                            with open(arquivo, "rb") as f:
                                st.download_button(
                                    label=f"Baixar {nome_base}",
                                    data=f,
                                    file_name=nome_base,
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document" if nome_base.endswith(".docx") else "application/pdf"
                                )
                except Exception as e:
                    st.error(f"❌ Ocorreu um erro ao gerar o relatório: {e}")
                    st.exception(e)

st.divider()
st.info("Nota: Para a conversão de PDF funcionar localmente, é necessário ter o Microsoft Word instalado no sistema.")
