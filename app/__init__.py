"""Painel Web da Rede GPON - fábrica da aplicação Flask (card W03)."""
import json
import os
import secrets
from pathlib import Path

from flask import Flask

from . import db

RAIZ = Path(__file__).resolve().parents[1]


def create_app(teste_config=None):
    app = Flask(__name__)
    cfg = {"BANCO": str(RAIZ / "dados" / "painel.sqlite"), "SECRET_KEY": None,
           "INTERVALO_ATUALIZACAO_SEG": 30}
    arq = RAIZ / "config.json"                       # só no servidor; fora do Git
    if arq.exists():
        cfg.update({k: v for k, v in json.loads(arq.read_text(encoding="utf-8")).items() if k in cfg})
    if teste_config:
        cfg.update(teste_config)
    if not cfg["SECRET_KEY"] or str(cfg["SECRET_KEY"]).startswith("<"):
        cfg["SECRET_KEY"] = os.environ.get("PAINEL_SECRET_KEY") or secrets.token_hex(32)
    app.config.update(cfg, SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")

    db.criar_tabelas(app.config["BANCO"])
    app.teardown_appcontext(db.fechar)

    from .auth import bp as auth_bp
    from .painel import bp as painel_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(painel_bp)
    return app
