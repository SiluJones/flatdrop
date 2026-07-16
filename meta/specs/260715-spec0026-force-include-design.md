# spec0026 — DESIGN: force-include por caminho exato (resgatar arquivo barrado)

- **Tipo:** design (decisões + contrato + verificação). NÃO altera código. Gera **DEC-021**
  e prepara a implementação (spec0027).
- **Data:** 2026-07-15 · **Versão-alvo:** 0.7.0 (feature menor na core).
- **Motivação (caso real):** `webapp/static/vendor/htmx.min.js` não chega ao mount, e o
  `!` do `.flatdropignore` não resgata. Precisamos **liberar um arquivo específico** barrado
  por um ignore embutido, **sem** liberar todos os `*.min.js`.
- **Aplicação desta spec pelo Code:** apenas append de **DEC-021** ao fim de
  `meta/DECISIONS.md` (texto exato + âncora no §9). Sem código, sem testes.

---

## 1. Causa raiz (verificada, não suposta)

No `_scan`, os filtros de arquivo rodam nesta ordem:
1. **embutidos** — `low in cfg.file_ignores or low.endswith(cfg.suffix_ignores)` → rótulo
   `ignore_padrão`;
2. matcher gitignore/`.flatdropignore` (`_ignore_status`);
3. sensível; 4. tipo; 5. filtro de pasta.

`.min.js` está em `DEFAULT_SUFFIX_IGNORES`, então some no **passo 1**, **antes** do matcher
onde o `!` age (passo 2). Por isso `!htmx.min.js` nunca teve chance. Além disso, pastas como
`node_modules/` são **podadas** antes da varredura descer, então um arquivo lá dentro nem é
visitado. Conclusão: o `!` (que vive no matcher) não é o lever certo; precisamos de um
override que aja **acima de todos os cortes embutidos** e alcance **dentro de pastas podadas**.

## 2. Decisões de design

**2.1. Sintaxe: marcador `++` por linha no `.flatdropignore`.** Uma linha cujos dois
primeiros caracteres não-brancos são `++` declara um force-include; o resto (aparado) é um
**caminho relativo EXATO** (posix). Ex.:
```
++webapp/static/vendor/htmx.min.js
++vendor/htmx.min.js
```
Distinto do `!` (negação gitignore) de propósito — não sobrecarrega a semântica do DEC-017.
O FlatDrop **extrai** as linhas `++` antes de entregar o resto ao `pathspec` (senão o
`pathspec` leria `++foo` como "ignore um arquivo chamado `++foo`").

**2.2. Caminho EXATO, ancorado onde é declarado (não glob).** Nada de curinga. Um `++x` num
`.flatdropignore` aninhado em `sub/` resolve para `sub/x` (mesma ancoragem multi-segmento do
resto do arquivo). Motivos: (a) casa com a necessidade cirúrgica ("este arquivo, não todos");
(b) torna o resgate um `stat` direto do caminho — alcança dentro de pastas podadas **sem**
varrê-las; (c) elimina o risco de reinundar o mount. Quem quiser uma pasta inteira usa o
fluxo existente (`!dir/` + re-excluir por folha, DEC-017); force-include é precisão.

**2.3. Vence tudo, EXCETO "sensível".** Um force-include resgata o arquivo mesmo que ele
seja barrado por suffix/file-ignore, poda de pasta, matcher gitignore/`.flatdropignore` ou
**tipo** (o autor nomeou o arquivo exato — quer ele, qualquer que seja a extensão). A **única**
barreira que permanece é **sensível**: forçar um segredo (`.env`, `id_rsa`, chave) o
empurraria para o Projeto — proibido, coerente com "`!` não vence sensível". Um force-include
que aponte para sensível é **ignorado com aviso**.

**2.4. Independe do `pathspec`.** Como usa caminho exato (pertinência de conjunto, não
casamento de glob), o force-include funciona **mesmo sem `pathspec`** — ao contrário do resto
do `.flatdropignore`, que desliga sem ele.

