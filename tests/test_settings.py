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
