import { CategoriaRelatorio, TipoRelatorio } from "../types/report.types";

export interface ConcessionTheme {
  primary: string;
  badgeBg: string;
  textPrimary: string;
  borderLeft: string;
  lightBg: string;
  lightBorder: string;
}

export function getConcessionTheme(
  tipo: TipoRelatorio,
  categoria: CategoriaRelatorio = "Fiscalização"
): ConcessionTheme {
  const isMonitoring = categoria === "Monitoramento";

  if (isMonitoring) {
    switch (tipo) {
      case "SOCICAM":
        return {
          primary: "#ea580c", // Laranja quente
          badgeBg: "bg-[#ea580c]",
          textPrimary: "text-[#ea580c]",
          borderLeft: "border-l-[#ea580c]",
          lightBg: "#fff7ed",
          lightBorder: "#fed7aa",
        };
      case "CRC":
        return {
          primary: "#e11d48", // Coral / Roseo de transição
          badgeBg: "bg-[#e11d48]",
          textPrimary: "text-[#e11d48]",
          borderLeft: "border-l-[#e11d48]",
          lightBg: "#fff1f2",
          lightBorder: "#fecdd3",
        };
      case "CRA":
      default:
        return {
          primary: "#dc2626", // Vermelho regulatório
          badgeBg: "bg-[#dc2626]",
          textPrimary: "text-[#dc2626]",
          borderLeft: "border-l-[#dc2626]",
          lightBg: "#fef2f2",
          lightBorder: "#fecaca",
        };
    }
  }

  // Modo Fiscalização (Tons frios corporativos)
  switch (tipo) {
    case "CRC":
      return {
        primary: "#0095c4", // Ciano Oceânico
        badgeBg: "bg-[#0095c4]",
        textPrimary: "text-[#0095c4]",
        borderLeft: "border-l-[#0095c4]",
        lightBg: "#f0f9ff",
        lightBorder: "#bae6fd",
      };
    case "SOCICAM":
      return {
        primary: "#5b52c6", // Índigo / Púrpura
        badgeBg: "bg-[#5b52c6]",
        textPrimary: "text-[#5b52c6]",
        borderLeft: "border-l-[#5b52c6]",
        lightBg: "#f5f3ff",
        lightBorder: "#ddd6fe",
      };
    case "CRA":
    default:
      return {
        primary: "#2563eb", // Azul Royal
        badgeBg: "bg-[#2563eb]",
        textPrimary: "text-[#2563eb]",
        borderLeft: "border-l-[#2563eb]",
        lightBg: "#eff6ff",
        lightBorder: "#bfdbfe",
      };
  }
}
