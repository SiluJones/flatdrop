# spec0027 — IMPLEMENTAÇÃO: force-include por caminho exato (`++path`)

- **Tipo:** implementação. Aplica DEC-021. Roda `python -m pytest -q`.
- **Data:** 2026-07-16 · **Versão-alvo:** 0.7.0 (0.6.0 → 0.7.0).
- **Ordem:** aplicar ANTES da spec0028 (FIX do nome). A spec0028 assume 0.7.0.
- **Verificado no sandbox** (spec0026 §3) contra a core real antes desta escrita.

## GUARDAS (DEC-020) — LEIA ANTES

`flatdrop/cli.py`, `gui._build_cli_args`, `gui._generate_bat`, `gui._sources`: **zero
edições**. O force-include vive na core/scan, lido do `.flatdropignore` que GUI e CLI
consomem igual. Ao terminar, `git diff` deve mostrar essas quatro **intocadas**. Se alguma
âncora parecer exigir tocá-las, PARE e reporte.

---

## Edit 1 — `core._rebase_ignore`: não deixar `++` virar padrão do `pathspec`

**Âncora exata:**
```
    s = line.strip()
    if not s or s.startswith("#"):
        return []
```
Trocar por:
```
    s = line.strip()
    # '++' é force-include (DEC-021), tratado à parte — nunca vira padrão de ignore.
    if not s or s.startswith("#") or s.startswith("++"):
        return []
```

## Edit 2 — `core`: novo coletor `_collect_force_includes`

**Âncora exata** (fim de `_collect_ignore_lines`, imediatamente antes de `_make_spec`):
```
def _make_spec(lines: list[str]):
```
Inserir ANTES dessa linha:
```
def _collect_force_includes(root: Path, cfg: ScanConfig) -> list[str]:
    """Coleta os force-includes ('++caminho') de todos os .flatdropignore da árvore.

    Cada caminho é EXATO, ancorado onde é declarado (um '++x' num .flatdropignore em
    'sub/' vira 'sub/x'), rebaseado para relativo à raiz (posix). Dedup preservando
    ordem. Ao contrário dos ignores, NÃO usa pathspec — é caminho exato (DEC-021).
    """
    forced: list[str] = []
    seen: set[str] = set()
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        cur = Path(dirpath)
        rel = cur.relative_to(root).as_posix()
        base = "" if rel == "." else rel
        # mesma poda do _collect_ignore_lines (não desce em node_modules etc.)
        dirnames[:] = [d for d in dirnames if d not in cfg.dir_ignores]
        for _nm in C.FLATDROPIGNORE_NAMES:
            if _nm in filenames:
                for ln in _read_ignore_lines(cur / _nm):
                    s = ln.strip()
                    if not s.startswith("++"):
                        continue
                    p = s[2:].strip().lstrip("/")
                    if not p:
                        continue
                    full_rel = f"{base}/{p}" if base else p
                    if full_rel not in seen:
                        seen.add(full_rel)
                        forced.append(full_rel)
                break  # precedência: primeiro nome encontrado no diretório vence
    return forced


```

## Edit 3 — `core._scan`: resgate pós-varredura

**Âncora exata** (fim de `_scan`):
```
    return candidates, skipped, samples, warnings, skipped_items
```
Trocar por:
```
    # Force-include (DEC-021): resgata caminhos '++' barrados por corte embutido.
    # stat direto — alcança dentro de pastas podadas sem varrê-las; vence tudo
    # EXCETO sensível. Roda por ÚLTIMO para poder tirar o arquivo dos pulados.
    forced = _collect_force_includes(root, cfg)
    if forced:
        have = {rel.as_posix() for _src, rel, _sz in candidates}
        for frel in forced:
            if frel in have:
                continue
            full = root / frel
            if not full.is_file():
                warnings.append(f"force-include nao encontrado: {frel}")
                continue
            if not cfg.include_sensitive and is_sensitive(full.name):
                warnings.append(f"force-include ignorado (sensivel): {frel}")
                continue
            # tira o arquivo dos pulados (se a varredura o marcou) p/ não contar 2x
            for _i in range(len(skipped_items) - 1, -1, -1):
                _srel, _sreason = skipped_items[_i]
                if _srel == frel:
                    skipped_items.pop(_i)
                    if skipped.get(_sreason):
                        skipped[_sreason] -= 1
                    if frel in samples.get(_sreason, []):
                        samples[_sreason].remove(frel)
            try:
                size = full.stat().st_size
            except OSError:
                size = 0
            candidates.append((full, PurePath(frel), size))
            have.add(frel)

    return candidates, skipped, samples, warnings, skipped_items
```

