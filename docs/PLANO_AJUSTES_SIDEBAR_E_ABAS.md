# Plano de Implementação — Ajustes Visuais da `Sidebar` e Troca de Abas (`App.tsx`)

> **Objetivo:** Refinar o menu lateral (`Sidebar.tsx`) e conectar a troca visual de abas (`Relatório`, `Vistorias`, `Painel`, `Quadro`) no `App.tsx`, deixando as novas abas prontas com tela em branco para a próxima etapa.

---

## 1. Topo da Sidebar (`Logo ARPE`) — [Sidebar.tsx](file:///c:/Users/pedro.vsouza/Desktop/pedro/git-team/workTree/frontend/src/components/Sidebar.tsx)

1. **Ocultar ícone da ARPE quando o menu estiver fechado (`!expanded`):**
   * Quando `expanded === false`, não renderizar a `logoIcone` no topo (evitando conflito visual com o avatar do perfil logo abaixo).
   * Quando `expanded === true`, exibir a `logoIcone` + texto `ARPE / Agência de Regulação de PE` + botão recolher (`ChevronLeft`).
2. **Remover caixa/círculo em volta da logo ARPE:**
   * Remover `rounded-2xl bg-white/[0.06] p-1.5 ring-1 ring-white/10` do wrapper de `logoIcone`, mantendo a imagem solta diretamente sobre o fundo do menu.

---

## 2. Perfil Solto no Fundo do Menu — [Sidebar.tsx](file:///c:/Users/pedro.vsouza/Desktop/pedro/git-team/workTree/frontend/src/components/Sidebar.tsx)

* Remover o container `rounded-2xl border border-white/10 bg-white/[0.04]` ao redor do bloco do Perfil quando expandido.
* Deixar o `<UserAvatar>` e o nome `{perfil.nome_completo}` soltos diretamente no fundo azul do menu (no mesmo estilo visual limpo do botão `Relatório`), mantendo a sanfona com as opções (`Usuário corporativo`, `Nível de acesso`, `Painel ADM`, `Aprovações de Acesso`, `Gestionamento`, `Configurações`, `Logout`) ao clicar no avatar ou no nome.

---

## 3. Botão `Relatório`, Rotas com Menu Fechado e Remoção da Seta

1. **Remover a seta (`ChevronDown`) do botão `Relatório`:**
   * O botão `Relatório` não atua mais como abre/fecha manual por clique nele mesmo.
   * Ele permanece aberto (`activeTab === "relatorio"`) e **só fecha** quando o usuário clicar em outra aba (`Vistorias`, `Painel` ou `Quadro`).
2. **Manter os ícones das rotas visíveis mesmo com o menu fechado (`!expanded`):**
   * Alterar a condição de visibilidade das rotas de `expanded && relatorioOpen` para **`activeTab === "relatorio"`**.
   * **Com menu expandido (`expanded === true`):** mostra ícones + labels indentados abaixo de `Relatório` (`pl-2 ml-5 border-l border-white/10`).
   * **Com menu recolhido (`expanded === false`):** mantém os ícones das etapas visíveis logo abaixo do ícone `Relatório`, levemente deslocados à frente (`pl-2 ml-3 border-l border-white/10`), preservando a barra indicadora da etapa ativa e tooltips.

---

## 4. Troca de Abas (`Relatório`, `Vistorias`, `Painel`, `Quadro`) — [App.tsx](file:///c:/Users/pedro.vsouza/Desktop/pedro/git-team/workTree/frontend/src/App.tsx) e [Sidebar.tsx](file:///c:/Users/pedro.vsouza/Desktop/pedro/git-team/workTree/frontend/src/components/Sidebar.tsx)

1. **Estado compartilhado da aba ativa:**
   * Criar tipo `SidebarTab = "relatorio" | "vistorias" | "painel" | "quadro"` (em `App.tsx` ou no `navigationSlice` / prop para `Sidebar`).
   * Passar `activeTab` e `onSelectTab(tab: SidebarTab)` para `Sidebar`.
2. **Comportamento ao clicar nos itens do menu:**
   * Clicar em **`Relatório`**: define `activeTab = "relatorio"` (volta para o Gerador de Relatórios completo e reabre as rotas).
   * Clicar em **`Vistorias`**, **`Painel`** ou **`Quadro`**: define `activeTab` correspondente, fecha automaticamente a lista de rotas do `Relatório` e destaca o botão ativo no menu.
3. **Renderização no `App.tsx`:**
   * Se `activeTab === "relatorio"`: renderiza normalmente o `TopHeader` + o formulário/blocos `#b1..#b5` do Gerador de Relatórios.
   * Se `activeTab !== "relatorio"` (`vistorias`, `painel` ou `quadro`): exibe a área principal em branco limpa (preparada para receber os respectivos conteúdos na próxima etapa).

---

## 5. Arquivos a Alterar (Roteiro para `/developer`)

| Ordem | Arquivo | Alteração |
| :---: | :--- | :--- |
| **1** | `frontend/src/App.tsx` | Gerenciar estado `activeTab` (`"relatorio"` por padrão), passar para `Sidebar` e renderizar área em branco quando `activeTab !== "relatorio"`. |
| **2** | `frontend/src/components/Sidebar.tsx` | Ocultar logo ARPE quando `!expanded`, remover borda/fundo da logo e do Perfil, remover `ChevronDown` de `Relatório`, exibir ícones da rota mesmo recolhido quando `activeTab === "relatorio"`, e alternar `activeTab` ao clicar em `Relatório`, `Vistorias`, `Painel` e `Quadro`. |
| **3** | Validação | Rodar `npx.cmd tsc --noEmit` (zero erros nos arquivos alterados) e `npm.cmd --prefix frontend run build`. |
