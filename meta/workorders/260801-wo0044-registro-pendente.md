# WO 0044 — fechar o registro pendente da leva 0.12.0 → 0.14.0

> **Tipo:** mista — CÓDIGO (duas docstrings + uma constante morta) e REGISTRO (logs + modelo de WO).
> **Config sugerida:** modelo intermediário, `/effort` médio. As edições 1–3 são mecânicas; a 5 e a 6
> **delegam julgamento** (você reconstrói o conteúdo dos logs a partir do `git log`), então leia-as
> inteiras antes de começar.
> **Pré-requisito:** versão **0.14.0**, suíte verde (79 relatados em 29/07), árvore limpa **exceto**
> pelo `.flatdropignore` da raiz, que está modificado e não commitado de propósito (edição 7).
> **Base:** `260729-HANDOFF-BRIEF.md` seção 3.1 + a sessão de 2026-08-01 (DEC-028).
> **Depende de:** nada. Mas o autor está aplicando, na mesma leva, oito arquivos entregues pelo chat
> (CEREBRO, INSTRUÇÕES, CLAUDE.md, `.claude/settings.json`, as duas skills, `.flatdropignore`,
> `meta/SPEC.md`) e sete documentos de registro. Se algum ainda não estiver no disco, **aplique
> mesmo assim** — nenhuma edição abaixo depende deles.
> **Âncora semântica:** se um trecho-âncora não bater EXATAMENTE, **PARE e reporte** — nunca chute um
> lugar próximo.
> **Idempotência:** antes de cada inserção, procure a frase-chave do texto NOVO. Se já existir,
> **PULE** o item e diga no relatório — não duplique.

> **Canal dos meta neste ciclo = CHAT.** O chat já entregou `meta/STATUS.md`, `meta/IDEAS.md`,
> `meta/DECISIONS.md`, `meta/CHANGELOG.md`, `meta/GLOSSARY.md`, `meta/ROADMAP.md` e
> `logs/2026-08-01.md` como arquivos inteiros. **Não faça append em nenhum deles.** Esta WO toca
> código, `logs/` de dias anteriores e `meta/workorders/_TEMPLATE.md` — nada mais.

---

## 1. Por que

A leva 0.12.0 → 0.14.0 (seis WOs, cinco decisões) foi aplicada e commitada, mas deixou quatro
rastros de registro para trás. Três são baratos; o quarto — os logs — é o único registro do
raciocínio das sessões de 28 e 29/07, e se não for escrito agora se perde para valer.

As duas docstrings foram sinalizadas pelo próprio Code no relatório da wo0043, que **corretamente**
não as tocou por estarem fora das âncoras daquela WO. Agora é para corrigir.

## 2. Contexto factual

Ordem dos fatos, para os textos abaixo não afirmarem nada que não aconteceu:

- **wo0038 (0.12.0)** — FIX-011: a poda passou a consultar as pastas alcançadas por negação; e o
  `_TREE` passou a **nomear** o que foi pulado por ignore do autor, com teto `TREE_NAME_CAP` (10) e
  `(+N mais)`. *(medido: `match_file` já devolvia «não ignorado» para o arquivo negado — quem o
  perdia era a poda.)*
- **wo0041 + wo0042 (0.13.0)** — DEC-027, trava por pasta no editor.
- **wo0043 (0.14.0)** — o teto simples virou **amostra**: `TREE_NAME_HEAD` (6) primeiros +
  `TREE_NAME_TAIL` (4) últimos + o meio contado, via a função nova `_tree_amostra`. **Desde então,
  `TREE_NAME_CAP` não é lido por nenhum código** *(medido nesta sessão: as únicas ocorrências no
  pacote são a definição em `config.py` e as duas docstrings desta WO).*
- O relatório da wo0043 registra: 79 testes verdes, commit `e772d45`, e o `.flatdropignore` já
  modificado antes daquela sessão — deixado fora do commit por estar fora do escopo.

---

## Edição 1 — `flatdrop/core.py` · docstring de `_peek_children`

**Âncora** *(primeira linha da docstring da função `_peek_children`)*:

