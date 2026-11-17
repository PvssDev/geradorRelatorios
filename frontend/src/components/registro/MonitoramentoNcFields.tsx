import React from "react";
import { TipoRelatorio } from "../../types/report.types";
import { DIRECOES_CRA, RegistroField, registroInputCls } from "./registroShared";

interface MonitoramentoNcFieldsProps {
  tipoRelatorio: TipoRelatorio;
  dense: boolean;
  hasOldPhotos: boolean;
  codificacao: string;
  pistaPersistida: string;
  trechoPersistido: string;
  direcaoFaixa: "Direita" | "Esquerda";
  legendaFotoMon: string;
  posConcessionariaMon: string;
  constatacaoMon: string;
  analiseArpeMon: string;
  onChangeCodificacao: (val: string) => void;
  onChangePista: (val: string) => void;
  onChangeTrecho: (val: string) => void;
  onChangeDirecao: (val: "Direita" | "Esquerda") => void;
  onChangeLegenda: (val: string) => void;
  onChangePosConcessionaria: (val: string) => void;
  onChangeConstatacao: (val: string) => void;
  onChangeAnaliseArpe: (val: string) => void;
}

export const MonitoramentoNcFields: React.FC<MonitoramentoNcFieldsProps> = ({
  tipoRelatorio,
  dense,
  hasOldPhotos,
  codificacao,
  pistaPersistida,
  trechoPersistido,
  direcaoFaixa,
  legendaFotoMon,
  posConcessionariaMon,
  constatacaoMon,
  analiseArpeMon,
  onChangeCodificacao,
  onChangePista,
  onChangeTrecho,
  onChangeDirecao,
  onChangeLegenda,
  onChangePosConcessionaria,
  onChangeConstatacao,
  onChangeAnaliseArpe,
}) => {
  return (
    <div
      className={
        dense
          ? "xl:min-h-full flex flex-col justify-between gap-4"
          : "space-y-8"
      }
    >
      {!hasOldPhotos && (
        <div
          className={`grid gap-6 ${
            tipoRelatorio === "CRA"
              ? "sm:grid-cols-4"
              : tipoRelatorio === "CRC"
              ? "sm:grid-cols-3"
              : "sm:grid-cols-1"
          }`}
        >
          <RegistroField label="Codificação / NC Anterior">
            <input
              className={`${registroInputCls} font-mono text-xs`}
              placeholder={
                tipoRelatorio === "SOCICAM"
                  ? "Ex: Vidraças quebradas na plataforma"
                  : `Ex: ${tipoRelatorio}.ST601.2794-2834/2025.001`
              }
              value={codificacao}
              onChange={(e) => onChangeCodificacao(e.target.value)}
            />
          </RegistroField>

          {tipoRelatorio !== "SOCICAM" && (
            <>
              <RegistroField label="Pista">
                <input
                  className={registroInputCls}
                  placeholder="Sul / Norte"
                  value={pistaPersistida}
                  onChange={(e) => onChangePista(e.target.value)}
                />
              </RegistroField>
              <RegistroField label="Trecho">
                <input
                  className={registroInputCls}
                  placeholder="KM / Estaca"
                  value={trechoPersistido}
                  onChange={(e) => onChangeTrecho(e.target.value)}
                />
              </RegistroField>
            </>
          )}

          {tipoRelatorio === "CRA" && (
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
          )}
        </div>
      )}

      <RegistroField label="Legenda da Foto Atual">
        <input
          className={registroInputCls}
          placeholder="Descrição exibida abaixo da foto atual no relatório..."
          value={legendaFotoMon}
          onChange={(e) => onChangeLegenda(e.target.value)}
        />
      </RegistroField>

      <div
        className={`grid grid-cols-1 ${
          dense ? "gap-4 xl:flex xl:flex-1 xl:flex-col" : "gap-6"
        }`}
      >
        <RegistroField
          label={
            tipoRelatorio === "SOCICAM"
              ? "Informação SOCICAM *"
              : `Posicionamento ${tipoRelatorio} *`
          }
          className={dense ? "xl:flex xl:flex-col xl:flex-1" : ""}
        >
          <textarea
            rows={3}
            className={`${registroInputCls} ${
              dense ? "xl:flex-1 xl:min-h-[68px]" : ""
            }`}
            placeholder="Manifestação informada pela concessionária"
            value={posConcessionariaMon}
            onChange={(e) => onChangePosConcessionaria(e.target.value)}
          />
        </RegistroField>
        <RegistroField
          label="Constatação em Campo *"
          className={dense ? "xl:flex xl:flex-col xl:flex-1" : ""}
        >
          <textarea
            rows={3}
            className={`${registroInputCls} ${
              dense ? "xl:flex-1 xl:min-h-[68px]" : ""
            }`}
            placeholder="Situação verificada pela equipe técnica da ARPE"
            value={constatacaoMon}
            onChange={(e) => onChangeConstatacao(e.target.value)}
          />
        </RegistroField>
        <RegistroField
          label="Análise ARPE *"
          className={dense ? "xl:flex xl:flex-col xl:flex-1" : ""}
        >
          <textarea
            rows={3}
            className={`${registroInputCls} ${
              dense ? "xl:flex-1 xl:min-h-[68px]" : ""
            }`}
            placeholder="Conclusão regulatória sobre o saneamento"
            value={analiseArpeMon}
            onChange={(e) => onChangeAnaliseArpe(e.target.value)}
          />
        </RegistroField>
      </div>
    </div>
  );
};

