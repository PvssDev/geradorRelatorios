# -*- coding: utf-8 -*-
"""
Wrapper Python para o Componente de File System Access API.

Permite salvar e ler estados e mídias diretamente em uma pasta local física
na máquina do usuário (ex: geradorRelatorios/), sem salvar no servidor da nuvem.
"""

import os
import streamlit as st
import streamlit.components.v1 as components
from typing import Optional, Dict, Any, List

_COMPONENT_DIR = os.path.dirname(os.path.abspath(__file__))
_fs_access_component = components.declare_component("local_file_system_sync", path=_COMPONENT_DIR)


def render_local_file_system_sync(
    queue: Optional[List[Dict[str, Any]]] = None,
    tipo: str = "CRA",
    cat: str = "Fiscalização",
    session_id: str = "",
    key: str = "local_fs_sync"
) -> Optional[Dict[str, Any]]:
    """
    Renderiza o componente de sincronização com o sistema de arquivos local da máquina do usuário.

    `queue` é a lista de ações ainda não confirmadas (cada uma com "version" crescente):
    - "SAVE": grava 'state_data' em estado/estado.json.
    - "SYNC_MEDIA": sincroniza midia/fotos/ e midia/arquivos/ (grava novos e remove órfãos).
    - "LOAD": lê estado e mídias da pasta local.
    - "CLEAR": exclui a pasta do relatório ativo.

    O componente devolve {"action": "ACK" | "LOADED_FROM_DISK" | "CLEARED_ON_DISK", "ackVersion": n, ...}.
    As ações com version <= ackVersion podem ser descartadas da fila.
    """
    return _fs_access_component(
        queue=queue or [],
        tipo=tipo,
        cat=cat,
        sessionId=session_id,
        default=None,
        key=key
    )


import io
import base64

class RestoredLocalFile:
    """
    Objeto que emula um UploadedFile para mídias recuperadas da pasta local do usuário.
    Possui atributos .name, .size, .type, .read(), .seek() e .b64_data.
    """
    def __init__(self, name: str, size: int, mime_type: str, b64_data: str):
        self.name = name
        self.size = size
        self.type = mime_type
        self.b64_data = b64_data
        
        # Converte Data URL Base64 para buffer de bytes na memória
        try:
            raw_b64 = b64_data.split(",")[-1]
            raw_bytes = base64.b64decode(raw_b64)
            self._buffer = io.BytesIO(raw_bytes)
        except Exception:
            self._buffer = io.BytesIO()

    def read(self, *args, **kwargs):
        return self._buffer.read(*args, **kwargs)

    def seek(self, *args, **kwargs):
        return self._buffer.seek(*args, **kwargs)

    def tell(self):
        return self._buffer.tell()

    def getbuffer(self):
        return self._buffer.getbuffer()

    def getvalue(self):
        return self._buffer.getvalue()

    def __len__(self):
        return self.size or len(self._buffer.getvalue())

    def __getattr__(self, name):
        return getattr(self._buffer, name)

    def __repr__(self):
        return f"<RestoredLocalFile name={self.name} size={self.size}>"