```
    """Nomes dos filhos DIRETOS de uma pasta ignorada, ate ``C.TREE_NAME_CAP``.
```

**Substituir por:**

```
    """Nomes dos filhos DIRETOS de uma pasta ignorada, resumidos por ``_tree_amostra``.
```

## Edição 2 — `flatdrop/core.py` · docstring de `write_tree`

**Âncora** *(fim da docstring de `write_tree`, logo antes do `"""` de fechamento)*:

```
    A arvore e montada a partir de plan.files (copiados) e plan.skipped_items
    (pulados, ja em memoria). A UNICA leitura de disco e a espiada rasa nos filhos
    diretos de cada pasta ignorada pelo AUTOR (wo0038): sem recursao, limitada por
    C.TREE_NAME_CAP, e tolerante a falha (devolve vazio).
```

**Substituir por:**

```
    A arvore e montada a partir de plan.files (copiados) e plan.skipped_items
    (pulados, ja em memoria). A UNICA leitura de disco e a espiada rasa nos filhos
    diretos de cada pasta ignorada pelo AUTOR (wo0038): sem recursao, resumida por
    _tree_amostra (C.TREE_NAME_HEAD primeiros + C.TREE_NAME_TAIL ultimos, com o meio
    contado — wo0043), e tolerante a falha (devolve vazio).
```

## Edição 3 — `flatdrop/config.py` · remover a constante morta

> **Opcional, e o autor pode dispensá-la sem prejuízo do resto.** `TREE_NAME_CAP` deixou de ser
> lido na wo0043; o que sobrou foi a definição e as duas docstrings das edições 1 e 2. Constante
> morta com comentário que descreve um mecanismo aposentado é armadilha para quem ler depois.
> Se preferir mantê-la, **pule esta edição e diga no relatório** — as edições 1 e 2 já resolvem a
> desinformação.

**Âncora:**

```
# Quantos nomes o _TREE.md lista antes de agregar o resto ("+N mais"), tanto para
# arquivos pulados por ignore DO AUTOR quanto para a espiada rasa numa pasta ignorada.
TREE_NAME_CAP = 10

```

**Remover o bloco inteiro** (as três linhas e a linha em branco seguinte).

> Antes de remover, confirme com `grep -rn "TREE_NAME_CAP" .` que **não sobra nenhuma outra
> referência** além das que as edições 1 e 2 acabaram de corrigir. Se sobrar qualquer uma em
> código (não em comentário), **PARE e reporte** — a constante não estava morta.

## Edição 4 — `meta/workorders/_TEMPLATE.md` · conferir e, se faltar, criar

**Sem âncora — verificação primeiro.** Se o arquivo **já existir**, não o toque: apenas informe no
relatório se ele é o modelo de WO ou outra coisa, e cole as 5 primeiras linhas. Se **não existir**,
crie-o com exatamente este conteúdo *(a cerca externa tem quatro crases porque o
conteúdo tem blocos de três)*:

````
# WO NNNN — [titulo curto e concreto, no que a WO ENTREGA]

> **Este arquivo e o MODELO — nao o preencha aqui.** Copie para `meta/workorders/AAMMDD-woNNNN-desc.md`
> e preencha a copia. Ele sobe sempre ao Projeto (o `.flatdropignore` ignora `meta/workorders/*` mas
> reinclui `!meta/workorders/_TEMPLATE.md`), para que a primeira sessao depois de uma transferencia
> tenha o formato a mao sem precisar das WOs antigas.
>
> **O que e uma WO:** instrucao de APLICACAO — ancora + texto exato — que o chat autora e o Code posiciona.
> **O que NAO e:** a spec de feature diz **o que** construir e quando esta pronto; a WO diz **como aplicar**.
> Se voce ainda nao sabe o que construir, nao e hora de escrever WO — e hora de analise ou spec.

---

## Cabecalho — preencha as linhas que se aplicam e apague as que nao

