# spec-0002 — Atualizações de meta desta sessão (2026-06-22)

**Tipo:** doc · **Alvos:** `meta/DECISIONS.md`, `meta/IDEAS.md`, `meta/ROADMAP.md`, `meta/STATUS.md`
**Autor:** chat · **Aplicador:** Claude Code · Sem build (só doc; a rede é o `git diff`).
**Regra:** localizar cada âncora EXATAMENTE; se faltar, PARAR e reportar. Não tocar fora do nomeado.

---

## 1) DECISIONS.md — acrescentar DUAS entradas ao FINAL do arquivo

**Âncora (fim do arquivo):**
```
de ser perguntada ao sistema, ou o fallback mascara o problema.
```
**Ação:** após essa linha, acrescentar:
```

---

## DEC-012 — Desenvolvimento em duas raias (chat autora, Claude Code implementa)
**Data:** 2026-06-22 · **Status:** aceita

**Contexto.** O kit passou a suportar o modo Claude Code. Antes, o chat planejava E
implementava o código no mesmo turno (via mount). Isso mistura curadoria com execução e
gasta contexto do chat com detalhe de implementação.

**Decisão.** Adotar duas raias: o **chat** autora documentos (arquivo inteiro para
novo/pequeno; **spec** em `meta/specs/` com texto exato + âncora semântica para delta em doc
grande) e specs de código; o **Claude Code** implementa o código, aplica as specs, roda
`pytest`, faz edições append-only nos meta e commita. "Um canal por doc por ciclo": se um doc
foi por spec, o chat não o entrega inteiro no mesmo ciclo. Criados os arquivos de arranque na
raiz (`CLAUDE.md`, `.claude/settings.json`, `.claude/commands/`). O antigo `meta/CLAUDE.md`
(comportamento) virou `meta/CEREBRO.md` — superconjunto exato do anterior (nada perdido); o
nome `CLAUDE.md` passou a ser o guia-raiz curto do Code.

**Alternativas.** Seguir implementando tudo no chat (mistura raias, gasta contexto);
implementar só no chat e usar o Code só para doc (subaproveita o Code em código).

**Consequência.** O chat fica mais enxuto e focado em decisão/arquitetura/curadoria; o código
é implementado e testado no Code com diff auditável. Custo: disciplina de manter specs com
âncoras exatas e de não duplicar canal por doc.

## DEC-013 — Expandir a allowlist de tipos (defaults), sem virar pega-tudo
**Data:** 2026-06-22 · **Status:** aceita

**Contexto.** Faltavam tipos que o Projeto do Claude aceita (PDF/DOCX/XLSX e ainda ODT/RTF/EPUB)
e os do engine do usuário (Godot: `.gd`, `.gd.uid`…), além de várias linguagens/config comuns.

**Decisão.** Acrescentar um conjunto curado à `DEFAULT_EXTENSIONS` (ver `spec-0001`), incluindo
os documentos binários aceitos pelo Projeto — mantendo imagens/áudio/vídeo FORA. Defaults
generosos cobrem o caso comum; o ajuste fino por projeto fica para o `.flatdropignore` (futuro),
em vez de inflar o config indefinidamente.

**Alternativas.** Só os 5 tipos pedidos (deixaria gaps óbvios de linguagem); só `.flatdropignore`
e nenhum default novo (todo projeto teria de reconfigurar do zero).

**Consequência.** Mais tipos chegam ao Projeto sem configuração. Ressalva: a estimativa de
tokens (`bytes/4`) não vale para binários, e binários grandes podem estourar o teto de 30 MB.
```

---

## 2) IDEAS.md — novos itens em "Ativas" + nova seção "Feedback para o Kit"

