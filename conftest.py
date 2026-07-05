"""Configuração de teste do pytest — raiz do repositório.

Único propósito: garantir que a raiz do repo esteja no sys.path ANTES da coleta,
para que os testes possam fazer `from flatdrop import ...` com `pytest` puro, sem
depender de `python -m pytest`, de variável PYTHONPATH, nem de instalar o pacote.

O pytest importa o conftest.py da rootdir automaticamente antes de coletar os
testes; este insert espelha o ajuste que o run.py já faz para a aplicação (DEC-009:
a raiz cuida do PYTHONPATH; GUI/CLI/testes só amarram a core).
"""

import sys
from pathlib import Path

# Raiz do repo = pasta deste arquivo. Colocada à frente do sys.path para que
# `import flatdrop` resolva o pacote local, não um homônimo instalado.
sys.path.insert(0, str(Path(__file__).resolve().parent))
