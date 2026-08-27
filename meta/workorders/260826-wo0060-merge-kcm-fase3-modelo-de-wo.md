# WO 0060 — merge do KCM v1.120.0, fase 3 (parcial): o modelo de WO aprende com as sete ultimas

> **Tipo:** REGISTRO — `meta/workorders/_TEMPLATE.md`, `meta/IDEAS.md`, `meta/STATUS.md`.
> Nao toca codigo, nao toca `.claude/`.
> **Config sugerida:** modelo intermediario, `/effort` baixo. Seis edicoes, ancoras curtas.
> **Pre-requisito:** wo0059 aplicada e empurrada (`e9099b5`), **122 testes verdes**, arvore limpa.
> **Base:** o que as wo0053 a wo0059 ensinaram, medido nos relatorios de aplicacao; e os nomes de
> campo (`Ancoras lidas em`, `Proximo comando`, "tres campos por passo de verificacao") registrados
> na comparacao do pacote v1.120.0 feita em 25/08.
> **Ancoras lidas em:** *(as seis edicoes foram GERADAS por script a partir dos arquivos vivos do
> mount de 2026-08-26 19:46 — nenhum trecho de ancora foi digitado)*
> - `meta/workorders/_TEMPLATE.md` — linhas do cabecalho («Base» e «Depende de»), o bloco «Ancora»
>   da Edicao 1 do modelo, e as duas primeiras linhas do checklist.
> - `meta/IDEAS.md` — a nota de Foco (linhas 63-70) e o primeiro item de «Ativas».
> - `meta/STATUS.md` — a linha 127, do fechamento do CEREBRO.
> **Idempotencia:** procure `Ancoras lidas em`, `Extraia a ancora do arquivo` e `Carta 04 ao KCM`.
> Se ja existirem, **PULE** e diga no relatorio.
> **Proximo comando:** nao ha — os 11 modelos restantes dependem de o pacote voltar ao mount.

> **Canal dos meta neste ciclo = CODE** (`workorders/_TEMPLATE.md`, `IDEAS`, `STATUS`).

---

## 1. Por que

**O pacote saiu do mount de novo.** Conferido na listagem de 2026-08-26 19:46: nenhum
`__template-update` presente. Dos 12 modelos da fase 3, **11 dependem do pacote** — e o unico que
nao depende e este, o modelo de WO, porque o que ele precisa aprender **nao esta no pacote: esta
nos nossos proprios relatorios de aplicacao das ultimas sete WOs.**

Tres licoes, todas medidas, todas com o caso registrado:

1. **Ancora se extrai, nao se digita.** Desde a wo0056, um script le o trecho vivo e o cola na WO,
   e outro confere que cada ancora ainda casa. **Nenhuma ancora falhou desde entao** — contra
   varios «desvios de posicionamento» antes disso.
2. **A ancora tem de cobrir o que o texto novo torna redundante.** Na wo0058, uma ancora de uma
   linha veio com um substituto que reescrevia cinco: quem aplicou teve de decidir sozinho apagar
   as quatro orfas. Decisao que uma WO nao deveria delegar.
3. **Numero de conferencia e medido DEPOIS de fechar as edicoes, contando o que a propria WO
   acrescenta.** Cinco WOs seguidas erraram isso, e a ultima delas — a wo0059 — errou de um jeito
   novo e instrutivo: o checklist previa **2** ocorrencias de «sess» e o executor mediu **3**,
   porque a Edicao 1 da propria WO introduziu a terceira, num texto que eu escrevi depois de medir.
   O executor nao consertou, reportou. Certo.

**A redacao destas tres regras e NOSSA, nao copia do kit.** Os nomes dos campos (`Ancoras lidas
em`, `Proximo comando`, "tres campos por passo de verificacao") foram mantidos iguais aos do pacote
para que o proximo merge encontre o mesmo vocabulario e nao proponha duplicata. **Quando o pacote
voltar, cabe uma passada de diff** sobre este arquivo — pode haver redacao melhor la, e isso fica
registrado como pendencia no STATUS.

**Junto vai uma pendencia que a wo0059 criou.** A secao «Correspondencia entre projetos», que
entrou naquela WO, diz que *o que fica pendente do outro lado e seu, nao dele*: carta enviada e nao
respondida vira item **com gatilho**, senao o projeto trava sem ninguem perceber. A carta 04 esta
nesse estado desde 26/08. A Edicao 5 lhe da o gatilho.

