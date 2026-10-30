# -*- coding: utf-8 -*-
"""
Serviço Unificado de Auditoria e Extração de Relatório Anterior (Fiscalização ou Monitoramento).
Conforme estritamente com a LGPD (Lei nº 13.709/2018):
- Processa documentos diretamente em memória (io.BytesIO).
- Extrai evidências fotográficas em streams voláteis sem persistir imagens em diretórios órfãos do disco.
- Sanitiza logs evitando expor caminhos e dados pessoais nos terminais.
"""
import io
import os
import re
import shutil
import tempfile
import unicodedata
from typing import Any, Dict, List, Optional, Tuple, Union

from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph

from core.models.entities import MetadadosMonitoramento, Quadro1ItemAnterior, FotoEvidencia


def _strip_accents(s: Any) -> str:
    """Remove acentuação gráfica e converte para caixa alta para comparações seguras."""
    if not s:
        return ""
    return "".join(c for c in unicodedata.normalize("NFD", str(s)) if unicodedata.category(c) != "Mn").upper()


def carregar_documento_word(documento_anterior: Any) -> Optional[Document]:
    """
    Carrega um arquivo .docx de forma resiliente e polimórfica:
    aceita caminho de arquivo (str/Path), buffer de upload (BytesIO/UploadedFile),
    ou uma instância já inicializada de docx.Document.
    """
    if documento_anterior is None:
        return None

    # Verifica se já é uma instância de documento do python-docx
    if hasattr(documento_anterior, "paragraphs") and hasattr(documento_anterior, "tables"):
        return documento_anterior


    try:
        if hasattr(documento_anterior, "seek") and hasattr(documento_anterior, "read"):
            try:
                documento_anterior.seek(0)
            except Exception:
                pass
            conteudo = documento_anterior.read()
            try:
                documento_anterior.seek(0)
            except Exception:
                pass
            return Document(io.BytesIO(conteudo))

        if isinstance(documento_anterior, bytes):
            return Document(io.BytesIO(documento_anterior))

        if isinstance(documento_anterior, (str, os.PathLike)):
            caminho_str = str(documento_anterior)
            if os.path.exists(caminho_str):
                return Document(caminho_str)

    except Exception:
        return None

    return None


def encontrar_quadro1_table(doc: Optional[Document]) -> Optional[Table]:
    """Localiza a tabela do Quadro 1 em um documento Word (.docx)."""
    if not doc or len(doc.tables) == 0:
        return None

    chaves_cabecalho = [
        "IDENTIFICAÇÃO", "IDENTIFICACAO", "ID.NC", "ID NC", "REGISTRO FOTOGRÁFICO",
        "REGISTRO FOTOGRAFICO", "NÃO CONFORMIDADE", "NAO CONFORMIDADE",
        "REFERÊNCIA", "REFERENCIA"
    ]

    for t in doc.tables:
        header_text = " ".join([c.text.upper() for r in t.rows[:min(2, len(t.rows))] for c in r.cells])
        if any(k in header_text for k in chaves_cabecalho):
            return t

    return doc.tables[0]


