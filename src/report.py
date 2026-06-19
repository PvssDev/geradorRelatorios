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

def _obter_caminhos_base(fotos_dir, relatorios_dir):
    """Define diretórios base para fotos e relatórios."""
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    fotos = fotos_dir if fotos_dir else os.path.join(base_dir, "assets")
    relatorios = relatorios_dir if relatorios_dir else os.path.join(base_dir, "reports")
    return base_dir, fotos, relatorios

def _identificar_abas(sheet_names):
    """Identifica as abas necessárias com lógica de fallback."""
    def find_sheet(target, sheets):
        if target in sheets:
            return target
        target_clean = target.strip().lower()
        for s in sheets:
            if s.strip().lower() == target_clean:
                return s
        return None

    abas = {
        "fiscalizacoes": find_sheet("Fiscalizações", sheet_names),
        "nao_conformidades": find_sheet("Não-conformidades ", sheet_names),
        "observacoes": find_sheet("Observações Importantes", sheet_names),
        "recomendacoes": find_sheet("Recomendações", sheet_names),
    }

    # Fallback por índice se os nomes não baterem
    fallbacks = ["fiscalizacoes", "nao_conformidades", "observacoes", "recomendacoes"]
    for i, key in enumerate(fallbacks):
        if not abas[key] and len(sheet_names) > i:
            abas[key] = sheet_names[i]
    
    return abas

def _carregar_e_normalizar_df(excel_file, sheet_name):
    """Carrega uma aba e normaliza o nome das colunas."""
    if not sheet_name:
        return pd.DataFrame()
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    df.columns = [str(c).strip() for c in df.columns]
    return df

def _garantir_colunas_obrigatorias(df, colunas, sheet_name):
    """Verifica se colunas essenciais existem (busca insensível a caso)."""
    for nome_esperado in colunas:
        encontrada = False
        if nome_esperado in df.columns:
            encontrada = True
        else:
            for col in df.columns:
                if col.lower() == nome_esperado.lower():
                    df.rename(columns={col: nome_esperado}, inplace=True)
                    encontrada = True
                    break
        if not encontrada:
             raise KeyError(f"Coluna '{nome_esperado}' não encontrada na aba '{sheet_name}'.")

