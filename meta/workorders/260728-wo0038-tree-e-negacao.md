# wo0038 — Tornar visivel e liberavel o que o ignore esconde

**Data:** 2026-07-28 · **Autor:** chat (planejamento) · **Aplicar com:** `/apply-wo meta/workorders/260728-wo0038-tree-e-negacao.md`

> Origem: notas do autor de 2026-07-23 e 2026-07-24. Causa raiz medida e registrada na
> **DEC-025**. Esta WO corrige a causa (FIX-011) e paga a divida de visibilidade do `_TREE`.
> **Mexe em CODIGO** — rode `python -m pytest -q` ao fim.

## Problema (resumo)

1. Um `!pasta/arquivo.md` no `.flatdropignore` **nao resgata nada** quando a pasta esta
   ignorada na forma `pasta/`: `_scan` **poda o diretorio antes de descer**, entao a negacao
   nunca chega a ser avaliada. O motor de padroes ja liberaria o arquivo — quem o perde e a poda.
2. O `_TREE.md` nao diz **o que** foi ignorado: pasta podada vira uma linha
   (`meta/legacy/  [ignorada: flatdropignore]`) e arquivo pulado vira contagem
   (`[pulados: flatdropignore x37]`). Sem nome, o chat futuro nao tem como decidir o que liberar.

## Fora de escopo

- O **gerador** do editor de `.flatdropignore` (`build_flatdropignore`) continua emitindo pasta
  parcial por folha em vez de `pasta/*` + `!pasta/mantido`. Depois desta WO isso deixa de ser
  bloqueio (o `!` passa a funcionar nas duas formas) e vira polimento — mexe na maquinaria de
  round-trip da DEC-016/spec0020 e pede analise antes. Fica no item 5 do backlog do STATUS.
- Multi-raiz: nao tocar.
- `flatdrop/cli.py`, `gui._build_cli_args`, `gui._generate_bat`, `gui._sources`: **intocados**
  (DEC-020). Esta WO nao chega perto deles; se algo parecer exigir isso, **PARE e reporte**.

---

## Edicao 1 — `flatdrop/config.py`: teto e motivos nomeaveis

**Ancora** (fim do bloco do `_TREE`):

```python
TREE_NAME = "_TREE.md"
TREE_SIGNATURE = "<!-- flatdrop-tree v1 -->"
```

**Substituir por:**

```python
TREE_NAME = "_TREE.md"
TREE_SIGNATURE = "<!-- flatdrop-tree v1 -->"

# Quantos nomes o _TREE.md lista antes de agregar o resto ("+N mais"), tanto para
# arquivos pulados por ignore DO AUTOR quanto para a espiada rasa numa pasta ignorada.
TREE_NAME_CAP = 10

# Motivos que saem NOMEADOS no _TREE.md. So o ignore do autor entra: e o unico que ele
# pode querer liberar com "!". Ruido estrutural (tipo, embutido, sensivel) segue agregado.
TREE_NAMED_REASONS = ("gitignore", "flatdropignore")
```

## Edicao 2 — `flatdrop/core.py`: prefixos alcancados por negacao

**Ancora** (funcao inteira, logo acima de `_ignore_status`):

```python
def _build_ignore_specs(root: Path, cfg: ScanConfig):
    """(full, gi, fd): ``full`` = decisão (gitignore + flatdropignore, este por último
    p/ ter a palavra final); ``gi``/``fd`` = só p/ atribuir o motivo e detectar liberação."""
    if not HAS_PATHSPEC:
        return None, None, None
    gi_lines, fd_lines = _collect_ignore_lines(root, cfg)
    if not gi_lines and not fd_lines:
        return None, None, None
    return _make_spec(gi_lines + fd_lines), _make_spec(gi_lines), _make_spec(fd_lines)
```

**Substituir por:**

