# Catálogo Completo de Regras de Negócio: Os 6 Estados Regulatórios

Este manual compila todas as regras de negócio canônicas que o **Desenvolvedor** deve satisfazer em suas implementações.

---

## 🗺️ Matriz das 6 Modalidades

```text
                     [ VISTORIA INICIAL ]                [ AUDITORIA DE PENDÊNCIAS ]
                     1. CRA Fiscalização                 2. CRA Monitoramento
                     3. CRC Fiscalização                 4. CRC Monitoramento
                     5. SOCICAM Fiscalização             6. SOCICAM Monitoramento
```

---

## 🚗 1. Modalidade CRA (Concessionária Rota do Atlântico)

Regras implementadas puramente em `src/core/rules/cra_rules.py`.

### 1.1. CRA Fiscalização
* **Entidades Viárias:** Pistas (Norte, Sul), Faixas (Faixa 1, Faixa 2, Acostamento, Canteiro Central), Subtrechos, Estacas métricas.
* **Algoritmo de Codificação CRA:**
  - Máscara canônica: `CRA.ST{subtrecho}.{estacas}/{ano}.{seq:03d}`
  - Exemplo: `CRA.ST601.2790-2794/2026.001`
  - Se a entrada já contiver offset inicial (ex: `.../2026.003`), a sequência calcula: `offset + seq_idx - 1`.
* **Diferenciação Crítica de Achados:**
  - **Não Conformidade (NC):** Infração contratual grave que gera determinação formal de correção com prazo estrito.
  - **Ponto de Atenção (PA):** Defeito incipiente ou desgaste preventivo que gera recomendação técnica.

### 1.2. CRA Monitoramento
* **Entrada:** Upload do relatório anterior (`.docx`) ou planilha de acompanhamento.
* **Evolução de Ciclo:**
  - O número da vistoria evolui: $N_{curr} = N_{prev} + 1$.
  - Extração mandatória: Processo SEI anterior, Ofício de Notificação e Carta Resposta da Concessionária.
* **Auditoria das Irregularidades:**
  - Cada achado anterior é classificado como: `Saneada`, `Parcialmente Saneada` ou `Pendente`.
  - As novas fotos de campo devem ser associadas comprovando a evolução de cada item.

---

## 🌴 2. Modalidade CRC (Concessionária Rota dos Coqueiros - Paiva)

Regras implementadas puramente em `src/core/rules/crc_rules.py`.

### 2.1. CRC Fiscalização
* **Contrato:** Parceria Público-Privada CGPE – 001/2006 (PE-024).
* **Regra Gramatical Mandatória (Extenso Feminino):**
  - Todas as conclusões e textos síntese de Não Conformidades DEVEM expressar a contagem por extenso no gênero feminino:
    - 1 achado: `"1 (uma)"`
    - 2 achados: `"2 (duas)"`
    - 3 achados: `"3 (três)"` ... `"10 (dez)"`
  - Implementado em `formatar_extenso_feminino_achados(total_ncs)`. É terminantemente proibido exibir `"1 (um) não conformidade"`.
* **Cláusulas Específicas:** Vinculação com o Anexo V (Indicadores de Desempenho e Qualidade de Serviço da Concessão).

### 2.2. CRC Monitoramento
* **Estrutura de Rastreabilidade:**
  - Cruzamento de dados de ofícios regulatórios e pareceres de recurso interpostos pela Rota dos Coqueiros.
  - Comparativo temporal de saneamento exibido no Quadro 1.

---

## 🏢 3. Modalidade SOCICAM (Terminais Rodoviários de Pernambuco)

Regras implementadas puramente em `src/core/rules/socicam_rules.py`.

### 3.1. SOCICAM Fiscalização
* **Contrato:** Concessão de Serviço Público Nº 1.041.080/08.
* **Abrangência Predial:**
  1. TIP (Terminal Rodoviário de Passageiros do Recife)
  2. Terminal Rodoviário de Caruaru
  3. Terminal Rodoviário de Garanhuns
  4. Terminal Rodoviário de Petrolina
* **PROIBIÇÃO DE TERMOS VIÁRIOS:**
  - A interface e os dados da SOCICAM **NÃO possuem pistas, faixas de rolamento, estacas ou quilômetros**.
  - Os setores de localização são estritamente prediais:
    - Plataformas de Embarque e Desembarque
    - Sanitários Públicos e Fraldários
    - Saguão de Espera e Circulação
    - Bilheterias e Guarda-volumes
    - Acessibilidade (piso tátil, rampas, escadas rolantes, elevadores)
    - Estacionamento e baias de táxi
* **Normalização Rigorosa de Nomes dos Terminais:**
  - **Títulos e Introdução:** Deve usar `normalizar_nome_terminal_rodoviario(local)`:
    - `"TIP"` $\to$ `"Terminal Rodoviário de Passageiros do Recife (TIP)"`
    - `"Petrolina"` $\to$ `"Terminal Rodoviário de Petrolina"`
  - **Conclusões:** Deve usar `normalizar_nome_terminal_curto(local)`:
    - `"TIP"` $\to$ `"Terminal de Passageiros do Recife (TIP)"`
    - `"Petrolina"` $\to$ `"Terminal de Petrolina"`

### 3.2. SOCICAM Monitoramento
* **Quadro 1 Padronizado:**
  A tabela de auditoria possui 3 colunas calibradas em polegadas no Word:
  1. `NÃO CONFORMIDADE` (largura: ~3.20 polegadas) – identificação da NC anterior.
  2. `INFORMAÇÃO SOCICAM` (largura: ~3.20 polegadas) – contestação, ação informada ou plano de obras da concessionária.
  3. `SITUAÇÃO` (largura: ~1.17 polegadas) – veredito do auditor (`SANEADA` ou `PENDENTE`).

---

## 💾 4. Isolamento e Persistência de Estado

* O sistema mantém armazenamento atômico e independente por modalidade:
  - Arquivo de Sessão: `geradorRelatorios/<modalidade>.json`
  - Mídia Física: `geradorRelatorios/<modalidade>/midia/fotos/`
* Ao alternar de modalidade no menu superior:
  1. O estado da modalidade ativa é serializado e salvo em disco.
  2. A memória volátil de fotos e tabelas é resetada.
  3. Os dados da nova modalidade são restaurados.
* **Violação Crítica:** Permitir que fotos ou cadastros de CRA apareçam em SOCICAM constitui bug severo de isolamento de sessão.
