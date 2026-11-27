# -*- coding: utf-8 -*-
"""Dependências FastAPI de autenticação e autorização (RBAC).

- `get_current_user`: aceita Bearer JWT (APK) ou Cookie HttpOnly (Web).
- Sessões por cookie em métodos mutáveis exigem `Origin` confiável (anti-CSRF).
- `require_roles(...)`: fábrica de guardas por perfil.
"""

from typing import Any, Callable, Dict, Optional

from fastapi import Cookie, Depends, Header, HTTPException, Request

from server.security_config import carregar_allowed_origins, origem_confiavel
from services.auth_service import AuthError, AuthService
from services.supabase_gateway import HttpSupabaseGateway, SupabaseGatewayError, get_supabase_gateway

ACCESS_COOKIE_NAME = "arpe_access_token"
REFRESH_COOKIE_NAME = "arpe_refresh_token"
METODOS_SEGUROS = {"GET", "HEAD", "OPTIONS"}


def get_auth_service(gateway: HttpSupabaseGateway = Depends(get_supabase_gateway)) -> AuthService:
    return AuthService(gateway)


def verificar_origem_confiavel(request: Request) -> None:
    """Proteção anti-CSRF / Request Injection em rotas mutáveis de Auth."""
    origin = request.headers.get("origin")
    if origin and not origem_confiavel(origin, request.headers.get("host"), carregar_allowed_origins()):
        raise HTTPException(status_code=403, detail="Origem da requisição não autorizada.")


def extract_bearer_or_cookie_token(
    request: Request,
    authorization: Optional[str] = Header(default=None),
    cookie_token: Optional[str] = Cookie(default=None, alias=ACCESS_COOKIE_NAME),
) -> str:
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
        if token:
            return token
    if cookie_token:
        if request.method.upper() not in METODOS_SEGUROS and not origem_confiavel(
            request.headers.get("origin"), request.headers.get("host"), carregar_allowed_origins()
        ):
            raise HTTPException(status_code=403, detail="Origem da requisição não autorizada.")
        return cookie_token.strip()
    raise HTTPException(status_code=401, detail="Autenticação obrigatória.")


def get_current_user(
    token: str = Depends(extract_bearer_or_cookie_token),
    service: AuthService = Depends(get_auth_service),
) -> Dict[str, Any]:
    try:
        return service.resolver_perfil_por_token(token)
    except AuthError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail)
    except SupabaseGatewayError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))


# Alias retrocompatível (usado por sync_router e testes existentes).
get_authenticated_perfil = get_current_user


def require_roles(*roles: str) -> Callable[..., Dict[str, Any]]:
    permitidos = set(roles)

    def _guard(caller: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        if caller.get("role") not in permitidos:
            raise HTTPException(status_code=403, detail="Perfil sem permissão para este recurso.")
        return caller

    return _guard


def require_adm_perfil(caller: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    if caller.get("role") != "adm":
        raise HTTPException(status_code=403, detail="Acesso restrito ao Administrador (ADM).")
    return caller
