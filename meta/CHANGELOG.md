# Changelog — FlatDrop

Todas as mudanças notáveis deste projeto são registradas aqui.
Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/);
versionamento conforme [SemVer](https://semver.org/lang/pt-BR/).

## [Não lançado]

Candidatos da Fase 2 ainda abertos em `ROADMAP.md`: `_TREE.md` (B), pastas
recentes/persistência (C), ignores de pasta editáveis (D).

## [0.2.0] — 2026-06-14

Linha de comando, coleta multi-fonte com manifesto único, filtros de seleção e
duas correções. Tudo reaproveitando a core existente (a separação core×gui pagou
a aposta: a CLI não duplicou regra de negócio).

### Adicionado
- **CLI** (`flatdrop/cli.py`): `python run.py` sem argumentos abre a GUI; com
  argumentos roda no terminal. Flags: `--root`, `--dest`, `--name`, `--mode`,
  `--sep`, `--only-ext`, `--exclude-ext`, `--add-ext`, `--only-folder`,
  `--folder-match`, `--no-gitignore`, `--include-sensitive`, `--no-manifest`,
  `--no-clear`, `--also-md-from`, `--preview`.
- **Coleta multi-fonte** (`make_plan_sources`, tipo `Source`): combina várias
  raízes/filtros numa única saída e **um** `_MANIFEST.md`, com caminhos relativos
  à raiz comum e deduplicação por caminho real (nenhum arquivo entra duas vezes).
- **`--also-md-from <raiz>`**: atalho que adiciona a coleta "todos os `.md` a
  partir de `<raiz>`" à mesma saída — monta o padrão "docs do repo + conteúdo de
  uma área" sem dois manifestos.
- **Filtros de execução** no `ScanConfig` e na GUI/CLI: `only_ext` (restringe),
  `exclude_ext` (subtrai), filtro de pasta `only_folders` + `folder_match`
  (starts/contains/exact; termo com `/` vira prefixo de caminho); e `--add-ext`
  para acrescentar extensões à allowlist (ex.: `gd,tscn,tres` para Godot).
- **5 `.bat` do cinzeiro** em `bat/cinzeiro/`: `00-todos-md.bat` (só os `.md` do
  grupo) e `story/art/game/ost-pack.bat` (não-`.md` da área + todos os `.md`).
- **Testes**: `tests/test_cli.py` (3) e novos casos no core (filtros, multi-fonte,
  Downloads). Total: 26 testes passando.

### Corrigido
- **FIX-001 — poda de pastas era silenciosa.** Pasta inteira engolida pelo
  `.gitignore` (ou pelos ignores embutidos) sumia com a subárvore sem deixar
  rastro na pré-visualização. Agora é contabilizada (`gitignore (pasta)` /
  `ignore_padrão (pasta)`), com amostras, e o `.gitignore` que engole pastas vira
  aviso de primeira classe. A GUI passou a exibir as amostras de pulados por
  motivo (antes só mostrava contadores). Caso real: pastas renomeadas para `logs`
  no monorepo `cinzeiro` casavam `logs/` do `.gitignore` e "sumiam".
- **FIX-002 — Downloads caía na raiz do perfil.** `default_downloads_dir` agora
  resolve o local REAL: no Windows via Known Folder (`SHGetKnownFolderPath`,
  ctypes, sem dependência nova) — cobre o caso da pasta movida/redirecionada de
  disco; no Linux via `XDG_DOWNLOAD_DIR`/`user-dirs.dirs`. A home só é usada como
  último recurso (antes o fallback disparava cedo demais).

## [0.1.0] — 2026-06-05

Primeira versão funcional (MVP). Projeto, arquitetura, código e documentação de
contexto criados na sessão de gênese.

### Adicionado
- Pipeline de duas fases: `make_plan` (pré-visualização, não grava nada) e
  `execute_plan` (copia e gera manifesto).
- Varredura recursiva a partir de uma pasta raiz com `os.walk(followlinks=False)`
  e poda de diretórios in-place.
- Leitura do `.gitignore` da raiz via pathspec (dependência opcional, com modo
  degradado e aviso quando ausente).
- Ignores embutidos de diretórios (`node_modules`, `.git`, `dist`, `.next`…),
  arquivos (lockfiles, `.DS_Store`…) e sufixos (`.min.js`, `.map`, compilados).
- Allowlist de tipos de texto/código úteis ao Claude e lista de arquivos sem
  extensão permitidos (`Dockerfile`, `Makefile`, `.gitignore`…).
- Denylist de arquivos sensíveis (`.env` real, `*.pem`/`*.key`, `id_rsa`,
  `secrets.*`…) sempre pulada por padrão, com exceção para exemplos
  (`.env.example`/`.sample`/`.template`).
- Renomeação à prova de colisão com unicidade garantida (case-insensitive),
  desambiguação por profundidade uniforme dentro de cada grupo de nome,
  truncamento de nomes longos com hash e passe final de contador.
- Três modos de renomeação: `collisions` (padrão), `all` e `fullpath`.
- `safe_clear` / `is_our_folder` / `_resolve_dest`: limpa e reusa apenas pastas
  vazias ou comprovadamente do FlatDrop; pasta de terceiros vira variante `(2)`.
- `_MANIFEST.md` na saída: assinatura, metadados (origem, data, modo, contagem,
  tamanho, estimativa grosseira de tokens) e tabela `caminho original → nome plano`.
- Interface gráfica em tkinter amarrando tudo, com trabalho em thread separada.
- Entrypoint `run.py`, `requirements.txt` e `README.md`.
- Suíte de 13 testes em `tests/test_core.py` (pytest), todos passando.
