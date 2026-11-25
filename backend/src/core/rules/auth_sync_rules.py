# -*- coding: utf-8 -*-
"""Regras puras de Domínio para Autenticação Sem E-mail, Criptografia Temporária,
Account Lockout, Presigned Upload e Paridade dos 6 Estados Regulatórios.

Zero dependências de FastAPI, HTTP ou banco de dados (SOLID - DIP / SRP).
"""

import base64
import hashlib
import hmac
import os
import re
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

USUARIO_REGEX = re.compile(r"^[a-z0-9._-]{3,32}$")
VISTORIA_ID_SAFE_REGEX = re.compile(r"^[a-zA-Z0-9._-]{3,80}$")
DOMINIO_INTERNO = "arpe.internal"
SENHA_DESCARTADA_SENTINEL = "REDACTED"

MAX_TENTATIVAS_LOGIN = 5
LOCKOUT_MINUTOS = 15
PRESIGN_EXPIRES_SECONDS = 600
MAX_FOTO_KB = 500


def normalizar_usuario(raw: str) -> str:
    return (raw or "").strip().lower()


def validar_formato_usuario(usuario: str) -> bool:
    return bool(USUARIO_REGEX.match(normalizar_usuario(usuario)))


def montar_email_sintetico(usuario: str) -> str:
    return f"{normalizar_usuario(usuario)}@{DOMINIO_INTERNO}"


def validar_forca_senha(senha: str, role: str = "analista") -> Optional[str]:
    min_len = 12 if role == "adm" else 10
    if len(senha or "") < min_len:
        return f"A senha deve ter no mínimo {min_len} caracteres."
    if not re.search(r"[A-Z]", senha) or not re.search(r"[a-z]", senha) or not re.search(r"[0-9]", senha):
        return "Use letras maiúsculas, minúsculas e ao menos um número."
    if role == "adm" and not re.search(r"[^A-Za-z0-9]", senha):
        return "Contas ADM exigem ao menos um caractere especial."
    return None


def pode_aprovar_acessos(role: str) -> bool:
    return role in ("adm", "coordenador")


def _agora_utc(agora: Optional[datetime] = None) -> datetime:
    if agora is None:
        return datetime.now(timezone.utc)
    if agora.tzinfo is None:
        return agora.replace(tzinfo=timezone.utc)
    return agora.astimezone(timezone.utc)


def esta_conta_bloqueada(bloqueado_ate_iso: Optional[str], agora: Optional[datetime] = None) -> bool:
    if not bloqueado_ate_iso:
        return False
    try:
        normalized = bloqueado_ate_iso.replace("Z", "+00:00")
        dt_bloqueio = datetime.fromisoformat(normalized)
        if dt_bloqueio.tzinfo is None:
            dt_bloqueio = dt_bloqueio.replace(tzinfo=timezone.utc)
        return dt_bloqueio > _agora_utc(agora)
    except ValueError:
        return False


def calcular_estado_pos_falha_login(
    tentativas_atuais: int,
    agora: Optional[datetime] = None,
) -> Tuple[int, Optional[str], bool]:
    """Retorna (novas_tentativas, bloqueado_ate_iso, bloqueou_agora)."""
    novas = max(0, int(tentativas_atuais)) + 1
    if novas >= MAX_TENTATIVAS_LOGIN:
        ate = (_agora_utc(agora) + timedelta(minutes=LOCKOUT_MINUTOS)).isoformat()
        return novas, ate, True
    return novas, None, False


def _derivar_chaves(secret: str, salt: bytes) -> Tuple[bytes, bytes]:
    if not secret or len(secret) < 16:
        raise ValueError("Chave secreta do servidor ausente ou curta demais para criptografia.")
    material = hashlib.pbkdf2_hmac("sha256", secret.encode("utf-8"), salt, 100_000, dklen=64)
    return material[:32], material[32:]


def _keystream(enc_key: bytes, nonce: bytes, length: int) -> bytes:
    out = bytearray()
    counter = 0
    while len(out) < length:
        block = hmac.new(
            enc_key,
            nonce + counter.to_bytes(4, "big"),
            hashlib.sha256,
        ).digest()
        out.extend(block)
        counter += 1
    return bytes(out[:length])


def criptografar_senha_temporaria(senha: str, secret: str) -> str:
    """Encrypt-then-MAC (PBKDF2-SHA256 + Stream HMAC-SHA256) sem dependências nativas."""
    plaintext = senha.encode("utf-8")
    salt = secrets.token_bytes(16)
    nonce = secrets.token_bytes(16)
    enc_key, mac_key = _derivar_chaves(secret, salt)
    stream = _keystream(enc_key, nonce, len(plaintext))
    ciphertext = bytes(a ^ b for a, b in zip(plaintext, stream))
    tag = hmac.new(mac_key, b"ENCv1" + salt + nonce + ciphertext, hashlib.sha256).digest()
    blob = salt + nonce + tag + ciphertext
    return "ENCv1:" + base64.urlsafe_b64encode(blob).decode("ascii")


def descriptografar_senha_temporaria(token: str, secret: str) -> str:
    if not token or not token.startswith("ENCv1:"):
        raise ValueError("Formato de credencial temporária inválido ou já descartado.")
    raw = base64.urlsafe_b64decode(token[6:].encode("ascii"))
    if len(raw) < 64:
        raise ValueError("Credencial temporária corrompida.")
    salt = raw[:16]
    nonce = raw[16:32]
    tag = raw[32:64]
    ciphertext = raw[64:]
    enc_key, mac_key = _derivar_chaves(secret, salt)
    expected_tag = hmac.new(mac_key, b"ENCv1" + salt + nonce + ciphertext, hashlib.sha256).digest()
    if not hmac.compare_digest(tag, expected_tag):
        raise ValueError("Falha de integridade na credencial temporária.")
    stream = _keystream(enc_key, nonce, len(ciphertext))
    plaintext = bytes(a ^ b for a, b in zip(ciphertext, stream))
    return plaintext.decode("utf-8")


