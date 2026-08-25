# ANALISE — o formato do `_MANIFEST` (resposta à carta 01 do KCM)

- **Status:** **Decidida em parte** (item 1 decidido em 2026-08-23; item 2 segue em discussão)
- **Data:** 2026-08-23 (criação — não muda depois)
- **Decisão registrada em:** DEC-030 (item 1). Item 2: sem decisão.
- **Virou:** wo0051 (item 1). Item 2: ver «Adendo», abaixo.
- **Base:** `260821-kcm-para-flatdrop-01-o-manifesto-e-o-que-chegou.md`, itens **1** e **2**.
  O item **3** da mesma carta (`ahead/behind`) **não** entra aqui: já está decidido e virou a
  **wo0050** — é execução, não análise.

## Problema

O `_MANIFEST.md` abre afirmando, com todas as letras, que *«a tabela abaixo mapeia cada nome plano
de volta ao seu caminho original»*. Para uma classe inteira de arquivos essa afirmação é **falsa no
destino**: o Projeto do Claude renomeia no upload, e o nome declarado na coluna «Nome na pasta»
**não existe** na pasta que o assistente enxerga.

O sintoma não é estético. Quem lê o manifesto busca pelo nome declarado, não encontra nada, e
**ausência de arquivo é indistinguível de «não subiu»** — que é exatamente a dúvida que o manifesto
existe para eliminar. O KCM relata que, do lado deles, isso reintroduz a inferência de caminho que a
regra dura de entrega proíbe, e que atinge justo os arquivos mais lidos (os três *dotfiles* de
configuração e, lá, o `index.template.html`).

O segundo problema é de outra natureza: o mount **zera o `mtime`** de todo arquivo. O cabeçalho do
manifesto responde *«este lote é novo?»* (e responde bem — o KCM reconheceu isso na carta e rebaixou
o próprio pedido por causa disso), mas ninguém consegue responder *«qual arquivo mudou desde a
geração anterior?»*. Sem isso, a alternativa é reler tudo ou adivinhar — e adivinhar já custou uma
WO refeita inteira num projeto irmão.

**Se nada for feito:** a promessa do cabeçalho segue falsa para ~5% dos arquivos de cada lote, em
pelo menos três projetos que leem esse arquivo em toda abertura de sessão.

## Restrições / o que foi medido

**Medido aqui, em 2026-08-23**, por script sobre o `_MANIFEST_flatdrop.md` (gerado 2026-08-22 09:43,
38 entradas), cruzando cada nome declarado com o conteúdo real de `/mnt/project/`:

| Caminho original | Declarado na tabela | Existe no mount |
|---|---|---|
| `.flatdropignore` | `.flatdropignore` | `_flatdropignore` |
| `.gitignore` | `.gitignore` | `_gitignore` |
| `.claude/settings.local.json` | `settings.local.json` | `settings_local.json` |

**3 de 38 (7,9%).** O KCM mediu **11 de 109** em dois repos com modos de renomeação diferentes
(`collisions` e `fullpath`), o que descarta interferência do nosso renomeador.

**Regra do destino — deduzida, não documentada.** Sobre os 14 casos conhecidos: ponto inicial → `_`;
ponto interno → `_`; a última extensão sobrevive. É **inferência sobre software de terceiro**, sem
documentação pública e sem garantia de estabilidade. Rotular isso como fato dentro do nosso
manifesto é assumir um risco que não é nosso.

**Medido:** todo arquivo do mount chega com `mtime` `1979-12-31 00:00`, sem exceção, nos três
projetos observados.

**Limites que a solução tem de respeitar:**

- **A assinatura `<!-- flatdrop-manifest v1 -->` não pode mudar.** É ela que `is_our_folder` usa
  para autorizar o `safe_clear` — mexer nisso é arriscar apagar pasta de terceiro (DEC-007).
- **A tabela é contrato com leitor externo.** Ela é lida por sessões de chat em pelo menos três
  projetos (flatdrop, contexto-modular, mapsmith). Mudar o número de colunas é mudar o formato de um
  artefato que outra pessoa lê — o gatilho de análise, e o motivo deste documento existir.
- **DEC-020:** nada aqui toca `flatdrop/cli.py`, `gui._build_cli_args`, `gui._generate_bat` ou
  `gui._sources`. Tudo se resolve dentro de `write_manifest` — se alguma opção exigir sair de lá,
  é sinal de que a opção está errada.
