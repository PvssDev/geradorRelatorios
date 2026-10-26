# -*- coding: utf-8 -*-
"""
Regras de Negócio e Algoritmos de Domínio para o Relatório SOCICAM (Terminais Rodoviários).
Contrato de Concessão de Serviço Público Nº 1.041.080/08 (TIP, Caruaru, Garanhuns, Petrolina).
Totalmente puro e desacoplado de Streamlit, python-docx e sistema de arquivos.
"""
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd

from core.models.entities import NaoConformidadeRecord, ResumoAchados, FiscalizacaoRecord


def normalizar_nome_terminal_rodoviario(local_val: Any) -> str:
    """
    Padroniza o nome oficial do terminal rodoviário com o prefixo 'Terminal Rodoviário'
    para títulos e parágrafos de introdução/objetivo:
    - 'TIP' -> 'Terminal Rodoviário de Passageiros do Recife (TIP)'
    - 'Petrolina' -> 'Terminal Rodoviário de Petrolina'
    - 'Terminal de Caruaru' -> 'Terminal Rodoviário de Caruaru'
    - 'Terminal Rodoviário de Garanhuns' -> 'Terminal Rodoviário de Garanhuns'
    """
    if not local_val or pd.isna(local_val):
        return "Terminal Rodoviário de Passageiros do Recife (TIP)"

    l_str = str(local_val).strip()
    if not l_str or l_str.lower() in ("nan", "none", "=local="):
        return "Terminal Rodoviário de Passageiros do Recife (TIP)"

    if l_str.upper() == "TIP":
        return "Terminal Rodoviário de Passageiros do Recife (TIP)"

    l_lower = l_str.lower()
    if l_lower.startswith("terminal rodoviário"):
        return l_str
    elif l_lower.startswith("terminal de ") or l_lower.startswith("terminal do ") or l_lower.startswith("terminal da "):
        return "Terminal Rodoviário " + l_str[len("Terminal "):].strip()
    elif l_lower.startswith("terminal"):
        return "Terminal Rodoviário " + l_str[len("Terminal"):].strip()

    return f"Terminal Rodoviário de {l_str}"


def normalizar_nome_terminal_curto(local_val: Any) -> str:
    """
    Padroniza o nome do terminal rodoviário no formato curto 'Terminal de ...'
    para as conclusões do relatório:
    - 'Terminal Rodoviário de Petrolina' -> 'Terminal de Petrolina'
    - 'Terminal Rodoviário de Passageiros do Recife (TIP)' -> 'Terminal de Passageiros do Recife (TIP)'
    - 'Terminal de Caruaru' -> 'Terminal de Caruaru'
    - 'Garanhuns' -> 'Terminal de Garanhuns'
    """
    if not local_val or pd.isna(local_val):
        return "Terminal de Passageiros do Recife (TIP)"

    l_str = str(local_val).strip()
    if not l_str or l_str.lower() in ("nan", "none", "=local="):
        return "Terminal de Passageiros do Recife (TIP)"

    if l_str.upper() == "TIP":
        return "Terminal de Passageiros do Recife (TIP)"

    l_lower = l_str.lower()
    if l_lower.startswith("terminal rodoviário de "):
        return "Terminal de " + l_str[len("Terminal Rodoviário de "):].strip()
    elif l_lower.startswith("terminal rodoviário do "):
        return "Terminal do " + l_str[len("Terminal Rodoviário do "):].strip()
    elif l_lower.startswith("terminal rodoviário da "):
        return "Terminal da " + l_str[len("Terminal Rodoviário da "):].strip()
    elif l_lower.startswith("terminal rodoviário "):
        return "Terminal de " + l_str[len("Terminal Rodoviário "):].strip()
    elif l_lower.startswith("terminal de ") or l_lower.startswith("terminal do ") or l_lower.startswith("terminal da "):
        return l_str
    elif l_lower.startswith("terminal "):
        return l_str

    return f"Terminal de {l_str}"


def extrair_sigla_terminal(local_val: Any) -> str:
    """
    Extrai a sigla ou nome em caixa alta do terminal para os títulos de Apêndices e Sumário.
    Exemplo: 'Terminal Rodoviário de Passageiros do Recife (TIP)' -> 'TIP'
             'PETROLINA (PE)' -> 'PETROLINA'
             'Caruaru' -> 'CARUARU'
    """
    if not local_val or pd.isna(local_val):
        return "TIP"

    l_str = str(local_val).strip()
    if not l_str or l_str.lower() in ("nan", "none"):
        return "TIP"

    l_upper = l_str.upper()
    if "TIP" in l_upper:
        return "TIP"
    if "(" in l_upper:
        return l_upper.split("(")[0].strip()

    return l_upper


