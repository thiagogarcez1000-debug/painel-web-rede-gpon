# Registro da Sprint 03 (W08, W09, W13 e testes do MVP)

Período oficial: 26/10 a 08/11/2026. **Nada foi feito no período** (nenhum commit, nenhum card movido).
A implementação abaixo foi feita em **15/11/2026**, no período da Sprint 4, com dados fictícios.

| Card | Entrega | Situação |
|---|---|---|
| W08 | Detalhe do ponto (`/ponto/<id>`): dados de rede, tempo fora do ar e histórico de quedas a partir de `evento_status` | Implementado e testado em desenvolvimento |
| W09 | Rota da fibra OLT → CTO → ponto desenhada no detalhe (tabela `cto` nova); aviso de rota incompleta | Implementado com posições fictícias; importação do KMZ real pendente |
| W13 | Gestão de usuários (`/usuarios`, só admin): criar, mudar perfil, desativar/reativar, com registro em `log_acao` | Implementado e testado |
| W07 | Telas verificadas em Chromium (1280 px) e em dois celulares emulados (Pixel 7 e Galaxy S9+) | Parcial: falta Edge e celulares reais |

## MVP e RF05
RF05 (mapa e rota) continua no MVP, como na Seção 6.2 do relatório. Não houve pedido nem decisão da docente para retirá-lo.
A revisão de 12/11, que tratava o W09 como condicionado, foi desfeita em 15/11: o W09 foi implementado com dados fictícios.

## Testes (`python -m pytest -q testes`) – 15/11/2026: 25 passed
- `test_painel.py` (13, Sprint 2) e `test_sprint3.py` (12, novos).
- CA01: matriz de permissões por perfil (admin, operador, consulta) em 6 rotas e no POST de usuários; sem login, nada abre.
- CA03: filtro por CTO isolado e combinado com OLT e tipo; indicador de tempo da consulta na tela.
- CA05/CA08: histórico igual ao banco e igual depois de "reiniciar" a aplicação com o mesmo banco.
- W13: criar, alterar, desativar (desativado não entra), admin não se desativa, ações no log.

## Medições (Chromium, servidor de desenvolvimento)
| Ambiente | Carga do painel (média de 5) | Painel | Busca | Detalhe | Usuários |
|---|---|---|---|---|---|
| Chromium 1280 px | 33 ms | sem rolagem | sem rolagem | sem rolagem | sem rolagem |
| Pixel 7 (emulado) | 24 ms | sem rolagem | sem rolagem | sem rolagem | sem rolagem |
| Galaxy S9+ (emulado) | 31 ms | sem rolagem | sem rolagem | sem rolagem | sem rolagem |

Perfil consulta: menu Usuários não aparece e `/usuarios` responde 403.

## Pendências para a Sprint 4
- Importar planilhas e KMZ reais no servidor interno e comparar o painel com o serviço de varredura no mesmo ciclo (CA02).
- Edge e dois celulares Android reais (CA04); 10 pontos sorteados com a equipe (CA05); busca cronometrada com a equipe (CA03).
- Validação com a equipe da TI (W12).
