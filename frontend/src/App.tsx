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
    <div className="min-h-screen bg-muted">
      <Toaster position="top-right" richColors closeButton />

      {/* Sidebar Desktop Infinita (Topo, Base e Esquerda colados na tela): Alterna entre 76px e 288px */}
      <div className="fixed inset-y-0 left-0 z-40 hidden lg:block transition-all duration-300 ease-in-out">
        <Sidebar
          expanded={sidebarExpanded}
          onToggleExpand={() => setSidebarExpanded((prev) => !prev)}
          dense={dense}
          onToggleDense={setDense}
        />
      </div>

      {/* Drawer Mobile Infinito na Vertical e Esquerda */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 flex lg:hidden">
          <button
            type="button"
            aria-label="Fechar menu"
            className="fixed inset-0 bg-foreground/40 backdrop-blur-[1px]"
            onClick={() => setMobileMenuOpen(false)}
          />
          <div className="relative z-10 h-full">
            <Sidebar
              expanded={true}
              onToggleExpand={() => setMobileMenuOpen(false)}
              onNavigate={() => setMobileMenuOpen(false)}
              dense={dense}
              onToggleDense={setDense}
            />
          </div>
        </div>
      )}

      {/* Área Principal alinhada exatamente com a largura da barra (76px recolhida ou 288px expandida) */}
      <main
        className={`min-h-screen bg-muted transition-[padding] duration-300 ease-in-out ${
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
