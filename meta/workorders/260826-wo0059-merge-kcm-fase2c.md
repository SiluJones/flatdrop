# WO 0059 — merge do KCM v1.120.0, fase 2c: as tres secoes novas, e o CEREBRO fecha

> **Tipo:** REGISTRO/comportamento — `meta/CEREBRO.md`, `meta/IDEAS.md`, `meta/STATUS.md`.
> Nao toca codigo, nao toca `.claude/`.
> **Config sugerida:** modelo intermediario, `/effort` medio. A Edicao 2 cola um bloco grande com
> cercas ``` dentro — atencao a isso, nao a julgamento.
> **Pre-requisito:** wo0058 aplicada e empurrada (`9cea715`), **122 testes verdes**, arvore limpa.
> **Base:** `CEREBRO__template-update.md` (kit v1.120.0), secoes «Tecnicas especificas deste
> projeto», «Sonda e exploracao — o par que produz evidencia» e «Correspondencia entre projetos»,
> mais cinco deltas menores.
> **Ancoras lidas em:** *(as doze edicoes foram GERADAS por script a partir dos arquivos vivos do
> mount de 2026-08-26 16:07 — nenhum trecho foi digitado, exceto os seis itens da Edicao 1, que
> sao conteudo NOVO deste projeto e nao copia de lugar nenhum)*
> - `meta/CEREBRO.md` — linhas 99, 101 e 160; as linhas do funil, do primeiro teste barato, do
>   «Se aparecerem no mount» e do «Nao inche»; o titulo `## Convenções` e o titulo
>   `## Medição delegada (...)`, usados como pontos de insercao.
> - `CEREBRO__template-update.md` — as tres secoes novas, lidas inteiras.
> - `meta/IDEAS.md` — primeiro item de «Feedback para o Kit».
> - `meta/STATUS.md` — linhas 121-125, o paragrafo da fase 2c.
> **Idempotencia:** procure `Sonda e exploração`, `Correspondência entre projetos` e `Técnicas
> específicas deste projeto`. Se ja existirem, **PULE** e diga no relatorio.
> **Proximo comando:** nao ha — a fase 3 (os 12 modelos) sai do chat depois desta aplicada.

> **Canal dos meta neste ciclo = CODE** (`CEREBRO`, `IDEAS`, `STATUS`).

---

## 1. Por que

Ultima fatia do `CEREBRO.md`. Depois desta WO, **o merge do CEREBRO esta fechado** e sobra so a
fase 3, que sao os 12 modelos do pacote.

**Tres secoes novas, e cada uma tem uso imediato aqui:**

- **«Tecnicas especificas deste projeto»** — o template a manda comecar **vazia**. A Edicao 1 a
  traz com **seis itens**, todos com caso registrado neste repositorio: a extracao de ancora por
  script (wo0056), o escopo da ancora (wo0058), a contagem medida e nao estimada (wo0055-0057), o
  bloqueio do classificador em `.claude/` (wo0054), o ASCII do console (wo0052/FIX-003) e a
  sanitizacao do upload (DEC-030). O criterio do proprio template e «escreva quando doer duas
  vezes» — os seis ja doeram. Comecar vazia seria fingir que o projeto nasceu hoje. **E o template
  garante que esta secao nunca sera sobrescrita por um update futuro.**
- **«Sonda e exploracao»** — este projeto ja usa o padrao sem ter nome para ele: as ultimas quatro
  WOs foram escritas com scripts descartaveis que mediram o mount (tamanho de secao, contagem de
  bullets, extracao de ancora) e devolveram numero com o comando ao lado. A secao nomeia isso,
  separa **exploracao** (produz hipotese) de **sonda** (produz evidencia), e traz o esqueleto de
  relatorio — inclusive a regra que ja esta na nossa tabela de gatilhos desde a fase 2b: *existencia
  nao e aptidao*.
- **«Correspondencia entre projetos»** — quatro cartas trocadas com o KCM. A secao confirma o que
  fizemos por instinto (contador unico e compartilhado; um assunto por carta; marcar de que lado
  vem cada afirmacao) e o que so acertamos depois do fato: **carta nao se versiona**. Vale ler o
  ultimo bullet: *o que fica pendente do outro lado e seu, nao dele* — carta enviada e nao
  respondida vira item com gatilho, senao o projeto trava sem ninguem perceber. **A carta 04 esta
  nesse estado agora.**

