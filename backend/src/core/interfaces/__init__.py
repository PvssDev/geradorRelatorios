"""
Contratos e interfaces segregadas (ISP) do sistema de relatórios.
"""
from core.interfaces.report_contracts import (
    ICapaConfig,
    ISumarioConfig,
    IQuadroConfig,
    IApendiceConfig,
    IFinalizacaoConfig,
    IReportContract,
)

__all__ = [
    "ICapaConfig",
    "ISumarioConfig",
    "IQuadroConfig",
    "IApendiceConfig",
    "IFinalizacaoConfig",
    "IReportContract",
]
