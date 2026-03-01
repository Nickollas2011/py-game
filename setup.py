import sys
import subprocess
import venv
from pathlib import Path
import re

# Configuracoes do projeto atual
PROJECT_NAME = "Jogo 2D Tkinter"
VENV_DIR = Path("venv")
REQUIREMENTS_FILE = Path("requirements.txt")
APP_FILE = Path("jogo_2d_3_fases.py")
REQUIRED_PACKAGES = set()

def is_venv():
    """Verifica se o script esta rodando dentro de um ambiente virtual."""
    return (
        hasattr(sys, "real_prefix")
        or (hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix)
    )

def get_venv_python():
    """Retorna o caminho do executavel Python do venv."""
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"

def _normalize_req_name(name: str) -> str:
    return name.strip().lower().replace("_", "-")


def _parse_requirements_file(path: Path) -> set:
    if not path.exists():
        return set()
    reqs = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # Remove extras/markers/version specifiers for comparison.
        name = re.split(r"[<>=!~;\\[]", line, maxsplit=1)[0].strip()
        reqs.add(_normalize_req_name(name))
    return reqs


def verify_requirements():
    """Valida se requirements.txt contem o necessario para o projeto."""
    if not REQUIRED_PACKAGES:
        return True

    if not REQUIREMENTS_FILE.exists():
        print("Erro: requirements.txt nao encontrado.")
        return False

    reqs = _parse_requirements_file(REQUIREMENTS_FILE)
    missing = sorted({ _normalize_req_name(r) for r in REQUIRED_PACKAGES } - reqs)
    if missing:
        print("Requisitos faltando no requirements.txt:")
        for pkg in missing:
            print(f"- {pkg}")
        return False

    return True


def install_dependencies():
    """Instala as dependencias listadas."""
    if not REQUIRED_PACKAGES:
        return True

    if not REQUIREMENTS_FILE.exists():
        print("Erro: requirements.txt nao encontrado.")
        return False

    if not _ensure_pip():
        return False

    try:
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-q",
                "--upgrade",
                "--only-binary=:all:",
                "-r",
                str(REQUIREMENTS_FILE),
            ]
        )
        return True
    except subprocess.CalledProcessError as exc:
        print(f"Erro ao instalar dependencias: {exc}")
        return False


def _ensure_pip():
    """Garante que pip exista no Python/venv atual."""
    check_cmd = [sys.executable, "-m", "pip", "--version"]
    if subprocess.call(check_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
        return True

    print("pip nao encontrado neste ambiente. Tentando instalar com ensurepip...")
    try:
        subprocess.check_call([sys.executable, "-m", "ensurepip", "--upgrade"])
    except subprocess.CalledProcessError as exc:
        print(f"Falha ao preparar pip com ensurepip: {exc}")
        return False

    if subprocess.call(check_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0:
        print("pip continua indisponivel apos ensurepip.")
        return False

    return True


def main():
    # Modo silencioso por padrao. Ative logs com --verbose.
    verbose = "--verbose" in sys.argv
    if verbose:
        print("Iniciando setup do ambiente...\n")

    # 1. Garantir Venv (Ambiente Virtual)
    if not is_venv():
        if verbose:
            print("Ambiente virtual NAO detectado/ativo.")

        if not VENV_DIR.exists():
            if verbose:
                print(f"Criando venv em: {VENV_DIR}")
            try:
                venv.create(VENV_DIR, with_pip=True)
            except Exception as exc:
                print(f"Erro ao criar ambiente virtual em {VENV_DIR}: {exc}")
                print("Tente criar manualmente com: python -m venv venv")
                return

        venv_python = get_venv_python()
        if not venv_python.exists():
            print(f"Erro critico: Python da venv nao encontrado em {venv_python}")
            return

        if verbose:
            print("Reiniciando setup dentro da venv para garantir isolamento...")
        # Re-executa este script usando o Python da venv
        try:
            return_code = subprocess.call([str(venv_python), __file__] + sys.argv[1:])
            if return_code != 0:
                print(f"Setup finalizado com erro dentro da venv (codigo {return_code}).")
        except KeyboardInterrupt:
            print("\nAplicacao interrompida pelo usuario.")
        return

    if verbose:
        print("Rodando dentro do ambiente virtual.")

    # 2. Verificar requisitos
    if verbose:
        print(f"Verificando requisitos do projeto: {PROJECT_NAME}...")
    if not verify_requirements():
        print("Corrija o requirements.txt e rode novamente.")
        return

    # 3. Instalar Bibliotecas
    if verbose:
        print("Verificando dependencias do Python...")
        print(f"Instalando dependencias de {REQUIREMENTS_FILE}...")
    if not install_dependencies():
        print("Nao foi possivel instalar dependencias.")
        return
    if verbose:
        print("Instalacao concluida.")

    # 4. Identificar ambiente
    if verbose:
        if sys.platform.startswith("win"):
            print("Ambiente detectado: Windows")
        elif sys.platform.startswith("linux"):
            print("Ambiente detectado: Linux")
        else:
            print(f"Ambiente detectado: {sys.platform}")

    # 5. Executar app no terminal
    if not APP_FILE.exists():
        print(f"Erro: arquivo principal nao encontrado ({APP_FILE}).")
        return
    if verbose:
        print(f"\nIniciando {PROJECT_NAME} ({APP_FILE}) no terminal...")
    print(f"Rodando: python {APP_FILE}")
    try:
        subprocess.call([sys.executable, str(APP_FILE)])
    except KeyboardInterrupt:
        print("\nAplicacao interrompida pelo usuario.")
    else:
        if verbose:
            print("Aplicacao finalizada.")

if __name__ == "__main__":
    main()
