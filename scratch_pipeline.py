import pandas as pd
import sys
import os
from docx import Document

sys.path.append(os.path.join(os.getcwd(), 'src'))
from reports.cra_monitoramento import CraMonitoramentoReport
from sections.finalizacao.finalizacao import gerar_secao_finalizacao
import utils

# Create dummy row
row = pd.Series({
    "ID da Fiscalização": "=ID da Fiscalização=",
    "Data": "20/04/2026",
    "Local": "CRA"
})

# Create dummy nc_df
data = {
    "ID da Fiscalização": ["=ID da Fiscalização="],
    "Não Conformidade": ["=Não Conformidade="],
    "Identificação": ["=Identificação 1="],
    "Observações": ["=legenda da foto atual="],
    "Determinação": ["=POSICIONAMENTO CRA="],
    "Situação": ["Pendente"],
    "Foto": [""],
    "Foto Anterior": [""],
    "Pista": ["=Pista="],
    "Trecho": ["=Trecho="]
}
nc_df = pd.DataFrame(data)

report_config = CraMonitoramentoReport()
doc = Document()

# Call generating function
gerar_secao_finalizacao(doc, row, 1, nc_df, "fotos_dir", report_config)

doc.save("test_output.docx")
print("Saved to test_output.docx")
