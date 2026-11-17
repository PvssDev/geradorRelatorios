import React, { useEffect, useState, useMemo } from "react";
import { ImagePlus, AlertTriangle, Eye } from "lucide-react";
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
import { FiscalizacaoNcFields } from "./registro/FiscalizacaoNcFields";
import { MonitoramentoNcFields } from "./registro/MonitoramentoNcFields";
import { RegistroActionFooter } from "./registro/RegistroActionFooter";

interface RegistroNcFormProps {
  dense?: boolean;
  onOpenCustomNcModal: (onSelectSigla: (siglaOrDesc: string) => void) => void;
  onOpenRelacionarModal: (currentPhotoName?: string) => void;
  onOpenGalleryModal: () => void;
  onOpenEditModal?: (tab?: "fisc" | "nc") => void;
}

export const RegistroNcForm: React.FC<RegistroNcFormProps> = ({
  dense = false,
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
    setPistaPersistida,
    setTrechoPersistido,
    addOrUpdateRegistroNc,
    upsertActiveFiscalizacao,
    monitoringNewPhotoName: selectedNewPhotoMon,
    setMonitoringNewPhotoName: setSelectedNewPhotoMon,
  } = useReportStore();

  const ws = getActiveWorkspace();
  const isMonitoring = categoriaRelatorio === "Monitoramento";
  const optionsNc = getNcOptionsForCurrent();
  const theme = getConcessionTheme(tipoRelatorio, categoriaRelatorio);

  const [tipo, setTipo] = useState<"NC" | "PA">("NC");
  const [direcaoFaixa, setDirecaoFaixa] = useState<"Direita" | "Esquerda">("Direita");
  const [codificacao, setCodificacao] = useState("");
  const [siglas, setSiglas] = useState<string[]>([]);
  const [fund, setFund] = useState("");
  const [det, setDet] = useState("");

  const [situacaoMon, setSituacaoMon] = useState<SituacaoNC>("Pendente");
  const [legendaFotoMon, setLegendaFotoMon] = useState("");
  const [posConcessionariaMon, setPosConcessionariaMon] = useState("");
  const [constatacaoMon, setConstatacaoMon] = useState("");
  const [analiseArpeMon, setAnaliseArpeMon] = useState("");

  useEffect(() => {
    if (isMonitoring) {
      setTipo("NC");
    }
    setSiglas([]);
    setCodificacao("");
  }, [tipoRelatorio, categoriaRelatorio, isMonitoring]);

  const currentOldItem =
    isMonitoring && ws.oldPhotosToMatch.length > 0
      ? ws.oldPhotosToMatch[
          Math.max(0, Math.min(ws.carouselIndex, ws.oldPhotosToMatch.length - 1))
        ]
      : null;

  // Hidrata os campos de auditoria apenas ao entrar em Monitoramento ou trocar a ocorrência anterior
  useEffect(() => {
    if (!isMonitoring || !currentOldItem) return;
    const saved = ws.registrosNc.find(
      (r) => !r.is_relacionado && r.Identificação === currentOldItem.id_nc
    );
    setPosConcessionariaMon(saved?.Determinação || "");
    setConstatacaoMon(saved?.Observações || currentOldItem.constatacao || "");
    setAnaliseArpeMon(saved?.["Análise ARPE"] || "");
    setLegendaFotoMon(saved?.["Legenda da Foto"] || "");
    setSituacaoMon(saved?.Situação || "Pendente");
    if (saved?.Foto) {
      setSelectedNewPhotoMon(saved.Foto);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isMonitoring, tipoRelatorio, currentOldItem?.id_nc]);

  // Garante que a foto recente selecionada exista na lista atual sem travar a navegação
  useEffect(() => {
    if (!isMonitoring) return;
    if (
      !selectedNewPhotoMon ||
      !ws.photos.some((p) => p.name === selectedNewPhotoMon)
    ) {
      setSelectedNewPhotoMon(ws.photos[0]?.name || "");
    }
  }, [isMonitoring, ws.photos, selectedNewPhotoMon, setSelectedNewPhotoMon]);

  const fotos = ws.photos;
  const fotoIdx = Math.max(0, Math.min(ws.carouselIndex, Math.max(0, fotos.length - 1)));
  const activePhoto = fotos[fotoIdx] || null;

  const activeFiscIdx = Math.max(
    0,
    Math.min(ws.activeFiscalizacaoIndex, Math.max(0, ws.fiscalizacoes.length - 1))
  );
  const activeFisc = ws.fiscalizacoes[activeFiscIdx];
  const dataBr = activeFisc?.Data || new Date().toLocaleDateString("pt-BR");
  const ano = dataBr.split("/")[2] || String(new Date().getFullYear());

  const currentFiscId = activeFisc?.["ID da Fiscalização"]?.trim() || "";
  const currentFiscRegs = useMemo(
    () =>
      ws.registrosNc.filter(
        (r) => !currentFiscId || (r["ID da Fiscalização"] || "").trim() === currentFiscId
      ),
    [ws.registrosNc, currentFiscId]
  );

  const maxSeqInFiscalizacao = useMemo(() => {
    let max = 0;
    for (const r of currentFiscRegs) {
      const cod = (r.Codificação || r.Identificação || "").trim();
      const m = cod.match(/[\/.](\d{4})\.(\d+)$/) || cod.match(/[\/.](\d+)$/);
      if (m) {
        const num = parseInt(m[2] || m[1], 10);
        if (!isNaN(num) && num > max) max = num;
      }
    }
    return max > 0 ? max + 1 : currentFiscRegs.length + 1;
  }, [currentFiscRegs]);

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

  const ensureFiscalizacaoHeader = (): { id: string; local: string } => {
    const existing = ws.fiscalizacoes[activeFiscIdx];
    if (existing && existing["ID da Fiscalização"]?.trim()) {
      return {
        id: existing["ID da Fiscalização"].trim(),
        local: existing.Local,
      };
    }
    const prefix = isMonitoring ? "MON" : "FISC";
    const generatedId = `${prefix}-${tipoRelatorio}-${ano}-001`;
    const defaultLocal =
      tipoRelatorio === "CRA"
        ? "Rota do Atlântico"
        : tipoRelatorio === "CRC"
        ? "Sistema Viário do Paiva"
        : locaisSocicam[5] || "TIP Recife";

    upsertActiveFiscalizacao({
      "ID da Fiscalização": generatedId,
      Data: dataBr,
      Hora: tipoRelatorio === "CRA" ? "09:00" : "",
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

  const targetPhotoName = isMonitoring
    ? selectedNewPhotoMon || activePhoto?.name || ""
    : activePhoto?.name || "";

  const registroExistenteComFoto = useMemo(() => {
    if (!targetPhotoName) return null;
    const nameLower = targetPhotoName.trim().toLowerCase();
    return (
      ws.registrosNc.find(
        (r) => (r.Foto || "").trim().toLowerCase() === nameLower
      ) || null
    );
  }, [ws.registrosNc, targetPhotoName]);

  const registroExistenteComFotoAnterior = useMemo(() => {
    if (!isMonitoring || !currentOldItem) return null;
    return (
      ws.registrosNc.find(
        (r) =>
          !r.is_relacionado &&
          (r.Identificação === currentOldItem.id_nc ||
            (Boolean(currentOldItem.old_photo_path) &&
              r["Foto Anterior"] === currentOldItem.old_photo_path))
      ) || null
    );
  }, [isMonitoring, currentOldItem, ws.registrosNc]);

  const isFotoBloqueada = Boolean(
    registroExistenteComFoto || registroExistenteComFotoAnterior
  );

  const addReg = () => {
    if (!targetPhotoName) {
      toast.error("Envie e selecione ao menos uma foto no bloco 02.");
      return;
    }

    if (registroExistenteComFoto) {
      toast.error(
        `Esta foto atual já está cadastrada no Item #${registroExistenteComFoto["Nº"]} (${registroExistenteComFoto.Identificação || "Ocorrência"}). Selecione outra foto para novo cadastro.`
      );
      return;
    }

    if (registroExistenteComFotoAnterior) {
      toast.error(
        `Esta foto anterior (${currentOldItem?.id_nc}) já foi registrada no Item #${registroExistenteComFotoAnterior["Nº"]}. Selecione outra foto anterior ou edite em 'Editar Dados'.`
      );
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

      const { id: idVinculo, local: localVinculo } = ensureFiscalizacaoHeader();
      const identMon =
        currentOldItem?.id_nc ||
        codificacao.trim() ||
        siglas.join(", ") ||
        `NC ${seqStr}`;

      addOrUpdateRegistroNc({
        "ID da Fiscalização": idVinculo,
        "Nº": currentFiscRegs.length + 1,
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

    if (siglas.length === 0 && !codificacao.trim()) {
      toast.error(
        "Selecione ao menos uma sigla/irregularidade ou preencha a codificação."
      );
      return;
    }

    const { id: idVinculo, local: localVinculo } = ensureFiscalizacaoHeader();
    const isPa =
      (tipoRelatorio === "CRA" || tipoRelatorio === "SOCICAM") && tipo === "PA";

    if (tipoRelatorio === "CRA" || tipoRelatorio === "SOCICAM") {
      const tipoRegistroStr = isPa ? "Ponto de Atenção" : "Não Conformidade";
      const fotoNum = fotoIdx + 1;
      const grpId = `grp_${idVinculo}_${fotoNum}_${Date.now()}`;
      const defaultBase =
        tipoRelatorio === "SOCICAM" ? "SOCICAM" : "CRA.ST601.2794-2834";
      const baseRaw = codificacao.trim() || defaultBase;
      const baseLimpa = baseRaw.split("/")[0].trim() || baseRaw;

      const siglasParaCadastrar = siglas.length > 0 ? siglas : [baseRaw];
      const tempNcClone = [...ws.registrosNc];

      siglasParaCadastrar.forEach((s, idx) => {
        const seqIdx = obterProximoSequencialCra(
          tempNcClone,
          idVinculo,
          tipoRegistroStr
        );
        const codFormatado = calcularCodificacaoCra(baseLimpa, dataBr, seqIdx);
        const obsSigla = (mapSiglas[s] || s).toLowerCase();
        const isUltima = idx === siglasParaCadastrar.length - 1;

        const novoRec: RegistroNcItem = {
          "ID da Fiscalização": idVinculo,
          "Nº": fotoNum,
          Terminal: localVinculo,
          Pista: tipoRelatorio === "CRA" ? ws.pistaPersistida.trim() : "",
          Trecho: tipoRelatorio === "CRA" ? codFormatado : "",
          "Não Conformidade": isPa ? "" : s,
          "Ponto de Atenção": isPa ? s : "",
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
        `${isPa ? "Ponto de Atenção" : "Não Conformidade"} (${
          siglasParaCadastrar.length > 1
            ? `${siglasParaCadastrar.length} itens`
            : baseLimpa
        }) adicionado(a)!`
      );
      setSiglas([]);
      setCodificacao("");
      setFund("");
      setDet("");
      return;
    }

    const codPadrao = `CRC.SH015.0646+0648/${ano}.${seqStr}`;
    const identFinal = codificacao.trim() || codPadrao;
    const descStr = siglas.join(", ") || identFinal;
    const obsFinal = siglas.length
      ? siglas.map((s) => (mapSiglas[s] || s).toLowerCase()).join(", ")
      : descStr;
    const nextNum = currentFiscRegs.length + 1;

    addOrUpdateRegistroNc({
      "ID da Fiscalização": idVinculo,
      "Nº": nextNum,
      Terminal: localVinculo,
      Pista: ws.pistaPersistida.trim(),
      Trecho: ws.trechoPersistido.trim(),
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

    toast.success(`Não Conformidade (${identFinal}) adicionada!`);
    setSiglas([]);
    setCodificacao("");
    setFund("");
    setDet("");
  };

  const temOcorrenciaBase = currentFiscRegs.some((r) => !r.is_relacionado);
  const podeRelacionar = Boolean(temOcorrenciaBase && fotos.length > 0);

  return (
    <Card
      n={3}
      icon={<ImagePlus className="h-5 w-5" />}
      title={
        isMonitoring
          ? "Auditoria de Não Conformidade (Monitoramento)"
          : "Registro de Não Conformidade ou Ponto de Atenção"
      }
    >
      {/* Topo do Card 03: Seletor de Tipo/Situação */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        {!isMonitoring ? (
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
          <div className="inline-flex flex-wrap gap-1.5 rounded-2xl border border-border bg-secondary/70 p-1.5 shadow-inner">
            {(["Pendente", "Parcialmente Sanada", "Sanada"] as SituacaoNC[]).map(
              (sit) => {
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
              }
            )}
          </div>
        )}
      </div>

      {/* Carrossel + Campos */}
      <div
        className={
          dense
            ? "mt-6 grid grid-cols-1 xl:grid-cols-12 gap-8 items-start xl:items-stretch"
            : "mt-8 space-y-8"
        }
      >
        <div className={dense ? "xl:col-span-6" : ""}>
          <PhotoCarouselPanel
            selectedNewPhotoName={selectedNewPhotoMon}
            onSelectNewPhotoName={setSelectedNewPhotoMon}
            onOpenGalleryModal={onOpenGalleryModal}
          />
        </div>

        <div className={dense ? "xl:col-span-6 xl:relative" : ""}>
          <div className={dense ? "xl:absolute xl:inset-0 flex flex-col" : "space-y-8"}>
            <div className={dense ? "xl:flex-1 xl:min-h-0 xl:overflow-y-auto xl:pr-1.5" : ""}>
              {!isMonitoring ? (
                <FiscalizacaoNcFields
                  tipoRelatorio={tipoRelatorio}
                  dense={dense}
                  ano={ano}
                  seqStr={seqStr}
                  pistaPersistida={ws.pistaPersistida}
                  trechoPersistido={ws.trechoPersistido}
                  direcaoFaixa={direcaoFaixa}
                  codificacao={codificacao}
                  siglas={siglas}
                  optionsNc={optionsNc}
                  mapSiglas={mapSiglas}
                  fund={fund}
                  det={det}
                  contratoPadrao={contratosPadrao[tipoRelatorio]}
                  themePrimary={theme.primary}
                  onChangePista={setPistaPersistida}
                  onChangeTrecho={setTrechoPersistido}
                  onChangeDirecao={setDirecaoFaixa}
                  onChangeCodificacao={setCodificacao}
                  onSugerirCodificacao={sugerirCodificacao}
                  onToggleSigla={(s) =>
                    setSiglas((x) =>
                      x.includes(s) ? x.filter((y) => y !== s) : [...x, s]
                    )
                  }
                  onOpenCustomNcModal={() =>
                    onOpenCustomNcModal((novaSigla) =>
                      setSiglas((prev) =>
                        prev.includes(novaSigla) ? prev : [...prev, novaSigla]
                      )
                    )
                  }
                  onChangeFund={setFund}
                  onChangeDet={setDet}
                />
              ) : (
                <MonitoramentoNcFields
                  tipoRelatorio={tipoRelatorio}
                  dense={dense}
                  hasOldPhotos={ws.oldPhotosToMatch.length > 0}
                  codificacao={codificacao}
                  pistaPersistida={ws.pistaPersistida}
                  trechoPersistido={ws.trechoPersistido}
                  direcaoFaixa={direcaoFaixa}
                  legendaFotoMon={legendaFotoMon}
                  posConcessionariaMon={posConcessionariaMon}
                  constatacaoMon={constatacaoMon}
                  analiseArpeMon={analiseArpeMon}
                  onChangeCodificacao={setCodificacao}
                  onChangePista={setPistaPersistida}
                  onChangeTrecho={setTrechoPersistido}
                  onChangeDirecao={setDirecaoFaixa}
                  onChangeLegenda={setLegendaFotoMon}
                  onChangePosConcessionaria={setPosConcessionariaMon}
                  onChangeConstatacao={setConstatacaoMon}
                  onChangeAnaliseArpe={setAnaliseArpeMon}
                />
              )}
            </div>

            <RegistroActionFooter
              dense={dense}
              isMonitoring={isMonitoring}
              hasActivePhoto={Boolean(activePhoto)}
              isFotoBloqueada={isFotoBloqueada}
              registroExistenteComFoto={registroExistenteComFoto}
              registroExistenteComFotoAnterior={registroExistenteComFotoAnterior}
              podeRelacionar={podeRelacionar}
              currentFiscRegs={currentFiscRegs}
              isRegistrosExpanded={isRegistrosExpanded}
              themePrimary={theme.primary}
              themeLightBg={theme.lightBg}
              themeLightBorder={theme.lightBorder}
              onAddReg={addReg}
              onOpenRelacionar={() =>
                onOpenRelacionarModal(
                  (isMonitoring ? selectedNewPhotoMon : activePhoto?.name) ||
                    activePhoto?.name
                )
              }
              onToggleExpanded={() => setIsRegistrosExpanded((prev) => !prev)}
              onOpenEditModal={onOpenEditModal}
            />
          </div>
        </div>
      </div>
    </Card>
  );
};
