import os
import json

DB_DIR = os.path.dirname(os.path.abspath(__file__))
RESPONSAVEIS_FILE = os.path.join(DB_DIR, "responsaveis.json")
COORDENADORES_FILE = os.path.join(DB_DIR, "coordenadores.json")
CONTRATOS_FILE = os.path.join(DB_DIR, "contratos.json")

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
    "Maria Ângela Albuquerque de Freitas"
]

DEFAULT_CONTRATOS = [
    "1.041.080/08"
]

# --- RESPONSÁVEIS ---
def carregar_responsaveis():
    """Carrega a lista de responsáveis do banco de dados local (JSON)."""
    if not os.path.exists(RESPONSAVEIS_FILE):
        salvar_responsaveis(DEFAULT_RESPONSAVEIS)
        return DEFAULT_RESPONSAVEIS.copy()
    try:
        with open(RESPONSAVEIS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                # Se for lista de strings (versão antiga), converte para a nova estrutura de dicionários
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
            return DEFAULT_RESPONSAVEIS.copy()
    except Exception:
        return DEFAULT_RESPONSAVEIS.copy()

def salvar_responsaveis(lista):
    """Salva a lista de responsáveis no banco de dados local (JSON)."""
    try:
        os.makedirs(DB_DIR, exist_ok=True)
        with open(RESPONSAVEIS_FILE, "w", encoding="utf-8") as f:
            json.dump(lista, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

# --- COORDENADORES ---
def carregar_coordenadores():
    """Carrega a lista de coordenadores do banco de dados local (JSON)."""
    if not os.path.exists(COORDENADORES_FILE):
        salvar_coordenadores(DEFAULT_COORDENADORES)
        return DEFAULT_COORDENADORES.copy()
    try:
        with open(COORDENADORES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return DEFAULT_COORDENADORES.copy()
    except Exception:
        return DEFAULT_COORDENADORES.copy()

def salvar_coordenadores(lista):
    """Salva a lista de coordenadores no banco de dados local (JSON)."""
    try:
        os.makedirs(DB_DIR, exist_ok=True)
        with open(COORDENADORES_FILE, "w", encoding="utf-8") as f:
            json.dump(lista, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

# --- CONTRATOS ---
def carregar_contratos():
    """Carrega a lista de contratos do banco de dados local (JSON)."""
    if not os.path.exists(CONTRATOS_FILE):
        salvar_contratos(DEFAULT_CONTRATOS)
        return DEFAULT_CONTRATOS.copy()
    try:
        with open(CONTRATOS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return DEFAULT_CONTRATOS.copy()
    except Exception:
        return DEFAULT_CONTRATOS.copy()

def salvar_contratos(lista):
    """Salva a lista de contratos no banco de dados local (JSON)."""
    try:
        os.makedirs(DB_DIR, exist_ok=True)
        with open(CONTRATOS_FILE, "w", encoding="utf-8") as f:
            json.dump(lista, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False
