# spec0030 — Atalho "abrir GUI" semeia a navegação (`--start-dir`) e começa limpo

- **Tipo:** implementação (GUI + launcher). Roda `python -m pytest -q`. Versão-alvo:
  **0.8.0** (0.7.1 → 0.8.0; feature nova).
- **Data:** 2026-07-20 · **Referência:** ASU specs 0011 (semear) + 0012 (começar limpo),
  adaptadas à estrutura do FlatDrop (tkinter + `run.py` como entry compartilhado).
- **Pedido:** o `flatdrop-ui.bat` (atalho "abrir GUI") é copiado para pastas de projetos
  variados. Ao abrir a GUI e clicar "Procurar…" na Raiz, o diálogo deve começar **na pasta
  onde o `.bat` está** — entra-se no projeto com um clique, sem caçar.

## GUARDA (DEC-020) — atenção: mexe PERTO do caminho do `.bat`

O gerador do **RUN `.bat`** (`gui._build_cli_args`, `gui._generate_bat`, `gui._sources`,
`flatdrop/cli.py`) **NÃO é tocado** — permanece na lista intocável, com prova no `git diff`.
Esta spec mexe no `run.py` (dispatch de entrada, compartilhado com o RUN `.bat`) de forma
**aditiva**: extrai `--start-dir` **antes** do dispatch. O **RUN `.bat` nunca passa
`--start-dir`**, então o argv que chega à CLI de flatten é **idêntico** ao de hoje. Há
**teste de guarda** (`test_run_root_still_flatten`) que trava isso. E o `flatdrop-ui.bat`
editado é o atalho "abrir GUI" — arquivo **estático**, NÃO é o RUN `.bat` gerado. Se alguma
âncora parecer exigir tocar as quatro funções protegidas, PARE e reporte.

**Alternativa considerada e descartada:** usar `start "" /d "%~dp0." …` e ler o `cwd` na
GUI (não tocaria `run.py`). Descartada porque o `cwd` não é sinal confiável de "aberto pelo
atalho" — e precisamos desse sinal para a GUI **começar limpa** (senão a última raiz salva
sobrescreve a semente, exatamente o bug do ASU spec0012). O `--start-dir` é o marcador
explícito e inequívoco.

---

## Edit 1 — `run.py`: extrair `--start-dir` antes do dispatch (com helper testável)

**Âncora exata** (a função `_run` inteira):
```
def _run() -> None:
    argv = sys.argv[1:]
    if argv:
        # Modo terminal/.bat: roda direto, sem abrir janela.
        from flatdrop.cli import main as cli_main

        raise SystemExit(cli_main(argv))
    # Sem argumentos: experiência de duplo-clique -> interface gráfica.
    from flatdrop.gui import main as gui_main

    gui_main()
```
Trocar por:
```
def _split_start_dir(argv: list[str]) -> tuple[str | None, list[str]]:
    """Extrai ``--start-dir`` (argumento SÓ-GUI) de ``argv``.

    Devolve ``(start_dir, resto)``. O ``resto`` VAZIO significa "abrir a GUI"; o
    ``resto`` não-vazio (ex.: ``--root``) significa "rodar o flatten". O RUN .bat
    NUNCA passa ``--start-dir``, então para ele o ``resto`` é idêntico ao ``argv``
    original — o caminho do .bat não muda (DEC-020). Função pura e testável.
    """
    if "--start-dir" not in argv:
        return None, argv
    i = argv.index("--start-dir")
    if i + 1 < len(argv):
        return argv[i + 1], argv[:i] + argv[i + 2:]
    return None, argv[:i] + argv[i + 1:]


def _run() -> None:
    start_dir, rest = _split_start_dir(sys.argv[1:])
    if rest:
        # Modo terminal/.bat: roda direto, sem abrir janela.
        from flatdrop.cli import main as cli_main

        raise SystemExit(cli_main(rest))
    # Sem argumentos de flatten: experiência de duplo-clique -> interface gráfica.
    from flatdrop.gui import main as gui_main

    gui_main(start_dir=start_dir)
```

## Edit 2 — `gui.main()`: aceitar e repassar `start_dir`

**Âncora exata:**
```
def main() -> None:
    """Ponto de entrada: cria a janela e entra no loop do tkinter."""
    root = tk.Tk()
    try:
        ttk.Style().theme_use("vista" if sys.platform.startswith("win") else "clam")
    except tk.TclError:
        pass
    FlatDropApp(root)
    root.mainloop()
```
Trocar por:
```
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
```

