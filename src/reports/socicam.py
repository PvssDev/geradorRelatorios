# -*- coding: utf-8 -*-
"""
Especialização do Relatório para a Concessionária SOCICAM (Terminais Rodoviários).
Contrato de Concessão de Serviço Público Nº 1.041.080/08 (TIP, Caruaru, Garanhuns, Petrolina).
Implementa os contratos do core e utiliza templates modulares padronizados.
"""
from typing import Any, Dict, List, Optional, Tuple
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import pandas as pd

from reports.base import BaseReport
from core.interfaces.report_contracts import IReportContract
from core.rules.socicam_rules import (
    normalizar_nome_terminal_rodoviario,
    normalizar_nome_terminal_curto,
    extrair_sigla_terminal,
    formatar_extenso_achados_socicam,
    formatar_frase_conclusao_achados_socicam,
    classificar_achados_socicam,
    separar_achados_df_socicam,
)
from reports.templates.socicam_templates import (
    SOCICAM_KEY,
    SOCICAM_DISPLAY_NAME,
    SOCICAM_DEFAULT_CONTRATO,
    SOCICAM_CAPA_ORGAO_CONCEDENTE,
    SOCICAM_CAPA_SECRETARIA,
    SOCICAM_CAPA_TITULO,
    SOCICAM_CAPA_CTR_NUMBER_TEMPLATE,
    SOCICAM_CAPA_PRESTADOR_LABEL,
    SOCICAM_CAPA_CONTRATO_LABEL,
    SOCICAM_CAPA_REGULADOR_LABEL,
    SOCICAM_ANALYST_TITLE,
    SOCICAM_ABBREVIATIONS,
    SOCICAM_BASE_SUMARIO_LINHAS,
    SOCICAM_GENERAL_INFO_COL_WIDTHS,
    SOCICAM_GENERAL_INFO_HEADERS_INDICES,
    SOCICAM_METHODOLOGY_PARAGRAPHS,
    SOCICAM_REFERENCES_BULLETS,
    SOCICAM_REFERENCES_LEFT_INDENT_PT,
    SOCICAM_POST_METHODOLOGY_PARAGRAPHS,
    SOCICAM_QUADROS_SECTION_TITLE,
    SOCICAM_QUADRO_TITLE_TEMPLATE,
    SOCICAM_NC_TABLE_HEADERS,
    SOCICAM_FINALIZACAO_SECTIONS_CONFIG,
    SOCICAM_RECOMMENDATIONS_PARAGRAPHS,
    get_socicam_capa_titulos,
    get_socicam_intro_paragraphs,
    get_socicam_objective_paragraphs,
    get_socicam_general_info_rows,
    get_socicam_quadro_intro_paragraphs,
    get_socicam_determinations_paragraphs,
    get_socicam_conclusions_paragraphs,
)


def _obter_terminal_rodoviario_nome(local_val: Any) -> str:
    """Função legada para compatibilidade retroativa, delega para socicam_rules."""
    return normalizar_nome_terminal_rodoviario(local_val)


def _obter_terminal_de_nome(local_val: Any) -> str:
    """Função legada para compatibilidade retroativa, delega para socicam_rules."""
    return normalizar_nome_terminal_curto(local_val)


