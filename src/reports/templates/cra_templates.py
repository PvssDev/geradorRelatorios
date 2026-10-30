# -*- coding: utf-8 -*-
"""
Templates, textos regulatórios e configurações estáticas do Relatório CRA (Rota do Atlântico).
Contrato de Concessão CT. nº 043/2011 (Complexo Viário e Logístico de Suape – Expressway).
"""

CRA_KEY = "CRA"
CRA_DISPLAY_NAME = "CRA"
CRA_DEFAULT_CONTRATO = "CT. nº 043/2011"

# Capa / Cabeçalho
CRA_CAPA_ORGAO_CONCEDENTE = "GOVERNO DO ESTADO DE PERNAMBUCO"
CRA_CAPA_SECRETARIA = "SECRETARIA DE MOBILIDADE E INFRAESTRUTURA - SEMOBI"
CRA_CAPA_TITULO = "RELATÓRIO DE FISCALIZAÇÃO PROCESSO ADMINISTRATIVO"
CRA_CAPA_CTR_NUMBER_TEMPLATE = "RELATÓRIO DE FISCALIZAÇÃO PROCESSO ADMINISTRATIVO CTR Nº {mes_ano}"
CRA_CAPA_PRESTADOR_LABEL = "PRESTADOR DE SERVIÇO: CONCESSIONÁRIA ROTA DO ATLÂNTICO (CRA)"
CRA_CAPA_CONTRATO_LABEL = "CONTRATO DE CONCESSÃO"
CRA_CAPA_REGULADOR_LABEL = "AGÊNCIA DE REGULAÇÃO DOS SERVIÇOS PÚBLICOS DELEGADOS DO ESTADO DE PERNAMBUCO - ARPE"
CRA_ANALYST_TITLE = "Analista de Regulação"

CRA_CAPA_TITULOS = [
    "FISCALIZAÇÃO DO COMPLEXO VIÁRIO E LOGÍSTICO DE SUAPE – EXPRESSWAY",
    "PRESTADOR DE SERVIÇO: CONCESSIONÁRIA ROTA DO ATLÂNTICO (CRA)",
    "CONTRATO DE CONCESSÃO CT. Nº 043/2011"
]

