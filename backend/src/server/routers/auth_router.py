# -*- coding: utf-8 -*-
"""Router FastAPI de Autenticação (camada HTTP apenas).

Toda regra de negócio vive em `services.auth_service.AuthService`; aqui só há
tradução HTTP ⇄ caso de uso, cookies de sessão e rate limit por IP.
"""

import os
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Cookie, Depends, HTTPException, Query, Request, Response

from server.auth_sync_schemas import (
    AdminAtualizarUsuarioRequestSchema,
    AdminConfirmacaoRequestSchema,
    AdminCriarUsuarioRequestSchema,
    AdminDeletarUsuarioRequestSchema,
    AdminResetSenhaRequestSchema,
    AuditLogItemSchema,
    DecidirSolicitacaoRequestSchema,
    LoginRequestSchema,
    RefreshRequestSchema,
    SolicitacaoItemResponseSchema,
    SolicitarAcessoRequestSchema,
    UsuarioGerenciavelSchema,
)
from server.dependencies.auth_deps import (
    ACCESS_COOKIE_NAME,
    REFRESH_COOKIE_NAME,
    get_auth_service,
    get_authenticated_perfil,  # noqa: F401  (reexport retrocompatível)
    get_current_user,
    require_adm_perfil,
    require_roles,
    verificar_origem_confiavel,
)
from server.dependencies.rate_limit import client_ip, enforce_ip_rate_limit, reset_rate_limiter  # noqa: F401
from services.auth_service import AuthError, AuthService, SessaoAutenticada, serializar_perfil_publico
from services.supabase_gateway import SupabaseGatewayError
from core.rules.auth_sync_rules import esta_conta_bloqueada

router = APIRouter(prefix="/api/auth", tags=["auth"])

ACCESS_COOKIE_MAX_AGE = 900
REFRESH_COOKIE_MAX_AGE = 604800


def _executar(fn, *args, **kwargs):
    """Traduz exceções de domínio/infra para HTTP sem vazar detalhes sensíveis."""
    try:
        return fn(*args, **kwargs)
    except AuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)
    except SupabaseGatewayError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))


def _aplicar_cookies_sessao(request: Request, response: Response, sessao: SessaoAutenticada) -> None:
    is_secure = os.environ.get("VERCEL", "") == "1" or request.url.scheme == "https"
    response.set_cookie(
        key=ACCESS_COOKIE_NAME, value=sessao.access_token, httponly=True, secure=is_secure,
        samesite="strict", max_age=ACCESS_COOKIE_MAX_AGE, path="/",
    )
    response.set_cookie(
        key=REFRESH_COOKIE_NAME, value=sessao.refresh_token, httponly=True, secure=is_secure,
        samesite="strict", max_age=REFRESH_COOKIE_MAX_AGE, path="/api/auth",
    )


def _resposta_sessao(request: Request, response: Response, sessao: SessaoAutenticada, client_type: str) -> Dict[str, Any]:
    if client_type == "web":
        _aplicar_cookies_sessao(request, response, sessao)
        return {"perfil": sessao.perfil}
    return {"access_token": sessao.access_token, "refresh_token": sessao.refresh_token, "perfil": sessao.perfil}


# ---------------------------------------------------------------------- #
# Sessão
# ---------------------------------------------------------------------- #
@router.post("/login", dependencies=[Depends(verificar_origem_confiavel)])
def login_corporativo(
    payload: LoginRequestSchema,
    request: Request,
    response: Response,
    background_tasks: BackgroundTasks,
    service: AuthService = Depends(get_auth_service),
):
    ip = client_ip(request)
    enforce_ip_rate_limit(ip)
    sessao = _executar(
        service.login,
        payload.usuario,
        payload.senha,
        ip,
        payload.client_type,
        background_tasks.add_task,
    )
    return _resposta_sessao(request, response, sessao, payload.client_type)


@router.post("/refresh", dependencies=[Depends(verificar_origem_confiavel)])
def renovar_sessao(
    request: Request,
    response: Response,
    background_tasks: BackgroundTasks,
    payload: Optional[RefreshRequestSchema] = None,
    refresh_cookie: Optional[str] = Cookie(default=None, alias=REFRESH_COOKIE_NAME),
    service: AuthService = Depends(get_auth_service),
):
    """Web: usa o cookie HttpOnly de refresh. APK: envia `refresh_token` no corpo."""
    ip = client_ip(request)
    enforce_ip_rate_limit(ip)
    if payload and payload.refresh_token:
        sessao = _executar(service.refresh, payload.refresh_token, ip, background_tasks.add_task)
        return _resposta_sessao(request, response, sessao, "mobile")
    sessao = _executar(service.refresh, refresh_cookie, ip, background_tasks.add_task)
    return _resposta_sessao(request, response, sessao, "web")


@router.get("/me")
def perfil_sessao_atual(caller: Dict[str, Any] = Depends(get_current_user)):
    """Restaura a sessão no F5 do Web sem expor JWT ao JavaScript."""
    return {"perfil": serializar_perfil_publico(caller)}


@router.post("/logout", dependencies=[Depends(verificar_origem_confiavel)])
def logout_corporativo(response: Response):
    response.delete_cookie(ACCESS_COOKIE_NAME, path="/")
    response.delete_cookie(REFRESH_COOKIE_NAME, path="/api/auth")
    return {"ok": True}


# ---------------------------------------------------------------------- #
# Solicitação e aprovação individual
# ---------------------------------------------------------------------- #
@router.post("/solicitar-acesso", status_code=201, dependencies=[Depends(verificar_origem_confiavel)])
def solicitar_acesso(
    payload: SolicitarAcessoRequestSchema,
    request: Request,
    service: AuthService = Depends(get_auth_service),
):
    ip = client_ip(request)
    enforce_ip_rate_limit(ip)
    sol_id = _executar(
        service.solicitar_acesso, payload.nome_completo, payload.usuario, payload.role_solicitado, payload.senha, ip
    )
    return {"ok": True, "id": sol_id}


