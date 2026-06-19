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


def _run() -> None:
    argv = sys.argv[1:]
    if argv:
        # Modo terminal/.bat: roda direto, sem abrir janela.
        from flatdrop.cli import main as cli_main

        raise SystemExit(cli_main(argv))
    # Sem argumentos: experiência de duplo-clique -> interface gráfica.
    from flatdrop.gui import main as gui_main

    gui_main()


if __name__ == "__main__":
    _run()
