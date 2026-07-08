from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
import os
import pandas as pd
from utils import adicionar_titulo_secao, extrair_ano
from database.manager import carregar_responsaveis, carregar_coordenadores

def formatar_data_dd_mm_yyyy(data_val):
    if pd.isna(data_val) or not data_val:
        return ""
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
        return dt.strftime("%d/%m/%Y")
    except Exception:
        return str(data_val)

def criar_grade_fotos(doc, df_fotos, terminal_nc, fotos_dir, data_fisc):
    if df_fotos.empty:
        return
    
    # Compatibilidade com planilhas antigas
    if "Pista" not in df_fotos.columns:
        df_fotos = df_fotos.copy()
        df_fotos["Pista"] = ""
    if "Trecho" not in df_fotos.columns:
        df_fotos = df_fotos.copy()
        df_fotos["Trecho"] = ""
    
    # Agrupa por Pista mantendo ordem de inserção
    pistas_unicas = []
    for p in df_fotos["Pista"].tolist():
        p_str = str(p).strip() if not pd.isna(p) else ""
        if not p_str:
            p_str = "Única"
        if p_str not in pistas_unicas:
            pistas_unicas.append(p_str)
            
    for idx_pista, pista_val in enumerate(pistas_unicas):
        # Filtra os itens desta pista
        mask = df_fotos["Pista"].apply(lambda x: (str(x).strip() if not pd.isna(x) else "") == (pista_val if pista_val != "Única" else ""))
        df_pista = df_fotos[mask].copy()
        if df_pista.empty:
            continue
            
        # Adiciona a tabela de grade (2 colunas)
        table = doc.add_table(rows=0, cols=2)
        table.style = 'Table Grid'
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        table.columns[0].width = Inches(3.635)
        table.columns[1].width = Inches(3.635)
        
        # Cabeçalho da Pista
        if pista_val.lower().startswith("pista"):
            header_text = f"{terminal_nc}, {pista_val}"
        else:
            header_text = f"{terminal_nc}, Pista sentido {pista_val}"
            
        row_h = table.add_row()
        row_h.cells[0].width = Inches(3.635)
        row_h.cells[1].width = Inches(3.635)
        cell_merged = row_h.cells[0].merge(row_h.cells[1])
        cell_merged.width = Inches(7.27)
        p_h = cell_merged.paragraphs[0]
        p_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_h.paragraph_format.space_before = Pt(6)
        p_h.paragraph_format.space_after = Pt(6)
        run_h = p_h.add_run(header_text)
        run_h.bold = True
        run_h.font.name = 'Aptos'
        run_h.font.size = Pt(11)
        
        records = df_pista.to_dict('records')
        for i in range(0, len(records), 2):
            rec_left = records[i]
            rec_right = records[i+1] if i+1 < len(records) else None
            
            # Linha de Imagens
            row_img = table.add_row()
            row_img.cells[0].width = Inches(3.635)
            row_img.cells[1].width = Inches(3.635)
            
            # Imagem Esquerda
            p_img_left = row_img.cells[0].paragraphs[0]
            p_img_left.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img_left.paragraph_format.left_indent = Inches(0)
            p_img_left.paragraph_format.first_line_indent = Inches(0)
            p_img_left.paragraph_format.space_before = Pt(4)
            p_img_left.paragraph_format.space_after = Pt(4)
            foto_left = rec_left.get("Foto", "")
            if pd.isna(foto_left) or not isinstance(foto_left, str) or not foto_left.strip():
                foto_left = ""
            foto_path_left = os.path.join(fotos_dir, foto_left) if fotos_dir and foto_left else ""
            if foto_path_left and os.path.exists(foto_path_left):
                run_img_left = p_img_left.add_run()
                run_img_left.add_picture(foto_path_left, width=Inches(3.15), height=Inches(3.15))
                
            # Imagem Direita
            p_img_right = row_img.cells[1].paragraphs[0]
            p_img_right.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img_right.paragraph_format.left_indent = Inches(0)
            p_img_right.paragraph_format.first_line_indent = Inches(0)
            p_img_right.paragraph_format.space_before = Pt(4)
            p_img_right.paragraph_format.space_after = Pt(4)
            if rec_right:
                foto_right = rec_right.get("Foto", "")
                if pd.isna(foto_right) or not isinstance(foto_right, str) or not foto_right.strip():
                    foto_right = ""
                foto_path_right = os.path.join(fotos_dir, foto_right) if fotos_dir and foto_right else ""
                if foto_path_right and os.path.exists(foto_path_right):
                    run_img_right = p_img_right.add_run()
                    run_img_right.add_picture(foto_path_right, width=Inches(3.15), height=Inches(3.15))
            else:
                row_img.cells[1].width = Inches(3.635)
                    
            # Linha de Descrições
            row_desc = table.add_row()
            row_desc.cells[0].width = Inches(3.635)
            row_desc.cells[1].width = Inches(3.635)
            
            # Descrição Esquerda
            p_desc_left = row_desc.cells[0].paragraphs[0]
            p_desc_left.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p_desc_left.paragraph_format.left_indent = Inches(0)
            p_desc_left.paragraph_format.first_line_indent = Inches(0)
            p_desc_left.paragraph_format.space_before = Pt(4)
            p_desc_left.paragraph_format.space_after = Pt(4)
            
            num_left = str(rec_left.get("Nº", i+1)).zfill(2)
            trecho_left = str(rec_left.get("Trecho", "")).strip()
            obs_left = str(rec_left.get("Observações", rec_left.get("Legenda da Foto", ""))).strip()
            
            desc_text_left = f"Foto {num_left} – Trecho {trecho_left} apresentando {obs_left}, ({data_fisc})."
            run_desc_left = p_desc_left.add_run(desc_text_left)
            run_desc_left.font.name = 'Aptos'
            run_desc_left.font.size = Pt(10)
            
            # Descrição Direita
            p_desc_right = row_desc.cells[1].paragraphs[0]
            p_desc_right.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p_desc_right.paragraph_format.left_indent = Inches(0)
            p_desc_right.paragraph_format.first_line_indent = Inches(0)
            p_desc_right.paragraph_format.space_before = Pt(4)
            p_desc_right.paragraph_format.space_after = Pt(4)
            
            if rec_right:
                num_right = str(rec_right.get("Nº", i+2)).zfill(2)
                trecho_right = str(rec_right.get("Trecho", "")).strip()
                obs_right = str(rec_right.get("Observações", rec_right.get("Legenda da Foto", ""))).strip()
                
                desc_text_right = f"Foto {num_right} – Trecho {trecho_right} apresentando {obs_right}, ({data_fisc})."
                run_desc_right = p_desc_right.add_run(desc_text_right)
                run_desc_right.font.name = 'Aptos'
                run_desc_right.font.size = Pt(10)
            
            # Forçar a largura de todas as células das duas linhas para 3.635 polegadas (metade exata)
            row_img.cells[0].width = Inches(3.635)
            row_img.cells[1].width = Inches(3.635)
            row_desc.cells[0].width = Inches(3.635)
            row_desc.cells[1].width = Inches(3.635)
                
        if idx_pista < len(pistas_unicas) - 1:
            doc.add_paragraph()

