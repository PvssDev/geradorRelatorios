# Botões, Controles & Componentes de Ação no Streamlit

Este guia estabelece os padrões de taxonomia de botões, convenções de nomenclatura de `key`, microinterações, comportamentos em modais e feedback ao usuário.

---

## 🔘 1. Taxonomia e Hierarquia dos Botões

O sistema opera com 5 níveis bem delimitados de botões:

### 1.1. Botão Primário (`type="primary"`)
* **Uso:** Ação principal e de avanço no fluxo de trabalho (ex: `Gerar Relatório Automático`, `Salvar e Continuar`, `Adicionar Fiscalização`).
* **Visual:** Fundo escuro `#0D2740`, texto claro `#D7D8D9`, borda `#011A33`, `font-weight: 600`, sombra sutil `0 2px 6px rgba(1, 26, 51, 0.25)`.
* **Microinteração:** Hover transita suavemente para `#2F5173`, com `transform: translateY(-1px)` e sombra expandida. No `:active`, encolhe com `transform: scale(0.98)` para sensação tátil de clique.
* **Exemplo Python:**
  ```python
  st.button(
      "Salvar e Continuar",
      icon=":material/check_circle:",
      type="primary",
      use_container_width=True,
      key=f"btn_save_step1_{form_counter}"
  )
  ```

### 1.2. Botão Secundário / Outline (`type="secondary"` ou default)
* **Uso:** Ações de navegação, apoio ou cancelamento (ex: `Voltar`, `Galeria`, `Limpar Registros`).
* **Visual:** Fundo `#D7D8D9`, texto `#011A33`, borda `1.5px solid #2F5173`.
* **Microinteração:** No hover inverte para fundo `#2F5173` com texto `#D7D8D9`.
* **Exemplo Python:**
  ```python
  st.button(
      "Voltar",
      icon=":material/keyboard_backspace:",
      type="secondary",
      use_container_width=True,
      key=f"btn_back_step2_{form_counter}"
  )
  ```

### 1.3. Botões de Ícone Compacto (Ações de Grid / Gestão)
* **Uso:** Ações pontuais em cabeçalhos de formulários ou tabelas (ex: gerenciar responsáveis, configurações, zoom).
* **Visual:** Botão sem texto longo ou apenas ícone, contendo `help="..."` com tooltip informativo.
* **Exemplo Python:**
  ```python
  st.button(
      "",
      icon=":material/tune:",
      help="Editar Fiscalizações e Não Conformidades cadastradas",
      key="btn_manage_edicao_relatorio"
  )
  ```

### 1.4. Botão de Exclusão / Crítico
* **Uso:** Exclusão em lote ou limpeza de estado.
* **Regra de Ouro:** NUNCA execute exclusão irreversível em um clique direto na tela principal. O botão inicial apenas aciona a modal de confirmação `@st.dialog`.
* **Exemplo Python:**
  ```python
  if st.button(
      "Excluir Selecionadas",
      icon=":material/delete_sweep:",
      type="secondary",
      disabled=len(selecionadas) == 0,
      key="btn_bulk_delete"
  ):
      confirmar_exclusao_modal(selecionadas)
  ```

### 1.5. Navegadores em Pílulas (`st.pills`)
* **Uso:** Alternância de modalidade no topo (`CRA`, `CRC`, `SOCICAM` e `Fiscalização`, `Monitoramento`) e seleção rápida de tipo de registro / status de saneamento.
* **Visual Customizado no CSS:**
  - Pílula inativa: Neutra, integrada ao fundo.
  - Pílula ativa: Fundo `#dae0e7`, contorno escuro nítido `#011A33`, texto em negrito `#011A33`.
  - Tooltips automáticos injetados via JavaScript para siglas de NC.

---

## 🔑 2. Convenção Rigorosa de Chaveamento (`key`)

Todo botão no Streamlit precisa de uma `key` que atenda a duas funções:
1. **Estabilidade de Re-renderização:** Evitar que o Streamlit confunda o estado de botões em listas dinâmicas.
2. **Alvo de Estilização CSS:** O CSS do projeto faz match em seletores `div[class*="st-key-btn_..."] button`.

### Padrão de Nomenclatura:
| Padrão de Chave | Finalidade | Exemplo |
| :--- | :--- | :--- |
| `btn_<acao>_<entidade>` | Ações globais únicas | `btn_clear_uploads`, `btn_run_report_main` |
| `btn_<acao>_<entidade>_{counter}` | Ações dinâmicas de formulário | `btn_fisc_add_1`, `btn_zoom_old_3` |
| `btn_manage_<entidade>` | Abertura de modais de gestão | `btn_manage_responsaveis`, `btn_manage_coordenadores` |
| `btn_confirm_<acao>` | Confirmação final dentro de dialog | `btn_confirm_nc_del`, `btn_limpar_estado_relatorio` |
| `btn_cancel_<acao>` | Cancelamento dentro de dialog | `btn_cancel_nc_del` |

---

## 🪟 3. Modais e Diálogos (`@st.dialog`)

O sistema adota modais nativas `@st.dialog` com larguras parametrizadas (`width="large"`):

```python
@st.dialog("Confirmar Exclusão de Itens", icon=":material/delete:")
def confirmar_exclusao_nc_modal(nc_keys: list):
    st.write("Você tem certeza que deseja excluir os seguintes itens selecionados?")
    for item in nc_keys:
        st.write(f"- **{item}**")
    
    st.warning("Esta ação não pode ser desfeita.")
    
    col_sim, col_nao = st.columns(2)
    with col_sim:
        if st.button("Sim, Excluir", icon=":material/delete:", type="primary", use_container_width=True, key="btn_confirm_del"):
            # Lógica de exclusão e persistência
            st.session_state.pending_toast = ":green[:material/check_circle:] Itens excluídos com sucesso!"
            st.rerun()
    with col_nao:
        if st.button("Cancelar", icon=":material/close:", use_container_width=True, key="btn_cancel_del"):
            st.rerun()
```

### Padrão para Ações Extremas (Contagem de Segurança):
Em modais destrutivas globais (ex: `confirmar_limpar_registros_modal`), adote contagem regressiva de segurança (ex: 5 segundos) antes de habilitar o botão de confirmação, prevenindo cliques acidentais.

---

## 🍞 4. Padrão de Feedback: Notificações com Toasts

Para evitar poluição visual de múltiplos `st.success` ou `st.info` empilhados que permanecem fixos na tela após re-runs:
1. Registre o toast em `st.session_state.pending_toast`.
2. No início do ciclo de renderização de `app.py`:
   ```python
   if st.session_state.get("pending_toast"):
       st.toast(st.session_state.pending_toast)
       st.session_state.pending_toast = None
   ```
3. Use ícones ricos nos toasts:
   - Sucesso: `:green[:material/check_circle:] Operação concluída!`
   - Atenção: `:orange[:material/warning:] Registro pendente de foto.`
   - Erro: `:red[:material/error:] O documento anterior não pôde ser lido.`
