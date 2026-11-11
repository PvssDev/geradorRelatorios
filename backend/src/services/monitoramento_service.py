# -*- coding: utf-8 -*-
import base64
import io
import os
import tempfile
from typing import Any, BinaryIO, Dict, List
from monitoramento_utils import extrair_metadados_anterior, extrair_ncs_e_fotos_anterior


def _calcular_display_labels(items: List[Dict[str, Any]]) -> None:
    """
    Adiciona o rótulo 'display_label' desambiguado ("{id_nc} - {trecho}" ou "{id_nc} - {trecho} (N)")
    em cada item extraído do monitoramento anterior.
    """
    label_counts: Dict[str, int] = {}
    for item in items:
        id_nc = str(item.get("id_nc", "")).strip()
        t = str(item.get("trecho", "")).strip()
        if len(t) > 35:
            t = t[:32] + "..."
        base_label = f"{id_nc} - {t}"
        label_counts[base_label] = label_counts.get(base_label, 0) + 1

    label_current_indices: Dict[str, int] = {}
    for item in items:
        id_nc = str(item.get("id_nc", "")).strip()
        t = str(item.get("trecho", "")).strip()
        if len(t) > 35:
            t = t[:32] + "..."
        base_label = f"{id_nc} - {t}"
        total = label_counts[base_label]
        if total > 1:
            idx_l = label_current_indices.get(base_label, 0) + 1
            label_current_indices[base_label] = idx_l
            item["display_label"] = f"{base_label} ({idx_l})"
        else:
            item["display_label"] = base_label


def processar_documento_monitoramento_anterior(file_bytes: bytes, filename: str = "anterior.docx") -> Dict[str, Any]:
    """
    Processa um arquivo .docx de monitoramento/fiscalização anterior de forma 100% stateless e
    aderente à LGPD (em diretório temporário autodestrutivo), retornando:
    - metadados extraídos (N_prev, N_curr, ctr_num, processo_sei_prev, etc.)
    - itens_pendentes com foto antiga convertida em Base64 data URL e nome determinístico.
    """
    stream = io.BytesIO(file_bytes)
    stream.name = filename

    metadados = extrair_metadados_anterior(stream)
    itens_serializados: List[Dict[str, Any]] = []

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
        raw_items = extrair_ncs_e_fotos_anterior(stream, output_dir=temp_dir)
        _calcular_display_labels(raw_items)

        for item in raw_items:
            photo_path = item.get("old_photo_path", "")
            photo_name = os.path.basename(photo_path) if photo_path else ""
            photo_b64_url = ""

            if photo_path and os.path.exists(photo_path):
                ext = os.path.splitext(photo_name)[1].lower()
                mime = "image/png" if ext == ".png" else "image/jpeg"
                with open(photo_path, "rb") as f:
                    b64_str = base64.b64encode(f.read()).decode("utf-8")
                    photo_b64_url = f"data:{mime};base64,{b64_str}"

            itens_serializados.append({
                "id_nc": item.get("id_nc", ""),
                "constatacao": item.get("constatacao", ""),
                "pista": item.get("pista", ""),
                "trecho": item.get("trecho", ""),
                "old_legend": item.get("old_legend", ""),
                "old_photo_path": photo_name,
                "old_photo_b64": photo_b64_url,
                "display_label": item.get("display_label", item.get("id_nc", "Sem Identificação"))
            })

    return {
        "metadados": metadados,
        "itens_pendentes": itens_serializados
    }

