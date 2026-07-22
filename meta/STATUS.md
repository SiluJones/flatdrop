# STATUS — FlatDrop

Estado atual do projeto. Atualize ao fim de cada sessão de trabalho (rolante: o
resolvido sai daqui e vira `CHANGELOG`/`DECISIONS`).

> **Mudanças nesta revisão (2026-07-20):** **DEC-022** (spec0036, 0.11.0) — checkbox
> default-ON que nomeia `_MANIFEST`/`_TREE` com o nome da pasta no fim
> (`_MANIFEST_<pasta>.md`), desambiguando no Projeto do Claude e mantendo o prefixo p/ busca.
> Flag aditivo `--no-name-meta` na CLI e em `_build_cli_args` (DEC-020, **autorizado**);
> `_generate_bat`/`_sources` intocados. **Desvio registrado:** a spec não ligava o campo ao
> `_gather_cfg` (execução ao vivo); acrescentei a linha p/ manter a paridade GUI×`.bat`
> (FIX-004). `is_our_folder` reconhece o sufixo. Antes, nesta leva: FIX-010 (0.10.1), layout
> em duas colunas (0.10.0), atalho da UI (0.9.0), Recentes compacto (0.9.1), FIX-009 (0.9.2).
> Versão **0.11.0**, **68 testes verdes**. **O projeto entra de novo em PAUSA a partir de
> 2026-07-21** — uso real, estável, sem bug aberto. **Ao retomar:** ler este STATUS, o
> `CHANGELOG` e as Ativas do `IDEAS.md`. **Frente candidata maior:** multi-raiz (decisão A/B
> pendente, ver abaixo). **Antes de tudo:** conferir o backup do repo (ver Riscos).

- **Versão:** 0.11.0 no `__init__.py` (spec0036/DEC-022: nomear `_MANIFEST`/`_TREE` com o
  nome da pasta). `[Não lançado]` no CHANGELOG só tem itens de produto em aberto.
- **Data:** 2026-07-21
- **Fase:** F1 (MVP) OK · F2 (robustez/conveniência) OK — **C (persistência) e D (editor
  de `.flatdropignore`) fechados**; em aberto só **multi-raiz na GUI** e **UI-2/UI-3**
  (polimento, opcionais) · F3 (gerador de `.bat` + multi-fonte na GUI) OK · F4
  (distribuição: `.exe`, single-file, contagem de tokens) não iniciada — ver `ROADMAP.md`.
- **Situação geral:** em uso real, **estável**, em **pausa** (2026-07-21). Fluxo do monorepo
  `cinzeiro` coberto de ponta a ponta (GUI, CLI e `.bat`). Modo Claude Code em operação;
  **specs 0001–0037 aplicadas e commitadas**. **68 testes verdes**; nenhum bug aberto. Esta
  leva (0.8.0–0.11.0): atalho "abrir GUI" semeia navegação (0.8.0), gerar atalho da UI +
  Recentes compacto + layout em duas colunas (0.9.0–0.10.0), FIX-010 persistência de
  preferências + padrões de fábrica (0.10.1), e nomeação dos meta com o nome da pasta
  (0.11.0).
- **Decisão pendente (bloqueia a próxima frente):** **multi-raiz na GUI** não tem versão
  "só-GUI, zero-toque" — a core já aceita N fontes, mas a CLI só tem `--root` + N
  `--also-md-from` (fontes só-`.md`). Ou (**B**) a GUI roda N raízes e o botão "Gerar
  .bat…" fica **desabilitado** no modo multi-raiz (o `.bat` nunca mente; caminho protegido
  intocado), ou (**A**) cria-se um flag aditivo `--add-root` e o `.bat` passa a codificar N
  raízes — o que **toca o caminho protegido** e, por DEC-020, exige aval consciente do
  autor + prova de que todo `.bat` de raiz única segue idêntico. **Recomendação: B.**
  Nada foi desenhado; a spec de design só começa depois dessa escolha.
- **(2026-07-15, spec0021 aplicada) Editor de `.flatdropignore` (Fase 2-D) fechado:**
  glifo da pasta correto já na visão colapsada (`core.folder_effective_state`, FIX-007).
- **(2026-07-15, spec0024 aplicada) Item C — persistência entregue:** `flatdrop/settings.py`
  grava config + recentes (só-GUI; DEC-020 blinda o `.bat`). Versão **0.6.0**,
  **58 testes verdes**. Próxima = multi-raiz na GUI.