## Edit 4 — novo arquivo `tests/test_force_include.py`

```python
"""Testes do force-include (++ no .flatdropignore) — DEC-021 / spec0027."""

from __future__ import annotations

from pathlib import Path

from flatdrop import core
from flatdrop.core import ScanConfig


def _tree(root: Path) -> None:
    (root / "lib").mkdir()
    (root / "node_modules" / "dep").mkdir(parents=True)
    (root / "webapp" / "static" / "vendor").mkdir(parents=True)
    (root / "keep.py").write_text("x", encoding="utf-8")
    (root / "app.min.js").write_text("x", encoding="utf-8")
    (root / "lib" / "vendor.min.js").write_text("x", encoding="utf-8")
    (root / "node_modules" / "dep" / "thing.min.js").write_text("x", encoding="utf-8")
    (root / "webapp" / "static" / "vendor" / "htmx.min.js").write_text("x", encoding="utf-8")
    (root / "id_rsa").write_text("secret", encoding="utf-8")


def _kept(plan) -> set[str]:
    return {f.rel.as_posix() for f in plan.files}


def test_force_include_rescues_barred_and_pruned(tmp_path):
    _tree(tmp_path)
    (tmp_path / ".flatdropignore").write_text(
        "++app.min.js\n++lib/vendor.min.js\n"
        "++node_modules/dep/thing.min.js\n++webapp/static/vendor/htmx.min.js\n",
        encoding="utf-8")
    plan = core.make_plan(tmp_path, ScanConfig())
    kept = _kept(plan)
    assert "app.min.js" in kept
    assert "lib/vendor.min.js" in kept
    assert "node_modules/dep/thing.min.js" in kept   # dentro de pasta PODADA
    assert "webapp/static/vendor/htmx.min.js" in kept
    # saiu dos pulados (não conta duas vezes)
    assert "app.min.js" not in {r for r, _ in plan.skipped_items}


def test_force_include_never_beats_sensitive(tmp_path):
    _tree(tmp_path)
    (tmp_path / ".flatdropignore").write_text("++id_rsa\n", encoding="utf-8")
    plan = core.make_plan(tmp_path, ScanConfig())
    assert "id_rsa" not in _kept(plan)
    assert any("sensivel" in w for w in plan.warnings)


def test_force_include_missing_warns(tmp_path):
    _tree(tmp_path)
    (tmp_path / ".flatdropignore").write_text("++nao/existe.min.js\n", encoding="utf-8")
    plan = core.make_plan(tmp_path, ScanConfig())
    assert any("nao encontrado" in w for w in plan.warnings)


def test_force_include_line_not_fed_to_matcher(tmp_path):
    # um '++x' não pode virar padrão de exclusão do pathspec
    _tree(tmp_path)
    (tmp_path / ".flatdropignore").write_text("++app.min.js\n", encoding="utf-8")
    kept = _kept(core.make_plan(tmp_path, ScanConfig()))
    assert "keep.py" in kept  # nada mais foi excluído por engano
```

## Edit 5 — `flatdrop/__init__.py`: bump

**Âncora exata:** `__version__ = "0.6.0"` → trocar por `__version__ = "0.7.0"`

## Edit 6 — `GLOSSARY.md`: termo novo

