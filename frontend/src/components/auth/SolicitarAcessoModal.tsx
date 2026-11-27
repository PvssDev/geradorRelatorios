import React, { useState } from "react";
import { Loader2, Lock, ShieldCheck, User, UserPlus, X } from "lucide-react";
import { toast } from "sonner";
import { AuthApiError, solicitarAcessoApi } from "../../services/authApi";
import { RequestableRole } from "../../types/auth.types";

interface SolicitarAcessoModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SolicitarAcessoModal: React.FC<SolicitarAcessoModalProps> = ({
  isOpen,
  onClose,
}) => {
  const [nomeCompleto, setNomeCompleto] = useState("");
  const [usuario, setUsuario] = useState("");
  const [roleSolicitado, setRoleSolicitado] =
    useState<RequestableRole>("analista");
  const [senha, setSenha] = useState("");
  const [submitting, setSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleClose = () => {
    if (submitting) return;
    onClose();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting) return;
    setSubmitting(true);

    try {
      await solicitarAcessoApi({
        nome_completo: nomeCompleto,
        usuario,
        role_solicitado: roleSolicitado,
        senha,
      });
      toast.success("Solicitação enviada", {
        description:
          "Seu acesso aguarda aprovação de um Coordenador ou Administrador.",
      });
      setNomeCompleto("");
      setUsuario("");
      setRoleSolicitado("analista");
      setSenha("");
      onClose();
    } catch (err) {
      const msg =
        err instanceof AuthApiError || err instanceof Error
          ? err.message
          : "Erro ao enviar solicitação.";
      toast.error("Não foi possível solicitar acesso", { description: msg });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/55 p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="solicitar-acesso-title"
    >
      <div className="w-full max-w-md rounded-3xl bg-white p-6 shadow-2xl border border-slate-200">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
              Cadastro Institucional ARPE
            </p>
            <h2
              id="solicitar-acesso-title"
              className="mt-0.5 text-lg font-extrabold text-[#071d36]"
            >
              Solicitar Acesso
            </h2>
          </div>
          <button
            type="button"
            onClick={handleClose}
            disabled={submitting}
            className="grid h-9 w-9 place-items-center rounded-full bg-slate-100 text-slate-500 hover:bg-slate-200 transition"
            aria-label="Fechar modal"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="mt-5 space-y-4">
          <div>
            <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1.5">
              Nome completo
            </label>
            <input
              type="text"
              required
              minLength={3}
              maxLength={120}
              value={nomeCompleto}
              onChange={(e) => setNomeCompleto(e.target.value)}
              placeholder="Ex.: Maria Silva"
              className="w-full rounded-xl border border-slate-300 bg-slate-50 px-3.5 py-2.5 text-sm text-slate-900 outline-none focus:border-[#071d36] focus:bg-white transition"
            />
          </div>

          <div>
            <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1.5">
              Usuário institucional
            </label>
            <div className="relative">
              <User className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <input
                type="text"
                required
                minLength={3}
                maxLength={32}
                autoCapitalize="none"
                autoCorrect="off"
                value={usuario}
                onChange={(e) => setUsuario(e.target.value)}
                placeholder="Ex.: maria.silva"
                className="w-full rounded-xl border border-slate-300 bg-slate-50 pl-10 pr-3.5 py-2.5 text-sm text-slate-900 outline-none focus:border-[#071d36] focus:bg-white transition"
              />
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1.5">
              Perfil solicitado
            </label>
            <div className="grid grid-cols-2 gap-2.5">
              {(
                [
                  { value: "analista", label: "Analista" },
                  { value: "coordenador", label: "Coordenador" },
                ] as const
              ).map((op) => {
                const active = roleSolicitado === op.value;
                return (
                  <button
                    key={op.value}
                    type="button"
                    onClick={() => setRoleSolicitado(op.value)}
                    className={`flex items-center justify-center gap-2 rounded-xl border px-3 py-2.5 text-xs font-bold transition ${
                      active
                        ? "border-[#071d36] bg-[#071d36] text-white shadow-sm"
                        : "border-slate-300 bg-slate-50 text-slate-700 hover:bg-slate-100"
                    }`}
                  >
                    <ShieldCheck className="h-3.5 w-3.5" />
                    {op.label}
                  </button>
                );
              })}
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1.5">
              Senha (mín. 10 caracteres)
            </label>
            <div className="relative">
              <Lock className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <input
                type="password"
                required
                minLength={10}
                maxLength={128}
                value={senha}
                onChange={(e) => setSenha(e.target.value)}
                placeholder="Letras maiúsculas, minúsculas e números"
                className="w-full rounded-xl border border-slate-300 bg-slate-50 pl-10 pr-3.5 py-2.5 text-sm text-slate-900 outline-none focus:border-[#071d36] focus:bg-white transition"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-[#071d36] px-4 py-3 text-sm font-bold text-white shadow-md hover:bg-[#0c2b4d] disabled:opacity-60 transition"
          >
            {submitting ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <UserPlus className="h-4 w-4" />
            )}
            {submitting ? "Enviando..." : "Enviar solicitação"}
          </button>
        </form>
      </div>
    </div>
  );
};
