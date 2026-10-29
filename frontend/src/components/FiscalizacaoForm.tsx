import React, { useEffect, useState, type ReactNode } from "react";
import { Building2, Plus, Settings } from "lucide-react";
import { toast } from "sonner";
import { Card } from "./Card";
import { useReportStore } from "../store/useReportStore";
import { FiscalizacaoItem } from "../types/report.types";

interface FiscalizacaoFormProps {
  onOpenResponsaveisModal: () => void;
  onOpenCoordenadoresModal: () => void;
  onOpenContratosModal: (onSelectContrato?: (c: string) => void) => void;
}

const inputCls =
  "w-full rounded-lg border border-input bg-secondary/60 px-3 py-2 text-sm text-foreground outline-none focus:border-ring focus:ring-2 focus:ring-ring/20";

const pill = (on: boolean) =>
  `rounded-full border px-3 py-1.5 text-xs font-medium transition ${
    on
      ? "border-accent bg-accent text-accent-foreground"
      : "border-border bg-card text-muted-foreground hover:border-accent/50"
  }`;

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="block space-y-1.5">
      <span className="text-xs font-semibold uppercase tracking-wide text-slate-blue">
        {label}
      </span>
      {children}
    </label>
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
  } = useReportStore();

  const ws = getActiveWorkspace();
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
      ? activeFisc["Pessoal Responsável"]
          .split(/[,;]/)
          .map((s) => s.trim())
          .filter(Boolean)
      : allRespNames
  );
  const [coord, setCoord] = useState(
    activeFisc?.Coordenador || coordenadores[0]?.nome || ""
  );

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
      setIdFisc(f["ID da Fiscalização"] || "");
      setDataIso(fDataIso);
      setPeriodo(
        f.Período && !f.Período.startsWith("=") ? f.Período : isoToBr(fDataIso)
      );
      setHora(f.Hora && !f.Hora.startsWith("=") ? f.Hora : "");
      setMun(f.Cidade && !f.Cidade.startsWith("=") ? f.Cidade : "");
      setLocal(f.Local && !f.Local.startsWith("=") ? f.Local : defaultLocal);
      setContrato(
        f.Contrato || contratosPadrao[tipoRelatorio] || "CT. nº 043/2011"
      );
      setEquipe(
        f["Pessoal Responsável"] && !f["Pessoal Responsável"].startsWith("=")
          ? f["Pessoal Responsável"]
              .split(/[,;]/)
              .map((s) => s.trim())
              .filter(Boolean)
          : responsaveis.map((r) => r.nome)
      );
      setCoord(f.Coordenador || coordenadores[0]?.nome || "");
    } else {
      const today = getTodayIso();
      setIdFisc("");
      setDataIso(today);
      setPeriodo(isoToBr(today));
      setHora("");
      setMun("");
      setLocal(defaultLocal);
      setContrato(contratosPadrao[tipoRelatorio] || "CT. nº 043/2011");
      setEquipe(responsaveis.map((r) => r.nome));
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
      "Pessoal Responsável": responsaveis.map((r) => r.nome).join(", "),
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
      n={2}
      icon={<Building2 className="h-5 w-5" />}
      title={
        isMonitoring
          ? "Informações do Monitoramento"
          : "Informações da Fiscalização"
      }
    >
      {/* Barra de Múltiplos IDs de Fiscalização / Monitoramento */}
      <div className="mb-6 flex flex-wrap items-center justify-between gap-2 rounded-xl border border-border bg-secondary/40 px-3.5 py-2.5">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-[11px] font-semibold uppercase tracking-wide text-slate-blue">
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
                <button
                  key={`${label}_${idx}`}
                  type="button"
                  onClick={() => setActiveFiscalizacaoIndex(idx)}
                  className={pill(isAct)}
                >
                  {label}
                </button>
              );
            })
          )}
        </div>
        <button
          type="button"
          onClick={handleAddNewHeader}
          className="inline-flex items-center gap-1 rounded-lg border border-border bg-card px-2.5 py-1 text-xs font-semibold text-foreground hover:border-accent hover:text-accent transition"
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
        {/* Linha 1: ID + Data + (Hora na CRA | Período em CRC/SOCICAM) */}
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

          <Field label="Data da Vistoria">
            <input
              type="date"
              className={inputCls}
              value={dataIso}
              onChange={(e) => {
                const nextIso = e.target.value;
                const oldBr = isoToBr(dataIso);
                const nextBr = isoToBr(nextIso);
                const shouldSyncPeriodo = !periodo.trim() || periodo === oldBr;
                setDataIso(nextIso);
                if (shouldSyncPeriodo) {
                  setPeriodo(nextBr);
                }
                syncToStore({
                  data: nextIso,
                  periodo: shouldSyncPeriodo ? nextBr : periodo,
                });
              }}
            />
          </Field>

          {tipoRelatorio === "CRA" ? (
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
          ) : (
            <Field label="Período da Vistoria">
              <input
                className={inputCls}
                placeholder="Ex: 15 a 16/06/2026"
                value={periodo}
                onChange={(e) => {
                  setPeriodo(e.target.value);
                  syncToStore({ periodo: e.target.value });
                }}
              />
            </Field>
          )}
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

            <Field label="Período da Vistoria">
              <input
                className={inputCls}
                placeholder="Ex: 15 a 16/06/2026"
                value={periodo}
                onChange={(e) => {
                  setPeriodo(e.target.value);
                  syncToStore({ periodo: e.target.value });
                }}
              />
            </Field>

            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wide text-slate-blue">
                  Contrato
                </span>
                <button
                  type="button"
                  onClick={() =>
                    onOpenContratosModal((c) => {
                      setContrato(c);
                      syncToStore({ contrato: c });
                    })
                  }
                  className="text-[11px] font-medium text-muted-foreground hover:text-accent transition"
                >
                  + Gerenciar
                </button>
              </div>
              <select
                className={inputCls}
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
            </div>
          </div>
        ) : (
          <div className="grid gap-6 sm:grid-cols-2">
            {tipoRelatorio === "SOCICAM" ? (
              <Field label="Terminal Rodoviário (Local)">
                <select
                  className={inputCls}
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

            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wide text-slate-blue">
                  Contrato de Concessão
                </span>
                <button
                  type="button"
                  onClick={() =>
                    onOpenContratosModal((c) => {
                      setContrato(c);
                      syncToStore({ contrato: c });
                    })
                  }
                  className="text-[11px] font-medium text-muted-foreground hover:text-accent transition"
                >
                  + Gerenciar
                </button>
              </div>
              <select
                className={inputCls}
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
            </div>
          </div>
        )}

        {/* Linha 3: Equipe Técnica + Coordenador */}
        <div className="grid gap-6 sm:grid-cols-2">
          <div className="space-y-1.5">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <span className="text-xs font-semibold uppercase tracking-wide text-slate-blue">
                Equipe Técnica (Pessoal Responsável)
              </span>
              <div className="flex items-center gap-2 text-[11px]">
                <button
                  type="button"
                  onClick={() => {
                    const next =
                      equipe.length === responsaveis.length
                        ? []
                        : responsaveis.map((r) => r.nome);
                    setEquipe(next);
                    syncToStore({ equipe: next });
                  }}
                  className="font-medium text-muted-foreground hover:text-accent transition"
                >
                  {equipe.length === responsaveis.length
                    ? "Desmarcar todos"
                    : "Todos"}
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
            <div className="flex flex-wrap gap-2">
              {responsaveis.map((p) => {
                const selected = equipe.includes(p.nome);
                return (
                  <button
                    type="button"
                    key={p.nome}
                    className={pill(selected)}
                    onClick={() => {
                      const next = selected
                        ? equipe.filter((x) => x !== p.nome)
                        : [...equipe, p.nome];
                      setEquipe(next);
                      syncToStore({ equipe: next });
                    }}
                  >
                    {p.nome}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-wide text-slate-blue">
                Coordenador(a) de Transportes e Rodovias
              </span>
              <button
                type="button"
                onClick={onOpenCoordenadoresModal}
                className="inline-flex items-center gap-1 text-[11px] font-medium text-muted-foreground hover:text-accent transition"
                title="Gerenciar coordenadores"
              >
                <Settings className="h-3 w-3" /> Gerenciar
              </button>
            </div>
            <select
              className={inputCls}
              value={coord}
              onChange={(e) => {
                setCoord(e.target.value);
                syncToStore({ coord: e.target.value });
              }}
            >
              {coordenadores.map((c) => (
                <option key={c.nome} value={c.nome}>
                  {c.nome}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>
    </Card>
  );
};
