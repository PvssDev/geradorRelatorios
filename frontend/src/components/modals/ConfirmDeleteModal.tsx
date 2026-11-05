import React from "react";
import { AlertTriangle, Trash2, X } from "lucide-react";

export const ConfirmDeleteModal: React.FC<{
  title: string;
  description: string;
  itemsPreview: string[];
  onConfirm: () => void;
  onClose: () => void;
}> = ({ title, description, itemsPreview, onConfirm, onClose }) => {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-foreground/60 p-4 backdrop-blur-[1px]"
      role="dialog"
      aria-modal="true"
    >
      <div className="w-full max-w-md overflow-hidden rounded-2xl border border-border bg-card shadow-card-lg">
        <div className="flex items-center justify-between border-b border-border bg-nc px-5 py-4 text-destructive-foreground">
          <h3 className="flex items-center gap-2 text-base font-bold">
            <Trash2 className="h-5 w-5" />
            {title}
          </h3>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1 text-white/80 hover:bg-white/10 hover:text-white"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="space-y-4 p-5">
          <p className="text-sm text-foreground">{description}</p>
          {itemsPreview.length > 0 && (
            <ul className="max-h-40 space-y-1 overflow-y-auto rounded-xl border border-border bg-secondary/40 p-3 text-xs font-semibold text-foreground">
              {itemsPreview.map((it, idx) => (
                <li key={idx}>• {it}</li>
              ))}
            </ul>
          )}
          <div className="rounded-xl border border-pa/30 bg-pa-soft p-3 text-xs font-medium text-pa">
            Esta ação não pode ser desfeita.
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-xl border border-border bg-card px-4 py-2 text-xs font-semibold text-foreground hover:bg-muted transition"
            >
              Cancelar
            </button>
            <button
              type="button"
              onClick={() => {
                onConfirm();
                onClose();
              }}
              className="inline-flex items-center gap-1.5 rounded-xl border border-red-500/60 bg-red-600 px-4 py-2 text-xs font-bold text-white shadow-[0_2px_0_0_#991b1b] hover:bg-red-500 active:translate-y-[1px] transition"
            >
              <Trash2 className="h-4 w-4" />
              Sim, Excluir
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

/* -------------------------------------------------------------------------- */
/* 7. MODAL EDITAR DADOS REGISTRADOS (FISCALIZAÇÕES E NCs/PAs)                */
/* -------------------------------------------------------------------------- */
