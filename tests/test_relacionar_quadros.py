# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pandas as pd
from sections.quadros.quadros import agrupar_registros, criar_tabela_quadros
from docx import Document
from reports.cra import CraReport


def test_agrupar_registros_mesma_sigla():
    config = CraReport()
    records = [
        {
            "ID da Fiscalização": "FISC-01",
            "Nº": 1,
            "Codificação": "CRA.ST601.2790-2794/2026.001",
            "Não Conformidade": "FI",
            "Ponto de Atenção": "",
            "Direção (faixa)": "Faixa 1",
            "Fundamento da infração": "Art. 10",
            "Determinação": "Corrigir",
            "grupo_relacao": "grp_01"
        },
        {
            "ID da Fiscalização": "FISC-01",
            "Nº": 2,
            "Codificação": "CRA.ST601.2790-2794/2026.001",
            "Não Conformidade": "FI",
            "Ponto de Atenção": "",
            "Direção (faixa)": "Faixa 1",
            "Fundamento da infração": "Art. 10",
            "Determinação": "Corrigir",
            "grupo_relacao": "grp_01"
        }
    ]
    df = pd.DataFrame(records)
    grouped = agrupar_registros(df, report_config=config)
    assert len(grouped) == 1
    assert "Fotos 01 e 02" in grouped[0]["localizacao_formatada"]
    assert grouped[0]["Codificação"] == "CRA.ST601.2790-2794/2026.001"


def test_agrupar_registros_siglas_diferentes_n_para_1():
    config = CraReport()
    records = [
        {
            "ID da Fiscalização": "FISC-01",
            "Nº": 1,
            "Codificação": "CRA.ST601.2790-2794/2026.001",
            "Não Conformidade": "FI",
            "Ponto de Atenção": "",
            "Direção (faixa)": "Faixa 1",
            "Fundamento da infração": "Art. 10",
            "Determinação": "Corrigir",
            "grupo_relacao": "grp_01"
        },
        {
            "ID da Fiscalização": "FISC-01",
            "Nº": 2,
            "Codificação": "CRA.ST601.2790-2794/2026.002",
            "Não Conformidade": "P",
            "Ponto de Atenção": "",
            "Direção (faixa)": "Faixa 1",
            "Fundamento da infração": "Art. 10",
            "Determinação": "Corrigir",
            "grupo_relacao": "grp_01"
        }
    ]
    df = pd.DataFrame(records)
    grouped = agrupar_registros(df, report_config=config)
    # Devem existir 2 linhas (1 para cada sigla e sua codificação)
    assert len(grouped) == 2
    assert grouped[0]["Codificação"] == "CRA.ST601.2790-2794/2026.001"
    assert grouped[0]["Não Conformidade"] == "FI"
    assert "Fotos 01 e 02" in grouped[0]["localizacao_formatada"]

    assert grouped[1]["Codificação"] == "CRA.ST601.2790-2794/2026.002"
    assert grouped[1]["Não Conformidade"] == "P"
    assert "Fotos 01 e 02" in grouped[1]["localizacao_formatada"]

    # Testa a criação da tabela no Word e a mesclagem vertical
    doc = Document()
    criar_tabela_quadros(doc, df, is_pa=False, report_config=config)
    table = doc.tables[0]
    # Header: 2 linhas, Dados: 2 linhas, Total: 1 linha -> Total de 5 linhas
    assert len(table.rows) == 5


def test_foto_ja_em_nc_identifica_fotos_usadas():
    from services.image_service import obter_nomes_fotos_em_nc, foto_esta_em_nc

    temp_nc = [
        {"Foto": "Foto1.jpg", "Não Conformidade": "FI", "Ponto de Atenção": ""},
        {"Foto": "Foto2.jpg", "Não Conformidade": "P", "Ponto de Atenção": "", "is_relacionado": True}
    ]
    nomes_em_nc = obter_nomes_fotos_em_nc(temp_nc)

    assert bool(foto_esta_em_nc("Foto1.jpg", nomes_em_nc)) is True
    assert bool(foto_esta_em_nc("Foto2.jpg", nomes_em_nc)) is True
    assert bool(foto_esta_em_nc("Foto3.jpg", nomes_em_nc)) is False


