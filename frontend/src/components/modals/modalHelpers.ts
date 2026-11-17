export const modalInputCls =
  "w-full rounded-lg border border-input bg-secondary/60 px-3 py-2 text-sm text-foreground outline-none transition-all duration-200 hover:border-slate-300 hover:bg-secondary/90 hover:shadow-xs focus:border-[var(--modal-primary,var(--concession-primary))] focus:bg-card focus:ring-2 focus:ring-[var(--modal-primary,var(--concession-primary))]/20";

export const modalPill = (on: boolean) =>
  `rounded-full border px-3 py-1 text-xs font-medium transition ${
    on
      ? "border-[var(--modal-primary)] bg-[var(--modal-primary)] text-white shadow-xs"
      : "border-border bg-card text-muted-foreground hover:border-[var(--modal-primary)]/60"
  }`;

export const modalPrimaryBtnCls =
  "flex h-11 w-full cursor-pointer items-center justify-center gap-2 rounded-2xl bg-[var(--modal-primary)] text-xs font-bold text-white shadow-sm transition-all duration-150 hover:brightness-110 active:scale-[0.98]";

export const modalCountBadgeCls =
  "flex h-5 min-w-5 items-center justify-center rounded-full bg-[var(--modal-soft)] px-2 text-[10px] font-bold text-[var(--modal-primary)]";

export const modalSoftCardCls =
  "flex items-center justify-between gap-3 rounded-2xl border border-[var(--modal-border)] bg-[var(--modal-soft)] p-3 transition-all hover:shadow-xs";
