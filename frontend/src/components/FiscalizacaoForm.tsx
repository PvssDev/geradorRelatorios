import React, { useEffect, useState, type ReactNode } from "react";
import {
  Building2,
  Plus,
  Settings,
  X,
  UserCheck,
  ChevronDown,
  Users,
} from "lucide-react";
import { toast } from "sonner";
import { Card } from "./Card";
import { ConfirmDeleteModal } from "./Modals";
import { useReportStore } from "../store/useReportStore";
import { FiscalizacaoItem } from "../types/report.types";
import { getConcessionTheme } from "../utils/concessionTheme";

interface FiscalizacaoFormProps {
  onOpenResponsaveisModal: () => void;
  onOpenCoordenadoresModal: () => void;
  onOpenContratosModal: (onSelectContrato?: (c: string) => void) => void;
}

const inputCls =
  "w-full h-[42px] rounded-xl border border-[#d0e1f3] bg-[#f0f6fc] px-3.5 py-2 text-sm text-[#0f172a] font-medium outline-none transition-all duration-200 hover:border-primary/50 hover:bg-[#eaf3fc] hover:shadow-xs focus:border-primary focus:bg-white focus:ring-2 focus:ring-primary/20";

const pillFisc = (on: boolean) =>
  `rounded-xl px-3.5 py-1.5 text-xs font-semibold transition-all duration-150 ${
    on
      ? "text-white font-bold border-0 shadow-sm"
      : "border border-slate-300 bg-white text-slate-700 hover:bg-slate-50 hover:border-slate-400 font-semibold shadow-xs"
  }`;

function formatNomeAbreviado(nomeCompleto: string, compactar: boolean): string {
  if (!compactar) return nomeCompleto;
  const partes = nomeCompleto.trim().split(/\s+/);
  if (partes.length <= 1) return nomeCompleto;
  const primeiro = partes[0];
  const ultimo = partes[partes.length - 1];
  return `${primeiro} ${ultimo.charAt(0)}.`;
}

function Field({
  label,
  rightElement,
  children,
}: {
  label: string;
  rightElement?: ReactNode;
  children: ReactNode;
}) {
  return (
    <div className="space-y-1.5">
      <div className="flex h-5 items-center justify-between gap-2">
        <span className="text-[11px] font-bold uppercase tracking-wider text-[#1e3a5a] truncate">
          {label}
        </span>
        {rightElement}
      </div>
      {children}
    </div>
  );
}

function getTodayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

function isoToBr(iso: string): string {
  if (!iso) return "";
  const parts = iso.split("-");
  return parts.length === 3 ? `${parts[2]}/${parts[1]}/${parts[0]}` : iso;
}

function brToIso(br: string): string {
  if (!br || br.startsWith("=")) return getTodayIso();
  const parts = br.split("/");
  return parts.length === 3 ? `${parts[2]}-${parts[1]}-${parts[0]}` : getTodayIso();
}

function formatarPeriodoVistoria(inicioIso: string, fimIso: string): string {
  if (!inicioIso) return "";
  if (!fimIso || fimIso === inicioIso) {
    return isoToBr(inicioIso);
  }
  const [y1, m1, d1] = inicioIso.split("-");
  const [y2, m2, d2] = fimIso.split("-");
  if (!y1 || !y2) return isoToBr(inicioIso);

  if (y1 !== y2) {
    return `${d1}/${m1}/${y1} a ${d2}/${m2}/${y2}`;
  }
  if (m1 !== m2) {
    return `${d1}/${m1} a ${d2}/${m2}/${y2}`;
  }
  return `${d1} a ${d2}/${m2}/${y2}`;
}

