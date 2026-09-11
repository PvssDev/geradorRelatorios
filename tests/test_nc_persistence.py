import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from services.data_service import desnormalizar_fiscalizacoes, gerar_planilha_excel_buffer
import pandas as pd


def test_adicao_multiplas_ncs_fiscalizacao_preserva_dados():
    """
    Garante que múltiplas Não Conformidades adicionadas à mesma fiscalização,
    inclusive com 'Identificação' vazia, mantêm seus dados e Não Conformidades
    distintas sem que uma reverta para a antiga.
    """
    temp_fiscalizacoes = [
        {
            "ID da Fiscalização": "FISC-CRA-01",
            "Data": "20/05/2026",
            "Hora": "09:00",
            "Cidade": "Cabo de Santo Agostinho",
            "Local": "Complexo Suape",
            "Pessoal Responsável": "Técnico 1",
            "Coordenador": "Coord 1",
            "Contrato": "CT. nº 043/2011",
            "Período": "Manhã"
        }
    ]

    # Duas NCs consecutivas com identificação vazia (caso típico de inserção por fotos)
    temp_nc = [
        {
            "ID da Fiscalização": "FISC-CRA-01",
            "Nº": 1,
            "Terminal": "Complexo Suape",
            "Pista": "Norte",
            "Trecho": "KM 10",
            "Não Conformidade": "FI",
            "Ponto de Atenção": "",
            "Foto": "foto1.jpg",
            "Observações": "Fissura na pista norte",
            "Identificação": "",
            "Direção (faixa)": "Faixa 1",
            "Fundamento da infração": "Subitem 4.2",
            "Determinação": "Reparo imediato",
            "Situação": "Pendente"
        },
        {
            "ID da Fiscalização": "FISC-CRA-01",
            "Nº": 2,
            "Terminal": "Complexo Suape",
            "Pista": "Sul",
            "Trecho": "KM 15",
            "Não Conformidade": "TTL",
            "Ponto de Atenção": "",
            "Foto": "foto2.jpg",
            "Observações": "Trinca transversal longa",
            "Identificação": "",
            "Direção (faixa)": "Faixa 2",
            "Fundamento da infração": "Subitem 4.3",
            "Determinação": "Selagem das trincas",
            "Situação": "Pendente"
        }
    ]

    flat = desnormalizar_fiscalizacoes(temp_fiscalizacoes, temp_nc)
    assert len(flat) == 2

    # Verifica que o item 1 manteve FI e o item 2 manteve TTL
    assert flat[0]["Não conformidade"] == "FI"
    assert flat[0]["Fotos"] == "foto1.jpg"
    assert flat[0]["Pista"] == "Norte"

    assert flat[1]["Não conformidade"] == "TTL"
    assert flat[1]["Fotos"] == "foto2.jpg"
    assert flat[1]["Pista"] == "Sul"


def test_edicao_nc_atualiza_valor_e_reflete_na_planilha():
    """
    Testa a simulação de edição de uma NC existente:
    modificando o registro em memória e verificando que a planilha gerada
    reflete a alteração corretamente sem manter o valor antigo.
    """
    temp_fiscalizacoes = [
        {
            "ID da Fiscalização": "FISC-SOC-01",
            "Data": "15/06/2026",
            "Local": "Terminal Integrado TIP",
            "Pessoal Responsável": "Técnico 2",
            "Coordenador": "Coord 2",
            "Contrato": "CT. nº 001/2020"
        }
    ]

    temp_nc = [
        {
            "ID da Fiscalização": "FISC-SOC-01",
            "Nº": 1,
            "Terminal": "Terminal Integrado TIP",
            "Não Conformidade": "Antiga NC Inicial",
            "Foto": "foto_velha.jpg",
            "Observações": "Problema inicial",
            "Identificação": "NC-01",
            "Determinação": "Corrigir",
            "Situação": "Pendente"
        }
    ]

    # Simula edição do registro (como feito pelo modal de edição corrigido)
    target = temp_nc[0]
    target["Não Conformidade"] = "Nova NC Corrigida e Salva"
    target["Observações"] = "Observação atualizada com sucesso"
    target["Determinação"] = "Nova determinação atualizada"

    buf = gerar_planilha_excel_buffer(temp_fiscalizacoes, temp_nc)
    excel = pd.ExcelFile(buf)
    df_fisc = pd.read_excel(excel, sheet_name="Fiscalizações")
    df_nc = pd.read_excel(excel, sheet_name="Não-conformidades ")

    assert df_fisc["Não conformidade"].iloc[0] == "Nova NC Corrigida e Salva"
    assert df_fisc["Observações"].iloc[0] == "Observação atualizada com sucesso"
    assert df_nc["Não Conformidade"].iloc[0] == "Nova NC Corrigida e Salva"
    assert df_nc["Determinação"].iloc[0] == "Nova determinação atualizada"
