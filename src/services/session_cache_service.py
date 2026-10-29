# -*- coding: utf-8 -*-
"""
Serviço de Persistência Local da Sessão (Cache em Disco).

Gerencia o salvamento e carregamento atômico das 6 combinações de relatórios
(CRA, CRC, SOCICAM x Fiscalização, Monitoramento) na pasta local `geradorRelatorios/`.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Pasta local de cache na máquina do usuário (fora do código do projeto)
USER_HOME = os.path.expanduser("~")
CACHE_DIR = os.path.join(USER_HOME, "geradorRelatorios")

# Mapeamento padronizado das 6 combinações
MAPA_ARQUIVOS_CACHE = {
    ("CRA", "Fiscalização"): "cra_fiscalizacao.json",
    ("CRA", "Monitoramento"): "cra_monitoramento.json",
    ("CRC", "Fiscalização"): "crc_fiscalizacao.json",
    ("CRC", "Monitoramento"): "crc_monitoramento.json",
    ("SOCICAM", "Fiscalização"): "socicam_fiscalizacao.json",
    ("SOCICAM", "Monitoramento"): "socicam_monitoramento.json",
}


def obter_caminho_arquivo_cache(tipo_relatorio: str, categoria_relatorio: str) -> str:
    """Retorna o caminho absoluto do arquivo JSON correspondente à combinação selecionada."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    nome_arquivo = MAPA_ARQUIVOS_CACHE.get(
        (tipo_relatorio, categoria_relatorio),
        f"{tipo_relatorio.lower()}_{categoria_relatorio.lower()}.json"
    )
    return os.path.join(CACHE_DIR, nome_arquivo)


def salvar_sessao_local(tipo_relatorio: str, categoria_relatorio: str, dados_estado: Dict[str, Any]) -> bool:
    """
    Salva atomicamente o estado da combinação atual em arquivo JSON local.
    
    Salva chaves como:
    - temp_fiscalizacoes (list)
    - temp_nc (list)
    - manual_relacao_map (dict)
    - outros metadados relevantes
    """
    caminho = obter_caminho_arquivo_cache(tipo_relatorio, categoria_relatorio)
    try:
        conteudo = {
            "tipo_relatorio": tipo_relatorio,
            "categoria_relatorio": categoria_relatorio,
            "temp_fiscalizacoes": dados_estado.get("temp_fiscalizacoes", []),
            "temp_nc": dados_estado.get("temp_nc", []),
            "manual_relacao_map": dados_estado.get("manual_relacao_map", {}),
            "pista_persistida": dados_estado.get("pista_persistida", ""),
            "trecho_persistido": dados_estado.get("trecho_persistido", ""),
            "codificacao_persistida": dados_estado.get("codificacao_persistida", ""),
            "fundamento_persistido": dados_estado.get("fundamento_persistido", ""),
            "determinacao_persistida": dados_estado.get("determinacao_persistida", ""),
            "faixa_persistida": dados_estado.get("faixa_persistida", "")
        }
        
        # Escrita atômica usando arquivo temporário para evitar corrupção
        caminho_tmp = f"{caminho}.tmp"
        with open(caminho_tmp, "w", encoding="utf-8") as f:
            json.dump(conteudo, f, ensure_ascii=False, indent=2)
            f.flush()
            os.fsync(f.fileno())
            
        if os.path.exists(caminho):
            os.replace(caminho_tmp, caminho)
        else:
            os.rename(caminho_tmp, caminho)
            
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar cache local para {tipo_relatorio} {categoria_relatorio}: {e}")
        return False


def carregar_sessao_local(tipo_relatorio: str, categoria_relatorio: str) -> Optional[Dict[str, Any]]:
    """
    Carrega o estado salvo do arquivo JSON local correspondente.
    Retorna None se o arquivo não existir ou for inválido.
    """
    caminho = obter_caminho_arquivo_cache(tipo_relatorio, categoria_relatorio)
    if not os.path.exists(caminho):
        return None
        
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            dados = json.load(f)
        if isinstance(dados, dict):
            return dados
    except Exception as e:
        logger.error(f"Erro ao carregar cache local de {caminho}: {e}")
    return None


def limpar_sessao_local(tipo_relatorio: str, categoria_relatorio: str) -> bool:
    """
    Remove ou reseta o arquivo JSON local da combinação especificada.
    """
    caminho = obter_caminho_arquivo_cache(tipo_relatorio, categoria_relatorio)
    try:
        if os.path.exists(caminho):
            os.remove(caminho)
        return True
    except Exception as e:
        logger.error(f"Erro ao limpar cache local de {caminho}: {e}")
        return False
