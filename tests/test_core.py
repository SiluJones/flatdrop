"""Testes da lógica central. Rode com: pytest -q  (a partir da raiz do repo)."""

from pathlib import Path

import pytest

from flatdrop.core import (
    ScanConfig,
    Source,
    default_downloads_dir,
    execute_plan,
    is_our_folder,
    make_plan,
    make_plan_sources,
    safe_clear,
    split_name,
)


def _tree(root: Path, files: dict[str, str]) -> None:
    for rel, content in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")


@pytest.fixture()
def project(tmp_path: Path) -> Path:
    root = tmp_path / "proj"
    root.mkdir()
    _tree(
        root,
        {
            "app/users/page.tsx": "1",
            "app/admin/page.tsx": "2",
            "app/users/index.tsx": "3",
            "app/admin/index.tsx": "4",
            "pages/users/index.tsx": "5",
            "src/users/index.tsx": "6",
            "src/core/__init__.py": "",
            "src/api/__init__.py": "",
            "src/only/here.ts": "u",  # único, em subpasta
            "README.md": "# r",
            ".gitignore": "*.log\nsecret.key\nbuild/\n",
            "secret.key": "x",
            ".env": "T=1",
            ".env.example": "T=",
            "logo.png": "PNG",
            "package-lock.json": "{}",
            "debug.log": "noise",
            "build/out.js": "compiled",
            "node_modules/a/b.js": "dep",
        },
    )
    return root


def _names(plan):
    return {f.target.lower() for f in plan.files}


@pytest.mark.parametrize("mode", ["collisions", "all", "fullpath"])
def test_names_are_unique(project, mode):
    plan = make_plan(project, ScanConfig(mode=mode))
    names = [f.target.lower() for f in plan.files]
    assert len(names) == len(set(names)), f"nomes repetidos no modo {mode}"


def test_gitignore_and_defaults_skip(project):
    plan = make_plan(project, ScanConfig(mode="collisions"))
    targets = {f.rel.as_posix() for f in plan.files}
    assert "debug.log" not in targets          # .gitignore *.log
    assert "secret.key" not in targets          # .gitignore + sensível
    assert "build/out.js" not in targets        # .gitignore build/
    assert "node_modules/a/b.js" not in targets  # dir ignore embutido
    assert "package-lock.json" not in targets    # ignore padrão
    assert "logo.png" not in targets             # tipo não aceito


def test_sensitive_env_but_example_allowed(project):
    plan = make_plan(project, ScanConfig(mode="collisions"))
    targets = {f.rel.as_posix() for f in plan.files}
    assert ".env" not in targets
    assert ".env.example" in targets  # exemplo é seguro


def test_collisions_mode_leaves_unique_file_intact(project):
    plan = make_plan(project, ScanConfig(mode="collisions"))
    by_rel = {f.rel.as_posix(): f for f in plan.files}
    assert by_rel["README.md"].target == "README.md"
    assert by_rel["README.md"].renamed is False
    # arquivo único em subpasta NÃO ganha sufixo no modo collisions
    assert by_rel["src/only/here.ts"].target == "here.ts"


def test_all_mode_suffixes_unique_file_in_subfolder(project):
    plan = make_plan(project, ScanConfig(mode="all"))
    by_rel = {f.rel.as_posix(): f for f in plan.files}
    # no modo "all", o arquivo único em subpasta ganha a pasta-pai
    assert by_rel["src/only/here.ts"].target == "here__only.ts"
    # arquivo na raiz não tem pasta-pai -> permanece
    assert by_rel["README.md"].target == "README.md"


def test_collision_group_uses_uniform_depth(project):
    plan = make_plan(project, ScanConfig(mode="collisions"))
    index_targets = {
        f.target for f in plan.files if f.rel.name == "index.tsx"
    }
    # todos os index.tsx desambiguam com 2 níveis (uniforme)
    assert index_targets == {
        "index__app__admin.tsx",
        "index__app__users.tsx",
        "index__pages__users.tsx",
        "index__src__users.tsx",
    }


def test_execute_writes_manifest_and_marks_folder(project, tmp_path):
    dest = tmp_path / "out" / "proj"
    cfg = ScanConfig(mode="collisions")
    res = execute_plan(make_plan(project, cfg), dest, cfg)
    assert res.copied == len(make_plan(project, cfg).files)
    assert (res.dest / "_MANIFEST.md").is_file()
    assert is_our_folder(res.dest) is True


