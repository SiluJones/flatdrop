# spec-0007 — UI-1: seleção de tipos por modal + tela compacta

**Tipo:** código · **Alvo:** `flatdrop/gui.py` · **Autor:** chat · **Aplicador:** Claude Code
**Depende de:** spec-0003 aplicada. (Independe de spec-0005: as âncoras aqui não tocam nos métodos que
a spec-0005 altera — `_on_preview`/`_on_execute`/`_choose_also_md`/`_sources`/imports/maximize. Aplique
spec-0005 e spec-0007 em qualquer ordem.)
**Origem:** design da UI aprovado pelo usuário (modal de tipos, tela compacta) + corrigir a pasta inicial
do "Gerar .bat".

## Objetivo (fase UI-1)
1. Trocar a caixa "Extensões aceitas" e os campos "Só estes/Exceto" por **um botão "Escolher tipos…"**
   que abre um **modal** (checklist categorizado + busca + marcar/limpar por grupo + adicionar tipo custom).
   A tela principal mostra só um resumo ("Tipos: N de M selecionados").
2. O modal vira a ÚNICA forma de mexer em tipo (subsume allowlist + só/exceto por seleção direta).
3. O `.bat` gerado reproduz FIELMENTE a seleção: adições viram `--add-ext`, remoções viram
   `--exclude-ext` (o `cli.py` já reseta `exclude_ext` na fonte de `.md`, então a fonte multi não é afetada).
4. "Gerar .bat…" passa a abrir a janela de salvar na **pasta-pai da raiz**.

## Nota de teste
Sem teste de GUI na suíte. Validar: `python -m pytest -q` segue 26/26 (core/CLI intactos) + **smoke manual
no Windows**: abrir, "Escolher tipos…" (marcar/limpar/buscar/adicionar custom/OK), conferir o resumo,
pré-visualizar, e "Gerar .bat…" conferindo que abre na pasta-pai e que o `.bat` reproduz a seleção.

---

## EDIÇÃO 1 — estado: trocar as vars de tipo por um conjunto

**Âncora:**
```
        self.only_ext_var = tk.StringVar()
        self.exclude_ext_var = tk.StringVar()
        self.also_md_var = tk.BooleanVar(value=False)
        self.also_md_root_var = tk.StringVar()
```
**Ação:** SUBSTITUIR por:
```
        self._selected_exts: set[str] = set(C.DEFAULT_EXTENSIONS)  # allowlist atual (editada no modal)
        self.also_md_var = tk.BooleanVar(value=False)
        self.also_md_root_var = tk.StringVar()
```

## EDIÇÃO 2 — categorias + classe do modal (após o helper `_parse_exts`)

