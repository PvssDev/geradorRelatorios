import React, { ReactNode } from "react";
import { useReportStore } from "../store/useReportStore";
import { getConcessionTheme } from "../utils/concessionTheme";

interface CardProps {
  n: number;
  icon: ReactNode;
  title: string;
  bodyClass?: string;
  children: ReactNode;
}

export const Card: React.FC<CardProps> = ({
  n,
  icon,
  title,
  bodyClass = "",
  children,
}) => {
  const { tipoRelatorio, categoriaRelatorio } = useReportStore();
  const theme = getConcessionTheme(tipoRelatorio, categoriaRelatorio);
  const accentColor = theme.primary;

  return (
    <section
      id={`b${n}`}
      className="group relative overflow-hidden rounded-2xl border border-[#d2e2f3] bg-white shadow-sm scroll-mt-28 transition-all duration-300 ease-out hover:shadow-xl hover:shadow-[#071d36]/10 hover:border-slate-300 hover:-translate-y-0.5"
    >
      <h2 className="flex items-center gap-3 bg-[#071d36] px-6 py-4 text-base font-bold text-white">
        <span
          className="grid h-8 w-8 place-items-center rounded-xl text-white shadow-sm"
          style={{ backgroundColor: accentColor }}
        >
          {icon}
        </span>
        <span className="font-extrabold" style={{ color: accentColor }}>
          0{n}
        </span>
        <span className="text-white font-bold">{title}</span>
      </h2>
      <div
        className={`border-l-4 p-6 sm:p-8 ${bodyClass}`}
        style={{ borderLeftColor: accentColor }}
      >
        {children}
      </div>
    </section>
  );
};
