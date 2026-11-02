import React, { Component, ErrorInfo, ReactNode } from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error in React ErrorBoundary:", error, errorInfo);
  }

  private handleReload = () => {
    window.location.reload();
  };

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen items-center justify-center bg-background p-6">
          <div className="w-full max-w-lg rounded-2xl border border-destructive/30 bg-card p-6 shadow-card-lg text-center">
            <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-destructive/10 text-destructive">
              <AlertTriangle className="h-7 w-7" />
            </div>
            <h2 className="text-xl font-bold tracking-tight text-foreground">
              Ocorreu uma falha temporária de exibição
            </h2>
            <p className="mt-2 text-sm text-muted-foreground">
              Um erro inesperado interrompeu a renderização do painel. Seus arquivos e dados em memória estão protegidos.
            </p>
            {this.state.error && (
              <pre className="mt-4 max-h-32 overflow-auto rounded-lg bg-muted p-3 text-left font-mono text-xs text-muted-foreground">
                {this.state.error.message}
              </pre>
            )}
            <div className="mt-6 flex items-center justify-center gap-3">
              <button
                type="button"
                onClick={this.handleReset}
                className="rounded-xl border border-border px-4 py-2 text-xs font-semibold text-foreground hover:bg-secondary/60 transition"
              >
                Tentar Novamente
              </button>
              <button
                type="button"
                onClick={this.handleReload}
                className="inline-flex items-center gap-2 rounded-xl bg-primary px-4 py-2 text-xs font-semibold text-primary-foreground shadow-sm hover:opacity-90 transition"
              >
                <RefreshCw className="h-3.5 w-3.5" />
                Recarregar Painel
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