class SocicamReport(BaseReport, IReportContract):
    """Relatório Técnico-Operacional de Fiscalização de Terminais Rodoviários (SOCICAM)."""

    @property
    def key(self) -> str:
        return SOCICAM_KEY

    @property
    def display_name(self) -> str:
        return SOCICAM_DISPLAY_NAME

    @property
    def default_contrato(self) -> str:
        return SOCICAM_DEFAULT_CONTRATO

    @property
    def capa_orgao_concedente(self) -> str:
        return SOCICAM_CAPA_ORGAO_CONCEDENTE

    @property
    def capa_secretaria(self) -> str:
        return SOCICAM_CAPA_SECRETARIA

    @property
    def capa_titulo(self) -> str:
        return SOCICAM_CAPA_TITULO

    @property
    def capa_ctr_number_template(self) -> str:
        return SOCICAM_CAPA_CTR_NUMBER_TEMPLATE

    @property
    def capa_prestador_label(self) -> str:
        return SOCICAM_CAPA_PRESTADOR_LABEL

    @property
    def capa_contrato_label(self) -> str:
        return SOCICAM_CAPA_CONTRATO_LABEL

    @property
    def capa_regulador_label(self) -> str:
        return SOCICAM_CAPA_REGULADOR_LABEL

    @property
    def analyst_title(self) -> str:
        return SOCICAM_ANALYST_TITLE

    def get_capa_titulos(self, row: Any, ano: str) -> List[str]:
        local_val = str(row.get("Local", "TIP")).upper() if hasattr(row, "get") else str(row["Local"]).upper()
        return get_socicam_capa_titulos(local_val)

    @property
    def sumario_before_abreviaturas(self) -> bool:
        return True

    def get_abbreviations(self) -> List[Tuple[str, str]]:
        return list(SOCICAM_ABBREVIATIONS)

    def get_sumario_linhas(self, row: Any, nc_df: Any = None) -> List[str]:
        local_val = row.get("Local", "TIP") if hasattr(row, "get") else row["Local"]
        local_sigla = extrair_sigla_terminal(local_val)
        linhas = list(SOCICAM_BASE_SUMARIO_LINHAS)

        id_fisc = str(row.get("ID da Fiscalização", "")).strip() if hasattr(row, "get") else str(row["ID da Fiscalização"]).strip()
        resumo = classificar_achados_socicam(nc_df, id_fisc=id_fisc)

        if resumo.ambos_presentes:
            linhas.append(f"\tAPÊNDICE A - REGISTROS FOTOGRÁFICOS DAS NÃO CONFORMIDADES APONTADAS PARA O {local_sigla}\t7")
            linhas.append(f"\tAPÊNDICE B - REGISTROS FOTOGRÁFICOS DOS PONTOS DE ATENÇÃO APONTADOS PARA O {local_sigla}\t7")
        else:
            linhas.append(f"\tAPÊNDICE ÚNICO - MEMORIAL FOTOGRÁFICO - FISCALIZAÇÃO NO {local_sigla}\t7")

        return linhas

    def get_intro_paragraphs(self, row: Any, ano: str, data_extenso: str) -> List[Any]:
        local_val = row.get("Local", "Terminal Rodoviário de Passageiros do Recife (TIP)") if hasattr(row, "get") else row["Local"]
        terminal_nome = normalizar_nome_terminal_rodoviario(local_val)
        return get_socicam_intro_paragraphs(terminal_nome)

    def get_objective_paragraphs(self, row: Any) -> List[Any]:
        local_val = row.get("Local", "Terminal Rodoviário de Passageiros do Recife (TIP)") if hasattr(row, "get") else row["Local"]
        terminal_nome = normalizar_nome_terminal_rodoviario(local_val)
        return get_socicam_objective_paragraphs(terminal_nome)

    def get_general_info_rows(self, row: Any, responsaveis_formatted: str, periodo_val: str) -> List[Any]:
        return get_socicam_general_info_rows(responsaveis_formatted, periodo_val)

    @property
    def general_info_col_widths(self) -> List[Any]:
        return list(SOCICAM_GENERAL_INFO_COL_WIDTHS)

    @property
    def general_info_headers_indices(self) -> List[int]:
        return list(SOCICAM_GENERAL_INFO_HEADERS_INDICES)

    def get_methodology_paragraphs(self, data_extenso: str) -> List[Any]:
        return list(SOCICAM_METHODOLOGY_PARAGRAPHS)

    def get_references_bullets(self) -> List[Any]:
        return list(SOCICAM_REFERENCES_BULLETS)

    @property
    def references_left_indent_pt(self) -> float:
        return SOCICAM_REFERENCES_LEFT_INDENT_PT

    def get_post_methodology_paragraphs(self, total_ncs: int) -> List[Any]:
        return list(SOCICAM_POST_METHODOLOGY_PARAGRAPHS)

    def get_levels_data(self) -> Optional[Dict[str, Any]]:
        return None

    def get_post_metodologia_extra_paragraphs(self, row: Any, data_extenso: str, total_achados: int) -> Tuple[Any, List[Any]]:
        return (None, [])

    @property
    def quadros_section_title(self) -> str:
        return SOCICAM_QUADROS_SECTION_TITLE

    def get_quadro_intro_paragraphs(self, row: Any, data_extenso: str, responsaveis_formatted: str) -> List[Any]:
        raw_resp = row.get("Pessoal Responsável", "") if hasattr(row, "get") else row["Pessoal Responsável"]
        if pd.isna(raw_resp) or str(raw_resp).strip().lower() in ["", "nan", "none"]:
            responsaveis_list = []
        else:
            responsaveis_list = [
                r.strip() for r in str(raw_resp).split(",")
                if r.strip() and r.strip().lower() not in ["nan", "none"]
            ]
        from database.manager import carregar_responsaveis
        db_resp = carregar_responsaveis()

        team_runs = []
        for idx, nome in enumerate(responsaveis_list):
            match = next((d for d in db_resp if d["nome"].strip().lower() == nome.lower()), None)
            matricula = match["matricula"] if match else "xxxxxxx/xx"
            nome_real = match["nome"] if match else nome

            if idx > 0:
                if idx == len(responsaveis_list) - 1:
                    team_runs.append((" e ", False, False, None))
                else:
                    team_runs.append((", ", False, False, None))
            team_runs.append((nome_real, True, False, None))
            team_runs.append((f" (matrícula nº {matricula})", False, False, None))

        local_val = str(row.get("Local", "Terminal Rodoviário de Passageiros do Recife (TIP)")) if hasattr(row, "get") else str(row["Local"])
        return get_socicam_quadro_intro_paragraphs(data_extenso, team_runs, local_val)

    @property
    def quadro_title_template(self) -> str:
        return SOCICAM_QUADRO_TITLE_TEMPLATE

    @property
    def nc_table_headers(self) -> List[str]:
        return list(SOCICAM_NC_TABLE_HEADERS)

    @property
    def nc_table_col_widths(self) -> List[Any]:
        return [Inches(1.24), Inches(1.62), Inches(1.26), Inches(1.69), Inches(2.25)]

    def format_nc_table_total_row(self, table: Any, row_idx: int, total_ncs: int, col_widths: Optional[List[Any]] = None) -> None:
        r_total = table.rows[row_idx]
        r_total.cells[0].merge(r_total.cells[1]).merge(r_total.cells[2]).merge(r_total.cells[3])
        r_total.cells[0].text = "TOTAL"
        r_total.cells[4].text = str(total_ncs)

        widths = col_widths if col_widths is not None else self.nc_table_col_widths
        r_total.cells[0].width = widths[0] + widths[1] + widths[2] + widths[3]
        r_total.cells[4].width = widths[4]

    def render_quadros(self, doc: Any, row: Any, nc_df: Any, criar_tabela_quadros_fn: Any) -> None:
        from utils import formatar_data_extenso, adicionar_titulo_secao

        data_extenso = formatar_data_extenso(row["Data"])

        # 1. Título da Seção
        adicionar_titulo_secao(doc, self.quadros_section_title)
        doc.add_paragraph()

        # 2. Parágrafos introdutórios (todos em negrito para SOCICAM)
        intro_paragraphs = self.get_quadro_intro_paragraphs(row, data_extenso, "")
        for paragraph_runs in intro_paragraphs:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.line_spacing = 1.15
            for text, bold, italic, _ in paragraph_runs:
                run = p.add_run(text)
                run.font.name = "Aptos"
                run.font.size = Pt(11)
                if bold:
                    run.bold = True
                if italic:
                    run.italic = True

        doc.add_paragraph()

        # Obter dados de NC via separador otimizado em O(N)
        id_fisc = str(row.get("ID da Fiscalização", "")).strip() if hasattr(row, "get") else str(row["ID da Fiscalização"]).strip()
        ncs_reais, pas_reais, resumo = separar_achados_df_socicam(nc_df, id_fisc=id_fisc)

        local_val = str(row.get("Local", "Terminal Rodoviário de Passageiros do Recife (TIP)")) if hasattr(row, "get") else str(row["Local"])

        ambos_presentes = resumo.ambos_presentes
        tem_nc = resumo.tem_nc
        tem_pa = resumo.tem_pa

        if tem_nc or (not tem_nc and not tem_pa):
            # Quadro 1
            p7 = doc.add_paragraph()
            p7.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p7.paragraph_format.space_after = Pt(6)
            r7_1 = p7.add_run("Quadro 1")
            r7_1.bold = True
            r7_1.font.name = "Aptos"
            r7_1.font.size = Pt(11)
            r7_2 = p7.add_run(f" – Não Conformidades do {local_val}")
            r7_2.font.name = "Aptos"
            r7_2.font.size = Pt(11)

            criar_tabela_quadros_fn(doc, ncs_reais, is_pa=False, report_config=self)
            doc.add_paragraph()

            if ambos_presentes:
                p_q2 = doc.add_paragraph()
                p_q2.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_q2.paragraph_format.space_after = Pt(6)
                r_q2_1 = p_q2.add_run("Quadro 2")
                r_q2_1.bold = True
                r_q2_1.font.name = "Aptos"
                r_q2_1.font.size = Pt(11)
                r_q2_2 = p_q2.add_run(f" – Pontos de Atenção do {local_val}")
                r_q2_2.font.name = "Aptos"
                r_q2_2.font.size = Pt(11)

                criar_tabela_quadros_fn(doc, pas_reais, is_pa=True, report_config=self)
                doc.add_paragraph()
        elif tem_pa:
            # Apenas Pontos de Atenção
            p7 = doc.add_paragraph()
            p7.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p7.paragraph_format.space_after = Pt(6)
            r7_1 = p7.add_run("Quadro 1")
            r7_1.bold = True
            r7_1.font.name = "Aptos"
            r7_1.font.size = Pt(11)
            r7_2 = p7.add_run(f" – Pontos de Atenção do {local_val}")
            r7_2.font.name = "Aptos"
            r7_2.font.size = Pt(11)

            criar_tabela_quadros_fn(doc, pas_reais, is_pa=True, report_config=self)
            doc.add_paragraph()

    @property
    def finalizacao_sections_config(self) -> Dict[str, str]:
        return dict(SOCICAM_FINALIZACAO_SECTIONS_CONFIG)

    def get_determinations_paragraphs(self, total_ncs: int) -> List[Any]:
        extenso_ncs = formatar_extenso_achados_socicam(total_ncs)
        return get_socicam_determinations_paragraphs(total_ncs, extenso_ncs)

    def get_recommendations_paragraphs(self) -> List[Any]:
        return list(SOCICAM_RECOMMENDATIONS_PARAGRAPHS)

    def get_conclusions_paragraphs(self, total_ncs: int, local_val: str) -> List[Any]:
        nc_frase = formatar_frase_conclusao_achados_socicam(total_ncs)
        terminal_curto = normalizar_nome_terminal_curto(local_val)
        return get_socicam_conclusions_paragraphs(nc_frase, terminal_curto)

    def render_apendices(self, doc: Any, row: Any, ncs_reais: Any, pas_reais: Any, fotos_dir: Any, data_fisc: Any, ano: Any, criar_grade_fotos_fn: Any) -> None:
        from utils import adicionar_titulo_secao

        local_val = row.get("Local", "TIP") if hasattr(row, "get") else row["Local"]
        local_sigla = extrair_sigla_terminal(local_val)

        ambos_presentes = not ncs_reais.empty and not pas_reais.empty
        tem_nc = not ncs_reais.empty
        tem_pa = not pas_reais.empty

        if ambos_presentes:
            p_ap_a = adicionar_titulo_secao(doc, f"APÊNDICE A - REGISTROS FOTOGRÁFICOS DAS NÃO CONFORMIDADES APONTADAS PARA O {local_sigla}")
            p_ap_a.paragraph_format.page_break_before = True

            criar_grade_fotos_fn(doc, ncs_reais, row.get("Local", "") if hasattr(row, "get") else row["Local"], fotos_dir, data_fisc, self.key)

            p_ap_b = adicionar_titulo_secao(doc, f"APÊNDICE B - REGISTROS FOTOGRÁFICOS DOS PONTOS DE ATENÇÃO APONTADOS PARA O {local_sigla}")
            p_ap_b.paragraph_format.page_break_before = True

            criar_grade_fotos_fn(doc, pas_reais, row.get("Local", "") if hasattr(row, "get") else row["Local"], fotos_dir, data_fisc, self.key)
        else:
            p_ap_a = adicionar_titulo_secao(doc, f"APÊNDICE ÚNICO - MEMORIAL FOTOGRÁFICO - FISCALIZAÇÃO NO {local_sigla}")
            p_ap_a.paragraph_format.page_break_before = True

            df_render = pas_reais if (tem_pa and not tem_nc) else ncs_reais
            if not df_render.empty:
                criar_grade_fotos_fn(doc, df_render, row.get("Local", "") if hasattr(row, "get") else row["Local"], fotos_dir, data_fisc, self.key)
            else:
                p_empty = doc.add_paragraph()
                r_empty = p_empty.add_run("Nenhum registro fotográfico cadastrado.")
                r_empty.font.name = "Aptos"
                r_empty.font.size = Pt(11)

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
            f"RELATÓRIO DE FISCALIZAÇÃO TÉCNICO-OPERACIONAL PROC ADM Nº {mes_ano} - CTR",
            "SEI Nº xxxxxxxx-xxx"
        ]
