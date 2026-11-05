import React, { useState } from "react";
import { X, Plus, Trash2, Save, Users, ShieldCheck } from "lucide-react";
import { toast } from "sonner";
import { useReportStore } from "../../store/useReportStore";
import { saveCoordenadoresApi, saveResponsaveisApi } from "../../services/api";
import { modalInputCls } from "./modalHelpers";

export const StaffManagerModal: React.FC<{
  mode: "responsaveis" | "coordenadores";
  onClose: () => void;
}> = ({ mode, onClose }) => {
  const { responsaveis, coordenadores, setResponsaveis, setCoordenadores } =
    useReportStore();

  const isResp = mode === "responsaveis";
  const items = isResp ? responsaveis : coordenadores;

  const [nome, setNome] = useState("");
  const [matricula, setMatricula] = useState("");
  const [funcao, setFuncao] = useState(
    isResp
      ? "Analista de Regulação"
      : "Coordenador(a) de Transportes e Rodovias"
  );

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!nome.trim() || !matricula.trim() || !funcao.trim()) {
      toast.error("Preencha Nome, Matrícula e Função/Cargo.");
      return;
    }
    const exists = items.some(
      (i) => i.nome.trim().toLowerCase() === nome.trim().toLowerCase()
    );
    if (exists) {
      toast.warning("Este nome já está cadastrado.");
      return;
    }
    const nextList = [
      ...items,
      {
        nome: nome.trim(),
        matricula: matricula.trim(),
        funcao: funcao.trim(),
      },
    ];
    if (isResp) {
      setResponsaveis(nextList);
      await saveResponsaveisApi(nextList).catch(() => {});
    } else {
      setCoordenadores(nextList);
      await saveCoordenadoresApi(nextList).catch(() => {});
    }
    toast.success(`'${nome.trim()}' adicionado com sucesso!`);
    setNome("");
    setMatricula("");
  };

  const handleRemove = async (idx: number) => {
    const nextList = items.filter((_, i) => i !== idx);
    if (isResp) {
      setResponsaveis(nextList);
      await saveResponsaveisApi(nextList).catch(() => {});
    } else {
      setCoordenadores(nextList);
      await saveCoordenadoresApi(nextList).catch(() => {});
    }
    toast.info("Item removido.");
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
            {isResp ? (
              <Users className="h-5 w-5 text-accent" />
            ) : (
              <ShieldCheck className="h-5 w-5 text-accent" />
            )}
            {isResp
              ? "Gerenciar Pessoal Responsável"
              : "Gerenciar Coordenadores"}
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
                Nome Completo *
              </label>
              <input
                type="text"
                value={nome}
                onChange={(e) => setNome(e.target.value)}
                placeholder="Digite o nome completo..."
                className={modalInputCls}
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                  Matrícula *
                </label>
                <input
                  type="text"
                  value={matricula}
                  onChange={(e) => setMatricula(e.target.value)}
                  placeholder="Ex: 40672015/01"
                  className={modalInputCls}
                />
              </div>
              <div>
                <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                  Função / Cargo *
                </label>
                <input
                  type="text"
                  value={funcao}
                  onChange={(e) => setFuncao(e.target.value)}
                  className={modalInputCls}
                />
              </div>
            </div>
            <button
              type="submit"
              className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-xs font-semibold text-primary-foreground hover:bg-navy-2 transition"
            >
              <Plus className="h-4 w-4" />
              Adicionar {isResp ? "Responsável" : "Coordenador"}
            </button>
          </form>

          <div className="border-t border-border pt-3">
            <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Cadastrados ({items.length})
            </h4>
            <div className="space-y-2">
              {items.map((item, idx) => (
                <div
                  key={`${item.nome}_${idx}`}
                  className="flex items-center justify-between gap-2 rounded-xl border border-border bg-secondary/40 p-2.5"
                >
                  <div>
                    <p className="text-xs font-semibold text-foreground">
                      {item.nome}
                    </p>
                    <p className="text-[11px] text-muted-foreground">
                      {item.funcao} • Matrícula: {item.matricula}
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleRemove(idx)}
                    className="rounded-md p-1.5 text-nc hover:bg-nc-soft"
                    title="Remover"
                  >
                    <Trash2 className="h-4 w-4" />
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
/* 2. MODAL GERENCIAR CONTRATOS                                               */
/* -------------------------------------------------------------------------- */
