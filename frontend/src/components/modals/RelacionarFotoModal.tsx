import React, { useEffect, useState, useMemo } from "react";
import { createPortal } from "react-dom";
import { X, Link2, CheckCircle2, AlertTriangle, Images, Search } from "lucide-react";
import { toast } from "sonner";
import { useReportStore, derivarProximaCodificacao } from "../../store/useReportStore";
import { obterTermosUI, SituacaoNC } from "../../types/report.types";
import { modalInputCls, modalPill } from "./modalHelpers";
import { useLockBodyScroll } from "../../hooks/useLockBodyScroll";

export const RelacionarFotoModal: React.FC<{
  initialPhotoName?: string;
  onClose: () => void;
}> = ({ initialPhotoName, onClose }) => {
  useLockBodyScroll(true);
  const {
    tipoRelatorio,
    categoriaRelatorio,
    getActiveWorkspace,
    relacionarFotoComNc,
    getNcOptionsForCurrent,
    mapSiglas,
  } = useReportStore();

  const optionsNc = getNcOptionsForCurrent();
  const isCraFisc = tipoRelatorio === "CRA" && categoriaRelatorio === "Fiscalização";

  const ws = getActiveWorkspace();
  const isMonitoring = categoriaRelatorio === "Monitoramento";

  // Ocorrências principais elegíveis (que ainda não possuem 2 fotos no mesmo grupo_relacao)
  const ocorrenciasBase = useMemo(() => {
    return ws.registrosNc.filter((nc) => !nc.is_relacionado);
  }, [ws.registrosNc]);

  const countInGroup = (grp?: string) => {
    if (!grp) return 1;
    return ws.registrosNc.filter((r) => r.grupo_relacao === grp).length;
  };

  // Por padrão seleciona a última ocorrência adicionada que ainda tenha vaga (< 2 fotos)
  const defaultTarget = useMemo(() => {
    for (let i = ocorrenciasBase.length - 1; i >= 0; i--) {
      if (countInGroup(ocorrenciasBase[i].grupo_relacao) < 2) {
        return ocorrenciasBase[i];
      }
    }
    return ocorrenciasBase[ocorrenciasBase.length - 1] || null;
  }, [ocorrenciasBase, ws.registrosNc]);

  const [selectedTargetKey, setSelectedTargetKey] = useState<string>(
    defaultTarget
      ? `${defaultTarget["ID da Fiscalização"]}__${defaultTarget["Nº"]}`
      : ""
  );

  const targetNc = useMemo(() => {
    return (
      ocorrenciasBase.find(
        (nc) =>
          `${nc["ID da Fiscalização"]}__${nc["Nº"]}` === selectedTargetKey
      ) || null
    );
  }, [ocorrenciasBase, selectedTargetKey]);

  const fotosUsadasSet = useMemo(() => {
    const set = new Set<string>();
    ws.registrosNc.forEach((nc) => {
      if (nc.Foto) set.add(nc.Foto.trim().toLowerCase());
    });
    return set;
  }, [ws.registrosNc]);

  // Lista estrita de fotos disponíveis para relacionamento (não pode ser a foto da NC alvo nem foto já cadastrada em outra NC)
  const fotosDisponiveis = useMemo(() => {
    return ws.photos.filter((p) => {
      const nameLower = p.name.trim().toLowerCase();
      if (targetNc && nameLower === targetNc.Foto.trim().toLowerCase()) return false;
      return !fotosUsadasSet.has(nameLower);
    });
  }, [ws.photos, targetNc, fotosUsadasSet]);

  const defaultSecondPhoto = useMemo(() => {
    if (
      initialPhotoName &&
      !fotosUsadasSet.has(initialPhotoName.trim().toLowerCase()) &&
      (!targetNc || initialPhotoName !== targetNc.Foto)
    ) {
      return initialPhotoName;
    }
    return fotosDisponiveis[0]?.name || "";
  }, [initialPhotoName, targetNc, fotosDisponiveis, fotosUsadasSet]);

  const [foto2Name, setFoto2Name] = useState<string>(defaultSecondPhoto);

  useEffect(() => {
    if (fotosDisponiveis.length > 0) {
      if (!foto2Name || !fotosDisponiveis.some((p) => p.name === foto2Name)) {
        setFoto2Name(fotosDisponiveis[0].name);
      }
    } else {
      setFoto2Name("");
    }
  }, [fotosDisponiveis]);
  const [trecho2, setTrecho2] = useState<string>(targetNc?.Trecho || "");
  const [obs2, setObs2] = useState<string>(
    isMonitoring
      ? targetNc?.["Legenda da Foto"] || targetNc?.Observações || ""
      : targetNc?.Observações || ""
  );
  const [situacao2, setSituacao2] = useState<SituacaoNC>(
    targetNc?.Situação || "Pendente"
  );

  const baseSiglasList = useMemo(() => {
    if (!targetNc) return [];
    const val = targetNc["Não Conformidade"] || targetNc["Ponto de Atenção"] || "";
    return val
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
  }, [targetNc]);

  const [tipo2, setTipo2] = useState<"Não Conformidade" | "Ponto de Atenção">("Não Conformidade");
  const [siglas2, setSiglas2] = useState<string[]>([]);
  const [direcaoFaixa2, setDirecaoFaixa2] = useState<string>("Direita");
  const [codificacao2, setCodificacao2] = useState<string>("");

  useEffect(() => {
    if (targetNc) {
      const isBasePa = Boolean(targetNc["Ponto de Atenção"] && !targetNc["Não Conformidade"]);
      setTipo2(isBasePa ? "Ponto de Atenção" : "Não Conformidade");
      const sList = (targetNc["Não Conformidade"] || targetNc["Ponto de Atenção"] || "")
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
      setSiglas2(sList);
      setDirecaoFaixa2(targetNc["Direção (faixa)"] || "Direita");
      setCodificacao2("");
      setTrecho2(targetNc.Trecho || "");
      setObs2(
        isMonitoring
          ? targetNc["Legenda da Foto"] || targetNc.Observações || ""
          : targetNc.Observações || ""
      );
      setSituacao2(targetNc.Situação || "Pendente");
    }
  }, [targetNc, isMonitoring]);

  const siglasMudaram = useMemo(() => {
    const a = [...siglas2].sort().join(",");
    const b = [...baseSiglasList].sort().join(",");
    return a !== b;
  }, [siglas2, baseSiglasList]);

  const proximaSugerida = useMemo(() => {
    if (!targetNc) return "";
    return derivarProximaCodificacao(
      targetNc.Codificação || targetNc.Identificação || ""
    );
  }, [targetNc]);

  const foto1Obj = ws.photos.find((p) => p.name === targetNc?.Foto) || null;
  const foto2Obj = ws.photos.find((p) => p.name === foto2Name) || null;
  const jaTemDuas = targetNc ? countInGroup(targetNc.grupo_relacao) >= 2 : false;

  const handleConfirm = (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetNc) {
      toast.error("Selecione uma ocorrência base para relacionar.");
      return;
    }
    if (!foto2Name) {
      toast.error("Selecione a 2ª foto para relacionar.");
      return;
    }
    if (fotosUsadasSet.has(foto2Name.trim().toLowerCase())) {
      toast.error(
        "Esta foto já está cadastrada em uma ocorrência e não pode ser relacionada como 2ª foto."
      );
      return;
    }
    if (jaTemDuas) {
      toast.error(
        "Esta ocorrência já atingiu o limite máximo de 2 fotos relacionadas."
      );
      return;
    }

    const res = relacionarFotoComNc({
      targetIdFiscalizacao: targetNc["ID da Fiscalização"],
      targetNumero: targetNc["Nº"],
      fotoName: foto2Name,
      trecho: tipoRelatorio !== "SOCICAM" ? trecho2.trim() : "",
      observacoes: isMonitoring ? targetNc.Observações : obs2.trim(),
      legendaDaFoto: isMonitoring ? obs2.trim() : undefined,
      situacao: isMonitoring ? situacao2 : targetNc.Situação,
      tipoRegistro: tipoRelatorio === "CRA" && !isMonitoring ? tipo2 : "Não Conformidade",
      siglas: siglas2,
      direcaoFaixa: tipoRelatorio === "CRA" ? direcaoFaixa2 : undefined,
      codificacao: codificacao2.trim() || undefined,
    });

    if (!res.ok) {
      toast.error(res.error || "Não foi possível relacionar a foto.");
      return;
    }

    toast.success(
      `Foto '${foto2Name}' relacionada lado a lado com o Item #${targetNc["Nº"]}!`
    );
    onClose();
  };

  return createPortal(
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-md"
      role="dialog"
      aria-modal="true"
    >
      <div className="flex max-h-[92vh] w-full max-w-3xl flex-col overflow-hidden rounded-[28px] border border-slate-700/30 bg-white shadow-2xl animate-in fade-in zoom-in-95 duration-150">
        {/* Topo Dark Executivo com Badge de Ícone */}
        <div className="flex items-center justify-between border-b border-slate-800 bg-[#0b1728] px-6 py-4 text-white">
          <div className="flex items-center gap-3 min-w-0">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-blue-600 text-white shadow-sm">
              <Link2 className="h-4 w-4" />
            </div>
            <div>
              <h3 className="truncate text-sm font-bold tracking-wide">
                Relacionar 2ª Foto a uma Ocorrência
              </h3>
              <p className="text-[11px] text-slate-400">
                Posiciona 2 fotos lado a lado no mesmo quadro do Memorial Fotográfico
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1 text-slate-400 hover:bg-white/10 hover:text-white transition"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleConfirm} className="space-y-5 overflow-y-auto p-6">
          {ocorrenciasBase.length === 0 ? (
            <div className="rounded-xl border border-border bg-secondary/50 p-6 text-center text-sm text-muted-foreground">
              Cadastre ao menos uma ocorrência primeiro para poder relacionar uma
              2ª foto.
            </div>
          ) : (
            <>
              <div>
                <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                  1. Selecione a Ocorrência Principal (1ª Foto)
                </label>
                <select
                  value={selectedTargetKey}
                  onChange={(e) => setSelectedTargetKey(e.target.value)}
                  className={modalInputCls}
                >
                  {ocorrenciasBase.map((nc) => {
                    const key = `${nc["ID da Fiscalização"]}__${nc["Nº"]}`;
                    const qtd = countInGroup(nc.grupo_relacao);
                    const labelDesc =
                      nc["Não Conformidade"] ||
                      nc["Ponto de Atenção"] ||
                      nc.Identificação ||
                      "Sem sigla";
                    return (
                      <option key={key} value={key}>
                        Item #{nc["Nº"]} ({nc["ID da Fiscalização"]}) —{" "}
                        {nc.Identificação ? `${nc.Identificação} · ` : ""}
                        {labelDesc}{" "}
                        {qtd >= 2 ? "[JÁ POSSUI 2 FOTOS]" : "[Disponível]"}
                      </option>
                    );
                  })}
                </select>
              </div>

              {jaTemDuas && (
                <div className="flex items-center gap-2 rounded-xl border border-pa/40 bg-pa-soft p-3 text-xs font-medium text-pa">
                  <AlertTriangle className="h-4 w-4 shrink-0" />
                  Esta ocorrência já possui 2 fotos relacionadas (limite máximo
                  por quadro fotográfico no Word). Escolha outra ocorrência
                  acima.
                </div>
              )}

              {/* Comparativo visual lado a lado igual ao documento Word */}
              <div className="grid gap-4 sm:grid-cols-2">
                {/* Coluna Esquerda: 1ª Foto já salva */}
                <div className="rounded-xl border border-border bg-secondary/40 p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-bold uppercase tracking-wide text-slate-blue">
                      Coluna Esquerda · 1ª Foto
                    </span>
                    <span className="rounded-md bg-primary px-2 py-0.5 font-mono text-[10px] font-semibold text-primary-foreground">
                      Foto #{String(targetNc?.["Nº"] || 1).padStart(2, "0")}
                    </span>
                  </div>

                  <div className="aspect-[4/3] w-full overflow-hidden rounded-lg border border-border bg-navy-2 grid place-items-center">
                    {foto1Obj ? (
                      <img
                        src={foto1Obj.previewUrl}
                        alt={foto1Obj.name}
                        className="h-full w-full object-cover"
                      />
                    ) : (
                      <span className="text-xs text-primary-foreground/60">
                        {targetNc?.Foto || "Sem foto"}
                      </span>
                    )}
                  </div>

                  <div className="space-y-1 text-xs">
                    <div>
                      <span className="font-semibold text-slate-blue">
                        Codificação / Siglas:{" "}
                      </span>
                      <span className="font-mono">
                        {targetNc?.Identificação || "—"}
                      </span>{" "}
                      (
                      {targetNc?.["Não Conformidade"] ||
                        targetNc?.["Ponto de Atenção"] ||
                        "—"}
                      )
                    </div>
                    {tipoRelatorio !== "SOCICAM" && (
                      <div>
                        <span className="font-semibold text-slate-blue">
                          Pista / Trecho:{" "}
                        </span>
                        {targetNc?.Pista || "—"} · {targetNc?.Trecho || "—"}
                        {tipoRelatorio === "CRA" &&
                        targetNc?.["Direção (faixa)"]
                          ? ` (${targetNc["Direção (faixa)"]})`
                          : ""}
                      </div>
                    )}
                    <div className="text-muted-foreground italic">
                      “{targetNc?.Observações || "Sem observações"}”
                    </div>
                  </div>
                </div>

                {/* Coluna Direita: 2ª Foto sendo relacionada */}
                <div className="rounded-xl border-2 border-accent/60 bg-card p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-bold uppercase tracking-wide text-accent">
                      Coluna Direita · 2ª Foto Relacionada
                    </span>
                    <span className="rounded-md bg-accent px-2 py-0.5 font-mono text-[10px] font-semibold text-accent-foreground">
                      Nova Evidência
                    </span>
                  </div>

                  <div className="aspect-[4/3] w-full overflow-hidden rounded-lg border border-border bg-navy-2 grid place-items-center">
                    {foto2Obj ? (
                      <img
                        src={foto2Obj.previewUrl}
                        alt={foto2Obj.name}
                        className="h-full w-full object-cover"
                      />
                    ) : (
                      <span className="text-xs text-primary-foreground/60">
                        Selecione uma foto abaixo
                      </span>
                    )}
                  </div>

                  <div>
                    <label className="mb-1 block text-[11px] font-semibold uppercase tracking-wide text-slate-blue">
                      Escolher 2ª Foto (Disponíveis: {fotosDisponiveis.length})
                    </label>
                    {fotosDisponiveis.length === 0 ? (
                      <div className="rounded-xl border border-amber-300 bg-amber-50/90 p-2.5 text-xs text-amber-950">
                        <AlertTriangle className="h-4 w-4 inline mr-1 text-amber-600" />
                        Todas as fotos do lote já foram cadastradas em ocorrências. Não há fotos órfãs disponíveis para relacionamento.
                      </div>
                    ) : (
                      <select
                        value={foto2Name}
                        onChange={(e) => setFoto2Name(e.target.value)}
                        className={modalInputCls}
                      >
                        {fotosDisponiveis.map((p) => {
                          const origIdx = ws.photos.findIndex((ph) => ph.name === p.name);
                          return (
                            <option key={p.id} value={p.name}>
                              Foto {String(origIdx >= 0 ? origIdx + 1 : 1).padStart(2, "0")} — {p.name}
                            </option>
                          );
                        })}
                      </select>
                    )}
                  </div>

                  {/* Tipo de Registro (NC vs PA para CRA Fiscalização) */}
                  {tipoRelatorio === "CRA" && !isMonitoring && (
                    <div>
                      <label className="mb-1 block text-[11px] font-semibold uppercase tracking-wide text-slate-blue">
                        Tipo de Registro da 2ª Foto
                      </label>
                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => setTipo2("Não Conformidade")}
                          className={modalPill(tipo2 === "Não Conformidade")}
                        >
                          Não Conformidade
                        </button>
                        <button
                          type="button"
                          onClick={() => setTipo2("Ponto de Atenção")}
                          className={modalPill(tipo2 === "Ponto de Atenção")}
                        >
                          Ponto de Atenção
                        </button>
                      </div>
                    </div>
                  )}

                  {/* Direção / Faixa da 2ª Foto (CRA) */}
                  {tipoRelatorio === "CRA" && (
                    <div>
                      <label className="mb-1 block text-[11px] font-semibold uppercase tracking-wide text-slate-blue">
                        Direção / Faixa da 2ª Foto
                      </label>
                      <div className="grid grid-cols-2 gap-1.5 rounded-lg border border-input bg-secondary/60 p-1">
                        {(["Direita", "Esquerda"] as const).map((dir) => (
                          <button
                            key={dir}
                            type="button"
                            onClick={() => setDirecaoFaixa2(dir)}
                            className={`rounded-md py-1 text-xs font-semibold transition ${
                              direcaoFaixa2 === dir
                                ? "bg-primary text-primary-foreground shadow-sm"
                                : "text-muted-foreground hover:text-foreground"
                            }`}
                          >
                            {dir}
                          </button>
                        ))}
                      </div>
                      {targetNc?.["Direção (faixa)"] &&
                        targetNc["Direção (faixa)"].toLowerCase().includes("esq") !==
                          direcaoFaixa2.toLowerCase().includes("esq") && (
                          <div className="mt-1.5 flex items-center gap-1.5 rounded-lg border border-sky-400/30 bg-sky-500/10 p-2 text-[11px] font-medium text-sky-700 dark:text-sky-300">
                            <span>
                              <b>Faixa Combinada:</b> Como uma foto é da{" "}
                              {targetNc["Direção (faixa)"]} e a outra da{" "}
                              {direcaoFaixa2}, a legenda de ambas terá a sigla{" "}
                              <b>FED</b> e no Quadro constará{" "}
                              <b>Esquerda e Direita</b>.
                            </span>
                          </div>
                        )}
                    </div>
                  )}

                  {/* Codificação da 2ª Foto */}
                  <div>
                    <label className="mb-1 block text-[11px] font-semibold uppercase tracking-wide text-slate-blue">
                      Codificação da 2ª Foto (opcional)
                    </label>
                    <input
                      type="text"
                      value={codificacao2}
                      onChange={(e) => setCodificacao2(e.target.value)}
                      placeholder={
                        proximaSugerida
                          ? `Em branco = auto-incrementar (${proximaSugerida})`
                          : `Em branco = herdar anterior (${targetNc?.Identificação || "—"})`
                      }
                      className={`${modalInputCls} font-mono text-xs`}
                    />
                  </div>
                </div>
              </div>

              {/* Seleção de Siglas da 2ª Foto */}
              {!isMonitoring && (
                <div className="rounded-xl border border-border bg-secondary/30 p-4 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold uppercase tracking-wide text-slate-blue">
                      Siglas da 2ª Foto ({tipoRelatorio})
                    </span>
                    <span className="text-[11px] text-muted-foreground font-mono">
                      {siglas2.length} selecionada(s)
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-1.5 max-h-32 overflow-y-auto p-1">
                    {optionsNc.map((s) => {
                      const d = mapSiglas[s] || s;
                      const isSel = siglas2.includes(s);
                      return (
                        <button
                          key={s}
                          type="button"
                          title={d}
                          onClick={() =>
                            setSiglas2((prev) =>
                              prev.includes(s)
                                ? prev.filter((x) => x !== s)
                                : [...prev, s]
                            )
                          }
                          className={modalPill(isSel)}
                        >
                          <b>{s}</b>
                        </button>
                      );
                    })}
                  </div>
                  {siglas2.length > 0 && (
                    <div className="text-[11px] text-muted-foreground italic bg-card/60 p-2 rounded-lg border border-border/60">
                      {siglas2.map((s) => `${s}: ${mapSiglas[s] || s}`).join(" · ")}
                    </div>
                  )}
                </div>
              )}

              {/* Banner Informativo sobre a Relação das Fotos no Relatório Word */}
              {isCraFisc && (
                <div
                  className={`rounded-xl border p-3.5 text-xs flex items-center gap-3 shadow-xs ${
                    !siglasMudaram
                      ? "border-amber-300 bg-amber-50/90 text-amber-950"
                      : "border-orange-300 bg-orange-50/90 text-orange-950"
                  }`}
                >
                  {!siglasMudaram ? (
                    <>
                      <Link2 className="h-4 w-4 shrink-0 text-amber-600" />
                      <div>
                        <span className="font-bold text-amber-950">Mesmas Siglas Mantidas:</span> A 2ª foto será agrupada sob a mesma linha e codificação ({codificacao2.trim() || targetNc?.Identificação || "—"}) no Quadro de Não Conformidades (relação 1:1).
                      </div>
                    </>
                  ) : (
                    <>
                      <AlertTriangle className="h-4 w-4 shrink-0 text-orange-600" />
                      <div>
                        <span className="font-bold text-orange-950">Siglas Diferentes Detectadas:</span> No Quadro será gerada uma codificação para cada sigla (Linha 1: {targetNc?.Identificação || "—"} | Linha 2: {codificacao2.trim() || proximaSugerida}) e as fotos ficarão relacionadas com colunas de registro fotográfico mescladas no Word.
                      </div>
                    </>
                  )}
                </div>
              )}

              {/* Campos específicos da 2ª foto */}
              <div className="grid gap-4 sm:grid-cols-2">
                {tipoRelatorio !== "SOCICAM" && (
                  <div>
                    <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                      Trecho / KM da 2ª Foto
                    </label>
                    <input
                      type="text"
                      value={trecho2}
                      onChange={(e) => setTrecho2(e.target.value)}
                      placeholder="Ex: KM 29,08 - 29,14"
                      className={modalInputCls}
                    />
                  </div>
                )}

                {isMonitoring && (
                  <div>
                    <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                      Situação
                    </label>
                    <select
                      value={situacao2}
                      onChange={(e) =>
                        setSituacao2(e.target.value as SituacaoNC)
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
                )}

                <div
                  className={
                    tipoRelatorio === "SOCICAM" && !isMonitoring
                      ? "sm:col-span-2"
                      : tipoRelatorio !== "SOCICAM" && !isMonitoring
                      ? "sm:col-span-1"
                      : "sm:col-span-2"
                  }
                >
                  <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                    {isMonitoring
                      ? "Legenda da 2ª Foto Atual"
                      : "Observações / Legenda da 2ª Foto"}
                  </label>
                  <input
                    type="text"
                    value={obs2}
                    onChange={(e) => setObs2(e.target.value)}
                    placeholder="Descrição exibida abaixo da 2ª foto no relatório..."
                    className={modalInputCls}
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 border-t border-border pt-4">
                <button
                  type="button"
                  onClick={onClose}
                  className="rounded-xl border border-slate-300 bg-white px-4 py-2 text-xs font-semibold text-slate-700 shadow-xs hover:bg-slate-50 hover:text-slate-900 hover:border-slate-400 active:scale-[0.98] transition-all"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={!targetNc || !foto2Name || jaTemDuas || fotosDisponiveis.length === 0}
                  className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-amber-500 via-amber-600 to-amber-700 px-5 py-2 text-xs font-bold text-stone-950 shadow-md shadow-amber-500/20 hover:brightness-105 active:scale-[0.98] transition-all disabled:opacity-40 disabled:pointer-events-none"
                >
                  <Link2 className="h-4 w-4" />
                  Confirmar Relação de Fotos
                </button>
              </div>
            </>
          )}
        </form>
      </div>
    </div>,
    document.body
  );
};

/* -------------------------------------------------------------------------- */
/* 6. MODAL CONFIRMAR EXCLUSÃO EM LOTE                                        */
/* -------------------------------------------------------------------------- */
