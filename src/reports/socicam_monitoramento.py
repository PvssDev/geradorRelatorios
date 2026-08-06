from reports.socicam import SocicamReport

class SocicamMonitoramentoReport(SocicamReport):
    @property
    def key(self) -> str:
        return "SOCICAM_MONITORAMENTO"

    @property
    def display_name(self) -> str:
        return "SOCICAM (Monitoramento)"

    @property
    def capa_titulo(self) -> str:
        return "RELATÓRIO DE MONITORAMENTO TÉCNICO-OPERACIONAL"

    @property
    def capa_ctr_number_template(self) -> str:
        return "RELATÓRIO DE MONITORAMENTO TÉCNICO-OPERACIONAL CTR Nº 03/{ano}"

    def get_process_sei_texts(self, ano) -> list:
        return [
            f"RELATÓRIO DE MONITORAMENTO TÉCNICO-OPERACIONAL PROC ADM Nº 04/{ano} - CTR",
            f"SEI Nº 0030200023.002186/2026-99"
        ]

    def get_capa_titulos(self, row, ano) -> list:
        local_val = str(row.get("Local", "TIP")).upper()
        if "TERMINAL" not in local_val and "MONITORAMENTO" not in local_val:
            local_val = f"TERMINAL RODOVIÁRIO DE PASSAGEIROS DO RECIFE ({local_val})" if "RECIFE" in local_val or "TIP" in local_val else f"TERMINAL RODOVIÁRIO DE PASSAGEIROS ({local_val})"
        return [
            f"MONITORAMENTO NO {local_val}",
            "PRESTADOR DE SERVIÇO: SOCICAM - ADMINISTRAÇÃO, PROJETOS E REPRESENTAÇÕES LTDA"
        ]

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