def numero_por_extenso(n):
    extenso_map = {
        0: "zero", 1: "um", 2: "dois", 3: "três", 4: "quatro", 5: "cinco",
        6: "seis", 7: "sete", 8: "oito", 9: "nove", 10: "dez",
        11: "onze", 12: "doze", 13: "treze", 14: "quatorze", 15: "quinze",
        16: "dezesseis", 17: "dezessete", 18: "dezoito", 19: "dezenove", 20: "vinte",
        21: "vinte e um", 22: "vinte e dois", 23: "vinte e três", 24: "vinte e quatro",
        25: "vinte e cinco", 26: "vinte e seis", 27: "vinte e sete", 28: "vinte e oito",
        29: "vinte e nove", 30: "trinta", 31: "trinta e um", 32: "trinta e dois",
        33: "trinta e três", 34: "trinta e quatro", 35: "trinta e cinco",
        36: "trinta e seis", 37: "trinta e sete", 38: "trinta e oito", 39: "trinta e nove",
        40: "quarenta", 41: "quarenta e um", 42: "quarenta e dois", 43: "quarenta e três",
        44: "quarenta e quatro", 45: "quarenta e cinco", 46: "quarenta e seis",
        47: "quarenta e sete", 48: "quarenta e oito", 49: "quarenta e nove", 50: "cinquenta"
    }
    return extenso_map.get(n, str(n))

