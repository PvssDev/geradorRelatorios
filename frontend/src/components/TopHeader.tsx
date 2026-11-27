import React, { useEffect, useRef, useState } from "react";
import {
  ChevronDown,
  FolderOpen,
  HardDrive,
  Menu,
  RefreshCw,
  Rows3,
  Save,
  Wand2,
  Zap,
} from "lucide-react";
import { toast } from "sonner";
import { useReportStore } from "../store/useReportStore";
import { CategoriaRelatorio, TipoRelatorio } from "../types/report.types";
import { getConcessionTheme } from "../utils/concessionTheme";
import { useSmartHeader } from "../hooks/useSmartHeader";
import { useClickOutside } from "../hooks/useClickOutside";
import {
  carregarEstadoDeGeradorBD,
  PastaNaoEncontradaError,
  salvarEstadoEmGeradorBD,
  solicitarPastaGeradorBD,
  verificarStatusConexaoPasta,
} from "../services/localDirectoryStorage";
import { PastaGeradorBDModal } from "./modals/PastaGeradorBDModal";
import logoIcone from "../assets/logo/logo_icone.png";

interface TopHeaderProps {
  onToggleMobileMenu: () => void;
  dense: boolean;
  onToggleDense: (d: boolean) => void;
  performanceMode: boolean;
  onTogglePerformanceMode: (p: boolean) => void;
}

function Segmented<T extends string>({
  label,
  options,
  value,
  onChange,
  activeColor,
}: {
  label: string;
  options: T[];
  value: T;
  onChange: (v: T) => void;
  activeColor?: string;
}) {
  const containerRef = React.useRef<HTMLDivElement>(null);
  const buttonRefs = React.useRef<(HTMLButtonElement | null)[]>([]);
  const [sliderStyle, setSliderStyle] = React.useState<{
    left: number;
    width: number;
    ready: boolean;
  }>({
    left: 0,
    width: 0,
    ready: false,
  });

  const updateSlider = React.useCallback(() => {
    const activeIndex = options.indexOf(value);
    const activeBtn = buttonRefs.current[activeIndex];
    if (activeBtn) {
      setSliderStyle({
        left: activeBtn.offsetLeft,
        width: activeBtn.offsetWidth,
        ready: true,
      });
    }
  }, [value, options]);

  React.useEffect(() => {
    updateSlider();
    window.addEventListener("resize", updateSlider);
    return () => window.removeEventListener("resize", updateSlider);
  }, [updateSlider]);

  return (
    <div className="flex items-center gap-2 rounded-full border border-[#d6e5f5] bg-[#edf4fb] p-1 pl-3.5 shadow-xs">
      <span className="text-[10px] font-bold uppercase tracking-[0.16em] text-[#1e3a5a]">
        {label}
      </span>
      <div
        ref={containerRef}
        className="relative flex items-center rounded-full bg-white/70 p-0.5 border border-[#d6e5f5]"
      >
        {sliderStyle.ready && (
          <div
            className="absolute top-0.5 bottom-0.5 rounded-full shadow-sm transition-all duration-300 ease-[cubic-bezier(0.25,1,0.5,1)]"
            style={{
              left: `${sliderStyle.left}px`,
              width: `${sliderStyle.width}px`,
              backgroundColor: activeColor || "#2563eb",
            }}
          />
        )}
        {options.map((o, idx) => {
          const isAct = value === o;
          return (
            <button
              key={o}
              ref={(el) => (buttonRefs.current[idx] = el)}
              type="button"
              onClick={() => onChange(o)}
              className={`relative z-10 rounded-full px-3.5 py-1 text-xs font-bold transition-colors duration-200 ${isAct
                ? "text-white drop-shadow-xs"
                : "text-[#334e68] hover:text-[#071d36]"
                }`}
            >
              {o}
            </button>
          );
        })}
      </div>
    </div>
  );
}

