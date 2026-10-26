# -*- coding: utf-8 -*-
"""
Regras de Negócio e Algoritmos de Domínio para o Relatório CRA (Rota do Atlântico).
Totalmente puro e desacoplado de Streamlit, python-docx e sistema de arquivos.
"""
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd

from core.models.entities import NaoConformidadeRecord, ResumoAchados, FiscalizacaoRecord


def _extrair_ano_seguro(data_val: Any) -> str:
    """Extrai o ano em formato de 4 dígitos (ex: '2026') de forma segura."""
    if not data_val or pd.isna(data_val):
        return str(datetime.now().year)

    if hasattr(data_val, "year"):
        return str(data_val.year)

    data_str = str(data_val).strip()
    match = re.search(r"\b(20\d{2})\b", data_str)
    if match:
        return match.group(1)

    for fmt in ("%d/%m/%Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return str(datetime.strptime(data_str, fmt).year)
        except ValueError:
            continue

    return str(datetime.now().year)


def gerar_codigo_cra(base_input: str, data_fisc: Optional[str] = None, seq_idx: int = 1) -> str:
    """
    Calcula a codificação completa para o relatório CRA.
    Estrutura: {base}/{ano}.{num_final:03d} (ex: CRA.ST601.2790-2794/2026.001).
    Se base_input já contém /{ano}.{offset}, incrementa a partir do offset inicial (offset + seq_idx - 1).
    Caso contrário, formata com /{ano}.{seq_idx:03d}.
    """
    if not base_input:
        return ""

    ano_padrao = _extrair_ano_seguro(data_fisc)
    base_limpa = str(base_input).strip()

    if "/" in base_limpa:
        partes = base_limpa.split("/", 1)
        base = partes[0].strip()
        sufixo = partes[1].strip()

        m = re.match(r"^(\d{4})\.(\d+)$", sufixo)
        if m:
            ano = m.group(1)
            offset_inicial = int(m.group(2))
            num_final = offset_inicial + (int(seq_idx) - 1)
            return f"{base}/{ano}.{num_final:03d}"

        m_ano = re.match(r"^(\d{4})$", sufixo)
        if m_ano:
            ano = m_ano.group(1)
            return f"{base}/{ano}.{int(seq_idx):03d}"

        return f"{base}/{ano_padrao}.{int(seq_idx):03d}"
    else:
        return f"{base_limpa}/{ano_padrao}.{int(seq_idx):03d}"


def obter_proximo_sequencial_cra(registros: List[Dict[str, Any]], id_vinculo: str, tipo_registro: str) -> int:
    """
    Calcula o próximo número sequencial (.001, .002...) para a codificação CRA,
    contando estritamente em relação ao tipo selecionado ('Não Conformidade' ou 'Ponto de Atenção')
    para a fiscalização vinculada.
    """
    if not registros:
        return 1

    campo_filtro = "Não Conformidade" if tipo_registro == "Não Conformidade" else "Ponto de Atenção"
    recs_tipo = [
        nc for nc in registros
        if str(nc.get("ID da Fiscalização", "")).strip() == str(id_vinculo).strip()
        and str(nc.get(campo_filtro, "")).strip()
    ]

    max_num = 0
    for r in recs_tipo:
        cod = str(r.get("Codificação", "") or r.get("Trecho", "")).strip()
        m = re.search(r"/(\d{4})\.(\d+)$", cod)
        if m:
            try:
                num = int(m.group(2))
                if num > max_num:
                    max_num = num
            except ValueError:
                pass

    if max_num > 0:
        return max_num + 1

    return len(recs_tipo) + 1


def formatar_codificacoes_contraidas_cra(cods: List[str]) -> str:
    """
    Formata lista de codificações relacionadas no formato contraído:
    ex: 'codificação/2026.001 e 002.' se compartilharem a mesma base e ano.
    Caso contrário, retorna a concatenação separada.
    """
    if not cods:
        return ""

    unique_cods = []
    for c in cods:
        c_clean = str(c).strip()
        if c_clean and c_clean not in unique_cods:
            unique_cods.append(c_clean)

    if len(unique_cods) == 0:
        return ""
    if len(unique_cods) == 1:
        return unique_cods[0]

    pattern = re.compile(r"^(.*?)/(\d{4})\.(\d+)$")
    parsed = []
    for c in unique_cods:
        m = pattern.match(c)
        if m:
            parsed.append((m.group(1), m.group(2), m.group(3)))
        else:
            parsed.append(None)

    if all(p is not None for p in parsed):
        primeira_base = parsed[0][0]
        primeiro_ano = parsed[0][1]
        mesma_base_ano = all(p[0] == primeira_base and p[1] == primeiro_ano for p in parsed)
        if mesma_base_ano:
            sufixos = [p[2] for p in parsed]
            primeiro_completo = f"{primeira_base}/{primeiro_ano}.{sufixos[0]}"
            if len(sufixos) == 2:
                return f"{primeiro_completo} e {sufixos[1]}."
            else:
                outros = ", ".join(sufixos[1:-1])
                return f"{primeiro_completo}, {outros} e {sufixos[-1]}."

    if len(unique_cods) == 2:
        return f"{unique_cods[0]} e {unique_cods[1]}."
    return f"{', '.join(unique_cods[:-1])} e {unique_cods[-1]}."


def classificar_achados_cra(
    nc_data: Union[pd.DataFrame, List[Dict[str, Any]], Tuple[Any, ...]],
    id_fisc: Optional[str] = None
) -> ResumoAchados:
    """
    Classifica achados de fiscalização do CRA em tempo linear O(N) com uma única passagem.
    Separa Não Conformidades reais e Pontos de Atenção reais, montando entidades imutáveis.
    Substitui varreduras repetidas sobre DataFrames em múltiplos pontos do sistema.
    """
    if nc_data is None:
        return ResumoAchados()

    # Normalização de entrada para registros iteráveis
    if isinstance(nc_data, pd.DataFrame):
        if nc_data.empty:
            return ResumoAchados()
        df = nc_data
        if id_fisc and "ID da Fiscalização" in df.columns:
            id_fisc_str = str(id_fisc).strip()
            mask = df["ID da Fiscalização"].astype(str).str.strip() == id_fisc_str
            df_filtered = df[mask]
            # Fallback se não encontrar nada pelo ID mas houver registros gerais
            if not df_filtered.empty:
                df = df_filtered
        registros_brutos = df.to_dict(orient="records")
    elif isinstance(nc_data, (list, tuple)):
        if not nc_data:
            return ResumoAchados()
        if isinstance(nc_data[0], NaoConformidadeRecord):
            # Já é uma lista de records tipados
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
        # Mapeamento dinâmico insensível a maiúsculas/minúsculas
        col_nc = next((k for k in raw if str(k).strip().lower() in ("não conformidade", "nao conformidade")), None)
        col_pa = next((k for k in raw if str(k).strip().lower() in ("ponto de atenção", "ponto de atencao")), None)

        val_nc = str(raw.get(col_nc, "") or "").strip() if col_nc else ""
        val_pa = str(raw.get(col_pa, "") or "").strip() if col_pa else ""

        # Ignora valores nulos/vazios de pandas
        if val_nc.lower() in ("nan", "none"):
            val_nc = ""
        if val_pa.lower() in ("nan", "none"):
            val_pa = ""

        tem_conteudo_nc = bool(val_nc)
        tem_conteudo_pa = bool(val_pa)

        # Checa fallback quando nem NC nem PA estão explicitamente preenchidos
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
            # Garante flag is_ponto_atencao = True
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


def validar_vistoria_cra(fisc: Union[FiscalizacaoRecord, Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Valida as regras de negócio de cadastro da fiscalização CRA (Contrato Concessão CT. nº 043/2011).
    Regras mandatórias:
    - ID da Fiscalização deve ser informado.
    - Data da vistoria deve ser informada.
    - Cidade e Hora são obrigatórias para CRA (Suape).
    - Local ou Subtrecho deve ser informado.
    """
    erros: List[str] = []

    if isinstance(fisc, FiscalizacaoRecord):
        id_fisc = fisc.id_fisc
        data = fisc.data
        hora = fisc.hora
        cidade = fisc.cidade
        local = fisc.local
    elif isinstance(fisc, dict):
        id_fisc = str(fisc.get("ID da Fiscalização", "")).strip()
        data = str(fisc.get("Data", "")).strip()
        hora = str(fisc.get("Hora", "")).strip()
        cidade = str(fisc.get("Cidade", "")).strip()
        local = str(fisc.get("Local", "")).strip()
    else:
        return False, ["Formato de fiscalização inválido."]

    if not id_fisc:
        erros.append("ID da Fiscalização é obrigatório.")
    if not data or data.lower() in ("nan", "none"):
        erros.append("Data da fiscalização é obrigatória.")
    if not hora or hora.lower() in ("nan", "none"):
        erros.append("Hora da fiscalização é obrigatória no contrato CRA (Suape).")
    if not cidade or cidade.lower() in ("nan", "none"):
        erros.append("Cidade da vistoria é obrigatória no contrato CRA (Suape).")
    if not local or local.lower() in ("nan", "none", "=local="):
        erros.append("Local/Subtrecho da fiscalização é obrigatório.")
    return len(erros) == 0, erros



def separar_achados_df_cra(
    nc_df: Optional[pd.DataFrame],
    id_fisc: Optional[str] = None
) -> Tuple[pd.DataFrame, pd.DataFrame, ResumoAchados]:
    """
    Separa DataFrames de Não Conformidades (NC) e Pontos de Atenção (PA) para o relatório CRA,
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

    resumo = classificar_achados_cra(df, id_fisc=id_fisc)
    return ncs_df, pas_df, resumo

