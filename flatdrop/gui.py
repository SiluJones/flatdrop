"""Interface gráfica (tkinter) do FlatDrop.

A GUI não contém regra de negócio: ela coleta opções, chama a core numa
thread (para não travar a janela) e renderiza o resultado. Toda manipulação
de widget acontece na thread principal via ``self.after`` — tkinter não é
thread-safe.
"""

from __future__ import annotations

import os
import subprocess
import sys
import threading
from dataclasses import replace
from pathlib import Path

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

from . import config as C
from . import core
from . import settings as settings_store


def _parse_exts(text: str) -> set[str]:
    """Converte 'md, py .json' -> {'md','py','json'} (tolerante a vírgula/espaço/ponto)."""
    return {
        e.strip().lstrip(".").lower()
        for e in text.replace("\n", ",").replace(" ", ",").split(",")
        if e.strip()
    }


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


_GLYPH = {True: "☑", False: "☐", None: "▣"}  # checked / unchecked / partial


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
            if inherited is not None:
                want = inherited          # pasta ancestral marcada como um todo vence
            elif is_dir:
                # estado agregado real da subarvore (nao depende de expandir) — spec0021
                want = core.folder_effective_state(self.root_dir, self.cfg, rel, self.probes)
            else:
                want = base_in
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
        self._set_glyph(iid, self._folder_state(iid))  # recomputa a propria pasta
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
            return self.st[iid]["want"]  # ja e o agregado do core quando nao expandida
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
        target = core.flatdropignore_path(self.root_dir)
        existing = target.read_text(encoding="utf-8") if target.exists() else None
        text = core.build_flatdropignore(self.root_dir, self.cfg, wants, existing_text=existing)
        target.write_text(text, encoding="utf-8")
        if self.on_saved:
            self.on_saved(target)
        self.destroy()


