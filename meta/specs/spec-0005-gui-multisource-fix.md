# spec-0005 — GUI: multi-fonte ao vivo + Procurar na pasta-pai + abrir maximizada

**Tipo:** código · **Alvo:** `flatdrop/gui.py` · **Autor:** chat · **Aplicador:** Claude Code
**Depende de:** spec-0003 aplicada.
**Origem:** teste do usuário (print + console). Três correções pequenas.

## Problemas que isto corrige
1. **FIX-004 — o toggle multi-fonte não afetava a execução ao vivo.** `_on_preview`/`_on_execute`
   chamavam `core.make_plan(root, cfg)` (fonte única). O toggle "Também incluir todos os .md a partir de:"
   só era lido pelo gerador de `.bat` (`_build_cli_args`). Resultado: o `.bat` fazia área+todos-os-`.md`,
   mas "Pré-visualizar"/"Executar" na UI faziam só o normal. Omissão da spec-0003.
2. **"Procurar…"** do "Também incluir todos os .md" abria na pasta atual; o usuário quer que abra na
   **pasta-pai da raiz** (a raiz do repo costuma ser o pai da pasta de área).
3. **Abrir maximizada** — pedido para aproveitar melhor a tela.

## Validação
- `python -m pytest -q` → 26/26 (core/CLI intactos).
- Smoke manual no Windows: marcar o toggle, apontar a raiz do repo, clicar **Pré-visualizar** → deve
  mostrar "Fontes (2)" e os .md de todo o repo (igual ao `.bat`). Conferir que abre maximizada e que o
  "Procurar…" do multi-fonte começa na pasta-pai da raiz.

---

## EDIÇÃO 1 — importar `replace` (dataclasses)

**Âncora:**
```
import threading
```
**Ação:** inserir logo APÓS essa linha:
```
from dataclasses import replace
```

## EDIÇÃO 2 — abrir maximizada

**Âncora:**
```
        master.minsize(720, 620)
```
**Ação:** inserir logo APÓS essa linha:
```
        try:
            master.state("zoomed")  # abre maximizada (Windows; alguns Linux)
        except tk.TclError:
            try:
                master.attributes("-zoomed", True)  # fallback X11
            except tk.TclError:
                pass
```

## EDIÇÃO 3 — "Procurar…" do multi-fonte começa na pasta-pai da raiz

**Âncora (método atual, substituir inteiro):**
```
    def _choose_also_md(self) -> None:
        path = filedialog.askdirectory(title="Raiz para incluir todos os .md")
        if path:
            self.also_md_root_var.set(path)
            self.also_md_var.set(True)
```
**Ação:** SUBSTITUIR por:
```
    def _choose_also_md(self) -> None:
        root = self.root_var.get().strip()
        initial = str(Path(root).parent) if root and Path(root).is_dir() else None
        path = filedialog.askdirectory(
            title="Raiz para incluir todos os .md", initialdir=initial)
        if path:
            self.also_md_root_var.set(path)
            self.also_md_var.set(True)
```

## EDIÇÃO 4 — helper `_sources` (montar a lista de fontes do jeito do gerador)

**Âncora (fim do método `_gather_cfg`):**
```
            only_ext=(_parse_exts(self.only_ext_var.get()) or None),
            exclude_ext=_parse_exts(self.exclude_ext_var.get()),
        )
```
**Ação:** inserir logo APÓS esse método (antes de `def _dest_path`):
```

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
```

## EDIÇÃO 5 — `_on_preview` usa multi-fonte

**Âncora (método atual, substituir inteiro):**
```
    def _on_preview(self) -> None:
        if not self._validate_root():
            return
        cfg = self._gather_cfg()
        root = self.root_var.get().strip()
        self.status.config(text="Varrendo…")
        self._run_async(lambda: core.make_plan(root, cfg), self._render_preview)
```
**Ação:** SUBSTITUIR por:
```
    def _on_preview(self) -> None:
        if not self._validate_root():
            return
        primary = self._gather_cfg()
        sources = self._sources(primary)
        self.status.config(text="Varrendo…")
        self._run_async(lambda: core.make_plan_sources(sources), self._render_preview)
```

## EDIÇÃO 6 — `_on_execute` usa multi-fonte

**Âncora (método atual, substituir inteiro):**
```
    def _on_execute(self) -> None:
        if not self._validate_root():
            return
        cfg = self._gather_cfg()
        root = self.root_var.get().strip()
        dest = self._dest_path()
        self.status.config(text="Copiando…")

        def work():
            plan = core.make_plan(root, cfg)
            res = core.execute_plan(plan, dest, cfg)
            return plan, res

        self._run_async(work, self._render_execute)
```
**Ação:** SUBSTITUIR por:
```
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
```
