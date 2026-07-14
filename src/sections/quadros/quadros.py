from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import pandas as pd
from utils import formatar_mes_ano, adicionar_titulo_secao

MAP_SIGLAS = {
    "FI": "Fissuras",
    "TTC": "Trincas isoladas transversais curtas",
    "TTL": "Trincas isoladas transversais longas",
    "TLC": "Trincas isoladas longitudinais curtas",
    "TLL": "Trincas isoladas longitudinais longas",
    "J": "Trincas interligadas sem erosão acentuada nas bordas das trincas",
    "JE": "Trincas interligadas com erosão acentuada nas bordas das trincas",
    "TRR": "Trincas isoladas no revestimento devido à retração térmica ou dissecação da base (solo-cimento) ou do revestimento",
    "TB": "Trincas interligadas sem erosão acentuada nas bordas das trincas",
    "TBE": "Trincas interligadas com erosão acentuada nas bordas das trincas",
    "ALP": "Afundamento local plástico devido à fluência plástica de uma ou mais camadas do pavimento ou do subleito",
    "ATP": "Afundamento da trilha plástico devido à fluência plástica de uma ou mais camadas do pavimento ou do subleito",
    "ALC": "Afundamento local de consolidação devido à consolidação diferencial ocorrente em camadas do pavimento ou do subleito",
    "ATC": "Afundamento da trilha de consolidação devido à consolidação diferencial ocorrente em camadas do pavimento ou do subleito",
    "O": "Ondulação/Corrugação, caracterizada por ondulações transversais causadas por instabilidade da mistura betuminosa constituinte do revestimento ou da base",
    "E": "Escorregamento do revestimento betuminoso",
    "EX": "Exsudação do ligante betuminoso no revestimento",
    "D": "Desgaste acentuado na superfície do revestimento",
    "P": "buracos decorrentes da desagregação do revestimento e às vezes de camadas inferiores",
    "R": "Remendo"
}

def expandir_siglas(siglas_str):
    if not siglas_str or pd.isna(siglas_str):
        return ""
    parts = [p.strip() for p in str(siglas_str).split(",") if p.strip()]
    expanded = []
    for p in parts:
        if p in MAP_SIGLAS:
            expanded.append(f"{MAP_SIGLAS[p]} ({p})")
        else:
            expanded.append(p)
    return ", ".join(expanded)

def set_cell_shading(cell, color_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    for shd in tcPr.findall(qn('w:shd')):
        tcPr.remove(shd)
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), color_hex)
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    for tcMar in tcPr.findall(qn('w:tcMar')):
        tcPr.remove(tcMar)
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_borders(table):
    """Aplica bordas pretas e mais grossas (2.5 pt = sz 20) na tabela para maior legibilidade."""
    tblPr = table._tbl.tblPr
    tblBorders = tblPr.find(qn('w:tblBorders'))
    if tblBorders is not None:
        tblPr.remove(tblBorders)
        
    tblBorders = OxmlElement('w:tblBorders')
    
    # sz='20' significa 2.5 pt (cada unidade é 1/8 pt).
    borders = {
        'top': {'val': 'single', 'sz': '20', 'space': '0', 'color': '000000'},
        'left': {'val': 'single', 'sz': '20', 'space': '0', 'color': '000000'},
        'bottom': {'val': 'single', 'sz': '20', 'space': '0', 'color': '000000'},
        'right': {'val': 'single', 'sz': '20', 'space': '0', 'color': '000000'},
        'insideH': {'val': 'single', 'sz': '20', 'space': '0', 'color': '000000'},
        'insideV': {'val': 'single', 'sz': '20', 'space': '0', 'color': '000000'}
    }
    
    for border_name, border_attrs in borders.items():
        border = OxmlElement(f'w:{border_name}')
        for attr, val in border_attrs.items():
            border.set(qn(f'w:{attr}'), val)
        tblBorders.append(border)
        
    tblPr.append(tblBorders)