**Âncora (fim do helper `_parse_exts`):**
```
def _parse_exts(text: str) -> set[str]:
    """Converte 'md, py .json' -> {'md','py','json'} (tolerante a vírgula/espaço/ponto)."""
    return {
        e.strip().lstrip(".").lower()
        for e in text.replace("\n", ",").replace(" ", ",").split(",")
        if e.strip()
    }
```
**Ação:** inserir logo APÓS essa função (antes de `class FlatDropApp`):
```


# Agrupamento dos tipos só para EXIBIÇÃO no modal (o que não cair aqui vai para "Outros").
EXT_CATEGORIES: list[tuple[str, set[str]]] = [
    ("Godot", {"gd", "uid", "gdshader", "tscn", "tres", "godot", "import"}),
    ("Linguagens", {
        "py", "js", "ts", "jsx", "tsx", "java", "kt", "kts", "c", "h", "cpp", "hpp",
        "cc", "cxx", "cs", "go", "rs", "rb", "php", "swift", "scala", "clj", "cljs",
        "dart", "lua", "r", "jl", "nim", "zig", "hx", "coffee", "vb", "vbs", "pas",
        "pp", "f90", "f95", "for", "scm", "rkt", "lisp", "sol", "cu", "cuh", "pl",
        "pm", "ex", "exs", "erl", "elm", "fs", "ml", "hs", "groovy", "m", "mm",
        "sh", "bash", "zsh", "fish", "ps1", "psm1", "psd1", "bat", "cmd", "sql"}),
    ("Web e markup", {
        "html", "htm", "css", "scss", "sass", "less", "vue", "svelte", "astro",
        "md", "markdown", "mdx", "rst", "adoc", "asciidoc", "txt", "tex", "org",
        "rmd", "qmd", "xml", "svg"}),
    ("Config e dados", {
        "json", "jsonl", "ndjson", "yaml", "yml", "toml", "ini", "cfg", "conf",
        "env_example", "properties", "editorconfig", "csv", "tsv", "plist", "hcl",
        "tf", "tfvars", "nix", "cmake", "bicep", "gradle", "dockerfile", "makefile",
        "proto", "prisma", "graphql", "gql", "bib"}),
    ("Documentos", {"pdf", "docx", "doc", "xlsx", "rtf", "odt", "epub"}),
    ("Templates", {"hbs", "handlebars", "ejs", "pug", "liquid", "njk", "mustache", "twig"}),
]


def _categorize(exts: list[str]) -> list[tuple[str, list[str]]]:
    """Agrupa as extensões nas categorias de exibição; o resto vai para 'Outros'."""
    out: list[tuple[str, list[str]]] = []
    seen: set[str] = set()
    for name, members in EXT_CATEGORIES:
        group = sorted(e for e in exts if e in members)
        if group:
            out.append((name, group))
            seen.update(group)
    rest = sorted(e for e in exts if e not in seen)
    if rest:
        out.append(("Outros", rest))
    return out


class TypePickerDialog(tk.Toplevel):
    """Modal para escolher tipos por seleção (checklist categorizado + busca)."""

    def __init__(self, master: tk.Misc, selected: set[str], on_ok) -> None:
        super().__init__(master)
        self.title("Escolher tipos de arquivo")
        self.transient(master)
        self.on_ok = on_ok
        self._vars: dict[str, tk.BooleanVar] = {}
        self._rows: list[tuple[str, ttk.Checkbutton]] = []  # (ext, widget) para a busca

        universe = sorted(set(C.DEFAULT_EXTENSIONS) | set(selected))

        # Topo: busca + ações globais.
        top = ttk.Frame(self, padding=8)
        top.pack(fill="x")
        ttk.Label(top, text="Buscar:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._apply_search())
        ttk.Entry(top, textvariable=self.search_var, width=18).pack(side="left", padx=6)
        ttk.Button(top, text="Marcar tudo", command=lambda: self._set_all(True)).pack(side="left", padx=2)
        ttk.Button(top, text="Limpar", command=lambda: self._set_all(False)).pack(side="left", padx=2)
        ttk.Button(top, text="Restaurar padrão", command=self._reset_default).pack(side="left", padx=2)

        # Meio: área rolável (Canvas + Scrollbar + frame interno).
        mid = ttk.Frame(self)
        mid.pack(fill="both", expand=True, padx=8)
        canvas = tk.Canvas(mid, highlightthickness=0, width=580, height=420)
        sb = ttk.Scrollbar(mid, orient="vertical", command=canvas.yview)
        inner = ttk.Frame(canvas)
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw")
        canvas.configure(yscrollcommand=sb.set)
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        # Roda do mouse só enquanto o ponteiro está sobre a lista (não vaza para a tela principal).
        wheel = lambda e: canvas.yview_scroll(int(-e.delta / 120), "units")
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", wheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        for cat, exts in _categorize(universe):
            grp = ttk.LabelFrame(inner, text=cat, padding=6)
            grp.pack(fill="x", pady=4)
            bar = ttk.Frame(grp)
            bar.pack(fill="x")
            ttk.Button(bar, text="marcar grupo", width=13,
                       command=lambda es=exts: self._set_group(es, True)).pack(side="left")
            ttk.Button(bar, text="limpar grupo", width=13,
                       command=lambda es=exts: self._set_group(es, False)).pack(side="left", padx=4)
            grid = ttk.Frame(grp)
            grid.pack(fill="x", pady=(4, 0))
            for i, ext in enumerate(exts):
                var = tk.BooleanVar(value=ext in selected)
                self._vars[ext] = var
                cb = ttk.Checkbutton(grid, text=ext, variable=var, command=self._update_count)
                cb.grid(row=i // 6, column=i % 6, sticky="w", padx=4, pady=1)
                self._rows.append((ext, cb))

        # Rodapé: adicionar tipo custom + contagem + OK/Cancelar.
        bottom = ttk.Frame(self, padding=8)
        bottom.pack(fill="x")
        ttk.Label(bottom, text="Adicionar tipo:").pack(side="left")
        self.add_var = tk.StringVar()
        ttk.Entry(bottom, textvariable=self.add_var, width=10).pack(side="left", padx=4)
        ttk.Button(bottom, text="+", width=3, command=self._add_custom).pack(side="left")
        self.count_lbl = ttk.Label(bottom, text="")
        self.count_lbl.pack(side="left", padx=12)
        ttk.Button(bottom, text="OK", command=self._ok).pack(side="right")
        ttk.Button(bottom, text="Cancelar", command=self.destroy).pack(side="right", padx=6)

        self._update_count()
        self.grab_set()
        master.wait_window(self)

    def _set_all(self, value: bool) -> None:
        for v in self._vars.values():
            v.set(value)
        self._update_count()

    def _set_group(self, exts: list[str], value: bool) -> None:
        for ext in exts:
            if ext in self._vars:
                self._vars[ext].set(value)
        self._update_count()

    def _reset_default(self) -> None:
        for ext, v in self._vars.items():
            v.set(ext in C.DEFAULT_EXTENSIONS)
        self._update_count()

    def _add_custom(self) -> None:
        ext = self.add_var.get().strip().lstrip(".").lower()
        self.add_var.set("")
        if not ext:
            return
        if ext not in self._vars:
            self._vars[ext] = tk.BooleanVar(value=True)
            messagebox.showinfo(
                "FlatDrop",
                f"'{ext}' adicionado e marcado. Reabra o seletor para vê-lo na lista por categoria.")
        else:
            self._vars[ext].set(True)
        self._update_count()

    def _apply_search(self) -> None:
        term = self.search_var.get().strip().lower()
        for ext, w in self._rows:
            if term in ext:
                w.grid()
            else:
                w.grid_remove()

    def _update_count(self) -> None:
        n = sum(1 for v in self._vars.values() if v.get())
        self.count_lbl.config(text=f"Selecionados: {n}")

    def _ok(self) -> None:
        self.on_ok({ext for ext, v in self._vars.items() if v.get()})
        self.destroy()
```