def gerar_secao_finalizacao(doc: Document, row, total_ncs, nc_df=None, fotos_dir=None):
    """Gera o restante do relatório a partir da seção 5 (Determinações Gerais) até as assinaturas finais e apêndices com fotos."""
    
    ano = extrair_ano(row["Data"])
    ano_anterior = str(int(ano) - 1) if ano.isdigit() else "2025"

    # ----------------------------------------------------
    # 5. DETERMINAÇÕES GERAIS
    # ----------------------------------------------------
    doc.add_paragraph()  # Espaço
    adicionar_titulo_secao(doc, "5. DETERMINAÇÕES GERAIS")
    doc.add_paragraph()  # Pula linha abaixo do título
    
    p_det1 = doc.add_paragraph()
    p_det1.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_det1.paragraph_format.space_after = Pt(6)
    p_det1.paragraph_format.line_spacing = 1.15
    run_det1 = p_det1.add_run(
        "Considerando os dispositivos contratuais pertinentes e visando garantir a qualidade dos serviços prestados, "
        "determina-se que a CRA tome as seguintes medidas através de um plano de ação:"
    )
    run_det1.font.name = 'Aptos'
    run_det1.font.size = Pt(11)
    
    p_det2 = doc.add_paragraph()
    p_det2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_det2.paragraph_format.space_after = Pt(6)
    p_det2.paragraph_format.line_spacing = 1.15
    
    r_det2_1 = p_det2.add_run("Medidas de Manutenção / Conservação,")
    r_det2_1.bold = True
    r_det2_1.font.name = 'Aptos'
    r_det2_1.font.size = Pt(11)
    
    r_det2_2 = p_det2.add_run(
        f" detalhando cronograma com trechos a executar de forma que permita à Arpe uma programação mais efetiva do "
        f"monitoramento de suas soluções a execução de cada subtrecho, conforme o modelo encaminhado para {ano_anterior} "
        f"(Cronograma de Conserva Especial do Pavimento CRA {ano_anterior})."
    )
    r_det2_2.font.name = 'Aptos'
    r_det2_2.font.size = Pt(11)
    
    p_det3 = doc.add_paragraph()
    p_det3.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_det3.paragraph_format.space_after = Pt(6)
    p_det3.paragraph_format.line_spacing = 1.15
    
    r_det3_1 = p_det3.add_run("Medidas imediatas")
    r_det3_1.bold = True
    r_det3_1.font.name = 'Aptos'
    r_det3_1.font.size = Pt(11)
    
    r_det3_2 = p_det3.add_run(
        " resolutividade das NC de Sinalização, nos prazos estabelecidos no subitem 4.1.3.3.2.4. Tachas e Tachões "
        "Refletivos do PDCL, conforme disposto no Quadro 1, na coluna denominada Determinações."
    )
    r_det3_2.font.name = 'Aptos'
    r_det3_2.font.size = Pt(11)
    
    doc.add_paragraph()  # Espaço
    
    # ----------------------------------------------------
    # 6. RECOMENDAÇÕES
    # ----------------------------------------------------
    adicionar_titulo_secao(doc, "6. RECOMENDAÇÕES")
    doc.add_paragraph()  # Pula linha abaixo do título
    
    p_rec1 = doc.add_paragraph()
    p_rec1.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_rec1.paragraph_format.space_after = Pt(6)
    p_rec1.paragraph_format.line_spacing = 1.15
    run_rec1 = p_rec1.add_run(
        "Considerando as disposições do Contrato de Concessão, em especial, o Anexo IV - PDCL, Outras Sinalizações, "
        "dados do Relatório Anual 01 de novembro/2025 elaborado VI, e outras legislação aplicável, devem ser "
        "observadas pela CRA as seguintes recomendações:"
    )
    run_rec1.font.name = 'Aptos'
    run_rec1.font.size = Pt(11)
    
    p_rec2 = doc.add_paragraph()
    p_rec2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_rec2.paragraph_format.space_after = Pt(6)
    p_rec2.paragraph_format.line_spacing = 1.15
    run_rec2 = p_rec2.add_run(
        "Levantar a necessidade de reposição da SINALIZAÇÃO por tachas e tachões em todo o complexo viário Express Way, "
        " em especial a retirada das tachar anteriores danificadas que podem causar risco a segurança dos usuários. "
        "O vi verificou deficiências em todos os trechos."
    )
    run_rec2.font.name = 'Aptos'
    run_rec2.font.size = Pt(11)
    
    doc.add_paragraph()  # Espaço
    
    # ----------------------------------------------------
    # 7. CONCLUSÕES
    # ----------------------------------------------------
    adicionar_titulo_secao(doc, "7. CONCLUSÕES")
    doc.add_paragraph()  # Pula linha abaixo do título
    
    p_con1 = doc.add_paragraph()
    p_con1.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_con1.paragraph_format.space_after = Pt(6)
    p_con1.paragraph_format.line_spacing = 1.15
    
    extenso_ncs = numero_por_extenso(total_ncs)
    run_con1 = p_con1.add_run(
        f"Tendo em vista as ações de fiscalização realizadas pela Arpe foram constatadas {extenso_ncs} ({total_ncs}) pontos ou trechos "
        f"fiscalizados que apresentaram Não Conformidades distribuídas majoritariamente na PE 009, estas foram "
        f"analisadas e caracterizadas a partir dos indicadores do Grupo Condição de Superfície definidos no Contrato de Concessão CT. nº 043/2011."
    )
    run_con1.font.name = 'Aptos'
    run_con1.font.size = Pt(11)
    
    p_con2 = doc.add_paragraph()
    p_con2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_con2.paragraph_format.space_after = Pt(6)
    p_con2.paragraph_format.line_spacing = 1.15
    run_con2 = p_con2.add_run(
        f"Assim considerando a Programação de Conserva Especial do Pavimento - CRA {ano}, solicita-se a inclusão destas "
        f"não conformidades no cronograma detalhado de Conserva Especial do Pavimento que permita à Arpe uma "
        f"realização mais efetiva dos monitoramentos ao longo de {ano}."
    )
    run_con2.font.name = 'Aptos'
    run_con2.font.size = Pt(11)
    
    p_con3 = doc.add_paragraph()
    p_con3.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_con3.paragraph_format.space_after = Pt(6)
    p_con3.paragraph_format.line_spacing = 1.15
    run_con3 = p_con3.add_run(
        "Recomenda-se, por fim, o encaminhamento deste Relatório de Fiscalização para que Suape, na qualidade de "
        "Gestor do Contrato e Regulador desse Sistema Viário, realize as providências cabíveis junto à Concessionária Rota do "
        "Atlântico com o objetivo de garantir a regularização das Não Conformidades pendentes apontadas por esta Agência de Regulação."
    )
    run_con3.font.name = 'Aptos'
    run_con3.font.size = Pt(11)
    
    # Local e Data após conclusões
    p_loc1 = doc.add_paragraph()
    p_loc1.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_loc1.paragraph_format.space_after = Pt(6)
    run_loc1 = p_loc1.add_run("Recife, data da assinatura eletrônica.")
    run_loc1.font.name = 'Aptos'
    run_loc1.font.size = Pt(11)
    
    # APÊNDICES
    # ----------------------------------------------------
    import os
    import pandas as pd

    id_fisc = row["ID da Fiscalização"]
    terminal_nc = row.get("Local", "")
    data_fisc = formatar_data_dd_mm_yyyy(row["Data"])
    
    current_ncs = nc_df[nc_df["ID da Fiscalização"] == id_fisc] if nc_df is not None else pd.DataFrame()
    
    # 1. Filtra não conformidades reais e pontos de atenção
    ncs_reais = pd.DataFrame()
    pas_reais = pd.DataFrame()
    if not current_ncs.empty:
        if "Não Conformidade" in current_ncs.columns:
            ncs_reais = current_ncs[current_ncs["Não Conformidade"].fillna("").astype(str).str.strip() != ""].copy()
        if "Ponto de Atenção" in current_ncs.columns:
            pas_reais = current_ncs[current_ncs["Ponto de Atenção"].fillna("").astype(str).str.strip() != ""].copy()

    # APÊNDICE A
    p_ap_a = adicionar_titulo_secao(doc, "APÊNDICE A – REGISTROS FOTOGRÁFICOS DAS NÃO CONFORMIDADES")
    p_ap_a.paragraph_format.page_break_before = True
    
    if not ncs_reais.empty:
        criar_grade_fotos(doc, ncs_reais, terminal_nc, fotos_dir, data_fisc)
    else:
        p_empty = doc.add_paragraph()
        r_empty = p_empty.add_run("Nenhum registro fotográfico de não conformidade cadastrado.")
        r_empty.font.name = 'Aptos'
        r_empty.font.size = Pt(11)

    # APÊNDICE B
    p_ap_b = adicionar_titulo_secao(doc, "APÊNDICE B – REGISTROS FOTOGRÁFICOS DAS PONTOS DE ATENÇÃO")
    p_ap_b.paragraph_format.page_break_before = True
    
    if not pas_reais.empty:
        criar_grade_fotos(doc, pas_reais, terminal_nc, fotos_dir, data_fisc)
    else:
        p_empty = doc.add_paragraph()
        r_empty = p_empty.add_run("Nenhum registro fotográfico de ponto de atenção cadastrado.")
        r_empty.font.name = 'Aptos'
        r_empty.font.size = Pt(11)
    
    p_loc2 = doc.add_paragraph()
    p_loc2.paragraph_format.space_before = Pt(12)
    p_loc2.paragraph_format.space_after = Pt(12)
    run_loc2 = p_loc2.add_run("Recife, data da assinatura eletrônica.")
    run_loc2.font.name = 'Aptos'
    run_loc2.font.size = Pt(11)
    
    # ----------------------------------------------------
    # ASSINATURAS FINAIS DINÂMICAS
    # ----------------------------------------------------
    doc.add_paragraph()
    doc.add_paragraph()
    
    responsaveis_list = [r.strip() for r in str(row["Pessoal Responsável"]).split(",") if r.strip()]
    db_resp = carregar_responsaveis()
    
    for nome in responsaveis_list:
        match = next((d for d in db_resp if d["nome"].strip().lower() == nome.lower()), None)
        if match:
            r_nome = match["nome"]
            r_funcao = match["funcao"]
            r_matr = match["matricula"]
        else:
            r_nome = nome
            r_funcao = "Analista de Regulação"
            r_matr = "xxxxxxx/xx"
            
        p_ass = doc.add_paragraph()
        p_ass.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_ass.paragraph_format.space_after = Pt(0)
        run_ass = p_ass.add_run(r_nome)
        run_ass.bold = True
        run_ass.font.name = 'Aptos'
        run_ass.font.size = Pt(11)
        
        p_carg = doc.add_paragraph()
        p_carg.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_carg.paragraph_format.space_after = Pt(0)
        run_carg = p_carg.add_run(r_funcao)
        run_carg.font.name = 'Aptos'
        run_carg.font.size = Pt(11)
        
        p_mat = doc.add_paragraph()
        p_mat.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_mat.paragraph_format.space_after = Pt(12)
        run_mat = p_mat.add_run(f"Matrícula nº {r_matr}")
        run_mat.font.name = 'Aptos'
        run_mat.font.size = Pt(11)
        
        doc.add_paragraph()  # Espaço entre assinaturas
        
    # Ciente e de acordo (Coordenador)
    p_ciente = doc.add_paragraph()
    p_ciente.paragraph_format.space_before = Pt(12)
    p_ciente.paragraph_format.space_after = Pt(12)
    run_ciente = p_ciente.add_run("Ciente e de acordo.")
    run_ciente.font.name = 'Aptos'
    run_ciente.font.size = Pt(11)
    
    doc.add_paragraph()  # Espaço antes da assinatura do coordenador
    
    db_coord = carregar_coordenadores()
    coord_name = str(row["Coordenador"]).strip()
    match_coord = next((c for c in db_coord if c["nome"].strip().lower() == coord_name.lower()), None)
    if match_coord:
        c_nome = match_coord["nome"]
        c_funcao = match_coord["funcao"]
        c_matr = match_coord["matricula"]
    else:
        c_nome = coord_name
        c_funcao = "Coordenador(a) de Transportes e Rodovias"
        c_matr = "xxxxxxx/xx"
        
    p_ass3 = doc.add_paragraph()
    p_ass3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ass3.paragraph_format.space_after = Pt(0)
    run_ass3 = p_ass3.add_run(c_nome)
    run_ass3.bold = True
    run_ass3.font.name = 'Aptos'
    run_ass3.font.size = Pt(11)
    
    p_carg3 = doc.add_paragraph()
    p_carg3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_carg3.paragraph_format.space_after = Pt(0)
    run_carg3 = p_carg3.add_run(c_funcao)
    run_carg3.font.name = 'Aptos'
    run_carg3.font.size = Pt(11)
    
    p_mat3 = doc.add_paragraph()
    p_mat3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_mat3.paragraph_format.space_after = Pt(12)
    run_mat3 = p_mat3.add_run(f"Matrícula nº {c_matr}")
    run_mat3.font.name = 'Aptos'
    run_mat3.font.size = Pt(11)
