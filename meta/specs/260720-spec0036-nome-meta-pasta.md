# spec0036 — Nomear _MANIFEST/_TREE com o nome da pasta no fim (checkbox, default-ON)

- **Tipo:** implementação (core + CLI + GUI + settings). Roda `python -m pytest -q`.
  Versão-alvo: **0.11.0** (0.10.1 → 0.11.0; muda o nome padrão dos meta).
- **Data:** 2026-07-20 · **Ordem:** aplicar DEPOIS da spec0035 (anexa em `_apply_settings_to_vars`
  e no DECISIONS pós-FIX-010).
- **Pedido.** Um checkbox (default-ON) que nomeia `_MANIFEST.md`/`_TREE.md` com o **nome da
  pasta** (o campo "Nome da pasta" = `dest.name`, editável — NÃO o nome da raiz) **no fim**:
  `_MANIFEST_<pasta>.md` / `_TREE_<pasta>.md`. O prefixo `_MANIFEST`/`_TREE` fica intacto (os
  projetos buscam por ele no começo); o nome no fim desambigua no Projeto do Claude. Aplica-se
  só ao que estiver marcado (Gerar _MANIFEST / Gerar _TREE) — nomeação "inteligente".

## GUARDA (DEC-020) — AUTORIZADO pelo autor

Para o `.bat` reproduzir a saída (paridade FIX-004), o flag precisa viajar pela CLI — então
esta spec **toca `cli.py` e `gui._build_cli_args`**. É **aditivo** (mesmo padrão de
`--no-manifest`/`--tree`), NÃO reescreve o gerador. `_generate_bat`/`_sources` **não** mudam.
Ao terminar, `git diff` deve mostrar que os flags EXISTENTES seguem emitidos idênticos, e o
**portão de aceite** vale: gerar um `.bat` e rodá-lo deve produzir os mesmos nomes de arquivo
que a GUI. Se algo pedir reescrever o gerador, PARE e reporte.

---

## Edit 1 — `core.py` (ScanConfig): novo campo

**Âncora exata:**
```
    write_tree: bool = False  # gera _TREE.md (arvore da origem); desligado por padrao (spec0011)
```
Inserir DEPOIS:
```
    name_meta_with_folder: bool = True  # _MANIFEST/_TREE ganham _<pasta> no fim (spec0036)
```

## Edit 2 — `core.py`: helper `meta_name` + `is_our_folder` reconhece o sufixo

**Âncora exata** (o `is_our_folder` inteiro):
```
def is_our_folder(dest: Path) -> bool:
    """True se a pasta de destino foi criada pelo FlatDrop (tem manifesto nosso)."""
    mani = dest / C.MANIFEST_NAME
    if not mani.is_file():
        return False
    try:
        first = mani.read_text(encoding="utf-8", errors="ignore").splitlines()[:1]
    except OSError:
        return False
    return bool(first) and first[0].strip() == C.MANIFEST_SIGNATURE
```
Trocar por:
```
def meta_name(base: str, dest: Path, cfg: ScanConfig) -> str:
    """Nome de um arquivo meta (_MANIFEST.md / _TREE.md).

    Com ``name_meta_with_folder`` (padrão), insere o nome da pasta de saída no FIM,
    antes da extensão — ``_MANIFEST_<pasta>.md`` —, desambiguando no Projeto do
    Claude e mantendo o prefixo (_MANIFEST/_TREE) para a busca. (spec0036/DEC-022)
    """
    if not cfg.name_meta_with_folder:
        return base
    stem, _, ext = base.rpartition(".")       # "_MANIFEST", ".", "md"
    folder = _sanitize(dest.name)
    return f"{stem}_{folder}.{ext}" if folder else base


def is_our_folder(dest: Path) -> bool:
    """True se a pasta foi criada pelo FlatDrop (tem manifesto nosso). Reconhece
    _MANIFEST.md E _MANIFEST_<nome>.md (o sufixo da spec0036)."""
    for mani in sorted(dest.glob("_MANIFEST*.md")):
        try:
            first = mani.read_text(encoding="utf-8", errors="ignore").splitlines()[:1]
        except OSError:
            continue
        if first and first[0].strip() == C.MANIFEST_SIGNATURE:
            return True
    return False
```

## Edit 3 — `core.py`: usar `meta_name` ao escrever os dois meta

**Âncora exata (3a — em `write_manifest`):**
```
    mani = dest / C.MANIFEST_NAME
```
> Atenção: essa linha aparece 2× no arquivo. A alterar é a que está DENTRO de
> `write_manifest` (por volta da linha 1096, tem `cfg` no escopo). A outra (em
> `is_our_folder`) já foi tratada no Edit 2. Se houver dúvida de qual, PARE e reporte.

Trocar (a de `write_manifest`) por:
```
    mani = dest / meta_name(C.MANIFEST_NAME, dest, cfg)
```

