"""Testes do force-include (++ no .flatdropignore) — DEC-021 / spec0027."""

from __future__ import annotations

from pathlib import Path

from flatdrop import core
from flatdrop.core import ScanConfig


def _tree(root: Path) -> None:
    (root / "lib").mkdir()
    (root / "node_modules" / "dep").mkdir(parents=True)
    (root / "webapp" / "static" / "vendor").mkdir(parents=True)
    (root / "keep.py").write_text("x", encoding="utf-8")
    (root / "app.min.js").write_text("x", encoding="utf-8")
    (root / "lib" / "vendor.min.js").write_text("x", encoding="utf-8")
    (root / "node_modules" / "dep" / "thing.min.js").write_text("x", encoding="utf-8")
    (root / "webapp" / "static" / "vendor" / "htmx.min.js").write_text("x", encoding="utf-8")
    (root / "id_rsa").write_text("secret", encoding="utf-8")


def _kept(plan) -> set[str]:
    return {f.rel.as_posix() for f in plan.files}


def test_force_include_rescues_barred_and_pruned(tmp_path):
    _tree(tmp_path)
    (tmp_path / ".flatdropignore").write_text(
        "++app.min.js\n++lib/vendor.min.js\n"
        "++node_modules/dep/thing.min.js\n++webapp/static/vendor/htmx.min.js\n",
        encoding="utf-8")
    plan = core.make_plan(tmp_path, ScanConfig())
    kept = _kept(plan)
    assert "app.min.js" in kept
    assert "lib/vendor.min.js" in kept
    assert "node_modules/dep/thing.min.js" in kept   # dentro de pasta PODADA
    assert "webapp/static/vendor/htmx.min.js" in kept
    # saiu dos pulados (não conta duas vezes)
    assert "app.min.js" not in {r for r, _ in plan.skipped_items}


def test_force_include_never_beats_sensitive(tmp_path):
    _tree(tmp_path)
    (tmp_path / ".flatdropignore").write_text("++id_rsa\n", encoding="utf-8")
    plan = core.make_plan(tmp_path, ScanConfig())
    assert "id_rsa" not in _kept(plan)
    assert any("sensivel" in w for w in plan.warnings)


def test_force_include_missing_warns(tmp_path):
    _tree(tmp_path)
    (tmp_path / ".flatdropignore").write_text("++nao/existe.min.js\n", encoding="utf-8")
    plan = core.make_plan(tmp_path, ScanConfig())
    assert any("nao encontrado" in w for w in plan.warnings)


def test_force_include_line_not_fed_to_matcher(tmp_path):
    # um '++x' não pode virar padrão de exclusão do pathspec
    _tree(tmp_path)
    (tmp_path / ".flatdropignore").write_text("++app.min.js\n", encoding="utf-8")
    kept = _kept(core.make_plan(tmp_path, ScanConfig()))
    assert "keep.py" in kept  # nada mais foi excluído por engano