```python
def _negated_dir_prefixes(lines: list[str]) -> frozenset[str]:
    """Pastas (relativas, posix) que alguma negacao ``!`` alcanca.

    ``!meta/legacy/GOT.md`` devolve ``{'meta', 'meta/legacy'}``. E o insumo do FIX-011:
    o ``_scan`` NAO poda uma pasta ignorada quando ha um ``!`` apontando para dentro dela —
    com a pasta podada, a negacao nunca chegaria a ser avaliada.

    Conservador de proposito: ao encontrar um segmento com curinga (``*``, ``?``, ``[``),
    para de acumular. Errar para o lado de DESCER e barato; errar para o lado de podar
    esconde arquivo que o autor pediu.
    """
    dirs: set[str] = set()
    for ln in lines:
        s = ln.strip()
        if not s.startswith("!"):
            continue
        p = s[1:].strip().lstrip("/").rstrip("/")
        parts = [x for x in p.split("/") if x and x != "."]
        acc: list[str] = []
        for seg in parts[:-1]:            # so os DIRETORIOS do caminho, nunca a folha
            if any(ch in seg for ch in "*?["):
                break
            acc.append(seg)
            dirs.add("/".join(acc))
    return frozenset(dirs)


def _build_ignore_specs(root: Path, cfg: ScanConfig):
    """(full, gi, fd, negated): ``full`` = decisão (gitignore + flatdropignore, este por
    último p/ ter a palavra final); ``gi``/``fd`` = só p/ atribuir o motivo e detectar
    liberação; ``negated`` = pastas alcançadas por alguma negação ``!`` (FIX-011)."""
    if not HAS_PATHSPEC:
        return None, None, None, frozenset()
    gi_lines, fd_lines = _collect_ignore_lines(root, cfg)
    if not gi_lines and not fd_lines:
        return None, None, None, frozenset()
    return (_make_spec(gi_lines + fd_lines), _make_spec(gi_lines), _make_spec(fd_lines),
            _negated_dir_prefixes(gi_lines + fd_lines))
```

## Edicao 3 — `flatdrop/core.py`: os TRES desempacotamentos de `_build_ignore_specs`

> A funcao passou a devolver 4 itens. **Sao exatamente tres chamadas**; se encontrar uma
> quarta, PARE e reporte.

**3a — em `_ignore_probes`.** Ancora:

```python
    full, gi, fd = _build_ignore_specs(root, cfg)
```

**Substituir por:**

```python
    full, gi, fd, _negated = _build_ignore_specs(root, cfg)
```

**3b — em `build_flatdropignore`.** Ancora:

```python
    full, gi, _fd = _build_ignore_specs(root, cfg)
```

**Substituir por:**

```python
    full, gi, _fd, _negated = _build_ignore_specs(root, cfg)
```

**3c — em `_scan`.** Ancora:

```python
    full_spec, gi_spec, fd_spec = _build_ignore_specs(root, cfg)
```

**Substituir por:**

```python
    full_spec, gi_spec, fd_spec, negated_dirs = _build_ignore_specs(root, cfg)
```

## Edicao 4 — `flatdrop/core.py`: a poda respeita a negacao (FIX-011)

**Ancora** (dentro do laco de poda de `_scan`):

```python
            ign, src, _ = _ignore_status(rel_sub + "/", full_spec, gi_spec, fd_spec)
            if ign:
                note(f"{src} (pasta)", rel_sub + "/")
                continue
            kept.append(d)
```

**Substituir por:**

```python
            ign, src, _ = _ignore_status(rel_sub + "/", full_spec, gi_spec, fd_spec)
            # FIX-011: pasta com um "!" apontando para dentro NAO e podada. Podada, a
            # negacao nunca seria avaliada — o motor liberaria o arquivo, mas a varredura
            # nao chegaria ate ele. Aqui a gente desce e decide arquivo a arquivo (o custo
            # extra so aparece quando o autor de fato escreveu uma negacao).
            if ign and rel_sub not in negated_dirs:
                note(f"{src} (pasta)", rel_sub + "/")
                continue
            kept.append(d)
```

## Edicao 5 — `flatdrop/core.py`: no da arvore ganha a espiada

**Ancora:**

```python
def _tree_node() -> dict:
    return {"children": {}, "files": [], "collapsed": None, "skipped": []}
```

**Substituir por:**

