import React from "react";
import { createPortal } from "react-dom";
import { Trash2, X } from "lucide-react";
import { useLockBodyScroll } from "../../hooks/useLockBodyScroll";

export const ConfirmDeleteModal: React.FC<{
  title: string;
  description: string;
  itemsPreview: string[];
  onConfirm: () => void;
  onClose: () => void;
}> = ({ title, description, itemsPreview, onConfirm, onClose }) => {
  useLockBodyScroll(true);

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-md"
      role="dialog"
      aria-modal="true"
    >
      <div className="w-full max-w-md overflow-hidden rounded-[28px] border border-slate-700/30 bg-white shadow-2xl animate-in fade-in zoom-in-95 duration-150">
        {/* Topo Dark Executivo com Badge Rose de Alerta */}
        <div className="flex items-center justify-between border-b border-slate-800 bg-[#0b1728] px-5 py-4 text-white">
          <div className="flex items-center gap-3 min-w-0">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-rose-600 text-white shadow-sm">
              <Trash2 className="h-4 w-4" />
            </div>
            <h3 className="truncate text-sm font-bold tracking-wide">
              {title}
            </h3>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1 text-slate-400 hover:bg-white/10 hover:text-white transition"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

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
      </div>
    </div>,
    document.body
  );
};

/* -------------------------------------------------------------------------- */
/* 7. MODAL EDITAR DADOS REGISTRADOS (FISCALIZAÇÕES E NCs/PAs)                */
/* -------------------------------------------------------------------------- */
