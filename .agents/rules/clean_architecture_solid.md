# Regras Mandatórias: Clean Architecture, SOLID & Engenharia de Código

Este documento define as regras inegociáveis que todo código implementado neste repositório deve seguir rigorosamente.

---

## 🏛️ 1. Fronteiras de Camadas da Clean Architecture
1. **Núcleo de Domínio Puro (`src/core/`):**
   - **PROIBIÇÃO TOTAL:** `src/core/` JAMAIS deve importar `streamlit`, `docx`, `openpyxl`, `tempfile` ou manipular janelas/interfaces.
   - Todo arquivo em `src/core/rules/` deve conter apenas **funções puras e determinísticas** (mesma entrada $\to$ mesma saída, zero *side-effects*).
2. **Camada de Relatórios (`src/reports/`):**
   - Responsável exclusiva por orquestrar tabelas, parágrafos, cabeçalhos e estilos em documentos Word (`python-docx`).
   - Não deve conter regras de negócio de cálculo de estacas ou siglas contratuais — deve consumir as regras puras de `src/core/rules/`.
3. **Camada de Apresentação (`src/ui/`, `src/app.py`):**
   - Cuida unicamente de captura de dados, botões, modais e exibição visual.
   - Nenhuma lógica de Word ou validação de regras de concessão pode ser codificada diretamente em telas ou manipuladores de eventos do Streamlit.

---

## ⚖️ 2. Princípios SOLID Aplicados
1. **Responsabilidade Única (SRP):**
   - Se uma função/classe precisa mudar por mais de um motivo (ex: alteração na regra da CRA E alteração no layout da tabela Word), ela DEVE ser decomposta em duas.
2. **Aberto/Fechado (OCP):**
   - A inclusão de novas concessões ou modelos de relatório deve ser realizada criando subclasses de `BaseReport` e registrando no dicionário de `src/reports/factory.py`, sem adicionar novos `elif` no fluxo existente.
3. **Substituição de Liskov (LSP):**
   - Toda implementação concreta de relatório deve honrar fielmente os contratos estabelecidos pela classe base `BaseReport` e pelas interfaces em `src/core/interfaces/report_contracts.py`.
4. **Segregação de Interfaces (ISP):**
   - Utilize as interfaces segregadas de contrato (`ICapaConfig`, `ISumarioConfig`, `IQuadroConfig`, `IApendiceConfig`, `IFinalizacaoConfig`) em vez de forçar consumidores a depender de métodos desnecessários.
5. **Inversão de Dependências (DIP):**
   - O orquestrador central deve interagir com abstrações de relatórios e protocolos, nunca instanciar classes de relatório acopladas no fluxo principal.

---

## 🧊 3. Imutabilidade e Robustez de Dados
1. **Entidades Confeccionadas como Dataclasses Congeladas:**
   - Todo modelo de dados em `src/core/models/entities.py` deve utilizar `@dataclass(frozen=True)`.
   - Modificações de estado devem gerar novas instâncias (`replace` ou construtor), prevenindo mutações colaterais.
2. **Tipagem Estrita e Type Hints:**
   - Todos os métodos, parâmetros e retornos de funções devem conter anotações de tipo explícitas (`from typing import Optional, List, Dict, Tuple, Union`).

---

## 🧭 4. Integridade Canônica dos 6 Estados
1. **CRA:** Cumprir codificação `CRA.ST{subtrecho}.{estacas}/{ano}.{seq:03d}` e segregar Não Conformidades de Pontos de Atenção.
2. **CRC:** Cumprir regra gramatical feminina obrigatória `1 (uma)`, `2 (duas)` em conclusões de achados contratuais.
3. **SOCICAM:** Eliminar termos viários (sem pistas, faixas ou estacas); operar com setores prediais e normalizar nomes de terminais conforme o contexto (introdução vs conclusão).
4. **Monitoramento:** Extrair dados de ciclo anterior ($N_{prev} \to N_{curr}$), números SEI, ofícios e confrontar com novas evidências fotográficas.
