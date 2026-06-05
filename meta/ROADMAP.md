# ROADMAP — FlatDrop

Direção do projeto por fases. Sem datas: a ordem importa mais que o calendário.
Itens em aberto vêm de `IDEAS.md`; ao concluir, registre em `CHANGELOG.md`.

## Fase 1 — MVP ✅ (concluída em 2026-06-05)

A ferramenta faz o trabalho essencial de ponta a ponta.

- [x] Varredura recursiva com poda de diretórios.
- [x] Leitura de `.gitignore` (pathspec opcional) + ignores embutidos.
- [x] Allowlist de tipos + denylist de sensíveis.
- [x] Renomeação à prova de colisão com unicidade garantida (3 modos).
- [x] Pipeline planejar→executar com pré-visualização.
- [x] `safe_clear` e reuso seguro da pasta de saída.
- [x] `_MANIFEST.md` com mapa origem→nome e metadados.
- [x] GUI tkinter completa.
- [x] 13 testes passando.

## Fase 2 — Robustez e conveniência (próxima)

Tornar o uso diário mais agradável e cobrir casos reais.

- [ ] Testar em projetos reais (Next.js e Python) e ajustar a partir do feedback.
- [ ] Persistir configurações entre execuções (última raiz/destino/modo/extensões).
- [ ] Ler `.gitignore` aninhado (de subpastas), não só o da raiz.
- [ ] Resync incremental: comparar com o manifesto anterior e copiar só o que mudou.
- [ ] Mensagens e avisos mais visíveis quando o pathspec está ausente.

## Fase 3 — Distribuição e automação

Alcançar quem não tem Python e permitir uso por terminal.

- [ ] CLI sem GUI (`flatdrop <raiz> [opções]`) reaproveitando o core.
- [ ] Empacotar como `.exe` com PyInstaller (duplo-clique no Windows).

## Fase 4 — Modo arquivo-único (opcional)

- [ ] Botão que concatena tudo num único `.md`/`.xml` com cabeçalhos por arquivo,
      como complemento ao modo pasta (não substituto). Aproveitar aprendizados do
      Repomix (header explicativo, respeito a `.gitignore`, sensíveis fora).
- [ ] Contagem de tokens mais fiel (tokenizador real, opcional).

## Fora de escopo (decidido)

- **Upload automático para o Claude.** Não há API pública para os arquivos de
  Projeto; a etapa de arrastar permanece manual por enquanto. (Ver DEC-001 e
  "Descartadas" em `IDEAS.md`.)