> **Tipo:** WO de CODIGO · WO de DOC (registro) · mista.
> **Config sugerida:** modelo e esforco para quem for aplicar.
> **Pre-requisito:** versao/commit em que esta WO foi escrita, e o estado esperado (testes verdes, arvore limpa).
> **Base:** a decisao, a analise ou a conversa que originou.
> **Depende de:** WOs que precisam estar aplicadas antes — ou apague a linha.
> **Ancora semantica:** se um trecho-ancora nao bater EXATAMENTE, **PARE e reporte** — nunca chute um
> lugar proximo. Os arquivos podem ter mudado entre a escrita desta WO e a aplicacao.
> **Idempotencia:** antes de cada insercao, procure a frase-chave do texto NOVO. Se ja existir, **PULE**
> o item e diga no relatorio — nao duplique.

> **Canal dos meta neste ciclo = CHAT** *(ou **CODE** — escolha um e apague o outro)*.
> Se **CHAT**: esta WO toca so codigo/config — nao faca append nos `meta/`; o chat entrega os
> documentos depois da validacao. Se **CODE**: esta WO E o registro — aplique os appends previstos
> e nao espere doc do chat. *Uma fonte por doc por ciclo; escolher errado aqui duplica conteudo.*

---

## 1. Por que

[Uma a tres frases: a dor concreta, ou a causa raiz se for correcao. Quem aplica precisa saber o que
esta consertando para reconhecer quando o resultado sai errado. Se for correcao de defeito introduzido
por WO anterior, diga qual e assuma — historico honesto e o que impede repetir.]

## 2. Contexto factual *(so em WO de registro — apague em WO de codigo)*

[Os fatos que os textos das edicoes afirmam, na ordem em que aconteceram. Esta secao e a FONTE dos
blocos abaixo: fato que nao esta aqui nao deveria aparecer la. Marque o que foi **medido** e o que e
**deduzido** — inferencia sem rotulo vira fato na leitura seguinte.]

---

## Edicao 1 — `caminho/real/do/arquivo.ext` · [o que muda, em cinco palavras]

**Ancora** *(diga ONDE fica: secao, funcao, item — nunca numero de linha)*:

```
[trecho literal e unico do arquivo vivo, copiado sem reformatar]
```

**Substituir por:**

```
[texto exato que entra]
```

> Variantes — use a que couber, sempre com a ancora acima: **Inserir IMEDIATAMENTE APOS** ·
> **Inserir IMEDIATAMENTE ANTES** · **Remover o bloco inteiro** · **Criar arquivo novo** (sem ancora;
> diga o que fazer se ele ja existir).

## Edicao 2 — `caminho/real/do/arquivo.ext` · [...]

[Repita. Uma edicao por bloco. Se um arquivo recebe mudancas distantes entre si, numere 2a/2b/2c em
vez de empilhar num bloco so — cada uma com a propria ancora.]

---

## Fora de escopo

[O que esta WO deliberadamente NAO faz, para que quem aplica nao "aproveite a viagem". Melhoria que
voce enxergou no caminho vira ideia no IDEAS ou outra WO — nao entra aqui.]

## Armadilhas desta WO

[So quando houver. O que ja deu errado antes neste mesmo lugar e o que quem aplica pode quebrar sem
perceber: ancora que aparece duas vezes, arquivo com fim de linha CRLF (ancora multi-linha colada com
\n nao casa), bloco gerado que sera reescrito, numero de check ja usado.]

---

## Depois de aplicar — conferencia antes do commit

- [ ] `git diff` mostra **exatamente** os arquivos previstos, e nada alem.
- [ ] [Conferencia de forma especifica desta WO — ex.: "a entrada nova ficou dentro da secao certa".]
- [ ] **WO de codigo:** `python -m pytest -q` passa com **0 erros**. Se acusar erro, **PARE e reporte
      antes de commitar**.
- [ ] **WO so de doc:** nao precisa de suite — a rede e o `git diff`.
- [ ] **Teste manual que a suite NAO cobre** (obrigatorio quando a WO toca a GUI, que o pytest nao
      alcanca): [caso feliz · caso de borda · regressao possivel].
- [ ] **Invariante DEC-020:** se a WO tocar `flatdrop/cli.py`, `gui._build_cli_args`,
      `gui._generate_bat` ou `gui._sources`, PARE e reporte como URGENTE antes de aplicar.

## Relatorio de aplicacao *(quem aplica preenche ao terminar)*

