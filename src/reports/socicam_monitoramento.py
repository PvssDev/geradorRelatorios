# -*- coding: utf-8 -*-
from reports.base import BaseMonitoramentoMixin
from reports.socicam import SocicamReport


class SocicamMonitoramentoReport(BaseMonitoramentoMixin, SocicamReport):
    @property
    def key(self) -> str:
        return "SOCICAM_MONITORAMENTO"

    @property
    def display_name(self) -> str:
        return "SOCICAM (Monitoramento)"

    @property
    def capa_titulo(self) -> str:
        return "RELATÓRIO DE MONITORAMENTO TÉCNICO-OPERACIONAL"

    @property
    def capa_ctr_number_template(self) -> str:
        return "RELATÓRIO DE MONITORAMENTO TÉCNICO-OPERACIONAL CTR Nº 03/{ano}"

    def get_process_sei_texts(self, ano) -> list:
        return [
            f"RELATÓRIO DE MONITORAMENTO TÉCNICO-OPERACIONAL PROC ADM Nº 04/{ano} - CTR",
            f"SEI Nº 0030200023.002186/2026-99"
        ]

    def get_capa_titulos(self, row, ano) -> list:
        local_val = str(row.get("Local", "TIP")).upper()
        if "TERMINAL" not in local_val and "MONITORAMENTO" not in local_val:
            local_val = (
                f"TERMINAL RODOVIÁRIO DE PASSAGEIROS DO RECIFE ({local_val})"
                if "RECIFE" in local_val or "TIP" in local_val
                else f"TERMINAL RODOVIÁRIO DE PASSAGEIROS ({local_val})"
            )
        return [
            f"MONITORAMENTO NO {local_val}",
            "PRESTADOR DE SERVIÇO: SOCICAM - ADMINISTRAÇÃO, PROJETOS E REPRESENTAÇÕES LTDA"
        ]

    def gerar_capa_monitoramento(self, doc, logo_path, row, documento_anterior):
        from docx.shared import Inches, Pt
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        import os
        import re
        from docx import Document

        # 0. Ajuste de Estilo e Margens
        style = doc.styles['Normal']
        style.font.name = 'Aptos'
        
        section = doc.sections[0]
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.5)
        section.left_margin = Inches(0.5)
        section.right_margin = Inches(0.5)

        # 1. Extração do número do monitoramento anterior
        self.N_prev = "X"
        self.ctr_num = "XX/XXXX"
        self.processo_sei_prev = "XXXXXXXX"
        self.documento_anterior = documento_anterior
        
        if documento_anterior:
            try:
                prev_doc = Document(documento_anterior)
                
                pattern = re.compile(r'(\d+)(?:\u00ba|\u00b0)?\s*monitoramento', re.IGNORECASE)
                for p in prev_doc.paragraphs:
                    m = pattern.search(p.text)
                    if m:
                        self.N_prev = int(m.group(1))
                        break
                
                pattern_ctr = re.compile(r'CTR\s*(?:N\u00ba|n\u00ba|N\u00ba)?\s*(\d+/\d+)', re.IGNORECASE)
                for p in prev_doc.paragraphs:
                    m = pattern_ctr.search(p.text)
                    if m:
                        self.ctr_num = m.group(1)
                        break

                pattern_sei = re.compile(r'PROCESSO SEI\s*(?:N\u00ba|n\u00ba|N\u00ba)?\s*([\d\./-]+)', re.IGNORECASE)
                for p in prev_doc.paragraphs:
                    m = pattern_sei.search(p.text)
                    if m:
                        self.processo_sei_prev = m.group(1)
                        break
            except Exception as e:
                print(f"Erro ao extrair dados do documento anterior: {e}")

        if isinstance(self.N_prev, int):
            self.N_curr = self.N_prev + 1
        else:
            self.N_curr = "X"

        n_curr_str = f"{self.N_curr}º" if self.N_curr != "X" else "Xº"

        def add_cover_p(text, bold=True, size_pt=12, space_after=6, align=WD_ALIGN_PARAGRAPH.CENTER):
            p = doc.add_paragraph()
            p.alignment = align
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

        # Imagem da Capa (capa_1.png)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        capa_1 = os.path.join(base_dir, "assets", "capa_1.png")
        if not os.path.exists(capa_1):
            capa_1 = logo_path  # fallback
            
        if os.path.exists(capa_1):
            doc.add_picture(capa_1, width=Inches(5.90))
            doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
            doc.paragraphs[-1].paragraph_format.space_after = Pt(12)
            doc.paragraphs[-1].paragraph_format.space_before = Pt(12)

        # Títulos do Meio
        add_cover_p("PROCESSO DE FISCALIZAÇÃO TÉCNICO-OPERACIONAL DOS TERMINAIS RODOVIÁRIOS CONCEDIDOS À SOCICAM - ADMINISTRAÇÃO, PROJETOS E REPRESENTAÇÕES LTDA", bold=True, size_pt=11, space_after=6)
        add_cover_p("CONTRATO Nº 1.041.080/08", bold=True, size_pt=11, space_after=4)
        add_cover_p(f"PROCESSO SEI Nº {getattr(self, 'processo_sei_prev', 'XXXXXXXX')}", bold=True, size_pt=11, space_after=6)
        add_cover_p("", bold=False, size_pt=11, space_after=6)
        add_cover_p("Recife, data de assinatura eletrônica", bold=False, size_pt=11, space_after=0)
