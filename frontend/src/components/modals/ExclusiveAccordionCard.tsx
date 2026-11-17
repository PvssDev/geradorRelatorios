import React, { ReactNode } from "react";
import { ChevronDown } from "lucide-react";

interface ExclusiveAccordionCardProps {
  isOpen: boolean;
  onToggle: () => void;
  icon: ReactNode;
  title: string;
  subtitle: string;
  count?: number;
  primaryColor: string;
  borderColor: string;
  children: ReactNode;
}

/**
 * Card de acordeão com sombreado permanente, animação de elevação no hover
 * e indicador lateral na cor do relatório ativo.
 */
export const ExclusiveAccordionCard: React.FC<ExclusiveAccordionCardProps> = ({
  isOpen,
  onToggle,
  icon,
  title,
  subtitle,
  count,
  primaryColor,
  borderColor,
  children,
}) => {
  return (
    <div
      className="relative overflow-hidden rounded-2xl border bg-white shadow-md shadow-slate-900/10 transition-all duration-300 ease-out hover:shadow-xl hover:shadow-slate-900/15 hover:-translate-y-0.5"
      style={{
        borderColor: isOpen ? borderColor : "rgba(226, 232, 240, 0.85)",
      }}
    >
      {isOpen && (
        <span
          className="absolute left-0 top-3 bottom-3 w-1 rounded-r-full"
          style={{ backgroundColor: primaryColor }}
        />
      )}
      <button
        type="button"
        onClick={onToggle}
        aria-expanded={isOpen}
        className="flex w-full items-center justify-between px-4 py-3.5 text-left transition hover:bg-slate-50/70"
      >
        <div className="flex items-center gap-3 min-w-0">
          <div
            className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-white shadow-sm"
            style={{ backgroundColor: primaryColor }}
          >
            {icon}
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <span
                className="text-[11px] font-extrabold uppercase tracking-wider"
                style={{ color: primaryColor }}
              >
                {title}
              </span>
              {typeof count === "number" && (
                <span
                  className="flex h-5 min-w-5 items-center justify-center rounded-full px-1.5 text-[10px] font-bold text-white"
                  style={{ backgroundColor: primaryColor }}
                >
                  {count}
                </span>
              )}
            </div>
            <p className="text-[11px] text-slate-500 truncate">{subtitle}</p>
          </div>
        </div>
        <ChevronDown
          style={{ color: primaryColor }}
          className={`h-4 w-4 shrink-0 transition-transform duration-300 ${
            isOpen ? "rotate-180" : ""
          }`}
        />
      </button>

      <div
        className={`grid transition-all duration-300 ease-out ${
          isOpen ? "grid-rows-[1fr] opacity-100" : "grid-rows-[0fr] opacity-0"
        }`}
      >
        <div className="overflow-hidden">{children}</div>
      </div>
    </div>
  );
};