```python
def _peek_children(abs_dir: Path) -> list[str]:
    """Nomes dos filhos DIRETOS de uma pasta ignorada, ate ``C.TREE_NAME_CAP``.

    Leitura RASA (sem recursao) e so para pasta ignorada pelo AUTOR: o lixo estrutural
    (``node_modules``, ``.git``) segue colapsado sem custo. E o insumo que faltava para o
    autor — ou o chat — decidir o que liberar com ``!`` (wo0038). Falha de leitura devolve
    lista vazia: a arvore volta ao comportamento antigo em vez de quebrar.
    """
    try:
        entries = sorted(
            os.scandir(abs_dir),
            key=lambda e: (not e.is_dir(follow_symlinks=False), e.name.lower()),
        )
    except OSError:
        return []
    out = [
        (e.name + "/" if e.is_dir(follow_symlinks=False) else e.name)
        for e in entries[:C.TREE_NAME_CAP]
    ]
    resto = len(entries) - C.TREE_NAME_CAP
    if resto > 0:
        out.append(f"(+{resto} mais)")
    return out


def _tree_node() -> dict:
    return {"children": {}, "files": [], "collapsed": None, "skipped": [], "peek": []}
```

## Edicao 6 — `flatdrop/core.py`: renderizar a espiada

**Ancora** (dentro de `_tree_render`):

```python
            if data["collapsed"]:
                lines.append(f"{prefix}{name}/  [ignorada: {data['collapsed']}]")
```

**Substituir por:**

```python
            if data["collapsed"]:
                lines.append(f"{prefix}{name}/  [ignorada: {data['collapsed']}]")
                # Espiada rasa (wo0038): so pasta ignorada pelo AUTOR traz nomes — e o
                # que se precisa saber para liberar um item com "!".
                for peek in data.get("peek", []):
                    lines.append(f"{prefix}  {peek}")
```

## Edicao 7 — `flatdrop/core.py`: pulado por ignore do autor sai NOMEADO

**Ancora** (fim de `_tree_render`):

```python
    if mode == "summary" and node["skipped"]:
        counts: dict[str, int] = {}
        for _, label in node["skipped"]:
            counts[label] = counts.get(label, 0) + 1
        agg = ", ".join(f"{label} x{n}" for label, n in sorted(counts.items()))
        lines.append(f"{prefix}[pulados: {agg}]")
```

**Substituir por:**

```python
    if mode == "summary" and node["skipped"]:
        # Motivo do AUTOR sai NOMEADO ate o teto; o resto (tipo, embutido, sensivel) segue
        # so agregado — e ruido, nao alvo de "!". Modo "full" ja lista folha por folha.
        named: dict[str, list[str]] = {}
        counts: dict[str, int] = {}
        for name, label in node["skipped"]:
            if label in C.TREE_NAMED_REASONS:
                named.setdefault(label, []).append(name)
            else:
                counts[label] = counts.get(label, 0) + 1
        for label, names in sorted(named.items()):
            names = sorted(names)          # sem isto o teto guardaria um subconjunto aleatorio
            shown = names[:C.TREE_NAME_CAP]
            resto = len(names) - len(shown)
            sufixo = f" (+{resto} mais)" if resto else ""
            lines.append(f"{prefix}[pulados por {label}: {', '.join(shown)}{sufixo}]")
        if counts:
            agg = ", ".join(f"{label} x{n}" for label, n in sorted(counts.items()))
            lines.append(f"{prefix}[pulados: {agg}]")
```

## Edicao 8 — `flatdrop/core.py`: montar a espiada em `write_tree`

**Ancora:**

```python
    # Pastas colapsadas: uma entrada cada, sem interior.
    for rel, reason in folder_items:
        parts = rel[:-1].split("/")
        parent = _tree_get_node(root_node, tuple(parts[:-1]))
        parent["children"][parts[-1]] = {
            "children": {},
            "files": [],
            "collapsed": _tree_label(reason),
            "skipped": [],
        }
```

**Substituir por:**

```python
    # Pastas colapsadas: uma entrada cada, sem interior — mas a ignorada pelo AUTOR ganha
    # uma espiada RASA nos filhos diretos, para nao esconder o que se pode querer liberar.
    for rel, reason in folder_items:
        parts = rel[:-1].split("/")
        label = _tree_label(reason)
        parent = _tree_get_node(root_node, tuple(parts[:-1]))
        parent["children"][parts[-1]] = {
            "children": {},
            "files": [],
            "collapsed": label,
            "skipped": [],
            "peek": _peek_children(plan.root / rel[:-1]) if label in C.TREE_NAMED_REASONS else [],
        }
```

