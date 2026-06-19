"""Interface de linha de comando do FlatDrop.

A CLI reaproveita a MESMA core da GUI (DEC-009): aqui não há regra de negócio,
só tradução de argumentos -> ScanConfig/Source -> core. O entrypoint run.py
chama esta `main` quando recebe argumentos; sem argumentos, abre a GUI.

Exemplos:
    # Achatar um projeto inteiro (equivalente à GUI no modo padrão):
    python run.py --root "C:\\proj"

    # Só os .md a partir da raiz do repositório (ignorando .gitignore):
    python run.py --root "C:\\repo" --only-ext md --no-gitignore --name repo-md

    # Pacote de uma área: tudo MENOS .md da subpasta + TODOS os .md do repo,
    # num único manifesto (o multi-fonte que o --also-md-from monta):
    python run.py --root "C:\\repo\\Area" --exclude-ext md \\
                  --also-md-from "C:\\repo" --name Area-pack --no-gitignore
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from pathlib import Path

from . import config as C
from . import core


def _ext_set(raw: str) -> set[str]:
    """Converte 'md, py .json' -> {'md','py','json'} (tolerante a vírgula/espaço/ponto)."""
    return {
        e.strip().lstrip(".").lower()
        for e in raw.replace("\n", ",").replace(" ", ",").split(",")
        if e.strip()
    }


def _term_list(raw: str) -> list[str]:
    """Converte uma lista separada por vírgula em termos (preserva ordem, sem vazios)."""
    return [t.strip() for t in raw.split(",") if t.strip()]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="flatdrop",
        description="Achata uma pasta de projeto numa pasta plana para upload no "
        "Projeto do Claude, resolvendo colisões de nome.",
    )
    p.add_argument("root", nargs="?", help="pasta raiz do projeto (ou use --root)")
    p.add_argument("--root", dest="root_flag", metavar="PATH", help="alternativa ao argumento posicional")
    p.add_argument("--dest", metavar="PATH", help="pasta de destino (padrão: Downloads)")
    p.add_argument("--name", metavar="NOME", help="nome da pasta de saída (padrão: nome da raiz)")
    p.add_argument(
        "--mode", choices=("collisions", "all", "fullpath"), default="collisions",
        help="modo de renomeação (padrão: collisions)",
    )
    p.add_argument("--sep", default=C.DEFAULT_SEP, help=f"separador de sufixo (padrão: {C.DEFAULT_SEP})")
    p.add_argument("--only-ext", metavar="LISTA", help="só estas extensões (ex.: md ou md,txt)")
    p.add_argument("--exclude-ext", metavar="LISTA", help="exceto estas extensões (ex.: md)")
    p.add_argument(
        "--add-ext", metavar="LISTA",
        help="ACRESCENTA extensões à allowlist padrão (ex.: gd,tscn,tres p/ Godot). "
        "Diferente de --only-ext: soma em vez de restringir.",
    )
    p.add_argument("--only-folder", metavar="LISTA", help="só pastas que casam estes termos")
    p.add_argument(
        "--folder-match", choices=("starts", "contains", "exact"), default="starts",
        help="como casar os termos de --only-folder (padrão: starts)",
    )
    p.add_argument("--no-gitignore", action="store_false", dest="use_gitignore", help="não ler o .gitignore da raiz")
    p.add_argument("--include-sensitive", action="store_true", help="incluir arquivos sensíveis (.env, chaves)")
    p.add_argument("--no-manifest", action="store_false", dest="write_manifest", help="não gerar _MANIFEST.md")
    p.add_argument("--no-clear", action="store_false", dest="clear_dest", help="não limpar a pasta de destino antes")
    p.add_argument(
        "--also-md-from", metavar="PATH", action="append", default=[],
        help="adiciona uma fonte 'todos os .md a partir de PATH' à MESMA saída "
        "(pode repetir). Herda --mode/--sep/--no-gitignore; usa só .md.",
    )
    p.add_argument("--preview", action="store_true", help="só pré-visualizar (não escreve nada)")
    return p


def _primary_cfg(args: argparse.Namespace) -> core.ScanConfig:
    """Monta o ScanConfig da fonte primária a partir dos argumentos."""
    # --add-ext soma à allowlist padrão (não tem efeito quando --only-ext está
    # ativo, pois aquele é um corte duro que ignora a allowlist ampla).
    extensions = set(C.DEFAULT_EXTENSIONS)
    if args.add_ext:
        extensions |= _ext_set(args.add_ext)
    return core.ScanConfig(
        mode=args.mode,
        sep=args.sep or C.DEFAULT_SEP,
        use_gitignore=args.use_gitignore,
        include_sensitive=args.include_sensitive,
        write_manifest=args.write_manifest,
        clear_dest=args.clear_dest,
        extensions=extensions,
        only_ext=_ext_set(args.only_ext) if args.only_ext else None,
        exclude_ext=_ext_set(args.exclude_ext) if args.exclude_ext else set(),
        only_folders=_term_list(args.only_folder) if args.only_folder else [],
        folder_match=args.folder_match,
    )


def _summary(plan: core.FlattenPlan) -> str:
    """Resumo textual do plano (mesma informação da pré-visualização da GUI)."""
    lines = [
        f"Raiz comum: {plan.root}",
        f"Arquivos a copiar: {len(plan.files)}  |  nomes repetidos: {plan.collisions}  |  "
        f"total: {core.human_size(plan.total_bytes)}  (~{plan.est_tokens:,} tokens, estimativa)",
    ]
    if len(plan.sources) > 1:
        lines.append(f"Fontes ({len(plan.sources)}):")
        lines += [f"  • {d}" for d in plan.sources]
    skipped_txt = ", ".join(f"{k}={v}" for k, v in plan.skipped.items() if v)
    lines.append(f"Pulados: {skipped_txt or 'nenhum'}")
    for reason, sample in plan.skipped_samples.items():
        if not sample:
            continue
        total = plan.skipped.get(reason, 0)
        shown = sample[:5]
        extra = f" … (+{total - len(shown)})" if total > len(shown) else ""
        lines.append(f"  ↳ {reason}: " + ", ".join(shown) + extra)
    if plan.warnings:
        lines.append("")
        lines.append("AVISOS:")
        lines += [f"  ⚠ {w}" for w in plan.warnings]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada da CLI. Devolve código de saída (0 = ok)."""
    args = build_parser().parse_args(argv)

    root = args.root_flag or args.root
    if not root:
        print("Erro: informe a pasta raiz (posicional ou --root).", file=sys.stderr)
        return 2
    root_path = Path(root).expanduser()
    if not root_path.is_dir():
        print(f"Erro: pasta raiz não encontrada: {root_path}", file=sys.stderr)
        return 2

    primary = _primary_cfg(args)
    sources = [core.Source(root_path, primary)]

    # Cada --also-md-from vira uma fonte 'só .md' a partir daquele caminho,
    # herdando os parâmetros globais (mode/sep/gitignore) mas sem os filtros da
    # primária (exclude_ext/only_folder não se aplicam à coleta de .md).
    for md_root in args.also_md_from:
        mp = Path(md_root).expanduser()
        if not mp.is_dir():
            print(f"Erro: --also-md-from não encontrado: {mp}", file=sys.stderr)
            return 2
        md_cfg = replace(primary, only_ext={"md"}, exclude_ext=set(), only_folders=[])
        sources.append(core.Source(mp, md_cfg))

    try:
        plan = core.make_plan_sources(sources)
    except (NotADirectoryError, ValueError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1

    if args.preview:
        print("PRÉ-VISUALIZAÇÃO (nada foi escrito)")
        print("=" * 60)
        print(_summary(plan))
        return 0

    name = (args.name or root_path.name or "flatdrop_out").strip()
    dest_base = Path(args.dest).expanduser() if args.dest else core.default_downloads_dir()
    dest = dest_base / name

    res = core.execute_plan(plan, dest, primary)
    print("CONCLUÍDO")
    print("=" * 60)
    print(_summary(plan))
    print("")
    print(f"Copiados: {res.copied} arquivo(s)")
    print(f"Destino:  {res.dest}")
    print(f"Limpou antes: {'sim' if res.cleared else 'não'}")
    if res.manifest_path:
        print(f"Manifesto: {res.manifest_path.name}")
    if res.warnings:
        print("AVISOS de execução:")
        for w in res.warnings:
            print(f"  ⚠ {w}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
