import React, { useState } from "react";
import { Plus, Trash2, Users, ShieldCheck, User, Hash, Briefcase, ChevronDown, UserPlus } from "lucide-react";
import { toast } from "sonner";
import { useReportStore } from "../../store/useReportStore";
import { saveCoordenadoresApi, saveResponsaveisApi } from "../../services/api";
import { useConcessionTheme } from "../../hooks/useConcessionTheme";
import { ThemedModalShell } from "./ThemedModalShell";

export const StaffManagerModal: React.FC<{
  mode: "responsaveis" | "coordenadores";
  onClose: () => void;
}> = ({ mode, onClose }) => {
  const {
    responsaveis,
    coordenadores,
    setResponsaveis,
    setCoordenadores,
  } = useReportStore();
  const theme = useConcessionTheme();

  const isResp = mode === "responsaveis";
  const items = isResp ? responsaveis : coordenadores;

  const [openSection, setOpenSection] = useState<"cadastrados" | "novo">("cadastrados");
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
    setOpenSection("cadastrados");
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
    <ThemedModalShell
      icon={isResp ? <Users className="h-4 w-4" /> : <ShieldCheck className="h-4 w-4" />}
      title={`${isResp ? "Pessoal Responsável" : "Coordenadores"} · ${items.length}`}
      onClose={onClose}
    >

        {/* Corpo com fundo temático suave e Accordions Exclusivos (apenas 1 aberto por vez) */}
        <div
          className="space-y-3 overflow-y-auto p-4 sm:p-5"
          style={{ backgroundColor: theme.lightBg }}
        >
          {/* Accordion 1: Cadastrados */}
          <div
            className="relative overflow-hidden rounded-2xl border bg-white shadow-xs transition-all"
            style={{
              borderColor:
                openSection === "cadastrados" ? theme.lightBorder : "rgba(226, 232, 240, 0.85)",
            }}
          >
            {openSection === "cadastrados" && (
              <span
                className="absolute left-0 top-3 bottom-3 w-1 rounded-r-full"
                style={{ backgroundColor: theme.primary }}
              />
            )}
            <button
              type="button"
              onClick={() =>
                setOpenSection((prev) => (prev === "cadastrados" ? "novo" : "cadastrados"))
              }
              aria-expanded={openSection === "cadastrados"}
              className="flex w-full items-center justify-between px-4 py-3.5 text-left transition hover:bg-slate-50/70"
            >
              <div className="flex items-center gap-3 min-w-0">
                <div
                  className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-white shadow-xs"
                  style={{ backgroundColor: theme.primary }}
                >
                  <Users className="h-4 w-4" />
                </div>
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <span
                      className="text-[11px] font-extrabold uppercase tracking-wider"
                      style={{ color: theme.primary }}
                    >
                      Cadastrados
                    </span>
                    <span
                      className="flex h-5 min-w-5 items-center justify-center rounded-full px-1.5 text-[10px] font-bold text-white"
                      style={{ backgroundColor: theme.primary }}
                    >
                      {items.length}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-500 truncate">
                    Pessoas já registradas
                  </p>
                </div>
              </div>
              <ChevronDown
                style={{ color: theme.primary }}
                className={`h-4 w-4 shrink-0 transition-transform duration-300 ${
                  openSection === "cadastrados" ? "rotate-180" : ""
                }`}
              />
            </button>

            <div
              className={`grid transition-all duration-300 ease-out ${
                openSection === "cadastrados"
                  ? "grid-rows-[1fr] opacity-100"
                  : "grid-rows-[0fr] opacity-0"
              }`}
            >
              <div className="overflow-hidden">
                <div className="border-t border-slate-100 bg-white px-4 pb-4 pt-3">
                  {items.length === 0 ? (
                    <p className="py-2 text-center text-xs italic text-slate-400">
                      Nenhum membro cadastrado ainda.
                    </p>
                  ) : (
                    <div className="max-h-60 space-y-2.5 overflow-y-auto pr-1">
                      {items.map((item, idx) => (
                        <div
                          key={`${item.nome}_${idx}`}
                          className="flex items-center justify-between gap-3 rounded-2xl border border-slate-200/85 bg-white p-3.5 shadow-2xs transition-all hover:border-slate-300"
                        >
                          <div className="min-w-0 flex-1">
                            <div
                              className="truncate text-xs font-bold text-slate-900"
                              title={item.nome}
                            >
                              {item.nome}
                            </div>
                            <div
                              className="mt-0.5 truncate text-[11px] text-slate-500"
                              title={item.funcao}
                            >
                              {item.funcao}
                            </div>
                            <div className="mt-1.5">
                              <span
                                className="inline-flex items-center rounded-full px-2.5 py-0.5 font-mono text-[10px] font-semibold"
                                style={{
                                  backgroundColor: theme.lightBg,
                                  color: theme.primary,
                                }}
                              >
                                Mat. {item.matricula}
                              </span>
                            </div>
                          </div>
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
              </div>
            </div>
          </div>

          {/* Accordion 2: Novo Responsável / Coordenador */}
          <div
            className="relative overflow-hidden rounded-2xl border bg-white shadow-xs transition-all"
            style={{
              borderColor:
                openSection === "novo" ? theme.lightBorder : "rgba(226, 232, 240, 0.85)",
            }}
          >
            {openSection === "novo" && (
              <span
                className="absolute left-0 top-3 bottom-3 w-1 rounded-r-full"
                style={{ backgroundColor: theme.primary }}
              />
            )}
            <button
              type="button"
              onClick={() =>
                setOpenSection((prev) => (prev === "novo" ? "cadastrados" : "novo"))
              }
              aria-expanded={openSection === "novo"}
              className="flex w-full items-center justify-between px-4 py-3.5 text-left transition hover:bg-slate-50/70"
            >
              <div className="flex items-center gap-3 min-w-0">
                <div
                  className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-white shadow-xs"
                  style={{ backgroundColor: theme.primary }}
                >
                  <UserPlus className="h-4 w-4" />
                </div>
                <div className="min-w-0">
                  <span
                    className="block text-[11px] font-extrabold uppercase tracking-wider"
                    style={{ color: theme.primary }}
                  >
                    {isResp ? "Novo Responsável" : "Novo Coordenador"}
                  </span>
                  <p className="text-[11px] text-slate-500 truncate">
                    Cadastre uma nova pessoa
                  </p>
                </div>
              </div>
              <ChevronDown
                style={{ color: theme.primary }}
                className={`h-4 w-4 shrink-0 transition-transform duration-300 ${
                  openSection === "novo" ? "rotate-180" : ""
                }`}
              />
            </button>

            <div
              className={`grid transition-all duration-300 ease-out ${
                openSection === "novo"
                  ? "grid-rows-[1fr] opacity-100"
                  : "grid-rows-[0fr] opacity-0"
              }`}
            >
              <div className="overflow-hidden">
                <form
                  onSubmit={handleAdd}
                  className="space-y-3 border-t border-slate-100 bg-white px-4 pb-4 pt-3"
                >
                  {/* Input Nome com Ícone User */}
                  <div className="relative">
                    <User className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                    <input
                      type="text"
                      value={nome}
                      onChange={(e) => setNome(e.target.value)}
                      placeholder="Nome completo"
                      className="h-11 w-full rounded-full border border-slate-200 bg-white pl-11 pr-4 text-xs font-medium text-slate-800 outline-none transition-all duration-200 hover:border-slate-300 focus:border-[var(--concession-primary)] focus:ring-2 focus:ring-[var(--concession-primary)]/20"
                    />
                  </div>

                  {/* Matrícula + Cargo/Função (1 col no celular, 2 cols em >= sm) */}
                  <div className="grid grid-cols-1 gap-2.5 sm:grid-cols-2">
                    <div className="relative">
                      <Hash className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                      <input
                        type="text"
                        value={matricula}
                        onChange={(e) => setMatricula(e.target.value)}
                        placeholder="Matrícula"
                        className="h-11 w-full rounded-full border border-slate-200 bg-white pl-10 pr-4 text-xs font-medium text-slate-800 outline-none transition-all duration-200 hover:border-slate-300 focus:border-[var(--concession-primary)] focus:ring-2 focus:ring-[var(--concession-primary)]/20"
                      />
                    </div>
                    <div className="relative">
                      <Briefcase className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                      <input
                        type="text"
                        value={funcao}
                        onChange={(e) => setFuncao(e.target.value)}
                        placeholder="Cargo / Função"
                        className="h-11 w-full truncate rounded-full border border-slate-200 bg-white pl-10 pr-4 text-xs font-medium text-slate-800 outline-none transition-all duration-200 hover:border-slate-300 focus:border-[var(--concession-primary)] focus:ring-2 focus:ring-[var(--concession-primary)]/20"
                      />
                    </div>
                  </div>

                  {/* Botão de Ação Largo e Tátil */}
                  <button
                    type="submit"
                    style={{ backgroundColor: theme.primary }}
                    className="flex h-11 w-full cursor-pointer items-center justify-center gap-2 rounded-full text-xs font-bold text-white shadow-sm transition-all duration-150 hover:brightness-110 active:scale-[0.98]"
                  >
                    <Plus className="h-4 w-4 stroke-[2.5]" />
                    <span>Adicionar {isResp ? "responsável" : "coordenador"}</span>
                  </button>
                </form>
              </div>
            </div>
          </div>
        </div>
    </ThemedModalShell>
  );
};