## EDIÇÃO 3 — bloco "Extensões aceitas" → "Tipos de arquivo"

**Âncora (bloco inteiro):**
```
        # Extensões aceitas
        extf = ttk.LabelFrame(self, text="Extensões aceitas (separadas por vírgula ou espaço)", padding=8)
        extf.grid(row=r, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        extf.columnconfigure(0, weight=1)
        self.ext_text = tk.Text(extf, height=3, wrap="word")
        self.ext_text.grid(row=0, column=0, sticky="ew")
        self.ext_text.insert("1.0", ", ".join(sorted(C.DEFAULT_EXTENSIONS)))
        ttk.Button(extf, text="Restaurar padrão", command=self._reset_ext).grid(row=0, column=1, padx=(6, 0), sticky="n")
        r += 1
```
**Ação:** SUBSTITUIR por:
```
        # Tipos de arquivo (seleção via modal)
        typef = ttk.LabelFrame(self, text="Tipos de arquivo", padding=8)
        typef.grid(row=r, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        typef.columnconfigure(0, weight=1)
        self.types_summary = ttk.Label(typef, text="")
        self.types_summary.grid(row=0, column=0, sticky="w")
        ttk.Button(typef, text="Escolher tipos…", command=self._choose_types).grid(row=0, column=1, sticky="e")
        self._update_types_summary()
        r += 1
```

