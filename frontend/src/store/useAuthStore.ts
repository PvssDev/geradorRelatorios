import { create } from "zustand";
import {
  fetchCurrentUserApi,
  loginWebApi,
  logoutWebApi,
  refreshSessionWebApi,
} from "../services/authApi";
import { LoginPayload, PerfilUsuario } from "../types/auth.types";

interface AuthState {
  perfil: PerfilUsuario | null;
  checkingSession: boolean;
  submitting: boolean;
  erroAuth: string | null;

  bootstrapSession: () => Promise<void>;
  login: (payload: LoginPayload) => Promise<boolean>;
  logout: () => Promise<void>;
  limparErro: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  perfil: null,
  checkingSession: true,
  submitting: false,
  erroAuth: null,

  bootstrapSession: async () => {
    set({ checkingSession: true });
    try {
      const atual = await fetchCurrentUserApi();
      if (atual) {
        set({ perfil: atual, checkingSession: false, erroAuth: null });
        return;
      }
      const renovado = await refreshSessionWebApi();
      set({ perfil: renovado, checkingSession: false, erroAuth: null });
    } catch {
      set({ perfil: null, checkingSession: false });
    }
  },

  login: async (payload) => {
    set({ submitting: true, erroAuth: null });
    try {
      const perfil = await loginWebApi(payload);
      set({ perfil, submitting: false, erroAuth: null });
      return true;
    } catch (err) {
      const mensagem =
        err instanceof Error ? err.message : "Erro ao conectar ao servidor.";
      set({ submitting: false, erroAuth: mensagem });
      return false;
    }
  },

  logout: async () => {
    await logoutWebApi();
    set({ perfil: null, erroAuth: null });
  },

  limparErro: () => set({ erroAuth: null }),
}));
