# CONTEXT — FlatDrop

Documento de contexto principal. Leia este primeiro ao abrir uma nova conversa.
Para o estado atual, veja `STATUS.md`; para o porquê das escolhas, `DECISIONS.md`.

> **Mudanças nesta revisão (2026-06-24):** atualizado para o pós-0.2.0 (candidato a
> 0.3.0, ainda não versionado no `__init__.py`). Entram: expansão da allowlist de
> tipos (Godot, PDF/DOCX/XLSX/ODT/RTF/EPUB, +linguagens), a GUI repaginada (modal de
> seleção de tipos + tela compacta + abre maximizada), o **gerador de `.bat`** pela
> interface, o **multi-fonte ao vivo na GUI**, o **`.flatdropignore` + `.gitignore`
> aninhado**, e o launcher `flatdrop-ui.bat`. Correções FIX-003 (`.bat` ASCII) e
> FIX-004 (multi-fonte ao vivo). Adotado o modo Claude Code (duas raias) e integrada
> a atualização do KCM. Suíte agora com **27 testes**. O essencial do MVP permanece.

## O que é

FlatDrop é uma ferramenta de desktop (Windows em primeiro lugar) que **copia os
arquivos de uma pasta de projeto para uma única pasta plana** — por padrão no
`Downloads` —, achatando toda a árvore de subpastas em um nível só e renomeando
arquivos que colidiriam de nome, para que possam conviver soltos na mesma pasta.

O objetivo é prático: alimentar os **arquivos de um Projeto do Claude**. A
interface de upload aceita arquivos individuais, não pastas; então o fluxo manual
seria arrastar pasta por pasta e renomear duplicados (`page.tsx`, `__init__.py`,
`index.ts`…) à mão. O FlatDrop elimina isso: você roda (pela GUI ou por um `.bat`),
ele organiza tudo numa pasta, e você arrasta uma vez só.

## Para quem é (e o que NÃO é)

- **Alvo:** o próprio autor do projeto, atualizando o conhecimento de um Projeto
  do Claude a partir de uma pasta local.
- **NÃO é um "repo-packer"/concatenador** (estilo Repomix/OneFile). O FlatDrop
  mantém arquivos **individuais** de propósito — o Claude indexa cada um e a
  atualização é granular. (Concatenar num só arquivo é ideia futura — Fase 4.)
- **NÃO faz upload sozinho.** Não há API pública de upload para os arquivos de
  Projeto; arrastar continua manual (e é só uma etapa).
- **NÃO mexe na pasta de origem.** Apenas lê e copia.

## Stack

- **Python 3.11+** — tipagem moderna, `dataclasses`, `pathlib`.
- **tkinter** para a GUI — embutido no Python oficial de Windows/macOS (DEC-008).
- **CLI** (`argparse`, stdlib) para uso por terminal e `.bat` (DEC-011).
- **pathspec** — única dependência e **opcional**: interpreta o `.gitignore` (e o
  `.flatdropignore`) corretamente. Sem ela, modo degradado com só os ignores
  embutidos (DEC-004).
- **pytest** — só para a suíte de testes.

## Estrutura do repositório

```
flatdrop/                       # raiz do repo (é também a raiz do Git)
├── run.py                      # entrypoint: sem args -> GUI; com args -> CLI
├── CLAUDE.md                   # guia CURTO do Claude Code (ritual, build, convenções)
├── .claude/                    # settings.json (permissões) + commands/ (/apply-spec, /wrap)
├── requirements.txt            # pathspec (opcional)
├── README.md
├── flatdrop/                   # o pacote
│   ├── __init__.py             # __version__ = "0.2.0" (bump p/ 0.3.0 ao cortar release)
│   ├── config.py               # defaults: extensões (allowlist), ignores, sensíveis, separador
│   ├── core.py                 # LÓGICA PURA, sem UI — onde mora tudo que importa
│   ├── cli.py                  # interface de linha de comando (amarra a core)
│   └── gui.py                  # interface tkinter (amarra a core) — com o modal de tipos
├── bat/
│   ├── flatdrop-ui.bat         # launcher: abre a UI sem console (pythonw), copiavel
│   └── cinzeiro/               # 5 .bat prontos do monorepo do usuário (ASCII)
├── tests/                      # test_core.py (24) + test_cli.py (3) = 27 testes
├── logs/                       # logs de sessão (AAAA-MM-DD.md)
└── meta/                       # os .md de contexto (CONTEXT, STATUS, etc.)
    └── specs/                  # specs do chat p/ o Code aplicar (ver "modo Claude Code")
```

Atenção à transferência: no Projeto do Claude os docs de contexto ficam em
`meta/`, mas o mount (`/mnt/project/`) chega **achatado** (sem subpastas). O
`_MANIFEST.md` do repo é a fonte de verdade dos nomes/estrutura quando há colisão.

A separação **core × (gui, cli)** é proposital (DEC-009): toda a lógica fica em
`core.py`, sem importar tkinter; GUI e CLI só coletam opções e chamam a core. Foi
o que tornou a CLI (e depois o gerador de `.bat`) baratos de adicionar.

