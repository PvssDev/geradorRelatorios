from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
import os
from utils import adicionar_texto_centralizado, adicionar_texto_caixa_cinza

def gerar_capa_primeira_pagina(doc, logo_path):
    """
    Gera a primeira página do relatório (Capa) baseada no modelo de referência.
    """
    from docx.shared import Cm
    
    # 0. Ajuste de Estilo e Margens
    style = doc.styles['Normal']
    style.font.name = 'Aptos'
    
    section = doc.sections[0]
    if section.top_margin > Cm(1.15):
        section.top_margin = section.top_margin - Cm(1.15)
    if section.bottom_margin > Cm(1.15):
        section.bottom_margin = section.bottom_margin - Cm(1.15)

    # 1. Texto Superior em Caixa Cinza (tabela 1x1 sem bordas)
    adicionar_texto_caixa_cinza(doc, "RELATÓRIO DE FISCALIZAÇÃO PROCESSO ADMINISTRATIVO CTR Nº 01/2026")
    
    # 1. Imagem da Capa
    if os.path.exists(logo_path):
        doc.add_picture(logo_path, width=Inches(5.9))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 2. Títulos Principais
    titulos = [
        "FISCALIZAÇÃO DO COMPLEXO VIÁRIO E LOGÍSTICO DE SUAPE – EXPRESSWAY",
        "PRESTADOR DE SERVIÇO: CONCESSIONÁRIA ROTA DO ATLÂNTICO (CRA)",
        "CONTRATO DE CONCESSÃO CT. Nº 043/2011"
    ]
    from docx.shared import Cm
    for idx, titulo in enumerate(titulos):
        # Usando a lógica do utils diretamente para poder manipular o parágrafo
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(titulo)
        run.bold = True
        # Espaçamento de 12pt nas duas primeiras linhas, 0 na última
        if idx < 2:
            p.paragraph_format.space_after = Pt(12)
        else:
            p.paragraph_format.space_after = Pt(0)
            
    # Pular uma linha após o CONTRATO DE CONCESSÃO
    doc.add_paragraph()


    
    # 3. Lista de Analistas
    analistas = [
        ("Alcides Vieira de Azevedo Bezerra", "Analista de Regulação, matrícula nº 40672015/01"),
        ("Enildo Manoel da Silva Júnior", "Analista de Regulação, matrícula nº 1796500/02"),
        ("Maria Fernanda da Silva Novaes", "Auxiliar de Regulação, matrícula nº 18471080/01")
    ]
    
    for nome, cargo in analistas:
        # Nome em negrito
        p_nome = doc.add_paragraph()
        p_nome.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_nome = p_nome.add_run(nome)
        run_nome.bold = True
        run_nome.font.size = Pt(12)
        
        p_nome.paragraph_format.space_after = Pt(0)
        
        # Cargo normal
        p_cargo = doc.add_paragraph()
        p_cargo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_cargo = p_cargo.add_run(cargo)
        run_cargo.font.size = Pt(12)
        
        # Sem espaço extra entre os analistas (reduzindo ao máximo o espaçamento entre as linhas)
        p_cargo.paragraph_format.space_after = Pt(0)
        
        # Pular uma linha após o Alcides
        if "Alcides" in nome:
            doc.add_paragraph()

    
    # Espaço isolando a data
    doc.add_paragraph()
    
    # 4. Data
    p_data = doc.add_paragraph()
    p_data.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_data = p_data.add_run("Dezembro, 2025")
    run_data.bold = True
    run_data.font.size = Pt(12)
    p_data.paragraph_format.space_after = Pt(0)
    
    # Espaço isolando a data após ela
    doc.add_paragraph()
    
    # 5. Processo e SEI
    rodape_textos = [
        "RELATÓRIO DE FISCALIZAÇÃO PROCESSO ADMINISTRATIVO Nº 07/2025 - CTR",
        "SEI Nº xxxxxxxxxxxx/2025-XX"
    ]
    for texto in rodape_textos:
        p_rodape = doc.add_paragraph()
        p_rodape.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_rodape = p_rodape.add_run(texto)
        run_rodape.bold = True
        run_rodape.font.size = Pt(12)
    
    # 6. Quebra de página
    doc.add_section(WD_SECTION.NEW_PAGE)