**E a varredura de «sessao» nao tinha acabado.** A fase 2b fechou em zero pelo padrao varrido
(`de cada sess|fim de sess|inicio de sess|toda sess`) — mas o padrao era estreito. Uma varredura
por `sess` sozinho, feita nesta rodada, achou **mais tres**: «Modelo do log de sessao» (linha 99),
«se repete entre sessoes» (linha 101) e «se a sessao mexeu em STATUS» (linha 160). As tres saem nas
Edicoes 4, 5 e 6. **A licao e do proprio kit** — *varra pelo fato, nao pela frase* — e ela vale
contra quem a escreve: eu montei o padrao a partir das ocorrencias que ja conhecia, e ele so achou
o que eu ja sabia que existia.

---

## Edicao 1 — `meta/CEREBRO.md` · secao nova «Tecnicas especificas deste projeto»

**Ancora**:

```
## Convenções
```

**Substituir por:**

```
## Técnicas específicas deste projeto

> **Esta seção é sua.** Tudo o mais neste arquivo é genérico e é substituído quando o kit evolui; aqui é onde mora o conhecimento operacional que só este projeto tem — a coordenada que não se mexe, a armadilha da ferramenta que já custou uma sessão, o jeito certo de nomear uma coisa daqui. **Um template-update nunca sobrescreve esta seção**: ele traz a moldura, você mantém o recheio.

Escreva aqui quando doer duas vezes: técnica que precisou ser explicada de novo é candidata. Uma linha por item, com o nome do lugar onde ela vale. Se um item virar regra geral do projeto, promova-o para o corpo do CEREBRO e deixe aqui só o caso particular.

- **Âncora de WO se extrai do arquivo, não se digita.** Um script lê o trecho vivo e o cola na WO; depois, outro confere que cada âncora ainda casa com o arquivo. Desde que isto passou a ser feito assim (wo0056), nenhuma âncora falhou na aplicação. Vale para qualquer edição em documento grande.
- **A âncora tem de cobrir tudo o que o texto novo reescreve.** Âncora de uma linha só é segura quando o substituto fala só daquela linha. Na wo0058, o texto novo cobria um parágrafo de cinco linhas e a âncora pegava só a primeira — as outras quatro sobraram órfãs, e quem aplicou teve de decidir sozinho apagá-las. Antes de fechar uma edição, pergunte: *o que estou escrevendo torna alguma linha vizinha redundante?*
- **Número de conferência é medido no texto FINAL da WO, nunca estimado antes.** Três WOs seguidas erraram contagem por isso (`118` em três lugares, «16 bullets» que eram 18, `grep → 0` num arquivo onde o próprio texto novo citava o termo). Onde as âncoras já saem por script, as contagens saem do mesmo script.
- **Edição sob `.claude/` não vai por WO.** O classificador de permissão do Claude Code bloqueia o executor de alterar a própria configuração, e ele faz certo em não contornar. Esses arquivos o chat entrega INTEIROS, para baixar e substituir; a WO só os menciona no `git add`.
- **`.bat` no Windows é ASCII, e o console também.** Glifo fora do ASCII derruba a saída da CLI por `UnicodeEncodeError`: `↳` e `⚠` não codificam em cp1252, cp850 nem cp437; `•` e `…` não codificam em cp850, que é o CMD em português. Acento sobrevive em cp1252 e cp850, e morre em cp437 (FIX-003, wo0052).
- **O upload do Projeto renomeia dotfile e nome com ponto interno** (`.gitignore` → `_gitignore`, `settings.local.json` → `settings_local.json`). Regra observada, não documentada pela Anthropic: é previsão, e o manifesto a rotula como tal (DEC-030).

## Convenções
```

> **A moldura e do template; os seis itens sao NOSSOS.** O template manda comecar vazia («o primeiro item entra
> na primeira vez que uma tecnica precisar ser repetida»). Aqui seis ja doeram duas vezes ou mais, e cada um tem
> o caso registrado: wo0052 (glifos), wo0054 (classificador), wo0055-0058 (ancora e contagem), DEC-030 (upload).
> Comecar vazia seria fingir que o projeto nasceu hoje.

## Edicao 2 — `meta/CEREBRO.md` · secao nova «Sonda e exploracao»

**Ancora**:

```
## Medição delegada (quem tem o disco mede, quem tem o contexto decide)
```

**Substituir por:**

