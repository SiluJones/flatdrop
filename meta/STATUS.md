# STATUS — FlatDrop

Estado atual do projeto. Atualize ao fim de cada sessão de trabalho (rolante: o
resolvido sai daqui e vira `CHANGELOG`/`DECISIONS`).

> **Mudanças nesta revisão (2026-07-05):** **spec0014 aplicada e commitada**
> (`5acf16f`, nota 0952) — a ordem do `root_in_name` agora é a correta (stem +
> caminho invertido + raiz no fim, `page__routes__app__meuapp.tsx`); asserção extra
> trava "raiz é o último token"; 41 testes verdes. **spec0015 aplicada** — bump
> `0.3.0→0.3.1` e CHANGELOG com a seção `[0.3.1]` (root_in_name + fix de ordem);
> resolve o descompasso de versão.

> **Bug de infra de teste (FIX-005) — RESOLVIDO (spec0016 aplicada, `84be20e`):**
> `pytest` puro na raiz falhava na coleta com `ModuleNotFoundError: No module named
> 'flatdrop'` (só `python -m pytest` funcionava). Causa: nada punha a raiz do repo
> no `sys.path` na coleta e não havia `conftest.py`. Correção: `conftest.py` de 3
> linhas na raiz (espelha o `run.py`). Confirmado: `pytest -q` e
> `python -m pytest -q` verdes (41 testes), da raiz e de dentro de `tests/`. Sem
> mudança em `flatdrop/` nem `tests/`. Não era regressão da 0.3.1.

> **Descompasso de versão — RESOLVIDO (spec0015):** a 0.3.0 foi cortada (spec0012)
> ANTES da spec0013 entrar, então o `root_in_name` ficou no código sem constar no
> `### Adicionado` da `[0.3.0]`. A **spec0015 (aplicada)** cortou a **0.3.1**: bump
> `0.3.0→0.3.1`, nova seção `[0.3.1]` com o `root_in_name` (Adicionado) e o fix de
> ordem (Corrigido), sem reescrever a `[0.3.0]`.

- **Versão:** 0.3.1 no `__init__.py`. **spec0015 (corte da 0.3.1) aplicada** —
  CHANGELOG registra root_in_name (spec0013) + fix de ordem (spec0014).
- **Data:** 2026-07-05
- **Fase:** F1 (MVP) OK · F2 (robustez/conveniência): item B (`_TREE.md`) OK;
  restam C/D e polimento de UI · F3 (gerador de `.bat` + multi-fonte na GUI) OK —
  ver `ROADMAP.md`.
- **Situação geral:** em uso real. Fluxo do monorepo `cinzeiro` coberto de ponta a
  ponta (GUI, CLI e `.bat`). Modo Claude Code em operação (specs 0001–0016 aplicadas
  e commitadas — spec0016 é só `conftest.py` de teste, `84be20e`).

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
- **Fullpath com nome da pasta-raiz (spec0013, ajuste na 0014):** flag `root_in_name`
  — no modo fullpath e em fonte única, inclui o nome do projeto no nome de cada
  arquivo (inclusive os da raiz). Só no NOME planejado; o `rel` do manifesto/tree
  fica real. Ignorada com aviso fora do fullpath e em multi-fonte. CLI
  `--root-in-name`; checkbox na GUI serializada no `.bat`. **Formato final (spec0014):
  stem + caminho da mais interna à mais externa + raiz no fim**
  (`app/routes/page.tsx` sob `meuapp` → `page__routes__app__meuapp.tsx`).
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

- **41 testes pytest passando**, tanto `pytest -q` (puro) quanto `python -m pytest -q`,
  a partir da raiz (spec0016 — `conftest.py` — corrigiu o puro; FIX-005): test_core.py
  (MVP + FIX-001 + filtros/multi-fonte/Downloads + `.flatdropignore` + `_TREE.md` +
  `root_in_name`) + 3 em test_cli.py. A spec0014 (aplicada) ajustou as asserções de
  ordem do `root_in_name`, mantendo o total.
- A GUI **não** é coberta pela suíte (tkinter fora do CI) -> smoke manual no Windows.

## Em aberto (produto)

- **C — Persistir configurações + pastas recentes** na GUI (`settings.py` com JSON
  em `%APPDATA%`/`~/.config`; Combobox de raízes recentes).
- **D — Ignores de pasta editáveis na GUI** com núcleo imutável (`.git`/`node_modules`/…).
  (O `.flatdropignore` já cobre boa parte de forma declarativa.)
- **Multi-raiz na GUI** (selecionar N pastas, prefixar cada uma com sua raiz) —
  ideia da nota `.txt`; tarefa própria, mexe na UI de seleção.
- **Formato "caminho escrito"** (`raiz__pastas__stem.ext`) como seletor de formato do
  nome — ideia futura no IDEAS; útil para empilhar por raiz, não para o Claude achar
  por nome.
- **UI-2** (polimento de layout) e **UI-3** (presets "só docs"/"só código", lembrar
  última seleção) — melhorias de UX em fila.
- **Doc:** documentar o `.flatdropignore` no `README.md` de usuário. Considerar o
  trecho de **KCM** que ensina o Claude a ler o `_TREE.md` e ditar um
  `.flatdropignore` versionado (ideia da nota 0714).
- **Robustez (avaliar):** saída da CLI ASCII-safe (`->`/`*` em vez de `↳`/`•`);
  botão "Gerar atalho da UI" que crie o launcher sozinho.

## Riscos / pontos de atenção

- **Nenhum bug aberto.** (FIX-005 resolvido pela spec0016 — `conftest.py` na raiz.
  O comportamento de ordem do root_in_name não era bug — foi ajuste de formato
  pedido, endereçado pela spec0014.)
- O `_TREE.md` deste projeto mostra `Pulados: 0` (sem `.flatdropignore` nem arquivos
  pulados por tipo aqui) — a diferença `summary`x`full` e as linhas `[pulado: …]` só
  aparecem "ao vivo" num projeto com `.env`/`.flatdropignore`. Coberto por testes.
- O fix do Downloads e a GUI só foram exercidos por estrutura/lógica aqui (sem
  Windows no ambiente do chat); a validação final é o smoke manual no PC.
- A estimativa de tokens segue grosseira (`bytes/4`) e não vale para binários.
- `.flatdropignore` faz uma passada extra na árvore para coletar os ignores
  (aceitável; fundível numa passada depois, se virar gargalo).
