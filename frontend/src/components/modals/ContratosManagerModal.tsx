import React, { useState } from "react";
import { X, Plus, Trash2, Save, Tag, FileText } from "lucide-react";
import { toast } from "sonner";
import { useReportStore } from "../../store/useReportStore";
import { saveContratosApi } from "../../services/api";
import { modalInputCls } from "./modalHelpers";

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
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-foreground/60 p-4 backdrop-blur-[1px]"
      role="dialog"
      aria-modal="true"
    >
      <div className="flex max-h-[85vh] w-full max-w-md flex-col overflow-hidden rounded-2xl border border-border bg-card shadow-card-lg">
        <div className="flex items-center justify-between border-b border-border bg-navy-gradient px-5 py-4 text-primary-foreground">
          <h3 className="flex items-center gap-2 text-base font-bold">
            <FileText className="h-5 w-5 text-accent" />
            Gerenciar Contratos
          </h3>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1.5 text-primary-foreground/80 hover:bg-white/10 hover:text-primary-foreground"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="space-y-4 overflow-y-auto p-5">
          <form onSubmit={handleAdd} className="space-y-3">
            <div>
              <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                Número do Novo Contrato
              </label>
              <input
                type="text"
                value={novoContrato}
                onChange={(e) => setNovoContrato(e.target.value)}
                placeholder="Ex: CT. nº 043/2011"
                className={modalInputCls}
              />
            </div>
            <button
              type="submit"
              className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-xs font-semibold text-primary-foreground hover:bg-navy-2 transition"
            >
              <Plus className="h-4 w-4" />
              Adicionar Contrato
            </button>
          </form>

          <div className="border-t border-border pt-3">
            <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Contratos Salvos ({contratos.length})
            </h4>
            <div className="space-y-2">
              {contratos.map((c, idx) => (
                <div
                  key={`${c}_${idx}`}
                  className="flex items-center justify-between gap-2 rounded-xl border border-border bg-secondary/40 p-2.5"
                >
                  <button
                    type="button"
                    onClick={() => {
                      if (onSelectContrato) onSelectContrato(c);
                      onClose();
                    }}
                    className="flex-1 text-left font-mono text-xs font-semibold text-foreground hover:text-accent"
                  >
                    {c}
                  </button>
                  <button
                    type="button"
                    onClick={() => handleRemove(idx)}
                    className="rounded-md p-1.5 text-nc hover:bg-nc-soft"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

/* -------------------------------------------------------------------------- */
/* 3. MODAL ADICIONAR NÃO CONFORMIDADE PERSONALIZADA                          */
/* -------------------------------------------------------------------------- */
