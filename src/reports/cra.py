# -*- coding: utf-8 -*-
"""
Especialização do Relatório para a Concessionária Rota do Atlântico (CRA).
Contrato de Concessão CT. nº 043/2011 (Complexo Viário e Logístico de Suape – Expressway).
Implementa os contratos do core e utiliza templates modulares padronizados.
"""
from typing import Any, Dict, List, Optional, Tuple
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import pandas as pd

from reports.base import BaseReport
from core.interfaces.report_contracts import IReportContract
from core.rules.cra_rules import classificar_achados_cra, separar_achados_df_cra
from reports.templates.cra_templates import (
    CRA_KEY,
    CRA_DISPLAY_NAME,
    CRA_DEFAULT_CONTRATO,
    CRA_CAPA_ORGAO_CONCEDENTE,
    CRA_CAPA_SECRETARIA,
    CRA_CAPA_TITULO,
    CRA_CAPA_CTR_NUMBER_TEMPLATE,
    CRA_CAPA_PRESTADOR_LABEL,
    CRA_CAPA_CONTRATO_LABEL,
    CRA_CAPA_REGULADOR_LABEL,
    CRA_ANALYST_TITLE,
    CRA_CAPA_TITULOS,
    CRA_ABBREVIATIONS,
    CRA_BASE_SUMARIO_LINHAS,
    get_cra_intro_paragraphs,
    CRA_OBJECTIVE_PARAGRAPHS,
    get_cra_general_info_rows,
    get_cra_methodology_paragraphs,
    CRA_REFERENCES_BULLETS,
    CRA_POST_METHODOLOGY_PARAGRAPHS,
    CRA_LEVELS_DATA,
    CRA_QUADRO_INTRO_PARAGRAPHS,
    CRA_DETERMINATIONS_PARAGRAPHS,
    CRA_RECOMMENDATIONS_PARAGRAPHS,
    get_cra_conclusions_paragraphs,
)


