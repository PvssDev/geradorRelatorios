import React from "react";
import { Wand2 } from "lucide-react";
import { TipoRelatorio } from "../../types/report.types";
import {
  DIRECOES_CRA,
  PISTAS_SUGESTOES,
  RegistroField,
  registroInputCls,
  registroPillCls,
} from "./registroShared";

interface FiscalizacaoNcFieldsProps {
  tipoRelatorio: TipoRelatorio;
  dense: boolean;
  ano: string;
  seqStr: string;
  pistaPersistida: string;
  trechoPersistido: string;
  direcaoFaixa: "Direita" | "Esquerda";
  codificacao: string;
  siglas: string[];
  optionsNc: string[];
  mapSiglas: Record<string, string>;
  fund: string;
  det: string;
  contratoPadrao: string;
  themePrimary: string;
  onChangePista: (val: string) => void;
  onChangeTrecho: (val: string) => void;
  onChangeDirecao: (val: "Direita" | "Esquerda") => void;
  onChangeCodificacao: (val: string) => void;
  onSugerirCodificacao: () => void;
  onToggleSigla: (sigla: string) => void;
  onOpenCustomNcModal: () => void;
  onChangeFund: (val: string) => void;
  onChangeDet: (val: string) => void;
}

export const FiscalizacaoNcFields: React.FC<FiscalizacaoNcFieldsProps> = ({
  tipoRelatorio,
  dense,
  ano,
  seqStr,
  pistaPersistida,
  trechoPersistido,
  direcaoFaixa,
  codificacao,
  siglas,
  optionsNc,
  mapSiglas,
  fund,
  det,
  contratoPadrao,
  themePrimary,
  onChangePista,
  onChangeTrecho,
  onChangeDirecao,
  onChangeCodificacao,
  onSugerirCodificacao,
  onToggleSigla,
  onOpenCustomNcModal,
  onChangeFund,
  onChangeDet,
}) => {
  return (
    <div
      className={
        dense
          ? "xl:min-h-full flex flex-col justify-between gap-4"
          : "space-y-8"
      }
    >
      {tipoRelatorio === "CRA" && (
        <div
          className={`grid gap-6 sm:grid-cols-2 ${dense ? "" : "lg:grid-cols-4"}`}
        >
          <RegistroField label="Pista (persistente)">
            <input
              list="pistas-sugestoes"
              className={registroInputCls}
              placeholder="Ex: Sul ou Norte"
              value={pistaPersistida}
              onChange={(e) => onChangePista(e.target.value)}
            />
            <datalist id="pistas-sugestoes">
              {PISTAS_SUGESTOES.map((p) => (
                <option key={p} value={p} />
              ))}
            </datalist>
          </RegistroField>

          <RegistroField label="Trecho / Estaca (persistente)">
            <input
              className={registroInputCls}
              placeholder="Ex: PE-009 · KM 24+500"
              value={trechoPersistido}
              onChange={(e) => onChangeTrecho(e.target.value)}
            />
          </RegistroField>

          <RegistroField label="Direção / Faixa">
            <div className="grid h-[38px] grid-cols-2 gap-1.5 rounded-lg border border-input bg-secondary/60 p-1">
              {DIRECOES_CRA.map((dir) => (
                <button
                  key={dir}
                  type="button"
                  onClick={() => onChangeDirecao(dir)}
                  className={`rounded-md text-xs font-semibold transition ${
                    direcaoFaixa === dir
                      ? "bg-primary text-primary-foreground shadow-sm"
                      : "text-muted-foreground hover:text-foreground"
                  }`}
                >
                  {dir}
                </button>
              ))}
            </div>
          </RegistroField>

          <RegistroField
            label="Codificação"
            action={
              <button
                type="button"
                onClick={onSugerirCodificacao}
                className="inline-flex items-center gap-1 text-[11px] font-medium text-muted-foreground hover:text-accent transition"
                title="Gerar sugestão de código CRA"
              >
                <Wand2 className="h-3 w-3" /> Sugerir
              </button>
            }
          >
            <input
              className={`${registroInputCls} font-mono text-xs`}
              placeholder={`CRA.ST601.2794-2834/${ano}.${seqStr}`}
              value={codificacao}
              onChange={(e) => onChangeCodificacao(e.target.value)}
            />
          </RegistroField>
        </div>
      )}

      {tipoRelatorio === "CRC" && (
        <div className="grid gap-6 sm:grid-cols-3">
          <RegistroField
            label="Codificação"
            action={
              <button
                type="button"
                onClick={onSugerirCodificacao}
                className="inline-flex items-center gap-1 text-[11px] font-medium text-muted-foreground hover:text-accent transition"
                title="Gerar sugestão de código CRC"
              >
                <Wand2 className="h-3 w-3" /> Sugerir
              </button>
            }
          >
            <input
              className={`${registroInputCls} font-mono text-xs`}
              placeholder={`CRC.SH015.0646+0648/${ano}.${seqStr}`}
              value={codificacao}
              onChange={(e) => onChangeCodificacao(e.target.value)}
            />
          </RegistroField>

          <RegistroField label="Pista (persistente)">
            <input
              list="pistas-sugestoes-crc"
              className={registroInputCls}
              placeholder="Ex: Norte / Sul"
              value={pistaPersistida}
              onChange={(e) => onChangePista(e.target.value)}
            />
            <datalist id="pistas-sugestoes-crc">
              {PISTAS_SUGESTOES.map((p) => (
                <option key={p} value={p} />
              ))}
            </datalist>
          </RegistroField>

          <RegistroField label="Trecho / KM (persistente)">
            <input
              className={registroInputCls}
              placeholder="Ex: PE-024 · KM 04+200"
              value={trechoPersistido}
              onChange={(e) => onChangeTrecho(e.target.value)}
            />
          </RegistroField>
        </div>
      )}

      {/* Seleção de Siglas / Irregularidades */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold uppercase tracking-wide text-slate-blue">
            {tipoRelatorio === "SOCICAM"
              ? "Irregularidades do Terminal (SOCICAM)"
              : `Patologias / Irregularidades (siglas ${tipoRelatorio})`}
          </span>
          <button
            type="button"
            onClick={onOpenCustomNcModal}
            className="text-[11px] font-medium text-muted-foreground hover:text-accent transition"
          >
            + Personalizar siglas
          </button>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {optionsNc.map((s) => {
            const d = mapSiglas[s] || s;
            const isSelected = siglas.includes(s);
            return (
              <button
                type="button"
                key={s}
                title={d}
                className={registroPillCls(isSelected)}
                style={
                  isSelected
                    ? {
                        backgroundColor: themePrimary,
                        borderColor: themePrimary,
                      }
                    : undefined
                }
                onClick={() => onToggleSigla(s)}
              >
                {s}
              </button>
            );
          })}
        </div>

        {siglas.length > 0 && (
          <div className="mt-2.5 flex flex-wrap items-center gap-1.5 text-xs text-muted-foreground">
            <span className="font-semibold text-foreground">Selecionada(s):</span>
            {siglas.map((s) => (
              <span
                key={s}
                className="inline-flex items-center gap-1 rounded-md border border-border/80 bg-secondary/60 px-2 py-0.5 font-mono text-[11px] text-foreground"
                title={mapSiglas[s] || s}
              >
                <b style={{ color: themePrimary }}>{s}</b>
                {mapSiglas[s] && mapSiglas[s] !== s && (
                  <span className="font-sans text-muted-foreground">
                    · {mapSiglas[s]}
                  </span>
                )}
              </span>
            ))}
          </div>
        )}
      </div>

      {tipoRelatorio === "SOCICAM" && (
        <RegistroField
          label="Codificação / Identificação (opcional)"
          action={
            <button
              type="button"
              onClick={onSugerirCodificacao}
              className="inline-flex items-center gap-1 text-[11px] font-medium text-muted-foreground hover:text-accent transition"
            >
              <Wand2 className="h-3 w-3" /> Sugerir
            </button>
          }
        >
          <input
            className={`${registroInputCls} font-mono text-xs`}
            placeholder="Deixe em branco para usar a irregularidade selecionada"
            value={codificacao}
            onChange={(e) => onChangeCodificacao(e.target.value)}
          />
        </RegistroField>
      )}

      <div
        className={`grid sm:grid-cols-2 ${dense ? "gap-4 xl:flex-1" : "gap-6"}`}
      >
        <RegistroField
          label="Fundamento da Infração"
          className={dense ? "xl:flex xl:flex-col xl:h-full" : ""}
        >
          <textarea
            rows={2}
            className={`${registroInputCls} ${
              dense ? "xl:flex-1 xl:min-h-[76px]" : ""
            }`}
            placeholder={`Enquadramento contratual (${contratoPadrao})`}
            value={fund}
            onChange={(e) => onChangeFund(e.target.value)}
          />
        </RegistroField>
        <RegistroField
          label="Determinação / Prazo"
          className={dense ? "xl:flex xl:flex-col xl:h-full" : ""}
        >
          <textarea
            rows={2}
            className={`${registroInputCls} ${
              dense ? "xl:flex-1 xl:min-h-[76px]" : ""
            }`}
            placeholder="Determinação e prazo para saneamento"
            value={det}
            onChange={(e) => onChangeDet(e.target.value)}
          />
        </RegistroField>
      </div>
    </div>
  );
};

