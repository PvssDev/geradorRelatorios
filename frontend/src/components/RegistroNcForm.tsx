import React, { useEffect, useState, type ReactNode } from "react";
import {
  ImagePlus,
  AlertTriangle,
  Eye,
  Plus,
  Link2,
  Wand2,
} from "lucide-react";
import { toast } from "sonner";
import { Card } from "./Card";
import { PhotoCarouselPanel } from "./PhotoCarouselPanel";
import { useReportStore } from "../store/useReportStore";
import { SituacaoNC } from "../types/report.types";

interface RegistroNcFormProps {
  onOpenCustomNcModal: (onSelectSigla: (siglaOrDesc: string) => void) => void;
  onOpenRelacionarModal: (currentPhotoName?: string) => void;
  onOpenGalleryModal: () => void;
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
    "inline-flex items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground hover:bg-navy-2 transition disabled:opacity-40",
  secondary:
    "inline-flex items-center justify-center gap-2 rounded-lg border border-border bg-card px-4 py-2.5 text-sm font-semibold text-foreground hover:border-accent hover:text-accent transition disabled:opacity-40",
};

const pill = (on: boolean) =>
  `rounded-full border px-3 py-1.5 text-xs font-medium transition ${
    on
      ? "border-accent bg-accent text-accent-foreground"
      : "border-border bg-card text-muted-foreground hover:border-accent/50"
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
}) => {
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

  // Tipo NC vs PA (Ponto de Atenção é exclusivo de CRA Fiscalização)
  const [tipo, setTipo] = useState<"NC" | "PA">("NC");
  const [direcaoFaixa, setDirecaoFaixa] = useState<"Direita" | "Esquerda">(
    "Direita"
  );
  const [codificacao, setCodificacao] = useState("");
  const [siglas, setSiglas] = useState<string[]>([]);
  const [observacoes, setObservacoes] = useState("");
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
    setObservacoes("");
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

  // Sequencial baseado apenas nas ocorrências principais (não relacionadas)
  const baseOccurrencesCount = ws.registrosNc.filter(
    (r) => !r.is_relacionado
  ).length;
  const seqStr = String(baseOccurrencesCount + 1).padStart(3, "0");

  const sugerirCodificacao = () => {
    if (tipoRelatorio === "CRA") {
      setCodificacao(`CRA.ST601.2794-2834/${ano}.${seqStr}`);
    } else if (tipoRelatorio === "CRC") {
      setCodificacao(`CRC.SH015.0646+0648/${ano}.${seqStr}`);
    } else {
      setCodificacao(`SOCICAM.${ano}.${seqStr}`);
    }
  };

  const preencherObsPelasSiglas = () => {
    if (!siglas.length) {
      toast.info("Selecione ao menos uma sigla primeiro.");
      return;
    }
    const texto = siglas
      .map((s) => (mapSiglas[s] || s).toLowerCase())
      .join(", ");
    setObservacoes(texto);
  };

  // Prévia exata da legenda gerada por src/sections/finalizacao/finalizacao.py
  const numFotoPreview = String(
    (activePhoto ? fotoIdx : fotos.length) + 1
  ).padStart(2, "0");

  const legendaPreviewFisc = (() => {
    const obsText =
      observacoes.trim() ||
      (siglas.length
        ? siglas.map((s) => (mapSiglas[s] || s).toLowerCase()).join(", ")
        : "descrição da ocorrência");
    if (tipoRelatorio === "CRA" && ws.trechoPersistido.trim()) {
      return `Foto ${numFotoPreview} – Trecho ${ws.trechoPersistido.trim()} apresentando ${obsText}, em ${dataBr}.`;
    }
    return `Foto ${numFotoPreview} – ${obsText}, em ${dataBr}.`;
  })();

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
    if (siglas.length === 0 && !codificacao.trim() && !observacoes.trim()) {
      toast.error(
        "Selecione ao menos uma sigla/irregularidade ou preencha a codificação/observações."
      );
      return;
    }

    const { id: idVinculo, local: localVinculo } = ensureFiscalizacaoHeader();
    const descStr =
      siglas.join(", ") || codificacao.trim() || observacoes.trim();
    const isPa = tipoRelatorio === "CRA" && tipo === "PA";

    const obsFinal =
      observacoes.trim() ||
      (siglas.length
        ? siglas.map((s) => (mapSiglas[s] || s).toLowerCase()).join(", ")
        : descStr);

    const identFinal = codificacao.trim() || descStr;
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
      "Direção (faixa)": tipoRelatorio === "CRA" ? direcaoFaixa : "",
      "Fundamento da infração": fund.trim(),
      Determinação: det.trim(),
      Situação: "Pendente",
      "Análise ARPE": "",
      grupo_relacao: `${idVinculo}_${nextNum}`,
      is_relacionado: false,
    });

    toast.success(
      `${isPa ? "Ponto de Atenção" : "Não Conformidade"} (${identFinal}) adicionado(a)!`
    );
    setSiglas([]);
    setCodificacao("");
    setObservacoes("");
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
            <div className="inline-flex rounded-xl bg-muted p-1">
              {(["NC", "PA"] as const).map((t) => (
                <button
                  key={t}
                  type="button"
                  onClick={() => setTipo(t)}
                  className={`flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition ${
                    tipo === t
                      ? t === "NC"
                        ? "bg-nc-soft text-nc shadow-card"
                        : "bg-pa-soft text-pa shadow-card"
                      : "text-muted-foreground"
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
              ))}
            </div>
          ) : (
            <div className="inline-flex items-center gap-2 rounded-xl bg-nc-soft px-4 py-2 text-sm font-semibold text-nc">
              <AlertTriangle className="h-4 w-4" />
              Não Conformidade (NC) · {tipoRelatorio}
            </div>
          )
        ) : (
          <div className="inline-flex flex-wrap gap-1 rounded-xl bg-muted p-1">
            {(
              ["Pendente", "Parcialmente Sanada", "Sanada"] as SituacaoNC[]
            ).map((sit) => (
              <button
                key={sit}
                type="button"
                onClick={() => setSituacaoMon(sit)}
                className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
                  situacaoMon === sit
                    ? sit === "Sanada"
                      ? "bg-ok-soft text-ok shadow-card"
                      : sit === "Parcialmente Sanada"
                      ? "bg-pa-soft text-pa shadow-card"
                      : "bg-nc-soft text-nc shadow-card"
                    : "text-muted-foreground"
                }`}
              >
                {sit}
              </button>
            ))}
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
              <div className="flex flex-wrap gap-2">
                {optionsNc.map((s) => {
                  const d = mapSiglas[s] || s;
                  const shortDesc = d.length > 42 ? `${d.slice(0, 42)}…` : d;
                  return (
                    <button
                      type="button"
                      key={s}
                      title={d}
                      className={pill(siglas.includes(s))}
                      onClick={() =>
                        setSiglas((x) =>
                          x.includes(s)
                            ? x.filter((y) => y !== s)
                            : [...x, s]
                        )
                      }
                    >
                      <b>{s}</b>
                      {d !== s ? ` · ${shortDesc}` : ""}
                    </button>
                  );
                })}
              </div>
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

            {/* Observações (usadas diretamente na legenda da foto do .docx!) + Prévia da Legenda */}
            <div className="grid gap-6 sm:grid-cols-2">
              <Field
                label={
                  tipoRelatorio === "SOCICAM"
                    ? "Observações (Local no Terminal / Legenda da Foto)"
                    : "Observações (Descrição na Legenda da Foto)"
                }
                action={
                  siglas.length > 0 ? (
                    <button
                      type="button"
                      onClick={preencherObsPelasSiglas}
                      className="text-[11px] font-medium text-muted-foreground hover:text-accent transition"
                    >
                      + Usar descrição das siglas
                    </button>
                  ) : undefined
                }
              >
                <textarea
                  rows={2}
                  className={inputCls}
                  placeholder={
                    tipoRelatorio === "SOCICAM"
                      ? "Ex: banheiro masculino do saguão em condições inadequadas"
                      : tipoRelatorio === "CRA"
                      ? "Ex: fissuras e panela na faixa de rolamento"
                      : "Ex: degrau acentuado entre a pista e o acostamento"
                  }
                  value={observacoes}
                  onChange={(e) => setObservacoes(e.target.value)}
                />
              </Field>

              <Field label="Prévia da Legenda no Relatório (.docx)">
                <p className="min-h-[62px] rounded-lg border border-input bg-muted px-3 py-2 text-xs italic leading-relaxed text-muted-foreground">
                  {legendaPreviewFisc}
                </p>
              </Field>
            </div>

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
          className={`${btn.primary} flex-1 py-3`}
          disabled={!activePhoto}
          onClick={addReg}
        >
          <Plus className="h-4 w-4" />
          {isMonitoring
            ? "Salvar Auditoria no Relatório"
            : "Adicionar Registro ao Relatório"}
        </button>

        <button
          type="button"
          className={`${btn.secondary} py-3`}
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
    </Card>
  );
};
