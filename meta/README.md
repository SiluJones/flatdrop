# Templates — Desenvolvimento

Nicho: Desenvolvimento
Gerado por: Kit de Contexto Universal
Data: 2026-06-13

Arquivos:
- **SPEC.md** — OPCIONAL — modelo de spec de **feature** (Spec-Driven Development): problema, criterios de aceite verificaveis, decisoes, fora de escopo. Copiado para `meta/specs/AAMMDD-nome.md` so quando uma feature justifica. NAO e o modelo das WOs (ver DEC-023).
- **CONTEXT.md** — O que o projeto é: visão, stack, estrutura, como as peças críticas funcionam, armadilhas, produto. Estável.
- **STATUS.md** — O agora: o que funciona, o que está em progresso, o que está quebrado, backlog curto. Rolante — o resolvido sai.
- **DECISIONS.md** — Por que as coisas são como são: decisões de arquitetura (DEC) e bugs graves resolvidos (FIX). Cresce devagar.
- **CHANGELOG.md** — Histórico de versões entregues (SemVer + Keep a Changelog). Cresce no topo.
- **IDEAS.md** — Segundo cérebro: ideias suas e do assistente. Nunca perde nada — ideia muda de status, não some.
- **LOG-TEMPLATE.md** — Modelo do log de sessão. Referência fixa — nunca substituído pelo conteúdo preenchido.
- **ROADMAP.md** — OPCIONAL — plano deliberado de evolução em fases. Use quando o projeto tem direção de médio/longo prazo.
- **GLOSSARY.md** — OPCIONAL — termos próprios do projeto. Use quando há jargão que se repete entre sessões.
- **HISTORY.md** — OPCIONAL — conhecimento consolidado de fases antigas (guias, análises que não cabem no CONTEXT enxuto). Lido sob demanda.

Pastas irmas (nao sao templates do kit):
- **workorders/** — WOs: o delta que o Claude Code aplica (texto exato + ancora). Inclui as antigas `spec0001`-`spec0037`, que mantiveram o nome. Proxima: `wo0038`.
- **specs/** — specs de feature (nasce no primeiro uso).
- **../logs/** — log de sessao, um por dia, lido sob demanda.
