# -*- coding: utf-8 -*-
"""Router FastAPI de Sincronização Mobile <-> Web e Emissão de Presigned URLs
para o Bucket Privado (vistorias-temp) com validação dos 6 Estados Regulatórios.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from core.rules.auth_sync_rules import (
    PRESIGN_EXPIRES_SECONDS,
    extrair_registros_historico_achados,
    gerar_storage_key_segura,
    pode_aprovar_acessos,
    resolver_nome_unico_vistoria,
    validar_payload_vistoria_seis_estados,
    validar_presign_upload,
)
from server.auth_sync_schemas import (
    AtribuirVistoriaRequestSchema,
    ConcessaoLiteral,
    ModalidadeLiteral,
    PresignUploadRequestSchema,
    PresignUploadResponseSchema,
    VistoriaSyncRequestSchema,
)
from server.dependencies.auth_deps import get_authenticated_perfil, verificar_origem_confiavel
from services.supabase_gateway import HttpSupabaseGateway, SupabaseGatewayError, get_supabase_gateway

router = APIRouter(prefix="/api/sync", tags=["sync"])


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    if forwarded:
        return forwarded
    return request.client.host if request.client else "unknown"


@router.post("/presign-upload", response_model=PresignUploadResponseSchema, dependencies=[Depends(verificar_origem_confiavel)])
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


@router.post("/vistorias", dependencies=[Depends(verificar_origem_confiavel)])
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
        todas_nuvem = gateway.list_vistorias_transito()
        nomes_outros = [
            str(item.get("id_fiscalizacao", ""))
            for item in todas_nuvem
            if str(item.get("id")) != payload.id
        ]
        id_fiscalizacao_final = resolver_nome_unico_vistoria(
            payload.id_fiscalizacao,
            nomes_outros,
        )

        payload_json_ajustado = dict(payload.payload_json)
        if id_fiscalizacao_final != payload.id_fiscalizacao:
            fisc_dict = payload_json_ajustado.get("fiscalizacao")
            if isinstance(fisc_dict, dict):
                payload_json_ajustado["fiscalizacao"] = {
                    **fisc_dict,
                    "ID da Fiscalização": id_fiscalizacao_final,
                }
            recs = payload_json_ajustado.get("registros_nc")
            if isinstance(recs, list):
                payload_json_ajustado["registros_nc"] = [
                    {**r, "ID da Fiscalização": id_fiscalizacao_final}
                    if isinstance(r, dict)
                    else r
                    for r in recs
                ]

        saved = gateway.upsert_vistoria_transito(
            {
                "id": payload.id,
                "id_fiscalizacao": id_fiscalizacao_final,
                "autor_id": autor_id,
                "concessao": payload.concessao,
                "modalidade": payload.modalidade,
                "status_handoff": "aguardando_web",
                "payload_json": payload_json_ajustado,
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
                "id_fiscalizacao": id_fiscalizacao_final,
                "total_fotos": len(payload.fotos),
            },
        )
        return {
            "ok": True,
            "vistoria_id": saved.get("id", payload.id),
            "id_fiscalizacao": id_fiscalizacao_final,
            "total_fotos": len(payload.fotos),
        }
    except SupabaseGatewayError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))


@router.get("/vistorias")
def listar_vistorias_sincronizadas(
    concessao: Optional[ConcessaoLiteral] = Query(default=None),
    modalidade: Optional[ModalidadeLiteral] = Query(default=None),
    caller: Dict[str, Any] = Depends(get_authenticated_perfil),
    gateway: HttpSupabaseGateway = Depends(get_supabase_gateway),
):
    try:
        autor_filter = None if pode_aprovar_acessos(caller["role"]) else str(caller["id"])
        rows = gateway.list_vistorias_transito(autor_id_filter=autor_filter)
        if concessao:
            rows = [r for r in rows if r.get("concessao") == concessao]
        if modalidade:
            rows = [r for r in rows if r.get("modalidade") == modalidade]
        return {"vistorias": rows}
    except SupabaseGatewayError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))


@router.get("/vistorias/{vistoria_id}")
def obter_vistoria_para_editor(
    vistoria_id: str,
    marcar_revisao: bool = Query(default=False),
    caller: Dict[str, Any] = Depends(get_authenticated_perfil),
    gateway: HttpSupabaseGateway = Depends(get_supabase_gateway),
):
    try:
        vistoria = gateway.get_vistoria_transito(vistoria_id)
        if not vistoria:
            raise HTTPException(status_code=404, detail="Vistoria não encontrada.")
        if str(vistoria.get("autor_id")) != str(caller["id"]) and not pode_aprovar_acessos(caller["role"]):
            raise HTTPException(status_code=403, detail="Sem permissão para abrir esta vistoria.")

        if marcar_revisao and vistoria.get("status_handoff") == "aguardando_web":
            gateway.update_vistoria_status(vistoria_id, "em_revisao")
            vistoria["status_handoff"] = "em_revisao"
        return {"vistoria": vistoria}
    except SupabaseGatewayError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))


@router.post("/vistorias/{vistoria_id}/concluir", dependencies=[Depends(verificar_origem_confiavel)])
def concluir_e_expurgar_vistoria(
    vistoria_id: str,
    request: Request,
    caller: Dict[str, Any] = Depends(get_authenticated_perfil),
    gateway: HttpSupabaseGateway = Depends(get_supabase_gateway),
):
    """Grava achados anônimos no histórico permanente e expurga fotos temporárias (LGPD)."""
    try:
        vistoria = gateway.get_vistoria_transito(vistoria_id)
        if not vistoria:
            raise HTTPException(status_code=404, detail="Vistoria não encontrada.")
        if str(vistoria.get("autor_id")) != str(caller["id"]) and not pode_aprovar_acessos(caller["role"]):
            raise HTTPException(status_code=403, detail="Sem permissão para concluir esta vistoria.")

        id_fisc = str(vistoria.get("id_fiscalizacao") or vistoria_id)
        achados_inseridos = 0
        if not gateway.exists_historico_by_vistoria(id_fisc):
            registros = extrair_registros_historico_achados(
                id_vistoria=id_fisc,
                concessao=str(vistoria.get("concessao", "CRA")),
                modalidade=str(vistoria.get("modalidade", "Fiscalização")),
                payload_json=vistoria.get("payload_json") or {},
                fallback_iso=str(vistoria.get("atualizado_em") or ""),
            )
            achados_inseridos = gateway.insert_historico_achados(registros)

        fotos = gateway.list_fotos_temp_by_vistoria(vistoria_id)
        storage_keys = [str(f.get("storage_key", "")) for f in fotos if f.get("storage_key")]
        if storage_keys:
            gateway.delete_storage_objects(storage_keys)
        gateway.delete_fotos_temp_by_vistoria(vistoria_id)
        gateway.update_vistoria_status(vistoria_id, "emitida", total_fotos=0)

        gateway.insert_audit_log(
            ator_id=str(caller["id"]),
            acao="VISTORIA_CONCLUIDA_EXPURGADA",
            alvo=vistoria_id,
            ip=_client_ip(request),
            detalhes={
                "id_fiscalizacao": id_fisc,
                "fotos_expurgadas": len(storage_keys),
                "achados_historico": achados_inseridos,
            },
        )
        return {
            "ok": True,
            "vistoria_id": vistoria_id,
            "status_handoff": "emitida",
            "fotos_expurgadas": len(storage_keys),
            "achados_historico": achados_inseridos,
        }
    except SupabaseGatewayError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))


@router.delete("/vistorias/{vistoria_id}")
def remover_vistoria_sincronizada(
    vistoria_id: str,
    request: Request,
    caller: Dict[str, Any] = Depends(get_authenticated_perfil),
    gateway: HttpSupabaseGateway = Depends(get_supabase_gateway),
):
    try:
        vistoria = gateway.get_vistoria_transito(vistoria_id)
        if not vistoria:
            return {"ok": True, "removida": False}
        is_adm = caller["role"] == "adm"
        is_owner = str(vistoria.get("autor_id")) == str(caller["id"])
        if not is_adm and not is_owner:
            raise HTTPException(status_code=403, detail="Apenas o autor ou o ADM pode remover esta vistoria da nuvem.")

        fotos = gateway.list_fotos_temp_by_vistoria(vistoria_id)
        storage_keys = [str(f.get("storage_key", "")) for f in fotos if f.get("storage_key")]
        if storage_keys:
            gateway.delete_storage_objects(storage_keys)

        gateway.delete_vistoria_transito(vistoria_id)
        gateway.insert_audit_log(
            ator_id=str(caller["id"]),
            acao="VISTORIA_REMOVIDA_NUVEM",
            alvo=vistoria_id,
            ip=_client_ip(request),
            detalhes={"fotos_removidas": len(storage_keys)},
        )
        return {"ok": True, "removida": True, "fotos_removidas": len(storage_keys)}
    except SupabaseGatewayError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))


@router.post("/vistorias/{vistoria_id}/puxar")
def puxar_vistoria_da_nuvem(
    vistoria_id: str,
    request: Request,
    caller: Dict[str, Any] = Depends(get_authenticated_perfil),
    gateway: HttpSupabaseGateway = Depends(get_supabase_gateway),
):
    try:
        vistoria = gateway.get_vistoria_transito(vistoria_id)
        if not vistoria:
            raise HTTPException(status_code=404, detail="Vistoria não encontrada na nuvem.")

        autor_atual = gateway.get_perfil_by_id(str(vistoria.get("autor_id")))
        autor_role = str(autor_atual.get("role", "analista")) if autor_atual else "analista"
        is_owner = str(vistoria.get("autor_id")) == str(caller["id"])
        pode_puxar = (
            caller["role"] == "adm"
            or is_owner
            or (caller["role"] == "coordenador" and autor_role in ("analista", "coordenador"))
        )
        if not pode_puxar:
            raise HTTPException(status_code=403, detail="Sem permissão para puxar esta vistoria.")

        if not is_owner:
            gateway.update_vistoria_autor(vistoria_id, str(caller["id"]))
            vistoria["autor_id"] = str(caller["id"])

        fotos = gateway.list_fotos_temp_by_vistoria(vistoria_id)
        fotos_urls = [
            {
                "id": f["id"],
                "nome_arquivo": f["nome_arquivo"],
                "ocorrencia_numero": f.get("ocorrencia_numero"),
                "tamanho_kb": f["tamanho_kb"],
                "download_url": gateway.create_presigned_download_url(
                    str(f["storage_key"]),
                    expires_in=PRESIGN_EXPIRES_SECONDS,
                ),
            }
            for f in fotos
        ]
        gateway.insert_audit_log(
            ator_id=str(caller["id"]),
            acao="VISTORIA_PUXADA_NUVEM",
            alvo=vistoria_id,
            ip=_client_ip(request),
            detalhes={"autor_anterior_role": autor_role},
        )
        return {"vistoria": vistoria, "fotos": fotos_urls}
    except SupabaseGatewayError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc))


@router.patch("/vistorias/{vistoria_id}/atribuir")
def redirecionar_vistoria_adm(
    vistoria_id: str,
    payload: AtribuirVistoriaRequestSchema,
    request: Request,
    caller: Dict[str, Any] = Depends(get_authenticated_perfil),
    gateway: HttpSupabaseGateway = Depends(get_supabase_gateway),
):
    if caller["role"] != "adm":
        raise HTTPException(status_code=403, detail="Apenas o ADM pode redirecionar vistorias.")

    try:
        vistoria = gateway.get_vistoria_transito(vistoria_id)
        if not vistoria:
            raise HTTPException(status_code=404, detail="Vistoria não encontrada.")

        novo_autor = gateway.get_perfil_by_id(payload.novo_autor_id)
        if not novo_autor or not novo_autor.get("ativo"):
            raise HTTPException(status_code=404, detail="Usuário destino inativo ou não encontrado.")

        gateway.update_vistoria_autor(vistoria_id, str(novo_autor["id"]))
        gateway.insert_audit_log(
            ator_id=str(caller["id"]),
            acao="VISTORIA_REDIRECIONADA",
            alvo=vistoria_id,
            ip=_client_ip(request),
            detalhes={"novo_autor_id": str(novo_autor["id"]), "novo_autor_usuario": novo_autor.get("usuario")},
        )
        return {
            "ok": True,
            "vistoria_id": vistoria_id,
            "autor_id": str(novo_autor["id"]),
            "autor_usuario": str(novo_autor.get("usuario", "")),
            "autor_nome": str(novo_autor.get("nome_completo", "")),
            "autor_role": str(novo_autor.get("role", "analista")),
        }
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
