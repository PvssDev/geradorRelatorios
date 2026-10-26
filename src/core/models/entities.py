# -*- coding: utf-8 -*-
"""
Entidades de domínio puras e imutáveis da aplicação.
Seguem o princípio da Imutabilidade (Value Objects / Dataclasses congeladas)
para garantir segurança de concorrência e integridade referencial.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple


@dataclass(frozen=True)
class FotoEvidencia:
    """Representa uma evidência fotográfica coletada durante a vistoria."""
    nome_arquivo: str
    path_ou_bytes: Any = None
    timestamp: Optional[str] = None
    legenda: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def de_dicionario(cls, dados: Dict[str, Any]) -> "FotoEvidencia":
        return cls(
            nome_arquivo=str(dados.get("nome_arquivo", "") or dados.get("Foto", "")).strip(),
            path_ou_bytes=dados.get("path_ou_bytes"),
            timestamp=dados.get("timestamp"),
            legenda=str(dados.get("legenda", "") or dados.get("Observações", "")).strip(),
            metadata=dict(dados.get("metadata", {})),
        )


@dataclass(frozen=True)
class NaoConformidadeRecord:
    """
    Representa um achado de campo (Não Conformidade ou Ponto de Atenção).
    Totalmente imutável para evitar mutações acidentais durante a geração.
    """
    id_fisc: str
    numero: int
    trecho: str
    identificacao: str
    descricao: str
    foto: str
    direcao_faixa: str = ""
    fundamento: str = ""
    determinacao: str = ""
    situacao: str = "Pendente"
    is_ponto_atencao: bool = False
    codigo: str = ""
    observacoes: str = ""
    fotos_evidencia: Tuple[FotoEvidencia, ...] = field(default_factory=tuple)

    @classmethod
    def de_dicionario(cls, dados: Dict[str, Any], numero_default: int = 1) -> "NaoConformidadeRecord":
        col_nc = next(
            (c for c in dados if str(c).strip().lower() in ("não conformidade", "nao conformidade")),
            None
        )
        col_pa = next(
            (c for c in dados if str(c).strip().lower() in ("ponto de atenção", "ponto de atencao")),
            None
        )
        
        texto_nc = str(dados.get(col_nc, "")).strip() if col_nc else ""
        texto_pa = str(dados.get(col_pa, "")).strip() if col_pa else ""
        is_pa = bool(texto_pa and not texto_nc)
        descricao = texto_pa if is_pa else (texto_nc or str(dados.get("Descrição", "")).strip())
        
        raw_num = dados.get("Nº") or dados.get("numero") or dados.get("item")
        try:
            num = int(raw_num) if raw_num is not None else numero_default
        except (ValueError, TypeError):
            num = numero_default

        return cls(
            id_fisc=str(dados.get("ID da Fiscalização", "")).strip(),
            numero=num,
            trecho=str(dados.get("Trecho", "")).strip(),
            identificacao=str(dados.get("Identificação", "") or dados.get("identificacao", "")).strip(),
            descricao=descricao,
            foto=str(dados.get("Foto", "") or dados.get("Fotos", "")).strip(),
            direcao_faixa=str(dados.get("Direção/Faixa", "") or dados.get("Faixa", "")).strip(),
            fundamento=str(dados.get("Fundamento", "") or dados.get("FUNDAMENTO DA INFRAÇÃO (CONTRATO DE CONCESSÃO)", "")).strip(),
            determinacao=str(dados.get("Determinação", "") or dados.get("DETERMINAÇÃO / RECOMENDAÇÃO", "")).strip(),
            situacao=str(dados.get("Situacao", "") or dados.get("Situação", "Pendente")).strip(),
            is_ponto_atencao=is_pa,
            codigo=str(dados.get("Codificação", "") or dados.get("codigo", "")).strip(),
            observacoes=str(dados.get("Observações", "") or dados.get("Legenda da Foto", "")).strip(),
        )


@dataclass(frozen=True)
class FiscalizacaoRecord:
    """Representa os metadados cadastrais de uma fiscalização ou monitoramento."""
    id_fisc: str
    contrato: str
    data: str
    hora: str = ""
    cidade: str = ""
    local: str = ""
    responsaveis: Tuple[str, ...] = field(default_factory=tuple)
    coordenador: str = ""
    periodo: str = ""
    status_gerado: bool = False

    @classmethod
    def de_dicionario(cls, dados: Dict[str, Any]) -> "FiscalizacaoRecord":
        raw_resp = dados.get("Pessoal Responsável", "")
        if isinstance(raw_resp, str):
            resp_list = tuple(
                r.strip() for r in raw_resp.split(",")
                if r.strip() and r.strip().lower() not in ("nan", "none")
            )
        elif isinstance(raw_resp, (list, tuple)):
            resp_list = tuple(str(r).strip() for r in raw_resp if str(r).strip())
        else:
            resp_list = ()

        return cls(
            id_fisc=str(dados.get("ID da Fiscalização", "")).strip(),
            contrato=str(dados.get("Contrato", "")).strip(),
            data=str(dados.get("Data", "")).strip(),
            hora=str(dados.get("Hora", "")).strip(),
            cidade=str(dados.get("Cidade", "")).strip(),
            local=str(dados.get("Local", "")).strip(),
            responsaveis=resp_list,
            coordenador=str(dados.get("Coordenador", "")).strip(),
            periodo=str(dados.get("Período", "") or dados.get("Periodo", "")).strip(),
            status_gerado=bool(dados.get("Relatório Gerado", False)),
        )


@dataclass(frozen=True)
class ResumoAchados:
    """
    Agrupamento pré-calculado em tempo O(N) dos achados de uma fiscalização.
    Substitui varreduras iterativas repetitivas sobre DataFrames.
    """
    ncs: Tuple[NaoConformidadeRecord, ...] = field(default_factory=tuple)
    pontos_atencao: Tuple[NaoConformidadeRecord, ...] = field(default_factory=tuple)
    total_achados: int = 0
    tem_nc: bool = False
    tem_pa: bool = False
    ambos_presentes: bool = False


@dataclass(frozen=True)
class MetadadosMonitoramento:
    """Metadados extraídos do relatório anterior (Fiscalização ou Monitoramento N-1)."""
    n_prev: int = 0
    n_curr: int = 1
    ctr_num: str = "XX/XXXX"
    processo_sei_prev: str = "xxxxxxxx-xxx"
    data_vistoria_prev: str = "XX/XX/XXXX"
    oficio_num_prev: str = "xxx/xxxx"
    oficio_data_prev: str = "xx/xx/xxxx"
    carta_num_prev: str = "xxxx/xxxx"
    carta_data_prev: str = "xx/xx/xxxx"
    carta_sei_prev: str = "xxxxxxxx-xxx"
    n_ncs_pendentes_prev: int = 0
    is_fiscalizacao: bool = False

    @property
    def n_curr_ordinal(self) -> str:
        """Retorna formato ordinal: '1º', '2º', '3º'..."""
        return f"{self.n_curr}º"

    @classmethod
    def de_dicionario(cls, dados: Dict[str, Any]) -> "MetadadosMonitoramento":
        raw_n_prev = dados.get("N_prev", dados.get("n_prev", 0))
        try:
            n_prev = int(raw_n_prev)
        except (ValueError, TypeError):
            n_prev = 0

        raw_n_curr = dados.get("N_curr", dados.get("n_curr", n_prev + 1))
        try:
            n_curr = int(raw_n_curr)
        except (ValueError, TypeError):
            n_curr = n_prev + 1

        raw_pend = dados.get("N_ncs_pendentes_prev", dados.get("n_ncs_pendentes_prev", 0))
        try:
            n_ncs_pendentes_prev = int(raw_pend)
        except (ValueError, TypeError):
            n_ncs_pendentes_prev = 0

        return cls(
            n_prev=n_prev,
            n_curr=n_curr,
            ctr_num=str(dados.get("ctr_num", "XX/XXXX")),
            processo_sei_prev=str(dados.get("processo_sei_prev", "xxxxxxxx-xxx")),
            data_vistoria_prev=str(dados.get("data_vistoria_prev", "XX/XX/XXXX")),
            oficio_num_prev=str(dados.get("oficio_num_prev", "xxx/xxxx")),
            oficio_data_prev=str(dados.get("oficio_data_prev", "xx/xx/xxxx")),
            carta_num_prev=str(dados.get("carta_num_prev", "xxxx/xxxx")),
            carta_data_prev=str(dados.get("carta_data_prev", "xx/xx/xxxx")),
            carta_sei_prev=str(dados.get("carta_sei_prev", "xxxxxxxx-xxx")),
            n_ncs_pendentes_prev=n_ncs_pendentes_prev,
            is_fiscalizacao=bool(dados.get("is_fiscalizacao", False)),
        )


@dataclass(frozen=True)
class Quadro1ItemAnterior:
    """Item de Não Conformidade extraído da tabela do Quadro 1 do documento anterior."""
    id_nc: str
    info_ou_constatacao: str
    situacao: str = "PENDENTE"
    foto_ref: str = ""

