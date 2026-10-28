# Engenharia de Testes (TDD / BDD) & Conformidade LGPD

Este documento orienta o **Desenvolvedor** na formulação de testes automatizados e no cumprimento das exigências de privacidade da LGPD.

---

## 🧪 1. Desenvolvimento Orientado a Testes (TDD) e Comportamento (BDD)

Todas as funções puras de negócio em `src/core/rules/` devem ser desenvolvidas ou refatoradas guiadas por testes unitários com **pytest**.

### 1.1. Cenários BDD Canônicos (Exemplos Práticos)

#### Cenário 1: Codificação CRA com Offset Sequencial
```gherkin
Funcionalidade: Geração de Código Identificador CRA
  Como analista regulador da rodovia
  Quero que o código do achado siga a máscara contratual
  Para permitir auditoria sequencial por estaca

  Cenário: Incremento correto de sequência com offset inicial
    Dado que a base do subtrecho é "CRA.ST601.2790-2794"
    E a data da fiscalização é "15/03/2026"
    E o índice sequencial é 3
    Quando a função gerar_codigo_cra for invocada
    Então o código retornado deve ser "CRA.ST601.2790-2794/2026.003"
```

#### Cenário 2: Concordância Gramatical Feminina no Relatório CRC
```gherkin
Funcionalidade: Numerais por Extenso Feminino em Conclusões CRC
  Como revisor técnico da Rota dos Coqueiros
  Quero que a quantidade de Não Conformidades seja grafada no feminino
  Para atender à norma contratual CGPE-001/2006

  Cenário: Conclusão com exatamente 1 não conformidade
    Dado que o total de Não Conformidades identificadas é 1
    Quando a função formatar_extenso_feminino_achados for invocada
    Então o texto gerado deve ser "1 (uma)"
    E não deve conter a expressão "1 (um)"

  Cenário: Conclusão com exatamente 2 não conformidades
    Dado que o total de Não Conformidades identificadas é 2
    Quando a função formatar_extenso_feminino_achados for invocada
    Então o texto gerado deve ser "2 (duas)"
```

#### Cenário 3: Normalização de Nomes de Terminais SOCICAM
```gherkin
Funcionalidade: Normalização de Nomes Prediais SOCICAM
  Como fiscal de terminais rodoviários
  Quero que os nomes dos terminais sejam padronizados na introdução e na conclusão
  Para manter a uniformidade documental em processos SEI

  Cenário: Entrada com sigla "TIP" para introdução
    Dado o valor de local "TIP"
    Quando a função normalizar_nome_terminal_rodoviario for invocada
    Então o resultado deve ser "Terminal Rodoviário de Passageiros do Recife (TIP)"

  Cenário: Entrada com sigla "TIP" para conclusões
    Dado o valor de local "TIP"
    Quando a função normalizar_nome_terminal_curto for invocada
    Então o resultado deve ser "Terminal de Passageiros do Recife (TIP)"
```

---

## 🐍 2. Estrutura Padrão de Testes com Pytest

Ao codificar uma regra de negócio, crie testes isolados e determinísticos:

```python
import pytest
from core.rules.crc_rules import formatar_extenso_feminino_achados
from core.rules.socicam_rules import normalizar_nome_terminal_rodoviario, normalizar_nome_terminal_curto
from core.rules.cra_rules import gerar_codigo_cra

def test_crc_extenso_feminino():
    assert formatar_extenso_feminino_achados(1) == "1 (uma)"
    assert formatar_extenso_feminino_achados(2) == "2 (duas)"
    assert formatar_extenso_feminino_achados(0) == "0 (zero)"

def test_socicam_normalizacao_terminal():
    assert normalizar_nome_terminal_rodoviario("TIP") == "Terminal Rodoviário de Passageiros do Recife (TIP)"
    assert normalizar_nome_terminal_curto("TIP") == "Terminal de Passageiros do Recife (TIP)"
    assert normalizar_nome_terminal_rodoviario("Petrolina") == "Terminal Rodoviário de Petrolina"
    assert normalizar_nome_terminal_curto("Petrolina") == "Terminal de Petrolina"

def test_cra_geracao_codigo():
    assert gerar_codigo_cra("CRA.ST601.100-200", "2026-05-10", 1) == "CRA.ST601.100-200/2026.001"
```

---

## 🔒 3. Diretrizes Práticas de Conformidade com a LGPD

1. **Anonimização no Memorial Fotográfico:**
   - Fotos coletadas em terminais ou rodovias públicas que capturem transeuntes, passageiros (especialmente menores de idade) ou placas legíveis de veículos civis devem ser sinalizadas para desfoque.
2. **Minimização de Dados Pessoais:**
   - Registros de responsáveis fiscais e coordenadores devem restringir-se a: `Nome Completo` e `Cargo/Matrícula Funcional`.
   - NUNCA colete ou exiba CPF, endereço residencial ou telefone pessoal em relatórios ou metadados da aplicação.
3. **Soberania do Cache Local:**
   - Todos os dados gerados temporariamente ficam sob `geradorRelatorios/`, explicitamente cobertos no `.gitignore`.
   - Nenhuma foto ou documento de vistoria deve ser transmitido para APIs externas não autorizadas.
