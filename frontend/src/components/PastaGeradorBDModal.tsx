import React from "react";
import { Folder, FolderPlus, AlertCircle, CheckCircle2, X } from "lucide-react";

interface PastaGeradorBDModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectFolder: () => void;
  errorMessage?: string;
}

export const PastaGeradorBDModal: React.FC<PastaGeradorBDModalProps> = ({
  isOpen,
  onClose,
  onSelectFolder,
  errorMessage,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="relative w-full max-w-lg overflow-hidden rounded-3xl border border-white/20 bg-gradient-to-b from-navy to-[#0F1E38] p-6 text-white shadow-2xl">
        {/* Botão fechar */}
        <button
          type="button"
          onClick={onClose}
          aria-label="Fechar diálogo"
          className="absolute right-5 top-5 grid h-8 w-8 place-items-center rounded-full bg-white/10 text-white/70 hover:bg-white/20 hover:text-white transition"
        >
          <X className="h-4 w-4" />
        </button>

        {/* Cabeçalho */}
        <div className="flex items-start gap-4">
          <div className="grid h-12 w-12 shrink-0 place-items-center rounded-2xl bg-accent/20 border border-accent/40 text-accent shadow-inner">
            <FolderPlus className="h-6 w-6" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white tracking-tight">
              Pasta local <span className="text-accent font-mono">geradorBD</span> necessária
            </h3>
            <p className="mt-1 text-xs text-white/70 leading-relaxed">
              Para salvar e carregar dados e memoriais fotográficos diretamente no seu computador
              com segurança e conformidade LGPD, o sistema requer a pasta padrão.
            </p>
          </div>
        </div>

        {/* Mensagem de Erro/Aviso se houver */}
        {errorMessage && (
          <div className="mt-4 flex items-start gap-2.5 rounded-2xl border border-nc/30 bg-nc/10 p-3.5 text-xs text-nc-fg">
            <AlertCircle className="h-4 w-4 shrink-0 text-nc mt-0.5" />
            <div className="flex-1 text-[11px] leading-snug">{errorMessage}</div>
          </div>
        )}

        {/* Guia Passo a Passo */}
        <div className="mt-5 space-y-3 rounded-2xl border border-white/10 bg-white/5 p-4 text-xs">
          <div className="text-[11px] font-bold uppercase tracking-wider text-accent">
            Como configurar (em menos de 1 minuto):
          </div>

          <div className="flex items-start gap-3">
            <span className="grid h-5 w-5 shrink-0 place-items-center rounded-full bg-white/15 text-[11px] font-bold text-white">
              1
            </span>
            <span className="text-white/80 leading-snug">
              Abra o <strong>Explorador de Arquivos do Windows</strong> e escolha um local seguro (ex: <em>Documentos</em> ou <em>Área de Trabalho</em>).
            </span>
          </div>

          <div className="flex items-start gap-3">
            <span className="grid h-5 w-5 shrink-0 place-items-center rounded-full bg-white/15 text-[11px] font-bold text-white">
              2
            </span>
            <span className="text-white/80 leading-snug">
              Crie uma nova pasta com o nome exatamente:{" "}
              <code className="rounded bg-black/40 px-1.5 py-0.5 font-mono font-bold text-accent">
                geradorBD
              </code>
            </span>
          </div>

          <div className="flex items-start gap-3">
            <span className="grid h-5 w-5 shrink-0 place-items-center rounded-full bg-white/15 text-[11px] font-bold text-white">
              3
            </span>
            <span className="text-white/80 leading-snug">
              Clique no botão abaixo e selecione a pasta <strong>geradorBD</strong> criada.
            </span>
          </div>
        </div>

        {/* Nota de Soberania de Dados (LGPD) */}
        <div className="mt-4 flex items-center gap-2 text-[11px] text-white/50">
          <CheckCircle2 className="h-3.5 w-3.5 text-ok" />
          <span>Seus arquivos e fotos nunca saem do seu computador (armazenamento 100% local).</span>
        </div>

        {/* Botões de Ação */}
        <div className="mt-6 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <button
            type="button"
            onClick={onClose}
            className="rounded-xl border border-white/15 bg-white/10 px-4 py-2.5 text-xs font-semibold text-white hover:bg-white/15 transition"
          >
            Cancelar
          </button>
          <button
            type="button"
            onClick={() => {
              onClose();
              onSelectFolder();
            }}
            className="flex items-center justify-center gap-2 rounded-xl bg-accent px-5 py-2.5 text-xs font-bold text-white shadow-lg shadow-accent/25 hover:bg-accent/90 transition"
          >
            <Folder className="h-4 w-4" />
            Selecionar Pasta geradorBD
          </button>
        </div>
      </div>
    </div>
  );
};

