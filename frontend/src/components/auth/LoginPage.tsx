import React, { useState } from "react";
import { motion, useReducedMotion } from "framer-motion";
import {
  ArrowRight,
  Eye,
  EyeOff,
  Lightbulb,
  Loader2,
  Lock,
  User,
} from "lucide-react";
import { toast } from "sonner";
import logoInteira from "../../assets/logo/logo_inteira.png";
import checklistIcon from "../../assets/ref-icons/checklist.png";
import energiaIcon from "../../assets/ref-icons/energia.png";
import fibraIcon from "../../assets/ref-icons/fibra.png";
import fiscalizacaoIcon from "../../assets/ref-icons/fiscalizacao.png";
import rodoviaIcon from "../../assets/ref-icons/rodovia.png";
import saneamentoIcon from "../../assets/ref-icons/saneamento.png";
import terminalIcon from "../../assets/ref-icons/terminal.png";
import tubulacaoIcon from "../../assets/ref-icons/tubulacao.png";
import { useAuthStore } from "../../store/useAuthStore";
import { SolicitarAcessoModal } from "./SolicitarAcessoModal";

const EASE_OUT_EXPO = [0.22, 1, 0.36, 1] as const;
const EASE_OUT_LONG_TAIL = [0.06, 0.96, 0.14, 1] as const;

function calcularDerivaFlutuante(
  initialX: number,
  initialY: number,
  initialRotate: number,
  finalRotate: number,
  delay: number
) {
  // Continua suavemente o vetor do impulso inicial em micro-amplitude (gravidade zero)
  const dirX = initialX < 0 ? 3.5 : -3.5;
  const dirY = initialY > 0 ? -4 : 4;
  const dirRot = finalRotate >= initialRotate ? 1.6 : -1.6;
  const duration = 18.0 + (Math.round(delay * 100) % 7) * 1.2;

  return {
    animate: {
      x: [0, dirX, dirX * 0.3, -dirX * 0.5, 0],
      y: [0, dirY, -dirY * 0.2, -dirY * 0.6, 0],
      rotate: [0, dirRot, 0, -dirRot * 0.7, 0],
    },
    transition: {
      duration,
      delay: delay + 1.4,
      repeat: Infinity,
      ease: "easeInOut" as const,
    },
  };
}

interface IconeStickerProps {
  src: string;
  className: string;
  delay: number;
  initialX: number;
  initialY: number;
  initialRotate: number;
  finalRotate: number;
  reduceMotion: boolean | null;
}

const IconeSticker: React.FC<IconeStickerProps> = ({
  src,
  className,
  delay,
  initialX,
  initialY,
  initialRotate,
  finalRotate,
  reduceMotion,
}) => {
  const floatCfg = calcularDerivaFlutuante(
    initialX,
    initialY,
    initialRotate,
    finalRotate,
    delay
  );

  return (
    <motion.div
      aria-hidden="true"
      initial={
        reduceMotion
          ? false
          : {
            opacity: 0,
            x: initialX,
            y: initialY,
            scale: 0.78,
            rotate: initialRotate,
          }
      }
      animate={{
        opacity: 1,
        x: 0,
        y: 0,
        scale: 1,
        rotate: finalRotate,
      }}
      transition={{
        duration: 2.1,
        delay,
        ease: EASE_OUT_LONG_TAIL,
      }}
      className={`pointer-events-none absolute select-none ${className}`}
    >
      <motion.div
        animate={reduceMotion ? undefined : floatCfg.animate}
        transition={reduceMotion ? undefined : floatCfg.transition}
        className="relative h-full w-full"
      >
        <img
          src={src}
          alt=""
          style={{ filter: "url(#arpe-navy-cutout)" }}
          className="absolute inset-0 h-full w-full object-contain -translate-x-[2px] translate-y-[2px]"
        />
        <img
          src={src}
          alt=""
          className="relative h-full w-full object-contain opacity-95"
        />
      </motion.div>
    </motion.div>
  );
};

