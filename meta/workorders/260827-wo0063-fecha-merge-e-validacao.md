# WO 0063 — fecha a ultima pendencia do merge, e registra a validacao visual

> **Tipo:** REGISTRO — `meta/workorders/_TEMPLATE.md`, `meta/STATUS.md`, `meta/DECISIONS.md`.
> Nao toca codigo, nao toca `.claude/`.
> **Config sugerida:** modelo intermediario, `/effort` baixo. Dez edicoes, todas de texto.
> **Pre-requisito:** wo0062 aplicada e empurrada (`2fc6daa`), **122 testes verdes**.
> **Base:** a comparacao do `workorders/_TEMPLATE.md` contra o modelo do pacote v1.120.0, feita em
> 27/08 com o pacote de volta no mount; e as tres capturas de tela que o dono enviou no chat.
> **Ancoras lidas em:** *(as dez edicoes foram GERADAS por script a partir dos arquivos vivos do
> mount de 2026-08-27 12:47 — nenhum trecho de ancora foi digitado)*
> - `meta/workorders/_TEMPLATE.md` — a linha `## Edicao 1 — ...`, a linha `## Armadilhas desta WO`,
>   a linha do `Proximo comando` e a linha das armadilhas que termina em `numero de check ja usado.]`.
> - `meta/STATUS.md` — a secao «Pendente de validacao visual» (18 linhas), os itens 1, 3 e 8 do
>   backlog, e a secao «Ultima conversa».
> - `meta/DECISIONS.md` — a linha do cabecalho que diz `ja passou de 1.400`.
> - `workorders__TEMPLATE__template-update.md` — as secoes «Inventario» e «Medicao previa» e o
>   paragrafo «Afirmacao sobre artefato legivel», lidos inteiros.
> **Idempotencia:** procure `## Inventario`, `## Medicao previa` e `1.124`. Se ja existirem, **PULE**.
> **Proximo comando:** nao ha.

> **Canal dos meta neste ciclo = CODE.**

> **Um arquivo chega junto, pelo chat:** `logs/2026-08-27.md`. **Confira ANTES se ele ja existe.**
> Se NAO existir, salve o arquivo entregue como esta. Se JA existir (o `/wrap` pode te-lo criado),
> **nao substitua**: cole o conteudo entregue como uma secao `## Conversa 2` no fim do arquivo que
> ja esta la, preservando o que havia. **Diga no relatorio qual dos dois casos ocorreu.**

---

## 1. Por que

Tres coisas, todas de fecho.

**(a) A ultima pendencia do merge fecha.** O item 8 do backlog era conferir se o kit tinha redacao
melhor para o `workorders/_TEMPLATE.md`, cuja versao foi escrita daqui na wo0060 enquanto o pacote
estava fora do mount. O pacote voltou; comparei; **tinha**. Tres adocoes reais, nas Edicoes 1 a 4 —
e nenhuma delas substitui o que escrevemos: as duas regras que este projeto descobriu sozinho
(extrair ancora por script; a ancora cobre tudo o que o texto novo torna redundante) **nao existem
no modelo do kit** e ficam. Elas viram devolucao na proxima carta ao KCM.

**(b) A validacao visual saiu do zero.** O dono rodou a GUI e o editor e mandou tres capturas. Elas
confirmam **um** dos tres comportamentos pendentes — o rotulo `travada (manual)`, com a trava por
pasta visivel ao lado — e **nao exercitam** os outros dois, porque o `.flatdropignore` do projeto
testado nao tinha nem regra com `\` nem regra depois do marcador de fechamento. A Edicao 5 registra
o que foi visto **com a origem marcada** (`[relatado pelo dono, com print]`), e diz por que os dois
que faltam nao sao «quase o mesmo teste»: os tres caminhos sao independentes no codigo.

**(c) Um numero errado sai de dois lugares.** O `STATUS` e o cabecalho do `DECISIONS` afirmam que o
arquivo «passou de 1.400 linhas». **`wc -l` diz 1.124.** O 1.400 foi estimativa minha na wo0061; o
executor ja tinha reportado a divergencia na wo0062 e — corretamente — nao consertou por conta.

---

## Edicao 1 — `meta/workorders/_TEMPLATE.md` · secao «Inventario»

**Ancora**:

```
## Edicao 1 — `caminho/real/do/arquivo.ext` · [o que muda, em cinco palavras]
```

**Inserir IMEDIATAMENTE ANTES** *(a linha da ancora e preservada no fim do bloco novo)*:

```
## Inventario — de onde saiu a lista de edicoes *(apague se a WO tem uma edicao so)*

