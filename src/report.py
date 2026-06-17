from docx import Document
from docx2pdf import convert
from docx.shared import Inches
import pandas as pd
from tqdm import tqdm
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import sys
import os
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
)


def gerar_relatorio(caminho_planilha=None, fotos_dir=None, relatorios_dir=None):
    """
    Gera o relatório completo (docx + pdf) com base nos dados da fiscalização.
    """

    if getattr(sys, "frozen", False):
        BASE_DIR = os.path.dirname(sys.executable)
    else:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    FOTOS_DIR = fotos_dir if fotos_dir else os.path.join(BASE_DIR, "assets")
    RELATORIOS_DIR = relatorios_dir if relatorios_dir else os.path.join(BASE_DIR, "reports")
    CAMINHO_PLANILHA = caminho_planilha if caminho_planilha else os.path.join(BASE_DIR, "planilha_fiscalizacao.xlsx")
    COLUNA_STATUS = "Relatório Gerado"

    os.makedirs(RELATORIOS_DIR, exist_ok=True)
    os.makedirs(FOTOS_DIR, exist_ok=True)

    # Só verifica se está em uso se for um caminho de arquivo real (string)
    if isinstance(CAMINHO_PLANILHA, str) and os.path.exists(CAMINHO_PLANILHA):
        if arquivo_em_uso(CAMINHO_PLANILHA):
            print("⚠️ A planilha está em uso. Feche-a antes de executar o script.")
            return []

    fiscalizacoes_df = pd.read_excel(CAMINHO_PLANILHA, sheet_name="Fiscalizações")
    nao_conformidades_df = pd.read_excel(
        CAMINHO_PLANILHA, sheet_name="Não-conformidades "
    )
    observacoes_df = pd.read_excel(
        CAMINHO_PLANILHA, sheet_name="Observações Importantes"
    )
    recomendacoes_df = pd.read_excel(
        CAMINHO_PLANILHA, sheet_name="Recomendações"
    )

    if COLUNA_STATUS not in fiscalizacoes_df.columns:
        fiscalizacoes_df[COLUNA_STATUS] = False
    fiscalizacoes_df[COLUNA_STATUS] = (
        fiscalizacoes_df[COLUNA_STATUS].fillna(False).astype(bool)
    )

    pendentes = fiscalizacoes_df[~fiscalizacoes_df[COLUNA_STATUS]]

    if pendentes.empty:
        print("✅ Nenhum relatório pendente.")
        return []

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

        nome_arquivo = f"relatorio_{id_fisc}"
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

    # Salva a planilha apenas se um caminho foi fornecido e não for um buffer
    if isinstance(CAMINHO_PLANILHA, str) and not arquivo_em_uso(CAMINHO_PLANILHA):
        with pd.ExcelWriter(
            CAMINHO_PLANILHA, engine="openpyxl", mode="a", if_sheet_exists="replace"
        ) as writer:
            fiscalizacoes_df.to_excel(writer, sheet_name="Fiscalizações", index=False)
            nao_conformidades_df.to_excel(
                writer, sheet_name="Não-conformidades ", index=False
            )
            observacoes_df.to_excel(
                writer, sheet_name="Observações Importantes", index=False
            )
            recomendacoes_df.to_excel(
                writer, sheet_name="Recomendações", index=False
            )

        ajustar_largura_colunas(CAMINHO_PLANILHA)

    print("🎉 Relatórios gerados e planilha atualizada com sucesso.")

    return arquivos_gerados