def test_reexecute_clears_our_own_folder(project, tmp_path):
    dest = tmp_path / "out" / "proj"
    cfg = ScanConfig(mode="collisions")
    res1 = execute_plan(make_plan(project, cfg), dest, cfg)
    # deixa um arquivo órfão para provar que a limpeza acontece
    (res1.dest / "orfao__x.txt").write_text("velho", encoding="utf-8")
    res2 = execute_plan(make_plan(project, cfg), dest, cfg)
    assert res2.dest == res1.dest
    assert res2.cleared is True
    assert not (res2.dest / "orfao__x.txt").exists()


def test_safe_clear_refuses_foreign_folder(tmp_path):
    foreign = tmp_path / "importante"
    foreign.mkdir()
    (foreign / "dados.txt").write_text("não apague", encoding="utf-8")
    with pytest.raises(RuntimeError):
        safe_clear(foreign)
    assert (foreign / "dados.txt").exists()


def test_foreign_dest_gets_numbered_variant(project, tmp_path):
    dest = tmp_path / "out" / "proj"
    dest.mkdir(parents=True)
    (dest / "alheio.txt").write_text("preexistente", encoding="utf-8")
    cfg = ScanConfig(mode="collisions")
    res = execute_plan(make_plan(project, cfg), dest, cfg)
    assert res.dest.name == "proj (2)"      # não clobberou a original
    assert (dest / "alheio.txt").exists()   # original intacta


def test_gitignore_pruned_dirs_are_reported(tmp_path):
    """FIX-001: pasta inteira engolida pelo .gitignore agora deixa rastro.

    Reproduz o teste 2 do caso real (monorepo 'cinzeiro'): três subprojetos com
    pasta logs/ contendo arquivos de mesmo nome e um .gitignore com 'logs/'.
    Antes: poda silenciosa (sem contador, sem amostra, sem aviso) e os arquivos
    'sumiam'. Agora: contador + amostra + aviso de primeira classe.
    """
    root = tmp_path / "cinzeiro"
    root.mkdir()
    _tree(
        root,
        {
            ".gitignore": "logs/\n",
            "Cinzeiro-Story/logs/2026-06-11.md": "s",
            "Cinzeiro-Art/logs/2026-06-11.md": "a",
            "Cinzeiro-OST/logs/2026-06-11.md": "o",
            "Cinzeiro-Story/historia.md": "h",
        },
    )
    plan = make_plan(root, ScanConfig(mode="collisions"))
    targets = {f.rel.as_posix() for f in plan.files}
    assert "Cinzeiro-Story/historia.md" in targets
    assert not any("2026-06-11" in t for t in targets)      # podados de fato...
    assert plan.skipped["gitignore (pasta)"] == 3           # ...mas com rastro
    assert any(s.endswith("logs/") for s in plan.skipped_samples["gitignore (pasta)"])
    assert any("pasta(s) INTEIRA(s)" in w for w in plan.warnings)


def test_partial_prune_leaves_survivor_unsuffixed(tmp_path):
    """Documenta o teste 1 do usuário: duas pastas renomeadas para 'logs' são
    podadas pelo .gitignore; a sobrevivente fica SEM colisão e portanto mantém
    o nome original sem sufixo (não é sobrescrita — é filtragem na varredura).
    """
    root = tmp_path / "cinzeiro"
    root.mkdir()
    _tree(
        root,
        {
            ".gitignore": "logs/\n",
            "Cinzeiro-Story/logs-story/2026-06-11.md": "s",
            "Cinzeiro-Art/logs/2026-06-11.md": "a",
            "Cinzeiro-OST/logs/2026-06-11.md": "o",
        },
    )
    plan = make_plan(root, ScanConfig(mode="collisions"))
    by_rel = {f.rel.as_posix(): f for f in plan.files}
    logs_md = [r for r in by_rel if r.endswith("2026-06-11.md")]
    assert logs_md == ["Cinzeiro-Story/logs-story/2026-06-11.md"]
    assert by_rel["Cinzeiro-Story/logs-story/2026-06-11.md"].target == "2026-06-11.md"


