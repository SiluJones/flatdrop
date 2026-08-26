# WO 0056 — merge do KCM v1.120.0, fase 2a: as regras que governam a conduta

> **Tipo:** REGISTRO/comportamento — `meta/CEREBRO.md`, `CLAUDE.md`, `meta/IDEAS.md`,
> `meta/STATUS.md`. Nao toca codigo.
> **Config sugerida:** modelo intermediario, `/effort` medio. As ancoras sao de UMA linha; o
> volume esta no texto novo, nao no julgamento.
> **Pre-requisito:** wo0055 aplicada e empurrada (`37658b9`), **122 testes verdes**, arvore limpa.
> **Base:** `CEREBRO__template-update.md` (kit v1.120.0), secoes «Regras de higiene» e «Medicao
> delegada»; `CLAUDE__template-update.md`, secoes «Quando eu pedir medicao» e «Push e relatorio».
> O `_UPDATE-MANIFEST` manda aplicar PRIMEIRO as regras que governam a conduta durante o merge —
> e sao estas. Fases 2b e 2c vem depois.
> **Ancoras lidas em:** *(trecho literal lido NESTE turno; as edicoes 1 a 7 foram GERADAS a partir
> do arquivo vivo por script, nao digitadas — o texto da ancora e byte a byte o que esta em disco)*
> - `meta/CEREBRO.md`, secao «Regras de higiene (impedem inchaco e duplicacao)» — 8 bullets, linhas
>   135 a 142; cada um e UMA linha longa.
> - `meta/CEREBRO.md`, linha do titulo `## Bloco de fecho de turno (formato fixo)` — ancora da
>   secao nova.
> - `CLAUDE.md` — linha 3 (`> Arquivo-raiz lido...`), linha 20 (`- **Vocabulário (DEC-023):**...`)
>   e a linha `## Relatório em arquivo (sempre, sem pedir)`.
> - `meta/IDEAS.md` — primeiro item de «Feedback para o Kit».
> - `meta/STATUS.md` — item 3 do backlog, na versao que a wo0054 deixou.
> **Idempotencia:** procure `Medição delegada`, `Quando eu pedir medição` e `Varra pelo fato`. Se
> ja existirem, **PULE** e diga no relatorio.
> **Proximo comando:** nao ha — a fase 2b sai do chat depois desta aplicada.

> **Canal dos meta neste ciclo = CODE** (`CEREBRO`, `IDEAS`, `STATUS`). Esta WO E o registro deles.
> **Nao toque em `.claude/`** — ver a armadilha, no fim.

---

## 1. Por que

Este e o primeiro corte da fase 2 do merge, e vem primeiro por ordem do proprio pacote: o
`_UPDATE-MANIFEST` tem uma secao chamada «Aplique PRIMEIRO — as regras que governam o proprio
merge», com o argumento de que *quem esta muitas versoes atras passa o merge inteiro operando sob
as regras velhas que o pacote veio corrigir*. Duas das quatro regras dessa lista estao aqui
(medicao delegada e varredura pelo fato).

**Medido em 2026-08-26**, secao a secao, comparando os dois arquivos: a secao «Regras de higiene»
do template tem **12.922 bytes** contra **3.443** nossos — 16 bullets contra 8. Conferi os oito
nossos um a um: **seis viraram versao ampliada no template e dois estao identicos**, e em nenhum
caso o texto do template perde conteudo nosso. Nos dois bullets mais longos (o do artefato gerado
e o da releitura do mount), o texto do template **contem o nosso inteiro** e acrescenta — inclusive
a «Anatomia do bloco gerado», que nasceu aqui na DEC-029 e voltou formalizada em cinco regras.

**Tres dos dez bullets novos descrevem falhas que este projeto ja pagou:**

- *«Nao congele em documento estavel o que um artefato vivo ja responde»* — o `CLAUDE.md` diz
  **«a proxima e `wo0044`»**. Estamos na **wo0056**. O contador nasceu certo e envelheceu em
  silencio, e e exatamente o modo de falha que o bullet descreve. A Edicao 9 troca o valor pela
  regra.
- *«O que o `.gitignore`/`.flatdropignore` esconde, o assistente nao audita — e nao sabe que nao
  auditou»* — e o caso do `INSTRUCOES-DO-PROJETO.md`, que a DEC-032 acabou de consertar.
- *«Abertura de turno, antes de QUALQUER outra ferramenta»* — a versao forte da regra que faltava
  em 23/08, quando o assistente abriu um turno sem reler o mount.

