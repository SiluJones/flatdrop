---
name: wrap
description: Encerra a tarefa — append em STATUS/DECISIONS, suíte, git diff e comando de commit. Use quando o usuário pedir /wrap ou para fechar a sessão de trabalho.
disable-model-invocation: true
---
Encerre a tarefa:
- Atualize `meta/STATUS.md` (append, não reescreva) com o que mudou.
- Acrescente `DEC-`/`FIX-` em `meta/DECISIONS.md` se houve decisão de arquitetura ou bug grave.
- Se mexeu em código, rode `python -m pytest -q` e cole o resultado. Se mexeu na GUI, diga o que precisa de smoke manual no Windows (a suíte não cobre tkinter).
- Me mostre o `git diff` e o comando de commit (uma linha por comando, mensagem SEM acento, Conventional Commits).
- Feche com o RELATÓRIO de trabalho: o que fez, achados e desvios do que a tarefa pedia, arquivos tocados, resultado da suíte e o commit. Não use o bloco de fecho de turno do `meta/CEREBRO.md` — aquele é da raia do chat.
