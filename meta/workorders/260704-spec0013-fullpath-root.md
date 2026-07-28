# spec0013 — modo fullpath incluindo o nome da pasta-raiz (`fullpath-root`)

**Tipo:** código · **Alvos:** `flatdrop/core.py`, `flatdrop/cli.py`, `flatdrop/gui.py`, `tests/test_core.py`
**Autor:** chat · **Aplicador:** Claude Code
**Origem:** ideia do usuário (nota `.txt` de 2026-07-03). Ver IDEAS ("fullpath com pasta-raiz").

## Objetivo

Hoje o modo `fullpath` costura no nome o caminho **abaixo** da raiz: `page.tsx` em
`app/routes` vira `page__routes__app.tsx`… não — vira `page__app__routes.tsx`
(pastas da mais interna para a externa, a raiz NÃO entra). Consequência: arquivos
que estão **na própria raiz** ficam sem prefixo, e o nome da pasta-raiz do projeto
nunca aparece. A ideia é uma opção que **inclui o nome da pasta-raiz** como a pasta
mais externa do sufixo — assim todo arquivo (inclusive os da raiz) carrega o nome
do projeto, útil quando se junta o achatado de vários projetos numa mesma pilha
mental ou pasta de Downloads.

Exemplo (raiz = `meuapp/`, `sep=__`):
- Arquivo `meuapp/README.md` → hoje `README.md`; com a opção → `README__meuapp.md`.
- Arquivo `meuapp/app/routes/page.tsx` → hoje `page__routes__app.tsx`; com a opção →
  `page__routes__app__meuapp.tsx`.

## Decisões de projeto

1. **É um refinamento do `fullpath`, não um modo novo.** Um booleano
   `root_in_name: bool = False` no `ScanConfig`. Só tem efeito quando
   `mode == "fullpath"`; nos modos `collisions`/`all` é ignorado (documentar).
   Motivo: incluir a raiz só faz sentido quando já se está costurando o caminho
   inteiro; nos outros modos contradiz o propósito (mínimo diff / só desempate).
2. **Fonte única apenas.** A opção injeta `plan.root.name` (o nome da pasta-raiz)
   como a pasta mais externa. Em **multi-fonte** o `rel` já é relativo à raiz COMUM
   e normalmente já começa com o nome de cada pasta-fonte — incluir "a raiz" de novo
   seria redundante/ambíguo. Então: **se houver mais de uma fonte, a opção é
   ignorada** e um aviso é emitido (o usuário fica sabendo por que não valeu).
   Multi-raiz de verdade é outra tarefa (IDEAS: "multi-raiz na GUI").
3. **Respeita o limite de nome do Windows (preocupação do usuário).** A raiz vira só
   mais uma parte do sufixo ANTES do `_truncate_if_long`, que já corta o meio e cola
   um hash estável quando o nome passa de `MAX_NAME_LEN` (200). Ou seja, o
   truncamento com hash continua sendo a rede de segurança — a opção não fura o
   limite; nomes muito longos são truncados como já acontece hoje. Documentar isso
   no help/tooltip, sem lógica nova de limite.
4. **Determinismo e unicidade preservados.** A injeção é uniforme (a MESMA raiz para
   todos os arquivos da fonte), então não altera o desempate por grupo; o passe final
   de contador continua cobrindo empates residuais.

## Onde ancora (mecânica atual, confirmada no core)

- `_plan_names` calcula, por modo, um `floor` de `k` (quantas pastas entram):
  `fullpath` usa `floor = len(dir_parts)` (todas as pastas abaixo da raiz).
- `_compose(stem, dir_parts, k, sep, ext)` monta `stem + sep + join(pastas) + ext`,
  pegando as `k` pastas mais internas: `dir_parts[-k:]`.
- `rel` é relativo à raiz (fonte única) ou à raiz comum (multi-fonte); a pasta-raiz
  **não** está em `dir_parts`.

A forma mínima de incluir a raiz: quando a opção está ligada (e é fonte única +
fullpath), **prefixar `plan.root.name` em `dir_parts`** de cada candidato ANTES do
planejamento de nomes — assim ela passa a ser a pasta mais externa e o `k=len` do
fullpath a inclui naturalmente, inclusive para arquivos da raiz (que passam a ter
`dir_parts=(root_name,)`). Não é preciso mexer no `_compose`.

