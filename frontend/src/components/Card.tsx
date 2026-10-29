import React, { ReactNode } from "react";

interface CardProps {
  n: number;
  icon: ReactNode;
  title: string;
  bodyClass?: string;
  children: ReactNode;
}

export const Card: React.FC<CardProps> = ({
  n,
  icon,
  title,
  bodyClass = "",
  children,
}) => {
  return (
    <section
      id={`b${n}`}
      className="overflow-hidden rounded-2xl border border-border bg-card shadow-card scroll-mt-28"
    >
      <h2 className="flex items-center gap-3 bg-navy-gradient px-6 py-4 text-base font-semibold text-primary-foreground">
        <span className="grid h-9 w-9 place-items-center rounded-xl bg-accent text-accent-foreground">
          {icon}
        </span>
        <span className="text-accent">0{n}</span> {title}
      </h2>
      <div className={`border-l-4 border-accent p-6 sm:p-8 ${bodyClass}`}>
        {children}
      </div>
    </section>
  );
};
