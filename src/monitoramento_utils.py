# -*- coding: utf-8 -*-
"""
Utilitários de Monitoramento (Fachada de compatibilidade retroativa).
Delega a auditoria e extração para services.previous_report.previous_report_audit_service,
assegurando conformidade com a LGPD e evitando processamento redundante.
"""
from typing import Any, Dict, List, Optional
from docx.table import Table

from services.previous_report.previous_report_audit_service import (
    extrair_metadados_anterior as _audit_extrair_metadados,
    extrair_linhas_quadro1_anterior as _audit_extrair_linhas,
    extrair_ncs_e_fotos_anterior as _audit_extrair_fotos,
    encontrar_quadro1_table as _audit_encontrar_quadro1,
    _strip_accents,
)


def strip_accents(s: Any) -> str:
    """Função legada para compatibilidade de remoção de acentos."""
    return _strip_accents(s)


def encontrar_quadro1_table(doc: Any) -> Optional[Table]:
    """Localiza a tabela do Quadro 1 em um documento Word (.docx)."""
    return _audit_encontrar_quadro1(doc)


def extrair_metadados_anterior(documento_anterior: Any) -> Dict[str, Any]:
    """
    Extrai metadados do documento anterior (.docx) via serviço unificado.
    Retorna o dicionário com as chaves históricas esperadas pelos consumidores.
    """
    meta_obj = _audit_extrair_metadados(documento_anterior)
    return {
        "N_prev": meta_obj.n_prev,
        "N_curr": meta_obj.n_curr,
        "ctr_num": meta_obj.ctr_num,
        "processo_sei_prev": meta_obj.processo_sei_prev,
        "data_vistoria_prev": meta_obj.data_vistoria_prev,
        "oficio_num_prev": meta_obj.oficio_num_prev,
        "oficio_data_prev": meta_obj.oficio_data_prev,
        "carta_num_prev": meta_obj.carta_num_prev,
        "carta_data_prev": meta_obj.carta_data_prev,
        "carta_sei_prev": meta_obj.carta_sei_prev,
        "is_fiscalizacao": meta_obj.is_fiscalizacao,
    }


def extrair_linhas_quadro1_anterior(documento_anterior: Any) -> List[Dict[str, str]]:
    """
    Extrai as NCs e descrições do Quadro 1 do documento anterior.
    Retorna lista de dicionários [{"id_nc": ..., "info_ou_constatacao": ...}].
    """
    itens = _audit_extrair_linhas(documento_anterior)
    return [
        {
            "id_nc": item.id_nc,
            "info_ou_constatacao": item.info_ou_constatacao,
            "situacao": item.situacao,
            "foto_ref": item.foto_ref,
        }
        for item in itens
    ]


def extrair_ncs_e_fotos_anterior(documento_anterior: Any) -> List[Dict[str, Any]]:
    """
    Extrai as evidências fotográficas e NCs do documento anterior em memória (LGPD compliant).
    """
    return _audit_extrair_fotos(documento_anterior)


def criar_tabela_quadro1_monitoramento(doc, headers, ncs_from_prev, ncs_reais, col_widths=None):
    """
    Cria a tabela comparativa do Quadro 1 (3 colunas) para relatórios de monitoramento.
    """
    from docx.shared import Pt, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
    from sections.quadros.quadros import set_cell_shading, set_cell_margins, set_table_borders

    if not ncs_from_prev:
        if ncs_reais is None or ncs_reais.empty:
            p_empty = doc.add_paragraph()
            p_empty.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p_empty.add_run("Nenhuma Não Conformidade registrada.")
            run.font.name = "Aptos"
            run.font.size = Pt(10)
            return None
        for _, nc_row in ncs_reais.iterrows():
            ident = str(nc_row.get("Identificação", "")).strip()
            desc = str(nc_row.get("Não Conformidade", "")).strip()
            ncs_from_prev.append({
                "id_nc": f"{ident} - {desc}" if ident else desc,
                "info_ou_constatacao": str(nc_row.get("Observações", nc_row.get("Legenda da Foto", ""))).strip()
            })

    table = doc.add_table(rows=1 + len(ncs_from_prev), cols=3)
    table.style = "Table Grid"
    set_table_borders(table)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.allow_autofit = False

    if not col_widths:
        col_widths = [Inches(2.50), Inches(3.80), Inches(1.27)]

    for r in table.rows:
        for c_idx, width in enumerate(col_widths):
            if c_idx < len(r.cells):
                r.cells[c_idx].width = width

    # Cabeçalho
    for c_idx, text in enumerate(headers):
        cell = table.cell(0, c_idx)
        set_cell_shading(cell, "BFBFBF")
        set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        run = p.add_run(text)
        run.font.name = "Aptos"
        run.font.size = Pt(10)
        run.bold = True

    # Preencher dados
    for idx, item in enumerate(ncs_from_prev, 1):
        if isinstance(item, dict) and item.get("type") == "section":
            c_start = table.cell(idx, 0)
            c_end = table.cell(idx, 2)
            c_start.merge(c_end)
            set_cell_shading(c_start, "FFFFCC")
            set_cell_margins(c_start, top=100, bottom=100, left=150, right=150)
            c_start.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p = c_start.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            r = p.add_run(item.get("text", ""))
            r.font.name = "Aptos"
            r.font.size = Pt(10)
            r.bold = True
            continue

        id_nc_val = item.get("id_nc", "") if isinstance(item, dict) else getattr(item, "id_nc", "")
        info_val = item.get("info_ou_constatacao", item.get("constatacao", "")) if isinstance(item, dict) else getattr(item, "info_ou_constatacao", "")

        situacao_val = "Pendente"
        target_id = id_nc_val.strip().lower()
        if ncs_reais is not None and not ncs_reais.empty:
            for _, nc_row in ncs_reais.iterrows():
                curr_id = str(nc_row.get("Identificação", "")).strip().lower()
                if curr_id and (target_id == curr_id or target_id in curr_id or curr_id in target_id):
                    situacao_val = str(nc_row.get("Situação", "Pendente")).strip().title()
                    break

        # Coluna 0
        c0 = table.cell(idx, 0)
        set_cell_margins(c0, top=100, bottom=100, left=150, right=150)
        c0.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p0 = c0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p0.paragraph_format.space_before = Pt(0)
        p0.paragraph_format.space_after = Pt(0)
        p0.paragraph_format.line_spacing = 1.15
        r0 = p0.add_run(id_nc_val)
        r0.font.name = "Aptos"
        r0.font.size = Pt(10)

        # Coluna 1
        c1 = table.cell(idx, 1)
        set_cell_margins(c1, top=100, bottom=100, left=150, right=150)
        c1.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p1.paragraph_format.space_before = Pt(0)
        p1.paragraph_format.space_after = Pt(0)
        p1.paragraph_format.line_spacing = 1.15
        r1 = p1.add_run(info_val)
        r1.font.name = "Aptos"
        r1.font.size = Pt(10)

        # Coluna 2
        c2 = table.cell(idx, 2)
        set_cell_margins(c2, top=100, bottom=100, left=150, right=150)
        c2.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p2 = c2.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(0)
        r2 = p2.add_run(situacao_val)
        r2.font.name = "Aptos"
        r2.font.size = Pt(10)
        r2.bold = True

    return table
