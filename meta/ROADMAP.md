# ROADMAP — FlatDrop

Direção do projeto por fases. Sem datas: a ordem importa mais que o calendário.
Itens em aberto vêm de `IDEAS.md`; ao concluir, registre em `CHANGELOG.md`.

> **Mudanças nesta revisão (2026-06-14):** Fase 2 entrou **em curso** — testes em
> projeto real feitos; CLI, multi-fonte e filtros entregues (antecipando a CLI
> que era da Fase 3, porque destravava os `.bat`). Restam B/C/D na Fase 2. O
> gerador de `.bat` pela interface entrou como Fase 3.

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

## Fase 2 — Robustez e conveniência (em curso)

- [x] Testar em projeto real (monorepo `cinzeiro`) — funciona; daí o FIX-001.
- [x] **CLI** sem GUI (antecipada da Fase 3) reaproveitando a core.
- [x] **Multi-fonte com manifesto único** + `--also-md-from` (docs do repo +
      conteúdo de área numa saída só).
- [x] **Filtros de seleção**: `--only-ext`/`--exclude-ext`/`--add-ext` e
      `--only-folder`/`--folder-match`.
- [x] **5 `.bat` do cinzeiro** (só-`.md` e por área).
- [x] **FIX-001** (poda de pasta visível) e **FIX-002** (Downloads real).
- [ ] **B —** `_TREE.md` opcional na saída (árvore + pulados + pastas podadas).
- [ ] **C —** Persistir configurações + pastas recentes na GUI.
- [ ] **D —** Ignores de pasta editáveis na GUI (com núcleo imutável).
- [ ] Aviso mais visível quando o pathspec está ausente (destaque na GUI).
- [x] Acrescentar tipos à allowlist de defaults (spec-0001 aplicada: Godot, PDF/DOCX/XLSX/ODT/RTF/EPUB, +linguagens).
- [ ] **E2 —** Expor seleção de tipo na GUI (só-ext / exceto-ext) — filtros já existem na core.
- [ ] Liberar item específico do `.gitignore` na GUI (force-include), sem desligar a leitura inteira.
- [ ] **`.flatdropignore`** (ignore próprio, aninhado, com negação para liberar) + `.gitignore` aninhado — sai do stand-by; precisa de design.

## Fase 3 — Gerador de `.bat` e multi-fonte na GUI

- [ ] Botão "Exportar `.bat`…" na GUI: serializa a config da tela em linha de
      comando e salva o arquivo (a tela de config vira o editor do `.bat`).
- [ ] Expor multi-fonte na GUI (ex.: toggle "incluir todos os `.md` a partir de
      [raiz]"), em conjunto com o exportador.

## Fase 4 — Distribuição e modo arquivo-único

- [ ] Empacotar como `.exe` com PyInstaller (duplo-clique sem Python).
- [ ] Modo single-file (estilo Repomix) **com os mesmos filtros** (ex.: fundir só
      os `.md`), como complemento ao modo pasta.
- [ ] Contagem de tokens mais fiel (tokenizador real, opcional).

## Stand-by (sem fase definida)

- `.gitignore` aninhado (ler os de subpastas).
- Resync incremental por diff do manifesto.
- Drag-and-drop da pasta raiz na janela.

## Fora de escopo (decidido)

- **Upload automático para o Claude.** Não há API pública para os arquivos de
  Projeto; arrastar permanece manual. (Ver DEC-001 e "Descartadas" em `IDEAS.md`.)
