# -*- coding: utf-8 -*-
"""
Especialização do Relatório para o SOCICAM Monitoramento (Terminais Rodoviários).
Contrato de Concessão de Serviço Público Nº 1.041.080/08 (TIP, Caruaru, Garanhuns, Petrolina).
Utiliza a nova Engine de Monitoramento em memória e templates padronizados.
"""
import os
from typing import Any, Dict, List, Optional, Tuple
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import pandas as pd

from reports.base import BaseMonitoramentoMixin
from reports.socicam import SocicamReport
from core.interfaces.report_contracts import IReportContract
from core.rules.socicam_rules import normalizar_nome_terminal_rodoviario
from services.previous_report.previous_report_audit_service import (
    extrair_metadados_anterior,
    extrair_linhas_quadro1_anterior,
)
from monitoramento_utils import criar_tabela_quadro1_monitoramento
from reports.templates.socicam_monitoramento_templates import (
    SOCICAM_MONITORAMENTO_KEY,
    SOCICAM_MONITORAMENTO_DISPLAY_NAME,
    SOCICAM_MONITORAMENTO_DEFAULT_CONTRATO,
    SOCICAM_MONITORAMENTO_ABBREVIATIONS,
    SOCICAM_MONITORAMENTO_QUADRO1_HEADERS,
    SOCICAM_MONITORAMENTO_QUADRO1_COL_WIDTHS,
    get_socicam_monitoramento_intro_paragraphs,
    get_socicam_monitoramento_objective_paragraphs,
    get_socicam_monitoramento_conclusions_paragraphs,
)