## Modo de desenvolvimento (duas raias) — DEC-012

O projeto é tocado com o **Claude Code**, além do chat de planejamento:
- **Chat (planejamento):** autora docs (arquivo inteiro para novo/pequeno) e
  **specs** em `meta/specs/` (texto exato + âncora semântica) para deltas em docs
  grandes e para código. Nome novo de spec: `AAMMDD-specNNNN-desc.md` (as antigas
  `spec-0001…0009` ficam como estão).
- **Claude Code (execução):** implementa código, aplica as specs, roda
  `python -m pytest -q`, faz edições append-only nos meta/ e commita.
- Um canal por doc por ciclo; ao aplicar spec, ache a âncora EXATA ou PARE e reporte.

## Como funciona (o pipeline)

Duas fases, espelhadas pelos botões "Pré-visualizar"/"Executar" e pelos modos
`--preview`/execução da CLI:

1. **`make_plan(root, cfg) -> FlattenPlan`** (fonte única) ou
   **`make_plan_sources([Source, ...]) -> FlattenPlan`** (multi-fonte): varrem,
   calculam o nome final de cada arquivo e o que foi pulado, **sem escrever nada**.
2. **`execute_plan(plan, dest, cfg) -> ExecuteResult`**: resolve o destino, limpa
   se (e só se) for nosso, copia com `shutil.copy2` e grava o `_MANIFEST.md`.

### A varredura (`_scan`)

`os.walk(followlinks=False)` (não segue symlinks — evita loops). Poda diretórios
**in-place** (não desce em `node_modules`, `.git`, `dist`, `.next`…) e **contabiliza
cada poda** com motivo e amostra (FIX-001 — antes era silenciosa). Cada arquivo
passa por filtros e, se reprovado, é contado por motivo: ignores embutidos →
`.gitignore`/`.flatdropignore` → sensíveis → tipo (allowlist + filtros de execução)
→ filtro de pasta.

### Ignores: `.gitignore` aninhado + `.flatdropignore` (DEC-014)

Antes só o `.gitignore` da raiz era lido. Agora `_build_ignore_specs` coleta TODOS
os `.gitignore` e `.flatdropignore` da árvore (uma passada extra, podando os
ignores embutidos), reescreve os padrões de subpasta para casar relativo à raiz
(`_rebase_ignore`) e monta **três** matchers pathspec:
- **`full`** = decisão: todos os `.gitignore` (raso→fundo) **seguidos** de todos os
  `.flatdropignore` (raso→fundo). Como é "última regra vence" (semântica gitignore),
  o **`.flatdropignore` tem sempre a palavra final** sobre o `.gitignore`.
- **`gi`** e **`fd`** = só para atribuir o motivo do skip (`gitignore` vs
  `flatdropignore`) e detectar liberação.

O `.flatdropignore` é um arquivo por projeto, com a sintaxe do `.gitignore`:
padrões positivos excluem a mais (o que vai pro git mas não pro Projeto); padrões
com **`!`** re-incluem o que o `.gitignore` bloqueia — **até pasta inteira que
seria podada** (`!logs/` traz `logs/` de volta). `_ignore_status(rel, full, gi, fd)`
devolve `(ignored, source, liberated)`. O próprio `.flatdropignore` está no
`file_ignores` (não vai para o upload). Lógica verificada com o pathspec real
antes de implementar. Sem pathspec, ambos os ignores são desligados (só embutidos).

### Filtros de execução

Por cima da allowlist/denylist padrão, cada execução pode afinar a seleção:
- **`only_ext`** restringe a saída a certas extensões (corte duro — ignora a
  allowlist ampla e os extensionless). Ex.: só `.md`.
- **`exclude_ext`** subtrai extensões do que seria aceito. Ex.: tudo menos `.md`.
- **`add_ext`** (via `--add-ext`) acrescenta extensões à allowlist.
- **`only_folders` + `folder_match`** (`starts`/`contains`/`exact`): só pastas que
  casam os termos; termo com `/` vira prefixo de caminho relativo à raiz da fonte.

Na GUI (pós-UI-1), o **modal "Escolher tipos…"** (checklist categorizado + busca +
marcar/limpar por grupo + adicionar custom) define a allowlist da execução por
seleção; `only_ext`/`exclude_ext` de digitação saíram da tela (o modal os subsume).

### Coleta multi-fonte — o caso "docs + área"

`make_plan_sources` combina várias `Source` (cada uma = raiz + filtros próprios)
numa saída só: varre cada fonte, **une** os candidatos, **deduplica** por caminho
real, roda a renomeação sobre o conjunto unido e grava **um** `_MANIFEST.md` com
caminhos relativos à **raiz comum**. O atalho `--also-md-from <raiz>` adiciona a
coleta "todos os `.md` a partir de `<raiz>`". Na GUI, o toggle "Também incluir
todos os `.md` a partir de [raiz]" faz o mesmo — **ao vivo** (FIX-004: antes só o
`.bat` gerado respeitava o toggle; agora `_on_preview`/`_on_execute` montam as
fontes via o helper `_sources`, espelhando o `_build_cli_args`). O `cli.py` reseta
`exclude_ext` na fonte de `.md` (para as remoções de tipo não afetarem a coleta de md).

