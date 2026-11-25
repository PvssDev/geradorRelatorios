# -*- coding: utf-8 -*-
"""Router FastAPI de Sincronização Mobile <-> Web e Emissão de Presigned URLs
para o Bucket Privado (vistorias-temp) com validação dos 6 Estados Regulatórios.
"""

from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request

from core.rules.auth_sync_rules import (
    PRESIGN_EXPIRES_SECONDS,
    gerar_storage_key_segura,
    pode_aprovar_acessos,
    validar_payload_vistoria_seis_estados,
    validar_presign_upload,
)
from server.auth_sync_schemas import (
    PresignUploadRequestSchema,
    PresignUploadResponseSchema,
    VistoriaSyncRequestSchema,
)
from server.routers.auth_router import get_authenticated_perfil
from services.supabase_gateway import HttpSupabaseGateway, SupabaseGatewayError, get_supabase_gateway

router = APIRouter(prefix="/api/sync", tags=["sync"])


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    if forwarded:
        return forwarded
    return request.client.host if request.client else "unknown"


@router.post("/presign-upload", response_model=PresignUploadResponseSchema)
def emitir_presigned_upload(
    payload: PresignUploadRequestSchema,
    caller: Dict[str, Any] = Depends(get_authenticated_perfil),
    gateway: HttpSupabaseGateway = Depends(get_supabase_gateway),
):
    erro = validar_presign_upload(
        nome_arquivo=payload.nome_arquivo,
        content_type=payload.content_type,
        tamanho_kb=payload.tamanho_kb,
    )
    if erro:
        raise HTTPException(status_code=422, detail=erro)

    try:
        vistoria_existente = gateway.get_vistoria_transito(payload.vistoria_id)
        if (
            vistoria_existente
            and str(vistoria_existente.get("autor_id")) != str(caller["id"])
            and not pode_aprovar_acessos(caller["role"])
        ):
            raise HTTPException(status_code=403, detail="Sem permissão para anexar fotos nesta vistoria.")

        storage_key = gerar_storage_key_segura(payload.vistoria_id)
        upload_url = gateway.create_presigned_upload_url(storage_key)
        return PresignUploadResponseSchema(
            storage_key=storage_key,
            upload_url=upload_url,
            expires_in=PRESIGN_EXPIRES_SECONDS,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except SupabaseGatewayError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))


@router.post("/vistorias")
def sincronizar_vistoria_finalizada(
    payload: VistoriaSyncRequestSchema,
    request: Request,
    caller: Dict[str, Any] = Depends(get_authenticated_perfil),
    gateway: HttpSupabaseGateway = Depends(get_supabase_gateway),
):
    erro_dominio = validar_payload_vistoria_seis_estados(
        concessao=payload.concessao,
        modalidade=payload.modalidade,
        payload_json=payload.payload_json,
    )
    if erro_dominio:
        raise HTTPException(status_code=422, detail=erro_dominio)

    prefixo_esperado = f"{payload.id}/"
    for foto in payload.fotos:
        if not foto.storage_key.startswith(prefixo_esperado) or ".." in foto.storage_key:
            raise HTTPException(
                status_code=422,
                detail=f"Chave de storage inválida para a vistoria ({foto.nome_arquivo}).",
            )

    try:
        existente = gateway.get_vistoria_transito(payload.id)
        if (
            existente
            and str(existente.get("autor_id")) != str(caller["id"])
            and not pode_aprovar_acessos(caller["role"])
        ):
            raise HTTPException(status_code=403, detail="Sem permissão para sobrescrever esta vistoria.")

        autor_id = str(existente["autor_id"]) if existente else str(caller["id"])
        saved = gateway.upsert_vistoria_transito(
            {
                "id": payload.id,
                "id_fiscalizacao": payload.id_fiscalizacao,
                "autor_id": autor_id,
                "concessao": payload.concessao,
                "modalidade": payload.modalidade,
                "status_handoff": "aguardando_web",
                "payload_json": payload.payload_json,
                "total_fotos": len(payload.fotos),
                "atualizado_em": datetime.now(timezone.utc).isoformat(),
            }
        )

        if payload.fotos:
            gateway.upsert_fotos_temp(
                [
                    {
                        "id": f.id,
                        "vistoria_id": payload.id,
                        "storage_key": f.storage_key,
                        "nome_arquivo": f.nome_arquivo,
                        "tamanho_kb": f.tamanho_kb,
                        "ocorrencia_numero": f.ocorrencia_numero,
                    }
                    for f in payload.fotos
                ]
            )

        gateway.insert_audit_log(
            ator_id=str(caller["id"]),
            acao="VISTORIA_SINCRONIZADA",
            alvo=payload.id,
            ip=_client_ip(request),
            detalhes={
                "concessao": payload.concessao,
                "modalidade": payload.modalidade,
                "total_fotos": len(payload.fotos),
            },
        )
        return {"ok": True, "vistoria_id": saved.get("id", payload.id), "total_fotos": len(payload.fotos)}
    except SupabaseGatewayError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))


@router.get("/vistorias")
def listar_vistorias_sincronizadas(
    caller: Dict[str, Any] = Depends(get_authenticated_perfil),
    gateway: HttpSupabaseGateway = Depends(get_supabase_gateway),
):
    try:
        autor_filter = None if pode_aprovar_acessos(caller["role"]) else str(caller["id"])
        rows = gateway.list_vistorias_transito(autor_id_filter=autor_filter)
        return {"vistorias": rows}
    except SupabaseGatewayError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))


@router.get("/vistorias/{vistoria_id}/fotos-urls")
def obter_urls_assinadas_vistoria(
    vistoria_id: str,
    caller: Dict[str, Any] = Depends(get_authenticated_perfil),
    gateway: HttpSupabaseGateway = Depends(get_supabase_gateway),
):
    try:
        vistoria = gateway.get_vistoria_transito(vistoria_id)
        if not vistoria:
            raise HTTPException(status_code=404, detail="Vistoria não encontrada.")
        if str(vistoria.get("autor_id")) != str(caller["id"]) and not pode_aprovar_acessos(caller["role"]):
            raise HTTPException(status_code=403, detail="Sem permissão para acessar as fotos desta vistoria.")

        fotos = gateway.list_fotos_temp_by_vistoria(vistoria_id)
        assinadas = [
            {
                "id": f["id"],
                "nome_arquivo": f["nome_arquivo"],
                "ocorrencia_numero": f.get("ocorrencia_numero"),
                "tamanho_kb": f["tamanho_kb"],
                "download_url": gateway.create_presigned_download_url(
                    str(f["storage_key"]),
                    expires_in=PRESIGN_EXPIRES_SECONDS,
                ),
                "expires_in": PRESIGN_EXPIRES_SECONDS,
            }
            for f in fotos
        ]
        return {"vistoria_id": vistoria_id, "fotos": assinadas}
    except SupabaseGatewayError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))
