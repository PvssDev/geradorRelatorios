# -*- coding: utf-8 -*-
"""Fachada limpa para os modais e diálogos da interface do Streamlit.

Este módulo reexporta os diálogos definidos de forma modular em `ui.dialogs`,
mantendo total retrocompatibilidade com qualquer código legado.
"""

from ui.dialogs import (
    mostrar_foto_modal,
    galeria_fotos_modal,
    alerta_foto_duplicada_modal,
    confirmar_exclusao_lote_modal,
    confirmar_exclusao_nc_modal,
    confirmar_limpar_registros_modal,
    confirmar_reset_estado_modal,
    gerenciar_responsaveis_modal,
    gerenciar_coordenadores_modal,
    gerenciar_contratos_modal,
    adicionar_nc_personalizada_modal,
    formatar_sigla_nc,
    obter_lista_siglas_atuais,
    editar_registros_relatorio_modal,
    alerta_codificacao_obrigatoria_modal,
    relacionar_foto_modal,
)

__all__ = [
    "mostrar_foto_modal",
    "galeria_fotos_modal",
    "alerta_foto_duplicada_modal",
    "confirmar_exclusao_lote_modal",
    "confirmar_exclusao_nc_modal",
    "confirmar_limpar_registros_modal",
    "confirmar_reset_estado_modal",
    "gerenciar_responsaveis_modal",
    "gerenciar_coordenadores_modal",
    "gerenciar_contratos_modal",
    "adicionar_nc_personalizada_modal",
    "formatar_sigla_nc",
    "obter_lista_siglas_atuais",
    "editar_registros_relatorio_modal",
    "alerta_codificacao_obrigatoria_modal",
    "relacionar_foto_modal",
]