[Quando as edicoes abaixo sao **todos os lugares** que precisam mudar, diga como voce achou esses lugares.
Lista feita de cabeca, ou herdada do texto de quem apontou o problema, ja custou caro: o que ficou de fora
fica invisivel dos dois lados, porque a correcao e a conferencia saem do mesmo inventario incompleto.]

- **Saiu do artefato, nao da memoria.** A pergunta e sempre "que lugares declaram esta grandeza?", feita ao
  codigo. Grepe o **fato**, nao a frase: o mesmo campo aparece com outro nome de variavel, e a mesma regra
  aparece parafraseada. Procure o termo literal, a parafrase, e as listas de pendencia.
- **Nao truncar.** Nada de `head`, nada de "os principais". Inventario paginado e inventario errado, e o
  item que ficou de fora e justamente o que ninguem vai procurar depois.
- **Declare quantos.** Escreva o numero de pontos encontrados — "onze lugares montam este caminho" — para
  que quem aplica possa **contestar a contagem antes de agir**. Ja foi assim que um inventario truncado foi
  pego: a WO dizia onze, o executor achou doze. A contagem e a rede; a proibicao do `head` sozinha nao pega.

---

## Edicao 1 — `caminho/real/do/arquivo.ext` · [o que muda, em cinco palavras]
```

> Secao do modelo v1.120.0 que o nosso nao tinha. Ela resolve um risco que este projeto correu sem
> perceber: quando as edicoes de uma WO sao **todos os lugares** que precisam mudar, a correcao e a
> conferencia saem do MESMO inventario — se ele veio de cabeca, o que ficou de fora fica invisivel
> dos dois lados. A regra do «declare quantos» e a rede: quem aplica pode contestar a contagem
> antes de agir, que foi o que o executor fez tres vezes nesta semana.

## Edicao 2 — `meta/workorders/_TEMPLATE.md` · secao «Medicao previa»

**Ancora**:

```
## Armadilhas desta WO
```

**Inserir IMEDIATAMENTE ANTES** *(a linha da ancora e preservada no fim do bloco novo)*:

```
## Medicao previa *(so quando houver; nao e edicao)*

[So quando esta WO depender de um numero que a raia de planejamento nao pode ler. Diga O QUE contar e o
comando sugerido; peca de volta o valor e o comando que o produziu, sem interpretacao. Isto NAO tem ancora,
NAO tem commit e NAO muda arquivo — se a medicao contrariar o que a WO assume, PARE antes de editar e relate.]

## Armadilhas desta WO
```

> A outra secao que faltava. E o par da «Medicao delegada» do CEREBRO, do lado da WO: quando a raia
> de planejamento depende de um numero que ela **nao pode ler**, o numero e pedido — com o comando
> sugerido — e volta cru, sem interpretacao. Isto teria evitado varias das divergencias de
> contagem desta semana, porque a alternativa que sobrou foi estimar.

## Edicao 3 — `meta/workorders/_TEMPLATE.md` · o paragrafo que faltava no campo das ancoras

**Ancora**:

```
> **Proximo comando:** a linha `/apply-wo ...` da PROXIMA WO, crua e sozinha, ou "nao ha".
```

**Substituir por:**

```
> **Afirmacao sobre artefato legivel nao e opiniao, e leitura** — o que uma ferramenta faz, o que um
> simbolo contem, em que estado esta o mount. Nao cite simbolo, caminho ou capacidade de ferramenta
> que voce nao leu NESTE turno; dizer "nao li" nao autoriza escrever a WO em cima.
> **Proximo comando:** a linha `/apply-wo ...` da PROXIMA WO, crua e sozinha, ou "nao ha".
```

> Frase do modelo v1.120.0. E a generalizacao da nossa propria licao «ausencia de saida nao e
> ausencia de recurso» — a nossa falava do produto, esta fala de qualquer artefato legivel.

## Edicao 4 — `meta/workorders/_TEMPLATE.md` · a saida contra o CRLF

**Ancora**:

```
\n nao casa), bloco gerado que sera reescrito, numero de check ja usado.]
```

**Substituir por:**

```
\n nao casa), bloco gerado que sera reescrito, numero de check ja usado. Contra o CRLF a saida e
sempre a mesma: ancora de UMA linha nao tem quebra dentro, entao o fim de linha nao morde — para
inserir varias linhas, ancore em UMA so e diga se o texto novo entra antes ou depois dela.]
```

## Edicao 5 — `meta/STATUS.md` · a validacao visual: 2 de 3

**Ancora** (a secao inteira, 18 linhas, extraida por script):

```
## ⏳ Pendente de validação visual no Windows