class FlatDropApp(ttk.Frame):
    """Janela principal do FlatDrop."""

    def __init__(self, master: tk.Tk, *, start_dir: str | None = None) -> None:
        super().__init__(master, padding=12)
        master.title(f"FlatDrop {core.__import__('flatdrop').__version__}"
                     if False else "FlatDrop — achatar projeto para o Claude")
        master.minsize(720, 620)
        try:
            master.state("zoomed")  # abre maximizada (Windows; alguns Linux)
        except tk.TclError:
            try:
                master.attributes("-zoomed", True)  # fallback X11
            except tk.TclError:
                pass
        self.grid(row=0, column=0, sticky="nsew")
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)

        # estado
        self.root_var = tk.StringVar()
        self.dest_var = tk.StringVar(value=str(core.default_downloads_dir()))
        self.name_var = tk.StringVar()
        self.mode_var = tk.StringVar(value="collisions")
        self.sep_var = tk.StringVar(value=C.DEFAULT_SEP)
        self.name_meta_var = tk.BooleanVar(value=True)  # nomear meta c/ a pasta (spec0036)
        self.gitignore_var = tk.BooleanVar(value=True)
        self.skip_sensitive_var = tk.BooleanVar(value=True)
        self.clear_var = tk.BooleanVar(value=True)
        self.manifest_var = tk.BooleanVar(value=True)
        self.tree_var = tk.BooleanVar(value=False)  # _TREE.md desligado por padrao (spec0011)
        self.root_in_name_var = tk.BooleanVar(value=False)  # incluir pasta-raiz (spec0013)
        self._selected_exts: set[str] = set(C.DEFAULT_EXTENSIONS)  # allowlist atual (editada no modal)
        self.also_md_var = tk.BooleanVar(value=False)
        self.also_md_root_var = tk.StringVar()
        self._name_edited = False  # usuário mexeu no nome manualmente?
        self._last_dest: Path | None = None
        self._busy = False
        # Semente de navegação do atalho "abrir GUI" (--start-dir "%~dp0."): pasta
        # onde "Procurar…" começa quando não há raiz. NÃO define a raiz (spec0030).
        self._start_dir = start_dir or ""

        # Persistência é SÓ-GUI (DEC-020): carrega a última config nos widgets.
        # load_settings nunca lança; a CLI/.bat jamais leem este arquivo.
        self._settings = settings_store.load_settings()
        self._apply_settings_to_vars()

        self._build()

    # ------------------------------------------------------------------ #
    # Construção da UI
    # ------------------------------------------------------------------ #
    def _build(self) -> None:
        # Barra de menu: ações de configuração da própria ferramenta (uma vez), fora
        # do fluxo de execução. "Gerar atalho da UI…" cria o .bat que abre a GUI e que
        # você copia para pastas de projeto (spec0031). NÃO é o RUN .bat (DEC-020).
        menubar = tk.Menu(self.master)
        tools = tk.Menu(menubar, tearoff=0)
        tools.add_command(label="Gerar atalho da UI…",
                          command=self._generate_open_gui_bat)
        tools.add_command(label="Restaurar padrões de fábrica…",
                          command=self._reset_defaults)
        menubar.add_cascade(label="Ferramentas", menu=tools)
        self.master.config(menu=menubar)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # ---- Caminhos (topo compacto) ------------------------------------ #
        # Raiz (+ Procurar/Recentes) e "Nome da pasta" na MESMA linha (curtos).
        top = ttk.Frame(self)
        top.grid(row=0, column=0, columnspan=2, sticky="ew")
        top.columnconfigure(1, weight=1)
        ttk.Label(top, text="Pasta raiz *").grid(row=0, column=0, sticky="w")
        raiz = ttk.Frame(top)
        raiz.grid(row=0, column=1, sticky="ew", padx=(6, 12))
        raiz.columnconfigure(0, weight=1)  # só o Entry expande
        ttk.Entry(raiz, textvariable=self.root_var).grid(row=0, column=0, sticky="ew")
        ttk.Button(raiz, text="Procurar…", command=self._choose_root).grid(
            row=0, column=1, padx=(6, 0))
        self.recent_menu = tk.Menu(self, tearoff=0)
        self.recent_btn = ttk.Menubutton(
            raiz, text="Recentes ▾", menu=self.recent_menu)
        self.recent_btn.grid(row=0, column=2, padx=(6, 0))
        self._refresh_recent_menu()
        ttk.Label(top, text="Nome da pasta").grid(row=0, column=2, sticky="w")
        name_entry = ttk.Entry(top, textvariable=self.name_var, width=20)
        name_entry.grid(row=0, column=3, sticky="w", padx=6)
        name_entry.bind("<Key>", lambda _e: setattr(self, "_name_edited", True))
        ttk.Label(top, text="(padrão: nome da raiz)", foreground="#888").grid(
            row=0, column=4, sticky="w")

        # Destino (largura total)
        drow = ttk.Frame(self)
        drow.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        drow.columnconfigure(1, weight=1)
        ttk.Label(drow, text="Destino").grid(row=0, column=0, sticky="w")
        ttk.Entry(drow, textvariable=self.dest_var).grid(
            row=0, column=1, sticky="ew", padx=6)
        ttk.Button(drow, text="Procurar…", command=self._choose_dest).grid(row=0, column=2)
        ttk.Label(drow, text="(padrão: pasta Downloads)", foreground="#888").grid(
            row=1, column=1, sticky="w", padx=6)

        # ---- Duas colunas: Renomeação | Opções --------------------------- #
        modes = ttk.LabelFrame(self, text="Renomeação", padding=8)
        modes.grid(row=2, column=0, sticky="nsew", pady=(10, 0), padx=(0, 6))
        ttk.Radiobutton(modes, text="Só duplicados (recomendado) — só arquivos de nome repetido ganham sufixo",
                        variable=self.mode_var, value="collisions").grid(sticky="w")
        ttk.Radiobutton(modes, text="Todos os arquivos — todo arquivo recebe a pasta no nome",
                        variable=self.mode_var, value="all").grid(sticky="w")
        ttk.Radiobutton(modes, text="Caminho completo — todo arquivo carrega o caminho inteiro desde a raiz",
                        variable=self.mode_var, value="fullpath").grid(sticky="w")
        ttk.Checkbutton(modes, text="Incluir o nome da pasta-raiz (só no modo fullpath)",
                        variable=self.root_in_name_var).grid(sticky="w")
        ttk.Checkbutton(modes, text="Nomear _MANIFEST/_TREE com o nome da pasta (no fim, p/ desambiguar)",
                        variable=self.name_meta_var).grid(sticky="w")

        opts = ttk.LabelFrame(self, text="Opções", padding=8)
        opts.grid(row=2, column=1, sticky="nsew", pady=(10, 0), padx=(6, 0))
        opts.columnconfigure(0, weight=1)
        ttk.Checkbutton(opts, text="Ler .gitignore da raiz",
                        variable=self.gitignore_var).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(opts, text="Pular arquivos sensíveis (.env, chaves, segredos)",
                        variable=self.skip_sensitive_var).grid(row=1, column=0, sticky="w")
        ttk.Checkbutton(opts, text="Limpar a pasta de destino antes (só se foi criada pelo FlatDrop)",
                        variable=self.clear_var).grid(row=2, column=0, sticky="w")
        ttk.Checkbutton(opts, text="Gerar _MANIFEST.md (mapa origem → nome plano)",
                        variable=self.manifest_var).grid(row=3, column=0, sticky="w")
        ttk.Checkbutton(opts, text="Gerar _TREE.md (árvore: copiados, pulados c/ motivo, pastas colapsadas)",
                        variable=self.tree_var).grid(row=4, column=0, sticky="w")
        sepf = ttk.Frame(opts)
        sepf.grid(row=5, column=0, sticky="w", pady=(6, 0))
        ttk.Label(sepf, text="Separador:").grid(row=0, column=0, padx=(0, 4))
        ttk.Entry(sepf, textvariable=self.sep_var, width=6).grid(row=0, column=1)
        ttk.Label(sepf, text="(p/ projeto Python, '-' lê melhor)", foreground="#888").grid(
            row=0, column=2, padx=(8, 0))

        # ---- Duas colunas: Tipos de arquivo | Ignore --------------------- #
        typef = ttk.LabelFrame(self, text="Tipos de arquivo", padding=8)
        typef.grid(row=3, column=0, sticky="nsew", pady=(10, 0), padx=(0, 6))
        typef.columnconfigure(0, weight=1)
        self.types_summary = ttk.Label(typef, text="")
        self.types_summary.grid(row=0, column=0, sticky="w")
        ttk.Button(typef, text="Escolher tipos…", command=self._choose_types).grid(
            row=0, column=1, sticky="e")
        self._update_types_summary()

        ignf = ttk.LabelFrame(self, text="Ignore (.flatdropignore)", padding=8)
        ignf.grid(row=3, column=1, sticky="nsew", pady=(10, 0), padx=(6, 0))
        ignf.columnconfigure(0, weight=1)
        ttk.Label(ignf, text="Editar visualmente o que vai ao Projeto (gera o arquivo na raiz).").grid(
            row=0, column=0, sticky="w")
        ttk.Button(ignf, text="Editar .flatdropignore…", command=self._edit_ignore).grid(
            row=0, column=1, sticky="e")

        # ---- Multi-fonte (largura total, fina) --------------------------- #
        ff = ttk.LabelFrame(self, text="Multi-fonte (opcional)", padding=8)
        ff.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        ff.columnconfigure(1, weight=1)
        ttk.Checkbutton(ff, text="Também incluir todos os .md a partir de:",
                        variable=self.also_md_var).grid(row=0, column=0, sticky="w")
        ttk.Entry(ff, textvariable=self.also_md_root_var).grid(
            row=0, column=1, sticky="ew", padx=6)
        ttk.Button(ff, text="Procurar…", command=self._choose_also_md).grid(row=0, column=2, sticky="e")

        # ---- Ações ------------------------------------------------------- #
        actions = ttk.Frame(self)
        actions.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(12, 6))
        self.btn_preview = ttk.Button(actions, text="Pré-visualizar", command=self._on_preview)
        self.btn_preview.grid(row=0, column=0, padx=(0, 6))
        self.btn_exec = ttk.Button(actions, text="Executar", command=self._on_execute)
        self.btn_exec.grid(row=0, column=1, padx=6)
        self.btn_open = ttk.Button(actions, text="Abrir pasta", command=self._open_dest, state="disabled")
        self.btn_open.grid(row=0, column=2, padx=6)
        self.btn_genbat = ttk.Button(actions, text="Gerar .bat…", command=self._generate_bat)
        self.btn_genbat.grid(row=0, column=3, padx=6)
        self.status = ttk.Label(actions, text="", foreground="#06c")
        self.status.grid(row=0, column=4, padx=12, sticky="w")

        # ---- Saída / console (ocupa o espaço livre) ---------------------- #
        ttk.Label(self, text="Saída", foreground="#888").grid(
            row=6, column=0, columnspan=2, sticky="w")
        self.rowconfigure(7, weight=1)
        self.out = scrolledtext.ScrolledText(self, height=12, wrap="none", font=("Consolas", 9))
        self.out.grid(row=7, column=0, columnspan=2, sticky="nsew")

    # ------------------------------------------------------------------ #
    # Handlers de seleção
    # ------------------------------------------------------------------ #
    def _choose_root(self) -> None:
        # Começa na raiz já preenchida; senão na semente do atalho (--start-dir).
        # "" faz o tkinter usar o padrão dele. (spec0030)
        initial = self.root_var.get().strip() or self._start_dir
        path = filedialog.askdirectory(
            title="Escolha a pasta raiz do projeto", initialdir=initial)
        if not path:
            return
        self.root_var.set(path)
        if not self._name_edited:
            self.name_var.set(Path(path).name)

    def _choose_dest(self) -> None:
        path = filedialog.askdirectory(title="Escolha a pasta de destino")
        if path:
            self.dest_var.set(path)

    def _choose_also_md(self) -> None:
        root = self.root_var.get().strip()
        initial = str(Path(root).parent) if root and Path(root).is_dir() else None
        path = filedialog.askdirectory(
            title="Raiz para incluir todos os .md", initialdir=initial)
        if path:
            self.also_md_root_var.set(path)
            self.also_md_var.set(True)

    # ------------------------------------------------------------------ #
    # Persistência (só-GUI; DEC-020: nada disto toca a CLI nem o gerador de .bat)
    # ------------------------------------------------------------------ #
    def _apply_settings_to_vars(self) -> None:
        """Sobrescreve os valores iniciais dos widgets com a última config salva.

        PREFERÊNCIAS (renomeação, opções, tipos, separador, destino) são SEMPRE
        restauradas — inclusive abrindo pela GUI pelo atalho "abrir GUI" —, porque
        o autor quer a config montada persistente entre projetos (FIX-010). Só a
        LOCALIZAÇÃO (raiz, nome, multi-fonte, que é do projeto) NÃO é restaurada
        quando há --start-dir: o atalho é copiado para pastas variadas e restaurar
        o projeto anterior faria "Procurar…" abrir no lugar errado. Guardas: nenhum
        valor inválido do disco chega aos widgets.
        """
        s = self._settings
        # --- Preferências: sempre ---
        self.mode_var.set(s.mode)          # já saneado para {collisions,all,fullpath}
        self.sep_var.set(s.sep)            # já saneado para não-vazio
        self.gitignore_var.set(s.read_gitignore)
        self.skip_sensitive_var.set(s.skip_sensitive)
        self.clear_var.set(s.clear_dest)
        self.manifest_var.set(s.write_manifest)
        self.tree_var.set(s.write_tree)
        self.name_meta_var.set(s.name_meta_with_folder)
        self.root_in_name_var.set(s.root_in_name)
        # allowlist reconstruída do delta contra os defaults ATUAIS.
        defaults = set(C.DEFAULT_EXTENSIONS)
        self._selected_exts = (defaults | set(s.ext_added)) - set(s.ext_removed)
        # destino é preferência (não é do projeto): só se for uma pasta real.
        if s.dest and Path(s.dest).is_dir():
            self.dest_var.set(s.dest)

        # --- Localização: só quando NÃO aberto pelo atalho "abrir GUI" ---
        if self._start_dir:
            return
        if s.root:
            self.root_var.set(s.root)
        if s.name:
            # NAO trava _name_edited: trocar de raiz deve voltar a renomear
            # (bind <Key> marca a flag quando o usuario digita). (FIX-008)
            self.name_var.set(s.name)
        self.also_md_var.set(s.also_md)
        self.also_md_root_var.set(s.also_md_root)

    def _reset_defaults(self) -> None:
        """Volta a config ao padrão de fábrica e apaga o salvo (menu Ferramentas).
        Repinta só as PREFERÊNCIAS; a localização atual na tela (raiz/nome/multi-
        fonte) fica como está. Os recentes são mantidos (histórico, não config).
        (spec0035)"""
        if not messagebox.askyesno(
            "FlatDrop",
            "Restaurar as configurações ao padrão de fábrica? A config salva será "
            "apagada (os recentes são mantidos)."):
            return
        self._settings = settings_store.Settings(
            recent_roots=self._settings.recent_roots)
        settings_store.save_settings(self._settings)
        s = self._settings
        self.mode_var.set(s.mode)
        self.sep_var.set(s.sep)
        self.gitignore_var.set(s.read_gitignore)
        self.skip_sensitive_var.set(s.skip_sensitive)
        self.clear_var.set(s.clear_dest)
        self.manifest_var.set(s.write_manifest)
        self.tree_var.set(s.write_tree)
        self.name_meta_var.set(s.name_meta_with_folder)
        self.root_in_name_var.set(s.root_in_name)
        self._selected_exts = set(C.DEFAULT_EXTENSIONS)
        self._update_types_summary()
        self.status.config(text="Configurações restauradas ao padrão de fábrica.")

    def _refresh_recent_menu(self) -> None:
        """(Re)popula o menu "Recentes ▾" a partir dos recentes salvos."""
        self.recent_menu.delete(0, "end")
        roots = self._settings.recent_roots
        if not roots:
            self.recent_menu.add_command(label="(nenhum recente)", state="disabled")
            return
        for path in roots:
            self.recent_menu.add_command(
                label=path, command=lambda p=path: self._use_recent(p))

    def _use_recent(self, path: str) -> None:
        """Escolher um recente preenche a raiz (e o nome, se ainda não editado)."""
        path = (path or "").strip()
        if not path:
            return
        self.root_var.set(path)
        if not self._name_edited:
            self.name_var.set(Path(path).name)

    def _persist_settings(self) -> None:
        """Captura a config atual da tela num Settings e grava (best-effort).

        Chamado SÓ após um Executar bem-sucedido. Lê os widgets diretamente —
        NÃO chama _build_cli_args (que é do caminho do .bat, intocável). Uma
        falha de gravação nunca afeta o resultado já concluído.
        """
        defaults = set(C.DEFAULT_EXTENSIONS)
        root = self.root_var.get().strip()
        s = settings_store.Settings(
            root=root,
            dest=self.dest_var.get().strip(),
            name=self.name_var.get().strip(),
            mode=self.mode_var.get(),
            sep=self.sep_var.get(),
            ext_added=sorted(self._selected_exts - defaults),
            ext_removed=sorted(defaults - self._selected_exts),
            read_gitignore=self.gitignore_var.get(),
            skip_sensitive=self.skip_sensitive_var.get(),
            write_manifest=self.manifest_var.get(),
            write_tree=self.tree_var.get(),
            name_meta_with_folder=self.name_meta_var.get(),
            root_in_name=self.root_in_name_var.get(),
            clear_dest=self.clear_var.get(),
            also_md=self.also_md_var.get(),
            also_md_root=self.also_md_root_var.get().strip(),
            recent_roots=settings_store.push_recent(self._settings.recent_roots, root),
        )
        settings_store.save_settings(s)
        self._settings = s
        # Reflete o novo recente no Combobox dentro da mesma sessão.
        self._refresh_recent_menu()

    def _build_cli_args(self) -> list[str]:
        """Serializa a configuração atual da tela em argumentos da CLI (para o .bat)."""
        args: list[str] = ["--root", self.root_var.get().strip()]
        dest = self.dest_var.get().strip()
        if dest and Path(dest) != core.default_downloads_dir():
            args += ["--dest", dest]
        name = self.name_var.get().strip()
        if name:
            args += ["--name", name]
        if self.mode_var.get() != "collisions":
            args += ["--mode", self.mode_var.get()]
        sep = self.sep_var.get()
        if sep and sep != C.DEFAULT_SEP:
            args += ["--sep", sep]
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
        if not self.gitignore_var.get():
            args += ["--no-gitignore"]
        if not self.skip_sensitive_var.get():
            args += ["--include-sensitive"]
        if not self.manifest_var.get():
            args += ["--no-manifest"]
        if self.tree_var.get():
            args += ["--tree"]
        if not self.name_meta_var.get():
            args += ["--no-name-meta"]
        if self.root_in_name_var.get():
            args += ["--root-in-name"]
        if not self.clear_var.get():
            args += ["--no-clear"]
        if self.also_md_var.get() and self.also_md_root_var.get().strip():
            args += ["--also-md-from", self.also_md_root_var.get().strip()]
        return args

    def _generate_bat(self) -> None:
        """Gera um .bat ASCII que reproduz a configuração atual (chama a CLI)."""
        if not self._validate_root():
            return
        run_py = Path(__file__).resolve().parent.parent / "run.py"
        args = self._build_cli_args()
        # Caminhos com acento são frágeis no CMD (.bat). Avisa, mas gera se o usuário quiser.
        paths = [self.root_var.get(), self.dest_var.get(),
                 self.also_md_root_var.get(), str(run_py)]
        if any(p and not p.isascii() for p in paths):
            if not messagebox.askyesno(
                "FlatDrop",
                "Algum caminho tem acentos. Em .bat no CMD isso pode falhar "
                "(recomendo caminhos sem acento). Gerar mesmo assim?"):
                return
        # Linha de comando: valores entre aspas; flags sem aspas.
        parts = ["python", '"%FLATDROP%"']
        for a in args:
            parts.append(a if a.startswith("--") else '"' + a + '"')
        cmdline = " ".join(parts)
        name = self.name_var.get().strip() or Path(self.root_var.get()).name or "flatdrop"
        root = self.root_var.get().strip()
        initial = str(Path(root).parent) if root and Path(root).is_dir() else None
        path = filedialog.asksaveasfilename(
            title="Salvar .bat", defaultextension=".bat", initialdir=initial,
            initialfile=name + ".bat", filetypes=[("Arquivo .bat", "*.bat")])
        if not path:
            return
        lines = [
            "@echo off",
            "chcp 65001 >nul",
            "rem Gerado pelo FlatDrop. Corpo em ASCII (CMD + chcp nao lida com acento no .bat).",
            "rem Ajuste o caminho do run.py abaixo se mudar de maquina.",
            'set "FLATDROP=' + str(run_py) + '"',
            "",
            cmdline,
            "",
            "echo.",
            "pause",
        ]
        content = "\r\n".join(lines) + "\r\n"
        Path(path).write_text(content, encoding="utf-8", newline="")
        messagebox.showinfo("FlatDrop", "'.bat' gerado em:\n" + path)

    def _generate_open_gui_bat(self) -> None:
        """Gera o atalho 'abrir GUI' (menu Ferramentas). Genérico, sem config —
        você o copia para pastas de projeto. NÃO é o RUN .bat (DEC-020)."""
        run_py = Path(__file__).resolve().parent.parent / "run.py"
        # Default: uma pasta ACIMA da raiz do repo, onde os .bat do FlatDrop já
        # vivem (fora do worktree, não são achatados nem versionados). (spec0031)
        default_dir = run_py.parent.parent
        if not str(run_py).isascii():
            if not messagebox.askyesno(
                "FlatDrop",
                "O caminho da ferramenta tem acentos. Em .bat no CMD isso pode "
                "falhar. Gerar mesmo assim?"):
                return
        path = filedialog.asksaveasfilename(
            title="Salvar atalho 'abrir GUI'", defaultextension=".bat",
            initialdir=str(default_dir), initialfile="flatdrop-ui.bat",
            filetypes=[("Arquivo .bat", "*.bat")])
        if not path:
            return
        Path(path).write_text(
            _open_gui_bat_content(run_py), encoding="utf-8", newline="")
        messagebox.showinfo("FlatDrop", "Atalho 'abrir GUI' gerado em:\n" + path)

    def _update_types_summary(self) -> None:
        total = len(set(C.DEFAULT_EXTENSIONS) | self._selected_exts)
        self.types_summary.config(
            text=f"Tipos: {len(self._selected_exts)} de {total} selecionados")

    def _choose_types(self) -> None:
        TypePickerDialog(self.winfo_toplevel(), self._selected_exts, self._on_types_chosen)

    def _on_types_chosen(self, selected: set[str]) -> None:
        self._selected_exts = selected
        self._update_types_summary()

    def _edit_ignore(self) -> None:
        root = self.root_var.get().strip()
        if not self._validate_root():
            return
        FlatDropIgnoreEditor(self.winfo_toplevel(), root, self._gather_cfg(),
                             on_saved=self._on_ignore_saved)

    def _on_ignore_saved(self, path) -> None:
        self._write(f"[.flatdropignore gravado] {path}\n")
        self.status.config(text=".flatdropignore atualizado")

    # ------------------------------------------------------------------ #
    # Coleta de configuração
    # ------------------------------------------------------------------ #
    def _gather_cfg(self) -> core.ScanConfig:
        return core.ScanConfig(
            mode=self.mode_var.get(),
            sep=self.sep_var.get() or C.DEFAULT_SEP,
            use_gitignore=self.gitignore_var.get(),
            include_sensitive=not self.skip_sensitive_var.get(),
            extensions=self._selected_exts or set(C.DEFAULT_EXTENSIONS),
            clear_dest=self.clear_var.get(),
            write_manifest=self.manifest_var.get(),
            write_tree=self.tree_var.get(),
            name_meta_with_folder=self.name_meta_var.get(),
            root_in_name=self.root_in_name_var.get(),
        )

    def _sources(self, primary: core.ScanConfig) -> list[core.Source]:
        """Fontes de coleta: a raiz primária + (se marcado) TODOS os .md de outra raiz.

        Espelha o que `_build_cli_args` faz para o .bat, para que a execução ao vivo
        e o .bat gerado produzam o MESMO resultado.
        """
        sources = [core.Source(Path(self.root_var.get().strip()), primary)]
        md_root = self.also_md_root_var.get().strip()
        if self.also_md_var.get() and md_root:
            md_cfg = replace(primary, only_ext={"md"}, exclude_ext=set(), only_folders=[])
            sources.append(core.Source(Path(md_root), md_cfg))
        return sources

    def _dest_path(self) -> Path:
        base = Path(self.dest_var.get() or core.default_downloads_dir())
        name = self.name_var.get().strip() or Path(self.root_var.get()).name or "flatdrop_out"
        return base / name

    # ------------------------------------------------------------------ #
    # Execução em thread
    # ------------------------------------------------------------------ #
    def _run_async(self, work, on_done) -> None:
        """Roda ``work()`` numa thread e chama ``on_done(result, error)`` na UI."""
        if self._busy:
            return
        self._busy = True
        self._set_buttons(False)

        def runner():
            err = None
            result = None
            try:
                result = work()
            except Exception as exc:  # leva o erro de volta à UI
                err = exc
            self.after(0, lambda: self._finish(on_done, result, err))

        threading.Thread(target=runner, daemon=True).start()

    def _finish(self, on_done, result, err) -> None:
        self._busy = False
        self._set_buttons(True)
        on_done(result, err)

    def _set_buttons(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        self.btn_preview.config(state=state)
        self.btn_exec.config(state=state)

    # ------------------------------------------------------------------ #
    # Ações
    # ------------------------------------------------------------------ #
    def _validate_root(self) -> bool:
        root = self.root_var.get().strip()
        if not root or not Path(root).is_dir():
            messagebox.showerror("FlatDrop", "Escolha uma pasta raiz válida.")
            return False
        return True

    def _on_preview(self) -> None:
        if not self._validate_root():
            return
        primary = self._gather_cfg()
        sources = self._sources(primary)
        self.status.config(text="Varrendo…")
        self._run_async(lambda: core.make_plan_sources(sources), self._render_preview)

    def _on_execute(self) -> None:
        if not self._validate_root():
            return
        primary = self._gather_cfg()
        sources = self._sources(primary)
        dest = self._dest_path()
        self.status.config(text="Copiando…")

        def work():
            plan = core.make_plan_sources(sources)
            res = core.execute_plan(plan, dest, primary)
            return plan, res

        self._run_async(work, self._render_execute)

    def _open_dest(self) -> None:
        if not self._last_dest or not self._last_dest.exists():
            return
        path = str(self._last_dest)
        try:
            if sys.platform.startswith("win"):
                os.startfile(path)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.run(["open", path], check=False)
            else:
                subprocess.run(["xdg-open", path], check=False)
        except OSError as exc:
            messagebox.showwarning("FlatDrop", f"Não consegui abrir a pasta:\n{exc}")

    # ------------------------------------------------------------------ #
    # Renderização
    # ------------------------------------------------------------------ #
    def _write(self, text: str) -> None:
        self.out.delete("1.0", "end")
        self.out.insert("1.0", text)

    def _plan_summary(self, plan: core.FlattenPlan) -> list[str]:
        skipped_txt = ", ".join(f"{k}={v}" for k, v in plan.skipped.items() if v)
        lines = [
            f"Raiz: {plan.root}",
            f"Arquivos a copiar: {len(plan.files)}  |  "
            f"nomes repetidos: {plan.collisions}  |  "
            f"total: {core.human_size(plan.total_bytes)}  (~{plan.est_tokens:,} tokens, estimativa)",
            f"Pulados: {skipped_txt or 'nenhum'}",
        ]
        # Amostras do que foi pulado, por motivo. Sem isso, o sumiço de
        # arquivos/pastas é invisível na pré-visualização (FIX-001).
        for reason, sample in plan.skipped_samples.items():
            if not sample:
                continue
            total = plan.skipped.get(reason, 0)
            shown = sample[:5]
            extra = f" … (+{total - len(shown)})" if total > len(shown) else ""
            lines.append(f"  ↳ {reason}: " + ", ".join(shown) + extra)
        lines.append("")
        if plan.warnings:
            lines.append("AVISOS:")
            lines += [f"  ⚠ {w}" for w in plan.warnings]
            lines.append("")
        return lines

    def _render_preview(self, plan, err) -> None:
        self.status.config(text="")
        if err:
            self._write(f"Erro: {err}")
            return
        lines = ["PRÉ-VISUALIZAÇÃO (nada foi escrito ainda)", "=" * 60]
        lines += self._plan_summary(plan)
        lines.append("Mapeamento (origem → nome na pasta):")
        cap = 1000
        for f in plan.files[:cap]:
            flag = "   *" if f.renamed else ""
            lines.append(f"  {f.rel.as_posix():40} → {f.target}{flag}")
        if len(plan.files) > cap:
            lines.append(f"  … e mais {len(plan.files) - cap} (lista completa irá no _MANIFEST.md)")
        lines.append("")
        lines.append(f"Destino ao executar: {self._dest_path()}")
        self._write("\n".join(lines))

    def _render_execute(self, payload, err) -> None:
        self.status.config(text="")
        if err:
            self._write(f"Erro: {err}")
            return
        plan, res = payload
        self._last_dest = res.dest
        self.btn_open.config(state="normal")
        # Só-GUI: grava a config que acabou de dar certo + raiz recente (DEC-020).
        self._persist_settings()
        lines = ["CONCLUÍDO", "=" * 60]
        lines += self._plan_summary(plan)
        lines.append(f"Copiados: {res.copied} arquivo(s)")
        lines.append(f"Destino:  {res.dest}")
        lines.append(f"Limpou antes: {'sim' if res.cleared else 'não'}")
        if res.manifest_path:
            lines.append(f"Manifesto: {res.manifest_path.name}")
        if res.warnings:
            lines.append("")
            lines.append("AVISOS:")
            lines += [f"  ⚠ {w}" for w in res.warnings]
        lines.append("")
        lines.append("Agora é só abrir a pasta, selecionar tudo e arrastar para o Projeto do Claude.")
        self._write("\n".join(lines))


def _open_gui_bat_content(run_py: Path) -> str:
    """Conteúdo do atalho 'abrir GUI' (.bat). Função pura, testável.

    Genérico (sem --root): abre só a interface. Passa --start-dir "%~dp0." para o
    "Procurar…" começar na pasta do próprio .bat (spec0030). NÃO é o RUN .bat: não
    reproduz config nenhuma. chcp só quando o caminho tem não-ASCII (como no RUN).
    """
    precisa_utf8 = not str(run_py).isascii()
    linhas = ["@echo off"]
    if precisa_utf8:
        linhas.append("chcp 65001 >nul")
    linhas += [
        "rem FlatDrop - abre a interface grafica. Atalho gerado pela propria GUI.",
        "rem Copie este .bat para uma pasta de projeto: ao abrir, 'Procurar...' ja",
        'rem comeca nela (--start-dir "%~dp0."). NAO define a raiz; a GUI abre limpa.',
        'start "" pythonw "' + str(run_py) + '" --start-dir "%~dp0."',
    ]
    return "\r\n".join(linhas) + "\r\n"


def main(start_dir: str | None = None) -> None:
    """Ponto de entrada: cria a janela e entra no loop do tkinter.

    ``start_dir`` (opcional): pasta onde "Procurar…" começa quando não há raiz.
    Vem do atalho "abrir GUI" (``--start-dir "%~dp0."``); NÃO define a raiz. Sua
    presença também faz a GUI abrir LIMPA (não restaura a última sessão), pois o
    atalho é copiado para pastas variadas (spec0030).
    """
    root = tk.Tk()
    try:
        ttk.Style().theme_use("vista" if sys.platform.startswith("win") else "clam")
    except tk.TclError:
        pass
    FlatDropApp(root, start_dir=start_dir)
    root.mainloop()


if __name__ == "__main__":
    main()
