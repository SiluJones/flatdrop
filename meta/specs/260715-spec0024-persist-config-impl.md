# spec0024 — IMPLEMENTAÇÃO: persistir config + recentes (item C, só-GUI)

- **Tipo:** implementação. Aplica DEC-019 e obedece DEC-020. Roda `python -m pytest -q`.
- **Data:** 2026-07-15 · **Versão-alvo:** 0.6.0 (feature menor).
- **Pré-requisito:** spec0023 já aplicada e commitada (invariante DEC-020 no lugar).
- **Schema:** flat (a §2 da spec0022 desenhou um `last` aninhado; achatei para uma dataclass
  única `Settings` por simplicidade de round-trip — refinamento benigno, sem perder nenhum
  campo; declarado aqui para não divergir em silêncio).

## GUARDAS OBRIGATÓRIAS (DEC-020) — LEIA ANTES DE APLICAR

1. **OFF-LIMITS, zero edições:** `flatdrop/cli.py`, `gui._build_cli_args`,
   `gui._generate_bat`, `gui._sources`. Se qualquer âncora abaixo parecer exigir tocá-las,
   **PARE e reporte** — não é para acontecer.
2. Ao terminar, rode `git diff` e **confirme que essas quatro não têm uma linha alterada.**
   A persistência só ADICIONA: um módulo novo, `tk.Var` sendo pré-carregadas, um Combobox, e
   três métodos novos. Nada no caminho do `.bat`.
3. A CLI **não** importa nem lê `settings`. O teste `test_cli_has_no_settings` garante isso.

---

## Edit 1 — Novo arquivo `flatdrop/settings.py`