O que foi feito · o que fugiu do texto literal da WO · arquivos tocados · resultado da suite · o commit.
Grave o MESMO relatorio em `../AAMMDD-HHMM-code-flatdrop.txt` (pasta-pai do repo).
**Nao** substitua este relatorio pelo bloco de fecho do chat: aquele e da raia de planejamento, e trocar
relatorio por formulario perde justamente o que so quem aplicou viu.

## Commit — blocos separados, mensagem SEM acento

```
git add [caminhos]
```

```
git commit -m "tipo(escopo): descricao no imperativo curto" -m "Corpo explicando o porque, sem acento."
```

```
git push
```
````

## Edição 5 — `logs/2026-07-28.md` · acrescentar as sessões que faltam

> **Esta edição delega julgamento.** Não há texto exato: o conteúdo tem de ser reconstruído a partir
> do repositório. Trabalhe assim, nesta ordem:
>
> 1. `git log --oneline --since=2026-07-27 --until=2026-07-30` e `git show --stat <cada commit>` para
>    levantar o que cada sessão de fato entregou.
> 2. Leia o `logs/2026-07-28.md` existente para ver **onde ele para** — só o que vier depois entra.
> 3. Leia `meta/DECISIONS.md` (DEC-023 a DEC-027, FIX-011) e `meta/CHANGELOG.md` (0.12.0 a 0.14.0):
>    o **porquê** já está escrito lá, não o reinvente — referencie e resuma.

**Inserir ao FIM do arquivo** uma seção por sessão, no formato da DEC-026 e do `meta/LOG-TEMPLATE.md`:

```
## Sessão N — <periodo>: <assunto>
```

Cobrindo, em ordem: **wo0038** (FIX-011 + `_TREE` nomeando o ignorado, 0.12.0), **wo0039/wo0040** (se
existirem commits correspondentes — confira), **wo0041 + wo0042** (trava por pasta, DEC-027, 0.13.0).
Cada seção com os campos do molde: objetivo, o que foi feito, decisões, bugs, aprendizados, onde parei.

**Se o arquivo já contiver seções `## Sessão` cobrindo essas WOs, PULE e diga no relatório.**

## Edição 6 — `logs/2026-07-29.md` · criar

**Criar arquivo novo** (se já existir, **PARE e reporte** em vez de sobrescrever), no formato do
`meta/LOG-TEMPLATE.md`, cobrindo a sessão da **wo0043** (amostra do `_TREE`, 0.14.0, commit
`e772d45`) e a redação do `260729-HANDOFF-BRIEF.md` que encerrou aquela conversa. Mesmas fontes da
edição 5. Registre também, em «Aprendizados», o erro de processo daquela sessão que já está no
handoff: o assistente afirmou que uma WO estava pendente quando ela já estava aplicada, com dois
`.txt` no mount dizendo o contrário — não lidos.

## Edição 7 — `.flatdropignore` da raiz · conferir e commitar

**Nenhuma edição de conteúdo.** O chat entregou a versão nova (DEC-028) para o autor aplicar à mão —
o repo está no **modo manual** porque o editor da GUI não convive com regra escrita fora do bloco
gerenciado. Sua tarefa aqui é só:

1. `git diff -- .flatdropignore` e conferir que o arquivo tem, **dentro** do bloco
   `# >>> flatdrop-editor`, as quatro linhas `logs/*`, `meta/workorders/*`,
   `!meta/workorders/_TEMPLATE.md` e `INSTRUCOES-DO-PROJETO.md` — e **nada depois do `# <<<`**.
2. Incluí-lo no commit desta WO.

Se o arquivo no disco ainda for o antigo (com linhas repetidas dentro e fora do bloco), **não o
edite**: reporte, e o autor aplica o arquivo entregue.

---

## Fora de escopo

- **Não toque em `meta/STATUS.md`, `meta/IDEAS.md`, `meta/DECISIONS.md`, `meta/CHANGELOG.md`,
  `meta/GLOSSARY.md`, `meta/ROADMAP.md` nem `logs/2026-08-01.md`** — todos vieram inteiros do chat
  neste ciclo (canal = CHAT). Append seu ali duplicaria conteúdo.
