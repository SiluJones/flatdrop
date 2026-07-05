# Changelog — FlatDrop

Todas as mudanças notáveis deste projeto são registradas aqui.
Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/);
versionamento conforme [SemVer](https://semver.org/lang/pt-BR/).

## [Não lançado]

### Corrigido
- **FIX-005 — `pytest` puro falhava ao coletar (`ModuleNotFoundError: flatdrop`)**
  (spec0016): adicionado `conftest.py` na raiz do repo com
  `sys.path.insert(0, Path(__file__).resolve().parent)`. O pytest o importa antes de
  coletar, inserindo a raiz no `sys.path` — então `from flatdrop import ...` resolve
  com `pytest` puro, sem depender de `python -m pytest`. Espelha o que o `run.py` já
  faz para a aplicação. Sem mudança de código de produção. Entra no próximo corte de
  patch.

_Itens de produto em aberto: trecho de KCM (ler `_TREE.md` → gerar `.flatdropignore`),
editor de `.flatdropignore` na GUI (Fase 2-D), persistência/recentes (Fase 2-C),
multi-raiz na GUI, formato de nome "caminho escrito" (raiz→pastas→stem), UI-2/UI-3._

## [0.3.1] — 2026-07-05

Acabamento do modo fullpath: opção de incluir o nome da pasta-raiz no nome de cada
arquivo. Recurso pequeno e opt-in que entrou logo após o corte da 0.3.0; a mesma
sessão ajustou a ordem do sufixo antes de qualquer uso real. Suíte de 41 testes verde.

### Adicionado
- **`root_in_name` — pasta-raiz no nome (modo fullpath)** (spec0013): flag opcional
  (desligada por padrão) que, no modo `fullpath` e em **fonte única**, inclui o nome
  da pasta-raiz do projeto no nome de cada arquivo — inclusive os da raiz
  (`README.md` → `README__meuapp.md`). A injeção acontece só no **nome planejado**
  (via `root_prefix` em `_plan_names`); o `rel` de exibição do `_MANIFEST.md` e do
  `_TREE.md` permanece o caminho real. Ignorada com aviso fora do `fullpath` e em
  multi-fonte (lá o caminho já parte da raiz comum). Exposta como `--root-in-name`
  na CLI e como checkbox na GUI (serializada no `.bat`, FIX-004). O limite de nome do
  Windows segue protegido pelo truncamento com hash já existente.

### Corrigido
- **Ordem do sufixo do `root_in_name`** (spec0014): o formato passou a ser
  **stem + caminho da pasta mais interna à mais externa + nome da pasta-raiz por
  último** (ex.: `app/routes/page.tsx` sob `meuapp` → `page__routes__app__meuapp.tsx`),
  em vez da raiz logo após o stem que a primeira implementação produzia. Ajuste de
  uma linha em `_plan_names` (`(*reversed(dir_parts), root_prefix)`), sem tocar
  `_compose`; o `fullpath` sem a flag permanece idêntico.

## [0.3.0] — 2026-07-04

CLI completa, coleta multi-fonte com manifesto único, expansão de tipos aceitos,
seleção de tipos por modal na GUI, gerador de `.bat`, `.flatdropignore` (+ `.gitignore`
aninhado), `_TREE.md` opcional, adoção do modo Claude Code (duas raias) e integração
do KCM. Duas correções de peso (FIX-003 ASCII no `.bat`, FIX-004 multi-fonte ao vivo).
Suíte de 35 testes verde. A separação core×gui seguiu pagando: CLI e GUI compartilham
a mesma lógica sem duplicação.

### Adicionado
- **Allowlist de tipos expandida** (DEC-013, spec-0001): documentos que o Projeto
  do Claude aceita (`pdf`, `docx`, `doc`, `xlsx`, `rtf`, `odt`, `epub`); Godot
  (`gd`, `uid` para `.gd.uid`, `gdshader`, `tscn`, `tres`, `godot`, `import`); e um
  conjunto curado de linguagens/config (Julia, Nim, Zig, Solidity, CUDA, Terraform/
  HCL, Nix, templates, etc.). Imagens/áudio/vídeo seguem fora.
- **GUI — seleção de tipos por modal (UI-1, spec-0007):** botão "Escolher tipos…"
  abre um `TypePickerDialog` (checklist categorizado — Godot, Linguagens, Web,
  Config, Documentos, Templates, Outros — com busca, marcar/limpar por grupo,
  adicionar tipo custom). A tela principal ficou compacta (só o resumo "Tipos: N de
  M"); a caixa de extensões e os campos "Só estes/Exceto" saíram (o modal os subsume).
- **GUI — gerador de `.bat`** (spec-0003, refinado na 0007): botão "Gerar .bat…"
  serializa a config da tela (`_build_cli_args`) num `.bat` ASCII e salva (abre na
  pasta-pai da raiz). Reproduz a seleção do modal via `--add-ext` (adições) +
  `--exclude-ext` (remoções). Avisa em caminho com acento.
- **GUI — multi-fonte ao vivo** (spec-0005): toggle "Também incluir todos os `.md`
  a partir de [raiz]" passou a valer no Pré-visualizar/Executar (helper `_sources`
  + `make_plan_sources`), não só no `.bat` gerado. "Procurar…" do multi-fonte abre
  na pasta-pai da raiz. A janela abre **maximizada**.
- **`.flatdropignore` + `.gitignore` aninhado** (DEC-014, spec-0008): lê os
  `.gitignore` de subpastas (aninhado) e adiciona um `.flatdropignore` por projeto
  (sintaxe do gitignore, aninhado) que exclui a mais e, com `!`, **libera** o que o
  `.gitignore` bloqueia — até pasta que seria podada. Modelo de "última regra vence"
  com rebasing dos padrões de subpasta; o `.flatdropignore` tem a palavra final
  sobre o `.gitignore`. Atribui o motivo do skip (`gitignore`/`flatdropignore`).
  Verificado com o pathspec real antes de implementar. +3 testes.
- **Launcher `bat/flatdrop-ui.bat`:** abre a UI sem janela de console (`pythonw`),
  copiável para qualquer lugar (acesso rápido à interface).
- **Modo Claude Code** (DEC-012): arranque `CLAUDE.md` (raiz) + `.claude/`
  (`settings.json`, `commands/apply-spec.md`, `commands/wrap.md`); specs em
  `meta/specs/`. `meta/CLAUDE.md` (comportamento) → `meta/CEREBRO.md`.
- **Integração da atualização do KCM** (DEC-015, spec0010): seção "Recomendação de
  configuração" no CEREBRO, convenção nova de nome de spec `AAMMDD-specNNNN-desc.md`,
  `HISTORICO.md` → `HISTORY.md`. HUB omitido (projeto solo).
- **`_TREE.md` opcional na saída** (spec0011, Fase 2-B): árvore indentada da origem
  ao lado do `_MANIFEST.md` — arquivos copiados (renomeados marcados com o nome
  plano), pulados com o motivo, e **pastas ignoradas colapsadas em UMA linha, sem
  recursão** (padrão `tree --gitignore`/repomix; `node_modules/ [ignorada: embutido]`
  nunca expande). Desligado por padrão: checkbox na GUI + `--tree` na CLI (serializado
  no `.bat`, FIX-004). Detalhe dos pulados soltos via `--tree-detail summary|full`
  (default `summary`); o `_scan` passou a devolver a lista completa de pulados
  (`skipped_items`, sem o teto de 8 amostras). +8 testes (27 → 35).

### Corrigido
- **FIX-003 — `.bat` falhava no CMD por caracteres não-ASCII.** Travessão/acentos no
  corpo do `.bat` + `chcp 65001` desalinhavam a leitura do CMD (fragmentos viravam
  comando: `'FlatDrop'`/`'m'`/`'Use'`). Corpo dos `.bat` passou a ser ASCII puro
  (`chcp` só para a saída do Python); os 5 `.bat` do cinzeiro reentregues em ASCII
  e sem `--add-ext` redundante; o gerador emite sempre ASCII.
- **FIX-004 — toggle multi-fonte não afetava a execução ao vivo na GUI.** O toggle
  só estava ligado ao gerador de `.bat`; `_on_preview`/`_on_execute` chamavam
  `make_plan` (fonte única). Corrigido com o helper `_sources` + `make_plan_sources`.

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
  Downloads).

### Corrigido
- **FIX-001 — poda de pastas era silenciosa.** Pasta inteira engolida pelo
  `.gitignore` (ou pelos ignores embutidos) sumia com a subárvore sem deixar
  rastro na pré-visualização. Agora é contabilizada (`gitignore (pasta)` /
  `ignore_padrão (pasta)`), com amostras, e o `.gitignore` que engole pastas vira
  aviso de primeira classe. A GUI passou a exibir as amostras de pulados por
  motivo. Caso real: pastas renomeadas para `logs` no monorepo `cinzeiro`.
- **FIX-002 — Downloads caía na raiz do perfil.** `default_downloads_dir` agora
  resolve o local REAL: no Windows via Known Folder (`SHGetKnownFolderPath`,
  ctypes, sem dependência nova); no Linux via `XDG_DOWNLOAD_DIR`/`user-dirs.dirs`.
  A home só é usada como último recurso.

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
