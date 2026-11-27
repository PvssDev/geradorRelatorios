# -*- coding: utf-8 -*-
"""Router FastAPI de Histórico Analítico Permanente (LGPD: zero fotos, zero PII)."""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from core.rules.auth_sync_rules import agregar_resumo_historico
from server.auth_sync_schemas import ConcessaoLiteral, ModalidadeLiteral
from server.dependencies.auth_deps import get_current_user
from services.supabase_gateway import HttpSupabaseGateway, SupabaseGatewayError, get_supabase_gateway

router = APIRouter(prefix="/api/historico", tags=["historico"])


@router.get("/resumo")
def obter_resumo_historico(
    concessao: Optional[ConcessaoLiteral] = Query(default=None),
    modalidade: Optional[ModalidadeLiteral] = Query(default=None),
    data_inicio: Optional[str] = Query(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    data_fim: Optional[str] = Query(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    _caller: Dict[str, Any] = Depends(get_current_user),
    gateway: HttpSupabaseGateway = Depends(get_supabase_gateway),
):
    try:
        rows = gateway.list_historico_achados(
            concessao=concessao,
            modalidade=modalidade,
            data_inicio=data_inicio,
            data_fim=data_fim,
        )
        return agregar_resumo_historico(rows)
    except SupabaseGatewayError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))
