from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from utils import adicionar_titulo_secao, extrair_ano
from database.manager import carregar_responsaveis, carregar_coordenadores

def numero_por_extenso(n):
    extenso_map = {
        0: "zero", 1: "um", 2: "dois", 3: "três", 4: "quatro", 5: "cinco",
        6: "seis", 7: "sete", 8: "oito", 9: "nove", 10: "dez",
        11: "onze", 12: "doze", 13: "treze", 14: "quatorze", 15: "quinze",
        16: "dezesseis", 17: "dezessete", 18: "dezoito", 19: "dezenove", 20: "vinte",
        21: "vinte e um", 22: "vinte e dois", 23: "vinte e três", 24: "vinte e quatro",
        25: "vinte e cinco", 26: "vinte e seis", 27: "vinte e sete", 28: "vinte e oito",
        29: "vinte e nove", 30: "trinta", 31: "trinta e um", 32: "trinta e dois",
        33: "trinta e três", 34: "trinta e quatro", 35: "trinta e cinco",
        36: "trinta e seis", 37: "trinta e sete", 38: "trinta e oito", 39: "trinta e nove",
        40: "quarenta", 41: "quarenta e um", 42: "quarenta e dois", 43: "quarenta e três",
        44: "quarenta e quatro", 45: "quarenta e cinco", 46: "quarenta e seis",
        47: "quarenta e sete", 48: "quarenta e oito", 49: "quarenta e nove", 50: "cinquenta"
    }
    return extenso_map.get(n, str(n))

def gerar_secao_finalizacao(doc: Document, row, total_ncs):
    """Gera o restante do relatório a partir da seção 5 (Determinações Gerais) até as assinaturas finais."""
    
    ano = extrair_ano(row["Data"])
    ano_anterior = str(int(ano) - 1) if ano.isdigit() else "2025"

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
        f" detalhando cronograma com trechos a executar de forma que permita à Arpe uma programação mais efetiva do "
        f"monitoramento de suas soluções a execução de cada subtrecho, conforme o modelo encaminhado para {ano_anterior} "
        f"(Cronograma de Conserva Especial do Pavimento CRA {ano_anterior})."
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
    
    extenso_ncs = numero_por_extenso(total_ncs)
    run_con1 = p_con1.add_run(
        f"Tendo em vista as ações de fiscalização realizadas pela Arpe foram constatadas {extenso_ncs} ({total_ncs}) pontos ou trechos "
        f"fiscalizados que apresentaram Não Conformidades distribuídas majoritariamente na PE 009, estas foram "
        f"analisadas e caracterizadas a partir dos indicadores do Grupo Condição de Superfície definidos no Contrato de Concessão CT. nº 043/2011."
    )
    run_con1.font.name = 'Aptos'
    run_con1.font.size = Pt(11)
    
    p_con2 = doc.add_paragraph()
    p_con2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_con2.paragraph_format.space_after = Pt(6)
    p_con2.paragraph_format.line_spacing = 1.15
    run_con2 = p_con2.add_run(
        f"Assim considerando a Programação de Conserva Especial do Pavimento - CRA {ano}, solicita-se a inclusão destas "
        f"não conformidades no cronograma detalhado de Conserva Especial do Pavimento que permita à Arpe uma "
        f"realização mais efetiva dos monitoramentos ao longo de {ano}."
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
    # ASSINATURAS FINAIS DINÂMICAS
    # ----------------------------------------------------
    doc.add_paragraph()
    doc.add_paragraph()
    
    responsaveis_list = [r.strip() for r in str(row["Pessoal Responsável"]).split(",") if r.strip()]
    db_resp = carregar_responsaveis()
    
    for nome in responsaveis_list:
        match = next((d for d in db_resp if d["nome"].strip().lower() == nome.lower()), None)
        if match:
            r_nome = match["nome"]
            r_funcao = match["funcao"]
            r_matr = match["matricula"]
        else:
            r_nome = nome
            r_funcao = "Analista de Regulação"
            r_matr = "xxxxxxx/xx"
            
        p_ass = doc.add_paragraph()
        p_ass.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_ass.paragraph_format.space_after = Pt(0)
        run_ass = p_ass.add_run(r_nome)
        run_ass.bold = True
        run_ass.font.name = 'Aptos'
        run_ass.font.size = Pt(11)
        
        p_carg = doc.add_paragraph()
        p_carg.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_carg.paragraph_format.space_after = Pt(0)
        run_carg = p_carg.add_run(r_funcao)
        run_carg.font.name = 'Aptos'
        run_carg.font.size = Pt(11)
        
        p_mat = doc.add_paragraph()
        p_mat.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_mat.paragraph_format.space_after = Pt(12)
        run_mat = p_mat.add_run(f"Matrícula nº {r_matr}")
        run_mat.font.name = 'Aptos'
        run_mat.font.size = Pt(11)
        
        doc.add_paragraph()  # Espaço entre assinaturas
        
    # Ciente e de acordo (Coordenador)
    p_ciente = doc.add_paragraph()
    p_ciente.paragraph_format.space_before = Pt(12)
    p_ciente.paragraph_format.space_after = Pt(12)
    run_ciente = p_ciente.add_run("Ciente e de acordo.")
    run_ciente.font.name = 'Aptos'
    run_ciente.font.size = Pt(11)
    
    doc.add_paragraph()  # Espaço antes da assinatura do coordenador
    
    db_coord = carregar_coordenadores()
    coord_name = str(row["Coordenador"]).strip()
    match_coord = next((c for c in db_coord if c["nome"].strip().lower() == coord_name.lower()), None)
    if match_coord:
        c_nome = match_coord["nome"]
        c_funcao = match_coord["funcao"]
        c_matr = match_coord["matricula"]
    else:
        c_nome = coord_name
        c_funcao = "Coordenador(a) de Transportes e Rodovias"
        c_matr = "xxxxxxx/xx"
        
    p_ass3 = doc.add_paragraph()
    p_ass3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ass3.paragraph_format.space_after = Pt(0)
    run_ass3 = p_ass3.add_run(c_nome)
    run_ass3.bold = True
    run_ass3.font.name = 'Aptos'
    run_ass3.font.size = Pt(11)
    
    p_carg3 = doc.add_paragraph()
    p_carg3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_carg3.paragraph_format.space_after = Pt(0)
    run_carg3 = p_carg3.add_run(c_funcao)
    run_carg3.font.name = 'Aptos'
    run_carg3.font.size = Pt(11)
    
    p_mat3 = doc.add_paragraph()
    p_mat3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_mat3.paragraph_format.space_after = Pt(12)
    run_mat3 = p_mat3.add_run(f"Matrícula nº {c_matr}")
    run_mat3.font.name = 'Aptos'
    run_mat3.font.size = Pt(11)
