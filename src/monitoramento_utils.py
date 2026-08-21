# -*- coding: utf-8 -*-
import os
import re
import tempfile
import unicodedata
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

def strip_accents(s):
    if not s:
        return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(s)) if unicodedata.category(c) != 'Mn').upper()

def extrair_ncs_e_fotos_anterior(documento_anterior):
    """
    Lê o documento do monitoramento ou fiscalização anterior (.docx),
    extrai as NCs e suas respectivas fotos da tabela do apêndice.
    
    Retorna uma lista de dicionários com as fotos extraídas.
    """
    result = []
    if not documento_anterior:
        return result

    try:
        # Garante o reposicionamento do ponteiro do arquivo Streamlit (BytesIO)
        if hasattr(documento_anterior, "seek"):
            try:
                documento_anterior.seek(0)
            except Exception:
                pass

        doc = Document(documento_anterior)
        body = doc.element.body

        # Regex universal para IDs de NC (CRA, CRC, SOCICAM e variações de terminais/rodovias)
        nc_pattern = r'\b(?!(?:PE|BR|CT|CTR|PROC)[\s_\.-]*\d+)((?:NC|CRC|GAR|CAR|TIP|PET|PETRO|[A-Z]{3,5})[\s_\.-]*\d+[\w\.\-/]*\b)'

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
                
                m = re.search(nc_pattern, txt0, re.IGNORECASE)
                id_nc = m.group(1).upper() if m else None
                if id_nc:
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
        photo_counter_global = 0

        # Loop pelos elementos do corpo
        for child in body:
            tag = child.tag.split('}')[-1]
            if tag == 'p':
                p_text = Paragraph(child, doc).text.strip()
                if not p_text:
                    continue
                
                norm_p = strip_accents(p_text)
                
                # Detecta início do Apêndice com insensibilidade a acentos
                if any(kw in norm_p for kw in ["APENDICE", "MEMORIAL", "FOTOGRAFICO", "REGISTRO FOTOGRAFICO", "EVIDENCIAS FOTOGRAFICAS", "FOTOGRAFIAS", "ANEXO FOTOGRAFICO"]):
                    in_appendix = True
                
                if in_appendix:
                    # Detecta pista ou trecho
                    if "PISTA" in norm_p or "SENTIDO" in norm_p:
                        pista_m = re.search(r'PISTA\s*(?:SENTIDO)?\s*([A-Za-z\s]+)', p_text, re.IGNORECASE)
                        if pista_m:
                            current_pista = pista_m.group(1).strip().upper()
                        trecho_m = re.search(r'(RODOVIA(?:\s+ESTADUAL)?\s*[A-Za-z0-9\s-]+)', p_text, re.IGNORECASE)
                        if trecho_m:
                            current_trecho = trecho_m.group(1).strip()
                    
                    # Detecta ID de NC
                    m_nc = re.search(nc_pattern, p_text, re.IGNORECASE)
                    if m_nc:
                        current_nc_id = m_nc.group(1).upper()
                        parts = p_text.split('–', 2) if '–' in p_text else p_text.split('-', 2)
                        if len(parts) >= 2:
                            current_nc_desc = parts[-1].strip()
                        else:
                            current_nc_desc = p_text
                    elif not current_nc_id and len(p_text) < 100 and not norm_p.startswith("FOTO"):
                        current_nc_id = p_text.split('–')[0].split('-')[0].strip()

            elif tag == 'tbl':
                t = Table(child, doc)
                
                # Detecta início do Apêndice caso esteja na tabela banner
                if not in_appendix:
                    for r in t.rows:
                        for cell in r.cells:
                            c_txt = strip_accents(cell.text)
                            if any(kw in c_txt for kw in ["APENDICE", "MEMORIAL", "FOTOGRAFICO"]):
                                in_appendix = True
                                break
                        if in_appendix:
                            break
                
                if in_appendix:
                    photo_counter_global += 1
                    active_id = current_nc_id if current_nc_id else f"NC_{photo_counter_global:02d}"
                    
                    status = status_ncs.get(active_id, "Pendente")
                    if status.strip().lower() == "sanada":
                        continue

                    # Seleção inteligente de célula da imagem e legenda
                    cell_img = None
                    cell_leg = None
                    
                    if len(t.rows) >= 2 and len(t.columns) == 2:
                        embeds_right = t.cell(0, 1)._element.xpath('.//@r:embed')
                        if embeds_right:
                            cell_img = t.cell(0, 1)
                            cell_leg = t.cell(1, 1) if len(t.rows) > 1 else t.cell(0, 1)
                        else:
                            cell_img = t.cell(0, 0)
                            cell_leg = t.cell(1, 0) if len(t.rows) > 1 else t.cell(0, 0)
                    elif len(t.rows) >= 1 and len(t.columns) >= 1:
                        cell_img = t.cell(0, 0)
                        cell_leg = t.cell(1, 0) if len(t.rows) > 1 else t.cell(0, 0)

                    if cell_img:
                        embeds = cell_img._element.xpath('.//@r:embed')
                        if embeds:
                            for rId in embeds:
                                if rId in doc.part.related_parts:
                                    img_part = doc.part.related_parts[rId]
                                    img_bytes = img_part.image.blob
                                    
                                    ext = ".jpg"
                                    if "png" in img_part.content_type:
                                        ext = ".png"
                                    
                                    idx = photo_count_per_nc.get(active_id, 0) + 1
                                    photo_count_per_nc[active_id] = idx
                                    
                                    photo_name = f"{active_id}_{idx}{ext}"
                                    photo_path = os.path.join(extracted_dir, photo_name)
                                    
                                    with open(photo_path, "wb") as f:
                                        f.write(img_bytes)
                                    
                                    legend_text = cell_leg.text.strip() if cell_leg else ""
                                    
                                    result.append({
                                        "id_nc": active_id,
                                        "constatacao": nc_details.get(active_id, {}).get("constatacao", current_nc_desc),
                                        "pista": current_pista,
                                        "trecho": current_trecho,
                                        "old_photo_path": photo_path,
                                        "old_legend": legend_text
                                    })
                                    break
                                    
    except Exception as e:
        print(f"Erro ao extrair NCs e fotos do documento anterior: {e}")
        
    return result
