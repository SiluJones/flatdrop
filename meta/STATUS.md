# STATUS — FlatDrop

Estado atual do projeto. Atualize ao fim de cada sessão de trabalho (rolante: o
resolvido sai daqui e vira `CHANGELOG`/`DECISIONS`).

> **Mudanças nesta revisão (2026-07-04, sessão da tarde):** a spec0011 (`_TREE.md`)
> foi **aplicada e commitada** pelo Code (commit `304440a`, 27→35 testes verdes); o
> `_TREE.md` foi verificado no mount e saiu correto (pastas ignoradas colapsadas em
> uma linha, renomeados marcados). Autoradas **duas specs novas, aguardando o Code**:
> `260704-spec0012-release-0.3.0.md` (corte da 0.3.0) e
> `260704-spec0013-fullpath-root.md` (incluir o nome da pasta-raiz no modo fullpath).
> Capturado no IDEAS o refinamento da nota 0714 (KCM ensina o Claude a ler o
> `_TREE.md` e gerar um `.flatdropignore` versionado).
>
> **Atualização (mesma revisão):** **spec0012 aplicada** — `__version__` bumpado
> para `0.3.0`, CHANGELOG fechado (`[0.3.0] — 2026-07-04`, `_TREE.md` incluído,
> nova `[Não lançado]` aberta). 35 testes seguem verdes. Resta a spec0013 na fila.

- **Versão:** 0.3.0 no `__init__.py`. **spec0012 aplicada** (bump + fechamento do
  CHANGELOG).
- **Data:** 2026-07-04
- **Fase:** F1 (MVP) OK · F2 (robustez/conveniência): item B (`_TREE.md`) OK agora;
  restam C/D e polimento de UI · F3 (gerador de `.bat` + multi-fonte na GUI) OK —
  ver `ROADMAP.md`.
- **Situação geral:** em uso real. Fluxo do monorepo `cinzeiro` coberto de ponta a
  ponta (GUI, CLI e `.bat`). Modo Claude Code em operação (specs 0001–0011 aplicadas
  e commitadas; 0012–0013 na fila do Code).

## O que funciona (além do MVP)

- **CLI** (`python run.py <opções>`): mesma core da GUI. Sem args abre a GUI.
- **GUI repaginada (UI-1):** modal "Escolher tipos…" (checklist categorizado +
  busca + marcar/limpar por grupo + adicionar custom) no lugar da caixa de
  extensões e dos campos só/exceto; tela compacta (só um resumo "Tipos: N de M");
  abre **maximizada**.
- **`_TREE.md` opcional na saída (spec0011):** árvore indentada da origem ao lado do
  `_MANIFEST.md` — copiados (renomeados marcados com o nome plano), pulados com o
  motivo, e **pastas ignoradas colapsadas em UMA linha, sem recursão**
  (`node_modules/ [ignorada: embutido]` nunca expande). Desligado por padrão
  (checkbox na GUI + `--tree` na CLI, serializado no `.bat`). Detalhe dos pulados
  soltos via `--tree-detail summary|full` (default `summary`).
- **Gerador de `.bat` na GUI:** botão "Gerar .bat…" serializa a config da tela num
  `.bat` ASCII (reproduz a seleção do modal via `--add-ext`/`--exclude-ext`); abre
  a janela de salvar na pasta-pai da raiz.
- **Multi-fonte ao vivo na GUI:** toggle "Também incluir todos os `.md` a partir de
  [raiz]" vale no Pré-visualizar/Executar (não só no `.bat`) — FIX-004.
- **`.flatdropignore` + `.gitignore` aninhado (DEC-014):** ignore próprio por
  projeto, aninhado, com negação `!` para liberar o que o `.gitignore` bloqueia
  (até pasta podada). O `.flatdropignore` tem a palavra final sobre o `.gitignore`.
