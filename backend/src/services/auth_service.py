# -*- coding: utf-8 -*-
"""Serviço de aplicação de Autenticação Corporativa (Fase W1).

Responsabilidade única: orquestrar os casos de uso de autenticação sem e-mail,
lockout, aprovação individual de acessos e gestão ADM, combinando as regras puras
de `core.rules.auth_sync_rules` com a porta `IAuthGateway`.

Não conhece FastAPI, cookies ou HTTP: sinaliza falhas via `AuthError`, que a
camada de routers traduz para `HTTPException`.

LGPD: nenhuma senha, token ou e-mail sintético é escrito em `audit_logs` ou
retornado nas estruturas públicas.
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from core.interfaces.auth_gateway import IAuthGateway
from core.rules.auth_sync_rules import (
    calcular_estado_pos_falha_login,
    criptografar_senha_temporaria,
    descriptografar_senha_temporaria,
    esta_conta_bloqueada,
    montar_email_sintetico,
    normalizar_usuario,
    pode_aprovar_acessos,
    validar_forca_senha,
    validar_formato_usuario,
)

GENERIC_AUTH_ERROR = "Usuário ou senha inválidos."
MSG_USUARIO_INVALIDO = "Usuário deve ter 3 a 32 caracteres (letras minúsculas, números, . _ -)."
MAX_AUDIT_LOGS = 500


class AuthError(Exception):
    """Falha de caso de uso com status HTTP sugerido (sem dados sensíveis na mensagem)."""

    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(detail)
        self.detail = detail
        self.status_code = status_code


@dataclass(frozen=True)
class SessaoAutenticada:
    """Resultado imutável de login/refresh."""

    perfil: Dict[str, Any]
    access_token: str
    refresh_token: str


def serializar_perfil_publico(row: Dict[str, Any]) -> Dict[str, Any]:
    """Projeção mínima (LGPD): id, usuario, nome_completo, role, ativo."""
    return {
        "id": str(row["id"]),
        "usuario": str(row["usuario"]),
        "nome_completo": str(row["nome_completo"]),
        "role": row["role"],
        "ativo": bool(row["ativo"]),
    }


class AuthService:
    def __init__(self, gateway: IAuthGateway):
        self._gw = gateway

    # ------------------------------------------------------------------ #
    # Validações compartilhadas
    # ------------------------------------------------------------------ #
    @staticmethod
    def _validar_nome(nome: str) -> str:
        nome_limpo = (nome or "").strip()
        if len(nome_limpo) < 3:
            raise AuthError("Informe o nome completo.", 422)
        return nome_limpo

    @staticmethod
    def _validar_usuario_cadastro(usuario_raw: str) -> str:
        usuario = normalizar_usuario(usuario_raw)
        if not validar_formato_usuario(usuario):
            raise AuthError(MSG_USUARIO_INVALIDO, 422)
        return usuario

    @staticmethod
    def _validar_senha(senha: str, role: str) -> None:
        erro = validar_forca_senha(senha, role=role)
        if erro:
            raise AuthError(erro, 422)

    # ------------------------------------------------------------------ #
    # Sessão
    # ------------------------------------------------------------------ #
    def _despachar(self, defer: Optional[Callable[..., None]], fn: Callable[..., Any], *args: Any, **kwargs: Any) -> None:
        if defer is not None:
            defer(fn, *args, **kwargs)
        else:
            fn(*args, **kwargs)

    def login(
        self,
        usuario_raw: str,
        senha: str,
        ip: str,
        client_type: str,
        defer: Optional[Callable[..., None]] = None,
    ) -> SessaoAutenticada:
        """Dado usuario+senha, autentica no provedor aplicando lockout 5 falhas / 15 min."""
        usuario = normalizar_usuario(usuario_raw)
        if not validar_formato_usuario(usuario):
            raise AuthError(GENERIC_AUTH_ERROR, 401)

        perfil = self._gw.get_perfil_by_usuario(usuario)
        if perfil and esta_conta_bloqueada(perfil.get("bloqueado_ate")):
            self._gw.insert_audit_log(
                ator_id=perfil["id"],
                acao="LOGIN_BLOQUEADO_TENTATIVA",
                alvo=usuario,
                ip=ip,
            )
            raise AuthError(
                "Conta temporariamente bloqueada por excesso de tentativas. Aguarde 15 minutos.", 429
            )

        token_data = self._gw.sign_in_password(montar_email_sintetico(usuario), senha)
        if not token_data:
            self._registrar_falha_login(perfil, usuario, ip)
            raise AuthError(GENERIC_AUTH_ERROR, 401)

        if not perfil:
            user_id = (token_data.get("user") or {}).get("id")
            if user_id:
                perfil = self._gw.get_perfil_by_id(str(user_id))
        if not perfil or not perfil.get("ativo"):
            raise AuthError("Conta inativa ou sem perfil corporativo.", 403)

        if int(perfil.get("tentativas_falhas") or 0) > 0 or perfil.get("bloqueado_ate"):
            self._despachar(defer, self._gw.update_perfil_lockout, perfil["id"], 0, None)

        self._despachar(
            defer,
            self._gw.insert_audit_log,
            ator_id=perfil["id"],
            acao="LOGIN_SUCESSO",
            alvo=usuario,
            ip=ip,
            detalhes={"client_type": client_type},
        )
        return SessaoAutenticada(
            perfil=serializar_perfil_publico(perfil),
            access_token=str(token_data.get("access_token") or ""),
            refresh_token=str(token_data.get("refresh_token") or ""),
        )

    def _registrar_falha_login(
        self,
        perfil: Optional[Dict[str, Any]],
        usuario: str,
        ip: str,
    ) -> None:
        if not perfil:
            self._gw.insert_audit_log(
                ator_id=None,
                acao="LOGIN_FALHA_USUARIO_INEXISTENTE",
                alvo=usuario,
                ip=ip,
            )
            return
        atuais = int(perfil.get("tentativas_falhas") or 0)
        novas, bloqueado_ate, bloqueou_agora = calcular_estado_pos_falha_login(atuais)
        self._gw.update_perfil_lockout(perfil["id"], novas, bloqueado_ate)
        self._gw.insert_audit_log(
            ator_id=perfil["id"],
            acao="LOGIN_LOCKOUT" if bloqueou_agora else "LOGIN_FALHA",
            alvo=usuario,
            ip=ip,
            detalhes={"tentativas_falhas": novas},
        )
        if bloqueou_agora:
            raise AuthError("Conta bloqueada por 15 minutos após 5 tentativas inválidas.", 429)

    def refresh(
        self,
        refresh_token: Optional[str],
        ip: str,
        defer: Optional[Callable[..., None]] = None,
    ) -> SessaoAutenticada:
        """Rotaciona a sessão a partir do refresh token, revalidando perfil ativo e lockout."""
        if not refresh_token:
            raise AuthError("Sessão expirada. Faça login novamente.", 401)
        token_data = self._gw.refresh_session(refresh_token)
        if not token_data:
            raise AuthError("Sessão expirada. Faça login novamente.", 401)
        user_id = (token_data.get("user") or {}).get("id")
        perfil = self._gw.get_perfil_by_id(str(user_id)) if user_id else None
        if not perfil or not perfil.get("ativo") or esta_conta_bloqueada(perfil.get("bloqueado_ate")):
            raise AuthError("Conta inativa ou sem perfil corporativo.", 403)
        self._despachar(
            defer,
            self._gw.insert_audit_log,
            ator_id=perfil["id"],
            acao="SESSAO_RENOVADA",
            alvo=perfil["usuario"],
            ip=ip,
        )
        return SessaoAutenticada(
            perfil=serializar_perfil_publico(perfil),
            access_token=str(token_data.get("access_token") or ""),
            refresh_token=str(token_data.get("refresh_token") or ""),
        )

    def resolver_perfil_por_token(self, access_token: str) -> Dict[str, Any]:
        user_id = self._gw.get_user_id_from_token(access_token)
        if not user_id:
            raise AuthError("Sessão inválida ou expirada.", 401)
        perfil = self._gw.get_perfil_by_id(user_id)
        if not perfil or not perfil.get("ativo"):
            raise AuthError("Conta inativa ou sem perfil corporativo.", 403)
        return perfil

    # ------------------------------------------------------------------ #
    # Solicitação e aprovação individual
    # ------------------------------------------------------------------ #
    def solicitar_acesso(self, nome_completo: str, usuario_raw: str, role_solicitado: str, senha: str, ip: str) -> str:
        if role_solicitado not in ("analista", "coordenador"):
            raise AuthError("Perfil solicitado inválido.", 422)
        nome = self._validar_nome(nome_completo)
        usuario = self._validar_usuario_cadastro(usuario_raw)
        self._validar_senha(senha, role_solicitado)

        if self._gw.get_perfil_by_usuario(usuario):
            raise AuthError("Este nome de usuário já está em uso.", 409)
        existente = self._gw.get_solicitacao_by_usuario(usuario)
        if existente and existente.get("status") in ("pendente", "aprovada"):
            raise AuthError("Já existe uma solicitação ativa para este usuário.", 409)

        cifrada = criptografar_senha_temporaria(senha, self._gw.get_temp_crypto_secret())
        criada = self._gw.insert_solicitacao(
            usuario=usuario, nome_completo=nome, role_solicitado=role_solicitado, senha_hash_temp=cifrada
        )
        self._gw.insert_audit_log(
            ator_id=None,
            acao="SOLICITACAO_ACESSO_CRIADA",
            alvo=usuario,
            ip=ip,
            detalhes={"role_solicitado": role_solicitado},
        )
        return str(criada.get("id"))

    def listar_solicitacoes(self, caller: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not pode_aprovar_acessos(caller["role"]):
            raise AuthError("Apenas ADM ou Coordenador podem visualizar solicitações.", 403)
        return self._gw.list_solicitacoes_pendentes()

    def decidir_solicitacao(
        self,
        caller: Dict[str, Any],
        solicitacao_id: str,
        decisao: str,
        senha_confirmacao: Optional[str],
        ip: str,
    ) -> str:
        if not pode_aprovar_acessos(caller["role"]):
            raise AuthError("Apenas ADM ou Coordenador podem decidir solicitações.", 403)
        if caller["role"] == "adm":
            if not senha_confirmacao:
                raise AuthError(
                    "Contas ADM exigem reconfirmação de senha para aprovar ou rejeitar acessos.", 403
                )
            self.reconfirmar_senha_adm(caller, senha_confirmacao, solicitacao_id, ip)

        sol = self._gw.get_solicitacao_by_id(solicitacao_id)
        if not sol:
            raise AuthError("Solicitação não encontrada.", 404)
        if sol.get("status") != "pendente":
            raise AuthError("Esta solicitação já foi decidida.", 409)
        role_solicitado = str(sol["role_solicitado"])
        if role_solicitado not in ("analista", "coordenador"):
            raise AuthError("Perfil solicitado inválido.", 403)

        if decisao == "aprovada":
            try:
                senha_plana = descriptografar_senha_temporaria(
                    str(sol["senha_hash_temp"]), self._gw.get_temp_crypto_secret()
                )
            except ValueError as exc:
                raise AuthError(str(exc), 400)
            novo_uid = self._gw.admin_create_user(montar_email_sintetico(str(sol["usuario"])), senha_plana)
            self._gw.insert_perfil(
                user_id=novo_uid,
                usuario=str(sol["usuario"]),
                nome_completo=str(sol["nome_completo"]),
                role=role_solicitado,
            )

        self._gw.finalize_solicitacao(sol_id=solicitacao_id, status=decisao, decidido_por=str(caller["id"]))
        self._gw.insert_audit_log(
            ator_id=str(caller["id"]),
            acao="SOLICITACAO_APROVADA" if decisao == "aprovada" else "SOLICITACAO_REJEITADA",
            alvo=str(sol["usuario"]),
            ip=ip,
            detalhes={"solicitacao_id": solicitacao_id, "role": role_solicitado},
        )
        return decisao

    # ------------------------------------------------------------------ #
    # Gestão exclusiva ADM
    # ------------------------------------------------------------------ #
    def reconfirmar_senha_adm(self, adm: Dict[str, Any], senha_confirmacao: str, alvo: str, ip: str) -> None:
        if not self._gw.sign_in_password(montar_email_sintetico(str(adm["usuario"])), senha_confirmacao):
            self._gw.insert_audit_log(
                ator_id=str(adm["id"]), acao="ADM_RECONFIRMACAO_SENHA_FALHA", alvo=alvo, ip=ip
            )
            raise AuthError("Senha de confirmação do ADM incorreta.", 401)

    def _obter_alvo_nao_adm(self, user_id: str) -> Dict[str, Any]:
        alvo = self._gw.get_perfil_by_id(user_id)
        if not alvo:
            raise AuthError("Usuário não encontrado.", 404)
        if alvo.get("role") == "adm":
            raise AuthError("Contas ADM não podem ser alteradas ou excluídas por esta rota.", 403)
        return alvo

    def listar_usuarios(self) -> List[Dict[str, Any]]:
        return self._gw.list_perfis_gerenciaveis()

    def criar_usuario(
        self, adm: Dict[str, Any], nome_completo: str, usuario_raw: str, role: str, senha: str,
        senha_confirmacao: str, ip: str,
    ) -> Dict[str, Any]:
        nome = self._validar_nome(nome_completo)
        usuario = self._validar_usuario_cadastro(usuario_raw)
        self._validar_senha(senha, role)
        self.reconfirmar_senha_adm(adm, senha_confirmacao, usuario, ip)
        if self._gw.get_perfil_by_usuario(usuario):
            raise AuthError("Este nome de usuário já está em uso.", 409)

        novo_uid = self._gw.admin_create_user(montar_email_sintetico(usuario), senha)
        perfil = self._gw.insert_perfil(user_id=novo_uid, usuario=usuario, nome_completo=nome, role=role)
        self._gw.insert_audit_log(
            ator_id=str(adm["id"]), acao="ADM_CRIAR_USUARIO", alvo=usuario, ip=ip, detalhes={"role": role}
        )
        return serializar_perfil_publico(perfil)

    def atualizar_usuario(
        self, adm: Dict[str, Any], user_id: str, nome_completo: str, role: str, ativo: bool,
        nova_senha: Optional[str], senha_confirmacao: str, ip: str,
    ) -> Dict[str, Any]:
        nome = self._validar_nome(nome_completo)
        if nova_senha:
            self._validar_senha(nova_senha, role)
        self.reconfirmar_senha_adm(adm, senha_confirmacao, user_id, ip)
        alvo = self._obter_alvo_nao_adm(user_id)

        atualizado = self._gw.update_perfil_admin(user_id, {"nome_completo": nome, "role": role, "ativo": ativo})
        if nova_senha:
            self._gw.admin_update_user_password(user_id, nova_senha)
            self._gw.update_perfil_lockout(user_id, 0, None)
        self._gw.insert_audit_log(
            ator_id=str(adm["id"]),
            acao="ADM_EDITAR_USUARIO",
            alvo=str(alvo["usuario"]),
            ip=ip,
            detalhes={"role": role, "ativo": ativo, "senha_alterada": bool(nova_senha)},
        )
        return serializar_perfil_publico({**alvo, **atualizado})

    def deletar_usuario(self, adm: Dict[str, Any], user_id: str, senha_confirmacao: str, ip: str) -> str:
        self.reconfirmar_senha_adm(adm, senha_confirmacao, user_id, ip)
        alvo = self._obter_alvo_nao_adm(user_id)
        self._gw.admin_delete_user(user_id)
        self._gw.insert_audit_log(
            ator_id=str(adm["id"]),
            acao="ADM_DELETAR_USUARIO",
            alvo=str(alvo["usuario"]),
            ip=ip,
            detalhes={"role_alvo": alvo["role"]},
        )
        return str(alvo["usuario"])

    def resetar_senha(
        self, adm: Dict[str, Any], user_id: str, nova_senha: str, senha_confirmacao: str, ip: str
    ) -> str:
        self.reconfirmar_senha_adm(adm, senha_confirmacao, user_id, ip)
        alvo = self._obter_alvo_nao_adm(user_id)
        self._validar_senha(nova_senha, str(alvo["role"]))
        self._gw.admin_update_user_password(user_id, nova_senha)
        self._gw.update_perfil_lockout(user_id, 0, None)
        self._gw.insert_audit_log(
            ator_id=str(adm["id"]),
            acao="ADM_RESET_SENHA_USUARIO",
            alvo=str(alvo["usuario"]),
            ip=ip,
            detalhes={"role_alvo": alvo["role"]},
        )
        return str(alvo["usuario"])

    def desbloquear_usuario(self, adm: Dict[str, Any], user_id: str, senha_confirmacao: str, ip: str) -> str:
        """Remove o lockout de 15 min antes do prazo (somente contas não-ADM)."""
        self.reconfirmar_senha_adm(adm, senha_confirmacao, user_id, ip)
        alvo = self._obter_alvo_nao_adm(user_id)
        self._gw.update_perfil_lockout(user_id, 0, None)
        self._gw.insert_audit_log(
            ator_id=str(adm["id"]),
            acao="ADM_DESBLOQUEAR_USUARIO",
            alvo=str(alvo["usuario"]),
            ip=ip,
            detalhes={"role_alvo": alvo["role"]},
        )
        return str(alvo["usuario"])

    def listar_audit_logs(self, limit: int = 100) -> List[Dict[str, Any]]:
        limite = max(1, min(int(limit), MAX_AUDIT_LOGS))
        return self._gw.list_audit_logs(limit=limite)