**2.5. Sem mudança de GUI nesta feature.** O force-include é conteúdo do `.flatdropignore`
(o autor dita à mão ou via KCM; o `_TREE.md` mostra `arquivo [ignore_padrão]`, o autor
responde com `++arquivo`). O editor visual (Fase 2-D) poderá, no futuro, expor um **terceiro
estado** ("forçar mesmo assim") nos itens hoje barrados por ignore embutido — fora do escopo
desta spec.

## 3. Comportamento (VERIFICADO no sandbox contra a core real)

Árvore de teste: `keep.py`, `app.min.js`, `lib/vendor.min.js`,
`node_modules/dep/thing.min.js`, `webapp/static/vendor/htmx.min.js`, `id_rsa`, e um
`.flatdropignore` com `++` para cada um mais `++nao/existe.min.js`.

- **Baseline (hoje):** candidatos = `.flatdropignore`, `keep.py`; pulados = `app.min.js`,
  `lib/vendor.min.js`, `webapp/static/vendor/htmx.min.js` (`ignore_padrão`), `node_modules/`
  (pasta podada), `id_rsa` (`sensível`).
- **Com force-include:** entram `app.min.js`, `lib/vendor.min.js`,
  `webapp/static/vendor/htmx.min.js` **e** `node_modules/dep/thing.min.js` (dentro da pasta
  podada, via `stat` direto); `id_rsa` **segue bloqueado** (aviso "sensível");
  `nao/existe.min.js` vira **aviso** ("não encontrado"). Todas as asserts passaram.

## 4. Contrato de implementação (para a spec0027)

Tudo na core (camada de scan). **NÃO** toca `gui._build_cli_args`/`_generate_bat`/`_sources`
nem `cli.py` (o `.bat` só passa o `.flatdropignore` pelo scan normal).

- **Coleta:** um coletor (`_collect_force_includes(root, cfg) -> list[str]`, ou estender
  `_collect_ignore_lines` para devolver também as linhas `++`) que percorre a árvore com a
  MESMA poda de `_collect_ignore_lines`, lê as linhas `++` de cada `.flatdropignore`
  (respeitando a precedência de `FLATDROPIGNORE_NAMES`) e **rebaseia** cada caminho para
  relativo-à-raiz, ancorado-exato. Dedup preservando ordem.
- **Filtrar do matcher:** `_rebase_ignore` (ou o coletor de ignores) deve **pular** linhas
  `++` — elas NÃO podem virar padrão do `pathspec`. (Correção obrigatória.)
- **Resgate (pós-varredura, dentro do `_scan`, por fonte):** para cada `rel` forçado:
  - `full = source_root / rel`; se não for arquivo → `warnings += "force-include nao
    encontrado: {rel}"`; segue.
  - se `not cfg.include_sensitive and is_sensitive(full.name)` → `warnings += "force-include
    ignorado (sensivel): {rel}"`; segue.
  - se `rel` já é candidato → segue (dedup por rel).
  - senão → **remover** `(rel, motivo)` de `skipped_items` e decrementar `skipped[motivo]`
    se lá estava (para não contar duas vezes), e **acrescentar** `(full, PurePath(rel),
    size)` aos candidatos.
- **Multi-fonte:** o resgate roda por fonte, relativo à raiz da fonte; o dedup por caminho
  real de `make_plan_sources` cobre um arquivo forçado por mais de uma fonte.

## 5. Detalhes de relato (_TREE.md / _MANIFEST.md)

- Um arquivo forçado aparece como **copiado** (some dos pulados). Verificado que
  `app.min.js` etc. estavam em `skipped_items` — daí a remoção obrigatória acima.
- Um arquivo forçado de dentro de pasta podada (`node_modules/dep/thing.min.js`) entra como
  copiado; a linha colapsada `node_modules/ [ignorada…]` do tree **permanece** (a pasta
  segue podada em geral). Isso é aceitável; um polimento opcional (anotar "1 forçado") fica
  para depois — não nesta feature.