class SocicamMonitoramentoReport(BaseMonitoramentoMixin, SocicamReport, IReportContract):
    """Relatório Técnico-Operacional de Monitoramento da Concessionária SOCICAM."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.N_prev = 0
        self.N_curr = 1
        self.ctr_num = "XX/XXXX"
        self.processo_sei_prev = "xxxxxxxx-xxx"
        self.documento_anterior = None

    @property
    def key(self) -> str:
        return SOCICAM_MONITORAMENTO_KEY

    @property
    def display_name(self) -> str:
        return SOCICAM_MONITORAMENTO_DISPLAY_NAME

    @property
    def default_contrato(self) -> str:
        return SOCICAM_MONITORAMENTO_DEFAULT_CONTRATO

    @property
    def capa_titulo(self) -> str:
        return "RELATÓRIO DE MONITORAMENTO TÉCNICO-OPERACIONAL"

    @property
    def capa_ctr_number_template(self) -> str:
        return "RELATÓRIO DE MONITORAMENTO TÉCNICO-OPERACIONAL CTR Nº {mes_ano}"

    @property
    def sumario_before_abreviaturas(self) -> bool:
        return False

    @property
    def signatures_before_apendices(self) -> bool:
        return True

    def get_abbreviations(self) -> List[Tuple[str, str]]:
        return list(SOCICAM_MONITORAMENTO_ABBREVIATIONS)

    def get_process_sei_texts(self, row: Any, ano: Optional[Any] = None) -> List[str]:
        from utils import extrair_mes_ano_numerico, extrair_ano
        if isinstance(row, (str, int)) and ano is None:
            ano = str(row)
            mes_ano = f"01/{ano}"
        else:
            ano = ano or extrair_ano(row.get("Data", "") if hasattr(row, "get") else row["Data"])
            data_val = row.get("Data", "") if hasattr(row, "get") else (row["Data"] if isinstance(row, dict) or hasattr(row, "__getitem__") else "")
            mes_ano = extrair_mes_ano_numerico(data_val)
        return [
            f"RELATÓRIO DE MONITORAMENTO TÉCNICO-OPERACIONAL PROC ADM Nº {mes_ano} - CTR",
            f"SEI Nº {self.processo_sei_prev}"
        ]

    def get_sumario_linhas(self, row: Any, nc_df: Any = None) -> List[str]:
        from utils import formatar_mes_ano
        try:
            mes_ano = formatar_mes_ano(row["Data"]).upper()
        except Exception:
            mes_ano = "JULHO/2026"

        linhas = [
            "1.\tINTRODUÇÃO\t4",
            "2.\tOBJETIVO\t4",
            "3.\tRESULTADO DAS VISTORIAS DAS NÃO CONFORMIDADES\t5",
        ]

        id_fisc = str(row.get("ID da Fiscalização", "")).strip() if hasattr(row, "get") else str(row["ID da Fiscalização"]).strip()
        ncs_reais = []
        if nc_df is not None and not nc_df.empty and "ID da Fiscalização" in nc_df.columns:
            current_ncs = nc_df[nc_df["ID da Fiscalização"].astype(str).str.strip() == id_fisc]
            if "Não Conformidade" in current_ncs.columns:
                ncs_reais = current_ncs[
                    current_ncs["Não Conformidade"].fillna("").astype(str).str.strip() != ""
                ].to_dict('records')

        if ncs_reais:
            for idx, nc_row in enumerate(ncs_reais, 1):
                term_val = str(nc_row.get("Terminal", nc_row.get("Local", "TIP"))).strip()
                term_name = normalizar_nome_terminal_rodoviario(term_val).upper()
                sub_num = f"3.{idx}"
                p_num = min(5 + (idx - 1) // 2, 7)
                linhas.append(f"{sub_num}\t{term_name}\t{p_num}")
        else:
            linhas.append("3.1\tTERMINAL RODOVIÁRIO DE PASSAGEIROS DO RECIFE (TIP)\t5")

        linhas.extend([
            f"4.\tRESUMO DA SITUAÇÃO DAS NÃO CONFORMIDADES MONITORADAS ({mes_ano})\t8",
            "5.\tCONCLUSÕES E RECOMENDAÇÕES\t9",
            f"\tAPÊNDICE ÚNICO - MEMORIAL FOTOGRÁFICO - VISTORIAS REALIZADAS EM {mes_ano}\t10",
        ])
        return linhas

    def gerar_capa_monitoramento(self, doc: Any, logo_path: str, row: Any, documento_anterior: Any) -> None:
        """Renderiza a capa do SOCICAM Monitoramento com auditoria anterior integrada."""
        style = doc.styles["Normal"]
        style.font.name = "Aptos"

        section = doc.sections[0]
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.5)
        section.left_margin = Inches(0.5)
        section.right_margin = Inches(0.5)

        self.documento_anterior = documento_anterior
        meta = extrair_metadados_anterior(documento_anterior)
        self.N_prev = meta.n_prev
        self.N_curr = meta.n_curr
        self.ctr_num = meta.ctr_num if meta.ctr_num != "XX/XXXX" else "04/2025"
        self.processo_sei_prev = meta.processo_sei_prev if meta.processo_sei_prev not in ("XXXXXXXX", "xxxxxxxx", "") else "xxxxxxxx-xxx"

        n_curr_str = meta.n_curr_ordinal

        def add_cover_p(text: str, bold: bool = True, size_pt: int = 12, space_after: int = 6):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(space_after)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.line_spacing = 1.15
            if text:
                run = p.add_run(text)
                run.font.name = "Aptos"
                run.font.size = Pt(size_pt)
                run.bold = bold
            return p

        # Cabeçalho Superior
        add_cover_p("", bold=False, size_pt=12, space_after=6)
        add_cover_p("", bold=False, size_pt=12, space_after=6)
        add_cover_p("COORDENADORIA DE TRANSPORTES E RODOVIAS (CTR)", bold=True, size_pt=12, space_after=4)
        add_cover_p(f"RELATÓRIO DO {n_curr_str} MONITORAMENTO DAS NÃO CONFORMIDADES", bold=True, size_pt=12, space_after=4)
        add_cover_p(f"PROCESSO DE FISCALIZAÇÃO TÉCNICO-OPERACIONAL CTR Nº {self.ctr_num}", bold=True, size_pt=12, space_after=12)

        # Imagem da Capa
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        capa_mon = os.path.join(base_dir, "assets", "capa_monitoramento.png")
        if not os.path.exists(capa_mon):
            capa_mon = os.path.join(base_dir, "assets", "capa_1.png")
        if not os.path.exists(capa_mon):
            capa_mon = logo_path

        if os.path.exists(capa_mon):
            doc.add_picture(capa_mon, width=Inches(5.90))
            doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
            doc.paragraphs[-1].paragraph_format.space_after = Pt(12)
            doc.paragraphs[-1].paragraph_format.space_before = Pt(12)

        # Títulos Centrais
        add_cover_p("PROCESSO DE FISCALIZAÇÃO TÉCNICO-OPERACIONAL DOS TERMINAIS RODOVIÁRIOS CONCEDIDOS À SOCICAM - ADMINISTRAÇÃO, PROJETOS E REPRESENTAÇÕES LTDA", bold=True, size_pt=11, space_after=6)
        add_cover_p("CONTRATO Nº 1.041.080/08", bold=True, size_pt=11, space_after=4)
        add_cover_p(f"PROCESSO SEI Nº {self.processo_sei_prev}", bold=True, size_pt=11, space_after=6)
        add_cover_p("", bold=False, size_pt=11, space_after=6)
        add_cover_p("Recife, data de assinatura eletrônica", bold=False, size_pt=11, space_after=0)

    def gerar_secoes_monitoramento(self, doc: Any, row: Any, nc_df: Any, total_achados: int, documento_anterior: Any = None) -> None:
        """Gera as Seções 1 a 4 com suporte de auditoria em memória e templates modulares."""
        from utils import adicionar_titulo_secao, formatar_data_extenso, formatar_mes_ano

        meta = extrair_metadados_anterior(documento_anterior)
        N_curr = meta.n_curr if meta.n_curr else self.N_curr
        ctr_num = meta.ctr_num if meta.ctr_num != "XX/XXXX" else self.ctr_num
        n_curr_str = f"{N_curr}º"

        data_extenso = formatar_data_extenso(row["Data"])
        try:
            data_vistoria = pd.to_datetime(row["Data"], dayfirst=True).strftime("%d/%m/%Y")
        except Exception:
            data_vistoria = "XX/XX/XXXX"

        id_fisc = str(row.get("ID da Fiscalização", "")).strip() if hasattr(row, "get") else str(row["ID da Fiscalização"]).strip()
        mes_ano_cap = formatar_mes_ano(row["Data"]).upper()

        if nc_df is not None and not nc_df.empty and "ID da Fiscalização" in nc_df.columns:
            current_ncs = nc_df[nc_df["ID da Fiscalização"].astype(str).str.strip() == id_fisc].copy()
            if "Não Conformidade" in current_ncs.columns:
                ncs_reais = current_ncs[
                    current_ncs["Não Conformidade"].fillna("").astype(str).str.strip() != ""
                ].copy()
            else:
                ncs_reais = pd.DataFrame()
        else:
            ncs_reais = pd.DataFrame()

        def add_p(text: str, bold: bool = False):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.line_spacing = 1.15
            run = p.add_run(text)
            run.font.name = "Aptos"
            run.font.size = Pt(11)
            run.bold = bold
            return p

        def add_label_text(label: str, text: str):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.15
            run_l = p.add_run(label)
            run_l.bold = True
            run_l.font.name = "Aptos"
            run_l.font.size = Pt(11)
            run_t = p.add_run(text)
            run_t.font.name = "Aptos"
            run_t.font.size = Pt(11)
            return p

        # 1. INTRODUÇÃO
        adicionar_titulo_secao(doc, "1. INTRODUÇÃO")
        doc.add_paragraph()
        for p_runs in get_socicam_monitoramento_intro_paragraphs(n_curr_str, ctr_num, data_extenso):
            add_p(p_runs[0][0])

        # 2. OBJETIVO
        adicionar_titulo_secao(doc, "2. OBJETIVO")
        doc.add_paragraph()
        for p_runs in get_socicam_monitoramento_objective_paragraphs(n_curr_str, ctr_num):
            add_p(p_runs[0][0])

        # 3. RESULTADO DAS VISTORIAS
        adicionar_titulo_secao(doc, "3. RESULTADO DAS VISTORIAS DAS NÃO CONFORMIDADES")
        doc.add_paragraph()
        add_p(
            f"Estão registrados para cada Terminal Rodoviário os resultados da verificação pela ARPE das ações desenvolvidas pela SOCICAM, "
            f"visando solucionar as Não Conformidades apresentadas no Relatório de Fiscalização Técnico-Operacional ARPE/CTR nº {ctr_num}."
        )

        if ncs_reais.empty:
            add_p("Nenhuma Não Conformidade registrada para este monitoramento.")
        else:
            for sub_idx, (_, nc_row) in enumerate(ncs_reais.iterrows(), 1):
                term_val = str(nc_row.get("Terminal", nc_row.get("Local", "TIP"))).strip()
                term_name = normalizar_nome_terminal_rodoviario(term_val).upper()

                sub_title = f"3.{sub_idx} – {term_name}"
                adicionar_titulo_secao(doc, sub_title)
                doc.add_paragraph()

                ident = str(nc_row.get("Identificação", "")).strip()
                nc_desc = str(nc_row.get("Não Conformidade", "")).strip()
                observacoes = str(nc_row.get("Observações", nc_row.get("Legenda da Foto", ""))).strip()
                determinacao = str(nc_row.get("Determinação", "")).strip()
                analise_arpe = str(nc_row.get("Análise ARPE", "")).strip()
                situacao = str(nc_row.get("Situação", "Pendente")).strip()

                title_text = f"Não Conformidade {ident} - {nc_desc}" if ident and not ident.lower().startswith("foto") else (nc_desc if nc_desc else "Não Conformidade")
                add_p(title_text, bold=True)

                add_label_text("Informação da SOCICAM: ", determinacao if determinacao else "A ser preenchido.")
                add_label_text("Constatação: ", observacoes if observacoes else "A ser preenchido.")

                if analise_arpe:
                    texto_analise = analise_arpe
                elif situacao:
                    texto_analise = f"Não Conformidade {situacao.upper()}."
                else:
                    texto_analise = "A ser preenchido."

                add_label_text("Análise da ARPE: ", texto_analise)
                doc.add_paragraph()

        # 4. RESUMO DA SITUAÇÃO
        adicionar_titulo_secao(doc, f"4. RESUMO DA SITUAÇÃO DAS NÃO CONFORMIDADES MONITORADAS ({mes_ano_cap})")
        doc.add_paragraph()
        add_p(
            f"Apresenta-se no Quadro 1, a seguir, um resumo da situação das Não Conformidades pendentes do Relatório ARPE/CTR nº {ctr_num}, "
            f"de acordo com as vistorias técnicas realizadas em {data_vistoria}, dando continuidade ao monitoramento das respectivas soluções."
        )

    @property
    def quadros_section_title(self) -> str:
        return ""

    def render_quadros(self, doc: Any, row: Any, nc_df: Any, criar_tabela_quadros_fn: Any) -> None:
        """Renderiza o Quadro 1 de monitoramento da SOCICAM com 3 colunas."""
        id_fisc = str(row.get("ID da Fiscalização", "")).strip() if hasattr(row, "get") else str(row["ID da Fiscalização"]).strip()
        ctr_num = getattr(self, "ctr_num", "04/2025")

        current_ncs = nc_df[nc_df["ID da Fiscalização"].astype(str).str.strip() == id_fisc] if nc_df is not None and not nc_df.empty and "ID da Fiscalização" in nc_df.columns else pd.DataFrame()
        ncs_reais = pd.DataFrame()
        if not current_ncs.empty and "Não Conformidade" in current_ncs.columns:
            ncs_reais = current_ncs[
                current_ncs["Não Conformidade"].fillna("").astype(str).str.strip() != ""
            ].copy()

        # Título do Quadro 1
        p_q = doc.add_paragraph()
        p_q.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_q.paragraph_format.space_after = Pt(6)
        r_q1 = p_q.add_run("QUADRO 1")
        r_q1.bold = True
        r_q1.font.name = "Aptos"
        r_q1.font.size = Pt(11)
        r_q2 = p_q.add_run(f" – Resumo da Situação das Não Conformidades Relatório ARPE/CTR Nº {ctr_num}")
        r_q2.bold = True
        r_q2.font.name = "Aptos"
        r_q2.font.size = Pt(11)

        # Usar serviço tipado
        doc_anterior = getattr(self, "documento_anterior", None)
        itens_prev = extrair_linhas_quadro1_anterior(doc_anterior)
        ncs_from_prev = [{"id_nc": it.id_nc, "info_ou_constatacao": it.info_ou_constatacao} for it in itens_prev]

        headers = SOCICAM_MONITORAMENTO_QUADRO1_HEADERS
        col_widths = SOCICAM_MONITORAMENTO_QUADRO1_COL_WIDTHS
        criar_tabela_quadro1_monitoramento(doc, headers, ncs_from_prev, ncs_reais, col_widths)

        doc.add_paragraph()

    @property
    def finalizacao_sections_config(self) -> Dict[str, str]:
        return {"5": "conclusoes_monitoramento"}

    def get_conclusions_monitoramento_paragraphs(self, total_ncs: int, data_extenso: str) -> List[Any]:
        n_curr_str = f"{self.N_curr}º" if self.N_curr else "1º"
        ctr_num = getattr(self, "ctr_num", "04/2025")
        return get_socicam_monitoramento_conclusions_paragraphs(total_ncs, data_extenso, n_curr_str, ctr_num)

    def render_apendices(self, doc: Any, row: Any, ncs_reais: Any, pas_reais: Any, fotos_dir: Any, data_fisc: Any, ano: Any, criar_grade_fotos_fn: Any) -> None:
        from utils import adicionar_titulo_secao, formatar_mes_ano

        try:
            mes_ano = formatar_mes_ano(row["Data"]).upper()
        except Exception:
            mes_ano = "JULHO/2026"

        p_ap = adicionar_titulo_secao(doc, f"APÊNDICE ÚNICO - MEMORIAL FOTOGRÁFICO - VISTORIAS REALIZADAS EM {mes_ano}")
        p_ap.paragraph_format.page_break_before = True

        local_val = row.get("Local", "") if hasattr(row, "get") else row["Local"]
        if not local_val or str(local_val).strip() in ("", "=Local="):
            local_val = "Terminais Rodoviários"

        if ncs_reais is not None and not ncs_reais.empty:
            criar_grade_fotos_fn(doc, ncs_reais, local_val, fotos_dir, data_fisc, self.key)
        else:
            p_empty = doc.add_paragraph()
            r_empty = p_empty.add_run("Nenhuma foto de não conformidade anexada.")
            r_empty.font.name = "Aptos"
            r_empty.font.size = Pt(11)
