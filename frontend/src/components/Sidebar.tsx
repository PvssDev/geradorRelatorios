import React, { useState, useEffect, useRef, useId } from "react";
import { motion } from "framer-motion";
import {
  CloudUpload,
  Building2,
  ImagePlus,
  BarChart3,
  Rocket,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  LogOut,
  UserCheck,
  FileText,
  ClipboardList,
  LayoutDashboard,
  Table2,
  AtSign,
  Shield,
  ShieldCheck,
  Briefcase,
  Settings,
} from "lucide-react";
import { toast } from "sonner";
import { useReportStore } from "../store/useReportStore";
import { useAuthStore } from "../store/useAuthStore";
import { UserAvatar } from "./auth/UserAvatar";
import { obterLabelPerfil } from "../utils/avatarUtils";
import { getConcessionTheme } from "../utils/concessionTheme";
import logoIcone from "../assets/logo/logo_icone.png";

export type SidebarTab = "relatorio" | "vistorias" | "painel" | "quadro";

interface SidebarProps {
  expanded: boolean;
  onToggleExpand: () => void;
  onNavigate?: () => void;
  performanceMode: boolean;
  activeTab: SidebarTab;
  onSelectTab: (tab: SidebarTab) => void;
}

const BASE_NAV_ITEMS = [
  { n: 1, label: "Dados Gerais", icon: Building2 },
  { n: 2, label: "Upload de Mídia", icon: CloudUpload },
  { n: 3, label: "Ocorrências", icon: ImagePlus },
  { n: 4, label: "Emissão", icon: Rocket },
];

const SOCICAM_MON_NAV_ITEMS = [
  { n: 1, label: "Dados Gerais", icon: Building2 },
  { n: 2, label: "Upload de Mídia", icon: CloudUpload },
  { n: 3, label: "Ocorrências", icon: ImagePlus },
  { n: 4, label: "Recomendação Geral", icon: BarChart3 },
  { n: 5, label: "Emissão", icon: Rocket },
];