**E um bullet novo entra em choque com uma recomendacao que este chat deu em 24/08**, o que esta
WO registra em vez de esconder: a regra de referencia cruzada agora diz que **mensagem trocada com
outro projeto e nota, nao artefato — nao se cria pasta versionada para ela**, e que negociacao
continuada vira **carta**, com nome e contador proprios, **fora do repositorio**. O chat havia
recomendado criar `meta/cartas/` e versionar a carta 02. **Conferido no manifesto: a pasta nunca
foi criada.** A recomendacao morre aqui, e o texto novo entra no lugar dela.

## Edicao 1 — `meta/CEREBRO.md` · higiene, bullet 1

**Ancora** (uma linha):

```
- Referência cruzada, não duplicação: um dado tem UMA fonte de verdade. Quando uma ideia vira trabalho, ela aparece também no STATUS — mas continua no IDEAS, só mudando de status. Não copie o conteúdo para dois lugares.
```

**Substituir por:**

```
- Referência cruzada, não duplicação: um dado tem UMA fonte de verdade. Quando uma ideia vira trabalho, ela aparece também no STATUS — mas continua no IDEAS, só mudando de status. Não copie o conteúdo para dois lugares. **Mensagem trocada com outro projeto ou frente irmã é nota, não artefato:** vive fora do repositório enquanto serve e vai para o arquivo morto depois — **não crie pasta versionada para ela**. Quando a troca é uma negociação continuada, ela vira **carta** e ganha nome e contador próprios (CEREBRO, «Correspondência entre projetos»); continua fora do repositório. O que precisa sobreviver é o que você extraiu dela para os documentos, não o texto da mensagem; guardar os dois é duplicar, e o texto envelhece enquanto o registro fica.
```

## Edicao 2 — `meta/CEREBRO.md` · higiene, bullet 2

**Ancora** (uma linha):

```
- STATUS é só o agora: item resolvido sai do STATUS e vai para o CHANGELOG (e para o log da sessão). Médio/longo prazo vive no ROADMAP, não no STATUS.
```

**Substituir por:**

```
- STATUS é só o agora: item resolvido sai do STATUS e vai para o CHANGELOG (e para o log do dia). Médio/longo prazo vive no ROADMAP, não no STATUS.
```

## Edicao 3 — `meta/CEREBRO.md` · higiene, bullet 3

**Ancora** (uma linha):

```
- **Artefato gerado que convive com edição humana** precisa de três coisas: (i) **enxergar o que existe fora dele** — senão duplica em silêncio o que a pessoa já escreveu; (ii) **precedência definida por posição** — quem vence quando os dois falam do mesmo; (iii) **nunca apagar nem desfazer o que não é seu**. Bloco gerado dentro de arquivo editável: delimite com marcadores, mantenha-o no FIM do arquivo, escreva só dentro deles, e diga na primeira linha que ali dentro é território da ferramenta. Se o gerado não enxerga o manual, ele desfaz gestos sem avisar — e o sintoma aparece longe da causa. (Mover o próprio bloco para o fim é a ferramenta mexendo no que é dela; mover o texto que a pessoa escreveu, não.)
```

**Substituir por:**

```
- Artefato gerado que convive com edição humana precisa de três coisas: (i) **enxergar o que existe fora dele** — senão duplica em silêncio o que a pessoa já escreveu; (ii) **precedência definida por posição** — quem vence quando os dois falam do mesmo; (iii) **nunca apagar nem desfazer o que não é seu**. Bloco gerado dentro de arquivo editável: delimite com marcadores, mantenha-o no FIM do arquivo, escreva só dentro deles, e diga na primeira linha que ali dentro é território da ferramenta (o que a pessoa escrever ali será reescrito). Se o gerado não enxerga o manual, ele desfaz gestos sem avisar — e o sintoma aparece longe da causa. **Anatomia do bloco gerado — cinco regras, e são as cinco juntas que compram a liberdade de editar o mesmo arquivo à mão:** (1) comentário fica FORA do bloco — dentro, o gerador reescreve tudo e ele some; (2) regra fica DENTRO — é o território da ferramenta; (3) existe UM bloco, e só um — dois são ambiguidade; (4) o bloco é o ÚLTIMO conteúdo do arquivo, nada depois dele; (5) **os marcadores não se citam em comentário** — o gerador costuma procurá-los por substring, e um exemplo é indistinguível de um segundo bloco. A quinta decorre da terceira, mas precisa ser dita em voz alta: é o erro que se comete justamente ao DOCUMENTAR a convenção, então descreva os marcadores em vez de reproduzi-los. **Duas obrigações do lado da ferramenta:** diante de ambiguidade, **recusar, não adivinhar** — reescrever é a única operação irreversível, e chutar ali destrói conteúdo; e **normalizar só o que é seu** — mover o próprio bloco para o fim é legítimo, mover o texto da pessoa não, e se a normalização mudar o efeito de alguma regra dela, avise antes.
```

