# -*- coding: utf-8 -*-
import base64
import gc
import io
import os
import sys
import tempfile
from typing import Dict, List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

# Garante que o diretório 'src' esteja no sys.path para importações internas
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from server.schemas import (
    CustomNcSchema,
    GerarRelatorioPayloadSchema,
    PessoaSchema,
    PlanilhaRequestSchema,
)
from database.manager import (
    carregar_contratos,
    carregar_coordenadores,
    carregar_custom_ncs,
    carregar_custom_ncs_socicam,
    carregar_responsaveis,
    salvar_contratos,
    salvar_coordenadores,
    salvar_custom_ncs,
    salvar_custom_ncs_socicam,
    salvar_responsaveis,
)
from monitoramento_utils import extrair_ncs_e_fotos_anterior
from report import gerar_relatorio
from sections.quadros.quadros import MAP_SIGLAS
from services.data_service import gerar_planilha_excel_buffer
from services.image_service import comprimir_imagem_para_word
from services.monitoramento_service import processar_documento_monitoramento_anterior

BASE_NC_OPTIONS = [
    "FI", "TTC", "TTL", "TLC", "TLL", "TRR", "J", "TB",
    "JE", "TBE", "ALP", "ATP", "O", "P", "EX", "D", "R",
    "ALC", "ATC", "E"
]

LOCAIS_SOCICAM = [
    "Garanhuns",
    "Arcoverde",
    "Serra Talhada",
    "Petrolina",
    "Caruaru",
    "TIP Recife",
]

CONTRATOS_PADRAO = {
    "CRA": "CT. nº 043/2011",
    "CRC": "CGPE-001/2006",
    "SOCICAM": "CT. nº 1.041.080/08",
}

app = FastAPI(
    title="ARPE - Gerador de Relatórios API",
    description="Backend stateless para geração de relatórios regulatórios (CRA, CRC, SOCICAM x Fiscalização, Monitoramento)",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _sincronizar_map_siglas_global(
    custom_ncs: List[Dict[str, str]],
    custom_ncs_socicam: List[Dict[str, str]],
    extra_map: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    for item in custom_ncs + custom_ncs_socicam:
        sigla = str(item.get("sigla", "")).strip()
        desc = str(item.get("descricao", "")).strip()
        if sigla and desc:
            MAP_SIGLAS[sigla] = desc
    if extra_map:
        for k, v in extra_map.items():
            if k and v:
                MAP_SIGLAS[str(k).strip()] = str(v).strip()
    return dict(MAP_SIGLAS)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "gerador-relatorios-api"}


@app.get("/api/config/bootstrap")
def get_bootstrap_config():
    responsaveis = carregar_responsaveis()
    coordenadores = carregar_coordenadores()
    contratos = carregar_contratos()
    custom_ncs = carregar_custom_ncs()
    custom_ncs_socicam = carregar_custom_ncs_socicam()
    siglas_map = _sincronizar_map_siglas_global(custom_ncs, custom_ncs_socicam)

    return {
        "responsaveis": responsaveis,
        "coordenadores": coordenadores,
        "contratos": contratos,
        "contratos_padrao": CONTRATOS_PADRAO,
        "custom_ncs": custom_ncs,
        "custom_ncs_socicam": custom_ncs_socicam,
        "base_nc_options": BASE_NC_OPTIONS,
        "map_siglas": siglas_map,
        "locais_socicam": LOCAIS_SOCICAM,
    }


@app.put("/api/config/responsaveis")
def update_responsaveis(items: List[PessoaSchema]):
    lista = [item.model_dump() for item in items]
    persisted = salvar_responsaveis(lista)
    return {"responsaveis": lista, "persisted": persisted}


@app.put("/api/config/coordenadores")
def update_coordenadores(items: List[PessoaSchema]):
    lista = [item.model_dump() for item in items]
    persisted = salvar_coordenadores(lista)
    return {"coordenadores": lista, "persisted": persisted}


@app.put("/api/config/contratos")
def update_contratos(items: List[str]):
    lista = [str(c).strip() for c in items if str(c).strip()]
    persisted = salvar_contratos(lista)
    return {"contratos": lista, "persisted": persisted}


@app.put("/api/config/custom-ncs")
def update_custom_ncs(items: List[CustomNcSchema]):
    lista = [item.model_dump() for item in items]
    persisted = salvar_custom_ncs(lista)
    siglas_map = _sincronizar_map_siglas_global(lista, carregar_custom_ncs_socicam())
    return {"custom_ncs": lista, "map_siglas": siglas_map, "persisted": persisted}


@app.put("/api/config/custom-ncs-socicam")
def update_custom_ncs_socicam(items: List[CustomNcSchema]):
    lista = [item.model_dump() for item in items]
    persisted = salvar_custom_ncs_socicam(lista)
    siglas_map = _sincronizar_map_siglas_global(carregar_custom_ncs(), lista)
    return {"custom_ncs_socicam": lista, "map_siglas": siglas_map, "persisted": persisted}


@app.post("/api/monitoramento/parse")
async def parse_monitoramento_anterior(arquivo: UploadFile = File(...)):
    if not arquivo.filename:
        raise HTTPException(status_code=400, detail="Arquivo de monitoramento anterior inválido.")
    try:
        file_bytes = await arquivo.read()
        if not file_bytes:
            raise HTTPException(status_code=400, detail="O arquivo enviado está vazio.")
        resultado = processar_documento_monitoramento_anterior(file_bytes, arquivo.filename)
        return resultado
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Não foi possível processar o documento de monitoramento anterior: {str(exc)}",
        )


