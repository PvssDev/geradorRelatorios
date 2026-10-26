# -*- coding: utf-8 -*-
"""
Templates, textos regulatórios e configurações estáticas do Relatório SOCICAM (Terminais Rodoviários).
Contrato de Concessão de Serviço Público Nº 1.041.080/08 (TIP, Caruaru, Garanhuns, Petrolina).
"""

from docx.shared import Inches

SOCICAM_KEY = "SOCICAM"
SOCICAM_DISPLAY_NAME = "SOCICAM"
SOCICAM_DEFAULT_CONTRATO = "CT. nº 1.041.080/08"

# Capa / Cabeçalho
SOCICAM_CAPA_ORGAO_CONCEDENTE = "GOVERNO DO ESTADO DE PERNAMBUCO"
SOCICAM_CAPA_SECRETARIA = "SECRETARIA DE MOBILIDADE E INFRAESTRUTURA - SEMOBI"
SOCICAM_CAPA_TITULO = "RELATÓRIO DE FISCALIZAÇÃO TÉCNICO-OPERACIONAL"
SOCICAM_CAPA_CTR_NUMBER_TEMPLATE = "RELATÓRIO DE FISCALIZAÇÃO TÉCNICO-OPERACIONAL CTR Nº {mes_ano}"
SOCICAM_CAPA_PRESTADOR_LABEL = "PRESTADOR DE SERVIÇO: SOCICAM - ADMINISTRAÇÃO, PROJETOS E REPRESENTAÇÕES LTDA"
SOCICAM_CAPA_CONTRATO_LABEL = "CONTRATO DE CONCESSÃO DE SERVIÇO PÚBLICO"
SOCICAM_CAPA_REGULADOR_LABEL = "AGÊNCIA DE REGULAÇÃO DOS SERVIÇOS PÚBLICOS DELEGADOS DO ESTADO DE PERNAMBUCO - ARPE"
SOCICAM_ANALYST_TITLE = "Especialista em Regulação"


def get_socicam_capa_titulos(local_val: str) -> list:
    """Gera títulos da capa para o relatório SOCICAM baseado no terminal vistoriado."""
    l_upper = str(local_val).upper()
    if "TERMINAL" not in l_upper and "FISCALIZAÇÃO" not in l_upper:
        local_val_fmt = (
            f"TERMINAL RODOVIÁRIO DE PASSAGEIROS DO RECIFE ({l_upper})"
            if "RECIFE" in l_upper or "TIP" in l_upper
            else f"TERMINAL RODOVIÁRIO DE PASSAGEIROS ({l_upper})"
        )
    else:
        local_val_fmt = l_upper

    return [
        f"FISCALIZAÇÃO NO {local_val_fmt}",
        "PRESTADOR DE SERVIÇO: SOCICAM - ADMINISTRAÇÃO, PROJETOS E REPRESENTAÇÕES LTDA"
    ]


SOCICAM_ABBREVIATIONS = [
    ("ABNT", "Associação Brasileira de Normas Técnicas"),
    ("ARPE", "Agência de Regulação de Pernambuco"),
    ("EPTI", "Empresa Pernambucana de Transporte Coletivo Intermunicipal"),
    ("NC", "Não Conformidade"),
    ("PCD", "Pessoa com Deficiência"),
    ("TIP", "Terminal Rodoviário de Passageiros do Recife")
]

SOCICAM_BASE_SUMARIO_LINHAS = [
    "1.\tINTRODUÇÃO\t4",
    "2.\tOBJETIVO\t4",
    "3.\tMETODOLOGIA\t5",
    "4.\tFISCALIZAÇÃO\t5",
    "5.\tDETERMINAÇÕES GERAIS\t6",
    "6.\tRECOMENDAÇÕES\t6",
    "7.\tCONCLUSÕES\t7"
]