def test_split_name_edges():
    assert split_name("page.tsx") == ("page", ".tsx")
    assert split_name(".gitignore") == (".gitignore", "")
    assert split_name(".eslintrc.json") == (".eslintrc", ".json")
    assert split_name("Makefile") == ("Makefile", "")
    assert split_name("types.d.ts") == ("types.d", ".ts")


# --------------------------------------------------------------------------- #
# Filtros desta execução (only_ext / exclude_ext / pasta) — Lote E
# --------------------------------------------------------------------------- #
@pytest.fixture()
def mono(tmp_path: Path) -> Path:
    """Mini-monorepo no estilo cinzeiro: .md em cada área + alguns não-.md."""
    root = tmp_path / "cinzeiro"
    root.mkdir()
    _tree(
        root,
        {
            "HUB.md": "h",
            "Story/meta/BIBLIA.md": "b",
            "Story/dev/cena.gd": "x",       # .gd não está na allowlist padrão
            "Story/dev/dados.json": "{}",   # .json está
            "Story/sprite.png": "PNG",      # binário: nunca entra
            "Art/meta/ESTILO.md": "e",
            "Game/dev/player.gd": "x",
        },
    )
    return root


def test_only_ext_restricts_hard(mono):
    # só .md: nada de .json, .gd, .png, nem o extensionless seria incluído
    plan = make_plan(mono, ScanConfig(mode="collisions", only_ext={"md"}))
    exts = {Path(f.rel.name).suffix for f in plan.files}
    assert exts == {".md"}
    assert any(f.rel.name == "BIBLIA.md" for f in plan.files)


def test_exclude_ext_subtracts(mono):
    # tudo permitido MENOS .md; .json continua, .md sai, .gd nunca esteve, .png fora
    plan = make_plan(mono, ScanConfig(mode="collisions", exclude_ext={"md"}))
    names = {f.rel.name for f in plan.files}
    assert "dados.json" in names
    assert not any(n.endswith(".md") for n in names)


def test_add_to_allowlist_brings_gd(mono):
    # acrescentar "gd" à allowlist faz os scripts de engine entrarem
    exts = set(ScanConfig().extensions) | {"gd"}
    plan = make_plan(mono, ScanConfig(mode="collisions", extensions=exts))
    names = {f.rel.name for f in plan.files}
    assert "cena.gd" in names and "player.gd" in names
    assert "sprite.png" not in names  # binário continua de fora


def test_folder_filter_starts(mono):
    # só pastas que começam com "dev" (com gd na allowlist p/ haver conteúdo)
    exts = set(ScanConfig().extensions) | {"gd"}
    cfg = ScanConfig(mode="collisions", extensions=exts,
                     only_folders=["dev"], folder_match="starts")
    plan = make_plan(mono, cfg)
    parents = {f.rel.parent.as_posix() for f in plan.files}
    assert parents == {"Story/dev", "Game/dev"}
    assert all("dev" in p for p in parents)


# --------------------------------------------------------------------------- #
# Multi-fonte com manifesto único — Lote E (o caso do --also-md-from)
# --------------------------------------------------------------------------- #
def test_multisource_area_pack_single_manifest(mono, tmp_path):
    """Pacote de área: não-.md da subpasta + TODOS os .md do repo, num plano só.

    Reproduz o que o --also-md-from monta: duas fontes, uma saída, um manifesto,
    sem sobreposição (os .md vêm só da fonte global; os não-.md só da área).
    """
    primary = ScanConfig(
        mode="collisions", exclude_ext={"md"},
        extensions=set(ScanConfig().extensions) | {"gd"}, use_gitignore=False,
    )
    md_cfg = ScanConfig(mode="collisions", only_ext={"md"}, use_gitignore=False)
    sources = [Source(mono / "Story", primary), Source(mono, md_cfg)]
    plan = make_plan_sources(sources)

    names = {f.rel.name for f in plan.files}
    # não-.md só da Story:
    assert {"cena.gd", "dados.json"} <= names
    assert "player.gd" not in names           # player.gd é de Game, não entra
    # todos os .md do repo (inclusive de outras áreas):
    assert {"HUB.md", "BIBLIA.md", "ESTILO.md"} <= names
    assert "sprite.png" not in names          # binário fora

    # raiz comum = cinzeiro; caminhos do manifesto relativos a ela
    assert plan.root == (mono).resolve()
    by_name = {f.rel.name: f.rel.as_posix() for f in plan.files}
    assert by_name["ESTILO.md"] == "Art/meta/ESTILO.md"
    assert by_name["cena.gd"] == "Story/dev/cena.gd"

    # um único manifesto, com as duas fontes descritas
    assert len(plan.sources) == 2
    res = execute_plan(plan, tmp_path / "out" / "Story-pack", primary)
    manifests = list(res.dest.glob("_MANIFEST*.md"))
    assert len(manifests) == 1
    body = manifests[0].read_text(encoding="utf-8")
    assert "Fontes (2)" in body and "Raiz comum" in body


