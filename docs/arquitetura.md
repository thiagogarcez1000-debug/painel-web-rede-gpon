# Arquitetura inicial do painel web

Planejamento da Sprint 01 (card W01). Os diagramas serão revisados ao longo das sprints.

## Visão geral (cliente-servidor)

```mermaid
flowchart LR
  subgraph Cliente
    PC["Navegador no computador"]
    CEL["Navegador no celular"]
  end
  VPN["Rede interna / VPN"]
  subgraph Servidor["Servidor da TI"]
    WEB["Flask: páginas + API JSON + login"]
    SCAN["Serviço de varredura (ping)"]
    DB[("SQLite")]
  end
  PC <-->|HTTPS| VPN
  CEL <-->|HTTPS| VPN
  VPN <--> WEB
  WEB <--> DB
  SCAN --> DB
  SCAN -->|ICMP| GPON["Rede GPON (~580 pontos)"]
  SCAN -->|alerta| MSG["API de mensagens"]
```

## Fluxo de navegação

```mermaid
flowchart LR
  L[Login] --> P["Painel (resumo + cards)"]
  P --> B[Busca e filtros] --> D[Detalhe do ponto]
  P --> D
  P --> I[Incidentes] --> D
  D --> M[Mapa e rota]
  D --> H[Histórico de quedas]
  D --> R["Reiniciar ONU (confirmação)"]
  P --> REL[Relatórios] --> X[Download Excel]
```

## Modelo de dados

```mermaid
erDiagram
  OLT ||--o{ PONTO : possui
  PONTO ||--o{ EVENTO_STATUS : registra
  EVENTO_STATUS ||--o{ ALERTA : gera
  USUARIO ||--o{ LOG_ACAO : executa
  PONTO ||--o{ LOG_ACAO : recebe
```

## MVP
Login (RF01), painel com cards e atualização automática (RF02), busca e filtros (RF03),
detalhe do ponto (RF04) e mapa com rota (RF05), acessíveis em computador e celular.
