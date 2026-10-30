import React, { useEffect, useState } from "react";
import { Toaster } from "sonner";
import { Sidebar } from "./components/Sidebar";
import { TopHeader } from "./components/TopHeader";
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

export const App: React.FC = () => {
  const { hydrateBootstrapConfig } = useReportStore();

  // No desktop, alterna entre a barra estreita de ícones (false = 76px) e o card expandido (true = 288px)
  const [sidebarExpanded, setSidebarExpanded] = useState<boolean>(false);
  // No mobile (< lg), controla o drawer flutuante
  const [mobileMenuOpen, setMobileMenuOpen] = useState<boolean>(false);
  const [dense, setDense] = useState(false);

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
    <div className="min-h-screen bg-[#eaf1f8]">
      <Toaster position="top-right" richColors closeButton />

      {/* Sidebar Desktop Infinita (Topo, Base e Esquerda colados na tela): Alterna entre 76px e 288px com Animação Fluida */}
      <div
        className={`fixed inset-y-0 left-0 z-40 hidden lg:block transition-all duration-300 ease-[cubic-bezier(0.25,1,0.5,1)] ${
          sidebarExpanded ? "w-72" : "w-[76px]"
        }`}
      >
        <Sidebar
          expanded={sidebarExpanded}
          onToggleExpand={() => setSidebarExpanded((prev) => !prev)}
          dense={dense}
          onToggleDense={setDense}
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
          />
        </div>
      </div>

      {/* Área Principal com Transição Fluida no Padding */}
      <main
        className={`min-h-screen bg-[#eaf1f8] transition-[padding] duration-300 ease-[cubic-bezier(0.25,1,0.5,1)] ${
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
          {/* 01 · Fotos da Vistoria em Campo */}
          <UploadPanel onOpenGalleryModal={() => setShowGalleryModal(true)} />

          {/* 02 · Informações da Fiscalização / Monitoramento */}
          <FiscalizacaoForm
            onOpenResponsaveisModal={() => setStaffModalMode("responsaveis")}
            onOpenCoordenadoresModal={() => setStaffModalMode("coordenadores")}
            onOpenContratosModal={(cb) => {
              setContratosCallback(() => cb || null);
              setShowContratosModal(true);
            }}
          />

          {/* 03 · Registro de Não Conformidade ou Ponto de Atenção */}
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
          />

          {/* 04 e 05 · Auditoria & Tabela + Emissão e Exportação */}
          <SummaryAndActionsPanel
            onOpenEditModal={(tab = "nc") => {
              setEditModalTab(tab);
              setShowEditModal(true);
            }}
          />
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

export default App;