---

## EDIÇÃO 1 — core.py: flag `root_in_name` no ScanConfig

**Âncora (o comentário e a linha do `mode`):**
```
    # "fullpath"    -> todo arquivo carrega o caminho completo desde a raiz
    mode: str = "collisions"
```
**Ação:** SUBSTITUIR por:
```
    # "fullpath"    -> todo arquivo carrega o caminho completo desde a raiz
    mode: str = "collisions"
    # Só no modo "fullpath" e em FONTE ÚNICA: inclui o nome da pasta-raiz como a
    # pasta mais externa do sufixo (arquivos da raiz passam a levar o nome do
    # projeto). Ignorado nos outros modos e em multi-fonte (spec0013). O limite de
    # nome (MAX_NAME_LEN) segue protegido pelo truncamento com hash já existente.
    root_in_name: bool = False
```

## EDIÇÃO 2 — core.py: `make_plan_sources` injeta a raiz quando aplicável

A injeção acontece no ponto onde `all_candidates` já está montado e ANTES de
`_plan_names`. Precisa: (a) valer só em fonte única + fullpath + flag ligada;
(b) em multi-fonte com a flag ligada, emitir aviso e não injetar.

**Âncora:**
```
    planned, collisions, name_warnings = _plan_names(all_candidates, primary_cfg)
    warnings += name_warnings
```
**Ação:** SUBSTITUIR por:
```
    # spec0013: incluir o nome da pasta-raiz no sufixo (só fullpath + fonte única).
    if primary_cfg.root_in_name:
        if primary_cfg.mode != "fullpath":
            warnings.append(
                "Opção 'incluir pasta-raiz no nome' só vale no modo fullpath — "
                "ignorada neste modo."
            )
        elif len(sources) > 1:
            warnings.append(
                "Opção 'incluir pasta-raiz no nome' foi ignorada: com múltiplas "
                "fontes o caminho já parte da raiz comum. (Multi-raiz é tarefa futura.)"
            )
        else:
            root_name = common.name
            if root_name:
                # Prefixa a raiz como a pasta mais externa: vira parte de dir_parts,
                # e o floor=len(dir_parts) do fullpath a inclui em todos, inclusive
                # nos arquivos da raiz (que passam a ter dir_parts=(root_name,)).
                all_candidates = [
                    (src, PurePath(f"{root_name}/{rel.as_posix()}"), size)
                    for src, rel, size in all_candidates
                ]

    planned, collisions, name_warnings = _plan_names(all_candidates, primary_cfg)
    warnings += name_warnings
```

> **Atenção ao efeito colateral no `rel` exibido:** os `PlannedFile.rel` derivados de
> `all_candidates` passariam a começar com `root_name/`, o que mudaria o `_MANIFEST.md`
> (coluna "Caminho original") e o `_TREE.md`. Isso é INDESEJADO — a coluna de origem
> e a árvore devem refletir o caminho REAL, não o nome inflado. Portanto a injeção
> NÃO pode reusar o mesmo `rel` que alimenta o manifesto/tree.

**Correção obrigatória de design (o Code DEVE seguir):** a raiz entra apenas no
**nome planejado**, não no `rel` de exibição. Duas formas aceitáveis — o Code escolhe
a de menor diff:

- **(A) preferida)** Não prefixar `rel`. Em vez disso, passar a raiz a `_plan_names`
  como parâmetro opcional (`root_prefix: str | None`) que injeta a parte só no
  cálculo de `dir_parts`/`floor`, deixando `PlannedFile.rel` intacto. Ver Edição 2-bis.
- (B) Prefixar `rel` para o cálculo, mas restaurar o `rel` original em cada
  `PlannedFile` após `_plan_names` (guardar o rel real e reatribuir). Mais frágil.

## EDIÇÃO 2-bis — core.py: `_plan_names` aceita `root_prefix` (forma A, preferida)

Substitui a Edição 2 pela via limpa: `make_plan_sources` **não** mexe em
`all_candidates`; passa `root_prefix=common.name` a `_plan_names`, que injeta a parte
só internamente.

