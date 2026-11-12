"""Testes dos cards W03 a W06 (CA01, CA02 e CA03) com banco temporário e dados fictícios."""
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app            # noqa: E402
from app.auth import criar_usuario    # noqa: E402
import importar                       # noqa: E402

SENHA = "senha-de-teste-123"


@pytest.fixture()
def app(tmp_path):
    banco = str(tmp_path / "t.sqlite")
    a = create_app({"BANCO": banco, "SECRET_KEY": "teste"})
    importar.gravar(banco, importar.ficticios())
    with a.app_context():
        for login, perfil in (("adm", "admin"), ("op", "operador"), ("con", "consulta")):
            criar_usuario(login, login.upper(), perfil, SENHA)
    return a


def entrar(cli, login="op", senha=SENHA):
    return cli.post("/login", data={"login": login, "senha": senha})


# ---- W03: banco e importação
def test_banco_tem_as_tabelas_do_modelo(app):
    with sqlite3.connect(app.config["BANCO"]) as c:
        tabelas = {r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"olt", "ponto", "evento_status", "usuario", "log_acao"} <= tabelas


def test_importacao_repetida_nao_duplica(app):
    importar.gravar(app.config["BANCO"], importar.ficticios())
    with sqlite3.connect(app.config["BANCO"]) as c:
        assert c.execute("SELECT COUNT(*) FROM ponto").fetchone()[0] == 60


# ---- W04: login e perfis (CA01)
def test_sem_login_nao_acessa(app):
    cli = app.test_client()
    assert cli.get("/").status_code == 302
    assert cli.get("/busca").status_code == 302
    assert cli.get("/api/pontos").status_code == 401


def test_senha_errada_recusada(app):
    r = entrar(app.test_client(), senha="errada")
    assert r.status_code == 401 and "incorretos" in r.get_data(as_text=True)


@pytest.mark.parametrize("login", ["adm", "op", "con"])
def test_tres_perfis_entram(app, login):
    cli = app.test_client()
    assert entrar(cli, login).status_code == 302
    assert cli.get("/").status_code == 200


def test_senha_guardada_so_como_hash(app):
    with sqlite3.connect(app.config["BANCO"]) as c:
        hashes = [r[0] for r in c.execute("SELECT senha_hash FROM usuario")]
    assert all(SENHA not in h and h.startswith(("pbkdf2:", "scrypt:")) for h in hashes)


def test_login_fica_no_log(app):
    entrar(app.test_client())
    with sqlite3.connect(app.config["BANCO"]) as c:
        assert c.execute("SELECT COUNT(*) FROM log_acao WHERE acao='login'").fetchone()[0] == 1


# ---- W05: painel igual ao banco (CA02)
def test_painel_mostra_o_mesmo_que_o_banco(app):
    cli = app.test_client()
    entrar(cli)
    d = cli.get("/api/pontos").get_json()
    with sqlite3.connect(app.config["BANCO"]) as c:
        fora = c.execute("SELECT COUNT(*) FROM ponto WHERE status='OFFLINE'").fetchone()[0]
    assert d["resumo"]["OFFLINE"] == fora == sum(p["status"] == "OFFLINE" for p in d["pontos"])
    assert d["resumo"]["total"] == len(d["pontos"]) == 60
    assert d["pontos"][0]["status"] == "OFFLINE"            # fora do ar aparece primeiro


# ---- W06: busca e filtros (CA03)
def test_busca_por_ip_serial_e_nome(app):
    cli = app.test_client()
    entrar(cli)
    assert "192.0.2.10" in cli.get("/busca?texto=192.0.2.10").get_data(as_text=True)
    with sqlite3.connect(app.config["BANCO"]) as c:
        serial, nome = c.execute("SELECT serial, nome FROM ponto LIMIT 1").fetchone()
    assert "1 ponto(s)" in cli.get(f"/busca?texto={serial.lower()}").get_data(as_text=True)
    assert nome in cli.get("/busca?texto=" + nome.split()[-1]).get_data(as_text=True)


def test_filtros_combinados(app):
    cli = app.test_client()
    entrar(cli)
    html = cli.get("/busca?tipo=CAMERA&status=OFFLINE").get_data(as_text=True)
    with sqlite3.connect(app.config["BANCO"]) as c:
        n = c.execute("SELECT COUNT(*) FROM ponto WHERE tipo='CAMERA' AND status='OFFLINE'").fetchone()[0]
    assert f"{n} ponto(s)" in html


def test_texto_da_busca_nao_injeta_sql(app):
    cli = app.test_client()
    entrar(cli)
    assert cli.get("/busca?texto=' OR 1=1 --").status_code == 200
    assert "0 ponto(s)" in cli.get("/busca?texto=' OR 1=1 --").get_data(as_text=True)
