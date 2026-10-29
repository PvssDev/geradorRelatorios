# -*- coding: utf-8 -*-
import base64
import io
import json
import pytest
from PIL import Image
from fastapi.testclient import TestClient

from api.index import app

client = TestClient(app)


def _criar_foto_teste_bytes(color=(15, 23, 42)) -> bytes:
    img = Image.new("RGB", (320, 240), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=80)
    return buf.getvalue()


def test_health_and_bootstrap_config():
    res_health = client.get("/api/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "ok"

    res_boot = client.get("/api/config/bootstrap")
    assert res_boot.status_code == 200
    data = res_boot.json()
    assert "responsaveis" in data
    assert "coordenadores" in data
    assert "map_siglas" in data
    assert "FI" in data["base_nc_options"]
    assert "TIP Recife" in data["locais_socicam"]
    assert data["contratos_padrao"]["CRA"] == "CT. nº 043/2011"
    assert data["contratos_padrao"]["CRC"] == "CGPE-001/2006"
    assert data["contratos_padrao"]["SOCICAM"] == "CT. nº 1.041.080/08"


@pytest.mark.parametrize(
    "tipo,local,contrato",
    [
        ("CRA", "Rota do Atlântico", "CT. nº 043/2011"),
        ("CRC", "Sistema Viário do Paiva", "CGPE-001/2006"),
        ("SOCICAM", "TIP Recife", "CT. nº 1.041.080/08"),
    ],
)
def test_gerar_relatorio_fiscalizacao_3_concessoes(tipo, local, contrato):
    foto_bytes = _criar_foto_teste_bytes()
    payload = {
        "tipo_relatorio": tipo,
        "categoria_relatorio": "Fiscalização",
        "fiscalizacoes": [
            {
                "ID da Fiscalização": f"2026-{tipo}-01",
                "Data": "29/10/2026",
                "Hora": "10:00" if tipo == "CRA" else "",
                "Cidade": "Recife" if tipo == "CRA" else "",
                "Local": local,
                "Pessoal Responsável": "Alcides Vieira de Azevedo Bezerra",
                "Coordenador": "Maria Ângela Albuquerque de Freitas",
                "Contrato": contrato,
                "Período": "28 a 29/10/2026",
                "Relatório Gerado": False,
            }
        ],
        "registros_nc": [
            {
                "ID da Fiscalização": f"2026-{tipo}-01",
                "Nº": 1,
                "Terminal": local,
                "Pista": "Norte" if tipo == "CRA" else "",
                "Trecho": "VPE-034" if tipo == "CRA" else "",
                "Não Conformidade": "FI",
                "Ponto de Atenção": "",
                "Foto": "evidencia_01.jpg",
                "Foto Anterior": "",
                "Legenda Anterior": "",
                "Observações": "Fissura longitudinal identificada na pista.",
                "Identificação": "FI",
                "Direção (faixa)": "Faixa 1" if tipo == "CRA" else "",
                "Fundamento da infração": "Cláusula 12.1",
                "Determinação": "Executar selagem de trinca em 15 dias.",
                "Situação": "Pendente",
                "Análise ARPE": "",
            }
        ],
    }

    response = client.post(
        "/api/relatorios/gerar",
        data={"payload_json": json.dumps(payload)},
        files=[("fotos_atuais", ("evidencia_01.jpg", foto_bytes, "image/jpeg"))],
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert len(body["relatorios"]) == 1
    assert body["relatorios"][0]["nome"] == f"relatorio_2026-{tipo}-01.docx"
    docx_bytes = base64.b64decode(body["relatorios"][0]["base64"])
    assert len(docx_bytes) > 5000
    assert body["avisos"] == []


@pytest.mark.parametrize(
    "tipo,local,contrato",
    [
        ("CRA", "Rota do Atlântico", "CT. nº 043/2011"),
        ("CRC", "Sistema Viário do Paiva", "CGPE-001/2006"),
        ("SOCICAM", "TIP Recife", "CT. nº 1.041.080/08"),
    ],
)
def test_gerar_relatorio_monitoramento_3_concessoes(tipo, local, contrato):
    # Primeiro gera um docx inicial para servir de documento anterior no monitoramento
    foto_ant_bytes = _criar_foto_teste_bytes(color=(120, 30, 30))
    foto_nova_bytes = _criar_foto_teste_bytes(color=(30, 120, 60))

    init_payload = {
        "tipo_relatorio": tipo,
        "categoria_relatorio": "Fiscalização",
        "fiscalizacoes": [
            {
                "ID da Fiscalização": f"FISC-{tipo}-ANT",
                "Data": "01/09/2026",
                "Hora": "09:00",
                "Cidade": "Recife",
                "Local": local,
                "Pessoal Responsável": "Alcides Vieira de Azevedo Bezerra",
                "Coordenador": "Maria Ângela Albuquerque de Freitas",
                "Contrato": contrato,
                "Período": "01/09/2026",
                "Relatório Gerado": False,
            }
        ],
        "registros_nc": [
            {
                "ID da Fiscalização": f"FISC-{tipo}-ANT",
                "Nº": 1,
                "Terminal": local,
                "Pista": "Sul",
                "Trecho": "PE-024",
                "Não Conformidade": "FI",
                "Ponto de Atenção": "",
                "Foto": "foto_antiga.jpg",
                "Foto Anterior": "",
                "Legenda Anterior": "",
                "Observações": "Trinca anterior.",
                "Identificação": "NC_01",
                "Direção (faixa)": "Faixa 1",
                "Fundamento da infração": "Contrato",
                "Determinação": "Corrigir",
                "Situação": "Pendente",
                "Análise ARPE": "",
            }
        ],
    }

    res_init = client.post(
        "/api/relatorios/gerar",
        data={"payload_json": json.dumps(init_payload)},
        files=[("fotos_atuais", ("foto_antiga.jpg", foto_ant_bytes, "image/jpeg"))],
    )
    assert res_init.status_code == 200
    doc_anterior_bytes = base64.b64decode(res_init.json()["relatorios"][0]["base64"])

    # Testa o endpoint /api/monitoramento/parse com o docx anterior
    res_parse = client.post(
        "/api/monitoramento/parse",
        files=[
            (
                "arquivo",
                (
                    f"relatorio_fiscalizacao_{tipo}.docx",
                    doc_anterior_bytes,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                ),
            )
        ],
    )
    assert res_parse.status_code == 200

    # Agora gera o relatório de Monitoramento
    mon_payload = {
        "tipo_relatorio": tipo,
        "categoria_relatorio": "Monitoramento",
        "fiscalizacoes": [
            {
                "ID da Fiscalização": f"MON-{tipo}-01",
                "Data": "29/10/2026",
                "Hora": "",
                "Cidade": "",
                "Local": local,
                "Pessoal Responsável": "Alcides Vieira de Azevedo Bezerra",
                "Coordenador": "Maria Ângela Albuquerque de Freitas",
                "Contrato": contrato,
                "Período": "29/10/2026",
                "Relatório Gerado": False,
            }
        ],
        "registros_nc": [
            {
                "ID da Fiscalização": f"MON-{tipo}-01",
                "Nº": 1,
                "Terminal": local,
                "Pista": "Sul",
                "Trecho": "PE-024",
                "Não Conformidade": "NC_01",
                "Ponto de Atenção": "",
                "Foto": "foto_atual.jpg",
                "Foto Anterior": "NC_01_1.jpg",
                "Legenda Anterior": "Trinca anterior.",
                "Observações": "Trinca permanece parcialmente aberta.",
                "Identificação": "NC_01",
                "Direção (faixa)": "",
                "Fundamento da infração": "",
                "Determinação": "Concessionária informou programação de reparo.",
                "Situação": "Pendente",
                "Análise ARPE": "Permanece pendente de saneamento definitivo.",
            }
        ],
        "fotos_anteriores_b64": {
            "NC_01_1.jpg": "data:image/jpeg;base64,"
            + base64.b64encode(foto_ant_bytes).decode("utf-8")
        },
    }

    res_mon = client.post(
        "/api/relatorios/gerar",
        data={"payload_json": json.dumps(mon_payload)},
        files=[
            ("fotos_atuais", ("foto_atual.jpg", foto_nova_bytes, "image/jpeg")),
            (
                "documento_anterior",
                (
                    f"relatorio_fiscalizacao_{tipo}.docx",
                    doc_anterior_bytes,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                ),
            ),
        ],
    )
    assert res_mon.status_code == 200, res_mon.text
    mon_body = res_mon.json()
    assert len(mon_body["relatorios"]) == 1
    assert mon_body["relatorios"][0]["nome"] == f"relatorio_MON-{tipo}-01.docx"


def test_relacionar_duas_fotos_mesma_nc_com_direcao_direita_esquerda():
    """
    BDD:
    Dado uma NC da CRA com Direção 'Direita', Codificação 'CRA.ST601.2794-2834/2026.001'
    e uma 2ª foto relacionada no mesmo 'grupo_relacao' com Observações próprias;
    Quando o relatório .docx é gerado;
    Então o Quadro 1 agrupa ambas em 'Direita/ Fotos 01 e 02' e ambas as legendas aparecem.
    """
    from docx import Document

    f1 = _criar_foto_teste_bytes(color=(20, 60, 120))
    f2 = _criar_foto_teste_bytes(color=(120, 60, 20))

    payload = {
        "tipo_relatorio": "CRA",
        "categoria_relatorio": "Fiscalização",
        "compress_images": True,
        "fiscalizacoes": [
            {
                "ID da Fiscalização": "FISC-CRA-REL-01",
                "Data": "29/10/2026",
                "Hora": "09:30",
                "Cidade": "Cabo de Santo Agostinho",
                "Local": "Rota do Atlântico",
                "Pessoal Responsável": "Alcides Vieira de Azevedo Bezerra",
                "Coordenador": "Maria Ângela Albuquerque de Freitas",
                "Contrato": "CT. nº 043/2011",
                "Período": "29/10/2026",
                "Relatório Gerado": False,
            }
        ],
        "registros_nc": [
            {
                "ID da Fiscalização": "FISC-CRA-REL-01",
                "Nº": 1,
                "Terminal": "Rota do Atlântico",
                "Pista": "Sul",
                "Trecho": "PE-009 KM 24+500",
                "Não Conformidade": "FI, P",
                "Ponto de Atenção": "",
                "Foto": "foto_01.jpg",
                "Observações": "fissuras e panela no bordo direito",
                "Identificação": "CRA.ST601.2794-2834/2026.001",
                "Direção (faixa)": "Direita",
                "Fundamento da infração": "Cláusula 14",
                "Determinação": "Recompor revestimento em 7 dias",
                "Situação": "Pendente",
                "grupo_relacao": "FISC-CRA-REL-01_1",
                "is_relacionado": False,
            },
            {
                "ID da Fiscalização": "FISC-CRA-REL-01",
                "Nº": 2,
                "Terminal": "Rota do Atlântico",
                "Pista": "Sul",
                "Trecho": "PE-009 KM 24+520",
                "Não Conformidade": "FI, P",
                "Ponto de Atenção": "",
                "Foto": "foto_02.jpg",
                "Observações": "detalhe aproximado da panela na faixa direita",
                "Identificação": "CRA.ST601.2794-2834/2026.001",
                "Direção (faixa)": "Direita",
                "Fundamento da infração": "Cláusula 14",
                "Determinação": "Recompor revestimento em 7 dias",
                "Situação": "Pendente",
                "grupo_relacao": "FISC-CRA-REL-01_1",
                "is_relacionado": True,
            },
        ],
    }

    res = client.post(
        "/api/relatorios/gerar",
        data={"payload_json": json.dumps(payload)},
        files=[
            ("fotos_atuais", ("foto_01.jpg", f1, "image/jpeg")),
            ("fotos_atuais", ("foto_02.jpg", f2, "image/jpeg")),
        ],
    )
    assert res.status_code == 200, res.text
    docx_bytes = base64.b64decode(res.json()["relatorios"][0]["base64"])
    doc = Document(io.BytesIO(docx_bytes))

    all_tables_text = "\n".join(
        cell.text for tbl in doc.tables for row in tbl.rows for cell in row.cells
    )
    assert "Direita/ Fotos 01 e 02" in all_tables_text
    assert "fissuras e panela no bordo direito" in all_tables_text
    assert "detalhe aproximado da panela na faixa direita" in all_tables_text


def test_comprimir_imagem_acima_de_500kb():
    from services.image_service import comprimir_imagem_para_word

    # Cria imagem ruidosa > 600 KB
    import random

    rng = random.Random(42)
    raw = bytes(rng.getrandbits(8) for _ in range(1400 * 1000 * 3))
    big_img = Image.frombytes("RGB", (1400, 1000), raw)
    buf = io.BytesIO()
    big_img.save(buf, format="PNG")
    original_bytes = buf.getvalue()
    assert len(original_bytes) > 500 * 1024

    compressed = comprimir_imagem_para_word(original_bytes, max_kb=500)
    assert len(compressed) <= 500 * 1024 or len(compressed) < len(original_bytes)