@app.post("/api/relatorios/planilha")
def baixar_planilha_excel(req: PlanilhaRequestSchema):
    fisc_list = [f.model_dump(by_alias=True) for f in req.fiscalizacoes]
    nc_list = [nc.model_dump(by_alias=True) for nc in req.registros_nc]
    excel_buffer = gerar_planilha_excel_buffer(fisc_list, nc_list)
    return Response(
        content=excel_buffer.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="planilha_fiscalizacao.xlsx"'},
    )


def _salvar_data_url_em_disco(data_url_or_b64: str, dest_path: str) -> None:
    if not data_url_or_b64:
        return
    raw_b64 = data_url_or_b64.split(",", 1)[-1] if "," in data_url_or_b64 else data_url_or_b64
    img_bytes = base64.b64decode(raw_b64)
    with open(dest_path, "wb") as f:
        f.write(img_bytes)


@app.post("/api/relatorios/gerar")
async def gerar_relatorios_endpoint(
    payload_json: str = Form(...),
    fotos_atuais: List[UploadFile] = File(default=[]),
    documento_anterior: Optional[UploadFile] = File(default=None),
    planilha_elegibilidade: Optional[UploadFile] = File(default=None),
):
    try:
        payload = GerarRelatorioPayloadSchema.model_validate_json(payload_json)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Payload JSON inválido: {str(exc)}")

    if not payload.fiscalizacoes:
        raise HTTPException(status_code=400, detail="Adicione pelo menos uma fiscalização/monitoramento primeiro.")

    is_monitoring = payload.categoria_relatorio == "Monitoramento"
    tipo_key = f"{payload.tipo_relatorio}_MONITORAMENTO" if is_monitoring else payload.tipo_relatorio

    if tipo_key == "CRC_MONITORAMENTO" and not documento_anterior:
        raise HTTPException(
            status_code=400,
            detail="O arquivo do monitoramento anterior (.docx) é obrigatório para gerar o relatório CRC Monitoramento.",
        )

    # Sincroniza overrides em memória (garante funcionamento stateless em Serverless)
    if payload.responsaveis_override is not None:
        salvar_responsaveis([r.model_dump() for r in payload.responsaveis_override])
    if payload.coordenadores_override is not None:
        salvar_coordenadores([c.model_dump() for c in payload.coordenadores_override])
    _sincronizar_map_siglas_global(
        carregar_custom_ncs(),
        carregar_custom_ncs_socicam(),
        payload.custom_siglas_map,
    )

    fisc_list = [f.model_dump(by_alias=True) for f in payload.fiscalizacoes]
    nc_list = []
    for nc_item in payload.registros_nc:
        d = nc_item.model_dump(by_alias=True, exclude_none=True)
        nc_list.append(d)

    avisos: List[str] = []
    relatorios_gerados: List[Dict[str, str]] = []

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
        fotos_dir = os.path.join(temp_dir, "fotos")
        reports_dir = os.path.join(temp_dir, "reports")
        os.makedirs(fotos_dir, exist_ok=True)
        os.makedirs(reports_dir, exist_ok=True)

        # 1. Salvar fotos atuais enviadas via multipart (com compressão opcional <= 500 KB)
        for upload in fotos_atuais:
            if upload and upload.filename:
                safe_name = os.path.basename(upload.filename)
                dest_path = os.path.join(fotos_dir, safe_name)
                content = await upload.read()
                if payload.compress_images:
                    content = comprimir_imagem_para_word(content, max_kb=500)
                with open(dest_path, "wb") as f:
                    f.write(content)

        # 1.1 Processar planilha de elegibilidade (Quadro 1 CRA Fiscalização)
        planilha_elegibilidade_stream: Optional[io.BytesIO] = None
        if planilha_elegibilidade and planilha_elegibilidade.filename:
            eleg_bytes = await planilha_elegibilidade.read()
            if eleg_bytes:
                planilha_elegibilidade_stream = io.BytesIO(eleg_bytes)
                planilha_elegibilidade_stream.name = planilha_elegibilidade.filename

        # 2. Se for Monitoramento, extrair fotos antigas do documento_anterior e/ou fotos_anteriores_b64
        doc_anterior_stream: Optional[io.BytesIO] = None
        if documento_anterior and documento_anterior.filename:
            doc_bytes = await documento_anterior.read()
            if doc_bytes:
                doc_anterior_stream = io.BytesIO(doc_bytes)
                doc_anterior_stream.name = documento_anterior.filename
                if is_monitoring:
                    extrair_ncs_e_fotos_anterior(doc_anterior_stream, output_dir=fotos_dir)
                    doc_anterior_stream.seek(0)

        for fname, b64_val in payload.fotos_anteriores_b64.items():
            safe_old_name = os.path.basename(fname)
            if safe_old_name and b64_val:
                dest_old = os.path.join(fotos_dir, safe_old_name)
                if not os.path.exists(dest_old):
                    try:
                        _salvar_data_url_em_disco(b64_val, dest_old)
                    except Exception:
                        pass

        # Normalizar "Foto Anterior" nos registros para apontar para o arquivo dentro de fotos_dir
        for nc in nc_list:
            foto_ant = str(nc.get("Foto Anterior", "")).strip()
            if foto_ant:
                candidate = os.path.join(fotos_dir, os.path.basename(foto_ant))
                if os.path.exists(candidate):
                    nc["Foto Anterior"] = candidate

        # Diagnóstico de fotos atuais referenciadas
        fotos_salvas = {f.lower() for f in os.listdir(fotos_dir)} if os.path.isdir(fotos_dir) else set()
        fotos_referenciadas = set()
        for nc in nc_list:
            foto_nome = str(nc.get("Foto", "")).strip()
            if foto_nome:
                fotos_referenciadas.add(os.path.basename(foto_nome))

        if fotos_referenciadas and not fotos_salvas:
            avisos.append(
                f"Diagnóstico de Fotos: As NCs referenciam {len(fotos_referenciadas)} foto(s), "
                "mas nenhuma foto foi recebida no lote de geração."
            )
        elif fotos_referenciadas:
            faltando = [f for f in sorted(fotos_referenciadas) if f.lower() not in fotos_salvas]
            if faltando:
                amostra = ", ".join(faltando[:5]) + ("..." if len(faltando) > 5 else "")
                avisos.append(
                    f"Diagnóstico de Fotos: {len(faltando)} foto(s) referenciada(s) nas NCs não foram encontradas: {amostra}"
                )

        excel_buffer = gerar_planilha_excel_buffer(fisc_list, nc_list)

        try:
            arquivos_paths, _ = gerar_relatorio(
                caminho_planilha=excel_buffer,
                fotos_dir=fotos_dir,
                relatorios_dir=reports_dir,
                gerar_todos=True,
                tipo_relatorio=tipo_key,
                documento_anterior=doc_anterior_stream,
                planilha_elegibilidade=planilha_elegibilidade_stream,
            )

            for arq_path in arquivos_paths:
                nome_base = os.path.basename(arq_path)
                with open(arq_path, "rb") as f:
                    b64_docx = base64.b64encode(f.read()).decode("utf-8")
                relatorios_gerados.append({
                    "nome": nome_base,
                    "base64": b64_docx,
                })
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Erro ao compilar o documento Word (.docx): {str(exc)}")
        finally:
            gc.collect()

    return {
        "relatorios": relatorios_gerados,
        "avisos": avisos,
    }

