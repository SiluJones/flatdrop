# wo0041 — Trava por pasta: parte do CORE (+ testes)

**Data:** 2026-07-28 · **Autor:** chat · **Aplicar com:** `/apply-wo meta/workorders/260728-wo0041-trava-por-pasta-core.md`

> **Mexe em CODIGO** — rode `python -m pytest -q` ao fim.
> Esta e a **parte 1 de 2**. A parte 2 (coluna da trava na GUI) sai depois, em WO propria.
> Depois desta WO o comportamento visivel do editor NAO muda: a GUI ainda nao manda `locks`,
> e sem `locks` o gerador deriva o estado do que ja esta nos ignores. O que muda e o contrato.
> Desenho e medicoes: `meta/analises/260728-ANALISE-gerador-flatdropignore.md`.

## O que esta WO faz

Da ao gerador a informacao que faltava — **a trava de cada pasta**, que responde a uma unica
pergunta: *arquivo novo aqui entra ou nao entra?* — e **remove a heuristica de colapso**, que
adivinhava essa resposta a partir dos filhos.

Regra nova, deterministica (o core nao infere nada alem do default documentado):

| Pasta | Ja escondida pelo git? | Emite sobre a PASTA | Emite sobre os ARQUIVOS |
|---|---|---|---|
| 🔒 fechada | nao | `pasta/*` | `!pasta/y.md` por arquivo **marcado** |
| 🔒 fechada | sim | nada (ja esta fora) | `!pasta/y.md` por arquivo **marcado** |
| 🔓 aberta | nao | nada | `pasta/x.md` por arquivo **desmarcado** |
| 🔓 aberta | sim | `!pasta/*` | `pasta/x.md` por arquivo **desmarcado** |

**Sem colapso automatico.** Pasta aberta com os 20 filhos desmarcados escreve **20 linhas** — e
esta certo: o autor desmarcou arquivos, nao fechou a pasta. Quem fecha e a trava.

## Fora de escopo

- **GUI** (coluna da trava, estado herdado do git, marcar/desmarcar todos): parte 2.
- **Bump de versao e CHANGELOG:** ficam na parte 2, quando a feature fica visivel.
- `flatdrop/cli.py`, `gui._build_cli_args`, `gui._generate_bat`, `gui._sources`: **intocados**
  (DEC-020). Se algo parecer exigir isso, **PARE e reporte**.

---

## Edicao 1 — assinatura e docstring

**Ancora:**

```python
def build_flatdropignore(root, cfg: ScanConfig, wants: dict[str, bool],
                         existing_text: str | None = None) -> str:
    """Gera o texto do ``.flatdropignore`` (bloco gerenciado) a partir de ``wants``.

    ``wants``: ``{rel_arquivo: bool}`` — inclusao desejada por FOLHA; ausentes seguem o
    ESTADO EFETIVO atual (preserva o .flatdropignore existente no round-trip). Regras:
    - base de geracao = GIT PURO (uma exclusao so-do-flatdropignore e re-emitida);
    - LIBERAR pasta que o git esconde: ``!dir/`` + re-excluir os indesejados;
    - EXCLUIR do lado versionado: colapsa pasta CHEIA em ``dir/`` (a prova de arquivo
      novo); pasta parcial sai por folha (preserva o irmao mantido).
    Preserva linhas fora do bloco gerenciado (round-trip, DEC-016 opcao i).
    """
```

**Substituir por:**

```python
def build_flatdropignore(root, cfg: ScanConfig, wants: dict[str, bool],
                         existing_text: str | None = None,
                         locks: dict[str, bool] | None = None) -> str:
    """Gera o texto do ``.flatdropignore`` (bloco gerenciado) a partir de ``wants`` + ``locks``.

    Duas perguntas independentes, dois parametros (DEC-027):

    - ``wants``: ``{rel_arquivo: bool}`` — *este arquivo sobe?*, por FOLHA.
    - ``locks``: ``{rel_pasta: bool}`` — *arquivo novo aqui sobe?*, por PASTA.
      ``True`` = trava FECHADA (nao sobe), ``False`` = ABERTA (sobe).

    Ausentes nos dois casos seguem o ESTADO EFETIVO atual dos ignores — e o que preserva o
    round-trip do ``.flatdropignore`` existente (DEC-016). Uma pasta hoje ignorada volta como
    fechada; uma pasta hoje liberada por ``!`` volta como aberta.

    Emissao (base de geracao = GIT PURO; exclusao so-do-flatdropignore e re-emitida):

    ==========  ==================  ====================  =========================
    trava       escondida pelo git  linha da PASTA        linhas dos ARQUIVOS
    ==========  ==================  ====================  =========================
    fechada     nao                 ``pasta/*``           ``!pasta/y`` p/ marcado
    fechada     sim                 (nada)                ``!pasta/y`` p/ marcado
    aberta      nao                 (nada)                ``pasta/x`` p/ desmarcado
    aberta      sim                 ``!pasta/*``          ``pasta/x`` p/ desmarcado
    ==========  ==================  ====================  =========================

    NAO ha colapso automatico: pasta aberta com todos os filhos desmarcados sai por folha,
    uma linha cada. Quem torna uma pasta a prova de arquivo novo e a trava, nao o gesto nos
    filhos — era exatamente esse palpite que a DEC-027 removeu.

    Preserva linhas fora do bloco gerenciado (round-trip, DEC-016 opcao i).
    """
```

