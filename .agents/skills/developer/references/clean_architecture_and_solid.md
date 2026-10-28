# Clean Architecture & SOLID no Gerador de Relatórios

Este manual estabelece as diretrizes arquiteturais invioláveis para o desenvolvimento de software no repositório.

---

## 🏛️ 1. Diagrama de Camadas da Clean Architecture

A arquitetura do projeto organiza-se em círculos concêntricos com regra de dependência estrita apontando para o centro:

```text
               ┌────────────────────────────────────────────────────────┐
               │              FRAMEWORKS & DRIVERS (Camada Externa)     │
               │   • Streamlit (app.py, widgets)                        │
               │   • python-docx (geração de arquivos binários .docx)   │
               │   • File System (OS, JSON, imagens em disco)           │
               │                                                        │
               │   ┌────────────────────────────────────────────────┐   │
               │   │      ADAPTERS & SERVICES (Camada Intermediária)│   │
               │   │   • ReportController (src/ui/controllers/)     │   │
               │   │   • ImageService / MediaStorageService         │   │
               │   │   • PreviousReportAuditService                 │   │
               │   │                                                │   │
               │   │   ┌────────────────────────────────────────┐   │   │
               │   │   │   USE CASES & ENGINES (Aplicação)      │   │   │
               │   │   │   • BaseReport, CraReport, etc.        │   │   │
               │   │   │   • Report Factory Registry            │   │   │
               │   │   │                                        │   │   │
               │   │   │   ┌────────────────────────────────┐   │   │   │
               │   │   │   │   CORE DOMAIN (Núcleo Puro)    │   │   │   │
               │   │   │   │   • Models: Entidades Imutáveis│   │   │   │
               │   │   │   │   • Rules: Funções Puras       │   │   │   │
               │   │   │   │   • Interfaces: Protocols (ISP)│   │   │   │
               │   │   │   └────────────────────────────────┘   │   │   │
               │   │   └────────────────────────────────────────┘   │   │
               │   └────────────────────────────────────────────────┘   │
               └────────────────────────────────────────────────────────┘
```

### 🚨 Regra de Ouro da Dependência
* O **Core Domain (`src/core/`)** NÃO conhece e NUNCA importa:
  - `streamlit` ou qualquer componente de UI.
  - `docx` (`python-docx`) ou manipulação de documentos Word.
  - Funções de I/O bloqueante direto em arquivos do sistema operacional.
* O fluxo é sempre:
  `UI / Streamlit` $\to$ `Controllers` $\to$ `Services` $\to$ `Reports Engine` $\to$ `Core Rules & Models`.

---

## ⚖️ 2. Os 5 Princípios SOLID Aplicados no Código

### 2.1. S - Single Responsibility Principle (Responsabilidade Única)
* Cada módulo possui uma única razão para mudar:
  - `src/core/rules/cra_rules.py`: Apenas regras matemáticas e textuais da concessão CRA.
  - `src/reports/socicam.py`: Apenas estrutura e layout das seções do relatório Socicam.
  - `src/services/image_service.py`: Apenas compressão, extração de data e manipulação de bytes de fotos.
  - `src/ui/controllers/report_controller.py`: Apenas orquestração do ciclo de montagem de arquivos temporários e despacho.
* **Anti-padrão Proibido:** Escrever validações contratuais ou cálculos de estacas dentro de manipuladores de clique no Streamlit (`app.py`).

### 2.2. O - Open/Closed Principle (Aberto para Extensão, Fechado para Modificação)
* O sistema foi arquitetado para suportar novas concessões ou tipos de relatório sem alterar o orquestrador principal:
  - Para adicionar uma 4ª concessão (ex: *RODOANEL*):
    1. Crie `src/core/rules/rodoanel_rules.py` com funções puras de regras.
    2. Crie `src/reports/rodoanel.py` herdando de `BaseReport`.
    3. Registre a nova classe em `src/reports/factory.py` no dicionário `_registry`.
    4. **Nenhuma linha de código existente em CRA, CRC ou SOCICAM é tocada!**

### 2.3. L - Liskov Substitution Principle (Substituição de Liskov)
* Todas as classes derivadas de `BaseReport` devem honrar fielmente os contratos estabelecidos:
  - Métodos como `get_capa_titulos()`, `get_abbreviations()`, `render_quadros()` devem retornar os tipos esperados e nunca lançar exceções inesperadas por contratos não atendidos.
  - Uma chamada genérica `report.render_quadros(doc, row, nc_df, ...)` opera identicamente para qualquer modalidade.

### 2.4. I - Interface Segregation Principle (Segregação de Interfaces)
* Em vez de uma interface monolítica pesada, o sistema em [report_contracts.py](file:///c:/Users/pedri/Desktop/vscode/github-team/geradorRelatorios/src/core/interfaces/report_contracts.py) segrega o comportamento em protocolos enxutos (`typing.Protocol`):
  - `ICapaConfig`: Apenas títulos e processos da capa.
  - `ISumarioConfig`: Apenas abreviaturas e tópicos.
  - `IQuadroConfig`: Apenas cabeçalhos e tabelas de achados.
  - `IApendiceConfig`: Apenas memorial fotográfico.
  - `IFinalizacaoConfig`: Apenas determinações, recomendações e conclusões.
  - `IReportContract`: Agrega todos os papéis apenas para o orquestrador consolidado.

### 2.5. D - Dependency Inversion Principle (Inversão de Dependência)
* Módulos de alto nível não dependem de implementações concretas:
  - O gerador de relatórios em [report.py](file:///c:/Users/pedri/Desktop/vscode/github-team/geradorRelatorios/src/report.py) consome instâncias através do `get_report(key)` da fábrica ([factory.py](file:///c:/Users/pedri/Desktop/vscode/github-team/geradorRelatorios/src/reports/factory.py)), dependendo da abstração `BaseReport`.

---

## 🧊 3. Imutabilidade e Value Objects (`frozen=True`)

O estado de uma vistoria não pode sofrer mutações colaterais durante o pipeline de renderização:

```python
from dataclasses import dataclass, field
from typing import Tuple, Dict, Any

@dataclass(frozen=True)
class NaoConformidadeRecord:
    """Entidade pura e imutável. Tentativas de alterar atributos em tempo de execução
    lançam FrozenInstanceError."""
    id_fisc: str
    numero: int
    trecho: str
    identificacao: str
    descricao: str
    foto: str
    direcao_faixa: str = ""
    fundamento: str = ""
    determinacao: str = ""
    situacao: str = "Pendente"
    is_ponto_atencao: bool = False
    codigo: str = ""
```

* **Benefício:** Elimina bugs difíceis de rastrear onde uma função de formatação alterava uma coluna do DataFrame em memória e contaminava exibições subsequentes.
* **Coleções:** Use `Tuple` em vez de `List` dentro de dataclasses congeladas para garantir imutabilidade profunda.