- **Custo do `mtime`, medido no código:** `PlannedFile` já carrega `size`, obtido de um `stat()` em
  `_scan`. Acrescentar `mtime` **não precisa** tocar `_scan` nem o `candidates`/`_plan_names` (o
  coração da renomeação): basta `f.src.stat().st_mtime` dentro do próprio `write_manifest` — um
  `stat` por arquivo, sobre arquivo recém-copiado e ainda em cache. **Estimativa:** irrelevante para
  38–109 arquivos; a medir se algum dia alguém achatar milhares.
- **Ressalva do `mtime` que ninguém mencionou:** `git clone`/`checkout` carimba o `mtime` da hora do
  checkout, não do commit. Numa árvore de trabalho de uso diário (o caso real) o dado é bom; num
  clone recém-feito, todos os arquivos parecem novos ao mesmo tempo. O dado é útil, **não é
  autoridade** — a mesma ressalva de «foto da geração» vale aqui.

## Opções consideradas

### A — a coluna «Nome na pasta» passa a declarar o nome já sanitizado
- **O que é:** aplicar a regra do destino e escrever `_gitignore` na tabela.
- **Custo:** baixo (uma função de sanitização + testes). Formato intacto.
- **Ganha:** a busca pelo nome da tabela passa a encontrar o arquivo no mount.
- **Perde:** a tabela deixa de descrever **o que a ferramenta escreveu em disco**. Quem abre a pasta
  plana localmente vê `.gitignore` e lê `_gitignore` — o descasamento apenas troca de lado. Pior:
  **é frágil na direção mais provável**. Se a Anthropic afrouxar a sanitização, o nome declarado
  volta a não existir, e desta vez por culpa nossa. Descartada por isso.

### B — terceira coluna «nome no Projeto», preenchida só quando difere
- **O que é:** a tabela ganha uma coluna.
- **Custo:** baixo em código; **alto em compatibilidade** — muda a forma de todas as linhas.
- **Ganha:** honestidade máxima, diferença visível linha a linha.
- **Perde:** quebra qualquer leitor que espere duas colunas (o script desta análise, escrito em
  trinta segundos, quebrou). E paga esse preço em **100% das linhas** para carregar informação que
  só vale para 8% delas.

### C — uma linha no cabeçalho avisando da sanitização
- **O que é:** o «mínimo aceitável» que o próprio KCM propõe.
- **Custo:** uma linha.
- **Ganha:** resolve a **leitura** (quem lê o cabeçalho entende o que houve).
- **Perde:** não resolve a **busca** — o assistente que procura `.gitignore` continua achando nada,
  e é aí que dói. Boa como complemento, insuficiente sozinha.

### D — a ferramenta grava o arquivo já com o nome sanitizado
- **O que é:** o FlatDrop escreve `_gitignore` na pasta plana; tabela e disco voltam a concordar,
  dos dois lados.
- **Custo:** **o maior dos cinco, e no pior lugar.** A sanitização teria de rodar **dentro** de
  `_plan_names`, antes da verificação de unicidade — senão `settings.local.json` e
  `settings_local.json` na mesma árvore viram o mesmo nome e um sobrescreve o outro. `_plan_names` é
  o coração da ferramenta, com truncamento por hash e desempate por profundidade uniforme.
- **Ganha:** é a única opção **imune à direção mais provável de mudança** do destino (nome sem ponto
  não é sanitizado por regra nenhuma).
- **Perde:** a pasta plana deixa de ser cópia com nome fiel; e paga risco no código mais delicado do
  projeto para resolver um problema de **relato**. Descartada agora — fica registrada como a saída
  correta caso o problema deixe de ser de relato (ex.: se o upload passar a falhar, e não só a
  renomear).

### E — bloco de exceções depois da tabela *(não estava na carta)*
- **O que é:** a tabela fica **exatamente como está**, e logo abaixo dela entra uma seção curta,
  presente só quando houver caso, mais ou menos assim:

  ```
  > **Nomes que chegam diferentes ao Projeto (3).** O upload sanitiza: ponto inicial e ponto
  > interno viram `_`; só a última extensão sobrevive. Regra observada em 2026-08, não documentada
  > pela Anthropic — é PREVISÃO, não promessa.

  | Nome na pasta | Como chega ao Projeto (previsto) |
  |---|---|
  | `.gitignore` | `_gitignore` |
  ```

- **Custo:** baixo, todo dentro de `write_manifest`; nenhuma linha da tabela muda.
- **Ganha:** resolve **leitura e busca nas duas direções** (procurar `.gitignore` acha a linha da
  tabela *e* a exceção; procurar `_gitignore` acha a exceção). Mantém a tabela verdadeira sobre o
  disco. Rotula a inferência como inferência — e, se a regra do destino mudar, o que fica errado é
  um bloco datado e isolado, não a tabela.