## Edicao 9 — `flatdrop/core.py`: docstring de `write_tree` deixa de mentir

**Ancora:**

```python
    A arvore e montada a partir de plan.files (copiados) e plan.skipped_items
    (pulados, ja em memoria) — nenhuma nova varredura de disco.
```

**Substituir por:**

```python
    A arvore e montada a partir de plan.files (copiados) e plan.skipped_items
    (pulados, ja em memoria). A UNICA leitura de disco e a espiada rasa nos filhos
    diretos de cada pasta ignorada pelo AUTOR (wo0038): sem recursao, limitada por
    C.TREE_NAME_CAP, e tolerante a falha (devolve vazio).
```

## Edicao 10 — testes (`tests/test_core.py`)

Acrescente ao fim do arquivo, no estilo dos que ja existem (tmp_path + `ScanConfig`):

1. `test_negacao_resgata_arquivo_em_pasta_ignorada` — arvore com `meta/legacy/a.md` e
   `meta/legacy/b.md`, `.flatdropignore` com `meta/legacy/` **e** `!meta/legacy/a.md`.
   Espera: `a.md` entre os copiados, `b.md` entre os pulados, e **nenhuma** entrada de pasta
   colapsada para `meta/legacy/`. (E o caso que falhava — FIX-011.)
2. `test_pasta_ignorada_sem_negacao_continua_podada` — mesma arvore, sem a linha `!`.
   Espera: `meta/legacy/` colapsada, nenhum filho entre os pulados. (Guarda a poda do FIX-001.)
3. `test_tree_nomeia_pulados_do_autor` — `.flatdropignore` com `docs/*`, tres `.md` dentro.
   Espera: o `_TREE.md` contem `[pulados por flatdropignore:` com os tres nomes e **nao**
   contem `[pulados: flatdropignore x3]`.
4. `test_tree_espia_pasta_ignorada` — `.flatdropignore` com `docs/` (forma pasta, sem `!`).
   Espera: a linha `[ignorada: flatdropignore]` seguida dos nomes dos filhos diretos.
5. `test_peek_respeita_teto` — pasta ignorada com mais de `C.TREE_NAME_CAP` filhos.
   Espera: `(+N mais)` presente e no maximo `TREE_NAME_CAP` nomes.

Se algum teste EXISTENTE quebrar por causa da forma nova do `_TREE`, **ajuste o teste**
(o formato mudou de proposito) e **registre o ajuste no relatorio** — nao mude o codigo
para caber no teste velho.

## Edicao 11 — versao

`flatdrop/__init__.py`: `__version__ = "0.11.0"` → `__version__ = "0.12.0"`.

## Edicao 12 — `meta/CHANGELOG.md`

**Ancora:**

```
## [0.11.0] — 2026-07-20
```

**Inserir ANTES dela:**

```
## [0.12.0] — 2026-07-28

### Corrigido
- **A negação `!` volta a resgatar arquivo dentro de pasta ignorada (FIX-011, wo0038).**
  `_scan` podava o diretório antes de descer, então a negação nunca era avaliada — o motor
  de padrões já liberava o arquivo, mas a varredura não chegava até ele. Agora a poda
  consulta os prefixos alcançados por algum `!` e desce nesses casos; o custo extra só
  aparece quando o autor de fato escreveu uma negação.

### Adicionado
- **O `_TREE.md` passa a dizer O QUE foi ignorado (wo0038).** Arquivo pulado por ignore do
  autor sai **nomeado** (até `TREE_NAME_CAP`, depois `(+N mais)`) em vez de virar contagem;
  pasta ignorada pelo autor ganha uma **espiada rasa** nos filhos diretos. Ruído estrutural
  (`node_modules`, `.git`, tipo, sensível) segue colapsado/agregado.

```

## Edicao 13 — `meta/DECISIONS.md`

Acrescente ao FIM do arquivo:

```
## FIX-011 — A negação `!` não resgatava arquivo dentro de pasta ignorada
**Data:** 2026-07-28

- **Sintoma:** `meta/legacy/` + `!meta/legacy/GOT.md` no `.flatdropignore` não trazia o
  arquivo; o `_TREE` mostrava só `meta/legacy/  [ignorada: flatdropignore]`, e o editor da
  GUI, ao salvar, caía no fallback de listar arquivo a arquivo.
- **Causa raiz:** não era o motor de padrões. `core._scan` **poda diretórios in-place**
  antes de descer (`dirnames[:] = kept`, herança do FIX-001); com a pasta podada, o `!`
  nunca chega a ser avaliado. Medido em DEC-025: `match_file` devolve *não ignorado* para o
  arquivo negado — quem o perde é a poda.
- **Solução:** `_negated_dir_prefixes` calcula, dos ignores coletados, as pastas alcançadas
  por alguma negação; a poda só descarta a pasta se ela **não** estiver nesse conjunto.
  Conservador com curinga: na dúvida, desce. O custo extra só existe quando há `!`.
- **Lição:** poda ≠ filtro. Otimização que corta a árvore antes de decidir muda a semântica,
  não só a performance — e o sintoma aparece longe da causa. A convenção `pasta/*` (DEC-025)
  continua valendo como cinto e suspensório, mas deixou de ser obrigatória.
```

## Edicao 14 — `meta/STATUS.md`

**Ancora** (item 5 do backlog):

```
5. **Editor de `.flatdropignore` deve gravar `pasta/*`** em vez de `pasta/` + fallback por
   arquivo (causa raiz em DEC-025). Enquanto não entra: **não salvar o `.flatdropignore` pela
   GUI** — o bloco `# >>> flatdrop-editor` reescreveria a forma antiga e quebraria o `!`.
```

**Substituir por:**

```
5. **Editor de `.flatdropignore` deveria gravar `pasta/*` + `!mantido`** em vez de listar a
   pasta parcial por folha. Depois do FIX-011 (0.12.0) deixou de ser bloqueio — o `!` funciona
   nas duas formas —, mas a lista por folha continua não sendo à prova de arquivo novo. Mexe na
   maquinaria de round-trip (DEC-016/spec0020): **pede análise antes da WO**.
```

**Ancora** (primeiro item de Riscos):

```
- **Um comportamento aberto (não é regressão): o `!` não resgata arquivo dentro de pasta
  ignorada.** Causa raiz medida em **DEC-025** — `core._scan` poda o diretório casado antes de
  descer, então a negação nunca é avaliada. Contornado por convenção (`pasta/*`); a correção de
  produto é o item 5 do backlog. O `.flatdropignore` da raiz já está na forma nova.
```

**Substituir por:**

```
- ~~O `!` não resgata arquivo dentro de pasta ignorada.~~ **RESOLVIDO na 0.12.0 (FIX-011,
  wo0038).** A poda passou a consultar as pastas alcançadas por negação. A convenção `pasta/*`
  (DEC-025) segue recomendada, mas deixou de ser obrigatória.
```

---

## Validado em sandbox antes de virar WO

As 10 edicoes de codigo foram aplicadas numa copia de `core.py`/`config.py` e exercitadas com
`make_plan` + `write_tree` de verdade. As ancoras casaram 1x cada, e a saida foi:

```
# .flatdropignore = "meta/legacy/" + "!meta/legacy/GOT.md" + "docs/"
t1/
  docs/  [ignorada: flatdropignore]
    d00.md
    ...
    (+3 mais)
  meta/
    legacy/                                        <- NAO colapsou: ha "!" apontando pra dentro
      GOT.md                                       <- resgatado (era o bug)
      [pulados por flatdropignore: outro.md]
```

Foi essa rodada que pegou um defeito no rascunho: sem `sorted(names)` na Edicao 7, o teto
guardava um subconjunto em ordem de varredura (`d09, d00, d10, d08...`). Ja corrigido acima.

---

## Checklist de fecho

- [ ] `python -m pytest -q` verde (68 + os novos; diga o número final).
- [ ] `git diff` conferido: nada fora das edicoes nomeadas; `cli.py`/`_generate_bat`/`_sources`/
      `_build_cli_args` **intocados**.
- [ ] Smoke manual sugerido ao autor (a suite nao cobre tkinter nem disco real): rodar
      `python run.py` num projeto com `.flatdropignore` de verdade e conferir o `_TREE.md` novo.
- [ ] Commit sem acento, Conventional Commits.
- [ ] **Relatorio**: o que fez, desvios do texto desta WO, arquivos tocados, resultado da
      suite e o commit.