---

## Edicao 1 — `meta/workorders/_TEMPLATE.md` · dois campos novos no cabecalho

**Ancora**:

```
> **Base:** a decisao, a analise ou a conversa que originou.
> **Depende de:** WOs que precisam estar aplicadas antes — ou apague a linha.
```

**Substituir por:**

```
> **Base:** a decisao, a analise ou a conversa que originou.
> **Depende de:** WOs que precisam estar aplicadas antes — ou apague a linha.
> **Ancoras lidas em:** *(obrigatorio)* de onde saiu cada ancora — arquivo e trecho — LIDOS NESTE
> turno. Nao vale "li o arquivo": diga a primeira linha de cada ancora, ou diga que o script as
> extraiu. **Quem aplica pode recusar a WO se este campo vier vazio:** quem escreveu a WO e quem
> tem o vies, e a conferencia e de quem aplica justamente por isso.
> **Proximo comando:** a linha `/apply-wo ...` da PROXIMA WO, crua e sozinha, ou "nao ha".
```

## Edicao 2 — `meta/workorders/_TEMPLATE.md` · como se faz uma ancora

**Ancora**:

```
**Ancora** *(diga ONDE fica: secao, funcao, item — nunca numero de linha)*:

```
[trecho literal e unico do arquivo vivo, copiado sem reformatar]
```
```

**Substituir por:**

```
**Ancora** *(diga ONDE fica: secao, funcao, item — nunca numero de linha)*:

```
[trecho literal e unico do arquivo vivo, copiado sem reformatar]
```

> **Extraia a ancora do arquivo, nao a digite.** Um script que le o trecho vivo e o cola aqui erra
> zero; a mao, erra em quebra de linha, acento e barra invertida. Depois de montar a WO, rode o
> mesmo script no sentido inverso: cada ancora tem de ser encontrada, literal, no arquivo vivo.
> **A ancora precisa cobrir tudo o que o texto novo torna redundante.** Ancora de uma linha so e
> segura quando o substituto fala so daquela linha; se o texto novo reescreve o paragrafo, a
> ancora e o paragrafo. Senao sobram linhas orfas dizendo em versao velha o que a nova ja diz — e
> quem aplica tem de decidir sozinho apaga-las, que e decisao que uma WO nao deveria delegar.
```

## Edicao 3 — `meta/workorders/_TEMPLATE.md` · o que todo passo de conferencia diz

**Ancora**:

```
- [ ] `git diff` mostra **exatamente** os arquivos previstos, e nada alem.
- [ ] [Conferencia de forma especifica desta WO — ex.: "a entrada nova ficou dentro da secao certa".]
```

**Substituir por:**

```
- [ ] `git diff` mostra **exatamente** os arquivos previstos, e nada alem.
- [ ] [Conferencia de forma especifica desta WO — ex.: "a entrada nova ficou dentro da secao certa".]

> **Todo passo de conferencia diz TRES coisas:** quem executa (voce ou o autor), o numero cru
> esperado, e **qual das duas perguntas ele responde** — *"esta la?"* (existencia) ou *"presta?"*
> (aptidao). Verde de existencia lido como verde de aptidao ja passou por aqui: contar arquivo nao
> abre arquivo.
>
> **Numero de conferencia e MEDIDO no texto final da WO, nunca estimado antes dele.** Cinco WOs
> seguidas erraram contagem por isso — `118` em tres lugares quando dois eram estado e um era
> registro datado; "16 bullets" que eram 18; `grep -> 0` num arquivo onde o proprio texto novo
> citava o termo; "18 linhas de tabela" que eram 18 mas por outro motivo; "2 ocorrencias de sess"
> que viraram 3 porque a propria WO introduziu a terceira. Meca DEPOIS de fechar as edicoes,
> contando tambem **o que a WO acrescenta**. Onde as ancoras ja saem por script, as contagens saem
> do mesmo script.
>
> **`grep` casa por LINHA.** Frase quebrada em duas linhas devolve zero, e zero vira "nao existe"
> na leitura seguinte. Quando o termo pode estar quebrado, procure a palavra mais rara dele.
>
> **A propria WO entra no `git add`** — ela e o registro de por que o commit tem essa forma.
```

