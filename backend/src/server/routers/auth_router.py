# -*- coding: utf-8 -*-
"""Router FastAPI de Autenticação Sem E-mail, Lockout, Cookies HttpOnly e
Aprovação Individual de Acessos (ADM ou Coordenador).
"""

import os
import time
from collections import defaultdict, deque
from typing import Any, Deque, Dict, List, Optional

from fastapi import APIRouter, Cookie, Depends, Header, HTTPException, Request, Response

from core.rules.auth_sync_rules import (
    calcular_estado_pos_falha_login,
    criptografar_senha_temporaria,
    descriptografar_senha_temporaria,
    esta_conta_bloqueada,
    montar_email_sintetico,
    normalizar_usuario,
    pode_aprovar_acessos,
    validar_forca_senha,
    validar_formato_usuario,
)
from server.auth_sync_schemas import (
    AdminResetSenhaRequestSchema,
    DecidirSolicitacaoRequestSchema,
    LoginRequestSchema,
    PerfilPublicoSchema,
    SolicitacaoItemResponseSchema,
    SolicitarAcessoRequestSchema,
    UsuarioGerenciavelSchema,
)
from services.supabase_gateway import HttpSupabaseGateway, SupabaseGatewayError, get_supabase_gateway

router = APIRouter(prefix="/api/auth", tags=["auth"])

GENERIC_AUTH_ERROR = "Usuário ou senha inválidos."
ACCESS_COOKIE_NAME = "arpe_access_token"
REFRESH_COOKIE_NAME = "arpe_refresh_token"
IP_RATE_WINDOW_SECONDS = 60.0
IP_RATE_MAX_REQUESTS = 20

_ip_buckets: Dict[str, Deque[float]] = defaultdict(deque)


def reset_rate_limiter() -> None:
    _ip_buckets.clear()


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    if forwarded:
        return forwarded
    return request.client.host if request.client else "unknown"


def _enforce_ip_rate_limit(ip: str) -> None:
    now = time.monotonic()
    bucket = _ip_buckets[ip]
    while bucket and (now - bucket[0]) > IP_RATE_WINDOW_SECONDS:
        bucket.popleft()
    if len(bucket) >= IP_RATE_MAX_REQUESTS:
        raise HTTPException(
            status_code=429,
            detail="Muitas tentativas deste endereço IP. Aguarde 1 minuto.",
        )
    bucket.append(now)


def _serializar_perfil_publico(row: Dict[str, Any]) -> Dict[str, Any]:
    return PerfilPublicoSchema(
        id=str(row["id"]),
        usuario=str(row["usuario"]),
        nome_completo=str(row["nome_completo"]),
        role=row["role"],
        ativo=bool(row["ativo"]),
    ).model_dump()


def extract_bearer_or_cookie_token(
    authorization: Optional[str] = Header(default=None),
    cookie_token: Optional[str] = Cookie(default=None, alias=ACCESS_COOKIE_NAME),
) -> str:
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
        if token:
            return token
    if cookie_token:
        return cookie_token.strip()
    raise HTTPException(status_code=401, detail="Autenticação obrigatória.")


def get_authenticated_perfil(
    token: str = Depends(extract_bearer_or_cookie_token),
    gateway: HttpSupabaseGateway = Depends(get_supabase_gateway),
) -> Dict[str, Any]:
    try:
        user_id = gateway.get_user_id_from_token(token)
        if not user_id:
            raise HTTPException(status_code=401, detail="Sessão inválida ou expirada.")
        perfil = gateway.get_perfil_by_id(user_id)
        if not perfil or not perfil.get("ativo"):
            raise HTTPException(status_code=403, detail="Conta inativa ou sem perfil corporativo.")
        return perfil
    except SupabaseGatewayError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))


