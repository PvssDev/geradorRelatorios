export const modalInputCls =
  "w-full rounded-lg border border-input bg-secondary/60 px-3 py-2 text-sm text-foreground outline-none focus:border-ring focus:ring-2 focus:ring-ring/20";

export const modalPill = (on: boolean) =>
  `rounded-full border px-3 py-1 text-xs font-medium transition ${
    on
      ? "border-accent bg-accent text-accent-foreground"
      : "border-border bg-card text-muted-foreground hover:border-accent/50"
  }`;
