"""Painel com resumo e cards (W05 - RF02) e busca com filtros (W06 - RF03)."""
from datetime import datetime

from flask import Blueprint, current_app, g, render_template, request

from .auth import login_obrigatorio
from .db import conectar

bp = Blueprint("painel", __name__)
TIPOS = {"UNIDADE": "Unidade", "WIFI": "Wi-Fi", "CAMERA": "Câmera"}

SQL_PONTOS = """SELECT p.id, p.nome, p.tipo, p.ip, p.serial, p.cto, p.porta_gpon, p.endereco, p.critico,
                       p.status, p.desde, o.nome AS olt
                FROM ponto p LEFT JOIN olt o ON o.id = p.olt_id"""


def _minutos(desde):
    if not desde:
        return None
    return int((datetime.now() - datetime.fromisoformat(desde)).total_seconds() // 60)


def _como_dict(r):
    d = dict(r)
    d["min_no_status"] = _minutos(r["desde"])
    return d


def buscar(texto="", tipo="", olt="", status="", cto=""):
    """Filtros combináveis (CA03). O texto procura em nome, IP, serial e CTO, sem diferenciar maiúsculas."""
    where, args = [], []
    if texto:
        t = f"%{texto.strip().lower()}%"
        where.append("(lower(p.nome) LIKE ? OR p.ip LIKE ? OR lower(p.serial) LIKE ? OR lower(p.cto) LIKE ?)")
        args += [t, t, t, t]
    for campo, valor in (("p.tipo", tipo), ("o.nome", olt), ("p.status", status), ("p.cto", cto)):
        if valor:
            where.append(f"{campo} = ?")
            args.append(valor)
    sql = SQL_PONTOS + (" WHERE " + " AND ".join(where) if where else "")
    sql += " ORDER BY p.status = 'OFFLINE' DESC, p.critico DESC, p.desde ASC, p.nome"
    return [_como_dict(r) for r in conectar().execute(sql, args)]


def resumo():
    db = conectar()
    linhas = db.execute("SELECT tipo, status, COUNT(*) n FROM ponto GROUP BY tipo, status").fetchall()
    r = {"total": 0, "ONLINE": 0, "OFFLINE": 0, "SEM_TESTE": 0, "por_tipo": {}}
    for l in linhas:
        r["total"] += l["n"]
        r[l["status"]] += l["n"]
        t = r["por_tipo"].setdefault(l["tipo"], {"total": 0, "ONLINE": 0, "OFFLINE": 0, "SEM_TESTE": 0})
        t["total"] += l["n"]
        t[l["status"]] += l["n"]
    return r


@bp.route("/")
@login_obrigatorio()
def inicio():
    return render_template("painel.html", resumo=resumo(), pontos=buscar(), tipos=TIPOS,
                           intervalo=current_app.config["INTERVALO_ATUALIZACAO_SEG"])


@bp.route("/busca")
@login_obrigatorio()
def busca():
    f = {k: request.args.get(k, "").strip() for k in ("texto", "tipo", "olt", "status", "cto")}
    olts = [r["nome"] for r in conectar().execute("SELECT nome FROM olt ORDER BY nome")]
    return render_template("busca.html", pontos=buscar(**f), f=f, olts=olts, tipos=TIPOS)


@bp.route("/api/pontos")
@login_obrigatorio()
def api_pontos():
    """Usada pela atualização automática do painel (RF02)."""
    return {"resumo": resumo(), "pontos": buscar(), "gerado_em": datetime.now().isoformat(timespec="seconds"),
            "usuario": g.usuario["login"]}
