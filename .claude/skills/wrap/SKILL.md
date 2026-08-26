---
name: wrap
description: Encerra a tarefa — append em STATUS/DECISIONS, suíte, git diff e comando de commit. Use quando o usuário pedir /wrap ou para fechar a sessão de trabalho.
disable-model-invocation: true
---
Encerre a tarefa:
- Atualize `meta/STATUS.md` (append, não reescreva) com o que mudou.
- Acrescente `DEC-`/`FIX-` em `meta/DECISIONS.md` se houve decisão de arquitetura ou bug grave.
- Se mexeu em código, rode `python -m pytest -q` e cole o resultado. Se mexeu na GUI, diga o que precisa de smoke manual no Windows (a suíte não cobre tkinter).
- ANTES de escrever qualquer coisa: abra o relatório mais recente em `../AAMMDD-HHMM-code-flatdrop.txt` e confira o que ele AFIRMA contra `git status` e `git log`. Relatório é escrito antes da última ação, então um push que saiu depois dele fica registrado como não feito — foi o que aconteceu com o da wo0051. Divergência vira uma linha de correção no log do dia; conferência que passa não vira linha.
- Confira o `git diff`: a forma esperada, nada além. Mensagem de commit SEM acento, Conventional Commits.
- Ao mudar um NÚMERO ou um ESTADO no `meta/STATUS.md` (contagem de testes, versão, commit, «funciona até X»), procure o valor ANTIGO no arquivo INTEIRO e atualize todas as ocorrências — o cabeçalho não é o único lugar onde ele aparece, e a cópia esquecida no meio do texto passa a mentir. Aconteceu aqui: o campo `Commit` ficou 20 dias apontando um hash que já não era o do repo.
- Escreva o log do dia em `logs/AAAA-MM-DD.md` (formato em `meta/LOG-TEMPLATE.md`). Se o arquivo do dia NÃO existe, CRIE — não regenerar é uma coisa, não criar é outra.
- **Verde:** `add` e `commit` sem perguntar. **Push:** peça confirmação — **DESVIO REGISTRADO** deste projeto em relação ao kit v1.104.0, que manda empurrar sem perguntar (motivo e revisão em DEC-032). **Resolva o push ANTES de escrever o relatório:** o relatório é o ÚLTIMO passo e diz o que de fato aconteceu — empurrado com o hash, ou não empurrado com o motivo. Se a confirmação chegar depois de o relatório existir, **reescreva o relatório**, não deixe a versão velha valendo.
- **Vermelho** (suíte falhou, âncora não encontrada, `git diff` com arquivo fora do previsto): não commite e não empurre. Feche com um MENU de saídas reais, a recomendada em primeiro lugar e marcada `(Recomendado)` — pela ferramenta `AskUserQuestion` se ela existir; sem ela, menu numerado em texto, **dizendo que caiu no fallback**. Nunca pergunte em prosa: pergunta escrita no meio do texto passa despercebida.
- Feche com o RELATÓRIO de trabalho: o que fez, achados e desvios do que a tarefa pedia, arquivos tocados, resultado da suíte e o commit. Não use o bloco de fecho de turno do `meta/CEREBRO.md` — aquele é da raia do chat.
- Grave o MESMO relatório em `../AAMMDD-HHMM-code-flatdrop.txt` (pasta-pai do repo). Se a escrita for negada, diga e siga.