def agrupar_registros(df):
    """
    Agrupa registros que possuem as mesmas características de infração,
    combinando seus números de fotos na mesma linha.
    """
    if df.empty:
        return []
        
    records = df.to_dict('records')
    grouped = []
    
    for rec in records:
        found = False
        for g_rec in grouped:
            chaves = [
                "Identificação", "Não Conformidade", "Ponto de Atenção",
                "Direção (faixa)", "Pista", "Trecho", "Observações",
                "Fundamento da infração", "Determinação"
            ]
            
            match = True
            for key in chaves:
                val1 = str(rec.get(key, "")).strip()
                val2 = str(g_rec.get(key, "")).strip()
                if val1 != val2:
                    match = False
                    break
            
            if match:
                num_foto = rec.get("Nº")
                if num_foto not in g_rec["foto_numeros"]:
                    g_rec["foto_numeros"].append(num_foto)
                found = True
                break
                
        if not found:
            new_g_rec = rec.copy()
            new_g_rec["foto_numeros"] = [rec.get("Nº")]
            grouped.append(new_g_rec)
            
    # Formatar o texto de localização/foto de cada grupo
    for g_rec in grouped:
        faixa = str(g_rec.get("Direção (faixa)", "")).strip()
        nums = sorted(g_rec["foto_numeros"])
        
        nums_formatted = [str(n).zfill(2) for n in nums]
        if len(nums_formatted) == 1:
            fotos_str = f"Foto {nums_formatted[0]}"
        elif len(nums_formatted) == 2:
            fotos_str = f"Fotos {nums_formatted[0]} e {nums_formatted[1]}"
        else:
            fotos_str = f"Fotos {', '.join(nums_formatted[:-1])} e {nums_formatted[-1]}"
            
        g_rec["localizacao_formatada"] = f"{faixa}/ {fotos_str}" if faixa else fotos_str
        
    return grouped

