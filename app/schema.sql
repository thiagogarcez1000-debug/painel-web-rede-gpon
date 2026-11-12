-- Modelo de dados do painel (card W03). Segue o diagrama de docs/arquitetura.md.
CREATE TABLE IF NOT EXISTS olt (
  id      INTEGER PRIMARY KEY,
  nome    TEXT NOT NULL UNIQUE,
  lat     REAL, lon REAL
);
CREATE TABLE IF NOT EXISTS ponto (
  id        INTEGER PRIMARY KEY,
  nome      TEXT NOT NULL,
  tipo      TEXT NOT NULL CHECK (tipo IN ('UNIDADE','WIFI','CAMERA')),
  ip        TEXT, serial TEXT, cto TEXT, porta_gpon TEXT,
  olt_id    INTEGER REFERENCES olt(id),
  endereco  TEXT, lat REAL, lon REAL,
  critico   INTEGER NOT NULL DEFAULT 0,
  status    TEXT NOT NULL DEFAULT 'SEM_TESTE' CHECK (status IN ('ONLINE','OFFLINE','SEM_TESTE')),
  desde     TEXT,                    -- desde quando está no status atual (ISO 8601)
  UNIQUE (ip)
);
CREATE TABLE IF NOT EXISTS evento_status (
  id        INTEGER PRIMARY KEY,
  ponto_id  INTEGER NOT NULL REFERENCES ponto(id),
  status    TEXT NOT NULL,
  quando    TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS usuario (
  id        INTEGER PRIMARY KEY,
  login     TEXT NOT NULL UNIQUE,
  nome      TEXT NOT NULL,
  perfil    TEXT NOT NULL CHECK (perfil IN ('admin','operador','consulta')),
  senha_hash TEXT NOT NULL,
  ativo     INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS log_acao (
  id        INTEGER PRIMARY KEY,
  usuario_id INTEGER REFERENCES usuario(id),
  ponto_id  INTEGER REFERENCES ponto(id),
  acao      TEXT NOT NULL,
  detalhe   TEXT,
  quando    TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_ponto_status ON ponto(status);
CREATE INDEX IF NOT EXISTS ix_evento_ponto ON evento_status(ponto_id, quando);
