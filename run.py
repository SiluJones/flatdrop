#!/usr/bin/env python3
"""Ponto de entrada do FlatDrop.

Use assim (na raiz do repositório):

    python run.py

Este arquivo só existe para você poder dar dois cliques / rodar um comando só
sem se preocupar com PYTHONPATH. Ele garante que o pacote ``flatdrop`` (que
está nesta mesma pasta) seja importável e então chama a GUI.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Garante que a pasta deste arquivo esteja no caminho de importação, para que
# "import flatdrop" funcione mesmo se você rodar de outro diretório.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from flatdrop.gui import main  # noqa: E402  (import após ajustar o sys.path)

if __name__ == "__main__":
    main()