```
## Sonda e exploração — o par que produz evidência

A medição delegada acima responde a pergunta que alguém já soube fazer. Quando o material é grande demais para caber numa conversa, ou quando ninguém sabe ainda qual é a pergunta, ela não basta — e o que falta são **dois** artefatos, não um:

- **Sonda** — script **determinístico** que a raia de planejamento escreve, a de execução roda sobre os dados, e que devolve um relatório pequeno. Responde perguntas que alguém já sabia fazer. **Produz evidência.** É reexecutável: rodar duas vezes (antes/depois de uma mudança) e comparar os dois relatórios é o que prova que a mudança fez o que prometia.
- **Exploração** — passada de leitura **sem hipótese prévia**, feita pela raia de execução, que devolve **candidatos a checagem**. Descobre as perguntas que ninguém fez. **Produz hipótese.**

**Funil:** `exploração` (levanta a pergunta) → `sonda` (mede) → **`instrumento`** (mede sempre) → `análise` (raciocina) → ordem de trabalho (muda). **Exploração e sonda não são ordem de trabalho:** não têm âncora, não têm commit, não mudam o repositório. O relatório é a única saída.

**O terceiro estado: sonda que amadurece vira instrumento — e aí passa a dar veredito, de propósito.** Script que ninguém roda sozinho, sem teste, tem vida curta. Quando a mesma medição vale para sempre, ela sai do descartável e entra no produto: **versionada, com teste, e devolvendo código de erro quando o que ela mede está errado.** Aí é comando entregue, não sonda — e a proibição de veredito **deixa de valer**, porque instrumento que não reprova ninguém roda.
- **Gatilho da promoção: a sonda foi rodada uma SEGUNDA vez para comparar antes/depois.** A partir daí ela não é mais descartável — é instrumento sem teste, e o custo de deixá-la assim só cresce.
- **A promoção exige o oposto do descarte.** A sonda vive fora do que sobe ao Projeto; o instrumento é versionado, testado e citado nas decisões. Confundir os dois nas duas direções custa: script frágil virando dependência, ou medição madura sendo reescrita do zero a cada vez.

**Três propriedades do relatório — as três juntas, ou o relatório vira lixo:**
1. **Tabela e contagens, nunca prosa.** Número solto é contestável; número ao lado do comando que o produziu, não.
2. **O que NÃO foi olhado é declarado — e qual das duas perguntas o instrumento não responde, também.** Sem a primeira metade, ausência vira zero na leitura seguinte, e zero é um fato enquanto ausência não é: seção que não pôde ser medida sai marcada como não conferida, **nunca omitida**. A segunda metade é a que quase ninguém escreve: toda conferência responde a *«está lá?»* ou a *«presta?»*, e a que ela **não** responde precisa aparecer no relatório com o mesmo destaque do que não foi olhado — senão o verde de uma vira leitura de verde da outra. Costuma custar pouco fechar a lacuna: ler 30 bytes de cabeçalho respondeu «presta?» por 45 arquivos de uma vez, sem dependência nenhuma.
3. **Nada truncado em silêncio, e amostra nunca se apresenta como cobertura.** São dois defeitos diferentes: truncar esconde o FIM da lista (lista cortada mostra o TOTAL); amostrar esconde que a lista nem foi lida inteira. `os 3 primeiros` num relatório sem a palavra «amostra» vira, na leitura seguinte, «conferi tudo» — e ninguém volta para checar. Se olhou uma parte, diga **quantos de quantos**.

**Nenhuma das duas dá veredito, e a razão é a que importa: teste de conformidade não detecta que a especificação está errada.** A sonda relata o fato e **não nomeia a causa** — ausências de origens diferentes produzem o mesmo sintoma. Decidir é da raia de planejamento, com o dono.
- **Existência não é aptidão.** «Está no disco?» e «o que está no disco presta?» são perguntas diferentes, e instrumento que só sabe contar responde sempre a primeira. Caso real: um relatório verde em tudo — arquivos existem, extensão certa, índice bate — sobre imagens destruídas por dentro, porque **nenhum instrumento abriu uma imagem**. Ao escrever uma sonda, pergunte o que ela NÃO abre.
- **A exploração não parte da lista de checagens da sonda.** Se ela só olhar onde a sonda já olha, ela só acha o que a sonda já acharia. É a mesma regra do inventário — a lista sai do artefato, não de quem já a escreveu — vista uma camada acima.
- **Todo achado vem com o comando que o reproduz.** Achado sem forma de reproduzir não entra: vai para «observações descartadas», com o motivo. Número contado de cabeça não vale.

**O esqueleto do relatório — o que sobreviveu a dezenas de execuções nos dois projetos que o escreveram:**

```
# SONDA — <assunto>                     <- o nome diz o QUE, não o quando
- Gerado em: <data>  *(única linha não-determinística deste relatório)*
- Insumo: <caminho> · <tamanho> · sha256 <hash> · mtime <data>
- Referência: <caminho> | nenhuma — as seções comparativas saem NÃO CONFERIDAS
> A sonda não dá veredito: ela conta, compara e imprime. Decidir é humano.