**Âncora A (último item de "## Ativas"):**
```
- **Drag-and-drop da pasta raiz na janela.** Arrastar a pasta em vez de navegar
```
**Ação:** ANTES da linha `## Concluídas`, acrescentar (mantendo o item Drag-and-drop existente):
```
- **`.flatdropignore` (ignore próprio da ferramenta).** Um arquivo por projeto, lido como o
  `.gitignore` (via pathspec) e ANINHADO (lido ao entrar em subpastas), para excluir o que vai
  para o git mas não para o Projeto do Claude (docs gerados, dados grandes). Com negação (`!`)
  também LIBERA o que o `.gitignore` bloqueia — resolvendo de uma vez "excluir a mais" e
  "liberar do gitignore". Ideia do usuário (260615-2). Substitui inflar o config para sempre.
- **GUI: selecionar tipo na hora (só-ext / exceto-ext).** Os filtros `only_ext`/`exclude_ext` já
  existem na core/CLI; falta expô-los na interface (ex.: campo "só estes tipos: md"). Pedido do usuário.
- **GUI: liberar item específico do `.gitignore`** sem desligar a leitura inteira (force-include /
  campo de exceções), além do toggle on/off que já existe. Conecta com o `.flatdropignore` (negação).
- **`_TREE.md`: tratamento de conteúdo ignorado.** Preocupação do usuário (260615-2): a árvore NÃO
  deve listar o interior de pastas ignoradas (node_modules etc.) — isso incharia o arquivo. Padrão
  profissional (tree --gitignore, repomix): pasta podada vira UMA linha colapsada
  ("node_modules/ [ignorada]"), sem recursão. O `_TREE` deve seguir isso.
```
**Âncora B (fim do arquivo, após a seção "## Descartadas"):** acrescentar nova seção:
```

## Feedback para o Kit

Registro do que ESTE projeto observou/mudou além do kit (material que volta para evoluí-lo).

- **Adotado o modo Claude Code (duas raias).** Chat autora docs/specs; Code implementa e commita.
  Criados os arquivos de arranque (`CLAUDE.md` raiz, `.claude/`). Ver DEC-012.
- **`meta/CLAUDE.md` → `meta/CEREBRO.md`.** O arquivo de comportamento foi renomeado pelo kit;
  confirmado como superconjunto exato do anterior (princípios 1-19, higiene, transferência
  idênticos; só ACRESCENTOU a nota de adaptar instruções, a seção de raias e o apêndice de
  arranque). Nada se perdeu — não houve merge a fazer.
- **Método "doc por spec" exercitado.** Specs em `meta/specs/` com âncora semântica; um canal por
  doc por ciclo. Funcionou para code (spec-0001) e doc (spec-0002).
```

---

## 3) ROADMAP.md — acrescentar itens à Fase 2

**Âncora (último item da Fase 2):**
```
- [ ] Aviso mais visível quando o pathspec está ausente (destaque na GUI).
```
**Ação:** logo APÓS essa linha (ainda dentro da Fase 2, antes de `## Fase 3`), acrescentar:
```
- [ ] Acrescentar tipos à allowlist de defaults (spec-0001: Godot, PDF/DOCX/XLSX/ODT/RTF/EPUB, +linguagens).
- [ ] **E2 —** Expor seleção de tipo na GUI (só-ext / exceto-ext) — filtros já existem na core.
- [ ] Liberar item específico do `.gitignore` na GUI (force-include), sem desligar a leitura inteira.
- [ ] **`.flatdropignore`** (ignore próprio, aninhado, com negação para liberar) + `.gitignore` aninhado — sai do stand-by; precisa de design.
```

---

## 4) STATUS.md — acrescentar à seção de pendências

**Âncora (item D em "Pendências imediatas"):**
```
- **D — Ignores de pasta editáveis** com núcleo imutável
```
**Ação:** acrescentar, logo ANTES de `## Riscos / pontos de atenção`, o bloco:
```

### Modo Claude Code + design em curso (2026-06-22)
- **Modo Claude Code adotado** (DEC-012): chat autora docs/specs, Code implementa. Arranque criado
  (`CLAUDE.md` raiz, `.claude/`). `meta/CEREBRO.md` substitui o antigo `meta/CLAUDE.md`.
- **spec-0001 (tipos de arquivo)** pendente de aplicação no Claude Code.
- **Em design (aguardando decisões):** seleção de tipo na GUI; liberação do `.gitignore` na GUI;
  gerador de `.bat` na GUI; `.flatdropignore` + `.gitignore` aninhado; `_TREE.md`.
- **Observação dos consoles (260615/260617):** antes do `CONCLUÍDO` aparecem erros do CMD
  (`'FlatDrop'`/`'m'`/`'Use'` não reconhecidos); o Python roda certo (multi-fonte OK, 86 arquivos).
  Causa provável no conteúdo do `.bat` — a confirmar com o arquivo real. Reforça o valor do gerador de `.bat`.
```