CRA_ABBREVIATIONS = [
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

CRA_BASE_SUMARIO_LINHAS = [
    "1.\tINTRODUÇÃO\t4",
    "2.\tOBJETIVO\t4",
    "3.\tINFORMAÇÕES GERAIS\t4",
    "4.\tMETODOLOGIA\t5",
    "5.\tFISCALIZAÇÃO\t7",
    "6.\tDETERMINAÇÕES GERAIS\t11",
    "7.\tRECOMENDAÇÕES\t11",
    "8.\tCONCLUSÕES\t11"
]


def get_cra_intro_paragraphs(ano: str, data_extenso: str) -> list:
    """Gera parágrafos formatados da seção 1. Introdução."""
    return [
        [(
            f"A Coordenadoria de Transporte e Rodovias da Arpe implementou o cronograma de fiscalização para {ano} "
            "do Complexo Viário e Logístico de SUAPE, sob a responsabilidade da Concessionária Rota do Atlântico (CRA), "
            "visualizando a necessidade de serem reservados dois dias consecutivos, para melhor estruturar suas ações "
            "de fiscalização técnico-operacionais da Rodovia.",
            False, False, None
        )],
        [(
            "Ainda com a visão de implantar melhorias na contribuição da Agência sobre os trabalhos desenvolvidos na rodovia, "
            "foi introduzida uma visita técnica prévia, realizada uma semana antes do período de fiscalização, com o objetivo "
            "de elaborar um roteiro que é encaminhado para a CRA e SUAPE contendo os trechos mapeados com possíveis Não Conformidades, "
            "tornando os levantamentos fotográficos mais ágeis e a fiscalização efetiva.",
            False, False, None
        )],
        [(
            "Posteriormente, as possíveis Não Conformidades levantadas in campo são analisadas de acordo com os critérios elencados "
            "no PDCL anexo ao Contrato de Concessão, em conjunto com o último Relatório Anual elaborado pelo Verificador Independente.",
            False, False, None
        )],
        [(
            "Destaca-se preliminarmente que as ações de fiscalização registradas neste Relatório foram concentradas na Rodovia PE-009, "
            "do Entroncamento BR-101 ao Entroncamento PE-038, que abrange os subtrechos concedidos, especificamente, o Contorno do Cabo, "
            "TDR Norte, TDR Sul e a Ligação Rótula Curva do Boi a Nossa Senhora do Ó; e Rodovia Estadual VPE-034.",
            False, False, None
        )],
        [
            (f"É importante observar que foram realizadas ações de fiscalização, no dia {data_extenso}, conforme comunicado enviado à SUAPE por meio do Ofício Arpe/DTO nº ", False, False, None),
            ("xxx (Doc. SEI nº xxxxxxxx-xxx)", False, False, (255, 0, 0)),
            (".", False, False, None)
        ],
        [(
            "Destaca-se que as fiscalizações realizadas pela Arpe são tratadas com caráter educativo, preferencialmente, e contributivo "
            "para correção de procedimentos e solução de Não Conformidades evidenciados por defeitos e/ou problemas na infraestrutura "
            "disponibilizada e respectivos serviços concedidos pelo Estado.",
            False, False, None
        )]
    ]


CRA_OBJECTIVE_PARAGRAPHS = [
    [(
        "A fiscalização direta e periódica do complexo viário e logístico de Suape – Expressway concedido à CRA, "
        "tem por objetivo verificar as condições de operação, manutenção, segurança viária e níveis de serviço, bem "
        "como identificar não conformidades, subsidiar medidas corretivas e assegurar a observância das disposições "
        "contratuais, regulamentares e normativas aplicáveis, preservando a segurança, a qualidade do serviço, e a "
        "adequada prestação do serviço público aos usuários. Dessa forma a ação de fiscalização da Arpe verifica o grau "
        "de conformidade dessas instalações com o Contrato de Concessão, bem como com a legislação e normas vigentes "
        "de modo a determinar/ou recomendar medidas corretivas, com foco na qualidade dos serviços prestados.",
        False, False, None
    )]
]


def get_cra_general_info_rows(responsaveis_formatted: str, periodo_val: str) -> list:
    """Retorna os dados cadastrais das entidades da Seção 3. Informações Gerais."""
    return [
        ("3.1 DO TITULAR E REGULADOR", "", True, False),
        ("Titular:", "SUAPE – Complexo Industrial Portuário Governador Eraldo Gueiros", False, False),
        ("Endereço:", "Engenho Massangana – Km 10 – Rodovia PE – 60 Ipojuca/PE CEP: 55.590-000", False, False),
        ("Responsável:", "JOSÉ CONSTANTINO DA SILVA FILHO", False, True),
        ("Representantes por acompanhar:", "Viviane Alves Walzertudes", False, False),

        ("3.2 DO VERIFICADOR INDEPENDENTE", "", True, False),
        ("Verificador Independente:", "Consórcio das Empresas TPF/ECR", False, False),
        ("Endereço:", "Rua Irene Ramos Gomes de Mattos, Nº 176, Pina, Recife/PE CEP: 51011-530", False, False),
        ("Responsável:", "RICARDO MEDEIROS PEREIRA DE CARVALHO", False, True),
        ("Representantes por acompanhar:", "Sónya Albuquerque; Ricardo Henrique Ferraz de Farias; Lauro Ricardo Torres Galindo e Maynara Milena Silva de Lima", False, False),

        ("3.3 DO REGULADO", "", True, False),
        ("Regulado:", "CRA - Concessionária Rota do Atlântico", False, False),
        ("Responsável:", "RAFAELA ELAINE DA COSTA LIMA ARAÚJO", False, True),
        ("Endereço:", "Rodovia PE-009, Km 38,5(TDR Norte, 2074) – Distrito Industrial Suape, Cabo de Santo Agostinho/PE – CEP: 54.590-000", False, False),
        ("Representantes por acompanhar:", "Vanessa Monteiro e OuvidoraXXXCRA", False, False),

        ("3.4 DO FISCALIZADOR (CONVÊNIO SUAPE/ARPE Nº 003/2021)", "", True, False),
        ("Regulador:", "Agência de Regulação de Pernambuco (Arpe)", False, False),
        ("Diretor Presidente:", "CARLOS PORTO FILHO", False, True),
        ("Endereço:", "Avenida Conselheiro Rosa e Silva, 975, Aflitos, Recife/PE, CEP: 52.050-020.\nEstacionamento: Rua do Futuro, 150, Aflitos, Recife/PE.", False, False),

        ("Responsáveis pela fiscalização:", responsaveis_formatted, False, False),
        ("Período da Fiscalização:", periodo_val, False, False),
        ("Tipo de Fiscalização:", "Direta e periódica.", False, False)
    ]


def get_cra_methodology_paragraphs(ano: str) -> list:
    """Gera parágrafos da Seção 4. Metodologia."""
    return [
        [(
            f"A Coordenadoria de Transporte e Rodovias da Arpe implementou o cronograma de fiscalização para {ano} do Complexo Viário "
            "e Logístico de SUAPE reservando dois dias consecutivos, para melhor estruturar suas ações de fiscalização técnico-operacionais "
            "no Complexo Rodoviário, após uma visita técnica prévia, realizada antes do período de fiscalização, com o objetivo de elaborar "
            "um roteiro que é encaminhado para a CRA e SUAPE contendo os trechos mapeados com possíveis Não Conformidades, tornando os "
            "levantamentos fotográficos mais ágeis e a fiscalização efetiva.",
            False, False, None
        )],
        [(
            "Posteriormente, as possíveis Não Conformidades levantadas em campo são analisadas de acordo com os critérios elencados no PDCL "
            "(Anexo IV do Contrato de Concessão), em conjunto com o último Relatório Anual elaborado pelo Verificador Independente.",
            False, False, None
        )],
        [(
            "Assim, a fiscalização direta e periódica realizada pela Coordenadoria de Transportes e Rodovias da Arpe está submetida a uma "
            "metodologia organizada em três etapas: Preparação e Planejamento, Execução da Fiscalização e Monitoramento e Avaliação.",
            False, False, None
        )],
        [(
            "Preparação e Planejamento - compreende a organização e estruturação das atividades preliminares à execução da fiscalização, "
            "destacando-se a elaboração e o envio de avisos de fiscalização à Concessionária e demais atividades de suporte à fiscalização, "
            "bem como a análise de fiscalizações anteriores com a identificação de eventuais Não Conformidades pendentes.",
            False, False, None
        )],
        [(
            "Execução da Fiscalização - a execução da fiscalização é pautada por um arcabouço de normas e diretrizes, possibilitando que "
            "todas as etapas sejam desenvolvidas de maneira eficiente e em conformidade aos padrões estabelecidos, destacando-se:",
            False, False, None
        )]
    ]


CRA_REFERENCES_BULLETS = [
    ("Lei Estadual nº. 12.524, de 30 de dezembro de 2003, regulamentada pelo Decreto Estadual nº. 30.200, de 09 de fevereiro de 2007, que altera e consolida as disposições da Lei nº. 12.126, de 12 de dezembro de 2001, que cria a Agência de Regulação dos Serviços Públicos Delegados do Estado de Pernambuco - ARPE, e dá outras providências;", False, True),
    ("Art. 3º Compete à ARPE a regulação de todos os serviços públicos delegados pelo Estado de Pernambuco, ou por ele diretamente prestados, embora sujeitos à delegação, quer de sua competência ou a ele delegados por outros entes federados, em decorrência de norma legal ou regulamentar, disposição convenial ou contratual.", True, False),
    ("§ 1º A atividade reguladora da ARPE deverá ser exercida, em especial, nas seguintes áreas:", True, False),
    ("[...]", True, False),
    ("III - rodovias;", True, False),
    ("[...]", True, False),
    ("Art. 4º Compete ainda à ARPE:", True, False),
    ("[...]", True, False),
    ("X - Fiscalizar diretamente ou mediante convênio com o Estado de Pernambuco, através de seus órgãos ou entidades vinculadas, com sua supervisão, os aspects técnico, econômico, contábil, financeiro, operacional e jurídico dos serviços públicos delegados, valendo-se inclusive, de indicadores e procedimentos amostrais.", True, False),
    ("", False, False),
    ("Contrato de Concessão CT. nº 043/2011, de 18 de julho de 2011, para a delegação da exploração do Complexo Viário e Logístico de SUAPE – EXPRESSWAY, conforme detalhado no Anexo IV do Edital (PDCL) e regidos pela Constituição Federal; pela Lei Federal Nº 8.987/95; Lei Federal Nº 9.074/95; Lei Federal 8.666/93 e Lei Estadual Nº 14.233/2010.", False, True),
    ("", False, False),
    ("Convênio de Cooperação Técnica n° 003/2021 de 22 de setembro 2021, firmado entre o Complexo Industrial Portuário Governador Eraldo Gueiros – SUAPE e a Agência de Regulação de Pernambuco – ARPE, e Renovação do Termo Aditivo que prorroga o prazo de vigência e execução contratual até 22 de setembro de 2026.", False, True),
    ("", False, False),
    ("Norma DNIT 005/2003 – que define os termos técnicos empregados in defeitos que ocorrem nos pavimentos flexíveis e semirrígidos e serve para padronizar a linguagem adotada na elaboração das normas, manuais, projetos e textos relativos aos pavimentos flexíveis e semirrígidos.", False, True),
    ("", False, False),
    ("Relatórios elaborados pelo Verificador Independente.", False, True)
]

CRA_POST_METHODOLOGY_PARAGRAPHS = [
    [("Registra-se que as Não conformidades (NC) são codificadas de acordo com os seguintes níveis de informação, separados por “.” (ponto):", False, False, None)]
]

CRA_LEVELS_DATA = {
    "niveis": [
        "Nível 1 - três dígitos, caracterizando a concessionária: CRA ou CRC.",
        "Nível 2 - composto por cinco dígitos: os dois primeiros representam as subdivisões utilizadas na rodovia concedida, por exemplo, Trecho (TR); Subtrecho (ST); Segmento Homogêneo (SH) e os três últimos dígitos identificam a subdivisão utilizada em cada contrato.",
        "Nível 3 – composto por nove dígitos os quatro primeiros e os quatro últimos delimitam a localização das NC em escala de 0,01Km e o dígito intermediário informa se a NC é pontual \"+\" ou distribuída.",
        "Nível 4 – informa o ano da constatação da NC com quatro dígitos, antecedido de “/”.",
        "Nível 5 - contendo o sequencial numérico da NC no ano, expresso em três dígitos."
    ],
    "ex_str": "CRA.ST601.2794-2834/2025.013",
    "ex_desc": "Indica que esta Não Conformidade foi apontada para a CRA, no subtrecho 6.01, distribuída do km 27,94 ao km 28,34, sendo a 13ª NC registrada pela Arpe em 2025"
}

CRA_QUADRO_INTRO_PARAGRAPHS = [
    [(
        "Os trechos com Não Conformidades registradas no Quadro 1, a seguir, associadas aos respectivos subtrechos, "
        "foram avaliadas pelos valores do Índice de Gravidade Global (IGG) que ultrapassaram o limite máximo previsto ≥ 30, "
        "como também os valores do Índice Irregularidade Longitudinal (IRI) que ultrapassaram o limite máximo previsto ≥ 2,7 m/km "
        "constantes do Relatório Anual 01 de novembro/2025 elaborado pelo Verificador Independente.",
        False, False, None
    )],
    [],
    [(
        "A partir das vistorias de campo, e das avaliações das Não Conformidades registradas pelo Verificador Independente, "
        "foram consolidadas as informações no Quadro 2, a seguir, as Não Conformidades e Determinações/Recomendações expedidas pela Arpe.",
        False, False, None
    )]
]

CRA_DETERMINATIONS_PARAGRAPHS = [
    [("Considerando os dispositivos contratuais pertinentes e visando garantir a qualidade dos serviços prestados, determina-se que a CRA tome as seguintes medidas através de um plano de ação:", False, False, None)],
    [
        ("Medidas de Manutenção / Conservação,", True, False, None),
        (" detalhando cronograma com trechos a executar de forma que permita à Arpe uma programação mais efetiva do monitoramento de suas soluções a execução de cada subtrecho, conforme o modelo encaminhado para {ano_anterior} (Cronograma de Conserva Especial do Pavimento CRA {ano_anterior}).", False, False, None)
    ],
    [
        ("Medidas imediatas", True, False, None),
        (" resolutividade das NC de Sinalização, nos prazos estabelecidos no subitem 4.1.3.3.2.4. Tachas e Tachões Refletivos do PDCL, conforme disposto no Quadro 1, na coluna denominada Determinações.", False, False, None)
    ]
]

CRA_RECOMMENDATIONS_PARAGRAPHS = [
    [("Considerando as disposições do Contrato de Concessão, em especial, o Anexo IV - PDCL, Outras Sinalizações, dados do Relatório Anual 01 de novembro/2025 elaborado VI, e outras legislação aplicável, devem ser observadas pela CRA as seguintes recomendações:", False, False, None)],
    [("Levantar a necessidade de reposição da SINALIZAÇÃO por tachas e tachões em todo o complexo viário Express Way,  em especial a retirada das tachar anteriores danificadas que podem causar risco a segurança dos usuários. O vi verificou deficiências em todos os trechos.", False, False, None)]
]


def get_cra_conclusions_paragraphs(total_ncs: int, extenso_ncs: str) -> list:
    """Gera parágrafos da Seção 8. Conclusões."""
    return [
        [(
            f"Tendo em vista as ações de fiscalização realizadas pela Arpe foram constatadas {extenso_ncs} ({total_ncs}) "
            "pontos ou trechos fiscalizados que apresentaram Não Conformidades distribuídas majoritariamente na PE 009, "
            "estas foram analisadas e caracterizadas a partir dos indicadores do Grupo Condição de Superfície definidos "
            "no Contrato de Concessão CT. nº 043/2011.",
            False, False, None
        )],
        [(
            "Assim considerando a Programação de Conserva Especial do Pavimento - CRA {ano}, solicita-se a inclusão destas "
            "não conformidades no cronograma detalhado de Conserva Especial do Pavimento que permita à Arpe uma realização "
            "mais efetiva dos monitoramentos ao longo de {ano}.",
            False, False, None
        )],
        [(
            "Recomenda-se, por fim, o encaminhamento deste Relatório de Fiscalização para que Suape, na qualidade de Gestor "
            "do Contrato e Regulador desse Sistema Viário, realize as providências cabíveis junto à Concessionária Rota do "
            "Atlântico com o objetivo de garantir a regularização das Não Conformidades pendentes apontadas por esta Agência de Regulação.",
            False, False, None
        )]
    ]