export const TopHeader: React.FC<TopHeaderProps> = ({
  onToggleMobileMenu,
  dense,
  onToggleDense,
  performanceMode,
  onTogglePerformanceMode,
}) => {
  const { headerRef, offsetY, isAnimating, resetHeader } = useSmartHeader();
  const {
    tipoRelatorio,
    categoriaRelatorio,
    setTipoRelatorio,
    setCategoriaRelatorio,
    getActiveWorkspace,
    executarAutoPreenchimento,
    importarEstadoModalidade,
    pastaLocalConectada,
    nomePastaLocal,
    setPastaLocalStatus,
  } = useReportStore();
  const ws = getActiveWorkspace();

  const [storageOpen, setStorageOpen] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [showFolderModal, setShowFolderModal] = useState(false);
  const [modalErrorMessage, setModalErrorMessage] = useState("");
  const [lastPendingAction, setLastPendingAction] = useState<
    "salvar" | "carregar" | "trocar" | null
  >(null);

  const storageRef = useRef<HTMLDivElement>(null);
  useClickOutside(storageRef, () => setStorageOpen(false), storageOpen);

  useEffect(() => {
    verificarStatusConexaoPasta().then(({ conectado, nomePasta }) => {
      setPastaLocalStatus(conectado, nomePasta);
    });
  }, [setPastaLocalStatus]);

  const handleSalvar = async () => {
    if (isSaving || isLoading) return;
    setIsSaving(true);
    setLastPendingAction("salvar");
    try {
      const dirHandle = await solicitarPastaGeradorBD(false);
      const res = await salvarEstadoEmGeradorBD(
        dirHandle,
        tipoRelatorio,
        categoriaRelatorio,
        ws,
        useReportStore.getState().monitoringNewPhotoName
      );
      setPastaLocalStatus(true, dirHandle.name);
      const extras = [
        `${res.totalSessoes} relatório(s)`,
        `${res.totalFotos} fotos`,
        `${res.totalNcs} ocorrências`,
      ];
      if (res.totalArquivos > 0) extras.push(`${res.totalArquivos} anexo(s)`);
      toast.success(
        `Estado salvo com sucesso em ${dirHandle.name}! (${extras.join(", ")})`
      );
      setStorageOpen(false);
    } catch (err: any) {
      if (err.name === "AbortError") return;
      if (err instanceof PastaNaoEncontradaError) {
        setPastaLocalStatus(false);
        setModalErrorMessage(err.message);
        setShowFolderModal(true);
        return;
      }
      toast.error(`Falha ao salvar na pasta geradorBD: ${err.message || err}`);
      verificarStatusConexaoPasta().then(({ conectado, nomePasta }) => {
        setPastaLocalStatus(conectado, nomePasta);
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleCarregar = async () => {
    if (isSaving || isLoading) return;
    setIsLoading(true);
    setLastPendingAction("carregar");
    try {
      const dirHandle = await solicitarPastaGeradorBD(false);
      const dados = await carregarEstadoDeGeradorBD(
        dirHandle,
        tipoRelatorio,
        categoriaRelatorio
      );
      importarEstadoModalidade(tipoRelatorio, categoriaRelatorio, dados);
      setPastaLocalStatus(true, dirHandle.name);
      const extras = [];
      if (dados.photos.length > 0) extras.push(`${dados.photos.length} fotos`);
      if (dados.documentoAnteriorFile) extras.push("documento anterior");
      if (dados.planilhaElegibilidadeFile) extras.push("planilha");
      const det = extras.length > 0 ? ` (${extras.join(", ")})` : "";
      toast.success(`Dados de ${tipoRelatorio} carregados!${det}`);
      setStorageOpen(false);
    } catch (err: any) {
      if (err.name === "AbortError") return;
      if (err instanceof PastaNaoEncontradaError) {
        setPastaLocalStatus(false);
        setModalErrorMessage(err.message);
        setShowFolderModal(true);
        return;
      }
      toast.error(`Falha ao carregar: ${err.message || err}`);
      verificarStatusConexaoPasta().then(({ conectado, nomePasta }) => {
        setPastaLocalStatus(conectado, nomePasta);
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleTrocarPasta = async () => {
    setLastPendingAction("trocar");
    try {
      const dirHandle = await solicitarPastaGeradorBD(true);
      setPastaLocalStatus(true, dirHandle.name);
      toast.success(`Pasta '${dirHandle.name}' vinculada com sucesso!`);
    } catch (err: any) {
      if (err.name === "AbortError") return;
      if (err instanceof PastaNaoEncontradaError) {
        setPastaLocalStatus(false);
        setModalErrorMessage(err.message);
        setShowFolderModal(true);
        return;
      }
      toast.error(`Erro ao vincular pasta: ${err.message || err}`);
    }
  };

  const handleRetryPendingAction = () => {
    if (lastPendingAction === "salvar") void handleSalvar();
    else if (lastPendingAction === "carregar") void handleCarregar();
    else void handleTrocarPasta();
  };

  const handleDemo = () => {
    executarAutoPreenchimento();
    toast.success("Dados preenchidos automaticamente!");
  };

  const theme = getConcessionTheme(tipoRelatorio, categoriaRelatorio);
  const activePillColor = theme.primary;
  const tipos: TipoRelatorio[] = ["CRA", "CRC", "SOCICAM"];
  const categorias: CategoriaRelatorio[] = ["Fiscalização", "Monitoramento"];

  const kicker =
    tipoRelatorio === "SOCICAM"
      ? `CTR · ${categoriaRelatorio} de Terminais`
      : `CTR · ${categoriaRelatorio} Rodoviária`;

  return (
    <>
      <header
        ref={headerRef as React.RefObject<HTMLElement>}
        onClick={() => {
          if (offsetY > 0) {
            resetHeader();
          }
        }}
        style={{
          transform: `translate3d(0, -${offsetY}px, 0)`,
          willChange: "transform",
        }}
        className={`sticky top-0 z-30 border-b border-[#d8e5f2]/80 bg-white/95 shadow-[0_6px_18px_-6px_rgba(7,29,54,0.12)] before:absolute before:inset-x-0 before:-top-[500px] before:h-[500px] before:bg-white/95 pointer-events-auto ${isAnimating
          ? "transition-transform duration-300 ease-[cubic-bezier(0.16,1,0.3,1)]"
          : "transition-none"
          } ${offsetY > 0 ? "cursor-pointer" : ""}`}
      >
        <div className="mx-auto max-w-5xl px-6 py-3.5 space-y-3">
          {/* Linha 1: Identidade + Armazenamento Local (sem container) & Ações Rápidas */}
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <button
                type="button"
                aria-label="Abrir menu"
                className="lg:hidden grid h-10 w-10 place-items-center rounded-xl border border-[#d6e5f5] bg-[#edf4fb] text-[#1e3a5a]"
                onClick={onToggleMobileMenu}
              >
                <Menu className="h-5 w-5" />
              </button>

              <span className="grid h-11 w-11 shrink-0 place-items-center rounded-2xl bg-[#071d36] p-2 text-white shadow-card">
                <img
                  src={logoIcone}
                  alt="CTR"
                  className="h-full w-full object-contain brightness-0 invert"
                />
              </span>

              <div>
                <div
                  className="text-[11px] font-bold uppercase tracking-[0.22em] transition-colors duration-300"
                  style={{ color: theme.primary }}
                >
                  {kicker}
                </div>
                <h1 className="text-2xl font-extrabold leading-none tracking-tight text-[#071d36] sm:text-3xl">
                  Gerador de Relatórios
                </h1>
              </div>
            </div>

            {/* Ferramentas da aba Gerador: Armazenamento Local + Ações Rápidas */}
            <div className="flex flex-wrap items-center gap-3">
              {/* Armazenamento Local (solto, sem container em volta, abre opções abaixo) */}
              <div ref={storageRef} className="relative">
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    setStorageOpen((prev) => !prev);
                  }}
                  aria-expanded={storageOpen}
                  title={
                    pastaLocalConectada
                      ? `geradorBD conectado (${nomePastaLocal || "ativo"})`
                      : "Armazenamento Local (geradorBD)"
                  }
                  className="flex items-center gap-2 rounded-lg px-2 py-1.5 text-left text-[#071d36] hover:bg-[#edf4fb] transition"
                >
                  <span className="relative grid h-7 w-7 place-items-center text-[#1e3a5a]">
                    <HardDrive className="h-4 w-4" />
                    <span
                      className={`absolute top-0.5 right-0.5 h-2 w-2 rounded-full ${pastaLocalConectada
                        ? "bg-emerald-500 shadow-[0_0_5px_rgba(16,185,129,0.8)]"
                        : "bg-amber-500 shadow-[0_0_5px_rgba(245,158,11,0.8)]"
                        }`}
                    />
                  </span>
                  <div className="leading-tight">
                    <div className="text-xs font-bold text-[#071d36]">
                      Armazenamento Local
                    </div>
                    <div className="text-[10px] text-[#52606d]">
                      {pastaLocalConectada ? "geradorBD conectado" : "Não vinculado"}
                    </div>
                  </div>
                  <ChevronDown
                    className={`h-3.5 w-3.5 text-[#52606d] transition-transform duration-200 ${storageOpen ? "rotate-180 text-[#071d36]" : ""
                      }`}
                  />
                </button>

                {storageOpen && (
                  <div className="absolute right-0 top-full mt-2 w-52 rounded-2xl border border-[#d6e5f5] bg-white p-2 shadow-xl z-40 space-y-1">
                    {pastaLocalConectada && (
                      <button
                        type="button"
                        onClick={() => void handleTrocarPasta()}
                        disabled={isSaving || isLoading}
                        className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-xs font-semibold text-[#334e68] hover:bg-[#edf4fb] disabled:opacity-50 transition"
                      >
                        <RefreshCw className="h-3.5 w-3.5 text-[#52606d]" />
                        <span>Trocar pasta ({nomePastaLocal || "geradorBD"})</span>
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={() => void handleSalvar()}
                      disabled={isSaving || isLoading}
                      className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-xs font-bold text-[#071d36] hover:bg-[#edf4fb] disabled:opacity-50 transition"
                    >
                      <Save className="h-3.5 w-3.5 text-emerald-600" />
                      <span>{isSaving ? "Salvando..." : "Salvar"}</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => void handleCarregar()}
                      disabled={isSaving || isLoading}
                      className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-xs font-bold text-[#071d36] hover:bg-[#edf4fb] disabled:opacity-50 transition"
                    >
                      <FolderOpen className="h-3.5 w-3.5 text-[#0a274c]" />
                      <span>{isLoading ? "Lendo..." : "Carregar"}</span>
                    </button>
                  </div>
                )}
              </div>

              <div className="h-6 w-px bg-[#d8e5f2]" aria-hidden="true" />

              {/* Ações Rápidas: ícones que acendem quando ativados + Auto preenchimento */}
              <div className="flex items-center gap-1">
                <button
                  type="button"
                  onClick={() => onTogglePerformanceMode(!performanceMode)}
                  aria-pressed={performanceMode}
                  aria-label="Modo Desempenho"
                  title={
                    performanceMode
                      ? "Modo Desempenho ativado (clique para desativar)"
                      : "Ativar Modo Desempenho"
                  }
                  className="grid h-9 w-9 place-items-center rounded-lg transition-all duration-200 active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0a274c]/30"
                >
                  <Zap
                    className={`h-[18px] w-[18px] transition-all duration-200 ${
                      performanceMode
                        ? "fill-amber-400 text-amber-500 drop-shadow-[0_0_6px_rgba(245,158,11,0.55)]"
                        : "text-[#94a3b8] hover:text-[#475569]"
                    }`}
                  />
                </button>

                <button
                  type="button"
                  onClick={() => onToggleDense(!dense)}
                  aria-pressed={dense}
                  aria-label="Modo Compacto"
                  title={
                    dense
                      ? "Modo Compacto ativado (clique para desativar)"
                      : "Ativar Modo Compacto"
                  }
                  className="grid h-9 w-9 place-items-center rounded-lg transition-all duration-200 active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0a274c]/30"
                >
                  <Rows3
                    className={`h-[18px] w-[18px] transition-all duration-200 ${
                      dense
                        ? "text-sky-500 drop-shadow-[0_0_6px_rgba(14,165,233,0.45)]"
                        : "text-[#94a3b8] hover:text-[#475569]"
                    }`}
                  />
                </button>

                <button
                  type="button"
                  onClick={handleDemo}
                  aria-label="Auto preenchimento de dados de teste"
                  title="Auto preenchimento de dados de teste"
                  className="grid h-9 w-9 place-items-center rounded-lg text-[#94a3b8] transition-all duration-200 hover:text-amber-500 active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#0a274c]/30"
                >
                  <Wand2 className="h-[18px] w-[18px]" />
                </button>
              </div>
            </div>
          </div>

          {/* Linha 2: Escolha de Concessão e Tipo de Fiscalização (abaixo de Gerador de Relatórios) */}
          <div className="flex flex-wrap items-center justify-start gap-2.5 border-t border-[#e6eff8] pt-2.5">
            <Segmented
              label="Concessão"
              options={tipos}
              value={tipoRelatorio}
              onChange={setTipoRelatorio}
              activeColor={theme.primary}
            />
            <Segmented
              label="Tipo"
              options={categorias}
              value={categoriaRelatorio}
              onChange={setCategoriaRelatorio}
              activeColor={activePillColor}
            />
          </div>
        </div>
      </header>

      <PastaGeradorBDModal
        isOpen={showFolderModal}
        onClose={() => setShowFolderModal(false)}
        onSelectFolder={handleRetryPendingAction}
        errorMessage={modalErrorMessage}
      />
    </>
  );
};
