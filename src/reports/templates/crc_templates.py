# -*- coding: utf-8 -*-
"""
Templates, textos regulatórios e configurações estáticas do Relatório CRC (Rota dos Coqueiros - Paiva).
Contrato de Concessão Patrocinada CGPE – 001/2006 (PE-024).
"""

CRC_KEY = "CRC"
CRC_DISPLAY_NAME = "CRC"
CRC_DEFAULT_CONTRATO = "CGPE – 001/2006"

# Capa / Cabeçalho
CRC_CAPA_ORGAO_CONCEDENTE = "GOVERNO DO ESTADO DE PERNAMBUCO"
CRC_CAPA_SECRETARIA = "SECRETARIA DE PLANEJAMENTO, GESTÃO E DESENVOLVIMENTO REGIONAL - SEPLAG"
CRC_CAPA_TITULO = "RELATÓRIO DE FISCALIZAÇÃO TÉCNICO-OPERACIONAL"
CRC_CAPA_CTR_NUMBER_TEMPLATE = "RELATÓRIO DE FISCALIZAÇÃO TÉCNICO-OPERACIONAL CTR Nº {mes_ano}"
CRC_CAPA_PRESTADOR_LABEL = "PRESTADOR DE SERVIÇO: CONCESSIONÁRIA ROTA DOS COQUEIROS (CRC)"
CRC_CAPA_CONTRATO_LABEL = "CONTRATO DE CONCESSÃO PATROCINADA"
CRC_CAPA_REGULADOR_LABEL = "AGÊNCIA DE REGULAÇÃO DOS SERVIÇOS PÚBLICOS DELEGADOS DO ESTADO DE PERNAMBUCO - ARPE"
CRC_ANALYST_TITLE = "Analista de Regulação"

CRC_CAPA_TITULOS = [
    "FISCALIZAÇÃO TÉCNICO-OPERACIONAL NO SISTEMA VIÁRIO DO PAIVA (PE – 024)",
    "PRESTADOR DE SERVIÇO: CONCESSIONÁRIA ROTA DOS COQUEIROS (CRC)"
]

CRC_ABBREVIATIONS = [
    ("ABNT", "Associação Brasileira de Normas Técnicas"),
    ("ARPE", "Agência de Regulação de Pernambuco"),
    ("SEPPE", "Secretaria Executiva de Parcerias e Projetos Estratégicos"),
    ("NC", "Não Conformidade"),
    ("CRC", "Concessionária Rota dos Coqueiros S. A."),
    ("PER", "Programa de Exploração da Rodovia, anexo ao Contrato de Concessão Patrocinada CGPE-001/2006"),
    ("VI", "Verificador Independente, atualmente, o Consórcio formado pelas empresas Maciel Consultores S/S Ltda e Estratégica Serviços de Engenharia Consultiva Ltda")
]

CRC_BASE_SUMARIO_LINHAS = [
    "1.\tINTRODUÇÃO\t4",
    "2.\tOBJETIVO\t4",
    "3.\tINFORMAÇÕES GERAIS\t4",
    "4.\tMETODOLOGIA\t5",
    "5.\tFISCALIZAÇÃO\t7",
    "6.\tCONCLUSÕES\t11"
]


def get_crc_intro_paragraphs(ano: str) -> list:
    """Gera parágrafos formatados da seção 1. Introdução para o CRC."""
    return [
        [(
            f"A Coordenadoria de Transportes e Rodovias da ARPE, em cumprimento ao cronograma de fiscalização de {ano}, "
            "realizou fiscalização na Concessão Patrocinada da Ponte de Acesso e Sistema Viário da Praia do Paiva, "
            "sob responsabilidade da Concessionária Rota dos Coqueiros (CRC). A ação foi comunicada à concessionária "
            "por meio do Ofício ARPE/DTO nº 145/2026, de 26/05/2026 (Doc. SEI nº xxxxxxxx-xxx), e à Secretaria Executiva "
            "de Parcerias e Projetos Estratégicos (SEPPE) por meio do Ofício ARPE/DTO nº 146/2026, de 26/05/2026 (Doc. SEI nº xxxxxxxx-xxx).",
            False, False, None
        )],
        [(
            "As ações de fiscalização registradas neste Relatório se referem à Rodovia Estadual PE-024, trecho Barra de Jangada – Itapuama, "
            "medindo 6,5 Km de extensão, compreendendo duas praças de pedágio, pela Ponte sobre o Rio Jaboatão e a via principal "
            "do Destino de Turismo e Lazer Praia do Paiva.",
            False, False, None
        )],
        [(
            "Este relatório apresenta as observações realizadas pela equipe da Coordenadoria de Transportes e Rodovias da ARPE, "
            "sob a perspectiva técnico-operacional, com o objetivo de verificar as condições de operação, conservação, manutenção "
            "e segurança del trecho rodoviário concedido, bem como o cumprimento da legislação aplicável e a eficiência dos serviços prestados.",
            False, False, None
        )],
        [(
            "As fiscalizações realizadas pela ARPE possuem, prioritariamente, caráter orientativo e corretivo, visando contribuir "
            "para o aperfeiçoamento dos procedimentos e para a correção de não conformidades identificadas na infraestrutura "
            "disponibilizada e nos serviços concedidos pelo Estado.",
            False, False, None
        )]
    ]


