# -*- coding: utf-8 -*-
"""Módulo agregador dos diálogos e modais da interface do usuário."""

from ui.dialogs.photo_dialogs import (
    mostrar_foto_modal,
    galeria_fotos_modal,
    alerta_foto_duplicada_modal,
    confirmar_exclusao_lote_modal,
    relacionar_foto_modal,
)
from ui.dialogs.records_dialogs import (
    confirmar_exclusao_nc_modal,
    confirmar_limpar_registros_modal,
    formatar_sigla_nc,
    obter_lista_siglas_atuais,
    editar_registros_relatorio_modal,
    alerta_codificacao_obrigatoria_modal,
)
from ui.dialogs.management_dialogs import (
    gerenciar_responsaveis_modal,
    gerenciar_coordenadores_modal,
    gerenciar_contratos_modal,
    adicionar_nc_personalizada_modal,
)

__all__ = [
    "mostrar_foto_modal",
    "galeria_fotos_modal",
    "alerta_foto_duplicada_modal",
    "confirmar_exclusao_lote_modal",
    "relacionar_foto_modal",
    "confirmar_exclusao_nc_modal",
    "confirmar_limpar_registros_modal",
    "formatar_sigla_nc",
    "obter_lista_siglas_atuais",
    "editar_registros_relatorio_modal",
    "alerta_codificacao_obrigatoria_modal",
    "gerenciar_responsaveis_modal",
    "gerenciar_coordenadores_modal",
    "gerenciar_contratos_modal",
    "adicionar_nc_personalizada_modal",
]