def test_relacao_com_modificacao_de_faixa():
    config = CraReport()
    records = [
        {
            "ID da Fiscalização": "FISC-01",
            "Nº": 1,
            "Codificação": "CRA.ST601.2790-2794/2026.001",
            "Não Conformidade": "FI",
            "Ponto de Atenção": "",
            "Direção (faixa)": "Faixa 1",
            "Fundamento da infração": "Art. 10",
            "Determinação": "Corrigir",
            "grupo_relacao": "grp_01"
        },
        {
            "ID da Fiscalização": "FISC-01",
            "Nº": 2,
            "Codificação": "CRA.ST601.2790-2794/2026.001",
            "Não Conformidade": "FI",
            "Ponto de Atenção": "",
            "Direção (faixa)": "Faixa 2 - Sul",
            "Fundamento da infração": "Art. 10",
            "Determinação": "Corrigir",
            "grupo_relacao": "grp_01"
        }
    ]
    df = pd.DataFrame(records)
    grouped = agrupar_registros(df, report_config=config)
    assert len(grouped) == 1
    # Mantém o grupo de fotos 01 e 02
    assert "Fotos 01 e 02" in grouped[0]["localizacao_formatada"]


def test_verificar_foto_elegivel_relacionar_regras_estritas():
    from services.image_service import verificar_foto_elegivel_relacionar, extrair_nome_foto

    class FakeUploadedFile:
        def __init__(self, name):
            self.name = name

    # 1. Sem registros em temp_nc -> False
    pode, motivo = verificar_foto_elegivel_relacionar("foto1.jpg", [])
    assert pode is False
    assert "Adicione um registro primeiro" in motivo

    # 2. Com 1 registro normal (não relacionado)
    temp_nc = [
        {"Foto": "foto1.jpg", "Não Conformidade": "FI", "Ponto de Atenção": "", "is_relacionado": False}
    ]

    # Mesma foto do registro anterior -> False
    pode, motivo = verificar_foto_elegivel_relacionar("foto1.jpg", temp_nc)
    assert pode is False
    assert "já é a foto do registro anterior" in motivo

    # Nova foto ainda não usada -> True
    pode, motivo = verificar_foto_elegivel_relacionar("foto2.jpg", temp_nc)
    assert pode is True

    # Testando com objeto similar a UploadedFile
    fake_foto2 = FakeUploadedFile("foto2.jpg")
    pode, motivo = verificar_foto_elegivel_relacionar(fake_foto2, temp_nc)
    assert pode is True

    # 3. Agora adicionamos foto2 como relacionada e marcamos ambas com is_relacionado = True
    temp_nc[0]["is_relacionado"] = True
    temp_nc.append({
        "Foto": "foto2.jpg",
        "Não Conformidade": "FI",
        "Ponto de Atenção": "",
        "is_relacionado": True
    })

    # foto1 (já adicionada e já relacionada) não pode ser relacionada
    pode, motivo = verificar_foto_elegivel_relacionar("foto1.jpg", temp_nc)
    assert pode is False

    # foto2 (já adicionada e já relacionada) não pode ser relacionada
    pode, motivo = verificar_foto_elegivel_relacionar("foto2.jpg", temp_nc)
    assert pode is False

    # foto3 (nova foto) tentando se relacionar ao último registro (que já é relacionado):
    # Deve ser BLOQUEADA porque o último registro já está relacionado a outra foto!
    pode, motivo = verificar_foto_elegivel_relacionar("foto3.jpg", temp_nc)
    assert pode is False
    assert "já faz parte de um relacionamento" in motivo

    # 4. Se o usuário cadastrar um novo registro normal (foto4)
    temp_nc.append({
        "Foto": "foto4.jpg",
        "Não Conformidade": "P",
        "Ponto de Atenção": "",
        "is_relacionado": False
    })

    # Agora foto3 (que nunca foi adicionada nem relacionada) pode se relacionar à foto4
    pode, motivo = verificar_foto_elegivel_relacionar("foto3.jpg", temp_nc)
    assert pode is True

    # Mas se tentar relacionar foto1 ou foto2 (que já foram relacionadas anteriormente)
    pode, motivo = verificar_foto_elegivel_relacionar("foto1.jpg", temp_nc)
    assert pode is False
    assert "já foi relacionada" in motivo

    pode, motivo = verificar_foto_elegivel_relacionar("foto2.jpg", temp_nc)
    assert pode is False
    assert "já foi relacionada" in motivo