```python
"""Persistência da configuração da GUI do FlatDrop (só-GUI).

INVARIANTE (ver meta/DECISIONS.md, DEC-020): este módulo é EXCLUSIVO da GUI.
A CLI e o gerador de .bat NUNCA leem este arquivo — o .bat precisa continuar
sendo um snapshot reproduzível. Nada aqui pode alcançar flatdrop/cli.py nem
gui._build_cli_args/_generate_bat/_sources.

Contrato de segurança:
- load_settings() NUNCA lança (arquivo ausente/corrompido -> defaults).
- save_settings() é atômico (temp + os.replace) e best-effort: se não puder
  gravar, desliga a persistência em silêncio (loga uma vez) e devolve False,
  sem derrubar a GUI.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

from . import config as C

SETTINGS_VERSION = 1
MAX_RECENTS = 8
_MODES = ("collisions", "all", "fullpath")
_warned_save = False  # loga a falha de escrita só uma vez por processo


@dataclass
class Settings:
    """Estado persistido da GUI. Espelha os campos que a tela já serializa no
    .bat, com a allowlist como DELTA (added/removed vs DEFAULT_EXTENSIONS) para
    não congelar defaults futuros, mais a lista de raízes recentes."""

    root: str = ""
    dest: str = ""
    name: str = ""
    mode: str = "collisions"
    sep: str = C.DEFAULT_SEP
    ext_added: list[str] = field(default_factory=list)
    ext_removed: list[str] = field(default_factory=list)
    read_gitignore: bool = True
    skip_sensitive: bool = True
    write_manifest: bool = True
    write_tree: bool = False
    root_in_name: bool = False
    clear_dest: bool = True
    also_md: bool = False
    also_md_root: str = ""
    recent_roots: list[str] = field(default_factory=list)


def settings_path() -> Path:
    """Caminho do settings.json por plataforma. Só resolve; não cria nada.

    Espelha o padrão de core.default_downloads_dir(): usa a pasta de config de
    cada SO. %APPDATA% está sempre no ambiente do Windows, então dispensa a
    Known Folder API (ctypes) que o Downloads precisou.
    """
    if sys.platform.startswith("win"):
        base = os.environ.get("APPDATA")
        root = Path(base) if base else Path.home() / "AppData" / "Roaming"
        return root / "FlatDrop" / "settings.json"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "FlatDrop" / "settings.json"
    base = os.environ.get("XDG_CONFIG_HOME")
    root = Path(base) if base else Path.home() / ".config"
    return root / "flatdrop" / "settings.json"


def _norm_ext_list(value) -> list[str]:
    """Normaliza uma lista de extensões vinda do disco (tolerante a lixo)."""
    if not isinstance(value, list):
        return []
    return [x.strip().lstrip(".").lower()
            for x in value if isinstance(x, str) and x.strip()]


def _sanitize(data: dict) -> Settings:
    """Constrói um Settings tolerante a lixo: cada campo cai no default se
    ausente ou com tipo/valor inválido. Nunca lança. Garante que a allowlist
    fica como delta 'puro' (added sem defaults, removed só de defaults, sem
    sobreposição) — é o que alimenta o gerador do .bat, então tem de ser limpo."""
    s = Settings()

    def _str(k: str, default: str) -> str:
        v = data.get(k, default)
        return v if isinstance(v, str) else default

    def _bool(k: str, default: bool) -> bool:
        v = data.get(k, default)
        return v if isinstance(v, bool) else default

    s.root = _str("root", "")
    s.dest = _str("dest", "")
    s.name = _str("name", "")
    mode = _str("mode", "collisions")
    s.mode = mode if mode in _MODES else "collisions"
    sep = _str("sep", C.DEFAULT_SEP)
    s.sep = sep if sep.strip() else C.DEFAULT_SEP

    defaults = {e.lower() for e in C.DEFAULT_EXTENSIONS}
    added = set(_norm_ext_list(data.get("ext_added"))) - defaults
    removed = set(_norm_ext_list(data.get("ext_removed"))) & defaults
    overlap = added & removed
    s.ext_added = sorted(added - overlap)
    s.ext_removed = sorted(removed - overlap)

    s.read_gitignore = _bool("read_gitignore", True)
    s.skip_sensitive = _bool("skip_sensitive", True)
    s.write_manifest = _bool("write_manifest", True)
    s.write_tree = _bool("write_tree", False)
    s.root_in_name = _bool("root_in_name", False)
    s.clear_dest = _bool("clear_dest", True)
    s.also_md = _bool("also_md", False)
    s.also_md_root = _str("also_md_root", "")

    recents = data.get("recent_roots", [])
    if not isinstance(recents, list):
        recents = []
    seen: set[str] = set()
    out: list[str] = []
    for r in recents:
        if isinstance(r, str) and r and r not in seen:
            seen.add(r)
            out.append(r)
    s.recent_roots = out[:MAX_RECENTS]
    return s


def load_settings() -> Settings:
    """Lê o settings.json. NUNCA lança: qualquer problema devolve defaults."""
    try:
        raw = settings_path().read_text(encoding="utf-8")
        data = json.loads(raw)
        if not isinstance(data, dict):
            return Settings()
        return _sanitize(data)
    except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError):
        return Settings()


def save_settings(s: Settings) -> bool:
    """Grava atômico (temp + os.replace no mesmo volume). Best-effort: em falha
    de I/O devolve False sem lançar (desliga a persistência sem derrubar a GUI)
    e loga UMA vez por processo."""
    global _warned_save
    path = settings_path()
    payload = {"version": SETTINGS_VERSION, **asdict(s)}
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                       encoding="utf-8")
        os.replace(tmp, path)
        return True
    except OSError as exc:
        if not _warned_save:
            print(f"[FlatDrop] nao consegui gravar settings ({exc}); "
                  "persistencia desligada nesta sessao.", file=sys.stderr)
            _warned_save = True
        return False


def push_recent(recents: list[str], root: str, limit: int = MAX_RECENTS) -> list[str]:
    """Devolve a lista com `root` no topo, sem duplicata, cortada em `limit`.
    Função pura (não muda `recents` no lugar)."""
    root = (root or "").strip()
    if not root:
        return list(recents[:limit])
    return [root] + [r for r in recents if r != root][: limit - 1]
```

## Edit 2 — `flatdrop/gui.py`: importar o módulo

**Âncora exata:**
```
from . import config as C
from . import core
```
Trocar por:
```
from . import config as C
from . import core
from . import settings as settings_store
```

## Edit 3 — `flatdrop/gui.py`: carregar a config no `__init__`