def get_socicam_intro_paragraphs(terminal_nome: str) -> list:
    """Gera parágrafos formatados da seção 1. Introdução para o SOCICAM."""
    return [
        [
            ("A Coordenadoria de Transportes e Rodovias da Arpe realizou vistorias no ", False, False, None),
            (terminal_nome, True, False, None),
            (
                " com o objetivo de verificar as condições operacionais, de conservação, de manutenção e de segurança e da qualidade "
                "do serviço prestado no referido terminal, conforme Contrato de Concessão de Serviço Público No 1.041.080/08, firmado "
                "entre o Governo do Estado, atualmente representado pela Empresa Pernambucana de Transportes Intermunicipal (EPTI) e a "
                "SOCICAM - Administração, Projetos e Representações Ltda (SOCICAM) visando a operação, manutenção e administração de "
                "terminais rodoviários no Estado de Pernambuco, com execução de obras de reforma e construção, incluindo, ainda, a "
                "cessão de uso de espaços para a exploração comercial através de locação e publicidade.",
                False, False, None
            )
        ]
    ]


def get_socicam_objective_paragraphs(terminal_nome: str) -> list:
    """Gera parágrafos formatados da seção 2. Objetivo para o SOCICAM."""
    return [
        [
            (
                "A fiscalização direta e periódica dos Terminais Rodoviários de Passageiros concedidos à SOCICAM, tem por objetivo "
                "verificar as condições de conservação, limpeza e higiene das áreas de embarque e desembarque, dos sanitários, as "
                "condições do pavimento das vias de circulação interna, a infraestrutura oferecida, a segurança e o atendimento ao "
                "usuário, bem como toda estrutura para funcionamento desses terminais. Dessa forma, a ação de fiscalização no ",
                False, False, None
            ),
            (terminal_nome, True, False, None),
            (
                ", realizada pela ARPE verificou o grau de conformidade dessas instalações com o Contrato de Concessão, bem como com a "
                "legislação e normas vigentes de modo a determinar e/ou recomendar medidas corretivas, com foco na qualidade dos "
                "serviços prestados.",
                False, False, None
            )
        ]
    ]


def get_socicam_general_info_rows(responsaveis_formatted: str, periodo_val: str) -> list:
    """Retorna os dados cadastrais das entidades da Seção 3. Informações Gerais do SOCICAM."""
    return [
        ("3.1 DO TITULAR", "", True, False),
        ("Titular:", "Empresa Pernambucana de Transportes Intermunicipal (EPTI)", False, False),
        ("Endereço:", "Av. Caxangá, 2.200 Cordeiro Recife/PE CEP: 50.711-000", False, False),
        ("Responsável:", "THIAGO EDGLES SOBRAL DE SOUZA", False, True),

        ("3.2 DO REGULADO", "", True, False),
        ("Regulado:", "SOCICAM - Administração, Projetos e Representações Ltda", False, False),
        ("Responsável:", "THIAGO DUARTE PIMENTEL", False, True),
        ("Endereço:", "Avenida Prefeito Antônio Pereira, S/N Várzea Recife/PE CEP: 50.950-030", False, False),
        ("Representantes para acompanhar:", "Recife (TIP): Monalisa Pereira", False, False),

        ("3.3 DO REGULADOR", "", True, False),
        ("Regulador:", "Agência de Regulação de Pernambuco (Arpe)", False, False),
        ("Diretor Presidente:", "CARLOS PORTO FILHO", False, True),
        ("Endereço:", "Av. Cons. Rosa e Silva, 975, Aflitos, Recife/PE, CEP: 52.050-020", False, False),
        ("Estacionamento:", "Rua do Futuro, 150, Aflitos, Recife/PE", False, False),
        ("Responsáveis pela fiscalização:", responsaveis_formatted, False, False),
        ("Período da Fiscalização:", periodo_val, False, False),
        ("Tipo de Fiscalização:", "Direta e periódica.", False, False)
    ]


SOCICAM_GENERAL_INFO_COL_WIDTHS = [Inches(3.0), Inches(4.57)]
SOCICAM_GENERAL_INFO_HEADERS_INDICES = [0, 4, 9]


