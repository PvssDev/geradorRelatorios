import React, { useState, useMemo, useEffect } from "react";
import { X, Edit3, Trash2, Save, AlertTriangle, Search, FileText } from "lucide-react";
import { toast } from "sonner";
import { useReportStore, derivarProximaCodificacao } from "../../store/useReportStore";
import { SituacaoNC, obterTermosUI } from "../../types/report.types";
import { modalInputCls, modalPill } from "./modalHelpers";

export const EditRecordsModal: React.FC<{
  initialTab?: "fisc" | "nc";
  onClose: () => void;
}> = ({ initialTab = "fisc", onClose }) => {
  const {
    tipoRelatorio,
    categoriaRelatorio,
    locaisSocicam,
    mapSiglas,
    getActiveWorkspace,
    getNcOptionsForCurrent,
    updateFiscalizacao,
    updateRegistroNcAt,
  } = useReportStore();

  const ws = getActiveWorkspace();
  const isMonitoring = categoriaRelatorio === "Monitoramento";
  const terms = obterTermosUI(isMonitoring);
  const optionsNc = getNcOptionsForCurrent();

  const [activeTab, setActiveTab] = useState<"fisc" | "nc">(initialTab);

  // Estado Tab 1: Editar Fiscalização
  const [selectedFiscId, setSelectedFiscId] = useState(
    ws.fiscalizacoes[0]?.["ID da Fiscalização"] || ""
  );
  const currentFisc = ws.fiscalizacoes.find(
    (f) => f["ID da Fiscalização"] === selectedFiscId
  );

  const [editId, setEditId] = useState(
    currentFisc?.["ID da Fiscalização"] || ""
  );
  const [editData, setEditData] = useState(currentFisc?.Data || "");
  const [editHora, setEditHora] = useState(currentFisc?.Hora || "");
  const [editCidade, setEditCidade] = useState(currentFisc?.Cidade || "");
  const [editLocal, setEditLocal] = useState(currentFisc?.Local || "");
  const [editContrato, setEditContrato] = useState(currentFisc?.Contrato || "");
  const [editResp, setEditResp] = useState(
    currentFisc?.["Pessoal Responsável"] || ""
  );
  const [editCoord, setEditCoord] = useState(currentFisc?.Coordenador || "");
  const [editPeriodo, setEditPeriodo] = useState(currentFisc?.Período || "");

  const handleSelectFiscChange = (newId: string) => {
    setSelectedFiscId(newId);
    const found = ws.fiscalizacoes.find(
      (f) => f["ID da Fiscalização"] === newId
    );
    if (found) {
      setEditId(found["ID da Fiscalização"]);
      setEditData(found.Data);
      setEditHora(found.Hora);
      setEditCidade(found.Cidade);
      setEditLocal(found.Local);
      setEditContrato(found.Contrato);
      setEditResp(found["Pessoal Responsável"]);
      setEditCoord(found.Coordenador);
      setEditPeriodo(found.Período);
    }
  };

  const handleSaveFisc = (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentFisc) return;
    const res = updateFiscalizacao(selectedFiscId, {
      ...currentFisc,
      "ID da Fiscalização": editId.trim(),
      Data: editData.trim(),
      Hora: tipoRelatorio === "CRA" ? editHora.trim() : "",
      Cidade: tipoRelatorio === "CRA" ? editCidade.trim() : "",
      Local:
        tipoRelatorio === "CRA"
          ? "Rota do Atlântico"
          : tipoRelatorio === "CRC"
          ? "Sistema Viário do Paiva"
          : editLocal.trim() || locaisSocicam[0],
      Contrato: editContrato.trim(),
      "Pessoal Responsável": editResp.trim(),
      Coordenador: editCoord.trim(),
      Período: editPeriodo.trim(),
    });
    if (!res.ok) {
      toast.error(res.error || "Erro ao salvar alterações.");
      return;
    }
    setSelectedFiscId(editId.trim());
    toast.success(`${terms.term_fisc} atualizada com sucesso!`);
  };

  // Estado Tab 2: Editar NC / PA (filtrado por ID igual ao modals.py)
  const idsComNc = useMemo(() => {
    return Array.from(
      new Set(ws.registrosNc.map((nc) => nc["ID da Fiscalização"]))
    );
  }, [ws.registrosNc]);

  const [filterIdForNc, setFilterIdForNc] = useState<string>(
    idsComNc[0] || ""
  );

  const ncsFiltradas = useMemo(() => {
    return ws.registrosNc.filter(
      (nc) => !filterIdForNc || nc["ID da Fiscalização"] === filterIdForNc
    );
  }, [ws.registrosNc, filterIdForNc]);

  const [selectedNcLocalIdx, setSelectedNcLocalIdx] = useState(0);
  const currentNc = ncsFiltradas[selectedNcLocalIdx] || null;

  const parseSiglasList = (raw?: string): string[] => {
    if (!raw) return [];
    return raw
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
  };

  const [editIsPa, setEditIsPa] = useState(false);
  const [editSiglas, setEditSiglas] = useState<string[]>([]);
  const [editIdentificacao, setEditIdentificacao] = useState("");
  const [editNcPista, setEditNcPista] = useState("");
  const [editNcTrecho, setEditNcTrecho] = useState("");
  const [editNcObs, setEditNcObs] = useState("");
  const [editNcLegendaFoto, setEditNcLegendaFoto] = useState("");
  const [editNcDir, setEditNcDir] = useState("");
  const [editNcFund, setEditNcFund] = useState("");
  const [editNcDet, setEditNcDet] = useState("");
  const [editNcSit, setEditNcSit] = useState<SituacaoNC>("Pendente");
  const [editNcAnalise, setEditNcAnalise] = useState("");

  useEffect(() => {
    if (!currentNc) return;
    const isPaInit =
      Boolean(currentNc["Ponto de Atenção"]) &&
      !Boolean(currentNc["Não Conformidade"]);
    setEditIsPa(isPaInit);
    setEditSiglas(
      parseSiglasList(
        isPaInit ? currentNc["Ponto de Atenção"] : currentNc["Não Conformidade"]
      )
    );
    setEditIdentificacao(currentNc.Identificação || "");
    setEditNcPista(currentNc.Pista || "");
    setEditNcTrecho(currentNc.Trecho || "");
    setEditNcObs(currentNc.Observações || "");
    setEditNcLegendaFoto(currentNc["Legenda da Foto"] || "");
    setEditNcDir(currentNc["Direção (faixa)"] || "");
    setEditNcFund(currentNc["Fundamento da infração"] || "");
    setEditNcDet(currentNc.Determinação || "");
    setEditNcSit((currentNc.Situação as SituacaoNC) || "Pendente");
    setEditNcAnalise(currentNc["Análise ARPE"] || "");
  }, [currentNc]);

  const handleSaveNc = (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentNc) return;
    const siglasJoined = editSiglas.join(", ");

    if (isMonitoring && (tipoRelatorio === "CRC" || tipoRelatorio === "SOCICAM")) {
      updateRegistroNcAt(currentNc["ID da Fiscalização"], currentNc["Nº"], {
        Situação: editNcSit,
        "Legenda da Foto": editNcLegendaFoto,
        Determinação: editNcDet,
        Observações: editNcObs,
        "Análise ARPE": editNcAnalise,
      });
    } else if (isMonitoring && tipoRelatorio === "CRA") {
      updateRegistroNcAt(currentNc["ID da Fiscalização"], currentNc["Nº"], {
        Pista: editNcPista,
        Trecho: editNcTrecho,
        Situação: editNcSit,
        "Não Conformidade": siglasJoined || currentNc["Não Conformidade"],
        Identificação:
          editIdentificacao.trim() || siglasJoined || currentNc.Identificação,
        "Legenda da Foto": editNcLegendaFoto,
        Observações: editNcObs,
        "Direção (faixa)": editNcDir,
        "Fundamento da infração": editNcFund,
        Determinação: editNcDet,
        "Análise ARPE": editNcAnalise,
      });
    } else if (tipoRelatorio === "CRA" && !isMonitoring) {
      updateRegistroNcAt(currentNc["ID da Fiscalização"], currentNc["Nº"], {
        Pista: editNcPista,
        Trecho: editNcTrecho,
        "Não Conformidade": editIsPa ? "" : siglasJoined,
        "Ponto de Atenção": editIsPa ? siglasJoined : "",
        Identificação: editIdentificacao.trim() || siglasJoined,
        Observações: editNcObs,
        "Direção (faixa)": editNcDir,
        "Fundamento da infração": editNcFund,
        Determinação: editNcDet,
      });
    } else {
      // CRC ou SOCICAM em Fiscalização
      updateRegistroNcAt(currentNc["ID da Fiscalização"], currentNc["Nº"], {
        Pista: tipoRelatorio === "CRC" ? editNcPista : "",
        Trecho: tipoRelatorio === "CRC" ? editNcTrecho : "",
        "Não Conformidade": siglasJoined,
        "Ponto de Atenção": "",
        Identificação: editIdentificacao.trim() || siglasJoined,
        Observações: editNcObs,
        "Fundamento da infração": editNcFund,
        Determinação: editNcDet,
      });
    }

    toast.success(`Item #${currentNc["Nº"]} atualizado com sucesso!`);
  };

  const allSiglaChoices = useMemo(() => {
    const merged = [...optionsNc];
    for (const s of editSiglas) {
      if (s && !merged.includes(s)) merged.push(s);
    }
    return merged;
  }, [optionsNc, editSiglas]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-md"
      role="dialog"
      aria-modal="true"
    >
      <div className="flex max-h-[92vh] w-full max-w-2xl flex-col overflow-hidden rounded-2xl border border-border bg-card shadow-card-lg">
        <div className="flex items-center justify-between border-b border-border bg-navy-gradient px-5 py-4 text-primary-foreground">
          <h3 className="flex items-center gap-2 text-base font-bold">
            <Edit3 className="h-5 w-5 text-accent" />
            Editar Dados Registrados — {tipoRelatorio} ({categoriaRelatorio})
          </h3>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1.5 text-primary-foreground/80 hover:bg-white/10 hover:text-primary-foreground"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Abas */}
        <div className="flex gap-2 border-b border-border bg-muted px-5 pt-3">
          <button
            type="button"
            onClick={() => setActiveTab("fisc")}
            className={`rounded-t-lg border-b-2 px-4 py-2 text-xs font-bold transition ${
              activeTab === "fisc"
                ? "border-accent bg-card text-foreground"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            {terms.term_fisc_plural} ({ws.fiscalizacoes.length})
          </button>
          <button
            type="button"
            onClick={() => {
              setActiveTab("nc");
              if (!filterIdForNc && idsComNc[0]) setFilterIdForNc(idsComNc[0]);
              setSelectedNcLocalIdx(0);
            }}
            className={`rounded-t-lg border-b-2 px-4 py-2 text-xs font-bold transition ${
              activeTab === "nc"
                ? "border-accent bg-card text-foreground"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            {tipoRelatorio === "CRA" && !isMonitoring
              ? `Não Conformidades e Pontos de Atenção (${ws.registrosNc.length})`
              : `Não Conformidades (${ws.registrosNc.length})`}
          </button>
        </div>

        <div className="overflow-y-auto p-5">
          {activeTab === "fisc" ? (
            ws.fiscalizacoes.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                Nenhum cabeçalho cadastrado.
              </p>
            ) : (
              <form onSubmit={handleSaveFisc} className="space-y-4">
                <div>
                  <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                    Selecione o ID {terms.term_fisc_prep} para editar
                  </label>
                  <select
                    value={selectedFiscId}
                    onChange={(e) => handleSelectFiscChange(e.target.value)}
                    className={modalInputCls}
                  >
                    {ws.fiscalizacoes.map((f) => (
                      <option
                        key={f["ID da Fiscalização"]}
                        value={f["ID da Fiscalização"]}
                      >
                        {f["ID da Fiscalização"]} — {f.Local}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                      ID {terms.term_fisc_prep}
                    </label>
                    <input
                      type="text"
                      value={editId}
                      onChange={(e) => setEditId(e.target.value)}
                      className={modalInputCls}
                    />
                  </div>
                  <div>
                    <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                      Data (DD/MM/AAAA)
                    </label>
                    <input
                      type="text"
                      value={editData}
                      onChange={(e) => setEditData(e.target.value)}
                      className={modalInputCls}
                    />
                  </div>
                </div>

                {tipoRelatorio === "CRA" && (
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                        Hora
                      </label>
                      <input
                        type="text"
                        value={editHora}
                        onChange={(e) => setEditHora(e.target.value)}
                        className={modalInputCls}
                      />
                    </div>
                    <div>
                      <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                        Cidade
                      </label>
                      <input
                        type="text"
                        value={editCidade}
                        onChange={(e) => setEditCidade(e.target.value)}
                        className={modalInputCls}
                      />
                    </div>
                  </div>
                )}

                {tipoRelatorio === "SOCICAM" && (
                  <div>
                    <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                      Terminal Rodoviário (Local)
                    </label>
                    <select
                      value={editLocal}
                      onChange={(e) => setEditLocal(e.target.value)}
                      className={modalInputCls}
                    >
                      {locaisSocicam.map((l) => (
                        <option key={l} value={l}>
                          {l}
                        </option>
                      ))}
                    </select>
                  </div>
                )}

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                      Período
                    </label>
                    <input
                      type="text"
                      value={editPeriodo}
                      onChange={(e) => setEditPeriodo(e.target.value)}
                      className={modalInputCls}
                    />
                  </div>
                  <div>
                    <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                      Contrato
                    </label>
                    <input
                      type="text"
                      value={editContrato}
                      onChange={(e) => setEditContrato(e.target.value)}
                      className={modalInputCls}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                      Pessoal Responsável
                    </label>
                    <input
                      type="text"
                      value={editResp}
                      onChange={(e) => setEditResp(e.target.value)}
                      className={modalInputCls}
                    />
                  </div>
                  <div>
                    <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                      Coordenador
                    </label>
                    <input
                      type="text"
                      value={editCoord}
                      onChange={(e) => setEditCoord(e.target.value)}
                      className={modalInputCls}
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-xs font-semibold text-primary-foreground shadow-sm hover:bg-navy-2 active:scale-[0.98] transition-all"
                >
                  <Save className="h-4 w-4" />
                  Salvar Alterações {terms.term_fisc_prep}
                </button>
              </form>
            )
          ) : ws.registrosNc.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              Nenhum registro de ocorrência cadastrado.
            </p>
          ) : (
            <form onSubmit={handleSaveNc} className="space-y-4">
              <div className="grid gap-3 sm:grid-cols-2">
                <div>
                  <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                    Filtrar por ID {terms.term_fisc_prep}
                  </label>
                  <select
                    value={filterIdForNc}
                    onChange={(e) => {
                      setFilterIdForNc(e.target.value);
                      setSelectedNcLocalIdx(0);
                    }}
                    className={modalInputCls}
                  >
                    {idsComNc.map((id) => (
                      <option key={id} value={id}>
                        {id}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                    Selecione o Item para editar
                  </label>
                  <select
                    value={selectedNcLocalIdx}
                    onChange={(e) =>
                      setSelectedNcLocalIdx(Number(e.target.value))
                    }
                    className={modalInputCls}
                  >
                    {ncsFiltradas.map((nc, i) => {
                      const tipoTag =
                        nc["Ponto de Atenção"] && !nc["Não Conformidade"]
                          ? "PA"
                          : "NC";
                      const desc =
                        nc["Não Conformidade"] ||
                        nc["Ponto de Atenção"] ||
                        nc.Identificação ||
                        "Sem descrição";
                      return (
                        <option
                          key={`${nc["ID da Fiscalização"]}_${nc["Nº"]}`}
                          value={i}
                        >
                          Item nº {nc["Nº"]} [{tipoTag}] — {desc.slice(0, 42)}
                        </option>
                      );
                    })}
                  </select>
                </div>
              </div>

              {currentNc && (
                <>
                  {tipoRelatorio === "CRA" && !isMonitoring && (
                    <div className="inline-flex rounded-xl bg-muted p-1">
                      <button
                        type="button"
                        onClick={() => setEditIsPa(false)}
                        className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
                          !editIsPa
                            ? "bg-nc-soft text-nc shadow-card"
                            : "text-muted-foreground"
                        }`}
                      >
                        Não Conformidade (NC)
                      </button>
                      <button
                        type="button"
                        onClick={() => setEditIsPa(true)}
                        className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition ${
                          editIsPa
                            ? "bg-pa-soft text-pa shadow-card"
                            : "text-muted-foreground"
                        }`}
                      >
                        Ponto de Atenção (PA)
                      </button>
                    </div>
                  )}

                  {(tipoRelatorio === "CRA" ||
                    (tipoRelatorio === "CRC" && !isMonitoring)) && (
                    <div className="grid gap-3 sm:grid-cols-3">
                      <div>
                        <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                          Pista
                        </label>
                        <input
                          type="text"
                          value={editNcPista}
                          onChange={(e) => setEditNcPista(e.target.value)}
                          className={modalInputCls}
                        />
                      </div>
                      <div>
                        <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                          Trecho
                        </label>
                        <input
                          type="text"
                          value={editNcTrecho}
                          onChange={(e) => setEditNcTrecho(e.target.value)}
                          className={modalInputCls}
                        />
                      </div>
                      {tipoRelatorio === "CRA" && (
                        <div>
                          <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                            Direção / Faixa
                          </label>
                          <select
                            value={editNcDir}
                            onChange={(e) => setEditNcDir(e.target.value)}
                            className={modalInputCls}
                          >
                            <option value="Direita">Direita</option>
                            <option value="Esquerda">Esquerda</option>
                            <option value="">Sem faixa específica</option>
                          </select>
                        </div>
                      )}
                    </div>
                  )}

                  {(!isMonitoring || tipoRelatorio === "CRA") && (
                    <>
                      <div>
                        <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                          Codificação
                        </label>
                        <input
                          type="text"
                          value={editIdentificacao}
                          onChange={(e) => setEditIdentificacao(e.target.value)}
                          className={`${modalInputCls} font-mono`}
                        />
                      </div>

                      <div>
                        <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                          Siglas Selecionadas
                        </label>
                        <div className="flex flex-wrap gap-1.5">
                          {allSiglaChoices.map((s) => {
                            const active = editSiglas.includes(s);
                            return (
                              <button
                                key={s}
                                type="button"
                                title={mapSiglas[s] || s}
                                onClick={() =>
                                  setEditSiglas((prev) =>
                                    prev.includes(s)
                                      ? prev.filter((x) => x !== s)
                                      : [...prev, s]
                                  )
                                }
                                className={modalPill(active)}
                              >
                                {s}
                              </button>
                            );
                          })}
                        </div>
                      </div>
                    </>
                  )}

                  {isMonitoring ? (
                    <>
                      <div className="grid gap-3 sm:grid-cols-2">
                        <div>
                          <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                            Situação
                          </label>
                          <select
                            value={editNcSit}
                            onChange={(e) =>
                              setEditNcSit(e.target.value as SituacaoNC)
                            }
                            className={modalInputCls}
                          >
                            <option value="Pendente">Pendente</option>
                            <option value="Parcialmente Sanada">
                              Parcialmente Sanada
                            </option>
                            <option value="Sanada">Sanada</option>
                          </select>
                        </div>
                        <div>
                          <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                            Legenda da Foto Atual
                          </label>
                          <input
                            type="text"
                            value={editNcLegendaFoto}
                            onChange={(e) =>
                              setEditNcLegendaFoto(e.target.value)
                            }
                            className={modalInputCls}
                          />
                        </div>
                      </div>

                      <div>
                        <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                          {tipoRelatorio === "SOCICAM"
                            ? "Informação SOCICAM"
                            : `Posicionamento ${tipoRelatorio}`}
                        </label>
                        <textarea
                          rows={2}
                          value={editNcDet}
                          onChange={(e) => setEditNcDet(e.target.value)}
                          className={modalInputCls}
                        />
                      </div>

                      <div>
                        <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                          Constatação
                        </label>
                        <textarea
                          rows={2}
                          value={editNcObs}
                          onChange={(e) => setEditNcObs(e.target.value)}
                          className={modalInputCls}
                        />
                      </div>

                      <div>
                        <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                          Análise ARPE
                        </label>
                        <textarea
                          rows={2}
                          value={editNcAnalise}
                          onChange={(e) => setEditNcAnalise(e.target.value)}
                          className={modalInputCls}
                        />
                      </div>
                    </>
                  ) : (
                    <>
                      <div>
                        <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                          Observações (Legenda da Foto)
                        </label>
                        <textarea
                          rows={2}
                          value={editNcObs}
                          onChange={(e) => setEditNcObs(e.target.value)}
                          className={modalInputCls}
                        />
                      </div>

                      <div className="grid gap-3 sm:grid-cols-2">
                        <div>
                          <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                            Fundamento da Infração
                          </label>
                          <textarea
                            rows={2}
                            value={editNcFund}
                            onChange={(e) => setEditNcFund(e.target.value)}
                            className={modalInputCls}
                          />
                        </div>
                        <div>
                          <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                            Determinação
                          </label>
                          <textarea
                            rows={2}
                            value={editNcDet}
                            onChange={(e) => setEditNcDet(e.target.value)}
                            className={modalInputCls}
                          />
                        </div>
                      </div>
                    </>
                  )}

                  <button
                    type="submit"
                    className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-primary px-4 py-2.5 text-xs font-semibold text-primary-foreground shadow-sm hover:bg-navy-2 active:scale-[0.98] transition-all"
                  >
                    <Save className="h-4 w-4" />
                    Salvar Alterações no Item #{currentNc["Nº"]}
                  </button>
                </>
              )}
            </form>
          )}
        </div>
      </div>
    </div>
  );
};
