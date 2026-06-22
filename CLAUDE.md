# FlatDrop — guia para o Claude Code

> Arquivo-raiz lido pelo Claude Code em toda sessão. Mantenha CURTO (custa token em todo turno).
> O comportamento detalhado do assistente está em `meta/CEREBRO.md`.

## Ritual de início
Leia `meta/CEREBRO.md` → `meta/CONTEXT.md` → `meta/STATUS.md` antes de agir. Confirme em uma frase o que entendeu.

## Build / validação
- Não há build (app Python puro). **Validação = testes:** `python -m pytest -q` (rode a partir da raiz do repo, antes de commitar mudança de código).
- Rodar o app: `python run.py` (sem args abre a GUI; com args roda a CLI).
- Mudança só de doc (`meta/`) NÃO precisa de testes; a rede é o `git diff`.

## Convenções
- Identificadores em inglês; comentários e docs em PT-BR. Docstring em toda função pública.
- Mensagens de commit **sem acento** (o ambiente do Code usa Git Bash; o CMD do usuário corrompe acento). Conventional Commits.
- Edições nos `meta/` são **append-only** pelo Code (linha no STATUS, `DEC-`/`FIX-` em DECISIONS, marcar estado de fase no ROADMAP). Curadoria que REESCREVE um doc vem do chat (arquivo inteiro OU spec em `meta/specs/`).
- Ao aplicar uma spec de `meta/specs/`: ache cada âncora EXATAMENTE; se não achar, PARE e reporte — não chute lugar próximo. Não mexa fora das edições nomeadas. `git diff` antes do commit.

## Mapa rápido
- `flatdrop/core.py` — lógica pura (varredura, nomeação, multi-fonte). Sem UI.
- `flatdrop/cli.py` — CLI. `flatdrop/gui.py` — GUI tkinter. `flatdrop/config.py` — defaults (allowlist, ignores).
- `tests/` — pytest. `bat/cinzeiro/` — .bat de exemplo do usuário. `meta/` — contexto. `meta/specs/` — specs do chat.