- **(2026-07-16, spec0027 aplicada) Force-include por caminho exato entregue (DEC-021):**
  `++caminho` no `.flatdropignore` resgata arquivo barrado por ignore embutido (vence tudo
  menos sensível); `.bat` intocado. Versão **0.7.0**, **62 testes**.
- **(2026-07-16, spec0028 aplicada) FIX-008:** o nome volta a renomear ao trocar de raiz
  (regressão da persistência corrigida). Versão **0.7.1**. Próxima = multi-raiz na GUI.
- **(2026-07-20, specs 0031–0033 aplicadas) Leva de conveniências de GUI, 0.9.0 → 0.9.2,
  66 testes verdes.** spec0031: menu **Ferramentas → "Gerar atalho da UI…"** gera o `.bat`
  que abre a interface (gerador NOVO e separado; RUN `.bat` intocado, DEC-020) — 1 teste
  novo (65 → 66). spec0032: **Recentes** compacto como botão **"Recentes ▾"** na linha da
  Raiz. spec0033/**FIX-009**: sub-frame na linha da Raiz tira a coluna global morta que o
  botão criava (grade de volta a 3 colunas). Pendências de smoke manual no Windows e dois
  prints candidatos a README (menu Ferramentas; linha da Raiz corrigida). Próxima = multi-
  raiz na GUI (decisão A/B do autor antes de desenhar).

## O que funciona (além do MVP)

- **CLI** (`python run.py <opções>`): mesma core da GUI. Sem args abre a GUI.
- **GUI repaginada (UI-1):** modal "Escolher tipos…" (checklist categorizado +
  busca + marcar/limpar por grupo + adicionar custom); tela compacta (resumo
  "Tipos: N de M"); abre **maximizada**.
- **`_TREE.md` opcional na saída (spec0011):** árvore da origem ao lado do
  `_MANIFEST.md` — copiados (renomeados marcados), pulados com o motivo, e pastas
  ignoradas colapsadas em UMA linha, sem recursão. Desligado por padrão (checkbox
  GUI + `--tree` CLI, serializado no `.bat`). Detalhe dos pulados via
  `--tree-detail summary|full`. É o par visual do `.flatdropignore`.
- **`root_in_name` (spec0013 + spec0014):** flag opcional — no modo fullpath e em
  fonte única, inclui o nome do projeto no nome de cada arquivo. Formato final:
  stem + caminho invertido + raiz no fim (`app/routes/page.tsx` sob `meuapp` →
  `page__routes__app__meuapp.tsx`; `README.md` → `README__meuapp.md`). Só no nome
  planejado; `rel` do manifesto/tree fica real. CLI `--root-in-name`; checkbox na
  GUI serializada no `.bat`.
- **Gerador de `.bat` na GUI:** "Gerar .bat…" serializa a config da tela num `.bat`
  ASCII (reproduz a seleção do modal via `--add-ext`/`--exclude-ext`).
- **Multi-fonte ao vivo na GUI:** toggle "Também incluir todos os `.md` a partir de
  [raiz]" vale no Pré-visualizar/Executar (FIX-004).
- **`.flatdropignore` + `.gitignore` aninhado (DEC-014):** ignore próprio por
  projeto, aninhado, com `!` para liberar o que o `.gitignore` bloqueia. Palavra
  final sobre o `.gitignore`. **Criável à mão ou pelo editor visual da GUI** (Fase 2-D,
  entregue na 0.4.0 — spec0018; gerador corrigido na 0.5.1 — spec0020, FIX-006).
  Aceita nomes alternativos (`.flatdropignore.txt`, `flatdropignore.txt`) e vai ao
  mount como o `.gitignore` (spec0019, DEC-018).
- **Allowlist expandida (DEC-013):** documentos aceitos pelo Projeto, Godot e várias
  linguagens/config. Imagens/áudio/vídeo fora.
- **Multi-fonte com manifesto único** (`make_plan_sources`) + `--also-md-from`.
- **Filtros de execução:** `only_ext`/`exclude_ext`/`add_ext`, `only_folder`/`folder_match`.
- **5 `.bat` do cinzeiro** (ASCII) + **launcher `flatdrop-ui.bat`**.
- **Downloads resolvido de verdade** (Known Folder / XDG) — FIX-002.
- Poda de pastas **visível** (contador + amostra + aviso) na GUI e CLI — FIX-001.

## Qualidade / testes

- **48 testes pytest passando.** Rodar da raiz: **`pytest -q`** (o `conftest.py` na
  raiz resolve o import — FIX-005) ou `python -m pytest -q`.
- test_core.py (MVP + FIX-001 + filtros/multi-fonte/Downloads + `.flatdropignore` +
  `_TREE.md` + `root_in_name` + editor/spec0018 + aliases/spec0019 + gerador
  corrigido/spec0020) + 3 em test_cli.py.
- A GUI **não** é coberta pela suíte (tkinter fora do CI) → smoke manual no Windows.

## Em aberto (produto) — backlog curto, na ordem sugerida

1. **Trecho de KCM: "Claude lê o `_TREE.md` → dita o `.flatdropignore`".** Conteúdo
   portável (não é código do FlatDrop): ensina o Claude de qualquer Projeto que usa
   FlatDrop a ler o `_TREE.md` (que mostra o motivo de cada exclusão) e devolver um
   `.flatdropignore` pronto — sobretudo para **liberar via `!` o que o `.gitignore`
   esconde**. Entregável: um bloco de KCM + exemplo no README. Rápido; destrava o
   fluxo que o `_TREE.md` já habilita. **PRIMEIRA tarefa da próxima conversa.**
2. ~~**Editor de `.flatdropignore` na GUI (= Fase 2-D).**~~ **ENTREGUE (0.4.0,
   spec0018; nomes alternativos + vai ao mount na 0.5.0, spec0019; gerador corrigido —
   colapso de pasta cheia, base git-pura no round-trip, checkbox indeterminado ao
   expandir — na 0.5.1, spec0020, FIX-006).** Modal `FlatDropIgnoreEditor` (árvore lazy,
   checkbox binário Opção B, tri-state por pasta, sinaliza o que o `.gitignore` esconde)
   + `annotate_children` / `build_flatdropignore` no core. Bloco gerenciado no
   round-trip. 3 testes (spec0018) + 2 (spec0019) + 2 (spec0020) novos. Falta só o
   smoke manual da GUI no Windows (a suíte não cobre tkinter).
3. **C — Persistir configurações + pastas recentes** na GUI (`settings.py`, JSON em
   `%APPDATA%`/`~/.config`; Combobox de recentes). **PRÓXIMA tarefa.**
4. **Multi-raiz na GUI** (selecionar N pastas, prefixar cada uma com sua raiz).
5. **UI-2** (polimento de layout) e **UI-3** (presets "só docs"/"só código", lembrar
   última seleção).
6. **Formato "caminho escrito"** (`raiz__pastas__stem.ext`) como seletor de formato
   do nome — útil para empilhar por raiz, não para o Claude achar por nome. Espera.
7. Aviso mais visível quando o pathspec está ausente (destaque na GUI).
8. Saída da CLI ASCII-safe (`->`/`*`); botão "Gerar atalho da UI".

## Riscos / pontos de atenção

- **Nenhum bug aberto.** (FIX-005 resolvido pelo `conftest.py`; FIX-008 corrigido na
  spec0028 — falta só o smoke manual de confirmação no Windows.)
- **Backup do repositório (atenção numa pausa longa).** Os commits recentes foram feitos
  na `main` **sem `git push`** e o repo não parecia ter remoto configurado. O repositório é
  a memória do projeto (specs, DECISIONS, CHANGELOG, logs) — se ficar só no disco local
  durante meses, uma falha de máquina apaga tudo. **Configurar um remoto (mesmo privado) e
  enviar antes de pausar.**
- O `_TREE.md` deste projeto mostra `Pulados: 0` (sem `.flatdropignore` nem arquivos
  pulados por tipo aqui) — a diferença `summary`×`full` e as linhas `[pulado: …]` só
  aparecem "ao vivo" num projeto com `.env`/`.flatdropignore`. Coberto por testes.
- O fix do Downloads e a GUI só foram exercidos por estrutura/lógica no sandbox (sem
  Windows no ambiente do chat); a validação final é o smoke manual no PC.
- A estimativa de tokens segue grosseira (`bytes/4`) e não vale para binários.
- `.flatdropignore` faz uma passada extra na árvore para coletar os ignores
  (aceitável; fundível numa passada depois, se virar gargalo).
