# spec-0003 — GUI: filtros de tipo + gerador de .bat

**Tipo:** código · **Alvo:** `flatdrop/gui.py` · **Autor:** chat · **Aplicador:** Claude Code
**Depende de:** spec-0001 (allowlist com Godot etc.) já aplicada.
**Origem:** decisões de 2026-06-22/24 — expor os filtros `only_ext`/`exclude_ext` na GUI e gerar `.bat` a partir da configuração da tela.

## Objetivo
1. Dois campos na GUI para selecionar tipo na hora: "Só estes tipos" (`only_ext`) e "Exceto estes" (`exclude_ext`).
2. Um toggle multi-fonte na GUI ("Também incluir todos os .md a partir de [raiz]") → `--also-md-from`.
3. Botão "Gerar .bat…" que serializa a config atual da tela num `.bat` **ASCII puro** e pede onde salvar.

## Por que ASCII no .bat (regra dura do gerador)
Um `.bat` com caracteres não-ASCII no corpo (travessão "—", acentos) + `chcp 65001` faz o CMD
**desalinhar a leitura das linhas** e executar fragmentos como comando (bug real: erros `'FlatDrop'`/`'m'`/`'Use'`
antes do `CONCLUÍDO`). Por isso o gerador emite **comentários/estrutura em ASCII** e mantém `chcp 65001`
só para a SAÍDA do Python. Caminhos com acento ainda são frágeis no CMD → o gerador AVISA se algum caminho
tiver não-ASCII (mas gera, a pedido).

## Nota de teste
Não há teste de GUI na suíte (tkinter fora do CI). A validação é: `python -m pytest -q` segue 26/26 (nada do
core/CLI quebrou) + **smoke manual no Windows**: abrir a GUI, preencher "Só estes tipos: md", pré-visualizar;
marcar o toggle multi-fonte; clicar "Gerar .bat…" e conferir que o arquivo sai ASCII e roda.

---

## EDIÇÃO 1 — helper de parsing (após os imports, antes da classe)

**Âncora:**
```
from . import config as C
from . import core
```
**Ação:** inserir logo APÓS essa âncora:
```


def _parse_exts(text: str) -> set[str]:
    """Converte 'md, py .json' -> {'md','py','json'} (tolerante a vírgula/espaço/ponto)."""
    return {
        e.strip().lstrip(".").lower()
        for e in text.replace("\n", ",").replace(" ", ",").split(",")
        if e.strip()
    }
```

## EDIÇÃO 2 — novas variáveis de estado

**Âncora:**
```
        self.manifest_var = tk.BooleanVar(value=True)
```
**Ação:** inserir logo APÓS essa linha:
```
        self.only_ext_var = tk.StringVar()
        self.exclude_ext_var = tk.StringVar()
        self.also_md_var = tk.BooleanVar(value=False)
        self.also_md_root_var = tk.StringVar()
```

## EDIÇÃO 3 — bloco de UI dos filtros + multi-fonte (antes dos botões de ação)

**Âncora (o comentário que abre os botões de ação):**
```
        # Botões de ação
        actions = ttk.Frame(self)
```
**Ação:** inserir IMEDIATAMENTE ANTES dessa âncora (mantendo o `r += 1` do bloco anterior):
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

## EDIÇÃO 4 — botão "Gerar .bat…" + mover o status de coluna

**Âncora (bloco do botão Abrir pasta + status):**
```
        self.btn_open = ttk.Button(actions, text="Abrir pasta", command=self._open_dest, state="disabled")
        self.btn_open.grid(row=0, column=2, padx=6)
        self.status = ttk.Label(actions, text="", foreground="#06c")
        self.status.grid(row=0, column=3, padx=12, sticky="w")
```
**Ação:** SUBSTITUIR esse bloco por:
```
        self.btn_open = ttk.Button(actions, text="Abrir pasta", command=self._open_dest, state="disabled")
        self.btn_open.grid(row=0, column=2, padx=6)
        self.btn_genbat = ttk.Button(actions, text="Gerar .bat…", command=self._generate_bat)
        self.btn_genbat.grid(row=0, column=3, padx=6)
        self.status = ttk.Label(actions, text="", foreground="#06c")
        self.status.grid(row=0, column=4, padx=12, sticky="w")
```

## EDIÇÃO 5 — passar os filtros no _gather_cfg

**Âncora (última linha do `core.ScanConfig(...)` em `_gather_cfg`):**
```
            write_manifest=self.manifest_var.get(),
        )
```
**Ação:** SUBSTITUIR por:
```
            write_manifest=self.manifest_var.get(),
            only_ext=(_parse_exts(self.only_ext_var.get()) or None),
            exclude_ext=_parse_exts(self.exclude_ext_var.get()),
        )
```

## EDIÇÃO 6 — novos métodos (after `_choose_dest`)

**Âncora (fim do método `_choose_dest`):**
```
    def _choose_dest(self) -> None:
        path = filedialog.askdirectory(title="Escolha a pasta de destino")
        if path:
            self.dest_var.set(path)
```
**Ação:** inserir logo APÓS esse método:
```

    def _choose_also_md(self) -> None:
        path = filedialog.askdirectory(title="Raiz para incluir todos os .md")
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
```

## Validação
- `python -m pytest -q` → 26/26 (core/CLI intactos).
- Smoke manual no Windows: filtros funcionam na pré-visualização; "Gerar .bat…" produz um arquivo ASCII
  (abra no editor e confira que não há "—" nem acentos no corpo) que roda sem os erros de CMD.
