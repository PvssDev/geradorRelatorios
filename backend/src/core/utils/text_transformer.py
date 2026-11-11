# -*- coding: utf-8 -*-
"""
Engine Semântica de Substituição Textual em Tempo Linear O(N).
Substitui todas as 36 chamadas sequenciais de .replace() por uma expressão regular compilada
em passagem única, transformando termos de fiscalização em monitoramento de forma determinística.
"""
import re
from typing import Any, List, Tuple

# Mapeamento estrito de termos regulatórios de Fiscalização -> Monitoramento
TRANSFORM_MAP = {
    # Formas no Plural (palavras mais longas primeiro para evitar prefixos parciais)
    "fiscalizações": "monitoramentos",
    "Fiscalizações": "Monitoramentos",
    "FISCALIZAÇÕES": "MONITORAMENTOS",
    "fiscalizadores": "monitoradores",
    "Fiscalizadores": "Monitorador",  # Mantido para compatibilidade histórica do relatório
    "FISCALIZADORES": "MONITORADORES",
    "fiscalizatórias": "monitoradoras",
    "Fiscalizatórias": "Monitoradoras",
    "fiscalizatórios": "monitoradores",
    "Fiscalizatórios": "Monitoradores",
    "fiscalizadoras": "monitoradoras",
    "Fiscalizadoras": "Monitoradoras",
    "fiscalizados": "monitorados",
    "Fiscalizados": "Monitorados",
    "FISCALIZADOS": "MONITORADOS",
    "fiscalizadas": "monitoradas",
    "Fiscalizadas": "Monitoradas",
    
    # Formas no Singular
    "fiscalização": "monitoramento",
    "Fiscalização": "Monitoramento",
    "FISCALIZAÇÃO": "MONITORAMENTO",
    "fiscalizatória": "monitoradora",
    "Fiscalizatória": "Monitoradora",
    "fiscalizatório": "monitorador",
    "Fiscalizatório": "Monitorador",
    "fiscalizador": "monitorador",
    "Fiscalizador": "Monitorador",
    "FISCALIZADOR": "MONITORADOR",
    "fiscalizadora": "monitoradora",
    "Fiscalizadora": "Monitoradora",
    "fiscalizado": "monitorado",
    "Fiscalizado": "Monitorado",
    "FISCALIZADO": "MONITORADO",
    "fiscalizada": "monitorada",
    "Fiscalizada": "Monitorada",
    "fiscalizar": "monitorar",
    "Fiscalizar": "Monitorar",
    "FISCALIZAR": "MONITORAR",
}

# Expressão regular compilada em passagem única O(N) com chaves ordenadas por tamanho decrescente
_KEYS_SORTED = sorted(TRANSFORM_MAP.keys(), key=len, reverse=True)
_PATTERN = re.compile("|".join(re.escape(k) for k in _KEYS_SORTED))


def transformar_para_monitoramento(texto: Any) -> str:
    """
    Substitui todos os termos de fiscalização por termos de monitoramento em tempo linear O(N).
    Se o valor for nulo ou vazio, retorna string vazia.
    """
    if texto is None:
        return ""
    texto_str = str(texto)
    if not texto_str:
        return ""
    return _PATTERN.sub(lambda m: TRANSFORM_MAP[m.group(0)], texto_str)


def transformar_paragrafos_monitoramento(paragraphs_list: List[List[Tuple[str, bool, bool, Any]]]) -> List[List[Tuple[str, bool, bool, Any]]]:
    """
    Transforma listas de tuplas de parágrafos [(texto, bold, italic, color), ...]
    para termos de monitoramento em tempo linear.
    """
    if not paragraphs_list:
        return []
    res = []
    for p in paragraphs_list:
        new_p = []
        for text, bold, italic, color in p:
            new_p.append((transformar_para_monitoramento(text), bold, italic, color))
        res.append(new_p)
    return res
