# -*- coding: utf-8 -*-
"""
Contratos segregados de configuração e renderização (Interface Segregation Principle - ISP).
Cada interface isola uma responsabilidade específica da montagem do relatório,
permitindo que relatórios rodoviários e de terminais implementem apenas o que lhes compete.
"""
from typing import Any, Dict, List, Optional, Tuple, Protocol, runtime_checkable


@runtime_checkable
class ICapaConfig(Protocol):
    """Contrato para elementos visuais e textuais da primeira página (Capa)."""
    @property
    def key(self) -> str:
        ...

    @property
    def display_name(self) -> str:
        ...

    @property
    def default_contrato(self) -> str:
        ...

    @property
    def capa_orgao_concedente(self) -> str:
        ...

    @property
    def capa_secretaria(self) -> str:
        ...

    @property
    def capa_titulo(self) -> str:
        ...

    @property
    def capa_ctr_number_template(self) -> str:
        ...

    @property
    def capa_prestador_label(self) -> str:
        ...

    @property
    def capa_contrato_label(self) -> str:
        ...

    @property
    def capa_regulador_label(self) -> str:
        ...

    def get_capa_titulos(self, row: Any, ano: str) -> List[str]:
        ...

    def get_process_sei_texts(self, row: Any, ano: Optional[str] = None) -> List[str]:
        ...


@runtime_checkable
class ISumarioConfig(Protocol):
    """Contrato para paginação, lista de abreviaturas e tópicos do sumário."""
    @property
    def sumario_before_abreviaturas(self) -> bool:
        ...

    def get_abbreviations(self) -> List[Tuple[str, str]]:
        ...

    def get_sumario_linhas(self, row: Any, nc_df: Any = None) -> List[str]:
        ...


@runtime_checkable
class IQuadroConfig(Protocol):
    """Contrato para estruturação das tabelas de não conformidades e pontos de atenção."""
    @property
    def quadros_section_title(self) -> str:
        ...

    @property
    def nc_table_headers(self) -> List[str]:
        ...

    @property
    def nc_table_col_widths(self) -> List[Any]:
        ...

    def format_nc_table_total_row(self, table: Any, row_idx: int, total_ncs: int, col_widths: Optional[List[Any]] = None) -> None:
        ...

    def render_quadros(self, doc: Any, row: Any, nc_df: Any, criar_tabela_quadros_fn: Any) -> None:
        ...


@runtime_checkable
class IApendiceConfig(Protocol):
    """Contrato para renderização dos apêndices e memoriais fotográficos."""
    def render_apendices(
        self,
        doc: Any,
        row: Any,
        ncs_reais: Any,
        pas_reais: Any,
        fotos_dir: str,
        data_fisc: str,
        ano: str,
        criar_grade_fotos_fn: Any
    ) -> None:
        ...


@runtime_checkable
class IFinalizacaoConfig(Protocol):
    """Contrato para seções finais: determinações, recomendações e conclusões."""
    @property
    def finalizacao_sections_config(self) -> Dict[str, str]:
        ...

    def get_determinations_paragraphs(self, total_ncs: int) -> List[Any]:
        ...

    def get_recommendations_paragraphs(self) -> List[Any]:
        ...

    def get_conclusions_paragraphs(self, total_ncs: int, local_val: str) -> List[Any]:
        ...


@runtime_checkable
class IReportContract(
    ICapaConfig,
    ISumarioConfig,
    IQuadroConfig,
    IApendiceConfig,
    IFinalizacaoConfig,
    Protocol
):
    """Contrato consolidado que agrega as interfaces segregadas para o orquestrador."""
    ...
