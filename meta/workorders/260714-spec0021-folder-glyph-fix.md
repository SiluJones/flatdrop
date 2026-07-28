# 260714-spec0021 — Glifo da pasta correto na visão colapsada (correção)

> **Tipo:** implementação (correção). Fecha a última pendência do editor visual.
> **Bump:** 0.5.1 → **0.5.2**.

## 0. Problema e causa raiz (diagnosticado, não suposto)

Ao abrir o editor numa raiz que já tem `.flatdropignore`, uma pasta com conteúdo
**parcialmente excluído** (ex.: `meta/`, que contém `meta/specs/` excluído) aparece
**☑ marcada** em vez de **▣ indeterminada**. O estado só se corrige **depois de expandir**
a pasta — "só sinaliza após alcançar a pasta na árvore".

**Causa raiz:** `_folder_state` calcula o estado a partir dos **filhos carregados na
árvore**, e o lazy load só carrega ao expandir. Sem filhos, a função cai no
`return self.st[iid]["want"]` — o `want` da **própria pasta** (que não está ignorada) —
e devolve ☑. Confirmado por simulação da lógica: colapsado → `CHECK` (errado);
expandido → `PARTIAL` (correto). O fix da spec0020 (`_on_open` recomputa o glifo) estava
certo, mas **só age ao expandir**; a visão inicial continua mentindo.

O dado necessário **já existe no core** e não depende de UI: `annotate_children` marca
`meta/specs` com `base_in=False` corretamente. A correção é o glifo **perguntar ao core**
o estado agregado da subárvore, em vez de olhar os filhos da `Treeview`.

## 1. Edição A — core.py: `folder_effective_state` (novo, testável)

**Âncora:** inserir logo após a função `_walk_leaves` (antes de `def build_flatdropignore(`).
**Inserir:**

```python
def folder_effective_state(root, cfg: ScanConfig, rel_dir: str, probes=None):
    """Estado agregado de uma pasta, SEM depender do lazy load da GUI (spec0021).

    Retorna ``True`` (todas as folhas sob ela iriam ao Projeto), ``False`` (nenhuma) ou
    ``None`` (misto -> checkbox indeterminado). Pasta vazia cai no proprio estado dela.
    A GUI usa isto para pintar o glifo mesmo com a pasta colapsada — antes, o estado vinha
    dos filhos ja carregados na arvore, entao uma pasta nao expandida mentia (FIX-007).
    """
    root = Path(root)
    base_in, source = probes or _ignore_probes(root, cfg)
    leaves, _gd, _b = _walk_leaves(root, cfg, (base_in, source))
    prefix = rel_dir + "/"
    under = [l for l in leaves if l.startswith(prefix)]
    if not under:
        return base_in(rel_dir, True)
    vals = [base_in(l, False) for l in under]
    if all(vals):
        return True
    if not any(vals):
        return False
    return None
```

> **Performance:** `_walk_leaves` varre a subárvore inteira. Para não repetir a varredura a
> cada pasta, a GUI a chama **uma vez por pasta ao popular** (não a cada clique) — ver §2.
> Se em repo muito grande isso pesar, o passo seguinte é `_walk_leaves` receber um
> `rel_dir` inicial (otimização deixada de fora agora: mudança mínima primeiro).

## 2. Edição B — gui.py: o glifo inicial vem do core

**B.1 — ao popular.** **Âncora:** em `FlatDropIgnoreEditor._populate`, o bloco

```python
            want = inherited if inherited is not None else base_in
```

**Substituir por:**

```python
            if inherited is not None:
                want = inherited          # pasta ancestral marcada como um todo vence
            elif is_dir:
                # estado agregado real da subarvore (nao depende de expandir) — spec0021
                want = core.folder_effective_state(self.root_dir, self.cfg, rel, self.probes)
            else:
                want = base_in
```

> `want` de pasta passa a poder ser `None` (indeterminado). `_GLYPH` já mapeia `None` → ▣ e
> `_style` já trata `None` como "vai" (`state in (True, None)`), então a pintura funciona.

**B.2 — o estado da pasta prefere os filhos carregados, senão o do core.**
**Âncora:** o corpo de `_folder_state`, a linha

```python
        if not vals:
            return self.st[iid]["want"]
```

**Substituir por:**

```python
        if not vals:
            return self.st[iid]["want"]  # ja e o agregado do core quando nao expandida
```

(Comentário apenas — o retorno agora está correto porque `want` de pasta não expandida
já é o agregado calculado em B.1.)

**B.3 — o toggle continua binário.** `_toggle` faz `new = not self._eff_want(iid)`, e
`_eff_want` trata `None` como "vai" → clicar numa pasta ▣ **desmarca tudo** (comportamento
que o autor já validou no spike e aprovou). Nada a mudar.

## 3. Edição C — test_core.py: teste do estado agregado (append)

```python
@pytest.mark.skipif(not core.HAS_PATHSPEC, reason="requer pathspec")
def test_folder_effective_state(tmp_path):
    for p in ("meta/specs/s1.md", "meta/refs/r.md", "logs/a.md", "README.md"):
        f = tmp_path / p
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("x", encoding="utf-8")
    (tmp_path / ".gitignore").write_text("", encoding="utf-8")
    (tmp_path / ".flatdropignore").write_text(
        core.FLATDROP_EDITOR_MARK_A + "\nlogs/\nmeta/specs/\n" + core.FLATDROP_EDITOR_MARK_B + "\n",
        encoding="utf-8")
    cfg = core.ScanConfig(mode="collisions")
    st = lambda d: core.folder_effective_state(str(tmp_path), cfg, d)
    assert st("meta") is None       # misto -> indeterminado (o bug dos prints)
    assert st("meta/specs") is False
    assert st("meta/refs") is True
    assert st("logs") is False
```

1 teste novo → 48 → **49**.

## 4. Validação

- `python -m pytest -q` → **49 verdes**.
- **Smoke manual (Windows) — é o teste que importa:** abrir o editor numa raiz com
  `.flatdropignore` que exclua `logs/` e `meta/specs/`. **Sem expandir nada**, conferir:
  `logs` ☐, `meta` ▣ (indeterminado), demais ☑. Expandir `meta` → `refs` ☑, `specs` ☐, e
  `meta` continua ▣. Clicar em `meta` ▣ → desmarca tudo; remarcar filhos → volta a ▣.

## 5. Fecho

- **Bump 0.5.2**; `CHANGELOG.md` *Fixed:* glifo da pasta correto na visão colapsada.
- **FIX-007:** o estado de checkbox de pasta não pode derivar dos filhos carregados na
  árvore (lazy load faz a visão colapsada mentir) — deriva do core
  (`folder_effective_state`). Impede a regressão de "otimizar" de volta para a árvore.
- **STATUS.md:** editor de `.flatdropignore` (Fase 2-D) fechado; próxima = item C.

## 6. Commit (pronto, sem acento)

```
git add -A && git commit -m "fix(gui): glifo de pasta correto na visao colapsada do editor" -m "Adiciona core.folder_effective_state (agregado da subarvore: todas/nenhuma/misto) e a GUI passa a pintar o checkbox de pasta a partir dele, em vez dos filhos carregados na arvore — o lazy load fazia a pasta colapsada aparecer marcada mesmo com conteudo excluido. 1 teste novo (49). FIX-007. Bump 0.5.2."
```
