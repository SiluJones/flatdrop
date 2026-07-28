# spec-0009 — Meta: DEC-014 (.flatdropignore) + STATUS/IDEAS/ROADMAP

**Tipo:** doc · **Alvos:** `meta/DECISIONS.md`, `meta/STATUS.md`, `meta/IDEAS.md`, `meta/ROADMAP.md`
**Autor:** chat · **Aplicador:** Claude Code · Sem build.
**Regra:** achar cada âncora EXATAMENTE; se faltar, PARAR e reportar.

---

## 1) DECISIONS.md — acrescentar DEC-014 ao FINAL

**Âncora (fim do arquivo):**
```
caminho de execução ao vivo no mesmo ciclo — senão a GUI e o `.bat` divergem.
```
**Ação:** após essa linha, acrescentar:
```

---

## DEC-014 — `.flatdropignore` (ignore próprio) + `.gitignore` aninhado
**Data:** 2026-06-24 · **Status:** aceita

**Contexto.** Faltava (a) respeitar `.gitignore` de subpastas (só o da raiz era lido) e (b) um jeito de
excluir o que vai para o git mas não para o Projeto, e de LIBERAR o que o `.gitignore` bloqueia — sem
desligar o `.gitignore` inteiro nem inflar o config.

**Decisão.** Um arquivo `.flatdropignore` por projeto, lido como o `.gitignore` e ANINHADO, com negação
`!` para re-incluir (até pasta inteira que seria podada). Tudo é unido num único matcher por "última regra
vence": todos os `.gitignore` (raso→fundo), depois todos os `.flatdropignore` (raso→fundo) — então o
**`.flatdropignore` tem sempre a palavra final** sobre o `.gitignore`, em qualquer profundidade. Padrões de
subpasta são reescritos para casar relativo à raiz. Três specs: `full` (decisão) + `gi`/`fd` (para atribuir
o motivo do skip e detectar liberação). A lógica foi VERIFICADA com o pathspec real antes de implementar.
O próprio `.flatdropignore` entra no ignore de arquivos (não vai para o upload).

**Alternativas.** Só campos avulsos na GUI (não cobre o aninhado nem "liberar do gitignore" de forma
declarativa); seguir só com `--no-gitignore` (tudo-ou-nada); inflar o config para sempre (não escala).

**Consequência.** Controle fino e declarativo por projeto, versionável, que também simplifica a config dos
`.bat`. Semântica deliberada: o `.flatdropignore` sobrepõe o `.gitignore` (≠ git puro, onde o mais fundo
vence) — bate com a intenção "`!` libera o que o gitignore bloqueia". Custo: uma passada extra na árvore
para coletar os arquivos de ignore (aceitável; fundível numa passada depois).
```

---

## 2) STATUS.md — substituir a subseção do modo code por um resumo limpo

**Âncora (a subseção inteira, do cabeçalho até a última linha antes de "## Riscos"):**
```
### Modo Claude Code + design em curso (2026-06-22)
- **Modo Claude Code adotado** (DEC-012): chat autora docs/specs, Code implementa. Arranque criado
  (`CLAUDE.md` raiz, `.claude/`). `meta/CEREBRO.md` substitui o antigo `meta/CLAUDE.md`.
- **spec-0001 (tipos) e spec-0002 (docs) APLICADAS** e commitadas no Claude Code (26/26 testes).
- **spec-0003 (GUI: filtros + gerador de `.bat`) e spec-0004 (docs) APLICADAS** (commit e56aa81; 26/26).
- **spec-0005 (GUI: multi-fonte ao vivo + Procurar na pasta-pai + abrir maximizada)** autorada — pendente.
- **FIX-004:** o toggle multi-fonte não afetava a execução ao vivo na GUI — corrigido na spec-0005.
- **FIX-003:** `.bat` falhava no CMD por não-ASCII — corrigido; os 5 `.bat` do cinzeiro reentregues em ASCII.
- **Próximas specs (em design):** `.flatdropignore` (ignore próprio, aninhado, com negação para
  liberar — unifica "excluir a mais" + "liberar do gitignore") + `.gitignore` aninhado; depois `_TREE.md`.
- **spec-0007 (GUI: modal de tipos + tela compacta + .bat pasta-pai) APLICADA** — commit f09de95; 26/26 testes.
```
**Ação:** SUBSTITUIR por:
```
### Modo Claude Code + features em curso
- **Modo Claude Code** (DEC-012): chat autora docs/specs, Code implementa. Arranque em `CLAUDE.md` raiz + `.claude/`.
- **Aplicado (v0.2.x, não lançado):** tipos de arquivo (DEC-013); GUI com filtros, gerador de `.bat`,
  multi-fonte ao vivo, modal de seleção de tipos e tela compacta (UI-1), abrir maximizada; launcher
  `flatdrop-ui.bat`. Bugs resolvidos: FIX-003 (`.bat` ASCII), FIX-004 (multi-fonte ao vivo).
- **Autorado, pendente de aplicar:** `.flatdropignore` + `.gitignore` aninhado (spec-0008, com 3 testes — DEC-014).
- **Próximas:** `_TREE.md` (pastas ignoradas em uma linha, sem recursão); UI-2 (polimento de layout) e
  UI-3 (presets/lembrar seleção); documentar `.flatdropignore` no README/CONTEXT; avaliar saída ASCII da
  CLI e um botão "Gerar atalho da UI" que crie o launcher sozinho.
```