def test_contagem_codificacao_cra_nc_e_pt_independentes():
    from utils import obter_proximo_numero_sequencial_cra, calcular_codificacao_cra

    # Lista vazia -> inicia em 1
    assert obter_proximo_numero_sequencial_cra([], "FISC-01", "Não Conformidade") == 1
    assert obter_proximo_numero_sequencial_cra([], "FISC-01", "Ponto de Atenção") == 1

    temp_nc = [
        {
            "ID da Fiscalização": "FISC-01",
            "Não Conformidade": "FI",
            "Ponto de Atenção": "",
            "Codificação": "CRA.ST601.2790-2794/2026.001"
        },
        {
            "ID da Fiscalização": "FISC-01",
            "Não Conformidade": "P",
            "Ponto de Atenção": "",
            "Codificação": "CRA.ST601.2790-2794/2026.002"
        }
    ]

    # Próxima NC deve ser 3 (.003)
    assert obter_proximo_numero_sequencial_cra(temp_nc, "FISC-01", "Não Conformidade") == 3

    # Mas o próximo Ponto de Atenção ainda deve ser 1 (.001) porque nenhum PT foi adicionado ainda
    assert obter_proximo_numero_sequencial_cra(temp_nc, "FISC-01", "Ponto de Atenção") == 1

    # Adicionando um Ponto de Atenção
    temp_nc.append({
        "ID da Fiscalização": "FISC-01",
        "Não Conformidade": "",
        "Ponto de Atenção": "D",
        "Codificação": "CRA.ST601.2790-2794/2026.001"
    })

    # Próximo PT agora deve ser 2 (.002)
    assert obter_proximo_numero_sequencial_cra(temp_nc, "FISC-01", "Ponto de Atenção") == 2
    # Próxima NC continua sendo 3 (.003)
    assert obter_proximo_numero_sequencial_cra(temp_nc, "FISC-01", "Não Conformidade") == 3


def test_calcular_codificacao_cra_sem_duplicacao_offset():
    from utils import calcular_codificacao_cra

    # Base sem sufixo
    cod = calcular_codificacao_cra("CRA.ST601.2790-2794", data_fisc="01/03/2026", seq_idx=1)
    assert cod == "CRA.ST601.2790-2794/2026.001"

    cod_b = calcular_codificacao_cra("CRA.ST601.2790-2794", data_fisc="01/03/2026", seq_idx=2)
    assert cod_b == "CRA.ST601.2790-2794/2026.002"

    # Base com offset inicial (ex: 81)
    cod2 = calcular_codificacao_cra("CRA.ST601.2790-2794/2026.081", data_fisc="01/03/2026", seq_idx=1)
    assert cod2 == "CRA.ST601.2790-2794/2026.081"

    cod3 = calcular_codificacao_cra("CRA.ST601.2790-2794/2026.081", data_fisc="01/03/2026", seq_idx=2)
    assert cod3 == "CRA.ST601.2790-2794/2026.082"