export const Sidebar: React.FC<SidebarProps> = ({
  expanded,
  onToggleExpand,
  onNavigate,
  performanceMode,
  activeTab,
  onSelectTab,
}) => {
  const {
    tipoRelatorio,
    categoriaRelatorio,
    getActiveWorkspace,
  } = useReportStore();
  const perfil = useAuthStore((s) => s.perfil);
  const logout = useAuthStore((s) => s.logout);
  const ws = getActiveWorkspace();
  const theme = getConcessionTheme(tipoRelatorio, categoriaRelatorio);

  const [perfilOpen, setPerfilOpen] = useState(false);
  const relatorioOpen = activeTab === "relatorio";

  const totalFotos = ws.photos.length;

  const hasFiscalizacao = Boolean(
    ws.fiscalizacoes?.length &&
    ws.fiscalizacoes.some((f) => Boolean(f["ID da Fiscalização"]?.trim()))
  );
  const activeFiscId =
    ws.fiscalizacoes[ws.activeFiscalizacaoIndex]?.["ID da Fiscalização"]?.trim() || "";
  const canOpenRegistro =
    categoriaRelatorio === "Monitoramento"
      ? totalFotos > 0 && Boolean(ws.documentoAnteriorFile)
      : totalFotos > 0;
  const hasRegistros = Boolean(
    ws.registrosNc?.some(
      (r) => !activeFiscId || (r["ID da Fiscalização"] || "").trim() === activeFiscId
    )
  );
  const hasRelatorios = ws.relatoriosGerados.length > 0;

  const isSocicamMonitoramento =
    tipoRelatorio === "SOCICAM" && categoriaRelatorio === "Monitoramento";
  const navItems = isSocicamMonitoramento ? SOCICAM_MON_NAV_ITEMS : BASE_NAV_ITEMS;
  const totalSteps = navItems.length;

  // Maior etapa desbloqueada (1 a 4 ou 1 a 5), alinhada exatamente aos blocos de App.tsx
  let maxUnlockedStep = 1;
  if (hasFiscalizacao && canOpenRegistro && hasRegistros) maxUnlockedStep = totalSteps;
  else if (hasFiscalizacao && canOpenRegistro) maxUnlockedStep = 3;
  else if (hasFiscalizacao) maxUnlockedStep = 2;

  const [selectedStep, setSelectedStep] = useState<number>(maxUnlockedStep);
  const scrollLockUntilRef = useRef<number>(0);
  const navIndicatorId = useId();

  useEffect(() => {
    setSelectedStep(maxUnlockedStep);
  }, [maxUnlockedStep]);

  useEffect(() => {
    if (!expanded) {
      setPerfilOpen(false);
    }
  }, [expanded]);

  // Scroll-Spy bidirecional: acompanha a seção visível (#b1..#b4) ao rolar para cima ou para baixo
  useEffect(() => {
    let rafId = 0;

    const updateActiveStepOnScroll = () => {
      rafId = 0;
      if (Date.now() < scrollLockUntilRef.current) return;

      const atBottom =
        window.innerHeight + window.scrollY >=
        document.documentElement.scrollHeight - 40;
      if (atBottom) {
        setSelectedStep(maxUnlockedStep);
        return;
      }

      const threshold = window.innerHeight * 0.35;
      let active = 1;
      for (let n = 1; n <= maxUnlockedStep; n++) {
        const el = document.getElementById(`b${n}`);
        if (!el) continue;
        const rect = el.getBoundingClientRect();
        if (rect.top <= threshold) {
          active = n;
        }
      }
      setSelectedStep(active);
    };

    const handleScroll = () => {
      if (rafId) return;
      rafId = window.requestAnimationFrame(updateActiveStepOnScroll);
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => {
      window.removeEventListener("scroll", handleScroll);
      if (rafId) window.cancelAnimationFrame(rafId);
    };
  }, [maxUnlockedStep]);

  const focusRotaFechada = !expanded && relatorioOpen;

  return (
      <aside
        className={`no-scrollbar flex h-full shrink-0 flex-col justify-between overflow-x-hidden overflow-y-auto border-r border-white/10 bg-navy-gradient p-4 text-sidebar-foreground shadow-2xl select-none transition-[width] duration-300 ease-[cubic-bezier(0.22,1,0.36,1)] ${expanded ? "w-72" : focusRotaFechada ? "w-[92px]" : "w-[76px]"
          }`}
      >
        <div className="space-y-4">
          {/* 1. Topo: Marca ARPE (oculta quando recolhido; sem círculo em volta) + Recolher */}
          {expanded && (
            <div className="flex items-center justify-between">
              <button
                type="button"
                onClick={onToggleExpand}
                className="group flex min-w-0 items-center text-left transition hover:opacity-95"
                title="Recolher menu lateral"
                aria-label="Recolher menu lateral"
              >
                <img
                  src={logoIcone}
                  alt="ARPE"
                  className="h-9 w-9 shrink-0 object-contain"
                />

                <div className="ml-2.5 overflow-hidden whitespace-nowrap">
                  <div className="text-base font-extrabold tracking-wider text-white leading-none">
                    ARPE
                  </div>
                  <div className="mt-0.5 text-[9.5px] font-medium tracking-tight text-slate-300/80 leading-tight">
                    Agência de Regulação de PE
                  </div>
                </div>
              </button>

              <button
                type="button"
                onClick={onToggleExpand}
                title="Recolher menu lateral"
                aria-label="Recolher menu lateral"
                className="grid h-8 w-8 shrink-0 place-items-center rounded-xl bg-sidebar-accent text-sidebar-foreground/70 hover:bg-sidebar-primary hover:text-white transition"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
            </div>
          )}

          {/* 2. Perfil do Usuário (solto no fundo do menu, sem caixa/borda ao redor) */}
          {perfil && (
            <div className="w-full">
              {!expanded ? (
                <div className="flex justify-center">
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      onToggleExpand();
                      setPerfilOpen(true);
                    }}
                    title={`${perfil.nome_completo} (@${perfil.usuario})`}
                    aria-label="Abrir perfil do usuário"
                    className="rounded-full p-0.5 transition hover:scale-105"
                  >
                    <UserAvatar
                      nomeCompleto={perfil.nome_completo}
                      usuario={perfil.usuario}
                      size={40}
                      bordered
                    />
                  </button>
                </div>
              ) : (
                <div className="w-full">
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      setPerfilOpen((prev) => !prev);
                    }}
                    aria-expanded={perfilOpen}
                    className="flex w-full flex-col items-center px-2 py-2 text-center hover:opacity-95 transition"
                  >
                    <UserAvatar
                      nomeCompleto={perfil.nome_completo}
                      usuario={perfil.usuario}
                      size={50}
                      bordered
                    />
                    <div className="mt-2 flex items-center justify-center gap-1 max-w-full">
                      <span className="truncate text-xs font-bold text-white">
                        {perfil.nome_completo}
                      </span>
                      <ChevronDown
                        className={`h-3.5 w-3.5 shrink-0 text-white/65 transition-transform duration-200 ${perfilOpen ? "rotate-180 text-white" : ""
                          }`}
                      />
                    </div>
                  </button>

                  {/* Sanfona de informações e ações do perfil (mesmas opções do APK + Gestionamento) */}
                  <div
                    className={`grid transition-all duration-300 ease-in-out ${perfilOpen
                      ? "grid-rows-[1fr] opacity-100 px-2.5 pb-2.5"
                      : "grid-rows-[0fr] opacity-0 px-2.5 pb-0 pointer-events-none"
                      }`}
                  >
                    <div className="overflow-hidden">
                      <div className="border-t border-white/10 pt-2 space-y-1 text-left">
                        <div className="flex items-center gap-2.5 rounded-xl px-2.5 py-1.5 bg-white/[0.04]">
                          <AtSign className="h-3.5 w-3.5 shrink-0 text-white/60" />
                          <div className="min-w-0">
                            <div className="text-[9.5px] uppercase tracking-wider text-white/50">
                              Usuário corporativo
                            </div>
                            <div className="truncate text-[11px] font-semibold text-white">
                              @{perfil.usuario}
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center gap-2.5 rounded-xl px-2.5 py-1.5 bg-white/[0.04]">
                          <Shield className="h-3.5 w-3.5 shrink-0 text-white/60" />
                          <div className="min-w-0">
                            <div className="text-[9.5px] uppercase tracking-wider text-white/50">
                              Nível de acesso
                            </div>
                            <div className="truncate text-[11px] font-semibold text-white">
                              {obterLabelPerfil(perfil.role)}
                            </div>
                          </div>
                        </div>

                        {perfil.role === "adm" && (
                          <button
                            type="button"
                            onClick={() =>
                              toast.info("Painel ADM", {
                                description: "Disponível na próxima etapa da aba Painel.",
                              })
                            }
                            className="flex w-full items-center gap-2.5 rounded-xl px-2.5 py-2 text-[11px] font-semibold text-white/90 hover:bg-white/10 transition"
                          >
                            <ShieldCheck className="h-3.5 w-3.5 shrink-0 text-amber-300" />
                            <span>Painel ADM</span>
                          </button>
                        )}

                        {(perfil.role === "adm" || perfil.role === "coordenador") && (
                          <button
                            type="button"
                            onClick={() =>
                              toast.info("Aprovações de Acesso", {
                                description: "Disponível na próxima etapa da aba Painel.",
                              })
                            }
                            className="flex w-full items-center gap-2.5 rounded-xl px-2.5 py-2 text-[11px] font-semibold text-white/90 hover:bg-white/10 transition"
                          >
                            <UserCheck className="h-3.5 w-3.5 shrink-0 text-sky-300" />
                            <span>Aprovações de Acesso</span>
                          </button>
                        )}

                        {(perfil.role === "coordenador" || perfil.role === "adm") && (
                          <button
                            type="button"
                            onClick={() =>
                              toast.info("Gestionamento", {
                                description: "Disponível na próxima etapa da aba Painel.",
                              })
                            }
                            className="flex w-full items-center gap-2.5 rounded-xl px-2.5 py-2 text-[11px] font-semibold text-white/90 hover:bg-white/10 transition"
                          >
                            <Briefcase className="h-3.5 w-3.5 shrink-0 text-emerald-300" />
                            <span>Gestionamento</span>
                          </button>
                        )}

                        <button
                          type="button"
                          onClick={() =>
                            toast.info("Configurações", {
                              description: "Preferências do perfil disponíveis em breve.",
                            })
                          }
                          className="flex w-full items-center gap-2.5 rounded-xl px-2.5 py-2 text-[11px] font-semibold text-white/90 hover:bg-white/10 transition"
                        >
                          <Settings className="h-3.5 w-3.5 shrink-0 text-white/75" />
                          <span>Configurações</span>
                        </button>

                        <button
                          type="button"
                          onClick={() => void logout()}
                          className="flex w-full items-center gap-2.5 rounded-xl px-2.5 py-2 text-[11px] font-bold text-red-300 hover:bg-red-500/20 hover:text-red-200 transition"
                        >
                          <LogOut className="h-3.5 w-3.5 shrink-0" />
                          <span>Logout</span>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* 3. Navegação Principal: Gerador (rotas sempre visíveis nesta aba, sem seta), Vistorias, Painel e Quadro */}
          <div className="border-t border-white/10 pt-3 space-y-1">
            {/* Botão Gerador */}
            <div>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  onSelectTab("relatorio");
                  if (onNavigate && expanded) onNavigate();
                }}
                title="Gerador"
                className={`flex w-full items-center rounded-xl text-xs font-bold transition-all duration-300 ease-out ${focusRotaFechada
                  ? "opacity-20 text-white/70"
                  : activeTab === "relatorio"
                    ? "bg-white/12 text-white"
                    : "text-white/80 hover:bg-white/10 hover:text-white"
                  }`}
              >
                <div className="grid h-11 w-11 shrink-0 place-items-center text-white">
                  <FileText className="h-4 w-4" />
                </div>
                <div
                  className={`flex flex-1 items-center overflow-hidden whitespace-nowrap transition-all duration-200 ${expanded
                    ? "pr-3 opacity-100"
                    : "max-w-0 opacity-0 pointer-events-none"
                    }`}
                >
                  <span>Gerador</span>
                </div>
              </button>

              {/* Rotas do Gerador (abertas enquanto activeTab === "relatorio", inclusive com menu fechado) */}
              <div
                className={`grid transition-all duration-300 ease-[cubic-bezier(0.22,1,0.36,1)] ${relatorioOpen
                  ? "grid-rows-[1fr] opacity-100 mt-1"
                  : "grid-rows-[0fr] opacity-0 pointer-events-none"
                  }`}
              >
                <div className="overflow-hidden">
                  <nav
                    className={`border-l border-white/15 transition-all duration-300 ease-[cubic-bezier(0.22,1,0.36,1)] ${expanded
                      ? "ml-5 pl-2 space-y-1"
                      : "ml-3.5 pl-2 space-y-1.5 py-0.5"
                      }`}
                  >
                    {navItems.map(({ n, label, icon: Icon }) => {
                      const unlocked = n <= maxUnlockedStep;
                      const cur = n === selectedStep;
                      const done = n < maxUnlockedStep || (n === totalSteps && hasRelatorios);
                      return (
                        <a
                          key={n}
                          href={unlocked ? `#b${n}` : undefined}
                          aria-disabled={!unlocked}
                          title={
                            !unlocked
                              ? `${n}. ${label} (complete a etapa anterior)`
                              : expanded
                                ? undefined
                                : `${n}. ${label}`
                          }
                          onClick={(e) => {
                            e.stopPropagation();
                            if (!unlocked) {
                              e.preventDefault();
                              return;
                            }
                            scrollLockUntilRef.current = Date.now() + 700;
                            setSelectedStep(n);
                            const target = document.getElementById(`b${n}`);
                            if (target) {
                              e.preventDefault();
                              target.scrollIntoView({ behavior: "smooth", block: "start" });
                            }
                            if (onNavigate) onNavigate();
                          }}
                          style={unlocked && done ? { color: theme.primary } : undefined}
                          className={`relative flex items-center text-xs font-medium transition-all duration-300 ease-out overflow-hidden rounded-lg ${focusRotaFechada ? "h-11" : "h-10"
                            } ${!unlocked
                              ? "cursor-not-allowed text-sidebar-foreground/30"
                              : cur
                                ? `${done ? "" : "text-white"} font-semibold`
                                : done
                                  ? "hover:opacity-90"
                                  : "text-white/80 hover:text-white"
                            }`}
                        >
                          {cur && (
                            <motion.span
                              layoutId={navIndicatorId}
                              transition={
                                performanceMode
                                  ? { duration: 0 }
                                  : { type: "spring", stiffness: 380, damping: 32 }
                              }
                              style={{ backgroundColor: theme.primary }}
                              className="absolute left-0 h-5 w-1 rounded-r-full transition-colors duration-200"
                            />
                          )}
                          <div
                            className={`relative grid shrink-0 place-items-center transition-all duration-300 ease-out ${focusRotaFechada ? "h-11 w-10 scale-115" : "h-10 w-8 scale-100"
                              }`}
                          >
                            <Icon
                              style={unlocked && done ? { color: theme.primary } : undefined}
                              className={`transition-all duration-300 ease-out ${focusRotaFechada ? "h-[18px] w-[18px]" : "h-4 w-4"
                                } ${!unlocked
                                  ? "text-sidebar-foreground/30"
                                  : done
                                    ? ""
                                    : cur
                                      ? "text-white"
                                      : "text-white/80"
                                }`}
                            />
                          </div>
                          {expanded && <span className="truncate pr-2">{label}</span>}
                        </a>
                      );
                    })}
                  </nav>
                </div>
              </div>
            </div>

            {/* Botões abaixo de Gerador: Vistorias, Painel e Quadro */}
            {(
              [
                { key: "vistorias", label: "Vistorias", icon: ClipboardList },
                { key: "painel", label: "Painel", icon: LayoutDashboard },
                { key: "quadro", label: "Quadro", icon: Table2 },
              ] as const
            ).map(({ key, label, icon: ItemIcon }) => {
              const isActive = activeTab === key;
              return (
                <button
                  key={key}
                  type="button"
                  title={label}
                  onClick={(e) => {
                    e.stopPropagation();
                    onSelectTab(key);
                    if (onNavigate) onNavigate();
                  }}
                  className={`flex w-full items-center rounded-xl text-xs font-semibold transition-all duration-300 ease-out ${focusRotaFechada
                    ? "opacity-20 text-white/70"
                    : isActive
                      ? "bg-white/15 text-white"
                      : "text-white/80 hover:bg-white/10 hover:text-white"
                    }`}
                >
                  <div className="grid h-11 w-11 shrink-0 place-items-center">
                    <ItemIcon className="h-4 w-4" />
                  </div>
                  <div
                    className={`overflow-hidden whitespace-nowrap transition-all duration-200 ${expanded
                      ? "pr-3 opacity-100"
                      : "max-w-0 opacity-0 pointer-events-none"
                      }`}
                  >
                    <span>{label}</span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* 4. Parte Inferior: Botão expandir quando recolhido */}
        {!expanded && (
          <div className="pt-4 flex flex-col items-center">
            <button
              type="button"
              onClick={onToggleExpand}
              title="Abrir menu completo"
              aria-label="Abrir menu completo"
              className="grid h-11 w-11 place-items-center rounded-2xl bg-white text-primary shadow-md hover:bg-secondary transition"
            >
              <ChevronRight className="h-5 w-5" />
            </button>
          </div>
        )}
      </aside>
  );
};
