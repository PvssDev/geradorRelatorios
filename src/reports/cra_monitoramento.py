# -*- coding: utf-8 -*-
from reports.base import BaseMonitoramentoMixin
from reports.cra import CraReport


class CraMonitoramentoReport(BaseMonitoramentoMixin, CraReport):
    @property
    def key(self) -> str:
        return "CRA_MONITORAMENTO"

    @property
    def display_name(self) -> str:
        return "CRA (Monitoramento)"

    @property
    def capa_titulo(self) -> str:
        return "RELATÓRIO DE MONITORAMENTO PROCESSO ADMINISTRATIVO"

    @property
    def capa_ctr_number_template(self) -> str:
        return "RELATÓRIO DE MONITORAMENTO PROCESSO ADMINISTRATIVO CTR Nº 01/{ano}"

    def get_process_sei_texts(self, ano) -> list:
        return [
            f"RELATÓRIO DE MONITORAMENTO PROCESSO ADMINISTRATIVO Nº 07/{ano} - CTR",
            f"SEI Nº xxxxxxxxxxxx/{ano}-XX"
        ]

    def get_capa_titulos(self, row, ano) -> list:
        base_titulos = super().get_capa_titulos(row, ano)
        return [t.replace("FISCALIZAÇÃO", "MONITORAMENTO") for t in base_titulos]
