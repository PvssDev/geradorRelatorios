import sys
import os
import pandas as pd
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'src')))

from sections.quadros.quadros import agrupar_registros
from reports.cra import CraReport
from core.rules.cra_rules import (
    formatar_codificacoes_contraidas_cra,
    consolidar_dados_legenda_grupo_cra,
    formatar_legenda_foto_cra,
    combinar_faixas_relacionadas_cra
)


def test_quadro1_faixas_distintas():
    cra_rep = CraReport()
    df_diff = pd.DataFrame([
        {
            "ID da Fiscalização": "FISC_01",
            "Nº": 1,
            "Foto": "foto1.jpg",
            "Identificação": "CRA.ST601.2794-2834/2026.001",
            "Codificação": "CRA.ST601.2794-2834/2026.001",
            "Não Conformidade": "TRR",
            "Direção (faixa)": "Esquerda",
            "grupo_relacao": "grp_1"
        },
        {
            "ID da Fiscalização": "FISC_01",
            "Nº": 2,
            "Foto": "foto2.jpg",
            "Identificação": "CRA.ST601.2794-2834/2026.002",
            "Codificação": "CRA.ST601.2794-2834/2026.002",
            "Não conformidade": "J",
            "Direção (faixa)": "Direita",
            "grupo_relacao": "grp_1"
        }
    ])

    grouped = agrupar_registros(df_diff, report_config=cra_rep)
    assert len(grouped) == 2
    assert grouped[0]["Codificação"] == "CRA.ST601.2794-2834/2026.001"
    assert grouped[0]["localizacao_formatada"] == "Esquerda e Direita/\nFotos 01 e 02"
    assert grouped[0]["Direção (faixa)"] == "Esquerda e Direita"

    assert grouped[1]["Codificação"] == "CRA.ST601.2794-2834/2026.002"
    assert grouped[1]["localizacao_formatada"] == "Esquerda e Direita/\nFotos 01 e 02"
    assert grouped[1]["Direção (faixa)"] == "Esquerda e Direita"


def test_quadro1_mesma_faixa():
    cra_rep = CraReport()
    df_same = pd.DataFrame([
        {
            "ID da Fiscalização": "FISC_01",
            "Nº": 1,
            "Foto": "foto1.jpg",
            "Identificação": "CRA.ST601.2794-2834/2026.001",
            "Codificação": "CRA.ST601.2794-2834/2026.001",
            "Não Conformidade": "TRR",
            "Direção (faixa)": "Direita",
            "grupo_relacao": "grp_1"
        },
        {
            "ID da Fiscalização": "FISC_01",
            "Nº": 2,
            "Foto": "foto2.jpg",
            "Identificação": "CRA.ST601.2794-2834/2026.002",
            "Codificação": "CRA.ST601.2794-2834/2026.002",
            "Não conformidade": "J",
            "Direção (faixa)": "Direita",
            "grupo_relacao": "grp_1"
        }
    ])

    grouped = agrupar_registros(df_same, report_config=cra_rep)
    assert len(grouped) == 2
    assert grouped[0]["localizacao_formatada"] == "Direita/\nFotos 01 e 02"
    assert grouped[0]["Direção (faixa)"] == "Direita"
    assert grouped[1]["localizacao_formatada"] == "Direita/\nFotos 01 e 02"
    assert grouped[1]["Direção (faixa)"] == "Direita"


def test_apendice_legenda_contraida_e_fed():
    related = [
        {
            "Foto": "foto1.jpg",
            "Identificação": "CRA.ST601.2790-2794/2026.001",
            "Codificação": "CRA.ST601.2790-2794/2026.001",
            "Não Conformidade": "TRR",
            "Direção (faixa)": "Esquerda",
            "Data da Fiscalização": "12/03/2026"
        },
        {
            "Foto": "foto2.jpg",
            "Identificação": "CRA.ST601.2790-2794/2026.002",
            "Codificação": "CRA.ST601.2790-2794/2026.002",
            "Não Conformidade": "J",
            "Direção (faixa)": "Direita",
            "Data da Fiscalização": "12/03/2026"
        }
    ]

    contraida = formatar_codificacoes_contraidas_cra(
        ["CRA.ST601.2790-2794/2026.001", "CRA.ST601.2790-2794/2026.002"]
    )
    assert "CRA.ST601.2790-2794/2026.001 e 002" in contraida

    cod_contraida, descricoes_siglas, faixa_sigla = consolidar_dados_legenda_grupo_cra(related)
    assert faixa_sigla == "FED"
    assert "TRR" in descricoes_siglas
    assert "J" in descricoes_siglas

    legenda1 = formatar_legenda_foto_cra(
        num="1",
        codificacao=cod_contraida,
        siglas_ou_ncs=descricoes_siglas,
        faixa=faixa_sigla,
        data_foto="12/03/2026"
    )
    assert "Foto 1" in legenda1
    assert "CRA.ST601.2790-2794/2026.001 e 002" in legenda1
    assert "FED" in legenda1
    assert "12/03/2026" in legenda1
