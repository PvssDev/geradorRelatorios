# -*- coding: utf-8 -*-
import os
import re
import tempfile
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

def extrair_ncs_e_fotos_anterior(documento_anterior):
    """
    Lê o documento do monitoramento anterior (.docx), extrai as NCs e suas
    respectivas fotos da direita (novas no anterior, antigas no atual)
    para trechos que não estejam com status "Sanada".
    
    Retorna uma lista de dicionários:
    [
        {
            "id_nc": str,
            "constatacao": str,
            "pista": str,
            "trecho": str,
            "old_photo_path": str,
            "old_legend": str
        },
        ...
    ]
    """
    result = []
    if not documento_anterior:
        return result

    try:
        # Se for um objeto BytesIO do Streamlit, docx consegue ler diretamente
        doc = Document(documento_anterior)
        body = doc.element.body

        # 1. Extrair status das NCs a partir do Quadro 1 (primeira tabela)
        status_ncs = {}
        nc_details = {}
        if len(doc.tables) > 0:
            q1 = doc.tables[0]
            for row in q1.rows[1:]:
                cells = row.cells
                if len(cells) < 3:
                    continue
                txt0 = cells[0].text.strip()
                txt1 = cells[1].text.strip()
                txt2 = cells[2].text.strip()
                if txt0 == txt1 == txt2:
                    continue
                
                # Extrair o ID base (ex: NC_01_SH04)
                m = re.search(r'(NC_\d+_[A-Za-z0-9]+)', txt0, re.IGNORECASE)
                if m:
                    id_nc = m.group(1).upper()
                    status_ncs[id_nc] = txt2
                    nc_details[id_nc] = {
                        "constatacao": txt1
                    }

        # 2. Varrer o corpo do documento para encontrar as fotos do apêndice
        temp_dir = tempfile.gettempdir()
        extracted_dir = os.path.join(temp_dir, "arpe_extracted_photos")
        os.makedirs(extracted_dir, exist_ok=True)

        current_trecho = "PE-024"
        current_pista = "SUL"
        current_nc_id = None
        current_nc_desc = ""
        
        in_appendix = False
        photo_count_per_nc = {}

        # Loop pelos elementos do corpo
        for child in body:
            tag = child.tag.split('}')[-1]
            if tag == 'p':
                p_text = Paragraph(child, doc).text.strip()
                if not p_text:
                    continue
                
                # Detecta início do Apêndice
                if "APÊNDICE" in p_text.upper() or "MEMORIAL FOTOGRÁFICO" in p_text.upper():
                    in_appendix = True
                
                if in_appendix:
                    # Detecta pista ou trecho
                    if "PISTA SENTIDO" in p_text.upper():
                        pista_m = re.search(r'PISTA SENTIDO\s*([A-Za-z\s]+)', p_text, re.IGNORECASE)
                        if pista_m:
                            current_pista = pista_m.group(1).strip().upper()
                        trecho_m = re.search(r'(RODOVIA(?:\s+ESTADUAL)?\s*[A-Za-z0-9\s-]+)', p_text, re.IGNORECASE)
                        if trecho_m:
                            current_trecho = trecho_m.group(1).strip()
                    
                    # Detecta ID de NC
                    m_nc = re.search(r'(NC_\d+_[A-Za-z0-9]+)', p_text, re.IGNORECASE)
                    if m_nc:
                        current_nc_id = m_nc.group(1).upper()
                        # Descrição opcional que vem na linha
                        parts = p_text.split('-', 2)
                        if len(parts) >= 3:
                            current_nc_desc = parts[2].strip()
                        elif len(parts) == 2:
                            current_nc_desc = parts[1].strip()
                        else:
                            current_nc_desc = p_text

            elif tag == 'tbl':
                t = Table(child, doc)
                
                # Detecta início do Apêndice caso esteja na tabela banner
                if not in_appendix:
                    for r in t.rows:
                        for cell in r.cells:
                            c_txt = cell.text.upper()
                            if "APÊNDICE" in c_txt or "MEMORIAL FOTOGRÁFICO" in c_txt:
                                in_appendix = True
                                break
                        if in_appendix:
                            break
                
                if in_appendix and current_nc_id:
                    # Verifica se é uma tabela de fotos de 2x2
                    if len(t.rows) == 2 and len(t.columns) == 2:
                        status = status_ncs.get(current_nc_id, "Pendente")
                        # Se já está Sanada no anterior, não deve ir para o novo monitoramento
                        if status.strip().lower() == "sanada":
                            continue
                        
                        # Extrai a foto da direita (novas fotos do monitoramento anterior)
                        cell_img = t.cell(0, 1)
                        cell_leg = t.cell(1, 1)
                        
                        drawings = cell_img._element.xpath('.//w:drawing')
                        if drawings:
                            drawing = drawings[0]
                            embeds = drawing.xpath('.//a:blip/@r:embed')
                            if embeds:
                                rId = embeds[0]
                                img_part = doc.part.related_parts[rId]
                                img_bytes = img_part.image.blob
                                
                                # Define extensão correta
                                ext = ".jpg"
                                if "png" in img_part.content_type:
                                    ext = ".png"
                                
                                idx = photo_count_per_nc.get(current_nc_id, 0) + 1
                                photo_count_per_nc[current_nc_id] = idx
                                
                                photo_name = f"{current_nc_id}_{idx}{ext}"
                                photo_path = os.path.join(extracted_dir, photo_name)
                                
                                with open(photo_path, "wb") as f:
                                    f.write(img_bytes)
                                
                                # Legenda anterior
                                legend_text = cell_leg.text.strip()
                                
                                result.append({
                                    "id_nc": current_nc_id,
                                    "constatacao": nc_details.get(current_nc_id, {}).get("constatacao", current_nc_desc),
                                    "pista": current_pista,
                                    "trecho": current_trecho,
                                    "old_photo_path": photo_path,
                                    "old_legend": legend_text
                                })
                                
    except Exception as e:
        print(f"Erro ao extrair NCs e fotos do documento anterior: {e}")
        
    return result
