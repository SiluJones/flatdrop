# FlatDrop — guia para o Claude Code

> Arquivo-raiz lido pelo Claude Code em todo TURNO. Mantenha CURTO (< 200 linhas — custa token em todo turno).
> Regra prática: se remover uma linha e o Claude ainda acerta, ela não pertence aqui. Procedural detalhado → vira skill em `.claude/skills/`.
> O comportamento detalhado do assistente está em `meta/CEREBRO.md`.

## Ritual de início
Leia `meta/CEREBRO.md` → `meta/CONTEXT.md` → `meta/STATUS.md` antes de agir. Confirme em uma frase o que entendeu.

## Build / validação
- Não há build (app Python puro). **Validação = testes:** `python -m pytest -q` (rode a partir da raiz do repo, antes de commitar mudança de código).
- Rodar o app: `python run.py` (sem args abre a GUI; com args roda a CLI).
- Mudança só de doc (`meta/`) NÃO precisa de testes; a rede é o `git diff`.
- A suíte não cobre tkinter: mudança de GUI pede **smoke manual no Windows** — aponte o que testar, não afirme que está validado.

## Convenções
- Identificadores em inglês; comentários e docs em PT-BR. Docstring em toda função pública.
- Mensagens de commit **sem acento** (o ambiente do Code usa Git Bash; o CMD do usuário corrompe acento). Conventional Commits.
- Edições nos `meta/` são **append-only** pelo Code (linha no STATUS, `DEC-`/`FIX-` em DECISIONS, marcar estado de fase no ROADMAP). Curadoria que REESCREVE um doc vem do chat (arquivo inteiro OU WO em `meta/workorders/`).
- **Vocabulário (DEC-023):** **WO** = *como aplicar* (delta com texto exato + âncora), em `meta/workorders/AAMMDD-woNNNN-desc.md` — a numeração continua das antigas specs, e **a próxima livre é a maior existente + 1 — confira a pasta, não confie em número escrito aqui** (um contador copiado para dentro de documento estável nasce certo e envelhece em silêncio: este dizia `wo0044` quando o repo já ia na `wo0055`). **spec** = *o quê construir e quando está pronto* (spec de feature, modelo em `meta/SPEC.md`), em `meta/specs/`. Não confunda: as `spec0001`–`spec0037` que estão em `meta/workorders/` são WOs com nome antigo, e assim ficam.
- Ao aplicar uma WO: ache cada âncora EXATAMENTE; se não achar, PARE e reporte — não chute lugar próximo. Não mexa fora das edições nomeadas. `git diff` antes do commit.
- **Ao fechar a tarefa, RELATE o trabalho** — o que fez, achados e desvios do que a WO pedia, arquivos tocados, resultado de `python -m pytest -q` e o commit. **Não** copie o bloco de fecho de turno do `meta/CEREBRO.md`: aquele é da raia de planejamento, e trocar relatório por formulário perde o que só você viu.
- **Invariante — proteger o `.bat` (DEC-020).** O gerador/uso de `.bat` é o núcleo mais
  valioso; NÃO o quebre por conveniência. `flatdrop/cli.py`, `gui._build_cli_args`,
  `gui._generate_bat` e `gui._sources` são intocáveis por features de estado/persistência.
  Se algo só avançar mexendo neles, PARE e reporte ao autor — claro, mais de uma vez, como
  URGENTE — antes de priorizar a feature.

## Quando eu pedir medição
- Eu leio só o que chega pelo mount; você lê o disco. Se eu pedir para **medir**, o pedido não tem âncora nem commit: não edite nada, não conserte nada, não sugira nada.
- Responda com o **número cru e o comando que o produziu**. Sem interpretação, sem recomendação — se você achar que o número indica um problema, diga o número primeiro e a suspeita depois, separada.
- Se o alvo estiver fora da raiz do repositório, isso depende de `permissions.additionalDirectories` no `.claude/settings.json` (a mesma chave do relatório em arquivo). Se a leitura for negada, DIGA — não estime.

## Push e relatório — nesta ordem, sempre
- **Verde** (validação passou, ou WO só de doc com o `git diff` conferido) → `add`, `commit` e **`push`, sem perguntar.** Não peça permissão para o que já está decidido. *(A DEC-033 revogou o desvio da DEC-032, que mandava pedir confirmação: em nove WOs a confirmação foi dada nove vezes, custou um turno cada, e na wo0060 produziu uma pergunta em prosa — o anti-padrão que a própria regra proíbe.)*
- **Vermelho** (validação falhou, âncora não encontrada, `git diff` com arquivo fora do previsto) → **não commite e não empurre.** E **não pergunte em prosa** («posso dar push?») — pergunta escrita no meio do texto passa despercebida. Feche com um **menu numerado** de saídas reais, a recomendada em **1** — ex.: `1) corrigir <o quê> e revalidar (recomendado)  2) reverter as edições  3) commitar local, sem push  4) empurrar assim mesmo`.
- **O relatório é o ÚLTIMO passo** — só depois de resolvido o push. Ele diz o que de fato aconteceu: empurrado (com o hash), não empurrado (com o motivo), ou aguardando a escolha do menu. **Relatório escrito antes da decisão conta metade da história** e vira mentira assim que o push sai; se a escolha chegar depois, **reescreva o relatório**, não deixe a versão velha valendo.

## Relatório em arquivo (sempre, sem pedir)
- Ao fechar QUALQUER tarefa (`/apply-wo` ou `/wrap`), grave o MESMO relatório também em `../AAMMDD-HHMM-code-flatdrop.txt` — pasta-PAI do repo (`FlatDrop/`), fora do versionamento.
- Exige `permissions.additionalDirectories` no `.claude/settings.json`. Se a escrita for negada, DIGA e siga — o relatório no chat continua sendo a entrega.
- Por que: copiar o relatório do console à mão trunca e duplica (aconteceu com o da wo0043), e o relatório é a única fonte do que só quem aplicou viu.

## Config (modelo × esforço)
- WO com texto exato já validado → **Sonnet**, esforço proporcional (mecânico = baixo/médio).
- Tarefa com julgamento sem rede (refator multi-arquivo, WO que delega decisão, mexida no core de ignores/nomeação) → **Opus**, esforço alto.
- Esforço proporcional à ambiguidade; `/effort low` para o trivial. Não há toggle de pensamento no Code — para um turno difícil pontual, `ultrathink` no prompt.

## Mapa rápido
- `flatdrop/core.py` — lógica pura (varredura, nomeação, multi-fonte, ignores). Sem UI. **Atenção:** `_scan` **poda diretórios in-place** antes de descer — pasta casada por ignore leva a subárvore junto, e um `!` dentro dela nunca é avaliado (DEC-025).
- `flatdrop/cli.py` — CLI. `flatdrop/gui.py` — GUI tkinter. `flatdrop/config.py` — defaults (allowlist, ignores). `flatdrop/settings.py` — persistência (só-GUI).
- `tests/` — pytest. `bat/cinzeiro/` — .bat de exemplo do usuário. `meta/` — contexto. `meta/workorders/` — WOs do chat. `meta/specs/` — specs de feature (nasce no primeiro uso).
