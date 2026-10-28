# Padrões de Engenharia de Software: SOLID, BDD/TDD, LGPD e Streamlit

Este documento define os critérios de excelência técnica que o Tech Lead deve exigir em todas as análises de código do projeto **Gerador de Relatórios**.

---

## 🏛️ 1. Princípios SOLID Aplicados ao Projeto

### 1.1. S — Single Responsibility Principle (Princípio da Responsabilidade Única)
* **Violação Comum:** Arquivos como `app.py` acumulando lógica de widgets, validação de regras de trânsito, cálculo de estacas e geração de tabelas Word.
* **Padrão Exigido:**
  - `src/ui/`: Apenas renderização visual, formulários, modais e captura de eventos.
  - `src/core/rules/`: Regras de negócio puras (cálculo de códigos, filtros, normalizações) sem dependência de Streamlit.
  - `src/reports/`: Montagem do documento `docx` através da biblioteca `python-docx`.
  - `src/services/`: Persistência em disco, leitura de imagens e cache.

### 1.2. O — Open/Closed Principle (Princípio Aberto/Fechado)
* **Violação Comum:** Inclusão de um novo contrato (ex: Concessão Ferroviária) adicionando `if contrato == "FERROVIA": ...` em dezenas de métodos.
* **Padrão Exigido:**
  - Extensão via polimorfismo: herdar de `BaseReport` em `src/reports/base.py`.
  - Registro dinâmico na `src/reports/factory.py`.
  - O motor de compilação deve operar sobre a abstração de `BaseReport`, permanecendo fechado para modificações estruturais.

### 1.3. L — Liskov Substitution Principle (Princípio da Substituição de Liskov)
* **Padrão Exigido:**
  - Qualquer classe de relatório (`CraReport`, `SocicamReport`, `CrcMonitoramentoReport`) deve poder ser instanciada e executada pela mesma assinatura `gerar_relatorio(dados, fotos, output_path)` sem quebrar pressupostos ou lançar exceções inesperadas.

### 1.4. I — Interface Segregation Principle (Princípio da Segregação de Interfaces)
* **Padrão Exigido:**
  - Evitar objetos de transferência com centenas de campos não utilizados.
  - Modelos em `src/core/models/entities.py` devem ser coesos. Exemplo: `FotoEvidencia` contém apenas o necessário para a mídia; `MetadadosMonitoramento` contém apenas atributos pertinentes à extração do ciclo anterior.

### 1.5. D — Dependency Inversion Principle (Princípio da Inversão de Dependência)
* **Padrão Exigido:**
  - Módulos de domínio (`src/core/`) nunca devem importar módulos de infraestrutura (`src/ui/`, `streamlit`).
  - Funções de cálculo de regras devem receber dados simples (dicionários, dataclasses, tuplas) e retornar novos dados imutáveis, nunca depender de `st.session_state`.

---

## 🧪 2. BDD (Behavior-Driven Development) & TDD (Test-Driven Development)

### 2.1. Cultura de TDD para Regras de Domínio
Antes de qualquer alteração nas regras de codificação, gramática ou extração:
1. **Red:** Escrever o teste unitário (com `pytest`) expressando a regra de negócio esperada.
2. **Green:** Escrever o código mínimo em `src/core/rules/` para fazer o teste passar.
3. **Refactor:** Limpar e otimizar mantendo a pureza e a tipagem.

### 2.2. Especificação BDD em Cenários Gherkin
Toda nova funcionalidade complexa deve ter seu comportamento previamente validado através de cenários:

```gherkin
Cenário: Geração do código sequencial para CRA em novo ano
  Dado que o analista está no relatório CRA
  E a data da fiscalização é "15/03/2026"
  E a base fornecida é "CRA.ST601.2790-2794"
  Quando o sistema gerar a codificação para o primeiro achado (seq_idx = 1)
  Então o código retornado deve ser exatamente "CRA.ST601.2790-2794/2026.001"
```

```gherkin
Cenário: Redação de conclusão gramatical feminina no relatório CRC
  Dado que o relatório da Rota dos Coqueiros (CRC) possui 2 Não Conformidades registradas
  Quando a seção de conclusões for construída
  Então o texto de quantitativo deve formatar como "2 (duas) não conformidades"
  E nunca deve formatar como "2 (dois)"
```

---

## 🔒 3. LGPD (Lei Geral de Proteção de Dados - Lei 13.709/2018)

Como o sistema lida com fiscalizações públicas e documentos probatórios de concessões, as seguintes salvaguardas são mandatórias:

### 3.1. Tratamento de Imagens e Memoriais Fotográficos
* **Rostos de Pessoas:** Vistorias em terminais rodoviários (SOCICAM) registram rotineiramente passageiros, funcionários e menores de idade em áreas comuns. As fotos de evidência técnica devem focar exclusivamente na não conformidade física (ex: piso quebrado, extintor vencido). Se inevitável a captura de transeuntes, o Tech Lead deve recomendar o desfoque de rostos.
* **Placas de Veículos:** Vistorias rodoviárias (CRA/CRC) não devem evidenciar placas de veículos particulares de forma legível, a menos que o veículo seja o próprio objeto de infração contratual de fiscalização de tráfego regulado.

### 3.2. Minimização de Dados Cadastrais
* O cadastro de analistas, coordenadores e fiscais deve conter apenas os dados estritamente necessários para a autenticidade e validade jurídica do ato administrativo: Nome Completo e Função/Cargo.
* É expressamente vedado armazenar CPF, RG, endereços residenciais ou dados bancários no sistema.

### 3.3. Segurança e Retenção Local
* Os relatórios em geração e os caches em disco (`geradorRelatorios/*.json` e mídias) residem localmente na máquina do analista.
* Todos os diretórios de saída e caches locais devem constar no `.gitignore` para prevenir qualquer vazamento acidental em repositórios remotos.

---

## ⚡ 4. Ciclo de Vida do Streamlit e Otimização

* **O Modelo de Re-run:** A cada widget acionado pelo usuário, o Streamlit reexecuta o script do início ao fim.
* **Regras de Performance:**
  - Compressão de imagens (via Pillow) deve ocorrer na importação ou de forma lazy, nunca dentro do loop de renderização da UI.
  - Uso mandatório de `@st.cache_data` para leitura de arquivos estáticos (como brasões e logos em `assets/`).
  - Proteção contra condições de corrida nas alternâncias de abas/menus, garantindo que o `salvar_sessao_local()` seja executado antes da troca do par `(tipo_relatorio, categoria_relatorio)`.
