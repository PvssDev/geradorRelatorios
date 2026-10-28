# Assets Gráficos, Injeção de CSS & Componentes Customizados

Este documento descreve como o sistema lida com imagens de fundo, injeção de CSS dinâmico, integração de componentes bidirecionais e blindagem contra quebras de versão do Streamlit.

---

## 🖼️ 1. O Mecanismo de Texturas de Fundo Base64

Para criar uma identidade visual refinada sem recorrer a templates genéricos, o projeto combina duas texturas gráficas exclusivas (`fundo1.png` e `fundo2.png` em `src/assets/`).

### 1.1. Processamento e Controle de Transparência (Alpha Channel)
Em vez de depender de opacidades via CSS (que poderiam afetar a legibilidade dos elementos filhos), o sistema ajusta o canal alfa da imagem em memória usando **Pillow (PIL)**:

```python
import os
import io
import base64
from PIL import Image

def _obter_fundo_base64(filename: str, opacity: float = 0.35) -> str:
    img_path = os.path.join(os.path.dirname(__file__), "assets", filename)
    if not os.path.exists(img_path):
        return ""
    try:
        with Image.open(img_path) as img:
            img = img.convert("RGBA")
            r, g, b, a = img.split()
            a = a.point(lambda p: int(p * opacity))
            img.putalpha(a)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception:
        with open(img_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
```

### 1.2. Injeção Dinâmica em Variáveis CSS (`:root`)
As strings base64 geradas são injetadas em variáveis CSS globais no início da execução:

```python
def inject_custom_theme_css():
    css_path = os.path.join(os.path.dirname(__file__), "style.css")
    fundo1_b64 = _obter_fundo_base64("fundo1.png", opacity=0.38)
    fundo2_b64 = _obter_fundo_base64("fundo2.png", opacity=0.28)
    
    bg_vars = []
    if fundo1_b64:
        bg_vars.append(f"--bg-fundo1: url('data:image/png;base64,{fundo1_b64}');")
    if fundo2_b64:
        bg_vars.append(f"--bg-fundo2: url('data:image/png;base64,{fundo2_b64}');")
        
    bg_var_str = f":root {{ {' '.join(bg_vars)} }}" if bg_vars else ""
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.html(f"<style>{bg_var_str}\n{css_content}</style>")
```

### 1.3. Posicionamento e Comportamento no CSS (`style.css`)
```css
.stApp,
[data-testid="stAppViewContainer"] {
    background-color: #d7e6f0 !important;
    background-image: var(--bg-fundo1), var(--bg-fundo2) !important;
    background-repeat: no-repeat, no-repeat !important;
    background-position: -16vw calc(50% + 50vh), calc(100% + 20vw) calc(100% + 5vh) !important;
    background-size: clamp(520px, 48vw, 850px) auto, clamp(480px, 44vw, 750px) auto !important;
    background-attachment: fixed, fixed !important;
}
```
* **Efeito:** As texturas mantêm-se elegantes nas laterais e cantos inferiores, fixas durante a rolagem e dimensionadas de forma responsiva (`clamp()`).

---

## 🎠 2. Componentes Bidirecionais Customizados

Quando os componentes nativos do Streamlit não atendem aos requisitos estéticos e de usabilidade, o projeto integra componentes bidirecionais em `src/ui/components/`:

### 2.1. Swiper Carousel (`src/ui/components/swiper/`)
* **Propósito:** Apresentação fluida e interativa do memorial fotográfico de vistorias em campo.
* **Tecnologia:** HTML5 + JavaScript nativo com biblioteca Swiper.js, encapsulado via `streamlit.components.v1.declare_component`.
* **Capacidades:**
  - Suporte a toque, arraste com mouse e paginação com miniaturas (*thumbnails*).
  - Zoom e visualização em alta resolução sem sobrecarregar a memória do navegador.

### 2.2. Local Storage & File System Sync (`src/ui/components/local_storage/`)
* **Propósito:** Sincronizar em tempo real as fotos e estados de trabalho em uma pasta local do sistema de arquivos (`File System Access API`), garantindo que o usuário não perca horas de auditoria se fechar o navegador acidentalmente.
* **Comunicação:** Envio assíncrono de eventos e fila de ações versionadas (`enfileirar_acao_fs`).

---

## ⚡ 3. Otimizações de Desempenho e Ciclo de Vida

Para garantir que o Streamlit permaneça rápido mesmo com formulários extensos e dezenas de fotos:

1. **Cache de Codificação e Conversão de Imagens:**
   - Funções que calculam base64 de thumbnails ou fundos devem usar `@st.cache_data`.
2. **Evitar I/O Bloqueante no Thread Principal:**
   - Leituras de disco de arquivos grandes devem ser lazy ou pré-carregadas na inicialização da modalidade.
3. **Uso de MutationObserver para Tooltips em Tempo Real:**
   - A função `inject_tooltips_script()` monitora mutações no DOM do Streamlit para anexar atributos `title` em pills de siglas sem quebrar o ciclo de renderização do Python.
