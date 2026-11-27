# -*- coding: utf-8 -*-
"""Rate limit em memória por IP (janela deslizante) para rotas públicas de Auth."""

import time
from collections import defaultdict, deque
from typing import Deque, Dict

from fastapi import HTTPException, Request

IP_RATE_WINDOW_SECONDS = 60.0
IP_RATE_MAX_REQUESTS = 20

_ip_buckets: Dict[str, Deque[float]] = defaultdict(deque)


def reset_rate_limiter() -> None:
    _ip_buckets.clear()


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    if forwarded:
        return forwarded
    return request.client.host if request.client else "unknown"


def enforce_ip_rate_limit(ip: str) -> None:
    now = time.monotonic()
    bucket = _ip_buckets[ip]
    while bucket and (now - bucket[0]) > IP_RATE_WINDOW_SECONDS:
        bucket.popleft()
    if len(bucket) >= IP_RATE_MAX_REQUESTS:
        raise HTTPException(status_code=429, detail="Muitas tentativas deste endereço IP. Aguarde 1 minuto.")
    bucket.append(now)