def extrair_metadados_anterior(documento_anterior: Any) -> MetadadosMonitoramento:
    """
    Extrai com segurança e resiliência os metadados do relatório anterior:
    - N_prev: ciclo do relatório anterior (0 se fiscalização).
    - N_curr: próximo ciclo de monitoramento (N_prev + 1).
    - ctr_num: número da CTR (ex: '07/2025').
    - processo_sei_prev: número do processo SEI.
    - data_vistoria_prev, oficio_num_prev, oficio_data_prev, carta_num_prev, carta_data_prev, carta_sei_prev.
    """
    meta_dict = {
        "N_prev": 0,
        "N_curr": 1,
        "ctr_num": "XX/XXXX",
        "processo_sei_prev": "xxxxxxxx-xxx",
        "data_vistoria_prev": "XX/XX/XXXX",
        "oficio_num_prev": "xxx/xxxx",
        "oficio_data_prev": "xx/xx/xxxx",
        "carta_num_prev": "xxxx/xxxx",
        "carta_data_prev": "xx/xx/xxxx",
        "carta_sei_prev": "xxxxxxxx-xxx",
        "N_ncs_pendentes_prev": 0,
        "is_fiscalizacao": False
    }

    if not documento_anterior:
        return MetadadosMonitoramento.de_dicionario(meta_dict)

    try:
        filename = getattr(documento_anterior, "name", str(documento_anterior)).lower()
        if "fiscaliza" in filename:
            meta_dict["is_fiscalizacao"] = True
            meta_dict["N_prev"] = 0

        doc = carregar_documento_word(documento_anterior)
        if doc is None:
            return MetadadosMonitoramento.de_dicionario(meta_dict)

        if not meta_dict["is_fiscalizacao"]:
            pattern_mon = re.compile(r'(\d+)(?:\u00ba|\u00b0)?\s*monitoramento', re.IGNORECASE)
            for p in doc.paragraphs:
                m = pattern_mon.search(p.text)
                if m:
                    meta_dict["N_prev"] = int(m.group(1))
                    break

        pattern_ctr = re.compile(r'CTR\s*(?:N\u00ba|n\u00ba|N\u00ba)?\s*(\d+/\d+)', re.IGNORECASE)
        for p in doc.paragraphs:
            m = pattern_ctr.search(p.text)
            if m:
                meta_dict["ctr_num"] = m.group(1)
                break

        pattern_sei = re.compile(r'PROCESSO SEI\s*(?:N\u00ba|n\u00ba|N\u00ba)?\s*([\d\./-]+)', re.IGNORECASE)
        for p in doc.paragraphs:
            m = pattern_sei.search(p.text)
            if m:
                meta_dict["processo_sei_prev"] = m.group(1)
                break

        pattern_vist = re.compile(r'(?:realizada|vistorias).*em\s*(\d{2}/\d{2}/\d{4})', re.IGNORECASE)
        for p in doc.paragraphs:
            m = pattern_vist.search(p.text)
            if m:
                meta_dict["data_vistoria_prev"] = m.group(1)
                break

        pattern_oficio = re.compile(r'Of(?:í|i)cio\s+Arpe\s+DTO\s+(?:n|N)(?:º|o)?\s*([\w/.-]+),\s*de\s*(\d{2}/\d{2}/\d{4})', re.IGNORECASE)
        for p in doc.paragraphs:
            m = pattern_oficio.search(p.text)
            if m:
                meta_dict["oficio_num_prev"] = m.group(1)
                meta_dict["oficio_data_prev"] = m.group(2)
                break

        pattern_carta = re.compile(r'Carta\s+(?:CRC/REG|SAP/PER/ARPE|CRA/REG)\s+(?:n|N)(?:º|o)?\s*([\w/.-]+),\s*de\s*(\d{2}/\d{2}/\d{4})\s*\(\s*Doc\.\s*SEI\s*(?:n|N)(?:º|o)?\s*([\w/.-]+)\)', re.IGNORECASE)
        for p in doc.paragraphs:
            m = pattern_carta.search(p.text)
            if m:
                meta_dict["carta_num_prev"] = m.group(1)
                meta_dict["carta_data_prev"] = m.group(2)
                meta_dict["carta_sei_prev"] = m.group(3)
                break

        # Inspecionar Quadro 1 para data_vistoria_prev e contagem de pendências
        quadro1 = encontrar_quadro1_table(doc)
        if quadro1:
            if meta_dict["data_vistoria_prev"] == "XX/XX/XXXX":
                try:
                    for row_item in quadro1.rows[:min(2, len(quadro1.rows))]:
                        for cell in row_item.cells:
                            m_date = re.search(r'(\d{2}/\d{2}/\d{4})', cell.text)
                            if m_date:
                                meta_dict["data_vistoria_prev"] = m_date.group(1)
                                break
                        if meta_dict["data_vistoria_prev"] != "XX/XX/XXXX":
                            break
                except Exception:
                    pass

            try:
                p_count = 0
                for row_item in quadro1.rows[1:]:
                    cells = row_item.cells
                    if len(cells) < 2:
                        continue
                    txt0 = cells[0].text.strip()
                    txt_last = cells[-1].text.strip().lower()
                    if not txt0 or any(h in txt0.upper() for h in ["IDENTIFICAÇÃO", "ID.NC", "NÃO CONFORMIDADE", "TOTAL"]):
                        continue
                    if len(cells) >= 3 and cells[0].text.strip() == cells[1].text.strip() == cells[2].text.strip():
                        continue
                    if "pendente" in txt_last or meta_dict["is_fiscalizacao"] or "não sanad" in txt_last:
                        p_count += 1
                    elif len(cells) >= 3 and not any(ok in txt_last for ok in ["sanad", "atendid", "resolvid", "cumprid"]):
                        p_count += 1
                meta_dict["N_ncs_pendentes_prev"] = p_count
            except Exception:
                pass

    except Exception:
        pass

    if isinstance(meta_dict["N_prev"], int):
        meta_dict["N_curr"] = meta_dict["N_prev"] + 1

    return MetadadosMonitoramento.de_dicionario(meta_dict)


