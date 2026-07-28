# spec-0008 — `.flatdropignore` + `.gitignore` aninhado

**Tipo:** código · **Alvos:** `flatdrop/core.py`, `flatdrop/config.py`, `tests/test_core.py`
**Autor:** chat · **Aplicador:** Claude Code
**Depende de:** nada novo (estende a varredura atual). **Lógica verificada** com o pathspec real antes de escrever.

## Objetivo
1. **`.gitignore` aninhado:** respeitar `.gitignore` em subpastas (hoje só o da raiz é lido).
2. **`.flatdropignore`:** um arquivo por projeto, lido como o `.gitignore` e **aninhado**, que:
   - exclui o que vai para o git mas NÃO para o Projeto do Claude (regras positivas), e
   - com **negação `!`** LIBERA o que o `.gitignore` bloqueia (re-inclui, até pasta inteira que seria podada).
3. Atribuir o motivo do skip a `gitignore` ou `flatdropignore` (a pré-visualização continua dizendo POR QUÊ).

## Modelo (decisão de projeto)
- Junta-se TUDO num único matcher por "última regra vence" (semântica do gitignore, que o pathspec
  implementa). Ordem: todos os `.gitignore` (raso→fundo), depois todos os `.flatdropignore` (raso→fundo).
  Assim o **`.flatdropignore` tem sempre a palavra final** sobre o `.gitignore` — bate com a intenção
  ("`!` libera o que o gitignore bloqueia"), em qualquer profundidade.
- Padrões de um arquivo em subpasta são **reescritos** para casar relativo à raiz (ancorados ao diretório
  do arquivo; não-ancorados casam em qualquer profundidade abaixo dele).
- Três specs: `full` (decisão), `gi` e `fd` (só para atribuir o motivo e detectar liberação).
- Custo: a coleta dos arquivos de ignore faz uma passada extra na árvore (podando os ignores embutidos).
  Aceitável; dá para fundir numa passada só depois, se virar gargalo.

## Verificação feita (sandbox, pathspec real) — todos OK
`logs/` + `!logs/` → pasta liberada (não podada); `logs/a.md` → liberado; `*.tmp` → pula (gitignore);
`secret.txt` (no `.flatdropignore`) → pula (flatdropignore); `Area/*.bak` (gitignore aninhado) → pula;
`Area/data.keep` com `*.keep` (gitignore fundo) e `!*.keep` (flatdropignore raso) → **liberado** (fd vence).

---

## EDIÇÃO 1 — config.py: não copiar o próprio `.flatdropignore`

**Âncora:**
```
    ".ds_store", "thumbs.db", "desktop.ini",
}
```
**Ação:** SUBSTITUIR por:
```
    ".ds_store", "thumbs.db", "desktop.ini",
    ".flatdropignore",  # arquivo de controle do FlatDrop — nao vai para o upload
}
```

## EDIÇÃO 2 — core.py: trocar `_build_gitignore_spec` pelos novos helpers

