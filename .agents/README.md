# 🤖 Ecossistema de Agentes (.agents) - Gerador de Relatórios

Bem-vindo à pasta `.agents` do projeto **Gerador de Relatórios de Fiscalização e Monitoramento**.

Este diretório contém a infraestrutura de agentes inteligentes, regras de arquitetura, perfis especializados e competências (*skills*) que auxiliam a equipe no desenvolvimento, revisão de código e governança técnica do sistema.

---

## 🏛️ Agentes do Ecossistema

O ecossistema conta com perfis especializados para diferentes papéis técnicos:

1. **Tech Lead & Auditor de Arquitetura (`tech-lead-analyst`):**
   - Agente de governança técnica sênior. Foco em arquitetura SOLID, BDD/TDD, conformidade LGPD e integridade dos 6 estados regulatórios de relatórios.
   - **Princípio:** "Analisa, audita e orienta; não codifica diretamente a aplicação."

2. **Streamlit Specialist & Design System (`streamlit`):**
   - Especialista na camada visual, estética, Design System corporativo, botões, assets gráficos, injeção de CSS e ciclo de vida reativo do Streamlit.
   - **Princípio:** "Garante interfaces premium, harmonia estética, microinterações fluidas e desacoplamento do frontend."

3. **Software Engineer & Core Developer (`developer`):**
   - Engenheiro de implementação full-stack. Especialista em Clean Architecture, SOLID, SRP, regras de negócio dos 6 estados, imutabilidade de modelos e testes automatizados.
   - **Princípio:** "Codifica sempre respeitando as fronteiras de Clean Architecture, separação de responsabilidades e pureza do domínio."

---

## 📁 Estrutura do Diretório `.agents`

```text
.agents/
├── README.md                                  # Este arquivo descritivo
├── AGENTS.md                                  # Diretriz mestre lida automaticamente pela IDE/Agente
├── rules/
│   ├── tech_lead.md                           # Protocolo de atuação, limites e checklist de revisão
│   ├── domain_rules.md                        # Referência canônica dos 6 estados de relatórios
│   ├── streamlit.md                           # Regras de governança de UI/UX, botões e tokens visuais
│   └── clean_architecture_solid.md            # Regras mandatórias de Clean Architecture e SOLID
└── skills/
    ├── tech-lead-analyst/
    │   ├── SKILL.md                           # Skill executável sob demanda do Tech Lead
    │   └── references/
    │       ├── domain_and_states.md           # Peculiaridades de entrada e regras (CRA, CRC, SOCICAM)
    │       └── engineering_standards.md       # SOLID, BDD/TDD, LGPD e ciclo Streamlit
    ├── streamlit/
    │   ├── SKILL.md                           # Skill executável sob demanda do Especialista Streamlit
    │   └── references/
    │       ├── design_system_and_tokens.md    # Paleta de cores, tipografia, ícones e glassmorphism
    │       ├── buttons_and_components.md      # Padrões de botões, chaves, diálogos e toasts
    │       └── assets_and_css_injection.md    # Texturas base64, componentes Swiper/FS e performance
    └── developer/
        ├── SKILL.md                           # Skill executável sob demanda do Desenvolvedor
        └── references/
            ├── clean_architecture_and_solid.md# Camadas, SOLID, protocolos e imutabilidade
            ├── domain_business_rules.md       # Regras dos 6 estados (CRA, CRC, SOCICAM)
            └── tdd_bdd_and_quality.md         # BDD, testes com pytest e conformidade LGPD
```

---

## 🧭 Os 6 Estados de Relatórios do Projeto

O Tech Lead domina a matriz de 3 concessões $\times$ 2 tipos de vistoria:

| Modalidade | Concessão / Objeto | Tipo de Vistoria | Peculiaridades de Entrada & Regras |
| :--- | :--- | :--- | :--- |
| **CRA Fiscalização** | Rodovia Rota do Atlântico | Fiscalização Inicial | Pistas (Norte/Sul), faixas, estacas/km. Codificação de achados: `CRA.ST.../ANO.SEQ`. Separação de NCs e PAs. |
| **CRA Monitoramento** | Rodovia Rota do Atlântico | Acompanhamento | Upload de relatório anterior (`.docx`/`.pdf`) ou planilha. Extração de variáveis SEI e status de saneamento. |
| **CRC Fiscalização** | Rodovia Rota dos Coqueiros (Paiva) | Fiscalização Inicial | Contrato CGPE-001/2006. Regra gramatical estrita: conclusões com extensos femininos (`1 (uma)`, `2 (duas)`). |
| **CRC Monitoramento** | Rodovia Rota dos Coqueiros (Paiva) | Acompanhamento | Rastreabilidade de ofícios e cartas anteriores. Confronto de fotos atuais com o Quadro 1 anterior. |
| **SOCICAM Fiscalização** | Terminais Rodoviários de PE | Fiscalização Inicial | Contrato 1.041.080/08 (TIP Recife, Caruaru, Garanhuns, Petrolina). Sem pista/faixa viária. Entradas focadas em setores prediais e sanitários. |
| **SOCICAM Monitoramento**| Terminais Rodoviários de PE | Acompanhamento | Quadro 1 específico: `NÃO CONFORMIDADE`, `INFORMAÇÃO SOCICAM`, `SITUAÇÃO`. Validação de defesas da concessionária. |

---

## 🚀 Como Interagir com o Tech Lead

Ao conversar com a IA neste projeto, solicite avaliações como:
* *"Analise este diff no módulo de monitoramento quanto a SOLID e possíveis regressões."*
* *"Como você estruturaria o BDD para a codificação automática de CRA?"*
* *"Esta nova tela fere a LGPD ao coletar fotos nos terminais da Socicam?"*
* *"Revise a integração de extração de SEI sob a ótica de Clean Code."*

O Tech Lead fornecerá análises sólidas, diagnósticos arquiteturais, matrizes de riscos e orientações precisas, incentivando você a implementar a melhor solução.