def extrair_linhas_quadro1_anterior(documento_anterior: Any) -> List[Quadro1ItemAnterior]:
    """
    Extrai as Não Conformidades e constatações da tabela do Quadro 1 do documento anterior.
    Retorna uma lista tipada de Quadro1ItemAnterior.
    """
    ncs: List[Quadro1ItemAnterior] = []
    if not documento_anterior:
        return ncs

    doc = carregar_documento_word(documento_anterior)
    if doc is None:
        return ncs

    try:
        quadro1 = encontrar_quadro1_table(doc)
        if not quadro1:
            return ncs

        col_id = 0
        col_desc = 1
        if len(quadro1.columns) >= 2:
            for r_idx in range(min(2, len(quadro1.rows))):
                for c_idx, cell in enumerate(quadro1.rows[r_idx].cells):
                    txt = cell.text.strip().upper()
                    if any(k in txt for k in ["REFERÊNCIA", "REFERENCIA", "IDENTIFICAÇÃO", "IDENTIFICACAO", "ID.NC", "ID NC", "ID_NC", "ITEM"]):
                        col_id = c_idx
                    elif any(k in txt for k in ["CONSTATAÇÃO", "CONSTATACAO", "DESCRIÇÃO", "DESCRICAO", "INFORMAÇÃO", "INFORMACAO", "NÃO CONFORMIDADE", "NAO CONFORMIDADE"]):
                        if c_idx != col_id:
                            col_desc = c_idx

        for row_item in quadro1.rows[1:]:
            cells = row_item.cells
            if len(cells) <= max(col_id, col_desc):
                continue
            txt0 = cells[col_id].text.strip()
            txt1 = cells[col_desc].text.strip()
            if not txt0 or any(h in txt0.upper() for h in ["REFERÊNCIA", "REFERENCIA", "IDENTIFICAÇÃO", "IDENTIFICACAO", "ID.NC", "TOTAL", "QUADRO"]):
                continue

            if txt0 != txt1:
                ncs.append(Quadro1ItemAnterior(id_nc=txt0, info_ou_constatacao=txt1))
            elif len(cells) > 1 and txt0:
                ncs.append(Quadro1ItemAnterior(id_nc=txt0, info_ou_constatacao=cells[1].text.strip()))

    except Exception:
        pass

    return ncs


