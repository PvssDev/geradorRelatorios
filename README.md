# Gerador de Relatórios de Fiscalização e Monitoramento

Ferramenta corporativa automatizada para processamento de dados regulatórios, compilação de relatórios técnicos e geração de memoriais fotográficos padronizados em formatos `.docx` e `.pdf`.

---

## 📌 Contexto da Ferramenta

A ferramenta foi projetada para otimizar e padronizar o fluxo de trabalho dos analistas de regulação da **ARPE (Agência de Regulação de Pernambuco)**. Ela elimina o trabalho manual e repetitivo de formatação no Microsoft Word, convertendo planilhas de campo (Excel) e arquivos de imagens em relatórios prontos para assinatura e inserção no sistema SEI.

### Por que esta solução foi escolhida?
* **Stack Única (Python):** Toda a inteligência de processamento de tabelas (Pandas), compressão de imagem (Pillow) e manipulação de arquivos Office (python-docx) roda em Python de forma integrada.
* **Interface Simples com Streamlit:** O uso do Streamlit permite que os usuários interajam com uma aplicação web local intuitiva e direta, facilitando o upload de dados e a ordenação visual de fotos antes da geração do documento final.

---

## 💼 Regras de Negócio Principais

O gerador segue diretrizes rígidas baseadas nos modelos de relatórios de referência da agência:

### 1. Suporte Multi-Layout e Agências
O sistema adapta-se estruturalmente a 3 contratos de concessão distintos, cada um com regras de estilo, siglas, tabelas e cabeçalhos próprios:
* **CRA** (Concessionária Rota do Atlântico)
* **CRC** (Concessionária Rota dos Coqueiros)
* **SOCICAM** (Terminais Rodoviários)

### 2. Categorias de Relatórios
* **Fiscalização:** Gera o relatório base da vistoria inicial mapeando as Não Conformidades (NC) e Pontos de Atenção (PA).
* **Monitoramento:** Acompanha e audita a resolução de pendências anteriores.

### 3. Integração e Rastreabilidade no Monitoramento (CRC)
* **Upload Obrigatório:** Para relatórios do tipo CRC Monitoramento, é obrigatório fornecer o arquivo do monitoramento anterior (.docx).
* **Extração Dinâmica de Variáveis:** O sistema lê o documento anterior para identificar o número do monitoramento anterior (ex: 4º) e o número do CTR (ex: 03/2025). Ele incrementa automaticamente o número do monitoramento (para 5º) e replica o número do CTR em todo o relatório.
* **Placeholders como Fallback:** Se as variáveis não puderem ser encontradas no arquivo enviado, o sistema preenche o documento com os placeholders `"X"` e `"XX/XXXX"` para indicar a inconsistência.

### 4. Memorial Fotográfico
* As imagens são compactadas e organizadas dinamicamente em uma grade de duas colunas, associando cada foto à sua respectiva Não Conformidade e sentido de pista, respeitando as margens e a orientação da folha.