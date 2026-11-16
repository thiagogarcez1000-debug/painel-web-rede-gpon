"""Detalhe do ponto com histórico de quedas (W08 - RF04) e mapa com a rota da fibra (W09 - RF05).
Sprint 3, implementado em 15/11/2026. A rota usa as posições cadastradas: OLT -> CTO -> ponto."""
import math
from datetime import datetime

from flask import Blueprint, abort, render_template

from .auth import login_obrigatorio
from .db import conectar
from .painel import TIPOS, _minutos

bp = Blueprint("detalhe", __name__)


def distancia_m(a, b):
    (la1, lo1), (la2, lo2) = a, b
    f1, f2 = math.radians(la1), math.radians(la2)
    h = math.sin((f2 - f1) / 2) ** 2 + math.cos(f1) * math.cos(f2) * math.sin(math.radians(lo2 - lo1) / 2) ** 2
    return 2 * 6371000 * math.asin(math.sqrt(h))


def quedas(ponto_id):
    """Pares OFFLINE -> ONLINE do evento_status, do mais recente para o mais antigo. Queda sem retorno fica em aberto."""
    ev = conectar().execute("SELECT status, quando FROM evento_status WHERE ponto_id = ? ORDER BY quando", (ponto_id,)).fetchall()
    out, ini = [], None
    for e in ev:
        if e["status"] == "OFFLINE" and ini is None:
            ini = e["quando"]
        elif e["status"] == "ONLINE" and ini is not None:
            dur = int((datetime.fromisoformat(e["quando"]) - datetime.fromisoformat(ini)).total_seconds() // 60)
            out.append({"inicio": ini, "fim": e["quando"], "duracao_min": dur})
            ini = None
    if ini is not None:
        out.append({"inicio": ini, "fim": None, "duracao_min": _minutos(ini)})
    return list(reversed(out))


def rota(p):
    """Nós da rota (OLT, CTO, ponto) com coordenadas e distância em linha reta de cada trecho."""
    nos = []
    if p["olt_lat"] is not None:
        nos.append({"tipo": "OLT", "nome": p["olt"], "lat": p["olt_lat"], "lon": p["olt_lon"]})
    if p["cto_lat"] is not None:
        nos.append({"tipo": "CTO", "nome": p["cto"], "lat": p["cto_lat"], "lon": p["cto_lon"]})
    if p["lat"] is not None:
        nos.append({"tipo": "PONTO", "nome": p["nome"], "lat": p["lat"], "lon": p["lon"]})
    for a, b in zip(nos, nos[1:]):
        b["trecho_m"] = round(distancia_m((a["lat"], a["lon"]), (b["lat"], b["lon"])))
    completa = [n["tipo"] for n in nos] == ["OLT", "CTO", "PONTO"]
    return {"nos": nos, "completa": completa, "total_m": sum(n.get("trecho_m", 0) for n in nos)}


def svg_rota(r, largura=560, altura=300, margem=36):
    """Projeta a rota num SVG simples (sem mapa de fundo: a rede interna não acessa servidores de mapas)."""
    if len(r["nos"]) < 2:
        return None
    las = [n["lat"] for n in r["nos"]]; los = [n["lon"] for n in r["nos"]]
    dla, dlo = (max(las) - min(las)) or 1e-4, (max(los) - min(los)) or 1e-4
    esc = min((largura - 2 * margem) / dlo, (altura - 2 * margem) / dla)
    for n in r["nos"]:
        n["x"] = round(margem + (n["lon"] - min(los)) * esc, 1)
        n["y"] = round(altura - margem - (n["lat"] - min(las)) * esc, 1)
    return {"w": largura, "h": altura, "pts": " ".join(f'{n["x"]},{n["y"]}' for n in r["nos"])}


def carregar(ponto_id):
    p = conectar().execute("""SELECT p.*, o.nome AS olt, o.lat AS olt_lat, o.lon AS olt_lon, c.lat AS cto_lat, c.lon AS cto_lon
                              FROM ponto p LEFT JOIN olt o ON o.id = p.olt_id LEFT JOIN cto c ON c.nome = p.cto
                              WHERE p.id = ?""", (ponto_id,)).fetchone()
    if p is None:
        abort(404)
    return p


@bp.route("/ponto/<int:ponto_id>")
@login_obrigatorio()
def ponto(ponto_id):
    p = carregar(ponto_id)
    r = rota(p)
    return render_template("detalhe.html", p=p, tipos=TIPOS, quedas=quedas(ponto_id), rota=r, svg=svg_rota(r),
                           min_no_status=_minutos(p["desde"]))


@bp.route("/api/ponto/<int:ponto_id>")
@login_obrigatorio()
def api_ponto(ponto_id):
    p = carregar(ponto_id)
    return {"id": p["id"], "nome": p["nome"], "status": p["status"], "quedas": quedas(ponto_id), "rota": rota(p)}