def validar_presign_upload(nome_arquivo: str, content_type: str, tamanho_kb: int) -> Optional[str]:
    ext = os.path.splitext((nome_arquivo or "").strip())[1].lower()
    if ext not in (".jpg", ".jpeg"):
        return "Apenas imagens JPEG (.jpg / .jpeg) são permitidas."
    if (content_type or "").strip().lower() != "image/jpeg":
        return "Content-Type inválido: esperado image/jpeg."
    if tamanho_kb <= 0 or tamanho_kb > MAX_FOTO_KB:
        return f"Tamanho da foto inválido ({tamanho_kb} KB). Máximo permitido: {MAX_FOTO_KB} KB."
    return None


def gerar_storage_key_segura(vistoria_id: str) -> str:
    vid = (vistoria_id or "").strip()
    if not VISTORIA_ID_SAFE_REGEX.match(vid):
        raise ValueError("Identificador de vistoria inválido para caminho de armazenamento.")
    return f"{vid}/{uuid.uuid4().hex}.jpg"


def _extrair_itens_inspecao(payload_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    itens: List[Dict[str, Any]] = []
    for chave in ("ocorrencias", "registros_nc", "achados"):
        val = payload_json.get(chave)
        if isinstance(val, list):
            itens.extend(item for item in val if isinstance(item, dict))
    return itens


def validar_payload_vistoria_seis_estados(
    concessao: str,
    modalidade: str,
    payload_json: Dict[str, Any],
) -> Optional[str]:
    if concessao not in ("CRA", "CRC", "SOCICAM"):
        return "Concessão inválida."
    if modalidade not in ("Fiscalização", "Monitoramento"):
        return "Modalidade inválida."
    if not isinstance(payload_json, dict) or not payload_json:
        return "O payload JSON da vistoria não pode estar vazio."

    if concessao == "SOCICAM":
        campos_proibidos = ("pista", "Pista", "faixa", "Faixa", "direcao_faixa", "Direção (faixa)")
        for campo in campos_proibidos:
            if str(payload_json.get(campo, "")).strip():
                return "Violação de domínio SOCICAM: terminais rodoviários não possuem Pista ou Faixa."
        for item in _extrair_itens_inspecao(payload_json):
            for campo in campos_proibidos:
                if str(item.get(campo, "")).strip():
                    return "Violação de domínio SOCICAM: ocorrências não podem conter Pista ou Faixa."
    return None


def agregar_telemetria_acessos(
    logs: List[Dict[str, Any]],
    total_equipe_ativa: int,
    solicitacoes_pendentes: int,
    agora: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Agrega acessos reais Mobile vs Web nos últimos 7 dias a partir de audit_logs (sem PII)."""
    now_utc = _agora_utc(agora)
    dias_keys: List[Tuple[str, str]] = []
    buckets: Dict[str, Dict[str, int]] = {}
    for offset in range(6, -1, -1):
        dt = now_utc - timedelta(days=offset)
        iso_day = dt.strftime("%Y-%m-%d")
        label = dt.strftime("%d/%m")
        dias_keys.append((iso_day, label))
        buckets[iso_day] = {"mobile": 0, "web": 0}

    logins_mobile = 0
    logins_web = 0
    alertas = 0
    atividade_recente: List[Dict[str, str]] = []

    for row in logs:
        acao = str(row.get("acao") or "")
        alvo = str(row.get("alvo") or "sistema").split("@")[0]
        criado_em = str(row.get("criado_em") or "")
        detalhes = row.get("detalhes") if isinstance(row.get("detalhes"), dict) else {}
        canal_raw = str(detalhes.get("client_type") or "").lower()
        canal = canal_raw if canal_raw in ("mobile", "web") else "sistema"
        day_key = criado_em[:10]

        if acao == "LOGIN_SUCESSO":
            if canal == "web":
                logins_web += 1
                if day_key in buckets:
                    buckets[day_key]["web"] += 1
            else:
                canal = "mobile"
                logins_mobile += 1
                if day_key in buckets:
                    buckets[day_key]["mobile"] += 1
        elif "FALHA" in acao or "LOCKOUT" in acao or "BLOQUEADO" in acao:
            alertas += 1

        if len(atividade_recente) < 6:
            status = "alerta" if ("FALHA" in acao or "LOCKOUT" in acao or "BLOQUEADO" in acao) else "ok"
            atividade_recente.append(
                {
                    "usuario": alvo,
                    "acao": acao,
                    "canal": canal,
                    "status": status,
                    "criado_em": criado_em,
                }
            )

    serie_diaria = [
        {"dia": label, "mobile": buckets[iso_day]["mobile"], "web": buckets[iso_day]["web"]}
        for iso_day, label in dias_keys
    ]

    return {
        "equipe_ativa": max(0, int(total_equipe_ativa)),
        "solicitacoes_pendentes": max(0, int(solicitacoes_pendentes)),
        "logins_mobile_7d": logins_mobile,
        "logins_web_7d": logins_web,
        "alertas_7d": alertas,
        "serie_diaria": serie_diaria,
        "atividade_recente": atividade_recente,
    }
