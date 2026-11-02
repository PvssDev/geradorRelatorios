import sys
import os
import pandas as pd
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

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
    assert grouped[0]["localizacao_formatada"] == "Esquerda/\nFoto 01"
    assert grouped[0]["_mesclar_localizacao"] is False

    assert grouped[1]["Codificação"] == "CRA.ST601.2794-2834/2026.002"
    assert grouped[1]["localizacao_formatada"] == "Direita/\nFoto 02"
    assert grouped[1]["_mesclar_localizacao"] is False


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
    assert grouped[0]["_mesclar_localizacao"] is True
    assert grouped[1]["localizacao_formatada"] == "Direita/\nFotos 01 e 02"
    assert grouped[1]["_mesclar_localizacao"] is True


def test_apendice_legenda_contraida_e_fed():
    related = [
        {
            "Foto": "foto1.jpg",
            "Nº": 1,
            "Identificação": "CRA.ST601.2794-2834/2026.001",
            "Codificação": "CRA.ST601.2794-2834/2026.001",
            "Não Conformidade": "TRR",
            "Direção (faixa)": "Esquerda",
            "Data da Foto": "23/04/2026"
        },
        {
            "Foto": "foto2.jpg",
            "Nº": 2,
            "Identificação": "CRA.ST601.2794-2834/2026.002",
            "Codificação": "CRA.ST601.2794-2834/2026.002",
            "Não conformidade": "J",
            "Direção (faixa)": "Direita",
            "Data da Foto": "23/04/2026"
        }
    ]

    cod_grp, siglas_grp, faixa_grp = consolidar_dados_legenda_grupo_cra(related)
    assert cod_grp == "CRA.ST601.2794-2834/2026.001 e 002."
    assert "TRR" in siglas_grp and "J" in siglas_grp
    assert faixa_grp == "FED"

    leg1 = formatar_legenda_foto_cra(
        num=1,
        codificacao=cod_grp,
        siglas_ou_ncs=siglas_grp,
        faixa=faixa_grp,
        data_foto="23/04/2026"
    )
    leg2 = formatar_legenda_foto_cra(
        num=2,
        codificacao=cod_grp,
        siglas_ou_ncs=siglas_grp,
        faixa=faixa_grp,
        data_foto="23/04/2026"
    )

    assert "CRA.ST601.2794-2834/2026.001 e 002." in leg1
    assert "Trincas isoladas no revestimento (TRR)" in leg1
    assert "Trincas interligadas (J)" in leg1
    assert "na FED (23/04/2026)." in leg1
    assert leg1.startswith("Foto 1 – ")

    assert "CRA.ST601.2794-2834/2026.001 e 002." in leg2
    assert "na FED (23/04/2026)." in leg2
    assert leg2.startswith("Foto 2 – ")
