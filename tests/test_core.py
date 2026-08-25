"""Testes da lógica central. Rode com: pytest -q  (a partir da raiz do repo)."""

import subprocess
from pathlib import Path, PurePath

import pytest

from flatdrop import config as C
from flatdrop import core
from flatdrop.core import (
    ScanConfig,
    Source,
    _plan_names,
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


# --------------------------------------------------------------------------- #
# root_in_name: inclui o nome da pasta-raiz no sufixo, só no fullpath (spec0013)
# --------------------------------------------------------------------------- #
def test_root_in_name_fullpath_includes_root_folder(project):
    root_name = project.name  # "proj"
    plan = make_plan(project, ScanConfig(mode="fullpath", root_in_name=True))
    by_rel = {f.rel.as_posix(): f for f in plan.files}
    # arquivo da própria raiz: a raiz vira a única "pasta" do sufixo
    assert by_rel["README.md"].target == f"README__{root_name}.md"
    # arquivo em subpasta (spec0014): pastas invertidas (interna -> externa) e a
    # raiz por ÚLTIMO — stem + "users__app__proj".
    page = by_rel["app/users/page.tsx"]
    assert page.target == f"page__users__app__{root_name}.tsx"
    # a raiz é sempre o último token do sufixo (trava contra regressão de ordem)
    assert page.target.rsplit(".", 1)[0].endswith(f"{C.DEFAULT_SEP}{root_name}")


def test_root_in_name_keeps_display_rel_real(project):
    root_name = project.name
    plan = make_plan(project, ScanConfig(mode="fullpath", root_in_name=True))
    # o rel de exibição (manifesto/_TREE.md) NÃO leva a raiz injetada
    for f in plan.files:
        assert not f.rel.as_posix().startswith(root_name + "/")
    by_rel = {f.rel.as_posix(): f for f in plan.files}
    assert by_rel["README.md"].rel.as_posix() == "README.md"


def test_root_in_name_ignored_outside_fullpath(project):
    plan_off = make_plan(project, ScanConfig(mode="collisions"))
    plan_on = make_plan(project, ScanConfig(mode="collisions", root_in_name=True))
    names_off = {f.rel.as_posix(): f.target for f in plan_off.files}
    names_on = {f.rel.as_posix(): f.target for f in plan_on.files}
    assert names_off == names_on
    assert any("fullpath" in w for w in plan_on.warnings)


def test_root_in_name_ignored_in_multisource(tmp_path):
    root = tmp_path / "p"
    _tree(root, {"a/one.md": "1", "b/one.md": "2"})
    cfg_on = ScanConfig(mode="fullpath", root_in_name=True, only_ext={"md"}, use_gitignore=False)
    cfg_off = ScanConfig(mode="fullpath", root_in_name=False, only_ext={"md"}, use_gitignore=False)
    plan_on = make_plan_sources([Source(root / "a", cfg_on), Source(root / "b", cfg_on)])
    plan_off = make_plan_sources([Source(root / "a", cfg_off), Source(root / "b", cfg_off)])
    names_on = sorted(f.target for f in plan_on.files)
    names_off = sorted(f.target for f in plan_off.files)
    assert names_on == names_off  # a raiz NÃO foi injetada
    assert any("múltiplas" in w for w in plan_on.warnings)


def test_root_in_name_preserves_uniqueness(tmp_path):
    root = tmp_path / "proj"
    _tree(root, {"a/one.py": "1", "b/one.py": "2"})
    plan = make_plan(root, ScanConfig(mode="fullpath", root_in_name=True))
    targets = [f.target.lower() for f in plan.files]
    assert len(targets) == len(set(targets))


def test_root_in_name_respects_max_name_len():
    # Vai direto em _plan_names com candidatos sintéticos (sem tocar disco), pois
    # o que importa aqui é só o NOME final ultrapassar MAX_NAME_LEN — criar de
    # verdade uma árvore tão funda esbarraria no limite de caminho do Windows.
    long_root = "raiz-" + "x" * 60
    deep_parts = "/".join(f"pasta-{i:02d}-bem-longa" for i in range(8))
    rel = PurePath(f"{deep_parts}/arquivo.txt")
    candidates = [(Path("fake") / rel, rel, 1)]
    planned, _collisions, _warnings = _plan_names(
        candidates, ScanConfig(mode="fullpath", root_in_name=True), root_prefix=long_root
    )
    assert len(planned[0].target) <= C.MAX_NAME_LEN


def test_execute_writes_manifest_and_marks_folder(project, tmp_path):
    dest = tmp_path / "out" / "proj"
    cfg = ScanConfig(mode="collisions")
    res = execute_plan(make_plan(project, cfg), dest, cfg)
    assert res.copied == len(make_plan(project, cfg).files)
    # default-ON (spec0036): o manifesto ganha o nome da pasta no fim.
    assert (res.dest / "_MANIFEST_proj.md").is_file()
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


# --------------------------------------------------------------------------- #
# _TREE.md (spec0011)
# --------------------------------------------------------------------------- #
def test_tree_off_by_default(project, tmp_path):
    dest = tmp_path / "out" / "proj"
    cfg = ScanConfig(mode="collisions")
    res = execute_plan(make_plan(project, cfg), dest, cfg)
    assert not (res.dest / C.TREE_NAME).exists()
    assert is_our_folder(res.dest) is True  # só o _MANIFEST.md marca propriedade


def test_tree_on_creates_file(project, tmp_path):
    dest = tmp_path / "out" / "proj"
    cfg = ScanConfig(mode="collisions", write_tree=True)
    res = execute_plan(make_plan(project, cfg), dest, cfg)
    # default-ON (spec0036): o _TREE tambem ganha o nome da pasta no fim.
    tree_path = res.dest / "_TREE_proj.md"
    assert tree_path.is_file()
    first_line = tree_path.read_text(encoding="utf-8").splitlines()[0]
    assert first_line == C.TREE_SIGNATURE


def test_tree_collapses_ignored_folder(project, tmp_path):
    dest = tmp_path / "out" / "proj"
    cfg = ScanConfig(mode="collisions", write_tree=True, name_meta_with_folder=False)
    res = execute_plan(make_plan(project, cfg), dest, cfg)
    body = (res.dest / C.TREE_NAME).read_text(encoding="utf-8")
    assert "node_modules/  [ignorada: embutido]" in body
    assert not any("node_modules/a" in line for line in body.splitlines())


def test_tree_shows_renamed(project, tmp_path):
    dest = tmp_path / "out" / "proj"
    cfg = ScanConfig(mode="collisions", write_tree=True, name_meta_with_folder=False)
    res = execute_plan(make_plan(project, cfg), dest, cfg)
    body = (res.dest / C.TREE_NAME).read_text(encoding="utf-8")
    assert "[renomeado:" in body


def test_tree_summary_vs_full(project, tmp_path):
    dest_summary = tmp_path / "out" / "proj-summary"
    cfg_summary = ScanConfig(mode="collisions", write_tree=True, tree_skipped="summary",
                             name_meta_with_folder=False)
    res_summary = execute_plan(make_plan(project, cfg_summary), dest_summary, cfg_summary)
    body_summary = (res_summary.dest / C.TREE_NAME).read_text(encoding="utf-8")
    assert "pulados:" in body_summary
    assert ".env  [pulado:" not in body_summary  # summary não abre folha individual

    dest_full = tmp_path / "out" / "proj-full"
    cfg_full = ScanConfig(mode="collisions", write_tree=True, tree_skipped="full",
                          name_meta_with_folder=False)
    res_full = execute_plan(make_plan(project, cfg_full), dest_full, cfg_full)
    body_full = (res_full.dest / C.TREE_NAME).read_text(encoding="utf-8")
    assert ".env  [pulado: sensivel]" in body_full


def test_tree_full_lists_all_skipped_beyond_sample_cap(tmp_path):
    """skipped_items nao tem o teto de 8 de skipped_samples; o tree full lista tudo."""
    root = tmp_path / "manyskips"
    root.mkdir()
    files = {f"img{i}.png": "x" for i in range(12)}  # tipo não aceito, 12 itens
    files["leiame.md"] = "ok"
    _tree(root, files)

    plan = make_plan(root, ScanConfig(mode="collisions"))
    assert len(plan.skipped_items) == 12          # sem teto
    assert len(plan.skipped_samples["tipo"]) == 8  # amostra continua limitada a 8

    dest = tmp_path / "out" / "manyskips"
    cfg = ScanConfig(mode="collisions", write_tree=True, tree_skipped="full",
                     name_meta_with_folder=False)
    res = execute_plan(make_plan(root, cfg), dest, cfg)
    body = (res.dest / C.TREE_NAME).read_text(encoding="utf-8")
    for i in range(12):
        assert f"img{i}.png  [pulado: tipo]" in body


# --------------------------------------------------------------------------- #
# Editor de .flatdropignore (spec0018)
# --------------------------------------------------------------------------- #
def _editor_repo(tmp_path):
    for p in ("logs/run.md", "logs/skip.md", "logs/deep/c.md",
              "docs/a.md", "docs/b.md", "docs/keep.md", "README.md", "src/app.py"):
        f = tmp_path / p
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("x", encoding="utf-8")
    (tmp_path / ".gitignore").write_text("logs/\n", encoding="utf-8")  # logs escondido; docs versionado
    return tmp_path


def _copied(root):
    plan = core.make_plan(str(root), core.ScanConfig(mode="collisions"))
    return sorted(f.rel.as_posix() for f in plan.files)  # posix p/ portabilidade Windows


@pytest.mark.skipif(not core.HAS_PATHSPEC, reason="requer pathspec")
def test_editor_liberate_only_one(tmp_path):
    # pasta escondida pelo .gitignore, trava ABERTA: !logs/* + exclusao dos outros por nome.
    root = _editor_repo(tmp_path)
    txt = core.build_flatdropignore(str(root), core.ScanConfig(mode="collisions"),
                                    {"logs/skip.md": False, "logs/deep/c.md": False},
                                    locks={"logs": False})
    assert "!logs/*" in txt
    (root / ".flatdropignore").write_text(txt, encoding="utf-8")
    got = _copied(root)
    assert "logs/run.md" in got                       # unico filho que segue marcado
    assert "logs/skip.md" not in got                  # excluido por nome
    assert "logs/deep/c.md" not in got                # excluido por nome
    assert "docs/a.md" in got                         # nao tocado -> segue incluido


@pytest.mark.skipif(not core.HAS_PATHSPEC, reason="requer pathspec")
def test_editor_exclude_keeps_sibling(tmp_path):
    # pasta ABERTA (default), um filho desmarcado: so a linha do arquivo, nada sobre a pasta.
    root = _editor_repo(tmp_path)
    txt = core.build_flatdropignore(str(root), core.ScanConfig(mode="collisions"),
                                    {"docs/b.md": False})
    block = txt.split(core.FLATDROP_EDITOR_MARK_A, 1)[1]
    assert "docs/b.md" in block
    assert "docs/*" not in block and "!docs/*" not in block
    assert "docs/a.md" not in block and "docs/keep.md" not in block
    (root / ".flatdropignore").write_text(txt, encoding="utf-8")
    got = _copied(root)
    assert "docs/keep.md" in got
    assert "docs/a.md" in got
    assert "docs/b.md" not in got


@pytest.mark.skipif(not core.HAS_PATHSPEC, reason="requer pathspec")
def test_editor_roundtrip_preserves_manual(tmp_path):
    root = _editor_repo(tmp_path)
    existing = ("# regra minha\n*.tmp\n\n"
                + core.FLATDROP_EDITOR_MARK_A + "\nlogs/x\n" + core.FLATDROP_EDITOR_MARK_B + "\n")
    txt = core.build_flatdropignore(str(root), core.ScanConfig(mode="collisions"),
                                    {"docs/a.md": False}, existing_text=existing, locks={})
    assert "# regra minha" in txt and "*.tmp" in txt          # linhas manuais preservadas
    assert txt.count(core.FLATDROP_EDITOR_MARK_A) == 1         # um unico bloco gerenciado
    assert "docs/a.md" in txt


@pytest.mark.skipif(not core.HAS_PATHSPEC, reason="requer pathspec")
def test_flatdropignore_reaches_mount(tmp_path):
    (tmp_path / "keep.md").write_text("x", encoding="utf-8")
    (tmp_path / ".flatdropignore").write_text("# controle\n", encoding="utf-8")
    plan = core.make_plan(str(tmp_path), core.ScanConfig(mode="collisions"))
    names = {f.rel.as_posix() for f in plan.files}
    assert ".flatdropignore" in names  # agora vai ao Projeto (spec0019)


@pytest.mark.skipif(not core.HAS_PATHSPEC, reason="requer pathspec")
def test_flatdropignore_alias_txt_applies(tmp_path):
    (tmp_path / "logs").mkdir()
    (tmp_path / "logs" / "l.md").write_text("x", encoding="utf-8")
    (tmp_path / "keep.md").write_text("x", encoding="utf-8")
    # sem .flatdropignore canonico; so o alias sem ponto
    (tmp_path / "flatdropignore.txt").write_text("logs/\n", encoding="utf-8")
    plan = core.make_plan(str(tmp_path), core.ScanConfig(mode="collisions"))
    names = {f.rel.as_posix() for f in plan.files}
    assert "logs/l.md" not in names           # o alias foi aplicado
    assert "keep.md" in names


@pytest.mark.skipif(not core.HAS_PATHSPEC, reason="requer pathspec")
def test_editor_lock_closed_writes_star(tmp_path):
    # trava FECHADA em logs/: "logs/*" e nenhuma linha por arquivo.
    for p in ("logs/a.md", "logs/b.md", "keep.md"):
        f = tmp_path / p
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("x", encoding="utf-8")
    (tmp_path / ".gitignore").write_text("", encoding="utf-8")
    cfg = core.ScanConfig(mode="collisions")
    txt = core.build_flatdropignore(str(tmp_path), cfg, {}, locks={"logs": True})
    assert "logs/*" in txt
    assert "logs/a.md" not in txt and "logs/b.md" not in txt
    (tmp_path / ".flatdropignore").write_text(txt, encoding="utf-8")
    (tmp_path / "logs" / "NOVO.md").write_text("x", encoding="utf-8")  # arquivo novo
    names = {f.rel.as_posix() for f in core.make_plan(str(tmp_path), cfg).files}
    assert "logs/NOVO.md" not in names  # bloqueado pela trava
    assert "logs/a.md" not in names and "logs/b.md" not in names
    assert "keep.md" in names


@pytest.mark.skipif(not core.HAS_PATHSPEC, reason="requer pathspec")
def test_editor_open_folder_all_unchecked_lists_each(tmp_path):
    # pasta ABERTA (default) com TODOS os filhos desmarcados: uma linha por arquivo,
    # nunca "logs/*" — e o adendo da DEC-027, quem fecha a pasta e a trava, nao o gesto.
    for p in ("logs/a.md", "logs/b.md", "keep.md"):
        f = tmp_path / p
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("x", encoding="utf-8")
    (tmp_path / ".gitignore").write_text("", encoding="utf-8")
    cfg = core.ScanConfig(mode="collisions")
    txt = core.build_flatdropignore(str(tmp_path), cfg,
                                    {"logs/a.md": False, "logs/b.md": False})
    assert "logs/a.md" in txt and "logs/b.md" in txt
    assert "logs/*" not in txt


@pytest.mark.skipif(not core.HAS_PATHSPEC, reason="requer pathspec")
def test_editor_roundtrip_preserves_folder_exclusion(tmp_path):
    for p in ("logs/a.md", "docs/a.md", "docs/keep.md"):
        f = tmp_path / p
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("x", encoding="utf-8")
    (tmp_path / ".gitignore").write_text("", encoding="utf-8")
    cfg = core.ScanConfig(mode="collisions")
    first = core.build_flatdropignore(str(tmp_path), cfg, {}, locks={"logs": True})
    assert "logs/*" in first
    (tmp_path / ".flatdropignore").write_text(first, encoding="utf-8")
    existing = (tmp_path / ".flatdropignore").read_text(encoding="utf-8")
    # segunda chamada SEM locks: a pasta fechada na primeira volta fechada na segunda
    # (o default vem do estado efetivo, nao de locks repetido)
    second = core.build_flatdropignore(str(tmp_path), cfg, {"docs/a.md": False}, existing_text=existing)
    assert "logs/*" in second
    (tmp_path / ".flatdropignore").write_text(second, encoding="utf-8")
    names = {f.rel.as_posix() for f in core.make_plan(str(tmp_path), cfg).files}
    assert "logs/a.md" not in names   # exclusao preservada no round-trip
    assert "docs/a.md" not in names   # nova exclusao aplicada
    assert "docs/keep.md" in names    # irmao preservado


@pytest.mark.skipif(not core.HAS_PATHSPEC, reason="requer pathspec")
def test_editor_nested_closed_emits_line_per_level(tmp_path):
    # pasta/ e pasta/sub/ fechadas, um arquivo resgatado em pasta/sub/: precisa da linha
    # de AMBOS os niveis, senao o irmao nao resgatado vaza (armadilha medida na DEC-027).
    for p in ("pasta/top.md", "pasta/sub/deep.md", "pasta/sub/outro.md"):
        f = tmp_path / p
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("x", encoding="utf-8")
    (tmp_path / ".gitignore").write_text("", encoding="utf-8")
    cfg = core.ScanConfig(mode="collisions")
    txt = core.build_flatdropignore(str(tmp_path), cfg, {"pasta/sub/deep.md": True},
                                    locks={"pasta": True, "pasta/sub": True})
    assert "pasta/*" in txt and "pasta/sub/*" in txt
    (tmp_path / ".flatdropignore").write_text(txt, encoding="utf-8")
    names = {f.rel.as_posix() for f in core.make_plan(str(tmp_path), cfg).files}
    assert "pasta/sub/deep.md" in names       # resgatado
    assert "pasta/sub/outro.md" not in names  # irmao fica de fora
    assert "pasta/top.md" not in names


@pytest.mark.skipif(not core.HAS_PATHSPEC, reason="requer pathspec")
def test_folder_effective_state(tmp_path):
    for p in ("meta/specs/s1.md", "meta/refs/r.md", "logs/a.md", "README.md"):
        f = tmp_path / p
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("x", encoding="utf-8")
    (tmp_path / ".gitignore").write_text("", encoding="utf-8")
    (tmp_path / ".flatdropignore").write_text(
        core.FLATDROP_EDITOR_MARK_A + "\nlogs/\nmeta/specs/\n" + core.FLATDROP_EDITOR_MARK_B + "\n",
        encoding="utf-8")
    cfg = core.ScanConfig(mode="collisions")
    st = lambda d: core.folder_effective_state(str(tmp_path), cfg, d)
    assert st("meta") is None       # misto -> indeterminado (o bug dos prints)
    assert st("meta/specs") is False
    assert st("meta/refs") is True
    assert st("logs") is False


def test_meta_name_suffix_on_off(tmp_path):
    from flatdrop import core, config as C
    from flatdrop.core import ScanConfig
    dest = tmp_path / "cancioneiro"
    on = ScanConfig(name_meta_with_folder=True)
    off = ScanConfig(name_meta_with_folder=False)
    assert core.meta_name(C.MANIFEST_NAME, dest, on) == "_MANIFEST_cancioneiro.md"
    assert core.meta_name(C.TREE_NAME, dest, on) == "_TREE_cancioneiro.md"
    assert core.meta_name(C.MANIFEST_NAME, dest, off) == "_MANIFEST.md"


def test_is_our_folder_recognizes_suffixed_manifest(tmp_path):
    from flatdrop import core, config as C
    dest = tmp_path / "proj"
    dest.mkdir()
    (dest / "_MANIFEST_proj.md").write_text(
        C.MANIFEST_SIGNATURE + "\n", encoding="utf-8")
    assert core.is_our_folder(dest) is True


# --------------------------------------------------------------------------- #
# FIX-011 / wo0038 — negacao resgata arquivo em pasta ignorada + _TREE nomeia
# --------------------------------------------------------------------------- #
def test_negacao_resgata_arquivo_em_pasta_ignorada(tmp_path):
    """`!meta/legacy/a.md` resgata o arquivo mesmo com `meta/legacy/` ignorada (FIX-011)."""
    root = tmp_path / "proj"
    root.mkdir()
    _tree(root, {
        "meta/legacy/a.md": "a",
        "meta/legacy/b.md": "b",
        ".flatdropignore": "meta/legacy/\n!meta/legacy/a.md\n",
    })
    plan = make_plan(root, ScanConfig(mode="collisions"))
    targets = {f.rel.as_posix() for f in plan.files}
    assert "meta/legacy/a.md" in targets
    assert "meta/legacy/b.md" not in targets
    folder_collapsed = [rel for rel, _reason in plan.skipped_items if rel.endswith("/")]
    assert "meta/legacy/" not in folder_collapsed


def test_pasta_ignorada_sem_negacao_continua_podada(tmp_path):
    """Sem `!` apontando para dentro, a pasta ignorada segue podada (guarda o FIX-001)."""
    root = tmp_path / "proj"
    root.mkdir()
    _tree(root, {
        "meta/legacy/a.md": "a",
        "meta/legacy/b.md": "b",
        ".flatdropignore": "meta/legacy/\n",
    })
    plan = make_plan(root, ScanConfig(mode="collisions"))
    targets = {f.rel.as_posix() for f in plan.files}
    assert "meta/legacy/a.md" not in targets
    assert "meta/legacy/b.md" not in targets
    rels = [rel for rel, _reason in plan.skipped_items]
    assert "meta/legacy/" in rels
    assert "meta/legacy/a.md" not in rels  # podada: nunca visitada folha a folha
    assert "meta/legacy/b.md" not in rels


def test_tree_nomeia_pulados_do_autor(tmp_path):
    """Arquivo pulado por ignore do autor sai NOMEADO no _TREE.md, nao so contado."""
    root = tmp_path / "proj"
    root.mkdir()
    _tree(root, {
        "docs/a.md": "a",
        "docs/b.md": "b",
        "docs/c.md": "c",
        ".flatdropignore": "docs/*\n",
    })
    dest = tmp_path / "out" / "proj"
    cfg = ScanConfig(mode="collisions", write_tree=True, name_meta_with_folder=False)
    res = execute_plan(make_plan(root, cfg), dest, cfg)
    body = (res.dest / C.TREE_NAME).read_text(encoding="utf-8")
    assert "[pulados por flatdropignore: a.md, b.md, c.md]" in body
    assert "[pulados: flatdropignore x3]" not in body


def test_tree_espia_pasta_ignorada(tmp_path):
    """Pasta ignorada pelo autor ganha uma espiada rasa nos filhos diretos."""
    root = tmp_path / "proj"
    root.mkdir()
    _tree(root, {
        "docs/a.md": "a",
        "docs/b.md": "b",
        ".flatdropignore": "docs/\n",
    })
    dest = tmp_path / "out" / "proj"
    cfg = ScanConfig(mode="collisions", write_tree=True, name_meta_with_folder=False)
    res = execute_plan(make_plan(root, cfg), dest, cfg)
    body = (res.dest / C.TREE_NAME).read_text(encoding="utf-8")
    lines = body.splitlines()
    idx = next(i for i, ln in enumerate(lines) if "docs/  [ignorada: flatdropignore]" in ln)
    assert "a.md" in lines[idx + 1]
    assert "b.md" in lines[idx + 2]


def test_peek_respeita_teto(tmp_path):
    """A espiada rasa amostra as duas pontas (wo0043) em vez de um teto simples."""
    root = tmp_path / "proj"
    root.mkdir()
    files = {f"docs/d{i:02d}.md": "x" for i in range(C.TREE_NAME_HEAD + C.TREE_NAME_TAIL + 5)}
    files[".flatdropignore"] = "docs/\n"
    _tree(root, files)
    dest = tmp_path / "out" / "proj"
    cfg = ScanConfig(mode="collisions", write_tree=True, name_meta_with_folder=False)
    res = execute_plan(make_plan(root, cfg), dest, cfg)
    body = (res.dest / C.TREE_NAME).read_text(encoding="utf-8")
    lines = body.splitlines()
    idx = next(i for i, ln in enumerate(lines) if "docs/  [ignorada: flatdropignore]" in ln)
    peek_lines = []
    for ln in lines[idx + 1:]:
        if not ln.strip():
            break
        peek_lines.append(ln)
    assert any("no meio" in ln and "no total" in ln for ln in peek_lines)
    named = [ln for ln in peek_lines if "no total" not in ln]
    assert len(named) == C.TREE_NAME_HEAD + C.TREE_NAME_TAIL


def test_tree_amostra_curta_devolve_tudo():
    """Lista com HEAD + TAIL nomes sai inteira, sem a linha do meio."""
    nomes = [f"n{i:02d}" for i in range(C.TREE_NAME_HEAD + C.TREE_NAME_TAIL)]
    assert core._tree_amostra(nomes) == nomes


def test_tree_amostra_longa_mostra_as_duas_pontas():
    """39 nomes ordenados: primeiro e ultimo aparecem, o total aparece, e sobram HEAD+TAIL nomes."""
    nomes = [f"n{i:02d}" for i in range(39)]
    amostra = core._tree_amostra(nomes)
    assert amostra[0] == nomes[0]
    assert amostra[-1] == nomes[-1]
    meio = [ln for ln in amostra if "no total" in ln]
    assert len(meio) == 1
    assert "39 no total" in meio[0]
    nomeados = [x for x in amostra if x not in meio]
    assert len(nomeados) == C.TREE_NAME_HEAD + C.TREE_NAME_TAIL


def test_tree_pasta_grande_mostra_faixa(tmp_path):
    """Ponta a ponta: pasta com 39 arquivos ignorada mostra o primeiro, o ultimo e o total."""
    root = tmp_path / "proj"
    root.mkdir()
    files = {f"pasta/f{i:02d}.md": "x" for i in range(39)}
    files[".flatdropignore"] = "pasta/*\n"
    _tree(root, files)
    dest = tmp_path / "out" / "proj"
    cfg = ScanConfig(mode="collisions", write_tree=True, name_meta_with_folder=False)
    res = execute_plan(make_plan(root, cfg), dest, cfg)
    body = (res.dest / C.TREE_NAME).read_text(encoding="utf-8")
    assert "f00.md" in body
    assert "f38.md" in body
    assert "no total" in body


@pytest.mark.skipif(not core.HAS_PATHSPEC, reason="requer pathspec")
def test_folder_is_closed_le_o_estado_atual(tmp_path):
    """A sonda da trava (wo0042) le o estado ATUAL dos ignores, nao um cache proprio."""
    for p in ("pasta/x.md", "outra/y.md"):
        f = tmp_path / p
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("x", encoding="utf-8")
    (tmp_path / ".gitignore").write_text("escondida/\n", encoding="utf-8")
    (tmp_path / "escondida").mkdir()
    (tmp_path / "escondida" / "z.md").write_text("x", encoding="utf-8")
    cfg = core.ScanConfig(mode="collisions")
    closed = lambda d: core.folder_is_closed(str(tmp_path), cfg, d)

    assert closed("outra") is False  # pasta comum: arquivo novo entra

    (tmp_path / ".flatdropignore").write_text("pasta/*\n", encoding="utf-8")
    assert closed("pasta") is True  # travada: arquivo novo nao entra

    (tmp_path / ".flatdropignore").write_text("pasta/*\n!pasta/x.md\n", encoding="utf-8")
    assert closed("pasta") is True  # resgate de UM arquivo nao abre a pasta (DEC-027)

    assert closed("escondida") is True  # escondida pelo .gitignore: tambem travada


def test_marcador_citado_em_comentario_nao_corta_o_bloco(tmp_path):
    """Marcador mencionado num comentario nao pode ser confundido com o bloco (wo0045)."""
    (tmp_path / "logs").mkdir()
    (tmp_path / "logs" / "a.md").write_text("x\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("x\n", encoding="utf-8")
    texto = (
        '# Regra vai DENTRO do bloco "# >>> flatdrop-editor" e nada depois do "# <<<".\n'
        "logs/*\n"
        "# >>> flatdrop-editor\n"
        "# (sem alteracoes)\n"
        "# <<<\n"
    )
    (tmp_path / ".flatdropignore").write_text(texto, encoding="utf-8")
    out = core.build_flatdropignore(tmp_path, core.ScanConfig(), {}, existing_text=texto)
    assert out.count(core.FLATDROP_EDITOR_MARK_A) == 2   # o do comentario + o bloco real
    assert out.splitlines()[0] == texto.splitlines()[0]  # comentario intacto, nao cortado
    assert out.splitlines()[1] == "logs/*"


def test_dois_blocos_recusa_salvar(tmp_path):
    """Arquivo ambiguo para o salvamento em vez de adivinhar qual bloco vale (wo0045)."""
    (tmp_path / "README.md").write_text("x\n", encoding="utf-8")
    texto = ("# >>> flatdrop-editor\n# (sem alteracoes)\n# <<<\n"
             "# >>> flatdrop-editor\n# (sem alteracoes)\n# <<<\n")
    (tmp_path / ".flatdropignore").write_text(texto, encoding="utf-8")
    with pytest.raises(core.FlatdropIgnoreAmbiguo):
        core.build_flatdropignore(tmp_path, core.ScanConfig(), {}, existing_text=texto)


def test_salvar_duas_vezes_nao_acumula_linha_em_branco(tmp_path):
    """Estabilidade TEXTUAL, nao so das regras: o lstrip antigo deixava o arquivo crescer."""
    (tmp_path / "logs").mkdir()
    (tmp_path / "logs" / "a.md").write_text("x\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("x\n", encoding="utf-8")
    texto = "# cabecalho\nlogs/*\n# >>> flatdrop-editor\n# (sem alteracoes)\n# <<<\n"
    (tmp_path / ".flatdropignore").write_text(texto, encoding="utf-8")
    cfg = core.ScanConfig()
    t1 = core.build_flatdropignore(tmp_path, cfg, {}, existing_text=texto)
    (tmp_path / ".flatdropignore").write_text(t1, encoding="utf-8")
    t2 = core.build_flatdropignore(tmp_path, cfg, {}, existing_text=t1)
    assert t1 == t2


def _repo_com_curadoria_manual(tmp_path):
    """Arvore minima com regra manual FORA do bloco — o caso que o gerador nao enxergava."""
    (tmp_path / "logs").mkdir()
    (tmp_path / "meta").mkdir()
    for rel in ("logs/a.md", "logs/b.md", "meta/x.md", "INSTRUCOES.md", "run.py"):
        (tmp_path / rel).write_text("x\n", encoding="utf-8")
    (tmp_path / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
    texto = ("# comentario do autor\n"
             "logs/*\nmeta/*\nINSTRUCOES.md\n"
             "# >>> flatdrop-editor\n# (sem alteracoes)\n# <<<\n")
    (tmp_path / ".flatdropignore").write_text(texto, encoding="utf-8")
    return texto


def _bloco(texto):
    _pre, bloco, _pos = core._split_managed(texto)
    return [ln for ln in bloco.splitlines()[1:-1]]


def test_bloco_nao_duplica_curadoria_manual(tmp_path):
    """Salvar sem mexer em nada nao copia para dentro o que ja esta fora (wo0046)."""
    texto = _repo_com_curadoria_manual(tmp_path)
    out = core.build_flatdropignore(tmp_path, core.ScanConfig(), {}, existing_text=texto)
    assert _bloco(out) == ["# (sem alteracoes)"]


def test_destravar_vence_linha_manual(tmp_path):
    """Destravar pasta fechada a mao emite o "!" que a vence — antes era desfeito calado."""
    texto = _repo_com_curadoria_manual(tmp_path)
    out = core.build_flatdropignore(tmp_path, core.ScanConfig(), {},
                                    existing_text=texto, locks={"logs": False})
    assert _bloco(out) == ["!logs/*"]


def test_marcar_arquivo_em_pasta_fechada_a_mao(tmp_path):
    """So o resgate do arquivo marcado, sem as duplicatas da pasta (wo0046)."""
    texto = _repo_com_curadoria_manual(tmp_path)
    out = core.build_flatdropignore(tmp_path, core.ScanConfig(), {"logs/a.md": True},
                                    existing_text=texto, locks={"logs": True})
    assert _bloco(out) == ["!logs/a.md"]


def test_bloco_vai_para_o_fim_e_avisa(tmp_path):
    """Regra depois do bloco: o bloco sobe para o fim e rules_after_block a denuncia."""
    (tmp_path / "logs").mkdir()
    (tmp_path / "logs" / "a.md").write_text("x\n", encoding="utf-8")
    (tmp_path / "run.py").write_text("x\n", encoding="utf-8")
    texto = "# >>> flatdrop-editor\n!logs/*\n# <<<\nlogs/*\n"
    (tmp_path / ".flatdropignore").write_text(texto, encoding="utf-8")
    assert core.rules_after_block(texto) == ["logs/*"]
    out = core.build_flatdropignore(tmp_path, core.ScanConfig(), {}, existing_text=texto)
    linhas = [ln for ln in out.splitlines() if ln.strip()]
    assert linhas[-1] == core.FLATDROP_EDITOR_MARK_B      # o bloco e o ultimo conteudo
    assert linhas[0] == "logs/*"                          # a regra do autor subiu, intacta


def test_backslash_patterns_denuncia_linha_manual(tmp_path):
    """Padrao com contrabarra nao casa nada e precisa ser apontado (wo0047)."""
    (tmp_path / "static").mkdir()
    (tmp_path / "static" / "a.json").write_text("x\n", encoding="utf-8")
    (tmp_path / ".flatdropignore").write_text(
        "# comentario com \\ nao conta\n"
        "static/*\n"
        "!static\\a.json\n",
        encoding="utf-8")
    achados = core.backslash_patterns(tmp_path, core.ScanConfig())
    assert achados == [(".flatdropignore", "!static\\a.json")]


def test_backslash_patterns_vazio_quando_tudo_certo(tmp_path):
    """Arquivo bem escrito nao gera aviso — o aviso so aparece quando ha o que consertar."""
    (tmp_path / "static").mkdir()
    (tmp_path / "static" / "a.json").write_text("x\n", encoding="utf-8")
    (tmp_path / ".flatdropignore").write_text("static/*\n!static/a.json\n", encoding="utf-8")
    assert core.backslash_patterns(tmp_path, core.ScanConfig()) == []


def _git_disponivel():
    try:
        return subprocess.run(["git", "--version"], capture_output=True, timeout=5).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def test_git_snapshot_sem_repositorio(tmp_path):
    """Pasta que nao e repo nao ganha as linhas — e nao quebra nada (wo0048)."""
    assert core.git_snapshot(tmp_path) == (None, None)


@pytest.mark.skipif(not _git_disponivel(), reason="git nao instalado no ambiente")
def test_git_snapshot_repo_limpo(tmp_path):
    """Repo sem alteracao pendente sai como 'limpo', e o commit traz hash, data e assunto."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True)
    (tmp_path / "a.md").write_text("x\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "primeiro"], cwd=tmp_path, check=True)
    commit, status = core.git_snapshot(tmp_path)
    assert commit and commit.endswith("primeiro")
    assert len(commit.split()) >= 3          # hash + data + assunto
    assert status and "limpo" in status


@pytest.mark.skipif(not _git_disponivel(), reason="git nao instalado no ambiente")
def test_git_snapshot_conta_sem_listar(tmp_path):
    """O status e RESUMO: conta, e nao expoe nome de arquivo nao rastreado."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True)
    (tmp_path / "a.md").write_text("x\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "primeiro"], cwd=tmp_path, check=True)
    (tmp_path / "a.md").write_text("y\n", encoding="utf-8")
    (tmp_path / "segredo-pessoal.txt").write_text("z\n", encoding="utf-8")
    _commit, status = core.git_snapshot(tmp_path)
    assert "1 modificado(s)" in status and "1 nao rastreado(s)" in status
    assert "segredo-pessoal" not in status


@pytest.mark.skipif(not _git_disponivel(), reason="git nao instalado no ambiente")
def test_manifesto_traz_as_duas_linhas(tmp_path):
    """As linhas aparecem no manifesto, rotuladas como foto (wo0048).

    Desvio da WO (registrado no relatorio de aplicacao): a assinatura de make_plan/execute_plan
    na WO era (origem, dest, cfg) / (plan, cfg) — a real, conferida nos testes existentes
    (ex.: test_execute_writes_manifest_and_marks_folder), e make_plan(root, cfg) /
    execute_plan(plan, dest, cfg), e o manifesto pode sair com sufixo (_MANIFEST_<pasta>.md),
    por isso o glob em vez do nome fixo.
    """
    origem = tmp_path / "src"
    origem.mkdir()
    (origem / "a.md").write_text("x\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=origem, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=origem, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=origem, check=True)
    subprocess.run(["git", "add", "."], cwd=origem, check=True)
    subprocess.run(["git", "commit", "-qm", "primeiro"], cwd=origem, check=True)
    dest = tmp_path / "out"
    cfg = core.ScanConfig()
    plan = core.make_plan(origem, cfg)
    res = core.execute_plan(plan, dest, cfg)
    manifests = list(res.dest.glob("_MANIFEST*.md"))
    assert len(manifests) == 1
    texto = manifests[0].read_text(encoding="utf-8")
    assert "Git (foto da geração) — último commit:" in texto
    assert "Git (foto da geração) — status:" in texto


# --- sincronia com o remoto (wo0050) — puros, rodam sem git instalado ---

def test_divergencia_sem_upstream():
    """Branch sem upstream nao pode ler como repo em dia — e o pior caso dos tres."""
    assert core._divergence("## main") == " · sem upstream"


def test_divergencia_sincronizado():
    """Com upstream e sem divergencia, a linha DIZ que esta sincronizado, em vez de calar."""
    assert core._divergence("## main...origin/main") == " · sincronizado com origin/main"


def test_divergencia_ahead():
    """O caso que a wo0048 ja resolvia — fica coberto para nao regredir."""
    assert core._divergence("## main...origin/main [ahead 1]") == \
        " · 1 commit(s) a frente de origin/main"


def test_divergencia_behind():
    assert core._divergence("## main...origin/main [behind 3]") == \
        " · 3 commit(s) atras de origin/main"


def test_divergencia_ahead_e_behind():
    """O defeito da wo0048: o `.split(",")[0]` jogava o behind fora."""
    s = core._divergence("## main...origin/main [ahead 1, behind 2]")
    assert "1 a frente" in s and "2 atras" in s


def test_divergencia_head_solto():
    assert "HEAD solto" in core._divergence("## HEAD (no branch)")


def test_divergencia_linha_estranha_nao_inventa():
    """Diante de linha irreconhecivel, silencio — nunca um estado inventado."""
    assert core._divergence("##") == ""


@pytest.mark.skipif(not _git_disponivel(), reason="git nao instalado no ambiente")
def test_git_snapshot_sem_upstream_no_status(tmp_path):
    """Ponta a ponta: repo local sem remoto sai como 'limpo' E 'sem upstream'."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True)
    (tmp_path / "a.md").write_text("x\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "primeiro"], cwd=tmp_path, check=True)
    _commit, status = core.git_snapshot(tmp_path)
    assert "limpo" in status and "sem upstream" in status


# --- nome previsto no Projeto (wo0051, DEC-030) — puros ---

def test_previsao_dotfile():
    """Ponto inicial vira `_` — o caso dos tres dotfiles de configuracao."""
    assert core.project_upload_name(".gitignore") == "_gitignore"
    assert core.project_upload_name(".flatdropignore") == "_flatdropignore"
    assert core.project_upload_name(".gitattributes") == "_gitattributes"


def test_previsao_ponto_interno():
    """Ponto interno vira `_`; a ultima extensao sobrevive."""
    assert core.project_upload_name("settings.local.json") == "settings_local.json"
    assert core.project_upload_name("index.template.html") == "index_template.html"


def test_previsao_varios_pontos():
    """Todos os pontos internos caem, nao so o primeiro."""
    assert core.project_upload_name("map.2.0-avowed.json") == "map_2_0-avowed.json"


def test_previsao_nome_comum_nao_muda():
    """A esmagadora maioria nao diverge — e nao pode entrar no bloco de excecoes."""
    for nome in ("core.py", "README.md", "Dockerfile", "README__meta.md"):
        assert core.project_upload_name(nome) == nome


def test_previsao_nao_opina_alem_do_ponto():
    """Espaco e outros caracteres passam intactos: nunca foram medidos (DEC-030)."""
    assert core.project_upload_name("meu arquivo.md") == "meu arquivo.md"


def test_manifesto_traz_bloco_de_excecoes(tmp_path):
    """Nome com ponto interno gera o bloco, com o rotulo de PREVISAO."""
    origem = tmp_path / "src"
    origem.mkdir()
    (origem / "dados.v1.json").write_text("{}\n", encoding="utf-8")
    (origem / "a.md").write_text("x\n", encoding="utf-8")
    cfg = core.ScanConfig()
    plan = core.make_plan(origem, cfg)
    res = core.execute_plan(plan, tmp_path / "out", cfg)
    texto = list(res.dest.glob("_MANIFEST*.md"))[0].read_text(encoding="utf-8")
    assert "Nomes que chegam DIFERENTES ao Projeto (1)" in texto
    assert "`dados_v1.json`" in texto
    assert "PREVISÃO" in texto


def test_manifesto_sem_divergencia_nao_tem_bloco(tmp_path):
    """Sem caso, sem bloco — secao vazia e ruido em todo manifesto."""
    origem = tmp_path / "src"
    origem.mkdir()
    (origem / "a.md").write_text("x\n", encoding="utf-8")
    cfg = core.ScanConfig()
    plan = core.make_plan(origem, cfg)
    res = core.execute_plan(plan, tmp_path / "out", cfg)
    texto = list(res.dest.glob("_MANIFEST*.md"))[0].read_text(encoding="utf-8")
    assert "chegam DIFERENTES" not in texto


def test_manifesto_tabela_original_intacta(tmp_path):
    """A tabela continua declarando o nome EM DISCO — a excecao nao a reescreve."""
    origem = tmp_path / "src"
    origem.mkdir()
    (origem / "dados.v1.json").write_text("{}\n", encoding="utf-8")
    cfg = core.ScanConfig()
    plan = core.make_plan(origem, cfg)
    res = core.execute_plan(plan, tmp_path / "out", cfg)
    texto = list(res.dest.glob("_MANIFEST*.md"))[0].read_text(encoding="utf-8")
    assert "| `dados.v1.json` | `dados.v1.json` |" in texto
    assert (res.dest / "dados.v1.json").is_file()


def test_assinatura_continua_na_primeira_linha(tmp_path):
    """Invariante do DEC-007: e ela que autoriza o safe_clear. Nada pode empurra-la."""
    origem = tmp_path / "src"
    origem.mkdir()
    (origem / "dados.v1.json").write_text("{}\n", encoding="utf-8")
    cfg = core.ScanConfig()
    plan = core.make_plan(origem, cfg)
    res = core.execute_plan(plan, tmp_path / "out", cfg)
    texto = list(res.dest.glob("_MANIFEST*.md"))[0].read_text(encoding="utf-8")
    assert texto.splitlines()[0] == C.MANIFEST_SIGNATURE
    assert core.is_our_folder(res.dest)
