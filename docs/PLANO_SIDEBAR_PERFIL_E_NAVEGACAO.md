# Plano de Implementação — Redesign do Menu Lateral (`Sidebar.tsx`) com Perfil Unificado e Nova Navegação

> **Escopo desta entrega:** **Somente modificações visuais e de navegação no menu lateral (`Sidebar.tsx`)** e utilitários de avatar/perfil no frontend Web (`workTree/frontend`). As telas/modais de destino de `Vistorias`, `Painel`, `Quadro`, `Painel ADM`, `Aprovações de Acesso`, `Gestionamento` e `Configurações` serão conectadas nas etapas seguintes (W4).

---

## 1. Paridade Visual de Avatar & Perfil (APK ↔ Web)

Criar o utilitário compartilhado `frontend/src/utils/avatarUtils.ts` e o componente `frontend/src/components/auth/UserAvatar.tsx` replicando **exatamente** a regra pura de `geradorCampo/src/domain/rules/authRules.ts`:

* **Paleta oficial (`AVATAR_PALETTE`):**
  ```ts
  ["#1D4ED8", "#0E7490", "#047857", "#4338CA", "#B45309", "#9F1239", "#0F766E", "#6D28D9"]
  ```
* **Algoritmo de cor (`obterCorAvatar(identificador)`):**
  * Normalizar (`trim().toLowerCase()`), calcular hash DJB2 (`hash = 5381; hash = ((hash << 5) - hash + charCode) | 0`) e selecionar `AVATAR_PALETTE[Math.abs(hash) % AVATAR_PALETTE.length]`.
  * **Garantia:** o mesmo `usuario` terá exatamente a mesma cor de fundo no APK e no Web.
* **Algoritmo de iniciais (`extrairIniciaisAvatar(nomeCompleto, fallbackUsuario)`):**
  * Ignorar preposições `["da", "de", "do", "das", "dos", "e"]`; 1 palavra → 1ª letra; 2+ palavras relevantes → 1ª letra da primeira + 1ª letra da última; vazio → 1ª letra de `usuario` (ou `"A"`).
* **Rótulo de perfil (`obterLabelPerfil(role)`):**
  * `"adm"` → `"Administrador (ADM)"` · `"coordenador"` → `"Coordenador"` · `"analista"` → `"Analista"`.

---

## 2. Nova Estrutura Vertical da `Sidebar.tsx`

Reorganizar os blocos de [Sidebar.tsx](file:///c:/Users/pedro.vsouza/Desktop/pedro/git-team/workTree/frontend/src/components/Sidebar.tsx) na seguinte ordem de cima para baixo:

1. **Cabeçalho ARPE** *(mantido: logo ícone + texto `ARPE / Agência de Regulação de PE` + botão recolher).*
2. **Bloco de Perfil do Usuário (no lugar de `CRA · Fiscalização`):**
   * **Remover** o círculo `CRA/CRC/SOCICAM`, o texto `{tipoRelatorio} · {categoriaRelatorio}` e os **3 contadores (`Fotos`, `NCs`, `PAs`)**.
   * **Exibir no lugar:**
     * `<UserAvatar>` circular com a inicial/iniciais brancas e a cor do usuário (`size={48}` quando expandido; `size={36}` clicável se recolhido).
     * Abaixo do círculo: **`{perfil.nome_completo}`** (com indicador discreto de seta `ChevronDown` que gira ao abrir).
   * **Sanfona/Dropdown do Perfil (abre para baixo ao clicar no ícone ou no nome):**
     * **Usuário corporativo:** `@{perfil.usuario}` *(somente leitura)*
     * **Nível de acesso:** `{obterLabelPerfil(perfil.role)}` *(somente leitura)*
     * **Painel ADM** *(visível apenas se `perfil.role === "adm"`)*
     * **Aprovações de Acesso** *(visível se `perfil.role === "adm" || perfil.role === "coordenador"`)*
     * **Gestionamento** *(visível se `perfil.role === "coordenador" || perfil.role === "adm"`)*
     * **Configurações** *(todos os perfis)*
     * **Logout (Sair)** *(todos os perfis — executa `logout()` do `useAuthStore`)*
3. **Navegação Principal (com sanfona `Relatório` + novos itens):**
   * **Botão `Relatório`** *(expansível/sanfona)*:
     * Ao clicar, abre/fecha para baixo as **Rotas do Relatório** exatamente como funcionam hoje (`Dados Gerais`, `Upload de Mídia`, `Ocorrências`, `Recomendação Geral` quando SOCICAM Monitoramento, `Emissão`), mantendo barra indicadora, cadeados e scroll-spy.
   * **Botão `Vistorias`** *(abaixo de `Relatório`, visual no menu lateral)*
   * **Botão `Painel`** *(abaixo de `Vistorias`, visual no menu lateral)*
   * **Botão `Quadro`** *(abaixo de `Painel`, visual no menu lateral)*
   * *(Quando a Sidebar estiver recolhida em `76px`, todos exibem seus ícones alinhados com `title` tooltip; clicando em `Relatório` recolhido, expande a Sidebar e abre as rotas).*
4. **Armazenamento Local (`geradorBD`) movido para baixo:**
   * Mover o card sanfona **Armazenamento Local** (com status conectado/desconectado e botões `Salvar` / `Carregar`) da antiga posição #3 para a **parte inferior**, acima das `Ações Rápidas`.
5. **Rodapé (`Ações Rápidas` / Botão expandir):**
   * Remover o card duplicado de usuário + botão sair que havia sido colocado no rodapé, pois agora o perfil completo com `Logout` vive no bloco #2.

---

## 3. Arquivos a Criar / Alterar (Roteiro para o Agente Executor)

| Ordem | Ação | Arquivo |
| :---: | :--- | :--- |
| **1** | Criar | `frontend/src/utils/avatarUtils.ts` (`AVATAR_PALETTE`, `extrairIniciaisAvatar`, `obterCorAvatar`, `obterLabelPerfil`) |
| **2** | Criar | `frontend/src/components/auth/UserAvatar.tsx` (avatar circular com iniciais e cor determinística) |
| **3** | Alterar | `frontend/src/components/Sidebar.tsx` (perfil no topo com dropdown RBAC, remoção dos contadores, sanfona `Relatório` + itens `Vistorias`, `Painel`, `Quadro`, e `Armazenamento Local` movido para baixo) |
| **4** | Validar | `npx.cmd tsc --noEmit` (zero erros nos arquivos alterados) e `npm.cmd --prefix frontend run build` |
