# -*- coding: utf-8 -*-
"""
Especialização do Relatório para o CRC Monitoramento (Rota dos Coqueiros - Paiva).
Contrato de Concessão Patrocinada CGPE nº 001/2006 (PE-024 / Ponte sobre o Rio Jaboatão).
Utiliza a nova Engine de Monitoramento em memória e templates padronizados.
"""
import os
from typing import Any, Dict, List, Optional, Tuple
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import pandas as pd

from reports.base import BaseMonitoramentoMixin
from reports.crc import CrcReport
from core.interfaces.report_contracts import IReportContract
from services.previous_report.previous_report_audit_service import (
    extrair_metadados_anterior,
    extrair_linhas_quadro1_anterior,
)
from monitoramento_utils import criar_tabela_quadro1_monitoramento
from reports.templates.crc_monitoramento_templates import (
    CRC_MONITORAMENTO_KEY,
    CRC_MONITORAMENTO_DISPLAY_NAME,
    CRC_MONITORAMENTO_DEFAULT_CONTRATO,
    CRC_MONITORAMENTO_ABBREVIATIONS,
    CRC_MONITORAMENTO_QUADRO1_COL_WIDTHS,
    CRC_MONITORAMENTO_QUADRO1_NOTA,
    get_crc_monitoramento_quadro1_headers,
    get_crc_monitoramento_intro_paragraphs,
    get_crc_monitoramento_objective_paragraphs,
    get_crc_monitoramento_conclusions_paragraphs,
)


