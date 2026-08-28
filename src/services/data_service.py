# -*- coding: utf-8 -*-
import io
import os
import pandas as pd


def desnormalizar_fiscalizacoes(temp_fiscalizacoes: list, temp_nc: list) -> list:
    """
    Desnormaliza (achata) as listas relacionais de fiscalizações e não-conformidades
    para o formato tabular da aba 'Fiscalizações' da planilha de trabalho.
    
    Se uma fiscalização não possuir NCs associadas, gera uma linha com os dados da fiscalização
    e campos de NC em branco. Se possuir uma ou mais NCs, replica os dados da fiscalização
    para cada item de NC vinculado pelo 'ID da Fiscalização'.
    """
    flat_fiscalizacoes = []
    if not temp_fiscalizacoes:
        return flat_fiscalizacoes

    for fisc in temp_fiscalizacoes:
        id_fisc = fisc.get("ID da Fiscalização", "")
        ncs = [nc for nc in temp_nc if nc.get("ID da Fiscalização") == id_fisc] if temp_nc else []
        
        base_fisc = {
            "ID da Fiscalização": fisc.get("ID da Fiscalização", ""),
            "Data": fisc.get("Data", ""),
            "Hora": fisc.get("Hora", ""),
            "Cidade": fisc.get("Cidade", ""),
            "Local": fisc.get("Local", ""),
            "Pessoal Responsável": fisc.get("Pessoal Responsável", ""),
            "Coordenador": fisc.get("Coordenador", ""),
            "Contrato": fisc.get("Contrato", ""),
            "Período": fisc.get("Período", ""),
            "Relatório Gerado": fisc.get("Relatório Gerado", False)
        }

        if not ncs:
            flat_fiscalizacoes.append({
                **base_fisc,
                "Observações": "",
                "Fotos": "",
                "Não conformidade": "",
                "Ponto de Atenção": "",
                "Pista": "",
                "Trecho": "",
                "Identificação": "",
                "Direção (faixa)": "",
                "Fundamento da infração": "",
                "Determinação": "",
                "Situação": ""
            })
        else:
            for nc in ncs:
                flat_fiscalizacoes.append({
                    **base_fisc,
                    "Observações": nc.get("Observações", nc.get("Legenda da Foto", "")),
                    "Fotos": nc.get("Foto", nc.get("Fotos", "")),
                    "Não conformidade": nc.get("Não Conformidade", nc.get("Não conformidade", "")),
                    "Ponto de Atenção": nc.get("Ponto de Atenção", ""),
                    "Pista": nc.get("Pista", ""),
                    "Trecho": nc.get("Trecho", ""),
                    "Identificação": nc.get("Identificação", ""),
                    "Direção (faixa)": nc.get("Direção (faixa)", ""),
                    "Fundamento da infração": nc.get("Fundamento da infração", ""),
                    "Determinação": nc.get("Determinação", ""),
                    "Situação": nc.get("Situação", "Pendente")
                })

    return flat_fiscalizacoes


def gerar_planilha_excel_buffer(temp_fiscalizacoes: list, temp_nc: list) -> io.BytesIO:
    """
    Gera um buffer binário em memória (io.BytesIO) contendo a planilha Excel
    com as 4 abas padronizadas do sistema:
      1. Fiscalizações
      2. Não-conformidades 
      3. Observações Importantes
      4. Recomendações
    """
    flat_data = desnormalizar_fiscalizacoes(temp_fiscalizacoes, temp_nc)
    
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        pd.DataFrame(flat_data).to_excel(writer, sheet_name="Fiscalizações", index=False)
        pd.DataFrame(temp_nc if temp_nc else []).to_excel(writer, sheet_name="Não-conformidades ", index=False)
        pd.DataFrame().to_excel(writer, sheet_name="Observações Importantes", index=False)
        pd.DataFrame().to_excel(writer, sheet_name="Recomendações", index=False)
    
    excel_buffer.seek(0)
    return excel_buffer


def salvar_fotos_em_diretorio(fotos: list, destino_dir: str) -> None:
    """
    Salva uma lista de arquivos de imagem (Streamlit UploadedFile ou similares)
    no diretório de destino especificado de forma segura.
    """
    if not fotos or not destino_dir:
        return
    
    os.makedirs(destino_dir, exist_ok=True)
    for photo in fotos:
        foto_nome = getattr(photo, "name", str(photo))
        foto_path = os.path.join(destino_dir, os.path.basename(foto_nome))
        
        try:
            if hasattr(photo, "seek"):
                try:
                    photo.seek(0)
                except Exception:
                    pass

            with open(foto_path, "wb") as f:
                if hasattr(photo, "getbuffer"):
                    f.write(photo.getbuffer())
                elif hasattr(photo, "read"):
                    f.write(photo.read())
                elif isinstance(photo, bytes):
                    f.write(photo)
        except Exception as e:
            print(f"Erro ao salvar foto {foto_nome} em {destino_dir}: {e}")
