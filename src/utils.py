from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from openpyxl import load_workbook
import os
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import pandas as pd

def normalizar_status_gerado(serie):
    """Converte a coluna 'Relatório Gerado' para bool de forma consistente."""
    valores_gerado = {"true", "verdadeiro", "sim", "s", "1", "yes", "y"}
    valores_pendente = {"false", "falso", "nao", "não", "n", "0", "no", ""}

    def parse(valor):
        if pd.isna(valor):
            return False
        if isinstance(valor, bool):
            return valor
        if isinstance(valor, (int, float)):
            return bool(valor) and valor != 0
        texto = str(valor).strip().lower()
        if texto in valores_gerado:
            return True
        if texto in valores_pendente:
            return False
        return False

    return serie.map(parse)


def adicionar_titulo_secao(doc, texto):
    """Adiciona um título de seção formatado usando o estilo Heading 3."""
    secao = doc.add_paragraph(style='Heading 3')
    run = secao.add_run(texto)
    run.bold = True
    run.font.name = 'Aptos'
    run.font.size = Pt(12)
    run.font.color.rgb = RGBColor(0, 0, 0)
    secao.paragraph_format.space_before = Pt(8)
    secao.paragraph_format.space_after = Pt(4)
    return secao


def ajustar_largura_colunas(caminho_planilha):
    """Ajusta a largura das colunas do Excel para caber o conteúdo."""
    wb = load_workbook(caminho_planilha)
    ws = wb.active

    for coluna in ws.columns:
        max_length = 0
        coluna_letra = coluna[0].column_letter

        for celula in coluna:
            try:
                if celula.value:
                    max_length = max(max_length, len(str(celula.value)))
            except:
                pass

        # Define largura da coluna com margem extra
        ajuste = max_length + 2
        ws.column_dimensions[coluna_letra].width = ajuste

    wb.save(caminho_planilha)


def arquivo_em_uso(caminho):
    """Verifica se arquivo está em uso/aberto por outro programa."""
    try:
        os.rename(caminho, caminho)
        return False
    except PermissionError:
        return True


def adicionar_texto_caixa_cinza(doc, texto, altura_cm=1.0):
    """Cria uma tabela 1x1 sem bordas com fundo cinza para simular uma caixa de texto."""
    from docx.shared import Cm
    from docx.enum.table import WD_ALIGN_VERTICAL
    table = doc.add_table(rows=1, cols=1)
    
    # Define a altura da linha
    table.rows[0].height = Cm(altura_cm)
    
    cell = table.cell(0, 0)
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    
    # Aplica fundo cinza na célula
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), 'D9D9D9')
    tcPr.append(shd)
    
    # Adiciona o texto centralizado na célula
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(texto)
    run.bold = True
    
    # Ajusta espaçamento interno do parágrafo para 0, já que a célula está centralizada verticalmente
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)


