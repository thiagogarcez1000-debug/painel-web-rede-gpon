"""Importação dos pontos para o SQLite (card W03).

    python importar.py --ficticio                 -> 60 pontos fictícios (desenvolvimento e evidências)
    python importar.py --planilha dados/pontos.xlsx   -> planilha real, só no servidor da TI (fora do Git)

A planilha real usa as colunas do inventário: Descrição, Tipo, IP gerência, Serial, CTO, OLT, PON, Endereço, Latitude, Longitude.
Linhas sem IP são ignoradas; IP repetido atualiza o ponto existente (a importação pode ser repetida).
"""
import argparse
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from app import RAIZ
from app.db import criar_tabelas

TIPO_DA_PLANILHA = {"unidade": "UNIDADE", "wi-fi (ap)": "WIFI", "wifi": "WIFI", "câmera (ponto)": "CAMERA", "camera": "CAMERA"}
CRITICOS = ("SAMU", "UPA", "HOSPITAL", "CAIS", "POLICLÍNICA", "MATERNIDADE")


def _olt(c, nome):
    if not nome:
        return None
    c.execute("INSERT OR IGNORE INTO olt (nome) VALUES (?)", (nome,))
    return c.execute("SELECT id FROM olt WHERE nome = ?", (nome,)).fetchone()[0]


def gravar(banco, linhas):
    criar_tabelas(banco)
    with sqlite3.connect(banco) as c:
        n = 0
        for l in linhas:
            olt_id = _olt(c, l.get("olt"))
            c.execute("""INSERT INTO ponto (nome, tipo, ip, serial, cto, porta_gpon, olt_id, endereco, lat, lon, critico, status, desde)
                         VALUES (:nome, :tipo, :ip, :serial, :cto, :porta_gpon, :olt_id, :endereco, :lat, :lon, :critico, :status, :desde)
                         ON CONFLICT(ip) DO UPDATE SET nome=excluded.nome, tipo=excluded.tipo, serial=excluded.serial,
                           cto=excluded.cto, porta_gpon=excluded.porta_gpon, olt_id=excluded.olt_id, endereco=excluded.endereco,
                           lat=excluded.lat, lon=excluded.lon, critico=excluded.critico""",
                      {**l, "olt_id": olt_id, "critico": int(any(k in l["nome"].upper() for k in CRITICOS))})
            n += 1
    return n


def ficticios(qtd=60, semente=11):
    """Nomes e endereços inventados; IPs na faixa de documentação 192.0.2.0/24 e 198.51.100.0/24 (RFC 5737)."""
    rnd = random.Random(semente)
    agora = datetime.now()
    bases = [("UNIDADE", ["UBS", "CMEI", "Escola Municipal", "CRAS", "Secretaria"]),
             ("WIFI", ["Wi-Fi Praça", "Wi-Fi Parque", "Wi-Fi Terminal"]), ("CAMERA", ["Câmera Av.", "Câmera Praça", "Câmera Feira"])]
    bairros = ["Centro", "Jundiaí", "Vila Jaiara", "Maracanã", "Recanto do Sol", "Bairro de Lourdes", "Industrial", "Boa Vista"]
    out = []
    for i in range(qtd):
        tipo, prefixos = bases[i % 3]
        olt = f"OLT 0{rnd.randint(1, 6)}"
        porta = str(rnd.randint(1, 16))
        nome = f"{rnd.choice(prefixos)} {rnd.choice(bairros)} {i + 1:02d}"
        if i in (0, 3, 6, 9):                     # trecho comum: porta 7 da OLT 02 (como no incidente de 06/10)
            olt, porta = "OLT 02", "7"
            nome = {0: "SAMU Base Central (fictício)", 3: "UPA Norte (fictícia)"}.get(i, nome)
        fora = olt == "OLT 02" and porta in ("7", "8") or rnd.random() < 0.06
        out.append({"nome": nome, "tipo": tipo,
                    "ip": f"192.0.2.{i + 10}" if i < 200 else None, "serial": f"FICT{rnd.randint(100000, 999999)}",
                    "cto": f"CTO-{olt[-1]}{porta.zfill(2)}-{rnd.randint(1, 8):02d}", "porta_gpon": porta, "olt": olt,
                    "endereco": f"Endereço fictício, {rnd.choice(bairros)} - Anápolis/GO",
                    "lat": round(-16.33 + rnd.uniform(-0.04, 0.04), 6), "lon": round(-48.95 + rnd.uniform(-0.04, 0.04), 6),
                    "status": "OFFLINE" if fora else "ONLINE",
                    "desde": (agora - timedelta(minutes=rnd.randint(5, 600))).isoformat(timespec="seconds")})
    return out


def da_planilha(caminho):
    import openpyxl
    ws = openpyxl.load_workbook(caminho, read_only=True, data_only=True).active
    linhas = ws.iter_rows(values_only=True)
    cab = [str(c or "").strip() for c in next(linhas)]
    ix = {n: i for i, n in enumerate(cab)}
    def v(r, n):
        return r[ix[n]] if n in ix and r[ix[n]] is not None else None
    for r in linhas:
        if not v(r, "IP gerência"):
            continue
        yield {"nome": str(v(r, "Descrição") or "").strip(), "tipo": TIPO_DA_PLANILHA.get(str(v(r, "Tipo") or "").strip().lower(), "UNIDADE"),
               "ip": str(v(r, "IP gerência")).strip(), "serial": v(r, "Serial"), "cto": v(r, "CTO"), "porta_gpon": v(r, "PON"),
               "olt": v(r, "OLT"), "endereco": v(r, "Endereço"), "lat": v(r, "Latitude"), "lon": v(r, "Longitude"),
               "status": "SEM_TESTE", "desde": None}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--ficticio", action="store_true")
    g.add_argument("--planilha")
    ap.add_argument("--banco", default=str(RAIZ / "dados" / "painel.sqlite"))
    a = ap.parse_args()
    n = gravar(a.banco, ficticios() if a.ficticio else da_planilha(a.planilha))
    print(f"{n} pontos gravados em {Path(a.banco).name}")
