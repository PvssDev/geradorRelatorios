# Regras de Governança de UI/UX & Streamlit

Este documento define as regras mandatórias para qualquer desenvolvimento, refatoração ou adição de componentes na interface gráfica do projeto **Gerador de Relatórios**.

---

## 🎨 1. Fidelidade ao Design System Corporativo
1. **Paleta Restrita e Harmoniosa:**
   - **É terminantemente proibido** utilizar cores genéricas ou CSS ad-hoc fora da paleta (ex: azul puro `blue`, vermelho puro `red`, verde puro `green`).
   - Apenas os tokens oficiais são permitidos:
     - Primário escuro: `#0D2740`
     - Texto e contorno: `#011A33`
     - Acento e bordas: `#2F5173`
     - Fundos de apoio: `#D7D8D9`, `#c9d2db`, `#dfe5eb`
     - Fundo geral: `#d7e6f0`
2. **Tipografia Padrão:**
   - Todo componente deve herdar a tipografia `'Outfit', 'Work Sans', sans-serif`.
   - Ícones devem utilizar a convenção `:material/<nome_do_icone>:` renderizados pela fonte `Material Symbols Rounded`.

---

## 🔘 2. Governança de Botões e Componentes de Ação
1. **Obrigatoriedade de Chaves Únicas (`key`):**
   - Todo `st.button`, `st.pills`, `st.download_button` ou `st.popover` DEVE possuir uma `key` única com prefixo semântico (`btn_...`, `widget_...`).
   - NUNCA crie botões dinâmicos em loops sem incluir o contador ou ID na chave (`key=f"btn_del_{id}"`).
2. **Hierarquia de Tipo:**
   - Botões principais de avanço ou conclusão devem usar `type="primary"`.
   - Botões de suporte, navegação ou ação neutra devem usar `type="secondary"` ou padrão.
3. **Proteção Contra Ações Destrutivas:**
   - Botões de exclusão em massa ou limpeza de registros nunca devem excluir diretamente. Devem acionar uma modal de confirmação `@st.dialog` com aviso explícito.

---

## 🖼️ 3. Manipulação de Assets e Estilos CSS
1. **Injeção de CSS Centralizada:**
   - Modificações de estilo devem ser consolidadas em `src/style.css`. Evite injetar blocos `<style>` dispersos inline em múltiplos arquivos.
   - Utilize variáveis CSS (`:root`) quando for necessário injetar dados dinâmicos (como imagens base64 de fundo).
2. **Cache de Assets Pesados:**
   - Todo carregamento de imagens de capa, fundos ou conversão para base64 deve ser protegido com `@st.cache_data`.
3. **Não Quebrar Seletores Globais:**
   - Não remova ou desative as classes de cartões `.st-key-<container_name>` ou os ajustes de `overflow: visible` que sustentam o layout dos containers elevados.

---

## ⚖️ 4. Desacoplamento Arquitetural (SOLID - SRP)
1. **UI Agnóstica de Documentos Word:**
   - Arquivos em `src/ui/` ou `src/app.py` não devem instanciar diretamente classes do `python-docx` nem definir parágrafos ou tabelas de relatório. A geração de documentos pertence estritamente a `src/reports/`.
2. **UI Agnóstica de Regras Contratuais:**
   - O cálculo de codificação CRA (`CRA.ST...`), formatação por extenso CRC (`1 (uma)`) ou normalização Socicam pertencem a `src/core/rules/`. A interface deve apenas invocar essas funções puras.
