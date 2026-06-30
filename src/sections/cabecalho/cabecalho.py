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
    
    from docx.shared import Inches
    
    # 0. Ajuste de Estilo e Margens (Explicitas de 0.5 polegadas conforme a referência)
    style = doc.styles['Normal']
    style.font.name = 'Aptos'
    
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)
    section.left_margin = Inches(0.5)
    section.right_margin = Inches(0.5)

    # 1. Texto Superior em Caixa Cinza (tabela 1x1 sem bordas)
    adicionar_texto_caixa_cinza(doc, "RELATÓRIO DE FISCALIZAÇÃO PROCESSO ADMINISTRATIVO CTR Nº 01/2026")
    
    # 1. Imagem da Capa
    if os.path.exists(logo_path):
        doc.add_picture(logo_path, width=Inches(4.5))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # 2. Títulos Principais
    titulos = [
        "FISCALIZAÇÃO DO COMPLEXO VIÁRIO E LOGÍSTICO DE SUAPE – EXPRESSWAY",
        "PRESTADOR DE SERVIÇO: CONCESSIONÁRIA ROTA DO ATLÂNTICO (CRA)",
        "CONTRATO DE CONCESSÃO CT. Nº 043/2011"
    ]
    from docx.shared import Cm
    for idx, titulo in enumerate(titulos):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(titulo)
        run.bold = True
        # Espaçamento pós parágrafo nas duas primeiras linhas, e um espaçamento maior (24pt) na última
        if idx < 2:
            p.paragraph_format.space_after = Pt(6)
        else:
            p.paragraph_format.space_after = Pt(24)



    
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
        
        # Pular uma linha (espaço de 12pt) após o Alcides, e 0 para os outros
        if "Alcides" in nome:
            p_cargo.paragraph_format.space_after = Pt(12)
        else:
            p_cargo.paragraph_format.space_after = Pt(0)
    
    # 4. Data
    p_data = doc.add_paragraph()
    p_data.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_data = p_data.add_run("Dezembro, 2025")
    run_data.bold = True
    run_data.font.size = Pt(12)
    # Espaçamento superior e inferior para isolar a data nativamente
    p_data.paragraph_format.space_before = Pt(24)
    p_data.paragraph_format.space_after = Pt(24)
    
    # 5. Processo e SEI
    rodape_textos = [
        "RELATÓRIO DE FISCALIZAÇÃO PROCESSO ADMINISTRATIVO Nº 07/2025 - CTR",
        "SEI Nº xxxxxxxxxxxx/2025-XX"
    ]
    for idx, texto in enumerate(rodape_textos):
        p_rodape = doc.add_paragraph()
        p_rodape.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_rodape = p_rodape.add_run(texto)
        run_rodape.bold = True
        run_rodape.font.size = Pt(12)
        if idx == 0:
            p_rodape.paragraph_format.space_after = Pt(0)
        else:
            p_rodape.paragraph_format.space_after = Pt(0)
    
    # 6. Quebra de página para ir para a Página 2 (Lista de Abreviaturas)
    doc.add_page_break()
    
    # Gerar Lista de Abreviaturas (Página 2)
    gerar_lista_abreviaturas(doc)
    
    # Quebra de página para ir para a Página 3 (Sumário)
    doc.add_page_break()
    
    # Gerar Sumário (Página 3)
    gerar_sumario(doc)
    
    # 7. Quebra de seção para ir para a Página 4 (Introdução)
    doc.add_section(WD_SECTION.NEW_PAGE)