### O gerador de `.bat` (na GUI)

O botão "Gerar .bat…" serializa a configuração atual da tela (`_build_cli_args`)
num `.bat` **ASCII** (FIX-003: corpo sem acento; `chcp 65001` só para a saída do
Python) e pede onde salvar (abre na pasta-pai da raiz). A seleção de tipos do modal
é reproduzida fielmente: adições viram `--add-ext`, remoções viram `--exclude-ext`
(por isso não foi preciso a flag `--ext-set`). Avisa se um caminho tiver acento
(frágil no CMD). O launcher `flatdrop-ui.bat` (à parte) só abre a UI sem console.

### A renomeação à prova de colisão (`_plan_names`) — o coração

Garante **nomes únicos**, comparados **case-insensitive** (destino é Windows). Usa
**profundidade uniforme por grupo de nome**: agrupa pelo nome original e escolhe um
único `k` (quantas pastas entram no sufixo) que desempata o grupo, aplicando o
mesmo `k` a todos. Piso de `k` por modo: `collisions` (0 — único fica intacto),
`all` (1), `fullpath` (caminho inteiro). Trunca nomes > `MAX_NAME_LEN` (200) com
hash estável; passe final de contador para empates residuais. Em multi-fonte, a
desambiguação opera sobre os caminhos relativos à raiz comum.

### O destino e o manifesto

`_resolve_dest` (DEC-007): não existe/vazia → usa; **nossa** (tem a assinatura
`<!-- flatdrop-manifest v1 -->`) + "limpar" → `safe_clear` reusa a mesma pasta; de
**terceiros** → nunca apaga, cria `nome (2)`. `write_manifest` grava assinatura +
metadados + a tabela `caminho original → nome plano`; em multi-fonte, lista as
fontes e a raiz comum.

### A pasta Downloads (FIX-002)

`default_downloads_dir` resolve o local **real**: Windows via Known Folder
(`SHGetKnownFolderPath`, ctypes); Linux via `XDG_DOWNLOAD_DIR`/`user-dirs.dirs`;
macOS `~/Downloads`. Home só como último recurso.

## Armadilhas conhecidas (leia antes de mexer no core)

- **Windows é case-insensitive.** Toda comparação de unicidade é em minúsculas.
- **Sufixo só de pasta-pai não garante unicidade.** Daí a profundidade uniforme
  por grupo + o contador final.
- **Caminhos/nomes longos.** Truncamento com hash; não remova o hash.
- **Sensíveis vazam fácil.** A denylist é por nome/sufixo, não scanner de conteúdo.
  Sempre revise a pré-visualização.
- **Loops de symlink.** `followlinks=False`. Mantenha.
- **tkinter não é thread-safe.** Trabalho pesado em thread; todo toque em widget
  volta à thread principal via `self.after`. Modais (`Toplevel`) usam
  `grab_set`/`wait_window`.
- **pathspec ausente = `.gitignore` E `.flatdropignore` ignorados** (avisa, não falha).
- **Poda de pasta tem de deixar rastro** (FIX-001). Qualquer exclusão é contabilizada.
- **`.flatdropignore` sobrepõe o `.gitignore`** (decisão deliberata, ≠ git puro):
  todos os `fd` vêm depois de todos os `gi` no matcher `full`. Se mudar a ordem,
  quebra a re-inclusão por `!`. Ele exige uma passada extra na árvore.
- **`.bat` no CMD tem de ser ASCII no corpo** (FIX-003). Acento só na saída via `chcp`.
- **GUI e `.bat` têm de dar o mesmo resultado** (FIX-004): ao adicionar opção que o
  gerador serializa, ligue-a também à execução ao vivo (`_sources`) no mesmo ciclo.
- **Arquivos de engine.** Godot (`.gd`/`.tscn`/`.tres`/`.gdshader`/`.godot`/`.import`/
  `.gd.uid`→`uid`) já entraram no padrão (DEC-013). Outros engines: use `--add-ext`
  ou o modal, sem cravar no `config.py` sem evidência.
- **Multi-fonte e raiz comum.** Caminhos do manifesto relativos à raiz comum;
  raízes em drives diferentes (Windows) caem em modo degradado. Dedup por caminho real.

## Convenções

- Documentação e comentários em **PT-BR**; identificadores de código em **inglês**.
- Mensagens de commit em **PT-BR, sem acento** (Conventional Commits) — o Git Bash
  do Code e o CMD do usuário corrompem acento.
- Comandos de terminal no formato **CMD do Windows** (uma linha; `-m` repetido no
  commit; caminhos com `\`).
- Versionamento semântico; histórico em `CHANGELOG.md` (Keep a Changelog).
- Validação = `pytest` (a GUI não é testada pela suíte — tkinter fora do CI; smoke
  manual no Windows).
