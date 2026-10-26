# -*- coding: utf-8 -*-
"""
Regras de Negócio e Algoritmos de Domínio para o Relatório CRC (Rota dos Coqueiros - Paiva).
Contrato de Concessão Patrocinada CGPE – 001/2006 (PE-024).
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


def formatar_extenso_feminino_achados(total_ncs: int) -> str:
    """
    Formata o número de achados no padrão gramatical feminino singular/plural
    exigido pelas conclusões do relatório CRC:
    ex: '1 (uma)', '2 (duas)', '3 (três)'...
    """
    if total_ncs <= 0:
        return "0 (zero)"

    f_extenso = {
        1: "uma", 2: "duas", 3: "três", 4: "quatro", 5: "cinco",
        6: "seis", 7: "sete", 8: "oito", 9: "nove", 10: "dez"
    }

    if total_ncs in f_extenso:
        return f"{total_ncs} ({f_extenso[total_ncs]})"

    from sections.finalizacao.finalizacao import numero_por_extenso
    return f"{total_ncs} ({numero_por_extenso(total_ncs)})"


def gerar_codigo_crc(
    sh_num: Union[int, str],
    km_inicio: Union[float, int, str],
    km_fim: Union[float, int, str],
    tipo_marca: str = "+",
    ano: Optional[str] = None,
    sequencial: int = 1
) -> str:
    """
    Formata a codificação técnica de Não Conformidade para o CRC.
    Padrão: CRC.SH{sh_num:03d}.{km_inicio:04d}{tipo}{km_fim:04d}/{ano}.{sequencial:03d}
    Exemplo: CRC.SH015.0646+0648/2026.001
    """
    try:
        sh_int = int(str(sh_num).replace("SH", "").strip())
        sh_str = f"SH{sh_int:03d}"
    except (ValueError, TypeError):
        sh_str = f"SH{str(sh_num).strip()}"

    def _km_to_str(km_val: Union[float, int, str]) -> str:
        try:
            # Se vier como float km (ex: 6.46), converte para escala de 0.01km (646 -> 0646)
            f_val = float(str(km_val).replace(",", ".").strip())
            if f_val < 100.0:
                int_val = int(round(f_val * 100))
            else:
                int_val = int(round(f_val))
            return f"{int_val:04d}"
        except (ValueError, TypeError):
            digits = re.sub(r"\D", "", str(km_val))
            return digits.zfill(4)[:4] if digits else "0000"

    k_ini = _km_to_str(km_inicio)
    k_fim = _km_to_str(km_fim)
    marca = "+" if tipo_marca == "+" else "-"
    ano_str = str(ano).strip() if ano else str(datetime.now().year)

    return f"CRC.{sh_str}.{k_ini}{marca}{k_fim}/{ano_str}.{int(sequencial):03d}"


def classificar_achados_crc(
    nc_data: Union[pd.DataFrame, List[Dict[str, Any]], Tuple[Any, ...]],
    id_fisc: Optional[str] = None
) -> ResumoAchados:
    """
    Classifica achados de fiscalização do CRC em tempo linear O(N) com uma única passagem.
    Separa Não Conformidades reais e Pontos de Atenção reais para a PE-024 (Praia do Paiva).
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


def separar_achados_df_crc(
    nc_df: Optional[pd.DataFrame],
    id_fisc: Optional[str] = None
) -> Tuple[pd.DataFrame, pd.DataFrame, ResumoAchados]:
    """
    Separa DataFrames de Não Conformidades (NC) e Pontos de Atenção (PA) para o relatório CRC,
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

    resumo = classificar_achados_crc(df, id_fisc=id_fisc)
    return ncs_df, pas_df, resumo


def validar_vistoria_crc(fisc: Union[FiscalizacaoRecord, Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    Valida as regras de negócio de cadastro da fiscalização CRC (Contrato Concessão Patrocinada CGPE – 001/2006).
    Regras mandatórias:
    - ID da Fiscalização deve ser informado.
    - Data da fiscalização deve ser informada.
    - Local ou Trecho deve referenciar a PE-024 / Sistema Viário do Paiva.
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
        erros.append("Local/Trecho da fiscalização é obrigatório (ex: PE-024 / Sistema Viário do Paiva).")

    return len(erros) == 0, erros
