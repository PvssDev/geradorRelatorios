import React, { useState } from "react";
import { Plus, Trash2, Users, ShieldCheck, User, Hash, Briefcase, UserPlus } from "lucide-react";
import { toast } from "sonner";
import { useReportStore } from "../../store/useReportStore";
import { saveCoordenadoresApi, saveResponsaveisApi } from "../../services/api";
import { useConcessionTheme } from "../../hooks/useConcessionTheme";
import { ThemedModalShell } from "./ThemedModalShell";
import { ExclusiveAccordionCard } from "./ExclusiveAccordionCard";

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

  const [openSection, setOpenSection] = useState<"cadastrados" | "novo" | null>("cadastrados");
  const [nome, setNome] = useState("");
  const [matricula, setMatricula] = useState("");
  const [funcao, setFuncao] = useState(
    isResp
      ? "Especialista em Regulação"
      : "Coordenador(a) de Transportes e Rodovias"
  );

  const toggleSection = (section: "cadastrados" | "novo") => {
    setOpenSection((prev) => (prev === section ? null : section));
  };

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
      <div
        className="space-y-3 overflow-y-auto p-4 sm:p-5"
        style={{ backgroundColor: theme.lightBg }}
      >
        <ExclusiveAccordionCard
          isOpen={openSection === "cadastrados"}
          onToggle={() => toggleSection("cadastrados")}
          icon={<Users className="h-4 w-4" />}
          title="Cadastrados"
          subtitle="Pessoas já registradas"
          count={items.length}
          primaryColor={theme.primary}
          borderColor={theme.lightBorder}
        >
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
        </ExclusiveAccordionCard>

        <ExclusiveAccordionCard
          isOpen={openSection === "novo"}
          onToggle={() => toggleSection("novo")}
          icon={<UserPlus className="h-4 w-4" />}
          title={isResp ? "Novo Responsável" : "Novo Coordenador"}
          subtitle="Cadastre uma nova pessoa"
          primaryColor={theme.primary}
          borderColor={theme.lightBorder}
        >
          <form
            onSubmit={handleAdd}
            className="space-y-3 border-t border-slate-100 bg-white px-4 pb-4 pt-3"
          >
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

            <button
              type="submit"
              style={{ backgroundColor: theme.primary }}
              className="flex h-11 w-full cursor-pointer items-center justify-center gap-2 rounded-full text-xs font-bold text-white shadow-sm transition-all duration-150 hover:brightness-110 active:scale-[0.98]"
            >
              <Plus className="h-4 w-4 stroke-[2.5]" />
              <span>Adicionar {isResp ? "responsável" : "coordenador"}</span>
            </button>
          </form>
        </ExclusiveAccordionCard>
      </div>
    </ThemedModalShell>
  );
};
