import { useEffect, useRef } from "react";

/**
 * Hook para detectar cliques fora de um elemento de referência do DOM.
 * Utiliza o evento 'pointerdown' para captura imediata e compatibilidade
 * cross-device (mouse, touch, caneta).
 *
 * @param ref Referência React do elemento que deve ser monitorado.
 * @param handler Função de callback executada quando ocorrer clique fora.
 * @param enabled Se o listener deve estar ativo (útil para só monitorar quando o elemento estiver aberto).
 */
export function useClickOutside<T extends HTMLElement = HTMLElement>(
  ref: React.RefObject<T | null>,
  handler: (event: PointerEvent | MouseEvent) => void,
  enabled: boolean = true
): void {
  const handlerRef = useRef(handler);
  handlerRef.current = handler;

  useEffect(() => {
    if (!enabled) return;

    const listener = (event: PointerEvent | MouseEvent) => {
      const el = ref.current;
      if (!el) return;

      const target = event.target as Node | null;
      if (!target) return;

      // Se o clique ocorreu dentro do elemento referenciado, ignora
      if (el.contains(target)) return;

      handlerRef.current(event);
    };

    document.addEventListener("pointerdown", listener, { passive: true });
    return () => {
      document.removeEventListener("pointerdown", listener);
    };
  }, [ref, enabled]);
}

