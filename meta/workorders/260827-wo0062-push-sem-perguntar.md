# WO 0062 — o push volta ao desenho do kit, e o STATUS para de ser deposito

> **Tipo:** REGISTRO — `meta/IDEAS.md`, `CLAUDE.md`, `meta/DECISIONS.md`, `meta/STATUS.md`.
> Nao toca codigo. **Nao toca `.claude/`** — as duas skills vem INTEIRAS pelo chat, no mesmo turno.
> **Config sugerida:** modelo intermediario, `/effort` medio.
> **Pre-requisito:** wo0061 aplicada e empurrada (`15afac5`), **122 testes verdes**, arvore limpa.
> **Base:** o relatorio da wo0061 e a observacao do autor em 27/08 — a confirmacao de push saiu em
> PROSA, e ele perguntou se nao era melhor adotar de vez a forma do kit. E melhor; a DEC-033 diz
> por que, com o que foi medido.
> **Ancoras lidas em:** *(as sete edicoes foram GERADAS por script a partir dos arquivos vivos do
> mount de 2026-08-27 11:23 — nenhum trecho de ancora foi digitado)*
> - `meta/IDEAS.md` — os tres blocos de «Ativas» a remover/mover e a entrada da contrabarra em
>   «Concluidas»; conferido que as duas entradas «ENTREGUE na 0.15.0» existem antes de remover.
> - `CLAUDE.md` — a linha do «Verde» em «Push e relatorio».
> - `meta/DECISIONS.md` — as tres ultimas linhas do arquivo.
> - `meta/STATUS.md` — o item 3 do backlog (30 linhas) e o item 6 (3 linhas).
> **Idempotencia:** procure `DEC-033`, `sem perguntar.** Não peça permissão` e `Arquivar o
> \`meta/DECISIONS.md\``. Se ja existirem, **PULE** e diga no relatorio.
> **Proximo comando:** nao ha.

> **Canal dos meta neste ciclo = CODE** (`IDEAS`, `DECISIONS`, `STATUS`, `CLAUDE.md`).

> **IMPORTANTE — dois arquivos chegam junto, pelo chat:** `.claude/skills/apply-wo/SKILL.md` e
> `.claude/skills/wrap/SKILL.md`, entregues INTEIROS para baixar e substituir. **Voce nao os
> edita** (o classificador bloqueia edicao em `.claude/`, medido na wo0054) — so confere que estao
> no disco e os inclui no `git add`. Se nao estiverem, commite o resto e reporte.

---

## 1. Por que

**A pergunta do autor tem resposta curta: sim, e melhor adotar a forma do kit.** O desvio da
DEC-032 durou tres dias e nove aplicacoes. Foi pedido nove vezes e concedido nove vezes — nunca
impediu nada — e cobrou dois precos:

1. **Mantem vivo o defeito que a nossa propria Devolucao 2 ao KCM denunciou:** a confirmacao cria um
   passo DEPOIS do relatorio, e foi assim que o relatorio da wo0051 ficou afirmando «NAO executei o
   push» depois de o push ter saido.
2. **Produziu uma pergunta em PROSA** na wo0060 e na wo0061 («Confirma que empurro `15afac5`?»),
   que e o anti-padrao que o nosso texto proibe. **E a culpa e do desenho, nao do executor:** a
   DEC-032 criou um terceiro estado — *verde-que-pergunta* — e nunca lhe deu forma. O menu estava
   reservado ao vermelho, entao sobrou a prosa. **E por isso que o menu nao apareceu.**

A alternativa que o autor levantou — «menu tambem no verde-com-desvio» — foi considerada e
descartada na DEC-033, com o motivo: recria o terceiro estado, e o gatilho seria um erro do
PLANEJAMENTO (a previsao do checklist), nao da aplicacao. Bloquear o push puniria quem aplicou por
erro de quem escreveu. **O que entra no lugar:** divergencia entre previsto e medido nao bloqueia,
mas e obrigatoria em secao propria do relatorio — e o relatorio vem logo depois do push.

**E o STATUS virou deposito.** O item 3 do backlog cresceu por append durante o merge e hoje contem
versoes contraditorias do mesmo estado: «Fase 2 (a fazer)» ao lado de «Fase 2c (feita)», «8 de 20
arquivos» ao lado de «20 de 20». STATUS e so o agora, e o agora do merge e «fechado». A Edicao 6
colapsa; o historico fica nas DECs, onde nao envelhece.

