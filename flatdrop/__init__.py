"""FlatDrop — achata uma pasta de projeto numa pasta plana para upload no Claude.

Pacote dividido em camadas:
- config: defaults (extensões, ignores, sensíveis, separador).
- core: lógica pura, sem UI — testável isoladamente.
- gui: interface tkinter que apenas amarra a core.
"""

__version__ = "0.9.2"
