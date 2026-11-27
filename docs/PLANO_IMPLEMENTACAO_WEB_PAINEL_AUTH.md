# Plano de Implementação Web + FastAPI — Login, Aba de Painel e Integração com `geradorCampo`

> **Documento Base:** [ARQUITETURA_WEB_PAINEL_E_AUTH.md](./ARQUITETURA_WEB_PAINEL_E_AUTH.md)
> **Contrato Compartilhado com o APK:** `geradorCampo/supabase/migrations/001_init_arpe.sql`
> **Regra de Execução:** Execute **uma fase por vez** (`Fase W1` → `Fase W5`), validando `python -m pytest -q` (backend) e `npm.cmd --prefix frontend run build` (frontend) ao final de cada fase.

---

## Mapa Geral das Fases (Repositório Web `workTree`)

| Fase | Escopo Principal | Camada | Perfil Gemini |
| :---: | :--- | :--- | :---: |
| **Fase W1** | Infraestrutura Backend: Clientes Supabase/Storage, Auth Sem E-mail (Cookie `HttpOnly` + Bearer APK), Lockout, RBAC, Aprovações e CORS Fechado | `backend/src/` | **Carbon** |
| **Fase W2** | Endpoints de Sync & Handoff: Presigned PUT/GET (≤ 10 min), `vistorias_transito`, Expurgo Pós-Emissão e `historico_achados` | `backend/src/` | **Carbon** |
| **Fase W3** | Login Web (`usuario + senha`, sem e-mail), Modal "Solicitar Acesso", Guarda de Sessão e Navegação `Painel ↔ Editor` | `frontend/src/` | **Carbon** |
| **Fase W4** | Nova Aba `Painel`: Sub-abas **Recebidos do Campo** (com "Abrir no Editor" + Expurgo Pós-`.docx`), **Gráficos Históricos** e **Gestão de Acessos/Auditoria** | `frontend/src/` | **Orquestrador** |
| **Fase W5** | Auditoria OWASP Web + LGPD + Testes BDD de Integração nos 6 Estados (APK → Nuvem → Painel Web → `.docx` → Histórico) | `tests/` + `frontend/` | **Carbon** |

---

## Fase W1 — Backend FastAPI: Auth Sem E-mail, RBAC, Lockout e Hardening

> **Status: ✅ CONCLUÍDA (2026-11-26)** — `python -m pytest -q` verde, incluindo `tests/test_auth_rbac_bdd.py`.

### Arquivos Entregues
* `backend/src/core/interfaces/auth_gateway.py` — porta `IAuthGateway` (Protocol, DIP)
* `backend/src/services/supabase_gateway.py` — adaptador HTTP Supabase (+ `refresh_session`, `list_audit_logs`)
* `backend/src/services/auth_service.py` — casos de uso (`AuthService`, `AuthError`, `SessaoAutenticada`)
* `backend/src/server/dependencies/auth_deps.py` — `get_current_user`, `require_roles(...)`, `require_adm_perfil`, anti-CSRF por `Origin`
* `backend/src/server/dependencies/rate_limit.py` — rate limit por IP
* `backend/src/server/security_config.py` / `security_headers.py` — `ALLOWED_ORIGINS` fechado, CSP, `no-store`
* `backend/src/server/routers/auth_router.py` — camada HTTP enxuta
* `tests/test_auth_rbac_bdd.py`

### Endpoints Disponíveis (`/api/auth`)
| Método | Rota | Perfil |
| :--- | :--- | :--- |
| POST | `/login` (`client_type: web \| mobile`) | público |
| POST | `/refresh` (cookie no Web, `refresh_token` no corpo no APK) | público |
| GET | `/me` | autenticado |
| POST | `/logout` | público |
| POST | `/solicitar-acesso` | público |
| GET | `/solicitacoes` · POST `/solicitacoes/{id}/decidir` | `adm`, `coordenador` |
| GET/POST | `/admin/usuarios` · PUT `/admin/usuarios/{id}` | `adm` |
| POST | `/admin/usuarios/{id}/reset-senha` · `/deletar` · `/desbloquear` | `adm` (reconfirma senha) |
| GET | `/admin/audit-logs?limit=1..500` | `adm` |

