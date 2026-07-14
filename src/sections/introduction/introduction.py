from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from utils import adicionar_titulo_secao, formatar_data_extenso, extrair_ano
import os
import pandas as pd

def gerar_secao_introducao(doc: Document, row, total_achados, tipo_relatorio="CRA"):
    """Gera as seções de Introdução, Objetivo, Informações Gerais, Metodologia e Fiscalização."""
    
    ano = extrair_ano(row["Data"])
    data_extenso = formatar_data_extenso(row["Data"])

    # ----------------------------------------------------
    # 1. SEÇÃO: INTRODUÇÃO (Seção 1)
    # ----------------------------------------------------
    adicionar_titulo_secao(doc, "1. INTRODUÇÃO")
    doc.add_paragraph()  # Pula uma linha abaixo do título
    
    if tipo_relatorio == "CRA":
        paragraphs_intro = [
            f"A Coordenadoria de Transporte e Rodovias da Arpe implementou o cronograma de fiscalização para {ano} do Complexo Viário e Logístico de SUAPE, sob a responsabilidade da Concessionária Rota do Atlântico (CRA), visualizando a necessidade de serem reservados dois dias consecutivos, para melhor estruturar suas ações de fiscalização técnico-operacionais da Rodovia.",
            "Ainda com a visão de implantar melhorias na contribuição da Agência sobre os trabalhos desenvolvidos na rodovia, foi introduzida uma visita técnica prévia, realizada uma semana antes do período de fiscalização, com o objetivo de elaborar um roteiro que é encaminhado para a CRA e SUAPE contendo os trechos mapeados com possíveis Não Conformidades, tornando os levantamentos fotográficos mais ágeis e a fiscalização efetiva.",
            "Posteriormente, as possíveis Não Conformidades levantadas in campo são analisadas de acordo com os critérios elencados no PDCL anexo ao Contrato de Concessão, em conjunto com o último Relatório Anual elaborado pelo Verificador Independente.",
            "Destaca-se preliminarmente que as ações de fiscalização registradas neste Relatório foram concentradas na Rodovia PE-009, do Entroncamento BR-101 ao Entroncamento PE-038, que abrange os subtrechos concedidos, especificamente, o Contorno do Cabo, TDR Norte, TDR Sul e a Ligação Rótula Curva do Boi a Nossa Senhora do Ó; e Rodovia Estadual VPE-034.",
            f"É importante observar que foram realizadas ações de fiscalização, no dia {data_extenso}, conforme comunicado enviado à SUAPE por meio do Ofício Arpe/DTO nº 302 (Doc. SEI 75605952).",
            "Destaca-se que as fiscalizações realizadas pela Arpe são tratadas com caráter educativo, preferencialmente, e contributivo para correção de procedimentos e solução de Não Conformidades evidenciados por defeitos e/ou problemas na infraestrutura disponibilizada e respectivos serviços concedidos pelo Estado."
        ]
    else:
        paragraphs_intro = [
            f"A Coordenadoria de Transportes e Rodovias da ARPE, em cumprimento ao cronograma de fiscalização de {ano}, realizou fiscalização na Concessão Patrocinada da Ponte de Acesso e Sistema Viário da Praia do Paiva, sob responsabilidade da Concessionária Rota dos Coqueiros (CRC). A ação foi comunicada à concessionária por meio do Ofício ARPE/DTO nº 145/2026, de 26/05/2026 (Doc. SEI nº 86328395), e à Secretaria Executiva de Parcerias e Projetos Estratégicos (SEPPE) por meio do Ofício ARPE/DTO nº 146/2026, de 26/05/2026 (Doc. SEI nº 86328735).",
            "As ações de fiscalização registradas neste Relatório se referem à Rodovia Estadual PE-024, trecho Barra de Jangada – Itapuama, medindo 6,5 Km de extensão, compreendendo duas praças de pedágio, pela Ponte sobre o Rio Jaboatão e a via principal do Destino de Turismo e Lazer Praia do Paiva.",
            "Este relatório apresenta as observações realizadas pela equipe da Coordenadoria de Transportes e Rodovias da ARPE, sob a perspectiva técnico-operacional, com o objetivo de verificar as condições de operação, conservação, manutenção e segurança do trecho rodoviário concedido, bem como o cumprimento da legislação aplicável e a eficiência dos serviços prestados.",
            "As fiscalizações realizadas pela ARPE possuem, prioritariamente, caráter orientativo e corretivo, visando contribuir para o aperfeiçoamento dos procedimentos e para a correção de não conformidades identificadas na infraestrutura disponibilizada e nos serviços concedidos pelo Estado."
        ]

    for text in paragraphs_intro:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15
        
        if "302 (Doc. SEI 75605952)" in text:
            # Divide o texto para colorir "302 (Doc. SEI 75605952)" em vermelho
            part1 = f"É importante observar que foram realizadas ações de fiscalização, no dia {data_extenso}, conforme comunicado enviado à SUAPE por meio do Ofício Arpe/DTO nº "
            part2 = "302 (Doc. SEI 75605952)"
            part3 = "."
            
            run1 = p.add_run(part1)
            run1.font.name = 'Aptos'
            run1.font.size = Pt(11)
            
            run2 = p.add_run(part2)
            run2.font.name = 'Aptos'
            run2.font.size = Pt(11)
            from docx.shared import RGBColor
            run2.font.color.rgb = RGBColor(255, 0, 0)
            
            run3 = p.add_run(part3)
            run3.font.name = 'Aptos'
            run3.font.size = Pt(11)
        else:
            run = p.add_run(text)
            run.font.name = 'Aptos'
            run.font.size = Pt(11)

    # ----------------------------------------------------
    # 2. SEÇÃO: OBJETIVO (Seção 2)
    # ----------------------------------------------------
    adicionar_titulo_secao(doc, "2. OBJETIVO")
    doc.add_paragraph()  # Pula uma linha abaixo do título
    
    if tipo_relatorio == "CRA":
        text_objetivo = (
            "A fiscalização direta e periódica do complexo viário e logístico de Suape – Expressway concedido à CRA, "
            "tem por objetivo verificar as condições de operação, manutenção, segurança viária e níveis de serviço, bem "
            "como identificar não conformidades, subsidiar medidas corretivas e assegurar a observância das disposições "
            "contratuais, regulamentares e normativas aplicáveis, preservando a segurança, a qualidade do serviço, e a "
            "adequada prestação do serviço público aos usuários. Dessa forma a ação de fiscalização da Arpe verifica o grau "
            "de conformidade dessas instalações com o Contrato de Concessão, bem como com a legislação e normas vigentes "
            "de modo a determinar/ou recomendar medidas corretivas, com foco na qualidade dos serviços prestados."
        )
        
        p_obj = doc.add_paragraph()
        p_obj.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_obj.paragraph_format.space_after = Pt(12)
        p_obj.paragraph_format.line_spacing = 1.15
        run_obj = p_obj.add_run(text_objetivo)
        run_obj.font.name = 'Aptos'
        run_obj.font.size = Pt(11)
    else:
        text_obj_1 = (
            "A fiscalização direta e periódica do Sistema Viário do Paiva, concedido à CRC, tem por objetivo verificar "
            "as condições de operação, manutenção, segurança viária e níveis de serviço, bem como identificar não "
            "conformidades, subsidiar a adoção de medidas corretivas e assegurar o cumprimento das disposições contratuais, "
            "regulamentares e normativas aplicáveis, visando à preservação da segurança, da qualidade dos serviços e da "
            "adequada prestação do serviço público aos usuários."
        )
        text_obj_2 = (
            "Nesse contexto, a ação fiscalizatória da ARPE avalia o grau de conformidade da infraestrutura e dos serviços "
            "prestados em relação ao Contrato de Concessão, à legislação vigente e às normas aplicáveis, podendo determinar "
            "ou recomendar medidas corretivas destinadas ao aprimoramento contínuo da qualidade dos serviços."
        )
        
        for text in [text_obj_1, text_obj_2]:
            p_obj = doc.add_paragraph()
            p_obj.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p_obj.paragraph_format.space_after = Pt(6)
            p_obj.paragraph_format.line_spacing = 1.15
            run_obj = p_obj.add_run(text)
            run_obj.font.name = 'Aptos'
            run_obj.font.size = Pt(11)

    # ----------------------------------------------------
    # 3. SEÇÃO: INFORMAÇÕES GERAIS (Tabela)
    # ----------------------------------------------------
    p_info = doc.add_paragraph()
    p_info.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_info.paragraph_format.space_before = Pt(12)
    p_info.paragraph_format.space_after = Pt(12)
    
    info_title = "3. INFORMAÇÕES GERAIS" if tipo_relatorio == "CRC" else "INFORMAÇÕES GERAIS"
    run_info = p_info.add_run(info_title)
    run_info.bold = True
    run_info.font.name = 'Aptos'
    run_info.font.size = Pt(12)
    
    # Construção da tabela de Informações Gerais
    from docx.enum.table import WD_TABLE_ALIGNMENT
    num_rows = 22 if tipo_relatorio == "CRA" else 20
    table = doc.add_table(rows=num_rows, cols=2)
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

    # Responsáveis e Período dinâmicos
    responsaveis_formatted = str(row["Pessoal Responsável"]).replace(",", " e" if "," not in str(row["Pessoal Responsável"]) else ";")
    periodo_val = str(row["Período"]).strip() if pd.notna(row["Período"]) and str(row["Período"]).strip() else f"{data_extenso}."

    if tipo_relatorio == "CRA":
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
        
        format_normal_row(table.rows[19], "Responsáveis pela fiscalização:", responsaveis_formatted)
        format_normal_row(table.rows[20], "Período da Fiscalização:", periodo_val)
        format_normal_row(table.rows[21], "Tipo de Fiscalização:", "Direta e periódica.")
    else:
        # Preencher a estrutura da tabela conforme a referência (Seções 3.1, 3.2, 3.3, 3.4)
        format_header_row(table.rows[0], "3.1 DO PODER CONCEDENTE")
        format_normal_row(table.rows[1], "Titular:", "Conselho do Programa de Parcerias Estratégicas de Pernambuco– CPPPE")
        format_normal_row(table.rows[2], "Endereço:", "Rua da Moeda, nº 46, Recife-PE")
        format_normal_row(table.rows[3], "Responsável:", "MARCELO BRUTO DA COSTA CORREIA", val_bold=True)
        
        format_header_row(table.rows[4], "3.2 DO VERIFICADOR INDEPENDENTE")
        format_normal_row(table.rows[5], "Verificador Independente:", "Consórcio Estratégica e Grupo Maciel")
        format_normal_row(table.rows[6], "Endereço:", "Rua Irene Ramos Gomes de Mattos, Nº 176, Pina, Recife/PE CEP: 51011-530")
        format_normal_row(table.rows[7], "Responsável:", "José Theodozio Netto", val_bold=True)
        
        format_header_row(table.rows[8], "3.3 DO REGULADO")
        format_normal_row(table.rows[9], "Regulado:", "Concessionária Rota dos Coqueiros (CRC)")
        format_normal_row(table.rows[10], "Responsável:", "RAFAELA ELAINE DA COSTA LIMA ARAÚJO", val_bold=True)
        format_normal_row(table.rows[11], "Endereço:", "Rua Marmelo, s/nº - Praça de Pedágio – Barra de Jangada Jaboatão dos Guararapes – PE CEP: 54.495-760")
        format_normal_row(table.rows[12], "Representantes por acompanhar:", "Larissa Almeida e Everton Albuquerque")
        
        format_header_row(table.rows[13], "3.4 DO FISCALIZADOR (ARPE)")
        format_normal_row(table.rows[14], "Regulador:", "Agência de Regulação de Pernambuco (ARPE)")
        format_normal_row(table.rows[15], "Diretor Presidente:", "CARLOS PORTO FILHO", val_bold=True)
        format_normal_row(table.rows[16], "Endereço:", "Avenida Conselheiro Rosa e Silva, 975, Aflitos, Recife/PE, CEP: 52.050-020. Estacionamento: Rua do Futuro, 150, Aflitos, Recife/PE.")
        
        format_normal_row(table.rows[17], "Responsáveis pela fiscalização:", responsaveis_formatted)
        format_normal_row(table.rows[18], "Período da Fiscalização:", periodo_val)
        format_normal_row(table.rows[19], "Tipo de Fiscalização:", "Direta e periódica.")
        
    # Ajustar as larguras das colunas
    col_widths = [Inches(2.3), Inches(5.2)]
    headers_indices = [0, 5, 10, 15] if tipo_relatorio == "CRA" else [0, 4, 8, 13]
    for r_idx, row_obj in enumerate(table.rows):
        if r_idx in headers_indices:
            row_obj.cells[0].width = Inches(7.5)
        else:
            row_obj.cells[0].width = col_widths[0]
            row_obj.cells[1].width = col_widths[1]

    # ----------------------------------------------------
    # 4. SEÇÃO: METODOLOGIA
    # ----------------------------------------------------
    doc.add_paragraph()  # Pula uma linha antes do título
    metodo_title = "3. METODOLOGIA" if tipo_relatorio == "CRA" else "4. METODOLOGIA"
    adicionar_titulo_secao(doc, metodo_title)
    doc.add_paragraph()  # Pula uma linha abaixo do título
    
    # Parágrafos iniciais da Metodologia
    if tipo_relatorio == "CRA":
        paragraphs_metodo_1 = [
            f"A Coordenadoria de Transporte e Rodovias da Arpe implementou o cronograma de fiscalização para {ano} do Complexo Viário e Logístico de SUAPE reservando dois dias consecutivos, para melhor estruturar suas ações de fiscalização técnico-operacionais no Complexo Rodoviário, após uma visita técnica prévia, realizada antes do período de fiscalização, com o objetivo de elaborar um roteiro que é encaminhado para a CRA e SUAPE contendo os trechos mapeados com possíveis Não Conformidades, tornando os levantamentos fotográficos mais ágeis e a fiscalização efetiva.",
            "Posteriormente, as possíveis Não Conformidades levantadas em campo são analisadas de acordo com os critérios elencados no PDCL (Anexo IV do Contrato de Concessão), em conjunto com o último Relatório Anual elaborado pelo Verificador Independente.",
            "Assim, a fiscalização direta e periódica realizada pela Coordenadoria de Transportes e Rodovias da Arpe está submetida a uma metodologia organizada em três etapas: Preparação e Planejamento, Execução da Fiscalização e Monitoramento e Avaliação.",
            "Preparação e Planejamento - compreende a organização e estruturação das atividades preliminares à execução da fiscalização, destacando-se a elaboração e o envio de avisos de fiscalização à Concessionária e demais atividades de suporte à fiscalização, bem como a análise de fiscalizações anteriores com a identificação de eventuais Não Conformidades pendentes.",
            "Execução da Fiscalização - a execução da fiscalização é pautada por um arcabouço de normas e diretrizes, possibilitando que todas as etapas sejam desenvolvidas de maneira eficiente e em conformidade aos padrões estabelecidos, destacando-se:"
        ]
    else:
        paragraphs_metodo_1 = [
            f"A Coordenadoria de Transporte e Rodovias da ARPE realizou fiscalização direta e periódica no Sistema Viário do Paiva em {data_extenso}, seguindo metodologia estruturada em três etapas: Preparação e Planejamento, Execução da Fiscalização e Monitoramento e Avaliação.",
            "Preparação e Planejamento- compreende a organização e estruturação das atividades preliminares à execução da fiscalização, destacando-se a elaboração e o envio de avisos de fiscalização à Concessionária e demais atividades de suporte à fiscalização, bem como a análise de fiscalizações anteriores com a identificação de eventuais Não Conformidades pendentes.",
            "Execução da Fiscalização- as possíveis Não Conformidades levantadas em campo são analisadas de acordo com os critérios elencados no PER (Contrato de Concessão). A execução da fiscalização é pautada por um arcabouço de normas e diretrizes, possibilitando que todas as etapas sejam desenvolvidas de maneira eficiente e em conformidade aos padrões estabelecidos, destacando-se:"
        ]
    
    for text in paragraphs_metodo_1:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run(text)
        run.font.name = 'Aptos'
        run.font.size = Pt(11)
        
    # Referências com recuo de parágrafo estruturado nativamente no Word (Hanging Indent)
    if tipo_relatorio == "CRA":
        referencias = [
            ("Lei Estadual nº. 12.524, de 30 de dezembro de 2003, regulamentada pelo Decreto Estadual nº. 30.200, de 09 de fevereiro de 2007, que altera e consolida as disposições da Lei nº. 12.126, de 12 de dezembro de 2001, que cria a Agência de Regulação dos Serviços Públicos Delegados do Estado de Pernambuco - ARPE, e dá outras providências;", False, True),
            ("Art. 3º Compete à ARPE a regulação de todos os serviços públicos delegados pelo Estado de Pernambuco, ou por ele diretamente prestados, embora sujeitos à delegação, quer de sua competência ou a ele delegados por outros entes federados, em decorrência de norma legal ou regulamentar, disposição convenial ou contratual.", True, False),
            ("§ 1º A atividade reguladora da ARPE deverá ser exercida, em especial, nas seguintes áreas:", True, False),
            ("[...]", True, False),
            ("III - rodovias;", True, False),
            ("[...]", True, False),
            ("Art. 4º Compete ainda à ARPE:", True, False),
            ("[...]", True, False),
            ("X - Fiscalizar diretamente ou mediante convênio com o Estado de Pernambuco, através de seus órgãos ou entidades vinculadas, com sua supervisão, os aspectos técnico, econômico, contábil, financeiro, operacional e jurídico dos serviços públicos delegados, valendo-se inclusive, de indicadores e procedimentos amostrais.", True, False),
            ("", False, False),
            ("Contrato de Concessão CT. nº 043/2011, de 18 de julho de 2011, para a delegação da exploração do Complexo Viário e Logístico de SUAPE – EXPRESSWAY, conforme detalhado no Anexo IV do Edital (PDCL) e regidos pela Constituição Federal; pela Lei Federal Nº 8.987/95; Lei Federal Nº 9.074/95; Lei Federal 8.666/93 e Lei Estadual Nº 14.233/2010.", False, True),
            ("", False, False),
            ("Convênio de Cooperação Técnica n° 003/2021 de 22 de setembro 2021, firmado entre o Complexo Industrial Portuário Governador Eraldo Gueiros – SUAPE e a Agência de Regulação de Pernambuco – ARPE, e Renovação do Termo Aditivo que prorroga o prazo de vigência e execução contratual até 22 de setembro de 2026.", False, True),
            ("", False, False),
            ("Norma DNIT 005/2003 – que define os termos técnicos empregados em defeitos que ocorrem nos pavimentos flexíveis e semirrígidos e serve para padronizar a linguagem adotada na elaboração das normas, manuais, projetos e textos relativos aos pavimentos flexíveis e semirrígidos.", False, True),
            ("", False, False),
            ("Relatórios elaborados pelo Verificador Independente.", False, True)
        ]
    else:
        referencias = [
            ("Lei Estadual nº. 12.524, de 30 de dezembro de 2003, regulamentada pelo Decreto Estadual nº. 30.200, de 09 de fevereiro de 2007, que altera e consolida as disposições da Lei nº. 12.126, de 12 de dezembro de 2001, que cria a Agência de Regulação dos Serviços Públicos Delegados do Estado de Pernambuco - ARPE, e dá outras providências;", False, True),
            ("", False, False),
            ("Contrato de Concessão Patrocinada CGPE – 001/2006, de 28 de dezembro de 2006, e Termos Aditivos, para a exploração da ponte de acesso e sistema viário do destino de turismo e lazer Praia do Paiva, em conformidade com a Lei Federal nº 11.079/2004 e alterações; e a Lei Estadual nº 12.765/2005 e alterações.", False, True),
            ("", False, False),
            ("Resolução ARPE nº 083, de 30 de julho de 2013, que dispõe sobre os procedimentos de fiscalização, autuação e aplicação de penalidades aos prestadores de serviços públicos delegados no Estado de Pernambuco fiscalizados pela ARPE mediante delegação.", False, True),
            ("", False, False),
            ("Norma DNIT 005/2003 – que define os termos técnicos empregados em defeitos que ocorrem nos pavimentos flexíveis e semirrígidos e serve para padronizar a linguagem adotada na elaboração das normas, manuais, projetos e textos relativos aos pavimentos flexíveis e semirrígidos.", False, True)
        ]
        
    for text, recuado, is_bullet in referencias:
        if text == "":
            doc.add_paragraph()
            continue
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(6)
        if recuado:
            p.paragraph_format.left_indent = Pt(70.8)
            run = p.add_run(text)
            run.font.name = 'Aptos'
            run.font.size = Pt(9)
            run.font.italic = True
        elif is_bullet:
            p.paragraph_format.left_indent = Pt(36.0)
            p.paragraph_format.first_line_indent = Pt(-18.0)
            run_bullet = p.add_run("•\t")
            run_bullet.font.name = 'Aptos'
            run_bullet.font.size = Pt(11)
            run = p.add_run(text)
            run.font.name = 'Aptos'
            run.font.size = Pt(11)
        else:
            run = p.add_run(text)
            run.font.name = 'Aptos'
            run.font.size = Pt(11)

    doc.add_paragraph()
    
    # Texto de codificação das NCs
    p_cod = doc.add_paragraph()
    p_cod.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_cod.paragraph_format.space_after = Pt(6)
    p_cod.paragraph_format.line_spacing = 1.15
    run_cod = p_cod.add_run("Registra-se que as Não conformidades (NC) são codificadas de acordo com os seguintes níveis de informação, separados por “.” (ponto):")
    run_cod.font.name = 'Aptos'
    run_cod.font.size = Pt(11)
    
    if tipo_relatorio == "CRA":
        niveis = [
            "Nível 1 - três dígitos, caracterizando a concessionária: CRA ou CRC.",
            "Nível 2 - composto por cinco dígitos: os dois primeiros representam as subdivisões utilizadas na rodovia concedida, por exemplo, Trecho (TR); Subtrecho (ST); Segmento Homogêneo (SH) e os três últimos dígitos identificam a subdivisão utilizada em cada contrato.",
            "Nível 3 – composto por nove dígitos os quatro primeiros e os quatro últimos delimitam a localização das NC em escala de 0,01Km e o dígito intermediário informa se a NC é pontual \"+\" ou distribuída.",
            "Nível 4 – informa o ano da constatação da NC com quatro dígitos, antecedido de “/”.",
            "Nível 5 - contendo o sequencial numérico da NC no ano, expresso em três dígitos."
        ]
    else:
        niveis = [
            "Nível 1 - três dígitos, caracterizando a concessionária, nesse caso \"CRC\";",
            "Nível 2 - composto por cinco dígitos, os dois primeiros indicam a subdivisão utilizada na rodovia, neste caso, Segmento Homogêneo (SH) e os três últimos dígitos identificam a subdivisão utilizada no Contrato (nesse caso de 001 a 015);",
            "Nível 3 – composto por nove dígitos os quatro primeiros e os quatro últimos delimitam a localização das NC em escala de 0,01Km e o dígito intermediário informa se a NC é pontual \"+\" ou distribuída \"-\";",
            "Nível 4 – informa o ano da constatação da NC com quatro dígitos, antecedido de “/”; e",
            "Nível 5 - contém o sequencial numérico da NC no ano, expresso em três dígitos."
        ]
        
    for niv in niveis:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_after = Pt(0)  # Uma linha abaixo da outra, sem espaço extra
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.left_indent = Pt(54.0)       # Recuo da margem para o texto (0.75 in)
        p.paragraph_format.first_line_indent = Pt(-18.0) # Hanging Indent para o marcador (bullet)
        
        run_bullet = p.add_run("•\t")
        run_bullet.font.name = 'Aptos'
        run_bullet.font.size = Pt(11)
        
        run = p.add_run(niv)
        run.font.name = 'Aptos'
        run.font.size = Pt(11)
        
    # Exemplo (Sem pular linha antes)
    p_ex_label = doc.add_paragraph()
    p_ex_label.paragraph_format.left_indent = Pt(72.0)
    p_ex_label.paragraph_format.space_after = Pt(6)
    run_ex_lbl = p_ex_label.add_run("Exemplo:")
    run_ex_lbl.font.name = 'Aptos'
    run_ex_lbl.font.size = Pt(11)
    
    p_ex_val = doc.add_paragraph()
    p_ex_val.paragraph_format.left_indent = Pt(120.5)
    p_ex_val.paragraph_format.space_after = Pt(6)
    ex_str = "CRA.ST601.2794-2834/2025.013" if tipo_relatorio == "CRA" else "CRC.SH015.0646+0648/2026.001"
    run_ex_val = p_ex_val.add_run(ex_str)
    run_ex_val.bold = True
    run_ex_val.font.name = 'Aptos'
    run_ex_val.font.size = Pt(11)
    
    p_ex_desc = doc.add_paragraph()
    p_ex_desc.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_ex_desc.paragraph_format.left_indent = Pt(120.5)
    p_ex_desc.paragraph_format.space_after = Pt(6)
    p_ex_desc.paragraph_format.line_spacing = 1.15
    ex_desc_str = (
        "Indica que esta Não Conformidade foi apontada para a CRA, no subtrecho 6.01, distribuída do km 27,94 ao km 28,34, sendo a 13ª NC registrada pela Arpe em 2025"
        if tipo_relatorio == "CRA" else
        "Indica que esta Não Conformidade foi apontada para a CRC, no Segmento Homogêneo 15, concentrado na praça de pedágio do km 6,46 ao km 6,48, sendo a primeira NC registrada pela ARPE em 2026."
    )
    run_ex_desc = p_ex_desc.add_run(ex_desc_str)
    run_ex_desc.font.name = 'Aptos'
    run_ex_desc.font.size = Pt(11)
    
    # Monitoramento e Avaliação (Sem pular linha antes)
    p_mon = doc.add_paragraph()
    p_mon.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_mon.paragraph_format.space_after = Pt(6)
    p_mon.paragraph_format.line_spacing = 1.15
    run_mon_bold = p_mon.add_run("Monitoramento e Avaliação")
    run_mon_bold.bold = True
    run_mon_bold.font.name = 'Aptos'
    run_mon_bold.font.size = Pt(11)
    
    run_mon_text = p_mon.add_run(" - Esta etapa é fundamental para garantir a eficácia das ações corretivas a serem executadas pela Concessionária para a melhoria contínua dos serviços prestados. Os principais instrumentos do Monitoramento e Avaliação são: Termo de Notificação e respectivo Relatório de Fiscalização, Plano de Ação da Concessionária e Relatórios de Monitoramento e Avaliação Final.")
    run_mon_text.font.name = 'Aptos'
    run_mon_text.font.size = Pt(11)

    # ----------------------------------------------------
    # 5. SEÇÃO: FISCALIZAÇÃO
    # ----------------------------------------------------
    if tipo_relatorio == "CRA":
        fisc_title = "4. FISCALIZAÇÃO"
        adicionar_titulo_secao(doc, fisc_title)
        doc.add_paragraph()  # Pula uma linha abaixo do título
        
        # Parágrafo 1 de Fiscalização Dinâmico
        p_fisc1 = doc.add_paragraph()
        p_fisc1.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_fisc1.paragraph_format.space_after = Pt(6)
        p_fisc1.paragraph_format.line_spacing = 1.15
        
        p_fisc1.add_run("As ações de fiscalização foram realizadas pela equipe formada pelos servidores: ").font.name = 'Aptos'
        
        from database.manager import carregar_responsaveis
        responsaveis_list = [r.strip() for r in str(row["Pessoal Responsável"]).split(",") if r.strip()]
        db_resp = carregar_responsaveis()
        
        team_parts = []
        for nome in responsaveis_list:
            match = next((d for d in db_resp if d["nome"].strip().lower() == nome.lower()), None)
            if match:
                team_parts.append({"nome": match["nome"], "matricula": match["matricula"]})
            else:
                team_parts.append({"nome": nome, "matricula": "xxxxxxx/xx"})
                
        for i, member in enumerate(team_parts):
            r_name = p_fisc1.add_run(member["nome"])
            r_name.bold = True
            r_name.font.name = 'Aptos'
            p_fisc1.add_run(f", matrícula nº {member['matricula']}").font.name = 'Aptos'
            
            if i < len(team_parts) - 2:
                p_fisc1.add_run(", ").font.name = 'Aptos'
            elif i == len(team_parts) - 2:
                p_fisc1.add_run(" e ").font.name = 'Aptos'
                
        fisc_sufixo = f" nos dias {data_extenso}. Nessas ações foram identificados {total_achados} achados de fiscalização nas áreas sob concessão por meio de um levantamento de campo nas Rodovias com evidências de defeitos que poderiam se caracterizar Não Conformidades."
        p_fisc1.add_run(fisc_sufixo).font.name = 'Aptos'
        
        # Parágrafo 2 de Fiscalização
        p_fisc2 = doc.add_paragraph()
        p_fisc2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_fisc2.paragraph_format.space_after = Pt(6)
        p_fisc2.paragraph_format.line_spacing = 1.15
        
        run_fisc2 = p_fisc2.add_run(
            "Esses achados foram avaliados tomando por base as orientações do PDCL, em especial, o Subitem 4.2.2.1.3 - Parâmetros Mínimos Exigidos, "
            "visualizando que \"os pavimentos deverão ser analisados quanto às suas condições de superfície, conforto, deformabilidade, vida remanescente e segurança”, "
            "e ainda que os “parâmetros de aceitabilidade do pavimento para essas condições que deverão ser totalmente atendidas durante o período de CONCESSÃO”."
        )
        run_fisc2.font.name = 'Aptos'
        run_fisc2.font.size = Pt(11)
