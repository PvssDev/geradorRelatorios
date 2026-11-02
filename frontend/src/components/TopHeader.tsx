import React from "react";
import { FileText, Menu } from "lucide-react";
import { useReportStore } from "../store/useReportStore";
import { CategoriaRelatorio, TipoRelatorio } from "../types/report.types";
import { getConcessionTheme } from "../utils/concessionTheme";

interface TopHeaderProps {
  onToggleMobileMenu: () => void;
}

function Segmented<T extends string>({
  label,
  options,
  value,
  onChange,
  activeColor,
  compact = false,
}: {
  label: string;
  options: T[];
  value: T;
  onChange: (v: T) => void;
  activeColor?: string;
  compact?: boolean;
}) {
  const containerRef = React.useRef<HTMLDivElement>(null);
  const buttonRefs = React.useRef<(HTMLButtonElement | null)[]>([]);
  const [sliderStyle, setSliderStyle] = React.useState<{
    left: number;
    width: number;
    ready: boolean;
  }>({
    left: 0,
    width: 0,
    ready: false,
  });

  const updateSlider = React.useCallback(() => {
    const activeIndex = options.indexOf(value);
    const activeBtn = buttonRefs.current[activeIndex];
    if (activeBtn) {
      setSliderStyle({
        left: activeBtn.offsetLeft,
        width: activeBtn.offsetWidth,
        ready: true,
      });
    }
  }, [value, options]);

  React.useEffect(() => {
    updateSlider();
    window.addEventListener("resize", updateSlider);
    return () => window.removeEventListener("resize", updateSlider);
  }, [updateSlider]);

  // Recalibra o slider suavemente quando o cabeçalho encolhe ou expande
  React.useEffect(() => {
    const timer = setTimeout(updateSlider, 50);
    return () => clearTimeout(timer);
  }, [compact, updateSlider]);

  return (
    <div
      className={`flex items-center gap-2 rounded-full border border-[#cbd5e1] bg-[#f1f5f9] shadow-xs transition-all duration-300 ${
        compact ? "p-0.5 pl-3" : "p-1 pl-3.5"
      }`}
    >
      <span className="text-[10px] font-bold uppercase tracking-[0.16em] text-[#1e3a5a]">
        {label}
      </span>
      <div
        ref={containerRef}
        className="relative flex items-center rounded-full bg-white p-0.5 border border-[#cbd5e1]"
      >
        {sliderStyle.ready && (
          <div
            className="absolute top-0.5 bottom-0.5 rounded-full shadow-sm transition-all duration-300 ease-[cubic-bezier(0.25,1,0.5,1)]"
            style={{
              left: `${sliderStyle.left}px`,
              width: `${sliderStyle.width}px`,
              backgroundColor: activeColor || "#2563eb",
            }}
          />
        )}
        {options.map((o, idx) => {
          const isAct = value === o;
          return (
            <button
              key={o}
              ref={(el) => (buttonRefs.current[idx] = el)}
              type="button"
              onClick={() => onChange(o)}
              className={`relative z-10 rounded-full font-bold transition-all duration-200 ${
                compact ? "px-3 py-0.5 text-[11px]" : "px-3.5 py-1 text-xs"
              } ${
                isAct
                  ? "text-white drop-shadow-xs"
                  : "text-[#334e68] hover:text-[#071d36]"
              }`}
            >
              {o}
            </button>
          );
        })}
      </div>
    </div>
  );
}

export const TopHeader: React.FC<TopHeaderProps> = ({ onToggleMobileMenu }) => {
  const {
    tipoRelatorio,
    categoriaRelatorio,
    setTipoRelatorio,
    setCategoriaRelatorio,
  } = useReportStore();

  const [scrolled, setScrolled] = React.useState(false);

  React.useEffect(() => {
    const handleScroll = () => {
      const isPast = window.scrollY > 20;
      setScrolled((prev) => (prev !== isPast ? isPast : prev));
    };

    handleScroll();
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const theme = getConcessionTheme(tipoRelatorio, categoriaRelatorio);
  const activePillColor = theme.primary;

  const tipos: TipoRelatorio[] = ["CRA", "CRC", "SOCICAM"];
  const categorias: CategoriaRelatorio[] = ["Fiscalização", "Monitoramento"];

  const kicker =
    tipoRelatorio === "SOCICAM"
      ? `ARPE · ${categoriaRelatorio} de Terminais`
      : `ARPE · ${categoriaRelatorio} Rodoviária`;

  return (
    <header
      className={`sticky top-0 z-30 border-b border-[#cbd5e1] transition-all duration-300 ease-[cubic-bezier(0.25,1,0.5,1)] ${
        scrolled
          ? "bg-white/98 shadow-md shadow-slate-900/5 backdrop-blur-xl"
          : "bg-white/95 shadow-xs backdrop-blur-xl"
      }`}
    >
      <div
        className={`mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-x-6 gap-y-2 px-6 transition-all duration-300 ease-[cubic-bezier(0.25,1,0.5,1)] ${
          scrolled ? "py-2 sm:py-2.5" : "py-4 sm:py-5"
        }`}
      >
        {/* Bloco de Título e Marca */}
        <div className="flex items-center gap-3 sm:gap-4 transition-all duration-300">
          <button
            type="button"
            aria-label="Abrir menu"
            className="lg:hidden grid h-9 w-9 place-items-center rounded-xl border border-[#cbd5e1] bg-[#edf4fb] text-[#1e3a5a] transition hover:bg-[#dbeafe]"
            onClick={onToggleMobileMenu}
          >
            <Menu className="h-5 w-5" />
          </button>

          <span
            className={`grid shrink-0 place-items-center rounded-2xl bg-[#071d36] text-white shadow-card transition-all duration-300 ${
              scrolled ? "h-9 w-9 rounded-xl" : "h-12 w-12 rounded-2xl"
            }`}
          >
            <FileText
              className={`transition-all duration-300 ${
                scrolled ? "h-4 w-4" : "h-6 w-6"
              }`}
            />
          </span>

          <div className="flex flex-col justify-center transition-all duration-300">
            <div
              className={`font-bold uppercase tracking-[0.2em] transition-all duration-300 leading-tight ${
                scrolled ? "text-[9px] mb-0.5" : "text-[11px] mb-1"
              }`}
              style={{ color: theme.primary }}
            >
              {kicker}
            </div>
            <h1
              className={`font-extrabold leading-none tracking-tight text-[#071d36] transition-all duration-300 ${
                scrolled ? "text-xl sm:text-2xl" : "text-3xl sm:text-4xl"
              }`}
            >
              Gerador de Relatórios
            </h1>
          </div>
        </div>

        {/* Seletores Segmentados de Concessão e Tipo */}
        <div className="flex flex-wrap items-center gap-2 sm:gap-3 transition-all duration-300">
          <Segmented
            label="Concessão"
            options={tipos}
            value={tipoRelatorio}
            onChange={setTipoRelatorio}
            activeColor={theme.primary}
            compact={scrolled}
          />
          <Segmented
            label="Tipo"
            options={categorias}
            value={categoriaRelatorio}
            onChange={setCategoriaRelatorio}
            activeColor={activePillColor}
            compact={scrolled}
          />
        </div>
      </div>
    </header>
  );
};
