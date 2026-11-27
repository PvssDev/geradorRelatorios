import { CategoriaRelatorio, TipoRelatorio } from "../types/report.types";

export interface ConcessionTheme {
  primary: string;
  secondary: string;
  accentGlow: string;
  badgeBg: string;
  textPrimary: string;
  borderLeft: string;
  lightBg: string;
  lightBorder: string;
  pastelBg: string;
  stripeColors: [string, string, string];
}

export function isPerformanceModeActive(): boolean {
  try {
    return localStorage.getItem("arpe_perf_mode") === "true";
  } catch {
    return false;
  }
}

export function getConcessionTheme(
  tipo: TipoRelatorio,
  categoria: CategoriaRelatorio = "Fiscalização",
  forceDynamic: boolean = false
): ConcessionTheme {
  // Quando o modo de cor fixa estiver ativo, fixa os detalhes na cor padrão de CRA Fiscalização
  if (!forceDynamic && isPerformanceModeActive()) {
    return {
      primary: "#2563eb", // Azul Royal
      secondary: "#0ea5e9", // Sky blue luminoso
      accentGlow: "#6366f1", // Índigo corporativo
      badgeBg: "bg-[#2563eb]",
      textPrimary: "text-[#2563eb]",
      borderLeft: "border-l-[#2563eb]",
      lightBg: "#f0f6ff",
      lightBorder: "#bfdbfe",
      pastelBg: "#e8f1ff",
      stripeColors: ["#93c5fd", "#3b82f6", "#1d4ed8"],
    };
  }
  const isMonitoring = categoria === "Monitoramento";

  if (isMonitoring) {
    switch (tipo) {
      case "SOCICAM":
        return {
          primary: "#ea580c", // Laranja quente
          secondary: "#f59e0b", // Âmbar solar
          accentGlow: "#d97706", // Âmbar dourado
          badgeBg: "bg-[#ea580c]",
          textPrimary: "text-[#ea580c]",
          borderLeft: "border-l-[#ea580c]",
          lightBg: "#fff9f5",
          lightBorder: "#fed7aa",
          pastelBg: "#fff2e6",
          stripeColors: ["#fdba74", "#f97316", "#c2410c"],
        };
      case "CRC":
        return {
          primary: "#e11d48", // Coral / Roseo de transição
          secondary: "#f43f5e", // Rose vibrante
          accentGlow: "#fb7185", // Coral suave
          badgeBg: "bg-[#e11d48]",
          textPrimary: "text-[#e11d48]",
          borderLeft: "border-l-[#e11d48]",
          lightBg: "#fff5f6",
          lightBorder: "#fecdd3",
          pastelBg: "#ffecf0",
          stripeColors: ["#fda4af", "#f43f5e", "#be123c"],
        };
      case "CRA":
      default:
        return {
          primary: "#dc2626", // Vermelho regulatório
          secondary: "#ea580c", // Laranja carmim
          accentGlow: "#f43f5e", // Rose quente
          badgeBg: "bg-[#dc2626]",
          textPrimary: "text-[#dc2626]",
          borderLeft: "border-l-[#dc2626]",
          lightBg: "#fff5f5",
          lightBorder: "#fecaca",
          pastelBg: "#ffeded",
          stripeColors: ["#fca5a5", "#ef4444", "#b91c1c"],
        };
    }
  }

  // Modo Fiscalização (Tons frios corporativos)
  switch (tipo) {
    case "CRC":
      return {
        primary: "#0095c4", // Ciano Oceânico
        secondary: "#06b6d4", // Ciano turquesa
        accentGlow: "#0284c7", // Sky blue profundo
        badgeBg: "bg-[#0095c4]",
        textPrimary: "text-[#0095c4]",
        borderLeft: "border-l-[#0095c4]",
        lightBg: "#f0f9ff",
        lightBorder: "#bae6fd",
        pastelBg: "#e5f6fd",
        stripeColors: ["#67e8f9", "#06b6d4", "#0369a1"],
      };
    case "SOCICAM":
      return {
        primary: "#5b52c6", // Índigo / Púrpura
        secondary: "#8b5cf6", // Violeta elegante
        accentGlow: "#6366f1", // Índigo radiante
        badgeBg: "bg-[#5b52c6]",
        textPrimary: "text-[#5b52c6]",
        borderLeft: "border-l-[#5b52c6]",
        lightBg: "#f6f5ff",
        lightBorder: "#ddd6fe",
        pastelBg: "#f1efff",
        stripeColors: ["#c4b5fd", "#7c3aed", "#4338ca"],
      };
    case "CRA":
    default:
      return {
        primary: "#2563eb", // Azul Royal
        secondary: "#0ea5e9", // Sky blue luminoso
        accentGlow: "#6366f1", // Índigo corporativo
        badgeBg: "bg-[#2563eb]",
        textPrimary: "text-[#2563eb]",
        borderLeft: "border-l-[#2563eb]",
        lightBg: "#f0f6ff",
        lightBorder: "#bfdbfe",
        pastelBg: "#e8f1ff",
        stripeColors: ["#93c5fd", "#3b82f6", "#1d4ed8"],
      };
  }
}