@router.get("/solicitacoes", response_model=List[SolicitacaoItemResponseSchema])
def listar_solicitacoes(
    caller: Dict[str, Any] = Depends(require_roles("adm", "coordenador")),
    service: AuthService = Depends(get_auth_service),
):
    rows = _executar(service.listar_solicitacoes, caller)
    return [
        SolicitacaoItemResponseSchema(
            id=str(r["id"]),
            usuario=str(r["usuario"]),
            nome_completo=str(r["nome_completo"]),
            role_solicitado=r["role_solicitado"],
            status=r["status"],
            criado_em=str(r["criado_em"]),
        )
        for r in rows
    ]


@router.post("/solicitacoes/{solicitacao_id}/decidir")
def decidir_solicitacao(
    solicitacao_id: str,
    payload: DecidirSolicitacaoRequestSchema,
    request: Request,
    caller: Dict[str, Any] = Depends(require_roles("adm", "coordenador")),
    service: AuthService = Depends(get_auth_service),
):
    status = _executar(
        service.decidir_solicitacao, caller, solicitacao_id, payload.decisao, payload.senha_confirmacao,
        client_ip(request),
    )
    return {"ok": True, "status": status}


# ---------------------------------------------------------------------- #
# Gestão exclusiva ADM
# ---------------------------------------------------------------------- #
@router.get("/admin/usuarios", response_model=List[UsuarioGerenciavelSchema])
def listar_usuarios_gerenciaveis(
    _adm: Dict[str, Any] = Depends(require_adm_perfil),
    service: AuthService = Depends(get_auth_service),
):
    rows = _executar(service.listar_usuarios)
    return [
        UsuarioGerenciavelSchema(
            id=str(r["id"]),
            usuario=str(r["usuario"]),
            nome_completo=str(r["nome_completo"]),
            role=r["role"],
            ativo=bool(r["ativo"]),
            bloqueado=esta_conta_bloqueada(r.get("bloqueado_ate")),
            criado_em=str(r.get("criado_em", "")),
        )
        for r in rows
    ]


@router.post("/admin/usuarios", status_code=201)
def admin_criar_usuario(
    payload: AdminCriarUsuarioRequestSchema,
    request: Request,
    adm: Dict[str, Any] = Depends(require_adm_perfil),
    service: AuthService = Depends(get_auth_service),
):
    perfil = _executar(
        service.criar_usuario, adm, payload.nome_completo, payload.usuario, payload.role, payload.senha,
        payload.senha_confirmacao, client_ip(request),
    )
    return {"ok": True, "usuario": perfil}


@router.put("/admin/usuarios/{user_id}")
def admin_atualizar_usuario(
    user_id: str,
    payload: AdminAtualizarUsuarioRequestSchema,
    request: Request,
    adm: Dict[str, Any] = Depends(require_adm_perfil),
    service: AuthService = Depends(get_auth_service),
):
    perfil = _executar(
        service.atualizar_usuario, adm, user_id, payload.nome_completo, payload.role, payload.ativo,
        payload.nova_senha, payload.senha_confirmacao, client_ip(request),
    )
    return {"ok": True, "usuario": perfil}


@router.post("/admin/usuarios/{user_id}/deletar")
def admin_deletar_usuario(
    user_id: str,
    payload: AdminDeletarUsuarioRequestSchema,
    request: Request,
    adm: Dict[str, Any] = Depends(require_adm_perfil),
    service: AuthService = Depends(get_auth_service),
):
    usuario = _executar(service.deletar_usuario, adm, user_id, payload.senha_confirmacao, client_ip(request))
    return {"ok": True, "usuario": usuario}


@router.post("/admin/usuarios/{user_id}/reset-senha")
def admin_redefinir_senha_usuario(
    user_id: str,
    payload: AdminResetSenhaRequestSchema,
    request: Request,
    adm: Dict[str, Any] = Depends(require_adm_perfil),
    service: AuthService = Depends(get_auth_service),
):
    usuario = _executar(
        service.resetar_senha, adm, user_id, payload.nova_senha, payload.senha_confirmacao, client_ip(request)
    )
    return {"ok": True, "usuario": usuario}


@router.post("/admin/usuarios/{user_id}/desbloquear")
def admin_desbloquear_usuario(
    user_id: str,
    payload: AdminConfirmacaoRequestSchema,
    request: Request,
    adm: Dict[str, Any] = Depends(require_adm_perfil),
    service: AuthService = Depends(get_auth_service),
):
    usuario = _executar(service.desbloquear_usuario, adm, user_id, payload.senha_confirmacao, client_ip(request))
    return {"ok": True, "usuario": usuario}


@router.get("/admin/audit-logs", response_model=List[AuditLogItemSchema])
def admin_listar_audit_logs(
    limit: int = Query(default=100, ge=1, le=500),
    _adm: Dict[str, Any] = Depends(require_adm_perfil),
    service: AuthService = Depends(get_auth_service),
):
    rows = _executar(service.listar_audit_logs, limit)
    return [
        AuditLogItemSchema(
            id=str(r.get("id", "")),
            ator_id=str(r["ator_id"]) if r.get("ator_id") else None,
            acao=str(r.get("acao", "")),
            alvo=str(r["alvo"]) if r.get("alvo") else None,
            ip=str(r["ip"]) if r.get("ip") else None,
            detalhes=r.get("detalhes") or {},
            criado_em=str(r.get("criado_em", "")),
        )
        for r in rows
    ]
