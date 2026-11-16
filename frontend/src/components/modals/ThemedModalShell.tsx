import React, { ReactNode } from "react";
import { createPortal } from "react-dom";
import { X } from "lucide-react";
import { useLockBodyScroll } from "../../hooks/useLockBodyScroll";
import { useConcessionTheme } from "../../hooks/useConcessionTheme";

interface ThemedModalShellProps {
  icon: ReactNode;
  title: string;
  subtitle?: string;
  maxWidthClass?: string;
  accentColor?: string;
  onClose: () => void;
  children: ReactNode;
}

/**
 * Casca padronizada para todas as janelas/modais da aplicação.
 * Encapsula Portal, bloqueio de scroll, animação de abertura, cabeçalho Dark Navy
 * e injeta as variáveis CSS do tema ativo (--modal-primary, --modal-soft, --modal-border).
 */
export const ThemedModalShell: React.FC<ThemedModalShellProps> = ({
  icon,
  title,
  subtitle,
  maxWidthClass = "max-w-md",
  accentColor,
  onClose,
  children,
}) => {
  useLockBodyScroll(true);
  const theme = useConcessionTheme();
  const primary = accentColor || theme.primary;

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-[2px] animate-in fade-in"
      role="dialog"
      aria-modal="true"
    >
      <div
        style={
          {
            "--modal-primary": primary,
            "--modal-soft": theme.lightBg,
            "--modal-border": theme.lightBorder,
          } as React.CSSProperties
        }
        className={`flex max-h-[90dvh] w-full ${maxWidthClass} flex-col overflow-hidden rounded-[28px] border border-slate-700/30 bg-white shadow-2xl animate-in fade-in zoom-in-95 duration-150`}
      >
        <div className="flex items-center justify-between border-b border-slate-800 bg-[#0b1728] px-5 py-4 text-white">
          <div className="flex items-center gap-3 min-w-0">
            <div
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl text-white shadow-sm"
              style={{ backgroundColor: primary }}
            >
              {icon}
            </div>
            <div className="min-w-0">
              <h3 className="truncate text-sm font-bold tracking-wide">
                {title}
              </h3>
              {subtitle && (
                <p className="truncate text-[11px] text-slate-400">{subtitle}</p>
              )}
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label="Fechar janela"
            className="rounded-lg p-1 text-slate-400 hover:bg-white/10 hover:text-white transition shrink-0"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {children}
      </div>
    </div>,
    document.body
  );
};