- **Allowlist expandida (DEC-013):** documentos aceitos pelo Projeto
  (PDF/DOCX/XLSX/ODT/RTF/EPUB), Godot (`gd`/`uid`/`tscn`/`tres`/`gdshader`/`godot`/
  `import`) e várias linguagens/config. Imagens/áudio/vídeo seguem fora.
- **Multi-fonte com manifesto único** (`make_plan_sources`) + `--also-md-from`.
- **Filtros de execução:** `only_ext`/`exclude_ext`/`add_ext`, `only_folder`/`folder_match`.
- **5 `.bat` do cinzeiro** (ASCII) + **launcher `flatdrop-ui.bat`** (abre a UI sem console).
- **Downloads resolvido de verdade** (Known Folder no Windows; XDG no Linux) — FIX-002.
- Poda de pastas **visível** (contador + amostra + aviso) na GUI e na CLI — FIX-001.

## Qualidade / testes

- **35 testes pytest passando** (`python -m pytest -q` a partir da raiz):
  32 em `test_core.py` (MVP + FIX-001 + filtros/multi-fonte/Downloads + 3 do
  `.flatdropignore` + 8 do `_TREE.md`) + 3 em `test_cli.py`.
- A GUI **não** é coberta pela suíte (tkinter fora do CI) -> smoke manual no Windows.

## Em aberto (produto)

- **Aplicar a spec0013 (fullpath com pasta-raiz) — AUTORADA, AGUARDANDO O CODE.**
  Flag `root_in_name`: no modo fullpath e em fonte única, injeta o nome da
  pasta-raiz como a pasta mais externa do sufixo (arquivos da raiz passam a levar o
  nome do projeto). Injeção só no nome (via `root_prefix` em `_plan_names`); o `rel`
  do manifesto/tree continua real. Ignorada com aviso fora do fullpath e em
  multi-fonte. Limite do Windows protegido pelo truncamento com hash. CLI
  `--root-in-name`; checkbox na GUI serializada no `.bat`. +~6 testes (35->~41).
- **C — Persistir configurações + pastas recentes** na GUI (`settings.py` com JSON
  em `%APPDATA%`/`~/.config`; Combobox de raízes recentes).
- **D — Ignores de pasta editáveis na GUI** com núcleo imutável (`.git`/`node_modules`/…).
  (O `.flatdropignore` já cobre boa parte de forma declarativa.)
- **Multi-raiz na GUI** (selecionar N pastas, prefixar cada uma com sua raiz) —
  ideia da nota `.txt`; tarefa própria, mexe na UI de seleção.
- **UI-2** (polimento de layout) e **UI-3** (presets "só docs"/"só código", lembrar
  última seleção) — melhorias de UX em fila.
- **Doc:** documentar o `.flatdropignore` no `README.md` de usuário (CONTEXT já
  cobre). Considerar o trecho de **KCM** que ensina o Claude a ler o `_TREE.md` e
  ditar um `.flatdropignore` versionado (ideia da nota 0714).
- **Robustez (avaliar):** saída da CLI ASCII-safe (`->`/`*` em vez de `↳`/`•`) para
  dispensar `chcp` nos `.bat`; botão "Gerar atalho da UI" que crie o launcher sozinho.

## Riscos / pontos de atenção

- **Nenhum bug aberto.**
- O `_TREE.md` deste projeto mostrou `Pulados: 0` (não há `.flatdropignore` nem
  arquivos pulados por tipo aqui) — a diferença visual `summary`x`full` e as linhas
  `[pulado: …]` só aparecem "ao vivo" num projeto com `.env`/`.flatdropignore`.
  Está coberto por testes; é esperado.
- O fix do Downloads e a GUI só foram exercidos por estrutura/lógica aqui (sem
  Windows no ambiente do chat); a validação final é o smoke manual no PC.
- A estimativa de tokens segue grosseira (`bytes/4`) e não vale para binários
  (PDF/DOCX/XLSX) — não confie no número quando houver muitos binários.
- `.flatdropignore` faz uma passada extra na árvore para coletar os ignores
  (aceitável; fundível numa passada depois, se virar gargalo).
