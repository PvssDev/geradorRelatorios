# Top 10 Code Smells do Projeto — Auditoria Técnica

Documento de governança técnica com o levantamento dos **10 principais *code smells*** identificados no repositório **Gerador de Relatórios (ARPE)**, seus impactos em **SOLID / Manutenibilidade / LGPD** e o direcionamento de refatoração.

> [!NOTE]
> **Conformidade LGPD (Lei nº 13.709/2018):** Este documento contém exclusivamente metadados técnicos de arquitetura e engenharia de software (nomes de arquivos, métricas e padrões de código). Não há exposição de dados pessoais, matrículas, CPFs, segredos ou evidências fotográficas de terceiros.

---

## 🏆 Top 10 Code Smells

| # | Code Smell | Onde está (Evidência Original) | Por que é um problema | Direção de Refatoração | Status |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **1** | **God Store (Arquivo Monolítico)** | `frontend/src/store/useReportStore.ts` (1.848+ linhas) | Misturava catálogos (`responsaveis`, `coordenadores`, `contratos`), estado de UI (`autoAdvanceActive`), manipulação de `blob:`, ordenação natural, sessões por ID e regras de codificação das 6 modalidades no mesmo arquivo. | Fatiar em *slices* (`catalogSlice`, `navigationSlice`, `sessionMediaSlice`, `recordsSlice`) e mover funções puras para `domain/`. | ✅ **Resolvido** |
| **2** | **God Components na UI** | `FiscalizacaoForm.tsx` (1.216+ linhas, 12 `useState`), `RegistroNcForm.tsx` (1.083+ linhas), `PhotoCarouselPanel.tsx` (881+ linhas) | Componentes gigantes acumulavam lógica de estado, validação, dropdowns e renderização condicional de 6 modalidades, dificultando manutenção e revisão. | Quebrar em subcomponentes focados (`carousel/`, `registro/`, `AnchoredDropdown`, `fiscalizacaoDateUtils`). | ✅ **Mitigado** |
| **3** | **Cascatas Ternárias por Concessão (Violação OCP)** | `FiscalizacaoForm.tsx` e `RegistroNcForm.tsx` | Regras de `CRA`, `CRC` e `SOCICAM` espalhadas em `tipoRelatorio === "CRA" ? ... : tipoRelatorio === "CRC" ? ... : ...`. Padrão propenso a regressões ao adicionar comportamento em uma concessão. | Substituir por tabela declarativa `CONCESSION_CONFIG[tipoRelatorio]`. | ⏳ Pendente |
| **4** | **Duplicação de Catálogos Back ↔ Front** | `backend/src/server/main.py` (`#L45-L64`) e `catalogSlice.ts` (antes `useReportStore.ts`) | `BASE_NC_OPTIONS`, `LOCAIS_SOCICAM` e `MAP_SIGLAS` duplicados nos dois lados; alterar em um sem atualizar o outro gera divergência silenciosa. | Manter o endpoint `/api/config/bootstrap` como única fonte de verdade. | ⏳ Pendente |
| **5** | **Uso Excessivo de `any` (Perda de Type Safety)** | `frontend/src/services/localDirectoryStorage.ts` (~19 ocorrências de `as any` / `payload: any`) e `Sidebar.tsx` (`catch (err: any)`) | Oculta erros de schema ao ler `estado.json` / `index.json` e enfraquece a checagem do TypeScript na File System Access API. | Tipar `EstadoJsonPayload`, `IndexJsonPayload`, interfaces da File System API e usar `catch (err: unknown)`. | ⏳ Pendente |
| **6** | **Engolimento de Exceções (`except Exception:`)** | `backend/src/reports/*.py`, `image_service.py`, `media_storage_service.py`, `database/manager.py` (35+ blocos) | Muitos blocos capturam `Exception` genericamente e ignoram ou retornam vazio sem log adequado, mascarando falhas reais de I/O, imagem ou XML. | Capturar exceções específicas e logar com `logging` (sem expor dados pessoais — LGPD). | ⏳ Pendente |
| **7** | **Seções Word Monolíticas (Mistura Regra + XML)** | `finalizacao.py` (839 linhas), `cra_rules.py` (655 linhas), `monitoramento_utils.py` (525 linhas), `quadros.py` (504 linhas) | Lógica condicional de negócio convive com manipulação de XML/OxmlElement do `python-docx`, dificultando testes unitários puros. | Mover cálculos/textos puros para `core/rules/` e deixar `sections/` apenas renderizando `.docx`. | ⏳ Pendente |
| **8** | **Código Legado / Morto da Era Desktop & Streamlit** | `backend/src/report.py` (`#L21-L28`, `#L231-L237`), `utils.py` (451 linhas), `main.spec` | Fallbacks para PyInstaller (`sys.executable`), `modelo_base.xlsx` e `capa_1.png`/`capa_2.jpeg` aumentam ruído cognitivo e manutenção desnecessária. | Remover caminhos legados não utilizados e centralizar resolução de assets. | ⏳ Pendente |
| **9** | **CORS Permissivo + Persistência JSON Efêmera** | `backend/src/server/main.py` (`#L72-L78`: `allow_origins=["*"]` + `allow_credentials=True`) e `backend/src/database/*.json` | Combinação `allow_origins=["*"]` + `allow_credentials=True` é insegura para produção separada; JSONs locais se perdem em containers/serverless efêmeros. | Restringir `ALLOWED_ORIGINS` por ambiente e usar Volume Persistente ou banco quando separar o backend. | ⏳ Pendente |
| **10** | **Ausência de Testes Automatizados no Frontend** | `frontend/src/` (sem suíte `vitest` / `@testing-library/react`) | Regras críticas de estado (isolamento `sessionsById`, trava das 2 fotos, auto-avanço circular, deduplicação `nome(1)`) dependem apenas de `vite build` e teste manual. | Introduzir **Vitest** com testes BDD/unitários para funções puras do store e `localDirectoryStorage`. | ⏳ Pendente |

---

## 💡 Priorização Recomendada

1. **Curto prazo:** **#10** (Testes Vitest nas funções puras de `store/domain/`), **#5** (Tipar `localDirectoryStorage.ts`) e **#3** (Tabela declarativa por concessão).
2. **Médio prazo:** **#6** (Substituir `except Exception:` silenciosos por logging estruturado) e **#7** (Separar regras puras da geração XML em `sections/`).
3. **Na separação do Backend:** **#9** (CORS restrito + Volume Persistente), **#4** (Fonte única de catálogos) e **#8** (Limpeza de código legado PyInstaller/Streamlit).

