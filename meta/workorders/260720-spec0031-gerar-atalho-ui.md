# spec0031 — "Gerar atalho da UI" na GUI (menu Ferramentas), salvo uma pasta acima do repo

- **Tipo:** implementação (GUI + gerador). Roda `python -m pytest -q`. Versão-alvo:
  **0.9.0** (0.8.0 → 0.9.0; feature nova).
- **Data:** 2026-07-20 · **Referência:** o ASU tem "Criar atalho .bat (abrir GUI)"; aqui a
  ideia é a mesma, mas **posicionada melhor** (o ASU a pôs colada ao botão do `.bat` prático,
  o que o autor não quis).
- **Pedido:** um botão na GUI que **gera o `.bat` "abrir GUI"** (hoje o `flatdrop-ui.bat` é
  mantido à mão), salvando por padrão **uma pasta acima da raiz do repo** — que é onde os
  `.bat` do FlatDrop já vivem.
- **Fato de contexto (nota 260720-1651, antes não registrado):** o repo é
  `…\FlatDrop\flatdrop\`; o RUN `.bat` (`flatdrop.bat`) e o atalho "abrir GUI"
  (`Launcher\flatdrop-ui.bat`) ficam em `…\FlatDrop\` — **fora do worktree**, para não serem
  achatados nem versionados. O gerador respeita essa convenção: default = pai da raiz do repo.

## GUARDA (DEC-020)

Este é um gerador **NOVO e separado** (o atalho "abrir GUI", genérico, sem `--root`). O
gerador do **RUN `.bat`** (`_generate_bat`/`_build_cli_args`/`_generate_bat`/`_sources`/
`cli.py`) **não é tocado** — `git diff` deve confirmar. Se alguma âncora parecer exigir
mexer nele, PARE e reporte.

## Escolha de posição (decisão de design)

O atalho "abrir GUI" é uma ação de **configuração única** da ferramenta (gera-se uma vez e
copia-se para as pastas de projeto) — **não** é uma ação por-execução como
"Executar"/"Gerar .bat…" (que reproduzem a config atual). Por isso **não** vai na barra de
ações de baixo (evita o aperto que o ASU criou). Vai numa **barra de menu → "Ferramentas" →
"Gerar atalho da UI…"**: lugar convencional para setup, discreto, some do fluxo por-execução
e tem espaço para crescer. (Se preferir um botão visível, dá para trocar depois; o menu é a
escolha mais limpa para uma ação rara.)

---

## Edit 1 — `gui.py`: função pura com o conteúdo do atalho (testável)

**Âncora exata** (a assinatura de `main`, atualizada pela spec0030):
```
def main(start_dir: str | None = None) -> None:
```
Inserir ANTES dela:
```
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
```

## Edit 2 — `gui.py`: método que abre o diálogo e grava

**Âncora exata** (fim de `_generate_bat`):
```
        content = "\r\n".join(lines) + "\r\n"
        Path(path).write_text(content, encoding="utf-8", newline="")
        messagebox.showinfo("FlatDrop", "'.bat' gerado em:\n" + path)

    def _update_types_summary(self) -> None:
```
Trocar por:
```
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
```

## Edit 3 — `gui.py`: barra de menu "Ferramentas" no `_build`

**Âncora exata** (início de `_build`):
```
    def _build(self) -> None:
        self.columnconfigure(1, weight=1)
        r = 0
```
Trocar por:
```
    def _build(self) -> None:
        # Barra de menu: ações de configuração da própria ferramenta (uma vez), fora
        # do fluxo de execução. "Gerar atalho da UI…" cria o .bat que abre a GUI e que
        # você copia para pastas de projeto (spec0031). NÃO é o RUN .bat (DEC-020).
        menubar = tk.Menu(self.master)
        tools = tk.Menu(menubar, tearoff=0)
        tools.add_command(label="Gerar atalho da UI…",
                          command=self._generate_open_gui_bat)
        menubar.add_cascade(label="Ferramentas", menu=tools)
        self.master.config(menu=menubar)

        self.columnconfigure(1, weight=1)
        r = 0
```

## Edit 4 — teste do conteúdo do atalho em `tests/test_cli.py`

**Âncora:** acrescentar ao **fim** de `tests/test_cli.py` (junto dos testes de dispatch da
spec0030; se preferir, `tests/test_open_gui_bat.py` novo — **reporte** onde ficou):
```python


