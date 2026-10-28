# Matriz Canônica de Domínio: As 6 Modalidades do Gerador de Relatórios

Este documento detalha as especificidades de negócio e algoritmos para cada um dos 6 estados de geração de relatórios. O Tech Lead deve consultar e fazer valer estas regras em qualquer análise de código.

---

## 🗺️ Visão Geral das Modalidades

O sistema opera na interseção entre 3 contratos de concessão regulados e 2 naturezas de inspeção:

```text
               ┌───────────────────┴───────────────────┐
               ▼                                       ▼
       [ FISCALIZAÇÃO ]                        [ MONITORAMENTO ]
       (Vistoria Inicial)                      (Auditoria de Pendências)
       
  1. CRA Fiscalização                     2. CRA Monitoramento
     (Rodovia Rota do Atlântico)             (Acompanhamento CRA)
     
  3. CRC Fiscalização                     4. CRC Monitoramento
     (Rodovia Rota dos Coqueiros)            (Acompanhamento CRC)
     
  5. SOCICAM Fiscalização                 6. SOCICAM Monitoramento
     (Terminais Rodoviários PE)              (Acompanhamento SOCICAM)
```

---

## 🚗 1. Modalidade CRA (Concessionária Rota do Atlântico)

### Escopo Viário
- Concessão de rodovias do Complexo Industrial Portuário de Suape.
- Entidades de tráfego: Pistas expressas e locais, faixas (1, 2, acostamento, canteiro central), estacas métricas.

### 1.1. CRA Fiscalização
- **Entradas do Usuário:**
  - Metadados da equipe: data, hora, cidade, local, responsáveis e coordenador.
  - Achados de campo: tabela contendo `Trecho`, `Identificação`, `Descrição`, `Foto(s)`, `Faixa`, `Fundamento`, `Determinação`, `Codificação`.
  - Classificação obrigatória: **Não Conformidade (NC)** (infração) vs **Ponto de Atenção (PA)** (advertência/reparo preventivo).
- **Regra de Codificação CRA:**
  - Máscara: `CRA.ST{subtrecho}.{estacas}/{ano}.{seq:03d}`
  - Implementada de forma imutável e pura em `src/core/rules/cra_rules.py`.
- **Formatação do Documento:**
  - Cabeçalho específico com brasão e logotipo institucional da agência e da CRA.
  - Quadros de Achados com memorial fotográfico pareado (1 ou 2 fotos por página conforme layout).

### 1.2. CRA Monitoramento
- **Entradas do Usuário:**
  - Upload obrigatório do relatório anterior (`.docx`) ou planilha de acompanhamento.
  - Extração de metadados do ciclo anterior: número da vistoria ($N-1$), número do processo SEI, ofício regulatório de notificação, carta resposta da concessionária.
- **Lógica de Auditoria:**
  - O analista inspeciona as NCs abertas no ciclo anterior e atribui novo status:
    - `Saneada`
    - `Parcialmente Saneada`
    - `Não Saneada / Pendente`
  - Fotos de monitoramento são vinculadas aos achados originais para comprovação do saneamento ou persistência da falha.

---

## 🌴 2. Modalidade CRC (Concessionária Rota dos Coqueiros - Paiva)

### Escopo Viário
- Contrato de Concessão Patrocinada CGPE – 001/2006 (PE-024).
- Rodovia com praça de pedágio, ponte estaiada e trecho de praia/reserva.

### 2.1. CRC Fiscalização
- **Peculiaridade Gramatical Mandatória:**
  - As conclusões do relatório CRC exigem a redação de quantidades de Não Conformidades com numerais por extenso no gênero feminino:
    - `1 (uma)`
    - `2 (duas)`
    - `3 (três)` ... `10 (dez)`
  - Implementada em `formatar_extenso_feminino_achados()` em `src/core/rules/crc_rules.py`.
- **Classificação:**
  - Também diferencia NCs de Pontos de Atenção, com textos de determinação/recomendação alinhados às cláusulas do contrato CGPE – 001/2006.

### 2.2. CRC Monitoramento
- **Fluxo de Dados:**
  - Carregamento de relatório de fiscalização prévio ou monitoramento imediatamente anterior.
  - Rastreamento dos ofícios de cobrança emitidos pela agência e cartas de contestação da concessionária.
  - Montagem de tabela comparativa de evolução temporal das irregularidades.

---

## 🏢 3. Modalidade SOCICAM (Terminais Rodoviários de Pernambuco)

### Escopo Predial
- Contrato de Concessão de Serviço Público Nº 1.041.080/08.
- Abrange 4 terminais rodoviários:
  - **TIP** (Terminal Rodoviário de Passageiros do Recife)
  - **Terminal de Caruaru**
  - **Terminal de Garanhuns**
  - **Terminal de Petrolina**

### 3.1. SOCICAM Fiscalização
- **Diferenças Críticas de Entrada:**
  - **ZERO termos viários:** Não existem pistas, acostamentos ou quilometragens rodoviárias.
  - Os campos de localização são estruturados por setores prediais:
    - Plataformas de Embarque e Desembarque
    - Sanitários Públicos e Fraldários
    - Saguão Principal e Áreas de Espera
    - Bilheterias e Guarda-volumes
    - Acessibilidade (piso tátil, rampas, elevadores)
    - Estacionamento de veículos e táxis
- **Normalização de Títulos e Textos:**
  - Em parágrafos introdutórios: `Terminal Rodoviário de Passageiros do Recife (TIP)` ou `Terminal Rodoviário de Petrolina`.
  - Em conclusões: `Terminal do TIP` ou `Terminal de Petrolina`.
  - Implementada em `normalizar_nome_terminal_rodoviario()` e `normalizar_nome_terminal_curto()` em `src/core/rules/socicam_rules.py`.
- **Dicionário de Achados Personalizados:**
  - Utiliza base própria carregada via `carregar_custom_ncs_socicam()` com infrações prediais típicas.

### 3.2. SOCICAM Monitoramento
- **Estrutura Estrita do Quadro 1:**
  - Tabela com 3 colunas específicas e larguras calibradas:
    1. `NÃO CONFORMIDADE` (largura ~3.20 polegadas)
    2. `INFORMAÇÃO SOCICAM` (argumentação ou ação informada pela concessionária em resposta oficial, largura ~3.20 polegadas)
    3. `SITUAÇÃO` (avaliação do auditor: Saneada / Pendente, largura ~1.17 polegadas)
  - Implementada em `src/reports/socicam_monitoramento.py` e `src/reports/templates/socicam_monitoramento_templates.py`.

---

## 💾 4. Arquitetura de Isolamento de Sessão

Cada uma das 6 modalidades possui seu próprio armazenamento persistente:
- **Cache de Sessão:** `geradorRelatorios/<modalidade>.json` (ex: `socicam_monitoramento.json`)
- **Mídia Física:** `geradorRelatorios/<modalidade>/midia/fotos/` e `arquivos/`

Ao alternar de modalidade no menu do Streamlit, o sistema deve:
1. Salvar o estado da modalidade anterior.
2. Limpar a memória volátil de fotos e tabelas.
3. Restaurar o cache e fotos da nova modalidade selecionada.
4. Qualquer tentativa de misturar dados de uma modalidade em outra é considerada bug grave de regressão.