## ALARMES (N)
  N=0 -> «Nenhuma verificação falhou. ISSO NÃO QUER DIZER QUE ESTÁ CERTO —
        quer dizer que é coerente nos pontos medidos. Leia O QUE NÃO FOI OLHADO.»

## <seções do corpo>                    <- tabelas e contagens; lista longa mostra o TOTAL
  seção sem insumo -> **NÃO CONFERIDA**, nunca omitida

## O QUE NÃO FOI OLHADO
  - o que faltou NESTA execução (dinâmico)
  - o que esta sonda NUNCA olha (fixo, escrito uma vez e para sempre)
```

Três detalhes que só aparecem depois de usar: **(1)** marcar a data como a única linha não-determinística é o que torna dois relatórios diffáveis — sem isso, comparar antes/depois vira leitura à mão; **(2)** a lista fixa do «nunca olha» é mais valiosa que a dinâmica, porque é a que ninguém lembraria de escrever no dia; **(3)** o rodapé com contagem de alarmes em zero precisa negar a leitura fácil **na própria linha** — «zero alarmes» sem a negação ao lado vira «está certo» na conversa seguinte.

**Onde mora — e este é um padrão, não uma regra.** Por omissão, script e relatórios ficam **fora** do que sobe ao Projeto (workspace ao lado do repositório, ou pasta ignorada): são grandes, reexecutáveis, e o que importa deles é o que se extrai. Nome com **carimbo de tempo primeiro** (`AAMMDD-HHMM-EXPLORACAO.md`), para a pasta se ordenar sozinha. **Versionar em vez de descartar é uma escolha legítima, e tem um preço a pagar em voz alta:** ganha-se a comparação antes/depois (que só existe se os dois relatórios sobreviverem) e o tema no nome (`AAMMDD-SONDA-<tema>.md`, que se lê sem abrir); paga-se em repositório maior e no risco de o relatório velho ser lido como estado atual. Quem versiona, registra a escolha. O que sobe ao registro continua sendo o **extraído**: um número no `DECISIONS`, um candidato no `IDEAS`.

## Medição delegada (quem tem o disco mede, quem tem o contexto decide)
```

> **Entra logo ANTES da «Medicao delegada»** — nao depois: a propria secao abre dizendo «a medicao delegada
> ACIMA responde a pergunta que alguem ja soube fazer», entao ela precisa vir depois dela na leitura.
> **CUIDADO:** o bloco tem um exemplo de relatorio dentro de cercas ``` e, dentro dele, linhas que comecam com
> `## ` (`## ALARMES (N)`). Elas sao CONTEUDO do exemplo, nao titulos de secao. Cole o bloco inteiro sem
> interpretar essas linhas.

## Edicao 3 — `meta/CEREBRO.md` · secao nova «Correspondencia entre projetos»

**Ancora**:

```
## Medição delegada (quem tem o disco mede, quem tem o contexto decide)

```

**Substituir por:**

