"""
Regras de negócio puras, validações de contratos e algoritmos de domínio.
"""
from core.rules.cra_rules import (
    MAP_SIGLAS_CRA,
    gerar_codigo_cra,
    obter_proximo_sequencial_cra,
    formatar_codificacoes_contraidas_cra,
    converter_faixa_para_sigla_cra,
    combinar_faixas_relacionadas_cra,
    formatar_legenda_foto_cra,
    consolidar_dados_legenda_grupo_cra,
    sincronizar_legendas_grupo_cra,
    classificar_achados_cra,
    separar_achados_df_cra,
    validar_vistoria_cra,
)
from core.rules.crc_rules import (
    gerar_codigo_crc,
    formatar_extenso_feminino_achados,
    classificar_achados_crc,
    separar_achados_df_crc,
    validar_vistoria_crc,
)
from core.rules.socicam_rules import (
    normalizar_nome_terminal_rodoviario,
    normalizar_nome_terminal_curto,
    extrair_sigla_terminal,
    formatar_extenso_achados_socicam,
    formatar_frase_conclusao_achados_socicam,
    classificar_achados_socicam,
    separar_achados_df_socicam,
    validar_vistoria_socicam,
)

__all__ = [
    "MAP_SIGLAS_CRA",
    "gerar_codigo_cra",
    "obter_proximo_sequencial_cra",
    "formatar_codificacoes_contraidas_cra",
    "converter_faixa_para_sigla_cra",
    "combinar_faixas_relacionadas_cra",
    "formatar_legenda_foto_cra",
    "consolidar_dados_legenda_grupo_cra",
    "sincronizar_legendas_grupo_cra",
    "classificar_achados_cra",
    "separar_achados_df_cra",
    "validar_vistoria_cra",
    "gerar_codigo_crc",
    "formatar_extenso_feminino_achados",
    "classificar_achados_crc",
    "separar_achados_df_crc",
    "validar_vistoria_crc",
    "normalizar_nome_terminal_rodoviario",
    "normalizar_nome_terminal_curto",
    "extrair_sigla_terminal",
    "formatar_extenso_achados_socicam",
    "formatar_frase_conclusao_achados_socicam",
    "classificar_achados_socicam",
    "separar_achados_df_socicam",
    "validar_vistoria_socicam",
]