## Edicao 4 — `meta/CEREBRO.md` · higiene, bullet 4

**Ancora** (uma linha):

```
- **A releitura do mount não tem gatilho próprio — e é por isso que ela falha.** Quatro modos, todos já observados aqui: (1) **trabalho pedido expulsa ritual não-pedido** — mensagem cheia de perguntas empurra a releitura para fora, e é justamente aí que ela mais importa, porque quem pede muito costuma ter subido algo antes de pedir; (2) **previsão vestida de observação** — relatar o estado que o seu próprio turno anterior previa, que por dentro é indistinguível de ter verificado; (3) **campo obrigatório preenchido de memória**, quando falta dado fresco; (4) **regra escrita longe do ponto onde ela quebra**. O antídoto é sempre o mesmo: o gatilho mora no gesto, não no apêndice — se você está prestes a afirmar estado, essa é a hora de ler.
```

**Substituir por:**

```
- A releitura do mount não tem gatilho próprio — e é por isso que ela falha. Quatro modos, todos observados em projetos reais: (1) **trabalho pedido expulsa ritual não-pedido** — mensagem cheia de perguntas explícitas empurra a releitura para fora, e é justamente aí que ela mais importa, porque quem pede muito costuma ter subido algo antes de pedir; (2) **previsão vestida de observação** — relatar o estado que o seu próprio turno anterior previa («ele vai aplicar isso depois»), que por dentro é indistinguível de ter verificado; (3) **campo obrigatório preenchido de memória**, quando falta dado fresco; (4) **regra escrita longe do ponto onde ela quebra**. O antídoto é sempre o mesmo: o gatilho mora no gesto, não no apêndice — se você está prestes a afirmar estado, essa é a hora de ler. **E os canais não chegam juntos:** relatório que a execução grava em arquivo nasce no instante da aplicação, enquanto a cópia achatada exige um passo manual de quem a gera. O relatório lidera, sempre. Quando os dois discordam, **o relatório vence e a cópia está atrasada** — e a listagem do mount é o único lugar onde essa discordância aparece.
```

## Edicao 5 — `meta/CEREBRO.md` · higiene, bullet 5

**Ancora** (uma linha):

```
- A sua cópia não é a fonte da verdade: vale o arquivo que está no repo/mount AGORA, não o que você leu, gerou ou reconstruiu antes nesta conversa. Qualquer artefato que você produziu (um pacote, uma reconstrução, um resumo do estado) envelhece no instante em que alguém aplica alguma coisa. Antes de dizer que algo continua pendente — ou de reentregar trabalho — releia o arquivo vivo. Reentregar o que já foi aplicado custa mais caro que perguntar. **A contrapartida, que evita o excesso oposto:** o que envelhece é o **estado do repo e as âncoras** — não o **carimbo de emissão** de um artefato. Documento escrito e datado no dia 27 continua correto se for aplicado no dia 29: a data diz quando foi emitido, não quando foi aplicado. Não «corrija» data de arquivo entregue, nem renomeie WO ou análise por causa de atraso.
```

**Substituir por:**

```
- A sua cópia não é a fonte da verdade: vale o arquivo que está no repo/mount AGORA, não o que você leu, gerou ou reconstruiu antes nesta conversa. Qualquer artefato que você produziu (um pacote, uma reconstrução, um resumo do estado) envelhece no instante em que alguém aplica alguma coisa. Antes de dizer que algo continua pendente — ou de reentregar trabalho — releia o arquivo vivo. Reentregar o que já foi aplicado custa mais caro que perguntar. **A contrapartida, que evita o excesso oposto:** o que envelhece é o **estado do repo e as âncoras** — não o **carimbo de emissão** de um artefato. Documento escrito e datado no dia 27 continua correto se for aplicado no dia 29; a data diz quando foi emitido, não quando foi aplicado. Não «corrija» data de arquivo entregue, nem renomeie WO/análise por causa de atraso. **E cuidado com a falsa confirmação:** reconstruir o projeto em sandbox a partir da cópia que você tem NÃO é verificação de estado. Âncora que ainda casa prova que a sua cópia é velha, não que o trabalho está pendente — se o trabalho tivesse sido aplicado, a âncora estaria morta, e é o silêncio dela que engana. Antes de reconstruir, compare a versão do artefato copiado com o estado declarado no cabeçalho da cópia; divergiram, a cópia está atrasada e nenhuma conclusão sobre pendência vale.
```

## Edicao 6 — `meta/CEREBRO.md` · higiene, bullet 6

**Ancora** (uma linha):