**Âncora (assinatura de `_plan_names`):**
```
def _plan_names(
    candidates: list[tuple[Path, PurePath, int]], cfg: ScanConfig
) -> tuple[list[PlannedFile], int, list[str]]:
```
**Ação:** SUBSTITUIR por:
```
def _plan_names(
    candidates: list[tuple[Path, PurePath, int]],
    cfg: ScanConfig,
    root_prefix: str | None = None,
) -> tuple[list[PlannedFile], int, list[str]]:
```

**Âncora (o cálculo de `dir_parts` por candidato):**
```
    for src, rel, _size in candidates:
        stem, ext = split_name(rel.name)
        dir_parts = rel.parent.parts if rel.parent.as_posix() != "." else ()
        meta.append((stem, ext, dir_parts))
```
**Ação:** SUBSTITUIR por:
```
    for src, rel, _size in candidates:
        stem, ext = split_name(rel.name)
        dir_parts = rel.parent.parts if rel.parent.as_posix() != "." else ()
        # spec0013: raiz entra como a pasta mais EXTERNA (prefixo), só no NOME —
        # o rel de exibição (manifesto/tree) permanece o real, sem a raiz.
        if root_prefix:
            dir_parts = (root_prefix, *dir_parts)
        meta.append((stem, ext, dir_parts))
```

> Como `PlannedFile.rel` é construído a partir do `rel` original (não de `dir_parts`),
> o manifesto e o `_TREE.md` seguem mostrando o caminho real. Só o nome plano ganha a
> raiz. O Code confirma que a montagem de `PlannedFile` no fim de `_plan_names` usa o
> `rel` de `candidates[i]`, não `meta`/`dir_parts`.

**Âncora (a chamada em `make_plan_sources`):**
```
    planned, collisions, name_warnings = _plan_names(all_candidates, primary_cfg)
    warnings += name_warnings
```
**Ação:** SUBSTITUIR por:
```
    # spec0013: incluir o nome da pasta-raiz no sufixo (só fullpath + fonte única).
    root_prefix: str | None = None
    if primary_cfg.root_in_name:
        if primary_cfg.mode != "fullpath":
            warnings.append(
                "Opção 'incluir pasta-raiz no nome' só vale no modo fullpath — "
                "ignorada neste modo."
            )
        elif len(sources) > 1:
            warnings.append(
                "Opção 'incluir pasta-raiz no nome' foi ignorada: com múltiplas "
                "fontes o caminho já parte da raiz comum. (Multi-raiz é tarefa futura.)"
            )
        elif common.name:
            root_prefix = common.name

    planned, collisions, name_warnings = _plan_names(
        all_candidates, primary_cfg, root_prefix=root_prefix
    )
    warnings += name_warnings
```

> **O Code aplica a forma A (Edição 2-bis) e IGNORA a Edição 2** (mantida acima só
> para registrar o raciocínio do porquê não prefixar o `rel`). Se algo na âncora de
> 2-bis não bater exatamente, PARE e reporte.

## EDIÇÃO 3 — cli.py: flag `--root-in-name`

**Âncora:** o Code localiza o grupo de flags de nomeação (onde estão `--mode`/`--sep`)
e adiciona, logo após `--sep`:
```
    p.add_argument("--root-in-name", action="store_true", dest="root_in_name",
                   help="no modo fullpath, inclui o nome da pasta-raiz no nome de cada arquivo")
```
E no `ScanConfig(...)` de `_primary_cfg`, junto aos demais campos de nomeação:
```
        root_in_name=args.root_in_name,
```

## EDIÇÃO 4 — gui.py: checkbox condicional ao modo fullpath

**Âncora:** onde as BooleanVar de opções são criadas (perto de `self.tree_var`):
```
        self.tree_var = tk.BooleanVar(value=False)  # _TREE.md desligado por padrao (spec0011)
```
**Ação:** SUBSTITUIR por:
```
        self.tree_var = tk.BooleanVar(value=False)  # _TREE.md desligado por padrao (spec0011)
        self.root_in_name_var = tk.BooleanVar(value=False)  # incluir pasta-raiz (spec0013)
```