SOCICAM_METHODOLOGY_PARAGRAPHS = [
    [(
        "A fiscalização direta e periódica realizada pela Coordenadoria de Transportes e Rodovias da Arpe está submetida a uma "
        "metodologia organizada em três etapas: Preparação e Planejamento, Execução da Fiscalização e Monitoramento e Avaliação.",
        False, False, None
    )],
    [
        ("Preparação e Planejamento", True, False, None),
        (
            " - compreende a organização e estruturação das atividades preliminares à execução da fiscalização, destacando-se a "
            "elaboração e o envio de avisos de fiscalização à Concessionária e demais atividades de suporte à fiscalização, bem "
            "como a análise de fiscalizações anteriores com a identificação de eventuais Não Conformidades pendentes.",
            False, False, None
        )
    ],
    [
        ("Execução da Fiscalização", True, False, None),
        (
            " - a execução da fiscalização é pautada por um arcabouço de normas e diretrizes, possibilitando que todas as etapas "
            "sejam desenvolvidas de maneira eficiente e em conformidade aos padrões estabelecidos, destacando-se:",
            False, False, None
        )
    ]
]

SOCICAM_REFERENCES_BULLETS = [
    ("Lei nº 13.254, de 21 de junho de 2007, alterada pela Lei nº 15.200, de 17 de dezembro de 2013, e regulamentada pelo Decreto nº 40.559, de 31 de março de 2014.", False, True),
    ("", False, False),
    ("Resoluções Arpe nº 46, de 07 de abril de 2008 (Antiga nº 06/2008), alterada pela Resolução ARPE nº 53, de 26 de janeiro de 2009 (Antiga 003/2009); e nº 083, de 30 de julho de 2013.", False, True),
    ("", False, False),
    ("Contrato de Concessão de Serviço Público Nº 1.041.080/08, de 19 de setembro de 2008 e aditivos, em especial, o Segundo Termo Aditivo ao Contrato de Concessão, de 29 de setembro de 2017.", False, True),
    ("", False, False),
    ("Normas Técnicas da ABNT.", False, True)
]

SOCICAM_REFERENCES_LEFT_INDENT_PT = 53.4

SOCICAM_POST_METHODOLOGY_PARAGRAPHS = [
    [
        ("Monitoramento e Avaliação", True, False, None),
        (
            " - Esta etapa é fundamental para garantir a eficácia das ações corretivas a serem executadas pela Concessionária para "
            "a melhoria contínua dos serviços prestados. Os principais instrumentos do Monitoramento e Avaliação são: Termo de "
            "Notificação e respectivo Relatório de Fiscalização, Plano de Ação da Concessionária e Relatórios de Monitoramento e "
            "Avaliação Final.",
            False, False, None
        )
    ]
]

SOCICAM_QUADROS_SECTION_TITLE = "4. FISCALIZAÇÃO"
SOCICAM_QUADRO_TITLE_TEMPLATE = "Quadro 1 – Não Conformidades do {local_val}"

SOCICAM_NC_TABLE_HEADERS = [
    "IDENTIFICAÇÃO",
    "DESCRIÇÃO",
    "REGISTRO\nFOTOGRÁFICO",
    "FUNDAMENTO DA INFRAÇÃO\n(ANEXO V CONTRATO DE CONCESSÃO)",
    "DETERMINAÇÃO"
]


def get_socicam_quadro_intro_paragraphs(data_extenso: str, team_runs: list, local_val: str) -> list:
    """Gera parágrafos introdutórios da Seção 4. Fiscalização para o SOCICAM."""
    p1 = [
        ("As ações de fiscalização foram realizadas, em ", False, False, None),
        (f"{data_extenso}, ", False, False, None),
        ("pela equipe formada pelos Especialista em Regulação ", False, False, None)
    ] + team_runs + [
        (f", no {local_val}.", False, False, None)
    ]

    p2 = [
        ("As Não Conformidades constatadas estão relacionadas ao ", False, False, None),
        ("Programa de Manutenção dos Terminais Rodoviários", True, False, None),
        (", Anexo V do Contrato de Concessão, conforme descritas no ", False, False, None),
        ("Quadro 1", True, False, None),
        (", a seguir, com indicação dos respectivos registros fotográficos no ", False, False, None),
        ("Apêndice A", True, False, None),
        (".", False, False, None)
    ]
    return [p1, p2]


