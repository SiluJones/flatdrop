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


def _parse_exts(text: str) -> set[str]:
    """Converte 'md, py .json' -> {'md','py','json'} (tolerante a vírgula/espaço/ponto)."""
    return {
        e.strip().lstrip(".").lower()
        for e in text.replace("\n", ",").replace(" ", ",").split(",")
        if e.strip()
    }


class FlatDropApp(ttk.Frame):
    """Janela principal do FlatDrop."""

    def __init__(self, master: tk.Tk) -> None:
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
        self.gitignore_var = tk.BooleanVar(value=True)
        self.skip_sensitive_var = tk.BooleanVar(value=True)
        self.clear_var = tk.BooleanVar(value=True)
        self.manifest_var = tk.BooleanVar(value=True)
        self.only_ext_var = tk.StringVar()
        self.exclude_ext_var = tk.StringVar()
        self.also_md_var = tk.BooleanVar(value=False)
        self.also_md_root_var = tk.StringVar()
        self._name_edited = False  # usuário mexeu no nome manualmente?
        self._last_dest: Path | None = None
        self._busy = False

        self._build()

    # ------------------------------------------------------------------ #
    # Construção da UI
    # ------------------------------------------------------------------ #
    def _build(self) -> None:
        self.columnconfigure(1, weight=1)
        r = 0

        ttk.Label(
            self, text="Achata uma pasta de projeto numa pasta plana, "
            "renomeando arquivos repetidos, pronta para arrastar ao Projeto do Claude.",
            wraplength=680, foreground="#555",
        ).grid(row=r, column=0, columnspan=3, sticky="w", pady=(0, 10))
        r += 1

        # Pasta raiz
        ttk.Label(self, text="Pasta raiz *").grid(row=r, column=0, sticky="w")
        ttk.Entry(self, textvariable=self.root_var).grid(row=r, column=1, sticky="ew", padx=6)
        ttk.Button(self, text="Procurar…", command=self._choose_root).grid(row=r, column=2)
        r += 1

        # Destino
        ttk.Label(self, text="Destino").grid(row=r, column=0, sticky="w", pady=(6, 0))
        ttk.Entry(self, textvariable=self.dest_var).grid(row=r, column=1, sticky="ew", padx=6, pady=(6, 0))
        ttk.Button(self, text="Procurar…", command=self._choose_dest).grid(row=r, column=2, pady=(6, 0))
        r += 1
        ttk.Label(self, text="(padrão: pasta Downloads)", foreground="#888").grid(
            row=r, column=1, sticky="w", padx=6
        )
        r += 1

        # Nome da pasta
        ttk.Label(self, text="Nome da pasta").grid(row=r, column=0, sticky="w", pady=(6, 0))
        name_entry = ttk.Entry(self, textvariable=self.name_var)
        name_entry.grid(row=r, column=1, sticky="ew", padx=6, pady=(6, 0))
        name_entry.bind("<Key>", lambda _e: setattr(self, "_name_edited", True))
        ttk.Label(self, text="(padrão: nome da raiz)", foreground="#888").grid(row=r, column=2, sticky="w")
        r += 1

        # Modo de renomeação
        modes = ttk.LabelFrame(self, text="Renomeação", padding=8)
        modes.grid(row=r, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        ttk.Radiobutton(modes, text="Só duplicados (recomendado) — só arquivos de nome repetido ganham sufixo",
                        variable=self.mode_var, value="collisions").grid(sticky="w")
        ttk.Radiobutton(modes, text="Todos os arquivos — todo arquivo recebe a pasta no nome",
                        variable=self.mode_var, value="all").grid(sticky="w")
        ttk.Radiobutton(modes, text="Caminho completo — todo arquivo carrega o caminho inteiro desde a raiz",
                        variable=self.mode_var, value="fullpath").grid(sticky="w")
        r += 1

        # Opções
        opts = ttk.LabelFrame(self, text="Opções", padding=8)
        opts.grid(row=r, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        opts.columnconfigure(1, weight=1)
        ttk.Checkbutton(opts, text="Ler .gitignore da raiz", variable=self.gitignore_var).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(opts, text="Pular arquivos sensíveis (.env, chaves, segredos)",
                        variable=self.skip_sensitive_var).grid(row=1, column=0, sticky="w")
        ttk.Checkbutton(opts, text="Limpar a pasta de destino antes (só se foi criada pelo FlatDrop)",
                        variable=self.clear_var).grid(row=2, column=0, sticky="w")
        ttk.Checkbutton(opts, text="Gerar _MANIFEST.md (mapa origem → nome plano)",
                        variable=self.manifest_var).grid(row=3, column=0, sticky="w")
        sepf = ttk.Frame(opts)
        sepf.grid(row=0, column=2, rowspan=2, sticky="e")
        ttk.Label(sepf, text="Separador:").grid(row=0, column=0, padx=(12, 4))
        ttk.Entry(sepf, textvariable=self.sep_var, width=6).grid(row=0, column=1)
        ttk.Label(sepf, text="(p/ projeto Python, '-' lê melhor)", foreground="#888").grid(
            row=1, column=0, columnspan=2, sticky="e"
        )
        r += 1

        # Extensões aceitas
        extf = ttk.LabelFrame(self, text="Extensões aceitas (separadas por vírgula ou espaço)", padding=8)
        extf.grid(row=r, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        extf.columnconfigure(0, weight=1)
        self.ext_text = tk.Text(extf, height=3, wrap="word")
        self.ext_text.grid(row=0, column=0, sticky="ew")
        self.ext_text.insert("1.0", ", ".join(sorted(C.DEFAULT_EXTENSIONS)))
        ttk.Button(extf, text="Restaurar padrão", command=self._reset_ext).grid(row=0, column=1, padx=(6, 0), sticky="n")
        r += 1

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

        # Botões de ação
        actions = ttk.Frame(self)
        actions.grid(row=r, column=0, columnspan=3, sticky="ew", pady=(12, 6))
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
        r += 1

        # Saída / log
        self.rowconfigure(r, weight=1)
        self.out = scrolledtext.ScrolledText(self, height=12, wrap="none", font=("Consolas", 9))
        self.out.grid(row=r, column=0, columnspan=3, sticky="nsew")

    # ------------------------------------------------------------------ #
    # Handlers de seleção
    # ------------------------------------------------------------------ #
    def _choose_root(self) -> None:
        path = filedialog.askdirectory(title="Escolha a pasta raiz do projeto")
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
        if not self.gitignore_var.get():
            args += ["--no-gitignore"]
        if not self.skip_sensitive_var.get():
            args += ["--include-sensitive"]
        if not self.manifest_var.get():
            args += ["--no-manifest"]
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
        path = filedialog.asksaveasfilename(
            title="Salvar .bat", defaultextension=".bat",
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

    def _reset_ext(self) -> None:
        self.ext_text.delete("1.0", "end")
        self.ext_text.insert("1.0", ", ".join(sorted(C.DEFAULT_EXTENSIONS)))

    # ------------------------------------------------------------------ #
    # Coleta de configuração
    # ------------------------------------------------------------------ #
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


def main() -> None:
    """Ponto de entrada: cria a janela e entra no loop do tkinter."""
    root = tk.Tk()
    try:
        ttk.Style().theme_use("vista" if sys.platform.startswith("win") else "clam")
    except tk.TclError:
        pass
    FlatDropApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