## 6. DEC-020

Force-include vive na core/scan, lido do `.flatdropignore` — que **GUI e CLI consomem
igual** (preserva a paridade do FIX-004). Não é estado de GUI; é config de projeto,
versionada. Não toca o gerador de `.bat`. **DEC-020-safe.** A spec0027 deve provar no
`git diff` que o caminho do `.bat` segue intocado.

## 7. O que testar (na spec0027)

Espelhar o sandbox do §3, mais bordas:
- resgate de arquivo barrado por suffix (`app.min.js`) e por tipo (extensão fora do
  allowlist) — ambos entram;
- resgate **dentro de pasta podada** (`node_modules/...`) — entra sem varrer a pasta;
- **sensível forçado** — permanece bloqueado, com aviso;
- **caminho inexistente** — aviso, sem quebrar;
- arquivo forçado **sai dos pulados** (não é contado duas vezes);
- `++` aninhado (rebase correto por subárvore);
- **sem `pathspec`**: force-include ainda funciona;
- Windows: comparar caminhos com `.as_posix()`.

## 8. Perguntas em aberto (decidir na spec0027)

- Force-include vence os filtros de execução `only_ext`/`only_folders`? Proposta: **sim**
  (vence tudo menos sensível — mental model simples: "eu forcei este arquivo"). Consequência:
  num `--only-ext md`, um `++x.min.js` ainda aparece. Se preferir que respeite o narrow do
  run, ajusta-se aqui.
- Ponto exato de inserção: dentro de `_scan` (tem tudo em escopo) vs em `make_plan_sources`
  (agregado). Proposta: `_scan`, por fonte.

## 9. Edit em `meta/` desta spec (aplicar EXATO)

Append ao **fim** de `meta/DECISIONS.md`. **Âncora semântica:** a última linha do bloco
**DEC-020**. Inserir DEPOIS dela (uma linha em branco antes):

```
## DEC-021 — Force-include por caminho exato (`++path` no `.flatdropignore`)
**Data:** 2026-07-15 · **Status:** aceita (design; implementação na spec0027)

**Contexto.** Arquivos barrados por um ignore embutido (ex.: `.min.js` em
`DEFAULT_SUFFIX_IGNORES`) não podem ser resgatados pelo `!` do `.flatdropignore`: o corte
embutido roda antes do matcher onde o `!` age, e pastas podadas nem são visitadas. Faltava
liberar UM arquivo específico sem liberar todos os de um tipo.

**Decisão.** Novo mecanismo **force-include**: linhas `++caminho/exato` no `.flatdropignore`
(marcador distinto do `!`, extraídas antes do `pathspec`). Caminho EXATO, ancorado onde é
declarado. O arquivo é resgatado por `stat` direto (alcança dentro de pastas podadas sem
varrê-las) e **vence todos os cortes embutidos** (suffix/file-ignore, poda de pasta, matcher,
tipo) — **exceto "sensível"**, que permanece barrado (com aviso), coerente com "`!` não vence
sensível". Caminho inexistente vira aviso. Independe do `pathspec` (é pertinência de conjunto,
não glob).

**Consequência.** Resolve o caso `htmx.min.js` e afins de forma cirúrgica, sem reinundar o
mount. Vive na core/scan, lido do `.flatdropignore` que GUI e CLI consomem igual (paridade
FIX-004 preservada); não toca o gerador de `.bat` (DEC-020-safe). O arquivo forçado sai dos
pulados do `_TREE.md`/`_MANIFEST.md`. O editor visual poderá, no futuro, expor um terceiro
estado ("forçar mesmo assim"). Lógica verificada no sandbox contra a core real antes de virar
spec.
```

## 10. Próxima spec

**spec0027 (implementação):** coletor de `++` + filtro do matcher + resgate pós-varredura no
`_scan`; testes do §7; bump 0.7.0; CHANGELOG [0.7.0]; STATUS; nota no GLOSSARY (termo
"force-include"). Âncoras exatas de `core.py` fecham lá.