def extrair_ncs_e_fotos_anterior(documento_anterior: Any) -> List[Dict[str, Any]]:
    """
    Lê o documento anterior (.docx) e extrai as NCs e suas respectivas fotos do apêndice.
    
    CONFORMIDADE LGPD:
    As imagens são extraídas diretamente dos blobs em memória (io.BytesIO) sem gravar
    arquivos na pasta temporária do sistema operacional, eliminando vazamento de dados.
    """
    result: List[Dict[str, Any]] = []
    if not documento_anterior:
        return result

    doc = carregar_documento_word(documento_anterior)
    if doc is None:
        return result

    try:
        body = doc.element.body
        nc_pattern = r'\b((?:CRC|CRA|SOCICAM|CAR|GAR|TIP|NC|PET|PETRO)(?:[\s_\.-]*[A-Z0-9\+\-/]+)+)\b'

        quadro1 = encontrar_quadro1_table(doc)
        status_ncs: Dict[str, str] = {}
        nc_details: Dict[str, Dict[str, str]] = {}
        foto_to_id_map: Dict[str, str] = {}

        if quadro1:
            col_id = 0
            col_desc = 1
            col_foto = 2
            col_det = -1

            for r_idx in range(min(2, len(quadro1.rows))):
                for c_idx, cell in enumerate(quadro1.rows[r_idx].cells):
                    txt = cell.text.strip().upper()
                    if "IDENTIFICAÇÃO" in txt or "ID.NC" in txt:
                        col_id = c_idx
                    elif "DESCRIÇÃO" in txt or "CONSTATAÇÃO" in txt:
                        col_desc = c_idx
                    elif "REGISTRO FOTOGRÁFICO" in txt:
                        col_foto = c_idx
                    elif "DETERMINAÇÃO" in txt or "SITUAÇÃO" in txt:
                        col_det = c_idx

            for row in quadro1.rows:
                cells = [c.text.strip() for c in row.cells]
                if not cells or len(cells) <= max(col_id, col_desc):
                    continue

                txt_id = cells[col_id]
                if not txt_id or any(h in txt_id.upper() for h in ["IDENTIFICAÇÃO", "ID.NC", "NÃO CONFORMIDADE", "TOTAL"]):
                    continue

                txt_desc = cells[col_desc]
                txt_foto = cells[col_foto] if col_foto < len(cells) else ""
                txt_det = cells[col_det] if col_det != -1 and col_det < len(cells) else "Pendente"

                status_ncs[txt_id] = txt_det
                nc_details[txt_id] = {
                    "constatacao": txt_desc,
                    "foto_ref": txt_foto
                }

                if txt_foto:
                    foto_to_id_map[txt_foto.upper().strip()] = txt_id
                    m = re.search(r'FOTO\s*0*(\d+)', txt_foto.upper())
                    if m:
                        num = int(m.group(1))
                        foto_to_id_map[f"FOTO {num}"] = txt_id
                        foto_to_id_map[f"FOTO {num:02d}"] = txt_id

        current_trecho = "PE-024"
        current_pista = "SUL"
        current_nc_id: Optional[str] = None
        current_nc_desc = ""

        in_appendix = False
        photo_count_per_nc: Dict[str, int] = {}
        photo_counter_global = 0

        for child in body:
            tag = child.tag.split("}")[-1]
            if tag == "p":
                p_text = Paragraph(child, doc).text.strip()
                if not p_text:
                    continue

                norm_p = _strip_accents(p_text)
                if any(kw in norm_p for kw in ["APENDICE", "MEMORIAL", "FOTOGRAFICO", "REGISTRO FOTOGRAFICO", "EVIDENCIAS FOTOGRAFICAS"]):
                    in_appendix = True

                if in_appendix:
                    if "PISTA" in norm_p or "SENTIDO" in norm_p:
                        pista_m = re.search(r'PISTA\s*(?:SENTIDO)?\s*([A-Za-z\s]+)', p_text, re.IGNORECASE)
                        if pista_m:
                            current_pista = pista_m.group(1).strip().upper()
                        trecho_m = re.search(r'(RODOVIA(?:\s+ESTADUAL)?\s*[A-Za-z0-9\s-]+)', p_text, re.IGNORECASE)
                        if trecho_m:
                            current_trecho = trecho_m.group(1).strip()

                    m_foto = re.search(r'(FOTO\s*\d+)', p_text, re.IGNORECASE)
                    if m_foto and m_foto.group(1).upper() in foto_to_id_map:
                        current_nc_id = foto_to_id_map[m_foto.group(1).upper()]
                    else:
                        m_nc = re.search(nc_pattern, p_text, re.IGNORECASE)
                        if m_nc and not m_nc.group(1).upper().startswith("FOTO"):
                            current_nc_id = m_nc.group(1).upper()
                            parts = p_text.split("–", 2) if "–" in p_text else p_text.split("-", 2)
                            current_nc_desc = parts[-1].strip() if len(parts) >= 2 else p_text

            elif tag == "tbl":
                t = Table(child, doc)
                if not in_appendix:
                    for r in t.rows:
                        for cell in r.cells:
                            c_txt = _strip_accents(cell.text)
                            if any(kw in c_txt for kw in ["APENDICE", "MEMORIAL", "FOTOGRAFICO"]):
                                in_appendix = True
                                break
                        if in_appendix:
                            break

                if in_appendix:
                    cell_text_all = " ".join([c.text for r in t.rows for c in r.cells])
                    m_foto_tbl = re.search(r'(FOTO\s*\d+)', cell_text_all, re.IGNORECASE)
                    if m_foto_tbl and m_foto_tbl.group(1).upper() in foto_to_id_map:
                        active_id = foto_to_id_map[m_foto_tbl.group(1).upper()]
                    elif current_nc_id:
                        active_id = current_nc_id
                    else:
                        photo_counter_global += 1
                        active_id = f"NC_{photo_counter_global:02d}"

                    status = status_ncs.get(active_id, "Pendente")
                    if str(status).strip().lower() == "sanada":
                        continue

                    cell_img = None
                    cell_leg = None
                    if len(t.rows) >= 2 and len(t.columns) == 2:
                        embeds_right = t.cell(0, 1)._element.xpath(".//@r:embed")
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
                        embeds = cell_img._element.xpath(".//@r:embed")
                        if embeds:
                            for rId in embeds:
                                if rId in doc.part.related_parts:
                                    img_part = doc.part.related_parts[rId]
                                    img_bytes = img_part.image.blob

                                    ext = ".png" if "png" in img_part.content_type else ".jpg"
                                    idx = photo_count_per_nc.get(active_id, 0) + 1
                                    photo_count_per_nc[active_id] = idx

                                    safe_id = re.sub(r'[/\\:*?"<>|]', "_", active_id)
                                    photo_name = f"{safe_id}_{idx}{ext}"
                                    legend_text = cell_leg.text.strip() if cell_leg else ""

                                    # Armazena diretamente o buffer em memória (Sem poluir o disco)
                                    buffer_memoria = io.BytesIO(img_bytes)

                                    result.append({
                                        "id_nc": active_id,
                                        "constatacao": nc_details.get(active_id, {}).get("constatacao", current_nc_desc),
                                        "pista": current_pista,
                                        "trecho": current_trecho,
                                        "nome_arquivo": photo_name,
                                        "old_photo_bytes": img_bytes,
                                        "photo_bytes_io": buffer_memoria,
                                        "old_photo_path": photo_name,  # Nome virtual para compatibilidade
                                        "old_legend": legend_text,
                                        "foto_evidencia": FotoEvidencia(
                                            nome_arquivo=photo_name,
                                            path_ou_bytes=buffer_memoria,
                                            legenda=legend_text,
                                            metadata={"id_nc": active_id, "pista": current_pista}
                                        )
                                    })
                                    break

    except Exception:
        pass

    return result


def limpar_diretorio_temporario_legado() -> None:
    """
    Remove de forma segura a pasta temporária legada 'arpe_extracted_photos'
    caso tenha sido criada por versões antigas no disco do usuário.
    """
    try:
        legacy_dir = os.path.join(tempfile.gettempdir(), "arpe_extracted_photos")
        if os.path.exists(legacy_dir):
            shutil.rmtree(legacy_dir, ignore_errors=True)
    except Exception:
        pass