O ambiente do Claude Code não tem display do Windows, então a **lógica** dos três foi exercitada e
passou, mas **ninguém viu a tela**. É o primeiro gesto de quem retomar, e leva cinco minutos:

1. **`travada (manual)`** — abrir o editor num projeto com pasta fechada por linha manual e
   conferir a coluna «Arquivo novo». (`source(pasta/__flatdrop_arquivo_novo__)` já devolve
   `flatdropignore` corretamente — o que falta é ver o rótulo.)
2. **Aviso de contrabarra** — pôr uma linha com `\` num `.flatdropignore`, abrir o editor: o
   aviso deve aparecer com arquivo e linha; corrigir para `/` e reabrir: sem aviso.
3. **`askyesno` de regra depois do bloco** — escrever uma regra depois do marcador de fechamento
   e salvar: deve perguntar antes de mover o bloco para o fim.

E, no mesmo passo, o smoke da wo0045: salvar sem mexer em nada e conferir que o arquivo **não**
ganhou linha em branco no fim; duplicar o bloco à mão e conferir que o salvamento **recusa** com
mensagem e não escreve nada.
```

**Substituir por:**

```
## ⏳ Validação visual no Windows — 2 de 3 conferidos em 27/08

**[relatado pelo dono, com print]** O dono rodou a GUI e o editor de `.flatdropignore` sobre **outro
repositório** (um projeto com `meta/`, `src/`, `.githooks/` — não o FlatDrop) e mandou três capturas.
O que elas mostram:

1. **`travada (manual)` — CONFIRMADO.** Na coluna «Arquivo novo», `logs`, `meta/analises` e
   `meta/workorders` aparecem com o rótulo `travada (manual)`, e `.claude`, `.githooks`, `meta` e
   `src` com `entra`. É a entrega da wo0047 funcionando na tela, com a trava por pasta (DEC-027)
   visível ao lado.
2. **`askyesno` de regra depois do bloco — NÃO exercitado.** Não havia regra escrita depois do
   marcador de fechamento no arquivo testado, então o diálogo não tinha por que aparecer.
3. **Aviso de contrabarra — NÃO exercitado**, pelo mesmo motivo: o `.flatdropignore` daquele projeto
   não tem nenhuma linha com `\`.

**O que falta, e é o gesto de cinco minutos:** num `.flatdropignore` de teste, pôr uma linha com `\`
e abrir o editor (o aviso deve trazer arquivo e linha; corrigir para `/` e reabrir: sem aviso), e
escrever uma regra depois do marcador de fechamento e salvar (deve perguntar antes de mover o bloco
para o fim). No mesmo passo, o smoke da wo0045: salvar sem mexer em nada e conferir que o arquivo
**não** ganhou linha em branco no fim; duplicar o bloco à mão e conferir que o salvamento **recusa**
com mensagem e não escreve nada.

> **Por que os dois que faltam não são «quase o mesmo teste»:** os três caminhos são independentes
> no código — o rótulo vem de `source()`, o aviso vem do parser de padrões e o `askyesno` vem do
> salvamento. Ver um funcionar não diz nada sobre os outros dois.
```

