"""Testes da Sprint 3 (15/11/2026): detalhe e histórico (W08, CA05/CA08), rota (W09, CA05), gestão de usuários
(W13, RF11), permissões por perfil (CA01) e filtro por CTO (CA03). Dados fictícios em banco temporário."""
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
    lin = importar.ficticios()
    importar.gravar(banco, lin, importar.extras_ficticios(lin))
    with a.app_context():
        for login, perfil in (("adm", "admin"), ("op", "operador"), ("con", "consulta")):
            criar_usuario(login, login.upper(), perfil, SENHA)
    return a


def entrar(cli, login="op", senha=SENHA):
    return cli.post("/login", data={"login": login, "senha": senha})


def um_ponto_com_quedas(banco):
    with sqlite3.connect(banco) as c:
        return c.execute("""SELECT ponto_id, COUNT(*) FROM evento_status WHERE status = 'ONLINE'
                            GROUP BY ponto_id ORDER BY 2 DESC LIMIT 1""").fetchone()


# ---- W08: detalhe e histórico (RF04)
def test_detalhe_mostra_historico_igual_ao_banco(app):
    pid, voltas = um_ponto_com_quedas(app.config["BANCO"])
    cli = app.test_client(); entrar(cli)
    j = cli.get(f"/api/ponto/{pid}").get_json()
    encerradas = [q for q in j["quedas"] if q["fim"]]
    assert len(encerradas) == voltas
    assert all(q["duracao_min"] > 0 for q in encerradas)
    html = cli.get(f"/ponto/{pid}").get_data(as_text=True)
    assert f"Histórico de quedas ({len(j['quedas'])})" in html


def test_ponto_inexistente_404(app):
    cli = app.test_client(); entrar(cli)
    assert cli.get("/ponto/99999").status_code == 404


# ---- CA08: histórico continua depois de reiniciar a aplicação
def test_ca08_historico_persiste_apos_reiniciar(app):
    pid, _ = um_ponto_com_quedas(app.config["BANCO"])
    cli = app.test_client(); entrar(cli)
    antes = cli.get(f"/api/ponto/{pid}").get_json()["quedas"]
    novo = create_app({"BANCO": app.config["BANCO"], "SECRET_KEY": "outra"})   # "reinício": nova aplicação, mesmo banco
    cli2 = novo.test_client(); entrar(cli2)
    depois = cli2.get(f"/api/ponto/{pid}").get_json()["quedas"]
    assert [(q["inicio"], q["fim"]) for q in depois if q["fim"]] == [(q["inicio"], q["fim"]) for q in antes if q["fim"]]
    assert [q["duracao_min"] for q in depois if q["fim"]] == [q["duracao_min"] for q in antes if q["fim"]]


# ---- W09: rota OLT -> CTO -> ponto (RF05)
def test_rota_com_olt_cto_e_ponto(app):
    cli = app.test_client(); entrar(cli)
    r = cli.get("/api/ponto/1").get_json()["rota"]
    assert [n["tipo"] for n in r["nos"]] == ["OLT", "CTO", "PONTO"] and r["completa"]
    assert all(n["trecho_m"] > 0 for n in r["nos"][1:]) and r["total_m"] > 0
    assert "<polyline" in cli.get("/ponto/1").get_data(as_text=True)


def test_rota_incompleta_avisa(app):
    with sqlite3.connect(app.config["BANCO"]) as c:
        c.execute("UPDATE ponto SET lat = NULL, lon = NULL WHERE id = 2")
    cli = app.test_client(); entrar(cli)
    assert not cli.get("/api/ponto/2").get_json()["rota"]["completa"]
    assert "Rota incompleta" in cli.get("/ponto/2").get_data(as_text=True)


# ---- CA01: o que cada perfil pode e não pode fazer
ROTAS = ["/", "/busca", "/ponto/1", "/api/pontos", "/api/ponto/1", "/usuarios"]
ESPERADO = {"admin": [200, 200, 200, 200, 200, 200],
            "operador": [200, 200, 200, 200, 200, 403],
            "consulta": [200, 200, 200, 200, 200, 403]}


