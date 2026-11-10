import React, { useEffect, useState, useRef } from "react";
import { Toaster } from "sonner";
import { Sidebar } from "./components/Sidebar";
import { TopHeader } from "./components/TopHeader";
import { useClickOutside } from "./hooks/useClickOutside";
import { FiscalizacaoForm } from "./components/FiscalizacaoForm";
import { UploadPanel } from "./components/UploadPanel";
import { RegistroNcForm } from "./components/RegistroNcForm";
import { SummaryAndActionsPanel } from "./components/SummaryAndActionsPanel";
import {
  ContratosManagerModal,
  CustomNcModal,
  EditRecordsModal,
  PhotoGalleryModal,
  RelacionarFotoModal,
  StaffManagerModal,
} from "./components/Modals";
import { fetchBootstrapConfig } from "./services/api";
import { useReportStore } from "./store/useReportStore";
import { getConcessionTheme } from "./utils/concessionTheme";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { useLockBodyScroll } from "./hooks/useLockBodyScroll";

const AppContent: React.FC = () => {
  const { hydrateBootstrapConfig, tipoRelatorio, categoriaRelatorio } =
    useReportStore();

  const activeWorkspace = useReportStore((state) => {
    const key = `${state.tipoRelatorio}_${state.categoriaRelatorio}` as const;
    return state.workspaces[key];
  });
  const hasFiscalizacao = Boolean(
    activeWorkspace?.fiscalizacoes?.length &&
      activeWorkspace.fiscalizacoes.some((f) => Boolean(f["ID da Fiscalização"]?.trim()))
  );
  const activeFiscId =
    activeWorkspace?.fiscalizacoes[activeWorkspace.activeFiscalizacaoIndex]?.["ID da Fiscalização"]?.trim() || "";
  const hasFotos = Boolean(
    activeWorkspace?.photos?.length ||
      (activeWorkspace?.documentoAnteriorFile && categoriaRelatorio === "Monitoramento")
  );
  const hasRegistros = Boolean(
    activeWorkspace?.registrosNc?.some(
      (r) => !activeFiscId || (r["ID da Fiscalização"] || "").trim() === activeFiscId
    )
  );

  const [performanceMode, setPerformanceMode] = useState<boolean>(() => {
    try {
      return localStorage.getItem("arpe_perf_mode") === "true";
    } catch {
      return false;
    }
  });

  const theme = getConcessionTheme(tipoRelatorio, categoriaRelatorio);
  const craDefaultTheme = getConcessionTheme("CRA", "Fiscalização");
  const activeBgTheme = performanceMode ? craDefaultTheme : theme;

  // No desktop, alterna entre a barra estreita de ícones (false = 76px) e o card expandido (true = 288px)
  const [sidebarExpanded, setSidebarExpanded] = useState<boolean>(false);
  const desktopSidebarRef = useRef<HTMLDivElement>(null);

  // Fecha o menu lateral desktop ao clicar fora de sua área
  useClickOutside(
    desktopSidebarRef,
    () => {
      if (sidebarExpanded) {
        setSidebarExpanded(false);
      }
    },
    sidebarExpanded
  );
  // No mobile (< lg), controla o drawer flutuante
  const [mobileMenuOpen, setMobileMenuOpen] = useState<boolean>(false);
  const [dense, setDense] = useState(false);

  const handleTogglePerformanceMode = (val: boolean) => {
    setPerformanceMode(val);
    try {
      localStorage.setItem("arpe_perf_mode", String(val));
    } catch {}
    // Dispara evento customizado para que os componentes inscritos no tema atualizem instantaneamente
    window.dispatchEvent(new Event("storage"));
  };

  // Garante que o App re-renderize quando o modo mudar
  const [, setRerenderKey] = useState(0);
  useEffect(() => {
    const handleStorage = () => setRerenderKey((k) => k + 1);
    window.addEventListener("storage", handleStorage);
    return () => window.removeEventListener("storage", handleStorage);
  }, []);

  const [staffModalMode, setStaffModalMode] = useState<
    "responsaveis" | "coordenadores" | null
  >(null);
  const [contratosCallback, setContratosCallback] = useState<
    ((val: string) => void) | null
  >(null);
  const [showContratosModal, setShowContratosModal] = useState(false);

  const [customNcCallback, setCustomNcCallback] = useState<
    ((val: string) => void) | null
  >(null);
  const [showCustomNcModal, setShowCustomNcModal] = useState(false);

  const [showGalleryModal, setShowGalleryModal] = useState(false);

  const [relacionarPhotoName, setRelacionarPhotoName] = useState<
    string | undefined
  >(undefined);
  const [showRelacionarModal, setShowRelacionarModal] = useState(false);

  const [editModalTab, setEditModalTab] = useState<"fisc" | "nc">("nc");
  const [showEditModal, setShowEditModal] = useState(false);

  const hasAnyModalOpen = Boolean(
    staffModalMode ||
    showContratosModal ||
    showCustomNcModal ||
    showGalleryModal ||
    showRelacionarModal ||
    showEditModal
  );
  useLockBodyScroll(hasAnyModalOpen);

  useEffect(() => {
    fetchBootstrapConfig()
      .then((cfg) => {
        hydrateBootstrapConfig(cfg);
      })
      .catch(() => {
        // Mantém listas padrão da ARPE pré-carregadas silenciosamente
      });
  }, [hydrateBootstrapConfig]);

  return (
    <div
      className={`relative min-h-screen ${performanceMode ? "perf-mode" : "transition-colors duration-700 ease-in-out"}`}
      style={{
        backgroundColor: activeBgTheme.lightBg,
      }}
    >
      <Toaster position="top-right" richColors closeButton />

      {/* Fundo Corporativo (No modo desempenho, usa fundo sólido leve sem radial-gradient) */}
      <div
        aria-hidden="true"
        className={`pointer-events-none fixed inset-0 z-0 overflow-hidden ${performanceMode ? "" : "transition-colors duration-700 ease-in-out opacity-75"}`}
        style={{
          background: performanceMode
            ? activeBgTheme.lightBg
            : `radial-gradient(ellipse 135% 85% at 50% -15%, ${activeBgTheme.primary}18 0%, ${activeBgTheme.lightBorder} 38%, ${activeBgTheme.lightBg} 72%, #ffffff 100%)`,
        }}
      />

      {/* Sidebar Desktop Infinita (Topo, Base e Esquerda colados na tela): Alterna entre 76px e 288px com Animação Fluida */}
      <div
        ref={desktopSidebarRef}
        onClick={() => {
          if (!sidebarExpanded) {
            setSidebarExpanded(true);
          }
        }}
        className={`fixed inset-y-0 left-0 z-40 hidden lg:block transition-all duration-300 ease-[cubic-bezier(0.25,1,0.5,1)] ${
          sidebarExpanded ? "w-72" : "w-[76px] cursor-pointer"
        }`}
      >
        <Sidebar
          expanded={sidebarExpanded}
          onToggleExpand={() => setSidebarExpanded((prev) => !prev)}
          dense={dense}
          onToggleDense={setDense}
          performanceMode={performanceMode}
          onTogglePerformanceMode={handleTogglePerformanceMode}
        />
      </div>

      {/* Drawer Mobile Infinito com Animação Fluida de Slide */}
      <div
        className={`fixed inset-0 z-50 flex lg:hidden transition-opacity duration-300 ${
          mobileMenuOpen
            ? "opacity-100 pointer-events-auto"
            : "opacity-0 pointer-events-none"
        }`}
      >
        <button
          type="button"
          aria-label="Fechar menu"
          className="fixed inset-0 bg-foreground/50 backdrop-blur-[2px] transition-opacity duration-300"
          onClick={() => setMobileMenuOpen(false)}
        />
        <div
          className={`relative z-10 h-full transition-transform duration-300 ease-[cubic-bezier(0.25,1,0.5,1)] ${
            mobileMenuOpen ? "translate-x-0" : "-translate-x-full"
          }`}
        >
          <Sidebar
            expanded={true}
            onToggleExpand={() => setMobileMenuOpen(false)}
            onNavigate={() => setMobileMenuOpen(false)}
            dense={dense}
            onToggleDense={setDense}
            performanceMode={performanceMode}
            onTogglePerformanceMode={handleTogglePerformanceMode}
          />
        </div>
      </div>

      {/* Área Principal com Transição Fluida no Padding e Fundo Transparente para Atmosfera */}
      <main
        className={`relative z-10 min-h-screen bg-transparent transition-[padding] duration-300 ease-[cubic-bezier(0.25,1,0.5,1)] ${
          sidebarExpanded ? "lg:pl-72" : "lg:pl-[76px]"
        }`}
      >
        <TopHeader
          onToggleMobileMenu={() => setMobileMenuOpen((prev) => !prev)}
        />

        <div
          className={`mx-auto max-w-5xl px-6 py-10 ${
            dense ? "space-y-6" : "space-y-10"
          }`}
        >
          {/* 01 · Informações da Fiscalização / Monitoramento */}
          <FiscalizacaoForm
            onOpenResponsaveisModal={() => setStaffModalMode("responsaveis")}
            onOpenCoordenadoresModal={() => setStaffModalMode("coordenadores")}
            onOpenContratosModal={(cb) => {
              setContratosCallback(() => cb || null);
              setShowContratosModal(true);
            }}
          />

          {/* 02 · Fotos da Vistoria em Campo */}
          {hasFiscalizacao && (
            <div className="animate-reveal">
              <UploadPanel onOpenGalleryModal={() => setShowGalleryModal(true)} />
            </div>
          )}

          {/* 03 · Registro de Não Conformidade ou Ponto de Atenção */}
          {hasFiscalizacao && hasFotos && (
            <div className="animate-reveal">
              <RegistroNcForm
                onOpenCustomNcModal={(cb) => {
                  setCustomNcCallback(() => cb);
                  setShowCustomNcModal(true);
                }}
                onOpenRelacionarModal={(photoName) => {
                  setRelacionarPhotoName(photoName);
                  setShowRelacionarModal(true);
                }}
                onOpenGalleryModal={() => setShowGalleryModal(true)}
                onOpenEditModal={(tab = "nc") => {
                  setEditModalTab(tab);
                  setShowEditModal(true);
                }}
              />
            </div>
          )}

          {/* 04 · Emissão e Exportação do Relatório */}
          {hasFiscalizacao && hasFotos && hasRegistros && (
            <div className="animate-reveal">
              <SummaryAndActionsPanel
                onOpenEditModal={(tab = "nc") => {
                  setEditModalTab(tab);
                  setShowEditModal(true);
                }}
              />
            </div>
          )}
        </div>
      </main>

      {staffModalMode && (
        <StaffManagerModal
          mode={staffModalMode}
          onClose={() => setStaffModalMode(null)}
        />
      )}

      {showContratosModal && (
        <ContratosManagerModal
          onSelectContrato={contratosCallback || undefined}
          onClose={() => {
            setShowContratosModal(false);
            setContratosCallback(null);
          }}
        />
      )}

      {showCustomNcModal && (
        <CustomNcModal
          onSelectCallback={customNcCallback || undefined}
          onClose={() => {
            setShowCustomNcModal(false);
            setCustomNcCallback(null);
          }}
        />
      )}

      {showGalleryModal && (
        <PhotoGalleryModal onClose={() => setShowGalleryModal(false)} />
      )}

      {showRelacionarModal && (
        <RelacionarFotoModal
          initialPhotoName={relacionarPhotoName}
          onClose={() => {
            setShowRelacionarModal(false);
            setRelacionarPhotoName(undefined);
          }}
        />
      )}

      {showEditModal && (
        <EditRecordsModal
          initialTab={editModalTab}
          onClose={() => setShowEditModal(false)}
        />
      )}
    </div>
  );
};

export const App: React.FC = () => (
  <ErrorBoundary>
    <AppContent />
  </ErrorBoundary>
);

export default App;