**Âncora exata** (fim do bloco "estado" do `App.__init__`):
```
        self._name_edited = False  # usuário mexeu no nome manualmente?
        self._last_dest: Path | None = None
        self._busy = False

        self._build()
```
Trocar por:
```
        self._name_edited = False  # usuário mexeu no nome manualmente?
        self._last_dest: Path | None = None
        self._busy = False

        # Persistência é SÓ-GUI (DEC-020): carrega a última config nos widgets.
        # load_settings nunca lança; a CLI/.bat jamais leem este arquivo.
        self._settings = settings_store.load_settings()
        self._apply_settings_to_vars()

        self._build()
```

## Edit 4 — `flatdrop/gui.py`: Combobox de recentes na linha da raiz

**Âncora exata** (bloco "Pasta raiz" em `_build`):
```
        # Pasta raiz
        ttk.Label(self, text="Pasta raiz *").grid(row=r, column=0, sticky="w")
        ttk.Entry(self, textvariable=self.root_var).grid(row=r, column=1, sticky="ew", padx=6)
        ttk.Button(self, text="Procurar…", command=self._choose_root).grid(row=r, column=2)
        r += 1
```
Trocar por (acrescenta UMA linha nova logo abaixo; as demais linhas seguem o contador `r`,
então nada de layout existente é perturbado):
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

## Edit 5 — `flatdrop/gui.py`: três métodos novos

**Âncora exata** (fim do método `_choose_also_md`):
```
        if path:
            self.also_md_root_var.set(path)
            self.also_md_var.set(True)
```
Inserir DEPOIS desse bloco os métodos:
```

    # ------------------------------------------------------------------ #
    # Persistência (só-GUI; DEC-020: nada disto toca a CLI nem o gerador de .bat)
    # ------------------------------------------------------------------ #
    def _apply_settings_to_vars(self) -> None:
        """Sobrescreve os valores iniciais dos widgets com a última config salva.

        Guardas: nenhum valor inválido do disco chega aos widgets — assim o .bat
        gerado a partir da tela sempre serializa uma config válida.
        """
        s = self._settings
        if s.root:
            self.root_var.set(s.root)
        if s.name:
            self.name_var.set(s.name)
            self._name_edited = True  # não deixar o _choose_root sobrescrever
        # dest só é aceito se for uma pasta real; senão fica o default (Downloads).
        if s.dest and Path(s.dest).is_dir():
            self.dest_var.set(s.dest)
        self.mode_var.set(s.mode)          # já saneado para {collisions,all,fullpath}
        self.sep_var.set(s.sep)            # já saneado para não-vazio
        self.gitignore_var.set(s.read_gitignore)
        self.skip_sensitive_var.set(s.skip_sensitive)
        self.manifest_var.set(s.write_manifest)
        self.tree_var.set(s.write_tree)
        self.root_in_name_var.set(s.root_in_name)
        self.clear_var.set(s.clear_dest)
        self.also_md_var.set(s.also_md)
        self.also_md_root_var.set(s.also_md_root)
        # allowlist reconstruída do delta contra os defaults ATUAIS.
        defaults = set(C.DEFAULT_EXTENSIONS)
        self._selected_exts = (defaults | set(s.ext_added)) - set(s.ext_removed)

    def _on_recent_selected(self, _event=None) -> None:
        """Escolher um recente preenche a raiz (e o nome, se ainda não editado)."""
        path = self.recent_combo.get().strip()
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
            root_in_name=self.root_in_name_var.get(),
            clear_dest=self.clear_var.get(),
            also_md=self.also_md_var.get(),
            also_md_root=self.also_md_root_var.get().strip(),
            recent_roots=settings_store.push_recent(self._settings.recent_roots, root),
        )
        settings_store.save_settings(s)
        self._settings = s
        # Reflete o novo recente no Combobox dentro da mesma sessão.
        self.recent_combo.configure(values=list(s.recent_roots))
```

## Edit 6 — `flatdrop/gui.py`: gravar após Executar bem-sucedido