---

## 3) IDEAS.md — capturar launcher/atalho (novo item no topo de "Ativas")

**Âncora (1º item de "## Ativas"):**
```
- **Redesign da UI por seleção (UX, em fases).** Trocar a digitação de tipos por um **modal pop-up**:
```
**Ação:** inserir IMEDIATAMENTE ANTES desse item:
```
- **Atalho da UI + UI-2/UI-3.** UI-1 (modal de tipos) feita. Entregue o launcher `flatdrop-ui.bat` (abre a
  UI sem console, copiável). Futuro: um botão **"Gerar atalho da UI"** na própria GUI, que cria o launcher
  calculando o caminho do `run.py` sozinho (talvez um `.lnk` em vez de `.bat`). Depois: UI-2 (polimento de
  layout) e UI-3 (presets "só docs"/"só código", lembrar última seleção).
```

## 4) IDEAS.md — registrar no "Feedback para o Kit" (ao FINAL do arquivo)

**Âncora (último item do arquivo):**
```
- **Ideia (robustez):** tornar a SAÍDA da CLI ASCII-safe (`->` em vez de `↳`, `*` em vez de `•`) para
  dispensar `chcp 65001` nos `.bat` e evitar de vez problemas de code page. Baixo custo; avaliar.
```
**Ação:** acrescentar, logo após esse item:
```
- **Verificar lógica sutil no sandbox antes de virar spec.** O `.flatdropignore` (negação + aninhamento)
  foi testado com o pathspec real ANTES de escrever a spec — pegou uma expectativa minha errada e deu
  confiança no algoritmo. Vale como prática para qualquer regra não-óbvia.
```

---

## 5) ROADMAP.md — marcar itens da Fase 2

**Âncora:**
```
- [ ] **E2 —** Expor seleção de tipo na GUI (só-ext / exceto-ext) — filtros já existem na core.
- [ ] Liberar item específico do `.gitignore` na GUI (force-include), sem desligar a leitura inteira.
- [ ] **`.flatdropignore`** (ignore próprio, aninhado, com negação para liberar) + `.gitignore` aninhado — sai do stand-by; precisa de design.
```
**Ação:** SUBSTITUIR por:
```
- [x] **E2 —** Seleção de tipo na GUI por modal (UI-1 aplicada).
- [x] Liberar do `.gitignore` — resolvido pelo `.flatdropignore` (negação `!`), spec-0008.
- [x] **`.flatdropignore`** (aninhado + negação) + `.gitignore` aninhado — spec-0008 autorada, com testes (DEC-014).
```

**Âncora (item UI/UX):**
```
- [ ] **UI/UX (em fases, design primeiro):** seleção de tipo por modal pop-up (checklist + busca);
      tela principal compacta; abrir maximizada (feito na spec-0005). Avaliar flag CLI `--ext-set`.
```
**Ação:** SUBSTITUIR por:
```
- [~] **UI/UX (em fases):** UI-1 (modal de tipos + tela compacta + maximizada) feita; UI-2 (polimento de
      layout) e UI-3 (presets/lembrar seleção) na fila. (Não precisou de `--ext-set`: o `.bat` reproduz a
      seleção com `--add-ext`/`--exclude-ext`.)
```
