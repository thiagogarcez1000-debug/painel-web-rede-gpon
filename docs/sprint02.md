# Registro da Sprint 02 (W03–W07)

Período oficial da Sprint 02: 12/10 a 25/10/2026. **Nesse período não houve commits** neste repositório.
A implementação abaixo foi feita em **12/11/2026** (recuperação do atraso, já no período da Sprint 4).

## O que foi implementado (12/11/2026)

| Card | Entrega | Situação |
|---|---|---|
| W03 | Estrutura Flask (`app/`), banco SQLite (`schema.sql`), importação (`importar.py --ficticio` e `--planilha`) | Implementado e testado em ambiente de desenvolvimento |
| W04 | Login com senha em hash, perfis admin/operador/consulta, registro de acesso em `log_acao` | Implementado e testado |
| W05 | Painel com resumo por status/tipo, cartões coloridos, fora do ar primeiro, atualização automática (`/api/pontos`) | Implementado e testado |
| W06 | Busca por nome, IP, serial ou CTO e filtros por tipo, OLT e status | Implementado e testado |
| W07 | Verificação de responsividade em 1280 px e 390 px (Chromium) | Parcial: falta teste em celular real e outros navegadores |

## Dados

Somente **dados fictícios** (60 pontos, IPs da faixa de documentação 192.0.2.0/24 – RFC 5737).
Dados reais da rede (planilhas, KMZ, IPs) não entram no Git (ver `.gitignore`).

## Testes automatizados (`python -m pytest -q testes`)

Resultado em 12/11/2026: **13 passed**.

| Teste | Critério |
|---|---|
| tabelas criadas; reimportação sem duplicar | W03 |
| sem login → redireciona/401; senha errada → 401; 3 perfis entram; senha só em hash; login registrado | W04 / CA01 |
| `/api/pontos` igual ao banco; fora do ar primeiro | W05 / CA02 |
| busca por IP, serial, nome; filtros combinados; texto com SQL não quebra a consulta | W06 / CA03 |

## Responsividade (W07, parcial)

| Largura | Rolagem horizontal | Resultado |
|---|---|---|
| 1280 px (desktop) | não (scrollWidth = 1280) | grade em 4 colunas |
| 390 px (celular emulado) | não (scrollWidth = 390) | filtros e cartões em 1 coluna |

## Validação

Feita por mim (autoverificação contra CA01–CA03). A validação com a equipe da TI da Prefeitura
(parceiro) ainda **não foi realizada** e fica prevista para a Sprint 03.

## Pendências levadas para a Sprint 03

- W07: teste em celular real e em Firefox/Edge.
- W08 (detalhe do ponto), W09/W10 (rotas já documentadas em `docs/`).
- Importação das planilhas reais somente no servidor interno.
- Validação com a equipe da TI.
