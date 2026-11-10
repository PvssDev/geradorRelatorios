import React, { useState } from "react";
import { createPortal } from "react-dom";
import { X, Plus, Trash2, Users, ShieldCheck, User, Hash, Briefcase } from "lucide-react";
import { toast } from "sonner";
import { useReportStore } from "../../store/useReportStore";
import { saveCoordenadoresApi, saveResponsaveisApi } from "../../services/api";
import { useLockBodyScroll } from "../../hooks/useLockBodyScroll";

export const StaffManagerModal: React.FC<{
  mode: "responsaveis" | "coordenadores";
  onClose: () => void;
}> = ({ mode, onClose }) => {
  useLockBodyScroll(true);

  const { responsaveis, coordenadores, setResponsaveis, setCoordenadores } =
    useReportStore();

  const isResp = mode === "responsaveis";
  const items = isResp ? responsaveis : coordenadores;

  const [nome, setNome] = useState("");
  const [matricula, setMatricula] = useState("");
  const [funcao, setFuncao] = useState(
    isResp
      ? "Especialista em Regulação"
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
              {isResp ? (
                <Users className="h-4 w-4" />
              ) : (
                <ShieldCheck className="h-4 w-4" />
              )}
            </div>
            <h3 className="truncate text-sm font-bold tracking-wide">
              {isResp ? "Pessoal Responsável" : "Coordenadores"} · {items.length}
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
              + {isResp ? "NOVO RESPONSÁVEL" : "NOVO COORDENADOR"}
            </div>

            {/* Input Nome com Ícone User */}
            <div className="relative">
              <User className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 pointer-events-none" />
              <input
                type="text"
                value={nome}
                onChange={(e) => setNome(e.target.value)}
                placeholder="Nome completo"
                className="w-full h-11 rounded-2xl border border-slate-200 bg-[#f1f5f9] pl-10 pr-4 text-xs font-medium text-slate-800 outline-none transition-all duration-200 hover:border-blue-400 hover:bg-slate-100/80 focus:bg-white focus:border-blue-600 focus:ring-2 focus:ring-blue-600/20"
              />
            </div>

            {/* Linha dupla: Matrícula + Cargo/Função */}
            <div className="grid grid-cols-2 gap-2.5">
              <div className="relative">
                <Hash className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 pointer-events-none" />
                <input
                  type="text"
                  value={matricula}
                  onChange={(e) => setMatricula(e.target.value)}
                  placeholder="Matrícula"
                  className="w-full h-11 rounded-2xl border border-slate-200 bg-[#f1f5f9] pl-9 pr-3 text-xs font-medium text-slate-800 outline-none transition-all duration-200 hover:border-blue-400 hover:bg-slate-100/80 focus:bg-white focus:border-blue-600 focus:ring-2 focus:ring-blue-600/20"
                />
              </div>
              <div className="relative">
                <Briefcase className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 pointer-events-none" />
                <input
                  type="text"
                  value={funcao}
                  onChange={(e) => setFuncao(e.target.value)}
                  placeholder="Cargo / Função"
                  className="w-full h-11 rounded-2xl border border-slate-200 bg-[#f1f5f9] pl-9 pr-3 text-xs font-medium text-slate-800 outline-none transition-all duration-200 hover:border-blue-400 hover:bg-slate-100/80 focus:bg-white focus:border-blue-600 focus:ring-2 focus:ring-blue-600/20 truncate"
                />
              </div>
            </div>

            {/* Botão de Ação Largo e Tátil */}
            <button
              type="submit"
              className="w-full h-11 rounded-2xl bg-blue-600 hover:bg-blue-700 active:scale-[0.98] text-white font-bold text-xs shadow-sm transition-all duration-150 flex items-center justify-center gap-2 cursor-pointer"
            >
              <Plus className="h-4 w-4 stroke-[2.5]" />
              <span>Adicionar {isResp ? "responsável" : "coordenador"}</span>
            </button>
          </form>

          {/* Seção de Cadastrados */}
          <div className="border-t border-slate-200/80 pt-3 space-y-2.5">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                CADASTRADOS
              </span>
              <span className="flex h-5 items-center justify-center rounded-full bg-blue-100 px-2 text-[10px] font-bold text-blue-700">
                {items.length}
              </span>
            </div>

            {items.length === 0 ? (
              <p className="text-xs italic text-slate-400 py-2">
                Nenhum membro cadastrado ainda.
              </p>
            ) : (
              <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
                {items.map((item, idx) => (
                  <div
                    key={`${item.nome}_${idx}`}
                    className="flex items-center justify-between gap-3 rounded-2xl border border-blue-100 bg-[#f0f6fd] p-3 transition-all hover:border-blue-200 hover:shadow-xs"
                  >
                    <div className="min-w-0 flex-1">
                      <div
                        className="truncate text-xs font-bold text-slate-900"
                        title={item.nome}
                      >
                        {item.nome}
                      </div>
                      <div
                        className="truncate text-[11px] text-slate-500 mt-0.5"
                        title={item.funcao}
                      >
                        {item.funcao}
                      </div>
                      <div className="mt-1">
                        <span className="inline-flex items-center rounded-md border border-slate-200 bg-white px-2 py-0.5 text-[10px] font-mono font-medium text-slate-600 shadow-2xs">
                          Mat. {item.matricula}
                        </span>
                      </div>
                    </div>
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
      </div>
    </div>,
    document.body
  );
};
