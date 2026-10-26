# -*- coding: utf-8 -*-
"""
Templates, textos regulatórios e configurações estáticas do Relatório CRA Monitoramento.
Complexo Viário e Logístico de SUAPE – Express Way (Contrato CT Nº 043/2011 e Convênio ARPE/Suape nº 003/2021).
"""
from typing import Any, List, Tuple
from docx.shared import Inches

from reports.templates.cra_templates import CRA_ABBREVIATIONS

CRA_MONITORAMENTO_KEY = "CRA_MONITORAMENTO"
CRA_MONITORAMENTO_DISPLAY_NAME = "CRA (Monitoramento)"
CRA_MONITORAMENTO_DEFAULT_CONTRATO = "CT. nº 043/2011"
CRA_MONITORAMENTO_CONVENIO = "Convênio ARPE/Suape nº 003/2021"

CRA_MONITORAMENTO_CAPA_TITULO = "RELATÓRIO DO 1° MONITORAMENTO DO PROCESSO DE FISCALIZAÇÃO TÉCNICO-OPERACIONAL"
CRA_MONITORAMENTO_CAPA_CTR_NUMBER_TEMPLATE = (
    "COORDENADORIA DE TRANSPORTES E RODOVIAS\n"
    "RELATÓRIO DO 1° MONITORAMENTO DO PROCESSO\n"
    "DE FISCALIZAÇÃO TÉCNICO-OPERACIONAL CTR Nº {mes_ano}"
)

CRA_MONITORAMENTO_ABBREVIATIONS = list(CRA_ABBREVIATIONS)

CRA_MONITORAMENTO_QUADRO1_COL_WIDTHS = [Inches(1.80), Inches(4.20), Inches(1.57)]


def get_cra_monitoramento_quadro1_headers(ctr_num: str) -> List[str]:
    """Retorna os cabeçalhos das 3 colunas do Quadro 1 de monitoramento."""
    return [
        "REFERÊNCIA",
        f"CONSTATAÇÃO / NÃO CONFORMIDADE RELATÓRIO ARPE/CTR {ctr_num}",
        "SITUAÇÃO"
    ]


def get_cra_monitoramento_objective_paragraphs() -> List[List[Tuple[str, bool, bool, Any]]]:
    """Retorna parágrafo objetivo padrão do relatório."""
    return [
        [(
            "Este Relatório de Monitoramento tem por objetivo apresentar os resultados das vistorias realizadas pela ARPE "
            "no Complexo Viário e Logístico de SUAPE referentes às Não Conformidades do relatório anterior.",
            False, False, None
        )]
    ]


def get_cra_monitoramento_intro_paragraphs(ctr_num: str, n_curr_str: str, data_extenso: str) -> List[List[Tuple[str, bool, bool, Any]]]:
    """Gera parágrafos da Seção 1. Introdução para o CRA Monitoramento."""
    return [
        [(
            f"Registra-se, preliminarmente, que o Relatório de Fiscalização Técnico-Operacional ARPE/CTR {ctr_num} "
            f"registrou as Não Conformidades identificadas e foi devidamente encaminhado à Concessionária Rota do "
            f"Atlântico (CRA) e aos órgãos concedentes para as providências cabíveis.",
            False, False, None
        )],
        [(
            "A Concessionária Rota do Atlântico (CRA) apresentou o cronograma de obras atualizado por trecho, com detalhamento "
            "dos prazos de execução das ações de conservação especial do pavimento e sinalização viária.",
            False, False, None
        )],
        [(
            f"Neste contexto, este {n_curr_str} Relatório de Monitoramento descreve a evolução das Não Conformidades apontadas, "
            f"com base nas vistorias técnicas realizadas pela equipe da ARPE em {data_extenso} no Sistema Viário Express Way.",
            False, False, None
        )]
    ]


def get_cra_monitoramento_objective_section_paragraphs(ctr_num: str, n_curr_str: str, data_vistoria: str) -> List[List[Tuple[str, bool, bool, Any]]]:
    """Gera parágrafos da Seção 2. Objetivo para o CRA Monitoramento."""
    return [
        [(
            f"Este {n_curr_str} Relatório de Monitoramento tem como objetivo apresentar os resultados das vistorias realizadas pela ARPE, "
            f"em {data_vistoria}, no Sistema Viário Express Way referentes às Não Conformidades constantes do Relatório de Fiscalização "
            f"Técnico-Operacional ARPE/CTR {ctr_num}.",
            False, False, None
        )]
    ]


def get_cra_monitoramento_conclusions_paragraphs(n_curr_str: str, ctr_num: str, data_extenso: str) -> List[List[Tuple[str, bool, bool, Any]]]:
    """Gera parágrafos da Seção 5. Conclusões e Recomendações do CRA Monitoramento."""
    return [
        [(
            f"O resultado das vistorias realizadas nos dias {data_extenso} e das respectivas análises apresentadas neste "
            f"{n_curr_str} Relatório de Monitoramento demonstram a evolução do tratamento das Não Conformidades identificadas no "
            f"Relatório de Fiscalização Técnico-Operacional ARPE/CTR {ctr_num}. Recomenda-se que a Concessionária mantenha atualizado "
            f"o cronograma das obras e soluções pendentes visando permitir à ARPE uma programação efetiva do monitoramento.",
            False, False, None
        )],
        [(
            f"Por fim, solicita-se dar conhecimento deste {n_curr_str} Relatório de Monitoramento do Relatório de Fiscalização "
            f"Técnico-Operacional ARPE/CTR {ctr_num} à Diretoria de Desenvolvimento e Gestão Portuária de SUAPE para as devidas "
            f"providências, em atendimento ao Convênio ARPE/Suape nº 003/2021.",
            False, False, None
        )]
    ]
