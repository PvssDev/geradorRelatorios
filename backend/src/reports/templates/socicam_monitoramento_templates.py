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
    ("SOCICAM", "SOCICAM - Administração, Projetos e Representações Ltda"),
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
    data_extenso: str = "",
    n_curr_str: str = "1º",
    ctr_num: str = "04/2025",
    id_monitoramento: Any = None,
    qtd_pendentes: Any = None,
    local_val: Any = "Recife",
    recomendacoes_socicam: str = "",
) -> List[List[Tuple[str, bool, bool, Any]]]:
    """Gera os parágrafos estruturados para a Seção 5 (Conclusões e Recomendações) do SOCICAM Monitoramento."""
    from core.rules.socicam_rules import normalizar_nome_terminal_passageiros_municipio

    id_mon = str(id_monitoramento or "").strip() or str(ctr_num or "04/2025").strip()
    qtd_analisadas = max(0, int(total_ncs or 0))
    qtd_pend = max(0, int(qtd_pendentes if qtd_pendentes is not None else qtd_analisadas))
    terminal_str = normalizar_nome_terminal_passageiros_municipio(local_val)

    termo_analisadas = (
        "1 Não Conformidade pendente"
        if qtd_analisadas == 1
        else f"{qtd_analisadas} Não Conformidades pendentes"
    )
    termo_pendentes = (
        "1 permanece pendente"
        if qtd_pend == 1
        else f"{qtd_pend} permanecem pendentes"
    )

    rec_clean = str(recomendacoes_socicam or "").strip()
    if rec_clean.lower() in ("nan", "none"):
        rec_clean = ""
    if rec_clean:
        rec_sem_ponto_final = rec_clean.rstrip(".")
        if rec_sem_ponto_final and rec_sem_ponto_final[0] in (",", ";", ":", "-"):
            sufixo_rec = f"{rec_sem_ponto_final}."
        else:
            sufixo_rec = f" {rec_sem_ponto_final}."
    else:
        sufixo_rec = "."

    p1 = (
        f"Analisou-se neste {n_curr_str} Relatório de Monitoramento do Processo de Fiscalização "
        f"Técnico-Operacional ARPE/CTR nº {id_mon}, {termo_analisadas} no {terminal_str}, "
        f"constatando-se que {termo_pendentes}{sufixo_rec}"
    )
    p2 = (
        "Sugere-se o encaminhamento deste Relatório de Monitoramento também para conhecimento da EPTI, "
        "de modo a permitir o efetivo acompanhamento das ações fiscalizatórias desta Agência, em atendimento "
        "à Lei nº 13.254, de 2007 e alterações, e o Contrato de Concessão nº 1.041.080/08."
    )
    p3 = (
        "Por fim, informa-se que a próxima fiscalização nesse Terminal Rodoviário de Passageiros concedido "
        "à SOCICAM, está prevista para XXXXXX, conforme cronograma anual da Coordenadoria de Transportes e Rodovias."
    )
    return [
        [(p1, False, False, None)],
        [(p2, False, False, None)],
        [(p3, False, False, None)],
    ]