@router.post("/login")
def login_corporativo(
    payload: LoginRequestSchema,
    request: Request,
    response: Response,
    gateway: HttpSupabaseGateway = Depends(get_supabase_gateway),
):
    ip = _client_ip(request)
    _enforce_ip_rate_limit(ip)

    usuario = normalizar_usuario(payload.usuario)
    if not validar_formato_usuario(usuario):
        raise HTTPException(status_code=401, detail=GENERIC_AUTH_ERROR)

    try:
        perfil = gateway.get_perfil_by_usuario(usuario)
        if perfil and esta_conta_bloqueada(perfil.get("bloqueado_ate")):
            gateway.insert_audit_log(
                ator_id=perfil["id"],
                acao="LOGIN_BLOQUEADO_TENTATIVA",
                alvo=usuario,
                ip=ip,
            )
            raise HTTPException(
                status_code=429,
                detail="Conta temporariamente bloqueada por excesso de tentativas. Aguarde 15 minutos.",
            )

        token_data = gateway.sign_in_password(montar_email_sintetico(usuario), payload.senha)
        if not token_data:
            if perfil:
                atuais = int(perfil.get("tentativas_falhas") or 0)
                novas, bloqueado_ate, bloqueou_agora = calcular_estado_pos_falha_login(atuais)
                gateway.update_perfil_lockout(perfil["id"], novas, bloqueado_ate)
                gateway.insert_audit_log(
                    ator_id=perfil["id"],
                    acao="LOGIN_LOCKOUT" if bloqueou_agora else "LOGIN_FALHA",
                    alvo=usuario,
                    ip=ip,
                    detalhes={"tentativas_falhas": novas},
                )
                if bloqueou_agora:
                    raise HTTPException(
                        status_code=429,
                        detail="Conta bloqueada por 15 minutos após 5 tentativas inválidas.",
                    )
            else:
                gateway.insert_audit_log(ator_id=None, acao="LOGIN_FALHA_USUARIO_INEXISTENTE", alvo=usuario, ip=ip)
            raise HTTPException(status_code=401, detail=GENERIC_AUTH_ERROR)

        if not perfil:
            user_id = (token_data.get("user") or {}).get("id")
            if user_id:
                perfil = gateway.get_perfil_by_id(str(user_id))

        if not perfil or not perfil.get("ativo"):
            raise HTTPException(status_code=403, detail="Conta inativa ou sem perfil corporativo.")

        if int(perfil.get("tentativas_falhas") or 0) > 0 or perfil.get("bloqueado_ate"):
            gateway.update_perfil_lockout(perfil["id"], 0, None)

        gateway.insert_audit_log(
            ator_id=perfil["id"],
            acao="LOGIN_SUCESSO",
            alvo=usuario,
            ip=ip,
            detalhes={"client_type": payload.client_type},
        )

        access_token = str(token_data.get("access_token") or "")
        refresh_token = str(token_data.get("refresh_token") or "")
        perfil_publico = _serializar_perfil_publico(perfil)

        if payload.client_type == "web":
            is_secure = os.environ.get("VERCEL", "") == "1" or request.url.scheme == "https"
            response.set_cookie(
                key=ACCESS_COOKIE_NAME,
                value=access_token,
                httponly=True,
                secure=is_secure,
                samesite="strict",
                max_age=900,
                path="/",
            )
            response.set_cookie(
                key=REFRESH_COOKIE_NAME,
                value=refresh_token,
                httponly=True,
                secure=is_secure,
                samesite="strict",
                max_age=604800,
                path="/api/auth",
            )
            return {"perfil": perfil_publico}

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "perfil": perfil_publico,
        }
    except SupabaseGatewayError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))


@router.post("/logout")
def logout_corporativo(response: Response):
    response.delete_cookie(ACCESS_COOKIE_NAME, path="/")
    response.delete_cookie(REFRESH_COOKIE_NAME, path="/api/auth")
    return {"ok": True}


