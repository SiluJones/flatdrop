# spec-0004 — Meta da sessão 2026-06-24 (FIX-003 + estado + ideias)

**Tipo:** doc · **Alvos:** `meta/DECISIONS.md`, `meta/STATUS.md`, `meta/ROADMAP.md`, `meta/IDEAS.md`
**Autor:** chat · **Aplicador:** Claude Code · Sem build (só doc; a rede é o `git diff`).
**Regra:** achar cada âncora EXATAMENTE; se faltar, PARAR e reportar.

---

## 1) DECISIONS.md — acrescentar FIX-003 ao FINAL

**Âncora (fim do arquivo):**
```
tokens (`bytes/4`) não vale para binários, e binários grandes podem estourar o teto de 30 MB.
```
**Ação:** após essa linha, acrescentar:
```

---

## FIX-003 — .bat gerado falhava no CMD por caracteres não-ASCII
**Data:** 2026-06-24 · **Status:** corrigido

**Sintoma.** Ao rodar os `.bat` do cinzeiro, o CMD imprimia `'FlatDrop'`/`'Use'`/`'m'` "não
reconhecido" ANTES do `CONCLUÍDO`. O Python rodava certo (multi-fonte OK, 86 arquivos), mas a
saída vinha poluída.

**Causa raiz.** Os `.bat` tinham caracteres não-ASCII no corpo (travessão "—" e acentos nos
comentários `rem`) e `chcp 65001`. Trocar o code page para UTF-8 no meio do batch faz o CMD
**desalinhar a leitura por bytes** das linhas seguintes (os multibyte deslocam o offset): o `rem`
é lido cortado ("em"/"m") e o resto da linha vira comando. Confirmado com `cat -A`: as linhas que
erravam eram exatamente as que tinham "—"/"só". O Python rodava porque a linha `python ...` é
ASCII e o CMD re-sincronizava até ela.

**Solução.** Corpo do `.bat` em **ASCII puro** (sem "—", sem acentos nos comentários), mantendo
`chcp 65001` só para a SAÍDA do Python (impressa, não parseada pelo CMD). Os 5 `.bat` do cinzeiro
foram reentregues em ASCII (e sem `--add-ext`, redundante após a spec-0001). O **gerador de `.bat`**
(spec-0003) emite sempre ASCII e avisa se um caminho tiver acento (frágil no CMD).

**Lição.** `.bat` no CMD é sensível a encoding: trate o corpo como ASCII. Acento só na SAÍDA
(via `chcp`), nunca no texto que o CMD parseia. Geradores de `.bat` devem garantir isso.
```

---

## 2) STATUS.md — atualizar a subseção "Modo Claude Code + design em curso"

**Âncora A:**
```
- **spec-0001 (tipos de arquivo)** pendente de aplicação no Claude Code.
```
**Ação:** SUBSTITUIR essa linha por:
```
- **spec-0001 (tipos) e spec-0002 (docs) APLICADAS** e commitadas no Claude Code (26/26 testes).
- **spec-0003 (GUI: filtros de tipo + gerador de `.bat`)** autorada — pendente de aplicação.
- **FIX-003:** `.bat` falhava no CMD por não-ASCII — corrigido; os 5 `.bat` do cinzeiro reentregues em ASCII.
```

**Âncora B (o item "Em design", duas linhas):**
```
- **Em design (aguardando decisões):** seleção de tipo na GUI; liberação do `.gitignore` na GUI;
  gerador de `.bat` na GUI; `.flatdropignore` + `.gitignore` aninhado; `_TREE.md`.
```
**Ação:** SUBSTITUIR por:
```
- **Próximas specs (em design):** `.flatdropignore` (ignore próprio, aninhado, com negação para
  liberar — unifica "excluir a mais" + "liberar do gitignore") + `.gitignore` aninhado; depois `_TREE.md`.
```

---

## 3) ROADMAP.md — marcar o item de tipos como feito

**Âncora:**
```
- [ ] Acrescentar tipos à allowlist de defaults (spec-0001: Godot, PDF/DOCX/XLSX/ODT/RTF/EPUB, +linguagens).
```
**Ação:** SUBSTITUIR por:
```
- [x] Acrescentar tipos à allowlist de defaults (spec-0001 aplicada: Godot, PDF/DOCX/XLSX/ODT/RTF/EPUB, +linguagens).
```

---

## 4) IDEAS.md — acrescentar ao Feedback para o Kit

**Âncora (último item da seção "Feedback para o Kit"):**
```
- **Método "doc por spec" exercitado.** Specs em `meta/specs/` com âncora semântica; um canal por
```
**Ação:** acrescentar, ao FINAL do arquivo (após esse item e sua continuação), os itens:
```
- **`.bat` no CMD exige ASCII (FIX-003).** Encoding de `.bat` é armadilha: corpo ASCII, acento só na
  saída via `chcp`. O gerador de `.bat` passou a garantir isso.
- **Ideia (robustez):** tornar a SAÍDA da CLI ASCII-safe (`->` em vez de `↳`, `*` em vez de `•`) para
  dispensar `chcp 65001` nos `.bat` e evitar de vez problemas de code page. Baixo custo; avaliar.
```
