# spec0014 — `root_in_name`: ordem "stem primeiro, caminho invertido, raiz no fim"

**Tipo:** código (ajuste) · **Alvos:** `flatdrop/core.py`, `tests/test_core.py`
**Autor:** chat · **Aplicador:** Claude Code
**Depende de:** spec0013 aplicada (introduziu `root_in_name`/`root_prefix`).
**Origem:** validação da spec0013 no mount + nota 2144 do Code. O comportamento que
saiu (`page__meuapp__app__routes.tsx`, raiz no meio) é efeito colateral da
implementação; ninguém pediu por ele. O usuário quer a raiz **no fim**.

## Objetivo

Corrigir a ordem do sufixo quando `root_in_name=True` para: **stem na frente**,
**pastas do caminho invertidas** (interna → externa) e **nome da pasta-raiz por
último**. É o formato pedido pelo usuário ("modo real"):

| Arquivo (raiz `meuapp/`, `sep=__`) | Hoje (spec0013) | Alvo (spec0014) |
|---|---|---|
| `meuapp/README.md` | `README__meuapp.md` | `README__meuapp.md` |
| `meuapp/app/page.tsx` | `page__meuapp__app.tsx` | `page__app__meuapp.tsx` |
| `meuapp/app/routes/page.tsx` | `page__meuapp__app__routes.tsx` | `page__routes__app__meuapp.tsx` |

O stem continua na frente (essencial: é o que faz o Claude do Projeto achar o arquivo
por nome); só o **sufixo de caminho** passa a ler da pasta mais interna para a mais
externa, com a raiz fechando. Arquivos na raiz seguem virando `stem__raiz.ext`.

> Observação de projeto: isto muda a ordem das pastas **apenas** no caminho
> `root_in_name`. O modo `fullpath` SEM a flag permanece **idêntico** (`page__app__
> routes.tsx`, externa → interna). Sim, as duas ordens passam a coexistir — é
> aceitável porque a flag é um formato distinto e opt-in; unificar a ordem do
> fullpath comum seria mudança não pedida e quebraria nomes já em uso. Fora de escopo.

## Decisão de implementação (forma escolhida)

Há duas formas de obter a raiz no fim; a spec adota a **de menor diff e que NÃO toca
o `_compose`** (preservando o fullpath comum byte a byte):

- **NÃO** mexer em `_compose` (a costura segue costurando `dir_parts` na ordem dada).
- No `_plan_names`, quando há `root_prefix`, em vez de prefixar a raiz como a pasta
  mais externa (`(root_prefix, *dir_parts)`), montar `dir_parts` **já na ordem final
  desejada**: caminho invertido + raiz no fim →
  `(*reversed(dir_parts), root_prefix)`.

Assim, o `_compose` — que junta `dir_parts` na ordem em que chegam — produz
`routes__app__meuapp` sem qualquer alteração nele. A responsabilidade da ordem fica
concentrada no único ponto que já trata a raiz.

---

## EDIÇÃO 1 — core.py: inverter o caminho e pôr a raiz no fim, em `_plan_names`

**Âncora (o bloco atual que prefixa a raiz — deve bater exatamente; se não bater, PARE e reporte):**
```
        dir_parts = rel.parent.parts if rel.parent.as_posix() != "." else ()
        # spec0013: raiz entra como a pasta mais EXTERNA (prefixo), só no NOME —
        # o rel de exibição (manifesto/tree) permanece o real, sem a raiz.
        if root_prefix:
            dir_parts = (root_prefix, *dir_parts)
        meta.append((stem, ext, dir_parts))
```
**Ação:** SUBSTITUIR por:
```
        dir_parts = rel.parent.parts if rel.parent.as_posix() != "." else ()
        # spec0013/0014: com root_in_name, o sufixo de caminho é montado só no NOME
        # (o rel de exibição do manifesto/tree permanece o real, sem a raiz).
        # Ordem do sufixo (spec0014): pastas da mais INTERNA para a mais externa,
        # com o nome da pasta-raiz por ÚLTIMO. Ex.: app/routes/page.tsx (raiz meuapp)
        # -> stem "page" + "routes__app__meuapp". O _compose junta dir_parts na
        # ordem dada, então a inversão é feita aqui e o _compose fica intocado.
        if root_prefix:
            dir_parts = (*reversed(dir_parts), root_prefix)
        meta.append((stem, ext, dir_parts))
```

