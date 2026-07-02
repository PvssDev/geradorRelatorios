from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

def gerar_secao_quadros(doc: Document):
    """Gera a seção com as descrições e títulos dos Quadros (Quadros 1 a 5)."""
    
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
    
    # Runs de O Quadro 4
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
    
    # Parágrafo 24: Quadro 4 title...
    p7 = doc.add_paragraph()
    p7.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p7.paragraph_format.space_after = Pt(6)
    
    r7_1 = p7.add_run("Quadro 4")
    r7_1.bold = True
    r7_1.font.name = 'Aptos'
    r7_1.font.size = Pt(11)
    
    r7_2 = p7.add_run(" – Não Conformidades por Rodovia/Sentido")
    r7_2.font.name = 'Aptos'
    r7_2.font.size = Pt(11)
    
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
    
    # Parágrafos 27, 28, 29: Vazios
    doc.add_paragraph()
    doc.add_paragraph()
    doc.add_paragraph()
