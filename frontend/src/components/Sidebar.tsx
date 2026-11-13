import React, { useState, useEffect } from "react";
import {
  CloudUpload,
  Building2,
  ImagePlus,
  Rocket,
  Wand2,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  MoreVertical,
  Save,
  FolderOpen,
  HardDrive,
  RefreshCw,
  Palette,
  Zap,
} from "lucide-react";
import { toast } from "sonner";
import { useReportStore } from "../store/useReportStore";
import {
  solicitarPastaGeradorBD,
  salvarEstadoEmGeradorBD,
  carregarEstadoDeGeradorBD,
  verificarStatusConexaoPasta,
  PastaNaoEncontradaError,
} from "../services/localDirectoryStorage";
import { PastaGeradorBDModal } from "./modals/PastaGeradorBDModal";
import logoIcone from "../assets/logo/logo_icone.png";

interface SidebarProps {
  expanded: boolean;
  onToggleExpand: () => void;
  onNavigate?: () => void;
  dense: boolean;
  onToggleDense: (d: boolean) => void;
  performanceMode: boolean;
  onTogglePerformanceMode: (p: boolean) => void;
}

const NAV_ITEMS = [
  { n: 1, label: "Dados Gerais", icon: Building2 },
  { n: 2, label: "Upload de Mídia", icon: CloudUpload },
  { n: 3, label: "Ocorrências", icon: ImagePlus },
  { n: 4, label: "Emissão", icon: Rocket },
];