```
- Válvula de desvio registrado: os templates e a estrutura deste kit são PONTO DE PARTIDA, não contrato. Se a realidade do projeto não couber neles, adapte — dispense um arquivo que não serve, acrescente seção ou arquivo que falte — e REGISTRE o desvio (o que mudou e por quê) no DECISIONS, marcando-o também na seção «Feedback para o Kit» do IDEAS. Desviar SEM registrar é que é o erro; desviar registrando é como o kit aprende. E não duplique o que a estrutura já cobre.
```

**Substituir por:**

```
- Válvula de desvio registrado: os templates e a estrutura deste kit são PONTO DE PARTIDA, não contrato. Se a realidade do projeto não couber neles, adapte — dispense um arquivo que não serve, acrescente seção ou arquivo que falte — e REGISTRE o desvio (o que mudou e por quê) no DECISIONS, marcando-o também na seção «Feedback para o Kit» do IDEAS. Desviar SEM registrar é que é o erro; desviar registrando é como o kit aprende. E não duplique o que a estrutura já cobre. **Exemplo já visto e legítimo:** projeto cujo roadmap e registro de decisões referenciam ideias por **ID estável** organiza o IDEAS por status + ID, não pela divisão por autor do template — adotar o template ali seria regressão, e o desvio é o certo.
```

## Edicao 7 — `meta/CEREBRO.md` · os dez bullets novos

**Ancora** (a linha da Valvula, ja substituida na Edicao 6):

```
- Válvula de desvio registrado: os templates e a estrutura deste kit são PONTO DE PARTIDA, não contrato. Se a realidade do projeto não couber neles, adapte — dispense um arquivo que não serve, acrescente seção ou arquivo que falte — e REGISTRE o desvio (o que mudou e por quê) no DECISIONS, marcando-o também na seção «Feedback para o Kit» do IDEAS. Desviar SEM registrar é que é o erro; desviar registrando é como o kit aprende. E não duplique o que a estrutura já cobre. **Exemplo já visto e legítimo:** projeto cujo roadmap e registro de decisões referenciam ideias por **ID estável** organiza o IDEAS por status + ID, não pela divisão por autor do template — adotar o template ali seria regressão, e o desvio é o certo.
```

**Inserir IMEDIATAMENTE ANTES:**