**Âncora (a função inteira):**
```
def _build_gitignore_spec(root: Path, cfg: ScanConfig):
    """Lê .gitignore da raiz e devolve um matcher pathspec (ou None)."""
    if not (cfg.use_gitignore and HAS_PATHSPEC):
        return None
    gi = root / ".gitignore"
    if not gi.is_file():
        return None
    try:
        lines = gi.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return None
    # "gitignore" é o factory novo; "gitwildmatch" o antigo (depreciado).
    # Tenta o novo primeiro p/ evitar warning; cai no antigo em versões velhas.
    for factory in ("gitignore", "gitwildmatch"):
        try:
            return pathspec.PathSpec.from_lines(factory, lines)
        except Exception:  # nome de factory não registrado nesta versão
            continue
    return None
```
**Ação:** SUBSTITUIR por:
```
def _read_ignore_lines(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return []


def _rebase_ignore(line: str, base: str) -> list[str]:
    """Reescreve um padrão de ignore de um arquivo em ``base`` (rel posix, sem barra
    final) para casar contra caminhos relativos à RAIZ. Devolve [] p/ vazio/comentário.

    - âncora (`/inicio` ou com `/` no meio): casa só dentro de ``base``;
    - sem âncora (ex.: ``*.log``): casa direto em ``base`` E em qualquer profundidade abaixo.
    """
    s = line.strip()
    if not s or s.startswith("#"):
        return []
    neg = ""
    if s.startswith("!"):
        neg, s = "!", s[1:]
    if not base:  # arquivo na raiz: sem rebase
        return [neg + s]
    trailing = ""
    if s.endswith("/"):
        trailing, s = "/", s[:-1]
    anchored = s.startswith("/") or ("/" in s)
    if s.startswith("/"):
        s = s[1:]
    if anchored:
        return [f"{neg}{base}/{s}{trailing}"]
    return [f"{neg}{base}/{s}{trailing}", f"{neg}{base}/**/{s}{trailing}"]


def _rebase_all(lines: list[str], base: str) -> list[str]:
    out: list[str] = []
    for ln in lines:
        out += _rebase_ignore(ln, base)
    return out


def _collect_ignore_lines(root: Path, cfg: ScanConfig) -> tuple[list[str], list[str]]:
    """Junta as linhas (rebaseadas) de todos os .gitignore e .flatdropignore da árvore.

    Devolve (gitignore_lines, flatdropignore_lines), cada um em ordem raso->fundo.
    """
    gi_by: list[tuple[int, list[str]]] = []
    fd_by: list[tuple[int, list[str]]] = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        cur = Path(dirpath)
        rel = cur.relative_to(root).as_posix()
        base = "" if rel == "." else rel
        depth = 0 if base == "" else base.count("/") + 1
        # não desce nos ignores embutidos (evita varrer node_modules atrás de ignores)
        dirnames[:] = [d for d in dirnames if d not in cfg.dir_ignores]
        if cfg.use_gitignore and ".gitignore" in filenames:
            gi_by.append((depth, _rebase_all(_read_ignore_lines(cur / ".gitignore"), base)))
        if ".flatdropignore" in filenames:
            fd_by.append((depth, _rebase_all(_read_ignore_lines(cur / ".flatdropignore"), base)))
    gi_lines: list[str] = []
    for _, lines in sorted(gi_by, key=lambda t: t[0]):
        gi_lines += lines
    fd_lines: list[str] = []
    for _, lines in sorted(fd_by, key=lambda t: t[0]):
        fd_lines += lines
    return gi_lines, fd_lines


def _make_spec(lines: list[str]):
    if not lines:
        return None
    # "gitignore" é o factory novo; "gitwildmatch" o antigo (depreciado).
    for factory in ("gitignore", "gitwildmatch"):
        try:
            return pathspec.PathSpec.from_lines(factory, lines)
        except Exception:
            continue
    return None


def _build_ignore_specs(root: Path, cfg: ScanConfig):
    """(full, gi, fd): ``full`` = decisão (gitignore + flatdropignore, este por último
    p/ ter a palavra final); ``gi``/``fd`` = só p/ atribuir o motivo e detectar liberação."""
    if not HAS_PATHSPEC:
        return None, None, None
    gi_lines, fd_lines = _collect_ignore_lines(root, cfg)
    if not gi_lines and not fd_lines:
        return None, None, None
    return _make_spec(gi_lines + fd_lines), _make_spec(gi_lines), _make_spec(fd_lines)


def _ignore_status(rel: str, full, gi, fd) -> tuple[bool, str, bool]:
    """(ignored, source, liberated). source ∈ {'gitignore','flatdropignore',''}.
    liberated = o .gitignore pegaria, mas o .flatdropignore liberou (negação)."""
    if full is None:
        return False, "", False
    if full.match_file(rel):
        if fd is not None and fd.match_file(rel):
            return True, "flatdropignore", False
        return True, "gitignore", False
    if gi is not None and gi.match_file(rel):
        return False, "", True
    return False, "", False
```

## EDIÇÃO 3 — core.py `_scan`: montar os três specs

**Âncora:**
```
    spec = _build_gitignore_spec(root, cfg)
```
**Ação:** SUBSTITUIR por:
```
    full_spec, gi_spec, fd_spec = _build_ignore_specs(root, cfg)
```

## EDIÇÃO 4 — core.py `_scan`: motivos de skip do flatdropignore

