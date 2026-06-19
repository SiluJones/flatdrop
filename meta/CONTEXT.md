# CONTEXT — FlatDrop

Documento de contexto principal. Leia este primeiro ao abrir uma nova conversa.
Para o estado atual, veja `STATUS.md`; para o porquê das escolhas, `DECISIONS.md`.

> **Mudanças nesta revisão (2026-06-14):** atualizado para a 0.2.0 — entram a CLI,
> a coleta multi-fonte e os filtros de seleção; corrigida a descrição da estrutura
> (os docs de contexto vivem em `meta/` no repo real) e acrescentadas as
> armadilhas novas. O essencial do MVP permanece.

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
- **pathspec** — única dependência e **opcional**: interpreta o `.gitignore`
  corretamente. Sem ela, modo degradado com só os ignores embutidos (DEC-004).
- **pytest** — só para a suíte de testes.

## Estrutura do repositório

```
flatdrop/                       # raiz do repo (é também a raiz do Git)
├── run.py                      # entrypoint: sem args -> GUI; com args -> CLI
├── requirements.txt            # pathspec (opcional)
├── README.md
├── flatdrop/                   # o pacote
│   ├── __init__.py             # __version__ = "0.2.0"
│   ├── config.py               # defaults: extensões, ignores, sensíveis, separador
│   ├── core.py                 # LÓGICA PURA, sem UI — onde mora tudo que importa
│   ├── cli.py                  # interface de linha de comando (amarra a core)
│   └── gui.py                  # interface tkinter (amarra a core)
├── bat/
│   └── cinzeiro/               # 5 .bat prontos do monorepo do usuário
├── tests/                      # test_core.py + test_cli.py (26 testes)
├── logs/                       # logs de sessão (AAAA-MM-DD.md)
└── meta/                       # os .md de contexto (CONTEXT, STATUS, etc.)
```

Atenção à transferência: no Projeto do Claude os docs de contexto ficam em
`meta/`, mas o mount (`/mnt/project/`) chega **achatado** (sem subpastas). O
`_MANIFEST.md` do repo é a fonte de verdade dos nomes/estrutura quando há colisão.

A separação **core × (gui, cli)** é proposital (DEC-009): toda a lógica fica em
`core.py`, sem importar tkinter; GUI e CLI só coletam opções e chamam a core. Foi
o que tornou a CLI barata de adicionar.

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
`.gitignore` → sensíveis → tipo (allowlist + filtros de execução) → filtro de pasta.

### Filtros de execução (0.2.0)

Por cima da allowlist/denylist padrão, cada execução pode afinar a seleção:
- **`only_ext`** restringe a saída a certas extensões (corte duro — ignora a
  allowlist ampla e os extensionless). Ex.: só `.md`.
- **`exclude_ext`** subtrai extensões do que seria aceito. Ex.: tudo menos `.md`.
- **`add_ext`** (via `--add-ext`) acrescenta extensões à allowlist (ex.: `gd`,
  `tscn`, `tres` para arquivos de engine que não estão no padrão).
- **`only_folders` + `folder_match`** (`starts`/`contains`/`exact`): só pastas que
  casam os termos; termo com `/` vira prefixo de caminho relativo à raiz da fonte.

### Coleta multi-fonte (0.2.0) — o caso "docs + área"

`make_plan_sources` combina várias `Source` (cada uma = raiz + filtros próprios)
numa saída só: varre cada fonte, **une** os candidatos, **deduplica** por caminho
real, roda a renomeação sobre o conjunto unido e grava **um** `_MANIFEST.md` com
caminhos relativos à **raiz comum**. O atalho `--also-md-from <raiz>` adiciona a
coleta "todos os `.md` a partir de `<raiz>`" — é assim que um `.bat` de área traz
os arquivos desenvolvidos da área **mais** todos os `.md` do repositório, sem dois
manifestos (DEC-010, DEC-011).

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
macOS `~/Downloads`. Home só como último recurso. Antes caía na home quando a
pasta tinha sido movida de disco.

## Armadilhas conhecidas (leia antes de mexer no core)

- **Windows é case-insensitive.** Toda comparação de unicidade é em minúsculas.
- **Sufixo só de pasta-pai não garante unicidade.** Daí a profundidade uniforme
  por grupo + o contador final.
- **Caminhos/nomes longos.** Truncamento com hash; não remova o hash (é ele que
  mantém a unicidade após cortar).
- **Sensíveis vazam fácil.** A denylist é por nome/sufixo, não scanner de conteúdo.
  Sempre revise a pré-visualização.
- **Loops de symlink.** `followlinks=False`. Mantenha.
- **tkinter não é thread-safe.** Trabalho pesado em thread; todo toque em widget
  volta à thread principal via `self.after`.
- **pathspec ausente = `.gitignore` ignorado** (avisa, não falha).
- **Poda de pasta tem de deixar rastro** (FIX-001). Qualquer exclusão — arquivo ou
  pasta — é contabilizada e amostrada; não volte a podar em silêncio.
- **Arquivos de engine fora da allowlist.** `.gd`/`.tscn`/etc. não estão no padrão;
  use `--add-ext`. Não cravar extensões de um engine específico no `config.py` sem
  evidência do projeto real.
- **Multi-fonte e raiz comum.** Os caminhos do manifesto são relativos à raiz
  comum; raízes em drives diferentes (Windows) caem num modo degradado (cada
  arquivo relativo à própria fonte). Dedup é por caminho real (case-insensitive).

## Convenções

- Documentação e comentários em **PT-BR**; identificadores de código em **inglês**.
- Mensagens de commit em **PT-BR** (Conventional Commits).
- Versionamento semântico; histórico em `CHANGELOG.md` (Keep a Changelog).