**Junto vai higiene do `IDEAS`:** duas ideias estavam **duplicadas** em «Ativas» e «Concluidas» ao
mesmo tempo (o estado do repo no manifesto e a contrabarra, as duas entregues na 0.15.0), e uma
terceira (o formato do manifesto) continuava «Ativa» depois de entregue na DEC-030.

---

## Edicao 1 — `meta/IDEAS.md` · duas Ativas duplicadas saem (ja estao em Concluidas)

**Ancora**:

```
- **FlatDrop grava o estado do repo no `_MANIFEST`.** Quando a raiz tem `.git`, rodar
  `git log -1 --format=%h %ad %s --date=short` e um **resumo** de `git status` (`branch main ·
  limpo` ou `branch main · 3 modificados · 2 não rastreados · 1 à frente de origin`) e escrever
  as duas linhas no manifesto, rotuladas como **foto do momento da geração** — não como estado
  atual. Valor: o mount é uma cópia achatada e não tem `.git`, então hoje o assistente não
  consegue ler commit nenhum e precisa pedir. Com isso, a ressalva vira dado, e some uma regra
  inteira do CEREBRO. Se quiser a lista de arquivos, `--porcelain` com teto (~20 + «(+N mais)»):
  `git status` verboso é ruído e vaza nome de arquivo não rastreado. (Autor, notas de 2026-07-30
  e 2026-08-01; refinos do assistente.)
- **Contrabarra em padrão deveria ser detectada.** Sintaxe `.gitignore` usa só barra normal — a
  contrabarra é escape, não separador —, então `!pasta\arquivo.json` não casa nada e o arquivo
  sobe achando que foi ignorado. **Medido:** o gerador do bloco monta todo caminho com
  `as_posix()`/`/` (`core.py` `_walk_leaves`, `annotate_children`, emissão de `pasta/*`), logo a
  linha problemática veio de edição manual, não da ferramenta. A correção não é no gerador: é o
  editor **avisar (ou normalizar)** ao ler linha manual com `\`. Só faz sentido depois que o
  gerador passar a enxergar o que está fora do bloco — **mesma frente do bug do bloco
  gerenciado**, não uma frente separada. (Nota de 2026-08-01.)
```

**Remover o bloco inteiro** (as 17 linhas, mais a linha em branco que as separa):

```

```

> **Remover o bloco inteiro** — as duas ideias **ja tem entrada em «Concluidas»** («ENTREGUE na
> 0.15.0», wo0048 e wo0047). Ficaram duplicadas em «Ativas» porque a curadoria de 23/08 moveu
> outras duas e nao viu estas. Nada se perde: as entradas de Concluidas sao mais completas.
> **Se as entradas de Concluidas nao existirem, PARE** — a remocao so e segura porque elas existem.

## Edicao 2 — `meta/IDEAS.md` · a ideia do formato do manifesto foi entregue

**Ancora**:

```
- **O formato do `_MANIFEST` promete um nome que não existe no mount.** Carta 01 do KCM
  (2026-08-21), com dois pedidos. **(1)** O cabeçalho diz que a tabela mapeia cada nome plano de
  volta ao caminho original — e para dotfile e nome com ponto interno ela mapeia um nome que **não
  está lá**: o Projeto do Claude sanitiza no upload (ponto inicial → `_`, ponto interno → `_`, só a
  extensão final sobrevive). Medido neste mount em 23/08: 3 de 38 (`.gitignore`,
  `.flatdropignore`, `settings.local.json`); medido pelo KCM: 11 de 109 em dois repos. Quem busca
  pelo nome declarado encontra ausência, que é indistinguível de «não subiu». **(2)** O mount
  **zera o `mtime`** de todo arquivo (`1979-12-31`), então não há como saber qual arquivo mudou
  entre duas gerações — só se o manifesto carregar o `mtime` da origem. Quatro opções mapeadas em
  `meta/analises/260823-ANALISE-formato-do-manifesto.md` (Em discussão) — **decisão do autor.**
```

**Remover o bloco inteiro:**

```

```

> **Remover daqui** — ela foi ENTREGUE (DEC-030 na wo0051, mais a linha-ponteiro na wo0055) e a
> Edicao 3 a reescreve em «Concluidas». Remover sem a Edicao 3 perde conteudo: **aplique as duas.**

## Edicao 3 — `meta/IDEAS.md` · ela entra em «Concluidas»

**Ancora**:

```
- **Contrabarra em padrão deveria ser detectada.** **ENTREGUE na 0.15.0** (wo0047): o editor avisa
```

**Substituir por** *(a linha da ancora e preservada no fim do bloco novo)*:

```
- **O formato do `_MANIFEST` promete um nome que não existe no mount.** **ENTREGUE (DEC-030,
  wo0051 + wo0055).** A tabela não mudou — continua descrevendo o disco —, e a divergência saiu num
  bloco de exceções rotulado como **previsão**, com o próprio teste de falsificação dentro («se o
  arquivo aparecer no Projeto com o nome da coluna 1, a regra mudou»). Depois a carta 03 do KCM
  mediu que o bloco *chegava por busca, não por leitura*, e a wo0055 subiu a **contagem** para o
  cabeçalho, sempre presente, inclusive com `0`. Medido: 3 de 39 aqui, 11 de 109 nos repos do KCM.
- **Contrabarra em padrão deveria ser detectada.** **ENTREGUE na 0.15.0** (wo0047): o editor avisa
```

> Entra imediatamente antes da entrada da contrabarra, mantendo a ordem cronologica da secao.

## Edicao 4 — `CLAUDE.md` · o verde volta a empurrar sem perguntar

**Ancora**:

```
- **Verde** (validação passou, ou WO só de doc com o `git diff` conferido) → `add` e `commit` sem perguntar. **`push`: peça confirmação — DESVIO REGISTRADO deste projeto (DEC-032)**, contra a regra do kit v1.104.0, que manda empurrar direto. O gatilho para reabrir está na DEC-032: a primeira vez que a confirmação atrasar um relatório correto.
```

**Substituir por:**

```
- **Verde** (validação passou, ou WO só de doc com o `git diff` conferido) → `add`, `commit` e **`push`, sem perguntar.** Não peça permissão para o que já está decidido. *(A DEC-033 revogou o desvio da DEC-032, que mandava pedir confirmação: em nove WOs a confirmação foi dada nove vezes, custou um turno cada, e na wo0060 produziu uma pergunta em prosa — o anti-padrão que a própria regra proíbe.)*
```

## Edicao 5 — `meta/DECISIONS.md` · DEC-033 no fim do arquivo

**Ancora**:

```
leia como esquecimento. O `.flatdropignore` perde a linha das instruções e ganha a explicação do
porquê — mas a linha vive DENTRO do bloco gerenciado, então o editor da GUI pode devolvê-la no
próximo salvamento: conferir uma vez na tela faz parte desta decisão.
```

**Substituir por:**

```
leia como esquecimento. O `.flatdropignore` perde a linha das instruções e ganha a explicação do
porquê — mas a linha vive DENTRO do bloco gerenciado, então o editor da GUI pode devolvê-la no
próximo salvamento: conferir uma vez na tela faz parte desta decisão.

## DEC-033 — o desvio do push é revogado: verde empurra sem perguntar

**Contexto.** A **DEC-032** (24/08) adotou quase tudo o que o kit v1.104.0 trouxe sobre o fecho de
trabalho, **menos** o push automático: o executor continuaria pedindo confirmação antes de empurrar.
O gatilho de revisão ficou escrito: *a primeira vez que a confirmação atrasar um relatório correto*.

**O que se mediu em três dias.** A confirmação foi pedida em **nove** aplicações (wo0053 a wo0061) e
concedida em **nove**. Nunca serviu para impedir nada. E produziu dois defeitos:

- **O relatório da wo0051 ficou afirmando «NÃO executei o push»** depois de o push ter saído. Foi
  o caso que originou a nossa Devolução 2 ao KCM — e o desvio o mantinha vivo, porque a confirmação
  cria um passo depois do relatório.
- **Na wo0060 a confirmação saiu em PROSA** («Confirma que empurro `15afac5`?»), que é exatamente o
  anti-padrão que o nosso próprio texto proíbe: *nunca pergunte em prosa, pergunta escrita no meio
  do texto passa despercebida*. A causa é do desenho, não do executor: a DEC-032 criou um terceiro
  estado — **verde-que-pergunta** — e não lhe deu forma. O menu estava reservado ao vermelho.

**Decisão.** O desvio é revogado. **Verde → `add`, `commit` e `push`, sem perguntar.** O menu
(`AskUserQuestion`, ou numerado com aviso de fallback) fica **só para o vermelho**. Dois estados,
duas formas, nenhum estado sem forma.

**O que sustenta.** O que a confirmação protegia era um push indesejado num remoto — e este é um
repositório de um autor só, com histórico linear e `git revert` a um comando de distância. O custo
era um turno por WO e um relatório podendo nascer falso. Trocamos uma proteção que nunca disparou
por um relatório que sempre diz a verdade.

**Alternativa considerada — «menu também no verde-com-desvio».** Foi o que o autor sugeriu ao ver a
pergunta em prosa. Descartada por criar de novo o terceiro estado, com a agravante de o gatilho ser
um erro do PLANEJAMENTO (a previsão do checklist da WO), não da aplicação: bloquear o push punia
quem aplicou por erro de quem escreveu. **O que fica no lugar:** divergência entre previsto e medido
**não bloqueia**, mas é obrigatória em seção própria do relatório — e o relatório vem logo depois do
push, então a visibilidade é preservada sem custar um turno.

**Consequências.** A `apply-wo/SKILL.md` e a `wrap/SKILL.md` passam a dizer isso, e as duas foram
entregues **inteiras pelo chat**, não por WO: são arquivos sob `.claude/`, e o classificador do
Claude Code bloqueia o executor de alterar a própria configuração (medido na wo0054). O `CLAUDE.md`
volta ao texto do kit. A DEC-032 continua válida no resto — as instruções sobem ao mount, e o
relatório é o último passo.
```

> Ancora multilinha (as tres ultimas linhas do arquivo), extraida por script.

## Edicao 6 — `meta/STATUS.md` · o item 3 do backlog: sai o merge, entra o que sobrou

**Ancora** (o item 3 inteiro, 30 linhas, extraido por script):

```
3. **Merge do KCM v1.120.0 — em curso, 3 fases.** O pacote chegou em 25/08 com a carta 03 (o
   `CEREBRO.md` daqui marcava v1.95.0: 23 versões de distância). **Varredura de linhas revogadas:
   23 ocorrências, 18 para remoção, 5 relato legítimo.** Duas coberturas, que medem coisas
   diferentes e não se substituem:
   - **arquivos do pacote comparados: 8 de 20** — faltam os 2 de `fusao` e os 10 modelos de `meta/`;
   - **ocorrências corrigidas: 8 de 18** (esta WO) — e a varredura é **PARCIAL**: não alcançou
     `logs/` nem `meta/workorders/`, que o `.flatdropignore` mantém fora do mount.
   **Fase 2a (wo0056, feita):** as «Regras de higiene» do CEREBRO passaram de 8 para **18** bullets
   (3.443 → 12.922 bytes, medido em 26/08), entrou a seção «Medição delegada», e o `CLAUDE.md`
   ganhou «Quando eu pedir medição» e «Push e relatório» (esta com o desvio da DEC-032 escrito no
   corpo). **Fase 2b (wo0058, feita):** «Bloco de fecho de turno», «Tabela de gatilhos» (+8 linhas)
   e a seção «Ao final de cada sessão… entrega arquivos completos» substituída por «Ao final da
   conversa, o assistente REGISTRA o que falta» — mais os títulos do ritual e da recomendação de
   configuração. **As 4 ocorrências de «sessão» no CEREBRO foram a zero** — pelo padrão varrido;
   a fase 2c achou mais 3, de outra forma («log de sessão», «entre sessões», «se a sessão mexeu»),
   e as fechou. **Fase 2c (wo0059, feita):** entraram as seções «Sonda e exploração»,
   «Correspondência entre projetos» e «Técnicas específicas deste projeto» — esta última com seis
   itens reais deste projeto, não vazia. Mais o funil da análise (agora com sonda), o parágrafo
   «o merge sabe somar, não sabe subtrair» e o bullet «princípio sem gatilho não dispara».
   **O merge do KCM v1.120.0 está FECHADO (wo0054 a wo0061).** Coberturas finais: **20 de 20
   arquivos do pacote comparados**; **18 de 18 ocorrências de linha revogada** tratadas (as 5 que
   restam no repo são relato legítimo, não instrução). Fase 3: o `_TEMPLATE.md` de WO absorveu o
   que sete WOs ensinaram (wo0060); os 11 modelos restantes foram comparados um a um na wo0061 e
   renderam quatro adoções — «Última conversa» no `STATUS`, gatilho por evento no `LOG-TEMPLATE`,
   as duas regras de manutenção no cabeçalho do `DECISIONS` e o critério de conclusão por fase no
   `ROADMAP` — mais uma frase no modelo de análise. **CONTEXT, CHANGELOG, IDEAS, GLOSSARY, HISTORY
   e SPEC não mudaram:** os nossos são mais ricos que os modelos, e a regra é que genérico não
   substitui vivo. Dois desvios ficam registrados no `IDEAS`: o `IDEAS` não separa ideias por autor,
   e o agrupamento do `GLOSSARY` ficou como ideia com gatilho. **Pendência:** uma passada de diff
   sobre o `meta/workorders/_TEMPLATE.md`, cuja redação foi escrita daqui enquanto o pacote estava
   fora do mount.
   **wo0057 (feita):** corrigiu os dois números que a wo0056 tinha escrito errado — o `STATUS`
   afirmava 16 bullets (real: **18**, já refletido acima) e o `IDEAS` ganhou a lição de método
   (número de checklist é derivado do texto final da WO, nunca estimado antes dela; terceira
   ocorrência da mesma falha em três WOs seguidas).
   **Fase 1 (wo0054, feita):** `Write` no `settings.json`, as 3 linhas revogadas da `wrap/SKILL.md`,
   a instrução obsoleta do `.flatdropignore`, `sessão`→`turno` no `CLAUDE.md`, e as 4 das
   instruções — que passam a subir ao mount (DEC-032). **Fase 2 (a fazer):** fusão do
   `meta/CEREBRO.md` (10 ocorrências vivas) com o template de 83 KB, mais as duas seções novas do
   `CLAUDE.md` («Quando eu pedir medição» e «Push e relatório — nesta ordem»). **Fase 3:** os
   modelos (`_TEMPLATE.md` de WO e de análise, e os 10 de `meta/`).
   *(O raciocínio completo do merge está numa análise que o autor decidiu NÃO versionar — por isso
   os números que importam estão aqui e na DEC-032, e não numa referência a arquivo.)*
```

**Substituir por:**

```
3. **Arquivar o `meta/DECISIONS.md`** em `DECISIONS-archive.md`. O arquivo passou de **69 KB e
   1.400 linhas**, contra o teto de ~700 que agora está escrito no cabeçalho dele (wo0061). Precisa
   de um critério de corte antes de virar WO — por data ou por fase encerrada —, e o critério é
   decisão do autor.
   *(O item que estava neste lugar, o **merge do KCM v1.120.0**, saiu: fechou em 27/08 nas quatro
   fases, wo0054 a wo0061. 20 de 20 arquivos do pacote comparados, 18 de 18 ocorrências de linha
   revogada tratadas. O porquê vive na **DEC-032** e na **DEC-033**; o que sobrou de pendência está
   aqui como itens 7 e 8.)*
```

> **O item 3 tinha virado um deposito.** Ele cresceu por append durante o merge e passou a conter
> versoes contraditorias do mesmo estado: «Fase 2 (a fazer)» convivia com «Fase 2c (feita)», e
> «arquivos comparados: 8 de 20» com «20 de 20». **STATUS e so o agora** — e o agora do merge e
> «fechado». O historico fica nas DECs, que e onde ele nao envelhece.

## Edicao 7 — `meta/STATUS.md` · dois pendentes do merge entram no backlog

**Ancora** (tres linhas):

```
6. Adiadas, com gatilho de retorno em `IDEAS.md`: multi-raiz na GUI, `pasta/` como exclusão dura,
   UI-2/UI-3, formato «caminho escrito». *(A **saída da CLI ASCII-safe** deixou de ser adiada — o
   gatilho disparou em 02/08 e a curadoria de 23/08 a moveu para «Ativas».)*
```

**Substituir por:**

```
6. Adiadas, com gatilho de retorno em `IDEAS.md`: multi-raiz na GUI, `pasta/` como exclusão dura,
   UI-2/UI-3, formato «caminho escrito». *(A **saída da CLI ASCII-safe** deixou de ser adiada — o
   gatilho disparou em 02/08 e a curadoria de 23/08 a moveu para «Ativas».)*
7. **Critérios de conclusão das quatro fases do `ROADMAP`.** A regra entrou no cabeçalho (wo0061);
   os critérios em si precisam ser decididos com o autor — a Fase 2 está «quase concluída» há dois
   meses, que é o sintoma de fase sem critério.
8. **Passada de diff sobre o `meta/workorders/_TEMPLATE.md`.** A redação dele foi escrita daqui
   (wo0060) enquanto o pacote estava fora do mount; o pacote voltou, e vale conferir se o kit tem
   formulação melhor. Barato.
```

---

## Fora de escopo

- **Editar qualquer coisa sob `.claude/`** — as duas skills chegam prontas do chat.
- **Arquivar o `DECISIONS.md`** — entra no backlog como item 3 (Edição 6), não é feito aqui: precisa
  de critério de corte, que é decisão do autor.
- **Preencher os critérios de conclusão do `ROADMAP`** — vira item 7 do backlog.
- Nada em `flatdrop/`.

## Armadilhas desta WO

- **A Edição 1 remove 17 linhas** e só é segura porque as duas entradas «ENTREGUE na 0.15.0» já
  existem em «Concluídas». **Confira antes de remover** — se não estiverem lá, PARE.
- **As Edições 2 e 3 são um par:** a 2 remove e a 3 reescreve em «Concluídas». Aplicar só a 2 perde
  conteúdo.
- **A âncora da Edição 6 tem 30 linhas.** Foi extraída por script; se não casar, o `STATUS.md` mudou
  depois de 27/08 11:23 — PARE e reporte.
- Ordem sugerida: 1 → 2 → 3 (IDEAS), depois 4, 5, 6, 7. As âncoras não se sobrepõem.

---

## Depois de aplicar — conferência antes do commit

- [ ] `git diff` mostra exatamente: `meta/IDEAS.md`, `CLAUDE.md`, `meta/DECISIONS.md`,
      `meta/STATUS.md` — **mais as duas skills** entregues pelo chat, que aparecem modificadas sem
      você as ter editado. *(«está lá?»)*
- [ ] `grep -c "DEC-033" meta/DECISIONS.md` → **1**. *(«está lá?»)*
- [ ] `grep -c "FlatDrop grava o estado do repo" meta/IDEAS.md` → **1** (só a de «Concluídas»; era
      **2**, medido em 27/08). Mesma conferência para
      `grep -c "Contrabarra em padrão deveria ser detectada" meta/IDEAS.md` → **1** (era **2**).
- [ ] `grep -c "Merge do KCM v1.120.0 — em curso" meta/STATUS.md` → **0**.
- [ ] **Este responde «presta?», não «está lá?»:** leia a seção «Push e relatório» do `CLAUDE.md` e
      a linha equivalente nas duas skills, e confirme que as três dizem **a mesma coisa** — verde
      empurra sem perguntar, menu só no vermelho. Três arquivos com a mesma regra escrita em
      versões diferentes é o defeito que esta WO está consertando; repeti-lo aqui seria irônico.
- [ ] `python -m pytest -q` → **122**, sem mudança (WO só de doc).
- [ ] **Invariante DEC-020:** nada em `flatdrop/`.

## Relatório de aplicação *(quem aplica preenche ao terminar)*

O que foi feito · o que fugiu do texto literal · os números crus · o commit · **o push, com o
resultado real** — e a partir desta WO o push é feito **sem perguntar** no caso verde. Se houver
divergência entre previsto e medido, ela **não** bloqueia: entra em seção própria do relatório.
Grave o MESMO relatório em `../AAMMDD-HHMM-code-flatdrop.txt`.

## Commit — blocos separados, mensagem SEM acento

```
git add meta\IDEAS.md CLAUDE.md meta\DECISIONS.md meta\STATUS.md .claude\skills\apply-wo\SKILL.md .claude\skills\wrap\SKILL.md meta\workorders\260827-wo0062-push-sem-perguntar.md
```

```
git commit -m "chore(kit): revogar o desvio do push e limpar o STATUS" -m "DEC-033: verde volta a empurrar sem perguntar, como o kit v1.104.0 manda. Em nove WOs a confirmacao foi dada nove vezes, nunca impediu nada, manteve vivo o relatorio que nasce falso e produziu pergunta em prosa - porque a DEC-032 criou um terceiro estado sem forma. Menu fica so para o vermelho. STATUS: o item 3 do backlog, que virou deposito durante o merge, colapsa para o que sobrou. IDEAS: duas ideias estavam duplicadas em Ativas e Concluidas, e uma terceira seguia Ativa depois de entregue."
```

```
git push
```
