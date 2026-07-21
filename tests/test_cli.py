"""Testes da CLI. Rode com: pytest -q (a partir da raiz do repo).

A CLI é fina (traduz argumentos -> core), então aqui basta garantir que os
argumentos viram as fontes/filtros certos e que o multi-fonte do --also-md-from
é montado como esperado.
"""

from pathlib import Path

from flatdrop import cli


def _tree(root: Path, files: dict[str, str]) -> None:
    for rel, content in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")


def _mono(tmp_path: Path) -> Path:
    root = tmp_path / "cinzeiro"
    root.mkdir()
    _tree(
        root,
        {
            "HUB.md": "h",
            "Story/meta/BIBLIA.md": "b",
            "Story/dev/cena.gd": "x",
            "Art/meta/ESTILO.md": "e",
        },
    )
    return root


def test_only_md_preview(tmp_path, capsys):
    root = _mono(tmp_path)
    rc = cli.main(["--root", str(root), "--only-ext", "md", "--no-gitignore", "--preview"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "PRÉ-VISUALIZAÇÃO" in out
    assert "Arquivos a copiar: 3" in out  # os 3 .md (HUB, BIBLIA, ESTILO)


def test_also_md_from_builds_two_sources(tmp_path):
    root = _mono(tmp_path)
    args = cli.build_parser().parse_args(
        [
            "--root", str(root / "Story"), "--exclude-ext", "md",
            "--add-ext", "gd", "--also-md-from", str(root), "--no-gitignore",
        ]
    )
    primary = cli._primary_cfg(args)
    assert primary.exclude_ext == {"md"}
    assert "gd" in primary.extensions
    assert primary.use_gitignore is False
    assert args.also_md_from == [str(root)]


def test_execute_creates_single_manifest(tmp_path, capsys):
    root = _mono(tmp_path)
    dest = tmp_path / "out"
    rc = cli.main(
        [
            "--root", str(root / "Story"), "--exclude-ext", "md",
            "--add-ext", "gd", "--also-md-from", str(root),
            "--name", "Story-pack", "--no-gitignore", "--dest", str(dest),
            "--no-name-meta",
        ]
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "CONCLUÍDO" in out
    pack = dest / "Story-pack"
    names = {p.name for p in pack.iterdir()}
    assert {"cena.gd", "HUB.md", "BIBLIA.md", "ESTILO.md", "_MANIFEST.md"} <= names
    assert len(list(pack.glob("_MANIFEST*.md"))) == 1


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


def test_open_gui_bat_content_semeia_start_dir():
    """spec0031: o atalho 'abrir GUI' gerado leva --start-dir e NAO leva --root."""
    from pathlib import Path

    from flatdrop.gui import _open_gui_bat_content

    txt = _open_gui_bat_content(Path("C:/FlatDrop/flatdrop/run.py"))
    assert '--start-dir "%~dp0."' in txt
    assert "--root" not in txt          # generico: NAO e o RUN .bat (DEC-020)
    assert "run.py" in txt
    assert txt.startswith("@echo off")
    assert txt.endswith("\r\n")         # CRLF, como o RUN .bat