## EDIÇÃO 4 — bloco "Filtros e multi-fonte" → "Multi-fonte" (tira os campos de tipo)

**Âncora (bloco inteiro):**
```
        # Filtros de tipo desta execucao + multi-fonte (opcional)
        ff = ttk.LabelFrame(self, text="Filtros e multi-fonte (opcional)", padding=8)
        ff.grid(row=r, column=0, columnspan=3, sticky="ew", pady=(8, 0))
        ff.columnconfigure(1, weight=1)
        ff.columnconfigure(3, weight=1)
        ttk.Label(ff, text="Só estes tipos:").grid(row=0, column=0, sticky="w")
        ttk.Entry(ff, textvariable=self.only_ext_var).grid(row=0, column=1, sticky="ew", padx=6)
        ttk.Label(ff, text="Exceto estes:").grid(row=0, column=2, sticky="w", padx=(12, 0))
        ttk.Entry(ff, textvariable=self.exclude_ext_var).grid(row=0, column=3, sticky="ew", padx=6)
        ttk.Label(
            ff, foreground="#888",
            text="ex.: md  ·  vazio = usa a allowlist acima; 'Só estes' a ignora; 'Exceto' a subtrai.",
        ).grid(row=1, column=0, columnspan=4, sticky="w", pady=(2, 6))
        ttk.Checkbutton(ff, text="Também incluir todos os .md a partir de:",
                        variable=self.also_md_var).grid(row=2, column=0, columnspan=2, sticky="w")
        ttk.Entry(ff, textvariable=self.also_md_root_var).grid(row=2, column=2, sticky="ew", padx=6)
        ttk.Button(ff, text="Procurar…", command=self._choose_also_md).grid(row=2, column=3, sticky="e")
        r += 1
```
**Ação:** SUBSTITUIR por:
```
        # Multi-fonte (opcional)
        ff = ttk.LabelFrame(self, text="Multi-fonte (opcional)", padding=8)
        ff.grid(row=r, column=0, columnspan=3, sticky="ew", pady=(8, 0))
        ff.columnconfigure(1, weight=1)
        ttk.Checkbutton(ff, text="Também incluir todos os .md a partir de:",
                        variable=self.also_md_var).grid(row=0, column=0, sticky="w")
        ttk.Entry(ff, textvariable=self.also_md_root_var).grid(row=0, column=1, sticky="ew", padx=6)
        ttk.Button(ff, text="Procurar…", command=self._choose_also_md).grid(row=0, column=2, sticky="e")
        r += 1
```

## EDIÇÃO 5 — `_reset_ext` → métodos do modal (resumo, abrir, callback)

**Âncora (método inteiro):**
```
    def _reset_ext(self) -> None:
        self.ext_text.delete("1.0", "end")
        self.ext_text.insert("1.0", ", ".join(sorted(C.DEFAULT_EXTENSIONS)))
```
**Ação:** SUBSTITUIR por:
```
    def _update_types_summary(self) -> None:
        total = len(set(C.DEFAULT_EXTENSIONS) | self._selected_exts)
        self.types_summary.config(
            text=f"Tipos: {len(self._selected_exts)} de {total} selecionados")

    def _choose_types(self) -> None:
        TypePickerDialog(self.winfo_toplevel(), self._selected_exts, self._on_types_chosen)

    def _on_types_chosen(self, selected: set[str]) -> None:
        self._selected_exts = selected
        self._update_types_summary()
```

## EDIÇÃO 6 — `_gather_cfg` usa o conjunto selecionado

