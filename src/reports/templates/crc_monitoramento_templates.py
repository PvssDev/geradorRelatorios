# -*- coding: utf-8 -*-
"""
Templates, textos regulatórios e configurações estáticas do Relatório CRC Monitoramento.
Concessionária Rota dos Coqueiros (Contrato de Concessão Patrocinada CGPE nº 001/2006).
Sistema Viário da Praia do Paiva (PE-024 / Ponte sobre o Rio Jaboatão).
"""
from typing import Any, List, Tuple
from docx.shared import Inches

CRC_MONITORAMENTO_KEY = "CRC_MONITORAMENTO"
CRC_MONITORAMENTO_DISPLAY_NAME = "CRC (Monitoramento)"
CRC_MONITORAMENTO_DEFAULT_CONTRATO = "CGPE – 001/2006"

CRC_MONITORAMENTO_CAPA_TITULO = "RELATÓRIO DO {n_curr_str} MONITORAMENTO DO PROCESSO DE FISCALIZAÇÃO TÉCNICO-OPERACIONAL"
CRC_MONITORAMENTO_CAPA_CTR_NUMBER_TEMPLATE = (
    "COORDENADORIA DE TRANSPORTES E RODOVIAS\n"
    "RELATÓRIO DO {n_curr_str} MONITORAMENTO DO PROCESSO\n"
    "DE FISCALIZAÇÃO TÉCNICO-OPERACIONAL CTR Nº {ctr_num}"
)

CRC_MONITORAMENTO_ABBREVIATIONS = [
    ("ABNT", "Associação Brasileira de Normas Técnicas"),
    ("ARPE", "Agência de Regulação de Pernambuco"),
    ("SEPPE", "Secretaria Executiva de Parcerias e Projetos Estratégicos"),
    ("NC", "Não Conformidade"),
    ("CRC", "Concessionária Rota dos Coqueiros S. A."),
    ("PER", "Programa de Exploração da Rodovia, anexo ao Contrato de Concessão Patrocinada CGPE-001/2006"),
    ("VI", "Verificador Independente, atualmente, o Consórcio formado pelas empresas Maciel Consultores S/S Ltda e Estratégica Serviços de Engenharia Consultiva Ltda")
]

CRC_MONITORAMENTO_QUADRO1_COL_WIDTHS = [Inches(1.15), Inches(3.60), Inches(1.06)]

CRC_MONITORAMENTO_QUADRO1_NOTA = (
    "(*) ID. NC: Identificação da Não Conformidade, composta com o Segmento Homogêneo (SH) "
    "e a quilometragem do ponto fiscalizado (KM)."
)


def get_crc_monitoramento_quadro1_headers(data_vistoria_atual: str) -> List[str]:
    """Retorna os cabeçalhos das 3 colunas do Quadro 1 do CRC Monitoramento."""
    return ["ID.NC(*)", "CONSTATAÇÃO (27/05/2025)", f"SITUAÇÃO {data_vistoria_atual}"]