@router.post("/solicitar-acesso", status_code=201)
def solicitar_acesso(
    payload: SolicitarAcessoRequestSchema,
    request: Request,
    gateway: HttpSupabaseGateway = Depends(get_supabase_gateway),
):
    ip = _client_ip(request)
    _enforce_ip_rate_limit(ip)

    nome = payload.nome_completo.strip()
    usuario = normalizar_usuario(payload.usuario)
    if len(nome) < 3:
        raise HTTPException(status_code=422, detail="Informe o nome completo.")
    if not validar_formato_usuario(usuario):
        raise HTTPException(
            status_code=422,
            detail="Usuário deve ter 3 a 32 caracteres (letras minúsculas, números, . _ -).",
        )
    erro_senha = validar_forca_senha(payload.senha, role=payload.role_solicitado)
    if erro_senha:
        raise HTTPException(status_code=422, detail=erro_senha)

    try:
        if gateway.get_perfil_by_usuario(usuario):
            raise HTTPException(status_code=409, detail="Este nome de usuário já está em uso.")
        existente = gateway.get_solicitacao_by_usuario(usuario)
        if existente and existente.get("status") in ("pendente", "aprovada"):
            raise HTTPException(status_code=409, detail="Já existe uma solicitação ativa para este usuário.")

        encrypted = criptografar_senha_temporaria(payload.senha, gateway.get_temp_crypto_secret())
        created = gateway.insert_solicitacao(
            usuario=usuario,
            nome_completo=nome,
            role_solicitado=payload.role_solicitado,
            senha_hash_temp=encrypted,
        )
        gateway.insert_audit_log(
            ator_id=None,
            acao="SOLICITACAO_ACESSO_CRIADA",
            alvo=usuario,
            ip=ip,
            detalhes={"role_solicitado": payload.role_solicitado},
        )
        return {"ok": True, "id": created.get("id")}
    except SupabaseGatewayError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))


@router.get("/solicitacoes", response_model=List[SolicitacaoItemResponseSchema])
def listar_solicitacoes(
    caller: Dict[str, Any] = Depends(get_authenticated_perfil),
    gateway: HttpSupabaseGateway = Depends(get_supabase_gateway),
):
    if not pode_aprovar_acessos(caller["role"]):
        raise HTTPException(status_code=403, detail="Apenas ADM ou Coordenador podem visualizar solicitações.")
    try:
        rows = gateway.list_solicitacoes_pendentes()
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
    except SupabaseGatewayError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))


@router.post("/solicitacoes/{solicitacao_id}/decidir")
def decidir_solicitacao(
    solicitacao_id: str,
    payload: DecidirSolicitacaoRequestSchema,
    request: Request,
    caller: Dict[str, Any] = Depends(get_authenticated_perfil),
    gateway: HttpSupabaseGateway = Depends(get_supabase_gateway),
):
    if not pode_aprovar_acessos(caller["role"]):
        raise HTTPException(status_code=403, detail="Apenas ADM ou Coordenador podem decidir solicitações.")

    ip = _client_ip(request)
    try:
        if caller["role"] == "adm":
            if not payload.senha_confirmacao:
                raise HTTPException(
                    status_code=403,
                    detail="Contas ADM exigem reconfirmação de senha para aprovar ou rejeitar acessos.",
                )
            reauth = gateway.sign_in_password(
                montar_email_sintetico(caller["usuario"]),
                payload.senha_confirmacao,
            )
            if not reauth:
                gateway.insert_audit_log(
                    ator_id=caller["id"],
                    acao="ADM_RECONFIRMACAO_SENHA_FALHA",
                    alvo=solicitacao_id,
                    ip=ip,
                )
                raise HTTPException(status_code=401, detail="Senha de confirmação do ADM incorreta.")

        sol = gateway.get_solicitacao_by_id(solicitacao_id)
        if not sol:
            raise HTTPException(status_code=404, detail="Solicitação não encontrada.")
        if sol.get("status") != "pendente":
            raise HTTPException(status_code=409, detail="Esta solicitação já foi decidida.")

        role_solicitado = str(sol["role_solicitado"])
        if role_solicitado not in ("analista", "coordenador"):
            raise HTTPException(status_code=403, detail="Perfil solicitado inválido.")

        if payload.decisao == "aprovada":
            senha_plana = descriptografar_senha_temporaria(
                str(sol["senha_hash_temp"]),
                gateway.get_temp_crypto_secret(),
            )
            novo_uid = gateway.admin_create_user(
                montar_email_sintetico(str(sol["usuario"])),
                senha_plana,
            )
            gateway.insert_perfil(
                user_id=novo_uid,
                usuario=str(sol["usuario"]),
                nome_completo=str(sol["nome_completo"]),
                role=role_solicitado,
            )

        gateway.finalize_solicitacao(
            sol_id=solicitacao_id,
            status=payload.decisao,
            decidido_por=str(caller["id"]),
        )
        gateway.insert_audit_log(
            ator_id=str(caller["id"]),
            acao="SOLICITACAO_APROVADA" if payload.decisao == "aprovada" else "SOLICITACAO_REJEITADA",
            alvo=str(sol["usuario"]),
            ip=ip,
            detalhes={"solicitacao_id": solicitacao_id, "role": role_solicitado},
        )
        return {"ok": True, "status": payload.decisao}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except SupabaseGatewayError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))


