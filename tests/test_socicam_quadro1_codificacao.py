import sys
import os
import pytest
from docx import Document

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from reports.socicam import SocicamReport
from core.rules.cra_rules import normalizar_registros_cra_para_relatorio
from sections.quadros.quadros import criar_tabela_quadros

def test_socicam_quadro1_titulo_sem_negrito():
    """Garante que o título 'Quadro 1' no SOCICAM Fiscalização esteja com estilo normal (bold = False)."""
    doc = Document()
    report = SocicamReport()
    row = {"Data": "2026-11-09", "Local": "Terminal de Petrolina"}
    nc_df = None
    
    # Executa render_quadros
    report.render_quadros(doc, row, nc_df, lambda *a, **k: None)
    
    # Encontra parágrafo do Quadro 1
    p_quadro1 = None
    for p in doc.paragraphs:
        if "Quadro 1" in p.text and "Determinações para Não Conformidades" in p.text:
            p_quadro1 = p
            break
            
    assert p_quadro1 is not None, "Parágrafo do Quadro 1 não encontrado"
    
    # O run correspondente a 'Quadro 1' deve ter bold == False (ou None)
    for r in p_quadro1.runs:
        if "Quadro 1" in r.text:
            assert not r.bold, f"O texto 'Quadro 1' deve estar normal, mas r.bold={r.bold}"

def test_socicam_codificacao_sequencial_cra_logic():
    """Garante que a codificação de Não Conformidades na SOCICAM siga {cod}/2026.001, .002, .003."""
    registros = [
        {"ID da Fiscalização": "FISC-SOCICAM-2026-001", "Codificação": "SOCICAM.TIP", "Não Conformidade": "NC01", "Terminal": "TIP"},
        {"ID da Fiscalização": "FISC-SOCICAM-2026-001", "Codificação": "SOCICAM.TIP", "Não Conformidade": "NC02", "Terminal": "TIP"},
        {"ID da Fiscalização": "FISC-SOCICAM-2026-001", "Codificação": "SOCICAM.TIP", "Não Conformidade": "NC03", "Terminal": "TIP"},
    ]
    fisc_list = [{"ID da Fiscalização": "FISC-SOCICAM-2026-001", "Data": "2026-11-09"}]
    
    norm = normalizar_registros_cra_para_relatorio(registros, fisc_list=fisc_list)
    
    assert len(norm) == 3
    assert norm[0]["Identificação"] == "SOCICAM.TIP/2026.001"
    assert norm[1]["Identificação"] == "SOCICAM.TIP/2026.002"
    assert norm[2]["Identificação"] == "SOCICAM.TIP/2026.003"
