import React from "react";
import { Trash2 } from "lucide-react";
import { ThemedModalShell } from "./ThemedModalShell";

export const ConfirmDeleteModal: React.FC<{
  title: string;
  description: string;
  itemsPreview: string[];
  onConfirm: () => void;
  onClose: () => void;
}> = ({ title, description, itemsPreview, onConfirm, onClose }) => {
  return (
    <ThemedModalShell
      icon={<Trash2 className="h-4 w-4" />}
      title={title}
      accentColor="#e11d48"
      onClose={onClose}
    >

        <div className="space-y-4 p-5">
          <p className="text-xs sm:text-sm text-slate-700 font-medium">{description}</p>
          {itemsPreview.length > 0 && (
            <ul className="max-h-40 space-y-1.5 overflow-y-auto rounded-2xl border border-slate-200 bg-[#f1f5f9] p-3 text-xs font-semibold text-slate-800">
              {itemsPreview.map((it, idx) => (
                <li key={idx}>• {it}</li>
              ))}
            </ul>
          )}
          <div className="rounded-2xl border border-amber-300 bg-amber-50/90 p-3 text-xs font-semibold text-amber-950">
            Atenção: Esta ação não poderá ser desfeita.
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-xs font-semibold text-slate-700 shadow-xs hover:bg-slate-50 hover:text-slate-900 hover:border-slate-400 active:scale-[0.98] transition-all"
            >
              Cancelar
            </button>
            <button
              type="button"
              onClick={() => {
                onConfirm();
                onClose();
              }}
              className="inline-flex items-center gap-1.5 rounded-xl border border-red-600 bg-red-600 px-4 py-2 text-xs font-bold text-white shadow-sm hover:bg-red-700 active:scale-[0.98] transition-all"
            >
              <Trash2 className="h-4 w-4" />
              Sim, Excluir
            </button>
          </div>
        </div>
    </ThemedModalShell>
  );
};

/* -------------------------------------------------------------------------- */
/* 7. MODAL EDITAR DADOS REGISTRADOS (FISCALIZAÇÕES E NCs/PAs)                */
/* -------------------------------------------------------------------------- */
