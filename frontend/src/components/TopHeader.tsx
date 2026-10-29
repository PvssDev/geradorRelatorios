import React from "react";
import { FileText, Menu } from "lucide-react";
import { useReportStore } from "../store/useReportStore";
import { CategoriaRelatorio, TipoRelatorio } from "../types/report.types";

interface TopHeaderProps {
  onToggleMobileMenu: () => void;
}

function Segmented<T extends string>({
  label,
  options,
  value,
  onChange,
  tone,
}: {
  label: string;
  options: T[];
  value: T;
  onChange: (v: T) => void;
  tone: "accent" | "primary";
}) {
  const onCls =
    tone === "accent"
      ? "bg-accent text-accent-foreground"
      : "bg-primary text-primary-foreground";

  return (
    <div className="flex items-center gap-2 rounded-xl border border-border bg-secondary/70 p-1 pl-3">
      <span className="text-[10px] font-bold uppercase tracking-[0.16em] text-slate-blue">
        {label}
      </span>
      <div className="flex gap-1">
        {options.map((o) => (
          <button
            key={o}
            type="button"
            onClick={() => onChange(o)}
            className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
              value === o
                ? `${onCls} shadow-card`
                : "text-muted-foreground hover:bg-card hover:text-foreground"
            }`}
          >
            {o}
          </button>
        ))}
      </div>
    </div>
  );
}

export const TopHeader: React.FC<TopHeaderProps> = ({ onToggleMobileMenu }) => {
  const {
    tipoRelatorio,
    categoriaRelatorio,
    setTipoRelatorio,
    setCategoriaRelatorio,
  } = useReportStore();

  const tipos: TipoRelatorio[] = ["CRA", "CRC", "SOCICAM"];
  const categorias: CategoriaRelatorio[] = ["Fiscalização", "Monitoramento"];

  const kicker =
    tipoRelatorio === "SOCICAM"
      ? `ARPE · ${categoriaRelatorio} de Terminais`
      : `ARPE · ${categoriaRelatorio} Rodoviária`;

  return (
    <header className="sticky top-0 z-30 border-b border-border bg-card/95 backdrop-blur">
      <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-x-6 gap-y-4 px-6 py-5">
        <div className="flex items-center gap-4">
          <button
            type="button"
            aria-label="Abrir menu"
            className="lg:hidden grid h-10 w-10 place-items-center rounded-xl border border-border bg-secondary/70 text-slate-blue"
            onClick={onToggleMobileMenu}
          >
            <Menu className="h-5 w-5" />
          </button>

          <span className="grid h-12 w-12 shrink-0 place-items-center rounded-2xl bg-navy-gradient text-accent shadow-card">
            <FileText className="h-6 w-6" />
          </span>

          <div>
            <div className="text-[11px] font-bold uppercase tracking-[0.22em] text-accent">
              {kicker}
            </div>
            <h1 className="text-3xl font-bold leading-none tracking-tight text-primary sm:text-4xl">
              Gerador de Relatórios
            </h1>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Segmented
            label="Concessão"
            options={tipos}
            value={tipoRelatorio}
            onChange={setTipoRelatorio}
            tone="accent"
          />
          <Segmented
            label="Tipo"
            options={categorias}
            value={categoriaRelatorio}
            onChange={setCategoriaRelatorio}
            tone="primary"
          />
          <span className="flex items-center gap-1.5 rounded-full bg-ok-soft px-3 py-1.5 text-xs font-semibold text-ok">
            <span className="h-2 w-2 rounded-full bg-ok" /> Conectado
          </span>
        </div>
      </div>
    </header>
  );
};
