import React, { useEffect, useRef, useState, type ReactNode } from "react";
import { createPortal } from "react-dom";
import { Check } from "lucide-react";

/**
 * Gerencia abertura, fechamento (Escape) e coordenadas fixas para menus suspensos
 * ancorados abaixo de cards com overflow-hidden via React Portal.
 */
export function useAnchoredDropdown() {
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
export function AnchoredPortalMenu({
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
export function DropdownOptionItem({
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

