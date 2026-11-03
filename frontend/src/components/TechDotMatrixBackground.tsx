import React, { useEffect, useRef } from "react";
import { TipoRelatorio, CategoriaRelatorio } from "../types/report.types";

interface TechDotMatrixProps {
  tipo: TipoRelatorio;
  categoria: CategoriaRelatorio;
  primaryColor: string;
  secondaryColor?: string;
}

interface MatrixPoint {
  // Posição base normalizada (0 a 1)
  baseU: number;
  baseV: number;
  // Posição renderizada atual (pixels)
  x: number;
  y: number;
  targetX: number;
  targetY: number;
  // Raio e elevação
  radius: number;
  targetRadius: number;
  elevation: number;
  targetElevation: number;
  // Opacidade
  alpha: number;
  targetAlpha: number;
}

// Converte hex/rgb para {r, g, b}
function parseColorToRgb(colorStr: string): { r: number; g: number; b: number } {
  if (colorStr.startsWith("#")) {
    let hex = colorStr.slice(1);
    if (hex.length === 3) {
      hex = hex.split("").map((c) => c + c).join("");
    }
    const num = parseInt(hex, 16);
    return {
      r: (num >> 16) & 255,
      g: (num >> 8) & 255,
      b: num & 255,
    };
  }
  const match = colorStr.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/);
  if (match) {
    return {
      r: parseInt(match[1], 10),
      g: parseInt(match[2], 10),
      b: parseInt(match[3], 10),
    };
  }
  return { r: 37, g: 99, b: 235 }; // fallback azul ARPE
}