- **Perde:** o dado fica em dois lugares (é preciso olhar abaixo da tabela). Aceitável: são poucas
  linhas e elas se anunciam.

### F — não fazer nada, e responder «não vamos fazer»
- Registrada porque a carta pede explicitamente que essa resposta seja possível. **Descartada:** o
  defeito é uma afirmação **errada** no nosso arquivo, não um recurso ausente — e custa três linhas
  consertar. Não há defesa razoável para mantê-lo.

## Recomendação

**Item 1 → opção E, com o aviso da opção C embutido no próprio bloco. Item 2 → sim: uma coluna
`mtime` na tabela, implementada em `write_manifest`.**

O critério que separa os dois — e que é o argumento inteiro desta análise:

> **Dado que vale para TODOS os arquivos pertence à tabela. Dado que vale para a EXCEÇÃO pertence a
> uma lista de exceções.**

O `mtime` existe para todas as linhas e só serve comparado linha a linha: é dado tabular, e a coluna
é o lugar dele. O nome sanitizado vale para ~8% das linhas: virar coluna faria 92% do arquivo
carregar célula vazia — pagando, em todas as linhas, a quebra de forma que a carta pede em nome de
poucas.

Reconheço o custo dessa recomendação, porque ele é o mesmo em ambos os casos: **a tabela muda de
forma de qualquer jeito**, por causa do `mtime`. Ou seja, o argumento «não mexa na tabela» não me
serve para descartar B; o que descarta B é a **densidade** (célula vazia em 92% das linhas), não a
compatibilidade. Se o autor decidir **não** adotar o `mtime`, a tabela fica intacta e a
recomendação para o item 1 continua sendo E — ela não depende do item 2.

Uma nota sobre por que **não** recomendo mais «a linha (c) já, agora, que é de graça», como sugeri
na conversa antes de escrever isto: (c) só é neutra se a decisão final for E ou B. Sob A ela vira
redundante e sob D vira **falsa** (os arquivos não mudariam de nome ao chegar — já chegariam
mudados). Adiantar (c) antes da decisão é criar retrabalho de baixo valor.

## Riscos

- **Estamos declarando comportamento de terceiro.** Se a sanitização do Projeto mudar, o bloco de
  exceções fica errado. Mitigação: o bloco diz «previsto», traz a regra e a data da observação, e
  vive fora da tabela — o erro fica confinado e legível.
- **`mtime` de clone recente engana** (todos iguais, do checkout). Mitigação: uma frase no cabeçalho,
  na mesma linha da ressalva «foto da geração».
- **Ruído.** Uma coluna a mais em tabela de 109 linhas é 109 células a mais para o leitor atravessar.
  Vigiar: se o manifesto ficar desconfortável de ler, a coluna é a primeira candidata a sair.
- **Fuso e formato.** `mtime` precisa sair em formato fixo e local (`AAAA-MM-DD HH:MM`), igual ao
  «Gerado em» — dois formatos de data no mesmo arquivo é convite a leitura errada.
- **Regressão silenciosa:** o `_MANIFEST` é gravado por `write_manifest` e lido por `is_our_folder`
  só na primeira linha. Nada disso deve tocar a assinatura. Um teste tem de fixar isso.

## Ponto de decisão *(respondido em 2026-08-23 — mantido como estava, para o registro)*

**A tabela do `_MANIFEST` pode ganhar uma coluna `mtime`?**

- **Sim** → sai uma WO com as duas partes: coluna `mtime` + bloco de exceções (E/C).
- **Não** → sai uma WO só com o bloco de exceções, e o item 2 volta ao `IDEAS` como **Adiada**, com
  gatilho («volta quando alguém precisar comparar duas gerações do mesmo mount»), e a carta ao KCM
  responde «não faremos agora, porque X» — que a carta deles diz valer tanto quanto o sim.

Pergunta secundária, para a mesma resposta: **incomoda que o manifesto passe a afirmar uma regra de
sanitização que a Anthropic não documenta?** Se incomodar, a saída é D (mais cara, no código mais
delicado) — e aí vale reabrir esta análise, não emendar a decisão.

---

# Adendo — 2026-08-23: a decisão do item 1, e por que o item 2 mudou de pergunta

## Item 1 — decidido

**E + C, com o aviso embutido no bloco.** Vira a **wo0051** e a **DEC-030**. A tabela não muda; o
bloco de exceções aparece só quando houver caso. Nada a acrescentar ao que está acima.

## Item 2 — a objeção do autor, que procede, e o que sobra dela

