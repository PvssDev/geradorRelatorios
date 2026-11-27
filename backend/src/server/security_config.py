# -*- coding: utf-8 -*-
"""Configuração de segurança HTTP compartilhada (CORS fechado + verificação de Origin)."""

import os
from typing import List, Optional
from urllib.parse import urlparse

DEFAULT_DEV_ORIGINS: List[str] = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8081",
    "http://127.0.0.1:8081",
    "http://localhost:19006",
]


def carregar_allowed_origins() -> List[str]:
    """Lê `ALLOWED_ORIGINS` (CSV) descartando '*'; sem variável, usa apenas origens de dev."""
    raw = os.environ.get("ALLOWED_ORIGINS", "").strip()
    if not raw:
        return list(DEFAULT_DEV_ORIGINS)
    return [o.strip().rstrip("/") for o in raw.split(",") if o.strip() and o.strip() != "*"]


def origem_confiavel(origin: Optional[str], host: Optional[str], allowed: List[str]) -> bool:
    """Anti-CSRF para sessões por cookie: aceita origem da lista ou mesma origem do host."""
    if not origin:
        return True  # Navegadores sempre enviam Origin em POST cross-site; ausência = cliente não-browser.
    origem = origin.strip().rstrip("/")
    if origem in allowed:
        return True
    netloc = urlparse(origem).netloc
    return bool(host) and netloc == host