class CraReport(BaseReport, IReportContract):
    """Relatório Técnico-Operacional de Fiscalização da Concessionária Rota do Atlântico (CRA)."""

    @property
    def key(self) -> str:
        return CRA_KEY

    @property
    def display_name(self) -> str:
        return CRA_DISPLAY_NAME

    @property
    def default_contrato(self) -> str:
        return CRA_DEFAULT_CONTRATO

    @property
    def capa_orgao_concedente(self) -> str:
        return CRA_CAPA_ORGAO_CONCEDENTE

    @property
    def capa_secretaria(self) -> str:
        return CRA_CAPA_SECRETARIA

    @property
    def capa_titulo(self) -> str:
        return CRA_CAPA_TITULO

    @property
    def capa_ctr_number_template(self) -> str:
        return CRA_CAPA_CTR_NUMBER_TEMPLATE

    @property
    def capa_prestador_label(self) -> str:
        return CRA_CAPA_PRESTADOR_LABEL

    @property
    def capa_contrato_label(self) -> str:
        return CRA_CAPA_CONTRATO_LABEL

    @property
    def capa_regulador_label(self) -> str:
        return CRA_CAPA_REGULADOR_LABEL

    @property
    def analyst_title(self) -> str:
        return CRA_ANALYST_TITLE

    def get_capa_titulos(self, row: Any, ano: str) -> List[str]:
        return list(CRA_CAPA_TITULOS)

    @property
    def sumario_before_abreviaturas(self) -> bool:
        return False

    def get_abbreviations(self) -> List[Tuple[str, str]]:
        return list(CRA_ABBREVIATIONS)

    def get_sumario_linhas(self, row: Any, nc_df: Any = None) -> List[str]:
        linhas = list(CRA_BASE_SUMARIO_LINHAS)
        id_fisc = str(row.get("ID da Fiscalização", "")).strip() if hasattr(row, "get") else str(row["ID da Fiscalização"]).strip()
        resumo = classificar_achados_cra(nc_df, id_fisc=id_fisc)

        if resumo.ambos_presentes:
            linhas.append("\tAPÊNDICE A – REGISTROS FOTOGRÁFICOS DAS NÃO CONFORMIDADES\t12")
            linhas.append("\tAPÊNDICE B – REGISTROS FOTOGRÁFICOS DOS PONTOS DE ATENÇÃO\t12")
        else:
            linhas.append("\tAPÊNDICE ÚNICO - MEMORIAL FOTOGRÁFICO - FISCALIZAÇÃO\t12")
        return linhas

    def get_intro_paragraphs(self, row: Any, ano: str, data_extenso: str) -> List[Any]:
        return get_cra_intro_paragraphs(str(ano), data_extenso)

    def get_objective_paragraphs(self, row: Any) -> List[Any]:
        return list(CRA_OBJECTIVE_PARAGRAPHS)

    def get_general_info_rows(self, row: Any, responsaveis_formatted: str, periodo_val: str) -> List[Any]:
        return get_cra_general_info_rows(responsaveis_formatted, periodo_val)

    @property
    def general_info_col_widths(self) -> List[Any]:
        return [Inches(2.3), Inches(5.2)]

    @property
    def general_info_headers_indices(self) -> List[int]:
        return [0, 5, 10, 15]

    def get_methodology_paragraphs(self, data_extenso: str) -> List[Any]:
        ano = str(data_extenso)[-4:] if data_extenso and len(str(data_extenso)) > 4 else "2026"
        return get_cra_methodology_paragraphs(ano)

    def get_references_bullets(self) -> List[Any]:
        return list(CRA_REFERENCES_BULLETS)

    @property
    def references_left_indent_pt(self) -> float:
        return 36.0

    def get_post_methodology_paragraphs(self, total_ncs: int) -> List[Any]:
        return list(CRA_POST_METHODOLOGY_PARAGRAPHS)

    def get_levels_data(self) -> Dict[str, Any]:
        return dict(CRA_LEVELS_DATA)

    def get_post_metodologia_extra_paragraphs(self, row: Any, data_extenso: str, total_achados: int) -> Tuple[str, List[Any]]:
        raw_resp = row.get("Pessoal Responsável", "") if hasattr(row, "get") else row["Pessoal Responsável"]
        if pd.isna(raw_resp) or str(raw_resp).strip().lower() in ["", "nan", "none"]:
            responsaveis_list = []
        else:
            responsaveis_list = [r.strip() for r in str(raw_resp).split(",") if r.strip() and r.strip().lower() not in ["nan", "none"]]

        from database.manager import carregar_responsaveis
        db_resp = carregar_responsaveis()

        team_parts = []
        for nome in responsaveis_list:
            match = next((d for d in db_resp if d["nome"].strip().lower() == nome.lower()), None)
            team_parts.append({"nome": match["nome"], "matricula": match["matricula"]} if match else {"nome": nome, "matricula": "xxxxxxx/xx"})

        p1_runs = [("As ações de fiscalização foram realizadas pela equipe formada pelos servidores: ", False, False, None)]
        for i, member in enumerate(team_parts):
            p1_runs.append((member["nome"], True, False, None))
            p1_runs.append((f", matrícula nº {member['matricula']}", False, False, None))
            if i < len(team_parts) - 2:
                p1_runs.append((", ", False, False, None))
            elif i == len(team_parts) - 2:
                p1_runs.append((" e ", False, False, None))

        fisc_sufixo = f" nos dias {data_extenso}. Nessas ações foram identificados {total_achados} achados de fiscalização nas áreas sob concessão por meio de um levantamento de campo nas Rodovias com evidências de defeitos que poderiam se caracterizar Não Conformidades."
        p1_runs.append((fisc_sufixo, False, False, None))

        p2_runs = [("Esses achados foram avaliados tomando por base as orientações do PDCL, em especial, o Subitem 4.2.2.1.3 - Parâmetros Mínimos Exigidos, visualizando que \"os pavimentos deverão ser analisados quanto às suas condições de superfície, conforto, deformabilidade, vida remanescente e segurança”, e ainda que os “parâmetros de aceitabilidade do pavimento para essas condições que deverão ser totalmente atendidas durante o período de CONCESSÃO”.", False, False, None)]
        return ("5. FISCALIZAÇÃO", [p1_runs, p2_runs])

    def render_post_metodologia_extra_content(self, doc: Any, row: Any, planilha_elegibilidade: Any = None, *args, **kwargs) -> None:
        planilha = planilha_elegibilidade or kwargs.get("planilha_elegibilidade") or getattr(self, "planilha_elegibilidade", None)
        if not planilha:
            return
        try:
            from services.elegibilidade_service import extrair_dados_elegibilidade, renderizar_quadro_elegibilidade
            dados = extrair_dados_elegibilidade(planilha)
            if dados and dados.get("sections"):
                renderizar_quadro_elegibilidade(doc, dados)
        except Exception as e:
            import logging
            logging.error(f"Erro ao renderizar Quadro 1 de Elegibilidade: {e}")

    @property
    def quadros_section_title(self) -> str:
        return "5. FISCALIZAÇÃO"

    def get_quadro_intro_paragraphs(self, row: Any, data_extenso: str, responsaveis_formatted: str) -> List[Any]:
        return list(CRA_QUADRO_INTRO_PARAGRAPHS)

    @property
    def quadro_title_template(self) -> str:
        return "Quadro 1 – Registro das Não Conformidades na Área de Concessão da CRA - {mes_ano}"

    @property
    def nc_table_headers(self) -> List[str]:
        return [
            "TRECHO", "IDENTIFICAÇÃO", "DESCRIÇÃO / INFRAÇÃO",
            "REGISTRO FOTOGRÁFICO", "FUNDAMENTO DA INFRAÇÃO (CONTRATO DE CONCESSÃO)",
            "DETERMINAÇÃO / RECOMENDAÇÃO"
        ]

    @property
    def nc_table_col_widths(self) -> List[Any]:
        return [Inches(1.40), Inches(1.40), Inches(1.22), Inches(1.69), Inches(1.56)]

    def format_nc_table_total_row(self, table: Any, row_idx: int, total_ncs: int, col_widths: Optional[List[Any]] = None) -> None:
        r_total = table.rows[row_idx]
        r_total.cells[0].merge(r_total.cells[1]).merge(r_total.cells[2]).merge(r_total.cells[3])
        r_total.cells[0].text = "TOTAL"
        r_total.cells[4].text = str(total_ncs)

        widths = col_widths if col_widths is not None else self.nc_table_col_widths
        r_total.cells[0].width = widths[0] + widths[1] + widths[2] + widths[3]
        r_total.cells[4].width = widths[4]

    def render_quadros(self, doc: Any, row: Any, nc_df: Any, criar_tabela_quadros_fn: Any) -> None:
        from utils import formatar_mes_ano
        id_fisc = str(row.get("ID da Fiscalização", "")).strip() if hasattr(row, "get") else str(row["ID da Fiscalização"]).strip()
        ncs_reais, pas_reais, resumo = separar_achados_df_cra(nc_df, id_fisc=id_fisc)

        try:
            mes_ano = formatar_mes_ano(row["Data"]).replace(", ", "/").lower()
        except Exception:
            mes_ano = "junho/2026"

        # 1. Parágrafos introdutórios da Seção de Fiscalização
        for p_runs in self.get_quadro_intro_paragraphs(row, "", ""):
            if not p_runs:
                doc.add_paragraph()
                continue
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

        if resumo.tem_nc or (not resumo.tem_nc and not resumo.tem_pa):
            p_q2 = doc.add_paragraph()
            p_q2.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_q2.paragraph_format.space_after = Pt(6)
            r_q2_1 = p_q2.add_run("Quadro 2")
            r_q2_1.bold = True
            r_q2_1.font.name = 'Aptos'
            r_q2_1.font.size = Pt(11)
            r_q2_2 = p_q2.add_run(f" – Determinações para Não Conformidades Identificadas – {mes_ano}")
            r_q2_2.font.name = 'Aptos'
            r_q2_2.font.size = Pt(11)

            criar_tabela_quadros_fn(doc, ncs_reais, is_pa=False, report_config=self)
            doc.add_paragraph()

            if resumo.ambos_presentes:
                p_q3 = doc.add_paragraph()
                p_q3.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_q3.paragraph_format.space_after = Pt(6)
                r_q3_1 = p_q3.add_run("Quadro 3")
                r_q3_1.bold = True
                r_q3_1.font.name = 'Aptos'
                r_q3_1.font.size = Pt(11)
                r_q3_2 = p_q3.add_run(" – Pontos de Atenção por Rodovia/Sentido")
                r_q3_2.font.name = 'Aptos'
                r_q3_2.font.size = Pt(11)

                criar_tabela_quadros_fn(doc, pas_reais, is_pa=True, report_config=self)
        elif resumo.tem_pa:
            p_q2 = doc.add_paragraph()
            p_q2.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_q2.paragraph_format.space_after = Pt(6)
            r_q2_1 = p_q2.add_run("Quadro 2")
            r_q2_1.bold = True
            r_q2_1.font.name = 'Aptos'
            r_q2_1.font.size = Pt(11)
            r_q2_2 = p_q2.add_run(" – Pontos de Atenção por Rodovia/Sentido")
            r_q2_2.font.name = 'Aptos'
            r_q2_2.font.size = Pt(11)

            criar_tabela_quadros_fn(doc, pas_reais, is_pa=True, report_config=self)

        for _ in range(3):
            doc.add_paragraph()

    @property
    def finalizacao_sections_config(self) -> Dict[str, str]:
        return {"6": "determinações", "7": "recomendações", "8": "conclusões"}

    def get_determinations_paragraphs(self, total_ncs: int) -> List[Any]:
        return list(CRA_DETERMINATIONS_PARAGRAPHS)

    def get_recommendations_paragraphs(self) -> List[Any]:
        return list(CRA_RECOMMENDATIONS_PARAGRAPHS)

    def get_conclusions_paragraphs(self, total_ncs: int, local_val: str) -> List[Any]:
        from sections.finalizacao.finalizacao import numero_por_extenso
        extenso_ncs = numero_por_extenso(total_ncs)
        return get_cra_conclusions_paragraphs(total_ncs, extenso_ncs)

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
        from utils import adicionar_titulo_secao
        ambos_presentes = not ncs_reais.empty and not pas_reais.empty
        tem_nc = not ncs_reais.empty
        tem_pa = not pas_reais.empty

        local_val = row.get("Local", "") if hasattr(row, "get") else row["Local"]
        if not local_val or str(local_val).strip() in ("", "=Local="):
            local_val = "Rota do Atlântico"

        if ambos_presentes:
            p_ap_a = adicionar_titulo_secao(doc, "APÊNDICE A – REGISTROS FOTOGRÁFICOS DAS NÃO CONFORMIDADES")
            p_ap_a.paragraph_format.page_break_before = True
            criar_grade_fotos_fn(doc, ncs_reais, local_val, fotos_dir, data_fisc, self.key)

            p_ap_b = adicionar_titulo_secao(doc, "APÊNDICE B – REGISTROS FOTOGRÁFICOS DOS PONTOS DE ATENÇÃO")
            p_ap_b.paragraph_format.page_break_before = True
            criar_grade_fotos_fn(doc, pas_reais, local_val, fotos_dir, data_fisc, self.key)
        else:
            p_ap_u = adicionar_titulo_secao(doc, "APÊNDICE ÚNICO - MEMORIAL FOTOGRÁFICO - FISCALIZAÇÃO")
            p_ap_u.paragraph_format.page_break_before = True
            df_render = pas_reais if (tem_pa and not tem_nc) else ncs_reais

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
            f"RELATÓRIO DE FISCALIZAÇÃO PROCESSO ADMINISTRATIVO Nº {mes_ano} - CTR",
            "SEI Nº xxxxxxxx-xxx"
        ]
