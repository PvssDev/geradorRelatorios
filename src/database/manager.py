import os
import json
import tempfile

DB_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_DB_DIR = os.path.join(tempfile.gettempdir(), "arpe_db_cache")

RESPONSAVEIS_FILE = os.path.join(DB_DIR, "responsaveis.json")
COORDENADORES_FILE = os.path.join(DB_DIR, "coordenadores.json")
CONTRATOS_FILE = os.path.join(DB_DIR, "contratos.json")
CUSTOM_NCS_FILE = os.path.join(DB_DIR, "custom_ncs.json")
CUSTOM_NCS_SOCICAM_FILE = os.path.join(DB_DIR, "custom_ncs_socicam.json")

_RUNTIME_CACHE: dict[str, list] = {}

DEFAULT_RESPONSAVEIS = [
    {
        "nome": "Alcides Vieira de Azevedo Bezerra",
        "matricula": "40672015/01",
        "funcao": "Analista de Regulação"
    },
    {
        "nome": "Enildo Manoel da Silva Júnior",
        "matricula": "1796500/02",
        "funcao": "Analista de Regulação"
    },
    {
        "nome": "Cícero Ronaldo Mendes de Andrade Júnior",
        "matricula": "3485510/02",
        "funcao": "Analista de Regulação"
    },
    {
        "nome": "Maria Fernanda da Silva Novaes",
        "matricula": "18471080/01",
        "funcao": "Auxiliar de Regulação"
    }
]

DEFAULT_COORDENADORES = [
    {
        "nome": "Maria Ângela Albuquerque de Freitas",
        "matricula": "209640/01",
        "funcao": "Coordenadora de Transportes e Rodovias"
    }
]

DEFAULT_CONTRATOS = [
    "1.041.080/08"
]

DEFAULT_CUSTOM_NCS = []
DEFAULT_CUSTOM_NCS_SOCICAM = []


def _read_json_with_fallback(primary_path: str, cache_key: str):
    if cache_key in _RUNTIME_CACHE:
        return [item.copy() if isinstance(item, dict) else item for item in _RUNTIME_CACHE[cache_key]]

    tmp_path = os.path.join(TMP_DB_DIR, os.path.basename(primary_path))
    for candidate in (tmp_path, primary_path):
        if os.path.exists(candidate):
            try:
                with open(candidate, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        _RUNTIME_CACHE[cache_key] = data
                        return data
            except Exception:
                continue
    return None


def _write_json_with_fallback(primary_path: str, cache_key: str, lista: list) -> bool:
    _RUNTIME_CACHE[cache_key] = [item.copy() if isinstance(item, dict) else item for item in lista]
    try:
        os.makedirs(DB_DIR, exist_ok=True)
        with open(primary_path, "w", encoding="utf-8") as f:
            json.dump(lista, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        try:
            os.makedirs(TMP_DB_DIR, exist_ok=True)
            tmp_path = os.path.join(TMP_DB_DIR, os.path.basename(primary_path))
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(lista, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False


# --- RESPONSÁVEIS ---
def carregar_responsaveis():
    """Carrega a lista de responsáveis do banco de dados local (JSON) ou cache em memória."""
    data = _read_json_with_fallback(RESPONSAVEIS_FILE, "responsaveis")
    if data is None:
        salvar_responsaveis(DEFAULT_RESPONSAVEIS)
        return DEFAULT_RESPONSAVEIS.copy()
    if data and isinstance(data[0], str):
        nova_lista = []
        for nome in data:
            match = next((d for d in DEFAULT_RESPONSAVEIS if d["nome"] == nome), None)
            if match:
                nova_lista.append(match)
            else:
                nova_lista.append({
                    "nome": nome,
                    "matricula": "xxxxxxx/xx",
                    "funcao": "Analista de Regulação"
                })
        salvar_responsaveis(nova_lista)
        return nova_lista
    return data


def salvar_responsaveis(lista):
    """Salva a lista de responsáveis no banco de dados local (JSON) com fallback serverless."""
    return _write_json_with_fallback(RESPONSAVEIS_FILE, "responsaveis", lista)


# --- COORDENADORES ---
def carregar_coordenadores():
    """Carrega a lista de coordenadores do banco de dados local (JSON) ou cache em memória."""
    data = _read_json_with_fallback(COORDENADORES_FILE, "coordenadores")
    if data is None:
        salvar_coordenadores(DEFAULT_COORDENADORES)
        return DEFAULT_COORDENADORES.copy()
    if data and isinstance(data[0], str):
        nova_lista = []
        for nome in data:
            match = next((d for d in DEFAULT_COORDENADORES if d["nome"] == nome), None)
            if match:
                nova_lista.append(match)
            else:
                nova_lista.append({
                    "nome": nome,
                    "matricula": "xxxxxx/xx",
                    "funcao": "Coordenador(a)"
                })
        salvar_coordenadores(nova_lista)
        return nova_lista
    return data


def salvar_coordenadores(lista):
    """Salva a lista de coordenadores no banco de dados local (JSON) com fallback serverless."""
    return _write_json_with_fallback(COORDENADORES_FILE, "coordenadores", lista)


# --- CONTRATOS ---
def carregar_contratos():
    """Carrega a lista de contratos do banco de dados local (JSON) ou cache em memória."""
    data = _read_json_with_fallback(CONTRATOS_FILE, "contratos")
    if data is None:
        salvar_contratos(DEFAULT_CONTRATOS)
        return DEFAULT_CONTRATOS.copy()
    return data


def salvar_contratos(lista):
    """Salva a lista de contratos no banco de dados local (JSON) com fallback serverless."""
    return _write_json_with_fallback(CONTRATOS_FILE, "contratos", lista)


# --- CUSTOM NCS ---
def carregar_custom_ncs():
    """Carrega a lista de não conformidades customizadas do banco de dados local (JSON)."""
    data = _read_json_with_fallback(CUSTOM_NCS_FILE, "custom_ncs")
    if data is None:
        salvar_custom_ncs(DEFAULT_CUSTOM_NCS)
        return DEFAULT_CUSTOM_NCS.copy()
    return data


def salvar_custom_ncs(lista):
    """Salva a lista de não conformidades customizadas no banco de dados local (JSON)."""
    return _write_json_with_fallback(CUSTOM_NCS_FILE, "custom_ncs", lista)


# --- CUSTOM NCS SOCICAM ---
def carregar_custom_ncs_socicam():
    """Carrega a lista de não conformidades customizadas da SOCICAM (JSON)."""
    data = _read_json_with_fallback(CUSTOM_NCS_SOCICAM_FILE, "custom_ncs_socicam")
    if data is None:
        salvar_custom_ncs_socicam(DEFAULT_CUSTOM_NCS_SOCICAM)
        return DEFAULT_CUSTOM_NCS_SOCICAM.copy()
    return data


def salvar_custom_ncs_socicam(lista):
    """Salva a lista de não conformidades customizadas da SOCICAM no banco de dados local (JSON)."""
    return _write_json_with_fallback(CUSTOM_NCS_SOCICAM_FILE, "custom_ncs_socicam", lista)
