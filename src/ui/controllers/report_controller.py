# -*- coding: utf-8 -*-
"""Controlador da orquestração de relatórios e automação na interface Streamlit.

Encapsula o pipeline de preparação de buffers Excel, gestão volátil de fotos em disco,
execução de relatórios via camada de domínio e rotinas de auto preenchimento inteligente.
"""

from typing import List, Dict, Any, Tuple, Optional
import os
import tempfile
import gc
from services.data_service import (
    gerar_planilha_excel_buffer,
    salvar_fotos_em_diretorio,
)
import report


class ReportController:
    """Controlador responsável por orquestrar a geração e pré-preenchimento de relatórios."""

    @staticmethod
    def processar_geracao_relatorio(
        temp_fiscalizacoes: List[Dict[str, Any]],
        temp_nc: List[Dict[str, Any]],
        fill_photos: List[Any],
        tipo_relatorio: str,
        categoria_relatorio: str,
        uploaded_mon_anterior: Any = None,
        uploaded_planilha_elegibilidade: Any = None,
        otimizar_fotos: bool = True,
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Prepara o ambiente temporário, invoca o pipeline de geração de relatórios e
        retorna os arquivos gerados em memória com avisos/diagnósticos.

        Returns:
            Tuple[List[Dict[str, Any]], List[str]]:
                - Lista de dicionários contendo {'nome': str, 'bytes': bytes}
                - Lista de mensagens de advertência (diagnóstico de fotos faltantes, etc.)
        """
        avisos: List[str] = []
        relatorios_gerados_data: List[Dict[str, Any]] = []

        tipo_key = tipo_relatorio
        if categoria_relatorio == "Monitoramento":
            tipo_key = f"{tipo_key}_MONITORAMENTO"

        if tipo_key == "CRC_MONITORAMENTO" and not uploaded_mon_anterior:
            raise ValueError(
                "Por favor, faça o upload do arquivo do monitoramento anterior (.docx) para gerar o relatório CRC Monitoramento."
            )

        excel_buffer = gerar_planilha_excel_buffer(temp_fiscalizacoes, temp_nc)

        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
            fotos_dir = os.path.join(temp_dir, "fotos")
            reports_dir = os.path.join(temp_dir, "reports")
            os.makedirs(fotos_dir, exist_ok=True)
            os.makedirs(reports_dir, exist_ok=True)

            if fill_photos:
                salvar_fotos_em_diretorio(
                    fill_photos,
                    fotos_dir,
                    otimizar=otimizar_fotos,
                    target_size_kb=500,
                )

            # Diagnóstico: verificar fotos salvas vs fotos referenciadas nas NCs
            fotos_salvas = set(os.listdir(fotos_dir)) if os.path.isdir(fotos_dir) else set()
            fotos_referenciadas = set()
            for nc in temp_nc:
                foto_nome = nc.get("Foto", "")
                if foto_nome and isinstance(foto_nome, str) and foto_nome.strip():
                    fotos_referenciadas.add(foto_nome.strip())

            if fotos_referenciadas and not fotos_salvas:
                avisos.append(
                    f"Diagnóstico de Fotos: As NCs referenciam {len(fotos_referenciadas)} foto(s), "
                    f"mas nenhuma foto foi salva no diretório temporário. "
                    f"Verifique se as fotos foram carregadas no uploader."
                )
            elif fotos_referenciadas:
                fotos_faltando = fotos_referenciadas - fotos_salvas
                if fotos_faltando:
                    avisos.append(
                        f"Diagnóstico de Fotos: {len(fotos_faltando)} foto(s) referenciada(s) nas NCs "
                        f"não foram encontrada(s) no diretório: {', '.join(sorted(fotos_faltando)[:5])}"
                        f"{'...' if len(fotos_faltando) > 5 else ''}"
                    )

            try:
                arquivos_caminhos, _ = report.gerar_relatorio(
                    caminho_planilha=excel_buffer,
                    fotos_dir=fotos_dir,
                    relatorios_dir=reports_dir,
                    gerar_todos=True,
                    tipo_relatorio=tipo_key,
                    documento_anterior=uploaded_mon_anterior,
                    planilha_elegibilidade=uploaded_planilha_elegibilidade,
                )

                if arquivos_caminhos:
                    for arquivo in arquivos_caminhos:
                        nome_base = os.path.basename(arquivo)
                        with open(arquivo, "rb") as f:
                            relatorios_gerados_data.append({
                                "nome": nome_base,
                                "bytes": f.read(),
                            })
            finally:
                gc.collect()

        return relatorios_gerados_data, avisos

    @staticmethod
    def construir_auto_preenchimento(
        tipo_relatorio: str,
        categoria_relatorio: str,
        term_fisc_prep: str,
        pessoal_responsaveis: List[Dict[str, Any]],
        coordenadores: List[Dict[str, Any]],
        temp_fiscalizacoes: List[Dict[str, Any]],
        fill_photos: List[Any],
        old_photos_to_match: Optional[List[Dict[str, Any]]] = None,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Gera automaticamente a estrutura de fiscalização e registros/NCs padrões.

        Returns:
            Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
                - Nova lista de fiscalizações
                - Nova lista de Não Conformidades (temp_nc)
        """
        is_mon = categoria_relatorio == "Monitoramento"
        novas_fisc = list(temp_fiscalizacoes) if temp_fiscalizacoes else []
        novas_nc: List[Dict[str, Any]] = []

        if tipo_relatorio == "CRA":
            contrato = "CT. nº 043/2011"
            local_default = "Rota do Atlântico"
        elif tipo_relatorio == "CRC":
            contrato = "CGPE-001/2006"
            local_default = "Sistema Viário do Paiva"
        else:  # SOCICAM
            contrato = "CT. nº 1.041.080/08"
            local_default = "=Local="

        # Responsáveis
        if pessoal_responsaveis:
            resp_nomes = ", ".join([r["nome"] for r in pessoal_responsaveis if "nome" in r])
        else:
            resp_nomes = "=Pessoal Responsável="

        # Coordenador
        if coordenadores:
            coord_nome = coordenadores[0].get("nome", "=Coordenador=")
        else:
            coord_nome = "=Coordenador="

        # 1. Garante que exista pelo menos um registro de Fiscalização/Monitoramento
        if not novas_fisc:
            id_fisc_auto = f"=ID {term_fisc_prep}=" if term_fisc_prep else "=ID da Fiscalização="
            novas_fisc.append({
                "ID da Fiscalização": id_fisc_auto,
                "Data": "=Data=",
                "Hora": "=Hora=" if tipo_relatorio == "CRA" else "",
                "Cidade": "=Cidade=" if tipo_relatorio == "CRA" else "",
                "Local": local_default,
                "Pessoal Responsável": resp_nomes,
                "Coordenador": coord_nome,
                "Contrato": contrato,
                "Período": "=Período=",
                "Relatório Gerado": False,
            })
            id_vinculo = id_fisc_auto
            terminal_nc = local_default
        else:
            id_vinculo = novas_fisc[0].get("ID da Fiscalização", "=ID da Fiscalização=")
            terminal_nc = novas_fisc[0].get("Local", local_default)

        # 2. Preencher Não Conformidades / Registros
        if is_mon and old_photos_to_match:
            for idx, item in enumerate(old_photos_to_match):
                foto_nova = fill_photos[idx % len(fill_photos)].name if fill_photos else ""
                foto_ant = item.get("old_photo_path", "")
                legenda_ant = item.get("old_legend", "")
                id_nc = item.get("id_nc", f"=Identificação {idx+1}=")
                trecho_val = item.get("trecho") or "=Trecho="
                pista_val = item.get("pista") or "=Pista="
                constatacao_val = item.get("constatacao") or "=CONSTATAÇÃO="

                if tipo_relatorio == "SOCICAM":
                    pos_label = "=INFORMAÇÃO SOCICAM="
                elif tipo_relatorio == "CRA":
                    pos_label = "=POSICIONAMENTO CRA="
                else:
                    pos_label = "=POSICIONAMENTO CRC="

                rec = {
                    "ID da Fiscalização": id_vinculo,
                    "Nº": idx + 1,
                    "Terminal": terminal_nc,
                    "Pista": pista_val,
                    "Trecho": trecho_val,
                    "Não Conformidade": id_nc if tipo_relatorio in ["CRC", "SOCICAM", "CRA"] else "=Não Conformidade=",
                    "Ponto de Atenção": "",
                    "Foto": foto_nova,
                    "Foto Anterior": foto_ant,
                    "Legenda Anterior": legenda_ant,
                    "Legenda da Foto": "=legenda da foto atual=",
                    "Observações": constatacao_val if tipo_relatorio in ["CRC", "SOCICAM", "CRA"] else "=legenda da foto atual=",
                    "Identificação": id_nc,
                    "Direção (faixa)": "=Direção (faixa)=" if tipo_relatorio == "CRA" and not is_mon else "",
                    "Fundamento da infração": "=Fundamento da infração=" if tipo_relatorio == "CRA" and not is_mon else "",
                    "Determinação": pos_label if tipo_relatorio in ["CRC", "SOCICAM", "CRA"] else "=Determinação=",
                    "Situação": "Pendente",
                    "Análise ARPE": "=ANÁLISE ARPE=",
                }
                novas_nc.append(rec)
        elif fill_photos:
            for idx, photo in enumerate(fill_photos):
                i = idx + 1
                rec = {
                    "ID da Fiscalização": id_vinculo,
                    "Nº": i,
                    "Terminal": terminal_nc,
                    "Pista": "=Pista=" if tipo_relatorio == "CRA" else "",
                    "Trecho": "=Trecho=" if tipo_relatorio == "CRA" else "",
                    "Não Conformidade": "=Não Conformidade=",
                    "Ponto de Atenção": "",
                    "Foto": photo.name if hasattr(photo, "name") else str(photo),
                    "Foto Anterior": "",
                    "Legenda Anterior": "",
                    "Legenda da Foto": "=legenda da foto atual=",
                    "Observações": "=Observações=",
                    "Identificação": "=Não Conformidade=",
                    "Direção (faixa)": "=Direção (faixa)=" if tipo_relatorio == "CRA" else "",
                    "Fundamento da infração": "=Fundamento da infração=" if tipo_relatorio == "CRA" else "",
                    "Determinação": "=Determinação=",
                    "Situação": "Pendente",
                    "Análise ARPE": "=Análise ARPE=",
                }
                novas_nc.append(rec)

        return novas_fisc, novas_nc