def criar_tabela_quadros(doc, df_dados, is_pa, tipo_relatorio="CRA"):
    """Cria a tabela formatada de acordo com o padrão do documento de referência."""
    grouped_records = agrupar_registros(df_dados)
    num_rows = len(grouped_records)
    if num_rows == 0:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run("Nenhum registro encontrado.")
        run.font.name = 'Aptos'
        run.font.size = Pt(10)
        return
        
    table = doc.add_table(rows=2 + num_rows, cols=5)
    table.style = 'Table Grid'
    set_table_borders(table)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.allow_autofit = False
    
    # 1. Mesclar células do cabeçalho
    table.cell(0, 0).merge(table.cell(0, 1))
    table.cell(0, 2).merge(table.cell(1, 2))
    table.cell(0, 3).merge(table.cell(1, 3))
    table.cell(0, 4).merge(table.cell(1, 4))
    
    # 2. Definir os textos do cabeçalho
    if not is_pa:
        if tipo_relatorio == "CRA":
            table.cell(0, 0).text = "NÃO CONFORMIDADE (NC)"
            table.cell(1, 0).text = "IDENTIFICAÇÃO"
            table.cell(1, 1).text = "DESCRIÇÃO"
            table.cell(0, 2).text = "LOCALIZAÇÃO/\nREGISTRO FOTOGRÁFICO"
            table.cell(0, 3).text = "FUNDAMENTO DA INFRAÇÃO (PDCL)"
            table.cell(0, 4).text = "DETERMINAÇÃO"
            header_color = "D9D9D9"  # Cinza Quadro 2
            col_widths = [Inches(1.40), Inches(1.40), Inches(1.22), Inches(1.69), Inches(1.56)]
        else:
            table.cell(0, 0).text = "NÃO CONFORMIDADE (NC)"
            table.cell(1, 0).text = "IDENTIFICAÇÃO"
            table.cell(1, 1).text = "DESCRIÇÃO"
            table.cell(0, 2).text = "REGISTRO FOTOGRÁFICO"
            table.cell(0, 3).text = "FUNDAMENTO DA INFRAÇÃO (PER ANEXO IV - CONTRATO DE CONCESSÃO)"
            table.cell(0, 4).text = "DETERMINAÇÃO"
            header_color = "D9D9D9"
            col_widths = [Inches(1.34), Inches(1.68), Inches(0.81), Inches(2.46), Inches(0.98)]
    else:
        table.cell(0, 0).text = "PONTOS DE ATENÇÃO"
        table.cell(1, 0).text = "IDENTIFICAÇÃO"
        table.cell(1, 1).text = "DESCRIÇÃO DA EVIDÊNCIA"
        table.cell(0, 2).text = "LOCALIZAÇÃO/\nREGISTRO FOTOGRÁFICO"
        table.cell(0, 3).text = "JUSTIFICATIVA PARA PONTOS DE ATENÇÃO"
        table.cell(0, 4).text = "SOLICITAÇÃO"
        header_color = "E7E6E6"  # Cinza Claro Quadro 3
        col_widths = [Inches(1.18), Inches(1.74), Inches(1.14), Inches(1.81), Inches(1.40)]
        
    # Formatar cabeçalhos (Linhas 0 e 1)
    for r_idx in [0, 1]:
        row = table.rows[r_idx]
        for c_idx, cell in enumerate(row.cells):
            set_cell_shading(cell, header_color)
            set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            
            if cell.paragraphs:
                p = cell.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.0
                
                # O python-docx ao atribuir text pode limpar runs, garantimos estilo nos runs gerados
                for run in p.runs:
                    run.font.name = 'Aptos'
                    run.font.size = Pt(10)
                    run.bold = True
                    
    # Preencher dados
    for idx, rec in enumerate(grouped_records):
        r_idx = idx + 2
        row = table.rows[r_idx]
        
        ident = str(rec.get("Identificação", "")).strip()
        
        siglas_col = "Não Conformidade" if not is_pa else "Ponto de Atenção"
        siglas_str = rec.get(siglas_col, "")
        desc = expandir_siglas(siglas_str)
        
        localizacao = rec["localizacao_formatada"]
        
        fund = str(rec.get("Fundamento da infração", "")).strip()
        det = str(rec.get("Determinação", "")).strip()
        
        row.cells[0].text = ident
        row.cells[1].text = desc
        row.cells[2].text = localizacao
        row.cells[3].text = fund
        row.cells[4].text = det
        
        for c_idx, cell in enumerate(row.cells):
            set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            
            if cell.paragraphs:
                p = cell.paragraphs[0]
                if c_idx in [0, 2, 3, 4]:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                else:
                    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.0
                
                for run in p.runs:
                    run.font.name = 'Aptos'
                    run.font.size = Pt(10)
                    
    # Aplicar larguras fixas de forma robusta
    for row in table.rows:
        for c_idx, cell in enumerate(row.cells):
            cell.width = col_widths[c_idx]

    if tipo_relatorio == "CRC" and not is_pa:
        # Add TOTAL row
        r_total = table.add_row()
        # Merge first three cells (0, 1, 2)
        r_total.cells[0].merge(r_total.cells[1]).merge(r_total.cells[2])
        r_total.cells[0].text = "TOTAL"
        r_total.cells[3].text = ""
        r_total.cells[4].text = str(num_rows)
        
        # Set widths for cells after merging
        r_total.cells[0].width = col_widths[0] + col_widths[1] + col_widths[2]
        r_total.cells[3].width = col_widths[3]
        r_total.cells[4].width = col_widths[4]
        
        # Format the cells
        for c_idx, cell in enumerate(r_total.cells):
            set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            for run in p.runs:
                run.font.name = 'Aptos'
                run.font.size = Pt(10)
                run.bold = True