def formatar_extenso_achados_socicam(total_ncs: int) -> str:
    """
    Formata o número de Não Conformidades no gênero feminino exigido pelas determinações
    e conclusões do relatório SOCICAM:
    ex: 1 -> 'uma', 2 -> 'duas', 3 -> 'três'...
    """
    if total_ncs <= 0:
        return "zero"

    f_extenso = {
        1: "uma", 2: "duas", 3: "três", 4: "quatro", 5: "cinco",
        6: "seis", 7: "sete", 8: "oito", 9: "nove", 10: "dez"
    }

    if total_ncs in f_extenso:
        return f_extenso[total_ncs]

    from sections.finalizacao.finalizacao import numero_por_extenso
    return numero_por_extenso(total_ncs)


def formatar_frase_conclusao_achados_socicam(total_ncs: int) -> str:
    """
    Retorna a frase gramaticalmente correta para o parágrafo conclusivo do SOCICAM:
    - 0 -> 'nenhuma nova Não Conformidade'
    - 1 -> 'uma nova Não Conformidade'
    - 2 -> 'duas novas Não Conformidades'
    """
    if total_ncs == 0:
        return "nenhuma nova Não Conformidade"

    extenso = formatar_extenso_achados_socicam(total_ncs)
    if total_ncs == 1:
        return f"{extenso} nova Não Conformidade"

    return f"{extenso} novas Não Conformidades"


def classificar_achados_socicam(
    nc_data: Union[pd.DataFrame, List[Dict[str, Any]], Tuple[Any, ...]],
    id_fisc: Optional[str] = None
) -> ResumoAchados:
    """
    Classifica achados de fiscalização do SOCICAM em tempo linear O(N) com uma única passagem.
    Separa Não Conformidades reais e Pontos de Atenção reais para os terminais rodoviários.
    """
    if nc_data is None:
        return ResumoAchados()

    if isinstance(nc_data, pd.DataFrame):
        if nc_data.empty:
            return ResumoAchados()
        df = nc_data
        if id_fisc and "ID da Fiscalização" in df.columns:
            id_fisc_str = str(id_fisc).strip()
            mask = df["ID da Fiscalização"].astype(str).str.strip() == id_fisc_str
            df_filtered = df[mask]
            if not df_filtered.empty:
                df = df_filtered
        registros_brutos = df.to_dict(orient="records")
    elif isinstance(nc_data, (list, tuple)):
        if not nc_data:
            return ResumoAchados()
        if isinstance(nc_data[0], NaoConformidadeRecord):
            lista_records = list(nc_data)
            if id_fisc:
                id_fisc_str = str(id_fisc).strip()
                filtered = [r for r in lista_records if r.id_fisc == id_fisc_str]
                if filtered:
                    lista_records = filtered
            ncs = tuple(r for r in lista_records if not r.is_ponto_atencao)
            pas = tuple(r for r in lista_records if r.is_ponto_atencao)
            tem_nc = len(ncs) > 0
            tem_pa = len(pas) > 0
            return ResumoAchados(
                ncs=ncs,
                pontos_atencao=pas,
                total_achados=len(ncs) + len(pas),
                tem_nc=tem_nc,
                tem_pa=tem_pa,
                ambos_presentes=tem_nc and tem_pa
            )
        registros_brutos = [dict(r) if hasattr(r, "items") else {} for r in nc_data]
        if id_fisc:
            id_fisc_str = str(id_fisc).strip()
            filtered = [r for r in registros_brutos if str(r.get("ID da Fiscalização", "")).strip() == id_fisc_str]
            if filtered:
                registros_brutos = filtered
    else:
        return ResumoAchados()

    ncs_list: List[NaoConformidadeRecord] = []
    pas_list: List[NaoConformidadeRecord] = []

    fallback_cols = [
        "Foto", "Fotos", "Observações", "Legenda da Foto",
        "Identificação", "Descrição da Evidência", "Descrição"
    ]

    for idx, raw in enumerate(registros_brutos, start=1):
        col_nc = next((k for k in raw if str(k).strip().lower() in ("não conformidade", "nao conformidade")), None)
        col_pa = next((k for k in raw if str(k).strip().lower() in ("ponto de atenção", "ponto de atencao")), None)

        val_nc = str(raw.get(col_nc, "") or "").strip() if col_nc else ""
        val_pa = str(raw.get(col_pa, "") or "").strip() if col_pa else ""

        if val_nc.lower() in ("nan", "none"):
            val_nc = ""
        if val_pa.lower() in ("nan", "none"):
            val_pa = ""

        tem_conteudo_nc = bool(val_nc)
        tem_conteudo_pa = bool(val_pa)

        if not tem_conteudo_nc and not tem_conteudo_pa:
            tem_fallback = any(
                str(raw.get(c, "") or "").strip().lower() not in ("", "nan", "none")
                for c in fallback_cols if c in raw
            )
            if tem_fallback:
                tem_conteudo_nc = True

        if tem_conteudo_nc:
            rec = NaoConformidadeRecord.de_dicionario(raw, numero_default=idx)
            ncs_list.append(rec)
        elif tem_conteudo_pa:
            rec = NaoConformidadeRecord.de_dicionario(raw, numero_default=idx)
            if not rec.is_ponto_atencao:
                rec = NaoConformidadeRecord(
                    id_fisc=rec.id_fisc,
                    numero=rec.numero,
                    trecho=rec.trecho,
                    identificacao=rec.identificacao,
                    descricao=rec.descricao,
                    foto=rec.foto,
                    direcao_faixa=rec.direcao_faixa,
                    fundamento=rec.fundamento,
                    determinacao=rec.determinacao,
                    situacao=rec.situacao,
                    is_ponto_atencao=True,
                    codigo=rec.codigo,
                    observacoes=rec.observacoes,
                    fotos_evidencia=rec.fotos_evidencia
                )
            pas_list.append(rec)

    tem_nc = len(ncs_list) > 0
    tem_pa = len(pas_list) > 0
    total = len(ncs_list) + len(pas_list)

    return ResumoAchados(
        ncs=tuple(ncs_list),
        pontos_atencao=tuple(pas_list),
        total_achados=total,
        tem_nc=tem_nc,
        tem_pa=tem_pa,
        ambos_presentes=(tem_nc and tem_pa)
    )