CRC_OBJECTIVE_PARAGRAPHS = [
    [(
        "A fiscalização direta e periódica do Sistema Viário do Paiva, concedido à CRC, tem por objetivo verificar as condições "
        "de operação, manutenção, segurança viária e níveis de serviço, bem como identificar não conformidades, subsidiar a adoção "
        "de medidas corretivas e assegurar o cumprimento das disposições contratuais, regulamentares e normativas aplicáveis, "
        "visando à preservação da segurança, da qualidade dos serviços e da adequada prestação do serviço público aos usuários.",
        False, False, None
    )],
    [(
        "Nesse contexto, a ação fiscalizatória da ARPE avalia o grau de conformidade da infraestrutura e dos serviços prestados "
        "em relação ao Contrato de Concessão, à legislação vigente e às normas aplicáveis, podendo determinar ou recomendar medidas "
        "corretivas destinadas ao aprimoramento contínuo da qualidade dos serviços.",
        False, False, None
    )]
]


def get_crc_general_info_rows(responsaveis_formatted: str, periodo_val: str) -> list:
    """Retorna os dados cadastrais das entidades da Seção 3. Informações Gerais do CRC."""
    return [
        ("3.1 DO PODER CONCEDENTE", "", True, False),
        ("Titular:", "Conselho do Programa de Parcerias Estratégicas de Pernambuco– CPPPE", False, False),
        ("Endereço:", "Rua da Moeda, nº 46, Recife-PE", False, False),
        ("Responsável:", "MARCELO BRUTO DA COSTA CORREIA", False, True),

        ("3.2 DO VERIFICADOR INDEPENDENTE", "", True, False),
        ("Verificador Independente:", "Consórcio Estratégica e Grupo Maciel", False, False),
        ("Endereço:", "Rua Irene Ramos Gomes de Mattos, Nº 176, Pina, Recife/PE CEP: 51011-530", False, False),
        ("Responsável:", "José Theodozio Netto", False, True),

        ("3.3 DO REGULADO", "", True, False),
        ("Regulado:", "Concessionária Rota dos Coqueiros (CRC)", False, False),
        ("Responsável:", "RAFAELA ELAINE DA COSTA LIMA ARAÚJO", False, True),
        ("Endereço:", "Rua Marmelo, s/nº - Praça de Pedágio – Barra de Jangada Jaboatão dos Guararapes – PE CEP: 54.495-760", False, False),
        ("Representantes por acompanhar:", "Larissa Almeida e Everton Albuquerque", False, False),

        ("3.4 DO FISCALIZADOR (ARPE)", "", True, False),
        ("Regulador:", "Agência de Regulação de Pernambuco (ARPE)", False, False),
        ("Diretor Presidente:", "CARLOS PORTO FILHO", False, True),
        ("Endereço:", "Avenida Conselheiro Rosa e Silva, 975, Aflitos, Recife/PE, CEP: 52.050-020. Estacionamento: Rua do Futuro, 150, Aflitos, Recife/PE.", False, False),

        ("Responsáveis pela fiscalização:", responsaveis_formatted, False, False),
        ("Período da Fiscalização:", periodo_val, False, False),
        ("Tipo de Fiscalização:", "Direta e periódica.", False, False)
    ]


def get_crc_methodology_paragraphs(data_extenso: str) -> list:
    """Gera parágrafos da Seção 4. Metodologia para o CRC."""
    return [
        [(
            f"A Coordenadoria de Transporte e Rodovias da ARPE realizou fiscalização direta e periódica no Sistema Viário do Paiva "
            f"em {data_extenso}, seguindo metodologia estruturada em três etapas: Preparação e Planejamento, Execução da Fiscalização "
            "e Monitoramento e Avaliação.",
            False, False, None
        )],
        [
            ("Preparação e Planejamento", True, False, None),
            (
                " - compreende a organização e estruturação das atividades preliminares à execução da fiscalização, destacando-se "
                "a elaboração e o envio de avisos de fiscalização à Concessionária e demais atividades de suporte à fiscalização, "
                "bem como a análise de fiscalizações anteriores com a identificação de eventuais Não Conformidades pendentes.",
                False, False, None
            )
        ],
        [
            ("Execução da Fiscalização", True, False, None),
            (
                " - as possíveis Não Conformidades levantadas em campo são analisadas de acordo com os critérios elencados no PER "
                "(Contrato de Concessão). A execução da fiscalização é pautada por um arcabouço de normas e diretrizes, possibilitando "
                "que todas as etapas sejam desenvolvidas de maneira eficiente e em conformidade aos padrões estabelecidos, destacando-se:",
                False, False, None
            )
        ]
    ]