**Âncora exata:**
```
`.gitignore` bloqueia — até pasta que seria podada. Tem a **palavra final** sobre o
`.gitignore` (decisão deliberada, ≠ git puro). O próprio arquivo não vai para o
upload. (Ver DEC-014.)
```
Inserir DEPOIS (uma linha em branco antes):
```

**Force-include (`++caminho`).** Linha do `.flatdropignore` (marcador `++`, distinto do
`!`) que resgata UM arquivo EXATO barrado por um corte embutido. Ao contrário do `!` (que
age no matcher, abaixo dos cortes de suffix/tipo/poda), o `++` vence **todos** os cortes
embutidos — **exceto "sensível"** — via `stat` direto (alcança dentro de pastas podadas sem
varrê-las). Caminho exato ancorado onde é declarado; independe do `pathspec`. (Ver DEC-021.)
```

## Edit 7 — `meta/CHANGELOG.md`: entrada [0.7.0]

**Âncora exata:** `## [0.6.0] — 2026-07-15`
Inserir ANTES dela:
```
## [0.7.0] — 2026-07-16

### Adicionado
- **Force-include por caminho exato no `.flatdropignore`** (DEC-021, spec0027). Uma linha
  `++caminho/exato` resgata um arquivo barrado por um ignore embutido (ex.: `.min.js` da
  `DEFAULT_SUFFIX_IGNORES`) sem liberar todos do tipo. Vence suffix/file-ignore, poda de
  pasta, matcher gitignore/`.flatdropignore` e tipo — **exceto "sensível"**, que segue
  barrado (com aviso). Resgate por `stat` direto: alcança dentro de pastas podadas sem
  varrê-las. Caminho inexistente vira aviso. Independe do `pathspec`. **Só-core/scan: a CLI
  e o gerador de `.bat` seguem intocados (DEC-020).** 4 testes novos (58 → 62).

```

## Edit 8 — `meta/STATUS.md`: refletir 0.7.0

**Âncora exata:**
```
  **58 testes verdes**. Próxima = multi-raiz na GUI.
```
Trocar por:
```
  **58 testes verdes**. Próxima = multi-raiz na GUI.
- **(2026-07-16, spec0027 aplicada) Force-include por caminho exato entregue (DEC-021):**
  `++caminho` no `.flatdropignore` resgata arquivo barrado por ignore embutido (vence tudo
  menos sensível); `.bat` intocado. Versão **0.7.0**, **62 testes**. Próxima = corrigir o
  nome ao trocar de raiz (FIX-008, spec0028) e multi-raiz na GUI.
```

---

## O que testar

- **Automatizado** (`python -m pytest -q`): os 4 testes novos (58 → **62**), incluindo o
  resgate dentro de `node_modules` e a barreira de sensível.
- **Manual (opcional):** num projeto real, `++webapp/static/vendor/htmx.min.js` no
  `.flatdropignore`, gerar o mount e conferir que o arquivo entrou; e que rodar o **`.bat`**
  do mesmo projeto produz o MESMO resultado (paridade GUI×`.bat`, DEC-020).
- **`git diff`:** `cli.py`, `_build_cli_args`, `_generate_bat`, `_sources` sem uma linha
  alterada.

## Merece print no README

Um trecho de `.flatdropignore` com uma linha `++...` ao lado da saída mostrando o arquivo
resgatado. Só sinalizar; não gerar imagem.

## Commit sugerido (sem acento)

```
git add flatdrop/core.py flatdrop/__init__.py tests/test_force_include.py GLOSSARY.md meta/CHANGELOG.md meta/STATUS.md meta/specs/260715-spec0027-force-include-impl.md & git commit -m "feat(core): force-include por caminho exato (++) no flatdropignore" -m "Linha ++caminho resgata um arquivo barrado por ignore embutido (suffix/file/poda/matcher/tipo) sem liberar todos do tipo; vence tudo menos sensivel; stat direto alcanca dentro de pastas podadas; inexistente vira aviso; independe do pathspec. So-core/scan: CLI e gerador de .bat intocados (DEC-020). 4 testes novos (58 -> 62). Bump 0.7.0. DEC-021."
```