## Edicao 6 — `meta/STATUS.md` · o item 1 do backlog encolhe

**Ancora** (uma linha):

```
1. **Validar na tela os três comportamentos novos** (seção «Pendente de validação visual»).
```

**Substituir por:**

```
1. **Fechar a validação visual** — 2 dos 3 comportamentos foram confirmados em 27/08 (ver a seção
   «Validação visual no Windows»). Faltam o **aviso de contrabarra** e o **`askyesno` de regra depois
   do bloco**, que precisam de um `.flatdropignore` de teste montado de propósito.
```

## Edicao 7 — `meta/STATUS.md` · o numero de linhas do DECISIONS, medido

**Ancora** (duas linhas — a segunda continua a frase):

```
3. **Arquivar o `meta/DECISIONS.md`** em `DECISIONS-archive.md`. O arquivo passou de **69 KB e
   1.400 linhas**, contra o teto de ~700 que agora está escrito no cabeçalho dele (wo0061). Precisa
```

**Substituir por:**

```
3. **Arquivar o `meta/DECISIONS.md`** em `DECISIONS-archive.md`. O arquivo tem **69 KB e 1.124
   linhas** (medido em 27/08, `wc -l`), contra o teto de ~700 que agora está escrito no cabeçalho dele (wo0061). Precisa
```

> **1.400 era estimativa; 1.124 e `wc -l`.** O executor ja tinha reportado a divergencia na wo0062
> (ele mediu ~1085 no momento anterior ao commit) e nao corrigiu por conta, como manda a regra. A
> mesma correcao vai no `DECISIONS.md` pela Edicao 8.

## Edicao 8 — `meta/DECISIONS.md` · o mesmo numero, no cabecalho

**Ancora** (uma linha):

```
já passou de 1.400, e o arquivamento está no backlog do `STATUS`.
```

**Substituir por:**

```
tem **1.124 linhas** (medido em 2026-08-27), e o arquivamento está no backlog do `STATUS`.
```

## Edicao 9 — `meta/STATUS.md` · o item 8 do backlog fecha

**Ancora** (quatro linhas, extraidas por script):

```
8. **Passada de diff sobre o `meta/workorders/_TEMPLATE.md`.** A redação dele foi escrita daqui
   (wo0060) enquanto o pacote estava fora do mount; o pacote voltou, e vale conferir se o kit tem
   formulação melhor. Barato.

```

**Substituir por:**

```
8. **~~Passada de diff sobre o `meta/workorders/_TEMPLATE.md`~~ — FEITA em 27/08 (wo0063).** O
   pacote voltou ao mount e a comparação rendeu três adoções: as seções **«Inventário»** e
   **«Medição prévia»**, e o parágrafo *«afirmação sobre artefato legível não é opinião, é
   leitura»*. Os dois blocos que este projeto escreveu sozinho (extrair âncora por script; a âncora
   cobre o que o texto novo torna redundante) **não existem no kit** e ficaram — voltam ao KCM na
   próxima carta.
```

## Edicao 10 — `meta/STATUS.md` · a «Ultima conversa»

**Ancora** (quatro linhas):

```
**2026-08-27** — o merge do KCM v1.120.0 fechou nas quatro fases (wo0054 a wo0061); o `CEREBRO.md`,
o `CLAUDE.md`, as duas skills, as Instruções e os 12 modelos estão alinhados com o kit. **Onde
parou:** nada em curso. **Próximo passo óbvio:** a validação visual no Windows, que é o item 1 do
backlog e a única coisa entregue desde a 0.15.0 que ninguém viu na tela.
```

**Substituir por:**

```
**2026-08-27** — o merge do KCM v1.120.0 fechou (wo0054–wo0061), o desvio do push foi revogado
(DEC-033, wo0062) e a última pendência do merge — a passada de diff no modelo de WO — fechou na
wo0063. **Onde parou:** nada em curso; o kit está inteiro e o produto não anda desde 25/08.
**Próximo passo óbvio:** decidir *arquivo novo em pasta curada entra ou fica fora?* — é a análise
mais antiga em aberto (28/07) e destrava o item 2 do backlog e a Fase 2 do ROADMAP.
```