**Âncora exata** (início de `_render_execute`, no ponto de sucesso):
```
        plan, res = payload
        self._last_dest = res.dest
        self.btn_open.config(state="normal")
```
Trocar por:
```
        plan, res = payload
        self._last_dest = res.dest
        self.btn_open.config(state="normal")
        # Só-GUI: grava a config que acabou de dar certo + raiz recente (DEC-020).
        self._persist_settings()
```

## Edit 7 — `flatdrop/__init__.py`: bump de versão

**Âncora exata:**
```
__version__ = "0.5.2"
```
Trocar por:
```
__version__ = "0.6.0"
```

## Edit 8 — Novo arquivo `tests/test_settings.py`

```python
"""Testes do módulo de persistência (só-GUI). Puro, sem tkinter."""

from __future__ import annotations

import json

import pytest

from flatdrop import config as C
from flatdrop import settings as st


@pytest.fixture
def tmp_settings(tmp_path, monkeypatch):
    """Redireciona settings_path para um arquivo temporário."""
    target = tmp_path / "settings.json"
    monkeypatch.setattr(st, "settings_path", lambda: target)
    return target


def test_roundtrip(tmp_settings):
    s = st.Settings(root="/proj", sep="++", write_tree=True,
                    ext_added=["log"], recent_roots=["/proj", "/outra"])
    assert st.save_settings(s) is True
    got = st.load_settings()
    assert got.root == "/proj"
    assert got.sep == "++"
    assert got.write_tree is True
    assert got.recent_roots == ["/proj", "/outra"]


def test_missing_file_returns_defaults(tmp_settings):
    got = st.load_settings()
    assert got == st.Settings()  # nunca lança; tudo default


def test_corrupt_file_returns_defaults(tmp_settings):
    tmp_settings.write_text("{ isto nao e json valido ][", encoding="utf-8")
    got = st.load_settings()  # não lança
    assert got == st.Settings()


def test_sanitize_clamps_mode_and_sep(tmp_settings):
    tmp_settings.write_text(json.dumps({"mode": "banana", "sep": "   "}),
                            encoding="utf-8")
    got = st.load_settings()
    assert got.mode == "collisions"
    assert got.sep == C.DEFAULT_SEP


def test_ext_delta_is_pure(tmp_settings):
    """A allowlist salva fica como delta limpo: added sem defaults, removed só
    de defaults, sem sobreposição — é o que alimenta o gerador do .bat."""
    a_default = next(iter(C.DEFAULT_EXTENSIONS))
    tmp_settings.write_text(json.dumps({
        "ext_added": [a_default, "log", "log"],   # default e duplicata devem sair
        "ext_removed": [a_default, "xyznotdefault"],  # não-default deve sair
    }), encoding="utf-8")
    got = st.load_settings()
    assert a_default not in got.ext_added
    assert "log" in got.ext_added
    assert got.ext_removed == [a_default]
    assert not (set(got.ext_added) & set(got.ext_removed))


def test_push_recent_dedup_and_cap():
    recents = [f"/p{i}" for i in range(8)]
    out = st.push_recent(recents, "/p3")
    assert out[0] == "/p3"
    assert out.count("/p3") == 1
    assert len(out) <= st.MAX_RECENTS


def test_atomic_write_leaves_no_tmp(tmp_settings):
    st.save_settings(st.Settings(root="/x"))
    leftovers = list(tmp_settings.parent.glob("*.tmp"))
    assert leftovers == []


def test_save_failure_returns_false_no_raise(tmp_path, monkeypatch):
    # settings_path aponta para dentro de um "arquivo" (mkdir vai falhar).
    blocker = tmp_path / "blocker"
    blocker.write_text("x", encoding="utf-8")
    monkeypatch.setattr(st, "settings_path", lambda: blocker / "settings.json")
    assert st.save_settings(st.Settings()) is False  # não lança


def test_cli_has_no_settings():
    """GUARDA DEC-020: a CLI NUNCA pode ler a persistência. Se este teste
    falhar, a persistência vazou para o caminho do .bat — PARE."""
    import inspect

    from flatdrop import cli
    src = inspect.getsource(cli)
    assert "settings" not in src.lower()
    assert "import settings" not in src
```

## Edit 9 — `meta/CHANGELOG.md`: nova entrada no topo

