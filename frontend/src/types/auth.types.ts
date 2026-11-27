export type UserRole = "adm" | "coordenador" | "analista";
export type RequestableRole = "analista" | "coordenador";

export interface PerfilUsuario {
  readonly id: string;
  readonly usuario: string;
  readonly nome_completo: string;
  readonly role: UserRole;
  readonly ativo: boolean;
}

export interface LoginPayload {
  readonly usuario: string;
  readonly senha: string;
}

export interface SolicitarAcessoPayload {
  readonly nome_completo: string;
  readonly usuario: string;
  readonly role_solicitado: RequestableRole;
  readonly senha: string;
}
