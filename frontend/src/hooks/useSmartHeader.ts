import { useState, useEffect, useRef, useCallback } from "react";

export interface SmartHeaderControls {
  headerRef: React.RefObject<HTMLElement | null>;
  offsetY: number;
  isAnimating: boolean;
  resetHeader: () => void;
  headerHeight: number;
}

/**
 * Hook customizado para Cabeçalho Inteligente com Deslocamento Proporcional (Scroll Clamping).
 * - Acompanha a rolagem milimetricamente: se o usuário rolar 30px, o cabeçalho sobe 30px.
 * - Se o usuário parar de rolar, o cabeçalho permanece no ponto exato (visível pela metade).
 * - Ao rolar para cima, o cabeçalho desce proporcionalmente até a visibilidade total.
 * - Ao clicar no cabeçalho parcialmente visível, `resetHeader()` desliza-o suavemente de volta a 0.
 * - Execução a 60fps sincronizada via requestAnimationFrame e passive event listeners.
 */
export function useSmartHeader(initialHeight: number = 80): SmartHeaderControls {
  const headerRef = useRef<HTMLElement | null>(null);
  const [offsetY, setOffsetY] = useState<number>(0);
  const [isAnimating, setIsAnimating] = useState<boolean>(false);
  const [headerHeight, setHeaderHeight] = useState<number>(initialHeight);

  const lastScrollYRef = useRef<number>(0);
  const currentOffsetRef = useRef<number>(0);
  const tickingRef = useRef<boolean>(false);
  const animTimerRef = useRef<number | null>(null);

  // Sincroniza a altura real do elemento no DOM
  useEffect(() => {
    const measure = () => {
      if (headerRef.current) {
        const h = headerRef.current.offsetHeight;
        if (h > 0) {
          setHeaderHeight(h);
        }
      }
    };

    measure();
    window.addEventListener("resize", measure, { passive: true });
    return () => window.removeEventListener("resize", measure);
  }, []);

  // Restauração suave do cabeçalho ao ser clicado
  const resetHeader = useCallback(() => {
    setIsAnimating(true);
    currentOffsetRef.current = 0;
    setOffsetY(0);

    if (animTimerRef.current !== null) {
      window.clearTimeout(animTimerRef.current);
    }

    animTimerRef.current = window.setTimeout(() => {
      setIsAnimating(false);
      animTimerRef.current = null;
    }, 320);
  }, []);

  useEffect(() => {
    lastScrollYRef.current = Math.max(0, window.scrollY);

    const updateScroll = () => {
      const currentScrollY = Math.max(0, window.scrollY);
      const lastScrollY = lastScrollYRef.current;
      const delta = currentScrollY - lastScrollY;
      const maxH = headerRef.current?.offsetHeight || headerHeight || 80;

      if (currentScrollY <= 0) {
        currentOffsetRef.current = 0;
      } else {
        // Clamping proporcional contínuo
        const next = Math.min(maxH, Math.max(0, currentOffsetRef.current + delta));
        currentOffsetRef.current = next;
      }

      setOffsetY(currentOffsetRef.current);
      lastScrollYRef.current = currentScrollY;
      tickingRef.current = false;
    };

    const handleScroll = () => {
      // Se houver scroll do usuário enquanto animava, cancela a animação para resposta instantânea
      if (animTimerRef.current !== null) {
        window.clearTimeout(animTimerRef.current);
        animTimerRef.current = null;
        setIsAnimating(false);
      }

      if (!tickingRef.current) {
        window.requestAnimationFrame(updateScroll);
        tickingRef.current = true;
      }
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => {
      window.removeEventListener("scroll", handleScroll);
      if (animTimerRef.current !== null) {
        window.clearTimeout(animTimerRef.current);
      }
    };
  }, [headerHeight]);

  return {
    headerRef,
    offsetY,
    isAnimating,
    resetHeader,
    headerHeight,
  };
}