```
## Correspondência entre projetos — quando o interlocutor é outro assistente

Dois projetos com kits separados que dependem um do outro (um produz o dado, o outro consome; um gera o pacote, o outro renderiza) precisam **negociar um contrato**. O que trocam não é spec, não é análise, não é ordem de trabalho e não é bilhete: é **carta**, e ela tem regras próprias porque tem dois donos.

- **Nome:** `AAMMDD-<quem>-para-<quem>-NN-<assunto>.md`. O remetente e o destinatário no nome porque a mesma pasta guarda os dois sentidos.
- **O contador `NN` é ÚNICO e COMPARTILHADO pelos dois lados** — não um por remetente. Com duas séries, «respondendo à sua 7» vira ambíguo e ninguém sabe o que responde o quê. A carta nova é a **maior existente + 1**, contando as dos DOIS lados; confira a pasta antes de numerar, não confie na memória nem em número anotado em documento.
- **Uma carta, um assunto.** Carta que negocia três contratos ao mesmo tempo recebe uma resposta que aceita um e ignora dois, e o que foi ignorado não deixa rastro.
- **Diga de que lado está cada afirmação.** «O nosso lado já grava X» é fato do remetente; «vocês deveriam gravar Y» é pedido. Sem a marca, o destinatário lê pedido como fato e implementa contra uma premissa que nunca foi verdadeira.

**Correspondência é TRANSITÓRIA, e é aqui que ela custa caro.** A carta vive fora do repositório enquanto serve — chega como upload, é lida, e o que precisa sobreviver é **extraído** dela para os documentos duráveis: o acordo vira decisão registrada, o que não coube vira ideia com gatilho, o histórico vira uma linha no registro do projeto. **Versionar a correspondência cria uma segunda fonte de verdade que envelhece sozinha**: uma auditoria real achou três lacunas numa pasta de cartas versionadas, uma delas um dado de estado desatualizado que a leitura seguinte tratava como fato. O destino da carta depois de extraída é o arquivo morto, fora do projeto.
- **O que fica pendente do outro lado é seu, não dele.** Carta enviada e não respondida não é memória: vira item com gatilho no registro de ideias («se não vier resposta até X, decido sozinho por Y»). Esperar resposta sem gatilho é como o projeto trava sem ninguém perceber.

## Medição delegada (quem tem o disco mede, quem tem o contexto decide)

```

> Entra tambem antes da «Medicao delegada», DEPOIS da Edicao 2 — a ordem final fica: Sonda, Correspondencia,
> Medicao delegada. **Se a Edicao 2 nao tiver sido aplicada, esta ancora ainda casa** (o titulo continua unico);
> a ordem entre as duas novas e indiferente.

## Edicao 4 — `meta/CEREBRO.md` · a linha do LOG-TEMPLATE na tabela de artefatos

**Ancora**:

```
| `LOG-TEMPLATE.md` | Referência fixa | Modelo do log de sessão. Referência fixa — nunca substituído pelo conteúdo preenchido. |
```

**Substituir por:**

```
| `LOG-TEMPLATE.md` | Referência fixa | Modelo do log do dia. Referência fixa — nunca substituído pelo conteúdo preenchido. |
```

## Edicao 5 — `meta/CEREBRO.md` · a linha do GLOSSARY na mesma tabela

**Ancora**:

```
| `GLOSSARY.md` | Estável | OPCIONAL — termos próprios do projeto. Use quando há jargão que se repete entre sessões. |
```

**Substituir por:**

```
| `GLOSSARY.md` | Estável | OPCIONAL — termos próprios do projeto. Use quando há jargão que se repete entre conversas. |
```

## Edicao 6 — `meta/CEREBRO.md` · «se a sessao mexeu» vira «se o trabalho mexeu»

**Ancora**:

```
- Registra o que decorre do próprio trabalho: se a sessão mexeu em STATUS, decisões, ideias, etc., o assistente entrega esses arquivos atualizados — não espera o usuário pedir.
```

**Substituir por:**

```
- Registra o que decorre do próprio trabalho: se o trabalho mexeu em STATUS, decisões, ideias, etc., o assistente entrega esses arquivos atualizados — não espera o usuário pedir.
```

## Edicao 7 — `meta/CEREBRO.md` · o funil da analise passa a incluir sonda e exploracao

**Ancora**:

```
- **Funil:** análise → **WO** (`meta/workorders/`) → `DECISIONS.md`. Quando o trabalho é de produto, a análise pode virar **spec de feature** (`meta/specs/`, modelo em `meta/SPEC.md`) — a spec diz **o que** construir e quando está pronto; a WO diz **como aplicar**.
```

**Substituir por:**

```
- **Funil:** exploração/sonda (medem, não decidem) → análise → **WO** (`meta/workorders/`) → `DECISIONS.md`. Quando o trabalho é de produto, a análise pode virar **spec de feature** (`meta/specs/`, modelo em `meta/SPEC.md`) — a spec diz **o que** construir e quando está pronto; a WO diz **como aplicar**.
```

