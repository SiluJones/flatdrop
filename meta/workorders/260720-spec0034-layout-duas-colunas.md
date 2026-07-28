# spec0034 — Refino de layout da GUI (duas colunas, console de volta)

- **Tipo:** implementação (GUI, layout). Roda `python -m pytest -q` (segue verde; a GUI não é
  coberta pela suíte → validação por **smoke manual**). Versão-alvo: **0.10.0** (0.9.2 →
  0.10.0; reorganização visível da UI, sem mudança de comportamento).
- **Data:** 2026-07-20 · **Aprovado:** mockup de duas colunas com Raiz+Nome na mesma linha.
- **Motivo.** ~11 seções empilhadas em largura total empurravam o console (`self.out`) para
  fora da vista e esticavam os campos. Reorganizar em duas colunas encurta a altura do
  formulário e devolve espaço ao console.

## GUARDA (DEC-020)

Só **rearranjo** do `_build`. Todos os `tk.Var`, `command=` e widgets nomeados
(`recent_menu`, `recent_btn`, `types_summary`, `btn_preview`, `btn_exec`, `btn_open`,
`btn_genbat`, `status`, `out`) são **preservados** — nenhuma lógica muda.
`_build_cli_args`/`_generate_bat`/`_sources`/`cli.py` **não são tocados**; `git diff` deve
confirmar (o `.bat` reproduz exatamente o mesmo). Se algo pedir tocá-los, PARE e reporte.

---

## Edit único — `gui.py`: substituir o CORPO de `_build`

**Como aplicar:** o `_build` começa com o bloco da **barra de menu** (spec0031) e, logo
depois, `self.columnconfigure(1, weight=1)`. **Preserve o bloco do menu intacto** e
substitua **todo o resto do corpo** — de `self.columnconfigure(1, weight=1)` até a última
linha do método (`self.out.grid(...)`) — pelo novo corpo abaixo. Se o texto atual divergir
em algum caractere, use o **arquivo atual como fonte** para a região a apagar; o que importa
é o resultado final ser exatamente o novo corpo (mesmos Vars/commands, novo arranjo).

**Novo corpo (substitui de `self.columnconfigure(1, weight=1)` até o fim do método):**
```
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
        # (spec0035 insere aqui, abaixo, o checkbox de nomear _MANIFEST/_TREE.)

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
        ttk.Button(ff, text="Procurar…", command=self._choose_also_md).grid(
            row=0, column=2, sticky="e")

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
```

## Edit 2 — `flatdrop/__init__.py`: bump

**Âncora exata:** `__version__ = "0.9.2"` → trocar por `__version__ = "0.10.0"`

## Edit 3 — `meta/CHANGELOG.md`: entrada [0.10.0]

**Âncora exata:** `## [0.9.2] — 2026-07-20`
Inserir ANTES dela:
```
## [0.10.0] — 2026-07-20

### Alterado
- **Layout da GUI reorganizado em duas colunas (spec0034).** Raiz e "Nome da pasta" na mesma
  linha; Renomeação | Opções e Tipos | Ignore lado a lado; Multi-fonte numa linha fina; a
  descrição do topo foi removida (a barra de título já a diz). Isso encurta muito o
  formulário e **devolve espaço ao console de saída** (`Saída`), que antes sumia da vista, e
  encurta os campos (não mais "longos demais"). Só rearranjo: mesmos controles e
  comportamento; `.bat` intocado (DEC-020).

```

## Edit 4 — `meta/STATUS.md`: refletir 0.10.0

**Âncora exata** (bloco da nota de revisão, inteiro):
```
> **Mudanças nesta revisão (2026-07-20):** leva de conveniências de GUI, agora com o layout
> do Recentes corrigido. Menu **Ferramentas → "Gerar atalho da UI…"** (spec0031, 0.9.0);
> **Recentes** compacto como botão **"Recentes ▾"** na linha da Raiz (spec0032, 0.9.1); e o
> **FIX-009** (spec0033, 0.9.2) que tirou a coluna morta que o botão criava — Entry +
> botões num sub-frame, grade de volta a 3 colunas, como no ASU. Versão **0.9.2**,
> **66 testes verdes**. RUN `.bat` intocado (DEC-020). Nada quebrado. **Frente candidata:**
> **multi-raiz na GUI** (exige decisão A/B do autor antes de desenhar, ver "Decisão
> pendente").
```
Trocar por:
```
> **Mudanças nesta revisão (2026-07-20):** **layout da GUI reorganizado em duas colunas**
> (spec0034, 0.10.0) — Raiz+Nome na mesma linha, Renomeação|Opções e Tipos|Ignore lado a
> lado, e o **console de saída de volta à vista**. Antes, nesta leva: menu Ferramentas →
> "Gerar atalho da UI…" (0.9.0), Recentes compacto (0.9.1) e FIX-009 do layout (0.9.2).
> Versão **0.10.0**, **66 testes verdes**. Só rearranjo de UI; RUN `.bat` intocado
> (DEC-020). **Pendente (autorizado, a desenhar):** checkbox para nomear `_MANIFEST`/`_TREE`
> com o nome da pasta no fim (default-ON; toca `cli.py`/`_build_cli_args` para paridade —
> DEC-020). **Frente candidata maior:** multi-raiz na GUI (decisão A/B pendente).
```

---

## O que testar

- **Automatizado:** segue **66 verdes** (só layout).
- **Smoke manual (Windows) — é o ponto:** a janela fica **mais baixa**; Raiz e "Nome da
  pasta" na mesma linha; Renomeação|Opções e Tipos|Ignore em duas colunas; Multi-fonte numa
  linha; o **console "Saída" aparece** e expande com a janela. Rodar Pré-visualizar/Executar
  → o resultado aparece no console. Conferir que todos os campos/botões seguem funcionando
  (Procurar, Recentes ▾, Escolher tipos…, Editar .flatdropignore…, Gerar .bat…).
- **`git diff`:** só `gui.py` (corpo de `_build`), `__init__.py` e meta-docs.
  `_build_cli_args`/`_generate_bat`/`_sources`/`cli.py` intocados.

## Merece print no README

A janela nova (duas colunas + console visível), substituindo o print antigo. Só sinalizar.

## Commit sugerido (sem acento)

```
git add flatdrop/gui.py flatdrop/__init__.py meta/CHANGELOG.md meta/STATUS.md meta/specs/260720-spec0034-layout-duas-colunas.md & git commit -m "feat(gui): layout em duas colunas devolve espaco ao console" -m "Raiz+Nome na mesma linha; Renomeacao|Opcoes e Tipos|Ignore lado a lado; Multi-fonte fina; descricao do topo removida. Encurta o formulario e traz o console de saida de volta a vista. So rearranjo do _build: mesmos Vars/commands; .bat intocado (DEC-020). Bump 0.10.0."
```
