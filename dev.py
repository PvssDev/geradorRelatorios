# -*- coding: utf-8 -*-
"""
Script unificado de desenvolvimento local para o Gerador de Relatórios.
Inicia simultaneamente o Backend FastAPI (porta 8000) e o Frontend Vite (porta 5173),
com proxy reverso e recarregamento automático (hot-reload).
"""

import os
import sys
import time
import signal
import subprocess
import webbrowser
from threading import Thread

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
SRC_DIR = os.path.join(ROOT_DIR, "src")

def abrir_navegador():
    time.sleep(2.0)
    print("\n[INFO] Abrindo aplicacao no navegador: http://localhost:5173 ...\n")
    try:
        webbrowser.open("http://localhost:5173")
    except Exception:
        pass

def main():
    print("=" * 65)
    print("   ARPE - GERADOR DE RELATORIOS (MODO DESENVOLVIMENTO)")
    print("=" * 65)
    print(f"[1/2] Iniciando Backend FastAPI em http://127.0.0.1:8000 ...")
    print(f"[2/2] Iniciando Frontend Vite em http://localhost:5173 ...")
    print("=" * 65)
    print("Pressione Ctrl + C no terminal para encerrar ambos os servidores.")
    print("=" * 65 + "\n")

    # Comando do Backend
    backend_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "server.main:app",
        "--app-dir",
        SRC_DIR,
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
        "--reload",
    ]

    # Comando do Frontend (npm no Windows usa npm.cmd)
    npm_bin = "npm.cmd" if sys.platform == "win32" else "npm"
    frontend_cmd = [npm_bin, "run", "dev"]

    processos = []

    try:
        # Inicia Backend
        p_back = subprocess.Popen(
            backend_cmd,
            cwd=ROOT_DIR,
        )
        processos.append(p_back)

        # Inicia Frontend
        p_front = subprocess.Popen(
            frontend_cmd,
            cwd=FRONTEND_DIR,
        )
        processos.append(p_front)

        # Abre o navegador em thread de fundo
        Thread(target=abrir_navegador, daemon=True).start()

        # Aguarda interrupção do usuário ou encerramento de algum processo
        while True:
            for p in processos:
                ret = p.poll()
                if ret is not None:
                    print(f"\n[AVISO] Processo ({p.args}) encerrou com codigo {ret}.")
                    sys.exit(ret)
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n\n[INFO] Encerrando Frontend e Backend...")
    finally:
        for p in processos:
            try:
                if sys.platform == "win32":
                    subprocess.call(["taskkill", "/F", "/T", "/PID", str(p.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                else:
                    p.terminate()
            except Exception:
                pass
        print("[INFO] Todos os servidores foram finalizados com sucesso.\n")

if __name__ == "__main__":
    main()