SOCICAM_FINALIZACAO_SECTIONS_CONFIG = {
    "5": "determinações",
    "6": "recomendações",
    "7": "conclusões"
}


def get_socicam_determinations_paragraphs(total_ncs: int, extenso_ncs: str) -> list:
    """Gera parágrafos da Seção 5. Determinações Gerais para o SOCICAM."""
    return [
        [(
            "Considerando os dispositivos contratuais pertinentes e visando garantir a qualidade dos serviços prestados, "
            "determina-se que a SOCICAM tome as seguintes medidas através de plano de ação:",
            False, False, None
        )],
        [
            ("Manutenção e Monitoramento", True, False, None),
            (
                ": adotar medidas para assegurar a manutenção, o monitoramento contínuo e o cumprimento do Programa de Manutenção "
                "dos Terminais Rodoviários, constante da proposta da SOCICAM nos subitens 9.1.1 Manutenção Preventiva; 9.1.2 Manutenção "
                "Corretiva e 9.1.3 Tabela de Classificação de Níveis de Falha (tabela de tempos máximos para os níveis de atendimento).",
                False, False, None
            )
        ],
        [
            ("Medidas imediatas", True, False, None),
            (" para resolutividade das ", False, False, None),
            (f"{total_ncs} ({extenso_ncs}) novas Não Conformidades", True, False, None),
            (" constatadas, nos prazos estabelecidos, conforme disposto no Quadro 1, na coluna denominada Determinações.", False, False, None)
        ]
    ]


SOCICAM_RECOMMENDATIONS_PARAGRAPHS = [
    [(
        "Considerando as disposições do Contrato de Concessão, em especial, o Anexo III – Regulamento Interno dos Terminais "
        "Rodoviários, aprovado pela Resolução Arpe nº 46, de 07 de abril de 2008 (Antiga nº 06/2008), bem como a legislação "
        "aplicável, devem ser observadas pela SOCICAM as seguintes recomendações:",
        False, False, None
    )],
    [(
        "Garantir condições de segurança, higiene, acessibilidade e conforto aos usuários dos Terminais Rodoviários, sejam passageiros, "
        "público em geral, comerciantes neles estabelecidos, empresas de transportes e de seus empregados.",
        False, False, None
    )],
    [(
        "Exigir a utilização de EPI adequados, inclusive por funcionários de empresas terceirizadas que prestem serviços nos "
        "Terminais Rodoviários.",
        False, False, None
    )],
    [(
        "Providenciar a correta manutenção (evitar o vencimento) de extintores de incêndios nos Terminais Rodoviários.",
        False, False, None
    )],
    [(
        "Instalar, sempre que necessário, aviso de sinalização de segurança, principalmente em pontos de risco de acidentes.",
        False, False, None
    )]
]


def get_socicam_conclusions_paragraphs(nc_frase: str, terminal_curto: str) -> list:
    """Gera parágrafos da Seção 7. Conclusões para o SOCICAM."""
    return [
        [
            ("Tendo em vista as ações de fiscalização realizadas pela ARPE foram constatadas ", False, False, None),
            (f"{nc_frase} no {terminal_curto}", True, False, None),
            (", que devem ser solucionadas pela SOCICAM de acordo com as Determinações desta Agência de Regulação (v. Quadro 1).", False, False, None)
        ],
        [(
            "Por fim, solicita-se o encaminhamento deste Processo de Fiscalização para conhecimento e acompanhamento da EPTI, "
            "na qualidade de Poder Concedente do Contrato de Concessão e gestora do Sistema de Transporte Coletivo Intermunicipal "
            "de Passageiros (STCIP-PE).",
            False, False, None
        )]
    ]