function desmembrarPeriodoEmDatas(periodoStr: string, fallbackDataIso: string): { inicioIso: string; fimIso: string } {
  if (!periodoStr || periodoStr.trim() === "" || periodoStr.startsWith("=")) {
    return { inicioIso: fallbackDataIso, fimIso: fallbackDataIso };
  }
  const s = periodoStr.trim();
  // 1. "DD a DD/MM/AAAA"
  const m1 = s.match(/^(\d{1,2})\s*(?:a|à|-|e)\s*(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
  if (m1) {
    const [, d1, d2, m, y] = m1;
    const iso1 = `${y}-${m.padStart(2, "0")}-${d1.padStart(2, "0")}`;
    const iso2 = `${y}-${m.padStart(2, "0")}-${d2.padStart(2, "0")}`;
    return { inicioIso: iso1, fimIso: iso2 };
  }
  // 2. "DD/MM a DD/MM/AAAA"
  const m2 = s.match(/^(\d{1,2})\/(\d{1,2})\s*(?:a|à|-|e)\s*(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
  if (m2) {
    const [, d1, m1Val, d2, m2Val, y] = m2;
    const iso1 = `${y}-${m1Val.padStart(2, "0")}-${d1.padStart(2, "0")}`;
    const iso2 = `${y}-${m2Val.padStart(2, "0")}-${d2.padStart(2, "0")}`;
    return { inicioIso: iso1, fimIso: iso2 };
  }
  // 3. "DD/MM/AAAA a DD/MM/AAAA"
  const m3 = s.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})\s*(?:a|à|-|e)\s*(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
  if (m3) {
    const [, d1, m1Val, y1, d2, m2Val, y2] = m3;
    const iso1 = `${y1}-${m1Val.padStart(2, "0")}-${d1.padStart(2, "0")}`;
    const iso2 = `${y2}-${m2Val.padStart(2, "0")}-${d2.padStart(2, "0")}`;
    return { inicioIso: iso1, fimIso: iso2 };
  }
  // 4. "DD/MM/AAAA"
  const m4 = s.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
  if (m4) {
    const [, d, m, y] = m4;
    const iso = `${y}-${m.padStart(2, "0")}-${d.padStart(2, "0")}`;
    return { inicioIso: iso, fimIso: iso };
  }
  return { inicioIso: fallbackDataIso, fimIso: fallbackDataIso };
}

export const FiscalizacaoForm: React.FC<FiscalizacaoFormProps> = ({
  onOpenResponsaveisModal,
  onOpenCoordenadoresModal,
  onOpenContratosModal,
}) => {
  const {
    tipoRelatorio,
    categoriaRelatorio,
    responsaveis,
    coordenadores,
    contratos,
    contratosPadrao,
    locaisSocicam,
    getActiveWorkspace,
    setActiveFiscalizacaoIndex,
    addFiscalizacao,
    upsertActiveFiscalizacao,
    deleteFiscalizacoesBulk,
  } = useReportStore();

  const [fiscIndexToDelete, setFiscIndexToDelete] = useState<number | null>(null);

  const ws = getActiveWorkspace();
  const theme = getConcessionTheme(tipoRelatorio, categoriaRelatorio);
  const isMonitoring = categoriaRelatorio === "Monitoramento";
  const activeIdx = Math.max(
    0,
    Math.min(ws.activeFiscalizacaoIndex, Math.max(0, ws.fiscalizacoes.length - 1))
  );
  const activeFisc = ws.fiscalizacoes[activeIdx];

  const defaultLocal =
    tipoRelatorio === "CRA"
      ? "Rota do Atlântico"
      : tipoRelatorio === "CRC"
      ? "Sistema Viário do Paiva"
      : locaisSocicam[5] || "TIP Recife";

  const allRespNames = responsaveis.map((r) => r.nome);

  const [idFisc, setIdFisc] = useState(activeFisc?.["ID da Fiscalização"] || "");
  const [dataIso, setDataIso] = useState(
    activeFisc?.Data ? brToIso(activeFisc.Data) : getTodayIso()
  );
  const [dataFimIso, setDataFimIso] = useState(() => {
    const fallbackIso = activeFisc?.Data ? brToIso(activeFisc.Data) : getTodayIso();
    return desmembrarPeriodoEmDatas(activeFisc?.Período || "", fallbackIso).fimIso;
  });
  const [periodo, setPeriodo] = useState(
    activeFisc?.Período || isoToBr(getTodayIso())
  );
  const [hora, setHora] = useState(activeFisc?.Hora || "");
  const [mun, setMun] = useState(activeFisc?.Cidade || "");
  const [local, setLocal] = useState(activeFisc?.Local || defaultLocal);
  const [contrato, setContrato] = useState(
    activeFisc?.Contrato || contratosPadrao[tipoRelatorio] || "CT. nº 043/2011"
  );
  const [equipe, setEquipe] = useState<string[]>(
    activeFisc?.["Pessoal Responsável"]
      ? activeFisc["Pessoal Responsável"].startsWith("=")
        ? []
        : activeFisc["Pessoal Responsável"]
            .split(/[,;]/)
            .map((s) => s.trim())
            .filter(Boolean)
      : []
  );
  const [coord, setCoord] = useState(
    activeFisc?.Coordenador || coordenadores[0]?.nome || ""
  );

  const activeCoord =
    coordenadores.find((c) => c.nome === coord) ||
    coordenadores[0] ||
    null;

  // Sincroniza quando alterna modalidade, índice ativo ou quando "Auto preenchimento" hidrata o workspace
  useEffect(() => {
    const idx = Math.max(
      0,
      Math.min(
        ws.activeFiscalizacaoIndex,
        Math.max(0, ws.fiscalizacoes.length - 1)
      )
    );
    const f = ws.fiscalizacoes[idx];
    if (f) {
      const fDataIso = f.Data ? brToIso(f.Data) : getTodayIso();
      const { inicioIso, fimIso } = desmembrarPeriodoEmDatas(f.Período || "", fDataIso);
      setIdFisc(f["ID da Fiscalização"] || "");
      setDataIso(inicioIso);
      setDataFimIso(fimIso);
      setPeriodo(
        f.Período && !f.Período.startsWith("=")
          ? f.Período
          : formatarPeriodoVistoria(inicioIso, fimIso)
      );
      setHora(f.Hora && !f.Hora.startsWith("=") ? f.Hora : "");
      setMun(f.Cidade && !f.Cidade.startsWith("=") ? f.Cidade : "");
      setLocal(f.Local && !f.Local.startsWith("=") ? f.Local : defaultLocal);
      setContrato(
        f.Contrato || contratosPadrao[tipoRelatorio] || "CT. nº 043/2011"
      );
      setEquipe(
        f["Pessoal Responsável"]
          ? f["Pessoal Responsável"].startsWith("=")
            ? []
            : f["Pessoal Responsável"]
                .split(/[,;]/)
                .map((s) => s.trim())
                .filter(Boolean)
          : []
      );
      setCoord(f.Coordenador || coordenadores[0]?.nome || "");
    } else {
      const today = getTodayIso();
      setIdFisc("");
      setDataIso(today);
      setDataFimIso(today);
      setPeriodo(isoToBr(today));
      setHora("");
      setMun("");
      setLocal(defaultLocal);
      setContrato(contratosPadrao[tipoRelatorio] || "CT. nº 043/2011");
      setEquipe([]);
      setCoord(coordenadores[0]?.nome || "");
    }
  }, [
    tipoRelatorio,
    categoriaRelatorio,
    ws.fiscalizacoes,
    ws.activeFiscalizacaoIndex,
    contratosPadrao,
    defaultLocal,
    coordenadores,
    responsaveis,
  ]);

  const buildItem = (
    overrides: Partial<{
      id: string;
      data: string;
      periodo: string;
      hora: string;
      mun: string;
      local: string;
      contrato: string;
      equipe: string[];
      coord: string;
    }> = {}
  ): FiscalizacaoItem => {
    const nextId = overrides.id !== undefined ? overrides.id : idFisc;
    const nextData = overrides.data !== undefined ? overrides.data : dataIso;
    const dataBr = isoToBr(nextData);
    const nextPeriodo =
      overrides.periodo !== undefined
        ? overrides.periodo
        : periodo.trim() || dataBr;
    const nextHora =
      tipoRelatorio === "CRA"
        ? overrides.hora !== undefined
          ? overrides.hora
          : hora
        : "";
    const nextLocal =
      overrides.local !== undefined
        ? overrides.local
        : local.trim() || defaultLocal;
    const nextMun =
      tipoRelatorio === "CRA"
        ? overrides.mun !== undefined
          ? overrides.mun
          : mun
        : tipoRelatorio === "SOCICAM"
        ? nextLocal
        : "";
    const nextContrato =
      overrides.contrato !== undefined ? overrides.contrato : contrato;
    const nextEquipe =
      overrides.equipe !== undefined ? overrides.equipe : equipe;
    const nextCoord = overrides.coord !== undefined ? overrides.coord : coord;

    return {
      "ID da Fiscalização": nextId,
      Data: dataBr,
      Hora: nextHora,
      Cidade: nextMun,
      Local: nextLocal,
      "Pessoal Responsável": nextEquipe.join(", "),
      Coordenador: nextCoord || coordenadores[0]?.nome || "",
      Contrato: nextContrato,
      Período: nextPeriodo,
      "Relatório Gerado": false,
    };
  };

  const syncToStore = (
    overrides: Partial<{
      id: string;
      data: string;
      periodo: string;
      hora: string;
      mun: string;
      local: string;
      contrato: string;
      equipe: string[];
      coord: string;
    }>
  ) => {
    upsertActiveFiscalizacao(buildItem(overrides));
  };

  const handleAddNewHeader = () => {
    const prefix = isMonitoring ? "MON" : "FISC";
    const year = dataIso.slice(0, 4) || String(new Date().getFullYear());
    let seq = ws.fiscalizacoes.length + 1;
    let candidateId = `${prefix}-${tipoRelatorio}-${year}-${String(seq).padStart(
      3,
      "0"
    )}`;
    const existingIds = new Set(
      ws.fiscalizacoes.map((f) =>
        (f["ID da Fiscalização"] || "").trim().toLowerCase()
      )
    );
    while (existingIds.has(candidateId.toLowerCase())) {
      seq += 1;
      candidateId = `${prefix}-${tipoRelatorio}-${year}-${String(seq).padStart(
        3,
        "0"
      )}`;
    }

    // Se ainda não havia nenhuma fiscalização salva e o usuário preencheu algo, salva a primeira antes
    if (ws.fiscalizacoes.length === 0) {
      const firstId = idFisc.trim() || candidateId;
      const resFirst = addFiscalizacao(buildItem({ id: firstId }));
      if (resFirst.ok) {
        toast.success(
          `${isMonitoring ? "Monitoramento" : "Fiscalização"} '${firstId}' registrado(a)!`
        );
      } else if (resFirst.error) {
        toast.error(resFirst.error);
      }
      return;
    }

    const today = getTodayIso();
    const newItem: FiscalizacaoItem = {
      "ID da Fiscalização": candidateId,
      Data: isoToBr(today),
      Hora: tipoRelatorio === "CRA" ? "09:00" : "",
      Cidade:
        tipoRelatorio === "CRA"
          ? "Cabo de Santo Agostinho / Ipojuca"
          : tipoRelatorio === "SOCICAM"
          ? defaultLocal
          : "",
      Local: defaultLocal,
      "Pessoal Responsável": "",
      Coordenador: coordenadores[0]?.nome || "",
      Contrato: contratosPadrao[tipoRelatorio] || "CT. nº 043/2011",
      Período: isoToBr(today),
      "Relatório Gerado": false,
    };

    const res = addFiscalizacao(newItem);
    if (res.ok) {
      toast.success(
        `Novo cabeçalho '${candidateId}' criado! Cada ID gera um relatório independente.`
      );
    } else if (res.error) {
      toast.error(res.error);
    }
  };

  const handleRequestDeleteFisc = (idx: number) => {
    const targetFisc = ws.fiscalizacoes[idx];
    if (!targetFisc) return;
    const targetId = (targetFisc["ID da Fiscalização"] || "").trim();

    // Verifica se esta fiscalização possui ocorrências vinculadas
    const regsVinculados = targetId
      ? ws.registrosNc.filter((r) => (r["ID da Fiscalização"] || "").trim() === targetId)
      : [];

    if (regsVinculados.length > 0) {
      // Possui ocorrências: abre pop-up de confirmação
      setFiscIndexToDelete(idx);
    } else {
      // Sem ocorrências: apaga diretamente
      deleteFiscalizacoesBulk([targetId]);
      toast.success(
        `Fiscalização '${targetId || `#${idx + 1}`}' apagada com sucesso.`
      );
    }
  };

  const handleConfirmDeleteFisc = () => {
    if (fiscIndexToDelete === null) return;
    const targetFisc = ws.fiscalizacoes[fiscIndexToDelete];
    const targetId = (targetFisc?.["ID da Fiscalização"] || "").trim();
    deleteFiscalizacoesBulk([targetId]);
    setFiscIndexToDelete(null);
    toast.success(
      `Fiscalização '${targetId || `#${fiscIndexToDelete + 1}`}' e seus registros foram apagados.`
    );
  };

  // Garante que o contrato atual apareça no select mesmo que customizado
  const contratosDisponiveis = Array.from(
    new Set([
      ...(contratosPadrao[tipoRelatorio] ? [contratosPadrao[tipoRelatorio]] : []),
      ...contratos,
      ...(contrato ? [contrato] : []),
    ])
  );

  return (
    <Card
      n={1}
      icon={<Building2 className="h-5 w-5" />}
      title={
        isMonitoring
          ? "Informações do Monitoramento"
          : "Informações da Fiscalização"
      }
    >
      {/* Barra de Múltiplos IDs de Fiscalização / Monitoramento */}
      <div className="mb-6 flex flex-wrap items-center justify-between gap-2 rounded-2xl border border-[#d6e5f5] bg-[#edf4fb] px-4 py-3">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-[11px] font-bold uppercase tracking-wider text-[#1e3a5a]">
            {isMonitoring ? "Monitoramentos ativos:" : "Fiscalizações ativas:"}
          </span>
          {ws.fiscalizacoes.length === 0 ? (
            <span className="text-xs text-muted-foreground">
              Preencha os campos abaixo (sincronização automática)
            </span>
          ) : (
            ws.fiscalizacoes.map((f, idx) => {
              const label =
                f["ID da Fiscalização"]?.trim() || `#${idx + 1} (Sem ID)`;
              const isAct = idx === activeIdx;
              return (
                <div
                  key={`${label}_${idx}`}
                  className="group relative inline-flex items-center"
                >
                  <button
                    type="button"
                    onClick={() => setActiveFiscalizacaoIndex(idx)}
                    className={`${pillFisc(isAct)} inline-flex items-center gap-1.5 pr-2`}
                    style={
                      isAct
                        ? { backgroundColor: theme.primary }
                        : { borderColor: theme.primary + "60", color: theme.primary }
                    }
                  >
                    <span>{label}</span>
                    <span
                      role="button"
                      tabIndex={0}
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRequestDeleteFisc(idx);
                      }}
                      className={`inline-flex h-4 w-4 items-center justify-center rounded-full transition-all ${
                        isAct
                          ? "hover:bg-white/30 text-white"
                          : "hover:bg-rose-100 hover:text-rose-600 text-slate-400 group-hover:text-slate-600"
                      }`}
                      title={`Apagar fiscalização ${label}`}
                    >
                      <X className="h-3 w-3 stroke-[2.5]" />
                    </span>
                  </button>
                </div>
              );
            })
          )}
        </div>

        <button
          type="button"
          onClick={handleAddNewHeader}
          className="inline-flex items-center gap-1.5 rounded-xl border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 shadow-xs hover:bg-slate-50 hover:text-slate-900 hover:border-slate-400 active:scale-[0.98] transition-all"
          title="Cadastrar mais um ID para gerar múltiplos relatórios no mesmo lote"
        >
          <Plus className="h-3.5 w-3.5" />
            {ws.fiscalizacoes.length === 0
              ? isMonitoring
                ? "Fixar ID Inicial"
                : "Fixar ID Inicial"
              : isMonitoring
              ? "Novo Monitoramento"
              : "Nova Fiscalização"}
          </button>
        </div>

      <div className="grid gap-8">
        {/* Linha 1: ID + Data de Início + Data de Término (com visualização do Período) */}
        <div className="grid gap-6 sm:grid-cols-3">
          <Field
            label={isMonitoring ? "ID do Monitoramento" : "ID da Fiscalização"}
          >
            <input
              className={inputCls}
              placeholder={`${
                isMonitoring ? "MON" : "FISC"
              }-${tipoRelatorio}-${new Date().getFullYear()}-001`}
              value={idFisc}
              onChange={(e) => {
                setIdFisc(e.target.value);
                syncToStore({ id: e.target.value });
              }}
            />
          </Field>

          <Field label="Data de Início da Vistoria">
            <input
              type="date"
              className={inputCls}
              value={dataIso}
              onChange={(e) => {
                const nextIni = e.target.value;
                setDataIso(nextIni);
                const nextFim = dataFimIso < nextIni ? nextIni : dataFimIso;
                setDataFimIso(nextFim);
                const nextPer = formatarPeriodoVistoria(nextIni, nextFim);
                setPeriodo(nextPer);
                syncToStore({
                  data: nextIni,
                  periodo: nextPer,
                });
              }}
            />
          </Field>

          <Field
            label="Data de Término da Vistoria"
            rightElement={
              <span className="inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-bold bg-blue-50 text-blue-700 border border-blue-200 shrink-0">
                Período: {periodo || isoToBr(dataIso)}
              </span>
            }
          >
            <input
              type="date"
              className={inputCls}
              min={dataIso}
              value={dataFimIso}
              onChange={(e) => {
                const nextFim = e.target.value;
                setDataFimIso(nextFim);
                const nextPer = formatarPeriodoVistoria(dataIso, nextFim);
                setPeriodo(nextPer);
                syncToStore({
                  data: dataIso,
                  periodo: nextPer,
                });
              }}
            />
          </Field>
        </div>

        {/* Linha 2: Campos específicos da Concessão (CRA vs CRC vs SOCICAM) */}
        {tipoRelatorio === "CRA" ? (
          <div className="grid gap-6 sm:grid-cols-4">
            <Field label="Cidade (Município)">
              <input
                className={inputCls}
                placeholder="Cabo de Santo Agostinho / Ipojuca"
                value={mun}
                onChange={(e) => {
                  setMun(e.target.value);
                  syncToStore({ mun: e.target.value });
                }}
              />
            </Field>

            <Field label="Local / Rodovia">
              <input
                className={inputCls}
                placeholder="Rota do Atlântico"
                value={local}
                onChange={(e) => {
                  setLocal(e.target.value);
                  syncToStore({ local: e.target.value });
                }}
              />
            </Field>

            <Field label="Hora">
              <input
                type="time"
                className={inputCls}
                value={hora}
                onChange={(e) => {
                  setHora(e.target.value);
                  syncToStore({ hora: e.target.value });
                }}
              />
            </Field>

            <Field
              label="Contrato"
              rightElement={
                <button
                  type="button"
                  onClick={() =>
                    onOpenContratosModal((c) => {
                      setContrato(c);
                      syncToStore({ contrato: c });
                    })
                  }
                  className="text-[11px] font-medium text-muted-foreground hover:text-accent transition shrink-0"
                >
                  + Gerenciar
                </button>
              }
            >
              <div className="relative">
                <select
                  className={`${inputCls} appearance-none pr-9 cursor-pointer`}
                  value={contrato}
                  onChange={(e) => {
                    setContrato(e.target.value);
                    syncToStore({ contrato: e.target.value });
                  }}
                >
                  {contratosDisponiveis.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
                <ChevronDown className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[#45556c]" />
              </div>
            </Field>
          </div>
        ) : (
          <div className="grid gap-6 sm:grid-cols-2">
            {tipoRelatorio === "SOCICAM" ? (
              <Field label="Terminal Rodoviário (Local)">
                <div className="relative">
                  <select
                    className={`${inputCls} appearance-none pr-9 cursor-pointer`}
                    value={local}
                    onChange={(e) => {
                      setLocal(e.target.value);
                      setMun(e.target.value);
                      syncToStore({
                        local: e.target.value,
                        mun: e.target.value,
                      });
                    }}
                  >
                    {locaisSocicam.map((loc) => (
                      <option key={loc} value={loc}>
                        {loc}
                      </option>
                    ))}
                  </select>
                  <ChevronDown className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[#45556c]" />
                </div>
              </Field>
            ) : (
              <Field label="Local / Sistema Viário">
                <input
                  className={inputCls}
                  placeholder="Sistema Viário do Paiva"
                  value={local}
                  onChange={(e) => {
                    setLocal(e.target.value);
                    syncToStore({ local: e.target.value });
                  }}
                />
              </Field>
            )}

            <Field
              label="Contrato de Concessão"
              rightElement={
                <button
                  type="button"
                  onClick={() =>
                    onOpenContratosModal((c) => {
                      setContrato(c);
                      syncToStore({ contrato: c });
                    })
                  }
                  className="text-[11px] font-medium text-muted-foreground hover:text-accent transition shrink-0"
                >
                  + Gerenciar
                </button>
              }
            >
              <div className="relative">
                <select
                  className={`${inputCls} appearance-none pr-9 cursor-pointer`}
                  value={contrato}
                  onChange={(e) => {
                    setContrato(e.target.value);
                    syncToStore({ contrato: e.target.value });
                  }}
                >
                  {contratosDisponiveis.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
                <ChevronDown className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[#45556c]" />
              </div>
            </Field>
          </div>
        )}

        {/* Linha 3: Equipe Técnica + Coordenador (Perfeitamente Alinhados e Simétricos) */}
        <div className="grid gap-6 sm:grid-cols-2">
          {/* Equipe Técnica: Caixa Acumuladora */}
          <div className="space-y-2">
            <div className="flex h-6 items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wide text-slate-blue truncate">
                Equipe Técnica (Pessoal Responsável){" "}
                {equipe.length > 0 && (
                  <span className="font-bold text-sky-600">({equipe.length})</span>
                )}
              </span>
              <div className="flex shrink-0 items-center gap-2 text-[11px]">
                <button
                  type="button"
                  onClick={() => {
                    const next =
                      equipe.length > 0
                        ? []
                        : responsaveis.map((r) => r.nome);
                    setEquipe(next);
                    syncToStore({ equipe: next });
                  }}
                  className="font-medium text-muted-foreground hover:text-accent transition"
                >
                  {equipe.length > 0 ? "Desmarcar todos" : "Selecionar todos"}
                </button>
                <span className="text-border">·</span>
                <button
                  type="button"
                  onClick={onOpenResponsaveisModal}
                  className="font-medium text-muted-foreground hover:text-accent transition"
                  title="Gerenciar equipe técnica"
                >
                  + Gerenciar
                </button>
              </div>
            </div>

            {/* Card Executivo de Responsáveis (Simétrico ao Coordenador) */}
            <div className="relative flex h-[68px] items-center justify-between gap-2.5 overflow-hidden rounded-2xl border-2 border-border bg-card p-3 shadow-sm transition-all duration-200 hover:border-primary/50 hover:shadow-md">
              <div
                className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-white shadow-sm"
                style={{ backgroundColor: theme.primary }}
              >
                <Users className="h-5 w-5" />
              </div>

              {/* Área Central: Chips Laterais com Abreviação Inteligente */}
              <div className="flex flex-1 min-w-0 items-center gap-1.5 overflow-x-auto overflow-y-hidden py-1 flex-nowrap scrollbar-thin">
                {equipe.length === 0 ? (
                  <span className="text-xs italic text-muted-foreground truncate">
                    Nenhum responsável vinculado...
                  </span>
                ) : (
                  equipe.map((nome) => {
                    const nomeExibido = formatNomeAbreviado(
                      nome,
                      equipe.length >= 3
                    );
                    return (
                      <span
                        key={nome}
                        title={nome}
                        className="inline-flex shrink-0 items-center gap-1.5 rounded-xl py-1.5 pl-2.5 pr-1.5 text-xs font-bold text-white shadow-sm transition-all"
                        style={{ backgroundColor: theme.primary }}
                      >
                        <span className="max-w-[120px] truncate">
                          {nomeExibido}
                        </span>
                        <button
                          type="button"
                          onClick={() => {
                            const next = equipe.filter((x) => x !== nome);
                            setEquipe(next);
                            syncToStore({ equipe: next });
                          }}
                          className="rounded-full p-0.5 hover:bg-black/20 text-white/90 hover:text-white transition"
                          title={`Remover ${nome} da equipe`}
                        >
                          <X className="h-3.5 w-3.5" />
                        </button>
                      </span>
                    );
                  })
                )}
              </div>

              {/* Seletor Dropdown Compacto para Adicionar Membros */}
              {responsaveis.filter((p) => !equipe.includes(p.nome)).length > 0 ? (
                <div className="relative shrink-0">
                  <select
                    aria-label="Adicionar responsável"
                    className="w-[92px] cursor-pointer rounded-xl border border-border bg-secondary/80 py-1.5 pl-2.5 pr-6 text-[11px] font-semibold text-foreground outline-none focus:border-primary hover:bg-secondary transition appearance-none truncate"
                    value=""
                    onChange={(e) => {
                      if (e.target.value) {
                        const next = [...equipe, e.target.value];
                        setEquipe(next);
                        syncToStore({ equipe: next });
                      }
                    }}
                  >
                    <option value="">+ Incluir...</option>
                    {responsaveis
                      .filter((p) => !equipe.includes(p.nome))
                      .map((p) => (
                        <option key={p.nome} value={p.nome}>
                          {p.nome}
                        </option>
                      ))}
                  </select>
                  <ChevronDown className="pointer-events-none absolute right-2 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
                </div>
              ) : (
                <span className="shrink-0 rounded-xl border border-dashed border-border px-2 py-1 text-[10px] font-semibold text-muted-foreground">
                  Todos ativos
                </span>
              )}
            </div>
          </div>

          {/* Coordenador(a): Card Executivo com Contenção Rígida de Largura */}
          <div className="space-y-2">
            <div className="flex h-6 items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wide text-slate-blue truncate">
                Coordenador(a) de Transportes e Rodovias
              </span>
              <button
                type="button"
                onClick={onOpenCoordenadoresModal}
                className="inline-flex shrink-0 items-center gap-1 text-[11px] font-medium text-muted-foreground hover:text-accent transition"
                title="Gerenciar coordenadores"
              >
                <Settings className="h-3 w-3" /> Gerenciar
              </button>
            </div>

            {/* Card Executivo Perfeitamente Simétrico */}
            <div className="relative flex h-[68px] items-center justify-between gap-2.5 overflow-hidden rounded-2xl border-2 border-border bg-card p-3 shadow-sm transition-all duration-200 hover:border-primary/50 hover:shadow-md">
              <div className="flex flex-1 min-w-0 items-center gap-3 overflow-hidden">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#071d36] text-white shadow-sm">
                  <UserCheck className="h-5 w-5" />
                </div>
                <div className="min-w-0 flex-1 overflow-hidden">
                  <div
                    className="truncate text-xs font-bold text-foreground"
                    title={coord}
                  >
                    {coord || "Selecione o(a) coordenador(a)..."}
                  </div>
                  <div
                    className="truncate text-[11px] text-muted-foreground font-medium"
                    title={
                      activeCoord?.funcao
                        ? `${activeCoord.funcao}${
                            activeCoord.matricula
                              ? ` · Matr. ${activeCoord.matricula}`
                              : ""
                          }`
                        : "Coordenadoria de Transportes e Rodovias · ARPE"
                    }
                  >
                    {activeCoord?.funcao
                      ? `${activeCoord.funcao}${
                          activeCoord.matricula
                            ? ` · Matr. ${activeCoord.matricula}`
                            : ""
                        }`
                      : "Coordenadoria de Transportes e Rodovias · ARPE"}
                  </div>
                </div>
              </div>

              {/* Seletor dropdown compacto integrado */}
              <div className="relative shrink-0">
                <select
                  aria-label="Selecionar Coordenador"
                  className="w-[92px] cursor-pointer rounded-xl border border-border bg-secondary/80 py-1.5 pl-2.5 pr-6 text-[11px] font-semibold text-foreground outline-none focus:border-primary hover:bg-secondary transition appearance-none truncate"
                  value={coord}
                  onChange={(e) => {
                    setCoord(e.target.value);
                    syncToStore({ coord: e.target.value });
                  }}
                >
                  <option value="">Trocar...</option>
                  {coordenadores.map((c) => (
                    <option key={c.nome} value={c.nome}>
                      {c.nome}
                    </option>
                  ))}
                </select>
                <ChevronDown className="pointer-events-none absolute right-2 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Modal de Confirmação para Apagar Fiscalização com Registros */}
      {fiscIndexToDelete !== null && (() => {
        const targetFisc = ws.fiscalizacoes[fiscIndexToDelete];
        const targetId =
          targetFisc?.["ID da Fiscalização"]?.trim() || `#${fiscIndexToDelete + 1}`;
        const regsVinculados = ws.registrosNc.filter(
          (r) => (r["ID da Fiscalização"] || "").trim() === targetId
        );

        return (
          <ConfirmDeleteModal
            title={isMonitoring ? "Excluir Monitoramento" : "Excluir Fiscalização"}
            description={`A fiscalização "${targetId}" possui ${regsVinculados.length} ocorrência(s) cadastrada(s). Tem certeza de que deseja apagá-la? Todas as ocorrências vinculadas e fotos serão removidas permanentemente.`}
            itemsPreview={[
              `Identificação: ${targetId}`,
              `Total de ocorrências vinculadas: ${regsVinculados.length}`,
              ...(targetFisc?.Data ? [`Data da vistoria: ${targetFisc.Data}`] : []),
              ...(targetFisc?.Local ? [`Local: ${targetFisc.Local}`] : []),
            ]}
            onConfirm={handleConfirmDeleteFisc}
            onClose={() => setFiscIndexToDelete(null)}
          />
        );
      })()}
    </Card>
  );
};