def separar_achados_df_socicam(
    nc_df: Optional[pd.DataFrame],
    id_fisc: Optional[str] = None
) -> Tuple[pd.DataFrame, pd.DataFrame, ResumoAchados]:
    """
    Separa DataFrames de Não Conformidades (NC) e Pontos de Atenção (PA) para o relatório SOCICAM,
    retornando também o ResumoAchados correspondente em uma única passagem.
    """
    if nc_df is None or nc_df.empty:
        return pd.DataFrame(), pd.DataFrame(), ResumoAchados()

    df = nc_df
    if id_fisc and "ID da Fiscalização" in df.columns:
        id_fisc_str = str(id_fisc).strip()
        mask_id = df["ID da Fiscalização"].astype(str).str.strip() == id_fisc_str
        df_filtered = df[mask_id]
        if not df_filtered.empty:
            df = df_filtered

    col_nc = next((c for c in df.columns if str(c).strip().lower() in ("não conformidade", "nao conformidade")), None)
    col_pa = next((c for c in df.columns if str(c).strip().lower() in ("ponto de atenção", "ponto de atencao")), None)

    ncs_df = pd.DataFrame()
    pas_df = pd.DataFrame()

    if col_nc:
        mask_nc = df[col_nc].fillna("").astype(str).str.strip() != ""
        ncs_df = df[mask_nc].copy()

    if col_pa:
        mask_pa = df[col_pa].fillna("").astype(str).str.strip() != ""
        pas_df = df[mask_pa].copy()

    if ncs_df.empty and pas_df.empty:
        fallback_cols = [
            c for c in ["Foto", "Fotos", "Observações", "Legenda da Foto", "Identificação", "Descrição da Evidência", "Descrição"]
            if c in df.columns
        ]
        if fallback_cols:
            mask_any = df[fallback_cols].fillna("").astype(str).apply(
                lambda r: any(v.strip() != "" and v.strip().lower() not in ("nan", "none") for v in r), axis=1
            )
            ncs_df = df[mask_any].copy()
        else:
            ncs_df = df.copy()

    resumo = classificar_achados_socicam(df, id_fisc=id_fisc)
    return ncs_df, pas_df, resumo


def validar_vistoria_socicam(fisc: Union[FiscalizacaoRecord, Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Valida as regras de negócio de cadastro da fiscalização SOCICAM (CT. nº 1.041.080/08).
    Regras mandatórias:
    - ID da Fiscalização deve ser informado.
    - Data da fiscalização deve ser informada.
    - Local do Terminal Rodoviário deve ser informado (ex: TIP, Caruaru, Garanhuns, Petrolina).
    """
    erros: List[str] = []

    if isinstance(fisc, FiscalizacaoRecord):
        id_fisc = fisc.id_fisc
        data = fisc.data
        local = fisc.local
    elif isinstance(fisc, dict):
        id_fisc = str(fisc.get("ID da Fiscalização", "")).strip()
        data = str(fisc.get("Data", "")).strip()
        local = str(fisc.get("Local", "")).strip()
    else:
        return False, ["Formato de fiscalização inválido."]

    if not id_fisc:
        erros.append("ID da Fiscalização é obrigatório.")
    if not data or data.lower() in ("nan", "none"):
        erros.append("Data da fiscalização é obrigatória.")
    if not local or local.lower() in ("nan", "none", "=local="):
        erros.append("Local do terminal rodoviário é obrigatório (ex: TIP, Caruaru, Garanhuns, Petrolina).")

    return len(erros) == 0, erros
