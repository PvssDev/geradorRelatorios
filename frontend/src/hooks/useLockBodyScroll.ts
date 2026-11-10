import { useEffect } from "react";

let lockCount = 0;
let originalOverflow = "";
let originalPaddingRight = "";

/**
 * Hook para travar o scroll do body enquanto um modal ou diálogo estiver aberto.
 * Previne que o scroll do mouse na janela role a página de fundo.
 * Utiliza Reference Counting global para evitar bugs de reentrância em múltiplos modais.
 */
export function useLockBodyScroll(isLocked: boolean = true) {
  useEffect(() => {
    if (!isLocked) return;

    if (lockCount === 0) {
      originalOverflow = document.body.style.overflow;
      originalPaddingRight = document.body.style.paddingRight;

      // Calcula a largura da barra de scroll para evitar salto visual (layout shift)
      const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth;

      document.body.style.overflow = "hidden";
      if (scrollbarWidth > 0) {
        document.body.style.paddingRight = `${scrollbarWidth}px`;
      }
    }
    lockCount++;

    return () => {
      lockCount = Math.max(0, lockCount - 1);
      if (lockCount === 0) {
        document.body.style.overflow =
          originalOverflow && originalOverflow !== "hidden" ? originalOverflow : "";
        document.body.style.paddingRight = originalPaddingRight || "";
      }
    };
  }, [isLocked]);
}
