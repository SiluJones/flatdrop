# STATUS — FlatDrop

Estado atual do projeto. Atualize ao fim de cada sessão de trabalho (rolante: o
resolvido sai daqui e vira `CHANGELOG`/`DECISIONS`).

> **Mudanças nesta revisão (2026-07-05):** ciclo de release fechado e limpo. Todas
> as specs até a **0016 estão aplicadas e commitadas**; `pytest` puro passou a
> funcionar (FIX-005). Versão **0.3.1**, **41 testes verdes**. O descompasso de
> versão foi resolvido. Sessão de transferência de conversa: os meta/ foram
> regenerados completos. **Próxima conversa começa por: (1) trecho de KCM que ensina
> o Claude a ler o `_TREE.md` e ditar um `.flatdropignore`; (2) editor de
> `.flatdropignore` na GUI (= Fase 2-D).** O item C fica para depois dessas duas.

- **Versão:** 0.3.1 no `__init__.py`. `[Não lançado]` no CHANGELOG só tem o FIX-005
  (conftest) a registrar num próximo corte de patch, se/quando houver mais itens.
- **Data:** 2026-07-05
- **Fase:** F1 (MVP) OK · F2 (robustez/conveniência): quase toda feita — em aberto C
  (persistência), D (editor de ignores = editor de `.flatdropignore`), multi-raiz na
  GUI, UI-2/UI-3 · F3 (gerador de `.bat` + multi-fonte na GUI) OK · F4 (distribuição
  + single-file) não iniciada — ver `ROADMAP.md`.
- **Situação geral:** em uso real e estável. Fluxo do monorepo `cinzeiro` coberto de
  ponta a ponta (GUI, CLI e `.bat`). Modo Claude Code em operação; specs 0001–0016
  aplicadas e commitadas.

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
  final sobre o `.gitignore`. **Hoje é criado à mão; a ferramenta só o LÊ** (o
  editor visual é a Fase 2-D, próxima tarefa).
- **Allowlist expandida (DEC-013):** documentos aceitos pelo Projeto, Godot e várias
  linguagens/config. Imagens/áudio/vídeo fora.
- **Multi-fonte com manifesto único** (`make_plan_sources`) + `--also-md-from`.
- **Filtros de execução:** `only_ext`/`exclude_ext`/`add_ext`, `only_folder`/`folder_match`.
- **5 `.bat` do cinzeiro** (ASCII) + **launcher `flatdrop-ui.bat`**.
- **Downloads resolvido de verdade** (Known Folder / XDG) — FIX-002.
- Poda de pastas **visível** (contador + amostra + aviso) na GUI e CLI — FIX-001.

## Qualidade / testes

- **41 testes pytest passando.** Rodar da raiz: **`pytest -q`** (o `conftest.py` na
  raiz resolve o import — FIX-005) ou `python -m pytest -q`.
- test_core.py (MVP + FIX-001 + filtros/multi-fonte/Downloads + `.flatdropignore` +
  `_TREE.md` + `root_in_name`) + 3 em test_cli.py.
- A GUI **não** é coberta pela suíte (tkinter fora do CI) → smoke manual no Windows.

## Em aberto (produto) — backlog curto, na ordem sugerida

1. **Trecho de KCM: "Claude lê o `_TREE.md` → dita o `.flatdropignore`".** Conteúdo
   portável (não é código do FlatDrop): ensina o Claude de qualquer Projeto que usa
   FlatDrop a ler o `_TREE.md` (que mostra o motivo de cada exclusão) e devolver um
   `.flatdropignore` pronto — sobretudo para **liberar via `!` o que o `.gitignore`
   esconde**. Entregável: um bloco de KCM + exemplo no README. Rápido; destrava o
   fluxo que o `_TREE.md` já habilita. **PRIMEIRA tarefa da próxima conversa.**
2. **Editor de `.flatdropignore` na GUI (= Fase 2-D).** Interface para gerar o
   `.flatdropignore` sem decorar sintaxe: árvore navegável das pastas/arquivos da
   raiz, com checkbox por item, sinalizando o que o `.gitignore` já ignora, e
   manipulável (incluir/excluir/liberar). Grava o `.flatdropignore` na raiz.
   **Feature de UI não-trivial** — provavelmente pede uma spec de investigação/design
   (estado tri-state, leitura do que o git já pega, geração dos padrões) antes da spec
   de implementação. **SEGUNDA tarefa; o usuário reconhece que exige pesquisa/estudo.**
3. **C — Persistir configurações + pastas recentes** na GUI (`settings.py`, JSON em
   `%APPDATA%`/`~/.config`; Combobox de recentes). **Depois das duas acima.**
4. **Multi-raiz na GUI** (selecionar N pastas, prefixar cada uma com sua raiz).
5. **UI-2** (polimento de layout) e **UI-3** (presets "só docs"/"só código", lembrar
   última seleção).
6. **Formato "caminho escrito"** (`raiz__pastas__stem.ext`) como seletor de formato
   do nome — útil para empilhar por raiz, não para o Claude achar por nome. Espera.
7. Aviso mais visível quando o pathspec está ausente (destaque na GUI).
8. Saída da CLI ASCII-safe (`->`/`*`); botão "Gerar atalho da UI".

## Riscos / pontos de atenção

- **Nenhum bug aberto.** (FIX-005 resolvido pelo `conftest.py`.)
- O `_TREE.md` deste projeto mostra `Pulados: 0` (sem `.flatdropignore` nem arquivos
  pulados por tipo aqui) — a diferença `summary`×`full` e as linhas `[pulado: …]` só
  aparecem "ao vivo" num projeto com `.env`/`.flatdropignore`. Coberto por testes.
- O fix do Downloads e a GUI só foram exercidos por estrutura/lógica no sandbox (sem
  Windows no ambiente do chat); a validação final é o smoke manual no PC.
- A estimativa de tokens segue grosseira (`bytes/4`) e não vale para binários.
- `.flatdropignore` faz uma passada extra na árvore para coletar os ignores
  (aceitável; fundível numa passada depois, se virar gargalo).
