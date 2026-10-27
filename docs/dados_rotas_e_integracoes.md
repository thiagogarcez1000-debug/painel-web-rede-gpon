# Dados das rotas da fibra e condições das integrações (27/10/2026)

Revisão feita a partir do feedback da Proposta (seções 6.6 e 6.7).

## Rotas da fibra (RF05)
**Origem:** arquivo KMZ do projeto as built da rede (PANA 01 a 04), que já contém OLTs, CTOs, pontos e o traçado dos cabos (backbone, distribuição e drop).

**Importação (script, sob demanda):**
1. Extrair o KML de dentro do KMZ.
2. Cada linha (LineString) vira um **trecho** de cabo: id, tipo (backbone/distribuição/drop), OLT, comprimento e coordenadas.
3. Cada marcador (Placemark) vira OLT, CTO ou ponto, com coordenadas.
4. O vínculo ONU → ponto do mapa usa a planilha de vínculo já existente (confiança alta/média/baixa) e, quando faltar, OLT + porta + CTO.

**Organização no banco (SQLite):**
| Tabela | Campos principais |
|---|---|
| TRECHO | id, tipo, olt_id, comprimento_m, geojson (coordenadas) |
| CTO | id, nome, olt_id, latitude, longitude |
| ROTA_PONTO | ponto_id, ordem, trecho_id |

A rota de um ponto é a sequência de trechos da OLT até a CTO do ponto, montada na importação (caminho pelos trechos que se tocam) e gravada em ROTA_PONTO.

**Recuperação:** a rota `/api/pontos/<id>/rota` devolve um GeoJSON com os trechos em ordem, desenhado no mapa (Leaflet). Pontos sem vínculo confiável mostram só a localização, com o aviso "rota não confirmada".

## Envio de mensagens (RF07) – escolha pendente
| Opção | Condições de acesso | Custo | Situação |
|---|---|---|---|
| WhatsApp Business (API oficial da Meta) | Conta empresarial verificada, número dedicado, modelos de mensagem aprovados | Cobrança por mensagem conforme a tabela da Meta | Depende de autorização e verba da Prefeitura |
| Bot do Telegram | Criar o bot e cadastrar o grupo da equipe | Gratuito | **Alternativa adotada se o WhatsApp não for autorizado** |
| E-mail institucional (SMTP) | Conta de envio da Prefeitura | Gratuito | Alternativa para a gerência |

## Serviços externos indisponíveis
- Mensagens: o alerta fica numa fila e é reenviado a cada 5 min; o painel continua mostrando o alerta e marca "aviso não entregue".
- Mapas (OpenStreetMap): sem as imagens do mapa, o detalhe mostra endereço, CTO e a lista de trechos; o resto do painel funciona normalmente.
- Nenhum dado da rede (IP, serial) é enviado nas mensagens; só o nome da unidade e o estado.