**Âncora exata (3b — em `write_tree`):**
```
    tree = dest / C.TREE_NAME
```
Trocar por:
```
    tree = dest / meta_name(C.TREE_NAME, dest, cfg)
```

## Edit 4 — `cli.py`: flag `--no-name-meta`

**Âncora exata:**
```
    p.add_argument("--no-manifest", action="store_false", dest="write_manifest", help="não gerar _MANIFEST.md")
```
Inserir DEPOIS:
```
    p.add_argument("--no-name-meta", action="store_false", dest="name_meta_with_folder",
                   help="não incluir o nome da pasta no fim de _MANIFEST/_TREE")
```
E passar ao ScanConfig. **Âncora exata:**
```
        write_manifest=args.write_manifest,
        write_tree=args.write_tree,
```
Trocar por:
```
        write_manifest=args.write_manifest,
        write_tree=args.write_tree,
        name_meta_with_folder=args.name_meta_with_folder,
```

## Edit 5 — `gui.py` (`_build_cli_args`): emitir o flag (aditivo)

**Âncora exata:**
```
        if not self.manifest_var.get():
            args += ["--no-manifest"]
        if self.tree_var.get():
            args += ["--tree"]
```
Trocar por:
```
        if not self.manifest_var.get():
            args += ["--no-manifest"]
        if self.tree_var.get():
            args += ["--tree"]
        if not self.name_meta_var.get():
            args += ["--no-name-meta"]
```
> Guarda DEC-020: os dois primeiros ifs seguem IDÊNTICOS; só se ACRESCENTA o terceiro.

## Edit 6 — `gui.py`: `Var` + checkbox

**Âncora exata (6a — declaração do Var):**
```
        self.sep_var = tk.StringVar(value=C.DEFAULT_SEP)
```
Inserir DEPOIS:
```
        self.name_meta_var = tk.BooleanVar(value=True)  # nomear meta c/ a pasta (spec0036)
```

**Âncora exata (6b — placeholder na Renomeação, deixado pela spec0034):**
```
        # (spec0035 insere aqui, abaixo, o checkbox de nomear _MANIFEST/_TREE.)
```
Trocar por:
```
        ttk.Checkbutton(modes, text="Nomear _MANIFEST/_TREE com o nome da pasta (no fim, p/ desambiguar)",
                        variable=self.name_meta_var).grid(sticky="w")
```

## Edit 7 — `gui.py` (`_persist_settings`): salvar o campo

**Âncora exata:**
```
            write_tree=self.tree_var.get(),
            root_in_name=self.root_in_name_var.get(),
```
Trocar por:
```
            write_tree=self.tree_var.get(),
            name_meta_with_folder=self.name_meta_var.get(),
            root_in_name=self.root_in_name_var.get(),
```

## Edit 8 — `gui.py` (`_apply_settings_to_vars`): restaurar (é preferência)

**Âncora exata** (no grupo de preferências deixado pela spec0035):
```
        self.tree_var.set(s.write_tree)
        self.root_in_name_var.set(s.root_in_name)
```
Trocar por:
```
        self.tree_var.set(s.write_tree)
        self.name_meta_var.set(s.name_meta_with_folder)
        self.root_in_name_var.set(s.root_in_name)
```
> E no `_reset_defaults` (spec0035), acrescente junto às preferências:
> `self.name_meta_var.set(s.name_meta_with_folder)` (default True).

## Edit 9 — `settings.py`: novo campo + saneamento

**Âncora exata (9a — dataclass):**
```
    write_tree: bool = False
```
Inserir DEPOIS:
```
    name_meta_with_folder: bool = True
```
**Âncora exata (9b — no `_sanitize`, junto dos outros bool):**
```
    s.write_tree = _bool("write_tree", False)
```
Inserir DEPOIS:
```
    s.name_meta_with_folder = _bool("name_meta_with_folder", True)
```

## Edit 10 — `flatdrop/__init__.py`: bump

**Âncora exata:** `__version__ = "0.10.1"` → trocar por `__version__ = "0.11.0"`

## Edit 11 — testes em `tests/test_core.py`

**Âncora:** acrescentar ao fim de `tests/test_core.py`:
```python


def test_meta_name_suffix_on_off(tmp_path):
    from flatdrop import core, config as C
    from flatdrop.core import ScanConfig
    dest = tmp_path / "cancioneiro"
    on = ScanConfig(name_meta_with_folder=True)
    off = ScanConfig(name_meta_with_folder=False)
    assert core.meta_name(C.MANIFEST_NAME, dest, on) == "_MANIFEST_cancioneiro.md"
    assert core.meta_name(C.TREE_NAME, dest, on) == "_TREE_cancioneiro.md"
    assert core.meta_name(C.MANIFEST_NAME, dest, off) == "_MANIFEST.md"


def test_is_our_folder_recognizes_suffixed_manifest(tmp_path):
    from flatdrop import core, config as C
    dest = tmp_path / "proj"
    dest.mkdir()
    (dest / "_MANIFEST_proj.md").write_text(
        C.MANIFEST_SIGNATURE + "\n", encoding="utf-8")
    assert core.is_our_folder(dest) is True
```

