from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from utils import adicionar_titulo_secao
import os

def gerar_secao_introducao(doc: Document, row):
    """Gera as seções de Introdução, Objetivo, Informações Gerais e Metodologia no relatório."""
    
    # ----------------------------------------------------
    # 1. SEÇÃO: INTRODUÇÃO (Sem número)
    # ----------------------------------------------------
    adicionar_titulo_secao(doc, "INTRODUÇÃO")
    doc.add_paragraph()  # Pula uma linha abaixo do título
    
    paragraphs_intro = [
        "A Coordenadoria de Transporte e Rodovias da Arpe implementou o cronograma de fiscalização para 2026 do Complexo Viário e Logístico de SUAPE, sob a responsabilidade da Concessionária Rota do Atlântico (CRA), visualizando a necessidade de serem reservados dois dias consecutivos, para melhor estruturar suas ações de fiscalização técnico-operacionais da Rodovia.",
        "Ainda com a visão de implantar melhorias na contribuição da Agência sobre os trabalhos desenvolvidos na rodovia, foi introduzida uma visita técnica prévia, realizada uma semana antes do período de fiscalização, com o objetivo de elaborar um roteiro que é encaminhado para a CRA e SUAPE contendo os trechos mapeados com possíveis Não Conformidades, tornando os levantamentos fotográficos mais ágeis e a fiscalização efetiva.",
        "Posteriormente, as possíveis Não Conformidades levantadas em campo são analisadas de acordo com os critérios elencados no PDCL anexo ao Contrato de Concessão, em conjunto com o último Relatório Anual elaborado pelo Verificador Independente.",
        "Destaca-se preliminarmente que as ações de fiscalização registradas neste Relatório foram concentradas na Rodovia PE-009, do Entroncamento BR-101 ao Entroncamento PE-038, que abrange os subtrechos concedidos, especificamente, o Contorno do Cabo, TDR Norte, TDR Sul e a Ligação Rótula Curva do Boi a Nossa Senhora do Ó; e Rodovia Estadual VPE-034.",
        "É importante observar que foram realizadas ações de fiscalização, no dia 9 de junho de 2026, conforme comunicado enviado à SUAPE por meio do Ofício Arpe/DTO nº 302 (Doc. SEI 75605952).",
        "Destaca-se que as fiscalizações realizadas pela Arpe são tratadas com caráter educativo, preferencialmente, e contributivo para correção de procedimentos e solução de Não Conformidades evidenciados por defeitos e/ou problemas na infraestrutura disponibilizada e respectivos serviços concedidos pelo Estado."
    ]
    
    for text in paragraphs_intro:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run(text)
        run.font.name = 'Aptos'
        run.font.size = Pt(11)

    # ----------------------------------------------------
    # 2. SEÇÃO: OBJETIVO (Seção 1)
    # ----------------------------------------------------
    adicionar_titulo_secao(doc, "1. OBJETIVO")
    doc.add_paragraph()  # Pula uma linha abaixo do título
    
    text_objetivo = (
        "A fiscalização direta e periódica do complexo viário e logístico de Suape – Expressway concedido à CRA, "
        "tem por objetivo verificar as condições de operação, manutenção, segurança viária e níveis de serviço, bem "
        "como identificar não conformidades, subsidiar medidas corretivas e assegurar a observância das disposições "
        "contratuais, regulamentares e normativas aplicáveis, preservando a segurança, a qualidade do serviço, e a "
        "adequada prestação do serviço público aos usuários. Dessa forma a ação de fiscalização da Arpe verifica o grau "
        "de conformidade dessas instalações com o Contrato de Concessão, bem como com a legislação e normas vigentes "
        "de modo a determinar e/ou recomendar medidas corretivas, com foco na qualidade dos serviços prestados."
    )
    
    p_obj = doc.add_paragraph()
    p_obj.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_obj.paragraph_format.space_after = Pt(12)
    p_obj.paragraph_format.line_spacing = 1.15
    run_obj = p_obj.add_run(text_objetivo)
    run_obj.font.name = 'Aptos'
    run_obj.font.size = Pt(11)

    # ----------------------------------------------------
    # 3. SEÇÃO: INFORMAÇÕES GERAIS (Tabela)
    # ----------------------------------------------------
    p_info = doc.add_paragraph()
    p_info.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_info.paragraph_format.space_before = Pt(12)
    p_info.paragraph_format.space_after = Pt(12)
    run_info = p_info.add_run("INFORMAÇÕES GERAIS")
    run_info.bold = True
    run_info.font.name = 'Aptos'
    run_info.font.size = Pt(12)
    
    # Construção da tabela de Informações Gerais
    from docx.enum.table import WD_TABLE_ALIGNMENT
    table = doc.add_table(rows=22, cols=2)
    table.style = 'Table Grid'
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.allow_autofit = False
    
    def format_header_row(row, text):
        cell = row.cells[0].merge(row.cells[1])
        cell.text = text
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        for run in p.runs:
            run.bold = True
            run.font.size = Pt(11)
            run.font.name = 'Aptos'
            
        # Shading XML
        tcPr = cell._tc.get_or_add_tcPr()
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), 'DDDDDD')
        tcPr.append(shd)
        
    def format_normal_row(row, label, val, val_bold=False):
        # Col 0 (Label)
        cell_lbl = row.cells[0]
        cell_lbl.text = label
        p_lbl = cell_lbl.paragraphs[0]
        p_lbl.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_lbl.paragraph_format.space_before = Pt(4)
        p_lbl.paragraph_format.space_after = Pt(4)
        for run in p_lbl.runs:
            run.bold = True
            run.font.size = Pt(11)
            run.font.name = 'Aptos'
            
        # Col 1 (Value)
        cell_val = row.cells[1]
        cell_val.text = val
        p_val = cell_val.paragraphs[0]
        p_val.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p_val.paragraph_format.space_before = Pt(4)
        p_val.paragraph_format.space_after = Pt(4)
        for run in p_val.runs:
            if val_bold:
                run.bold = True
            run.font.size = Pt(11)
            run.font.name = 'Aptos'

    # Preencher a estrutura da tabela conforme a referência (Seções 2.1, 2.2, 2.3, 2.4)
    format_header_row(table.rows[0], "2.1 DO TITULAR E REGULADOR")
    format_normal_row(table.rows[1], "Titular:", "SUAPE – Complexo Industrial Portuário Governador Eraldo Gueiros")
    format_normal_row(table.rows[2], "Endereço:", "Engenho Massangana – Km 10 – Rodovia PE – 60 Ipojuca/PE CEP: 55.590-000")
    format_normal_row(table.rows[3], "Responsável:", "JOSÉ CONSTANTINO DA SILVA FILHO", val_bold=True)
    format_normal_row(table.rows[4], "Representantes por acompanhar:", "Viviane Alves Walzertudes")
    
    format_header_row(table.rows[5], "2.2 DO VERIFICADOR INDEPENDENTE")
    format_normal_row(table.rows[6], "Verificador Independente:", "Consórcio das Empresas TPF/ECR")
    format_normal_row(table.rows[7], "Endereço:", "Rua Irene Ramos Gomes de Mattos, Nº 176, Pina, Recife/PE CEP: 51011-530")
    format_normal_row(table.rows[8], "Responsável:", "RICARDO MEDEIROS PEREIRA DE CARVALHO", val_bold=True)
    format_normal_row(table.rows[9], "Representantes por acompanhar:", "Sónya Albuquerque; Ricardo Henrique Ferraz de Farias; Lauro Ricardo Torres Galindo e Maynara Milena Silva de Lima")
    
    format_header_row(table.rows[10], "2.3 DO REGULADO")
    format_normal_row(table.rows[11], "Regulado:", "CRA - Concessionária Rota do Atlântico")
    format_normal_row(table.rows[12], "Responsável:", "RAFAELA ELAINE DA COSTA LIMA ARAÚJO", val_bold=True)
    format_normal_row(table.rows[13], "Endereço:", "Rodovia PE-009, Km 38,5(TDR Norte, 2074) – Distrito Industrial Suape, Cabo de Santo Agostinho/PE – CEP: 54.590-000")
    format_normal_row(table.rows[14], "Representantes por acompanhar:", "Vanessa Monteiro e OuvidoraXXXCRA")
    
    format_header_row(table.rows[15], "2.4 DO FISCALIZADOR (CONVÊNIO SUAPE/ARPE Nº 003/2021)")
    format_normal_row(table.rows[16], "Regulador:", "Agência de Regulação de Pernambuco (Arpe)")
    format_normal_row(table.rows[17], "Diretor Presidente:", "CARLOS PORTO FILHO", val_bold=True)
    format_normal_row(table.rows[18], "Endereço:", "Avenida Conselheiro Rosa e Silva, 975, Aflitos, Recife/PE, CEP: 52.050-020.\nEstacionamento: Rua do Futuro, 150, Aflitos, Recife/PE.")
    format_normal_row(table.rows[19], "Responsáveis pela fiscalização:", "Alcides Vieira de Azevedo Bezerra; Enildo Manoel da Silva Júnior")
    format_normal_row(table.rows[20], "Período da Fiscalização:", "9 de junho de 2026.")
    format_normal_row(table.rows[21], "Tipo de Fiscalização:", "Direta e periódica.")
    
    # Ajustar as larguras das colunas
    col_widths = [Inches(2.3), Inches(5.2)]
    for r_idx, row_obj in enumerate(table.rows):
        if r_idx in [0, 5, 10, 15]:
            row_obj.cells[0].width = Inches(7.5)
        else:
            row_obj.cells[0].width = col_widths[0]
            row_obj.cells[1].width = col_widths[1]

    # ----------------------------------------------------
    # 4. SEÇÃO: METODOLOGIA (Seção 2)
    # ----------------------------------------------------
    doc.add_paragraph()  # Pula uma linha antes do título
    adicionar_titulo_secao(doc, "2. METODOLOGIA")
    doc.add_paragraph()  # Pula uma linha abaixo do título
    
    paragraphs_metodo = [
        "A Coordenadoria de Transporte e Rodovias da Arpe implementou o cronograma de fiscalização para 2026 do Complexo Viário e Logístico de SUAPE reservando dois dias consecutivos, para melhor estruturar suas ações de fiscalização técnico-operacionais no Complexo Rodoviário, após uma visita técnica prévia, realizada antes do período de fiscalização, com o objetivo de elaborar um roteiro que é encaminhado para a CRA e SUAPE contendo os trechos mapeados com possíveis Não Conformidades, tornando os levantamentos fotográficos mais ágeis e a fiscalização efetiva.",
        "Posteriormente, as possíveis Não Conformidades levantadas em campo são analisadas de acordo com os critérios elencados no PDCL anexo ao Contrato de Concessão, em conjunto com o último Relatório Anual elaborado pelo Verificador Independente."
    ]
    
    for text in paragraphs_metodo:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run(text)
        run.font.name = 'Aptos'
        run.font.size = Pt(11)