## Edit 3 — `FlatDropApp.__init__`: assinatura + guardar a semente

**Âncora exata (3a):**
```
    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master, padding=12)
```
Trocar por:
```
    def __init__(self, master: tk.Tk, *, start_dir: str | None = None) -> None:
        super().__init__(master, padding=12)
```

**Âncora exata (3b):**
```
        self._name_edited = False  # usuário mexeu no nome manualmente?
        self._last_dest: Path | None = None
        self._busy = False

        # Persistência é SÓ-GUI (DEC-020): carrega a última config nos widgets.
```
Trocar por:
```
        self._name_edited = False  # usuário mexeu no nome manualmente?
        self._last_dest: Path | None = None
        self._busy = False
        # Semente de navegação do atalho "abrir GUI" (--start-dir "%~dp0."): pasta
        # onde "Procurar…" começa quando não há raiz. NÃO define a raiz (spec0030).
        self._start_dir = start_dir or ""

        # Persistência é SÓ-GUI (DEC-020): carrega a última config nos widgets.
```

## Edit 4 — `_apply_settings_to_vars`: começar LIMPO quando aberto pelo atalho

**Âncora exata:**
```
        s = self._settings
        if s.root:
            self.root_var.set(s.root)
```
Trocar por:
```
        # Atalho "abrir GUI" (--start-dir presente): começa LIMPO — não restaura a
        # última sessão. O atalho é genérico e copiado para pastas variadas;
        # restaurar o projeto anterior faria "Procurar…" abrir no lugar errado
        # (a raiz restaurada venceria a semente). O Combobox de Recentes segue
        # disponível (nada se perde). Rodar a GUI sem --start-dir restaura como
        # antes. (spec0030 — espelha ASU spec0012.)
        if self._start_dir:
            return
        s = self._settings
        if s.root:
            self.root_var.set(s.root)
```

## Edit 5 — `_choose_root`: abrir o diálogo na semente

**Âncora exata:**
```
    def _choose_root(self) -> None:
        path = filedialog.askdirectory(title="Escolha a pasta raiz do projeto")
        if not path:
            return
        self.root_var.set(path)
        if not self._name_edited:
            self.name_var.set(Path(path).name)
```
Trocar por:
```
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
```

## Edit 6 — `flatdrop-ui.bat`: passar a própria pasta como semente

**Âncora exata:**
```
start "" pythonw "C:\Users\alexk\Arquiteturas\FlatDrop\flatdrop\run.py"
```
Trocar por:
```
rem  --start-dir "%~dp0." faz "Procurar..." abrir NA PASTA ONDE ESTE .bat ESTA
rem  (para onde voce copia o atalho, junto dos projetos). NAO define a raiz, e a
rem  GUI abre limpa. O sufixo "." e obrigatorio: %~dp0 termina em barra e "%~dp0"
rem  escaparia a aspa; "%~dp0." vira C:\pasta\. valido (mesmo truque do ASU).
start "" pythonw "C:\Users\alexk\Arquiteturas\FlatDrop\flatdrop\run.py" --start-dir "%~dp0."
```

## Edit 7 — testes do dispatch (guarda DEC-020) em `tests/test_cli.py`

**Âncora:** acrescentar ao **fim** de `tests/test_cli.py` (é o arquivo de testes de entrada;
se preferir, um `tests/test_run.py` novo — **reporte** onde ficou):
```python


def test_run_start_dir_routes_to_gui():
    """spec0030: só --start-dir => resto vazio => abre a GUI com a semente."""
    from run import _split_start_dir

    sd, rest = _split_start_dir(["--start-dir", "C:/proj"])
    assert sd == "C:/proj"
    assert rest == []


def test_run_root_still_flatten():
    """GUARDA DEC-020: o RUN .bat (--root ...) segue indo para o flatten, intacto."""
    from run import _split_start_dir

    argv = ["--root", "C:/proj", "--name", "proj", "--tree"]
    sd, rest = _split_start_dir(argv)
    assert sd is None
    assert rest == argv  # idêntico — o caminho do .bat não muda


def test_run_start_dir_with_root_goes_flatten():
    """Se sobrar --root além de --start-dir, é flatten (o resto não fica vazio)."""
    from run import _split_start_dir

    sd, rest = _split_start_dir(["--start-dir", "X", "--root", "C:/p"])
    assert sd == "X"
    assert rest == ["--root", "C:/p"]
```

## Edit 8 — `flatdrop/__init__.py`: bump

**Âncora exata:** `__version__ = "0.7.1"` → trocar por `__version__ = "0.8.0"`