**Âncora (método inteiro):**
```
    def _gather_cfg(self) -> core.ScanConfig:
        raw = self.ext_text.get("1.0", "end")
        exts = {
            e.strip().lstrip(".").lower()
            for e in raw.replace("\n", ",").replace(" ", ",").split(",")
            if e.strip()
        }
        return core.ScanConfig(
            mode=self.mode_var.get(),
            sep=self.sep_var.get() or C.DEFAULT_SEP,
            use_gitignore=self.gitignore_var.get(),
            include_sensitive=not self.skip_sensitive_var.get(),
            extensions=exts or set(C.DEFAULT_EXTENSIONS),
            clear_dest=self.clear_var.get(),
            write_manifest=self.manifest_var.get(),
            only_ext=(_parse_exts(self.only_ext_var.get()) or None),
            exclude_ext=_parse_exts(self.exclude_ext_var.get()),
        )
```
**Ação:** SUBSTITUIR por:
```
    def _gather_cfg(self) -> core.ScanConfig:
        return core.ScanConfig(
            mode=self.mode_var.get(),
            sep=self.sep_var.get() or C.DEFAULT_SEP,
            use_gitignore=self.gitignore_var.get(),
            include_sensitive=not self.skip_sensitive_var.get(),
            extensions=self._selected_exts or set(C.DEFAULT_EXTENSIONS),
            clear_dest=self.clear_var.get(),
            write_manifest=self.manifest_var.get(),
        )
```

## EDIÇÃO 7 — `_build_cli_args`: reproduzir a seleção (add + exclude)

**Âncora (a seção de tipos):**
```
        only = _parse_exts(self.only_ext_var.get())
        if only:
            args += ["--only-ext", ",".join(sorted(only))]
        exc = _parse_exts(self.exclude_ext_var.get())
        if exc:
            args += ["--exclude-ext", ",".join(sorted(exc))]
        # extensões ADICIONADAS à allowlist (delta sobre o default) -> --add-ext.
        # (Remoções da allowlist não são serializadas; para tirar tipos use 'Exceto estes'.)
        cur = _parse_exts(self.ext_text.get("1.0", "end"))
        added = sorted(cur - set(C.DEFAULT_EXTENSIONS))
        if added and not only:  # only-ext já ignora a allowlist
            args += ["--add-ext", ",".join(added)]
```
**Ação:** SUBSTITUIR por:
```
        # A allowlist do modal é reproduzida fielmente: adições viram --add-ext e
        # remoções viram --exclude-ext. O cli reseta exclude_ext na fonte de .md,
        # então a coleta multi-fonte de .md não é afetada pelas remoções.
        default = set(C.DEFAULT_EXTENSIONS)
        added = sorted(self._selected_exts - default)
        removed = sorted(default - self._selected_exts)
        if added:
            args += ["--add-ext", ",".join(added)]
        if removed:
            args += ["--exclude-ext", ",".join(removed)]
```

## EDIÇÃO 8 — "Gerar .bat…" abre na pasta-pai da raiz

**Âncora:**
```
        path = filedialog.asksaveasfilename(
            title="Salvar .bat", defaultextension=".bat",
            initialfile=name + ".bat", filetypes=[("Arquivo .bat", "*.bat")])
```
**Ação:** SUBSTITUIR por:
```
        root = self.root_var.get().strip()
        initial = str(Path(root).parent) if root and Path(root).is_dir() else None
        path = filedialog.asksaveasfilename(
            title="Salvar .bat", defaultextension=".bat", initialdir=initial,
            initialfile=name + ".bat", filetypes=[("Arquivo .bat", "*.bat")])
```

## Validação
- `python -m pytest -q` → 26/26.
- Smoke manual (Windows): a tela principal fica compacta (sem a caixa de extensões nem os campos só/exceto);
  "Escolher tipos…" abre o modal; marcar/limpar/buscar/adicionar custom/OK atualiza o resumo;
  pré-visualizar respeita a seleção; "Gerar .bat…" abre na pasta-pai e o `.bat` reproduz a seleção
  (some um tipo no modal → o `.bat` ganha `--exclude-ext <tipo>`).
