"""Cria um usuário do painel (a senha é pedida no terminal e guardada só como hash).
    python criar_usuario.py thiago "Thiago Garcez" admin
"""
import getpass
import sys

from app import create_app
from app.auth import criar_usuario

if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    login, nome, perfil = sys.argv[1:]
    with create_app().app_context():
        criar_usuario(login, nome, perfil, getpass.getpass("Senha (mínimo 8 caracteres): "))
    print("Usuário criado.")