## Edit 12 — `meta/DECISIONS.md`: DEC-022

**Âncora exata** (última linha do bloco FIX-010, da spec0035):
```
para as preferências. Persistência é só-GUI (DEC-020); nada disto toca o `.bat`.
```
Inserir DEPOIS:
```
## DEC-022 — Nomear _MANIFEST/_TREE com o nome da pasta no fim
**Data:** 2026-07-20 · **Status:** aceita (spec0036)

**Contexto.** Vários projetos achatados no Claude têm `_MANIFEST.md`/`_TREE.md` homônimos —
ambíguos. O autor quer desambiguar com o nome da pasta de saída, mas no FIM (os projetos
buscam pelo prefixo `_MANIFEST`/`_TREE` no começo).

**Decisão.** Checkbox **default-ON** "Nomear _MANIFEST/_TREE com o nome da pasta": os meta
gerados viram `_MANIFEST_<pasta>.md`/`_TREE_<pasta>.md`, onde `<pasta>` = `dest.name` (o
campo "Nome da pasta", editável — não a raiz). Aplica-se só ao que está marcado. O flag
`--no-name-meta` leva o desligamento à CLI (paridade GUI×`.bat`, FIX-004). `is_our_folder`
passou a reconhecer `_MANIFEST*.md` para o "limpar destino" seguir funcionando.

**Consequência.** Muda o nome PADRÃO dos meta (default-ON) — `.bat` antigos passam a gerar
os nomes com sufixo (comportamento desejado). Só-core/CLI/GUI; o gerador do `.bat`
(`_generate_bat`) não muda, só ganha um flag aditivo em `_build_cli_args` (DEC-020,
autorizado). É preferência persistida (settings).
```

## Edit 13 — `meta/CHANGELOG.md`: [0.11.0]

**Âncora exata:** `## [0.10.1] — 2026-07-20`
Inserir ANTES dela:
```
## [0.11.0] — 2026-07-20

### Adicionado
- **Nomear _MANIFEST/_TREE com o nome da pasta no fim (DEC-022, spec0036).** Checkbox
  default-ON: os meta gerados viram `_MANIFEST_<pasta>.md`/`_TREE_<pasta>.md` (`<pasta>` = o
  campo "Nome da pasta", editável), mantendo o prefixo para busca e desambiguando no Projeto
  do Claude. Só para o que está marcado. Flag `--no-name-meta` na CLI (paridade `.bat`).
  `is_our_folder` reconhece o sufixo. 2 testes (66 → 68).

```

## Edit 14 — `meta/STATUS.md`: refletir 0.11.0

**Âncora:** substituir o bloco da nota de revisão (o da spec0035) por um 0.11.0 que cite a
nomeação dos meta como entregue e remova-a de "pendente". Manter o ponteiro de multi-raiz
(decisão A/B) como frente maior. (Texto a critério do Code, curto; se preferir, o chat
fornece na próxima.)

---

## O que testar

- **Automatizado:** 66 → **68** (meta_name on/off; is_our_folder com sufixo).
- **Smoke manual (Windows) — portão do `.bat`:** com o checkbox ON, Executar → saem
  `_MANIFEST_<pasta>.md`/`_TREE_<pasta>.md`; desmarcar Gerar _TREE → só o manifest ganha
  nome. Gerar um `.bat` e **rodá-lo** → mesmos nomes da GUI. "Limpar destino" ainda
  reconhece a pasta (via `is_our_folder`).
- **`git diff`:** `_generate_bat`/`_sources` intocados; em `_build_cli_args` só o 3º `if`
  novo; os flags existentes idênticos.

## Commit sugerido (sem acento)

```
git add flatdrop/core.py flatdrop/cli.py flatdrop/gui.py flatdrop/settings.py flatdrop/__init__.py tests/test_core.py meta/DECISIONS.md meta/CHANGELOG.md meta/STATUS.md meta/specs/260720-spec0036-nome-meta-pasta.md & git commit -m "feat: nomear _MANIFEST/_TREE com o nome da pasta no fim (DEC-022)" -m "Checkbox default-ON: _MANIFEST_<pasta>.md / _TREE_<pasta>.md (pasta = campo Nome da pasta), mantendo o prefixo p/ busca. Flag --no-name-meta leva o off a CLI (paridade .bat). is_our_folder reconhece o sufixo. Gerador do .bat intocado; so um if aditivo em _build_cli_args (DEC-020, autorizado). 2 testes (66 -> 68). Bump 0.11.0."
```
