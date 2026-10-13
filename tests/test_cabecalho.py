import sys
import os

# Adiciona o diretório src ao path para poder importar o módulo report
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from report import gerar_relatorio

print("Testando geração de relatório com o novo cabeçalho...")
# Forçar geração de todos (gerar_todos=True) para testar
arquivos, planilha = gerar_relatorio(gerar_todos=True)
print("Arquivos gerados:", arquivos)
