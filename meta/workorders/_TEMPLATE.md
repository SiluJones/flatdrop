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
> **Ancoras lidas em:** *(obrigatorio)* de onde saiu cada ancora — arquivo e trecho — LIDOS NESTE
> turno. Nao vale "li o arquivo": diga a primeira linha de cada ancora, ou diga que o script as
> extraiu. **Quem aplica pode recusar a WO se este campo vier vazio:** quem escreveu a WO e quem
> tem o vies, e a conferencia e de quem aplica justamente por isso.
> **Afirmacao sobre artefato legivel nao e opiniao, e leitura** — o que uma ferramenta faz, o que um
> simbolo contem, em que estado esta o mount. Nao cite simbolo, caminho ou capacidade de ferramenta
> que voce nao leu NESTE turno; dizer "nao li" nao autoriza escrever a WO em cima.
> **Proximo comando:** a linha `/apply-wo ...` da PROXIMA WO, crua e sozinha, ou "nao ha".
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

## Medicao previa *(so quando houver; nao e edicao)*

[So quando esta WO depender de um numero que a raia de planejamento nao pode ler. Diga O QUE contar e o
comando sugerido; peca de volta o valor e o comando que o produziu, sem interpretacao. Isto NAO tem ancora,
NAO tem commit e NAO muda arquivo — se a medicao contrariar o que a WO assume, PARE antes de editar e relate.]

## Armadilhas desta WO

[So quando houver. O que ja deu errado antes neste mesmo lugar e o que quem aplica pode quebrar sem
perceber: ancora que aparece duas vezes, arquivo com fim de linha CRLF (ancora multi-linha colada com
\n nao casa), bloco gerado que sera reescrito, numero de check ja usado. Contra o CRLF a saida e
sempre a mesma: ancora de UMA linha nao tem quebra dentro, entao o fim de linha nao morde — para
inserir varias linhas, ancore em UMA so e diga se o texto novo entra antes ou depois dela.]

---

## Depois de aplicar — conferencia antes do commit

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
