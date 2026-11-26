# -*- coding: utf-8 -*-
"""Gateway HTTP isolado para Supabase Auth, PostgREST e Storage Privado.

Isola toda comunicação externa e uso de SUPABASE_SERVICE_ROLE_KEY no servidor,
permitindo injeção de dependência limpa nos testes BDD (SOLID - DIP).
"""

import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import httpx

from core.rules.auth_sync_rules import PRESIGN_EXPIRES_SECONDS, SENHA_DESCARTADA_SENTINEL


def carregar_env_raiz() -> None:
    """Carrega variáveis do arquivo .env na raiz do repositório sem exigir python-dotenv."""
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    env_path = os.path.join(root_dir, ".env")
    if not os.path.isfile(env_path):
        return
    try:
        with open(env_path, "r", encoding="utf-8") as fh:
            for raw_line in fh:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = val
    except OSError:
        pass


carregar_env_raiz()


class SupabaseGatewayError(Exception):
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


class HttpSupabaseGateway:
    def __init__(
        self,
        supabase_url: Optional[str] = None,
        anon_key: Optional[str] = None,
        service_role_key: Optional[str] = None,
        storage_bucket: Optional[str] = None,
    ):
        self.base_url = (supabase_url or os.environ.get("SUPABASE_URL", "")).strip().rstrip("/")
        self.anon_key = (anon_key or os.environ.get("SUPABASE_ANON_KEY", "")).strip()
        self.service_role_key = (service_role_key or os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")).strip()
        self.storage_bucket = (storage_bucket or os.environ.get("STORAGE_BUCKET", "vistorias-temp")).strip()

    def is_configured(self) -> bool:
        return bool(self.base_url and self.anon_key and self.service_role_key)

    def get_temp_crypto_secret(self) -> str:
        explicit = os.environ.get("ARPE_TEMP_SECRET_KEY", "").strip()
        if len(explicit) >= 16:
            return explicit
        if len(self.service_role_key) >= 16:
            return self.service_role_key
        raise SupabaseGatewayError("Servidor sem chave configurada (SUPABASE_SERVICE_ROLE_KEY).", 503)

    def _require_configured(self) -> None:
        if not self.is_configured():
            raise SupabaseGatewayError(
                "Integração Supabase não configurada no servidor (.env ausente).",
                status_code=503,
            )

    def _admin_headers(self, prefer: Optional[str] = None) -> Dict[str, str]:
        headers = {
            "apikey": self.service_role_key,
            "Authorization": f"Bearer {self.service_role_key}",
            "Content-Type": "application/json",
        }
        if prefer:
            headers["Prefer"] = prefer
        return headers

    def sign_in_password(self, email_sintetico: str, senha: str) -> Optional[Dict[str, Any]]:
        self._require_configured()
        res = httpx.post(
            f"{self.base_url}/auth/v1/token?grant_type=password",
            headers={"apikey": self.anon_key, "Content-Type": "application/json"},
            json={"email": email_sintetico, "password": senha},
            timeout=10.0,
        )
        if res.status_code != 200:
            return None
        return res.json()

    def get_user_id_from_token(self, access_token: str) -> Optional[str]:
        self._require_configured()
        if not access_token:
            return None
        res = httpx.get(
            f"{self.base_url}/auth/v1/user",
            headers={
                "apikey": self.anon_key,
                "Authorization": f"Bearer {access_token}",
            },
            timeout=8.0,
        )
        if res.status_code != 200:
            return None
        data = res.json()
        return data.get("id")

    def admin_create_user(self, email_sintetico: str, senha: str) -> str:
        self._require_configured()
        res = httpx.post(
            f"{self.base_url}/auth/v1/admin/users",
            headers=self._admin_headers(),
            json={
                "email": email_sintetico,
                "password": senha,
                "email_confirm": True,
            },
            timeout=10.0,
        )
        if res.status_code not in (200, 201):
            raise SupabaseGatewayError("Não foi possível provisionar a credencial no Auth.", 400)
        user_id = res.json().get("id")
        if not user_id:
            raise SupabaseGatewayError("Resposta inválida do provedor de autenticação.", 502)
        return str(user_id)

    def admin_update_user_password(self, user_id: str, nova_senha: str) -> None:
        self._require_configured()
        res = httpx.put(
            f"{self.base_url}/auth/v1/admin/users/{user_id}",
            headers=self._admin_headers(),
            json={"password": nova_senha},
            timeout=10.0,
        )
        if res.status_code not in (200, 204):
            raise SupabaseGatewayError("Não foi possível atualizar a senha do usuário no Auth.", 400)

    def admin_delete_user(self, user_id: str) -> None:
        self._require_configured()
        res = httpx.delete(
            f"{self.base_url}/auth/v1/admin/users/{user_id}",
            headers=self._admin_headers(),
            timeout=10.0,
        )
        if res.status_code not in (200, 204):
            raise SupabaseGatewayError(
                "Não foi possível excluir a conta (o usuário pode possuir vistorias ou registros de auditoria vinculados; desative a conta em Editar).",
                409,
            )

    def update_perfil_admin(self, user_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        self._require_configured()
        res = httpx.patch(
            f"{self.base_url}/rest/v1/perfis",
            headers=self._admin_headers(prefer="return=representation"),
            params={"id": f"eq.{user_id}"},
            json=fields,
            timeout=8.0,
        )
        if res.status_code not in (200, 204):
            raise SupabaseGatewayError("Não foi possível atualizar os dados do usuário.", 400)
        rows = res.json() if res.content else []
        return rows[0] if rows else {"id": user_id, **fields}

    def list_perfis_gerenciaveis(self) -> List[Dict[str, Any]]:
        self._require_configured()
        res = httpx.get(
            f"{self.base_url}/rest/v1/perfis",
            headers=self._admin_headers(),
            params={
                "role": "in.(coordenador,analista)",
                "select": "id,usuario,nome_completo,role,ativo,criado_em",
                "order": "role.desc,nome_completo.asc",
            },
            timeout=8.0,
        )
        if res.status_code != 200:
            raise SupabaseGatewayError("Erro ao listar coordenadores e analistas.", 502)
        return res.json()

    def get_perfil_by_usuario(self, usuario: str) -> Optional[Dict[str, Any]]:
        self._require_configured()
        res = httpx.get(
            f"{self.base_url}/rest/v1/perfis",
            headers=self._admin_headers(),
            params={
                "usuario": f"eq.{usuario}",
                "select": "id,usuario,nome_completo,role,ativo,tentativas_falhas,bloqueado_ate",
                "limit": "1",
            },
            timeout=8.0,
        )
        if res.status_code != 200:
            raise SupabaseGatewayError("Erro ao consultar perfil corporativo.", 502)
        rows = res.json()
        return rows[0] if rows else None

    def get_perfil_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        self._require_configured()
        res = httpx.get(
            f"{self.base_url}/rest/v1/perfis",
            headers=self._admin_headers(),
            params={
                "id": f"eq.{user_id}",
                "select": "id,usuario,nome_completo,role,ativo,tentativas_falhas,bloqueado_ate",
                "limit": "1",
            },
            timeout=8.0,
        )
        if res.status_code != 200:
            raise SupabaseGatewayError("Erro ao consultar perfil por ID.", 502)
        rows = res.json()
        return rows[0] if rows else None

    def update_perfil_lockout(
        self,
        user_id: str,
        tentativas_falhas: int,
        bloqueado_ate: Optional[str],
    ) -> None:
        self._require_configured()
        httpx.patch(
            f"{self.base_url}/rest/v1/perfis",
            headers=self._admin_headers(),
            params={"id": f"eq.{user_id}"},
            json={"tentativas_falhas": tentativas_falhas, "bloqueado_ate": bloqueado_ate},
            timeout=8.0,
        )

    def insert_perfil(self, user_id: str, usuario: str, nome_completo: str, role: str) -> Dict[str, Any]:
        self._require_configured()
        res = httpx.post(
            f"{self.base_url}/rest/v1/perfis",
            headers=self._admin_headers(prefer="return=representation"),
            json={
                "id": user_id,
                "usuario": usuario,
                "nome_completo": nome_completo,
                "role": role,
                "ativo": True,
            },
            timeout=8.0,
        )
        if res.status_code not in (200, 201):
            raise SupabaseGatewayError("Erro ao gravar perfil corporativo.", 400)
        rows = res.json()
        return rows[0] if rows else {"id": user_id, "usuario": usuario, "nome_completo": nome_completo, "role": role, "ativo": True}

    def get_solicitacao_by_usuario(self, usuario: str) -> Optional[Dict[str, Any]]:
        self._require_configured()
        res = httpx.get(
            f"{self.base_url}/rest/v1/solicitacoes_acesso",
            headers=self._admin_headers(),
            params={"usuario": f"eq.{usuario}", "select": "id,usuario,status", "limit": "1"},
            timeout=8.0,
        )
        if res.status_code != 200:
            return None
        rows = res.json()
        return rows[0] if rows else None

    def get_solicitacao_by_id(self, sol_id: str) -> Optional[Dict[str, Any]]:
        self._require_configured()
        res = httpx.get(
            f"{self.base_url}/rest/v1/solicitacoes_acesso",
            headers=self._admin_headers(),
            params={
                "id": f"eq.{sol_id}",
                "select": "id,usuario,nome_completo,role_solicitado,senha_hash_temp,status,criado_em",
                "limit": "1",
            },
            timeout=8.0,
        )
        if res.status_code != 200:
            return None
        rows = res.json()
        return rows[0] if rows else None

    def insert_solicitacao(
        self,
        usuario: str,
        nome_completo: str,
        role_solicitado: str,
        senha_hash_temp: str,
    ) -> Dict[str, Any]:
        self._require_configured()
        res = httpx.post(
            f"{self.base_url}/rest/v1/solicitacoes_acesso",
            headers=self._admin_headers(prefer="return=representation"),
            json={
                "usuario": usuario,
                "nome_completo": nome_completo,
                "role_solicitado": role_solicitado,
                "senha_hash_temp": senha_hash_temp,
                "status": "pendente",
            },
            timeout=8.0,
        )
        if res.status_code not in (200, 201):
            raise SupabaseGatewayError("Não foi possível registrar a solicitação de acesso.", 400)
        rows = res.json()
        return rows[0]

    def list_solicitacoes_pendentes(self) -> List[Dict[str, Any]]:
        self._require_configured()
        res = httpx.get(
            f"{self.base_url}/rest/v1/solicitacoes_acesso",
            headers=self._admin_headers(),
            params={
                "status": "eq.pendente",
                "select": "id,usuario,nome_completo,role_solicitado,status,criado_em",
                "order": "criado_em.desc",
            },
            timeout=8.0,
        )
        if res.status_code != 200:
            raise SupabaseGatewayError("Erro ao listar solicitações pendentes.", 502)
        return res.json()

    def finalize_solicitacao(self, sol_id: str, status: str, decidido_por: str) -> None:
        self._require_configured()
        res = httpx.patch(
            f"{self.base_url}/rest/v1/solicitacoes_acesso",
            headers=self._admin_headers(),
            params={"id": f"eq.{sol_id}"},
            json={
                "status": status,
                "decidido_por": decidido_por,
                "decidido_em": datetime.now(timezone.utc).isoformat(),
                "senha_hash_temp": SENHA_DESCARTADA_SENTINEL,
            },
            timeout=8.0,
        )
        if res.status_code not in (200, 204):
            raise SupabaseGatewayError("Erro ao finalizar status da solicitação.", 502)

    def insert_audit_log(
        self,
        ator_id: Optional[str],
        acao: str,
        alvo: Optional[str] = None,
        ip: Optional[str] = None,
        detalhes: Optional[Dict[str, Any]] = None,
    ) -> None:
        if not self.is_configured():
            return
        try:
            httpx.post(
                f"{self.base_url}/rest/v1/audit_logs",
                headers=self._admin_headers(),
                json={
                    "ator_id": ator_id,
                    "acao": acao,
                    "alvo": alvo,
                    "ip": ip,
                    "detalhes": detalhes or {},
                },
                timeout=6.0,
            )
        except httpx.HTTPError:
            pass

    def _normalize_storage_url(self, raw_path: str) -> str:
        if raw_path.startswith("http://") or raw_path.startswith("https://"):
            return raw_path
        if not raw_path.startswith("/"):
            raw_path = "/" + raw_path
        if raw_path.startswith("/storage/v1/"):
            return f"{self.base_url}{raw_path}"
        return f"{self.base_url}/storage/v1{raw_path}"

    def create_presigned_upload_url(self, storage_key: str) -> str:
        self._require_configured()
        res = httpx.post(
            f"{self.base_url}/storage/v1/object/upload/sign/{self.storage_bucket}/{storage_key}",
            headers=self._admin_headers(),
            json={},
            timeout=8.0,
        )
        if res.status_code not in (200, 201):
            raise SupabaseGatewayError("Falha ao emitir URL assinada de upload no Storage privado.", 502)
        body = res.json()
        raw_url = body.get("url") or body.get("signedURL") or ""
        if not raw_url:
            raise SupabaseGatewayError("Storage não retornou URL assinada válida.", 502)
        return self._normalize_storage_url(raw_url)

    def create_presigned_download_url(self, storage_key: str, expires_in: int = PRESIGN_EXPIRES_SECONDS) -> str:
        self._require_configured()
        res = httpx.post(
            f"{self.base_url}/storage/v1/object/sign/{self.storage_bucket}/{storage_key}",
            headers=self._admin_headers(),
            json={"expiresIn": min(expires_in, PRESIGN_EXPIRES_SECONDS)},
            timeout=8.0,
        )
        if res.status_code not in (200, 201):
            raise SupabaseGatewayError("Falha ao emitir URL assinada de leitura no Storage privado.", 502)
        body = res.json()
        raw_url = body.get("signedURL") or body.get("url") or ""
        if not raw_url:
            raise SupabaseGatewayError("Storage não retornou URL de download válida.", 502)
        return self._normalize_storage_url(raw_url)

    def upsert_vistoria_transito(self, record: Dict[str, Any]) -> Dict[str, Any]:
        self._require_configured()
        res = httpx.post(
            f"{self.base_url}/rest/v1/vistorias_transito",
            headers=self._admin_headers(prefer="resolution=merge-duplicates,return=representation"),
            json=record,
            timeout=10.0,
        )
        if res.status_code not in (200, 201):
            raise SupabaseGatewayError("Falha ao sincronizar vistoria em trânsito.", 400)
        rows = res.json()
        return rows[0] if rows else record

    def upsert_fotos_temp(self, fotos: List[Dict[str, Any]]) -> None:
        self._require_configured()
        if not fotos:
            return
        res = httpx.post(
            f"{self.base_url}/rest/v1/vistorias_fotos_temp",
            headers=self._admin_headers(prefer="resolution=merge-duplicates"),
            json=fotos,
            timeout=10.0,
        )
        if res.status_code not in (200, 201, 204):
            raise SupabaseGatewayError("Falha ao registrar metadados das fotos temporárias.", 400)

    def list_vistorias_transito(self, autor_id_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        self._require_configured()
        params: Dict[str, str] = {
            "status_handoff": "in.(aguardando_web,em_revisao)",
            "select": "id,id_fiscalizacao,autor_id,concessao,modalidade,status_handoff,payload_json,total_fotos,atualizado_em",
            "order": "atualizado_em.desc",
        }
        if autor_id_filter:
            params["autor_id"] = f"eq.{autor_id_filter}"
        res = httpx.get(
            f"{self.base_url}/rest/v1/vistorias_transito",
            headers=self._admin_headers(),
            params=params,
            timeout=10.0,
        )
        if res.status_code != 200:
            raise SupabaseGatewayError("Erro ao listar vistorias sincronizadas.", 502)
        return res.json()

    def get_vistoria_transito(self, vistoria_id: str) -> Optional[Dict[str, Any]]:
        self._require_configured()
        res = httpx.get(
            f"{self.base_url}/rest/v1/vistorias_transito",
            headers=self._admin_headers(),
            params={
                "id": f"eq.{vistoria_id}",
                "select": "id,id_fiscalizacao,autor_id,concessao,modalidade,status_handoff,payload_json,total_fotos,atualizado_em",
                "limit": "1",
            },
            timeout=8.0,
        )
        if res.status_code != 200:
            return None
        rows = res.json()
        return rows[0] if rows else None

    def list_fotos_temp_by_vistoria(self, vistoria_id: str) -> List[Dict[str, Any]]:
        self._require_configured()
        res = httpx.get(
            f"{self.base_url}/rest/v1/vistorias_fotos_temp",
            headers=self._admin_headers(),
            params={
                "vistoria_id": f"eq.{vistoria_id}",
                "select": "id,vistoria_id,storage_key,nome_arquivo,tamanho_kb,ocorrencia_numero,criado_em",
                "order": "criado_em.asc",
            },
            timeout=8.0,
        )
        if res.status_code != 200:
            raise SupabaseGatewayError("Erro ao consultar fotos da vistoria.", 502)
        return res.json()


_default_gateway = HttpSupabaseGateway()


def get_supabase_gateway() -> HttpSupabaseGateway:
    return _default_gateway
