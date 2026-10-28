# Design System & Tokens Visuais do Gerador de Relatórios

Este documento cataloga todos os padrões visuais, tokens de estilo, paleta de cores, tipografia e diretrizes de layout que compõem a estética corporativa do sistema.

---

## 🎨 1. Paleta de Cores Canônica

A identidade visual foi construída sobre uma harmonia sóbria de azuis institucionais e cinzas técnicos:

| Token / Papel | Código HEX | Amostra & Uso Principal |
| :--- | :--- | :--- |
| **Navy Profundo (Primary)** | `#0D2740` | Botões primários (`button[kind="primary"]`), botões de upload em dropzone, títulos principais com alto destaque. |
| **Dark Contraste / Texto** | `#011A33` | Cor principal de tipografia (`body`, `h1`-`h6`, `label`, `p`), contornos escuros de pills ativas e botões de destaque. |
| **Slate Blue (Acento)** | `#2F5173` | Hover de botões primários, bordas de containers (`1.5px solid #2F5173`), scrollbars, tags do multiselect. |
| **Light Blue Background** | `#d7e6f0` | Fundo geral da página (`.stApp`, `[data-testid="stAppViewContainer"]`), garantindo suavidade visual sem cansaço. |
| **Light Gray Neutro** | `#D7D8D9` | Fundo de botões secundários, fundo de inputs/textareas, expanders, caixas de alerta (`st.alert`). |
| **Card Slate Gray** | `#dfe5eb` | Fundo dos cartões principais de seção (`st.container border=True`), contraste ideal sobre o fundo azulado. |
| **Active Pill Gray** | `#dae0e7` | Fundo de pills selecionadas com contorno escuro (#011A33) para visual limpo sem cores berrantes. |
| **Glassmorphism Header** | `rgba(215, 230, 240, 0.92)` | Fundo translúcido do cabeçalho fixo com `backdrop-filter: blur(8px)`. |

---

## 🖋️ 2. Tipografia e Fontes

O projeto utiliza fontes modernas do Google Fonts importadas no início de `src/style.css`:

```css
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Work+Sans:wght@300;400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');
```

* **Fonte Primária:** `'Outfit', sans-serif` – usada para títulos, cabeçalhos, botões, números e destaques. Traz modernidade geométrica e clareza.
* **Fonte Secundária:** `'Work Sans', sans-serif` – excelente legibilidade para parágrafos longos, tabelas, descrições contratuais e inputs de texto.
* **Ícones Nativos:** `Material Symbols Rounded` (preenchido: `'FILL' 1, 'wght' 500, 'GRAD' 0, 'opsz' 24`). Substitui ícones genéricos por glifos com cantos arredondados, harmonizando com o design.

---

## 📦 3. Containers, Cartões e Elevação

O sistema envelopa os blocos de fluxo de trabalho em containers estilizados:

```text
.st-key-upload_arquivos_container
.st-key-top_fisc_container
.st-key-registros_main_container
.st-key-acoes_panel_container
.st-key-downloads_section_container
```

### Propriedades Canônicas dos Cartões:
* **Borda:** `1.5px solid #2F5173`
* **Arredondamento:** `border-radius: 12px`
* **Fundo:** `#dfe5eb`
* **Sombra em Repouso:** `box-shadow: 0 4px 12px rgba(13, 39, 64, 0.12)`
* **Transição em Hover:** `transition: box-shadow 0.3s ease, transform 0.3s ease`
* **Elevação em Hover:**
  ```css
  box-shadow: 0 10px 28px rgba(1, 26, 51, 0.28) !important;
  transform: translateY(-2px);
  ```

---

## 🌟 4. Cabeçalho Fixo com Efeito Glassmorphism

O cabeçalho superior do Streamlit (`header[data-testid="stHeader"]`) permanece fixo na rolagem:

* `position: fixed !important; top: 0; left: 0; right: 0; width: 100%;`
* `z-index: 999999 !important;`
* `background-color: rgba(215, 230, 240, 0.92) !important;`
* `backdrop-filter: blur(8px) !important;`
* `border-bottom: 1px solid rgba(47, 81, 115, 0.1) !important;`

Garante que o status de conexão, botões da IDE ou menus superiores fiquem legíveis e flutuando suavemente sobre o conteúdo da página.

---

## ♿ 5. Acessibilidade e Scrollbar Customizada

* **Foco Acessível (Navegação por Teclado):**
  ```css
  *:focus-visible {
      outline: 2px solid #0D2740 !important;
      outline-offset: 3px !important;
      transition: outline-offset 0.2s ease !important;
  }
  ```
* **Scrollbar Delicada:**
  - Largura: `8px`.
  - Trilho (*track*): `#D7D8D9` com raio de `4px`.
  - Polegar (*thumb*): `#2F5173` transitando para `#0D2740` em `:hover`.