**Âncora exata** (a linha do bloco "Não lançado" imediatamente antes de `## [0.5.2]`):
```
## [0.5.2] — 2026-07-15
```
Inserir ANTES dela:
```
## [0.6.0] — 2026-07-15

### Adicionado
- **Persistência de config + pastas recentes na GUI** (item C, spec0024, DEC-019). A GUI
  reabre com a última config usada e um Combobox de raízes recentes (dedup, até 8). Grava só
  após um Executar bem-sucedido, num `settings.json` por plataforma (`%APPDATA%\FlatDrop` no
  Windows, `~/.config/flatdrop` no Linux, `~/Library/Application Support/FlatDrop` no macOS).
  A allowlist é salva como delta (não congela defaults futuros). `load` nunca lança (arquivo
  ausente/corrompido → defaults) e `save` é atômico; falha de escrita desliga a persistência
  sem derrubar a GUI. **Escopo só-GUI (DEC-020): a CLI e o gerador de `.bat` não leem nada
  disto — o `.bat` segue snapshot reproduzível.** Guarda `test_cli_has_no_settings`.

```

## Edit 10 — `meta/STATUS.md`: refletir item C fechado

**Âncora exata** (a linha da revisão da spec0021):
```
- **(2026-07-15, spec0021 aplicada) Editor de `.flatdropignore` (Fase 2-D) fechado:**
  glifo da pasta correto já na visão colapsada (`core.folder_effective_state`, FIX-007).
  Versão **0.5.2**, **49 testes verdes**. Próxima = item C (persistência).
```
Trocar por:
```
- **(2026-07-15, spec0021 aplicada) Editor de `.flatdropignore` (Fase 2-D) fechado:**
  glifo da pasta correto já na visão colapsada (`core.folder_effective_state`, FIX-007).
- **(2026-07-15, spec0024 aplicada) Item C — persistência entregue:** `flatdrop/settings.py`
  grava config + recentes (só-GUI; DEC-020 blinda o `.bat`). Versão **0.6.0**,
  **58 testes verdes**. Próxima = multi-raiz na GUI.
```

---

## O que testar

- **Automatizado** (`python -m pytest -q`): os 9 testes novos de `tests/test_settings.py`
  (49 → 58 verdes). O `test_cli_has_no_settings` é a guarda do DEC-020.
- **Smoke manual da GUI (Windows) — PORTÃO DE ACEITE:**
  1. Abrir a GUI, montar uma config (raiz, tipos, flags), **Executar**. Reabrir → os campos
     voltam como estavam; a raiz aparece no Combobox de recentes.
  2. **Prova do `.bat` (o que importa):** com uma config carregada da última sessão, clicar
     **"Gerar .bat…"**, e conferir que o `.bat` gerado é **idêntico** ao que sairia digitando
     a mesma config à mão, e que **roda** e reproduz a saída. Se divergir, é regressão do
     `.bat` → PARE, reporte, reverta (DEC-020).
  3. `settings.json` com `dest` de uma pasta apagada → ao abrir cai no Downloads, sem erro.
  4. Corromper o `settings.json` à mão → a GUI abre com defaults, sem travar.

## Merece print no README

A linha da raiz com o **Combobox de recentes** aberto (mostra o atalho novo). Só sinalizar a
captura; não gerar imagem.

## Commit sugerido (sem acento)

```
git add flatdrop/settings.py flatdrop/gui.py flatdrop/__init__.py tests/test_settings.py meta/CHANGELOG.md meta/STATUS.md meta/specs/260715-spec0024-persist-config-impl.md & git commit -m "feat(gui): persistir config e pastas recentes (so-GUI)" -m "Novo flatdrop/settings.py grava config + recentes num settings.json por plataforma; a GUI reabre com a ultima config e um Combobox de recentes. Grava so apos Executar bem-sucedido. Escopo so-GUI: a CLI e o gerador de .bat nao leem nada (DEC-020), .bat segue reproduzivel. load nunca lanca, save atomico. 9 testes novos incl. guarda test_cli_has_no_settings (49 -> 58). Bump 0.6.0. item C / DEC-019."
```