def test_open_gui_bat_content_semeia_start_dir():
    """spec0031: o atalho 'abrir GUI' gerado leva --start-dir e NÃO leva --root."""
    from pathlib import Path

    from flatdrop.gui import _open_gui_bat_content

    txt = _open_gui_bat_content(Path("C:/FlatDrop/flatdrop/run.py"))
    assert '--start-dir "%~dp0."' in txt
    assert "--root" not in txt          # generico: NAO e o RUN .bat (DEC-020)
    assert "run.py" in txt
    assert txt.startswith("@echo off")
    assert txt.endswith("\r\n")         # CRLF, como o RUN .bat
```

## Edit 5 — `flatdrop/__init__.py`: bump

**Âncora exata:** `__version__ = "0.8.0"` → trocar por `__version__ = "0.9.0"`

## Edit 6 — `meta/CHANGELOG.md`: entrada [0.9.0]

**Âncora exata:** `## [0.8.0] — 2026-07-20`
Inserir ANTES dela:
```
## [0.9.0] — 2026-07-20

### Adicionado
- **Menu "Ferramentas → Gerar atalho da UI…" (spec0031).** A GUI passa a gerar o `.bat` que
  abre a interface (antes mantido à mão), já com `--start-dir "%~dp0."` (o "Procurar…" abre
  na pasta do atalho, spec0030). Salva por padrão **uma pasta acima da raiz do repo** — onde
  os `.bat` do FlatDrop já vivem, fora do worktree (não são achatados nem versionados). É um
  gerador **novo e separado**; o RUN `.bat` (`_generate_bat`/`_build_cli_args`) fica
  **intocado** (DEC-020). Colocado num menu (ação de setup, uma vez), não na barra de ações
  por-execução. 1 teste novo (65 → 66).

```

## Edit 7 — `meta/STATUS.md`: refletir 0.9.0

**Âncora exata** (bloco da nota de revisão, inteiro):
```
> **Mudanças nesta revisão (2026-07-20):** **pausa interrompida** pelo uso real. O atalho
> "abrir GUI" agora **semeia a navegação** (`--start-dir "%~dp0."`) e **abre limpo**
> (spec0030, 0.8.0) — clicar o `.bat` numa pasta de projeto faz o "Procurar…" abrir ali.
> Versão **0.8.0**, **65 testes verdes**. O RUN `.bat` seguiu intocado (DEC-020, teste de
> guarda). Nada quebrado; sem fase grande pendente. **Ao voltar ao repouso:** ler este
> STATUS, o `CHANGELOG` e as Ativas do `IDEAS.md`; a frente candidata segue sendo
> **multi-raiz na GUI**, que **exige decisão do autor antes de desenhar** (opções A/B na
> "Decisão pendente" abaixo). Pendente também: avaliar compactar os **Recentes** num botão
> "Recentes ▾" (estilo ASU) em vez do Combobox de linha inteira.
```
Trocar por:
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

---

## O que testar

- **Automatizado:** 65 → **66** (o teste do conteúdo é a guarda DEC-020: sem `--root`).
- **Manual (Windows):** menu **Ferramentas → "Gerar atalho da UI…"** → o diálogo de salvar
  abre **uma pasta acima do repo**; salvar; o `.bat` gerado abre a GUI e, copiado para uma
  pasta de projeto, faz o "Procurar…" abrir ali. Conferir que "Gerar .bat…" (o RUN) segue
  igual.
- **`git diff`:** `_build_cli_args`, `_generate_bat`, `_sources`, `cli.py` intocados.

## Merece print no README

O menu "Ferramentas" aberto com "Gerar atalho da UI…". Só sinalizar.

## Commit sugerido (sem acento)

```
git add flatdrop/gui.py flatdrop/__init__.py tests/test_cli.py meta/CHANGELOG.md meta/STATUS.md meta/specs/260720-spec0031-gerar-atalho-ui.md & git commit -m "feat(gui): menu Ferramentas gera o atalho abrir GUI" -m "Novo gerador do .bat que abre a interface (--start-dir %~dp0.), salvo por padrao uma pasta acima da raiz do repo (onde os .bat vivem, fora do worktree). Gerador novo e separado; RUN .bat intocado (DEC-020). Menu de setup, nao na barra de acoes. 1 teste (65 -> 66). Bump 0.9.0."
```