- **Não implemente a correção do bug do bloco gerenciado.** Ela depende de duas respostas do autor
  que ainda não vieram, e está desenhada em `meta/analises/260728-ANALISE-bloco-gerenciado-vs-manual.md`.
- **Não mexa no `_tree_amostra` nem em `TREE_NAME_HEAD`/`TREE_NAME_TAIL`.** As edições 1 e 2 corrigem
  a **descrição**, não o comportamento.
- **Não arquive o `meta/DECISIONS.md`.** Está previsto para depois do commit desta WO, como trabalho
  próprio.

## Armadilhas desta WO

- **A âncora da edição 2 é multi-linha.** `flatdrop/core.py` está em LF; cole o trecho como está,
  sem reindentar. Se a busca falhar por uma diferença de espaço, **reporte** em vez de aproximar.
- **`_peek_children` e `write_tree` citam a mesma constante.** Não conserte uma e esqueça a outra —
  e não use busca-e-troca global de `TREE_NAME_CAP`, que atingiria a definição em `config.py` antes
  de a edição 3 decidir sobre ela.
- **A edição 3 é a única destrutiva.** Rode o `grep` de confirmação antes; se houver qualquer uso em
  código, ela está errada e o certo é parar.
- **Logs são conteúdo novo, não cópia.** Não copie o CHANGELOG para dentro do log: o CHANGELOG diz o
  que saiu, o log diz o que se aprendeu no caminho. Se não houver material para uma seção do molde,
  escreva uma linha honesta em vez de encher.

---

## Depois de aplicar — conferência antes do commit

- [ ] `git diff` mostra exatamente: `flatdrop/core.py`, `flatdrop/config.py` (se a edição 3 entrou),
      `meta/workorders/_TEMPLATE.md` (se criado), `logs/2026-07-28.md`, `logs/2026-07-29.md` (novo),
      `.flatdropignore` — e nada além.
- [ ] `grep -rn "TREE_NAME_CAP" .` não devolve nada em `flatdrop/` (ou devolve só a definição, se a
      edição 3 foi dispensada).
- [ ] `python -m pytest -q` passa com **0 erros**. Se acusar erro, **PARE e reporte antes de commitar**
      — as edições 1 e 2 são docstrings e a 3 remove código morto; nenhuma deveria mexer no resultado.
- [ ] O `logs/2026-07-28.md` continua com a sessão original intacta no topo, e as novas vieram
      **depois**, como `## Sessão N`.
- [ ] Nenhum arquivo de `meta/` fora `workorders/_TEMPLATE.md` aparece no diff.

**Teste manual (a suíte não cobre):** rode `python run.py . --dest <tmp> --tree --preview` e confira
que o `_TREE.md` continua saindo com a faixa (`... (+N no meio, M no total) ...`) — é a rede contra a
edição 3 ter removido algo vivo.

## Relatório de aplicação

O que foi feito · o que fugiu do texto literal desta WO · arquivos tocados · resultado da suíte · o
commit. Grave o MESMO relatório em `../AAMMDD-HHMM-code-flatdrop.txt` (pasta-pai do repo); se a
escrita for negada, diga e siga.

**Diga explicitamente:** (a) se `meta/workorders/_TEMPLATE.md` já existia; (b) se a edição 3 foi
aplicada ou dispensada; (c) o que o `git log` mostrou das sessões de 28/29 de julho que **não**
estava no CHANGELOG — é justamente esse resto que justifica os logs.

## Commit — blocos separados, mensagem SEM acento

```
git add flatdrop/core.py flatdrop/config.py meta/workorders/_TEMPLATE.md logs/2026-07-28.md logs/2026-07-29.md .flatdropignore
```

```
git commit -m "docs(meta): fechar registro pendente da leva 0.12-0.14 (wo0044)" -m "Docstrings de _peek_children e write_tree citavam TREE_NAME_CAP, aposentado pela amostra do _TREE na wo0043; a constante morta sai do config. Logs das sessoes de 28 e 29 de julho escritos. Modelo de WO criado em meta/workorders para voltar a subir ao Projeto. flatdropignore reorganizado entra no commit."
```

```
git push
```
