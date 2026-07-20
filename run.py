#!/usr/bin/env python3
"""Ponto de entrada do FlatDrop.

Dois modos, decididos pela presença de argumentos:

    python run.py                 # SEM argumentos -> abre a GUI (duplo-clique)
    python run.py --root "C:\\proj" [opções]   # COM argumentos -> roda a CLI

Este arquivo só ajusta o PYTHONPATH (para "import flatdrop" funcionar de
qualquer diretório) e despacha para a interface certa. A lógica vive na core;
GUI e CLI apenas a amarram (DEC-009).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Garante que a pasta deste arquivo esteja no caminho de importação.
sys.path.insert(0, str(Path(__file__).resolve().parent))


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


if __name__ == "__main__":
    _run()
