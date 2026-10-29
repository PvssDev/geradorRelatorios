# -*- coding: utf-8 -*-
from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

TipoConcessao = Literal["CRA", "CRC", "SOCICAM"]
CategoriaVistoria = Literal["Fiscalização", "Monitoramento"]
SituacaoNC = Literal["Pendente", "Parcialmente Sanada", "Sanada"]


class PessoaSchema(BaseModel):
    nome: str
    matricula: str
    funcao: str


class CustomNcSchema(BaseModel):
    sigla: str = ""
    descricao: str


class FiscalizacaoItemSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id_fiscalizacao: str = Field(..., alias="ID da Fiscalização")
    data: str = Field("", alias="Data")
    hora: str = Field("", alias="Hora")
    cidade: str = Field("", alias="Cidade")
    local: str = Field(..., alias="Local")
    pessoal_responsavel: str = Field("", alias="Pessoal Responsável")
    coordenador: str = Field("", alias="Coordenador")
    contrato: str = Field(..., alias="Contrato")
    periodo: str = Field("", alias="Período")
    relatorio_gerado: bool = Field(False, alias="Relatório Gerado")


class RegistroNcItemSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id_fiscalizacao: str = Field(..., alias="ID da Fiscalização")
    numero: int = Field(1, alias="Nº")
    terminal: str = Field("", alias="Terminal")
    pista: str = Field("", alias="Pista")
    trecho: str = Field("", alias="Trecho")
    nao_conformidade: str = Field("", alias="Não Conformidade")
    ponto_atencao: str = Field("", alias="Ponto de Atenção")
    foto: str = Field("", alias="Foto")
    foto_anterior: str = Field("", alias="Foto Anterior")
    legenda_anterior: str = Field("", alias="Legenda Anterior")
    legenda_da_foto: Optional[str] = Field(None, alias="Legenda da Foto")
    observacoes: str = Field("", alias="Observações")
    identificacao: str = Field("", alias="Identificação")
    direcao_faixa: str = Field("", alias="Direção (faixa)")
    fundamento_infracao: str = Field("", alias="Fundamento da infração")
    determinacao: str = Field("", alias="Determinação")
    situacao: str = Field("Pendente", alias="Situação")
    analise_arpe: str = Field("", alias="Análise ARPE")
    is_relacionado: bool = False
    grupo_relacao: Optional[str] = None


class PlanilhaRequestSchema(BaseModel):
    fiscalizacoes: List[FiscalizacaoItemSchema]
    registros_nc: List[RegistroNcItemSchema]


class GerarRelatorioPayloadSchema(BaseModel):
    tipo_relatorio: TipoConcessao = "CRA"
    categoria_relatorio: CategoriaVistoria = "Fiscalização"
    fiscalizacoes: List[FiscalizacaoItemSchema]
    registros_nc: List[RegistroNcItemSchema]
    fotos_anteriores_b64: Dict[str, str] = Field(default_factory=dict)
    custom_siglas_map: Dict[str, str] = Field(default_factory=dict)
    responsaveis_override: Optional[List[PessoaSchema]] = None
    coordenadores_override: Optional[List[PessoaSchema]] = None
    compress_images: bool = True


