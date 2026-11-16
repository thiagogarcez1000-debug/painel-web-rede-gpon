"""Gestão de usuários pelo administrador (W13 - RF11). Sprint 3, implementado em 15/11/2026."""
from flask import Blueprint, flash, g, redirect, render_template, request, url_for

from .auth import PERFIS, criar_usuario, login_obrigatorio, registrar
from .db import conectar

bp = Blueprint("usuarios", __name__)


@bp.route("/usuarios")
@login_obrigatorio("admin")
def lista():
    us = conectar().execute("SELECT id, login, nome, perfil, ativo FROM usuario ORDER BY ativo DESC, nome").fetchall()
    return render_template("usuarios.html", us=us, perfis=PERFIS)


@bp.route("/usuarios/novo", methods=["POST"])
@login_obrigatorio("admin")
def novo():
    f = request.form
    try:
        criar_usuario(f.get("login", ""), f.get("nome", ""), f.get("perfil", ""), f.get("senha", ""))
        registrar("usuario_criado", f"{f.get('login', '').strip().lower()} ({f.get('perfil')})")
        flash("Usuário criado.")
    except Exception as e:                       # perfil inválido, senha curta ou login repetido
        flash("Não foi possível criar: " + ("login já existe" if "UNIQUE" in str(e) else str(e)) + ".")
    return redirect(url_for("usuarios.lista"))


@bp.route("/usuarios/<int:uid>", methods=["POST"])
@login_obrigatorio("admin")
def alterar(uid):
    db = conectar()
    u = db.execute("SELECT * FROM usuario WHERE id = ?", (uid,)).fetchone()
    if u is None:
        return redirect(url_for("usuarios.lista"))
    perfil = request.form.get("perfil", u["perfil"])
    ativo = 1 if request.form.get("ativo") == "1" else 0
    if uid == g.usuario["id"] and (not ativo or perfil != "admin"):
        flash("Você não pode desativar nem rebaixar o próprio usuário.")
        return redirect(url_for("usuarios.lista"))
    if perfil not in PERFIS:
        flash("Perfil inválido.")
        return redirect(url_for("usuarios.lista"))
    db.execute("UPDATE usuario SET perfil = ?, ativo = ? WHERE id = ?", (perfil, ativo, uid))
    db.commit()
    registrar("usuario_alterado", f"{u['login']}: perfil {u['perfil']}->{perfil}, ativo {u['ativo']}->{ativo}")
    flash("Usuário atualizado.")
    return redirect(url_for("usuarios.lista"))
