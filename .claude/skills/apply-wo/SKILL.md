---
name: apply-wo
description: Aplica uma WO de meta/workorders/ ao repo — localiza cada âncora exatamente, substitui, e para se não achar. Use quando o usuário pedir /apply-wo ou para aplicar uma WO nomeada.
disable-model-invocation: true
---
Leia o arquivo de WO indicado em `meta/workorders/` e execute-o.

**Antes de tocar em qualquer arquivo:**
- Confira o campo **«Âncoras lidas em»** do cabeçalho. Se vier vazio ou genérico («li o arquivo»), **RECUSE a WO** e peça o campo — quem escreveu a WO é quem tem o viés, e esta conferência é sua justamente por isso.
- Rode a checagem de **idempotência** que a WO indicar. Item já presente se PULA e se reporta; não se duplica.

**Ao aplicar:**
- Localize cada âncora EXATAMENTE. Se não achar uma, **PARE e reporte** — não chute um lugar próximo, não case «o mais parecido».
- Não toque em nada fora das edições nomeadas. Melhoria que você enxergar no caminho vira linha no relatório, não edição.
- Se a WO tocar `flatdrop/cli.py`, `gui._build_cli_args`, `gui._generate_bat` ou `gui._sources`, **PARE e reporte como URGENTE** antes de aplicar (invariante DEC-020).
- **Não edite nada sob `.claude/`.** O classificador de permissão bloqueia o executor de alterar a própria configuração, e está certo — «eu autorizo» dito no chat não muda isso. Esses arquivos chegam prontos do chat; você só confere que estão no disco e os inclui no `git add`.
- Se a WO mexe em CÓDIGO, rode `python -m pytest -q` ao fim. Se mexe na GUI, diga o que precisa de smoke manual no Windows — a suíte não cobre tkinter.
- Rode `git diff` e confira a forma esperada: os arquivos previstos, e nada além.

**Números de conferência:** rode cada um e **reporte o número CRU com o comando ao lado**, mesmo quando bater. Se o número previsto pela WO não bater com o medido, **o medido vence** — reporte a divergência e **não conserte o arquivo para «fechar» o número**. Erro de previsão do checklist é erro de quem escreveu a WO, e já aconteceu sete vezes aqui. `grep` casa por LINHA: frase quebrada em duas linhas devolve zero, e zero vira «não existe» na leitura seguinte.

**Fecho — dois estados, duas formas:**
- **VERDE** (âncoras todas casadas, suíte passou ou WO só de doc, `git diff` na forma prevista) → `add`, `commit` e **`push`, sem perguntar.** Não peça permissão para o que já está decidido. Mensagem SEM acento, Conventional Commits. **A própria WO entra no `git add`.**
- **VERMELHO** (suíte falhou, âncora não encontrada, `git diff` com arquivo fora do previsto) → **não commite e não empurre.** Feche com um MENU de saídas reais, a recomendada em primeiro lugar e marcada `(Recomendado)` — pela ferramenta `AskUserQuestion` se ela existir; sem ela, menu numerado em texto, **dizendo que caiu no fallback**. **Nunca pergunte em prosa:** pergunta escrita no meio do texto passa despercebida.
- **Divergência entre previsto e medido NÃO é vermelho** e não bloqueia o push: o executor não errou. Ela é obrigatória em **seção própria do relatório**, com o número previsto, o número medido e a causa se você a souber. *(DEC-033: o estado intermediário «verde-que-pergunta» foi tentado e revogado — ele criava um terceiro caso sem forma, e a pergunta saía em prosa.)*

**O relatório é o ÚLTIMO passo**, escrito depois de o push estar resolvido. Ele diz o que de fato aconteceu: empurrado com o hash, ou não empurrado com o motivo. RELATE: o que foi feito · o que fugiu do texto literal da WO · arquivos tocados · os números crus das conferências · resultado da suíte · o commit e o push.

Grave o MESMO relatório em `../AAMMDD-HHMM-code-flatdrop.txt` (pasta-pai do repo). Se a escrita for negada, diga e siga.

Nota: as WOs com nome antigo (`spec0001`–`spec0037`) são WOs — o nome ficou, a pasta mudou. A próxima livre é a maior existente + 1: confira a pasta, não confie em número escrito em documento.

WO: $ARGUMENTS
