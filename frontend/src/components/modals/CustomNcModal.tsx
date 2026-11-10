import React, { useState } from "react";
import { createPortal } from "react-dom";
import { X, Plus, Trash2, Tag, FileText } from "lucide-react";
import { toast } from "sonner";
import { useReportStore } from "../../store/useReportStore";
import { saveCustomNcsApi } from "../../services/api";
import { useLockBodyScroll } from "../../hooks/useLockBodyScroll";

export const CustomNcModal: React.FC<{
  onSelectCallback?: (val: string) => void;
  onClose: () => void;
}> = ({ onSelectCallback, onClose }) => {
  useLockBodyScroll(true);

  const {
    tipoRelatorio,
    customNcs,
    customNcsSocicam,
    setCustomNcs,
    setCustomNcsSocicam,
  } = useReportStore();

  const isSocicam = tipoRelatorio === "SOCICAM";
  const currentList = isSocicam ? customNcsSocicam : customNcs;

  const [sigla, setSigla] = useState("");
  const [descricao, setDescricao] = useState("");

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    const descClean = descricao.trim();
    const siglaClean = sigla.trim().toUpperCase();
    if (!descClean) {
      toast.error("O campo 'Descrição' é obrigatório.");
      return;
    }

    const nextList = [
      ...currentList,
      { sigla: siglaClean, descricao: descClean },
    ];
    if (isSocicam) {
      setCustomNcsSocicam(nextList);
      await saveCustomNcsApi(nextList, true).catch(() => {});
    } else {
      setCustomNcs(nextList);
      await saveCustomNcsApi(nextList, false).catch(() => {});
    }

    const valToSelect = siglaClean || descClean;
    if (onSelectCallback) onSelectCallback(valToSelect);
    toast.success("Nova Não Conformidade cadastrada e selecionada!");
    onClose();
  };

  const handleDelete = async (idx: number) => {
    const nextList = currentList.filter((_, i) => i !== idx);
    if (isSocicam) {
      setCustomNcsSocicam(nextList);
      await saveCustomNcsApi(nextList, true).catch(() => {});
    } else {
      setCustomNcs(nextList);
      await saveCustomNcsApi(nextList, false).catch(() => {});
    }
    toast.info("Não Conformidade personalizada removida.");
  };

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-md"
      role="dialog"
      aria-modal="true"
    >
      <div className="flex max-h-[90vh] w-full max-w-md flex-col overflow-hidden rounded-[28px] border border-slate-700/30 bg-white shadow-2xl animate-in fade-in zoom-in-95 duration-150">
        {/* Topo Dark Navy Executivo com Ícone em Badge */}
        <div className="flex items-center justify-between border-b border-slate-800 bg-[#0b1728] px-5 py-4 text-white">
          <div className="flex items-center gap-3 min-w-0">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-blue-600 text-white shadow-sm">
              <Tag className="h-4 w-4" />
            </div>
            <h3 className="truncate text-sm font-bold tracking-wide">
              Não Conformidades · {currentList.length}
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

        {/* Corpo com Formulário e Lista de Cadastrados */}
        <div className="space-y-4 overflow-y-auto p-5">
          <form onSubmit={handleAdd} className="space-y-3">
            <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
              + NOVA NÃO CONFORMIDADE ({isSocicam ? "SOCICAM" : "RODOVIAS"})
            </div>

            <div className="relative">
              <Tag className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 pointer-events-none" />
              <input
                type="text"
                value={sigla}
                onChange={(e) => setSigla(e.target.value)}
                placeholder={isSocicam ? "Sigla opcional (Ex: NC01)" : "Sigla opcional (Ex: ABC)"}
                className="w-full h-11 rounded-2xl border border-slate-200 bg-[#f1f5f9] pl-10 pr-4 text-xs font-medium text-slate-800 outline-none transition-all duration-200 hover:border-blue-400 hover:bg-slate-100/80 focus:bg-white focus:border-blue-600 focus:ring-2 focus:ring-blue-600/20"
              />
            </div>

            <div className="relative">
              <FileText className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 pointer-events-none" />
              <input
                type="text"
                value={descricao}
                onChange={(e) => setDescricao(e.target.value)}
                placeholder="Descrição completa da irregularidade *"
                className="w-full h-11 rounded-2xl border border-slate-200 bg-[#f1f5f9] pl-10 pr-4 text-xs font-medium text-slate-800 outline-none transition-all duration-200 hover:border-blue-400 hover:bg-slate-100/80 focus:bg-white focus:border-blue-600 focus:ring-2 focus:ring-blue-600/20"
              />
            </div>

            <button
              type="submit"
              className="w-full h-11 rounded-2xl bg-blue-600 hover:bg-blue-700 active:scale-[0.98] text-white font-bold text-xs shadow-sm transition-all duration-150 flex items-center justify-center gap-2 cursor-pointer"
            >
              <Plus className="h-4 w-4 stroke-[2.5]" />
              <span>Cadastrar e selecionar</span>
            </button>
          </form>

          {/* Seção de Não Conformidades Cadastradas */}
          <div className="border-t border-slate-200/80 pt-3 space-y-2.5">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                CADASTRADAS
              </span>
              <span className="flex h-5 items-center justify-center rounded-full bg-blue-100 px-2 text-[10px] font-bold text-blue-700">
                {currentList.length}
              </span>
            </div>

            {currentList.length === 0 ? (
              <p className="text-xs italic text-slate-400 py-2">
                Nenhuma não conformidade personalizada cadastrada ainda.
              </p>
            ) : (
              <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
                {currentList.map((it, idx) => {
                  const val = it.sigla || it.descricao;
                  return (
                    <div
                      key={`${val}_${idx}`}
                      className="flex items-center justify-between gap-3 rounded-2xl border border-blue-100 bg-[#f0f6fd] p-3 transition-all hover:border-blue-200 hover:shadow-xs"
                    >
                      <button
                        type="button"
                        onClick={() => {
                          if (onSelectCallback) onSelectCallback(val);
                          onClose();
                        }}
                        className="flex-1 text-left min-w-0"
                        title={`Clique para selecionar: ${it.descricao}`}
                      >
                        {it.sigla && (
                          <span className="inline-flex items-center rounded-md border border-blue-200 bg-white px-2 py-0.5 text-[10px] font-mono font-bold text-blue-700 shadow-2xs mr-2">
                            {it.sigla}
                          </span>
                        )}
                        <span className="text-xs font-semibold text-slate-900 truncate">
                          {it.descricao}
                        </span>
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDelete(idx)}
                        className="rounded-lg p-1.5 text-slate-400 hover:bg-rose-50 hover:text-rose-600 transition shrink-0"
                        title="Remover"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>,
    document.body
  );
};
