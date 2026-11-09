import React, { useEffect, useState, useMemo, type ReactNode } from "react";
import {
  ImagePlus,
  AlertTriangle,
  Eye,
  Plus,
  Link2,
  Wand2,
  ChevronRight,
  ChevronDown,
  Table2,
  Sparkles,
} from "lucide-react";
import { RegistrosCadastradosPanel } from "./RegistrosCadastradosPanel";
import { toast } from "sonner";
import { Card } from "./Card";
import { PhotoCarouselPanel } from "./PhotoCarouselPanel";
import {
  useReportStore,
  calcularCodificacaoCra,
  obterProximoSequencialCra,
} from "../store/useReportStore";
import { SituacaoNC, RegistroNcItem } from "../types/report.types";
import { getConcessionTheme } from "../utils/concessionTheme";

interface RegistroNcFormProps {
  onOpenCustomNcModal: (onSelectSigla: (siglaOrDesc: string) => void) => void;
  onOpenRelacionarModal: (currentPhotoName?: string) => void;
  onOpenGalleryModal: () => void;
  onOpenEditModal?: (tab?: "fisc" | "nc") => void;
}

const DIRECOES_CRA = ["Direita", "Esquerda"] as const;
const PISTAS_SUGESTOES = [
  "Sul",
  "Norte",
  "Sentido Sul (Crescente)",
  "Sentido Norte (Decrescente)",
  "Ambos os sentidos",
];

const inputCls =
  "w-full rounded-lg border border-input bg-secondary/60 px-3 py-2 text-sm text-foreground outline-none focus:border-ring focus:ring-2 focus:ring-ring/20";

const btn = {
  primary:
    "inline-flex items-center justify-center gap-2 rounded-xl bg-amber-500 px-5 py-2.5 text-sm font-bold text-stone-950 shadow-[0_3px_0_0_#b45309] transition-all duration-150 hover:bg-amber-400 active:translate-y-[2px] active:shadow-[0_1px_0_0_#b45309] disabled:opacity-40 disabled:pointer-events-none",
  secondary:
    "inline-flex items-center justify-center gap-2 rounded-xl border border-border bg-card px-4 py-2.5 text-sm font-semibold text-foreground hover:border-accent hover:text-accent transition-all duration-200 active:translate-y-[1px] disabled:opacity-40 disabled:pointer-events-none",
};

const pill = (on: boolean) =>
  `rounded-lg border px-2.5 py-1 text-xs font-semibold transition-all duration-150 ${
    on
      ? "text-white shadow-xs"
      : "border-border/80 bg-card text-foreground hover:border-slate-400 hover:bg-secondary/40 shadow-2xs"
  }`;

function Field({
  label,
  action,
  children,
}: {
  label: string;
  action?: ReactNode;
  children: ReactNode;
}) {
  return (
    <div className="block space-y-1.5">
      <div className="flex items-center justify-between gap-2">
        <span className="text-xs font-semibold uppercase tracking-wide text-slate-blue">
          {label}
        </span>
        {action}
      </div>
      {children}
    </div>
  );
}

