# spec0032 — Recentes compacto: botão "Recentes ▾" na linha da Raiz (libera uma linha)

- **Tipo:** implementação (GUI). Roda `python -m pytest -q` (deve seguir verde; a mudança é
  só de widget). Versão-alvo: **0.9.1** (0.9.0 → 0.9.1; refinamento de UI).
- **Data:** 2026-07-20 · **Ordem:** aplicar DEPOIS da spec0031 (assume 0.9.0).
- **Pedido:** o Combobox de Recentes ocupa uma **linha inteira**. Trocar pela forma compacta
  do ASU — um botão **"Recentes ▾"** (menu suspenso) **na própria linha da Raiz**, ao lado
  de "Procurar…". Libera a linha e deixa a feature (que o autor não usa muito) discreta.
- **DEC-020:** só GUI; não toca o `.bat` nem seu caminho.

---

## Edit 1 — `gui.py`: Menubutton "Recentes ▾" na Raiz; remover a linha do Combobox

**Âncora exata:**
```
        # Pasta raiz
        ttk.Label(self, text="Pasta raiz *").grid(row=r, column=0, sticky="w")
        ttk.Entry(self, textvariable=self.root_var).grid(row=r, column=1, sticky="ew", padx=6)
        ttk.Button(self, text="Procurar…", command=self._choose_root).grid(row=r, column=2)
        r += 1

        # Recentes (só-GUI): atalho para as raízes usadas antes. Escolher preenche a raiz.
        ttk.Label(self, text="Recentes").grid(row=r, column=0, sticky="w", pady=(6, 0))
        self.recent_combo = ttk.Combobox(
            self, state="readonly", values=list(self._settings.recent_roots))
        self.recent_combo.grid(row=r, column=1, sticky="ew", padx=6, pady=(6, 0))
        self.recent_combo.bind("<<ComboboxSelected>>", self._on_recent_selected)
        r += 1
```
Trocar por:
```
        # Pasta raiz (+ Recentes compacto na mesma linha, à direita — spec0032).
        ttk.Label(self, text="Pasta raiz *").grid(row=r, column=0, sticky="w")
        ttk.Entry(self, textvariable=self.root_var).grid(row=r, column=1, sticky="ew", padx=6)
        ttk.Button(self, text="Procurar…", command=self._choose_root).grid(row=r, column=2)
        self.recent_menu = tk.Menu(self, tearoff=0)
        self.recent_btn = ttk.Menubutton(
            self, text="Recentes ▾", menu=self.recent_menu)
        self.recent_btn.grid(row=r, column=3, padx=(6, 0))
        self._refresh_recent_menu()
        r += 1
```

## Edit 2 — `gui.py`: trocar o handler do Combobox por menu + refresh

**Âncora exata:**
```
    def _on_recent_selected(self, _event=None) -> None:
        """Escolher um recente preenche a raiz (e o nome, se ainda não editado)."""
        path = self.recent_combo.get().strip()
        if not path:
            return
        self.root_var.set(path)
        if not self._name_edited:
            self.name_var.set(Path(path).name)
```
Trocar por:
```
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
```

## Edit 3 — `gui.py`: `_persist_settings` atualiza o menu, não o Combobox

**Âncora exata:**
```
        self.recent_combo.configure(values=list(s.recent_roots))
```
Trocar por:
```
        self._refresh_recent_menu()
```

> Nota: `_refresh_recent_menu` lê `self._settings.recent_roots`; como `_persist_settings`
> já atribui `self._settings = s` antes desta linha, o menu reflete o recente novo.

## Edit 4 — `flatdrop/__init__.py`: bump

**Âncora exata:** `__version__ = "0.9.0"` → trocar por `__version__ = "0.9.1"`

## Edit 5 — `meta/CHANGELOG.md`: entrada [0.9.1]

**Âncora exata:** `## [0.9.0] — 2026-07-20`
Inserir ANTES dela:
```
## [0.9.1] — 2026-07-20

### Alterado
- **Recentes compacto (spec0032).** O Combobox de Recentes (que ocupava uma linha inteira)
  virou um botão **"Recentes ▾"** na própria linha da Raiz, ao lado de "Procurar…" — libera
  a linha e deixa a feature discreta. Comportamento igual: escolher um recente preenche a
  raiz (e o nome, se não editado). Só GUI; o `.bat` não é afetado.

```

## Edit 6 — `meta/STATUS.md`: refletir 0.9.1

**Âncora exata** (bloco da nota de revisão da spec0031, inteiro):
```
> **Mudanças nesta revisão (2026-07-20):** a GUI ganhou o menu **Ferramentas → "Gerar
> atalho da UI…"** (spec0031, 0.9.0): gera o `.bat` que abre a interface, com
> `--start-dir "%~dp0."`, salvando por padrão **uma pasta acima da raiz do repo** (onde os
> `.bat` do FlatDrop já vivem, fora do worktree). Versão **0.9.0**, **66 testes verdes**.
> Gerador NOVO e separado — o RUN `.bat` segue intocado (DEC-020). Nada quebrado.
> **Frente candidata:** **multi-raiz na GUI** (exige decisão A/B do autor antes de desenhar,
> ver "Decisão pendente"). Pendente: compactar os **Recentes** num botão "Recentes ▾"
> (spec0032, a aplicar em seguida).
```
Trocar por:
```
> **Mudanças nesta revisão (2026-07-20):** **Recentes** virou um botão compacto
> **"Recentes ▾"** na linha da Raiz (spec0032, 0.9.1), liberando a linha inteira que o
> Combobox ocupava. Antes, nesta leva: menu **Ferramentas → "Gerar atalho da UI…"**
> (spec0031, 0.9.0). Versão **0.9.1**, **66 testes verdes**. RUN `.bat` intocado (DEC-020).
> Nada quebrado. **Frente candidata:** **multi-raiz na GUI** (exige decisão A/B do autor
> antes de desenhar, ver "Decisão pendente").
```

---

## O que testar

- **Automatizado:** segue **66 verdes** (mudança só de widget, não toca a core nem o `.bat`).
- **Smoke manual (Windows):** a linha "Recentes" some; na linha da Raiz aparece **"Recentes ▾"**
  ao lado de "Procurar…". Clicar → lista os recentes; escolher um → preenche a Raiz (e o
  nome, se não editado). Sem recentes → item "(nenhum recente)" desabilitado. Executar numa
  raiz nova → ela aparece no menu na próxima abertura.
- **`git diff`:** só `gui.py` (root row, `_refresh_recent_menu`/`_use_recent`,
  `_persist_settings`), `__init__.py` e os meta-docs. `.bat` e seu gerador intocados.

## Commit sugerido (sem acento)

```
git add flatdrop/gui.py flatdrop/__init__.py meta/CHANGELOG.md meta/STATUS.md meta/specs/260720-spec0032-recentes-compacto.md & git commit -m "feat(gui): Recentes vira botao compacto Recentes na linha da Raiz" -m "Combobox de linha inteira substituido por um Menubutton Recentes ao lado de Procurar; libera uma linha e deixa a feature discreta. Mesmo comportamento (escolher preenche a raiz e o nome). So GUI; .bat intocado. Bump 0.9.1."
```
