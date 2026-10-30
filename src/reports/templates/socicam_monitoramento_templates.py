# -*- coding: utf-8 -*-
"""
Templates, textos regulatórios e configurações estáticas do Relatório SOCICAM Monitoramento.
Concessionária SOCICAM - Administração, Projetos e Representações Ltda.
Contrato de Concessão de Serviço Público Nº 1.041.080/08 (Terminais de Recife/TIP, Caruaru, Garanhuns, Petrolina).
"""
from typing import Any, List, Tuple
from docx.shared import Inches

SOCICAM_MONITORAMENTO_KEY = "SOCICAM_MONITORAMENTO"
SOCICAM_MONITORAMENTO_DISPLAY_NAME = "SOCICAM (Monitoramento)"
SOCICAM_MONITORAMENTO_DEFAULT_CONTRATO = "CT. nº 1.041.080/08"
SOCICAM_MONITORAMENTO_CONTRATO_NUMERO = "1.041.080/08"

SOCICAM_MONITORAMENTO_ABBREVIATIONS = [
    ("ABNT", "Associação Brasileira de Normas Técnicas"),
    ("ARPE", "Agência de Regulação de Pernambuco"),
    ("EPTI", "Empresa Pernambucana de Transporte Coletivo Intermunicipal"),
    ("NC", "Não Conformidade"),
    ("PCD", "Pessoa com Deficiência"),
    ("TIP", "Terminal Rodoviário de Passageiros do Recife")
]

SOCICAM_MONITORAMENTO_QUADRO1_HEADERS = ["NÃO CONFORMIDADE", "INFORMAÇÃO SOCICAM", "SITUAÇÃO"]
SOCICAM_MONITORAMENTO_QUADRO1_COL_WIDTHS = [Inches(3.20), Inches(3.20), Inches(1.17)]


def get_socicam_monitoramento_intro_paragraphs(
    n_curr_str: str,
    ctr_num: str,
    data_extenso: str
) -> List[List[Tuple[str, bool, bool, Any]]]:
    """Gera os parágrafos estruturados para a Seção 1 (Introdução) do SOCICAM Monitoramento."""
    p1 = (
        "O monitoramento das Não Conformidades apontadas nos relatórios de fiscalização é fundamental para acompanhar as ações "
        "desenvolvidas pelas concessionárias, garantindo o cumprimento adequado dos Contratos de Concessão."
    )
    p2 = (
        f"Nesse contexto este {n_curr_str} Relatório de Monitoramento do Processo de Fiscalização Técnico-Operacional ARPE/CTR nº {ctr_num} "
        f"descreve a evolução das Não Conformidades listadas no Relatório de Fiscalização, referentes às vistorias realizadas nos Terminais "
        f"Rodoviários de Passageiros de Garanhuns, Caruaru e Recife (TIP) concedidos à Empresa SOCICAM - Administração, Projetos e Representações Ltda (SOCICAM)."
    )
    p3 = (
        f"As informações disponibilizadas pela SOCICAM foram consideradas como referência para as vistorias realizadas em {data_extenso} "
        f"nos referidos Terminais Rodoviários."
    )
    return [
        [(p1, False, False, None)],
        [(p2, False, False, None)],
        [(p3, False, False, None)]
    ]


def get_socicam_monitoramento_objective_paragraphs(
    n_curr_str: str,
    ctr_num: str
) -> List[List[Tuple[str, bool, bool, Any]]]:
    """Gera o parágrafo estruturado para a Seção 2 (Objetivo) do SOCICAM Monitoramento."""
    p = (
        f"Este Relatório do {n_curr_str} Monitoramento objetiva apresentar os resultados das vistorias acerca das Não Conformidades "
        f"registradas no Relatório de Fiscalização Técnico-Operacional ARPE/CTR nº {ctr_num}, referentes aos Terminais Rodoviários "
        f"de Passageiros dos municípios de Garanhuns, Caruaru e Recife (TIP), conforme o cronograma encaminhado pela Concessionária SOCICAM."
    )
    return [[(p, False, False, None)]]


def get_socicam_monitoramento_conclusions_paragraphs(
    total_ncs: int,
    data_extenso: str,
    n_curr_str: str,
    ctr_num: str
) -> List[List[Tuple[str, bool, bool, Any]]]:
    """Gera os parágrafos estruturados para a Seção 5 (Conclusões e Recomendações) do SOCICAM Monitoramento."""
    if total_ncs == 0:
        conc_nc = "todas as Não Conformidades foram sanadas"
        singular_plural_nc = "da Não Conformidade identificada"
    elif total_ncs == 1:
        conc_nc = "permanece uma Não Conformidade ainda sem solução definitiva"
        singular_plural_nc = "da Não Conformidade identificada"
    else:
        conc_nc = f"permanecem {total_ncs} Não Conformidades ainda sem solução definitiva"
        singular_plural_nc = "das Não Conformidades identificadas"

    p1 = (
        f"As vistorias técnicas, realizadas em {data_extenso}, bem como as análises apresentadas neste "
        f"{n_curr_str} Relatório de Monitoramento do Relatório de Fiscalização Técnico-Operacional ARPE/CTR "
        f"nº {ctr_num}, indicam que {conc_nc}."
    )
    p2 = (
        "Diante desse resultado, considera-se necessário que a ARPE continue realizando vistorias até que a "
        f"Concessionária efetive a execução dos serviços para correção {singular_plural_nc}."
    )
    return [
        [(p1, False, False, None)],
        [(p2, False, False, None)]
    ]
