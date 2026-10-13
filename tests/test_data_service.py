# -*- coding: utf-8 -*-
import sys
import os
import io
import pandas as pd

# Adiciona src ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from services.data_service import desnormalizar_fiscalizacoes, gerar_planilha_excel_buffer


def test_desnormalizar_sem_ncs():
    fisc = [{
        "ID da Fiscalização": "2026-001",
        "Data": "15/06/2026",
        "Hora": "10:00",
        "Cidade": "Recife",
        "Local": "TIP",
        "Pessoal Responsável": "Alcides Vieira",
        "Coordenador": "Maria Ângela",
        "Contrato": "CT. nº 043/2011",
        "Período": "15 a 18/06/2026",
        "Relatório Gerado": False
    }]
    ncs = []
    
    flat = desnormalizar_fiscalizacoes(fisc, ncs)
    assert len(flat) == 1
    assert flat[0]["ID da Fiscalização"] == "2026-001"
    assert flat[0]["Não conformidade"] == ""
    assert flat[0]["Local"] == "TIP"
    print("[PASS] test_desnormalizar_sem_ncs")


def test_desnormalizar_com_ncs():
    fisc = [{
        "ID da Fiscalização": "2026-001",
        "Data": "15/06/2026",
        "Hora": "10:00",
        "Cidade": "Recife",
        "Local": "TIP",
        "Pessoal Responsável": "Alcides Vieira",
        "Coordenador": "Maria Ângela",
        "Contrato": "CT. nº 043/2011",
        "Período": "15 a 18/06/2026",
        "Relatório Gerado": False
    }]
    ncs = [
        {
            "ID da Fiscalização": "2026-001",
            "Nº": 1,
            "Foto": "foto1.jpg",
            "Não Conformidade": "FI, TTC",
            "Ponto de Atenção": "",
            "Observações": "Fissura no pavimento",
            "Identificação": "NC_01",
            "Pista": "Norte",
            "Trecho": "PE-009",
            "Direção (faixa)": "FD",
            "Fundamento da infração": "Item 4.1",
            "Determinação": "Corrigir em 30 dias",
            "Situação": "Pendente"
        },
        {
            "ID da Fiscalização": "2026-001",
            "Nº": 2,
            "Foto": "foto2.jpg",
            "Não Conformidade": "",
            "Ponto de Atenção": "PA_01",
            "Observações": "Atenção no dreno",
            "Identificação": "PA_01",
            "Pista": "Sul",
            "Trecho": "PE-009",
            "Direção (faixa)": "FE",
            "Fundamento da infração": "Item 4.2",
            "Determinação": "Monitorar",
            "Situação": "Pendente"
        }
    ]
    
    flat = desnormalizar_fiscalizacoes(fisc, ncs)
    assert len(flat) == 2
    assert flat[0]["ID da Fiscalização"] == "2026-001"
    assert flat[0]["Não conformidade"] == "FI, TTC"
    assert flat[0]["Fotos"] == "foto1.jpg"
    assert flat[1]["Ponto de Atenção"] == "PA_01"
    assert flat[1]["Fotos"] == "foto2.jpg"
    print("[PASS] test_desnormalizar_com_ncs")


def test_gerar_planilha_excel_buffer():
    fisc = [{
        "ID da Fiscalização": "2026-001",
        "Data": "15/06/2026",
        "Hora": "10:00",
        "Cidade": "Recife",
        "Local": "TIP",
        "Pessoal Responsável": "Alcides Vieira",
        "Coordenador": "Maria Ângela",
        "Contrato": "CT. nº 043/2011",
        "Período": "15 a 18/06/2026",
        "Relatório Gerado": False
    }]
    ncs = [{
        "ID da Fiscalização": "2026-001",
        "Nº": 1,
        "Foto": "foto1.jpg",
        "Não Conformidade": "FI",
        "Observações": "Fissura",
        "Identificação": "NC_01"
    }]
    
    buf = gerar_planilha_excel_buffer(fisc, ncs)
    assert isinstance(buf, io.BytesIO)
    
    # Valida leitura das abas
    excel_file = pd.ExcelFile(buf)
    sheet_names = excel_file.sheet_names
    assert "Fiscalizações" in sheet_names
    assert "Não-conformidades " in sheet_names
    assert "Observações Importantes" in sheet_names
    assert "Recomendações" in sheet_names
    
    df_fisc = pd.read_excel(excel_file, sheet_name="Fiscalizações")
    assert len(df_fisc) == 1
    assert df_fisc.iloc[0]["ID da Fiscalização"] == "2026-001"
    print("[PASS] test_gerar_planilha_excel_buffer")


if __name__ == "__main__":
    test_desnormalizar_sem_ncs()
    test_desnormalizar_com_ncs()
    test_gerar_planilha_excel_buffer()
    print("\nTodos os testes de data_service passaram com sucesso!")