### Arquivos a Criar / Alterar (planejamento original)
* **Criar:** `backend/src/services/supabase_client.py` *(entregue como `supabase_gateway.py`)*
* **Criar:** `backend/src/services/auth_service.py`
* **Criar:** `backend/src/server/dependencies/auth_deps.py`
* **Criar:** `backend/src/server/routers/auth_router.py`
* **Alterar:** `backend/src/server/main.py` *(registrar routers, fechar `ALLOWED_ORIGINS` e adicionar middleware de headers de segurança)*
* **Criar:** `tests/test_auth_rbac_bdd.py`

### Entregas Técnicas
1. **Login Dual (Web + APK):** `POST /api/auth/login` aceita `{ usuario, senha, client_type?: "web" | "mobile" }`:
   * Mapeia `usuario` → `${usuario.toLowerCase()}@arpe.internal`;
   * Verifica `bloqueado_ate` (lockout de 15 min após 5 falhas) e aplica *rate limit* por IP;
   * Para `web`: grava cookies `HttpOnly; Secure; SameSite=Strict`; para `mobile`: retorna tokens no corpo JSON para o `expo-secure-store`;
   * Registra evento em `audit_logs` (sem logar senha/token).
2. **Solicitação e Aprovação Individual:**
   * `POST /api/auth/solicitar-acesso` (bloqueia `role_solicitado == "adm"` no Pydantic e no SQL);
   * `GET /api/auth/solicitacoes` e `POST /api/auth/solicitacoes/{id}/decidir` (permitido para `adm` ou `coordenador`; exige reconfirmação de senha quando `role == "adm"`).
3. **Gestão `ADM`:** `GET /api/auth/usuarios`, `PATCH /api/auth/usuarios/{id}` (ativar/desativar/desbloquear — bloqueia alteração de `role` para `adm`) e `GET /api/auth/audit-logs`.

### Critérios de Aceite (BDD)
* **Dado** 5 senhas incorretas seguidas para um usuário, **Quando** tentar a 6ª vez, **Então** o backend retorna `429`/`423` com bloqueio de 15 min e grava o evento em `audit_logs`.
* **Dado** um `analista` autenticado tentando acessar `GET /api/auth/solicitacoes` ou `GET /api/auth/audit-logs`, **Então** o backend retorna `403 Forbidden`.
* **Dado** uma solicitação de acesso com `role_solicitado = "adm"`, **Então** a API rejeita com `422 Unprocessable Entity`.

---

## Fase W2 — Backend FastAPI: Sync Handoff, Presigned URLs e Histórico Analítico

> **Status: ✅ CONCLUÍDA (2026-11-27)** — `tests/test_sync_handoff_bdd.py` e suíte completa verdes.

### Arquivos a Criar / Alterar
* **Criar:** `backend/src/services/sync_service.py`
* **Criar:** `backend/src/server/routers/sync_router.py`
* **Criar:** `backend/src/server/routers/historico_router.py`
* **Criar:** `tests/test_sync_handoff_bdd.py`

### Entregas Técnicas
1. **Upload Seguro do APK:**
   * `POST /api/sync/presign-upload`: valida tamanho (≤ 500 KB), tipo `image/jpeg`, gera `storage_key` sanitizado (`temp-sync/{user_id}/{vistoria_id}/{uuid}.jpg`) e retorna Presigned PUT URL (≤ 10 min).
   * `POST /api/sync/vistorias`: valida payload das 6 modalidades com Pydantic e faz *upsert* em `vistorias_transito` e `vistorias_fotos_temp`.
2. **Consumo pelo Painel Web:**
   * `GET /api/sync/vistorias`: aplica filtro RBAC (`analista` vê apenas `autor_id == user.id`; `coordenador`/`adm` veem todas).
   * `GET /api/sync/vistorias/{id}/fotos-urls`: retorna Presigned GET URLs (≤ 10 min) para preview e importação no Editor Web.
3. **Conclusão, Expurgo & Histórico:**
   * `POST /api/sync/vistorias/{id}/concluir`: grava registros anônimos de NCs/PAs em `historico_achados` (idempotente por `id_vistoria`), deleta os objetos no Storage Privado + `vistorias_fotos_temp`, marca `status_handoff = 'emitida'` e grava em `audit_logs`.
   * `GET /api/historico/resumo`: retorna séries mensais, taxa de saneamento e Top NCs filtráveis por concessão, modalidade e período.

