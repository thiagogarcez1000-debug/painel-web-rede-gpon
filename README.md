# Painel Web de Monitoramento da Rede Óptica Municipal (GPON)

Projeto extensionista da disciplina **Programação Web Aplicada** – UniEVANGÉLICA, 2026/2.

**Aluno:** Thiago José da Silva Garcez
**Instituição parceira:** Prefeitura Municipal de Anápolis – Gerência de Tecnologia da Informação
**Kanban:** https://trello.com/b/Zw9klzwh/painel-web-gpon-programacao-web-aplicada

## Objetivo
Painel web, acessível pelo computador e pelo celular (rede interna ou VPN), para acompanhar em tempo real
os cerca de 580 pontos da rede GPON da Prefeitura (unidades públicas, Wi-Fi público e câmeras), com busca,
detalhe do ponto, histórico de quedas, mapa com a rota da fibra, destaque de quedas em massa e alertas.

## Situação
- Já existe um **protótipo** (servidor HTTP próprio em Python) usado internamente pela Gerência de TI.
  Ele fica em repositório **privado**, porque contém configurações e dados da rede.
- Este repositório é a versão estruturada da disciplina (Flask + SQLite), desenvolvida ao longo das sprints.

## Estrutura planejada
- `app/` – aplicação Flask (rotas, templates, API JSON, autenticação)
- `app/static/` – CSS e JavaScript do painel (responsivo)
- `varredura/` – serviço de varredura por ping
- `docs/` – arquitetura, modelo de dados e documentação

## Segurança
Senhas, chaves de API e planilhas com IPs **não** são versionadas. Use `config.exemplo.json` como modelo
e crie o `config.json` apenas no servidor interno.

## Sprints
| Sprint | Período | Foco |
|---|---|---|
| 1 | 28/09 a 11/10/2026 | Requisitos, wireframes, arquitetura e estrutura do projeto |
| 2 | 12/10 a 25/10/2026 | Banco de dados, login, painel com cards, busca e testes de responsividade |
| 3 | 26/10 a 08/11/2026 | Detalhe do ponto, histórico, mapa e rota, incidentes e alertas |
| 4 | 09/11 a 22/11/2026 | Reinício de ONU, relatórios, testes finais e validação |
