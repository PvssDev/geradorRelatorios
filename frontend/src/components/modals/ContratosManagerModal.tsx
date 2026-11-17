import React, { useState } from "react";
import { Plus, Trash2, FileText } from "lucide-react";
import { toast } from "sonner";
import { useReportStore } from "../../store/useReportStore";
import { saveContratosApi } from "../../services/api";
import { ThemedModalShell } from "./ThemedModalShell";
import { modalCountBadgeCls, modalPrimaryBtnCls, modalSoftCardCls } from "./modalHelpers";

export const ContratosManagerModal: React.FC<{
  onSelectContrato?: (contrato: string) => void;
  onClose: () => void;
}> = ({ onSelectContrato, onClose }) => {
  const { contratos, setContratos } = useReportStore();
  const [novoContrato, setNovoContrato] = useState("");

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

        {/* Corpo com Formulário e Lista de Cadastrados */}
        <div className="space-y-4 overflow-y-auto p-5">
          <form onSubmit={handleAdd} className="space-y-3">
            <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              + NOVO CONTRATO
            </div>

            <div className="relative">
              <FileText className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 pointer-events-none" />
              <input
                type="text"
                value={novoContrato}
                onChange={(e) => setNovoContrato(e.target.value)}
                placeholder="Ex: CT. nº 043/2011"
                className="w-full h-11 rounded-2xl border border-slate-200 bg-[#f1f5f9] pl-10 pr-4 text-xs font-medium text-slate-800 outline-none transition-all duration-200 hover:border-slate-300 hover:bg-slate-100/80 focus:bg-white focus:border-[var(--concession-primary)] focus:ring-2 focus:ring-[var(--concession-primary)]/20"
              />
            </div>

            <button type="submit" className={modalPrimaryBtnCls}>
              <Plus className="h-4 w-4 stroke-[2.5]" />
              <span>Adicionar contrato</span>
            </button>
          </form>

          {/* Seção de Contratos Cadastrados */}
          <div className="border-t border-slate-200/80 pt-3 space-y-2.5">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                CADASTRADOS
              </span>
              <span className={modalCountBadgeCls}>{contratos.length}</span>
            </div>

            {contratos.length === 0 ? (
              <p className="text-xs italic text-slate-400 py-2">
                Nenhum contrato cadastrado ainda.
              </p>
            ) : (
              <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
                {contratos.map((c, idx) => (
                  <div key={`${c}_${idx}`} className={modalSoftCardCls}>
                    <button
                      type="button"
                      onClick={() => {
                        if (onSelectContrato) onSelectContrato(c);
                        onClose();
                      }}
                      className="flex-1 text-left font-mono text-xs font-bold text-slate-900 hover:text-blue-600 truncate"
                      title={`Clique para selecionar ${c}`}
                    >
                      {c}
                    </button>
                    <button
                      type="button"
                      onClick={() => handleRemove(idx)}
                      className="rounded-lg p-1.5 text-slate-400 hover:bg-rose-50 hover:text-rose-600 transition shrink-0"
                      title="Remover"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
    </ThemedModalShell>
  );
};
