# ADR 2: Migração de Streamlit para Arquitetura Desacoplada (React SPA + FastAPI)

* **Status:** Aceito e Implementado
* **Data:** 2026-10-15
* **Contexto:** Evolução da Arquitetura do Gerador de Relatórios

---

## 1. Histórico e Trajetória do Projeto

O ecossistema do **Gerador de Relatórios** evoluiu através de três fases arquiteturais marcantes:

1. **Fase 1 — Terminal / CLI em Python:**
   - O projeto nasceu como um script em lote de linha de comando no terminal.
   - Processava planilhas Excel brutas (`pandas`) e gerava documentos Word (`python-docx`).
   - *Limitação:* Operação restrita a desenvolvedores; ausência de conferência visual e ordenação de fotos em campo.

2. **Fase 2 — Interface Rápida com Streamlit:**
   - Adotou-se o Streamlit para disponibilizar rapidamente uma interface gráfica departamental em Python puro sem necessidade de API REST intermediária ([ADR 0001](./0001-escolha-do-streamlit.md)).
   - *Limitação:* Com o crescimento da base de dados e a introdução dos 6 estados regulatórios (CRA, CRC e SOCICAM), o modelo de execução do Streamlit (reexecução integral do script a cada clique e gerenciamento frágil de `st.session_state`) gerou gargalos críticos de reatividade, bloqueios no upload massivo de fotos em alta resolução e restrições severas de customização da interface (carrosséis 3D, modais dinâmicos e persistência local).

3. **Fase 3 — Arquitetura Moderna Desacoplada (React + FastAPI):**
   - Para permitir escalabilidade, experiência do usuário (UX) fluida e desacoplamento total entre regras de negócio e apresentação, a aplicação foi migrada para uma arquitetura em camadas concêntricas (Clean Architecture) composta por **React (SPA)** no frontend e **FastAPI (REST)** no backend.

---

## 2. Decisão Arquitetural

Decidiu-se desacoplar a aplicação em duas camadas independentes e especializadas:
- **Frontend SPA:** Desenvolvido em **React 18 + Vite + Tailwind CSS + Zustand**, operando com armazenamento client-side no navegador (IndexedDB e File System Access API) e compressão em hardware local via HTML5 Canvas.
- **Backend API:** Desenvolvido em **FastAPI (Python)**, expondo contratos RESTful tipados via Pydantic, desacoplado de qualquer dependência visual e estruturado sob os princípios SOLID e Clean Architecture.

---

## 3. Benefícios Alcançados

1. **Reatividade Instantânea e Eliminação de Re-runs:**
   - O frontend React gerencia o estado da vistoria e o carrossel fotográfico localmente sem recarregar o backend a cada clique.
2. **Compressão Client-Side e Economia de Banda:**
   - Imagens pesadas de 8 MB a 15 MB são redimensionadas no navegador para ~80 KB via Canvas antes do upload, eliminando estouros de payload e timeouts.
3. **Persistência Offline / Local (IndexedDB):**
   - Os dados e lotes de fotos em edição persistem com segurança no navegador do usuário, protegendo contra perda de trabalho em caso de fechamento acidental da aba.
4. **Isolamento de Domínio e Testabilidade:**
   - O núcleo do sistema (`src/core/rules/` e `src/reports/`) tornou-se 100% puro e testável por testes unitários (`pytest`), sem qualquer dependência de Streamlit ou UI.