## Edit 9 — `meta/CHANGELOG.md`: entrada [0.8.0]

**Âncora exata:** `## [0.7.1] — 2026-07-16`
Inserir ANTES dela:
```
## [0.8.0] — 2026-07-20

### Adicionado
- **Atalho "abrir GUI" semeia a navegação (`--start-dir`, spec0030).** O `flatdrop-ui.bat`
  passa a mandar `--start-dir "%~dp0."`, então o "Procurar…" da Raiz abre **na pasta onde o
  `.bat` está** — que é para onde o atalho é copiado, junto dos projetos. O argumento apenas
  SEMEIA a navegação; **não define a raiz**. E, quando presente, a GUI **abre limpa** (não
  restaura a última sessão) — senão a raiz salva sobrescreveria a semente e o diálogo abriria
  no projeto anterior. O Combobox de **Recentes** segue disponível. Rodar `run.py` sem
  `--start-dir` restaura a sessão como antes. **Só-GUI/launcher: o gerador do RUN `.bat` e a
  CLI de flatten ficam intocados (DEC-020), com teste de guarda.** 3 testes novos (62 → 65).

```

## Edit 10 — `meta/STATUS.md`: sair da pausa, refletir 0.8.0

**Âncora exata** (bloco da nota de revisão, inteiro):
```
> **Mudanças nesta revisão (2026-07-17):** specs 0021–0029 aplicadas e commitadas.
> Fechados nesta leva: **editor de `.flatdropignore` (Fase 2-D)**, **item C
> (persistência + recentes)**, **force-include `++`** e o **FIX-008** (nome voltando a
> renomear ao trocar de raiz). Versão **0.7.1**, **62 testes verdes**. Invariante
> **DEC-020** grava que o `.bat` não pode ser degradado por conveniência.
> **O projeto entra em PAUSA PLANEJADA a partir de 2026-07-17** — ferramenta estável e
> em uso real, sem bug aberto e sem fase grande pendente. **Ao retomar:** ler este
> STATUS, o `CHANGELOG` e as Ativas do `IDEAS.md`; a frente candidata é **multi-raiz na
> GUI**, que **exige decisão do autor antes de desenhar** (ver "Decisão pendente" abaixo).
```
Trocar por:
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

---

## O que testar

- **Automatizado** (`python -m pytest -q`): 62 → **65**. O `test_run_root_still_flatten` é a
  guarda DEC-020 (o RUN `.bat` segue indo ao flatten com argv idêntico).
- **Smoke manual (Windows) — é o ponto da spec:**
  1. Copiar `flatdrop-ui.bat` para uma pasta de projeto qualquer; duplo-clique.
  2. A GUI abre **limpa** (Raiz vazia). Clicar "Procurar…" na Raiz → o diálogo abre
     **naquela pasta**, não em Downloads nem no último projeto. Repetir com o `.bat` noutra
     pasta → a semente acompanha o arquivo.
  3. Conferir que o Combobox **Recentes** ainda lista os projetos anteriores.
  4. Rodar `python run.py` na mão (sem `--start-dir`) → a última sessão **volta** a ser
     restaurada (comportamento de antes).
  5. **Regressão do `.bat`:** gerar um RUN `.bat` pela GUI ("Gerar .bat…") e rodá-lo →
     produz o MESMO resultado de sempre (não foi afetado).
- **`git diff`:** `_build_cli_args`, `_generate_bat`, `_sources`, `cli.py` sem uma linha
  alterada.

## Merece print no README

O diálogo "Procurar…" abrindo já na pasta do projeto após clicar o atalho copiado. Só
sinalizar; não gerar imagem.

## Commit sugerido (sem acento)

```
git add run.py flatdrop/gui.py flatdrop-ui.bat flatdrop/__init__.py tests/test_cli.py meta/CHANGELOG.md meta/STATUS.md meta/specs/260720-spec0030-start-dir-atalho-gui.md & git commit -m "feat: atalho abrir GUI semeia a navegacao (--start-dir) e comeca limpo" -m "flatdrop-ui.bat passa --start-dir %~dp0.; run.py extrai o arg SO-GUI antes do dispatch (RUN .bat nunca passa --start-dir, entao o flatten fica identico, com teste de guarda). Procurar da Raiz abre na pasta do .bat; com --start-dir a GUI abre limpa (nao restaura a ultima sessao); Recentes segue disponivel. Gerador do RUN .bat intocado (DEC-020). 3 testes (62 -> 65). Bump 0.8.0."
```