```
- **Abertura de turno, antes de QUALQUER outra ferramenta:** liste o mount, leia o cabeçalho da cópia achatada se houver (data de geração + estado do repo), e confira a versão viva do artefato principal contra a que você acha que sabe. Um passo, quatro fatos, e só então o trabalho. **Sem cópia achatada nem manifesto** o passo continua valendo com o que houver — a listagem sozinha já mostra nota nova —; o que muda é o carimbo do fecho, que declara a base pobre em vez de fingir precisão. Não é cerimônia de início de SESSÃO: é de TURNO, e o turno pesado é justamente o que a dispensa por conta própria.
- **Varra pelo fato, não pela frase.** Fechar um item, trocar um nome ou registrar uma refutação não termina no arquivo onde a decisão nasceu. Procure três coisas, sempre: (a) o termo antigo literal; (b) o mesmo conceito em paráfrase, que o `grep` não acha; (c) as listas de pendência — STATUS, IDEAS, checklists. E **as skills por último e com mais atenção**: são a superfície mais esquecida e a mais perigosa, porque são lidas ANTES de trabalhar, então uma linha morta ali dirige o trabalho seguinte em vez de só informar mal.
- **Documento derivado nunca é fonte.** Handoff, brief, resumo, reconstrução, checklist, relatório — inclusive os que você mesmo escreveu — são saída de assistente, não cânone. Eles congelam quando nascem enquanto o repo anda, e o modo de falha é sempre o mesmo: o derivado é lido como fato por um turno inteiro antes de alguém conferir. Duas defesas: **a derivação aparece no nome do arquivo** (prefixo/sufixo que se lê de relance), e **antes de usar um dado dele, confira no arquivo vivo**. Divergência entre derivado e fonte: a fonte vence, e o derivado é reescrito lendo a fonte, nunca ajustado de memória.
- **Cite a frase-gatilho antes de perguntar.** Quando a dúvida nasce de algo que o usuário escreveu — uma nota, um pedido, uma linha de arquivo —, a frase inteira entra citada ANTES da pergunta. Referência cruzada nua (`arquivo:linha`, «ver DEC-0XX») pode acompanhar o texto literal, nunca substituí-lo: quem escreveu não decora o que escreveu. E nunca pergunte usando um rótulo que você inventou para o assunto — o usuário não reconhece o nome que você deu à dúvida dele.
- **Mudança de método não se adota no meio do trabalho.** Refinar o conteúdo é dever contínuo; mudar COMO o trabalho é feito — ordem, sequência, formato do ciclo, o que entra em cada leva — é troca de trilho, e troca de trilho para e vira análise, com o dono decidindo. O modo de falha é específico e já custou caro: um único dado ruim numa etapa vira proposta de reprojeto, a proposta é aceita no impulso, e o custo só aparece na etapa seguinte. Propor continua permitido e é esperado; o que não é permitido é otimizar o processo em vez de executá-lo.
- **Não congele em documento estável o que um artefato vivo já responde.** Contador escrito à mão («a próxima livre é a 118»), contagem de arquivos, versão instalada, estado de branch: tudo isso é derivável de algo que muda sozinho, e o documento que o copia não muda junto. O instantâneo nasce certo e envelhece em silêncio — e o pior é que ele parece autoridade, então a leitura seguinte confia nele em vez de conferir. **Escreva a REGRA, não o valor:** «a maior existente + 1, confira a pasta» em vez do número. Quando o valor precisa mesmo aparecer (um relatório, uma decisão), ele vem **datado e com a origem**, como registro do que era naquele momento — não como estado atual.
- **O que o `.gitignore`/`.flatdropignore` esconde, o assistente não audita — e não sabe que não auditou.** As duas listas decidem o que chega ao Projeto, e uma linha errada ali apaga uma superfície inteira **sem erro nenhum**: a varredura roda, não acha nada, e o silêncio é lido como limpeza. O caso que dói é `.claude/` — skills e permissões, que são lidas ANTES de trabalhar. **Duas conferências baratas:** (1) o comentário do arquivo bate com as regras dele? «NÃO ignore .claude/» duas linhas acima de `.claude/` é contradição que ninguém relê; (2) o que está ignorado está **versionado em algum lugar**? Config ignorada não tem backup nem histórico, e some com a máquina. **Ausência de resultado não é resultado:** antes de dizer «varri e está limpo», confirme que havia o que varrer.
- **Antes de destruir ou sobrescrever, leia o que está lá — e proponha a proteção mais barata.** Duas metades da mesma falta de cuidado. (1) **Ler antes de escrever por cima:** arquivo que já existe pode ter conteúdo que ninguém pediu para preservar porque ninguém lembrou dele. Abrir custa um comando; recuperar custa a conversa inteira, e às vezes não custa nada porque não dá. (2) **Restrição do dono não se cumpre ao pé da letra quando há forma mais barata de obter a mesma proteção:** «não apague os originais» é um MEDO, não uma especificação — a resposta certa é copiar para fora do espaço de trabalho e seguir, dizendo que fez. Cumprir a letra e deixar o problema de pé é obedecer contra o interesse de quem pediu. Custo real: uma pasta de trabalho que ficou impossível de limpar por dias, e um arquivo de configuração sobrescrito sem leitura prévia.
- **Todo comando entregue ao usuario vai INTEIRO e diz QUEM executa.** Inteiro: nada de `<...>`, `<caminho>` ou reticencias no lugar de um valor que voce ja tem impresso na conversa. Placeholder so vale quando o valor e genuinamente desconhecido — e ai vem NOMEADO («troque `<id>` pelo id do mapa»), nunca como reticencias. Quem executa: **«e do usuario» e conclusao, nao rotulo, e exige nomear o impedimento** — a pergunta de uma linha antes de escrever isso e *o que este comando faz que o executor nao consegue?*, e sem resposta o comando e do executor. **Impedimento de um passo nao se herda para o passo vizinho:** descobrir que a rede local derruba HTTPS nao torna manual um comando que so le arquivo local. Custo medido em campo: cinco tarefas seguidas carimbadas «conferencia do dono» para um comando que o executor rodaria sozinho, e um caminho entregue com reticencias que estava completo em tres relatorios do mesmo dia.
- **Quem abre, fecha — e o que não fechar, declara.** Toda tarefa cria coisas **fora** do repositório: processo, porta, servidor de desenvolvimento, arquivo temporário, download de teste. Elas são de quem as criou, e a tarefa termina com a máquina como a encontrou. O que não puder ser fechado entra no relatório **com o caminho**, não como nota vaga — é exatamente o que ninguém lembra de limpar, e o custo aparece longe: servidor esquecido entre sessões chega a travar a pasta e impedir o teste seguinte; arquivo de teste largado numa pasta pessoal vira pergunta («isto aqui é seu?») numa conversa que já tinha fechado. E vale o par: **entrega bloco para outro rodar quem NÃO pode rodá-lo.** Quem tem o terminal executa e relata; devolver bloco para o dono colar, tendo como rodar, é trocar de raia.
```

## Edicao 8 — `meta/CEREBRO.md` · secao nova «Medicao delegada»

**Ancora** (uma linha, o titulo da secao seguinte):

```
## Bloco de fecho de turno (formato fixo)
```

**Inserir IMEDIATAMENTE ANTES** (com uma linha em branco depois do bloco novo):

