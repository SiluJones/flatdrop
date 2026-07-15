# ROADMAP — FlatDrop

Direção do projeto por fases. Sem datas: a ordem importa mais que o calendário.
Itens em aberto vêm de `IDEAS.md`; ao concluir, registre em `CHANGELOG.md`.

> **Mudanças nesta revisão (2026-07-15):** specs 0017–0024 aplicadas. **KCM**, **editor
> visual de `.flatdropignore` (Fase 2-D)** e **item C (persistência + recentes)**
> concluídos; **0.6.0**, **58 testes**. O invariante **DEC-020** grava que o `.bat` não
> pode ser degradado por conveniência. Próximas frentes: **multi-raiz na GUI** e o
> **force-include por caminho exato** (correção do `.min.js`).

> **Mudanças nesta revisão (2026-07-05, transferência):** ciclo fechado — specs
> 0011–0016 aplicadas, `pytest` puro corrigido (FIX-005), **0.3.1** cortada, 41
> testes. Prioridade da Fase 2 redefinida: as **próximas duas tarefas** são (1) o
> trecho de KCM (ler `_TREE.md` → gerar `.flatdropignore`) e (2) o **editor de
> `.flatdropignore` na GUI** (= item D); o item C (persistência) vem depois delas.

## Fase 1 — MVP ✅ (concluída em 2026-06-05)

- [x] Varredura recursiva com poda de diretórios.
- [x] Leitura de `.gitignore` (pathspec opcional) + ignores embutidos.
- [x] Allowlist de tipos + denylist de sensíveis.
- [x] Renomeação à prova de colisão com unicidade garantida (3 modos).
- [x] Pipeline planejar→executar com pré-visualização.
- [x] `safe_clear` e reuso seguro da pasta de saída.
- [x] `_MANIFEST.md` com mapa origem→nome e metadados.
- [x] GUI tkinter completa.
- [x] 13 testes passando.

## Fase 2 — Robustez e conveniência (quase concluída)

- [x] Testar em projeto real (monorepo `cinzeiro`) — funciona; daí o FIX-001.
- [x] **CLI** sem GUI (antecipada da Fase 3) reaproveitando a core.
- [x] **Multi-fonte com manifesto único** + `--also-md-from`.
- [x] **Filtros de seleção**: `--only-ext`/`--exclude-ext`/`--add-ext` e `--only-folder`/`--folder-match`.
- [x] **5 `.bat` do cinzeiro** (só-`.md` e por área) + launcher `flatdrop-ui.bat`.
- [x] **FIX-001** (poda de pasta visível) e **FIX-002** (Downloads real).
- [x] Acrescentar tipos à allowlist (spec-0001: Godot, PDF/DOCX/XLSX/ODT/RTF/EPUB, +linguagens).
- [x] **E2 —** Seleção de tipo na GUI por modal (UI-1).
- [x] Liberar do `.gitignore` — resolvido pela negação `!` do `.flatdropignore` (spec-0008).
- [x] **`.flatdropignore`** (aninhado + negação) + `.gitignore` aninhado (DEC-014, spec-0008).
- [x] **FIX-003** (`.bat` ASCII) e **FIX-004** (multi-fonte ao vivo na GUI).
- [x] **B — `_TREE.md`** opcional na saída (árvore + pulados + pastas ignoradas colapsadas em UMA linha, sem recursão). Entregue na spec0011 (35 testes; verificado no mount).
- [x] **Trecho de KCM: ler `_TREE.md` → gerar `.flatdropignore`.** Entregue (bloco de KCM portável + exemplo no README; material externo, não é código do repo). Habilitado pela spec0011.
- [x] **D — Editor de `.flatdropignore` na GUI** (Fase 2-D, specs 0017–0021). Modal com árvore lazy, checkbox binário, badges de tipo/sensível, bloco gerenciado no arquivo e glifo indeterminado correto na visão colapsada (FIX-007). Consolidou "ignores de pasta editáveis".
- [x] **C —** Persistir configurações + pastas recentes na GUI (specs 0022–0024, 0.6.0). `settings.json` por plataforma, Combobox de recentes, grava ao Executar; escopo só-GUI (DEC-020) para não tocar o `.bat`.
- [ ] **Multi-raiz na GUI**: selecionar N pastas de uma vez, prefixando cada uma com o nome da sua raiz (a core já suporta multi-fonte; falta a UI de N raízes).
- [x] **Fullpath com pasta-raiz** (spec0013 + spec0014): flag `root_in_name` inclui o nome do projeto no nome de cada arquivo, no modo fullpath. Formato final: stem + caminho invertido + raiz no fim.
- [x] **FIX-005** (`conftest.py` na raiz para `pytest` puro achar o pacote) — spec0016.
- [ ] Aviso mais visível quando o pathspec está ausente (destaque na GUI).
- [~] **UI/UX (em fases):** UI-1 feita; **UI-2** (polimento de layout) e **UI-3** (presets/lembrar seleção) na fila.

## Fase 3 — Gerador de `.bat` e multi-fonte na GUI ✅ (concluída em 2026-06-24)

- [x] Botão "Gerar .bat…" na GUI: serializa a config da tela em linha de comando e salva o arquivo (a tela vira o editor do `.bat`), sempre ASCII.
- [x] Expor multi-fonte na GUI (toggle "incluir todos os `.md` a partir de [raiz]"), ao vivo.

## Fase 4 — Distribuição e modo arquivo-único

- [ ] Empacotar como `.exe` com PyInstaller (duplo-clique sem Python).
- [ ] Modo single-file (estilo Repomix) **com os mesmos filtros** (ex.: fundir só os `.md`).
- [ ] Contagem de tokens mais fiel (tokenizador real, opcional).

## Stand-by (sem fase definida)

- Resync incremental por diff do manifesto.
- Drag-and-drop da pasta raiz na janela.
- Saída da CLI ASCII-safe (dispensa `chcp` nos `.bat`).
- Botão "Gerar atalho da UI" (cria o launcher calculando o caminho sozinho).

## Fora de escopo (decidido)

- **Upload automático para o Claude.** Não há API pública para os arquivos de
  Projeto; arrastar permanece manual. (Ver DEC-001 e "Descartadas" em `IDEAS.md`.)

## Release pendente

- ~~Cortar **0.3.0**~~ — **spec0012 aplicada** (bump `flatdrop/__init__.py`
  0.2.0->0.3.0 + CHANGELOG fechado com `[0.3.0] — 2026-07-04`, `_TREE.md` incluído,
  nova `[Não lançado]` aberta). 35 testes verdes.
- ~~Cortar **0.3.1**~~ — **spec0015 aplicada** (`root_in_name` do spec0013 entrou
  APÓS o corte da 0.3.0, então não constava no `### Adicionado` da `[0.3.0]`): bump
  `flatdrop/__init__.py` 0.3.0→0.3.1 + nova seção `[0.3.1] — 2026-07-05` com o
  root_in_name (Adicionado) e o fix de ordem (Corrigido); `[0.3.0]` intacta. 41
  testes verdes.
