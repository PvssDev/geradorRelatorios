import React, { useEffect, useRef, useState, useMemo, type ReactNode } from "react";
import { createPortal } from "react-dom";
import { AnimatePresence, motion } from "framer-motion";
import { DateRangePicker, type RangeValue } from "@heroui/react";
import { parseDate, type DateValue } from "@internationalized/date";
import {
  Building2,
  Plus,
  Settings,
  X,
  UserCheck,
  ChevronDown,
  Users,
  Check,
} from "lucide-react";
import { toast } from "sonner";
import { Card } from "./Card";
import { ConfirmDeleteModal } from "./Modals";
import { useReportStore } from "../store/useReportStore";
import { FiscalizacaoItem } from "../types/report.types";
import { getConcessionTheme, isPerformanceModeActive } from "../utils/concessionTheme";

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
      ? "text-white font-bold border border-transparent shadow-sm hover:border-[#001630]/60 hover:ring-2 hover:ring-[#001630]/25 hover:shadow-md"
      : "border border-[#bdd0e4] bg-white text-slate-700 hover:bg-[#f0f6fc] hover:border-[#001630]/60 hover:ring-2 hover:ring-[#001630]/15 font-semibold shadow-xs"
  }`;

function formatNomeAbreviado(nomeCompleto: string, compactar: boolean): string {
  if (!compactar) return nomeCompleto;
  const partes = nomeCompleto.trim().split(/\s+/);
  if (partes.length <= 1) return nomeCompleto;
  const primeiro = partes[0];
  const ultimo = partes[partes.length - 1];
  return `${primeiro} ${ultimo.charAt(0)}.`;
}

/**
 * Gerencia abertura, fechamento (Escape) e coordenadas fixas para menus suspensos
 * ancorados abaixo de cards com overflow-hidden via React Portal.
 */
function useAnchoredDropdown() {
  const cardRef = useRef<HTMLDivElement>(null);
  const [open, setOpen] = useState(false);
  const [rect, setRect] = useState<{
    top: number;
    left: number;
    width: number;
  } | null>(null);

  const updatePos = () => {
    if (cardRef.current) {
      const r = cardRef.current.getBoundingClientRect();
      setRect({ top: r.bottom + 6, left: r.left, width: r.width });
    }
  };

  const toggle = () => {
    if (open) {
      setOpen(false);
      return;
    }
    updatePos();
    setOpen(true);
  };

  useEffect(() => {
    if (!open) return;
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("scroll", updatePos, true);
    window.addEventListener("resize", updatePos);
    window.addEventListener("keydown", onKeyDown);
    return () => {
      window.removeEventListener("scroll", updatePos, true);
      window.removeEventListener("resize", updatePos);
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  return { cardRef, open, setOpen, toggle, rect };
}

/**
 * Renderiza o container flutuante do dropdown via React Portal, alinhado abaixo do card pai.
 */
function AnchoredPortalMenu({
  dropdown,
  children,
}: {
  dropdown: ReturnType<typeof useAnchoredDropdown>;
  children: ReactNode;
}) {
  if (!dropdown.open || !dropdown.rect) return null;
  return createPortal(
    <>
      <div
        className="fixed inset-0 z-[9998]"
        onClick={() => dropdown.setOpen(false)}
      />
      <div
        style={{
          position: "fixed",
          top: dropdown.rect.top,
          left: dropdown.rect.left,
          width: dropdown.rect.width,
          zIndex: 9999,
        }}
        className="max-h-64 overflow-y-auto rounded-2xl border border-border bg-white p-1.5 shadow-2xl"
      >
        <div className="flex flex-col gap-0.5">{children}</div>
      </div>
    </>,
    document.body
  );
}

/**
 * Item padronizado de opção com título, subtítulo opcional e checkmark animado na cor do tema.
 */
function DropdownOptionItem({
  title,
  subtitle,
  selected,
  accentColor,
  onClick,
}: {
  title: string;
  subtitle?: string;
  selected: boolean;
  accentColor: string;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      style={selected ? { backgroundColor: `${accentColor}12` } : undefined}
      className={`group w-full text-left flex items-center justify-between gap-3 px-3 py-2 rounded-xl text-xs transition cursor-pointer ${
        selected ? "hover:brightness-95" : "hover:bg-secondary/80"
      }`}
    >
      <div className="flex flex-col min-w-0">
        <span
          className="font-semibold truncate transition-colors"
          style={selected ? { color: accentColor } : undefined}
        >
          {title}
        </span>
        {subtitle && (
          <span className="text-[11px] text-muted-foreground truncate">
            {subtitle}
          </span>
        )}
      </div>

      {selected && (
        <span
          className="shrink-0 flex items-center justify-center animate-check-pop"
          style={{ color: accentColor }}
          aria-hidden="true"
        >
          <Check className="h-4 w-4 stroke-[2.75] animate-check-draw" />
        </span>
      )}
    </button>
  );
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
    activeFisc?.Data && !activeFisc.Data.startsWith("=") ? brToIso(activeFisc.Data) : ""
  );
  const [dataFimIso, setDataFimIso] = useState(() => {
    if (!activeFisc?.Data || activeFisc.Data.startsWith("=")) return "";
    return desmembrarPeriodoEmDatas(activeFisc?.Período || "", brToIso(activeFisc.Data)).fimIso;
  });
  const [periodo, setPeriodo] = useState(
    activeFisc?.Período && !activeFisc.Período.startsWith("=") ? activeFisc.Período : ""
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
  const equipeDropdown = useAnchoredDropdown();
  const coordDropdown = useAnchoredDropdown();
  const contratoDropdown = useAnchoredDropdown();

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
      const fDataIso = f.Data && !f.Data.startsWith("=") ? brToIso(f.Data) : "";
      const { inicioIso, fimIso } = fDataIso
        ? desmembrarPeriodoEmDatas(f.Período || "", fDataIso)
        : { inicioIso: "", fimIso: "" };
      setIdFisc(f["ID da Fiscalização"] || "");
      setDataIso(inicioIso);
      setDataFimIso(fimIso);
      setPeriodo(
        f.Período && !f.Período.startsWith("=")
          ? f.Período
          : inicioIso && fimIso
          ? formatarPeriodoVistoria(inicioIso, fimIso)
          : ""
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
      setIdFisc("");
      setDataIso("");
      setDataFimIso("");
      setPeriodo("");
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
        : tipoRelatorio === "CRA" || tipoRelatorio === "CRC"
        ? defaultLocal
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

  const dateRangeValue = useMemo(() => {
    if (!dataIso || !/^\d{4}-\d{2}-\d{2}$/.test(dataIso)) return null;
    try {
      const start = parseDate(dataIso);
      const end =
        dataFimIso && /^\d{4}-\d{2}-\d{2}$/.test(dataFimIso)
          ? parseDate(dataFimIso)
          : start;
      return { start, end };
    } catch {
      return null;
    }
  }, [dataIso, dataFimIso]);

  const handleDateRangeChange = (range: RangeValue<DateValue> | null) => {
    if (!range || !range.start || !range.end) return;
    const startIso = range.start.toString();
    const endIso = range.end.toString();
    setDataIso(startIso);
    setDataFimIso(endIso);
    const nextPer = formatarPeriodoVistoria(startIso, endIso);
    setPeriodo(nextPer);
    syncToStore({
      data: startIso,
      periodo: nextPer,
    });
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

  const renderContratoField = (labelText: string) => {
    const isPerf = isPerformanceModeActive();
    return (
      <Field
        label={labelText}
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
        <div ref={contratoDropdown.cardRef} className="relative">
          <button
            type="button"
            onClick={contratoDropdown.toggle}
            aria-label={labelText}
            aria-expanded={contratoDropdown.open}
            className={`${inputCls} flex items-center justify-between gap-2 text-left cursor-pointer`}
          >
            <div className="min-w-0 flex-1 overflow-hidden">
              <AnimatePresence mode="wait" initial={false}>
                <motion.span
                  key={contrato || "empty-contrato"}
                  initial={isPerf ? false : { opacity: 0, y: 4 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={isPerf ? { opacity: 0 } : { opacity: 0, y: -4 }}
                  transition={{
                    duration: isPerf ? 0 : 0.16,
                    ease: [0.22, 1, 0.36, 1],
                  }}
                  className="block truncate"
                >
                  {contrato || "Selecione o contrato..."}
                </motion.span>
              </AnimatePresence>
            </div>
            <ChevronDown
              className={`h-4 w-4 shrink-0 text-[#45556c] transition-transform duration-200 ${
                contratoDropdown.open ? "rotate-180" : ""
              }`}
            />
          </button>

          {contratosDisponiveis.length > 0 && (
            <AnchoredPortalMenu dropdown={contratoDropdown}>
              {contratosDisponiveis.map((c) => (
                <DropdownOptionItem
                  key={c}
                  title={c}
                  selected={contrato === c}
                  accentColor={theme.primary}
                  onClick={() => {
                    setContrato(c);
                    syncToStore({ contrato: c });
                    contratoDropdown.setOpen(false);
                  }}
                />
              ))}
            </AnchoredPortalMenu>
          )}
        </div>
      </Field>
    );
  };

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
      <div className="mb-6 flex flex-wrap items-center justify-between gap-2 rounded-2xl border border-[#bdd0e4] bg-[#edf4fb] px-4 py-3 transition-colors duration-200 hover:border-[#001630]/35">
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
                        : { color: theme.primary }
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
          className="inline-flex items-center gap-1.5 rounded-xl border border-[#bdd0e4] bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 shadow-xs hover:bg-[#f0f6fc] hover:text-slate-900 hover:border-[#001630]/60 hover:ring-2 hover:ring-[#001630]/15 active:scale-[0.98] transition-all"
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
        {/* Linha 1: ID + Período da Vistoria (HeroUI DateRangePicker) */}
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

          <div
            className="sm:col-span-2"
            style={{
              ["--concession-primary" as string]: theme.primary,
              ["--concession-soft" as string]: theme.lightBg,
              ["--concession-border" as string]: theme.lightBorder,
              ["--concession-glow" as string]: `${theme.primary}25`,
            }}
          >
            <Field
              label="Período da Vistoria (Início e Término)"
              rightElement={
                periodo ? (
                  <span
                    className="inline-flex items-center px-2 py-0.5 rounded-md text-[10px] font-bold border shrink-0 transition-all shadow-2xs"
                    style={{
                      backgroundColor: theme.lightBg,
                      borderColor: theme.lightBorder,
                      color: theme.primary,
                    }}
                  >
                    Período: {periodo}
                  </span>
                ) : (
                  <span className="text-[10px] font-medium text-slate-400 shrink-0">
                    dd/mm/aaaa – dd/mm/aaaa
                  </span>
                )
              }
            >
              <DateRangePicker
                aria-label="Período da Vistoria"
                value={dateRangeValue}
                onChange={handleDateRangeChange}
                variant="bordered"
                visibleMonths={1}
                className="w-full arpe-date-range-picker"
                popoverProps={{
                  className: "arpe-date-range-popover",
                  style: {
                    ["--concession-primary" as string]: theme.primary,
                    ["--concession-soft" as string]: theme.lightBg,
                    ["--concession-border" as string]: theme.lightBorder,
                    ["--concession-glow" as string]: `${theme.primary}35`,
                  },
                }}
              />
            </Field>
          </div>
        </div>

        {/* Linha 2: Campos específicos da Concessão (CRA vs CRC vs SOCICAM) */}
        {tipoRelatorio === "CRA" ? (
          <div className="grid gap-6 sm:grid-cols-3">
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

            {renderContratoField("Contrato")}
          </div>
        ) : tipoRelatorio === "SOCICAM" ? (
          <div className="grid gap-6 sm:grid-cols-2">
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

            {renderContratoField("Contrato de Concessão")}
          </div>
        ) : (
          <div className="grid gap-6 sm:grid-cols-2">
            {renderContratoField("Contrato de Concessão")}
          </div>
        )}

        {/* Linha 3: Equipe Técnica + Coordenador (Perfeitamente Alinhados e Simétricos) */}
        <div className="grid gap-6 sm:grid-cols-2">
          {/* Equipe Técnica: Card Executivo com Seletor de Seta Compacto */}
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
            <div
              ref={equipeDropdown.cardRef}
              className="relative flex h-[68px] items-center justify-between gap-2.5 overflow-hidden rounded-2xl border-2 border-border bg-card p-3 shadow-sm transition-all duration-200 hover:border-primary/50 hover:shadow-md"
            >
              <div
                className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-white shadow-sm"
                style={{ backgroundColor: theme.primary }}
              >
                <Users className="h-5 w-5" />
              </div>

              {/* Área Central: Chips Laterais com Abreviação Inteligente e Animação de Entrada/Saída */}
              <div className="relative flex flex-1 min-w-0 items-center gap-1.5 overflow-x-auto overflow-y-hidden py-1 flex-nowrap scrollbar-thin">
                <AnimatePresence initial={false} mode="popLayout">
                  {equipe.length === 0 ? (
                    <motion.span
                      key="empty-equipe"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      transition={{
                        duration: isPerformanceModeActive() ? 0 : 0.15,
                      }}
                      className="text-xs italic text-muted-foreground truncate"
                    >
                      Nenhum responsável vinculado...
                    </motion.span>
                  ) : (
                    equipe.map((nome) => {
                      const nomeExibido = formatNomeAbreviado(
                        nome,
                        equipe.length >= 3
                      );
                      const isPerf = isPerformanceModeActive();
                      return (
                        <motion.span
                          key={nome}
                          layout="position"
                          initial={
                            isPerf ? false : { opacity: 0, scale: 0.82, x: -6 }
                          }
                          animate={{ opacity: 1, scale: 1, x: 0 }}
                          exit={
                            isPerf
                              ? { opacity: 0 }
                              : { opacity: 0, scale: 0.78, y: -4 }
                          }
                          transition={{
                            duration: isPerf ? 0 : 0.2,
                            ease: [0.22, 1, 0.36, 1],
                          }}
                          title={nome}
                          className="inline-flex shrink-0 items-center gap-1.5 rounded-xl py-1.5 pl-2.5 pr-1.5 text-xs font-bold text-white shadow-sm"
                          style={{ backgroundColor: theme.primary }}
                        >
                          <span className="max-w-[130px] truncate">
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
                            aria-label={`Remover ${nome} da equipe`}
                          >
                            <X className="h-3.5 w-3.5" />
                          </button>
                        </motion.span>
                      );
                    })
                  )}
                </AnimatePresence>
              </div>

              {/* Seta para Baixo sem fundo, borda ou margem */}
              {responsaveis.length > 0 ? (
                <button
                  type="button"
                  onClick={equipeDropdown.toggle}
                  className="shrink-0 m-0 p-0 bg-transparent border-0 text-muted-foreground hover:text-foreground transition cursor-pointer flex items-center justify-center focus:outline-none"
                  title="Selecionar responsáveis da equipe"
                  aria-label="Selecionar responsáveis da equipe"
                  aria-expanded={equipeDropdown.open}
                >
                  <ChevronDown
                    className={`h-4 w-4 transition-transform duration-200 ${
                      equipeDropdown.open ? "rotate-180" : ""
                    }`}
                  />
                </button>
              ) : (
                <span className="shrink-0 rounded-xl border border-dashed border-border px-2 py-1 text-[10px] font-semibold text-muted-foreground">
                  Sem equipe
                </span>
              )}

              {/* Lista suspensa renderizada em Portal (mantém-se aberta com toggle animado) */}
              {responsaveis.length > 0 && (
                <AnchoredPortalMenu dropdown={equipeDropdown}>
                  {responsaveis.map((p) => {
                    const isSelected = equipe.includes(p.nome);
                    return (
                      <DropdownOptionItem
                        key={p.nome}
                        title={p.nome}
                        subtitle={p.funcao}
                        selected={isSelected}
                        accentColor={theme.primary}
                        onClick={() => {
                          const next = isSelected
                            ? equipe.filter((x) => x !== p.nome)
                            : [...equipe, p.nome];
                          setEquipe(next);
                          syncToStore({ equipe: next });
                        }}
                      />
                    );
                  })}
                </AnchoredPortalMenu>
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
            <div
              ref={coordDropdown.cardRef}
              className="relative flex h-[68px] items-center justify-between gap-2.5 overflow-hidden rounded-2xl border-2 border-border bg-card p-3 shadow-sm transition-all duration-200 hover:border-primary/50 hover:shadow-md"
            >
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

              {/* Seta para Baixo sem fundo, borda ou margem (seleção única fecha ao clicar) */}
              {coordenadores.length > 0 && (
                <button
                  type="button"
                  onClick={coordDropdown.toggle}
                  className="shrink-0 m-0 p-0 bg-transparent border-0 text-muted-foreground hover:text-foreground transition cursor-pointer flex items-center justify-center focus:outline-none"
                  title="Selecionar coordenador(a)"
                  aria-label="Selecionar coordenador(a)"
                  aria-expanded={coordDropdown.open}
                >
                  <ChevronDown
                    className={`h-4 w-4 transition-transform duration-200 ${
                      coordDropdown.open ? "rotate-180" : ""
                    }`}
                  />
                </button>
              )}

              {/* Lista suspensa via Portal (fecha automaticamente ao selecionar 1 coordenador) */}
              {coordenadores.length > 0 && (
                <AnchoredPortalMenu dropdown={coordDropdown}>
                  {coordenadores.map((c) => (
                    <DropdownOptionItem
                      key={c.nome}
                      title={c.nome}
                      subtitle={
                        c.funcao
                          ? `${c.funcao}${
                              c.matricula ? ` · Matr. ${c.matricula}` : ""
                            }`
                          : undefined
                      }
                      selected={coord === c.nome}
                      accentColor={theme.primary}
                      onClick={() => {
                        setCoord(c.nome);
                        syncToStore({ coord: c.nome });
                        coordDropdown.setOpen(false);
                      }}
                    />
                  ))}
                </AnchoredPortalMenu>
              )}
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