CRC_REFERENCES_BULLETS = [
    ("Lei Estadual nº. 12.524, de 30 de dezembro de 2003, regulamentada pelo Decreto Estadual nº. 30.200, de 09 de fevereiro de 2007, que altera e consolida as disposições da Lei nº. 12.126, de 12 de dezembro de 2001, que cria a Agência de Regulação dos Serviços Públicos Delegados do Estado de Pernambuco - ARPE, e dá outras providências;", False, True),
    ("", False, False),
    ("Contrato de Concessão Patrocinada CGPE – 001/2006, de 28 de dezembro de 2006, e Termos Aditivos, para a exploração da ponte de acesso e sistema viário do destino de turismo e lazer Praia do Paiva, em conformidade com a Lei Federal nº 11.079/2004 e alterações; e a Lei Estadual nº 12.765/2005 e alterações.", False, True),
    ("", False, False),
    ("Resolução ARPE nº 083, de 30 de julho de 2013, que dispõe sobre os procedimentos de fiscalização, autuação e aplicação de penalidades aos prestadores de serviços públicos delegados no Estado de Pernambuco fiscalizados pela ARPE mediante delegação.", False, True),
    ("", False, False),
    ("Norma DNIT 005/2003 – que define os termos técnicos empregados em defeitos que ocorrem nos pavimentos flexíveis e semirrígidos e serve para padronizar a linguagem adotada na elaboração das normas, manuais, projetos e textos relativos aos pavimentos flexíveis e semirrígidos.", False, True)
]

CRC_REFERENCES_LEFT_INDENT_PT = 53.4

CRC_POST_METHODOLOGY_PARAGRAPHS = [
    [("Registra-se que as Não conformidades (NC) são codificadas de acordo com os seguintes níveis de informação, separados por “.” (ponto):", False, False, None)]
]

CRC_LEVELS_DATA = {
    "niveis": [
        "Nível 1 - três dígitos, caracterizando a concessionária, nesse caso \"CRC\";",
        "Nível 2 - composto por cinco dígitos, os dois primeiros indicam a subdivisão utilizada na rodovia, neste caso, Segmento Homogêneo (SH) e os três últimos dígitos identificam a subdivisão utilizada no Contrato (nesse caso de 001 a 015);",
        "Nível 3 – composto por nove dígitos os quatro primeiros e os quatro últimos delimitam a localização das NC em escala de 0,01Km e o dígito intermediário informa se a NC é pontual \"+\" ou distribuída \"-\";",
        "Nível 4 – informa o ano da constatação da NC com quatro dígitos, antecedido de “/”; e",
        "Nível 5 - contém o sequencial numérico da NC no ano, expresso em três dígitos."
    ],
    "ex_str": "CRC.SH015.0646+0648/2026.001",
    "ex_desc": "Indica que esta Não Conformidade foi apontada para a CRC, no Segmento Homogêneo 15, concentrado na praça de pedágio do km 6,46 ao km 6,48, sendo a primeira NC registrada pela ARPE em 2026."
}


def get_crc_quadro_intro_paragraphs(data_extenso: str) -> list:
    """Gera o parágrafo de introdução dos Quadros do CRC."""
    return [
        [(f"As NC identificadas, em {data_extenso}, pela equipe de fiscalização da ARPE estão detalhadas no Quadro 1 a seguir.", False, False, None)]
    ]


CRC_NC_TABLE_HEADERS = [
    "IDENTIFICAÇÃO",
    "DESCRIÇÃO DA EVIDÊNCIA",
    "REGISTRO FOTOGRÁFICO",
    "FUNDAMENTO DA NC (PER)",
    "DETERMINAÇÃO"
]

CRC_PEDESTRIAN_SAFETY_NOTE = (
    "É importante destacar que as observações apontadas se referem à segurança dos pedestres na rodovia, "
    "visando evitar a ocorrência de acidentes."
)


def get_crc_conclusions_paragraphs(extenso_com_parenteses: str) -> list:
    """Gera parágrafos da Seção 6. Conclusões para o CRC."""
    return [
        [(
            f"Em decorrência das ações de fiscalização realizadas pela ARPE foram identificadas {extenso_com_parenteses} "
            "novas Não Conformidades na fiscalização do trecho rodoviário sob a responsabilidade da Concessionária Rota dos Coqueiros.",
            False, False, None
        )],
        [(
            "Por fim, solicita-se o encaminhamento deste Relatório de Fiscalização à Concessionária Rota dos Coqueiros, "
            "para adoção das providências necessárias à regularização das não conformidades apontadas por esta Agência Reguladora, "
            "bem como dar conhecimento à SEPPE, gestora do Contrato de Concessão.",
            False, False, None
        )]
    ]
