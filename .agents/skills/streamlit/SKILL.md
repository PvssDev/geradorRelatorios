---
name: streamlit
description: >-
  Especialista em interface, estética, botões, assets, injeção de CSS avançado e componentes no Streamlit para o projeto Gerador de Relatórios. Use esta skill ao criar, refatorar, estilizar telas, botões, cartões, diálogos, carrosséis ou otimizar a experiência visual e ciclo de vida do Streamlit.
---

# 🎨 Skill: Especialista em Streamlit, Estética & UI/UX

Esta competência define o conhecimento aprofundado sobre a camada de apresentação do **Gerador de Relatórios**, cobrindo o Design System corporativo, estilizações CSS injetadas, padrões de botões, tratamento de assets gráficos, componentes customizados e boas práticas do ciclo de vida reativo do Streamlit.

---

## 🎯 Missão e Escopo de Atuação do Agente Streamlit

O especialista em Streamlit assegura que a interface do usuário:
1. **Transmita Alta Estética & Elegância:** Aplicação rigorosa da paleta institucional (tons de azul profundo `#011A33`, `#0D2740`, slate `#2F5173`, e cinzas neutros `#D7D8D9`, `#c9d2db`).
2. **Harmonize a Hierarquia de Botões:** Padrões claros para ações primárias, secundárias, destrutivas, botões de ícone e seletores em pills.
3. **Gerencie Assets com Performance:** Injeção limpa de texturas de fundo em base64 com controle de transparência e cache, evitando lentidão nos re-runs do Streamlit.
4. **Mantenha Robustez nos Seletores CSS:** Estilização baseada em chaves (`st-key-...`), classes personalizadas e minimização de seletores frágeis de nós internos do Streamlit.
5. **Preserve a Separação de Camadas (SOLID - SRP):** A camada visual cuida apenas de layout, renderização e captura de eventos do usuário, delegando cálculos e validações a `src/core/rules/` e persistência a `src/services/`.

---

## 📚 Guias Técnicos Especializados (Progressive Disclosure)

Consulte os manuais de referência dedicados para especificações aprofundadas:

* 🎨 **[Design System & Tokens Visuais](./references/design_system_and_tokens.md):**
  Paleta de cores hexadecimais, tipografia (`Outfit` + `Work Sans`), ícones `Material Symbols Rounded`, elevações, sombras, bordas e glassmorphism do header fixo.

* 🔘 **[Botões, Controles & Componentes de Ação](./references/buttons_and_components.md):**
  Padrões canônicos para `st.button`, `st.pills`, `st.popover`, `@st.dialog`, botões de exclusão em lote, tags multiselect, feedback por `st.toast` e convenção de chaves (`key="btn_..."`).

* 🖼️ **[Assets Gráficos & Injeção de CSS](./references/assets_and_css_injection.md):**
  Mecanismo de injeção de fundo duplo base64 com alfa variável, organização da pasta `src/assets/`, componentes bidirecionais (`Swiper` e `LocalStorage`) e blindagem de seletores CSS.

---

## 🛠️ Procedimento Operacional Padrão (Passo a Passo)

Ao criar ou estilizar qualquer elemento na aplicação Streamlit:

### 1. Definir a Hierarquia e Tipo de Botão
* **Ação Primária Positiva** (ex: *Gerar Relatório*, *Adicionar NC*, *Salvar e Continuar*):
  - Usar `type="primary"` e ícone do Material Symbols (ex: `:material/check_circle:`, `:material/add:`).
  - Background escuro `#0D2740`, texto `#D7D8D9`, hover `#2F5173`, active scale `0.98`.
* **Ação Secundária** (ex: *Voltar*, *Galeria*, *Limpar Uploads*):
  - Usar `type="secondary"` (ou default), contorno `1.5px solid #2F5173`, fundo `#D7D8D9`, texto `#011A33`.
* **Ação Crítica/Perigo** (ex: *Excluir NC*, *Confirmar Limpeza Completa*):
  - Sempre encapsular em `@st.dialog` com aviso claro e contagem de tempo/segurança quando destrutivo.

### 2. Garantir Chaveamento Consistente (`key`)
* Todo widget iterativo ou dinâmico DEVE possuir uma `key` única e descritiva:
  - Formato: `key=f"btn_{acao}_{contexto}_{counter}"` ou `key="btn_bulk_delete"`.
  - Isso garante estabilidade no `st.session_state` e permite estilização cirúrgica via CSS `.st-key-<nome_da_key>`.

### 3. Encapsular em Containers Estilizados
* Agrupar seções lógicas em `st.container(border=True)`.
* Aplicar chaves semânticas no container (`key="upload_arquivos_container"`, etc.) para herdar as bordas arredondadas de 12px, cor `#dfe5eb` e sombras suaves de elevação.

### 4. Respeitar o Ciclo de Vida do Streamlit (Sem Mutações Fantasma)
* Não instanciar processamento pesado de imagem sem `@st.cache_data`.
* Utilizar `on_change` / `on_click` para transições de estado limpas antes do script re-executar.
* Evitar chamadas consecutivas de `st.rerun()` sem alteração real de estado.

---

## 🛡️ Checklist de Qualidade de UI/UX

Antes de finalizar qualquer modificação na interface, passe pelo crivo:
- [ ] O contraste de texto atende a padrões de legibilidade (fundo claro com fonte `#011A33` ou fundo escuro com fonte `#D7D8D9`)?
- [ ] Os botões possuem ícones nativos `:material/<nome>:` coerentes com a ação?
- [ ] O header fixo com efeito glassmorphism (`backdrop-filter: blur(8px)`) permanece funcional e sem quebras visuais?
- [ ] A navegação superior via `st.pills` reflete com exatidão a modalidade ativa?
- [ ] Não há vazamento de estilos que desconfigurem outros componentes nativos do Streamlit?
- [ ] Nenhuma regra de negócio regulatória ou lógica do Word foi acoplada no arquivo de UI?
