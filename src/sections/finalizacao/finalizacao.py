from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from utils import adicionar_titulo_secao

def gerar_secao_finalizacao(doc: Document):
    """Gera o restante do relatório a partir da seção 5 (Determinações Gerais) até as assinaturas finais."""
    
    # ----------------------------------------------------
    # 5. DETERMINAÇÕES GERAIS
    # ----------------------------------------------------
    doc.add_paragraph()  # Espaço
    adicionar_titulo_secao(doc, "5. DETERMINAÇÕES GERAIS")
    doc.add_paragraph()  # Pula linha abaixo do título
    
    p_det1 = doc.add_paragraph()
    p_det1.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_det1.paragraph_format.space_after = Pt(6)
    p_det1.paragraph_format.line_spacing = 1.15
    run_det1 = p_det1.add_run(
        "Considerando os dispositivos contratuais pertinentes e visando garantir a qualidade dos serviços prestados, "
        "determina-se que a CRA tome as seguintes medidas através de um plano de ação:"
    )
    run_det1.font.name = 'Aptos'
    run_det1.font.size = Pt(11)
    
    p_det2 = doc.add_paragraph()
    p_det2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_det2.paragraph_format.space_after = Pt(6)
    p_det2.paragraph_format.line_spacing = 1.15
    
    r_det2_1 = p_det2.add_run("Medidas de Manutenção / Conservação,")
    r_det2_1.bold = True
    r_det2_1.font.name = 'Aptos'
    r_det2_1.font.size = Pt(11)
    
    r_det2_2 = p_det2.add_run(
        " detalhando cronograma com trechos a executar de forma que permita à Arpe uma programação mais efetiva do "
        "monitoramento de suas soluções a execução de cada subtrecho, conforme o modelo encaminhado para 2025 "
        "(Cronograma de Conserva Especial do Pavimento CRA 2025)."
    )
    r_det2_2.font.name = 'Aptos'
    r_det2_2.font.size = Pt(11)
    
    p_det3 = doc.add_paragraph()
    p_det3.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_det3.paragraph_format.space_after = Pt(6)
    p_det3.paragraph_format.line_spacing = 1.15
    
    r_det3_1 = p_det3.add_run("Medidas imediatas")
    r_det3_1.bold = True
    r_det3_1.font.name = 'Aptos'
    r_det3_1.font.size = Pt(11)
    
    r_det3_2 = p_det3.add_run(
        " resolutividade das NC de Sinalização, nos prazos estabelecidos no subitem 4.1.3.3.2.4. Tachas e Tachões "
        "Refletivos do PDCL, conforme disposto no Quadro 1, na coluna denominada Determinações."
    )
    r_det3_2.font.name = 'Aptos'
    r_det3_2.font.size = Pt(11)
    
    doc.add_paragraph()  # Espaço
    
    # ----------------------------------------------------
    # 6. RECOMENDAÇÕES
    # ----------------------------------------------------
    adicionar_titulo_secao(doc, "6. RECOMENDAÇÕES")
    doc.add_paragraph()  # Pula linha abaixo do título
    
    p_rec1 = doc.add_paragraph()
    p_rec1.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_rec1.paragraph_format.space_after = Pt(6)
    p_rec1.paragraph_format.line_spacing = 1.15
    run_rec1 = p_rec1.add_run(
        "Considerando as disposições do Contrato de Concessão, em especial, o Anexo IV - PDCL, Outras Sinalizações, "
        "dados do Relatório Anual 01 de novembro/2025 elaborado VI, e outras legislação aplicável, devem ser "
        "observadas pela CRA as seguintes recomendações:"
    )
    run_rec1.font.name = 'Aptos'
    run_rec1.font.size = Pt(11)
    
    p_rec2 = doc.add_paragraph()
    p_rec2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_rec2.paragraph_format.space_after = Pt(6)
    p_rec2.paragraph_format.line_spacing = 1.15
    run_rec2 = p_rec2.add_run(
        "Levantar a necessidade de reposição da SINALIZAÇÃO por tachas e tachões em todo o complexo viário Express Way, "
        " em especial a retirada das tachar anteriores danificadas que podem causar risco a segurança dos usuários. "
        "O vi verificou deficiências em todos os trechos."
    )
    run_rec2.font.name = 'Aptos'
    run_rec2.font.size = Pt(11)
    
    doc.add_paragraph()  # Espaço
    
    # ----------------------------------------------------
    # 7. CONCLUSÕES
    # ----------------------------------------------------
    adicionar_titulo_secao(doc, "7. CONCLUSÕES")
    doc.add_paragraph()  # Pula linha abaixo do título
    
    p_con1 = doc.add_paragraph()
    p_con1.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_con1.paragraph_format.space_after = Pt(6)
    p_con1.paragraph_format.line_spacing = 1.15
    run_con1 = p_con1.add_run(
        "Tendo em vista as ações de fiscalização realizadas pela Arpe foram constatadas quatorze (14) pontos ou trechos "
        "fiscalizados que apresentaram Não Conformidades distribuídas majoritariamente na PE 009, estas foram "
        "analisadas e caracterizadas a partir dos indicadores do Grupo Condição de Superfície definidos no Contrato de Concessão CT. nº 043/2011."
    )
    run_con1.font.name = 'Aptos'
    run_con1.font.size = Pt(11)
    
    p_con2 = doc.add_paragraph()
    p_con2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_con2.paragraph_format.space_after = Pt(6)
    p_con2.paragraph_format.line_spacing = 1.15
    run_con2 = p_con2.add_run(
        "Assim considerando a Programação de Conserva Especial do Pavimento - CRA 2026, solicita-se a inclusão destas "
        "não conformidades no cronograma detalhado de Conserva Especial do Pavimento que permita à Arpe uma "
        "realização mais efetiva dos monitoramentos ao longo de 2026."
    )
    run_con2.font.name = 'Aptos'
    run_con2.font.size = Pt(11)
    
    p_con3 = doc.add_paragraph()
    p_con3.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_con3.paragraph_format.space_after = Pt(6)
    p_con3.paragraph_format.line_spacing = 1.15
    run_con3 = p_con3.add_run(
        "Recomenda-se, por fim, o encaminhamento deste Relatório de Fiscalização para que Suape, na qualidade de "
        "Gestor do Contrato e Regulador desse Sistema Viário, realize as providências cabíveis junto à Concessionária Rota do "
        "Atlântico com o objetivo de garantir a regularização das Não Conformidades pendentes apontadas por esta Agência de Regulação."
    )
    run_con3.font.name = 'Aptos'
    run_con3.font.size = Pt(11)
    
    # Local e Data após conclusões
    p_loc1 = doc.add_paragraph()
    p_loc1.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_loc1.paragraph_format.space_after = Pt(6)
    run_loc1 = p_loc1.add_run("Recife, data da assinatura eletrônica.")
    run_loc1.font.name = 'Aptos'
    run_loc1.font.size = Pt(11)
    
    doc.add_paragraph()  # Espaço antes dos apêndices
    
    # ----------------------------------------------------
    # APÊNDICES
    # ----------------------------------------------------
    adicionar_titulo_secao(doc, "APÊNDICE A – REGISTROS FOTOGRÁFICOS DAS NÃO CONFORMIDADES")
    doc.add_paragraph()
    doc.add_paragraph()
    doc.add_paragraph()
    doc.add_paragraph()
    
    adicionar_titulo_secao(doc, "APÊNDICE B – REGISTROS FOTOGRÁFICOS DAS PONTOS DE ATENÇÃO")
    doc.add_paragraph()
    doc.add_paragraph()
    
    p_loc2 = doc.add_paragraph()
    p_loc2.paragraph_format.space_before = Pt(12)
    p_loc2.paragraph_format.space_after = Pt(12)
    run_loc2 = p_loc2.add_run("Recife, data da assinatura eletrônica.")
    run_loc2.font.name = 'Aptos'
    run_loc2.font.size = Pt(11)
    
    # ----------------------------------------------------
    # ASSINATURAS FINAIS
    # ----------------------------------------------------
    doc.add_paragraph()
    doc.add_paragraph()
    
    # Alcides
    p_ass1 = doc.add_paragraph()
    p_ass1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ass1.paragraph_format.space_after = Pt(0)
    run_ass1 = p_ass1.add_run("Alcides Vieira de Azevedo Bezerra")
    run_ass1.bold = True
    run_ass1.font.name = 'Aptos'
    run_ass1.font.size = Pt(11)
    
    p_carg1 = doc.add_paragraph()
    p_carg1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_carg1.paragraph_format.space_after = Pt(0)
    run_carg1 = p_carg1.add_run("Analista de Regulação")
    run_carg1.font.name = 'Aptos'
    run_carg1.font.size = Pt(11)
    
    p_mat1 = doc.add_paragraph()
    p_mat1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_mat1.paragraph_format.space_after = Pt(12)
    run_mat1 = p_mat1.add_run("Matrícula 40672015/01")
    run_mat1.font.name = 'Aptos'
    run_mat1.font.size = Pt(11)
    
    doc.add_paragraph()  # Espaço entre assinaturas
    
    # Enildo
    p_ass2 = doc.add_paragraph()
    p_ass2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ass2.paragraph_format.space_after = Pt(0)
    run_ass2 = p_ass2.add_run("Enildo Manoel da Silva Júnior")
    run_ass2.bold = True
    run_ass2.font.name = 'Aptos'
    run_ass2.font.size = Pt(11)
    
    p_carg2 = doc.add_paragraph()
    p_carg2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_carg2.paragraph_format.space_after = Pt(0)
    run_carg2 = p_carg2.add_run("Analista de Regulação")
    run_carg2.font.name = 'Aptos'
    run_carg2.font.size = Pt(11)
    
    p_mat2 = doc.add_paragraph()
    p_mat2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_mat2.paragraph_format.space_after = Pt(12)
    run_mat2 = p_mat2.add_run("Matrícula nº 1796500/02")
    run_mat2.font.name = 'Aptos'
    run_mat2.font.size = Pt(11)
    
    doc.add_paragraph()  # Espaço
    
    # Ciente e de acordo
    p_ciente = doc.add_paragraph()
    p_ciente.paragraph_format.space_before = Pt(12)
    p_ciente.paragraph_format.space_after = Pt(12)
    run_ciente = p_ciente.add_run("Ciente e de acordo.")
    run_ciente.font.name = 'Aptos'
    run_ciente.font.size = Pt(11)
    
    doc.add_paragraph()  # Espaço antes de Maria Ângela
    
    # Maria Ângela
    p_ass3 = doc.add_paragraph()
    p_ass3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ass3.paragraph_format.space_after = Pt(0)
    run_ass3 = p_ass3.add_run("Maria Ângela Albuquerque de Freitas")
    run_ass3.bold = True
    run_ass3.font.name = 'Aptos'
    run_ass3.font.size = Pt(11)
    
    p_carg3 = doc.add_paragraph()
    p_carg3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_carg3.paragraph_format.space_after = Pt(0)
    run_carg3 = p_carg3.add_run("Coordenadora de Transportes e Rodovias")
    run_carg3.font.name = 'Aptos'
    run_carg3.font.size = Pt(11)
    
    p_mat3 = doc.add_paragraph()
    p_mat3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_mat3.paragraph_format.space_after = Pt(12)
    run_mat3 = p_mat3.add_run("Matrícula nº 209640/01")
    run_mat3.font.name = 'Aptos'
    run_mat3.font.size = Pt(11)
