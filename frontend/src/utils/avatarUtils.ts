import { UserRole } from "../types/auth.types";

/**
 * Paleta e funções idênticas às de `geradorCampo/src/domain/rules/authRules.ts`
 * para que a cor de fundo e as iniciais do usuário no Web sejam idênticas às do APK.
 */
export const AVATAR_PALETTE = [
  "#1D4ED8",
  "#0E7490",
  "#047857",
  "#4338CA",
  "#B45309",
  "#9F1239",
  "#0F766E",
  "#6D28D9",
] as const;

const PREPOSICOES_NOME = new Set(["da", "de", "do", "das", "dos", "e"]);

export function normalizarUsuarioAvatar(raw: string): string {
  return (raw || "").trim().toLowerCase();
}

export function extrairIniciaisAvatar(
  nomeCompleto: string,
  fallbackUsuario?: string
): string {
  const tokens = (nomeCompleto || "")
    .trim()
    .split(/\s+/)
    .filter(Boolean);

  if (tokens.length === 0) {
    const fb = normalizarUsuarioAvatar(fallbackUsuario ?? "");
    return fb ? fb[0].toUpperCase() : "A";
  }

  if (tokens.length === 1) {
    return tokens[0][0].toUpperCase();
  }

  const relevantes = tokens.filter((t) => !PREPOSICOES_NOME.has(t.toLowerCase()));
  const base = relevantes.length >= 2 ? relevantes : tokens;
  const primeiro = base[0][0] ?? "";
  const ultimo = base[base.length - 1][0] ?? "";
  return `${primeiro}${ultimo}`.toUpperCase();
}

export function obterCorAvatar(identificador: string): string {
  const norm = normalizarUsuarioAvatar(identificador || "arpe");
  let hash = 5381;
  for (let i = 0; i < norm.length; i += 1) {
    hash = ((hash << 5) - hash + norm.charCodeAt(i)) | 0;
  }
  return AVATAR_PALETTE[Math.abs(hash) % AVATAR_PALETTE.length];
}

export function obterLabelPerfil(role: UserRole): string {
  if (role === "adm") return "Administrador (ADM)";
  if (role === "coordenador") return "Coordenador";
  return "Analista";
}