## Edicao 2 — constante da sonda

**Ancora:**

```python
FLATDROP_EDITOR_MARK_A = "# >>> flatdrop-editor"
```

**Substituir por:**

```python
# Nome de arquivo que nao existe, usado para PERGUNTAR ao ignore o que ele faria com um
# arquivo novo dentro de uma pasta. E como o gerador descobre o estado de uma trava que o
# chamador nao informou (wo0041 / DEC-027).
FLATDROP_PROBE = "__flatdrop_arquivo_novo__"
FLATDROP_EDITOR_MARK_A = "# >>> flatdrop-editor"
```

> Limite conhecido: a sonda nao tem extensao, entao um padrao manual do tipo `docs/*.log`
> devolveria "aberta" para `docs/`. E so o **padrao inicial** que a GUI pinta — a trava
> explicita do autor sempre vence. Nao vale complicar por isso.

## Edicao 3 — o miolo: trava no lugar da heuristica

**Ancora** (do `_walk_leaves` ate o fim do bloco de exclusao):

```python
    leaves, _gd, _b = _walk_leaves(root, cfg, _ignore_probes(root, cfg))
    all_dirs = {"/".join(l.split("/")[:i]) for l in leaves for i in range(1, len(l.split("/")))}
    gi_dirs = sorted(d for d in all_dirs if not git_in(d, True))  # pastas escondidas pelo GIT
    want_of = lambda rel: wants.get(rel, full_in(rel))            # default: efetivo atual

    def nearest_gi(rel: str):
        best = None
        for g in gi_dirs:
            if rel.startswith(g + "/") and (best is None or len(g) > len(best)):
                best = g
        return best

    # LIBERAR: pasta git-ignored com alguma folha desejada -> !dir/ + re-exclui indesejados
    liberate: list[str] = []
    reexclude: list[str] = []
    freed: set[str] = set()
    for g in gi_dirs:
        under = [l for l in leaves if l.startswith(g + "/")]
        if any(want_of(l) for l in under) and not any(g.startswith(o + "/") for o in freed):
            liberate.append(f"!{g}/")
            freed.add(g)
            for l in under:
                if not want_of(l):
                    reexclude.append(l)

    # EXCLUIR: base git puro; colapsa pasta CHEIA (a prova de arquivo novo)
    excluded = {l for l in leaves if git_in(l) and not want_of(l) and nearest_gi(l) is None}
    cand = {"/".join(l.split("/")[:i]) for l in excluded for i in range(1, len(l.split("/")))}

    def fully_excluded(d: str) -> bool:
        under = [l for l in leaves if l.startswith(d + "/")]
        return bool(under) and all(l in excluded for l in under)

    collapsible = {d for d in cand if fully_excluded(d)}
    maximal = {d for d in collapsible if not any(d != o and d.startswith(o + "/") for o in collapsible)}
    exclude = [f"{d}/" for d in sorted(maximal)]
    exclude += [l for l in sorted(excluded) if not any(l.startswith(d + "/") for d in maximal)]
```

**Substituir por:**