@pytest.mark.parametrize("login,perfil", [("adm", "admin"), ("op", "operador"), ("con", "consulta")])
def test_ca01_matriz_de_permissoes(app, login, perfil):
    cli = app.test_client(); entrar(cli, login)
    assert [cli.get(r).status_code for r in ROTAS] == ESPERADO[perfil]
    # alterar usuários (POST) também é recusado para quem não é admin
    st = cli.post("/usuarios/novo", data={"login": "x" + login, "nome": "X", "perfil": "consulta", "senha": SENHA}).status_code
    assert st == (302 if perfil == "admin" else 403)


def test_ca01_sem_login_nada_abre(app):
    cli = app.test_client()
    assert [cli.get(r).status_code for r in ROTAS] == [302, 302, 302, 401, 401, 302]


# ---- W13: gestão de usuários (RF11)
def test_w13_admin_cria_altera_e_desativa(app):
    adm = app.test_client(); entrar(adm, "adm")
    adm.post("/usuarios/novo", data={"login": "tecnico1", "nome": "Técnico 1", "perfil": "consulta", "senha": SENHA})
    t = app.test_client()
    assert entrar(t, "tecnico1").status_code == 302                       # criado e entra
    with sqlite3.connect(app.config["BANCO"]) as c:
        uid = c.execute("SELECT id FROM usuario WHERE login = 'tecnico1'").fetchone()[0]
    adm.post(f"/usuarios/{uid}", data={"perfil": "operador", "ativo": "1"})
    adm.post(f"/usuarios/{uid}", data={"perfil": "operador", "ativo": "0"})
    assert entrar(app.test_client(), "tecnico1").status_code == 401        # desativado não entra
    with sqlite3.connect(app.config["BANCO"]) as c:
        perfil = c.execute("SELECT perfil FROM usuario WHERE id = ?", (uid,)).fetchone()[0]
        acoes = [r[0] for r in c.execute("SELECT acao FROM log_acao WHERE acao LIKE 'usuario_%'")]
    assert perfil == "operador" and acoes.count("usuario_alterado") == 2 and "usuario_criado" in acoes


def test_w13_admin_nao_se_desativa(app):
    adm = app.test_client(); entrar(adm, "adm")
    with sqlite3.connect(app.config["BANCO"]) as c:
        uid = c.execute("SELECT id FROM usuario WHERE login = 'adm'").fetchone()[0]
    adm.post(f"/usuarios/{uid}", data={"perfil": "admin", "ativo": "0"})
    assert entrar(app.test_client(), "adm").status_code == 302


# ---- CA03: filtro por CTO, isolado e combinado
def test_ca03_filtro_por_cto(app):
    cli = app.test_client(); entrar(cli)
    with sqlite3.connect(app.config["BANCO"]) as c:
        cto, n, olt = c.execute("""SELECT p.cto, COUNT(*), o.nome FROM ponto p JOIN olt o ON o.id = p.olt_id
                                   GROUP BY p.cto ORDER BY 2 DESC LIMIT 1""").fetchone()
        n_comb = c.execute("""SELECT COUNT(*) FROM ponto p JOIN olt o ON o.id = p.olt_id
                              WHERE p.cto = ? AND o.nome = ? AND p.tipo = 'UNIDADE'""", (cto, olt)).fetchone()[0]
    assert f"{n} ponto(s) encontrado(s)" in cli.get(f"/busca?cto={cto}").get_data(as_text=True)
    assert f"{n_comb} ponto(s) encontrado(s)" in cli.get(f"/busca?cto={cto}&olt={olt}&tipo=UNIDADE").get_data(as_text=True)
    assert "consulta em" in cli.get("/busca?cto=" + cto).get_data(as_text=True)      # indicador de tempo