def formatar_data_extenso(data_val):
    """Converte datas (Timestamp, string, datetime) para o formato 'd de mês de ano' em português."""
    if pd.isna(data_val) or not data_val:
        return "data da assinatura eletrônica"
    
    try:
        from datetime import datetime
        if hasattr(data_val, "to_pydatetime"):
            dt = data_val.to_pydatetime()
        elif isinstance(data_val, datetime):
            dt = data_val
        else:
            data_str = str(data_val).strip()
            for fmt in ("%d/%m/%Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                try:
                    dt = datetime.strptime(data_str, fmt)
                    break
                except ValueError:
                    continue
            else:
                return data_str
        
        meses = {
            1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
            5: "maio", 6: "junho", 7: "julho", 8: "agosto",
            9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
        }
        return f"{dt.day} de {meses[dt.month]} de {dt.year}"
    except Exception:
        return str(data_val)


def formatar_mes_ano(data_val):
    """Converte datas para o formato 'Mês, Ano' em português (ex: 'Junho, 2026')."""
    if pd.isna(data_val) or not data_val:
        return "Dezembro, 2025"
    
    try:
        from datetime import datetime
        if hasattr(data_val, "to_pydatetime"):
            dt = data_val.to_pydatetime()
        elif isinstance(data_val, datetime):
            dt = data_val
        else:
            data_str = str(data_val).strip()
            for fmt in ("%d/%m/%Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                try:
                    dt = datetime.strptime(data_str, fmt)
                    break
                except ValueError:
                    continue
            else:
                return data_str
        
        meses = {
            1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
            5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
            9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
        }
        return f"{meses[dt.month]}, {dt.year}"
    except Exception:
        return str(data_val)


def extrair_ano(data_val):
    """Extrai o ano de uma data."""
    if pd.isna(data_val) or not data_val:
        return "2026"
    try:
        from datetime import datetime
        if hasattr(data_val, "to_pydatetime"):
            return str(data_val.year)
        elif isinstance(data_val, datetime):
            return str(data_val.year)
        else:
            data_str = str(data_val).strip()
            for fmt in ("%d/%m/%Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                try:
                    dt = datetime.strptime(data_str, fmt)
                    return str(dt.year)
                except ValueError:
                    continue
            if len(data_str) >= 4 and data_str[-4:].isdigit():
                return data_str[-4:]
            return "2026"
    except Exception:
        return "2026"


def extrair_mes_ano_numerico(data_val):
    """
    Extrai o mês e ano no formato 'MM/AAAA' (ex: '07/2026') a partir de uma data
    (string, Timestamp, datetime, date).
    """
    if pd.isna(data_val) or not data_val:
        return "01/2026"
    
    try:
        from datetime import datetime, date
        import re
        
        if hasattr(data_val, "to_pydatetime"):
            dt = data_val.to_pydatetime()
            return f"{dt.month:02d}/{dt.year}"
        elif isinstance(data_val, (datetime, date)):
            return f"{data_val.month:02d}/{data_val.year}"
        else:
            data_str = str(data_val).strip()
            for fmt in ("%d/%m/%Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%m/%Y", "%d/%m/%y", "%m/%y"):
                try:
                    dt = datetime.strptime(data_str, fmt)
                    return f"{dt.month:02d}/{dt.year}"
                except ValueError:
                    continue
            
            # Se for formato MM/AAAA (ex: '07/2026')
            m_mes_ano = re.match(r'^(\d{1,2})/(\d{4})$', data_str)
            if m_mes_ano:
                mes = int(m_mes_ano.group(1))
                ano = m_mes_ano.group(2)
                return f"{mes:02d}/{ano}"
            
            # Se for formato DD/MM/AAAA (ex: '15/07/2026')
            m_full = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', data_str)
            if m_full:
                mes = int(m_full.group(2))
                ano = m_full.group(3)
                return f"{mes:02d}/{ano}"
            
            ano_extraido = extrair_ano(data_val)
            return f"01/{ano_extraido}"
    except Exception:
        ano_extraido = extrair_ano(data_val)
        return f"01/{ano_extraido}"


def formatar_data_curta(data_val):
    """
    Converte datas (Timestamp, string, datetime, date) para o formato 'DD/MM/AAAA'.
    """
    if pd.isna(data_val) or not data_val:
        return "27/05/2026"
    try:
        from datetime import datetime, date
        if hasattr(data_val, "to_pydatetime"):
            dt = data_val.to_pydatetime()
            return dt.strftime("%d/%m/%Y")
        elif isinstance(data_val, (datetime, date)):
            return data_val.strftime("%d/%m/%Y")
        else:
            data_str = str(data_val).strip()
            for fmt in ("%d/%m/%Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d-%m-%Y"):
                try:
                    dt = datetime.strptime(data_str, fmt)
                    return dt.strftime("%d/%m/%Y")
                except ValueError:
                    continue
            return data_str
    except Exception:
        return str(data_val)


def adicionar_metadados_geracao(doc):
    """
    Adiciona metadados informativos de autoria e carimbo de data/hora da geração
    ao documento Word (.docx) sob a marca 'geradorARPE'.
    Não altera visualmente o corpo do documento.
    """
    from datetime import datetime
    agora = datetime.now()
    props = doc.core_properties
    props.author = "geradorARPE"
    props.last_modified_by = "geradorARPE"
    props.created = agora
    props.modified = agora
    props.keywords = "geradorARPE"
    props.comments = f"Gerado pelo geradorARPE em {agora.strftime('%d/%m/%Y %H:%M:%S')}"
    props.identifier = f"geradorARPE_{agora.strftime('%Y%m%d_%H%M%S')}"
    return doc


def calcular_codificacao_cra(base_input, data_fisc=None, seq_idx=1):
    """
    Calcula a codificação completa para o relatório CRA.
    Estrutura: {base}/{ano}.{num_final:03d} (ex: CRA.ST601.2790-2794/2026.001).
    Se base_input já contém /{ano}.{offset}, incrementa a partir do offset inicial (offset + seq_idx - 1).
    Caso contrário, formata com /{ano}.{seq_idx:03d}.
    """
    if not base_input:
        return ""
    ano_padrao = extrair_ano(data_fisc)
    base_limpa = str(base_input).strip()
    if "/" in base_limpa:
        partes = base_limpa.split("/", 1)
        base = partes[0].strip()
        sufixo = partes[1].strip()
        import re
        m = re.match(r"^(\d{4})\.(\d+)$", sufixo)
        if m:
            ano = m.group(1)
            offset_inicial = int(m.group(2))
            num_final = offset_inicial + (int(seq_idx) - 1)
            return f"{base}/{ano}.{num_final:03d}"
        m_ano = re.match(r"^(\d{4})$", sufixo)
        if m_ano:
            ano = m_ano.group(1)
            return f"{base}/{ano}.{int(seq_idx):03d}"
        return f"{base}/{ano_padrao}.{int(seq_idx):03d}"
    else:
        return f"{base_limpa}/{ano_padrao}.{int(seq_idx):03d}"


def obter_proximo_numero_sequencial_cra(temp_nc: list, id_vinculo: str, tipo_registro: str) -> int:
    """
    Calcula o próximo número sequencial (.001, .002...) para a codificação CRA,
    contando estritamente em relação ao tipo selecionado ('Não Conformidade' ou 'Ponto de Atenção')
    adicionado para a fiscalização vinculada.
    """
    if not temp_nc:
        return 1

    campo_filtro = "Não Conformidade" if tipo_registro == "Não Conformidade" else "Ponto de Atenção"
    recs_tipo = [
        nc for nc in temp_nc
        if str(nc.get("ID da Fiscalização", "")).strip() == str(id_vinculo).strip()
        and str(nc.get(campo_filtro, "")).strip()
    ]

    import re
    max_num = 0
    for r in recs_tipo:
        cod = str(r.get("Codificação", "") or r.get("Trecho", "")).strip()
        m = re.search(r"/(\d{4})\.(\d+)$", cod)
        if m:
            try:
                num = int(m.group(2))
                if num > max_num:
                    max_num = num
            except ValueError:
                pass

    if max_num > 0:
        return max_num + 1

    return len(recs_tipo) + 1


def formatar_codificacoes_contraidas(cods: list) -> str:
    """
    Formata lista de codificações relacionadas no formato contraído:
    ex: 'codificação/2026.001 e .002.' se compartilharem a mesma base e ano.
    Caso contrário, retorna a concatenação separada.
    """
    if not cods:
        return ""
    unique_cods = []
    for c in cods:
        c_clean = str(c).strip()
        if c_clean and c_clean not in unique_cods:
            unique_cods.append(c_clean)

    if len(unique_cods) == 0:
        return ""
    if len(unique_cods) == 1:
        return unique_cods[0]

    import re
    pattern = re.compile(r"^(.*?)/(\d{4})\.(\d+)$")
    parsed = []
    for c in unique_cods:
        m = pattern.match(c)
        if m:
            parsed.append((m.group(1), m.group(2), m.group(3)))
        else:
            parsed.append(None)

    if all(p is not None for p in parsed):
        primeira_base = parsed[0][0]
        primeiro_ano = parsed[0][1]
        mesma_base_ano = all(p[0] == primeira_base and p[1] == primeiro_ano for p in parsed)
        if mesma_base_ano:
            sufixos = [p[2] for p in parsed]
            primeiro_completo = f"{primeira_base}/{primeiro_ano}.{sufixos[0]}"
            if len(sufixos) == 2:
                return f"{primeiro_completo} e {sufixos[1]}."
            else:
                outros = ", ".join(sufixos[1:-1])
                return f"{primeiro_completo}, {outros} e {sufixos[-1]}."

    if len(unique_cods) == 2:
        return f"{unique_cods[0]} e {unique_cods[1]}."
    return f"{', '.join(unique_cods[:-1])} e {unique_cods[-1]}."


def fotos_tem_mesmas_ncs(related_records: list) -> bool:
    """
    Verifica se todos os registros do grupo possuem exatamente as mesmas siglas de NC / PT.
    """
    if not related_records or len(related_records) <= 1:
        return True

    def _siglas_rec(rec):
        nc = str(rec.get("Não Conformidade") or "").strip().lower()
        pt = str(rec.get("Ponto de Atenção") or "").strip().lower()
        parts_nc = set(p.strip() for p in nc.split(",") if p.strip())
        parts_pt = set(p.strip() for p in pt.split(",") if p.strip())
        return (frozenset(parts_nc), frozenset(parts_pt))

    primeira = _siglas_rec(related_records[0])
    for r in related_records[1:]:
        if _siglas_rec(r) != primeira:
            return False
    return True


def carregar_mapa_siglas_completo() -> dict:
    """
    Carrega o mapa consolidado de siglas e descrições técnicas,
    mesclando MAP_SIGLAS com os cadastros personalizados de custom_ncs.json
    e custom_ncs_socicam.json.
    """
    try:
        from sections.quadros.quadros import MAP_SIGLAS
        local_map = MAP_SIGLAS.copy()
    except Exception:
        local_map = {
            "FI": "Fissuras",
            "TTC": "Trincas isoladas transversais curtas",
            "TTL": "Trincas isoladas transversais longas",
            "TLC": "Trincas isoladas longitudinais curtas",
            "TLL": "Trincas isoladas longitudinais longas",
            "J": "Trincas interligadas sem erosão acentuada nas bordas das trincas",
            "JE": "Trincas interligadas com erosão acentuada nas bordas das trincas",
            "TRR": "Trincas isoladas no revestimento devido à retração térmica ou dissecação da base (solo-cimento) ou do revestimento",
            "TB": "Trincas interligadas sem erosão acentuada nas bordas das trincas",
            "TBE": "Trincas interligadas com erosão acentuada nas bordas das trincas",
            "ALP": "Afundamento local plástico devido à fluência plástica de uma ou mais camadas do pavimento ou do subleito",
            "ATP": "Afundamento da trilha plástico devido à fluência plástica de uma ou mais camadas do pavimento ou do subleito",
            "ALC": "Afundamento local de consolidação devido à consolidação diferencial ocorrente em camadas do pavimento ou do subleito",
            "ATC": "Afundamento da trilha de consolidação devido à consolidação diferencial ocorrente em camadas do pavimento ou do subleito",
            "O": "Ondulação/Corrugação, caracterizada por ondulações transversais causadas por instabilidade da mistura betuminosa constituinte do revestimento ou da base",
            "E": "Escorregamento do revestimento betuminoso",
            "EX": "Exsudação do ligante betuminoso no revestimento",
            "D": "Desgaste acentuado na superfície do revestimento",
            "P": "buracos decorrentes da desagregação do revestimento e às vezes de camadas inferiores",
            "R": "Remendo"
        }

    try:
        import os
        import json
        quadros_dir = os.path.dirname(os.path.abspath(__file__))
        for fname in ["custom_ncs.json", "custom_ncs_socicam.json"]:
            c_path = os.path.abspath(os.path.join(quadros_dir, "database", fname))
            if not os.path.exists(c_path):
                c_path = os.path.abspath(os.path.join(quadros_dir, "..", "database", fname))
            if os.path.exists(c_path):
                with open(c_path, "r", encoding="utf-8") as f:
                    custom_list = json.load(f)
                    for item in custom_list:
                        s = item.get("sigla", "")
                        d = item.get("descricao", "")
                        if s and d:
                            local_map[s] = d
    except Exception:
        pass

    return local_map


def converter_faixa_para_sigla(faixa: str | None) -> str:
    """
    Converte a descrição da faixa para sua respectiva sigla oficial:
    - Faixa da Esquerda / Esquerda -> FE
    - Faixa da Direita / Direita -> FD
    - Faixa Esquerda e Direita / Esquerda e Direita / Ambas / FED -> FED
    """
    if not faixa:
        return ""
    texto = str(faixa).strip()
    if not texto or texto.lower() in ("none", "nan", "null", "-", "não informado"):
        return ""

    u = texto.upper()
    if u.startswith("NA "):
        u = u[3:].strip()
    elif u.startswith("NO "):
        u = u[3:].strip()

    if u in ("FE", "FD", "FED"):
        return u

    tem_esq = ("ESQ" in u) or ("FE" in u.split()) or (u == "E")
    tem_dir = ("DIR" in u) or ("FD" in u.split()) or (u == "D")

    if (tem_esq and tem_dir) or "FED" in u or "AMBAS" in u:
        return "FED"
    if tem_esq:
        return "FE"
    if tem_dir:
        return "FD"

    return u


def combinar_faixas_relacionadas(faixa1: str | None, faixa2: str | None) -> str:
    """
    Combina as faixas de fotos que se juntam:
    - Se uma for Esquerda (FE) e a outra Direita (FD), o resultado é 'FED'.
    - Se ambas forem Esquerda, o resultado é 'FE'.
    - Se ambas forem Direita, o resultado é 'FD'.
    - Se qualquer uma já for 'FED', o resultado é 'FED'.
    """
    s1 = converter_faixa_para_sigla(faixa1)
    s2 = converter_faixa_para_sigla(faixa2)

    if not s1 and not s2:
        return ""
    if not s1:
        return s2
    if not s2:
        return s1

    if s1 == "FED" or s2 == "FED":
        return "FED"

    if (s1 == "FE" and s2 == "FD") or (s1 == "FD" and s2 == "FE"):
        return "FED"

    if s1 == s2:
        return s1

    tem_esq = s1 in ("FE", "FED") or s2 in ("FE", "FED")
    tem_dir = s1 in ("FD", "FED") or s2 in ("FD", "FED")
    if tem_esq and tem_dir:
        return "FED"

    return s1 or s2


def formatar_legenda_foto(
    num: int | str,
    codificacao: str,
    siglas_ou_ncs: list | str,
    faixa: str,
    data_foto: str
) -> str:
    """
    Formata a legenda da foto seguindo o padrão oficial:
    foto 01 - (codificação). (descrição das não conformidades) na (sigla da faixa (FE/FD/FED)). (DATA do metadado)
    """
    # 1. Prefixo da foto (ex: 'foto 01 - ')
    try:
        num_clean = str(num).strip()
        num_int = int(num_clean)
        num_str = f"{num_int:02d}"
    except Exception:
        num_str = str(num).strip().zfill(2) if str(num).strip() else "01"
    prefixo = f"foto {num_str} - "

    # 2. Codificação (ex: 'CRA.ST601.2790-2794/2026.001. ')
    cod_clean = str(codificacao or "").strip().rstrip(".")
    cod_part = f"{cod_clean}. " if cod_clean else ""

    # 3. Descrições das Não Conformidades (ex: 'desc1 e desc2' ou 'desc1, desc2 e desc3')
    if isinstance(siglas_ou_ncs, str):
        siglas_lista = [s.strip() for s in siglas_ou_ncs.split(",") if s.strip()]
    elif isinstance(siglas_ou_ncs, (list, tuple, set)):
        siglas_lista = [str(s).strip() for s in siglas_ou_ncs if str(s).strip()]
    else:
        siglas_lista = []

    mapa = carregar_mapa_siglas_completo()
    descs = []
    for s in siglas_lista:
        d = mapa.get(s, s).strip().rstrip(".")
        if d and d not in descs:
            descs.append(d)

    if not descs:
        desc_part = ""
    elif len(descs) == 1:
        desc_part = descs[0]
    elif len(descs) == 2:
        desc_part = f"{descs[0]} e {descs[1]}"
    else:
        desc_part = f"{', '.join(descs[:-1])} e {descs[-1]}"

    # 4. Faixa em siglas (ex: ' na FE', ' na FD', ' na FED')
    sigla_faixa = converter_faixa_para_sigla(faixa)
    if not sigla_faixa:
        faixa_part = ""
    else:
        faixa_part = f" na {sigla_faixa}"

    # 5. Data do metadado (ex: '. (14/10/2026)')
    corpo_legenda = f"{cod_part}{desc_part}{faixa_part}".strip().rstrip(".")
    data_clean = str(data_foto or "").strip().strip("()")
    if data_clean and data_clean.lower() not in ("none", "nan", ""):
        if corpo_legenda:
            corpo = f"{corpo_legenda}. ({data_clean})"
        else:
            corpo = f"({data_clean})"
    else:
        corpo = f"{corpo_legenda}." if corpo_legenda else ""

    return f"{prefixo}{corpo}"