```python
    locks = locks or {}
    leaves, _gd, _b = _walk_leaves(root, cfg, _ignore_probes(root, cfg))
    all_dirs = {"/".join(l.split("/")[:i]) for l in leaves for i in range(1, len(l.split("/")))}
    parent_of = lambda rel: rel.rsplit("/", 1)[0] if "/" in rel else ""

    # Trava ausente: pergunta ao proprio ignore o que ele faria com um arquivo INEXISTENTE.
    # E a definicao literal da trava ("arquivo novo aqui entra?"), e e a unica sonda que
    # funciona: "pasta/*" de proposito NAO casa a pasta como diretorio, entao sondar
    # full_in(d, True) daria "aberta" para toda pasta que o proprio editor fechou.
    closed_of = lambda d: locks.get(d, not full_in(f"{d}/{FLATDROP_PROBE}"))

    def want_of(rel: str) -> bool:
        """Este arquivo sobe? Explicito vence; senao segue a trava recem-mexida; senao,
        o estado efetivo de hoje (e o que preserva o round-trip)."""
        if rel in wants:
            return wants[rel]
        d = parent_of(rel)
        if d and d in locks:      # trava mexida NESTA chamada manda no que nao foi dito
            return not locks[d]
        return full_in(rel)

    folder_lines: list[str] = []
    file_lines: list[str] = []

    # --- linhas da PASTA. Uma por pasta que contem arquivo direto: "pasta/*" NAO alcanca
    # "pasta/sub/arquivo" (medido), so a subpasta como diretorio. Enquanto ninguem resgata
    # nada la dentro, a poda basta; assim que um "!" desce, faltaria a linha do nivel de
    # baixo. Emitir por nivel custa uma linha e fecha o buraco.
    dirs_com_arquivo = {parent_of(l) for l in leaves if parent_of(l)}
    for d in sorted(all_dirs):
        fechada, git_fora = closed_of(d), not git_in(d, True)
        if fechada and not git_fora and d in dirs_com_arquivo:
            folder_lines.append(f"{d}/*")
        elif not fechada and git_fora:
            folder_lines.append(f"!{d}/*")

    # --- linhas dos ARQUIVOS. A pasta MAIS PROXIMA manda: dentro de fechada so aparece o
    # resgate do que foi marcado; dentro de aberta so aparece a exclusao do desmarcado.
    for l in sorted(leaves):
        d = parent_of(l)
        if not d:                                   # raiz nao tem trava: regra antiga
            if git_in(l) and not want_of(l):
                file_lines.append(l)
            continue
        if closed_of(d):
            if want_of(l):
                file_lines.append(f"!{l}")
        else:
            if not want_of(l):
                file_lines.append(l)
```

## Edicao 4 — a ordem do bloco

**Ancora:**

```python
    block = liberate + sorted(set(reexclude)) + exclude
```

**Substituir por:**

```python
    # PASTA antes de ARQUIVO, e raso antes de fundo: vale a ULTIMA regra que casa, entao o
    # resgate precisa vir depois da exclusao que o pegaria (e vice-versa).
    block = folder_lines + file_lines
```

## Edicao 5 — `meta/DECISIONS.md`

Acrescente ao FIM:

```
## DEC-027 — A trava da pasta decide o futuro; o checkbox decide o presente
**Data:** 2026-07-28 · **Status:** aceita (altera o contrato da DEC-016)

**Contexto.** O editor de `.flatdropignore` tinha **um** controle (o checkbox tri-estado)
tentando responder **duas** perguntas independentes: *este arquivo sobe?* e *o que aparecer
aqui depois sobe?*. Pior: o checkbox da pasta nem é uma escolha — `folder_effective_state`
o **deriva** dos filhos, então "indeterminado" significa "os filhos estão misturados", nunca
"o autor decidiu algo sobre a pasta". A intenção da pasta não estava perdida no caminho:
**nunca existiu**. O gerador então adivinhava — colapsava a pasta em `pasta/` quando todos os
filhos estavam desmarcados — e o palpite errava nos dois sentidos: arquivo novo entrava numa
pasta parcialmente curada, e uma pasta esvaziada à mão virava exclusão dura sem ninguém pedir.

**Decisão.** Separar os dois controles.

- **Checkbox de arquivo:** *este arquivo sobe?* — como sempre foi.
- **Checkbox de pasta:** atalho para marcar/desmarcar todos os filhos. **Não influencia a
  trava** e continua sendo um agregado.
- **Trava da pasta (controle novo):** *arquivo novo aqui sobe?* — 🔓 aberta (padrão) ou
  🔒 fechada. É a única informação nova, e não é derivada de nada.

No core, `build_flatdropignore` ganha `locks: {rel_pasta: bool}` ao lado de `wants`, e a
heurística de colapso é **removida**. Trava ausente = estado efetivo de hoje, o que preserva o
round-trip sem palpite.

**Consequência (quebra de contrato assumida).** Pasta aberta com todos os filhos desmarcados
passa a escrever **uma linha por arquivo**, não `pasta/`. É o que o autor pediu explicitamente:
desmarcar 20 arquivos é desmarcar 20 arquivos; fechar a pasta é outro gesto. O teste
`test_editor_collapse_blocks_new_files` afirmava o contrário e foi reescrito — o comportamento
que ele protegia agora se obtém fechando a trava.

**Medido antes de decidir** (0.12.0, varredura real): `pasta/*` + `!pasta/x.md` deixa entrar só
`x.md` **e mantém arquivo novo fora**; `!pasta/*` abre pasta escondida pelo git e deixa arquivo
novo entrar; `!pasta/` e `!pasta/*` se comportam igual (padronizado em `/*`, DEC-025). E a
armadilha do aninhamento: `pasta/*` **não** casa `pasta/sub/arquivo.md` — só `pasta/sub/` como
diretório. Enquanto ninguém resgata nada lá dentro, a poda resolve; assim que um `!` desce, a
subpasta precisa da linha dela. Por isso o gerador emite uma linha por nível fechado.
```

## Edicao 6 — testes (`tests/test_core.py`)

Os 5 testes do editor passam a declarar tambem a trava. **Reescreva-os** (nao acrescente ao
lado — o contrato mudou):

1. `test_editor_exclude_keeps_sibling` — pasta ABERTA, um filho desmarcado.
   Espera **so** `docs/b.md`; nada sobre a pasta; o irmao continua fora do bloco.
2. `test_editor_collapse_blocks_new_files` → **renomeie** para
   `test_editor_lock_closed_writes_star`: trava FECHADA em `logs/`.
   Espera `logs/*` e **nenhuma** linha por arquivo.
3. **NOVO** `test_editor_open_folder_all_unchecked_lists_each` — pasta ABERTA, TODOS os filhos
   desmarcados. Espera **uma linha por arquivo** e **nenhum** `logs/*`. (E a quebra de contrato
   da DEC-027; e o caso que o autor pediu por escrito.)
4. `test_editor_liberate_only_one` — pasta escondida pelo `.gitignore`, trava ABERTA, um filho
   marcado. Espera `!legacy/*` + a exclusao dos outros filhos por nome.
5. `test_editor_roundtrip_preserves_manual` — inalterado no proposito: linhas fora do bloco
   gerenciado sobrevivem. Passe `locks` vazio.
6. `test_editor_roundtrip_preserves_folder_exclusion` — chame duas vezes; a pasta fechada na
   primeira volta fechada na segunda **sem** `locks` (o default vem do estado efetivo). E o
   teste do round-trip sem palpite.
7. **NOVO** `test_editor_nested_closed_emits_line_per_level` — `pasta/` e `pasta/sub/` fechadas,
   um arquivo resgatado em `pasta/sub/`. Espera `pasta/*` **e** `pasta/sub/*` no bloco, e que
   `pasta/sub/outro.md` NAO seja copiado num `make_plan` com esse `.flatdropignore`.
   (E a armadilha medida na DEC-027 — sem a linha do nivel de baixo, o irmao vaza.)

Se outro teste quebrar, **ajuste o teste e registre no relatorio** — o contrato mudou de
proposito. Nao mude o codigo para caber no teste velho.

## Checklist de fecho

- [ ] `python -m pytest -q` verde (73 era o numero antes; diga o final).
- [ ] `git diff` conferido: 4 edicoes em `core.py`, 1 em `DECISIONS.md`, os testes. Nada mais.
- [ ] `cli.py` / `_build_cli_args` / `_generate_bat` / `_sources` **intocados**.
- [ ] Sem bump de versao e sem CHANGELOG — ficam na parte 2 (GUI).
- [ ] Commit sem acento, Conventional Commits.
- [ ] **Relatorio**: o que fez, desvios, arquivos tocados, suite, commit.

---

## Validado em sandbox antes de virar WO

As 4 edicoes de codigo foram aplicadas numa copia de `core.py` (0.12.0) e exercitadas com
`build_flatdropignore` + `make_plan` reais:

| Caso | Bloco gerado | Confere? |
|---|---|---|
| pasta aberta, 1 de 20 desmarcado | `docs/d05.md` | uma linha, so |
| pasta aberta, **20 desmarcados** | 20 linhas, **sem** `docs/*` | e o adendo do autor |
| trava fechada, 1 marcado | `docs/*` + `!docs/d05.md` | 2 linhas para 20 arquivos |
| git esconde a pasta, trava aberta | `!legacy/*` | abre e deixa novo entrar |
| aninhado, resgate no fundo | `pasta/*` + `pasta/sub/*` + `!pasta/sub/deep.md` | `outro.md` fica fora, **e um `NOVO.md` criado depois tambem** |
| round-trip nos 3 modos (fechada / aberta / liberada do git) | segunda passada sem `locks` devolve texto **identico** | estavel |

Duas armadilhas foram pegas nesta rodada e ja estao corrigidas no texto acima:

1. **Default dentro de pasta fechada.** Com `want_of` caindo no estado efetivo, fechar uma pasta
   pela primeira vez resgatava os 20 arquivos (`docs/*` + 20 negacoes) — a trava nao fechava
   nada. Dai o `want_of` seguir a trava quando ela foi mexida na chamada.
2. **Sonda da trava.** `full_in(d, True)` parecia o jeito obvio de descobrir se a pasta esta
   fechada, mas `pasta/*` **nao casa** `pasta/` — entao toda pasta fechada pelo proprio editor
   voltava como aberta na segunda passada, e o round-trip se desfazia. Dai a sonda por arquivo
   inexistente.
