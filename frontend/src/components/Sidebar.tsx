import React from "react";
import {
  CloudUpload,
  Building2,
  ImagePlus,
  Table2,
  Rocket,
  Wand2,
  Check,
  ChevronLeft,
  ChevronRight,
  MoreVertical,
} from "lucide-react";
import { toast } from "sonner";
import { useReportStore } from "../store/useReportStore";

interface SidebarProps {
  expanded: boolean;
  onToggleExpand: () => void;
  onNavigate?: () => void;
  dense: boolean;
  onToggleDense: (d: boolean) => void;
}

const NAV_ITEMS = [
  { n: 1, label: "Upload de Mídia", icon: CloudUpload },
  { n: 2, label: "Dados Gerais", icon: Building2 },
  { n: 3, label: "Ocorrências", icon: ImagePlus },
  { n: 4, label: "Auditoria & Tabela", icon: Table2 },
  { n: 5, label: "Emissão", icon: Rocket },
];

export const Sidebar: React.FC<SidebarProps> = ({
  expanded,
  onToggleExpand,
  onNavigate,
  dense,
  onToggleDense,
}) => {
  const {
    tipoRelatorio,
    categoriaRelatorio,
    getActiveWorkspace,
    executarAutoPreenchimento,
  } = useReportStore();
  const ws = getActiveWorkspace();

  const totalFotos = ws.photos.length;
  const ncsCount = ws.registrosNc.filter(
    (r) => (r["Não Conformidade"] || "").trim() !== ""
  ).length;
  const pasCount = ws.registrosNc.length - ncsCount;

  const activeHeader = ws.fiscalizacoes[0];
  const hasHeader = Boolean(
    activeHeader &&
      activeHeader["ID da Fiscalização"]?.trim() &&
      (activeHeader.Cidade?.trim() || activeHeader.Local?.trim())
  );

  // Etapa ativa (1 a 5)
  let step = 1;
  if (ws.relatoriosGerados.length > 0) step = 5;
  else if (ws.registrosNc.length > 0) step = 4;
  else if (totalFotos > 0 && hasHeader) step = 3;
  else if (totalFotos > 0) step = 2;

  const handleDemo = () => {
    executarAutoPreenchimento();
    toast.success("Dados preenchidos automaticamente!");
    if (onNavigate) onNavigate();
  };

  /* ------------------------------------------------------------------------ */
  /* ESTADO RECOLHIDO (Pilar Estreito de Ícones — Coluna 2 da Referência)     */
  /* ------------------------------------------------------------------------ */
  if (!expanded) {
    return (
      <aside className="flex h-full w-[76px] flex-col items-center justify-between border-r border-white/10 bg-navy-gradient py-6 text-sidebar-foreground shadow-xl select-none">
        {/* Topo: Orbe da Marca (clicar expande o menu) */}
        <button
          type="button"
          onClick={onToggleExpand}
          title="Expandir menu lateral"
          aria-label="Expandir menu lateral"
          className="group relative grid h-10 w-10 place-items-center rounded-full bg-brand-gradient shadow-md transition hover:scale-105"
        >
          <span className="text-xs font-extrabold tracking-tighter text-white">
            AR
          </span>
          <span className="absolute -bottom-0.5 -right-0.5 h-2.5 w-2.5 rounded-full border-2 border-navy bg-nc" />
        </button>

        {/* Centro: Ícones de Navegação com Destaque no Item Ativo */}
        <nav className="flex flex-col items-center gap-3">
          {NAV_ITEMS.map(({ n, label, icon: Icon }) => {
            const cur = n === step;
            const done = n < step;
            return (
              <a
                key={n}
                href={`#b${n}`}
                title={`${n}. ${label}`}
                onClick={onNavigate}
                className={`relative grid h-12 w-12 place-items-center rounded-2xl transition ${
                  cur
                    ? "border border-white/15 bg-sidebar-accent text-white shadow-lg"
                    : "text-sidebar-foreground/45 hover:bg-sidebar-accent/50 hover:text-white"
                }`}
              >
                <Icon className="h-5 w-5" />
                {done && (
                  <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-ok" />
                )}
              </a>
            );
          })}
        </nav>

        {/* Rodapé: Ação Rápida + Botão Branco de Expandir (Coluna 3 da Referência) */}
        <div className="flex flex-col items-center gap-3">
          <button
            type="button"
            onClick={handleDemo}
            title="Auto preenchimento"
            aria-label="Auto preenchimento"
            className="grid h-10 w-10 place-items-center rounded-2xl text-sidebar-foreground/55 hover:bg-sidebar-accent hover:text-white transition"
          >
            <Wand2 className="h-4 w-4" />
          </button>

          <button
            type="button"
            onClick={onToggleExpand}
            title="Abrir menu completo"
            aria-label="Abrir menu completo"
            className="grid h-10 w-10 place-items-center rounded-xl bg-white text-primary shadow-md hover:bg-secondary transition"
          >
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>
      </aside>
    );
  }

  /* ------------------------------------------------------------------------ */
  /* ESTADO EXPANDIDO (Card Flutuante Completo — Colunas 1 e 4 da Referência) */
  /* ------------------------------------------------------------------------ */
  return (
    <aside className="flex h-full w-72 flex-col justify-between overflow-y-auto border-r border-white/10 bg-navy-gradient p-6 text-sidebar-foreground shadow-xl select-none">
      {/* Topo: Marca + Botão de Recolher */}
      <div>
        <div className="flex items-center justify-between">
          <button
            type="button"
            onClick={onToggleExpand}
            className="flex items-center gap-2.5 text-left group"
            title="Recolher para barra de ícones"
          >
            <span className="relative grid h-7 w-7 shrink-0 place-items-center rounded-full bg-brand-gradient shadow">
              <span className="h-2 w-2 rounded-full bg-nc absolute -bottom-0.5 -right-0.5 border border-navy" />
            </span>
            <span className="text-base font-bold tracking-tight text-white">
              ARPE<span className="text-accent">.gov</span>
            </span>
          </button>

          <button
            type="button"
            onClick={onToggleExpand}
            title="Recolher menu lateral"
            aria-label="Recolher menu lateral"
            className="grid h-8 w-8 place-items-center rounded-xl bg-sidebar-accent text-sidebar-foreground/70 hover:bg-sidebar-primary hover:text-white transition"
          >
            <ChevronLeft className="h-4 w-4" />
          </button>
        </div>

        {/* Bloco Central de Identidade da Modalidade (Estilo Avatar Central da Coluna 1) */}
        <div className="mt-6 flex flex-col items-center text-center">
          <div className="relative grid h-16 w-16 place-items-center rounded-full border-2 border-accent/60 bg-sidebar-accent shadow-inner">
            <span className="text-base font-extrabold tracking-wider text-white">
              {tipoRelatorio}
            </span>
            <span
              className="absolute bottom-0.5 right-0.5 h-3.5 w-3.5 rounded-full border-2 border-navy bg-ok"
              title="Pasta local sincronizada"
            />
          </div>
          <div className="mt-2.5 text-sm font-bold text-white">
            {tipoRelatorio} · {categoriaRelatorio}
          </div>
          <div className="text-[11px] text-sidebar-foreground/55">
            Agência de Regulação de PE
          </div>

          {/* Mini Pílulas de Estatísticas (Fotos / NCs / PAs) */}
          <div className="mt-4 grid w-full grid-cols-3 gap-2">
            {[
              ["Fotos", totalFotos],
              ["NCs", ncsCount],
              ["PAs", pasCount],
            ].map(([l, v]) => (
              <div
                key={String(l)}
                className="rounded-2xl bg-sidebar-accent/90 py-2 px-1 border border-white/5"
              >
                <div className="text-sm font-bold text-white">{v}</div>
                <div className="text-[10px] text-sidebar-foreground/60">{l}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Menu de Navegação com Indicador Lateral Esquerdo e Pílula Curva */}
        <nav className="mt-6 space-y-1.5">
          {NAV_ITEMS.map(({ n, label, icon: Icon }) => {
            const cur = n === step;
            const done = n < step;
            return (
              <a
                key={n}
                href={`#b${n}`}
                onClick={onNavigate}
                className={`relative flex items-center gap-3.5 rounded-2xl px-4 py-2.5 text-xs font-medium transition ${
                  cur
                    ? "bg-sidebar-accent text-white font-semibold shadow-sm"
                    : "text-sidebar-foreground/65 hover:bg-sidebar-accent/50 hover:text-white"
                }`}
              >
                {/* Barra vertical luminosa na esquerda para o item ativo (igual Coluna 1) */}
                {cur && (
                  <span className="absolute -left-6 h-7 w-1.5 rounded-r-full bg-accent" />
                )}
                <Icon
                  className={`h-4 w-4 shrink-0 ${
                    cur ? "text-accent" : "text-sidebar-foreground/60"
                  }`}
                />
                <span className="flex-1 truncate">{label}</span>
                {done && (
                  <span className="grid h-4 w-4 place-items-center rounded-full bg-ok text-[10px] text-white">
                    <Check className="h-2.5 w-2.5" />
                  </span>
                )}
              </a>
            );
          })}
        </nav>
      </div>

      {/* Card Inferior em Gradiente (Idêntico ao Card "Create Teams" da Coluna 1) */}
      <div className="mt-6 rounded-3xl border border-white/15 bg-gradient-to-br from-accent/40 via-sidebar-accent to-navy p-4 shadow-lg">
        <div className="flex items-start justify-between">
          <div className="grid h-9 w-9 place-items-center rounded-xl bg-white/15 text-white">
            <Wand2 className="h-4 w-4" />
          </div>
          <button
            type="button"
            onClick={() => onToggleDense(!dense)}
            title={`Densidade: ${dense ? "Compacta" : "Confortável"} (clique para alternar)`}
            className="inline-flex items-center gap-1 rounded-full bg-white/10 px-2.5 py-1 text-[10px] font-semibold text-white/90 hover:bg-white/20 transition"
          >
            <MoreVertical className="h-3 w-3" />
            {dense ? "Compacta" : "Confortável"}
          </button>
        </div>

        <div className="mt-3 text-xs font-bold text-white">Ações Rápidas</div>
        <div className="mt-0.5 text-[11px] leading-snug text-white/65">
          Preencha dados de teste ou vá direto para a emissão Word.
        </div>

        <div className="mt-3 flex flex-col gap-2">
          <button
            type="button"
            onClick={handleDemo}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-white py-2 px-3 text-xs font-bold text-primary shadow hover:bg-secondary transition"
          >
            <Wand2 className="h-3.5 w-3.5 text-accent" /> Auto preenchimento
          </button>
          <a
            href="#b5"
            onClick={onNavigate}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-white/10 py-1.5 px-3 text-[11px] font-semibold text-white hover:bg-white/20 transition"
          >
            <Rocket className="h-3.5 w-3.5" /> Ir para emissão
          </a>
        </div>
      </div>
    </aside>
  );
};
