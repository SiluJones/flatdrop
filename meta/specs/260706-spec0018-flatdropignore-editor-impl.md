# 260706-spec0018 — Editor visual de `.flatdropignore` na GUI (implementação)

> **Tipo:** spec de **implementação** (Fase 2-D). Parte das 3 decisões já fechadas na
> **DEC-016** (checkbox binário / bloco gerenciado / spike feito) e do código do gerador
> **verificado rodando o `make_plan` real** nesta sessão. Aplica o Code, roda
> `python -m pytest -q`, smoke manual da GUI no Windows, e commita.
>
> **Bump:** 0.3.1 → **0.4.0** (fecha o item "editor de `.flatdropignore`" do ROADMAP).

## 0. Achado que revisa a spec0017 §5 (importante)

A verificação em sandbox expôs uma **assimetria do gitignore** que o §5 subestimava:

- **`dir/` + `!dir/arquivo` NÃO reinclui** o arquivo (regra "não dá para reincluir um
  arquivo se a pasta-pai está excluída").
- **Liberar** itens de uma pasta que o git esconde exige **reincluir a pasta**
  (`!dir/`) e depois **re-excluir por folha** os indesejados (re-exclusão vale em
  qualquer profundidade). `!dir/` sozinho já traz tudo em qualquer profundidade
  (confirmado: `!dir/**` é desnecessário).
- **Excluir** do lado versionado (base incluída) sai **por folha** (`caminho`), em
  qualquer profundidade.

O gerador abaixo já implementa essa assimetria e foi validado: liberar `logs/` querendo
só `logs/run.md` gera `!logs/` + re-exclusão de `logs/skip.md` e `logs/deep/c.md`, e o
`make_plan` real copia exatamente `logs/run.md`.

## 1. Edição A — core.py: anotação da árvore + gerador (novo bloco)

**Âncora:** inserir logo após a função `_ignore_status` (que termina em
`    return False, "", False`) e ANTES do separador `# Varredura` / `def _scan(`.

**Inserir:**

```python
# --------------------------------------------------------------------------- #
# Editor de .flatdropignore (spec0018): anotacao da arvore + geracao dos padroes
# --------------------------------------------------------------------------- #
FLATDROP_EDITOR_MARK_A = "# >>> flatdrop-editor"
FLATDROP_EDITOR_MARK_B = "# <<<"


def _ignore_probes(root: Path, cfg: ScanConfig):
    """(base_in, source): dizem, por caminho, se ele iria ao Projeto com os ignores
    atuais e qual a fonte do ignore. Pastas sao sondadas com barra final (semantica
    gitignore de diretorio) — sem isso, `dist/` nao casa a string `dist`."""
    full, gi, fd = _build_ignore_specs(root, cfg)

    def base_in(rel: str, is_dir: bool) -> bool:
        if full is None:
            return True
        return not full.match_file(rel + "/" if is_dir else rel)

    def source(rel: str, is_dir: bool) -> str:
        if full is None:
            return ""
        _ig, src, _lib = _ignore_status((rel + "/") if is_dir else rel, full, gi, fd)
        return src

    return base_in, source


def annotate_children(root, cfg: ScanConfig, rel_dir: str = "", probes=None):
    """Anota os filhos DIRETOS de ``rel_dir`` (nao recursivo) — para o lazy load da GUI.

    Cada item: ``(rel, is_dir, base_in, source, allowed_type, sensitive)``. Poda o
    nucleo imutavel (``dir_ignores``/``file_ignores``) e DESCE em pasta gitignored (o
    editor mostra o que o git esconde para o autor poder liberar via ``!``).
    """
    root = Path(root)
    base_in, source = probes or _ignore_probes(root, cfg)
    abs_dir = root / rel_dir if rel_dir else root
    try:
        entries = sorted(
            os.scandir(abs_dir),
            key=lambda e: (not e.is_dir(follow_symlinks=False), e.name.lower()),
        )
    except OSError:
        return
    for e in entries:
        is_dir = e.is_dir(follow_symlinks=False)
        if is_dir and e.name in cfg.dir_ignores:
            continue
        if (not is_dir) and e.name in cfg.file_ignores:
            continue
        rel = f"{rel_dir}/{e.name}" if rel_dir else e.name
        if is_dir:
            yield (rel, True, base_in(rel, True), source(rel, True), True, False)
        else:
            yield (rel, False, base_in(rel, False), source(rel, False),
                   is_allowed_type(e.name, cfg), is_sensitive(e.name))


def _walk_leaves(root: Path, cfg: ScanConfig, probes):
    """(leaves, gi_dirs, base): todas as folhas (arquivos) + pastas gitignored, recursivo
    — insumo do gerador. ``base`` = {rel: base_in} por folha."""
    root = Path(root)
    base_in, source = probes
    leaves: list[str] = []
    gi_dirs: list[str] = []
    base: dict[str, bool] = {}
    for dp, dns, fns in os.walk(root, followlinks=False):
        rel_dir = Path(dp).relative_to(root).as_posix()
        rel_dir = "" if rel_dir == "." else rel_dir
        dns[:] = sorted(d for d in dns if d not in cfg.dir_ignores)
        for d in dns:
            rel = f"{rel_dir}/{d}" if rel_dir else d
            if not base_in(rel, True) and source(rel, True) == "gitignore":
                gi_dirs.append(rel)
        for fn in sorted(fns):
            if fn in cfg.file_ignores:
                continue
            rel = f"{rel_dir}/{fn}" if rel_dir else fn
            leaves.append(rel)
            base[rel] = base_in(rel, False)
    return leaves, sorted(gi_dirs), base


def build_flatdropignore(root, cfg: ScanConfig, wants: dict[str, bool],
                         existing_text: str | None = None) -> str:
    """Gera o texto do ``.flatdropignore`` (bloco gerenciado) a partir de ``wants``.

    ``wants``: ``{rel_arquivo: bool}`` — inclusao desejada por FOLHA; ausentes seguem o
    baseline do git. Respeita a assimetria do gitignore (ver spec0018 §0):
    - LIBERAR: para cada pasta gitignored com alguma folha desejada, ``!dir/`` +
      re-exclui (``dir/arquivo``) as folhas indesejadas sob ela (senao vazam);
    - EXCLUIR: folhas versionadas que o autor tirou saem por folha.
    Preserva linhas fora do bloco gerenciado (round-trip, DEC-016 opcao i).
    """
    root = Path(root)
    probes = _ignore_probes(root, cfg)
    leaves, gi_dirs, base = _walk_leaves(root, cfg, probes)
    want_of = lambda rel: wants.get(rel, base.get(rel, True))

    def nearest_gi(rel: str):
        best = None
        for g in gi_dirs:
            if rel.startswith(g + "/") and (best is None or len(g) > len(best)):
                best = g
        return best

    liberate: list[str] = []
    reexclude: list[str] = []
    exclude: list[str] = []
    freed: set[str] = set()
    for g in gi_dirs:
        under = [l for l in leaves if l.startswith(g + "/")]
        # so libera se ha algo desejado e a pasta nao esta sob outra ja liberada
        if any(want_of(l) for l in under) and not any(g.startswith(o + "/") for o in freed):
            liberate.append(f"!{g}/")
            freed.add(g)
            for l in under:
                if not want_of(l):
                    reexclude.append(l)
    for l in leaves:
        if base.get(l, True) and not want_of(l) and nearest_gi(l) is None:
            exclude.append(l)

    block = liberate + sorted(set(reexclude)) + sorted(set(exclude))
    body = "\n".join(block) if block else "# (sem alteracoes)"
    managed = f"{FLATDROP_EDITOR_MARK_A}\n{body}\n{FLATDROP_EDITOR_MARK_B}"
    if existing_text and FLATDROP_EDITOR_MARK_A in existing_text and FLATDROP_EDITOR_MARK_B in existing_text:
        pre = existing_text.split(FLATDROP_EDITOR_MARK_A)[0].rstrip("\n")
        pos = existing_text.split(FLATDROP_EDITOR_MARK_B, 1)[1].lstrip("\n")
        return "\n".join(p for p in (pre, managed, pos) if p) + "\n"
    if existing_text and existing_text.strip():
        return existing_text.rstrip("\n") + "\n\n" + managed + "\n"
    return managed + "\n"
```

## 2. Edição B — test_core.py: testes do gerador (append no fim)

**Âncora:** fim do arquivo. **Inserir:**

```python
# --------------------------------------------------------------------------- #
# Editor de .flatdropignore (spec0018)
# --------------------------------------------------------------------------- #
def _editor_repo(tmp_path):
    for p in ("logs/run.md", "logs/skip.md", "logs/deep/c.md",
              "docs/a.md", "docs/b.md", "docs/keep.md", "README.md", "src/app.py"):
        f = tmp_path / p
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("x", encoding="utf-8")
    (tmp_path / ".gitignore").write_text("logs/\n", encoding="utf-8")  # logs escondido; docs versionado
    return tmp_path


def _copied(root):
    plan = core.make_plan(str(root), core.ScanConfig(mode="collisions"))
    return sorted(str(f.rel) for f in plan.files)


@pytest.mark.skipif(not core.HAS_PATHSPEC, reason="requer pathspec")
def test_editor_liberate_only_one(tmp_path):
    root = _editor_repo(tmp_path)
    txt = core.build_flatdropignore(str(root), core.ScanConfig(mode="collisions"),
                                    {"logs/run.md": True})
    (root / ".flatdropignore").write_text(txt, encoding="utf-8")
    got = _copied(root)
    assert "logs/run.md" in got                       # liberado
    assert "logs/skip.md" not in got                  # re-excluido (nao vazou)
    assert "logs/deep/c.md" not in got                # re-excluido em profundidade
    assert "docs/a.md" in got                         # nao tocado -> segue incluido


@pytest.mark.skipif(not core.HAS_PATHSPEC, reason="requer pathspec")
def test_editor_exclude_keeps_sibling(tmp_path):
    root = _editor_repo(tmp_path)
    txt = core.build_flatdropignore(str(root), core.ScanConfig(mode="collisions"),
                                    {"docs/a.md": False, "docs/b.md": False})
    (root / ".flatdropignore").write_text(txt, encoding="utf-8")
    got = _copied(root)
    assert "docs/keep.md" in got
    assert "docs/a.md" not in got and "docs/b.md" not in got


@pytest.mark.skipif(not core.HAS_PATHSPEC, reason="requer pathspec")
def test_editor_roundtrip_preserves_manual(tmp_path):
    root = _editor_repo(tmp_path)
    existing = ("# regra minha\n*.tmp\n\n"
                + core.FLATDROP_EDITOR_MARK_A + "\nlogs/x\n" + core.FLATDROP_EDITOR_MARK_B + "\n")
    txt = core.build_flatdropignore(str(root), core.ScanConfig(mode="collisions"),
                                    {"docs/a.md": False}, existing_text=existing)
    assert "# regra minha" in txt and "*.tmp" in txt          # linhas manuais preservadas
    assert txt.count(core.FLATDROP_EDITOR_MARK_A) == 1         # um unico bloco gerenciado
    assert "docs/a.md" in txt
```

> Nota: os testes já contam com `import pytest` e `from flatdrop import core` no topo do
> arquivo (padrão da suíte); se algum faltar, adicionar. São 3 testes novos → 41 → **44**.

## 3. Edição C — gui.py: o modal `FlatDropIgnoreEditor`

**Âncora:** inserir imediatamente ANTES de `class FlatDropApp(ttk.Frame):`.

**Inserir** (adaptado do spike já validado no Windows; Opção B — checkbox binário,
tri-state por pasta, lazy load; grava via `core.build_flatdropignore`):

```python
_GLYPH = {True: "\u2611", False: "\u2610", None: "\u25a3"}  # checked / unchecked / partial


class FlatDropIgnoreEditor(tk.Toplevel):
    """Editor visual do .flatdropignore (Opcao B): marca-se 'quero no Projeto'; a
    ferramenta deriva `!`/exclusao. Le a arvore via core.annotate_children (lazy) e
    grava via core.build_flatdropignore (bloco gerenciado). Ver DEC-016 / spec0018."""

    def __init__(self, master, root_dir: str, cfg, on_saved=None):
        super().__init__(master)
        self.title("Editar .flatdropignore")
        self.geometry("820x560")
        self.root_dir = Path(root_dir)
        self.cfg = cfg
        self.on_saved = on_saved
        self.probes = core._ignore_probes(self.root_dir, cfg)
        self.st: dict[str, dict] = {}
        self.folder_override: dict[str, bool] = {}
        self._build()
        self._populate("", "")
        self.transient(master)
        self.grab_set()

    # ----- construcao ----- #
    def _build(self):
        self.tree = ttk.Treeview(self, columns=("chk",), selectmode="browse")
        self.tree.heading("#0", text="Arquivo / pasta")
        self.tree.heading("chk", text="No Projeto")
        self.tree.column("chk", width=90, anchor="center", stretch=False)
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        bar = ttk.Frame(self, padding=6)
        bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        ttk.Button(bar, text="Salvar .flatdropignore", command=self._save).pack(side="right")
        ttk.Button(bar, text="Cancelar", command=self.destroy).pack(side="right", padx=6)
        self.info = ttk.Label(bar, text="", foreground="#888")
        self.info.pack(side="left")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.tree.tag_configure("in", foreground="#137333")
        self.tree.tag_configure("out", foreground="#9aa0a6")
        self.tree.tag_configure("freed", foreground="#1a73e8")
        self.tree.bind("<Button-1>", self._on_click)
        self.tree.bind("<<TreeviewOpen>>", self._on_open)
        self.tree.bind("<space>", lambda e: (self._toggle(self.tree.focus()), "break")[1])

    # ----- populacao / lazy ----- #
    def _populate(self, parent_iid, rel_dir):
        inherited = self._nearest_override(rel_dir)
        for rel, is_dir, base_in, src, allowed, sens in core.annotate_children(
                self.root_dir, self.cfg, rel_dir, self.probes):
            want = inherited if inherited is not None else base_in
            note = ""
            if not is_dir and not allowed:
                note = "  (nao vem: tipo)"
            elif not is_dir and sens:
                note = "  (barrado: sensivel)"
            name = rel.rsplit("/", 1)[-1] + note
            iid = self.tree.insert(parent_iid, "end", text=name, values=(_GLYPH[want],))
            self.st[iid] = dict(path=rel, is_dir=is_dir, base_in=base_in,
                                allowed=allowed, sens=sens, loaded=not is_dir, want=want)
            self._style(iid, want)
            if is_dir:
                self.tree.insert(iid, "end", text="(carregando...)")

    def _on_open(self, _e):
        iid = self.tree.focus()
        s = self.st.get(iid)
        if not s or s["loaded"]:
            return
        for c in self.tree.get_children(iid):
            self.tree.delete(c)
        self._populate(iid, s["path"])
        s["loaded"] = True
        self._refresh_chain(iid)

    def _nearest_override(self, rel_dir):
        cur = rel_dir
        while cur:
            if cur in self.folder_override:
                return self.folder_override[cur]
            cur = cur.rsplit("/", 1)[0] if "/" in cur else ""
        return self.folder_override.get("", None)

    # ----- toggle ----- #
    def _on_click(self, e):
        region = self.tree.identify("region", e.x, e.y)
        col = self.tree.identify_column(e.x)
        row = self.tree.identify_row(e.y)
        if row and region == "cell" and col == "#1":
            self._toggle(row)
            return "break"

    def _toggle(self, iid):
        if not iid or iid not in self.st:
            return
        s = self.st[iid]
        new = not self._eff_want(iid)
        if s["is_dir"]:
            self.folder_override[s["path"]] = new
            self._set_sub(iid, new)
        s["want"] = new
        self._set_glyph(iid, new)
        self._refresh_chain(iid)

    def _set_sub(self, iid, val):
        for c in self.tree.get_children(iid):
            cs = self.st.get(c)
            if not cs:
                continue
            cs["want"] = val
            if cs["is_dir"]:
                self.folder_override[cs["path"]] = val
                self._set_sub(c, val)
            self._set_glyph(c, val)

    def _eff_want(self, iid):
        s = self.st[iid]
        if s["is_dir"] and s["loaded"]:
            st = self._folder_state(iid)
            return st in (True, None)
        return bool(s["want"])

    def _folder_state(self, iid):
        vals = []
        for c in self.tree.get_children(iid):
            cs = self.st.get(c)
            if not cs:
                continue
            vals.append(self._folder_state(c) if cs["is_dir"] and cs["loaded"] else cs["want"])
        if not vals:
            return self.st[iid]["want"]
        if all(v is True for v in vals):
            return True
        if all(v is False for v in vals):
            return False
        return None

    def _refresh_chain(self, iid):
        cur = self.tree.parent(iid)
        while cur:
            self._set_glyph(cur, self._folder_state(cur))
            cur = self.tree.parent(cur)

    def _set_glyph(self, iid, state):
        self.tree.set(iid, "chk", _GLYPH[state])
        self._style(iid, state)

    def _style(self, iid, state):
        s = self.st[iid]
        goes = state in (True, None)
        tag = "freed" if (goes and not s["base_in"]) else ("in" if goes else "out")
        self.tree.item(iid, tags=(tag,))

    # ----- salvar ----- #
    def _collect_wants(self):
        # forca carregar as pastas com override para resolver as folhas
        for iid, s in list(self.st.items()):
            if s["is_dir"] and not s["loaded"] and s["path"] in self.folder_override:
                self.tree.focus(iid)
                self._on_open(None)
        wants = {}
        for s in self.st.values():
            if not s["is_dir"]:
                wants[s["path"]] = bool(s["want"])
        return wants

    def _save(self):
        wants = self._collect_wants()
        target = self.root_dir / ".flatdropignore"
        existing = target.read_text(encoding="utf-8") if target.exists() else None
        text = core.build_flatdropignore(self.root_dir, self.cfg, wants, existing_text=existing)
        target.write_text(text, encoding="utf-8")
        if self.on_saved:
            self.on_saved(target)
        self.destroy()
```

> Imports em `gui.py`: já há `from pathlib import Path`, `tkinter as tk`, `ttk`. O
> editor usa `core._ignore_probes`/`annotate_children`/`build_flatdropignore` — funções
> do core (não é lógica na GUI; a GUI só coleta marcações e renderiza).

## 4. Edição D — gui.py: botão + handler

**Âncora do botão:** em `_build`, inserir ANTES do comentário `# Multi-fonte (opcional)`.
**Inserir:**

```python
        # Editor visual do .flatdropignore
        ignf = ttk.LabelFrame(self, text="Ignore (.flatdropignore)", padding=8)
        ignf.grid(row=r, column=0, columnspan=3, sticky="ew", pady=(8, 0))
        ignf.columnconfigure(0, weight=1)
        ttk.Label(ignf, text="Editar visualmente o que vai ao Projeto (gera o arquivo na raiz).").grid(row=0, column=0, sticky="w")
        ttk.Button(ignf, text="Editar .flatdropignore…", command=self._edit_ignore).grid(row=0, column=1, sticky="e")
        r += 1
```

**Âncora do handler:** logo após o método `_on_types_chosen` (antes do separador
`# Coleta de configuração`). **Inserir:**

```python
    def _edit_ignore(self) -> None:
        root = self.root_var.get().strip()
        if not self._validate_root():
            return
        FlatDropIgnoreEditor(self.winfo_toplevel(), root, self._gather_cfg(),
                             on_saved=self._on_ignore_saved)

    def _on_ignore_saved(self, path) -> None:
        self._write(f"[.flatdropignore gravado] {path}\n")
        self.status.config(text=".flatdropignore atualizado")
```

## 5. Validação

- **pytest:** `python -m pytest -q` → **44 verdes** (41 + 3). Os 3 novos exercitam o
  gerador contra o `make_plan` real (liberação sem vazamento, exclusão preservando
  irmão, round-trip).
- **Smoke manual (Windows)** — a GUI não é coberta pela suíte:
  1. Abrir a GUI, escolher uma raiz com `.gitignore`, clicar "Editar .flatdropignore…".
  2. Marcar/desmarcar pastas e arquivos; conferir tri-state e lazy load (validados no
     spike).
  3. Salvar; abrir o `.flatdropignore` na raiz e conferir o bloco gerenciado; rodar o
     FlatDrop e ver o resultado no `_TREE.md`.
  4. Repetir com um `.flatdropignore` que já tenha linhas manuais → conferir que foram
     preservadas fora do bloco.
- **Print para o README:** a janela do editor com a árvore + checkboxes é boa captura
  para documentar a Fase 2-D (não gerar imagem, só marcar a tela).

## 6. Fecho (docs + versão)

- Bump **0.4.0** em `config.py` (ou onde vive `__version__`) e nova entrada no
  `CHANGELOG.md` ("Added: editor visual de `.flatdropignore` na GUI").
- `STATUS.md`: mover o item 2 (editor) de backlog para entregue; próxima passa a ser o
  item C (persistência).
- `DECISIONS.md`: se desejado, um FIX/DEC curto registrando a assimetria do gitignore
  (spec0018 §0) como armadilha canônica — evita alguém "otimizar" para `dir/`+`!dir/x`
  no futuro.

## 7. Commit (entregar pronto, sem acento)

```
git add -A && git commit -m "feat(gui): editor visual de .flatdropignore (Fase 2-D)" -m "Adiciona annotate_children e build_flatdropignore no core (gerador que respeita a assimetria do gitignore: liberar via !dir/ + re-exclusao; excluir por folha) e o modal FlatDropIgnoreEditor na gui, com bloco gerenciado no round-trip. 3 testes novos (44 verdes). Fecha spec0018 / DEC-016. Bump 0.4.0."
```
