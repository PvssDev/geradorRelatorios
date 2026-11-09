# 🏛️ Gerador de Relatórios Técnicos Regulatórios — ARPE

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg?logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-3.x-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Tests](https://img.shields.io/badge/Pytest-190%20passed-success.svg?logo=pytest&logoColor=white)](https://docs.pytest.org/)

Ferramenta corporativa para compilação automatizada de relatórios técnicos regulatórios, auditoria de dados de campo e geração padronizada de memoriais fotográficos em formatos `.docx` e `.pdf` para a **Agência de Regulação de Pernambuco (ARPE)**.

---

## 📜 1. Trajetória e Evolução do Projeto

O sistema passou por uma evolução técnica contínua para acompanhar a demanda de dados e a necessidade de usabilidade da equipe:

1. **Fase 1 — Terminal / CLI em Python:**
   - Script inicial executado exclusivamente via linha de comando no terminal.
   - Lia planilhas de campo em Excel via `pandas` e preenchia modelos Word via `python-docx`.
   - *Limitação:* Operação restrita a desenvolvedores; ausência de conferência visual e ordenação de fotos.
2. **Fase 2 — Prototipação com Streamlit:**
   - Introdução de uma interface web gráfica rápida em Python puro, eliminando a dependência do terminal para os analistas ([ADR 0001](./docs/0001-escolha-do-streamlit.md)).
   - *Gargalo de Escalabilidade:* Com o aumento no volume de fotos (centenas de fotos de alta resolução por vistoria) e a implementação do fluxo de monitoramento com extração dinâmica de documentos, o ciclo de reexecução (*re-runs*) a cada clique no Streamlit gerou lentidão, perda de estado e rigidez na experiência visual.
3. **Fase 3 — Arquitetura Atual Desacoplada (React SPA + FastAPI):**
   - Transição para uma **Single Page Application (SPA)** desacoplada ([ADR 0002](./docs/0002-migracao-para-react-fastapi.md)).
   - O **React + Vite** no frontend oferece reatividade instantânea, compressão de imagens em hardware local (Canvas) e carrosséis interativos.
   - O **FastAPI** no backend provê uma API RESTful de alta velocidade, desacoplada e 100% testável sob os princípios da **Clean Architecture**.

---

## 🏛️ 2. Arquitetura e Engenharia de Software

O projeto adota práticas avançadas de engenharia de software para garantir robustez, sustentabilidade e segurança:

* **Clean Architecture:** Camadas concêntricas bem definidas. O núcleo de regras de negócio (`src/core/`) é puro e completamente isolado de bibliotecas visuais ou de entrada/saída.
* **Princípios SOLID:**
  - **SRP (Single Responsibility):** Desacoplamento estrito entre transporte HTTP (`server/`), regras de negócio (`core/rules/`) e montagem tipográfica de documentos (`sections/`).
  - **OCP (Open/Closed):** Extensão modular de layouts via herança de `BaseReport` e registro em `src/reports/factory.py`.
  - **LSP / ISP / DIP:** Interfaces e contratos segregados (`IReportContract`), permitindo substituição transparente e injeção de dependências.
* **Princípio DRY (*Don't Repeat Yourself*):** Algoritmos universais para ordenação natural de fotos, cálculo determinístico de sequenciais anuais (`/{ano}.001`, `/{ano}.002`) e dimensionamento na grade da página A4 (7.27 polegadas).
* **BDD / TDD:** Cobertura de testes unitários e de integração estruturados com `pytest` baseados em cenários de comportamento (*Given/When/Then*).
* **LGPD & Segurança:** Processamento e armazenamento soberanos em ambiente local. Não há exposição de fotos de terceiros em servidores públicos nem persistência indevida de dados sensíveis.

---

## 🛠️ 3. Tecnologias e Bibliotecas Utilizadas

### Frontend
- **React 18 & TypeScript:** Componentização reativa com tipagem estrita de contratos.
- **Vite:** Build tool moderno e servidor de desenvolvimento com Hot Module Replacement (HMR).
- **Tailwind CSS:** Design system corporativo moderno, responsivo e de alta performance.
- **Zustand:** Gerenciamento de estado global previsível e desacoplado.
- **HTML5 Canvas API:** Compressão client-side de imagens de alta resolução (redução de fotos de 8 MB para ~80 KB).
- **File System Access API:** Seleção em massa de pastas de fotos de campo diretamente do disco.
- **IndexedDB:** Persistência local e cache de vistorias em andamento no navegador.

### Backend
- **Python 3.10+:** Plataforma base do motor de dados e processamento de documentos.
- **FastAPI & Uvicorn:** Framework web assíncrono de alto desempenho e servidor ASGI local.
- **python-docx:** Motor nativo de manipulação e geração de documentos Microsoft Word (.docx).
- **Pillow (PIL):** Processamento de imagens, autocorreção de rotação de fotos de celular (`exif_transpose`) e extração de data original de captura EXIF (`DateTimeOriginal`).
- **Pandas & OpenPyXL:** Manipulação, auditoria e exportação de dados tabulares em Excel.
- **Pytest:** Suíte com mais de 190 testes automatizados de regressão e domínio.

---

## 🚦 4. Os 6 Estados Regulatórios Atendidos

O sistema atende de forma unificada e especializada às seguintes combinações contratuais:

| Concessão | Fiscalização (Vistoria Inicial) | Monitoramento (Acompanhamento e Resolução) |
| :--- | :--- | :--- |
| **CRA** (Rota do Atlântico) | Vias expressas Suape. Controle de Pista, Faixa, Trecho/KM. Codificação `CRA.ST{subtrecho}.{estacas}/{ano}.{seq:03d}`. Distinção entre NC e Ponto de Atenção (PA). | Auditoria de cumprimento em relação a ofícios e vistorias anteriores do Convênio SUAPE/ARPE nº 003/2021. |
| **CRC** (Rota dos Coqueiros) | Rodovia PE-024 e Ponte do Paiva (PPP CGPE-001/2006). Redação mandatória de conclusões com numerais femininos por extenso ("1 (uma)", "2 (duas)"). | Leitura do relatório anterior (`.docx`), extração de dados SEI, avanço de ciclo ($N-1 \rightarrow N_{curr}$) e montagem do Quadro de Situação das pendências. |
| **SOCICAM** (Terminais Rodoviários) | Terminais TIP Recife, Caruaru, Garanhuns e Petrolina. Setorização predial (sem faixas rodoviárias), normalização de nomes e codificação `{base}/{ano}.{seq:03d}`. | Acompanhamento do saneamento das irregularidades nos terminais rodoviários e Quadro de Determinações. |

---

## 🚀 5. Instalação e Execução

### Pré-requisitos
- **Python 3.10+** instalado no PATH.
- **Node.js 18+** e **npm** instalados.

### Passo a Passo

1. **Clonar o Repositório:**
   ```bash
   git clone <url-do-repositorio>
   cd workTree
   ```

2. **Instalar Dependências do Backend:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Instalar Dependências do Frontend:**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Execução Simultânea (Modo de Desenvolvimento):**
   Execute o script unificado na raiz do projeto:
   ```bash
   python dev.py
   ```
   *(ou `npm run dev`)*

O script iniciará automaticamente:
* **Backend FastAPI:** `http://127.0.0.1:8000` (com documentação interativa em `/docs`).
* **Frontend Vite:** `http://localhost:5173` (aberto diretamente no seu navegador).

---

## 🧪 6. Testes Automatizados

Para executar toda a suíte de testes de regressão e validação dos 6 estados regulatórios:

```bash
py -m pytest tests/
```

Para validar a tipagem e compilação do frontend:
```bash
cd frontend
npm run build
```

---

## 📚 Documentação Complementar

- [ADR 0001: Escolha Inicial do Streamlit](./docs/0001-escolha-do-streamlit.md)
- [ADR 0002: Migração para React SPA e FastAPI](./docs/0002-migracao-para-react-fastapi.md)
- [Arquitetura Detalhada e Diretrizes de Engenharia](./docs/ARQUITETURA.md)
