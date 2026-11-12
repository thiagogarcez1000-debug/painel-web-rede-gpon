"""Login e perfis (card W04 - RF01, CA01). Senhas guardadas só como hash (PBKDF2 do Werkzeug)."""
import functools
import time
from datetime import datetime

from flask import Blueprint, abort, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from .db import conectar

bp = Blueprint("auth", __name__)
PERFIS = ("admin", "operador", "consulta")


def criar_usuario(login, nome, perfil, senha):
    if perfil not in PERFIS:
        raise ValueError("perfil inválido")
    if len(senha) < 8:
        raise ValueError("a senha precisa ter pelo menos 8 caracteres")
    db = conectar()
    db.execute("INSERT INTO usuario (login, nome, perfil, senha_hash) VALUES (?, ?, ?, ?)",
               (login.strip().lower(), nome.strip(), perfil, generate_password_hash(senha)))
    db.commit()


def registrar(acao, detalhe="", ponto_id=None):
    db = conectar()
    db.execute("INSERT INTO log_acao (usuario_id, ponto_id, acao, detalhe, quando) VALUES (?, ?, ?, ?, ?)",
               (g.usuario["id"] if g.get("usuario") else None, ponto_id, acao, detalhe,
                datetime.now().isoformat(timespec="seconds")))
    db.commit()


@bp.before_app_request
def carregar_usuario():
    uid = session.get("uid")
    g.usuario = None
    if uid:
        g.usuario = conectar().execute("SELECT id, login, nome, perfil FROM usuario WHERE id = ? AND ativo = 1",
                                       (uid,)).fetchone()


def login_obrigatorio(*perfis):
    """@login_obrigatorio() exige qualquer usuário; @login_obrigatorio('admin') exige o perfil."""
    def deco(view):
        @functools.wraps(view)
        def envolta(*a, **k):
            if g.usuario is None:
                if request.path.startswith("/api/"):
                    return {"erro": "login"}, 401
                return redirect(url_for("auth.login", proximo=request.path))
            if perfis and g.usuario["perfil"] not in perfis:
                abort(403)
            return view(*a, **k)
        return envolta
    return deco


@bp.route("/login", methods=["GET", "POST"])
def login():
    erro = None
    if request.method == "POST":
        usuario = conectar().execute("SELECT * FROM usuario WHERE login = ? AND ativo = 1",
                                     (request.form.get("login", "").strip().lower(),)).fetchone()
        if usuario and check_password_hash(usuario["senha_hash"], request.form.get("senha", "")):
            session.clear()
            session["uid"] = usuario["id"]
            g.usuario = usuario
            registrar("login")
            destino = request.args.get("proximo", "")
            return redirect(destino if destino.startswith("/") and not destino.startswith("//") else url_for("painel.inicio"))
        time.sleep(0.5)                       # atrasa tentativas seguidas
        erro = "Usuário ou senha incorretos."
    return render_template("login.html", erro=erro), (401 if erro else 200)


@bp.route("/sair")
def sair():
    session.clear()
    flash("Você saiu do painel.")
    return redirect(url_for("auth.login"))