## Edicao 8 — `meta/CEREBRO.md` · o primeiro teste barato ganha a forma do template

**Ancora**:

```
- **Antes de escrever, dois testes baratos.** (1) **O QUÊ já está decidido?** Então isto é execução, não análise — vá para o trabalho, que já tem critério de aceite e armadilhas. (2) **Cabe em meia página de conversa?** Então é conversa. Cerimônia em cima de trivialidade é desperdício; análise é para a decisão cara de desfazer, cujo custo precisa estar à vista ANTES do compromisso.
```

**Substituir por:**

```
- **Antes de escrever, dois testes baratos.** (1) **Quem ainda decide?** O dono já decidiu o QUÊ? Então isto é execução, não análise — vá para o trabalho, que já tem critério de aceite e armadilhas. (2) **Cabe em meia página de conversa?** Então é conversa. Cerimônia em cima de trivialidade é desperdício; análise é para a decisão cara de desfazer, cujo custo precisa estar à vista ANTES do compromisso.
```

## Edicao 9 — `meta/CEREBRO.md` · o merge sabe somar, nao sabe subtrair

**Ancora**:

```
Se aparecerem no mount arquivos com sufixo `__template-update` junto de um `_UPDATE-MANIFEST.md`: são atualizações genéricas do próprio kit (propositalmente vazias do específico desta obra), não conteúdo novo do projeto. Para cada arquivo: compara com o vivo equivalente (o destino real está no manifesto) e **reporta** — (a) novidade útil que falta aqui, (b) choque com o que já existe (lado a lado, o usuário decide), (c) algo que este projeto tem e o template não cobre.
```

**Substituir por:**

```
Se aparecerem no mount arquivos com sufixo `__template-update` junto de um `_UPDATE-MANIFEST.md`: são atualizações genéricas do próprio kit (propositalmente vazias do específico desta obra), não conteúdo novo do projeto. Para cada arquivo: compara com o vivo equivalente (o destino real está no manifesto) e **reporta** — (a) novidade útil que falta aqui, (b) choque com o que já existe (lado a lado, o usuário decide), (c) algo que este projeto tem e o template não cobre.
**O merge sabe somar, não sabe subtrair — e por isso o manifesto traz duas seções que a comparação não produz.** (1) **Linhas revogadas:** o kit às vezes APAGA uma linha de propósito, e comparar arquivos só revela o que é novo — o texto antigo continua vivo no seu, invisível ao merge, dirigindo comportamento que já foi corrigido. Procure cada texto listado; se achar, remova, ou registre o desvio se este projeto tiver motivo para manter. (2) **Carimbo de modos:** o manifesto declara com quais modos o pacote foi gerado. Seção de um modo declarado como `nao` que ainda exista no seu arquivo é sobra de configuração antiga — **ou** o pacote foi gerado com o modo esquecido. O assistente **não tem como distinguir os dois casos**, então **reporta como choque com a seção citada e não remove sozinho**. Migrar de modo (ASU→Code, por exemplo) não limpa o CEREBRO já gerado: um CEREBRO gerado é arquivo, não função.
```

> Duas linhas onde havia uma. E a licao que este projeto pagou em 25/08: comparar os dois arquivos **nao produz**
> as linhas revogadas nem o carimbo de modos — as duas secoes que o manifesto traz de proposito. Sem elas, texto
> que o kit apagou continua vivo aqui e dirige o trabalho seguinte.

## Edicao 10 — `meta/CEREBRO.md` · principio sem gatilho nao dispara

**Ancora**:

```
- **Não inche.** Antes de acrescentar uma regra às Instruções, pergunte se ela cabe no CEREBRO. Só vai para as Instruções o que precisa ser lembrado em TODO turno.
```

**Substituir por:**

```
- **Princípio sem gatilho não dispara — e o remédio é oportunista, não uma auditoria.** Virtude é escrita no infinitivo («analisa antes de aceitar», «explica trade-offs») e não tem hora; gatilho é escrito com o **evento na frente** («quando o dono impõe uma restrição para evitar perda, proponha a forma mais barata de obter a mesma proteção») e dispara sozinho. Percorrer todos os princípios inventando gatilhos gera tabela longa que ninguém lê. **A política é outra: toda vez que um princípio falhar em campo, aquele princípio ganha o gatilho — com o evento real que o teria disparado, colhido do caso.** O caso é o que torna o gatilho específico; sem ele, você escreve outra virtude e acha que escreveu um gatilho.
- **Não inche.** Antes de acrescentar uma regra às Instruções, pergunte se ela cabe no CEREBRO. Só vai para as Instruções o que precisa ser lembrado em TODO turno.
```

