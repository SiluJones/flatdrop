# spec-0006 — Meta: FIX-004 (multi-fonte ao vivo) + estado + ideias da UI

**Tipo:** doc · **Alvos:** `meta/DECISIONS.md`, `meta/STATUS.md`, `meta/IDEAS.md`, `meta/ROADMAP.md`
**Autor:** chat · **Aplicador:** Claude Code · Sem build (só doc).
**Regra:** achar cada âncora EXATAMENTE; se faltar, PARAR e reportar.

---

## 1) DECISIONS.md — acrescentar FIX-004 ao FINAL

**Âncora (fim do arquivo, fim do FIX-003):**
```
(via `chcp`), nunca no texto que o CMD parseia. Geradores de `.bat` devem garantir isso.
```
**Ação:** após essa linha, acrescentar:
```

---

## FIX-004 — toggle multi-fonte não afetava a execução ao vivo na GUI
**Data:** 2026-06-24 · **Status:** corrigido (spec-0005)

**Sintoma.** Com "Também incluir todos os .md a partir de:" MARCADO, o `.bat` gerado fazia
área + todos os `.md` (2 fontes, correto), mas "Pré-visualizar"/"Executar" na própria GUI
faziam só a coleta normal da raiz (1 fonte).

**Causa raiz.** Omissão da spec-0003: o toggle (`also_md_var`/`also_md_root_var`) foi ligado
apenas ao `_build_cli_args` (gerador de `.bat`). Os handlers `_on_preview`/`_on_execute`
continuavam chamando `core.make_plan(root, cfg)` (fonte única), sem montar as fontes.

**Solução.** Helper `_sources(primary)` que espelha o `_build_cli_args` (raiz primária + fonte
"todos os .md" via `replace(primary, only_ext={'md'}, ...)`); `_on_preview`/`_on_execute` passam
a usar `core.make_plan_sources(...)`. Assim a execução ao vivo e o `.bat` dão o MESMO resultado.

**Lição.** Ao adicionar uma opção que o gerador de `.bat` serializa, ligar a MESMA opção ao
caminho de execução ao vivo no mesmo ciclo — senão a GUI e o `.bat` divergem.
```

---

## 2) STATUS.md — atualizar a subseção do modo code / design

**Âncora A:**
```
- **spec-0003 (GUI: filtros de tipo + gerador de `.bat`)** autorada — pendente de aplicação.
```
**Ação:** SUBSTITUIR essa linha por:
```
- **spec-0003 (GUI: filtros + gerador de `.bat`) e spec-0004 (docs) APLICADAS** (commit e56aa81; 26/26).
- **spec-0005 (GUI: multi-fonte ao vivo + Procurar na pasta-pai + abrir maximizada)** autorada — pendente.
- **FIX-004:** o toggle multi-fonte não afetava a execução ao vivo na GUI — corrigido na spec-0005.
```

**Âncora B (o item "Observação dos consoles", 3 linhas):**
```
- **Observação dos consoles (260615/260617):** antes do `CONCLUÍDO` aparecem erros do CMD
  (`'FlatDrop'`/`'m'`/`'Use'` não reconhecidos); o Python roda certo (multi-fonte OK, 86 arquivos).
  Causa provável no conteúdo do `.bat` — a confirmar com o arquivo real. Reforça o valor do gerador de `.bat`.
```
**Ação:** SUBSTITUIR por:
```
- **Redesign da UI (UX) em design — aguardando aprovação do usuário:** filtros e "Extensões aceitas"
  por SELEÇÃO num modal pop-up (checklist categorizado + busca), tela principal mais compacta. Em fases;
  estrutura desenhada primeiro, sem código até aprovar.
```

---

## 3) IDEAS.md — acrescentar itens em "Ativas"

**Âncora (1º item de "## Ativas"):**
```
- **`_TREE.md` na saída.** Gerar (opcional, ligado por padrão) uma árvore
```
**Ação:** inserir IMEDIATAMENTE ANTES desse item (logo após o cabeçalho `## Ativas` e a linha em branco):
```
- **Redesign da UI por seleção (UX, em fases).** Trocar a digitação de tipos por um **modal pop-up**:
  botão "Tipos…" abre um diálogo (Toplevel modal) com checklist categorizado (Linguagens, Web, Config,
  Documentos, Godot…), busca, "marcar todos/limpar" por grupo, OK/Cancelar. Subsume "Extensões aceitas"
  e os filtros "Só estes/Exceto" numa só interface, deixando a tela principal compacta (só um resumo
  "Tipos: N selecionados"). Pedido do usuário (mais prático, intuitivo, bonito; melhor uso de espaço).
  Desenhar a estrutura primeiro e aprovar antes de implementar.
- **Flag CLI `--ext-set a,b,c` (allowlist exata).** Para o gerador de `.bat` reproduzir FIELMENTE uma
  allowlist customizada no modal (hoje só dá para somar via `--add-ext`; remoções não se expressam).
  Avaliar junto do redesign da UI.
```

---

## 4) ROADMAP.md — registrar a fase de UI/UX

**Âncora (último item da Fase 2):**
```
- [ ] **`.flatdropignore`** (ignore próprio, aninhado, com negação para liberar) + `.gitignore` aninhado — sai do stand-by; precisa de design.
```
**Ação:** inserir logo APÓS essa linha (ainda na Fase 2, antes de `## Fase 3`):
```
- [ ] **UI/UX (em fases, design primeiro):** seleção de tipo por modal pop-up (checklist + busca);
      tela principal compacta; abrir maximizada (feito na spec-0005). Avaliar flag CLI `--ext-set`.
```