export const TechDotMatrixBackground: React.FC<TechDotMatrixProps> = ({
  tipo,
  categoria,
  primaryColor,
  secondaryColor = "#0284c7",
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const pointsRef = useRef<MatrixPoint[]>([]);
  const animFrameRef = useRef<number | null>(null);
  const colorCurrentRef = useRef<{ r: number; g: number; b: number }>({ r: 30, g: 58, b: 138 });
  const colorTargetRef = useRef<{ r: number; g: number; b: number }>({ r: 30, g: 58, b: 138 });
  const isTransitioningRef = useRef<boolean>(true);
  const transitionStartRef = useRef<number>(performance.now());
  const gridDimsRef = useRef<{ cols: number; rows: number }>({ cols: 32, rows: 20 });

  // Atualiza a cor alvo sempre que primaryColor mudar
  useEffect(() => {
    colorTargetRef.current = parseColorToRgb(primaryColor);
    isTransitioningRef.current = true;
    transitionStartRef.current = performance.now();
  }, [primaryColor]);

  // Função matemática para calcular elevação e deslocamento de cada ponto (6 combinações)
  const computePointTarget = (
    u: number,
    v: number,
    w: number,
    h: number,
    t: TipoRelatorio,
    c: CategoriaRelatorio
  ): { targetX: number; targetY: number; targetRadius: number; targetElevation: number; targetAlpha: number } => {
    let elevation = 0;
    let dispX = 0;
    let dispY = 0;

    const isMonitoramento = c === "Monitoramento";

    if (t === "CRA") {
      // CRA: Relevo Rodoviário Longitudinal (faixas de rolamento, aclives e curvas de nível de Suape)
      if (!isMonitoramento) {
        // Fiscalização: Duas faixas paralelas com relevo central (pista dupla)
        const wave1 = Math.sin(u * Math.PI * 3 + v * 1.5) * 0.5 + 0.5;
        const valley = Math.exp(-Math.pow((v - 0.45) * 3.5, 2));
        elevation = wave1 * valley;
        dispY = -elevation * 42;
        dispX = (v - 0.5) * 20 * elevation;
      } else {
        // Monitoramento: Malha de auditoria longitudinal com ondas intercaladas
        const wave = Math.sin(u * Math.PI * 4 + v * 2) * Math.cos(v * Math.PI * 2);
        elevation = Math.max(0, wave * 0.8 + 0.2);
        dispY = -elevation * 36;
        dispX = Math.sin(u * 5) * 12 * elevation;
      }
    } else if (t === "CRC") {
      // CRC: Ondulação Costeira Paramétrica & Curvatura de Ponte Estaiada (Litoral Paiva / PE-024)
      if (!isMonitoramento) {
        // Fiscalização: Crista marítima diagonal fluida
        const diag = u * 0.7 + v * 0.3;
        const wave = Math.sin(diag * Math.PI * 3.5) * 0.5 + 0.5;
        const envelope = Math.sin(u * Math.PI) * Math.sin(v * Math.PI);
        elevation = wave * envelope * 1.2;
        dispY = -elevation * 48;
        dispX = Math.cos(diag * 4) * 16 * elevation;
      } else {
        // Monitoramento: Arco estaiado contínuo (Ponte do Paiva) com ondulação litorânea perimetral de ponta a ponta
        const bridgeArc = Math.cos((u - 0.5) * Math.PI * 1.5) * Math.exp(-Math.pow((v - 0.42) * 2.8, 2));
        const edgeRipple = (Math.sin(u * Math.PI * 3.5 + v * 2) * 0.5 + 0.5) * 0.45;
        elevation = Math.min(1, Math.max(0.18, bridgeArc * 0.75 + edgeRipple));
        dispY = -elevation * 38;
        dispX = Math.sin((u - 0.5) * Math.PI) * 18 * elevation;
      }
    } else {
      // SOCICAM: Grelha Arquitetônica e Cúpulas de Terminais Rodoviários (Recife, Caruaru, Garanhuns, Petrolina)
      if (!isMonitoramento) {
        // Fiscalização: Cúpula esférica arquitetural central com expansão radial
        const cx = 0.55;
        const cy = 0.42;
        const dist = Math.hypot((u - cx) * 1.4, (v - cy));
        elevation = Math.max(0, Math.cos(Math.min(1, dist * 2.2) * Math.PI * 0.5));
        dispY = -elevation * 38;
        dispX = (u - cx) * 30 * elevation;
      } else {
        // Monitoramento: Matriz nodal de 4 quadrantes (terminais intermunicipais)
        const d1 = Math.hypot(u - 0.35, v - 0.35);
        const d2 = Math.hypot(u - 0.68, v - 0.52);
        const e1 = Math.max(0, 1 - d1 * 3.5);
        const e2 = Math.max(0, 1 - d2 * 3.5);
        elevation = Math.min(1, e1 + e2);
        dispY = -elevation * 34;
        dispX = (Math.sin(u * 10) * 8) * elevation;
      }
    }

    // Posição absoluta com o deslocamento tridimensional
    const targetX = u * w + dispX;
    const targetY = v * h + dispY;

    // Escala do ponto baseada na elevação: cristas recebem pontos maiores e mais destacados
    const targetRadius = 0.9 + elevation * 2.3;
    // Opacidade refinada: sutil no plano base (~0.05), expressiva nas elevações (~0.22 a 0.28)
    const targetAlpha = 0.045 + elevation * 0.18;

    return {
      targetX,
      targetY,
      targetRadius,
      targetElevation: elevation,
      targetAlpha,
    };
  };

  // Inicializa ou redimensiona a grade de pontos
  const setupGrid = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const w = canvas.offsetWidth;
    const h = canvas.offsetHeight;
    if (w <= 0 || h <= 0) return;

    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = w * dpr;
    canvas.height = h * dpr;

    const cols = Math.max(20, Math.floor(w / 38));
    const rows = Math.max(14, Math.floor(h / 38));
    gridDimsRef.current = { cols, rows };

    const newPoints: MatrixPoint[] = [];

    for (let j = 0; j < rows; j++) {
      for (let i = 0; i < cols; i++) {
        // Margem de 4% nas bordas para arremate visual
        const u = 0.04 + (i / (cols - 1)) * 0.92;
        const v = 0.04 + (j / (rows - 1)) * 0.92;

        const target = computePointTarget(u, v, w, h, tipo, categoria);

        // Se já existiam pontos, reaproveita posição atual para transição contínua
        const existingIdx = j * cols + i;
        const existing = pointsRef.current[existingIdx];

        newPoints.push({
          baseU: u,
          baseV: v,
          x: existing ? existing.x : target.targetX,
          y: existing ? existing.y : target.targetY,
          targetX: target.targetX,
          targetY: target.targetY,
          radius: existing ? existing.radius : target.targetRadius,
          targetRadius: target.targetRadius,
          elevation: existing ? existing.elevation : target.targetElevation,
          targetElevation: target.targetElevation,
          alpha: existing ? existing.alpha : target.targetAlpha,
          targetAlpha: target.targetAlpha,
        });
      }
    }

    pointsRef.current = newPoints;
    isTransitioningRef.current = true;
    transitionStartRef.current = performance.now();
  };

  // Atualiza os alvos dos pontos quando a concessão ou o tipo mudarem
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const w = canvas.offsetWidth;
    const h = canvas.offsetHeight;
    if (w <= 0 || h <= 0) return;

    const points = pointsRef.current;
    if (points.length === 0) {
      setupGrid();
      return;
    }

    for (let p of points) {
      const target = computePointTarget(p.baseU, p.baseV, w, h, tipo, categoria);
      p.targetX = target.targetX;
      p.targetY = target.targetY;
      p.targetRadius = target.targetRadius;
      p.targetElevation = target.targetElevation;
      p.targetAlpha = target.targetAlpha;
    }

    isTransitioningRef.current = true;
    transitionStartRef.current = performance.now();
  }, [tipo, categoria]);

  // Listener de resize com debounce
  useEffect(() => {
    let resizeTimer: number;
    const handleResize = () => {
      window.clearTimeout(resizeTimer);
      resizeTimer = window.setTimeout(() => {
        setupGrid();
      }, 100);
    };

    setupGrid();
    window.addEventListener("resize", handleResize, { passive: true });
    return () => {
      window.removeEventListener("resize", handleResize);
      window.clearTimeout(resizeTimer);
    };
  }, []);

  // Loop de Renderização a 60 FPS com desaceleração em repouso
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let isRunning = true;

    const render = () => {
      if (!isRunning) return;

      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const w = canvas.offsetWidth;
      const h = canvas.offsetHeight;

      ctx.save();
      ctx.scale(dpr, dpr);
      ctx.clearRect(0, 0, w, h);

      // Transição suave da cor primária (lerp)
      const colorCur = colorCurrentRef.current;
      const colorTar = colorTargetRef.current;
      colorCur.r += (colorTar.r - colorCur.r) * 0.08;
      colorCur.g += (colorTar.g - colorCur.g) * 0.08;
      colorCur.b += (colorTar.b - colorCur.b) * 0.08;

      const rInt = Math.round(colorCur.r);
      const gInt = Math.round(colorCur.g);
      const bInt = Math.round(colorCur.b);

      const points = pointsRef.current;
      const { cols, rows } = gridDimsRef.current;

      let maxDelta = 0;
      // Taxa de interpolação física dos pontos (easing suave)
      const lerpFactor = 0.095;

      for (let p of points) {
        const dx = (p.targetX - p.x) * lerpFactor;
        const dy = (p.targetY - p.y) * lerpFactor;
        const dr = (p.targetRadius - p.radius) * lerpFactor;
        const da = (p.targetAlpha - p.alpha) * lerpFactor;
        const de = (p.targetElevation - p.elevation) * lerpFactor;

        p.x += dx;
        p.y += dy;
        p.radius += dr;
        p.alpha += da;
        p.elevation += de;

        const delta = Math.abs(dx) + Math.abs(dy);
        if (delta > maxDelta) maxDelta = delta;
      }

      // 1. DESENHO DAS LINHAS PONTILHADAS TÉCNICAS (Grelhas de Elevação)
      // Conecta horizontalmente pontos adjacentes com traçado pontilhado fino
      ctx.lineWidth = 1;
      ctx.setLineDash([2, 5]);

      for (let j = 0; j < rows; j++) {
        const rowStartIdx = j * cols;
        // Desenha linhas pontilhadas técnicas apenas em fileiras selecionadas ou onde há elevação
        if (j % 2 === 0 || tipo === "SOCICAM") {
          ctx.beginPath();
          let lineHasElevation = false;

          for (let i = 0; i < cols; i++) {
            const pt = points[rowStartIdx + i];
            if (!pt) continue;

            if (pt.elevation > 0.08) lineHasElevation = true;

            if (i === 0) {
              ctx.moveTo(pt.x, pt.y);
            } else {
              ctx.lineTo(pt.x, pt.y);
            }
          }

          // A intensidade da linha acompanha a elevação do relevo
          const lineAlpha = lineHasElevation ? 0.08 : 0.035;
          ctx.strokeStyle = `rgba(${rInt}, ${gInt}, ${bInt}, ${lineAlpha})`;
          ctx.stroke();
        }
      }

      // 2. DESENHO DA MATRIZ DE PONTOS (Dot Matrix Halftone)
      ctx.setLineDash([]); // Restaura traço sólido para preenchimento dos círculos

      for (let p of points) {
        if (p.radius <= 0.1 || p.alpha <= 0.005) continue;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${rInt}, ${gInt}, ${bInt}, ${p.alpha})`;
        ctx.fill();

        // Auréola sutil em pontos de alta elevação (cristas topográficas)
        if (p.elevation > 0.55) {
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.radius + 1.8, 0, Math.PI * 2);
          ctx.fillStyle = `rgba(${rInt}, ${gInt}, ${bInt}, ${p.alpha * 0.28})`;
          ctx.fill();
        }
      }

      ctx.restore();

      // Se a transição se completou (delta mínimo e cor convergida), desacelera para economizar bateria
      const colorDiff =
        Math.abs(colorCur.r - colorTar.r) +
        Math.abs(colorCur.g - colorTar.g) +
        Math.abs(colorCur.b - colorTar.b);

      if (maxDelta < 0.04 && colorDiff < 0.5) {
        isTransitioningRef.current = false;
        // Entra em repouso: aguarda próximo ciclo de evento sem disparar 60fps desnecessários
        animFrameRef.current = window.setTimeout(render, 300) as unknown as number;
      } else {
        animFrameRef.current = window.requestAnimationFrame(render);
      }
    };

    render();

    return () => {
      isRunning = false;
      if (animFrameRef.current !== null) {
        window.cancelAnimationFrame(animFrameRef.current);
        window.clearTimeout(animFrameRef.current);
      }
    };
  }, [tipo, categoria]);

  return (
    <canvas
      ref={canvasRef}
      className="pointer-events-none fixed inset-0 z-0 h-full w-full select-none"
      aria-hidden="true"
    />
  );
};

