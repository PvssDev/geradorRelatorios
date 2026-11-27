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


def resolver_nome_unico_vistoria(nome_desejado: str, nomes_existentes: List[str]) -> str:
    """Resolve conflitos de nome na nuvem aplicando sufixo incremental (1), (2)..."""
    base = (nome_desejado or "").strip() or "VISTORIA"
    ocupados = {n.strip().casefold() for n in nomes_existentes if n and n.strip()}
    if base.casefold() not in ocupados:
        return base

    indice = 1
    while True:
        candidato = f"{base} ({indice})"
        if candidato.casefold() not in ocupados:
            return candidato
        indice += 1


def extrair_data_vistoria_iso(
    payload_json: Dict[str, Any],
    fallback_iso: Optional[str] = None,
) -> str:
    """Converte data da vistoria (DD/MM/YYYY ou YYYY-MM-DD) para YYYY-MM-DD."""
    fisc = payload_json.get("fiscalizacao") if isinstance(payload_json, dict) else None
    candidatos = []
    if isinstance(fisc, dict):
        candidatos.extend([fisc.get("data"), fisc.get("Data"), fisc.get("periodo")])
    if isinstance(payload_json, dict):
        candidatos.extend([payload_json.get("data"), payload_json.get("data_vistoria")])

    for raw in candidatos:
        texto = str(raw or "").strip()
        if not texto:
            continue
        m_br = re.search(r"\b(\d{2})/(\d{2})/(\d{4})\b", texto)
        if m_br:
            return f"{m_br.group(3)}-{m_br.group(2)}-{m_br.group(1)}"
        m_iso = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", texto)
        if m_iso:
            return m_iso.group(1)

    if fallback_iso:
        m_fb = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", str(fallback_iso))
        if m_fb:
            return m_fb.group(1)
    return datetime.now(timezone.utc).date().isoformat()


def normalizar_situacao_historico(situacao_raw: Optional[str], modalidade: str) -> str:
    """Mapeia situação para o enum SQL de historico_achados."""
    val = (situacao_raw or "").strip().casefold()
    if val in ("sanada", "saneada", "resolvida"):
        return "Sanada"
    if "parcial" in val:
        return "Parcialmente Sanada"
    if val in ("pendente", "nao sanada", "não sanada"):
        return "Pendente"
    if modalidade == "Fiscalização" and not val:
        return "Nova"
    return "Nova" if val == "nova" else "Pendente"


def extrair_registros_historico_achados(
    id_vistoria: str,
    concessao: str,
    modalidade: str,
    payload_json: Dict[str, Any],
    fallback_iso: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Extrai registros analíticos anônimos (zero fotos, zero PII) para historico_achados."""
    data_iso = extrair_data_vistoria_iso(payload_json, fallback_iso=fallback_iso)
    fisc = payload_json.get("fiscalizacao") if isinstance(payload_json, dict) else None
    local_base = ""
    if isinstance(fisc, dict):
        local_base = str(fisc.get("local") or fisc.get("Local") or fisc.get("terminal") or "").strip()
    if not local_base and isinstance(payload_json, dict):
        local_base = str(payload_json.get("local") or payload_json.get("terminal") or "").strip()

    itens = _extrair_itens_inspecao(payload_json)
    registros: List[Dict[str, Any]] = []
    for item in itens:
        tipo_raw = str(item.get("tipoAchado") or item.get("tipo") or item.get("Tipo") or "NC").strip().upper()
        tipo_achado = "PA" if tipo_raw == "PA" else "NC"

        categoria = str(
            item.get("constatacao")
            or item.get("categoria")
            or item.get("sigla")
            or item.get("identificacao")
            or item.get("Identificação")
            or "Não classificada"
        ).strip()[:120]

        local_item = str(
            item.get("setorPredial")
            or item.get("trecho")
            or item.get("terminal")
            or item.get("pista")
            or local_base
            or "Não informado"
        ).strip()[:140]

        situacao_raw = item.get("situacao") or item.get("Situação")
        situacao = normalizar_situacao_historico(
            str(situacao_raw) if situacao_raw is not None else None,
            modalidade,
        )

        registros.append(
            {
                "id_vistoria": id_vistoria,
                "concessao": concessao,
                "modalidade": modalidade,
                "data_vistoria": data_iso,
                "local_ou_trecho": local_item,
                "tipo_achado": tipo_achado,
                "categoria_nc": categoria,
                "situacao": situacao,
            }
        )
    return registros


def agregar_resumo_historico(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Agrega métricas para gráficos do Painel Web sem expor dados individuais/PII."""
    total = len(rows)
    total_ncs = 0
    total_pas = 0
    sanadas = 0
    parciais = 0
    pendentes = 0
    novas = 0

    por_mes: Dict[str, Dict[str, Any]] = {}
    por_categoria: Dict[str, int] = {}
    por_concessao: Dict[str, int] = {"CRA": 0, "CRC": 0, "SOCICAM": 0}

    for r in rows:
        tipo = str(r.get("tipo_achado", "NC")).upper()
        if tipo == "PA":
            total_pas += 1
        else:
            total_ncs += 1

        sit = str(r.get("situacao", "Pendente"))
        if sit == "Sanada":
            sanadas += 1
        elif sit == "Parcialmente Sanada":
            parciais += 1
        elif sit == "Nova":
            novas += 1
        else:
            pendentes += 1

        mes = str(r.get("data_vistoria", ""))[:7] or "0000-00"
        bucket = por_mes.setdefault(
            mes,
            {"mes": mes, "ncs": 0, "pas": 0, "sanadas": 0, "pendentes": 0},
        )
        if tipo == "PA":
            bucket["pas"] += 1
        else:
            bucket["ncs"] += 1
        if sit == "Sanada":
            bucket["sanadas"] += 1
        elif sit in ("Pendente", "Parcialmente Sanada"):
            bucket["pendentes"] += 1

        cat = str(r.get("categoria_nc") or "Não classificada").strip()
        por_categoria[cat] = por_categoria.get(cat, 0) + 1

        conc = str(r.get("concessao") or "")
        if conc in por_concessao:
            por_concessao[conc] += 1

    base_saneamento = sanadas + parciais + pendentes
    taxa_saneamento = round((sanadas / base_saneamento) * 100, 1) if base_saneamento > 0 else 0.0

    serie_mensal = [por_mes[k] for k in sorted(por_mes.keys())]
    top_categorias = [
        {"categoria": cat, "quantidade": qtd}
        for cat, qtd in sorted(por_categoria.items(), key=lambda x: (-x[1], x[0]))[:5]
    ]

    return {
        "totais": {
            "total_achados": total,
            "total_ncs": total_ncs,
            "total_pas": total_pas,
            "sanadas": sanadas,
            "parcialmente_sanadas": parciais,
            "pendentes": pendentes,
            "novas": novas,
            "taxa_saneamento_pct": taxa_saneamento,
        },
        "serie_mensal": serie_mensal,
        "top_categorias": top_categorias,
        "por_concessao": por_concessao,
    }

