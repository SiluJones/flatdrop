# STATUS — FlatDrop

Estado atual do projeto. Atualize ao fim de cada sessão de trabalho.

> **Mudanças nesta revisão (2026-06-14):** v0.1.0 → **0.2.0**. Saiu do STATUS o
> que virou release (foi para o CHANGELOG): a CLI, o multi-fonte, os filtros e as
> duas correções. Entrou o estado novo e o backlog re-priorizado. O teste em
> projeto real foi feito (funciona) — então deixou de ser pendência.

- **Versão:** 0.2.0
- **Data:** 2026-06-14
- **Fase:** F1 (MVP) concluída ✅ · F2 (robustez/conveniência) **em curso** — ver `ROADMAP.md`.
- **Situação geral:** em uso real. O fluxo do monorepo `cinzeiro` está coberto de
  ponta a ponta por linha de comando + `.bat`.

## O que já funciona (além do MVP)

- **CLI** (`python run.py <opções>`): mesma core da GUI. Sem argumentos abre a
  GUI; com argumentos roda no terminal e executa (com `--preview` para só simular).
- **Multi-fonte com manifesto único** (`make_plan_sources`): combina várias
  coletas (cada uma com raiz e filtros próprios) numa só pasta de saída, com um
  `_MANIFEST.md` único, caminhos relativos à raiz comum e dedup por caminho real.
- **Filtros desta execução:** `--only-ext` (restringe a certas extensões),
  `--exclude-ext` (subtrai), `--add-ext` (acrescenta à allowlist), `--only-folder`
  + `--folder-match` (starts/contains/exact).
- **`--also-md-from <raiz>`:** atalho que monta o padrão "todos os `.md` do repo +
  conteúdo de uma área" numa saída só (o caso `cinzeiro`).
- **5 `.bat` do cinzeiro** em `bat/cinzeiro/`: um só-`.md` do grupo e um por área
  (Story/Art/Game/OST), prontos para duplo-clique.
- **Downloads resolvido de verdade** (Known Folder no Windows via ctypes; XDG no
  Linux) — corrige a saída que caía na raiz do perfil quando a pasta fora movida.
- A poda de pastas pelo `.gitignore`/ignores agora é **visível** (contador +
  amostra + aviso), tanto na GUI quanto na CLI (FIX-001).

## Qualidade / testes

- **26 testes pytest passando** (`python -m pytest -q` a partir da raiz):
  13 do MVP + 2 do FIX-001 + 6 dos filtros/multi-fonte/Downloads + 3 da CLI
  (`tests/test_cli.py`).
- Validação manual da CLI com um `cinzeiro` simulado: pacote de área traz os
  não-`.md` da área + todos os `.md` do grupo num só manifesto; binário (`.png`)
  fica fora; `--add-ext gd` traz os scripts de engine.

## Pendências imediatas (próxima sessão) — restante da Fase 2

- **B — `_TREE.md` opcional:** árvore da origem na saída, marcando o que foi
  pulado e as pastas podadas (casa com o FIX-001). Era do plano da 0.2.0; ficou
  parqueado para a próxima leva.
- **C — Pastas recentes + persistência:** `settings.py` com JSON em
  `%APPDATA%`/`~/.config`; Combobox de raízes recentes na GUI.
- **D — Ignores de pasta editáveis** com núcleo imutável
  (`.git`/`node_modules`/`__pycache__`/VCS) na GUI.
- **Confirmar no Windows:** (a) a GUI abre e opera com tkinter nativo (aqui no
  Linux o tkinter não existe, só a core/CLI foram exercidas); (b) o fix do
  Downloads resolve no(s) PC(s) onde a pasta estava caindo na home; (c) os 5
  `.bat` rodam (ajustar `--add-ext` quando houver arquivos de dev de fato).

### Modo Claude Code + features em curso
- **Modo Claude Code** (DEC-012): chat autora docs/specs, Code implementa. Arranque em `CLAUDE.md` raiz + `.claude/`.
- **Aplicado (v0.2.x, não lançado):** tipos de arquivo (DEC-013); GUI com filtros, gerador de `.bat`,
  multi-fonte ao vivo, modal de seleção de tipos e tela compacta (UI-1), abrir maximizada; launcher
  `flatdrop-ui.bat`. Bugs resolvidos: FIX-003 (`.bat` ASCII), FIX-004 (multi-fonte ao vivo).
- **Autorado, pendente de aplicar:** `.flatdropignore` + `.gitignore` aninhado (spec-0008, com 3 testes — DEC-014).
- **Próximas:** `_TREE.md` (pastas ignoradas em uma linha, sem recursão); UI-2 (polimento de layout) e
  UI-3 (presets/lembrar seleção); documentar `.flatdropignore` no README/CONTEXT; avaliar saída ASCII da
  CLI e um botão "Gerar atalho da UI" que crie o launcher sozinho.

## Riscos / pontos de atenção

- Nenhum bug aberto.
- **`--add-ext` nos `.bat` de área é um palpite (Godot).** Hoje, sem arquivos de
  desenvolvimento no cinzeiro, não muda nada; quando você adicionar o conteúdo
  desenvolvido, ajuste a lista para os formatos reais do seu engine.
- Multi-fonte só existe na **CLI/`.bat`** (decisão CLI-first). A GUI segue
  fonte-única; expor multi-fonte na GUI virá com o exportador de `.bat` (futuro).
- O fix do Downloads no Windows usa ctypes e **só foi testável na estrutura**
  aqui (sem Windows no ambiente); confirmar no PC afetado.
- A estimativa de tokens segue grosseira (`bytes/4`).
