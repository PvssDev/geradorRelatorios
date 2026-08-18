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
    assert "fiscalização" not in text_mon.lower()
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
    assert any("MONITORAMENTO" in l for l in sum_mon)
    print("[PASS] test_socicam_monitoramento_mixin_behavior")


if __name__ == "__main__":
    test_factory_and_registry()
    test_cra_monitoramento_mixin_behavior()
    test_socicam_monitoramento_mixin_behavior()
    print("\nTodos os testes de relatórios passaram com sucesso!")
