import {
  LoginPayload,
  PerfilUsuario,
  SolicitarAcessoPayload,
} from "../types/auth.types";

/**
 * Resolve e valida a base da API contra request/URL injection.
 * Aceita apenas caminho relativo ("") ou origem http(s) sem credenciais, query ou hash.
 */
function resolverBaseUrlSegura(raw?: string): string {
  const valor = (raw || "").trim();
  if (!valor) return "";
  try {
    const parsed = new URL(valor);
    if (parsed.protocol !== "http:" && parsed.protocol !== "https:") {
      return "";
    }
    if (parsed.username || parsed.password || parsed.search || parsed.hash) {
      return "";
    }
    return parsed.origin + parsed.pathname.replace(/\/+$/, "");
  } catch {
    return "";
  }
}

const API_BASE = resolverBaseUrlSegura(import.meta.env.VITE_API_URL);

const AUTH_ENDPOINTS = Object.freeze({
  login: `${API_BASE}/api/auth/login`,
  me: `${API_BASE}/api/auth/me`,
  refresh: `${API_BASE}/api/auth/refresh`,
  logout: `${API_BASE}/api/auth/logout`,
  solicitarAcesso: `${API_BASE}/api/auth/solicitar-acesso`,
});

export class AuthApiError extends Error {
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function parseErrorDetail(res: Response, fallback: string): Promise<string> {
  const body = await res.json().catch(() => null);
  if (body && typeof body.detail === "string" && body.detail.trim()) {
    return body.detail;
  }
  return fallback;
}

async function authFetch(
  url: string,
  init: RequestInit = {}
): Promise<Response> {
  return fetch(url, {
    ...init,
    credentials: "include",
    cache: "no-store",
    redirect: "error",
    headers: {
      "Content-Type": "application/json",
      "X-Requested-With": "XMLHttpRequest",
      ...(init.headers || {}),
    },
  });
}

export async function loginWebApi(payload: LoginPayload): Promise<PerfilUsuario> {
  const res = await authFetch(AUTH_ENDPOINTS.login, {
    method: "POST",
    body: JSON.stringify({
      usuario: payload.usuario,
      senha: payload.senha,
      client_type: "web",
    }),
  });
  if (!res.ok) {
    throw new AuthApiError(
      await parseErrorDetail(res, "Não foi possível autenticar."),
      res.status
    );
  }
  const data = (await res.json()) as { perfil: PerfilUsuario };
  return data.perfil;
}

export async function fetchCurrentUserApi(): Promise<PerfilUsuario | null> {
  const res = await authFetch(AUTH_ENDPOINTS.me, { method: "GET" });
  if (res.status === 401 || res.status === 403) {
    return null;
  }
  if (!res.ok) {
    throw new AuthApiError(
      await parseErrorDetail(res, "Falha ao verificar sessão."),
      res.status
    );
  }
  const data = (await res.json()) as { perfil: PerfilUsuario };
  return data.perfil;
}

export async function refreshSessionWebApi(): Promise<PerfilUsuario | null> {
  const res = await authFetch(AUTH_ENDPOINTS.refresh, { method: "POST" });
  if (!res.ok) {
    return null;
  }
  const data = (await res.json()) as { perfil: PerfilUsuario };
  return data.perfil;
}

export async function logoutWebApi(): Promise<void> {
  await authFetch(AUTH_ENDPOINTS.logout, { method: "POST" }).catch(() => {});
}

export async function solicitarAcessoApi(
  payload: SolicitarAcessoPayload
): Promise<{ id: string }> {
  const res = await authFetch(AUTH_ENDPOINTS.solicitarAcesso, {
    method: "POST",
    body: JSON.stringify({
      nome_completo: payload.nome_completo,
      usuario: payload.usuario,
      role_solicitado: payload.role_solicitado,
      senha: payload.senha,
    }),
  });
  if (!res.ok) {
    throw new AuthApiError(
      await parseErrorDetail(res, "Não foi possível enviar a solicitação."),
      res.status
    );
  }
  return (await res.json()) as { id: string };
}