> Nada mais muda. `_compose`, o `floor`/`k` do fullpath, o `rel` de exibição, os
> avisos de fora-do-fullpath/multi-fonte e o truncamento com hash seguem como estão.
> Como o fullpath usa `k = len(dir_parts)`, todas as pastas (agora invertidas + raiz)
> entram — inclusive para arquivos da raiz, cujo `dir_parts` vira `(root_prefix,)`.

---

## EDIÇÃO 2 — tests/test_core.py: ajustar a asserção de ordem

A spec0013 deixou `test_root_in_name_fullpath_includes_root_folder` afirmando o
comportamento antigo (raiz logo após o stem). Atualizar para o formato-alvo.

**Ação:** o Code localiza `test_root_in_name_fullpath_includes_root_folder` e ajusta
a asserção para exigir a **nova ordem**: para um arquivo em subpasta, o nome plano
deve ser `stem + sep + <pastas invertidas> + sep + <root> + ext` — isto é, terminar
em `__<root_name><ext>` (raiz por último) E ter as pastas na ordem interna→externa.
Concretamente, para um arquivo tipo `app/routes/page.tsx` sob raiz `R`, o alvo é
`page__routes__app__R.tsx`. Para um arquivo na raiz, `stem__R.ext`.

Manter válidos e sem alteração os demais testes da spec0013:
`test_root_in_name_keeps_display_rel_real` (o `rel` continua real),
`test_root_in_name_ignored_outside_fullpath`,
`test_root_in_name_ignored_in_multisource`,
`test_root_in_name_preserves_uniqueness`,
`test_root_in_name_respects_max_name_len`. Se algum deles fixava a ordem antiga em
uma asserção literal, ajustar só a string esperada para a nova ordem — sem afrouxar
o que o teste garante.

Acrescentar (se ainda não coberto) uma asserção explícita de que a **raiz é o último
token** do sufixo (ex.: `assert target.rsplit(".", 1)[0].endswith(f"{sep}{root_name}")`),
para travar a ordem contra regressões.

Meta: suíte permanece em ~41 testes, todos verdes (`python -m pytest -q`). É ajuste
de asserção + 1 linha de código; não há teste novo de função, só correção de
expectativa.

---

## Sinais de teste / regressão a conferir

- **Fullpath sem a flag inalterado:** um teste do fullpath comum (se existir) deve
  seguir verde sem tocar — `page__app__routes.tsx` continua igual. Conferir que a
  Edição 1 só afeta o ramo `if root_prefix`.
- **Arquivo na raiz:** `README.md` → `README__<root>.md` (um só token de pasta, a raiz).
- **Profundidade 1:** `app/page.tsx` → `page__app__<root>.tsx` (raiz após a única pasta).
- **Unicidade:** dois `page.tsx` em `app/` e `app/routes/` seguem distintos
  (`page__app__R` vs `page__routes__app__R`).
- **Limite Windows:** raiz longa + caminho profundo ainda truncam com hash (o
  `_truncate_if_long` age sobre o nome final, depois da montagem — intocado).
- **Manifesto e `_TREE.md`:** coluna "Caminho original" e a árvore continuam
  mostrando o caminho REAL (o `rel` não mudou) — reconferir num smoke.

## Fora de escopo (vai para IDEAS)

- **Formato "caminho escrito"** (`meuapp__app__routes__page.tsx` — raiz na frente,
  ordem natural de leitura, stem no FIM). O usuário reconhece que **não** ajuda o
  Claude a achar por nome (o stem deixa de liderar), mas tem utilidade própria para
  empilhar projetos por raiz. Fica como **configuração futura** (um seletor de
  "formato do nome" com os dois estilos), não implementada agora. Capturar no IDEAS.
- Unificar a ordem das pastas do fullpath comum com a do `root_in_name` — não pedido;
  quebraria nomes já em uso.

## Após aplicar (Code)

1. `python -m pytest -q` — ~41 verdes.
2. `git diff` — só `core.py` (1 linha efetiva) e `tests/test_core.py` (asserções).
3. Commit:

```
git add flatdrop/core.py tests/test_core.py
git commit -m "fix(name): root_in_name poe a raiz no fim e inverte o caminho" -m "Com root_in_name, o sufixo passa a ser stem + pastas da mais interna para a externa + nome da pasta-raiz por ultimo (ex.: page__routes__app__meuapp.tsx), em vez da raiz logo apos o stem. Inversao feita no _plan_names (reversed(dir_parts) + root ao fim); _compose e o fullpath sem a flag ficam intocados. Testes da spec0013 ajustados para a nova ordem."
```