export const Sidebar: React.FC<SidebarProps> = ({
  expanded,
  onToggleExpand,
  onNavigate,
  dense,
  onToggleDense,
  performanceMode,
  onTogglePerformanceMode,
}) => {
  const {
    tipoRelatorio,
    categoriaRelatorio,
    getActiveWorkspace,
    executarAutoPreenchimento,
    importarEstadoModalidade,
    pastaLocalConectada,
    nomePastaLocal,
    setPastaLocalStatus,
  } = useReportStore();
  const ws = getActiveWorkspace();

  const [isSaving, setIsSaving] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [showFolderModal, setShowFolderModal] = useState(false);
  const [modalErrorMessage, setModalErrorMessage] = useState("");
  const [lastPendingAction, setLastPendingAction] = useState<"salvar" | "carregar" | "trocar" | null>(null);
  const [storageOpen, setStorageOpen] = useState(false);

  const totalFotos = ws.photos.length;
  const ncsCount = ws.registrosNc.filter(
    (r) => (r["Não Conformidade"] || "").trim() !== ""
  ).length;
  const pasCount = ws.registrosNc.length - ncsCount;

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

  // Maior etapa desbloqueada (1 a 4), alinhada exatamente aos blocos #b1-#b4 de App.tsx
  let maxUnlockedStep = 1;
  if (hasFiscalizacao && canOpenRegistro && hasRegistros) maxUnlockedStep = 4;
  else if (hasFiscalizacao && canOpenRegistro) maxUnlockedStep = 3;
  else if (hasFiscalizacao) maxUnlockedStep = 2;

  const [selectedStep, setSelectedStep] = useState<number>(maxUnlockedStep);

  useEffect(() => {
    setSelectedStep(maxUnlockedStep);
  }, [maxUnlockedStep]);

  // Identificação automática da pasta geradorBD na entrada do site
  useEffect(() => {
    verificarStatusConexaoPasta().then(({ conectado, nomePasta }) => {
      setPastaLocalStatus(conectado, nomePasta);
    });
  }, [setPastaLocalStatus]);

  const handleDemo = () => {
    executarAutoPreenchimento();
    toast.success("Dados preenchidos automaticamente!");
    if (onNavigate) onNavigate();
  };

  /* ------------------------------------------------------------------------ */
  /* AÇÕES DE PERSISTÊNCIA LOCAL (PASTA geradorBD)                            */
  /* ------------------------------------------------------------------------ */
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
        ws
      );
      setPastaLocalStatus(true, dirHandle.name);
      const extras = [`${res.totalFotos} fotos`, `${res.totalNcs} ocorrências`];
      if (res.totalArquivos > 0) extras.push(`${res.totalArquivos} anexo(s)`);
      toast.success(
        `Estado salvo com sucesso em ${dirHandle.name}! (${extras.join(", ")})`
      );
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
      if (dados.documentoAnteriorFile) extras.push(`documento anterior`);
      if (dados.planilhaElegibilidadeFile) extras.push(`planilha`);
      const det = extras.length > 0 ? ` (${extras.join(", ")})` : "";
      toast.success(
        `Dados de ${tipoRelatorio} - ${categoriaRelatorio} carregados!${det}`
      );
      if (onNavigate) onNavigate();
    } catch (err: any) {
      if (err.name === "AbortError") return;
      if (err instanceof PastaNaoEncontradaError) {
        setPastaLocalStatus(false);
        setModalErrorMessage(err.message);
        setShowFolderModal(true);
        return;
      }
      toast.error(`Falha ao carregar de geradorBD: ${err.message || err}`);
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
      toast.success(`Pasta vinculada com sucesso: ${dirHandle.name}`);
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
    if (lastPendingAction === "salvar") {
      handleSalvar();
    } else if (lastPendingAction === "carregar") {
      handleCarregar();
    } else {
      handleTrocarPasta();
    }
  };

  return (
    <>
      <aside
        className={`flex h-full shrink-0 flex-col justify-between overflow-x-hidden overflow-y-auto border-r border-white/10 bg-navy-gradient p-4 text-sidebar-foreground shadow-2xl select-none transition-[width] duration-300 ease-out ${
          expanded ? "w-72" : "w-[76px]"
        }`}
      >
        <div className="space-y-4">
          {/* 1. Topo: Marca ARPE + Recolher */}
          <div className="flex items-center justify-between">
            <button
              type="button"
              onClick={onToggleExpand}
              className="group flex min-w-0 items-center text-left transition hover:opacity-95"
              title={expanded ? "Recolher menu lateral" : "Expandir menu lateral"}
              aria-label={expanded ? "Recolher menu lateral" : "Expandir menu lateral"}
            >
              <div className="relative grid h-11 w-11 shrink-0 place-items-center rounded-2xl bg-white/[0.06] p-1.5 ring-1 ring-white/10 transition group-hover:bg-white/10">
                <img
                  src={logoIcone}
                  alt="ARPE"
                  className="h-full w-full object-contain"
                />
              </div>

              <div
                className={`overflow-hidden whitespace-nowrap transition-all duration-200 ${
                  expanded
                    ? "ml-2.5 max-w-[165px] opacity-100"
                    : "ml-0 max-w-0 opacity-0 pointer-events-none"
                }`}
              >
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
              className={`grid h-8 shrink-0 place-items-center rounded-xl bg-sidebar-accent text-sidebar-foreground/70 hover:bg-sidebar-primary hover:text-white transition-all duration-200 overflow-hidden ${
                expanded ? "w-8 opacity-100" : "w-0 opacity-0 pointer-events-none"
              }`}
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
          </div>

          {/* 2. Identidade da Modalidade (visível apenas com o menu expandido) */}
          <div
            className={`grid w-full transition-all duration-300 ease-out ${
              expanded
                ? "grid-rows-[1fr] opacity-100"
                : "grid-rows-[0fr] opacity-0 pointer-events-none !mt-0"
            }`}
          >
            <div className="overflow-hidden">
              <div className="flex flex-col items-center text-center">
                <div
                  className={`grid h-12 w-12 shrink-0 place-items-center rounded-full border-2 border-accent/45 bg-sidebar-accent/90 font-extrabold text-white shadow-inner ${
                    tipoRelatorio === "SOCICAM"
                      ? "text-[8.5px] tracking-tight"
                      : "text-[11px] tracking-wider"
                  }`}
                  title={`${tipoRelatorio} · ${categoriaRelatorio}`}
                >
                  {tipoRelatorio}
                </div>

                <div className="mt-2 text-xs font-bold text-white whitespace-nowrap">
                  {tipoRelatorio} · {categoriaRelatorio}
                </div>
                <div className="mt-2.5 grid w-full grid-cols-3 gap-1.5">
                  {[
                    ["Fotos", totalFotos],
                    ["NCs", ncsCount],
                    ["PAs", pasCount],
                  ].map(([l, v]) => (
                    <div
                      key={String(l)}
                      className="rounded-xl bg-sidebar-accent/90 py-1.5 px-1 border border-white/5"
                    >
                      <div className="text-sm font-bold text-white">{v}</div>
                      <div className="text-[10px] text-sidebar-foreground/60">{l}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* 3. Armazenamento Local (sempre na mesma posição acima da navegação) */}
          <div className="rounded-2xl border border-white/10 bg-white/5 overflow-hidden transition-colors shadow-sm">
            <button
              type="button"
              onClick={() => {
                if (!expanded) {
                  onToggleExpand();
                  setStorageOpen(true);
                } else {
                  setStorageOpen(!storageOpen);
                }
              }}
              className="flex w-full items-center text-left hover:bg-white/5 transition"
              title={
                pastaLocalConectada
                  ? `geradorBD conectado (${nomePastaLocal || "ativo"})`
                  : "Armazenamento Local (geradorBD)"
              }
              aria-label="Armazenamento Local geradorBD"
            >
              <div className="relative grid h-11 w-11 shrink-0 place-items-center text-accent">
                <HardDrive className="h-4 w-4" />
                <span
                  className={`absolute top-2 right-2 h-2 w-2 rounded-full transition-colors ${
                    pastaLocalConectada
                      ? "bg-emerald-500 shadow-[0_0_6px_rgba(16,185,129,0.8)]"
                      : "bg-amber-500 shadow-[0_0_6px_rgba(245,158,11,0.8)]"
                  }`}
                />
              </div>

              <div
                className={`flex flex-1 items-center justify-between overflow-hidden whitespace-nowrap transition-all duration-200 ${
                  expanded
                    ? "pr-3 opacity-100"
                    : "max-w-0 opacity-0 pointer-events-none"
                }`}
              >
                <div className="min-w-0">
                  <div className="text-xs font-bold text-white">
                    Armazenamento Local
                  </div>
                  <div className="text-[10px] text-sidebar-foreground/60">
                    {pastaLocalConectada ? "geradorBD conectado" : "Pasta não vinculada"}
                  </div>
                </div>
                <ChevronDown
                  className={`h-4 w-4 shrink-0 text-white/60 transition-transform duration-300 ${
                    storageOpen ? "rotate-180 text-white" : ""
                  }`}
                />
              </div>
            </button>

            {/* Sanfona Salvar / Carregar */}
            <div
              className={`grid transition-all duration-300 ease-in-out ${
                expanded && storageOpen
                  ? "grid-rows-[1fr] opacity-100 p-3 pt-0"
                  : "grid-rows-[0fr] opacity-0 p-0 pointer-events-none"
              }`}
            >
              <div className="overflow-hidden">
                <div className="pt-2.5 border-t border-white/10 space-y-2.5">
                  <div className="flex items-center justify-between text-[10px] text-white/70">
                    <span className="flex items-center gap-1.5 truncate">
                      <span
                        className={`h-1.5 w-1.5 shrink-0 rounded-full ${
                          pastaLocalConectada ? "bg-emerald-500" : "bg-amber-500"
                        }`}
                      />
                      <span className="truncate">
                        {pastaLocalConectada
                          ? `Conectado a ${nomePastaLocal || "geradorBD"}`
                          : "Pasta não encontrada"}
                      </span>
                    </span>
                    <button
                      type="button"
                      onClick={handleTrocarPasta}
                      className="text-accent hover:underline flex items-center gap-1 shrink-0 ml-2"
                      title="Selecionar ou trocar pasta local"
                    >
                      <RefreshCw className="h-2.5 w-2.5" />
                      {pastaLocalConectada ? "Trocar" : "Localizar"}
                    </button>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <button
                      type="button"
                      onClick={handleSalvar}
                      disabled={isSaving || isLoading}
                      className="flex items-center justify-center gap-1.5 rounded-xl bg-accent px-2.5 py-2 text-[11px] font-bold text-white shadow hover:bg-accent/90 disabled:opacity-50 transition"
                      title={`Salvar dados e fotos de ${tipoRelatorio} na pasta geradorBD`}
                    >
                      <Save className="h-3.5 w-3.5" />
                      {isSaving ? "Salvando..." : "Salvar"}
                    </button>

                    <button
                      type="button"
                      onClick={handleCarregar}
                      disabled={isSaving || isLoading}
                      className="flex items-center justify-center gap-1.5 rounded-xl border border-white/15 bg-white/10 px-2.5 py-2 text-[11px] font-semibold text-white hover:bg-white/20 disabled:opacity-50 transition"
                      title={`Carregar dados salvos anteriormente de ${tipoRelatorio}`}
                    >
                      <FolderOpen className="h-3.5 w-3.5 text-white/80" />
                      {isLoading ? "Lendo..." : "Carregar"}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* 4. Menu de Navegação (separado abaixo, sem contornos/fundos, clicável recolhido) */}
          <div className="!mt-7 border-t border-white/10 pt-5">
            {expanded && (
              <div className="mb-2 px-3 text-[10px] font-bold uppercase tracking-widest text-sidebar-foreground/45">
                Rota do Relatório
              </div>
            )}
            <nav className="space-y-1.5">
              {NAV_ITEMS.map(({ n, label, icon: Icon }) => {
                const unlocked = n <= maxUnlockedStep;
                const cur = n === selectedStep;
                const done = n < maxUnlockedStep || (n === 4 && hasRelatorios);
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
                      if (!unlocked) {
                        e.preventDefault();
                        return;
                      }
                      setSelectedStep(n);
                      const target = document.getElementById(`b${n}`);
                      if (target) {
                        e.preventDefault();
                        target.scrollIntoView({ behavior: "smooth", block: "start" });
                      }
                      if (onNavigate) onNavigate();
                    }}
                    className={`relative flex h-11 items-center text-xs font-medium transition-colors overflow-hidden ${
                      !unlocked
                        ? "cursor-not-allowed text-sidebar-foreground/30"
                        : cur
                          ? `${done ? "text-emerald-400" : "text-white"} font-semibold`
                          : done
                            ? "text-emerald-400 hover:text-emerald-300"
                            : "text-sidebar-foreground/65 hover:text-white"
                    }`}
                  >
                    {cur && (
                      <span
                        className={`absolute left-0 h-6 w-1 rounded-r-full ${
                          done ? "bg-emerald-400" : "bg-accent"
                        }`}
                      />
                    )}
                    <div className="relative grid h-11 w-11 shrink-0 place-items-center">
                      <Icon
                        className={`h-4 w-4 transition-colors ${
                          !unlocked
                            ? "text-sidebar-foreground/30"
                            : done
                              ? "text-emerald-400"
                              : cur
                                ? "text-accent"
                                : "text-sidebar-foreground/65"
                        }`}
                      />
                    </div>

                    <div
                      className={`flex flex-1 items-center justify-between overflow-hidden whitespace-nowrap transition-all duration-200 ${
                        expanded
                          ? "pr-3 opacity-100"
                          : "max-w-0 opacity-0 pointer-events-none"
                      }`}
                    >
                      <span className="truncate">{label}</span>
                    </div>
                  </a>
                );
              })}
            </nav>
          </div>
        </div>

        {/* 5. Rodapé (Auto preenchimento + Expandir recolhido / Ações Rápidas expandido) */}
        <div className="pt-4">
          {!expanded ? (
            <div className="flex flex-col items-center gap-2.5">
              <button
                type="button"
                onClick={handleDemo}
                title="Auto preenchimento"
                aria-label="Auto preenchimento"
                className="grid h-11 w-11 place-items-center rounded-2xl text-sidebar-foreground/60 hover:bg-sidebar-accent hover:text-white transition"
              >
                <Wand2 className="h-4 w-4" />
              </button>

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
          ) : (
            <div className="rounded-3xl border border-white/15 bg-gradient-to-br from-accent/40 via-sidebar-accent to-navy p-4 shadow-lg animate-in fade-in duration-200">
              <div className="flex items-start justify-between gap-2">
                <div className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-white/15 text-white">
                  <Wand2 className="h-4 w-4" />
                </div>
                <div className="flex flex-col items-end gap-1.5">
                  <button
                    type="button"
                    onClick={() => onToggleDense(!dense)}
                    title={`Densidade: ${dense ? "Compacta" : "Confortável"} (clique para alternar)`}
                    className="inline-flex items-center gap-1 rounded-full bg-white/10 px-2.5 py-1 text-[10px] font-semibold text-white/90 hover:bg-white/20 transition whitespace-nowrap"
                  >
                    <MoreVertical className="h-3 w-3" />
                    {dense ? "Compacta" : "Confortável"}
                  </button>
                  <button
                    type="button"
                    onClick={() => onTogglePerformanceMode(!performanceMode)}
                    title={`Modo de Renderização: ${performanceMode ? "Desempenho" : "Padrão"} (clique para alternar)`}
                    className="inline-flex items-center gap-1 rounded-full bg-white/10 px-2.5 py-1 text-[10px] font-semibold text-white/90 hover:bg-white/20 transition whitespace-nowrap"
                  >
                    <Zap className={`h-3 w-3 ${performanceMode ? "text-amber-300" : "text-white/70"}`} />
                    {performanceMode ? "Desempenho" : "Padrão"}
                  </button>
                </div>
              </div>

              <div className="mt-3 text-xs font-bold text-white whitespace-nowrap">
                Ações Rápidas
              </div>
              <div className="mt-0.5 text-[11px] leading-snug text-white/65">
                Preencha dados de teste ou vá direto para a emissão Word.
              </div>

              <div className="mt-3 flex flex-col gap-2">
                <button
                  type="button"
                  onClick={handleDemo}
                  className="flex w-full items-center justify-center gap-2 rounded-xl bg-white py-2 px-3 text-xs font-bold text-primary shadow hover:bg-secondary transition whitespace-nowrap"
                >
                  <Wand2 className="h-3.5 w-3.5 text-accent" /> Auto preenchimento
                </button>
                <a
                  href="#b5"
                  onClick={onNavigate}
                  className="flex w-full items-center justify-center gap-2 rounded-xl bg-white/10 py-1.5 px-3 text-[11px] font-semibold text-white hover:bg-white/20 transition whitespace-nowrap"
                >
                  <Rocket className="h-3.5 w-3.5" /> Ir para emissão
                </a>
              </div>
            </div>
          )}
        </div>
      </aside>

      {/* Modal de Instrução da pasta geradorBD */}
      <PastaGeradorBDModal
        isOpen={showFolderModal}
        onClose={() => setShowFolderModal(false)}
        onSelectFolder={handleRetryPendingAction}
        errorMessage={modalErrorMessage}
      />
    </>
  );
};