def gerar_secao_quadros(doc: Document, row, nc_df, tipo_relatorio="CRA"):
    """Gera a seção com as descrições e títulos dos Quadros (Quadros 1 a 5)."""
    
    if tipo_relatorio == "CRA":
        # Parágrafo 14: Os trechos com Não Conformidades...
        p1 = doc.add_paragraph()
        p1.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p1.paragraph_format.space_after = Pt(6)
        p1.paragraph_format.line_spacing = 1.15
        run1 = p1.add_run(
            "Os trechos com Não Conformidades registradas no Quadro 1 e Quadro 2, a seguir, associadas aos respectivos "
            "subtrechos, foram avaliadas pelos valores do Índice de Gravidade Global (IGG) que ultrapassaram o limite "
            "máximo previsto ≥ 30, como também os valores do Índice Irregularidade Longitudinal (IRI) que ultrapassaram o "
            "limite máximo previsto ≥ 2,7 m/km constantes do Relatório Anual 01 de novembro/2025 elaborado pelo Verificador Independente."
        )
        run1.font.name = 'Aptos'
        run1.font.size = Pt(11)
        
        # Parágrafo 15: Vazio
        doc.add_paragraph()
        
        # Parágrafo 16: Quadro 1...
        p2 = doc.add_paragraph()
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_after = Pt(6)
        run2 = p2.add_run("Quadro 1 – Aplicação dos Critérios de Elegibilidade Relativos ao Pavimento PE009")
        run2.font.name = 'Aptos'
        run2.font.size = Pt(11)
        
        # Parágrafo 17: Quadro 2...
        p3 = doc.add_paragraph()
        p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p3.paragraph_format.space_after = Pt(6)
        run3 = p3.add_run("Quadro 2 – Aplicação dos Critérios de Elegibilidade Relativos ao Pavimento VPE034")
        run3.font.name = 'Aptos'
        run3.font.size = Pt(11)
        
        # Parágrafo 18: Visando garantir...
        p4 = doc.add_paragraph()
        p4.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p4.paragraph_format.space_after = Pt(6)
        p4.paragraph_format.line_spacing = 1.15
        run4 = p4.add_run(
            "Visando garantir um pavimento de qualidade com a trafegabilidade e segurança viária para os usuários "
            "sugere-se que os Pontos de Atenção registrados no Quadro 3 sejam, tratados pela concessionaria. A seguir, "
            "estão associados aos respectivos subtrechos, possuem índices de Índice de Gravidade Global (IGG) e/ou Índice "
            "de Irregularidade Longitudinal (IRI) que não ultrapassaram o limite máximos previstos constantes do Relatório "
            "Anual 01 de novembro/2025 elaborado pelo Verificador Independente."
        )
        run4.font.name = 'Aptos'
        run4.font.size = Pt(11)
        
        # Parágrafo 19: Vazio
        doc.add_paragraph()
        
        # Parágrafo 20: Quadro 3...
        p5 = doc.add_paragraph()
        p5.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p5.paragraph_format.space_after = Pt(6)
        run5 = p5.add_run("Quadro 3 – Trecho dos pontos de Atenção:")
        run5.font.name = 'Aptos'
        run5.font.size = Pt(11)
        
        # Parágrafo 21: Vazio
        doc.add_paragraph()
        
        # Parágrafo 22: O Quadro 4, a seguir...
        p6 = doc.add_paragraph()
        p6.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p6.paragraph_format.space_after = Pt(6)
        p6.paragraph_format.line_spacing = 1.15
        
        runs_data = [
            ("O ", False),
            ("Quadro 4", True),
            (", a seguir, resume as Não Conformidades constatadas, relacionadas ao PDCL, com indicação dos respectivos registros fotográficos no ", False),
            ("Apêndice A", True),
            (" e Pontos de Atenção respectivos registros fotográficos no ", False),
            ("Apêndice B", True),
            (". A descrição da evidência está referenciada conforme a norma de descrição de defeitos do DNIT.", False)
        ]
        for text, is_bold in runs_data:
            r = p6.add_run(text)
            r.font.name = 'Aptos'
            r.font.size = Pt(11)
            if is_bold:
                r.bold = True
                
        # Parágrafo 23: Vazio
        doc.add_paragraph()
    else:
        # Modo CRC
        from utils import formatar_data_extenso
        data_extenso = formatar_data_extenso(row["Data"])
        
        adicionar_titulo_secao(doc, "5. FISCALIZAÇÃO")
        doc.add_paragraph() # Pula linha abaixo do título
        
        p1 = doc.add_paragraph()
        p1.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p1.paragraph_format.space_after = Pt(6)
        p1.paragraph_format.line_spacing = 1.15
        run1 = p1.add_run(f"As NC identificadas, em {data_extenso}, pela equipe de fiscalização da ARPE estão detalhadas no Quadro 1 a seguir.")
        run1.font.name = 'Aptos'
        run1.font.size = Pt(11)
        
        doc.add_paragraph() # Parágrafo vazio

    # Obter dados de NC e PA
    id_fisc = row["ID da Fiscalização"]
    current_ncs = nc_df[nc_df["ID da Fiscalização"] == id_fisc] if nc_df is not None else pd.DataFrame()
    
    ncs_reais = pd.DataFrame()
    pas_reais = pd.DataFrame()
    if not current_ncs.empty:
        if "Não Conformidade" in current_ncs.columns:
            ncs_reais = current_ncs[current_ncs["Não Conformidade"].fillna("").astype(str).str.strip() != ""].copy()
        if tipo_relatorio == "CRA" and "Ponto de Atenção" in current_ncs.columns:
            pas_reais = current_ncs[current_ncs["Ponto de Atenção"].fillna("").astype(str).str.strip() != ""].copy()
            
    try:
        mes_ano = formatar_mes_ano(row["Data"]).replace(", ", "/").lower()
    except Exception:
        mes_ano = "junho/2026"

    # Data formatada abreviada (dd/mm/aaaa) para o Quadro 1 do CRC
    try:
        dt_obj = pd.to_datetime(row["Data"])
        data_abreviada = dt_obj.strftime("%d/%m/%Y")
    except Exception:
        data_abreviada = "27/05/2026"

    if tipo_relatorio == "CRA":
        # Parágrafo 24: Quadro 4 title...
        p7 = doc.add_paragraph()
        p7.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p7.paragraph_format.space_after = Pt(6)
        
        r7_1 = p7.add_run("Quadro 4")
        r7_1.bold = True
        r7_1.font.name = 'Aptos'
        r7_1.font.size = Pt(11)
        
        r7_2 = p7.add_run(f" – Determinações para Não Conformidades Identificadas – {mes_ano}")
        r7_2.font.name = 'Aptos'
        r7_2.font.size = Pt(11)
        
        # Tabela de Não Conformidades (Quadro 4)
        criar_tabela_quadros(doc, ncs_reais, is_pa=False, tipo_relatorio=tipo_relatorio)
        
        # Parágrafo 25: Vazio
        doc.add_paragraph()
        
        # Parágrafo 26: Quadro 5 title...
        p8 = doc.add_paragraph()
        p8.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p8.paragraph_format.space_after = Pt(6)
        
        r8_1 = p8.add_run("Quadro 5")
        r8_1.bold = True
        r8_1.font.name = 'Aptos'
        r8_1.font.size = Pt(11)
        
        r8_2 = p8.add_run(" – Pontos de Atenção por Rodovia/Sentido")
        r8_2.font.name = 'Aptos'
        r8_2.font.size = Pt(11)
        
        # Tabela de Pontos de Atenção (Quadro 5)
        criar_tabela_quadros(doc, pas_reais, is_pa=True, tipo_relatorio=tipo_relatorio)
        
        # Parágrafos 27, 28, 29: Vazios
        doc.add_paragraph()
        doc.add_paragraph()
        doc.add_paragraph()
    else:
        # Quadro 1 do CRC
        p7 = doc.add_paragraph()
        p7.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p7.paragraph_format.space_after = Pt(6)
        
        r7_1 = p7.add_run("QUADRO 1")
        r7_1.bold = True
        r7_1.font.name = 'Aptos'
        r7_1.font.size = Pt(11)
        
        r7_2 = p7.add_run(f" – NÃO CONFORMIDADES IDENTIFICADAS CRC - {data_abreviada}")
        r7_2.bold = True
        r7_2.font.name = 'Aptos'
        r7_2.font.size = Pt(11)
        
        # Tabela de Não Conformidades (Quadro 1)
        criar_tabela_quadros(doc, ncs_reais, is_pa=False, tipo_relatorio=tipo_relatorio)
        
        doc.add_paragraph() # Parágrafo vazio
        
        # Observação abaixo da tabela no CRC (P67):
        p8 = doc.add_paragraph()
        p8.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p8.paragraph_format.space_before = Pt(6)
        p8.paragraph_format.space_after = Pt(6)
        p8.paragraph_format.line_spacing = 1.15
        run8 = p8.add_run("É importante destacar que as Não Conformidades apontadas se referem à segurança dos pedestres na rodovia, visando evitar a ocorrência de acidentes.")
        run8.font.name = 'Aptos'
        run8.font.size = Pt(11)