**Checkbox:** o Code adiciona um `ttk.Checkbutton` perto do seletor de modo, com texto
`"Incluir o nome da pasta-raiz (só no modo fullpath)"`, ligado a `self.root_in_name_var`.
Se houver um callback de troca de modo, habilitar/desabilitar a checkbox conforme
`mode == "fullpath"` (opcional; se não houver, deixar sempre habilitada — a core já
ignora fora do fullpath e avisa). Não reestruturar o layout além de inserir a linha.

**No `_gather_cfg`** (junto a `write_tree=`):
```
            root_in_name=self.root_in_name_var.get(),
```

**No `_build_cli_args`** (FIX-004 — serializar para o `.bat`), após o bloco do `--tree`:
```
        if self.root_in_name_var.get():
            args += ["--root-in-name"]
```

---

## EDIÇÃO 5 — tests/test_core.py: cobertura

Casos (o Code posiciona junto aos testes de `_plan_names`/modos):

1. **Fullpath + flag: raiz no nome.** Origem com `README.md` na raiz e um arquivo
   em subpasta; `mode="fullpath"`, `root_in_name=True` → ambos os nomes planos
   terminam com `__<root_name>` (o nome da pasta-raiz), inclusive o da raiz.
2. **rel/manifesto intactos.** No mesmo plano, `PlannedFile.rel` NÃO começa com o
   nome da raiz (o caminho de origem exibido continua real) — protege manifesto/tree.
3. **Ignorado fora do fullpath.** `mode="collisions"`, `root_in_name=True` → nomes
   idênticos ao caso sem a flag, e um aviso é emitido em `plan.warnings`.
4. **Ignorado em multi-fonte.** Duas fontes, `mode="fullpath"`, `root_in_name=True`
   → a raiz NÃO é injetada (nomes como sem a flag) e há aviso explicando o porquê.
5. **Unicidade preservada.** Dois arquivos de mesmo nome em subpastas distintas, com
   a flag → continuam distintos (o desempate por grupo não quebra com o prefixo).
6. **Nome longo trunca.** Raiz de nome grande + caminho profundo que ultrapasse
   `MAX_NAME_LEN` → o nome final respeita o limite (via `_truncate_if_long`, com o
   hash), confirmando que a opção não fura o teto do Windows.

Meta: **35 → ~41 testes**, verdes com `python -m pytest -q`.

## Sinais de teste / regressão a conferir

- Modos existentes (`collisions`/`all`/`fullpath` sem a flag) **inalterados** —
  `root_prefix=None` é o caminho default e não toca `dir_parts`.
- Smoke GUI (Windows): marcar modo fullpath + checkbox, Executar, conferir que os
  nomes levam a raiz; gerar `.bat` e confirmar `--root-in-name` no corpo; conferir
  que o `_MANIFEST.md` e o `_TREE.md` seguem mostrando o caminho REAL (sem a raiz
  inflada na coluna de origem).
- Caso de borda: raiz num drive (`C:\`) cujo `.name` é vazio — o `elif common.name`
  já protege (não injeta). Raiz com `.` no nome — o `_sanitize` do `_compose` cuida.

## Fora de escopo (IDEAS)

- **Multi-raiz na GUI** (selecionar N pastas, prefixar cada uma com sua raiz) — é a
  ideia irmã da nota `.txt`; tarefa própria, maior, mexe na UI de seleção.
- Seletor de posição da raiz (externa vs interna) — YAGNI; externa é o esperado.

## Após aplicar (Code)

1. `python -m pytest -q` — ~41 verdes.
2. `git diff` — só `core.py`, `cli.py`, `gui.py`, `tests/test_core.py`; nada fora das âncoras.
3. Commit:

```
git add flatdrop/core.py flatdrop/cli.py flatdrop/gui.py tests/test_core.py
git commit -m "feat(name): opcao de incluir a pasta-raiz no nome (modo fullpath)" -m "Nova flag root_in_name (ScanConfig): no modo fullpath e em fonte unica, injeta o nome da pasta-raiz como a pasta mais externa do sufixo, de forma que ate os arquivos da raiz levem o nome do projeto. Injecao so no nome planejado (via root_prefix em _plan_names); o rel de exibicao do manifesto e do _TREE.md continua real. Ignorada com aviso fora do fullpath e em multi-fonte. Limite de nome protegido pelo truncamento com hash ja existente. CLI --root-in-name; checkbox na GUI serializada no .bat (FIX-004). +6 testes."
```
