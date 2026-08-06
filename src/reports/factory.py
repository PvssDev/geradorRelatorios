from reports.cra import CraReport
from reports.crc import CrcReport
from reports.socicam import SocicamReport
from reports.cra_monitoramento import CraMonitoramentoReport
from reports.crc_monitoramento import CrcMonitoramentoReport
from reports.socicam_monitoramento import SocicamMonitoramentoReport

_registry = {
    "CRA": CraReport(),
    "CRC": CrcReport(),
    "SOCICAM": SocicamReport(),
    "CRA_MONITORAMENTO": CraMonitoramentoReport(),
    "CRC_MONITORAMENTO": CrcMonitoramentoReport(),
    "SOCICAM_MONITORAMENTO": SocicamMonitoramentoReport()
}

def get_report(key: str):
    """Retorna a instância de relatório correspondente à chave fornecida."""
    upper_key = str(key).upper().strip()
    if upper_key in _registry:
        return _registry[upper_key]
    # Fallback para o primeiro registrado se não encontrar
    return _registry["CRA"]

def get_all_reports():
    """Retorna a lista de todas as instâncias de relatório registradas."""
    return list(_registry.values())
