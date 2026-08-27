import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.join(os.getcwd(), 'src'))
from sections.finalizacao.finalizacao import gerar_secao_finalizacao

data = {
    "ID da Fiscalização": ["=ID da Fiscalização="],
    "Não Conformidade": [""],
    "Identificação": [""],
    "Observações": ["=legenda da foto atual="],
    "Determinação": [""],
    "Situação": ["Pendente"]
}
nc_df = pd.DataFrame(data)

current_ncs = nc_df[nc_df["ID da Fiscalização"].astype(str).str.strip() == "=ID da Fiscalização="].copy()
cols_check = [c for c in ["Não Conformidade", "Identificação", "Observações", "Determinação"] if c in current_ncs.columns]
mask_nc = current_ncs[cols_check].fillna("").astype(str).apply(lambda r_c: any(v.strip() != "" for v in r_c), axis=1)
ncs_reais = current_ncs[mask_nc].copy()
print("ncs_reais length:", len(ncs_reais))
