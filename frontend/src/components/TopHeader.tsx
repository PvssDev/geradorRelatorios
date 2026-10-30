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
}: {
  label: string;
  options: T[];
  value: T;
  onChange: (v: T) => void;
  activeColor?: string;
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

  return (
    <div className="flex items-center gap-2 rounded-full border border-[#d6e5f5] bg-[#edf4fb] p-1 pl-3.5 shadow-xs">
      <span className="text-[10px] font-bold uppercase tracking-[0.16em] text-[#1e3a5a]">
        {label}
      </span>
      <div
        ref={containerRef}
        className="relative flex items-center rounded-full bg-white/70 p-0.5 border border-[#d6e5f5]"
      >
        {/* Bullet animado com cor temática dinâmica da concessão/tipo */}
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
              className={`relative z-10 rounded-full px-3.5 py-1 text-xs font-bold transition-colors duration-200 ${
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

  const theme = getConcessionTheme(tipoRelatorio, categoriaRelatorio);
  const isFiscalizacao = categoriaRelatorio === "Fiscalização";
  const activePillColor = theme.primary;

  const tipos: TipoRelatorio[] = ["CRA", "CRC", "SOCICAM"];
  const categorias: CategoriaRelatorio[] = ["Fiscalização", "Monitoramento"];

  const kicker =
    tipoRelatorio === "SOCICAM"
      ? `ARPE · ${categoriaRelatorio} de Terminais`
      : `ARPE · ${categoriaRelatorio} Rodoviária`;

  return (
    <header className="sticky top-0 z-30 border-b border-[#d8e5f2] bg-white shadow-xs">
      <div className="mx-auto flex max-w-5xl flex-wrap items-center justify-between gap-x-6 gap-y-4 px-6 py-4">
        <div className="flex items-center gap-4">
          <button
            type="button"
            aria-label="Abrir menu"
            className="lg:hidden grid h-10 w-10 place-items-center rounded-xl border border-[#d6e5f5] bg-[#edf4fb] text-[#1e3a5a]"
            onClick={onToggleMobileMenu}
          >
            <Menu className="h-5 w-5" />
          </button>

          <span className="grid h-12 w-12 shrink-0 place-items-center rounded-2xl bg-[#071d36] text-white shadow-card">
            <FileText className="h-6 w-6 text-white" />
          </span>

          <div>
            <div className="text-[11px] font-bold uppercase tracking-[0.22em] text-[#2563eb]">
              {kicker}
            </div>
            <h1 className="text-3xl font-extrabold leading-none tracking-tight text-[#071d36] sm:text-4xl">
              Gerador de Relatórios
            </h1>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Segmented
            label="Concessão"
            options={tipos}
            value={tipoRelatorio}
            onChange={setTipoRelatorio}
            activeColor={theme.primary}
          />
          <Segmented
            label="Tipo"
            options={categorias}
            value={categoriaRelatorio}
            onChange={setCategoriaRelatorio}
            activeColor={activePillColor}
          />
          <span className="flex items-center gap-1.5 rounded-full bg-[#e8f8f0] px-3.5 py-1.5 text-xs font-bold text-[#059669] border border-[#bbf0d8]">
            <span className="h-2 w-2 rounded-full bg-[#10b981]" /> Conectado
          </span>
        </div>
      </div>
    </header>
  );
};