> Bullet novo do template, inserido antes do «Nao inche» que ja existe. **Nao troque nenhum outro bullet desta
> secao:** os nossos «Teto» e «Teto por configuracao» estao adaptados a este projeto (sem ASU) e as versoes do
> template regrediriam a adaptacao.

## Edicao 11 — `meta/IDEAS.md` · a licao da ancora, em «Feedback para o Kit»

**Ancora** (uma linha):

```
- **O pacote v1.120.0 traz cinco bullets do «Refino das Instruções» dentro da seção «Bloco de fecho
```

**Inserir IMEDIATAMENTE ANTES:**

```
- **Âncora de uma linha só é segura quando o texto novo fala só daquela linha.** Medido em
  2026-08-26, na wo0058: a edição de registro tinha âncora de uma linha, mas o texto substituto
  reescrevia o parágrafo inteiro — cinco linhas. Aplicada ao pé da letra, ela deixaria quatro
  linhas órfãs, dizendo em versão velha o que a nova já dizia. Quem aplicou percebeu, removeu as
  quatro e reportou; a decisão foi dele, não da WO, e é decisão que uma WO não deveria delegar.
  **A regra é de escopo, não de tamanho:** a âncora precisa cobrir tudo o que o substituto torna
  redundante. A pergunta antes de fechar qualquer edição: *o que estou escrevendo faz alguma linha
  vizinha virar repetição?* O modelo de WO poderia dizer isso ao lado do conselho de preferir
  âncora de uma linha — os dois são verdadeiros e um limita o outro.
```

## Edicao 12 — `meta/STATUS.md` · o merge do CEREBRO fecha

**Ancora** (cinco linhas — o paragrafo inteiro da fase 2c, extraido do arquivo):

```
   configuração. **As 4 ocorrências de «sessão» no CEREBRO foram a zero.** **Fase 2c (a fazer):**
   seções novas «Sonda e exploração» (4.882) e «Correspondência entre projetos» (2.126),
   «Técnicas específicas deste projeto» (765), e os deltas menores em «Análise antes do
   compromisso» (+1.146), «Ao receber um template-update» (+421) e «Princípios» (+391). **Fase 3:**
   os 12 modelos.
```

**Substituir por:**

```
   configuração. **As 4 ocorrências de «sessão» no CEREBRO foram a zero** — pelo padrão varrido;
   a fase 2c achou mais 3, de outra forma («log de sessão», «entre sessões», «se a sessão mexeu»),
   e as fechou. **Fase 2c (wo0059, feita):** entraram as seções «Sonda e exploração»,
   «Correspondência entre projetos» e «Técnicas específicas deste projeto» — esta última com seis
   itens reais deste projeto, não vazia. Mais o funil da análise (agora com sonda), o parágrafo
   «o merge sabe somar, não sabe subtrair» e o bullet «princípio sem gatilho não dispara».
   **O merge do CEREBRO está fechado. Fase 3 (a fazer):** os 12 modelos do pacote.
```

> **Ancora multilinha de proposito**, e pela licao da wo0058: o texto novo reescreve o paragrafo
> todo, entao a ancora cobre o paragrafo todo. Nada de linha orfa desta vez.

---

## Fora de escopo

- **Fase 3:** os 12 modelos do pacote (`SPEC`, `CONTEXT`, `STATUS`, `DECISIONS`, `CHANGELOG`,
  `IDEAS`, `LOG-TEMPLATE`, `ROADMAP`, `GLOSSARY`, `HISTORY`, `_TEMPLATE` de WO e de análise).
- **Os bullets «Teto» e «Teto por configuração»** do Refino: os nossos estão adaptados a este
  projeto (sem ASU) e as versões do template regrediriam a adaptação. **Não os toque.**
- **O princípio 8** (`Verifica antes de pedir arquivo — e antes de AFIRMAR`): o nosso é mais rico
  que o do template, que ainda traz a versão sem o «e antes de AFIRMAR». **Fica o nosso.**
- **A seção «Ao receber um template-update do KCM»**: só ganha uma linha (Edição 9). O resto é
  nosso e o template não cobre.
- Nada de `.claude/`, nada de `flatdrop/`.