export const LoginPage: React.FC = () => {
  const reduceMotion = useReducedMotion();
  const login = useAuthStore((s) => s.login);
  const submitting = useAuthStore((s) => s.submitting);
  const erroAuth = useAuthStore((s) => s.erroAuth);
  const limparErro = useAuthStore((s) => s.limparErro);

  const [usuario, setUsuario] = useState("");
  const [senha, setSenha] = useState("");
  const [mostrarSenha, setMostrarSenha] = useState(false);
  const [solicitarOpen, setSolicitarOpen] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting) return;
    const ok = await login({ usuario, senha });
    if (ok) {
      toast.success("Sessão iniciada", {
        description: "Bem-vindo(a) ao Gerador de Relatórios ARPE.",
      });
      return;
    }
    const erro = useAuthStore.getState().erroAuth;
    if (erro) {
      toast.error("Acesso negado", { description: erro });
    }
  };

  const handleEsqueceuSenha = () => {
    toast.info("Redefinição de senha", {
      description:
        "Solicite a redefinição de senha diretamente ao Administrador (ADM) da ARPE.",
    });
  };

  return (
    <div className="min-h-screen w-full grid grid-cols-1 lg:grid-cols-2 bg-white">
      {/* Metade Esquerda — Identidade Visual ARPE + Faixas Diagonais + Ícones de Fiscalização */}
      <div className="relative hidden lg:block overflow-hidden bg-[#07213e] select-none">
        {/* Filtro SVG para pintar a dupla traseira dos ícones na cor exata do fundo (#07213e) */}
        <svg className="absolute h-0 w-0" aria-hidden="true">
          <defs>
            <filter id="arpe-navy-cutout">
              <feFlood floodColor="#07213e" result="navy" />
              <feComposite in="navy" in2="SourceAlpha" operator="in" />
            </filter>
          </defs>
        </svg>

        {/* Camada 1: Faixa Amarela — sai por último de dentro da Verde como leque */}
        <motion.svg
          viewBox="0 0 1000 1000"
          preserveAspectRatio="none"
          aria-hidden="true"
          style={{
            transformOrigin: "100% 100%",
            filter: "drop-shadow(0px -5px 12px rgba(4, 14, 28, 0.38))",
          }}
          initial={reduceMotion ? false : { rotate: -22, opacity: 0 }}
          animate={{ rotate: 0, opacity: 1 }}
          transition={{ duration: 1.55, delay: 0.45, ease: EASE_OUT_EXPO }}
          className="pointer-events-none absolute inset-0 z-[1] h-full w-full"
        >
          <polygon points="0,495 1000,1000 0,1300" fill="#fde047" />
        </motion.svg>

        {/* Camada 2: Ícones que emergem da Faixa Amarela / Verde e giram até o ângulo final */}
        <IconeSticker
          src={fibraIcon}
          className="z-[2] left-[-1%] top-[24%] w-24 h-24"
          delay={0.72}
          initialX={-36}
          initialY={140}
          initialRotate={-42}
          finalRotate={-12}
          reduceMotion={reduceMotion}
        />
        <IconeSticker
          src={tubulacaoIcon}
          className="z-[2] left-[1%] top-[36%] w-32 h-32"
          delay={0.84}
          initialX={-24}
          initialY={120}
          initialRotate={-20}
          finalRotate={12}
          reduceMotion={reduceMotion}
        />
        <motion.div
          aria-hidden="true"
          initial={
            reduceMotion
              ? false
              : { opacity: 0, x: -20, y: 95, scale: 0.78, rotate: -38 }
          }
          animate={{ opacity: 1, x: 0, y: 0, scale: 1, rotate: -12 }}
          transition={{ duration: 2.1, delay: 0.94, ease: EASE_OUT_LONG_TAIL }}
          className="pointer-events-none absolute z-[2] left-[4%] top-[56%]"
        >
          <motion.div
            animate={
              reduceMotion
                ? undefined
                : calcularDerivaFlutuante(-20, 95, -38, -12, 0.94).animate
            }
            transition={
              reduceMotion
                ? undefined
                : calcularDerivaFlutuante(-20, 95, -38, -12, 0.94).transition
            }
            className="relative"
          >
            <Lightbulb className="absolute inset-0 w-16 h-16 text-[#07213e] stroke-[3] -translate-x-[2px] translate-y-[2px]" />
            <Lightbulb className="relative w-16 h-16 text-white/95 stroke-[1.7]" />
          </motion.div>
        </motion.div>
        <IconeSticker
          src={energiaIcon}
          className="z-[2] left-[23%] top-[50%] w-28 h-28"
          delay={1.02}
          initialX={-28}
          initialY={105}
          initialRotate={18}
          finalRotate={-6}
          reduceMotion={reduceMotion}
        />
        <IconeSticker
          src={terminalIcon}
          className="z-[2] left-[45%] top-[62%] w-20 h-20"
          delay={1.12}
          initialX={-18}
          initialY={95}
          initialRotate={-24}
          finalRotate={0}
          reduceMotion={reduceMotion}
        />
        <IconeSticker
          src={fiscalizacaoIcon}
          className="z-[2] left-[80%] top-[85%] w-24 h-24"
          delay={1.26}
          initialX={-16}
          initialY={75}
          initialRotate={16}
          finalRotate={-6}
          reduceMotion={reduceMotion}
        />

        {/* Camada 3: Faixa Verde — sai de dentro da Vermelha como leque */}
        <motion.svg
          viewBox="0 0 1000 1000"
          preserveAspectRatio="none"
          aria-hidden="true"
          style={{
            transformOrigin: "100% 100%",
            filter: "drop-shadow(0px -5px 12px rgba(4, 14, 28, 0.32))",
          }}
          initial={reduceMotion ? false : { rotate: -16, opacity: 0 }}
          animate={{ rotate: 0, opacity: 1 }}
          transition={{ duration: 1.45, delay: 0.25, ease: EASE_OUT_EXPO }}
          className="pointer-events-none absolute inset-0 z-[3] h-full w-full"
        >
          <polygon points="0,585 1000,1000 0,1300" fill="#1ea84c" />
        </motion.svg>

        {/* Camada 4: Ícones que emergem da Faixa Vermelha e ficam por trás dela */}
        <IconeSticker
          src={checklistIcon}
          className="z-[4] left-[22%] top-[68%] w-16 h-16"
          delay={1.08}
          initialX={-22}
          initialY={85}
          initialRotate={22}
          finalRotate={-12}
          reduceMotion={reduceMotion}
        />
        <IconeSticker
          src={saneamentoIcon}
          className="z-[4] left-[36%] top-[76%] w-20 h-20"
          delay={1.16}
          initialX={-20}
          initialY={88}
          initialRotate={-26}
          finalRotate={-8}
          reduceMotion={reduceMotion}
        />
        <IconeSticker
          src={rodoviaIcon}
          className="z-[4] left-[52%] top-[76%] w-36 h-36"
          delay={1.2}
          initialX={-26}
          initialY={90}
          initialRotate={-36}
          finalRotate={-12}
          reduceMotion={reduceMotion}
        />

        {/* Camada 5: Faixa Vermelha — base do leque que abre primeiro */}
        <motion.svg
          viewBox="0 0 1000 1000"
          preserveAspectRatio="none"
          aria-hidden="true"
          style={{
            transformOrigin: "100% 100%",
            filter: "drop-shadow(0px -5px 12px rgba(4, 14, 28, 0.32))",
          }}
          initial={reduceMotion ? false : { rotate: -12, opacity: 0 }}
          animate={{ rotate: 0, opacity: 1 }}
          transition={{ duration: 1.35, delay: 0.08, ease: EASE_OUT_EXPO }}
          className="pointer-events-none absolute inset-0 z-[5] h-full w-full"
        >
          <polygon points="0,675 1000,1000 0,1300" fill="#f42f2c" />
        </motion.svg>
      </div>

      {/* Metade Direita — Formulário Clean */}
      <div className="flex flex-col justify-between px-6 py-6 sm:px-10 bg-white">
        <div className="w-full flex justify-start">
          <img
            src={logoInteira}
            alt="ARPE — Agência de Regulação de Pernambuco"
            className="h-9 w-auto object-contain"
          />
        </div>

        <motion.div
          initial={reduceMotion ? false : { opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, delay: 0.1, ease: EASE_OUT_EXPO }}
          className="w-full max-w-[400px] mx-auto my-auto py-10"
        >
          <h1 className="text-[30px] font-extrabold tracking-tight text-[#0f172a]">
            Bem-vindo
          </h1>
          <p className="mt-1.5 text-sm text-slate-500">
            Entre com suas credenciais para continuar.
          </p>

          <form onSubmit={handleSubmit} className="mt-7 space-y-5">
            <div>
              <label
                htmlFor="login-usuario"
                className="block text-[11px] font-semibold uppercase tracking-wider text-slate-500 mb-1.5"
              >
                USUÁRIO
              </label>
              <div className="relative">
                <User className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                <input
                  id="login-usuario"
                  type="text"
                  required
                  autoComplete="username"
                  autoCapitalize="none"
                  autoCorrect="off"
                  value={usuario}
                  onChange={(e) => {
                    if (erroAuth) limparErro();
                    setUsuario(e.target.value);
                  }}
                  placeholder="seu.usuario"
                  className="w-full rounded-xl border border-slate-200 bg-white pl-10 pr-3.5 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 outline-none focus:border-[#0a274c] focus:ring-2 focus:ring-[#0a274c]/10 transition"
                />
              </div>
            </div>

            <div>
              <label
                htmlFor="login-senha"
                className="block text-[11px] font-semibold uppercase tracking-wider text-slate-500 mb-1.5"
              >
                SENHA
              </label>
              <div className="relative">
                <Lock className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                <input
                  id="login-senha"
                  type={mostrarSenha ? "text" : "password"}
                  required
                  autoComplete="current-password"
                  value={senha}
                  onChange={(e) => {
                    if (erroAuth) limparErro();
                    setSenha(e.target.value);
                  }}
                  placeholder="••••••••"
                  className="w-full rounded-xl border border-slate-200 bg-white pl-10 pr-11 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 outline-none focus:border-[#0a274c] focus:ring-2 focus:ring-[#0a274c]/10 transition"
                />
                <button
                  type="button"
                  onClick={() => setMostrarSenha((v) => !v)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-700 transition"
                  aria-label={mostrarSenha ? "Ocultar senha" : "Mostrar senha"}
                >
                  {mostrarSenha ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
              <div className="mt-2 flex justify-end">
                <button
                  type="button"
                  onClick={handleEsqueceuSenha}
                  className="text-xs font-medium text-[#0a274c] hover:underline"
                >
                  Esqueceu a senha?
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-[#0a274c] px-4 py-3 text-sm font-bold text-white shadow-md hover:bg-[#071d36] disabled:opacity-60 transition"
            >
              {submitting ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : null}
              <span>{submitting ? "Autenticando..." : "Entrar"}</span>
              {!submitting && <ArrowRight className="h-4 w-4" />}
            </button>
          </form>

          <div className="mt-4 flex items-center justify-between gap-2 text-xs">
            <span className="text-slate-500">Não tem acesso?</span>
            <button
              type="button"
              onClick={() => setSolicitarOpen(true)}
              className="font-semibold text-[#0a274c] hover:underline"
            >
              Solicitar acesso
            </button>
          </div>
        </motion.div>

        <div className="w-full max-w-[400px] mx-auto pb-2 text-center">
          <span className="text-xs text-slate-400">© 2026 ARPE</span>
        </div>
      </div>

      <SolicitarAcessoModal
        isOpen={solicitarOpen}
        onClose={() => setSolicitarOpen(false)}
      />
    </div>
  );
};
