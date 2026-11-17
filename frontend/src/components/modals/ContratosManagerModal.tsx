import React, { useState } from "react";
import { Plus, Trash2, FileText, FilePlus2 } from "lucide-react";
import { toast } from "sonner";
import { useReportStore } from "../../store/useReportStore";
import { saveContratosApi } from "../../services/api";
import { useConcessionTheme } from "../../hooks/useConcessionTheme";
import { ThemedModalShell } from "./ThemedModalShell";
import { ExclusiveAccordionCard } from "./ExclusiveAccordionCard";

export const ContratosManagerModal: React.FC<{
  onSelectContrato?: (contrato: string) => void;
  onClose: () => void;
}> = ({ onSelectContrato, onClose }) => {
  const { contratos, setContratos } = useReportStore();
  const theme = useConcessionTheme();
  const [openSection, setOpenSection] = useState<"cadastrados" | "novo" | null>("cadastrados");
  const [novoContrato, setNovoContrato] = useState("");

  const toggleSection = (section: "cadastrados" | "novo") => {
    setOpenSection((prev) => (prev === section ? null : section));
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    const clean = novoContrato.trim();
    if (!clean) {
      toast.error("Informe o número do contrato.");
      return;
    }
    if (contratos.includes(clean)) {
      toast.warning("Este contrato já está cadastrado.");
      return;
    }
    const next = [...contratos, clean];
    setContratos(next);
    await saveContratosApi(next).catch(() => {});
    if (onSelectContrato) onSelectContrato(clean);
    toast.success(`Contrato '${clean}' adicionado!`);
    setNovoContrato("");
    setOpenSection("cadastrados");
  };

  const handleRemove = async (idx: number) => {
    const next = contratos.filter((_, i) => i !== idx);
    setContratos(next);
    await saveContratosApi(next).catch(() => {});
    toast.info("Contrato removido.");
  };

  return (
    <ThemedModalShell
      icon={<FileText className="h-4 w-4" />}
      title={`Contratos Regulatórios · ${contratos.length}`}
      onClose={onClose}
    >
      <div
        className="space-y-3 overflow-y-auto p-4 sm:p-5"
        style={{ backgroundColor: theme.lightBg }}
      >
        <ExclusiveAccordionCard
          isOpen={openSection === "cadastrados"}
          onToggle={() => toggleSection("cadastrados")}
          icon={<FileText className="h-4 w-4" />}
          title="Cadastrados"
          subtitle="Contratos já registrados"
          count={contratos.length}
          primaryColor={theme.primary}
          borderColor={theme.lightBorder}
        >
          <div className="border-t border-slate-100 bg-white px-4 pb-4 pt-3">
            {contratos.length === 0 ? (
              <p className="py-2 text-center text-xs italic text-slate-400">
                Nenhum contrato cadastrado ainda.
              </p>
            ) : (
              <div className="max-h-60 space-y-2.5 overflow-y-auto pr-1">
                {contratos.map((c, idx) => (
                  <div
                    key={`${c}_${idx}`}
                    className="flex items-center justify-between gap-3 rounded-2xl border border-slate-200/85 bg-white p-3.5 shadow-2xs transition-all hover:border-slate-300"
                  >
                    <button
                      type="button"
                      onClick={() => {
                        if (onSelectContrato) onSelectContrato(c);
                        onClose();
                      }}
                      className="flex-1 truncate text-left font-mono text-xs font-bold text-slate-900 transition hover:opacity-80"
                      style={{ color: undefined }}
                      title={`Clique para selecionar ${c}`}
                    >
                      {c}
                    </button>
                    <button
                      type="button"
                      onClick={() => handleRemove(idx)}
                      className="shrink-0 rounded-lg p-1.5 text-slate-400 transition hover:bg-rose-50 hover:text-rose-600"
                      title="Remover"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </ExclusiveAccordionCard>

        <ExclusiveAccordionCard
          isOpen={openSection === "novo"}
          onToggle={() => toggleSection("novo")}
          icon={<FilePlus2 className="h-4 w-4" />}
          title="Novo Contrato"
          subtitle="Cadastre um contrato regulatório"
          primaryColor={theme.primary}
          borderColor={theme.lightBorder}
        >
          <form
            onSubmit={handleAdd}
            className="space-y-3 border-t border-slate-100 bg-white px-4 pb-4 pt-3"
          >
            <div className="relative">
              <FileText className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                value={novoContrato}
                onChange={(e) => setNovoContrato(e.target.value)}
                placeholder="Ex: CT. nº 043/2011"
                className="h-11 w-full rounded-full border border-slate-200 bg-white pl-11 pr-4 text-xs font-medium text-slate-800 outline-none transition-all duration-200 hover:border-slate-300 focus:border-[var(--concession-primary)] focus:ring-2 focus:ring-[var(--concession-primary)]/20"
              />
            </div>

            <button
              type="submit"
              style={{ backgroundColor: theme.primary }}
              className="flex h-11 w-full cursor-pointer items-center justify-center gap-2 rounded-full text-xs font-bold text-white shadow-sm transition-all duration-150 hover:brightness-110 active:scale-[0.98]"
            >
              <Plus className="h-4 w-4 stroke-[2.5]" />
              <span>Adicionar contrato</span>
            </button>
          </form>
        </ExclusiveAccordionCard>
      </div>
    </ThemedModalShell>
  );
};
