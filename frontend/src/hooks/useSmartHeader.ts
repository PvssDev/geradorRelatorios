import { useState, useEffect, useRef } from "react";

/**
 * Hook customizado para Cabeçalho Inteligente (Smart Auto-Hide).
 * - No topo (scrollY <= 60px): sempre visível.
 * - Ao rolar para baixo: recolhe suavemente (-translate-y-full).
 * - Ao rolar para cima: reaparece instantaneamente (translate-y-0).
 * - Execução a 60fps sincronizada via requestAnimationFrame e listener passivo.
 */
export function useSmartHeader(threshold: number = 60, minDelta: number = 8): boolean {
  const [isVisible, setIsVisible] = useState<boolean>(true);
  const lastScrollYRef = useRef<number>(0);
  const tickingRef = useRef<boolean>(false);

  useEffect(() => {
    // Inicializa com a posição atual da janela
    lastScrollYRef.current = window.scrollY;

    const updateScrollDirection = () => {
      const currentScrollY = window.scrollY;
      const lastScrollY = lastScrollYRef.current;
      const delta = currentScrollY - lastScrollY;

      // Se estiver próximo ao topo, garante que o cabeçalho fique sempre visível
      if (currentScrollY <= threshold) {
        setIsVisible(true);
      } else if (Math.abs(delta) >= minDelta) {
        // Rolou para baixo (delta positivo) -> esconde
        // Rolou para cima (delta negativo) -> exibe
        setIsVisible(delta < 0);
      }

      lastScrollYRef.current = currentScrollY <= 0 ? 0 : currentScrollY;
      tickingRef.current = false;
    };

    const handleScroll = () => {
      if (!tickingRef.current) {
        window.requestAnimationFrame(updateScrollDirection);
        tickingRef.current = true;
      }
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, [threshold, minDelta]);

  return isVisible;
}

