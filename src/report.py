from docx import Document
from docx2pdf import convert
from docx.shared import Inches
import pandas as pd
from tqdm import tqdm
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import sys
import os
import io
from sections.introduction.introduction import gerar_secao_introducao
from sections.legalbasis.legalbasis import gerar_secao_fundamentacao_legal
from sections.nonconformity.nonconformity import (
    gerar_secao_nao_conformidades_constatadas,
)
from sections.nonconformityresume.nonconformityresume import (
    gerar_secao_resumo_nao_conformidades,
)
from sections.finalconsiderations.finalconsiderations import (
    gerar_secao_consideracoes_finais,
)
from utils import (
    adicionar_texto_centralizado,
    ajustar_largura_colunas,
    arquivo_em_uso,
    normalizar_status_gerado,
)


def gerar_relatorio(
    caminho_planilha=None,
    fotos_dir=None,
    relatorios_dir=None,
    gerar_todos=False,
):
    """
    Gera o relatório completo (docx + pdf) com base nos dados da fiscalização.
    """

    if getattr(sys, "frozen", False):
        BASE_DIR = os.path.dirname(sys.executable)
    else:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    FOTOS_DIR = fotos_dir if fotos_dir else os.path.join(BASE_DIR, "assets")
    RELATORIOS_DIR = relatorios_dir if relatorios_dir else os.path.join(BASE_DIR, "reports")
    
    # Se não passar caminho, tenta o modelo base primeiro, depois o original
    if not caminho_planilha:
        modelo_base = os.path.join(BASE_DIR, "modelo_base.xlsx")
        if os.path.exists(modelo_base):
            CAMINHO_PLANILHA = modelo_base
        else:
            CAMINHO_PLANILHA = os.path.join(BASE_DIR, "planilha_fiscalizacao.xlsx")
    else:
        CAMINHO_PLANILHA = caminho_planilha

    if hasattr(CAMINHO_PLANILHA, "read") and not isinstance(CAMINHO_PLANILHA, (str, bytes)):
        CAMINHO_PLANILHA = io.BytesIO(CAMINHO_PLANILHA.read())

    COLUNA_STATUS = "Relatório Gerado"

    os.makedirs(RELATORIOS_DIR, exist_ok=True)
    os.makedirs(FOTOS_DIR, exist_ok=True)

    # Só verifica se está em uso se for um caminho de arquivo real (string)
    if isinstance(CAMINHO_PLANILHA, str) and os.path.exists(CAMINHO_PLANILHA):
        if arquivo_em_uso(CAMINHO_PLANILHA):
            print("⚠️ A planilha está em uso. Feche-a antes de executar o script.")
            return [], None

    # Carregar todas as abas para verificar nomes
    excel_file = pd.ExcelFile(CAMINHO_PLANILHA)
    sheet_names = excel_file.sheet_names

    def find_sheet(target, sheets):
        # Busca exata
        if target in sheets:
            return target
        # Busca ignorando espaços extras e case
        target_clean = target.strip().lower()
        for s in sheets:
            if s.strip().lower() == target_clean:
                return s
        # Busca parcial ou sem acentos (opcional, mas vamos focar no comum)
        return None

    sheet_fiscalizacoes = find_sheet("Fiscalizações", sheet_names)
    sheet_nao_conformidades = find_sheet("Não-conformidades ", sheet_names)
    sheet_observacoes = find_sheet("Observações Importantes", sheet_names)
    sheet_recomendacoes = find_sheet("Recomendações", sheet_names)

    # Fallback: Se não encontrou pelo nome, pega por ordem se existirem
    if not sheet_fiscalizacoes and len(sheet_names) > 0:
        sheet_fiscalizacoes = sheet_names[0]
    
    if not sheet_nao_conformidades and len(sheet_names) > 1:
        sheet_nao_conformidades = sheet_names[1]
    
    if not sheet_observacoes and len(sheet_names) > 2:
        sheet_observacoes = sheet_names[2]
        
    if not sheet_recomendacoes and len(sheet_names) > 3:
        sheet_recomendacoes = sheet_names[3]

    if not sheet_fiscalizacoes:
        raise ValueError(f"Nenhuma aba encontrada na planilha. Abas disponíveis: {sheet_names}")

    fiscalizacoes_df = pd.read_excel(CAMINHO_PLANILHA, sheet_name=sheet_fiscalizacoes)
    
    # Normalizar nomes das colunas (remover espaços extras)
    fiscalizacoes_df.columns = [str(c).strip() for c in fiscalizacoes_df.columns]
    
    # Carregar as outras abas ou criar DataFrames vazios se não existirem
    if sheet_nao_conformidades:
        nao_conformidades_df = pd.read_excel(CAMINHO_PLANILHA, sheet_name=sheet_nao_conformidades)
        nao_conformidades_df.columns = [str(c).strip() for c in nao_conformidades_df.columns]
    else:
        nao_conformidades_df = pd.DataFrame()

    if sheet_observacoes:
        observacoes_df = pd.read_excel(CAMINHO_PLANILHA, sheet_name=sheet_observacoes)
        observacoes_df.columns = [str(c).strip() for c in observacoes_df.columns]
    else:
        observacoes_df = pd.DataFrame()

    if sheet_recomendacoes:
        recomendacoes_df = pd.read_excel(CAMINHO_PLANILHA, sheet_name=sheet_recomendacoes)
        recomendacoes_df.columns = [str(c).strip() for c in recomendacoes_df.columns]
    else:
        recomendacoes_df = pd.DataFrame()

    # Função auxiliar para garantir que colunas essenciais existem (busca insensível a caso)
    def garantir_coluna(df, nome_esperado):
        if nome_esperado in df.columns:
            return True
        for col in df.columns:
            if col.lower() == nome_esperado.lower():
                df.rename(columns={col: nome_esperado}, inplace=True)
                return True
        return False

    # Verificar colunas essenciais
    colunas_obrigatorias = ["ID da Fiscalização", "Contrato", "Data", "Local"]
    for col in colunas_obrigatorias:
        if not garantir_coluna(fiscalizacoes_df, col):
            raise KeyError(f"Coluna obrigatória '{col}' não encontrada na aba '{sheet_fiscalizacoes}'. Colunas disponíveis: {list(fiscalizacoes_df.columns)}")

    if COLUNA_STATUS not in fiscalizacoes_df.columns:
        if not garantir_coluna(fiscalizacoes_df, COLUNA_STATUS):
            fiscalizacoes_df[COLUNA_STATUS] = False
    
    fiscalizacoes_df[COLUNA_STATUS] = normalizar_status_gerado(
        fiscalizacoes_df[COLUNA_STATUS]
    )

    if gerar_todos:
        pendentes = fiscalizacoes_df
    else:
        pendentes = fiscalizacoes_df[~fiscalizacoes_df[COLUNA_STATUS]]

    if pendentes.empty:
        print("✅ Nenhum relatório pendente.")
        return [], None

    arquivos_gerados = []

    for idx in tqdm(pendentes.index, desc="Gerando relatórios"):
        row = fiscalizacoes_df.loc[idx]
        id_fisc = row["ID da Fiscalização"]
        doc = Document()

        logo_path = os.path.join(BASE_DIR, "assets/logo_arpe.jpeg")
        if os.path.exists(logo_path):
            doc.add_picture(logo_path, width=Inches(2))
            logo_arpe = doc.paragraphs[-1]
            logo_arpe.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        
        adicionar_texto_centralizado(doc, "DIRETORIA DE REGULAÇÃO TÉCNICO-OPERACIONAL")
        adicionar_texto_centralizado(doc, "COORDENADORIA DE TRANSPORTES E RODOVIAS")
        adicionar_texto_centralizado(
            doc, "RELATÓRIO DE FISCALIZAÇÃO TÉCNICO-OPERACIONAL CTR 01/2025"
        )
        adicionar_texto_centralizado(
            doc, "TERMINAIS RODOVIÁRIOS INTERMUNICIPAIS CONCEDIDOS À EMPRESA SOCICAM"
        )
        adicionar_texto_centralizado(
            doc, "CONTRATO DE CONCESSÃO DE SERVIÇO PÚBLICO Nº 1.041.080/08"
        )

        doc.add_section(WD_SECTION.NEW_PAGE)

        gerar_secao_introducao(doc, row)
        gerar_secao_fundamentacao_legal(doc)
        gerar_secao_nao_conformidades_constatadas(
            doc, row, nao_conformidades_df, FOTOS_DIR, observacoes_df, recomendacoes_df
        )
        gerar_secao_resumo_nao_conformidades(doc, row, nao_conformidades_df)
        gerar_secao_consideracoes_finais(doc, row)

        # Sanitizar o ID para evitar erro de caracteres inválidos no nome do arquivo (Windows)
        id_fisc_str = str(id_fisc)
        # Substitui caracteres proibidos: \ / : * ? " < > |
        for char in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
            id_fisc_str = id_fisc_str.replace(char, "_")
        
        nome_arquivo = f"relatorio_{id_fisc_str.strip()}"
        caminho_docx = os.path.join(RELATORIOS_DIR, f"{nome_arquivo}.docx")
        caminho_pdf = os.path.join(RELATORIOS_DIR, f"{nome_arquivo}.pdf")

        doc.save(caminho_docx)
        try:
            convert(caminho_docx, caminho_pdf)
            arquivos_gerados.append(caminho_pdf)
        except Exception as e:
            print(f"⚠️ Não foi possível converter para PDF: {e}")
        
        arquivos_gerados.append(caminho_docx)
        fiscalizacoes_df.at[idx, COLUNA_STATUS] = True

    # 🔹 Garantir que a coluna Data seja salva no formato dd/mm/aaaa
    if "Data" in fiscalizacoes_df.columns:
        fiscalizacoes_df["Data"] = pd.to_datetime(
            fiscalizacoes_df["Data"], errors="coerce"
        ).dt.strftime("%d/%m/%Y")

    planilha_atualizada_buffer = None

    # Salva a planilha se for um caminho de arquivo real
    if isinstance(CAMINHO_PLANILHA, str) and not arquivo_em_uso(CAMINHO_PLANILHA):
        with pd.ExcelWriter(
            CAMINHO_PLANILHA, engine="openpyxl", mode="a", if_sheet_exists="replace"
        ) as writer:
            fiscalizacoes_df.to_excel(writer, sheet_name=sheet_fiscalizacoes, index=False)
            nao_conformidades_df.to_excel(
                writer, sheet_name=sheet_nao_conformidades if sheet_nao_conformidades else "Não-conformidades ", index=False
            )
            observacoes_df.to_excel(
                writer, sheet_name=sheet_observacoes if sheet_observacoes else "Observações Importantes", index=False
            )
            recomendacoes_df.to_excel(
                writer, sheet_name=sheet_recomendacoes if sheet_recomendacoes else "Recomendações", index=False
            )

        ajustar_largura_colunas(CAMINHO_PLANILHA)
    else:
        # Se for um buffer (Streamlit), gera um novo buffer com a planilha atualizada
        planilha_atualizada_buffer = io.BytesIO()
        with pd.ExcelWriter(planilha_atualizada_buffer, engine="openpyxl") as writer:
            fiscalizacoes_df.to_excel(writer, sheet_name=sheet_fiscalizacoes, index=False)
            nao_conformidades_df.to_excel(
                writer, sheet_name=sheet_nao_conformidades if sheet_nao_conformidades else "Não-conformidades ", index=False
            )
            observacoes_df.to_excel(
                writer, sheet_name=sheet_observacoes if sheet_observacoes else "Observações Importantes", index=False
            )
            recomendacoes_df.to_excel(
                writer, sheet_name=sheet_recomendacoes if sheet_recomendacoes else "Recomendações", index=False
            )
        planilha_atualizada_buffer.seek(0)

    print("🎉 Relatórios gerados e planilha atualizada com sucesso.")

    return arquivos_gerados, planilha_atualizada_buffer

