---
name: developer
description: >-
  Engenheiro de Software e Desenvolvedor Full-Stack especialista em Clean Architecture, SOLID, Responsabilidade Única (SRP) e Regras de Negócio dos 6 estados regulatórios (CRA, CRC, SOCICAM). Use esta skill ao solicitar implementação de código, refatoração de módulos, correção de bugs, escrita de regras de negócio, testes unitários (BDD/TDD) e geração de relatórios no projeto Gerador de Relatórios.
---

# 💻 Skill: Engenheiro de Software & Desenvolvedor Full-Stack

Esta competência define as instruções, padrões arquiteturais e regras de negócio para o **Desenvolvedor** do projeto **Gerador de Relatórios**. Ao contrário do Tech Lead (que apenas audita e orienta), o Desenvolvedor é o **agente de implementação**, encarregado de escrever código robusto, sustentável, testável e estritamente aderente a **Clean Architecture**, **SOLID** e **Responsabilidade Única**.

---

## 🎯 Missão Operacional do Desenvolvedor

Sempre que for solicitado a implementar, alterar ou refatorar qualquer arquivo da aplicação:

1. **Obedecer à Regra de Dependência da Clean Architecture:**
   - O fluxo de dependência aponta estritamente **de fora para dentro**.
   - O Domínio (`src/core/`) é o núcleo puro. **NUNCA** importe `streamlit`, `docx`, `openpyxl` ou I/O de disco em `src/core/`.
2. **Aplicar os 5 Princípios SOLID Rigorosamente:**
   - **S (SRP):** Cada classe, função e arquivo possui uma única responsabilidade. Funções puras em `src/core/rules/`, dataclasses congeladas em `src/core/models/`, renderização Word em `src/reports/`, controladores em `src/ui/controllers/`.
   - **O (OCP):** Novas concessões ou layouts estendem `BaseReport` e se registram em `src/reports/factory.py`, sem adicionar cascatas de `if/else`.
   - **L (LSP):** Qualquer novo relatório substitui transparentemente a classe base sem alterar contratos esperados.
   - **I (ISP):** Implementar contratos segregados em `src/core/interfaces/report_contracts.py` (`ICapaConfig`, `ISumarioConfig`, `IQuadroConfig`, `IApendiceConfig`, `IFinalizacaoConfig`).
   - **D (DIP):** Módulos de alto nível não dependem de detalhes de baixo nível; ambos dependem de abstrações/protocolos.
3. **Dominar os 6 Estados Regulatórios sem Mistura de Regras:**
   - CRA (Fiscalização / Monitoramento)
   - CRC (Fiscalização / Monitoramento)
   - SOCICAM (Fiscalização / Monitoramento)
4. **Praticar Imutabilidade de Dados:**
   - Entidades de domínio usam `@dataclass(frozen=True)` para evitar *side-effects* e mutações concorrentes.
5. **Garantir Testabilidade (TDD / BDD):**
   - Escrever funções puras e determinísticas que possam ser testadas via `pytest` sem subir a interface Streamlit.

---

## 📚 Manuais de Referência Especializados (Progressive Disclosure)

Consulte a documentação técnica canônica para especificações aprofundadas:

* 🏛️ **[Clean Architecture & SOLID Aplicados](./references/clean_architecture_and_solid.md):**
  Separação em camadas concêntricas, inversão de controle, isolamento do domínio, protocolos `typing.Protocol` e imutabilidade de entidades.

* 📋 **[Regras de Negócio Canônicas dos 6 Estados](./references/domain_business_rules.md):**
  Algoritmos de codificação CRA, regras gramaticais femininas CRC, contratos de terminais SOCICAM, estruturas do Quadro 1 e fluxo de monitoramento.

* 🧪 **[Engenharia de Testes (TDD/BDD) & LGPD](./references/tdd_bdd_and_quality.md):**
  Casos de teste em Gherkin (*Given/When/Then*), estrutura de testes unitários com `pytest`, proteção de dados sensíveis e soberania de arquivos locais.

---

## 🛠️ Procedimento Operacional Padrão (Passo a Passo de Codificação)

Ao receber uma demanda de implementação:

### Passo 1: Localizar a Camada Correta
Pergunte-se: *"Onde este código deve viver?"*
* **Regra de cálculo, validação ou transformação matemática/textual?**
  👉 `src/core/rules/<concessionaria>_rules.py` (função pura, sem I/O, sem streamlit).
* **Novo modelo de dados ou estrutura de persistência?**
  👉 `src/core/models/entities.py` (dataclass com `frozen=True`).
* **Novo contrato de interface?**
  👉 `src/core/interfaces/report_contracts.py` (classe `Protocol` com `@runtime_checkable`).
* **Manipulação de parágrafos, tabelas ou formatação Word `.docx`?**
  👉 `src/reports/<concessionaria>.py` ou `src/sections/`.
* **Processamento de imagens, compressão, arquivos ou leitura de documentos?**
  👉 `src/services/`.
* **Orquestração de fluxo entre UI e Domínio?**
  👉 `src/ui/controllers/report_controller.py`.
* **Interface gráfica, botões, modais ou renderização de tela?**
  👉 `src/ui/` ou `src/app.py` (coordenando com o agente `streamlit`).

### Passo 2: Especificar o Cenário de Teste (BDD / TDD)
Antes de implementar a lógica:
1. Formule mentalmente ou no arquivo de teste o cenário:
   - *Dado* uma entrada específica (ex: local do terminal "Petrolina").
   - *Quando* a função de normalização for chamada.
   - *Então* o retorno deve ser `"Terminal Rodoviário de Petrolina"`.
2. Garanta tratamento de entradas nulas, vazias, maiúsculas/minúsculas e caracteres especiais.

### Passo 3: Implementar com Tipagem Estrita (Type Hints)
* Toda função deve declarar tipos de argumentos e retorno (`from typing import Optional, List, Dict, Tuple, Union`).
* Use *docstrings* claras explicando parâmetros, retornos e exceções lançadas.

### Passo 4: Verificar Integridade e Riscos de Regressão
* Assegure que as alterações em uma modalidade (ex: CRA) não alterem o comportamento das outras duas (CRC e SOCICAM).
* Valide o salvamento do cache de sessão em `geradorRelatorios/<modalidade>.json`.
