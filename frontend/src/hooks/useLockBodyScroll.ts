import { useEffect } from "react";

/**
 * Hook para travar o scroll do body enquanto um modal ou diálogo estiver aberto.
 * Previne que o scroll do mouse na janela role a página de fundo.
 */
export function useLockBodyScroll(isLocked: boolean = true) {
  useEffect(() => {
    if (!isLocked) return;

    const originalOverflow = document.body.style.overflow;
    const originalPaddingRight = document.body.style.paddingRight;

    // Calcula a largura da barra de scroll para evitar salto visual (layout shift)
    const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;

    document.body.style.overflow = "hidden";
    if (scrollbarWidth > 0) {
      document.body.style.paddingRight = `${scrollbarWidth}px`;
    }

    return () => {
      document.body.style.overflow = originalOverflow;
      document.body.style.paddingRight = originalPaddingRight;
    };
  }, [isLocked]);
}