def gerar_relatorio(
    caminho_planilha=None,
    fotos_dir=None,
    relatorios_dir=None,
    gerar_todos=False,
):
    """Gera o relatório completo (docx + pdf) com base nos dados da fiscalização."""

    BASE_DIR, FOTOS_DIR, RELATORIOS_DIR = _obter_caminhos_base(fotos_dir, relatorios_dir)
    
    # Gerenciar caminho da planilha
    if not caminho_planilha:
        modelo_base = os.path.join(BASE_DIR, "modelo_base.xlsx")
        CAMINHO_PLANILHA = modelo_base if os.path.exists(modelo_base) else os.path.join(BASE_DIR, "planilha_fiscalizacao.xlsx")
    else:
        CAMINHO_PLANILHA = caminho_planilha

    if hasattr(CAMINHO_PLANILHA, "read") and not isinstance(CAMINHO_PLANILHA, (str, bytes)):
        CAMINHO_PLANILHA = io.BytesIO(CAMINHO_PLANILHA.read())

    os.makedirs(RELATORIOS_DIR, exist_ok=True)
    os.makedirs(FOTOS_DIR, exist_ok=True)

    if isinstance(CAMINHO_PLANILHA, str) and os.path.exists(CAMINHO_PLANILHA) and arquivo_em_uso(CAMINHO_PLANILHA):
        print("⚠️ A planilha está em uso. Feche-a antes de executar o script.")
        return [], None

    # Processamento de Dados
    excel_file = pd.ExcelFile(CAMINHO_PLANILHA)
    abas = _identificar_abas(excel_file.sheet_names)

    if not abas["fiscalizacoes"]:
        raise ValueError(f"Aba de fiscalizações não identificada. Abas: {excel_file.sheet_names}")

    fiscal_df = _carregar_e_normalizar_df(excel_file, abas["fiscalizacoes"])
    nc_df = _carregar_e_normalizar_df(excel_file, abas["nao_conformidades"])
    nc_df.rename(columns={
        "Não conformidade": "Não Conformidade",
        "Observações": "Legenda da Foto"
    }, inplace=True)
    obs_df = _carregar_e_normalizar_df(excel_file, abas["observacoes"])
    rec_df = _carregar_e_normalizar_df(excel_file, abas["recomendacoes"])

    _garantir_colunas_obrigatorias(fiscal_df, ["ID da Fiscalização", "Contrato", "Data", "Local"], abas["fiscalizacoes"])

    COLUNA_STATUS = "Relatório Gerado"
    if COLUNA_STATUS not in fiscal_df.columns:
        # Tenta achar insensível a caso antes de criar nova
        for col in fiscal_df.columns:
            if col.lower() == COLUNA_STATUS.lower():
                fiscal_df.rename(columns={col: COLUNA_STATUS}, inplace=True)
                break
        else:
            fiscal_df[COLUNA_STATUS] = False
    
    fiscal_df[COLUNA_STATUS] = normalizar_status_gerado(fiscal_df[COLUNA_STATUS])

    pendentes = fiscal_df if gerar_todos else fiscal_df[~fiscal_df[COLUNA_STATUS]]
    if pendentes.empty:
        print("✅ Nenhum relatório pendente.")
        return [], None

    arquivos_gerados = []

    for idx in tqdm(pendentes.index, desc="Gerando relatórios"):
        row = fiscal_df.loc[idx]
        id_fisc = row["ID da Fiscalização"]
        doc = Document()

        # Cabeçalho do Documento
        logo_path = os.path.join(BASE_DIR, "assets/logo_arpe.jpeg")
        if os.path.exists(logo_path):
            doc.add_picture(logo_path, width=Inches(2))
            doc.paragraphs[-1].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        
        for titulo in [
            "DIRETORIA DE REGULAÇÃO TÉCNICO-OPERACIONAL",
            "COORDENADORIA DE TRANSPORTES E RODOVIAS",
            "RELATÓRIO DE FISCALIZAÇÃO TÉCNICO-OPERACIONAL CTR 01/2025",
            "TERMINAIS RODOVIÁRIOS INTERMUNICIPAIS CONCEDIDOS À EMPRESA SOCICAM",
            "CONTRATO DE CONCESSÃO DE SERVIÇO PÚBLICO Nº 1.041.080/08"
        ]:
            adicionar_texto_centralizado(doc, titulo)

        doc.add_section(WD_SECTION.NEW_PAGE)

        # Geração das Seções
        gerar_secao_introducao(doc, row)
        gerar_secao_fundamentacao_legal(doc)
        gerar_secao_nao_conformidades_constatadas(doc, row, nc_df, FOTOS_DIR, obs_df, rec_df)
        gerar_secao_resumo_nao_conformidades(doc, row, nc_df)
        gerar_secao_consideracoes_finais(doc, row)

        # Sanitização e Salvamento
        id_safe = "".join([c if c not in r'\/:*?"<>|' else "_" for c in str(id_fisc)]).strip()
        nome_base = f"relatorio_{id_safe}"
        caminho_docx = os.path.join(RELATORIOS_DIR, f"{nome_base}.docx")
        
        doc.save(caminho_docx)
        arquivos_gerados.append(caminho_docx)
        
        try:
            caminho_pdf = os.path.join(RELATORIOS_DIR, f"{nome_base}.pdf")
            convert(caminho_docx, caminho_pdf)
            arquivos_gerados.append(caminho_pdf)
        except Exception as e:
            print(f"⚠️ Erro ao converter PDF ({id_fisc}): {e}")
        
        fiscal_df.at[idx, COLUNA_STATUS] = True

    # Finalização da Planilha
    if "Data" in fiscal_df.columns:
        fiscal_df["Data"] = pd.to_datetime(fiscal_df["Data"], errors="coerce").dt.strftime("%d/%m/%Y")

    def salvar_excel(writer):
        fiscal_df.to_excel(writer, sheet_name=abas["fiscalizacoes"], index=False)
        for key, df in [("nao_conformidades", nc_df), ("observacoes", obs_df), ("recomendacoes", rec_df)]:
            if not df.empty or abas[key]:
                df.to_excel(writer, sheet_name=abas[key] or key.capitalize(), index=False)

    planilha_buffer = None
    if isinstance(CAMINHO_PLANILHA, str) and not arquivo_em_uso(CAMINHO_PLANILHA):
        with pd.ExcelWriter(CAMINHO_PLANILHA, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            salvar_excel(writer)
        ajustar_largura_colunas(CAMINHO_PLANILHA)
    else:
        planilha_buffer = io.BytesIO()
        with pd.ExcelWriter(planilha_buffer, engine="openpyxl") as writer:
            salvar_excel(writer)
        planilha_buffer.seek(0)

    print("🎉 Processo concluído com sucesso.")
    return arquivos_gerados, planilha_buffer