def test_multisource_dedup_no_double_copy(tmp_path):
    """Se duas fontes aceitam o MESMO arquivo, ele entra uma vez só."""
    root = tmp_path / "p"
    _tree(root, {"a/README.md": "r", "a/b/nota.md": "n"})
    # duas fontes idênticas apontando para a mesma subpasta
    s = ScanConfig(mode="collisions", only_ext={"md"}, use_gitignore=False)
    plan = make_plan_sources([Source(root / "a", s), Source(root / "a", s)])
    rels = sorted(f.rel.as_posix() for f in plan.files)
    assert rels == ["README.md", "b/nota.md"]  # sem duplicatas


# --------------------------------------------------------------------------- #
# Resolução de Downloads (Lote A) — ramo XDG é testável no Linux
# --------------------------------------------------------------------------- #
def test_downloads_respects_xdg_env(tmp_path, monkeypatch):
    target = tmp_path / "Baixados"
    target.mkdir()
    monkeypatch.setattr("sys.platform", "linux")
    monkeypatch.setenv("XDG_DOWNLOAD_DIR", str(target))
    assert default_downloads_dir() == target


def test_downloads_fallback_to_home_when_no_downloads(tmp_path, monkeypatch):
    monkeypatch.setattr("sys.platform", "linux")
    monkeypatch.delenv("XDG_DOWNLOAD_DIR", raising=False)
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))
    # não há ~/Downloads nem user-dirs.dirs -> cai na home
    assert default_downloads_dir() == tmp_path


def test_flatdropignore_excludes_extra(tmp_path):
    """`.flatdropignore` exclui o que vai para o git mas nao para o Projeto."""
    root = tmp_path / "proj"
    root.mkdir()
    _tree(root, {
        ".flatdropignore": "notas-internas.md\n",
        "notas-internas.md": "x",
        "leiame.md": "y",
    })
    plan = make_plan(root, ScanConfig(mode="collisions"))
    targets = {f.rel.as_posix() for f in plan.files}
    assert "leiame.md" in targets
    assert "notas-internas.md" not in targets
    assert plan.skipped["flatdropignore"] >= 1


def test_flatdropignore_negation_reincludes_gitignored(tmp_path):
    """`!pasta/` no .flatdropignore libera o que o .gitignore bloqueia (ate pasta podada)."""
    root = tmp_path / "proj"
    root.mkdir()
    _tree(root, {
        ".gitignore": "logs/\n",
        ".flatdropignore": "!logs/\n",
        "logs/2026-06-11.md": "a",
        "leiame.md": "b",
    })
    plan = make_plan(root, ScanConfig(mode="collisions"))
    targets = {f.rel.as_posix() for f in plan.files}
    assert "logs/2026-06-11.md" in targets   # liberado de volta pelo !logs/
    assert "leiame.md" in targets


def test_nested_gitignore_scope(tmp_path):
    """`.gitignore` em subpasta vale so para aquela subarvore (aninhado)."""
    root = tmp_path / "proj"
    root.mkdir()
    _tree(root, {
        "Area/.gitignore": "rascunho.md\n",
        "Area/rascunho.md": "r",
        "Area/final.md": "f",
        "outro/rascunho.md": "x",
    })
    plan = make_plan(root, ScanConfig(mode="collisions"))
    targets = {f.rel.as_posix() for f in plan.files}
    assert "Area/final.md" in targets
    assert "Area/rascunho.md" not in targets   # gitignore aninhado pegou
    assert "outro/rascunho.md" in targets      # fora do escopo da subpasta -> mantido
    assert plan.skipped["gitignore"] >= 1
