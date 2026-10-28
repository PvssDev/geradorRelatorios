# Referência Aprofundada: Domínio e os 6 Estados de Relatórios

Este documento fornece a base de conhecimento técnica e de domínio para o Tech Lead auditar as 6 modalidades suportadas pelo Gerador de Relatórios.

---

## 🏗️ 1. Matriz de Entidades e Fluxo de Dados

A arquitetura de dados baseia-se em objetos de valor imutáveis localizados em `src/core/models/entities.py`:
* **`FotoEvidencia`:** Value Object imutável (`@dataclass(frozen=True)`). Contém `nome_arquivo`, `path_ou_bytes`, `timestamp`, `legenda` e metadados adicionais.
* **`NaoConformidadeRecord`:** Representa um achado de campo (NC ou Ponto de Atenção). Contém `id_fisc`, `numero`, `trecho`, `identificacao`, `descricao`, `foto`, `direcao_faixa`, `fundamento`, `determinacao`, `situacao`, `is_ponto_atencao`, `codigo`, `observacoes` e tupla de `fotos_evidencia`.
* **`FiscalizacaoRecord`:** Metadados da vistoria (`id_fisc`, `contrato`, `data`, `hora`, `cidade`, `local`, `responsaveis`, `coordenador`, `periodo`).
* **`ResumoAchados`:** Agrupamento pré-calculado em tempo $O(N)$ de NCs e Pontos de Atenção para otimizar renderizações.
* **`MetadadosMonitoramento`:** Dados do ciclo anterior (`n_prev`, `n_curr`, `processo_sei_prev`, `oficio_num_prev`, etc.).

---

## 🚗 2. Rodovias Concedidas: CRA e CRC

### CRA (Rota do Atlântico)
* **Contrato:** Rodovias de Suape (VPE-052, VPE-034, etc.).
* **Codificação:**
  - Padrão: `{base}/{ano}.{sequencial:03d}`
  - Exemplo: `CRA.ST601.2790-2794/2026.001`
  - Se a base informada já contiver ano/offset, incrementa a partir do offset inicial: `offset + seq_idx - 1`.
  - Função pura: `gerar_codigo_cra()` em `src/core/rules/cra_rules.py`.
* **Faixas e Direções:**
  - Direções: `Norte`, `Sul`, `Leste`, `Oeste`.
  - Faixas viárias: `Faixa 1` (rápida), `Faixa 2` (lenta), `Acostamento`, `Canteiro Central`, `Faixa de Domínio`.
* **Monitoramento CRA:**
  - Extração de itens pendentes anteriores e relacionamento com as fotos de vistoria atual.

### CRC (Rota dos Coqueiros - Paiva)
* **Contrato:** CGPE-001/2006 (PE-024).
* **Particularidade Linguística:**
  - Função pura: `formatar_extenso_feminino_achados(total_ncs: int)` em `src/core/rules/crc_rules.py`.
  - Exemplo: `1` -> `"1 (uma)"`, `2` -> `"2 (duas)"`, `3` -> `"3 (três)"`.
  - Caso `total_ncs == 0`: `"0 (zero)"`.
  - Regra gramatical mandatória nas minutas oficiais da agência para concordar com "Não Conformidade".
* **Monitoramento CRC:**
  - Comparativo temporal de NCs de pavimentação, iluminação, praça de pedágio e via parque.

---

## 🏢 3. Terminais Rodoviários: SOCICAM

### Particularidades de Negócio
* **Contrato:** 1.041.080/08.
* **Locais Regulados:**
  1. Terminal Rodoviário de Passageiros do Recife (TIP)
  2. Terminal Rodoviário de Caruaru
  3. Terminal Rodoviário de Garanhuns
  4. Terminal Rodoviário de Petrolina
* **Normalização de Nomes:**
  - `normalizar_nome_terminal_rodoviario()`: Garante prefixo oficial `Terminal Rodoviário de...` nas introduções.
  - `normalizar_nome_terminal_curto()`: Formata como `Terminal de...` nas conclusões.
* **Campos e Vocabulário:**
  - Proibido o uso de termos viários (pistas, estacas, acostamento).
  - Uso estrito de setores prediais: Plataformas, Sanitários, Saguão, Bilheterias, Acessibilidade.
* **SOCICAM Monitoramento (Quadro 1):**
  - Tabela Word com 3 colunas específicas:
    1. `NÃO CONFORMIDADE` (largura: 3.20 pol)
    2. `INFORMAÇÃO SOCICAM` (largura: 3.20 pol)
    3. `SITUAÇÃO` (largura: 1.17 pol)
  - Registra o confronto entre a resposta da concessionária e a constatação da equipe de regulação.

---

## 🔄 4. Diferenças de Input: Fiscalização vs Monitoramento

```text
+------------------------------+-------------------------------------+-------------------------------------+
| Característica               | Fiscalização                        | Monitoramento                       |
+------------------------------+-------------------------------------+-------------------------------------+
| Origem dos Dados             | Vistoria primária em campo          | Relatório anterior (.docx) + Fotos  |
| Entrada de Metadados         | Cadastro manual da vistoria         | Extração automática via parser      |
| Entrada de Achados           | Cadastro do zero de NCs e PAs       | Importação do Quadro 1 anterior     |
| Fotos                        | Novas evidências diretas            | Relacionamento com NCs anteriores   |
| Status dos Achados           | Sempre pendentes / sob apuração     | Saneada, Parcialmente ou Pendente   |
| Documento de Saída           | Relatório Base de Fiscalização      | Relatório de Acompanhamento         |
+------------------------------+-------------------------------------+-------------------------------------+
```
