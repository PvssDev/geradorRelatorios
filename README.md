# Gerador de Relatórios de Fiscalização e Monitoramento

Ferramenta corporativa automatizada para processamento de dados regulatórios, compilação de relatórios técnicos e geração de memoriais fotográficos padronizados em formatos `.docx` e `.pdf`.

---

## 📌 Contexto da Aplicação

A ferramenta foi projetada para otimizar e padronizar o fluxo de trabalho dos analistas de regulação. Ela elimina o trabalho manual e repetitivo de formatação no Microsoft Word, convertendo planilhas de campo (Excel) e arquivos de imagens em relatórios prontos para assinatura.

### Por que esta solução foi escolhida?
* **Stack Única (Python):** Toda a inteligência de processamento de tabelas (Pandas), compressão de imagem (Pillow) e manipulação de arquivos Office (python-docx) roda em Python de forma integrada.
* **Interface Simples com Streamlit:** O uso do Streamlit permite que os usuários interajam com uma aplicação web local intuitiva e direta, facilitando o upload de dados e a ordenação visual de fotos antes da geração do documento final.

---

## 💼 Caracteristicas Principais

O gerador segue diretrizes baseadas nos modelos de relatórios de referência da agência:

### 1. Suporte Multi-Layout e Agências
O sistema adapta-se estruturalmente a 3 contratos de concessão distintos, cada um com regras de estilo, siglas, tabelas e cabeçalhos próprios:


### 2. Categorias de Relatórios
* **Fiscalização:** Gera o relatório base da vistoria inicial mapeando as Não Conformidades (NC) e Pontos de Atenção (PA).
* **Monitoramento:** Acompanha e audita a resolução de pendências anteriores.

### 3. Integração e Rastreabilidade no Monitoramento (CRC)
* **Upload:** Para relatórios serem gerados é adicionada formas de uploads para categorizar e relacionar de forma automatizada.
* **Extração Dinâmica de Variáveis:** O sistema lê o documento anterior para identificar as devidas variaveis, Ele incrementa replica e utiliza de forma pratica e automatica.