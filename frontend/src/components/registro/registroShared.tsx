import React from "react";

export const DIRECOES_CRA = ["Direita", "Esquerda"] as const;
export const PISTAS_SUGESTOES = [
  "Sul",
  "Norte",
  "Leste",
  "Oeste",
  "Sul / Norte",
  "Sentido Recife",
  "Sentido Suape",
];

export const registroInputCls =
  "w-full rounded-xl border border-[#d0e1f3] bg-[#f0f6fc] px-3.5 py-2.5 text-sm text-foreground outline-none transition-all duration-200 hover:bg-[#eaf3fc] hover:border-primary/50 hover:shadow-xs focus:border-primary focus:bg-white focus:ring-2 focus:ring-primary/20";

export const registroBtn = {
  primary:
    "inline-flex items-center justify-center gap-2 rounded-xl bg-primary px-5 py-2.5 text-xs font-semibold text-primary-foreground shadow-sm hover:bg-navy-2 active:scale-[0.98] transition-all duration-150 disabled:opacity-40 disabled:pointer-events-none",
  secondary:
    "inline-flex items-center justify-center gap-2 rounded-xl border border-[#d0e1f3] bg-white px-4 py-2 text-xs font-semibold text-primary hover:bg-[#e6f0fb] hover:border-primary/40 active:scale-[0.98] transition-all duration-150 disabled:opacity-40 disabled:pointer-events-none",
};

export const registroPillCls = (on: boolean) =>
  `rounded-full border px-3 py-1 text-xs font-semibold transition-all duration-150 active:scale-95 ${
    on
      ? "text-white shadow-sm"
      : "border-border bg-secondary text-secondary-foreground hover:bg-muted"
  }`;

export function RegistroField({
  label,
  action,
  className = "",
  children,
}: {
  label: string;
  action?: React.ReactNode;
  className?: string;
  children: React.ReactNode;
}) {
  return (
    <div className={`space-y-1.5 ${className}`}>
      <div className="flex items-center justify-between gap-2">
        <span className="block text-xs font-semibold uppercase tracking-wide text-slate-blue">
          {label}
        </span>
        {action}
      </div>
      {children}
    </div>
  );
}

