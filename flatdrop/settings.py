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