class CrcMonitoramentoReport(BaseMonitoramentoMixin, CrcReport, IReportContract):
    """Relatório Técnico-Operacional de Monitoramento da Concessionária Rota dos Coqueiros (CRC)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.N_prev = 0
        self.N_curr = 1
        self.ctr_num = "XX/XXXX"
        self.processo_sei_prev = "xxxxxxxx-xxx"
        self.data_vistoria_prev = "XX/XX/XXXX"
        self.oficio_num_prev = "xxx/xxxx"
        self.oficio_data_prev = "xx/xx/xxxx"
        self.carta_num_prev = "xxxx/xxxx"
        self.carta_data_prev = "xx/xx/xxxx"
        self.carta_sei_prev = "xxxxxxxx-xxx"
        self.N_ncs_pendentes_prev = 0
        self.documento_anterior = None

    @property
    def key(self) -> str:
        return CRC_MONITORAMENTO_KEY

    @property
    def display_name(self) -> str:
        return CRC_MONITORAMENTO_DISPLAY_NAME

    @property
    def default_contrato(self) -> str:
        return CRC_MONITORAMENTO_DEFAULT_CONTRATO

    @property
    def sumario_before_abreviaturas(self) -> bool:
        return False

    @property
    def signatures_before_apendices(self) -> bool:
        return True

    def get_abbreviations(self) -> List[Tuple[str, str]]:
        return list(CRC_MONITORAMENTO_ABBREVIATIONS)

    def gerar_capa_monitoramento(self, doc: Any, logo_path: str, row: Any, documento_anterior: Any) -> None:
        """Renderiza a capa do CRC Monitoramento com auditoria anterior integrada."""
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
        self.ctr_num = meta.ctr_num if meta.ctr_num != "XX/XXXX" else "05/2025"
        self.processo_sei_prev = meta.processo_sei_prev if meta.processo_sei_prev not in ("XXXXXXXX", "xxxxxxxx", "xxxxxxxx-xxx", "") else "xxxxxxxx-xxx"
        self.data_vistoria_prev = meta.data_vistoria_prev
        self.oficio_num_prev = meta.oficio_num_prev
        self.oficio_data_prev = meta.oficio_data_prev
        self.carta_num_prev = meta.carta_num_prev
        self.carta_data_prev = meta.carta_data_prev
        self.carta_sei_prev = meta.carta_sei_prev
        self.N_ncs_pendentes_prev = meta.n_ncs_pendentes_prev

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
        add_cover_p("COORDENADORIA DE TRANSPORTES E RODOVIAS", bold=True, size_pt=12, space_after=4)
        add_cover_p(f"RELATÓRIO DO {n_curr_str} MONITORAMENTO DO PROCESSO", bold=True, size_pt=12, space_after=4)
        add_cover_p(f"DE FISCALIZAÇÃO TÉCNICO-OPERACIONAL CTR Nº {self.ctr_num}", bold=True, size_pt=12, space_after=12)

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
        add_cover_p(
            f"VISTORIA TÉCNICA SOBRE AS NÃO CONFORMIDADES APONTADAS NO RELATÓRIO DE FISCALIZAÇÃO TÉCNICO-OPERACIONAL CTR {self.ctr_num}.",
            bold=True, size_pt=11, space_after=6
        )
        add_cover_p("", bold=False, size_pt=11, space_after=6)
        add_cover_p("CONTRATO DE CONCESSÃO PATROCINADA – CGPE Nº 001/2006", bold=True, size_pt=11, space_after=4)
        add_cover_p("EXPLORAÇÃO DA PONTE DE ACESSO E SISTEMA VIÁRIO", bold=True, size_pt=11, space_after=4)
        add_cover_p("DO DESTINO DE TURISMO E LAZER PRAIA DO PAIVA", bold=True, size_pt=11, space_after=6)
        add_cover_p("", bold=False, size_pt=11, space_after=6)
        add_cover_p(f"PROCESSO SEI Nº {self.processo_sei_prev}", bold=True, size_pt=11, space_after=6)
        add_cover_p("", bold=False, size_pt=11, space_after=6)
        add_cover_p("Recife, data da assinatura eletrônica", bold=False, size_pt=11, space_after=0)

    def get_sumario_linhas(self, row: Any, nc_df: Any = None) -> List[str]:
        from utils import formatar_mes_ano
        try:
            mes_ano = formatar_mes_ano(row["Data"]).upper()
        except Exception:
            mes_ano = "MARÇO/2026"

        return [
            "1.\tINTRODUÇÃO\t4",
            "2.\tOBJETIVO\t4",
            "3.\tRESULTADOS DAS VISTORIAS DAS NÃO CONFORMIDADES\t5",
            f"4.\tRESUMO DA SITUAÇÃO DAS NÃO CONFORMIDADES MONITORADAS ({mes_ano})\t8",
            "5.\tCONCLUSÕES E RECOMENDAÇÕES\t9",
            f"\tAPÊNDÍCE ÚNCO - MEMORIAL FOTOGRÁFICO - {mes_ano}\t10",
        ]

    def gerar_secoes_monitoramento(self, doc: Any, row: Any, nc_df: Any, total_achados: int, documento_anterior: Any = None) -> None:
        """Gera as Seções 1 a 4 com suporte de auditoria em memória e templates modulares."""
        from utils import adicionar_titulo_secao, formatar_data_extenso, formatar_mes_ano

        if documento_anterior and (getattr(self, "N_prev", 0) == 0 or getattr(self, "ctr_num", "XX/XXXX") == "XX/XXXX"):
            meta = extrair_metadados_anterior(documento_anterior)
            self.N_prev = meta.n_prev
            self.N_curr = meta.n_curr
            self.ctr_num = meta.ctr_num if meta.ctr_num != "XX/XXXX" else self.ctr_num
            self.processo_sei_prev = meta.processo_sei_prev if meta.processo_sei_prev not in ("XXXXXXXX", "xxxxxxxx", "") else self.processo_sei_prev
            self.data_vistoria_prev = meta.data_vistoria_prev
            self.oficio_num_prev = meta.oficio_num_prev
            self.oficio_data_prev = meta.oficio_data_prev
            self.carta_num_prev = meta.carta_num_prev
            self.carta_data_prev = meta.carta_data_prev
            self.carta_sei_prev = meta.carta_sei_prev
            self.N_ncs_pendentes_prev = meta.n_ncs_pendentes_prev

        N_prev = getattr(self, "N_prev", 0)
        N_curr = getattr(self, "N_curr", 1)
        ctr_num = getattr(self, "ctr_num", "05/2025")
        n_prev_str = f"{N_prev}º" if N_prev else "1º"
        n_curr_str = f"{N_curr}º"

        data_extenso = formatar_data_extenso(row["Data"])
        try:
            data_vistoria = pd.to_datetime(row["Data"], dayfirst=True).strftime("%d/%m/%Y")
        except Exception:
            data_vistoria = "XX/XX/XXXX"

        id_fisc = str(row.get("ID da Fiscalização", "")).strip() if hasattr(row, "get") else str(row["ID da Fiscalização"]).strip()
        mes_ano_cap = formatar_mes_ano(row["Data"]).upper()

        # Extrair NCs anteriores do serviço tipado
        itens_prev = extrair_linhas_quadro1_anterior(documento_anterior)
        ncs_from_prev = [{"id_nc": it.id_nc, "constatacao": it.info_ou_constatacao} for it in itens_prev]

        if nc_df is not None and not nc_df.empty:
            if "ID da Fiscalização" in nc_df.columns:
                mask_id = nc_df["ID da Fiscalização"].astype(str).str.strip() == id_fisc
                current_ncs = nc_df[mask_id].copy()
            else:
                current_ncs = nc_df.copy()
            if current_ncs.empty:
                current_ncs = nc_df.copy()

            cols_check = [c for c in ["Não Conformidade", "Identificação", "Observações", "Determinação", "Foto", "Fotos", "Legenda da Foto"] if c in current_ncs.columns]
            if cols_check:
                mask_nc = current_ncs[cols_check].fillna("").astype(str).apply(lambda r_c: any(v.strip() != "" for v in r_c), axis=1)
                ncs_reais = current_ncs[mask_nc].copy()
            else:
                ncs_reais = current_ncs.copy()
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
        is_fiscalizacao = (N_prev == 0)
        intro_paragraphs = get_crc_monitoramento_intro_paragraphs(
            is_fiscalizacao=is_fiscalizacao,
            ctr_num=ctr_num,
            data_vist_prev=getattr(self, "data_vistoria_prev", "XX/XX/XXXX"),
            val_ncs=getattr(self, "N_ncs_pendentes_prev", len(ncs_from_prev) or 1),
            processo_sei_prev=getattr(self, "processo_sei_prev", "xxxxxxxx-xxx"),
            oficio_num_prev=getattr(self, "oficio_num_prev", "xxx/xxxx"),
            oficio_data_prev=getattr(self, "oficio_data_prev", "xx/xx/xxxx"),
            carta_num_prev=getattr(self, "carta_num_prev", "xxxx/xxxx"),
            carta_data_prev=getattr(self, "carta_data_prev", "xx/xx/xxxx"),
            carta_sei_prev=getattr(self, "carta_sei_prev", "xxxxxxxx-xxx"),
            n_prev_str=n_prev_str
        )
        for p_runs in intro_paragraphs:
            add_p(p_runs[0][0])

        # 2. OBJETIVO
        adicionar_titulo_secao(doc, "2. OBJETIVO")
        doc.add_paragraph()
        for p_runs in get_crc_monitoramento_objective_paragraphs(
            n_curr_str=n_curr_str,
            ctr_num=ctr_num,
            data_extenso=data_extenso,
            carta_num_prev=getattr(self, "carta_num_prev", "xxxx/xxxx")
        ):
            add_p(p_runs[0][0])

        # 3. RESULTADOS DAS VISTORIAS
        adicionar_titulo_secao(doc, "3. RESULTADOS DAS VISTORIAS DAS NÃO CONFORMIDADES")
        doc.add_paragraph()
        add_p(
            f"Apresentam-se os resultados das vistorias técnicas realizadas em {data_extenso} na Rodovia Estadual PE-024 "
            f"referentes às Não Conformidades (NC) registradas no Relatório de Fiscalização Técnico-Operacional ARPE/CTR "
            f"nº {ctr_num}, organizadas em subitens pelo sentido da pista, associadas a cada Segmento Homogêneo (SH) "
            f"com indicação do ponto fiscalizado (KM)."
        )

        if ncs_reais.empty:
            add_p("Nenhuma Não Conformidade registrada para esta fiscalização.")
        else:
            for nc_idx, (_, nc_row) in enumerate(ncs_reais.reset_index(drop=True).iterrows(), 1):
                ident = str(nc_row.get("Identificação", "")).strip()
                if not ident or ident.lower().startswith("foto"):
                    if (nc_idx - 1) < len(ncs_from_prev):
                        ident = ncs_from_prev[nc_idx - 1]["id_nc"]

                nc_desc = str(nc_row.get("Não Conformidade", "")).strip()
                pista_val = str(nc_row.get("Pista", "")).strip() if not pd.isna(nc_row.get("Pista")) else ""
                trecho_val = str(nc_row.get("Trecho", "")).strip() if not pd.isna(nc_row.get("Trecho")) else ""
                observacoes = str(nc_row.get("Observações", nc_row.get("Legenda da Foto", ""))).strip()
                determinacao = str(nc_row.get("Determinação", "")).strip()
                analise_arpe = str(nc_row.get("Análise ARPE", "")).strip()

                partes_titulo = []
                if ident and not ident.lower().startswith("foto"):
                    partes_titulo.append(ident)
                elif nc_desc:
                    partes_titulo.append(nc_desc)
                else:
                    partes_titulo.append(f"NÃO CONFORMIDADE {nc_idx}")

                if trecho_val:
                    partes_titulo.append(trecho_val)
                if pista_val and pista_val.lower() not in ["única", "unica"]:
                    partes_titulo.append(f"PISTA {pista_val.upper()}")

                sub_title = f"3.{nc_idx} " + " – ".join(partes_titulo)
                adicionar_titulo_secao(doc, sub_title)
                doc.add_paragraph()

                add_label_text("NÃO CONFORMIDADE: ", nc_desc if nc_desc else (ident if ident else "A ser preenchido."))
                add_label_text("POSICIONAMENTO DA CRC: ", determinacao if determinacao else "A ser preenchido.")
                add_label_text("CONSTATAÇÃO: ", observacoes if observacoes else "A ser preenchido.")
                add_label_text("ANÁLISE ARPE: ", analise_arpe if analise_arpe else "A ser preenchido.")
                doc.add_paragraph()

        # 4. RESUMO DA SITUAÇÃO
        adicionar_titulo_secao(doc, f"4. RESUMO DA SITUAÇÃO DAS NÃO CONFORMIDADES MONITORADAS ({mes_ano_cap})")
        doc.add_paragraph()
        add_p(
            f"Apresenta-se no Quadro 1, a seguir, um resumo da situação das Não Conformidades pendentes do Relatório "
            f"ARPE/CTR nº {ctr_num}, de acordo com as vistorias técnicas realizadas em {data_vistoria}, dando "
            f"continuidade ao monitoramento das respectivas soluções."
        )

    @property
    def quadros_section_title(self) -> str:
        return ""

    def render_quadros(self, doc: Any, row: Any, nc_df: Any, criar_tabela_quadros_fn: Any) -> None:
        """Renderiza o Quadro 1 de monitoramento da CRC com 3 colunas e nota explicativa."""
        id_fisc = str(row.get("ID da Fiscalização", "")).strip() if hasattr(row, "get") else str(row["ID da Fiscalização"]).strip()
        ctr_num = getattr(self, "ctr_num", "05/2025")

        try:
            data_vistoria_atual = pd.to_datetime(row["Data"], dayfirst=True).strftime("%d/%m/%Y")
        except Exception:
            data_vistoria_atual = "XX/XX/XXXX"

        current_ncs = pd.DataFrame()
        if nc_df is not None and not nc_df.empty:
            if "ID da Fiscalização" in nc_df.columns:
                mask_id = nc_df["ID da Fiscalização"].astype(str).str.strip() == id_fisc
                current_ncs = nc_df[mask_id].copy()
            if current_ncs.empty:
                current_ncs = nc_df.copy()

        ncs_reais = current_ncs.copy() if not current_ncs.empty else pd.DataFrame()

        # Título do Quadro 1
        p_q = doc.add_paragraph()
        p_q.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_q.paragraph_format.space_after = Pt(6)
        r_q1 = p_q.add_run("QUADRO 1")
        r_q1.bold = True
        r_q1.font.name = "Aptos"
        r_q1.font.size = Pt(11)
        r_q2 = p_q.add_run(f" – Situação das Não Conformidades Relatório ARPE/CTR Nº {ctr_num}")
        r_q2.bold = True
        r_q2.font.name = "Aptos"
        r_q2.font.size = Pt(11)

        # 1. Extração tipada do anterior
        itens_prev = extrair_linhas_quadro1_anterior(getattr(self, "documento_anterior", None))
        ncs_from_prev = [{"id_nc": it.id_nc, "info_ou_constatacao": it.info_ou_constatacao} for it in itens_prev]

        # Fallback caso não haja anterior
        if not ncs_from_prev and not ncs_reais.empty:
            pistas_ncs = {}
            if "Pista" in ncs_reais.columns:
                for _, nc_row in ncs_reais.iterrows():
                    p_val = str(nc_row.get("Pista", "")).strip() if not pd.isna(nc_row.get("Pista")) else ""
                    p_key = p_val if p_val else "Única"
                    pistas_ncs.setdefault(p_key, []).append(nc_row)
            else:
                pistas_ncs["Única"] = [r for _, r in ncs_reais.iterrows()]

            for pista, items in pistas_ncs.items():
                if pista != "Única":
                    ncs_from_prev.append({
                        "type": "section",
                        "text": f"PE - 024, PISTA SENTIDO {pista.upper()}"
                    })
                for nc_row in items:
                    ncs_from_prev.append({
                        "id_nc": str(nc_row.get("Identificação", "")).strip(),
                        "info_ou_constatacao": str(nc_row.get("Não Conformidade", "")).strip()
                    })

        headers = get_crc_monitoramento_quadro1_headers(data_vistoria_atual)
        col_widths = CRC_MONITORAMENTO_QUADRO1_COL_WIDTHS
        criar_tabela_quadro1_monitoramento(doc, headers, ncs_from_prev, ncs_reais, col_widths)

        doc.add_paragraph()
        p_nota = doc.add_paragraph()
        p_nota.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_nota.paragraph_format.space_before = Pt(4)
        p_nota.paragraph_format.space_after = Pt(6)
        p_nota.paragraph_format.line_spacing = 1.15
        run_nota = p_nota.add_run(CRC_MONITORAMENTO_QUADRO1_NOTA)
        run_nota.font.name = "Aptos"
        run_nota.font.size = Pt(10)
        run_nota.italic = True

    @property
    def finalizacao_sections_config(self) -> Dict[str, str]:
        return {"5": "conclusoes_monitoramento"}

    def get_conclusions_paragraphs(self, total_ncs: int, local_val: Any) -> List[Any]:
        return []

    def get_conclusions_monitoramento_paragraphs(self, total_ncs: int, data_extenso: str) -> List[Any]:
        n_curr_str = f"{self.N_curr}º" if self.N_curr else "1º"
        ctr_num = getattr(self, "ctr_num", "05/2025")
        return get_crc_monitoramento_conclusions_paragraphs(total_ncs, data_extenso, n_curr_str, ctr_num)

    def render_apendices(self, doc: Any, row: Any, ncs_reais: Any, pas_reais: Any, fotos_dir: Any, data_fisc: Any, ano: Any, criar_grade_fotos_fn: Any) -> None:
        from utils import adicionar_titulo_secao, formatar_mes_ano

        try:
            mes_ano = formatar_mes_ano(row["Data"]).upper()
        except Exception:
            mes_ano = "MARÇO/2026"

        p_ap = adicionar_titulo_secao(doc, f"APÊNDÍCE ÚNCO - MEMORIAL FOTOGRÁFICO - {mes_ano}")
        p_ap.paragraph_format.page_break_before = True

        total_ncs_val = len(ncs_reais) if ncs_reais is not None and not ncs_reais.empty else 0
        if total_ncs_val == 0:
            fotos_str = ""
        elif total_ncs_val == 1:
            fotos_str = "foto 01"
        elif total_ncs_val == 2:
            fotos_str = "fotos 01 e 02"
        else:
            fotos_str = f"fotos 01 a {str(total_ncs_val).zfill(2)}"

        n_curr_str = f"{self.N_curr}º" if self.N_curr else "1º"
        ctr_num = getattr(self, "ctr_num", "05/2025")
        fotos_suffix = f" ({fotos_str})" if fotos_str else ""

        p_intro = doc.add_paragraph()
        p_intro.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_intro.paragraph_format.space_before = Pt(6)
        p_intro.paragraph_format.space_after = Pt(12)
        p_intro.paragraph_format.line_spacing = 1.15
        run_intro = p_intro.add_run(
            f"Apresenta-se, a seguir, as evidências da situação das Não Conformidades, de acordo com o sentido da pista "
            f"e as identificações utilizadas neste {n_curr_str} Relatório de Monitoramento do Processo de Fiscalização "
            f"Técnico-Operacional nº {ctr_num}{fotos_suffix}."
        )
        run_intro.font.name = "Aptos"
        run_intro.font.size = Pt(11)

        local_val = row.get("Local", "") if hasattr(row, "get") else row["Local"]
        if not local_val or str(local_val).strip() in ("", "=Local="):
            local_val = "Rota dos Coqueiros"

        if ncs_reais is not None and not ncs_reais.empty:
            criar_grade_fotos_fn(doc, ncs_reais, local_val, fotos_dir, data_fisc, self.key)
        else:
            p_empty = doc.add_paragraph()
            r_empty = p_empty.add_run("Nenhuma foto de não conformidade anexada.")
            r_empty.font.name = "Aptos"
            r_empty.font.size = Pt(11)
