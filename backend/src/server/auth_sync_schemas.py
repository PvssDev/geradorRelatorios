# -*- coding: utf-8 -*-
"""Schemas Pydantic v2 estritos (extra='forbid') para Fase 1:
Auth Sem E-mail, Aprovações Individuais (ADM/Coordenador), Presigned URLs e Sync 6 Estados.
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

UserRoleLiteral = Literal["adm", "coordenador", "analista"]
RequestableRoleLiteral = Literal["coordenador", "analista"]
DecisaoLiteral = Literal["aprovada", "rejeitada"]
ClientTypeLiteral = Literal["mobile", "web"]
ConcessaoLiteral = Literal["CRA", "CRC", "SOCICAM"]
ModalidadeLiteral = Literal["Fiscalização", "Monitoramento"]
StatusHandoffLiteral = Literal["aguardando_web", "em_revisao", "emitida"]


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LoginRequestSchema(StrictBaseModel):
    usuario: str = Field(..., min_length=3, max_length=32)
    senha: str = Field(..., min_length=6, max_length=128)
    client_type: ClientTypeLiteral = "mobile"


class PerfilPublicoSchema(StrictBaseModel):
    id: str
    usuario: str
    nome_completo: str
    role: UserRoleLiteral
    ativo: bool


class SolicitarAcessoRequestSchema(StrictBaseModel):
    nome_completo: str = Field(..., min_length=3, max_length=120)
    usuario: str = Field(..., min_length=3, max_length=32)
    role_solicitado: RequestableRoleLiteral
    senha: str = Field(..., min_length=10, max_length=128)


class SolicitacaoItemResponseSchema(StrictBaseModel):
    id: str
    usuario: str
    nome_completo: str
    role_solicitado: RequestableRoleLiteral
    status: Literal["pendente", "aprovada", "rejeitada"]
    criado_em: str


class DecidirSolicitacaoRequestSchema(StrictBaseModel):
    decisao: DecisaoLiteral
    senha_confirmacao: Optional[str] = Field(default=None, max_length=128)


class PresignUploadRequestSchema(StrictBaseModel):
    vistoria_id: str = Field(..., min_length=3, max_length=80)
    nome_arquivo: str = Field(..., min_length=5, max_length=120)
    content_type: str = Field(default="image/jpeg", max_length=40)
    tamanho_kb: int = Field(..., gt=0, le=500)


class PresignUploadResponseSchema(StrictBaseModel):
    storage_key: str
    upload_url: str
    expires_in: int


class FotoTempSyncSchema(StrictBaseModel):
    id: str = Field(..., min_length=2, max_length=80)
    storage_key: str = Field(..., min_length=5, max_length=200)
    nome_arquivo: str = Field(..., min_length=5, max_length=120)
    tamanho_kb: int = Field(..., gt=0, le=500)
    ocorrencia_numero: Optional[int] = Field(default=None, ge=1)


class VistoriaSyncRequestSchema(StrictBaseModel):
    id: str = Field(..., min_length=3, max_length=80)
    id_fiscalizacao: str = Field(..., min_length=2, max_length=80)
    concessao: ConcessaoLiteral
    modalidade: ModalidadeLiteral
    payload_json: Dict[str, Any]
    fotos: List[FotoTempSyncSchema] = Field(default_factory=list)