def get_crc_monitoramento_intro_paragraphs(
    is_fiscalizacao: bool,
    ctr_num: str,
    data_vist_prev: str,
    val_ncs: int,
    processo_sei_prev: str,
    oficio_num_prev: str,
    oficio_data_prev: str,
    carta_num_prev: str,
    carta_data_prev: str,
    carta_sei_prev: str,
    n_prev_str: str = "1º"
) -> List[List[Tuple[str, bool, bool, Any]]]:
    """
    Gera os parágrafos estruturados para a Seção 1 (Introdução) do CRC Monitoramento.
    Ajusta a concordância gramatical para 1 ou múltiplas não conformidades pendentes.
    """
    if val_ncs == 1:
        nc_phrase = "1 Não Conformidade foi apontada" if is_fiscalizacao else "1 Não Conformidade restava pendente"
    else:
        nc_phrase = f"{val_ncs} Não Conformidades foram apontadas" if is_fiscalizacao else f"{val_ncs} Não Conformidades restavam pendentes"

    if is_fiscalizacao:
        p1 = (
            f"Registra-se, preliminarmente, que na vistoria técnica que originou o Relatório de Fiscalização "
            f"Técnico-Operacional CTR {ctr_num}, realizada na Rodovia Rota dos "
            f"Coqueiros em {data_vist_prev}, verificou-se que {nc_phrase}. "
            f"Assim, o referido Relatório de Fiscalização (Doc. SEI nº {processo_sei_prev}) foi encaminhado à Concessionária "
            f"Rota dos Coqueiros (CRC) pelo Ofício Arpe DTO nº {oficio_num_prev}, de {oficio_data_prev}, com a recomendação "
            f"para que a Concessionária mantenha a ARPE informada sobre as tratativas referentes às não conformidades apontadas."
        )
    else:
        p1 = (
            f"Registra-se, preliminarmente, que na última vistoria técnica de monitoramento das Não Conformidades "
            f"apontadas no Relatório de Fiscalização Técnico-Operacional CTR {ctr_num}, realizada na Rodovia Rota dos "
            f"Coqueiros em {data_vist_prev}, verificou-se que {nc_phrase}. "
            f"Assim, o Relatório do {n_prev_str} Monitoramento (Doc. SEI nº {processo_sei_prev}) foi encaminhado à Concessionária "
            f"Rota dos Coqueiros (CRC) pelo Ofício Arpe DTO nº {oficio_num_prev}, de {oficio_data_prev}, reforçando a recomendação "
            f"para que a Concessionária mantenha a ARPE informada sobre as tratativas referentes às não conformidades pendentes."
        )

    p2 = (
        f"Em sequência, a Concessionária, por meio da Carta CRC/REG nº {carta_num_prev}, de {carta_data_prev} "
        f"(Doc. SEI nº {carta_sei_prev}), enviou sua manifestação informando as ações tomadas referentes às Não Conformidades pendentes."
    )

    return [
        [(p1, False, False, None)],
        [(p2, False, False, None)]
    ]


def get_crc_monitoramento_objective_paragraphs(
    n_curr_str: str,
    ctr_num: str,
    data_extenso: str,
    carta_num_prev: str
) -> List[List[Tuple[str, bool, bool, Any]]]:
    """Gera o parágrafo estruturado para a Seção 2 (Objetivo) do CRC Monitoramento."""
    p = (
        f"Este {n_curr_str} Relatório de Monitoramento da ARPE tem como objetivo informar sobre o acompanhamento das ações da CRC "
        f"referentes às Não Conformidades pendentes do Relatório de Fiscalização Técnico-Operacional ARPE/CTR {ctr_num}, "
        f"de 27/05/2025, conforme as vistorias técnicas realizadas em {data_extenso}, considerando também o posicionamento da "
        f"Concessionária encaminhado à ARPE por meio da referida Carta CRC/REG nº {carta_num_prev}."
    )
    return [[(p, False, False, None)]]


def get_crc_monitoramento_conclusions_paragraphs(
    total_ncs: int,
    data_extenso: str,
    n_curr_str: str,
    ctr_num: str
) -> List[List[Tuple[str, bool, bool, Any]]]:
    """Gera os parágrafos estruturados para a Seção 5 (Conclusões e Recomendações) do CRC Monitoramento."""
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
        f"As vistorias técnicas, realizadas em {data_extenso}, bem como das análises apresentadas neste "
        f"{n_curr_str} Relatório de Monitoramento do Relatório de Fiscalização Técnico-Operacional ARPE/CTR "
        f"nº {ctr_num}, indicam que {conc_nc}."
    )
    p2 = (
        "Recomenda-se que a Concessionária mantenha a ARPE informada sobre as interações com a "
        "Associação Geral da Reserva do Paiva para evitar definitivamente a presença de detritos no trecho concedido."
    )
    p3 = (
        "Diante desse resultado, considera-se necessário que a ARPE continue realizando vistorias até que a "
        f"Concessionária efetive a execução dos serviços para correção {singular_plural_nc}."
    )

    return [
        [(p1, False, False, None)],
        [(p2, False, False, None)],
        [(p3, False, False, None)]
    ]
