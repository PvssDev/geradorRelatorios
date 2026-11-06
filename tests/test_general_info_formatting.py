import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from docx import Document
from docx.shared import Inches, Pt
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from reports.cra import CraReport
from reports.crc import CrcReport
from reports.socicam import SocicamReport
from sections.introduction.introduction import gerar_secao_introducao

def test_general_info_column_widths_all_concessions():
    """Garante que a soma das larguras das colunas seja exatamente 7.27 polegadas (margens padrão A4)."""
    configs = [CraReport(), CrcReport(), SocicamReport()]
    
    for cfg in configs:
        widths = cfg.general_info_col_widths
        assert len(widths) == 2, f"{cfg.key} deve ter 2 colunas em Informações Gerais"
        total_width = round(widths[0].inches + widths[1].inches, 2)
        assert total_width == 7.27, f"{cfg.key} total col width deve ser 7.27'', obteve {total_width}"
        assert widths[0].inches == 2.2, f"{cfg.key} coluna 0 deve ter 2.2''"
        assert widths[1].inches == 5.07, f"{cfg.key} coluna 1 deve ter 5.07''"

def test_gerar_secao_introducao_table_formatting():
    """Garante que a tabela gerada tenha bordas, alinhamento vertical e espaçamento enxuto."""
    doc = Document()
    cfg = SocicamReport()
    row = {
        "Data": "2026-06-15",
        "Período": "15 a 16/06/2026",
        "Pessoal Responsável": "Fiscal 1, Fiscal 2"
    }
    
    gerar_secao_introducao(doc, row, total_achados=3, report_config=cfg)
    
    # Procura a tabela de Informações Gerais
    assert len(doc.tables) >= 1
    table = doc.tables[0]
    
    # Valida linhas e células
    for r_idx, r in enumerate(table.rows):
        for cell in r.cells:
            assert cell.vertical_alignment == WD_CELL_VERTICAL_ALIGNMENT.CENTER
            for p in cell.paragraphs:
                assert p.paragraph_format.space_before <= Pt(2)
                assert p.paragraph_format.space_after <= Pt(2)
                assert p.paragraph_format.line_spacing <= 1.15

