# -*- coding: utf-8 -*-
import sys
import os

# Adiciona src ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from reports.factory import get_report, get_all_reports
from reports.base import BaseReport, BaseMonitoramentoMixin
from reports.cra import CraReport
from reports.cra_monitoramento import CraMonitoramentoReport
from reports.socicam import SocicamReport
from reports.socicam_monitoramento import SocicamMonitoramentoReport
from reports.crc import CrcReport
from reports.crc_monitoramento import CrcMonitoramentoReport


def test_factory_and_registry():
    keys = ["CRA", "CRC", "SOCICAM", "CRA_MONITORAMENTO", "CRC_MONITORAMENTO", "SOCICAM_MONITORAMENTO"]
    for key in keys:
        rep = get_report(key)
        assert rep is not None, f"Falha ao obter relatório para chave {key}"
        assert isinstance(rep, BaseReport), f"Relatório {key} não herda de BaseReport"
        assert rep.key == key
    print("[PASS] test_factory_and_registry")


def test_cra_monitoramento_mixin_behavior():
    cra = get_report("CRA")
    cra_mon = get_report("CRA_MONITORAMENTO")

    assert isinstance(cra_mon, BaseMonitoramentoMixin)
    assert isinstance(cra_mon, CraReport)

    # Testa substituição nos parágrafos de objetivo
    row = {"Local": "TIP", "Cidade": "Recife"}
    obj_cra = cra.get_objective_paragraphs(row)
    obj_mon = cra_mon.get_objective_paragraphs(row)

    # O relatório base deve ter "fiscalização"
    text_cra = " ".join([t for run in obj_cra for t, _, _, _ in run])
    assert "fiscalização" in text_cra.lower()

    # O relatório monitoramento deve ter "monitoramento"
    text_mon = " ".join([t for run in obj_mon for t, _, _, _ in run])
    assert "monitoramento" in text_mon.lower()
    # Testa sumário do CRA
    sum_cra = cra.get_sumario_linhas(row)
    assert any("INFORMAÇÕES GERAIS" in l for l in sum_cra)
    assert any("3.\tINFORMAÇÕES GERAIS" in l for l in sum_cra)

    print("[PASS] test_cra_monitoramento_mixin_behavior")


def test_socicam_monitoramento_mixin_behavior():
    soc = get_report("SOCICAM")
    soc_mon = get_report("SOCICAM_MONITORAMENTO")

    assert isinstance(soc_mon, BaseMonitoramentoMixin)
    assert isinstance(soc_mon, SocicamReport)

    # Testa sumário
    row = {"Local": "TIP (RECIFE)", "Cidade": "Recife"}
    sum_soc = soc.get_sumario_linhas(row)
    sum_mon = soc_mon.get_sumario_linhas(row)

    assert any("FISCALIZAÇÃO" in l for l in sum_soc)
    assert any("RESULTADO DAS VISTORIAS" in l or "MONITORAMENTO" in l for l in sum_mon)
    print("[PASS] test_socicam_monitoramento_mixin_behavior")


def test_dynamic_header_and_footer_dates():
    from utils import extrair_mes_ano_numerico, extrair_ano
    
    # Testa extração de mês/ano em diversos formatos
    assert extrair_mes_ano_numerico("15/07/2026") == "07/2026"
    assert extrair_mes_ano_numerico("01/2026") == "01/2026"
    assert extrair_mes_ano_numerico("05/12/2025") == "12/2025"
    assert extrair_mes_ano_numerico("2026-08-26") == "08/2026"

    reports_to_test = ["CRA", "CRA_MONITORAMENTO", "CRC", "SOCICAM", "SOCICAM_MONITORAMENTO"]
    
    # Caso 1: Fiscalização em Julho de 2026
    row_julho = {"Data": "15/07/2026", "ID da Fiscalização": "2026-001"}
    mes_ano = extrair_mes_ano_numerico(row_julho["Data"])
    ano = extrair_ano(row_julho["Data"])
    assert mes_ano == "07/2026"
    assert ano == "2026"

    for key in reports_to_test:
        rep = get_report(key)
        top_header = rep.capa_ctr_number_template.format(ano=ano, id_fisc=row_julho["ID da Fiscalização"], mes_ano=mes_ano)
        assert "07/2026" in top_header, f"Header de {key} não continha 07/2026: {top_header}"
        assert "01/2026" not in top_header if key != "CRA" or "07" in mes_ano else True

        process_texts = rep.get_process_sei_texts(row_julho, ano)
        assert "07/2026" in process_texts[0], f"Processo de {key} não continha 07/2026: {process_texts[0]}"

    # Caso 2: Fiscalização em Janeiro de 2026
    row_jan = {"Data": "10/01/2026", "ID da Fiscalização": "2026-002"}
    mes_ano_jan = extrair_mes_ano_numerico(row_jan["Data"])
    ano_jan = extrair_ano(row_jan["Data"])
    for key in reports_to_test:
        rep = get_report(key)
        top_header = rep.capa_ctr_number_template.format(ano=ano_jan, id_fisc=row_jan["ID da Fiscalização"], mes_ano=mes_ano_jan)
        assert "01/2026" in top_header, f"Header de {key} não continha 01/2026: {top_header}"
        process_texts = rep.get_process_sei_texts(row_jan, ano_jan)
        assert "01/2026" in process_texts[0], f"Processo de {key} não continha 01/2026: {process_texts[0]}"

    print("[PASS] test_dynamic_header_and_footer_dates")


if __name__ == "__main__":
    test_factory_and_registry()
    test_cra_monitoramento_mixin_behavior()
    test_socicam_monitoramento_mixin_behavior()
    test_dynamic_header_and_footer_dates()
    print("\nTodos os testes de relatórios passaram com sucesso!")