O autor questionou a utilidade do `mtime` nestes termos: *o que uma data que diz que um arquivo é o
mais recente tem a ver com o fato de que o protocolo exige LER o mount?* E completou: se o
assistente conclui «isto está velho» sem ler, o pecado é não ler — e se estiver de fato velho, a
conduta certa nunca foi gerar mesmo assim, foi **ler, comparar, constatar, e pedir a atualização**.

**Procede, e a análise acima subestimou isso.** Três pontos:

1. **O caso que originou o pedido não seria resolvido pelo `mtime`.** O próprio KCM já havia
   recuado metade do caminho na carta 01: o cabeçalho (`Gerado em` + commit + status) teria
   refutado de graça a crença «este mount é de ontem». O que faltou lá foi **olhar**, e nenhum dado
   novo conserta não-olhar.
2. **Um dado que diz «velho» é uma licença para não ler.** É o risco específico do `mtime`, e é
   grave porque veste de método exatamente o gesto que se quer proibir. Um instrumento que autoriza
   a pular a leitura precisa ser *conclusivo*; `mtime` é indiciário.
3. **`mtime` é um proxy que mente nas duas direções.** `git checkout`/`clone` carimba a hora do
   checkout em arquivos que não mudaram há meses; uma cópia com preservação de timestamp mantém
   data antiga em arquivo que acabou de chegar. Ele responde «quando foi tocado», não «mudou».

**O que sobra, e é real:** existe uma segunda pergunta, diferente da primeira, que o cabeçalho
**não** responde — *«dos 39 arquivos, qual eu preciso reler agora?»*. Ela aparece quando o mount é
regenerado no meio da conversa (o caso «já subi de novo»), que é frequente aqui. Mas para essa
pergunta o `mtime` continua sendo o instrumento errado. Duas alternativas melhores:

### Contraproposta 1 — listar os arquivos rastreados que divergem do commit *(recomendada)*

O `git status` **já sabe**, exatamente e sem custo novo, quais arquivos não são o commit. Hoje o
manifesto conta (`1 modificado(s)`) e não nomeia — recusa deliberada da wo0048, por privacidade e
ruído. A recusa continua certa para os **não rastreados** (é onde mora o arquivo pessoal), mas para
os **modificados que entraram no achatamento** ela não protege nada: esses nomes já estão na tabela,
duas linhas acima. Nomear esses — e só esses — responde a pergunta que o leitor faz o tempo todo:
*o que estou lendo é o commit, ou trabalho por cima dele?*

- **Custo:** ínfimo. `git status --porcelain=v1` já é chamado; basta cruzar os nomes com
  `plan.files` e listar a interseção.
- **Ganha:** dado **autoritativo** (vem do git, é de conteúdo), não proxy. E funciona com **um**
  manifesto só, sem depender de o assistente lembrar da geração anterior.
- **Perde:** não responde «mudou desde o mount anterior» quando as duas gerações estão no mesmo
  commit e o arquivo mudou nos dois — caso raro, e coberto pela contraproposta 2.

### Contraproposta 2 — hash curto por arquivo, se o objetivo for comparar duas gerações

Se o que se quer mesmo é *«mudou desde a geração anterior?»*, o instrumento correto é um **hash
curto** (8 hex), não a data:

> **hash igual ao que eu já li JUSTIFICA pular a releitura; `mtime` antigo apenas SUGERE.**

É a diferença entre pular por prova e pular por palpite — e o palpite é o defeito que o pedido
tentava consertar. Custo: hash calculado durante a cópia (`execute_plan` já lê cada byte), uma
coluna a mais na tabela. Fica **para depois**, se a contraproposta 1 não bastar em uso real.

### Recusa explícita, para a carta ao KCM

**O `mtime` como pedido: não faremos.** O motivo, dito por inteiro: ele não resolve o caso que o
motivou (o cabeçalho já resolvia, como vocês mesmos reconheceram), e cria um dado que **autoriza a
não ler** — que é o gesto que produziu a falha. Em troca vai a contraproposta 1, que responde à
mesma necessidade com dado do git em vez de proxy, e a 2, guardada com gatilho.

## Ponto de decisão que sobra

**A contraproposta 1 entra agora, na mesma leva do bloco de exceções?**

- **Sim** → vira a **wo0052** (listar os modificados rastreados que foram achatados), e a carta ao
  KCM sai depois dela, com as duas entregas fechadas.
- **Não** → a carta sai já com a recusa e a contraproposta descrita, e o item volta ao `IDEAS` com
  gatilho («volta na primeira vez que alguém precisar saber se o arquivo lido é o commit»).

A contraproposta 2 (hash) **não** entra nesta leva em nenhum dos dois casos: sem a 1 em uso real,
não há como saber se ela é necessária.
