from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
import os
from utils import adicionar_texto_caixa_cinza

def gerar_capa_primeira_pagina(doc, logo_path, row, report_config, documento_anterior=None):
    """
    Gera a primeira página do relatório (Capa) baseada no modelo de referência com dados dinâmicos.
    """
    if hasattr(report_config, "gerar_capa_monitoramento"):
        report_config.gerar_capa_monitoramento(doc, logo_path, row, documento_anterior)
    else:
        from docx.shared import Cm
        from docx.shared import Inches
        from database.manager import carregar_responsaveis
        from utils import formatar_mes_ano, extrair_ano
        
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
        ano = extrair_ano(row["Data"])
        id_fisc = str(row.get("ID da Fiscalização", "")).strip()
        ctr_text = report_config.capa_ctr_number_template.format(ano=ano, id_fisc=id_fisc)
        adicionar_texto_caixa_cinza(doc, ctr_text)
        
        # 1. Imagem da Capa
        if os.path.exists(logo_path):
            doc.add_picture(logo_path, width=Inches(4.0))
            doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
            
        doc.add_paragraph()  # Linha vazia antes de FISCALIZAÇÃO...
        
        # 2. Títulos Principais
        titulos = report_config.get_capa_titulos(row, ano)
            
        for idx, titulo in enumerate(titulos):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(titulo)
            run.bold = True
            # Espaçamento pós parágrafo nas duas primeiras linhas, e um espaçamento maior (24pt) na última
            if idx < len(titulos) - 1:
                p.paragraph_format.space_after = Pt(6)
            else:
                p.paragraph_format.space_after = Pt(12)

        
        # 3. Lista de Analistas Dinâmica
        responsaveis_list = [r.strip() for r in str(row["Pessoal Responsável"]).split(",") if r.strip()]
        db_resp = carregar_responsaveis()
        
        analistas = []
        for nome in responsaveis_list:
            match = next((d for d in db_resp if d["nome"].strip().lower() == nome.lower()), None)
            if match:
                funcao = report_config.analyst_title if report_config.key == "SOCICAM" else match["funcao"]
                analistas.append((match["nome"], f"{funcao}, matrícula nº {match['matricula']}"))
            else:
                funcao = report_config.analyst_title if report_config.key == "SOCICAM" else "Analista de Regulação"
                analistas.append((nome, f"{funcao}, matrícula nº xxxxxxx/xx"))
        
        for i, (nome, cargo) in enumerate(analistas):
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
            
            if i == len(analistas) - 1:
                p_cargo.paragraph_format.space_after = Pt(12)  # Espaço após o parágrafo do último
            else:
                p_cargo.paragraph_format.space_after = Pt(12)  # Espaço abaixo de cada analista
        
        # 4. Data Dinâmica
        p_data = doc.add_paragraph()
        p_data.alignment = WD_ALIGN_PARAGRAPH.CENTER
        data_extenso = formatar_mes_ano(row["Data"])
        run_data = p_data.add_run(data_extenso)
        run_data.bold = True
        run_data.font.size = Pt(12)
        # Espaçamento superior e inferior para isolar a data nativamente
        p_data.paragraph_format.space_before = Pt(12)
        p_data.paragraph_format.space_after = Pt(12)
        
        # 5. Processo e SEI Dinâmicos
        rodape_textos = report_config.get_process_sei_texts(ano)
            
        for idx, texto in enumerate(rodape_textos):
            p_rodape = doc.add_paragraph()
            p_rodape.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run_rodape = p_rodape.add_run(texto)
            run_rodape.bold = True
            run_rodape.font.size = Pt(12)
            p_rodape.paragraph_format.space_after = Pt(0)
    
    # 6. Geração de Sumário e Lista de Abreviaturas com ordem condicional
    has_abbr = bool(report_config.get_abbreviations())
    if not has_abbr:
        # Apenas Sumário na Página 2, sem Lista de Abreviaturas
        doc.add_page_break()
        gerar_sumario(doc, row, report_config)
    elif report_config.sumario_before_abreviaturas:
        # CRC/SOCICAM: Sumário na Página 2, Lista de Abreviaturas na Página 3
        doc.add_page_break()
        gerar_sumario(doc, row, report_config)
        
        doc.add_page_break()
        gerar_lista_abreviaturas(doc, report_config)
    else:
        # CRA: Lista de Abreviaturas na Página 2, Sumário na Página 3
        doc.add_page_break()
        gerar_lista_abreviaturas(doc, report_config)
        
        doc.add_page_break()
        gerar_sumario(doc, row, report_config)
        
    # 7. Quebra de seção para ir para a Página 4 (Introdução)
    doc.add_section(WD_SECTION.NEW_PAGE)


def gerar_lista_abreviaturas(doc, report_config):
    """Gera a segunda página do cabeçalho (Lista de Abreviaturas e Siglas)."""
    from docx.enum.table import WD_TABLE_ALIGNMENT
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("LISTA DE ABREVIATURAS E SIGLAS")
    run.bold = True
    run.font.size = Pt(12)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(24)
    
    abreviaturas = report_config.get_abbreviations()
        
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


def gerar_sumario(doc, row, report_config):
    """Gera a terceira página do cabeçalho (Sumário dinâmico utilizando tabulações e líderes de ponto)."""
    from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("SUMÁRIO")
    run.bold = True
    run.font.size = Pt(14)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(24)
    
    linhas = report_config.get_sumario_linhas(row)
        
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
