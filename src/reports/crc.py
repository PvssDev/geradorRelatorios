# -*- coding: utf-8 -*-
"""
Especialização do Relatório para a Concessionária Rota dos Coqueiros (CRC - Paiva).
Contrato de Concessão Patrocinada CGPE – 001/2006 (PE-024).
Implementa os contratos do core e utiliza templates modulares padronizados da SEPLAG/CPPPE.
"""
from typing import Any, Dict, List, Optional, Tuple
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import pandas as pd

from reports.base import BaseReport
from core.interfaces.report_contracts import IReportContract
from core.rules.crc_rules import (
    classificar_achados_crc,
    separar_achados_df_crc,
    formatar_extenso_feminino_achados,
)
from reports.templates.crc_templates import (
    CRC_KEY,
    CRC_DISPLAY_NAME,
    CRC_DEFAULT_CONTRATO,
    CRC_CAPA_ORGAO_CONCEDENTE,
    CRC_CAPA_SECRETARIA,
    CRC_CAPA_TITULO,
    CRC_CAPA_CTR_NUMBER_TEMPLATE,
    CRC_CAPA_PRESTADOR_LABEL,
    CRC_CAPA_CONTRATO_LABEL,
    CRC_CAPA_REGULADOR_LABEL,
    CRC_ANALYST_TITLE,
    CRC_CAPA_TITULOS,
    CRC_ABBREVIATIONS,
    CRC_BASE_SUMARIO_LINHAS,
    get_crc_intro_paragraphs,
    CRC_OBJECTIVE_PARAGRAPHS,
    get_crc_general_info_rows,
    get_crc_methodology_paragraphs,
    CRC_REFERENCES_BULLETS,
    CRC_REFERENCES_LEFT_INDENT_PT,
    CRC_POST_METHODOLOGY_PARAGRAPHS,
    CRC_LEVELS_DATA,
    get_crc_quadro_intro_paragraphs,
    CRC_NC_TABLE_HEADERS,
    CRC_PEDESTRIAN_SAFETY_NOTE,
    get_crc_conclusions_paragraphs,
)


