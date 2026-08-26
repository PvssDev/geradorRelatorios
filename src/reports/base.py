from abc import ABC, abstractmethod

class BaseReport(ABC):
    @property
    @abstractmethod
    def key(self) -> str:
        """Chave única do relatório (ex: 'CRA', 'CRC', 'SOCICAM')."""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Nome de exibição do relatório."""
        pass

    @property
    @abstractmethod
    def default_contrato(self) -> str:
        """Número do contrato padrão do relatório."""
        pass
    
    # Capa / Header
    @property
    @abstractmethod
    def capa_orgao_concedente(self) -> str:
        pass

    @property
    @abstractmethod
    def capa_secretaria(self) -> str:
        pass

    @property
    @abstractmethod
    def capa_titulo(self) -> str:
        pass

    @property
    @abstractmethod
    def capa_ctr_number_template(self) -> str:
        """Template do número do CTR na capa (ex: 'PROCESSO ADMINISTRATIVO CTR Nº {mes_ano}')."""
        pass

    @property
    @abstractmethod
    def capa_prestador_label(self) -> str:
        pass

    @property
    @abstractmethod
    def capa_contrato_label(self) -> str:
        pass

    @property
    @abstractmethod
    def capa_regulador_label(self) -> str:
        pass

    @abstractmethod
    def get_capa_titulos(self, row, ano) -> list:
        """Retorna os títulos da capa."""
        pass

    @property
    @abstractmethod
    def sumario_before_abreviaturas(self) -> bool:
        """Define se o sumário vem antes da lista de abreviaturas na paginação."""
        pass

    @property
    def signatures_before_apendices(self) -> bool:
        """Define se as assinaturas devem ser inseridas antes dos apêndices."""
        return False

    # Abreviaturas
    @abstractmethod
    def get_abbreviations(self) -> list:
        """Retorna uma lista de tuplas (sigla, definicao) para a seção de abreviaturas."""
        pass

    # Sumário
    @abstractmethod
    def get_sumario_linhas(self, row) -> list:
        """Retorna a lista de linhas formatadas com tabulações para o sumário."""
        pass

    # Introdução (Seção 1)
    @abstractmethod
    def get_intro_paragraphs(self, row, ano, data_extenso) -> list:
        """
        Retorna os parágrafos de introdução.
        Cada parágrafo é uma lista de tuplas (texto, bold, italic, color_rgb).
        color_rgb é uma tupla (R, G, B) ou None.
        """
        pass

    # Objetivo (Seção 2)
    @abstractmethod
    def get_objective_paragraphs(self, row) -> list:
        """
        Retorna os parágrafos de objetivo.
        Cada parágrafo é uma lista de tuplas (texto, bold, italic, color_rgb).
        """
        pass

    # Informações Gerais (Seção 3 / Tabela 1)
    @abstractmethod
    def get_general_info_rows(self, row, responsaveis_formatted, periodo_val) -> list:
        """Retorna as linhas (nome_campo, valor, is_header, val_bold) para a tabela de Informações Gerais."""
        pass

    @property
    @abstractmethod
    def general_info_col_widths(self) -> list:
        """Retorna as larguras das duas colunas da tabela de Informações Gerais."""
        pass

    @property
    @abstractmethod
    def general_info_headers_indices(self) -> list:
        """Retorna os índices das linhas de cabeçalho na tabela de Informações Gerais."""
        pass

    # Metodologia (Seção 3 ou 4)
    @abstractmethod
    def get_methodology_paragraphs(self, data_extenso) -> list:
        """
        Retorna os parágrafos de metodologia.
        Cada parágrafo é uma lista de tuplas (texto, bold, italic, color_rgb).
        """
        pass

    @abstractmethod
    def get_references_bullets(self) -> list:
        """Retorna as referências de Metodologia como tuplas (texto, recuado, is_bullet)."""
        pass

    @property
    @abstractmethod
    def references_left_indent_pt(self) -> float:
        """Retorna o recuo esquerdo em pontos para os bullets de referências."""
        pass

    @abstractmethod
    def get_post_methodology_paragraphs(self, total_ncs) -> list:
        """
        Retorna os parágrafos que ficam logo após as referências de metodologia.
        Cada parágrafo é uma lista de tuplas (texto, bold, italic, color_rgb).
        """
        pass

    @abstractmethod
    def get_levels_data(self) -> dict:
        """
        Retorna os dados de níveis de NC e exemplo para relatórios rodoviários,
        ou None para outros relatórios.
        Retorno esperado: {"niveis": list[str], "ex_str": str, "ex_desc": str} ou None.
        """
        pass

    @abstractmethod
    def get_post_metodologia_extra_paragraphs(self, row, data_extenso, total_achados) -> tuple:
        """
        Retorna uma tupla (titulo_secao_ou_None, lista_de_paragrafos_como_runs) 
        para seções extras logo após a metodologia (como a seção 4 do CRA).
        """
        pass

    # Quadros / Fiscalização (Seção 4 ou 5)
    @abstractmethod
    def render_quadros(self, doc, row, nc_df, criar_tabela_quadros_fn) -> None:
        """Renderiza a seção de Quadros/Fiscalização completa, incluindo títulos e tabelas."""
        pass

    @property
    @abstractmethod
    def quadros_section_title(self) -> str:
        """Título da seção de Fiscalização (ex: '4. FISCALIZAÇÃO')."""
        pass

    @abstractmethod
    def get_quadro_intro_paragraphs(self, row, data_extenso, responsaveis_formatted) -> list:
        """
        Retorna os parágrafos de introdução da seção de Fiscalização.
        Cada parágrafo é uma lista de tuplas (texto, bold, italic, color_rgb).
        """
        pass

    @property
    @abstractmethod
    def quadro_title_template(self) -> str:
        """Template do título do Quadro 1."""
        pass

    # Tabela de Não Conformidades (Quadro 1)
    @property
    @abstractmethod
    def nc_table_headers(self) -> list:
        """Lista de cabeçalhos das colunas do Quadro 1."""
        pass

    @property
    @abstractmethod
    def nc_table_col_widths(self) -> list:
        """Lista de larguras das colunas do Quadro 1."""
        pass

    @abstractmethod
    def format_nc_table_total_row(self, table, row_idx, total_ncs) -> None:
        """Formata a linha de TOTAL do Quadro 1 para este relatório."""
        pass

    # Seções Finais
    @property
    @abstractmethod
    def finalizacao_sections_config(self) -> dict:
        """Configuração das seções finais (número -> tipo)."""
        pass

    @abstractmethod
    def get_determinations_paragraphs(self, total_ncs) -> list:
        """
        Retorna os parágrafos da seção de determinações.
        Cada parágrafo é uma lista de tuplas (texto, bold, italic, color_rgb).
        """
        pass

    @abstractmethod
    def get_recommendations_paragraphs(self) -> list:
        """
        Retorna as recomendações listadas.
        Cada parágrafo é uma lista de tuplas (texto, bold, italic, color_rgb).
        """
        pass

    @abstractmethod
    def get_conclusions_paragraphs(self, total_ncs, local_val) -> list:
        """
        Retorna os parágrafos da seção de conclusões.
        Cada parágrafo é uma lista de tuplas (texto, bold, italic, color_rgb).
        """
        pass

    @abstractmethod
    def render_apendices(self, doc, row, ncs_reais, pas_reais, fotos_dir, data_fisc, ano, criar_grade_fotos_fn) -> None:
        """Renderiza os apêndices de fotos específicos de cada relatório."""
        pass

    # Assinaturas e Rodapé
    @property
    @abstractmethod
    def analyst_title(self) -> str:
        """Título padrão do analista/especialista para assinaturas da capa."""
        pass

    @abstractmethod
    def get_process_sei_texts(self, row, ano=None) -> list:
        """Retorna a lista de textos do rodapé da capa (Processo/SEI)."""
        pass

    def _replace_raw_text(self, text: str) -> str:
        if not text:
            return ""
        return (text.replace("fiscalização", "monitoramento")
                    .replace("Fiscalização", "Monitoramento")
                    .replace("FISCALIZAÇÃO", "MONITORAMENTO")
                    .replace("fiscalizações", "monitoramentos")
                    .replace("Fiscalizações", "Monitoramentos")
                    .replace("FISCALIZAÇÕES", "MONITORAMENTOS")
                    .replace("fiscalizatória", "monitoradora")
                    .replace("fiscalizatórias", "monitoradoras")
                    .replace("Fiscalizatória", "Monitoradora")
                    .replace("Fiscalizatórias", "Monitoradoras")
                    .replace("fiscalizatório", "monitorador")
                    .replace("fiscalizatórios", "monitoradores")
                    .replace("Fiscalizatório", "Monitorador")
                    .replace("Fiscalizatórios", "Monitoradores")
                    .replace("fiscalizado", "monitorado")
                    .replace("fiscalizados", "monitorados")
                    .replace("Fiscalizado", "Monitorado")
                    .replace("Fiscalizados", "Monitorados")
                    .replace("FISCALIZADO", "MONITORADO")
                    .replace("FISCALIZADOS", "MONITORADOS")
                    .replace("fiscalizador", "monitorador")
                    .replace("fiscalizadores", "monitoradores")
                    .replace("Fiscalizador", "Monitorador")
                    .replace("Fiscalizadores", "Monitorador")
                    .replace("FISCALIZADOR", "MONITORADOR")
                    .replace("FISCALIZADORES", "MONITORADORES")
                    .replace("fiscalizadora", "monitoradora")
                    .replace("fiscalizadoras", "monitoradoras")
                    .replace("Fiscalizadora", "Monitoradora")
                    .replace("Fiscalizadoras", "Monitoradoras")
                    .replace("fiscalizar", "monitorar")
                    .replace("Fiscalizar", "Monitorar")
                    .replace("FISCALIZAR", "MONITORAR"))

    def _replace_text(self, paragraphs_list) -> list:
        if not paragraphs_list:
            return []
        res = []
        for p in paragraphs_list:
            new_p = []
            for text, bold, italic, color in p:
                new_p.append((self._replace_raw_text(text), bold, italic, color))
            res.append(new_p)
        return res


class BaseMonitoramentoMixin:
    """
    Mixin reutilizável para relatórios de monitoramento.
    Aplica as transformações sistemáticas de termos de fiscalização para monitoramento
    em todas as seções textuais, sumário, quadros e tabelas padrão.
    """

    def get_sumario_linhas(self, row) -> list:
        base_linhas = super().get_sumario_linhas(row)
        return [l.replace("FISCALIZAÇÃO", "MONITORAMENTO") for l in base_linhas]

    @property
    def quadros_section_title(self) -> str:
        return super().quadros_section_title.replace("FISCALIZAÇÃO", "MONITORAMENTO")

    def get_intro_paragraphs(self, row, ano, data_extenso) -> list:
        return self._replace_text(super().get_intro_paragraphs(row, ano, data_extenso))

    def get_objective_paragraphs(self, row) -> list:
        return self._replace_text(super().get_objective_paragraphs(row))

    def get_quadro_intro_paragraphs(self, row, data_extenso, responsaveis_formatted) -> list:
        return self._replace_text(super().get_quadro_intro_paragraphs(row, data_extenso, responsaveis_formatted))

    def get_determinations_paragraphs(self, total_ncs) -> list:
        return self._replace_text(super().get_determinations_paragraphs(total_ncs))

    def get_recommendations_paragraphs(self) -> list:
        return self._replace_text(super().get_recommendations_paragraphs())

    def get_conclusions_paragraphs(self, total_ncs, local_val) -> list:
        return self._replace_text(super().get_conclusions_paragraphs(total_ncs, local_val))

    def get_general_info_rows(self, row, responsaveis_formatted, periodo_val) -> list:
        base_rows = super().get_general_info_rows(row, responsaveis_formatted, periodo_val)
        res = []
        for campo, valor, is_header, val_bold in base_rows:
            new_campo = (campo.replace("fiscalização", "monitoramento")
                              .replace("Fiscalização", "Monitoramento")
                              .replace("FISCALIZADOR", "MONITORADOR")
                              .replace("fiscalizador", "monitorador")
                              .replace("Fiscalizador", "Monitorador"))
            new_valor = (valor.replace("fiscalização", "monitoramento")
                              .replace("Fiscalização", "Monitoramento")
                              .replace("fiscalizações", "monitoramentos")
                              .replace("Fiscalizações", "Monitoramentos")
                              .replace("fiscalizado", "monitorado")
                              .replace("fiscalizados", "monitorados")
                              .replace("Fiscalizados", "Monitorados"))
            res.append((new_campo, new_valor, is_header, val_bold))
        return res

    def get_abbreviations(self) -> list:
        base_abbr = super().get_abbreviations()
        res = []
        for sigla, definicao in base_abbr:
            new_def = (definicao.replace("fiscalização", "monitoramento")
                                .replace("Fiscalização", "Monitoramento")
                                .replace("fiscalizações", "monitoramentos")
                                .replace("Fiscalizações", "Monitoramentos")
                                .replace("fiscalizar", "monitorar")
                                .replace("Fiscalizar", "Monitorar"))
            res.append((sigla, new_def))
        return res

    def get_methodology_paragraphs(self, data_extenso) -> list:
        return self._replace_text(super().get_methodology_paragraphs(data_extenso))

    def get_post_methodology_paragraphs(self, total_ncs) -> list:
        return self._replace_text(super().get_post_methodology_paragraphs(total_ncs))

    def get_references_bullets(self) -> list:
        base_bullets = super().get_references_bullets()
        return [(self._replace_raw_text(text), recuado, is_bullet) for text, recuado, is_bullet in base_bullets]

    def get_levels_data(self) -> dict:
        base_data = super().get_levels_data()
        if not base_data:
            return None
        return {
            "niveis": [n.replace("fiscalizada", "monitorada")
                        .replace("fiscalização", "monitoramento")
                        .replace("Fiscalização", "Monitoramento") for n in base_data["niveis"]],
            "ex_str": base_data["ex_str"],
            "ex_desc": (base_data["ex_desc"].replace("fiscalizada", "monitorada")
                                            .replace("fiscalização", "monitoramento")
                                            .replace("Fiscalização", "Monitoramento")
                                            .replace("fiscalizado", "monitorado")
                                            .replace("fiscalizados", "monitorados")
                                            .replace("Fiscalizados", "Monitorados")
                                            .replace("fiscalizadora", "monitoradora"))
        }

    def get_post_metodologia_extra_paragraphs(self, row, data_extenso, total_achados) -> tuple:
        title, paragraphs = super().get_post_metodologia_extra_paragraphs(row, data_extenso, total_achados)
        new_title = title.replace("FISCALIZAÇÃO", "MONITORAMENTO") if title else None
        return (new_title, self._replace_text(paragraphs))

