import React, { useState } from "react";
import { X, Plus, Trash2, Save, Tag } from "lucide-react";
import { toast } from "sonner";
import { useReportStore } from "../../store/useReportStore";
import { saveCustomNcsApi } from "../../services/api";
import { modalInputCls } from "./modalHelpers";

export const CustomNcModal: React.FC<{
  onSelectCallback?: (val: string) => void;
  onClose: () => void;
}> = ({ onSelectCallback, onClose }) => {
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

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-foreground/60 p-4 backdrop-blur-[1px]"
      role="dialog"
      aria-modal="true"
    >
      <div className="flex max-h-[88vh] w-full max-w-lg flex-col overflow-hidden rounded-2xl border border-border bg-card shadow-card-lg">
        <div className="flex items-center justify-between border-b border-border bg-navy-gradient px-5 py-4 text-primary-foreground">
          <h3 className="flex items-center gap-2 text-base font-bold">
            <Tag className="h-5 w-5 text-accent" />
            Não Conformidades Personalizadas (
            {isSocicam ? "SOCICAM" : "Rodovias"})
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
                Sigla (opcional)
              </label>
              <input
                type="text"
                value={sigla}
                onChange={(e) => setSigla(e.target.value)}
                placeholder={isSocicam ? "Ex: NC01" : "Ex: ABC"}
                className={modalInputCls}
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                Descrição Completa (obrigatório) *
              </label>
              <input
                type="text"
                value={descricao}
                onChange={(e) => setDescricao(e.target.value)}
                placeholder="Digite a descrição da não conformidade..."
                className={modalInputCls}
              />
            </div>
            <button
              type="submit"
              className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-xs font-semibold text-primary-foreground hover:bg-navy-2 transition"
            >
              <Plus className="h-4 w-4" />
              Cadastrar e Selecionar
            </button>
          </form>

          <div className="border-t border-border pt-3">
            <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Adicionadas Anteriormente ({currentList.length})
            </h4>
            {currentList.length === 0 ? (
              <p className="text-xs italic text-muted-foreground">
                Nenhuma não conformidade personalizada cadastrada ainda.
              </p>
            ) : (
              <div className="space-y-2">
                {currentList.map((it, idx) => {
                  const label = it.sigla
                    ? `${it.sigla} — ${it.descricao}`
                    : it.descricao;
                  const val = it.sigla || it.descricao;
                  return (
                    <div
                      key={`${val}_${idx}`}
                      className="flex items-center justify-between gap-2 rounded-xl border border-border bg-secondary/40 p-2.5"
                    >
                      <button
                        type="button"
                        onClick={() => {
                          if (onSelectCallback) onSelectCallback(val);
                          onClose();
                        }}
                        className="flex-1 truncate text-left text-xs font-semibold text-foreground hover:text-accent"
                      >
                        {label}
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDelete(idx)}
                        className="rounded-md p-1.5 text-nc hover:bg-nc-soft"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

/* -------------------------------------------------------------------------- */
/* 4. MODAL GALERIA DE FOTOS DO LEVANTAMENTO                                  */
/* -------------------------------------------------------------------------- */