```
## Medição delegada (quem tem o disco mede, quem tem o contexto decide)

A raia de planejamento tem teto de contexto e lê só o que chega pelo mount; a raia de execução lê o disco inteiro e não tem nenhum dos dois limites. Quando o dado que falta é **estado de arquivo** — quantas linhas, quais chaves, que dimensão, se existe —, a saída não é pedir upload de um arquivo grande nem escrever um script para o dono rodar: é **mandar medir**.

- **A regra:** quem tem acesso ao disco mede, quem tem contexto decide. Nunca afirme estado de arquivo que você não leu — nem para justificar uma escolha, nem para escrever caminho «mais ou menos certo». Caminho com `...` no meio é o sintoma clássico de estado deduzido.
- **O pedido de medição não é ordem de trabalho.** Não tem âncora, não tem edição, não tem commit e não muda arquivo nenhum. É bloco colável, entregue como qualquer instrução ao executor — não crie arquivo nem pasta para ele. Se virar ordem de trabalho, você já estará escrevendo a ordem sem os números que ela precisava, que é exatamente o erro que a medição evita.
- **Peça número cru, não interpretação.** Diga o comando ou o que contar, e peça de volta o valor e o comando que o produziu. Executor que interpreta devolve opinião no lugar de dado — e opinião de quem mediu é a mais difícil de contestar depois, porque parece medida.
- **Dados fora da raiz exigem permissão.** Se o material a medir vive ao lado do repositório e não dentro dele, o executor precisa de `permissions.additionalDirectories` no `.claude/settings.json` — a mesma chave que libera gravar o relatório na pasta-pai, agora para ler.
- **Onde o número pousa.** No relatório da execução, sempre. Se ele mudar uma decisão, também no registro de decisões; se ele revelar um risco, nas armadilhas da ordem de trabalho. Número medido e não registrado volta a ser deduzido no turno seguinte.
- **Fato que o usuário relata no chat não existe até estar num arquivo — e a origem vai junto.** `[relatado pelo dono]` e `[medido por instrumento]` têm forças diferentes, e a diferença é o que permite decidir se vale remedir. Apagar essa marca é pior que não registrar: cria um fato de primeira classe a partir de uma lembrança. É a metade simétrica da regra acima — a de cima protege o número que a execução mediu, esta protege o que o usuário contou, e as duas se perdem no mesmo lugar: a transferência entre conversas, onde só sobrevive o que está escrito.
```

## Edicao 9 — `CLAUDE.md` · o contador congelado vira regra

**Ancora** (uma linha):

```
- **Vocabulário (DEC-023):** **WO** = *como aplicar* (delta com texto exato + âncora), em `meta/workorders/AAMMDD-woNNNN-desc.md` — a numeração continua das antigas specs, a próxima é `wo0044`. **spec** = *o quê construir e quando está pronto* (spec de feature, modelo em `meta/SPEC.md`), em `meta/specs/`. Não confunda: as `spec0001`–`spec0037` que estão em `meta/workorders/` são WOs com nome antigo, e assim ficam.
```

**Substituir por:**

```
- **Vocabulário (DEC-023):** **WO** = *como aplicar* (delta com texto exato + âncora), em `meta/workorders/AAMMDD-woNNNN-desc.md` — a numeração continua das antigas specs, e **a próxima livre é a maior existente + 1 — confira a pasta, não confie em número escrito aqui** (um contador copiado para dentro de documento estável nasce certo e envelhece em silêncio: este dizia `wo0044` quando o repo já ia na `wo0055`). **spec** = *o quê construir e quando está pronto* (spec de feature, modelo em `meta/SPEC.md`), em `meta/specs/`. Não confunda: as `spec0001`–`spec0037` que estão em `meta/workorders/` são WOs com nome antigo, e assim ficam.
```

## Edicao 10 — `CLAUDE.md` · duas secoes novas do template

**Ancora** (uma linha):

```
## Relatório em arquivo (sempre, sem pedir)
```

**Inserir IMEDIATAMENTE ANTES** (com uma linha em branco depois do bloco novo):