def require_adm_perfil(
    caller: Dict[str, Any] = Depends(get_authenticated_perfil),
) -> Dict[str, Any]:
    if caller.get("role") != "adm":
        raise HTTPException(status_code=403, detail="Acesso restrito ao Administrador (ADM).")
    return caller


@router.get("/admin/usuarios", response_model=List[UsuarioGerenciavelSchema])
def listar_usuarios_gerenciaveis(
    _adm: Dict[str, Any] = Depends(require_adm_perfil),
    gateway: HttpSupabaseGateway = Depends(get_supabase_gateway),
):
    try:
        rows = gateway.list_perfis_gerenciaveis()
        return [
            UsuarioGerenciavelSchema(
                id=str(r["id"]),
                usuario=str(r["usuario"]),
                nome_completo=str(r["nome_completo"]),
                role=r["role"],
                ativo=bool(r["ativo"]),
                criado_em=str(r.get("criado_em", "")),
            )
            for r in rows
        ]
    except SupabaseGatewayError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))


@router.post("/admin/usuarios/{user_id}/reset-senha")
def admin_redefinir_senha_usuario(
    user_id: str,
    payload: AdminResetSenhaRequestSchema,
    request: Request,
    adm: Dict[str, Any] = Depends(require_adm_perfil),
    gateway: HttpSupabaseGateway = Depends(get_supabase_gateway),
):
    ip = _client_ip(request)
    try:
        reauth = gateway.sign_in_password(
            montar_email_sintetico(str(adm["usuario"])),
            payload.senha_confirmacao,
        )
        if not reauth:
            gateway.insert_audit_log(
                ator_id=str(adm["id"]),
                acao="ADM_RESET_SENHA_REAUTH_FALHA",
                alvo=user_id,
                ip=ip,
            )
            raise HTTPException(status_code=401, detail="Senha de confirmação do ADM incorreta.")

        alvo = gateway.get_perfil_by_id(user_id)
        if not alvo:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")
        if alvo.get("role") == "adm":
            raise HTTPException(
                status_code=403,
                detail="Contas ADM não podem ter senha alterada por esta rota.",
            )

        erro_senha = validar_forca_senha(payload.nova_senha, role=str(alvo["role"]))
        if erro_senha:
            raise HTTPException(status_code=422, detail=erro_senha)

        gateway.admin_update_user_password(user_id, payload.nova_senha)
        gateway.update_perfil_lockout(user_id, 0, None)
        gateway.insert_audit_log(
            ator_id=str(adm["id"]),
            acao="ADM_RESET_SENHA_USUARIO",
            alvo=str(alvo["usuario"]),
            ip=ip,
            detalhes={"role_alvo": alvo["role"]},
        )
        return {"ok": True, "usuario": alvo["usuario"]}
    except SupabaseGatewayError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))
