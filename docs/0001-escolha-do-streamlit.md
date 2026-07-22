# ADR 1: Escolha do Streamlit como Interface do Usuário e Aplicação Web

* **Status:** Aceito
* **Data:** 2026-06-15
* **Autor:** Pedro Vinicius - CTR

---

## 1. Contexto

O projeto "Gerador de Relatórios" nasceu originalmente como uma ferramenta de terminal (CLI) em Python, projetada para ler dados de fiscalização de planilhas Excel (via Pandas) e gerar relatórios automatizados no formato Word `.docx` (via python-docx) acompanhados de memoriais fotográficos formatados.

Para democratizar o uso do sistema por analistas e técnicos de regulação, surgiu a necessidade de criar uma interface gráfica amigável que eliminasse a interação direta com o terminal, facilitasse o upload de documentos e fotos e permitisse a ordenação visual e dinâmica do memorial fotográfico antes da compilação do relatório.

## 2. Decisão

Decidimos utilizar o **Streamlit** (biblioteca de código aberto em Python) como a plataforma exclusiva para o desenvolvimento da interface e do fluxo de aplicação web, em detrimento de abordagens tradicionais baseadas em arquiteturas desacopladas.

## 3. Prós e Contras

### Prós (Benefícios)

1. **Arquitetura Unificada (Single-Language Stack):**
   Como toda a lógica de negócio de processamento de dados (Pandas) e manipulação do Word (python-docx) já foi desenvolvida em Python, o Streamlit permite integrar a lógica do gerador diretamente à interface de usuário. Isso elimina a necessidade de construir, documentar e manter APIs REST intermediárias.

2. **Ciclo de Desenvolvimento Rápido (Time-to-Market):**
   A criação de widgets de entrada de dados, upload de arquivos (`st.file_uploader`), tabelas interativas (`st.data_editor`) e layouts responsivos (`st.columns`) é feita em poucas linhas de código declarativo em Python. O desenvolvimento de um frontend equivalente em JavaScript exigiria semanas de trabalho adicional.

3. **Facilidade de Deploy e Execução Local:**
   O Streamlit roda de forma integrada no ambiente Windows dos usuários reguladores. Ele pode ser executado localmente via `streamlit run` por meio de scripts simples em lote (`.bat`), sem a complexidade de gerenciar servidores Web e servidores API distintos no ambiente corporativo.

4. **Curva de Aprendizado e Manutenção:**
   Qualquer analista de dados ou desenvolvedor Python da equipe pode manter ou expandir a aplicação web, sem precisar dominar tecnologias de frontend moderno (HTML5, CSS3 avançado, React, NPM/Node).

### Contras (Desvantagens e Limitações)

1. **Modelo de Execução Baseado em Re-runs:**
   O Streamlit reexecuta todo o script Python a cada interação do usuário com qualquer elemento de UI. Isso exige o uso rigoroso de caches (`st.cache_data`, `st.cache_resource`) e controle manual de estados globais (`st.session_state`) para evitar sobrecarga de processamento ou lentidão ao ler dados.

2. **Limitação de Customização Visual:**
   A estilização padrão do Streamlit é rígida. Customizações avançadas exigem injeção manual de CSS através do parâmetro `unsafe_allow_html=True` no widget `st.markdown`, o que reduz a elegância e a manutenibilidade do design do frontend.

3. **Restrição de Concorrência e Escalabilidade:**
   Sendo baseado em um servidor Tornado single-threaded executado no ecossistema Python, o Streamlit não é projetado para alto tráfego. No entanto, como o gerador é uma aplicação departamental para uso concorrente baixo, essa limitação é irrelevante para o escopo do projeto.

## 4. Consequências

* **Manutenibilidade:** O código-fonte permanece condensado no repositório Python, facilitando a portabilidade.
* **Segurança e Privacidade:** Os dados e as fotos processadas não saem da máquina do usuário local caso a execução seja off-line.
* **Dependência:** A arquitetura do gerador fica acoplada ao ecossistema do Streamlit. Mudanças disruptivas em futuras versões da biblioteca podem demandar refatorações na estrutura de gerenciamento de sessões do `app.py`.