```
## Quando eu pedir medição
- Eu leio só o que chega pelo mount; você lê o disco. Se eu pedir para **medir**, o pedido não tem âncora nem commit: não edite nada, não conserte nada, não sugira nada.
- Responda com o **número cru e o comando que o produziu**. Sem interpretação, sem recomendação — se você achar que o número indica um problema, diga o número primeiro e a suspeita depois, separada.
- Se o alvo estiver fora da raiz do repositório, isso depende de `permissions.additionalDirectories` no `.claude/settings.json` (a mesma chave do relatório em arquivo). Se a leitura for negada, DIGA — não estime.

## Push e relatório — nesta ordem, sempre
- **Verde** (validação passou, ou WO só de doc com o `git diff` conferido) → `add`, `commit` e **`push`, sem perguntar.** Não peça permissão para o que já está decidido.
- **Vermelho** (validação falhou, âncora não encontrada, `git diff` com arquivo fora do previsto) → **não commite e não empurre.** E **não pergunte em prosa** («posso dar push?») — pergunta escrita no meio do texto passa despercebida. Feche com um **menu numerado** de saídas reais, a recomendada em **1** — ex.: `1) corrigir <o quê> e revalidar (recomendado)  2) reverter as edições  3) commitar local, sem push  4) empurrar assim mesmo`.
- **O relatório é o ÚLTIMO passo** — só depois de resolvido o push. Ele diz o que de fato aconteceu: empurrado (com o hash), não empurrado (com o motivo), ou aguardando a escolha do menu. **Relatório escrito antes da decisão conta metade da história** e vira mentira assim que o push sai; se a escolha chegar depois, **reescreva o relatório**, não deixe a versão velha valendo.
```

> **Sobre a secao «Push e relatorio»:** ela chega do template mandando empurrar sem perguntar no
> caso verde. **Este projeto tem desvio registrado (DEC-032): o push pede confirmacao.** Aplique o
> texto como esta e acrescente, LOGO APOS a linha do «Verde», esta frase — para o texto nao
> contradizer a decisao viva:

**Ancora** (uma linha, ja dentro do bloco que voce acabou de inserir):

```
- **Verde** (validação passou, ou WO só de doc com o `git diff` conferido) → `add`, `commit` e **`push`, sem perguntar.** Não peça permissão para o que já está decidido.
```

**Substituir por:**

```
- **Verde** (validação passou, ou WO só de doc com o `git diff` conferido) → `add` e `commit` sem perguntar. **`push`: peça confirmação — DESVIO REGISTRADO deste projeto (DEC-032)**, contra a regra do kit v1.104.0, que manda empurrar direto. O gatilho para reabrir está na DEC-032: a primeira vez que a confirmação atrasar um relatório correto.
```

## Edicao 11 — `meta/IDEAS.md` · dois itens para «Feedback para o Kit»

**Ancora** (uma linha, primeiro item da secao):

```
- **Ausência de saída não é ausência de recurso — leia o código antes de devolver a outra frente
```

**Inserir IMEDIATAMENTE ANTES:**

```
- **Edição em `.claude/` não vai por WO — vai pelo chat, como arquivo inteiro.** Medido em
  2026-08-26, na wo0054: o classificador de permissão do Claude Code **bloqueou** as duas edições
  que tocavam `.claude/settings.json` e `.claude/skills/wrap/SKILL.md`, e o executor fez certo em
  não contornar (a barreira existe para impedir que o Code se autoconceda permissão, e «eu
  autorizo» dito no chat não muda isso). O erro foi do **chat**, ao montar a WO: deveria ter
  previsto que edição na configuração do próprio executor não é aplicável por ele. **Regra:**
  arquivo sob `.claude/` o chat entrega INTEIRO, para download e substituição; a WO só o menciona
  no `git add`. O kit poderia marcar essas edições como «risco de bloqueio do classificador».
- **A distinção «MANDA × RELATA» vale para o próprio texto da WO, não só para a varredura.** Medido
  em 2026-08-26, na wo0055: a WO mandou trocar as **três** ocorrências de `118` no `STATUS.md`, e
  o executor trocou **duas** — deixando de pé a que estava dentro de um bloco datado («números
  lidos nesta revisão», 24/08), porque ali `118` era o número **medido naquele dia**. Ele estava
  certo e a WO estava errada: trocar teria falsificado o registro. Quem escreve a instrução de
  varredura precisa classificar as ocorrências ANTES de mandar trocar todas — é a mesma regra que
  o kit aplica às linhas revogadas, virada para dentro.
```

## Edicao 12 — `meta/STATUS.md` · o estado do merge

**Ancora** (uma linha, dentro do item 3 do backlog):

```
   **Fase 1 (wo0054, feita):** `Write` no `settings.json`, as 3 linhas revogadas da `wrap/SKILL.md`,
```

**Substituir por:**

```
   **Fase 2a (wo0056, feita):** as «Regras de higiene» do CEREBRO passaram de 8 para 16 bullets
   (3.443 → 12.922 bytes, medido em 26/08), entrou a seção «Medição delegada», e o `CLAUDE.md`
   ganhou «Quando eu pedir medição» e «Push e relatório» (esta com o desvio da DEC-032 escrito no
   corpo). **Fase 2b e 2c (a fazer):** «Bloco de fecho de turno» (2.797 → 6.861), «Tabela de
   gatilhos» (1.885 → 3.960), «Ao final da conversa, o assistente REGISTRA o que falta» (substitui
   a nossa «Ao final de cada sessão… entrega arquivos completos»), e as seções novas «Sonda e
   exploração» (4.882) e «Correspondência entre projetos» (2.126) — mais os 4 títulos com
   «sessão» que ainda restam no CEREBRO.
   **Fase 1 (wo0054, feita):** `Write` no `settings.json`, as 3 linhas revogadas da `wrap/SKILL.md`,
```

