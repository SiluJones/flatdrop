---
name: apply-wo
description: Aplica uma WO de meta/workorders/ ao repo — localiza cada âncora exatamente, substitui, e para se não achar. Use quando o usuário pedir /apply-wo ou para aplicar uma WO nomeada.
disable-model-invocation: true
---
Leia o arquivo de WO indicado em `meta/workorders/` e execute-o.
Localize cada âncora EXATAMENTE; se não achar uma, PARE e reporte — não chute um lugar próximo.
Não toque em nada fora das edições nomeadas. Se a WO mexe em CÓDIGO, rode `python -m pytest -q` ao fim.
Ao terminar, rode `git diff` e confira a forma esperada antes de commitar (mensagem SEM acento, Conventional Commits).
RELATE: o que foi feito, achados e desvios do texto da WO, arquivos tocados, resultado da suíte e o commit.
Se a WO tocar `flatdrop/cli.py`, `gui._build_cli_args`, `gui._generate_bat` ou `gui._sources`, PARE e reporte como URGENTE antes de aplicar (invariante DEC-020).
Nota: as WOs com nome antigo (`spec0001`–`spec0037`) são WOs — o nome ficou, a pasta mudou.
WO: $ARGUMENTS