## Edicao 4 — `meta/IDEAS.md` · a nota de Foco

**Ancora**:

```
> **Foco (2026-08-23):** a 0.15.0 fechou o único bug aberto e o repo ficou 20 dias parado
> (`8913a39`, 02/08). A frente atual **não é código do produto**: é a **carta 01 do KCM sobre o
> formato do `_MANIFEST`** — o nome plano declarado na tabela não existe no mount para dotfile e
> nome com ponto interno (medido: 3 de 38 aqui, 11 de 109 lá), e falta `mtime` por arquivo. A
> análise está em `meta/analises/260823-ANALISE-formato-do-manifesto.md`, «Em discussão», e para
> num ponto de decisão do autor. Em paralelo, a **wo0050** completa a linha de git do manifesto
> (`behind` e «sem upstream»), que já tinha o `ahead` desde a wo0048. Seguem esperando decisão do
> autor, sem prazo: o gerador (`pasta/*` + `!mantido`) e a multi-raiz na GUI.
```

**Substituir por:**

```
> **Foco (2026-08-26):** o merge do KCM **v1.120.0** consumiu a semana e está na última fatia — o
> `CEREBRO.md` fechou na wo0059; sobram os **12 modelos** do pacote (fase 3), que é a parte mais
> mecânica. Do ciclo anterior, a carta 01 do KCM está inteiramente respondida: item 1 entregue
> (DEC-030), item 3 entregue (wo0050) e item 2 **recusado com contraproposta entregue** (DEC-031).
> Seguem esperando **decisão do autor, sem prazo**: o gerador (`pasta/*` + `!mantido`) e a
> multi-raiz na GUI. E segue **sem resposta** a nossa carta 04 — ver o item com gatilho abaixo.
```

## Edicao 5 — `meta/IDEAS.md` · a carta 04 vira item com gatilho

**Ancora**:

```
- **O formato do `_MANIFEST` promete um nome que não existe no mount.** Carta 01 do KCM
```

**Inserir IMEDIATAMENTE ANTES:**

```
- **Carta 04 ao KCM, enviada em 26/08 e ainda sem resposta.** Ela devolve que a regra «o relatório
  lidera, sempre» só vale numa direção: quando o dono commita entre relatórios — o que aqui é
  rotina —, o manifesto fica com o commit mais novo, e a regra manda concluir que a cópia está
  atrasada justamente quando ela é a única em dia. A proposta é trocar a suposição por medição:
  **compare os dois carimbos, o mais recente vence**. **Gatilho:** se não vier resposta até
  **2026-09-09** (duas semanas), adotamos a regra por conta neste projeto, escrevemos a linha no
  `CEREBRO.md` e registramos a divergência como desvio — sem esperar mais. *(Registrado por causa
  da seção «Correspondência entre projetos», que entrou na wo0059: o que fica pendente do outro
  lado é nosso, não dele; carta esperando sem gatilho é como o projeto trava sem ninguém perceber.)*
- **O formato do `_MANIFEST` promete um nome que não existe no mount.** Carta 01 do KCM
```

## Edicao 6 — `meta/STATUS.md` · o estado da fase 3

**Ancora** (uma linha):

```
   **O merge do CEREBRO está fechado. Fase 3 (a fazer):** os 12 modelos do pacote.
```

**Substituir por:**

```
   **O merge do CEREBRO está fechado. Fase 3 (parcial, wo0060):** o `meta/workorders/_TEMPLATE.md`
   absorveu o que sete WOs seguidas ensinaram — campos «Âncoras lidas em» e «Próximo comando», a
   regra de extrair âncora por script e de a âncora cobrir o que o texto novo torna redundante, e
   os três campos de todo passo de conferência. **Escrito daqui, não copiado:** o pacote saiu do
   mount antes desta fase, então a redação é nossa e os nomes dos campos vieram do que ficou
   registrado na comparação de 25/08. **Falta:** os 11 modelos restantes e uma passada de diff
   sobre o `_TEMPLATE.md` de WO quando o pacote voltar.
```

---

## Fora de escopo

- **Os 11 modelos restantes da fase 3** (`SPEC`, `CONTEXT`, `STATUS`, `DECISIONS`, `CHANGELOG`,
  `IDEAS`, `LOG-TEMPLATE`, `ROADMAP`, `GLOSSARY`, `HISTORY`, `README` de `meta/`, e o
  `analises/_TEMPLATE.md`): **dependem do pacote**, que não está no mount. Não os toque de memória.
- **Nenhuma reescrita do `_TEMPLATE.md` além das três lições.** O restante do modelo é nosso e está
  em uso há 60 WOs.
- Nada de `.claude/`, nada de `flatdrop/`.

## Armadilhas desta WO

- A Edição 2 insere um bloco de citação `>` **depois** de um bloco de código com cercas ```. Confira
  que a cerca de fechamento continua fechando o bloco certo — se o `>` entrar dentro da cerca, ele
  vira texto de exemplo em vez de instrução.
- A Edição 4 tem âncora de **oito linhas** (a nota de Foco inteira), de propósito: o texto novo
  substitui a nota toda. É a lição da wo0058 aplicada aqui.
- O `meta/workorders/_TEMPLATE.md` é **ASCII sem acento** por convenção do arquivo (ele é lido pelo
  Code em terminal). **Mantenha o padrão:** os textos novos das Edições 1, 2 e 3 já vêm sem acento.
  As Edições 4, 5 e 6 são em `IDEAS`/`STATUS`, que usam acento normalmente.

---

## Depois de aplicar — conferência antes do commit

- [ ] `git diff` mostra exatamente: `meta/workorders/_TEMPLATE.md`, `meta/IDEAS.md`,
      `meta/STATUS.md`. *(Quem executa: você. Pergunta que responde: «está lá?».)*
- [ ] `grep -c "Ancoras lidas em" meta/workorders/_TEMPLATE.md` → **1**. *(«está lá?»)*
- [ ] `grep -c "Carta 04 ao KCM" meta/IDEAS.md` → **1**. *(«está lá?»)*
- [ ] **Nenhum acento entrou no modelo de WO** — este responde «presta?», não «está lá?»:
      `python -c "s=open('meta/workorders/_TEMPLATE.md',encoding='utf-8').read();print(sum(1 for c in s if ord(c)>127))"`
      → **38 antes desta WO** e **46 depois** (medido em 26/08: hoje são 25 travessões `—` e 13
      pontos médios `·`, nenhum acento; os textos novos das Edições 1 a 3 acrescentam **8
      travessões** e nada mais). Rode ANTES e DEPOIS e reporte os dois números crus. Se o segundo
      não for 46, entrou caractere que não deveria — **reporte, não conserte**. *(Número medido no
      texto final desta WO, contando o que ela própria acrescenta: é o erro que a wo0059 cometeu.)*
- [ ] `python -m pytest -q` → **122**, sem mudança (WO só de doc).
- [ ] **Invariante DEC-020:** nada em `flatdrop/`.

## Relatório de aplicação *(quem aplica preenche ao terminar)*

O que foi feito · o que fugiu do texto literal · os números crus (inclusive os DOIS da conferência
de não-ASCII) · o commit · **o push, com o resultado real**, escrito DEPOIS de o push estar
resolvido. Grave o MESMO relatório em `../AAMMDD-HHMM-code-flatdrop.txt`.

## Commit — blocos separados, mensagem SEM acento

```
git add meta\workorders\_TEMPLATE.md meta\IDEAS.md meta\STATUS.md meta\workorders\260826-wo0060-merge-kcm-fase3-modelo-de-wo.md
```

```
git commit -m "chore(kit): modelo de WO absorve o que as sete ultimas ensinaram" -m "Entram os campos Ancoras lidas em e Proximo comando, a regra de extrair ancora por script e de a ancora cobrir o que o texto novo torna redundante, e os tres campos de todo passo de conferencia (quem executa, numero cru, e se responde esta la ou presta). Numero de conferencia passa a ser medido depois de fechar as edicoes, contando o que a propria WO acrescenta - cinco WOs seguidas erraram isso. A carta 04 ao KCM ganha gatilho de 09-09. Redacao nossa: o pacote saiu do mount, entao os 11 modelos restantes ficam pendentes."
```

```
git push
```