---

## Fora de escopo

- **Os itens 2, 4, 5 e 7 do backlog** — parqueados por decisão do autor em 27/08.
- **Arquivar o `DECISIONS.md`** (item 3) — continua no backlog; precisa do critério de corte.
- Nada em `flatdrop/`, nada em `.claude/`.

## Armadilhas desta WO

- **A âncora da Edição 5 tem 18 linhas** (a seção de validação visual inteira) e a da 9 tem quatro.
  Foram extraídas por script; se alguma não casar, o `STATUS.md` mudou depois de 27/08 12:47 —
  **PARE e reporte**.
- A Edição 4 tem uma **contrabarra literal** dentro da âncora (`\n nao casa`). Copie como está.
- O `meta/workorders/_TEMPLATE.md` é **ASCII sem acento**; os textos das Edições 1 a 4 já vêm assim
  (vieram do modelo do kit, que segue a mesma convenção). As Edições 5 a 10 são em `STATUS`/
  `DECISIONS`, que usam acento normalmente.
- **O log do dia:** confira se existe antes de escrever. Ver o aviso no cabeçalho.

---

## Depois de aplicar — conferência antes do commit

- [ ] `git diff` mostra exatamente: `meta/workorders/_TEMPLATE.md`, `meta/STATUS.md`,
      `meta/DECISIONS.md` — **mais `logs/2026-08-27.md`**, criado ou acrescido. *(«está lá?»)*
- [ ] `grep -c "^## Inventario" meta/workorders/_TEMPLATE.md` → **1**; `grep -c "^## Medicao previa"
      meta/workorders/_TEMPLATE.md` → **1**. *(«está lá?»)*
- [ ] `grep -c "1.400" meta/STATUS.md meta/DECISIONS.md` → **0 nos dois**. *(«está lá?»)*
- [ ] **Este responde «presta?»:** abra o `meta/workorders/_TEMPLATE.md` e confirme que os dois
      blocos NOSSOS continuam lá — o que manda extrair a âncora por script e o que diz que a âncora
      cobre o que o texto novo torna redundante. O modelo do kit **não os tem**; se sumiram, alguma
      edição substituiu em vez de inserir. *(Comando de apoio:
      `grep -c "Extraia a ancora do arquivo" meta/workorders/_TEMPLATE.md` → **1**.)*
- [ ] `python -m pytest -q` → **122**, sem mudança (WO só de doc).
- [ ] **Havia 1 arquivo não rastreado** no manifesto das 12:47. Rode `git status --porcelain` e
      **diga qual é** no relatório — se for o log do dia, entra no `git add`; se for outra coisa,
      só reporte, não commite por conta.
- [ ] **Invariante DEC-020:** nada em `flatdrop/`.

## Relatório de aplicação *(quem aplica preenche ao terminar)*

O que foi feito · o que fugiu do texto literal · os números crus · **qual dos dois casos ocorreu com
o log do dia** · **qual era o arquivo não rastreado** · o commit · o push (feito sem perguntar, caso
verde — DEC-033). Grave o MESMO relatório em `../AAMMDD-HHMM-code-flatdrop.txt`.

## Commit — blocos separados, mensagem SEM acento

```
git add meta\workorders\_TEMPLATE.md meta\STATUS.md meta\DECISIONS.md logs\2026-08-27.md meta\workorders\260827-wo0063-fecha-merge-e-validacao.md
```

```
git commit -m "docs(meta): fechar a ultima pendencia do merge e registrar a validacao visual" -m "O modelo de WO ganha as secoes Inventario e Medicao previa e o paragrafo sobre afirmacao a partir de artefato legivel, vindos do pacote v1.120.0; os dois blocos que este projeto escreveu sozinho ficam, porque o kit nao os tem. Validacao visual: 1 de 3 confirmado por print do dono (rotulo travada manual), os outros dois nao foram exercitados por falta de regra com contrabarra e de regra depois do bloco. Corrige 1.400 para 1.124 linhas do DECISIONS, medido com wc -l, em dois lugares."
```

```
git push
```
