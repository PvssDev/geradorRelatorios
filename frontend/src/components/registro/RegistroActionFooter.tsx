import React from "react";
import {
  Plus,
  Link2,
  Sparkles,
  AlertTriangle,
  Table2,
  ChevronDown,
  ChevronRight,
  Edit3,
} from "lucide-react";
import { RegistroNcItem } from "../../types/report.types";
import { RegistrosCadastradosPanel } from "../RegistrosCadastradosPanel";
import { registroBtn } from "./registroShared";

interface RegistroActionFooterProps {
  dense: boolean;
  isMonitoring: boolean;
  hasActivePhoto: boolean;
  isFotoBloqueada: boolean;
  registroExistenteComFoto: RegistroNcItem | null;
  registroExistenteComFotoAnterior: RegistroNcItem | null;
  podeRelacionar: boolean;
  currentFiscRegs: RegistroNcItem[];
  isRegistrosExpanded: boolean;
  themePrimary: string;
  themeLightBg: string;
  themeLightBorder: string;
  onAddReg: () => void;
  onOpenRelacionar: () => void;
  onToggleExpanded: () => void;
  onOpenEditModal?: (tab: "fisc" | "nc") => void;
}

export const RegistroActionFooter: React.FC<RegistroActionFooterProps> = ({
  dense,
  isMonitoring,
  hasActivePhoto,
  isFotoBloqueada,
  registroExistenteComFoto,
  registroExistenteComFotoAnterior,
  podeRelacionar,
  currentFiscRegs,
  isRegistrosExpanded,
  themePrimary,
  themeLightBg,
  themeLightBorder,
  onAddReg,
  onOpenRelacionar,
  onToggleExpanded,
  onOpenEditModal,
}) => {
  const blockedSummaryItem =
    registroExistenteComFoto || registroExistenteComFotoAnterior;

  return (
    <div className={dense ? "shrink-0 pt-4" : ""}>
      <div
        className={dense ? "flex flex-wrap gap-3" : "mt-8 flex flex-wrap gap-3"}
      >
        <button
          type="button"
          className="group relative inline-flex items-center justify-between gap-3 overflow-hidden rounded-2xl bg-gradient-to-r from-amber-500 via-amber-600 to-amber-700 px-6 py-3.5 text-sm font-bold text-white shadow-md shadow-amber-500/20 transition-all duration-150 hover:brightness-105 hover:shadow-lg hover:shadow-amber-500/30 active:scale-[0.99] disabled:opacity-40 disabled:pointer-events-none flex-1"
          disabled={!hasActivePhoto || isFotoBloqueada}
          onClick={onAddReg}
        >
          <div className="flex items-center gap-2.5">
            <Plus className="h-4 w-4 stroke-[2.5]" />
            <span>
              {registroExistenteComFoto
                ? `Foto atual já cadastrada no Item #${registroExistenteComFoto["Nº"]}`
                : registroExistenteComFotoAnterior
                ? `Foto anterior já registrada no Item #${registroExistenteComFotoAnterior["Nº"]}`
                : isMonitoring
                ? "Salvar Auditoria no Relatório"
                : "Adicionar Registro ao Relatório"}
            </span>
          </div>
          <span className="flex h-7 w-7 items-center justify-center rounded-full bg-black/20 text-white transition-transform duration-200 group-hover:scale-110">
            <ChevronRight className="h-4 w-4 stroke-[2.5]" />
          </span>
        </button>

        <button
          type="button"
          className={`${registroBtn.secondary} py-3.5 px-5`}
          disabled={!podeRelacionar || Boolean(registroExistenteComFoto)}
          title={
            registroExistenteComFoto
              ? `Esta foto já possui cadastro próprio (Item #${registroExistenteComFoto["Nº"]}) e não pode ser relacionada como 2ª foto`
              : podeRelacionar
              ? "Abrir janela para vincular uma 2ª foto a uma ocorrência já registrada (máx. 2 fotos por NC)"
              : "Cadastre ao menos uma ocorrência e envie fotos para habilitar o relacionamento"
          }
          onClick={onOpenRelacionar}
        >
          <Link2 className="h-4 w-4" />
          Relacionar Foto
        </button>
      </div>

      {isFotoBloqueada && blockedSummaryItem && (
        <div className="mt-3 flex items-center justify-between gap-2 rounded-xl border border-amber-300 bg-amber-50 px-4 py-2.5 text-xs text-amber-900">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 shrink-0 text-amber-600" />
            <div>
              <span>
                Esta imagem já está vinculada ao{" "}
                <b>Item #{blockedSummaryItem["Nº"]}</b> (
                {blockedSummaryItem.Identificação || "—"}).
              </span>
              <p className="mt-0.5 text-[11px] text-amber-800">
                Avance para outra foto no bloco 2 ou gerencie a ocorrência no
                Sumário abaixo se desejar alterá-la.
              </p>
            </div>
          </div>
        </div>
      )}

      {!hasActivePhoto && (
        <p className="mt-2 text-center text-xs text-muted-foreground">
          Envie ao menos uma foto no bloco 02 para habilitar o registro.
        </p>
      )}

      {currentFiscRegs.length === 0 && (
        <div className="mt-3 flex items-center justify-center gap-2 rounded-xl border border-dashed border-amber-300/80 bg-amber-50/50 p-3 text-xs text-amber-900">
          <Sparkles className="h-3.5 w-3.5 text-amber-600 shrink-0" />
          <span>
            Cadastre a primeira ocorrência para desbloquear o painel de emissão e
            exportação.
          </span>
        </div>
      )}

      {/* Trigger do Sumário Retrátil */}
      {(() => {
        const baseRegs = currentFiscRegs.filter((r) => !r.is_relacionado);
        const sanadasCount = baseRegs.filter((r) => r.Situação === "Sanada").length;
        const pendentesCount = baseRegs.filter(
          (r) => !r.Situação || r.Situação === "Pendente"
        ).length;

        return (
          <div className="mt-5 border-t border-slate-200/90 pt-4">
            <div className="overflow-hidden rounded-2xl border border-slate-300/90 bg-white shadow-md shadow-slate-900/5 transition-all duration-200">
              <button
                type="button"
                onClick={onToggleExpanded}
                className={`group relative flex w-full items-center justify-between gap-4 p-4 text-left transition-colors duration-150 hover:bg-slate-50/80 ${
                  isRegistrosExpanded
                    ? "border-b border-slate-200 bg-white"
                    : "bg-white"
                }`}
              >
                <div className="flex items-center gap-3.5">
                  <div
                    className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl border shadow-xs transition-transform duration-200 group-hover:scale-105"
                    style={{
                      backgroundColor: themeLightBg,
                      borderColor: themeLightBorder,
                      color: themePrimary,
                    }}
                  >
                    <Table2 className="h-5 w-5" />
                  </div>
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-sm font-bold text-slate-900">
                        {isMonitoring
                          ? "Sumário de Auditoria e Ocorrências"
                          : "Sumário de Registros Cadastrados"}
                      </span>
                      <span
                        className="rounded-full border px-2.5 py-0.5 font-mono text-[11px] font-bold shadow-xs"
                        style={{
                          backgroundColor: themeLightBg,
                          borderColor: themeLightBorder,
                          color: themePrimary,
                        }}
                      >
                        {baseRegs.length}{" "}
                        {baseRegs.length === 1 ? "achado" : "achados"}
                      </span>
                      {isMonitoring && (
                        <div className="flex items-center gap-1.5">
                          <span className="inline-flex items-center gap-1 font-semibold text-[#008763] bg-[#e6fbf4] border border-[#a7f3d0] px-2 py-0.5 rounded-full text-[10px]">
                            <span className="h-1.5 w-1.5 rounded-full bg-[#008763]" />
                            {sanadasCount} saneada(s)
                          </span>
                          <span className="inline-flex items-center gap-1 font-semibold text-[#b45309] bg-[#fffbeb] border border-[#fde68a] px-2 py-0.5 rounded-full text-[10px]">
                            <span className="h-1.5 w-1.5 rounded-full bg-[#b45309]" />
                            {pendentesCount} pendente(s)
                          </span>
                        </div>
                      )}
                    </div>
                    <p className="mt-0.5 text-xs text-slate-500">
                      {isMonitoring
                        ? `Clique para ${
                            isRegistrosExpanded
                              ? "recolher"
                              : "abrir e gerenciar"
                          } a tabela completa de ocorrências`
                        : `Total de ${currentFiscRegs.length} foto(s) e ocorrências consolidadas neste relatório`}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3 shrink-0">
                  {currentFiscRegs.length > 0 && (
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        onOpenEditModal?.("nc");
                      }}
                      className="inline-flex items-center gap-1.5 rounded-xl border border-slate-300 bg-white px-3 py-1.5 text-[11px] font-bold text-slate-700 shadow-xs hover:bg-slate-50 hover:text-slate-900 hover:border-slate-400 active:scale-[0.98] transition-all"
                      title="Editar todas as ocorrências em lote"
                    >
                      <Edit3
                        className="h-3.5 w-3.5"
                        style={{ color: themePrimary }}
                      />
                      <span className="hidden sm:inline">Editar em Lote</span>
                    </button>
                  )}
                  <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 group-hover:text-slate-900 transition-colors">
                    <span className="hidden md:inline">
                      {isRegistrosExpanded
                        ? "Recolher Sumário"
                        : "Expandir Sumário"}
                    </span>
                    <span
                      className={`flex h-7 w-7 items-center justify-center rounded-full bg-slate-100 text-slate-600 transition-transform duration-300 ${
                        isRegistrosExpanded ? "rotate-180" : "rotate-0"
                      }`}
                    >
                      <ChevronDown className="h-4 w-4 stroke-[2.5]" />
                    </span>
                  </div>
                </div>
              </button>

              <div
                className={`grid transition-all duration-300 ease-in-out ${
                  isRegistrosExpanded
                    ? "grid-rows-[1fr] opacity-100"
                    : "grid-rows-[0fr] opacity-0 pointer-events-none"
                }`}
              >
                <div className="overflow-hidden">
                  <RegistrosCadastradosPanel
                    onOpenEditModal={onOpenEditModal || (() => {})}
                  />
                </div>
              </div>
            </div>
          </div>
        );
      })()}
    </div>
  );
};

