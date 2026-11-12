"""Conexão com o SQLite e criação do banco (card W03)."""
import sqlite3
from pathlib import Path

from flask import current_app, g


def conectar():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["BANCO"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def fechar(_=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def criar_tabelas(caminho_banco):
    Path(caminho_banco).parent.mkdir(parents=True, exist_ok=True)
    sql = (Path(__file__).parent / "schema.sql").read_text(encoding="utf-8")
    with sqlite3.connect(caminho_banco) as c:
        c.executescript(sql)