## Armadilhas desta WO

- **A Edição 2 cola um bloco com cercas de código dentro dele**, e dentro dessas cercas há linhas
  que começam com `## ` (`## ALARMES (N)`, `## O QUE NÃO FOI OLHADO`). **São conteúdo do exemplo,
  não títulos de seção.** Cole o bloco literal; não reformate, não «conserte» a indentação.
- **As Edições 2 e 3 usam o mesmo ponto de inserção** (o título da «Medição delegada»). Aplique a 2
  primeiro; a 3 continua casando depois, porque insere antes do mesmo título. A ordem final fica:
  Sonda → Correspondência → Medição delegada.
- **A Edição 1 insere antes de `## Convenções`**, que é um título curto e único — confira que não
  há outro `## Convenções` no arquivo antes de aplicar (`grep -c "^## Convenções"` → deve dar 1).
- Âncoras de uma linha nas Edições 4 a 10; **multilinha na 12, de propósito** (o texto novo
  reescreve o parágrafo todo).

---

## Depois de aplicar — conferência antes do commit

- [ ] `git diff` mostra exatamente: `meta/CEREBRO.md`, `meta/IDEAS.md`, `meta/STATUS.md`.
- [ ] **O número que fecha o merge do CEREBRO** — rode e reporte o cru:
      `grep -ci "sess" meta/CEREBRO.md` → **2**, e não zero. *(Eram 5 linhas antes desta WO; as
      Edições 4, 5 e 6 fecham três. As duas que ficam são **legítimas e não devem sair**: a linha
      do bullet «Abertura de turno», que diz «não é cerimônia de início de SESSÃO: é de TURNO» —
      contraste, e apagá-lo apagaria o argumento —, e a do bullet «Quem abre, fecha», que fala de
      «servidor esquecido entre sessões», texto do próprio kit v1.120.0. Se der 0, alguém varreu
      demais: **reporte, não conserte**.)*
      **Este número foi medido no arquivo vivo antes de a WO ser fechada** — na primeira redação
      dizia «0», que era estimativa. É a quarta vez que a medição corrige um número de checklist
      meu; ver «Técnicas específicas deste projeto», Edição 1.
- [ ] As três seções existem, uma vez cada:
      `grep -c "^## Sonda e exploração" meta/CEREBRO.md` → **1**;
      `grep -c "^## Correspondência entre projetos" meta/CEREBRO.md` → **1**;
      `grep -c "^## Técnicas específicas deste projeto" meta/CEREBRO.md` → **1**.
- [ ] `grep -c "^## Convenções" meta/CEREBRO.md` → **1** (a Edição 1 não duplicou o título).
- [ ] **Ordem das seções novas** — `grep -n "^## " meta/CEREBRO.md | grep -E "Sonda|Correspond|Medição"`
      deve sair nesta ordem: Sonda, Correspondência, Medição delegada. Reporte as três linhas.
- [ ] `python -m pytest -q` → **122**, sem mudança (WO só de doc).
- [ ] **Invariante DEC-020:** nada em `flatdrop/`.

## Relatório de aplicação *(quem aplica preenche ao terminar)*

O que foi feito · o que fugiu do texto literal · os números crus das conferências · o commit ·
**o push, com o resultado real**, escrito DEPOIS de o push estar resolvido. Grave o MESMO relatório
em `../AAMMDD-HHMM-code-flatdrop.txt`.

## Commit — blocos separados, mensagem SEM acento

```
git add meta\CEREBRO.md meta\IDEAS.md meta\STATUS.md meta\workorders\260826-wo0059-merge-kcm-fase2c.md
```

```
git commit -m "chore(kit): merge do KCM v1.120.0 fase 2c - fecha o CEREBRO" -m "Entram tres secoes novas: Sonda e exploracao (o par que produz evidencia, com o esqueleto de relatorio), Correspondencia entre projetos (contador compartilhado, um assunto por carta, carta nao se versiona) e Tecnicas especificas deste projeto, esta com seis itens reais em vez de vazia. Mais o funil da analise com sonda, o paragrafo o merge sabe somar mas nao subtrair, e o bullet principio sem gatilho nao dispara. A varredura ampla por sess achou mais tres ocorrencias que o padrao estreito da fase 2b escondia - as tres fechadas. Merge do CEREBRO concluido; sobra a fase 3, os modelos."
```

```
git push
```
