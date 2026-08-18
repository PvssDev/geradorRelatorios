# -*- coding: utf-8 -*-
from reports.base import BaseMonitoramentoMixin
from reports.socicam import SocicamReport


class SocicamMonitoramentoReport(BaseMonitoramentoMixin, SocicamReport):
    @property
    def key(self) -> str:
        return "SOCICAM_MONITORAMENTO"

    @property
    def display_name(self) -> str:
        return "SOCICAM (Monitoramento)"

    @property
    def capa_titulo(self) -> str:
        return "RELATÓRIO DE MONITORAMENTO TÉCNICO-OPERACIONAL"

    @property
    def capa_ctr_number_template(self) -> str:
        return "RELATÓRIO DE MONITORAMENTO TÉCNICO-OPERACIONAL CTR Nº 03/{ano}"

    def get_process_sei_texts(self, ano) -> list:
        return [
            f"RELATÓRIO DE MONITORAMENTO TÉCNICO-OPERACIONAL PROC ADM Nº 04/{ano} - CTR",
            f"SEI Nº 0030200023.002186/2026-99"
        ]

    def get_capa_titulos(self, row, ano) -> list:
        local_val = str(row.get("Local", "TIP")).upper()
        if "TERMINAL" not in local_val and "MONITORAMENTO" not in local_val:
            local_val = (
                f"TERMINAL RODOVIÁRIO DE PASSAGEIROS DO RECIFE ({local_val})"
                if "RECIFE" in local_val or "TIP" in local_val
                else f"TERMINAL RODOVIÁRIO DE PASSAGEIROS ({local_val})"
            )
        return [
            f"MONITORAMENTO NO {local_val}",
            "PRESTADOR DE SERVIÇO: SOCICAM - ADMINISTRAÇÃO, PROJETOS E REPRESENTAÇÕES LTDA"
        ]