def gerar_lista_abreviaturas(doc):
    """Gera a segunda página do cabeçalho (Lista de Abreviaturas e Siglas)."""
    from docx.enum.table import WD_TABLE_ALIGNMENT
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("LISTA DE ABREVIATURAS E SIGLAS")
    run.bold = True
    run.font.size = Pt(12)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(24)
    
    abreviaturas = [
        ("CRA", "Concessionária Rota do Atlântico"),
        ("ECR", "ECR Engenharia Ltda"),
        ("FD", "Faixa Direita"),
        ("FE", "Faixa Esquerda"),
        ("IGG", "Índice de Gravidade Global"),
        ("IRI", "Índice Irregularidade Longitudinal"),
        ("NC", "Não Conformidade"),
        ("PDCL", "Programa de Desenvolvimento do Complexo Logístico, Anexo IV do Contrato de Concessão nº 043/2011"),
        ("SUAPE", "Poder Concedente e Regulador do Contrato de Concessão firmado com a CRA"),
        ("TPF", "TPF Engenharia Ltda"),
        ("TDR", "Tronco Distribuidor Rodoviário"),
        ("VI", "Verificador Independente contratado por SUAPE, atualmente o Consórcio formado pelas Empresas TPF e ECR")
    ]
    
    table = doc.add_table(rows=1 + len(abreviaturas), cols=2)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.allow_autofit = False
    
    # Cabeçalho da tabela
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'SIGLA'
    hdr_cells[1].text = 'DEFINIÇÃO'
    
    # Formatação do cabeçalho
    for cell in hdr_cells:
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in cell.paragraphs[0].runs:
            run.bold = True
            run.font.size = Pt(11)
            
    # Preencher dados
    for idx, (sigla, definicao) in enumerate(abreviaturas):
        row_cells = table.rows[idx + 1].cells
        row_cells[0].text = sigla
        row_cells[1].text = definicao
        
        # Alinhamento
        row_cells[0].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        row_cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.LEFT
        
        # Garantir tamanho da fonte e normalizar estilo
        for cell in row_cells:
            for run in cell.paragraphs[0].runs:
                run.font.size = Pt(11)
                
    # Definir larguras das colunas
    col_widths = [Inches(1.0), Inches(5.0)]
    for row in table.rows:
        for idx, width in enumerate(col_widths):
            row.cells[idx].width = width


def gerar_sumario(doc):
    """Gera a terceira página do cabeçalho (Sumário dinâmico utilizando tabulações e líderes de ponto)."""
    from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("SUMÁRIO")
    run.bold = True
    run.font.size = Pt(14)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(24)
    
    linhas = [
        "\tINTRODUÇÃO\t4",
        "1.\tOBJETIVO\t4",
        "2.\tMETODOLOGIA\t5",
        "3.\tFISCALIZAÇÃO\t7",
        "4.\tDETERMINAÇÕES GERAIS\t11",
        "5.\tRECOMENDAÇÕES\t11",
        "6.\tCONCLUSÕES\t11",
        "\tAPÊNDICE ÚNICO  – REGISTROS FOTOGRÁFICOS DAS NÃO CONFORMIDADES\t12"
    ]
    
    for idx, linha in enumerate(linhas):
        p_line = doc.add_paragraph()
        p_line.paragraph_format.space_after = Pt(6)
        
        # Adiciona os tab stops necessários:
        # 1. Alinhamento esquerdo a 0.5 polegadas para afastar o título do número
        # 2. Alinhamento direito a 7.5 polegadas para colar o número da página no canto direito com pontilhado
        tab_stops = p_line.paragraph_format.tab_stops
        tab_stops.add_tab_stop(Inches(0.5), alignment=WD_TAB_ALIGNMENT.LEFT)
        tab_stops.add_tab_stop(Inches(7.5), alignment=WD_TAB_ALIGNMENT.RIGHT, leader=WD_TAB_LEADER.DOTS)
        
        parts = linha.split('\t')
        
        # Se houver número (ex: "1.")
        if parts[0]:
            run_num = p_line.add_run(parts[0])
            run_num.font.name = 'Aptos'
            run_num.font.size = Pt(11)
            run_num.bold = True
            
        # Pula para a primeira tabulação (título)
        p_line.add_run("\t")
        
        # Título
        run_title = p_line.add_run(parts[1])
        run_title.font.name = 'Aptos'
        run_title.font.size = Pt(11)
        run_title.bold = True
        
        # Pula para a segunda tabulação (página)
        run_page = p_line.add_run(f"\t{parts[2]}")
        run_page.font.name = 'Aptos'
        run_page.font.size = Pt(11)
        run_page.bold = True