export const RegistroNcForm: React.FC<RegistroNcFormProps> = ({
  onOpenCustomNcModal,
  onOpenRelacionarModal,
  onOpenGalleryModal,
  onOpenEditModal,
}) => {
  const [isRegistrosExpanded, setIsRegistrosExpanded] = useState(false);
  const {
    tipoRelatorio,
    categoriaRelatorio,
    mapSiglas,
    contratosPadrao,
    locaisSocicam,
    responsaveis,
    coordenadores,
    getActiveWorkspace,
    getNcOptionsForCurrent,
    setActiveFiscalizacaoIndex,
    setPistaPersistida,
    setTrechoPersistido,
    addOrUpdateRegistroNc,
    upsertActiveFiscalizacao,
  } = useReportStore();

  const ws = getActiveWorkspace();
  const isMonitoring = categoriaRelatorio === "Monitoramento";
  const optionsNc = getNcOptionsForCurrent();
  const theme = getConcessionTheme(tipoRelatorio, categoriaRelatorio);

  // Tipo NC vs PA (Ponto de Atenção é exclusivo de CRA Fiscalização)
  const [tipo, setTipo] = useState<"NC" | "PA">("NC");
  const [direcaoFaixa, setDirecaoFaixa] = useState<"Direita" | "Esquerda">(
    "Direita"
  );
  const [codificacao, setCodificacao] = useState("");
  const [siglas, setSiglas] = useState<string[]>([]);
  const [fund, setFund] = useState("");
  const [det, setDet] = useState("");

  // Campos de Monitoramento
  const [situacaoMon, setSituacaoMon] = useState<SituacaoNC>("Pendente");
  const [legendaFotoMon, setLegendaFotoMon] = useState("");
  const [posConcessionariaMon, setPosConcessionariaMon] = useState("");
  const [constatacaoMon, setConstatacaoMon] = useState("");
  const [analiseArpeMon, setAnaliseArpeMon] = useState("");
  const [selectedNewPhotoMon, setSelectedNewPhotoMon] = useState("");

  // Reseta tipo para NC caso mude para CRC ou SOCICAM (que só possuem NC)
  useEffect(() => {
    if (tipoRelatorio !== "CRA" || isMonitoring) {
      setTipo("NC");
    }
    setSiglas([]);
    setCodificacao("");
  }, [tipoRelatorio, categoriaRelatorio, isMonitoring]);

  const currentOldItem =
    isMonitoring && ws.oldPhotosToMatch.length > 0
      ? ws.oldPhotosToMatch[
          Math.max(
            0,
            Math.min(ws.carouselIndex, ws.oldPhotosToMatch.length - 1)
          )
        ]
      : null;

  useEffect(() => {
    if (isMonitoring && currentOldItem) {
      const saved = ws.registrosNc.find(
        (r) => !r.is_relacionado && r.Identificação === currentOldItem.id_nc
      );
      setPosConcessionariaMon(saved?.Determinação || "");
      setConstatacaoMon(
        saved?.Observações || currentOldItem.constatacao || ""
      );
      setAnaliseArpeMon(saved?.["Análise ARPE"] || "");
      setLegendaFotoMon(saved?.["Legenda da Foto"] || "");
      setSituacaoMon(saved?.Situação || "Pendente");
      const defaultPhoto =
        ws.photos[
          Math.min(ws.carouselIndex, Math.max(0, ws.photos.length - 1))
        ]?.name || "";
      setSelectedNewPhotoMon(saved?.Foto || defaultPhoto);
    } else if (isMonitoring) {
      const defaultPhoto =
        ws.photos[
          Math.min(ws.carouselIndex, Math.max(0, ws.photos.length - 1))
        ]?.name || "";
      setSelectedNewPhotoMon(defaultPhoto);
    }
  }, [
    isMonitoring,
    currentOldItem,
    ws.carouselIndex,
    ws.photos,
    ws.registrosNc,
  ]);

  const fotos = ws.photos;
  const fotoIdx = Math.max(
    0,
    Math.min(ws.carouselIndex, Math.max(0, fotos.length - 1))
  );
  const activePhoto = fotos[fotoIdx] || null;

  const activeFiscIdx = Math.max(
    0,
    Math.min(
      ws.activeFiscalizacaoIndex,
      Math.max(0, ws.fiscalizacoes.length - 1)
    )
  );
  const activeFisc = ws.fiscalizacoes[activeFiscIdx];
  const dataBr =
    activeFisc?.Data || new Date().toLocaleDateString("pt-BR");
  const ano = dataBr.split("/")[2] || String(new Date().getFullYear());

  // Sequencial baseado no maior sufixo numérico da fiscalização atual
  const maxSeqInFiscalizacao = useMemo(() => {
    let max = 0;
    const currentId = activeFisc?.["ID da Fiscalização"]?.trim() || "";
    for (const r of ws.registrosNc) {
      if (!currentId || r["ID da Fiscalização"] === currentId) {
        const cod = (r.Codificação || r.Identificação || "").trim();
        const m = cod.match(/[\/.](\d{4})\.(\d+)$/) || cod.match(/[\/.](\d+)$/);
        if (m) {
          const num = parseInt(m[2] || m[1], 10);
          if (!isNaN(num) && num > max) max = num;
        }
      }
    }
    return max > 0 ? max + 1 : ws.registrosNc.length + 1;
  }, [ws.registrosNc, activeFisc]);

  const seqStr = String(maxSeqInFiscalizacao).padStart(3, "0");

  const sugerirCodificacao = () => {
    if (tipoRelatorio === "CRA") {
      setCodificacao(`CRA.ST601.2794-2834/${ano}.${seqStr}`);
    } else if (tipoRelatorio === "CRC") {
      setCodificacao(`CRC.SH015.0646+0648/${ano}.${seqStr}`);
    } else {
      setCodificacao(`SOCICAM/${ano}.${seqStr}`);
    }
  };

  const legendaPreviewMon = `Foto 02 – ${
    legendaFotoMon.trim() ||
    constatacaoMon.trim() ||
    "registro atual verificado em campo"
  }, em ${dataBr}.`;

  const ensureFiscalizacaoHeader = (): { id: string; local: string } => {
    const existing = ws.fiscalizacoes[activeFiscIdx];
    if (existing && existing["ID da Fiscalização"]?.trim()) {
      return {
        id: existing["ID da Fiscalização"].trim(),
        local: existing.Local,
      };
    }
    const defaultLocal =
      tipoRelatorio === "CRA"
        ? "Rota do Atlântico"
        : tipoRelatorio === "CRC"
        ? "Sistema Viário do Paiva"
        : locaisSocicam[5] || "TIP Recife";
    const generatedId = `${
      isMonitoring ? "MON" : "FISC"
    }-${tipoRelatorio}-${ano}-001`;

    upsertActiveFiscalizacao({
      "ID da Fiscalização": generatedId,
      Data: dataBr,
      Hora: tipoRelatorio === "CRA" ? "09:30" : "",
      Cidade:
        tipoRelatorio === "CRA"
          ? "Cabo de Santo Agostinho / Ipojuca"
          : tipoRelatorio === "SOCICAM"
          ? defaultLocal
          : "",
      Local: defaultLocal,
      "Pessoal Responsável":
        responsaveis.map((r) => r.nome).join(", ") || "Equipe Técnica ARPE",
      Coordenador: coordenadores[0]?.nome || "",
      Contrato: contratosPadrao[tipoRelatorio] || "CT. nº 043/2011",
      Período: dataBr,
      "Relatório Gerado": false,
    });
    return { id: generatedId, local: defaultLocal };
  };

  const addReg = () => {
    const targetPhotoName = isMonitoring
      ? selectedNewPhotoMon || activePhoto?.name || ""
      : activePhoto?.name || "";

    if (!targetPhotoName) {
      toast.error("Envie e selecione ao menos uma foto no bloco 01.");
      return;
    }

    if (isMonitoring) {
      if (
        !posConcessionariaMon.trim() ||
        !constatacaoMon.trim() ||
        !analiseArpeMon.trim()
      ) {
        toast.error(
          `Preencha ${
            tipoRelatorio === "SOCICAM"
              ? "Informação SOCICAM"
              : `Posicionamento ${tipoRelatorio}`
          }, Constatação e Análise ARPE.`
        );
        return;
      }

      const { id: idVinculo, local: localVinculo } =
        ensureFiscalizacaoHeader();

      const identMon =
        currentOldItem?.id_nc ||
        codificacao.trim() ||
        siglas.join(", ") ||
        `NC ${seqStr}`;

      addOrUpdateRegistroNc({
        "ID da Fiscalização": idVinculo,
        "Nº": ws.registrosNc.length + 1,
        Terminal: localVinculo,
        Pista:
          tipoRelatorio === "SOCICAM"
            ? ""
            : currentOldItem?.pista || ws.pistaPersistida.trim(),
        Trecho:
          tipoRelatorio === "SOCICAM"
            ? ""
            : currentOldItem?.trecho || ws.trechoPersistido.trim(),
        "Não Conformidade":
          currentOldItem?.constatacao ||
          currentOldItem?.id_nc ||
          siglas.join(", ") ||
          identMon,
        "Ponto de Atenção": "",
        Foto: targetPhotoName,
        "Foto Anterior": currentOldItem?.old_photo_path || "",
        "Legenda Anterior": currentOldItem?.old_legend || "",
        "Legenda da Foto": legendaFotoMon.trim() || constatacaoMon.trim(),
        Observações: constatacaoMon.trim(),
        Identificação: identMon,
        "Direção (faixa)": tipoRelatorio === "CRA" ? direcaoFaixa : "",
        "Fundamento da infração": fund.trim(),
        Determinação: posConcessionariaMon.trim(),
        Situação: situacaoMon,
        "Análise ARPE": analiseArpeMon.trim(),
        grupo_relacao: `${idVinculo}_${identMon}`,
        is_relacionado: false,
      });

      toast.success(`Auditoria '${identMon}' salva no relatório!`);
      if (!currentOldItem) {
        setCodificacao("");
        setLegendaFotoMon("");
        setPosConcessionariaMon("");
        setConstatacaoMon("");
        setAnaliseArpeMon("");
      }
      return;
    }

    // Validação Fiscalização
    if (siglas.length === 0 && !codificacao.trim()) {
      toast.error(
        "Selecione ao menos uma sigla/irregularidade ou preencha a codificação."
      );
      return;
    }

    const { id: idVinculo, local: localVinculo } = ensureFiscalizacaoHeader();
    const isPa = tipoRelatorio === "CRA" && tipo === "PA";

    if (tipoRelatorio === "CRA" || tipoRelatorio === "SOCICAM") {
      const tipoRegistroStr = isPa ? "Ponto de Atenção" : "Não Conformidade";
      const fotoNum = fotoIdx + 1;
      const grpId = `grp_${idVinculo}_${fotoNum}_${Date.now()}`;
      const defaultBase = tipoRelatorio === "SOCICAM" ? "SOCICAM" : "CRA.ST601.2794-2834";
      const baseRaw = codificacao.trim() || defaultBase;
      const baseLimpa = baseRaw.split("/")[0].trim() || baseRaw;

      const siglasParaCadastrar = siglas.length > 0 ? siglas : [baseRaw];
      const tempNcClone = [...ws.registrosNc];

      siglasParaCadastrar.forEach((s, idx) => {
        const seqIdx = obterProximoSequencialCra(tempNcClone, idVinculo, tipoRegistroStr);
        const codFormatado = calcularCodificacaoCra(baseLimpa, dataBr, seqIdx);
        const descSigla = s;
        const obsSigla = (mapSiglas[s] || s).toLowerCase();
        const isUltima = idx === siglasParaCadastrar.length - 1;

        const novoRec: RegistroNcItem = {
          "ID da Fiscalização": idVinculo,
          "Nº": fotoNum,
          Terminal: localVinculo,
          Pista: tipoRelatorio === "CRA" ? ws.pistaPersistida.trim() : "",
          Trecho: tipoRelatorio === "CRA" ? codFormatado : "",
          "Não Conformidade": isPa ? "" : descSigla,
          "Ponto de Atenção": isPa ? descSigla : "",
          Foto: targetPhotoName,
          "Foto Anterior": "",
          "Legenda Anterior": "",
          Observações: obsSigla,
          Identificação: codFormatado,
          Codificação: codFormatado,
          "Direção (faixa)": tipoRelatorio === "CRA" ? direcaoFaixa : "",
          "Fundamento da infração": fund.trim(),
          Determinação: det.trim(),
          Situação: "Pendente",
          "Análise ARPE": "",
          grupo_relacao: grpId,
          is_relacionado: false,
        };

        tempNcClone.push(novoRec);
        addOrUpdateRegistroNc(novoRec, isUltima);
      });

      toast.success(
        `${isPa ? "Ponto de Atenção" : "Não Conformidade"} (${siglasParaCadastrar.length > 1 ? `${siglasParaCadastrar.length} itens` : baseLimpa}) adicionado(a)!`
      );
      setSiglas([]);
      setCodificacao("");
      setFund("");
      setDet("");
      return;
    }

    let codPadrao = "";
    if (tipoRelatorio === "CRC") {
      codPadrao = `CRC.SH015.0646+0648/${ano}.${seqStr}`;
    } else {
      codPadrao = `SOCICAM.${ano}.${seqStr}`;
    }

    const identFinal = codificacao.trim() || codPadrao;
    const descStr = siglas.join(", ") || identFinal;

    const obsFinal = siglas.length
      ? siglas.map((s) => (mapSiglas[s] || s).toLowerCase()).join(", ")
      : descStr;
    const nextNum = ws.registrosNc.length + 1;

    addOrUpdateRegistroNc({
      "ID da Fiscalização": idVinculo,
      "Nº": nextNum,
      Terminal: localVinculo,
      Pista: tipoRelatorio !== "SOCICAM" ? ws.pistaPersistida.trim() : "",
      Trecho: tipoRelatorio !== "SOCICAM" ? ws.trechoPersistido.trim() : "",
      "Não Conformidade": isPa ? "" : descStr,
      "Ponto de Atenção": isPa ? descStr : "",
      Foto: targetPhotoName,
      "Foto Anterior": "",
      "Legenda Anterior": "",
      Observações: obsFinal,
      Identificação: identFinal,
      Codificação: identFinal,
      "Direção (faixa)": "",
      "Fundamento da infração": fund.trim(),
      Determinação: det.trim(),
      Situação: "Pendente",
      "Análise ARPE": "",
      grupo_relacao: `${idVinculo}_${nextNum}`,
      is_relacionado: false,
    });

    toast.success(
      `Não Conformidade (${identFinal}) adicionada!`
    );
    setSiglas([]);
    setCodificacao("");
    setFund("");
    setDet("");
  };

  const temOcorrenciaBase = ws.registrosNc.some((r) => !r.is_relacionado);
  const podeRelacionar = Boolean(temOcorrenciaBase && fotos.length > 0);

  return (
    <Card
      n={3}
      icon={<ImagePlus className="h-5 w-5" />}
      title={
        isMonitoring
          ? "Auditoria de Não Conformidade (Monitoramento)"
          : tipoRelatorio === "CRA"
          ? "Registro de Não Conformidade ou Ponto de Atenção"
          : "Registro de Não Conformidade (NC)"
      }
    >
      {/* Topo do Card 03: Seletor de Tipo/Situação + Seletor de ID vinculado */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        {!isMonitoring ? (
          tipoRelatorio === "CRA" ? (
            <div className="inline-flex rounded-2xl border border-border bg-secondary/70 p-1.5 shadow-inner">
              {(["NC", "PA"] as const).map((t) => {
                const isSelected = tipo === t;
                return (
                  <button
                    key={t}
                    type="button"
                    onClick={() => setTipo(t)}
                    className={`flex items-center gap-2.5 rounded-xl px-4 py-2 text-xs font-bold transition-all duration-200 ${
                      isSelected
                        ? t === "NC"
                          ? "bg-nc-soft text-nc border border-nc/40 shadow-sm"
                          : "bg-amber-100 text-amber-800 border border-amber-400 shadow-sm"
                        : "text-muted-foreground hover:bg-card hover:text-foreground"
                    }`}
                  >
                    {t === "NC" ? (
                      <AlertTriangle className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                    {t === "NC"
                      ? "Não Conformidade (NC)"
                      : "Ponto de Atenção (PA)"}
                  </button>
                );
              })}
            </div>
          ) : (
            <div className="inline-flex items-center gap-2 rounded-xl border border-nc/30 bg-nc-soft px-4 py-2 text-xs font-bold text-nc">
              <AlertTriangle className="h-4 w-4" />
              Não Conformidade (NC) · {tipoRelatorio}
            </div>
          )
        ) : (
          <div className="inline-flex flex-wrap gap-1.5 rounded-2xl border border-border bg-secondary/70 p-1.5 shadow-inner">
            {(
              ["Pendente", "Parcialmente Sanada", "Sanada"] as SituacaoNC[]
            ).map((sit) => {
              const isSelected = situacaoMon === sit;
              return (
                <button
                  key={sit}
                  type="button"
                  onClick={() => setSituacaoMon(sit)}
                  className={`rounded-xl px-4 py-2 text-xs font-bold transition-all duration-200 ${
                    isSelected
                      ? sit === "Sanada"
                        ? "bg-ok-soft text-ok border border-ok/40 shadow-sm"
                        : sit === "Parcialmente Sanada"
                        ? "bg-amber-100 text-amber-800 border border-amber-400 shadow-sm"
                        : "bg-nc-soft text-nc border border-nc/40 shadow-sm"
                      : "text-muted-foreground hover:bg-card hover:text-foreground"
                  }`}
                >
                  {sit}
                </button>
              );
            })}
          </div>
        )}

        {ws.fiscalizacoes.length > 1 ? (
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wide text-slate-blue">
              Vincular ao ID:
            </span>
            <select
              value={activeFiscIdx}
              onChange={(e) =>
                setActiveFiscalizacaoIndex(Number(e.target.value))
              }
              className="rounded-lg border border-input bg-secondary/60 px-3 py-1.5 text-xs font-semibold text-foreground outline-none focus:border-ring"
            >
              {ws.fiscalizacoes.map((f, idx) => (
                <option key={`${f["ID da Fiscalização"]}_${idx}`} value={idx}>
                  {f["ID da Fiscalização"] || `#${idx + 1}`} — {f.Local}
                </option>
              ))}
            </select>
          </div>
        ) : activeFisc?.["ID da Fiscalização"] ? (
          <span className="rounded-full border border-border bg-secondary/60 px-3 py-1 text-xs font-medium text-muted-foreground">
            Vinculado a:{" "}
            <b className="text-foreground">
              {activeFisc["ID da Fiscalização"]}
            </b>
          </span>
        ) : null}
      </div>

      {/* Carrossel / Comparador Fotográfico */}
      <div className="mt-8 space-y-8">
        <PhotoCarouselPanel
          selectedNewPhotoName={selectedNewPhotoMon}
          onSelectNewPhotoName={setSelectedNewPhotoMon}
          onOpenGalleryModal={onOpenGalleryModal}
        />

        {/* MODO FISCALIZAÇÃO */}
        {!isMonitoring ? (
          <div className="space-y-8">
            {/* Localização Rodoviária e Codificação por Concessão */}
            {tipoRelatorio === "CRA" && (
              <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
                <Field label="Pista (persistente)">
                  <input
                    list="pistas-sugestoes"
                    className={inputCls}
                    placeholder="Ex: Sul ou Norte"
                    value={ws.pistaPersistida}
                    onChange={(e) => setPistaPersistida(e.target.value)}
                  />
                  <datalist id="pistas-sugestoes">
                    {PISTAS_SUGESTOES.map((p) => (
                      <option key={p} value={p} />
                    ))}
                  </datalist>
                </Field>

                <Field label="Trecho / Estaca (persistente)">
                  <input
                    className={inputCls}
                    placeholder="Ex: PE-009 · KM 24+500"
                    value={ws.trechoPersistido}
                    onChange={(e) => setTrechoPersistido(e.target.value)}
                  />
                </Field>

                <Field label="Direção / Faixa">
                  <div className="grid h-[38px] grid-cols-2 gap-1.5 rounded-lg border border-input bg-secondary/60 p-1">
                    {DIRECOES_CRA.map((dir) => (
                      <button
                        key={dir}
                        type="button"
                        onClick={() => setDirecaoFaixa(dir)}
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
                </Field>

                <Field
                  label="Codificação"
                  action={
                    <button
                      type="button"
                      onClick={sugerirCodificacao}
                      className="inline-flex items-center gap-1 text-[11px] font-medium text-muted-foreground hover:text-accent transition"
                      title="Gerar sugestão de código CRA"
                    >
                      <Wand2 className="h-3 w-3" /> Sugerir
                    </button>
                  }
                >
                  <input
                    className={`${inputCls} font-mono text-xs`}
                    placeholder={`CRA.ST601.2794-2834/${ano}.${seqStr}`}
                    value={codificacao}
                    onChange={(e) => setCodificacao(e.target.value)}
                  />
                </Field>
              </div>
            )}

            {tipoRelatorio === "CRC" && (
              <div className="grid gap-6 sm:grid-cols-3">
                <Field
                  label="Codificação"
                  action={
                    <button
                      type="button"
                      onClick={sugerirCodificacao}
                      className="inline-flex items-center gap-1 text-[11px] font-medium text-muted-foreground hover:text-accent transition"
                      title="Gerar sugestão de código CRC"
                    >
                      <Wand2 className="h-3 w-3" /> Sugerir
                    </button>
                  }
                >
                  <input
                    className={`${inputCls} font-mono text-xs`}
                    placeholder={`CRC.SH015.0646+0648/${ano}.${seqStr}`}
                    value={codificacao}
                    onChange={(e) => setCodificacao(e.target.value)}
                  />
                </Field>

                <Field label="Pista (persistente)">
                  <input
                    list="pistas-sugestoes-crc"
                    className={inputCls}
                    placeholder="Ex: Norte / Sul"
                    value={ws.pistaPersistida}
                    onChange={(e) => setPistaPersistida(e.target.value)}
                  />
                  <datalist id="pistas-sugestoes-crc">
                    {PISTAS_SUGESTOES.map((p) => (
                      <option key={p} value={p} />
                    ))}
                  </datalist>
                </Field>

                <Field label="Trecho / KM (persistente)">
                  <input
                    className={inputCls}
                    placeholder="Ex: PE-024 · KM 04+200"
                    value={ws.trechoPersistido}
                    onChange={(e) => setTrechoPersistido(e.target.value)}
                  />
                </Field>
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
                  onClick={() =>
                    onOpenCustomNcModal((novaSigla) =>
                      setSiglas((prev) =>
                        prev.includes(novaSigla) ? prev : [...prev, novaSigla]
                      )
                    )
                  }
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
                      className={pill(isSelected)}
                      style={
                        isSelected
                          ? {
                              backgroundColor: theme.primary,
                              borderColor: theme.primary,
                            }
                          : undefined
                      }
                      onClick={() =>
                        setSiglas((x) =>
                          x.includes(s)
                            ? x.filter((y) => y !== s)
                            : [...x, s]
                        )
                      }
                    >
                      {s}
                    </button>
                  );
                })}
              </div>

              {siglas.length > 0 && (
                <div className="mt-2.5 flex flex-wrap items-center gap-1.5 text-xs text-muted-foreground">
                  <span className="font-semibold text-foreground">
                    Selecionada(s):
                  </span>
                  {siglas.map((s) => (
                    <span
                      key={s}
                      className="inline-flex items-center gap-1 rounded-md border border-border/80 bg-secondary/60 px-2 py-0.5 font-mono text-[11px] text-foreground"
                      title={mapSiglas[s] || s}
                    >
                      <b style={{ color: theme.primary }}>{s}</b>
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
              <Field
                label="Codificação / Identificação (opcional)"
                action={
                  <button
                    type="button"
                    onClick={sugerirCodificacao}
                    className="inline-flex items-center gap-1 text-[11px] font-medium text-muted-foreground hover:text-accent transition"
                  >
                    <Wand2 className="h-3 w-3" /> Sugerir
                  </button>
                }
              >
                <input
                  className={`${inputCls} font-mono text-xs`}
                  placeholder="Deixe em branco para usar a irregularidade selecionada"
                  value={codificacao}
                  onChange={(e) => setCodificacao(e.target.value)}
                />
              </Field>
            )}


            <div className="grid gap-6 sm:grid-cols-2">
              <Field label="Fundamento da Infração">
                <textarea
                  rows={2}
                  className={inputCls}
                  placeholder={`Enquadramento contratual (${contratosPadrao[tipoRelatorio]})`}
                  value={fund}
                  onChange={(e) => setFund(e.target.value)}
                />
              </Field>
              <Field label="Determinação / Prazo">
                <textarea
                  rows={2}
                  className={inputCls}
                  placeholder="Determinação e prazo para saneamento"
                  value={det}
                  onChange={(e) => setDet(e.target.value)}
                />
              </Field>
            </div>
          </div>
        ) : (
          /* MODO MONITORAMENTO */
          <div className="space-y-8">
            {/* Caso não haja documento anterior carregado, permite informar identificação manual */}
            {ws.oldPhotosToMatch.length === 0 && (
              <div
                className={`grid gap-6 ${
                  tipoRelatorio === "CRA"
                    ? "sm:grid-cols-4"
                    : tipoRelatorio === "CRC"
                    ? "sm:grid-cols-3"
                    : "sm:grid-cols-1"
                }`}
              >
                <Field label="Codificação / NC Anterior">
                  <input
                    className={`${inputCls} font-mono text-xs`}
                    placeholder={
                      tipoRelatorio === "SOCICAM"
                        ? "Ex: Vidraças quebradas na plataforma"
                        : `Ex: ${tipoRelatorio}.ST601.2794-2834/2025.001`
                    }
                    value={codificacao}
                    onChange={(e) => setCodificacao(e.target.value)}
                  />
                </Field>

                {tipoRelatorio !== "SOCICAM" && (
                  <>
                    <Field label="Pista">
                      <input
                        className={inputCls}
                        placeholder="Sul / Norte"
                        value={ws.pistaPersistida}
                        onChange={(e) => setPistaPersistida(e.target.value)}
                      />
                    </Field>
                    <Field label="Trecho">
                      <input
                        className={inputCls}
                        placeholder="KM / Estaca"
                        value={ws.trechoPersistido}
                        onChange={(e) => setTrechoPersistido(e.target.value)}
                      />
                    </Field>
                  </>
                )}

                {tipoRelatorio === "CRA" && (
                  <Field label="Direção / Faixa">
                    <div className="grid h-[38px] grid-cols-2 gap-1.5 rounded-lg border border-input bg-secondary/60 p-1">
                      {DIRECOES_CRA.map((dir) => (
                        <button
                          key={dir}
                          type="button"
                          onClick={() => setDirecaoFaixa(dir)}
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
                  </Field>
                )}
              </div>
            )}

            <div className="grid gap-6 sm:grid-cols-2">
              <Field label="Legenda da Foto Atual">
                <input
                  className={inputCls}
                  placeholder="Descrição exibida abaixo da foto atual no relatório..."
                  value={legendaFotoMon}
                  onChange={(e) => setLegendaFotoMon(e.target.value)}
                />
              </Field>
              <Field label="Prévia da Legenda Atual (.docx)">
                <div className="flex min-h-[38px] items-center rounded-lg border border-input bg-muted px-3 py-2 text-xs italic text-muted-foreground">
                  {legendaPreviewMon}
                </div>
              </Field>
            </div>

            <div className="grid gap-6 sm:grid-cols-3">
              <Field
                label={
                  tipoRelatorio === "SOCICAM"
                    ? "Informação SOCICAM *"
                    : `Posicionamento ${tipoRelatorio} *`
                }
              >
                <textarea
                  rows={3}
                  className={inputCls}
                  placeholder="Manifestação informada pela concessionária"
                  value={posConcessionariaMon}
                  onChange={(e) => setPosConcessionariaMon(e.target.value)}
                />
              </Field>
              <Field label="Constatação em Campo *">
                <textarea
                  rows={3}
                  className={inputCls}
                  placeholder="Situação verificada pela equipe técnica da ARPE"
                  value={constatacaoMon}
                  onChange={(e) => setConstatacaoMon(e.target.value)}
                />
              </Field>
              <Field label="Análise ARPE *">
                <textarea
                  rows={3}
                  className={inputCls}
                  placeholder="Conclusão regulatória sobre o saneamento"
                  value={analiseArpeMon}
                  onChange={(e) => setAnaliseArpeMon(e.target.value)}
                />
              </Field>
            </div>
          </div>
        )}
      </div>

      {/* Botões de Ação: Adicionar + Janela de Relacionar Foto */}
      <div className="mt-8 flex flex-wrap gap-3">
        <button
          type="button"
          className="group relative inline-flex items-center justify-between gap-3 overflow-hidden rounded-2xl bg-gradient-to-r from-amber-500 via-amber-600 to-amber-700 px-6 py-3.5 text-sm font-bold text-white shadow-lg shadow-amber-500/25 transition-all duration-200 hover:brightness-105 hover:shadow-xl hover:shadow-amber-500/35 active:translate-y-[2px] active:scale-[0.99] disabled:opacity-40 disabled:pointer-events-none flex-1"
          disabled={!activePhoto}
          onClick={addReg}
        >
          <div className="flex items-center gap-2.5">
            <Plus className="h-4 w-4 stroke-[2.5]" />
            <span>
              {isMonitoring
                ? "Salvar Auditoria no Relatório"
                : "Adicionar Registro ao Relatório"}
            </span>
          </div>
          <span className="flex h-7 w-7 items-center justify-center rounded-full bg-black/20 text-white backdrop-blur-sm transition-transform duration-200 group-hover:scale-110">
            <ChevronRight className="h-4 w-4 stroke-[2.5]" />
          </span>
        </button>

        <button
          type="button"
          className={`${btn.secondary} py-3.5 px-5`}
          disabled={!podeRelacionar}
          title={
            podeRelacionar
              ? "Abrir janela para vincular uma 2ª foto a uma ocorrência já registrada (máx. 2 fotos por NC)"
              : "Cadastre ao menos uma ocorrência e envie fotos para habilitar o relacionamento"
          }
          onClick={() =>
            onOpenRelacionarModal(
              (isMonitoring ? selectedNewPhotoMon : activePhoto?.name) ||
                activePhoto?.name
            )
          }
        >
          <Link2 className="h-4 w-4" /> Relacionar Foto...
        </button>
      </div>

      {!activePhoto && (
        <p className="mt-2 text-center text-xs text-muted-foreground">
          Envie ao menos uma foto no bloco 01 para habilitar o registro.
        </p>
      )}

      {ws.registrosNc.length === 0 && (
        <div className="mt-3 flex items-center justify-center gap-2 rounded-xl border border-dashed border-amber-300/80 bg-amber-50/50 p-3 text-xs text-amber-900">
          <Sparkles className="h-3.5 w-3.5 text-amber-600 shrink-0" />
          <span>Cadastre a primeira ocorrência para desbloquear o painel de emissão e exportação.</span>
        </div>
      )}

      {/* Trigger do Sumário Retrátil que Abre para Baixo (Accordion) */}
      {(() => {
        const baseRegs = ws.registrosNc.filter((r) => !r.is_relacionado);
        const sanadasCount = baseRegs.filter((r) => r.Situação === "Sanada").length;
        const pendentesCount = baseRegs.filter((r) => !r.Situação || r.Situação === "Pendente").length;

        return (
          <div className="mt-5 border-t border-slate-200/90 pt-4">
            <div className={`transition-all duration-200 ${isRegistrosExpanded ? "shadow-lg shadow-indigo-950/5" : ""}`}>
              <button
                type="button"
                onClick={() => setIsRegistrosExpanded((prev) => !prev)}
                className={`group relative flex w-full items-center justify-between gap-4 p-4 text-left transition-all duration-200 active:translate-y-[1px] ${
                  isRegistrosExpanded
                    ? "rounded-t-2xl rounded-b-none border-t border-x border-b border-slate-300"
                    : "rounded-2xl border border-slate-300 bg-slate-50/80 hover:bg-[#fafbff] hover:shadow-md shadow-sm"
                }`}
                style={{
                  backgroundColor: isRegistrosExpanded ? theme.lightBg : undefined,
                  borderBottomColor: isRegistrosExpanded ? theme.lightBorder : undefined,
                }}
            >
              <div className="flex items-center gap-3.5">
                <div
                  className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl border shadow-xs transition-transform duration-200 group-hover:scale-105"
                  style={{
                    backgroundColor: theme.lightBg,
                    borderColor: theme.lightBorder,
                    color: theme.primary,
                  }}
                >
                  <Table2 className="h-5 w-5" />
                </div>
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-sm font-bold text-slate-900">
                      {isMonitoring
                        ? "Sumário de Auditoria e Ocorrências"
                        : "Sumário de Registros Cadastrados"}
                    </span>
                    <span
                      className="rounded-full border px-2.5 py-0.5 font-mono text-[11px] font-bold shadow-xs"
                      style={{
                        backgroundColor: theme.lightBg,
                        borderColor: theme.lightBorder,
                        color: theme.primary,
                      }}
                    >
                      {baseRegs.length} {baseRegs.length === 1 ? "achado" : "achados"}
                    </span>
                    {isMonitoring && (
                      <div className="flex items-center gap-1.5">
                        <span className="inline-flex items-center gap-1 font-semibold text-[#008763] bg-[#e6fbf4] border border-[#a7f3d0] px-2 py-0.5 rounded-full text-[10px]">
                          <span className="h-1.5 w-1.5 rounded-full bg-[#008763]" />
                          {sanadasCount} saneada(s)
                        </span>
                        <span className="inline-flex items-center gap-1 font-semibold text-[#b45309] bg-[#fffbeb] border border-[#fde68a] px-2 py-0.5 rounded-full text-[10px]">
                          <span className="h-1.5 w-1.5 rounded-full bg-[#b45309]" />
                          {pendentesCount} pendente(s)
                        </span>
                      </div>
                    )}
                  </div>
                  <p className="mt-0.5 text-xs text-slate-500">
                    {isMonitoring
                      ? `Clique para ${isRegistrosExpanded ? "recolher" : "abrir e gerenciar"} a tabela completa de ocorrências`
                      : `Total de ${ws.registrosNc.length} foto(s) e ocorrências consolidadas no relatório`}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2 text-xs font-semibold text-slate-500 group-hover:text-slate-900 transition-colors shrink-0">
                <span className="hidden sm:inline">
                  {isRegistrosExpanded ? "Recolher Sumário" : "Expandir Sumário"}
                </span>
                <span
                  className={`flex h-7 w-7 items-center justify-center rounded-full transition-transform duration-300 ${
                    isRegistrosExpanded ? "rotate-180" : "rotate-0 bg-slate-100 text-slate-600"
                  }`}
                  style={
                    isRegistrosExpanded
                      ? {
                          backgroundColor: theme.lightBg,
                          color: theme.primary,
                        }
                      : undefined
                  }
                >
                  <ChevronDown className="h-4 w-4 stroke-[2.5]" />
                </span>
              </div>
            </button>

              {/* Painel acoplado diretamente com animação fluida de abertura (CSS Grid) */}
              <div
                className={`grid transition-all duration-300 ease-in-out ${
                  isRegistrosExpanded
                    ? "grid-rows-[1fr] opacity-100"
                    : "grid-rows-[0fr] opacity-0 pointer-events-none"
                }`}
              >
                <div className="overflow-hidden">
                  <RegistrosCadastradosPanel onOpenEditModal={onOpenEditModal || (() => {})} />
                </div>
              </div>
            </div>
          </div>
        );
      })()}
    </Card>
  );
};
