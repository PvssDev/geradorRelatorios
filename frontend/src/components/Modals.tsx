import React, { useEffect, useMemo, useState } from "react";
import {
  X,
  Plus,
  Trash2,
  Save,
  Users,
  ShieldCheck,
  Tag,
  Edit3,
  Link2,
  Images,
  Search,
  CheckCircle2,
  AlertTriangle,
  FileText,
} from "lucide-react";
import { toast } from "sonner";
import { useReportStore } from "../store/useReportStore";
import {
  saveContratosApi,
  saveCoordenadoresApi,
  saveCustomNcsApi,
  saveResponsaveisApi,
} from "../services/api";
import { obterTermosUI, SituacaoNC } from "../types/report.types";

const modalInputCls =
  "w-full rounded-lg border border-input bg-secondary/60 px-3 py-2 text-sm text-foreground outline-none focus:border-ring focus:ring-2 focus:ring-ring/20";

const modalPill = (on: boolean) =>
  `rounded-full border px-3 py-1 text-xs font-medium transition ${
    on
      ? "border-accent bg-accent text-accent-foreground"
      : "border-border bg-card text-muted-foreground hover:border-accent/50"
  }`;

/* -------------------------------------------------------------------------- */
/* 1. MODAL GERENCIAR PESSOAL RESPONSÁVEL / COORDENADORES                     */
/* -------------------------------------------------------------------------- */
export const StaffManagerModal: React.FC<{
  mode: "responsaveis" | "coordenadores";
  onClose: () => void;
}> = ({ mode, onClose }) => {
  const { responsaveis, coordenadores, setResponsaveis, setCoordenadores } =
    useReportStore();

  const isResp = mode === "responsaveis";
  const items = isResp ? responsaveis : coordenadores;

  const [nome, setNome] = useState("");
  const [matricula, setMatricula] = useState("");
  const [funcao, setFuncao] = useState(
    isResp
      ? "Analista de Regulação"
      : "Coordenador(a) de Transportes e Rodovias"
  );

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!nome.trim() || !matricula.trim() || !funcao.trim()) {
      toast.error("Preencha Nome, Matrícula e Função/Cargo.");
      return;
    }
    const exists = items.some(
      (i) => i.nome.trim().toLowerCase() === nome.trim().toLowerCase()
    );
    if (exists) {
      toast.warning("Este nome já está cadastrado.");
      return;
    }
    const nextList = [
      ...items,
      {
        nome: nome.trim(),
        matricula: matricula.trim(),
        funcao: funcao.trim(),
      },
    ];
    if (isResp) {
      setResponsaveis(nextList);
      await saveResponsaveisApi(nextList).catch(() => {});
    } else {
      setCoordenadores(nextList);
      await saveCoordenadoresApi(nextList).catch(() => {});
    }
    toast.success(`'${nome.trim()}' adicionado com sucesso!`);
    setNome("");
    setMatricula("");
  };

  const handleRemove = async (idx: number) => {
    const nextList = items.filter((_, i) => i !== idx);
    if (isResp) {
      setResponsaveis(nextList);
      await saveResponsaveisApi(nextList).catch(() => {});
    } else {
      setCoordenadores(nextList);
      await saveCoordenadoresApi(nextList).catch(() => {});
    }
    toast.info("Item removido.");
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-foreground/60 p-4 backdrop-blur-[1px]"
      role="dialog"
      aria-modal="true"
    >
      <div className="flex max-h-[88vh] w-full max-w-lg flex-col overflow-hidden rounded-2xl border border-border bg-card shadow-card-lg">
        <div className="flex items-center justify-between border-b border-border bg-navy-gradient px-5 py-4 text-primary-foreground">
          <h3 className="flex items-center gap-2 text-base font-bold">
            {isResp ? (
              <Users className="h-5 w-5 text-accent" />
            ) : (
              <ShieldCheck className="h-5 w-5 text-accent" />
            )}
            {isResp
              ? "Gerenciar Pessoal Responsável"
              : "Gerenciar Coordenadores"}
          </h3>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1.5 text-primary-foreground/80 hover:bg-white/10 hover:text-primary-foreground"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="space-y-4 overflow-y-auto p-5">
          <form onSubmit={handleAdd} className="space-y-3">
            <div>
              <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                Nome Completo *
              </label>
              <input
                type="text"
                value={nome}
                onChange={(e) => setNome(e.target.value)}
                placeholder="Digite o nome completo..."
                className={modalInputCls}
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                  Matrícula *
                </label>
                <input
                  type="text"
                  value={matricula}
                  onChange={(e) => setMatricula(e.target.value)}
                  placeholder="Ex: 40672015/01"
                  className={modalInputCls}
                />
              </div>
              <div>
                <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                  Função / Cargo *
                </label>
                <input
                  type="text"
                  value={funcao}
                  onChange={(e) => setFuncao(e.target.value)}
                  className={modalInputCls}
                />
              </div>
            </div>
            <button
              type="submit"
              className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-xs font-semibold text-primary-foreground hover:bg-navy-2 transition"
            >
              <Plus className="h-4 w-4" />
              Adicionar {isResp ? "Responsável" : "Coordenador"}
            </button>
          </form>

          <div className="border-t border-border pt-3">
            <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Cadastrados ({items.length})
            </h4>
            <div className="space-y-2">
              {items.map((item, idx) => (
                <div
                  key={`${item.nome}_${idx}`}
                  className="flex items-center justify-between gap-2 rounded-xl border border-border bg-secondary/40 p-2.5"
                >
                  <div>
                    <p className="text-xs font-semibold text-foreground">
                      {item.nome}
                    </p>
                    <p className="text-[11px] text-muted-foreground">
                      {item.funcao} • Matrícula: {item.matricula}
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleRemove(idx)}
                    className="rounded-md p-1.5 text-nc hover:bg-nc-soft"
                    title="Remover"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

/* -------------------------------------------------------------------------- */
/* 2. MODAL GERENCIAR CONTRATOS                                               */
/* -------------------------------------------------------------------------- */
export const ContratosManagerModal: React.FC<{
  onSelectContrato?: (contrato: string) => void;
  onClose: () => void;
}> = ({ onSelectContrato, onClose }) => {
  const { contratos, setContratos } = useReportStore();
  const [novoContrato, setNovoContrato] = useState("");

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    const clean = novoContrato.trim();
    if (!clean) {
      toast.error("Informe o número do contrato.");
      return;
    }
    if (contratos.includes(clean)) {
      toast.warning("Este contrato já está cadastrado.");
      return;
    }
    const next = [...contratos, clean];
    setContratos(next);
    await saveContratosApi(next).catch(() => {});
    if (onSelectContrato) onSelectContrato(clean);
    toast.success(`Contrato '${clean}' adicionado!`);
    setNovoContrato("");
  };

  const handleRemove = async (idx: number) => {
    const next = contratos.filter((_, i) => i !== idx);
    setContratos(next);
    await saveContratosApi(next).catch(() => {});
    toast.info("Contrato removido.");
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-foreground/60 p-4 backdrop-blur-[1px]"
      role="dialog"
      aria-modal="true"
    >
      <div className="flex max-h-[85vh] w-full max-w-md flex-col overflow-hidden rounded-2xl border border-border bg-card shadow-card-lg">
        <div className="flex items-center justify-between border-b border-border bg-navy-gradient px-5 py-4 text-primary-foreground">
          <h3 className="flex items-center gap-2 text-base font-bold">
            <FileText className="h-5 w-5 text-accent" />
            Gerenciar Contratos
          </h3>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1.5 text-primary-foreground/80 hover:bg-white/10 hover:text-primary-foreground"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="space-y-4 overflow-y-auto p-5">
          <form onSubmit={handleAdd} className="space-y-3">
            <div>
              <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                Número do Novo Contrato
              </label>
              <input
                type="text"
                value={novoContrato}
                onChange={(e) => setNovoContrato(e.target.value)}
                placeholder="Ex: CT. nº 043/2011"
                className={modalInputCls}
              />
            </div>
            <button
              type="submit"
              className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-xs font-semibold text-primary-foreground hover:bg-navy-2 transition"
            >
              <Plus className="h-4 w-4" />
              Adicionar Contrato
            </button>
          </form>

          <div className="border-t border-border pt-3">
            <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Contratos Salvos ({contratos.length})
            </h4>
            <div className="space-y-2">
              {contratos.map((c, idx) => (
                <div
                  key={`${c}_${idx}`}
                  className="flex items-center justify-between gap-2 rounded-xl border border-border bg-secondary/40 p-2.5"
                >
                  <button
                    type="button"
                    onClick={() => {
                      if (onSelectContrato) onSelectContrato(c);
                      onClose();
                    }}
                    className="flex-1 text-left font-mono text-xs font-semibold text-foreground hover:text-accent"
                  >
                    {c}
                  </button>
                  <button
                    type="button"
                    onClick={() => handleRemove(idx)}
                    className="rounded-md p-1.5 text-nc hover:bg-nc-soft"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

/* -------------------------------------------------------------------------- */
/* 3. MODAL ADICIONAR NÃO CONFORMIDADE PERSONALIZADA                          */
/* -------------------------------------------------------------------------- */
export const CustomNcModal: React.FC<{
  onSelectCallback?: (val: string) => void;
  onClose: () => void;
}> = ({ onSelectCallback, onClose }) => {
  const {
    tipoRelatorio,
    customNcs,
    customNcsSocicam,
    setCustomNcs,
    setCustomNcsSocicam,
  } = useReportStore();

  const isSocicam = tipoRelatorio === "SOCICAM";
  const currentList = isSocicam ? customNcsSocicam : customNcs;

  const [sigla, setSigla] = useState("");
  const [descricao, setDescricao] = useState("");

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    const descClean = descricao.trim();
    const siglaClean = sigla.trim().toUpperCase();
    if (!descClean) {
      toast.error("O campo 'Descrição' é obrigatório.");
      return;
    }

    const nextList = [
      ...currentList,
      { sigla: siglaClean, descricao: descClean },
    ];
    if (isSocicam) {
      setCustomNcsSocicam(nextList);
      await saveCustomNcsApi(nextList, true).catch(() => {});
    } else {
      setCustomNcs(nextList);
      await saveCustomNcsApi(nextList, false).catch(() => {});
    }

    const valToSelect = siglaClean || descClean;
    if (onSelectCallback) onSelectCallback(valToSelect);
    toast.success("Nova Não Conformidade cadastrada e selecionada!");
    onClose();
  };

  const handleDelete = async (idx: number) => {
    const nextList = currentList.filter((_, i) => i !== idx);
    if (isSocicam) {
      setCustomNcsSocicam(nextList);
      await saveCustomNcsApi(nextList, true).catch(() => {});
    } else {
      setCustomNcs(nextList);
      await saveCustomNcsApi(nextList, false).catch(() => {});
    }
    toast.info("Não Conformidade personalizada removida.");
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-foreground/60 p-4 backdrop-blur-[1px]"
      role="dialog"
      aria-modal="true"
    >
      <div className="flex max-h-[88vh] w-full max-w-lg flex-col overflow-hidden rounded-2xl border border-border bg-card shadow-card-lg">
        <div className="flex items-center justify-between border-b border-border bg-navy-gradient px-5 py-4 text-primary-foreground">
          <h3 className="flex items-center gap-2 text-base font-bold">
            <Tag className="h-5 w-5 text-accent" />
            Não Conformidades Personalizadas (
            {isSocicam ? "SOCICAM" : "Rodovias"})
          </h3>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1.5 text-primary-foreground/80 hover:bg-white/10 hover:text-primary-foreground"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="space-y-4 overflow-y-auto p-5">
          <form onSubmit={handleAdd} className="space-y-3">
            <div>
              <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                Sigla (opcional)
              </label>
              <input
                type="text"
                value={sigla}
                onChange={(e) => setSigla(e.target.value)}
                placeholder={isSocicam ? "Ex: NC01" : "Ex: ABC"}
                className={modalInputCls}
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                Descrição Completa (obrigatório) *
              </label>
              <input
                type="text"
                value={descricao}
                onChange={(e) => setDescricao(e.target.value)}
                placeholder="Digite a descrição da não conformidade..."
                className={modalInputCls}
              />
            </div>
            <button
              type="submit"
              className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-xs font-semibold text-primary-foreground hover:bg-navy-2 transition"
            >
              <Plus className="h-4 w-4" />
              Cadastrar e Selecionar
            </button>
          </form>

          <div className="border-t border-border pt-3">
            <h4 className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Adicionadas Anteriormente ({currentList.length})
            </h4>
            {currentList.length === 0 ? (
              <p className="text-xs italic text-muted-foreground">
                Nenhuma não conformidade personalizada cadastrada ainda.
              </p>
            ) : (
              <div className="space-y-2">
                {currentList.map((it, idx) => {
                  const label = it.sigla
                    ? `${it.sigla} — ${it.descricao}`
                    : it.descricao;
                  const val = it.sigla || it.descricao;
                  return (
                    <div
                      key={`${val}_${idx}`}
                      className="flex items-center justify-between gap-2 rounded-xl border border-border bg-secondary/40 p-2.5"
                    >
                      <button
                        type="button"
                        onClick={() => {
                          if (onSelectCallback) onSelectCallback(val);
                          onClose();
                        }}
                        className="flex-1 truncate text-left text-xs font-semibold text-foreground hover:text-accent"
                      >
                        {label}
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDelete(idx)}
                        className="rounded-md p-1.5 text-nc hover:bg-nc-soft"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

/* -------------------------------------------------------------------------- */
/* 4. MODAL GALERIA DE FOTOS DO LEVANTAMENTO                                  */
/* -------------------------------------------------------------------------- */
export const PhotoGalleryModal: React.FC<{ onClose: () => void }> = ({
  onClose,
}) => {
  const { getActiveWorkspace, setCarouselIndex } = useReportStore();
  const ws = getActiveWorkspace();
  const [filtro, setFiltro] = useState("");

  const fotosEmNc = useMemo(() => {
    const set = new Set<string>();
    for (const nc of ws.registrosNc) {
      if (nc.Foto) set.add(nc.Foto.trim().toLowerCase());
    }
    return set;
  }, [ws.registrosNc]);

  const filtradas = useMemo(() => {
    const q = filtro.trim().toLowerCase();
    return ws.photos
      .map((photo, index) => ({ photo, index }))
      .filter(({ photo }) => !q || photo.name.toLowerCase().includes(q));
  }, [ws.photos, filtro]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-foreground/60 p-4 backdrop-blur-[1px]"
      role="dialog"
      aria-modal="true"
    >
      <div className="flex max-h-[90vh] w-full max-w-4xl flex-col overflow-hidden rounded-2xl border border-border bg-card shadow-card-lg">
        <div className="flex items-center justify-between border-b border-border bg-navy-gradient px-5 py-4 text-primary-foreground">
          <h3 className="flex items-center gap-2 text-base font-bold">
            <Images className="h-5 w-5 text-accent" />
            Galeria de Fotos do Levantamento ({ws.photos.length} fotos)
          </h3>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1.5 text-primary-foreground/80 hover:bg-white/10 hover:text-primary-foreground"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="space-y-4 overflow-y-auto p-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <p className="text-xs text-muted-foreground">
              Clique em qualquer foto para defini-la como a foto central do
              carrossel. Fotos com selo{" "}
              <b className="text-ok">Vinculada [NC]</b> já foram adicionadas ao
              relatório.
            </p>
            <div className="relative w-full sm:w-64">
              <Search className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                value={filtro}
                onChange={(e) => setFiltro(e.target.value)}
                placeholder="Filtrar por nome..."
                className={`${modalInputCls} pl-9`}
              />
            </div>
          </div>

          {filtradas.length === 0 ? (
            <div className="rounded-xl border border-border bg-secondary/40 p-8 text-center text-sm text-muted-foreground">
              Nenhuma foto encontrada.
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
              {filtradas.map(({ photo, index }) => {
                const isCurrent = index === ws.carouselIndex;
                const inNc = fotosEmNc.has(photo.name.trim().toLowerCase());
                return (
                  <button
                    key={photo.id}
                    type="button"
                    onClick={() => {
                      setCarouselIndex(index);
                      onClose();
                    }}
                    className={`group relative overflow-hidden rounded-xl border-2 text-left transition ${
                      isCurrent
                        ? "border-accent ring-2 ring-accent/30"
                        : inNc
                        ? "border-ok/50 opacity-80 hover:opacity-100"
                        : "border-border hover:border-accent/60"
                    }`}
                  >
                    <div className="relative aspect-[4/3] w-full bg-navy-2">
                      <img
                        src={photo.previewUrl}
                        alt={photo.name}
                        className="h-full w-full object-cover"
                      />
                      <span className="absolute left-2 top-2 rounded-md bg-primary/85 px-2 py-0.5 font-mono text-[10px] font-bold text-primary-foreground">
                        #{String(index + 1).padStart(2, "0")}
                      </span>
                      {inNc && (
                        <span className="absolute right-2 top-2 inline-flex items-center gap-1 rounded-md bg-ok px-2 py-0.5 text-[10px] font-bold text-white">
                          <CheckCircle2 className="h-3 w-3" /> NC
                        </span>
                      )}
                    </div>
                    <div className="bg-card p-2">
                      <p
                        className="truncate text-xs font-semibold text-foreground"
                        title={photo.name}
                      >
                        {photo.name}
                      </p>
                      <p className="text-[10px] text-muted-foreground">
                        {isCurrent ? "Selecionada no carrossel" : "Clique para selecionar"}
                      </p>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

/* -------------------------------------------------------------------------- */
/* 5. JANELA MODAL DE RELACIONAR FOTO À OCORRÊNCIA                            */
/* -------------------------------------------------------------------------- */
export const RelacionarFotoModal: React.FC<{
  initialPhotoName?: string;
  onClose: () => void;
}> = ({ initialPhotoName, onClose }) => {
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

  const defaultSecondPhoto = useMemo(() => {
    if (
      initialPhotoName &&
      (!targetNc || initialPhotoName !== targetNc.Foto)
    ) {
      return initialPhotoName;
    }
    const other = ws.photos.find((p) => p.name !== targetNc?.Foto);
    return other?.name || initialPhotoName || ws.photos[0]?.name || "";
  }, [initialPhotoName, targetNc, ws.photos]);

  const [foto2Name, setFoto2Name] = useState<string>(defaultSecondPhoto);
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

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-foreground/60 p-4 backdrop-blur-[1px]"
      role="dialog"
      aria-modal="true"
    >
      <div className="flex max-h-[92vh] w-full max-w-3xl flex-col overflow-hidden rounded-2xl border border-border bg-card shadow-card-lg">
        <div className="flex items-center justify-between border-b border-border bg-navy-gradient px-6 py-4 text-primary-foreground">
          <div>
            <h3 className="flex items-center gap-2 text-base font-bold">
              <Link2 className="h-5 w-5 text-accent" />
              Relacionar Nova Foto à Ocorrência
            </h3>
            <p className="text-xs text-primary-foreground/75">
              Posiciona 2 fotos lado a lado no mesmo quadro do Memorial
              Fotográfico e agrupa a numeração na tabela do relatório.
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1.5 text-primary-foreground/80 hover:bg-white/10 hover:text-primary-foreground"
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
                      Escolher 2ª Foto
                    </label>
                    <select
                      value={foto2Name}
                      onChange={(e) => setFoto2Name(e.target.value)}
                      className={modalInputCls}
                    >
                      {ws.photos.map((p, idx) => (
                        <option key={p.id} value={p.name}>
                          Foto {String(idx + 1).padStart(2, "0")} — {p.name}
                          {p.name === targetNc?.Foto ? " (mesma da 1ª)" : ""}
                        </option>
                      ))}
                    </select>
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
                      placeholder={`Em branco = herdar anterior (${targetNc?.Identificação || "—"})`}
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
                  className={`rounded-xl border p-3.5 text-xs flex items-center gap-3 ${
                    !siglasMudaram
                      ? "border-accent/40 bg-accent/10 text-accent-foreground"
                      : "border-pa/40 bg-pa-soft text-pa"
                  }`}
                >
                  {!siglasMudaram ? (
                    <>
                      <Link2 className="h-4 w-4 shrink-0 text-accent" />
                      <div>
                        <span className="font-bold">Mesmas Siglas Mantidas:</span> A 2ª foto será agrupada sob a mesma linha e codificação ({codificacao2.trim() || targetNc?.Identificação || "—"}) no Quadro de Não Conformidades (relação 1:1).
                      </div>
                    </>
                  ) : (
                    <>
                      <AlertTriangle className="h-4 w-4 shrink-0" />
                      <div>
                        <span className="font-bold">Siglas Diferentes Detectadas:</span> No Quadro será gerada uma codificação para cada sigla (N para 1) e as fotos ficarão relacionadas com colunas de registro fotográfico mescladas no Word.
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
                  className="rounded-xl border border-border bg-card px-4 py-2.5 text-xs font-semibold text-foreground hover:bg-muted transition"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={!targetNc || !foto2Name || jaTemDuas}
                  className="inline-flex items-center gap-2 rounded-xl bg-amber-500 px-5 py-2.5 text-xs font-bold text-stone-950 shadow-[0_2px_0_0_#b45309] hover:bg-amber-400 active:translate-y-[1px] transition disabled:opacity-40"
                >
                  <Link2 className="h-4 w-4" />
                  Confirmar Relação de Fotos
                </button>
              </div>
            </>
          )}
        </form>
      </div>
    </div>
  );
};

/* -------------------------------------------------------------------------- */
/* 6. MODAL CONFIRMAR EXCLUSÃO EM LOTE                                        */
/* -------------------------------------------------------------------------- */
export const ConfirmDeleteModal: React.FC<{
  title: string;
  description: string;
  itemsPreview: string[];
  onConfirm: () => void;
  onClose: () => void;
}> = ({ title, description, itemsPreview, onConfirm, onClose }) => {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-foreground/60 p-4 backdrop-blur-[1px]"
      role="dialog"
      aria-modal="true"
    >
      <div className="w-full max-w-md overflow-hidden rounded-2xl border border-border bg-card shadow-card-lg">
        <div className="flex items-center justify-between border-b border-border bg-nc px-5 py-4 text-destructive-foreground">
          <h3 className="flex items-center gap-2 text-base font-bold">
            <Trash2 className="h-5 w-5" />
            {title}
          </h3>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1 text-white/80 hover:bg-white/10 hover:text-white"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="space-y-4 p-5">
          <p className="text-sm text-foreground">{description}</p>
          {itemsPreview.length > 0 && (
            <ul className="max-h-40 space-y-1 overflow-y-auto rounded-xl border border-border bg-secondary/40 p-3 text-xs font-semibold text-foreground">
              {itemsPreview.map((it, idx) => (
                <li key={idx}>• {it}</li>
              ))}
            </ul>
          )}
          <div className="rounded-xl border border-pa/30 bg-pa-soft p-3 text-xs font-medium text-pa">
            Esta ação não pode ser desfeita.
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-xl border border-border bg-card px-4 py-2 text-xs font-semibold text-foreground hover:bg-muted transition"
            >
              Cancelar
            </button>
            <button
              type="button"
              onClick={() => {
                onConfirm();
                onClose();
              }}
              className="inline-flex items-center gap-1.5 rounded-xl border border-red-500/60 bg-red-600 px-4 py-2 text-xs font-bold text-white shadow-[0_2px_0_0_#991b1b] hover:bg-red-500 active:translate-y-[1px] transition"
            >
              <Trash2 className="h-4 w-4" />
              Sim, Excluir
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

/* -------------------------------------------------------------------------- */
/* 7. MODAL EDITAR DADOS REGISTRADOS (FISCALIZAÇÕES E NCs/PAs)                */
/* -------------------------------------------------------------------------- */
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
        editLocal.trim() ||
        (tipoRelatorio === "CRA"
          ? "Rota do Atlântico"
          : tipoRelatorio === "CRC"
          ? "Sistema Viário do Paiva"
          : locaisSocicam[0]),
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
      className="fixed inset-0 z-50 flex items-center justify-center bg-foreground/60 p-4 backdrop-blur-[1px]"
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
                  <div className="grid grid-cols-3 gap-3">
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
                    <div>
                      <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                        Local
                      </label>
                      <input
                        type="text"
                        value={editLocal}
                        onChange={(e) => setEditLocal(e.target.value)}
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

                {tipoRelatorio === "CRC" && (
                  <div>
                    <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-blue">
                      Local
                    </label>
                    <input
                      type="text"
                      value={editLocal}
                      onChange={(e) => setEditLocal(e.target.value)}
                      className={modalInputCls}
                    />
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
                  className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-xs font-semibold text-primary-foreground hover:bg-navy-2 transition"
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
                    className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-xs font-semibold text-primary-foreground hover:bg-navy-2 transition"
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