class CrcReport(BaseReport, IReportContract):
    """Relatório Técnico-Operacional de Fiscalização da Concessionária Rota dos Coqueiros (CRC)."""

    @property
    def key(self) -> str:
        return CRC_KEY

    @property
    def display_name(self) -> str:
        return CRC_DISPLAY_NAME

    @property
    def default_contrato(self) -> str:
        return CRC_DEFAULT_CONTRATO

    @property
    def capa_orgao_concedente(self) -> str:
        return CRC_CAPA_ORGAO_CONCEDENTE

    @property
    def capa_secretaria(self) -> str:
        return CRC_CAPA_SECRETARIA

    @property
    def capa_titulo(self) -> str:
        return CRC_CAPA_TITULO

    @property
    def capa_ctr_number_template(self) -> str:
        return CRC_CAPA_CTR_NUMBER_TEMPLATE

    @property
    def capa_prestador_label(self) -> str:
        return CRC_CAPA_PRESTADOR_LABEL

    @property
    def capa_contrato_label(self) -> str:
        return CRC_CAPA_CONTRATO_LABEL

    @property
    def capa_regulador_label(self) -> str:
        return CRC_CAPA_REGULADOR_LABEL

    @property
    def analyst_title(self) -> str:
        return CRC_ANALYST_TITLE

    def get_capa_titulos(self, row: Any, ano: str) -> List[str]:
        return list(CRC_CAPA_TITULOS)

    @property
    def sumario_before_abreviaturas(self) -> bool:
        """No CRC Fiscalização, o Sumário antecede a lista de Abreviaturas."""
        return True

    def get_abbreviations(self) -> List[Tuple[str, str]]:
        return list(CRC_ABBREVIATIONS)

    def get_sumario_linhas(self, row: Any, nc_df: Any = None) -> List[str]:
        linhas = list(CRC_BASE_SUMARIO_LINHAS)
        id_fisc = str(row.get("ID da Fiscalização", "")).strip() if hasattr(row, "get") else str(row["ID da Fiscalização"]).strip()
        resumo = classificar_achados_crc(nc_df, id_fisc=id_fisc)

        if resumo.ambos_presentes:
            linhas.append("\tAPÊNDICE A – REGISTROS FOTOGRÁFICOS DAS NÃO CONFORMIDADES\t12")
            linhas.append("\tAPÊNDICE B – REGISTROS FOTOGRÁFICOS DOS PONTOS DE ATENÇÃO\t12")
        else:
            linhas.append("\tAPÊNDICE ÚNICO - MEMORIAL FOTOGRÁFICO - FISCALIZAÇÃO\t12")
        return linhas

    def get_intro_paragraphs(self, row: Any, ano: str, data_extenso: str) -> List[Any]:
        return get_crc_intro_paragraphs(str(ano))

    def get_objective_paragraphs(self, row: Any) -> List[Any]:
        return list(CRC_OBJECTIVE_PARAGRAPHS)

    def get_general_info_rows(self, row: Any, responsaveis_formatted: str, periodo_val: str) -> List[Any]:
        return get_crc_general_info_rows(responsaveis_formatted, periodo_val)

    @property
    def general_info_col_widths(self) -> List[Any]:
        return [Inches(2.3), Inches(5.2)]

    @property
    def general_info_headers_indices(self) -> List[int]:
        return [0, 4, 8, 13]

    def get_methodology_paragraphs(self, data_extenso: str) -> List[Any]:
        return get_crc_methodology_paragraphs(data_extenso)

    def get_references_bullets(self) -> List[Any]:
        return list(CRC_REFERENCES_BULLETS)

    @property
    def references_left_indent_pt(self) -> float:
        return CRC_REFERENCES_LEFT_INDENT_PT

    def get_post_methodology_paragraphs(self, total_ncs: int) -> List[Any]:
        return list(CRC_POST_METHODOLOGY_PARAGRAPHS)

    def get_levels_data(self) -> Dict[str, Any]:
        return dict(CRC_LEVELS_DATA)

    def get_post_metodologia_extra_paragraphs(self, row: Any, data_extenso: str, total_achados: int) -> Tuple[Any, List[Any]]:
        return (None, [])

    @property
    def quadros_section_title(self) -> str:
        return "5. FISCALIZAÇÃO"

    def get_quadro_intro_paragraphs(self, row: Any, data_extenso: str, responsaveis_formatted: str) -> List[Any]:
        return get_crc_quadro_intro_paragraphs(data_extenso)

    @property
    def quadro_title_template(self) -> str:
        return "QUADRO 1 – NÃO CONFORMIDADES IDENTIFICADAS CRC - {data_abreviada}"

    @property
    def nc_table_headers(self) -> List[str]:
        return list(CRC_NC_TABLE_HEADERS)

    @property
    def nc_table_col_widths(self) -> List[Any]:
        return [Inches(1.34), Inches(1.68), Inches(0.81), Inches(2.46), Inches(0.98)]

    def format_nc_table_total_row(self, table: Any, row_idx: int, total_ncs: int, col_widths: Optional[List[Any]] = None) -> None:
        r_total = table.rows[row_idx]
        r_total.cells[0].merge(r_total.cells[1]).merge(r_total.cells[2])
        r_total.cells[0].text = "TOTAL"
        r_total.cells[3].text = ""
        r_total.cells[4].text = str(total_ncs)

        widths = col_widths if col_widths is not None else self.nc_table_col_widths
        r_total.cells[0].width = widths[0] + widths[1] + widths[2]
        r_total.cells[3].width = widths[3]
        r_total.cells[4].width = widths[4]

    def render_quadros(self, doc: Any, row: Any, nc_df: Any, criar_tabela_quadros_fn: Any) -> None:
        from utils import formatar_data_extenso, formatar_data_curta, adicionar_titulo_secao
        data_extenso = formatar_data_extenso(row["Data"])
        data_abreviada = formatar_data_curta(row.get("Data", "") if hasattr(row, "get") else row["Data"])

        # 1. Título da Seção
        adicionar_titulo_secao(doc, self.quadros_section_title)
        doc.add_paragraph()

        # 2. Parágrafos introdutórios
        for p_runs in self.get_quadro_intro_paragraphs(row, data_extenso, ""):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.line_spacing = 1.15
            for text, bold, italic, _ in p_runs:
                run = p.add_run(text)
                run.font.name = 'Aptos'
                run.font.size = Pt(11)
                run.bold = bold
                run.italic = italic

        doc.add_paragraph()

        id_fisc = str(row.get("ID da Fiscalização", "")).strip() if hasattr(row, "get") else str(row["ID da Fiscalização"]).strip()
        ncs_reais, pas_reais, resumo = separar_achados_df_crc(nc_df, id_fisc=id_fisc)

        # 3. Quadro 1
        p7 = doc.add_paragraph()
        p7.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p7.paragraph_format.space_after = Pt(6)
        r7_1 = p7.add_run("QUADRO 1")
        r7_1.bold = True
        r7_1.font.name = 'Aptos'
        r7_1.font.size = Pt(11)

        if resumo.tem_nc or (not resumo.tem_nc and not resumo.tem_pa):
            r7_2 = p7.add_run(f" – NÃO CONFORMIDADES IDENTIFICADAS CRC - {data_abreviada}")
            r7_2.bold = True
            r7_2.font.name = 'Aptos'
            r7_2.font.size = Pt(11)
            criar_tabela_quadros_fn(doc, ncs_reais, is_pa=False, report_config=self)
            doc.add_paragraph()

            if resumo.ambos_presentes:
                p_q2 = doc.add_paragraph()
                p_q2.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_q2.paragraph_format.space_after = Pt(6)
                r_q2_1 = p_q2.add_run("QUADRO 2")
                r_q2_1.bold = True
                r_q2_1.font.name = 'Aptos'
                r_q2_1.font.size = Pt(11)
                r_q2_2 = p_q2.add_run(f" – PONTOS DE ATENÇÃO IDENTIFICADOS CRC - {data_abreviada}")
                r_q2_2.bold = True
                r_q2_2.font.name = 'Aptos'
                r_q2_2.font.size = Pt(11)
                criar_tabela_quadros_fn(doc, pas_reais, is_pa=True, report_config=self)
                doc.add_paragraph()
        elif resumo.tem_pa:
            r7_2 = p7.add_run(f" – PONTOS DE ATENÇÃO IDENTIFICADOS CRC - {data_abreviada}")
            r7_2.bold = True
            r7_2.font.name = 'Aptos'
            r7_2.font.size = Pt(11)
            criar_tabela_quadros_fn(doc, pas_reais, is_pa=True, report_config=self)
            doc.add_paragraph()

        # 4. Nota de segurança de pedestres
        p8 = doc.add_paragraph()
        p8.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p8.paragraph_format.space_before = Pt(6)
        p8.paragraph_format.space_after = Pt(6)
        p8.paragraph_format.line_spacing = 1.15
        run8 = p8.add_run(CRC_PEDESTRIAN_SAFETY_NOTE)
        run8.font.name = 'Aptos'
        run8.font.size = Pt(11)

    @property
    def finalizacao_sections_config(self) -> Dict[str, str]:
        return {"6": "conclusões"}

    def get_determinations_paragraphs(self, total_ncs: int) -> List[Any]:
        return []

    def get_recommendations_paragraphs(self) -> List[Any]:
        return []

    def get_conclusions_paragraphs(self, total_ncs: int, local_val: str) -> List[Any]:
        extenso_com_parenteses = formatar_extenso_feminino_achados(total_ncs)
        return get_crc_conclusions_paragraphs(extenso_com_parenteses)

    def render_apendices(
        self,
        doc: Any,
        row: Any,
        ncs_reais: Any,
        pas_reais: Any,
        fotos_dir: str,
        data_fisc: str,
        ano: str,
        criar_grade_fotos_fn: Any
    ) -> None:
        from utils import adicionar_titulo_secao, extrair_mes_ano_numerico
        ambos_presentes = not ncs_reais.empty and not pas_reais.empty
        tem_nc = not ncs_reais.empty
        tem_pa = not pas_reais.empty
        mes_ano = extrair_mes_ano_numerico(row.get("Data", "") if hasattr(row, "get") else row["Data"])
        local_val = row.get("Local", "") if hasattr(row, "get") else row["Local"]

        if ambos_presentes:
            p_ap_a = adicionar_titulo_secao(doc, f"APÊNDICE A – REGISTROS FOTOGRÁFICOS DAS NÃO CONFORMIDADES EM {data_fisc}")
            p_ap_a.paragraph_format.page_break_before = True

            p_intro_fotos = doc.add_paragraph()
            p_intro_fotos.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p_intro_fotos.paragraph_format.space_before = Pt(6)
            p_intro_fotos.paragraph_format.space_after = Pt(12)
            p_intro_fotos.paragraph_format.line_spacing = 1.15
            run_intro_fotos = p_intro_fotos.add_run(
                f"Estão evidenciadas a seguir as Não Conformidades apontadas neste Relatório de Fiscalização Técnico-Operacional "
                f"ARPE/CTR Nº {mes_ano}."
            )
            run_intro_fotos.font.name = 'Aptos'
            run_intro_fotos.font.size = Pt(11)

            criar_grade_fotos_fn(doc, ncs_reais, local_val, fotos_dir, data_fisc, self.key)

            p_ap_b = adicionar_titulo_secao(doc, f"APÊNDICE B – REGISTROS FOTOGRÁFICOS DOS PONTOS DE ATENÇÃO EM {data_fisc}")
            p_ap_b.paragraph_format.page_break_before = True

            p_intro_pas = doc.add_paragraph()
            p_intro_pas.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p_intro_pas.paragraph_format.space_before = Pt(6)
            p_intro_pas.paragraph_format.space_after = Pt(12)
            p_intro_pas.paragraph_format.line_spacing = 1.15
            run_intro_pas = p_intro_pas.add_run(
                f"Estão evidenciados a seguir os Pontos de Atenção apontados neste Relatório de Fiscalização Técnico-Operacional "
                f"ARPE/CTR Nº {mes_ano}."
            )
            run_intro_pas.font.name = 'Aptos'
            run_intro_pas.font.size = Pt(11)

            criar_grade_fotos_fn(doc, pas_reais, local_val, fotos_dir, data_fisc, self.key)
        else:
            p_ap_u = adicionar_titulo_secao(doc, f"APÊNDICE ÚNICO - MEMORIAL FOTOGRÁFICO - FISCALIZAÇÃO EM {data_fisc}")
            p_ap_u.paragraph_format.page_break_before = True

            p_intro_fotos = doc.add_paragraph()
            p_intro_fotos.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p_intro_fotos.paragraph_format.space_before = Pt(6)
            p_intro_fotos.paragraph_format.space_after = Pt(12)
            p_intro_fotos.paragraph_format.line_spacing = 1.15

            if tem_pa and not tem_nc:
                tipo_txt = "os Pontos de Atenção apontados"
                df_render = pas_reais
            else:
                tipo_txt = "as Não Conformidades apontadas"
                df_render = ncs_reais

            run_intro_fotos = p_intro_fotos.add_run(
                f"Estão evidenciadas a seguir {tipo_txt} neste Relatório de Fiscalização Técnico-Operacional "
                f"ARPE/CTR Nº {mes_ano}."
            )
            run_intro_fotos.font.name = 'Aptos'
            run_intro_fotos.font.size = Pt(11)

            if not df_render.empty:
                criar_grade_fotos_fn(doc, df_render, local_val, fotos_dir, data_fisc, self.key)
            else:
                p_empty = doc.add_paragraph()
                r_empty = p_empty.add_run("Nenhum registro fotográfico cadastrado.")
                r_empty.font.name = 'Aptos'
                r_empty.font.size = Pt(11)

    def get_process_sei_texts(self, row: Any, ano: Optional[str] = None) -> List[str]:
        from utils import extrair_mes_ano_numerico, extrair_ano
        if isinstance(row, (str, int)) and ano is None:
            ano = str(row)
            mes_ano = f"01/{ano}"
        else:
            data_val = row.get("Data", "") if hasattr(row, "get") else (row["Data"] if isinstance(row, dict) or hasattr(row, "__getitem__") else "")
            ano = ano or extrair_ano(data_val)
            mes_ano = extrair_mes_ano_numerico(data_val)
        return [
            f"RELATÓRIO DE FISCALIZAÇÃO TÉCNICO-OPERACIONAL PROC ADM Nº {mes_ano} - CTR",
            "SEI Nº xxxxxxxx-xxx"
        ]