### Critérios de Aceite (BDD)
* **Dado** uma vistoria finalizada do `analista A`, **Quando** o `analista B` listar `GET /api/sync/vistorias`, **Então** a vistoria do `analista A` não aparece; **Quando** um `coordenador` listar, **Então** aparece.
* **Dado** a conclusão de uma vistoria emitida, **Quando** `POST /api/sync/vistorias/{id}/concluir` rodar, **Então** as fotos são removidas do Storage Privado e `historico_achados` recebe somente os registros estruturados sem fotos e sem PII.

---

## Fase W3 — Frontend Web: Tela de Login, Solicitar Acesso e Guarda de Sessão

### Arquivos a Criar / Alterar
* **Criar:** `frontend/src/types/auth.types.ts`
* **Criar:** `frontend/src/services/authApi.ts` *(usa `credentials: "include"` para cookies `HttpOnly`, zero `localStorage` para tokens)*
* **Criar:** `frontend/src/store/useAuthStore.ts`
* **Criar:** `frontend/src/components/auth/LoginPage.tsx`
* **Criar:** `frontend/src/components/auth/SolicitarAcessoModal.tsx`
* **Alterar:** `frontend/src/App.tsx` *(guarda de autenticação: sem sessão válida → `LoginPage`; autenticado → alternância limpa entre `Painel` e `Editor`)*
* **Alterar:** `frontend/src/components/Sidebar.tsx` *(adicionar item de navegação para aba `Painel`, exibir nome/perfil do usuário logado e botão `Sair`)*

### Critérios de Aceite (BDD)
* **Dado** um visitante sem cookie de sessão válido, **Quando** abrir o sistema Web, **Então** vê exclusivamente a tela de Login (`Usuário` + `Senha`, sem e-mail) e o link `"Solicitar Acesso"`.
* **Dado** um usuário autenticado, **Quando** recarregar a página (`F5`), **Então** `GET /api/auth/me` restaura a sessão sem expor JWT no `localStorage`.

---

## Fase W4 — Frontend Web: Nova Aba `Painel` (Recebidos do Campo, Gráficos e Gestão RBAC)

### Arquivos a Criar / Alterar
* **Criar:** `frontend/src/services/syncApi.ts`
* **Criar:** `frontend/src/components/painel/PainelPage.tsx` *(container principal com 3 sub-abas respeitando RBAC)*
* **Criar:** `frontend/src/components/painel/RecebidosCampoTab.tsx` *(filtros por 6 estados + botão **"Abrir no Editor"** + ação **"Concluir & Limpar Fotos"**)*
* **Criar:** `frontend/src/components/painel/HistoricoGraficosTab.tsx` *(gráficos SVG/Tailwind harmonizados com `concessionTheme.ts` consumindo `historico_achados`)*
* **Criar:** `frontend/src/components/painel/GestaoAcessosTab.tsx` *(fila de aprovação para `coordenador`/`adm` + usuários/lockout/`audit_logs` exclusivo `adm`)*
* **Alterar:** `frontend/src/components/SummaryAndActionsPanel.tsx` *(quando a sessão ativa tiver sido importada do Painel, exibir botão discreto pós-geração do `.docx` para confirmar conclusão, gravar no histórico e expurgar fotos temporárias)*

### Critérios de Aceite (BDD)
* **Dado** uma vistoria `SOCICAM Monitoramento` recebida do APK em `Recebidos do Campo`, **Quando** o analista clicar em **"Abrir no Editor"**, **Então** o `useReportStore` é hidratado na modalidade `SOCICAM_Monitoramento` com todas as fotos, NCs e `Recomendações à SOCICAM` prontas para gerar o `.docx`.
* **Dado** um `analista` logado na aba `Painel`, **Então** vê `Recebidos do Campo` (suas vistorias) e `Gráficos Históricos`, mas **não** vê a sub-aba `Gestão & Acessos`.

---

## Fase W5 — Auditoria OWASP Web, LGPD e Regressão dos 6 Estados

### Checklist Bloqueante de Go-Live
- [ ] **Zero e-mails** em telas ou respostas públicas do Web.
- [ ] Cookies de sessão com flags `HttpOnly`, `Secure` e `SameSite=Strict`; `localStorage` sem nenhum JWT.
- [ ] `ALLOWED_ORIGINS` restrito em produção (CORS `*` removido).
- [ ] Reconfirmação de senha exigida no Web para ações críticas do `ADM`.
- [ ] `python -m pytest -q` (incluindo os 194 testes existentes dos 6 estados + novos testes de Auth/Sync) **100% verde**.
- [ ] `npm.cmd --prefix frontend run build` **100% verde** com zero erros de TypeScript.