**Âncora:**
```
    skipped: dict[str, int] = {
        "gitignore": 0,
        "gitignore (pasta)": 0,
        "tipo": 0,
```
**Ação:** SUBSTITUIR por:
```
    skipped: dict[str, int] = {
        "gitignore": 0,
        "gitignore (pasta)": 0,
        "flatdropignore": 0,
        "flatdropignore (pasta)": 0,
        "tipo": 0,
```

## EDIÇÃO 5 — core.py `_scan`: poda de diretório

**Âncora:**
```
            if spec is not None and spec.match_file(rel_sub + "/"):
                note("gitignore (pasta)", rel_sub + "/")
                continue
```
**Ação:** SUBSTITUIR por:
```
            ign, src, _ = _ignore_status(rel_sub + "/", full_spec, gi_spec, fd_spec)
            if ign:
                note(f"{src} (pasta)", rel_sub + "/")
                continue
```

## EDIÇÃO 6 — core.py `_scan`: arquivo

**Âncora:**
```
            if spec is not None and spec.match_file(rel_str):
                note("gitignore", rel_str)
                continue
```
**Ação:** SUBSTITUIR por:
```
            ign, src, _ = _ignore_status(rel_str, full_spec, gi_spec, fd_spec)
            if ign:
                note(src, rel_str)
                continue
```

## EDIÇÃO 7 — tests/test_core.py: testes do flatdropignore (append ao FINAL)

**Ação:** acrescentar ao FINAL do arquivo:
```


def test_flatdropignore_excludes_extra(tmp_path):
    """`.flatdropignore` exclui o que vai para o git mas nao para o Projeto."""
    root = tmp_path / "proj"
    root.mkdir()
    _tree(root, {
        ".flatdropignore": "notas-internas.md\n",
        "notas-internas.md": "x",
        "leiame.md": "y",
    })
    plan = make_plan(root, ScanConfig(mode="collisions"))
    targets = {f.rel.as_posix() for f in plan.files}
    assert "leiame.md" in targets
    assert "notas-internas.md" not in targets
    assert plan.skipped["flatdropignore"] >= 1


def test_flatdropignore_negation_reincludes_gitignored(tmp_path):
    """`!pasta/` no .flatdropignore libera o que o .gitignore bloqueia (ate pasta podada)."""
    root = tmp_path / "proj"
    root.mkdir()
    _tree(root, {
        ".gitignore": "logs/\n",
        ".flatdropignore": "!logs/\n",
        "logs/2026-06-11.md": "a",
        "leiame.md": "b",
    })
    plan = make_plan(root, ScanConfig(mode="collisions"))
    targets = {f.rel.as_posix() for f in plan.files}
    assert "logs/2026-06-11.md" in targets   # liberado de volta pelo !logs/
    assert "leiame.md" in targets


def test_nested_gitignore_scope(tmp_path):
    """`.gitignore` em subpasta vale so para aquela subarvore (aninhado)."""
    root = tmp_path / "proj"
    root.mkdir()
    _tree(root, {
        "Area/.gitignore": "rascunho.md\n",
        "Area/rascunho.md": "r",
        "Area/final.md": "f",
        "outro/rascunho.md": "x",
    })
    plan = make_plan(root, ScanConfig(mode="collisions"))
    targets = {f.rel.as_posix() for f in plan.files}
    assert "Area/final.md" in targets
    assert "Area/rascunho.md" not in targets   # gitignore aninhado pegou
    assert "outro/rascunho.md" in targets      # fora do escopo da subpasta -> mantido
    assert plan.skipped["gitignore"] >= 1
```

## Validação
- `python -m pytest -q` → deve passar **29/29** (26 antigos + 3 novos).
- Manual (opcional): no `cinzeiro`, criar um `.flatdropignore` com `!logs/` e conferir na pré-visualização
  da GUI que os `.md` de `logs/` voltam, e que o motivo dos skips aparece como `flatdropignore` quando aplicável.

## Fora do escopo (próximas)
- Mostrar contador "liberado pelo .flatdropignore" no resumo (a lógica já detecta; só não reporta ainda).
- Documentar `.flatdropignore` no README/CONTEXT (vai no próximo lote de doc).
- `_TREE.md` (próxima spec).
