from report import gerar_relatorio


def main():
    arquivos, planilha = gerar_relatorio()
    if arquivos:
        print(f"✅ {len(arquivos)} relatórios gerados.")


if __name__ == "__main__":
    try:
        main()
    finally:
        input("\nExecução finalizada. Pressione Enter para sair...")
