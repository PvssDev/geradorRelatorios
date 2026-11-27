# -*- coding: utf-8 -*-
"""Middleware de cabeçalhos de segurança HTTP (OWASP)."""

from fastapi import FastAPI, Request

# A UI do Swagger carrega scripts de CDN; a CSP restritiva fica só nas rotas da API.
ROTAS_DOCUMENTACAO = ("/docs", "/redoc", "/openapi.json")
CSP_API = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"


def registrar_security_headers(app: FastAPI) -> None:
    @app.middleware("http")
    async def add_owasp_security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        path = request.url.path
        if not path.startswith(ROTAS_DOCUMENTACAO):
            response.headers["Content-Security-Policy"] = CSP_API
        if path.startswith("/api/auth"):
            response.headers["Cache-Control"] = "no-store"
        return response
