import sys
import os
import io
import pandas as pd
from PIL import Image

sys.path.append(os.path.join(os.getcwd(), 'src'))
from report import gerar_relatorio
from app import gerar_planilha_excel_buffer

# Mock state
temp_fisc = [{
    "ID da Fiscalização": "=ID da Fiscalização=",
    "Data": "20/04/2026",
    "Hora": "",
    "Cidade": "",
    "Local": "CRA",
    "Pessoal Responsável": "João",
    "Coordenador": "Maria",
    "Contrato": "Contrato",
    "Período": "=Período=",
    "Relatório Gerado": False
}]

temp_nc = [{
    "ID da Fiscalização": "=ID da Fiscalização=",
    "Nº": 1,
    "Terminal": "CRA",
    "Pista": "Sul",
    "Trecho": "KM 0",
    "Não Conformidade": "NC 1",
    "Ponto de Atenção": "",
    "Foto": "dummy.jpg",
    "Foto Anterior": "",
    "Legenda Anterior": "",
    "Legenda da Foto": "=legenda=",
    "Observações": "=legenda=",
    "Identificação": "NC 1",
    "Direção (faixa)": "",
    "Fundamento da infração": "",
    "Determinação": "Posicionamento",
    "Situação": "Pendente",
    "Análise ARPE": "Análise"
}]

abas = {
    "fiscalizacoes": "Fiscalização",
    "nao_conformidades": "Não Conformidades",
    "observacoes": "Observações",
    "recomendacoes": "Recomendações"
}

excel_buffer = gerar_planilha_excel_buffer(temp_fisc, temp_nc, [], [], abas)

# Create dummy image
os.makedirs("fotos", exist_ok=True)
img = Image.new('RGB', (100, 100), color = 'red')
img.save('fotos/dummy.jpg')

# create an empty docx for documento_anterior
from docx import Document
doc_prev = Document()
doc_prev.save("prev.docx")

try:
    with open("prev.docx", "rb") as f:
        doc_bytes = io.BytesIO(f.read())
        doc_bytes.name = "prev.docx"
        gerar_relatorio(
            gerar_todos=True,
            caminho_planilha=excel_buffer,
            abas=abas,
            base_dir=os.path.join(os.getcwd(), 'src'),
            fotos_dir="fotos",
            documento_anterior=doc_bytes,
            tipo_relatorio="CRA_MONITORAMENTO",
            ids_selecionados=["=ID da Fiscalização="]
        )
    print("SUCCESS")
except Exception as e:
    import traceback
    traceback.print_exc()
