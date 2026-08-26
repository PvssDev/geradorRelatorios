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
        return "RELATÓRIO DE MONITORAMENTO PROCESSO ADMINISTRATIVO CTR Nº {mes_ano}"

    def get_process_sei_texts(self, row, ano=None) -> list:
        from utils import extrair_mes_ano_numerico, extrair_ano
        if isinstance(row, (str, int)) and ano is None:
            ano = str(row)
            mes_ano = f"01/{ano}"
        else:
            ano = ano or extrair_ano(row.get("Data", "") if hasattr(row, "get") else row["Data"])
            data_val = row.get("Data", "") if hasattr(row, "get") else (row["Data"] if isinstance(row, dict) or hasattr(row, "__getitem__") else "")
            mes_ano = extrair_mes_ano_numerico(data_val)
        return [
            f"RELATÓRIO DE MONITORAMENTO PROCESSO ADMINISTRATIVO Nº {mes_ano} - CTR",
            f"SEI Nº xxxxxxxxxxxx/{ano}-XX"
        ]

    def get_capa_titulos(self, row, ano) -> list:
        base_titulos = super().get_capa_titulos(row, ano)
        return [t.replace("FISCALIZAÇÃO", "MONITORAMENTO") for t in base_titulos]