---

## Fora de escopo

- **Tudo o mais do `CEREBRO.md`** — fases 2b e 2c. Em especial: **não** mexa nos títulos que ainda
  dizem «sessão» (são 4, e saem junto com as seções a que pertencem) nem na seção «Ao final de cada
  sessão, o assistente entrega», que o template **substitui inteira** por outra com nome diferente.
- **`.claude/`** — nada. Ver armadilha.
- **Código, testes, `_TEMPLATE.md`** (fase 3).

## Armadilhas desta WO

- **NÃO tente editar nada sob `.claude/`.** Na wo0054 o classificador bloqueou as duas edições que
  tocavam essa pasta, e a barreira é do harness, não da WO. Esta WO foi montada sem nenhuma edição
  ali de propósito — se alguma instrução parecer pedir isso, **PARE e reporte**.
- **As âncoras das Edições 1 a 8 foram geradas do arquivo por script, não digitadas.** Se alguma
  não casar, o arquivo mudou depois de 2026-08-26 07:47 (geração do mount que eu li) — **PARE e
  reporte o texto real**, não aproxime.
- Cada bullet de higiene é **UMA linha longa**. Não quebre em várias ao colar; o `grep` de
  conferência conta linhas.
- O bloco novo da Edição 7 tem **dez linhas, cada uma um bullet**. Confira o número depois de
  aplicar: a seção passa a ter **16** bullets.

---

## Depois de aplicar — conferência antes do commit

- [ ] `git diff` mostra exatamente: `meta/CEREBRO.md`, `CLAUDE.md`, `meta/IDEAS.md`,
      `meta/STATUS.md` — e nada de `.claude/`.
- [ ] `grep -c "^- " meta/CEREBRO.md` na seção de higiene → **16 bullets**. Conte com
      `sed -n '/^## Regras de higiene/,/^## Como o assistente entrega/p' meta/CEREBRO.md | grep -c "^- "`.
- [ ] `grep -n "wo0044" CLAUDE.md` → **0**. *(Termo citado por uma edição só; esperado = 0.)*
- [ ] `grep -n "Medição delegada" meta/CEREBRO.md` → **1**; `grep -n "Quando eu pedir medição" CLAUDE.md` → **1**.
- [ ] **Prova de vida da varredura de «sessão»**, que ainda NÃO fecha nesta WO:
      `grep -ncE "de cada sess|fim de sess|inicio de sess|toda sess" meta/CEREBRO.md` →
      **esperado 4, não 0**. Zero aqui significaria que alguém varreu além do escopo; a fase 2b é
      que zera. *(Este passo responde «está lá?», não «presta?»: ele confirma que as ocorrências
      restantes continuam de pé, não que o texto novo faz sentido.)*
- [ ] **WO só de doc:** não há suíte a rodar. Rode `python -m pytest -q` mesmo assim e confirme
      **122** — se mudou, alguma edição saiu do lugar.
- [ ] **Invariante DEC-020:** nada de `flatdrop/`.

## Relatório de aplicação *(quem aplica preenche ao terminar)*

O que foi feito · o que fugiu do texto literal · arquivos tocados · a contagem de bullets · o
commit · **o push, com o resultado real** — e o relatório é escrito DEPOIS de o push estar
resolvido. Grave o MESMO relatório em `../AAMMDD-HHMM-code-flatdrop.txt`.

## Commit — blocos separados, mensagem SEM acento

```
git add meta\CEREBRO.md CLAUDE.md meta\IDEAS.md meta\STATUS.md meta\workorders\260826-wo0056-merge-kcm-fase2a.md
```

```
git commit -m "chore(kit): merge do KCM v1.120.0 fase 2a - regras de conduta" -m "Regras de higiene do CEREBRO passam de 8 para 16 bullets: abertura de turno antes de qualquer ferramenta, varredura pelo fato, documento derivado nunca e fonte, nao congelar em doc estavel o que artefato vivo responde, o que o ignore esconde ninguem audita, comando entregue inteiro dizendo quem executa, quem abre fecha. Entra a secao Medicao delegada. CLAUDE.md ganha Quando eu pedir medicao e Push e relatorio (com o desvio da DEC-032 escrito no corpo) e perde o contador congelado wo0044."
```

```
git push
```
