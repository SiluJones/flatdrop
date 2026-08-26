# WO 0058 — merge do KCM v1.120.0, fase 2b: a cadência do trabalho

> **Tipo:** REGISTRO/comportamento — `meta/CEREBRO.md`, `meta/IDEAS.md`, `meta/STATUS.md`.
> Nao toca codigo, nao toca `.claude/`.
> **Config sugerida:** modelo intermediario, `/effort` medio. As ancoras 4, 5 e 6 sao MULTILINHA
> (secoes inteiras) — o cuidado esta em casar o bloco todo, nao em julgar.
> **Pre-requisito:** wo0057 aplicada e o wrap fechado (`9e4c8df`), **122 testes verdes**, arvore
> limpa.
> **Base:** `CEREBRO__template-update.md` (kit v1.120.0), secoes «Ritual de inicio de turno»,
> «Bloco de fecho de turno», «Tabela de gatilhos», «Ao final da conversa, o assistente REGISTRA o
> que falta» e «Recomendacao de configuracao (fim de turno)».
> **Ancoras lidas em:** *(as dez edicoes foram GERADAS por script a partir dos arquivos vivos do
> mount de 2026-08-26 15:21 — nenhum trecho foi digitado)*
> - `meta/CEREBRO.md` — secoes acima, lidas inteiras; linha 103 (tabela de artefatos); linhas
>   223-227 (os cinco bullets do Refino, conferidos no lugar certo).
> - `CEREBRO__template-update.md` — as mesmas secoes, lidas inteiras.
> - `meta/IDEAS.md` — primeiro item de «Feedback para o Kit».
> - `meta/STATUS.md` — a linha do item 3 que descreve as fases 2b/2c.
> **Idempotencia:** procure `Ritual de início de turno`, `REGISTRA o que falta` e `Fim de QUALQUER
> turno`. Se ja existirem, **PULE** e diga no relatorio.
> **Proximo comando:** nao ha — a fase 2c sai do chat depois desta aplicada.

> **Canal dos meta neste ciclo = CODE** (`CEREBRO`, `IDEAS`, `STATUS`).

---

## 1. Por que

Fase 2a trouxe as regras que governam a conduta. Esta traz a **cadencia**: quando o assistente
fecha um turno, o que dispara cada entrega, e o que ele faz no fim de uma conversa. As tres secoes
maiores do merge que ainda faltavam estao aqui.

**Uma edicao troca REGRA, nao vocabulario — a Edicao 6.** A nossa secao mandava entregar todo
documento afetado INTEIRO, no fim da sessao. A nova diz que **num projeto com executor isso se
inverte**: documento grande e vivo muda por WO cirurgica, e reescrever documento grande no fim de
uma conversa pesada e justamente onde se perde conteudo. E a mesma regra que a wo0054 ja pos nas
Instrucoes do Projeto — aqui ela chega ao CEREBRO, que e onde mora a versao longa. As outras nove
edicoes sao vocabulario («sessao» -> «turno»/«conversa») ou linhas novas de tabela.

**Fim das ocorrencias de «sessao».** Eram 4 quando a fase 2a fechou (linhas 10, 103, 260/265 e
272/311). Todas saem aqui, dentro das secoes a que pertencem — nenhuma como rename solto.

**E o pacote tem um defeito, que esta WO nao copia.** Comparando as duas versoes, os cinco bullets
finais da secao «Bloco de fecho de turno» do template — «Sincronia com o CEREBRO», «Uma regra por
linha», «Teto», «Teto por configuracao» e «Registre» — **pertencem ao «Refino das Instrucoes do
Projeto»**, e nao estao la no template: sairam do lugar e foram parar no fim do fecho. No nosso
arquivo eles ja vivem no Refino (linhas 223-227), na versao adaptada a este projeto. Aplicar o
template ao pe da letra duplicaria os cinco no fecho e os perderia no Refino. **A Edicao 4 os
retira do texto adotado**, e o achado volta ao kit pela Edicao 9.

**O que e NOSSO e fica** (regra «template generico nao substitui vivo»): o paragrafo final da
tabela de gatilhos, que nomeia o conjunto de arquivos deste projeto, e a citacao da **DEC-026** na
linha do `logs/`. O template os substitui por texto generico sobre nichos — trocar seria perder
informacao que so existe aqui.

---

## Edicao 1 — `meta/CEREBRO.md` · o titulo do ritual (uma linha)

**Ancora**:

```
## Ritual de início de sessão
```

**Substituir por:**

```
## Ritual de início de turno
```

## Edicao 2 — `meta/CEREBRO.md` · o passo 4 do ritual (uma linha)

**Ancora**:

```
4. Lê última entrada do `CHANGELOG.md` — vê o que mudou desde a sessão anterior.
```

**Substituir por:**

```
4. Lê última entrada do `CHANGELOG.md` — vê o que mudou desde a conversa anterior.
```

## Edicao 3 — `meta/CEREBRO.md` · a linha do `logs/` na tabela de artefatos (uma linha)

**Ancora**:

```
| `logs/AAAA-MM-DD.md` | Histórico | Ao final de cada sessão (formato em LOG-TEMPLATE). **Um arquivo por DIA** (DEC-026): segunda sessão no mesmo dia vira `## Sessão N` no mesmo arquivo, nunca arquivo novo. |
```

**Substituir por:**

```
| `logs/AAAA-MM-DD.md` | Histórico | Ao bater um gatilho de evento — cortar versão, registrar decisão ou bug grave, virar o dia (formato em LOG-TEMPLATE). **Um arquivo por DIA** (DEC-026): segunda conversa no mesmo dia vira `## Conversa N` no mesmo arquivo, nunca arquivo novo — o nome é da data, não da conversa. |
```

> **Por que nao e o texto do template ao pe da letra:** o template diz «Duas conversas no mesmo dia = o MESMO
> arquivo, com `## Conversa N`». A regra e a mesma que a nossa **DEC-026** ja tinha decidido; o que muda e o
> vocabulario («sessao» -> «conversa») e o gatilho (por EVENTO, nao por fim de sessao). O texto acima mantem a
> citacao da DEC-026, que o template nao tem como conhecer — e a regra «template generico nao substitui vivo».

## Edicao 4 — `meta/CEREBRO.md` · a secao de fecho de turno INTEIRA

**Ancora**:

```
## Bloco de fecho de turno (formato fixo)

Todo turno de trabalho fecha assim, **emitindo só as linhas que se aplicam** — linha sem conteúdo real não aparece (não escreva «nada a arquivar» nem invente handoff). **Próximo** vem antes de um divisor; o resto vem depois dele:

1. **Próximo** — sempre presente, ANTES do divisor, em duas partes: **(a) Ação** — a próxima coisa concreta a fazer; **(b) Peça no próximo turno** — a frase que o usuário pode mandar de volta para retomar sem reconstruir contexto. Não é lista de possibilidades: é uma ação e um pedido.
2. **Estado** — uma linha: versão/fase, resultado da suíte (`python -m pytest -q`) quando houve mexida em código, e o commit, quando existir. **Todo dado desta linha vem de leitura FEITA NESTE TURNO.** Se algo não foi verificado agora, ou se verifica antes de escrever, ou se escreve "não verificado nesta rodada" — nunca se completa a linha de memória. Campo obrigatório é convite a preencher com o que se lembra, e o que se lembra é a expectativa do próprio turno anterior, não o repo. **Distinga «não verifiquei» de «não dá para ler daqui»:** o mount é uma cópia achatada e não tem `.git`, então nenhum `git log` existe para ler — nesse caso escreva «commit não legível pelo mount» e **peça uma vez** (`git log -1 --oneline`), em vez de repetir a ressalva todo turno. «Não verifiquei» é desleixo; «não é legível por este canal» é fato, e o remédio de cada um é diferente. *(Quando o FlatDrop passar a gravar o estado do repo no manifesto, use o que estiver lá e não peça — respeitando que é foto da hora da geração.)*
3. **Arquivar / Manter** — só se houver notas avulsas no mount. Em lista: uma linha **Arquivar:** com os nomes já absorvidos e uma linha **Manter:** com os que seguem vivos, cada um com o motivo em poucas palavras. Nome por nome — e sem esperar que o usuário pergunte.
4. **Config recomendada** — em lista, uma linha por raia (chat de planejamento / Claude Code), cada uma nomeando a raia, o tipo de modelo e o nível de esforço. Só as raias que o próximo passo realmente usa. Nunca afirme saber a config atual.
5. **Handoff** — por último, só quando houver arquivo trocando de mão: arquivo por arquivo, onde cada um vai. Handoff de sessão completo: o artefato se chama `AAMMDD-HANDOFF-BRIEF.md`.

**De quem é este bloco:** da raia de **planejamento** (o assistente no chat). Quem **executa** no Claude Code não fecha assim — fecha com o **relatório de trabalho**: o que fez, o que encontrou que foge do que a tarefa pedia, os arquivos tocados, o resultado de `python -m pytest -q` e o commit. Trocar o relatório por este formulário perde a informação que só quem executou tem.

Este formato é ponto de partida, não jaula: se um dado recorrente deste projeto merece linha própria, acrescente; se uma linha nunca se aplica aqui, proponha removê-la no refino.
```

**Substituir por:**

```
## Bloco de fecho de turno (formato fixo)
Todo turno de trabalho fecha assim, **emitindo só as linhas que se aplicam** — linha sem conteúdo real não aparece (não escreva «nada a arquivar» nem invente handoff). **Próximo** vem antes de um divisor; o resto vem depois dele:
1. **Próximo** — sempre presente, ANTES do divisor, em duas partes: **(a) Ação** — a próxima coisa concreta a fazer; **(b) Peça no próximo turno** — a frase que o usuário pode mandar de volta para retomar sem reconstruir contexto (a frente sugerida, já redigida como pedido). Não é lista de possibilidades: é uma ação e um pedido.
   **A frase só pode conter resultado que o usuário saiba produzir.** É aqui que a regra de instruções cuidadosas costuma falhar — não por má vontade, mas porque a linha é redigida rápido, no fim do turno, e ninguém a lê como um pedido de trabalho. Antes de escrevê-la, pergunte de quem é cada resultado que ela menciona: se é do executor, peça o **relatório** («aplicada, aqui o relatório»); se é de fato do usuário, o **comando exato, quem roda e o que esperar ver** vêm no MESMO turno, não na resposta seguinte. Pedir «o teste manual deu X» sem nunca ter dito que teste é esse, quem o roda e como se roda transfere ao usuário um trabalho que ele não sabe que tem — e ele descobre isso escrevendo de volta para perguntar.
2. **Estado** — uma linha: onde o projeto está agora (versão/fase e, havendo harness, o resultado dos testes) e o commit, quando existir. **Todo dado desta linha vem de leitura feita NESTE turno.** Se você não verificou, escreva «não verificado nesta rodada» — é resposta de primeira classe, não falha. E distinga do caso em que o dado **não é legível por este canal**: num Projeto alimentado por cópia achatada não há `.git`, então nenhum `git log` existe para ler — aí **comece pelo manifesto**: se o **manifesto da cópia achatada já trouxer o estado do repo** (último commit, branch, limpo/sujo), o dado está lido — use-o e NÃO peça, registrando que é foto da hora da geração, não do turno. Só quando não houver manifesto, ou ele não trouxer o estado, escreva «commit não legível pelo mount» e **peça uma vez** (`git log -1 --oneline`), em vez de repetir a ressalva todo turno. **A ordem desta regra é a regra:** exceção escrita depois da instrução chega tarde, porque quem lê de cima para baixo já pediu. **A linha abre com o carimbo `Base:`** — qual arquivo foi lido NESTE turno para saber o estado, com a data que ELE declara e o commit/versão que ELE traz (`Base: _MANIFEST 02/08 23:40 · d423747 · 3 .txt`). Sem cópia achatada, use o que houver: o doc de estado do projeto e a data dele. O carimbo existe porque campo de verificação genérico é inauditável — quem lê não sabe se você leu ou lembrou —, enquanto uma data que o próprio usuário gerou ele confere num olhar. Carimbo inventado é mentira detectável; campo vago não é. «Não verifiquei» é desleixo; «não dá para ler daqui» é fato, e o remédio de cada um é diferente. **O mount não carrega idade por arquivo** — medido: os arquivos chegam com a data zerada, e a única idade legível é a do manifesto, que vale para o lote inteiro e não diz qual arquivo mudou. Logo, «isto mudou desde que li?» é conferência de CONTEÚDO (uma frase-chave, um `grep`), nunca de data. Campo obrigatório sem dado fresco puxa a resposta da memória, e logo depois de entregar um trabalho a memória é a *expectativa* de que ele foi aplicado: previsão vestida de observação.
3. **Arquivar / Manter** — só se houver notas avulsas no mount. **Em lista**, como a Config e o Handoff: uma linha **Arquivar:** com os nomes já absorvidos e uma linha **Manter:** com os que seguem vivos, cada uma com o motivo em poucas palavras. **A lista é EXAUSTIVA:** todo arquivo avulso do mount entra numa das duas. Omissão é ambígua e o leitor não tem como desfazer a ambiguidade — pode significar «já extraí tudo» ou «nunca abri», e as duas pedem ações opostas. **«Arquivar» é afirmação forte:** só entra o que você leu INTEIRO naquele turno; na dúvida, «Manter» com o motivo. **E «Manter: não li» tem prazo** — fila indefinida não é cuidado: um relatório ficou quatro turnos nessa fila carregando a armadilha que voltou a acontecer duas vezes enquanto ele esperava. Nome por nome — e não espere que eu pergunte.
4. **Config recomendada** — em lista, **uma linha por raia**, cada uma nomeando a raia, o tipo de modelo e o nível de esforço (e o terminal, se a raia usar). Só as raias que este projeto realmente usa. Nunca afirme saber a config atual — recomende pela tarefa que vem.
5. **Handoff** — por último, só quando houver arquivo trocando de mão: arquivo por arquivo, onde cada um vai. Handoff de conversa completa: o artefato se chama `AAMMDD-HANDOFF-BRIEF.md`.
**De quem é este bloco:** da raia de **planejamento** (o assistente no chat). Quem **executa** no Claude Code não fecha assim — fecha com o **relatório de trabalho**: o que fez, o que encontrou que foge do que a tarefa pedia, os arquivos tocados, o resultado do build/validação e o commit. Trocar o relatório por este formulário perde a informação que só quem executou tem.
**Este formato é o ponto de partida, não uma jaula.** Se este projeto tem um dado recorrente que merece linha própria (prazo, custo, publicação, estoque, o que for), acrescente — e se uma linha nunca se aplica aqui, proponha removê-la no refino.
Vale para todo turno de trabalho, não só ao encerrar a conversa: é o que me deixa retomar sem reconstruir contexto.
```

> **Ancora multilinha, extraida do arquivo por script — nao digitada.** Se nao casar, o arquivo mudou depois de
> 2026-08-26 15:21 (geracao do mount que eu li): **PARE e reporte**, nao aproxime.
>
> **O que foi retirado do texto do template, de proposito:** os cinco bullets finais («Sincronia com o CEREBRO»,
> «Uma regra por linha», «Teto», «Teto por configuracao», «Registre») **nao pertencem a esta secao** — eles sao
> do «Refino das Instrucoes do Projeto», e no nosso arquivo ja vivem la (linhas 223-227), na versao adaptada a
> este projeto. No template v1.120.0 eles aparecem no fim do fecho e **somem** da secao de Refino: e defeito do
> pacote, nao conteudo novo. Copiar seria duplicar aqui e regredir la.

## Edicao 5 — `meta/CEREBRO.md` · a tabela de gatilhos INTEIRA

**Ancora**:

```
## Tabela de gatilhos (evento → o que o assistente entrega)

| Evento | O assistente entrega |
|---|---|
| Início de sessão | Lê CEREBRO.md → CONTEXT.md → STATUS.md → última entrada do CHANGELOG. |
| Decisão importante tomada | Entrega o DECISIONS.md completo e atualizado (nova entrada em formato ADR: contexto, decisão, alternativas, consequências). |
| Bug grave resolvido | Entrega o DECISIONS.md completo (nova entrada: sintoma, causa raiz, solução, lição). |
| Ideia mencionada (sua ou minha) | Entrega o IDEAS.md completo com a ideia capturada (na hora, sem pedir). |
| Feedback sobre o kit — dito OU feito (desvio estrutural: diretriz nova neste CEREBRO.md, template alterado/dispensado, arquivo novo criado) | Registra na hora no IDEAS.md, seção «Feedback para o Kit»: o que foi observado/mudado e por quê. É o material que volta para evoluir o kit — sem o registro, o aprendizado deste projeto se perde. |
| Fim de sessão | Entrega os arquivos completos afetados: STATUS.md + CHANGELOG.md (se fechou algo) + log da sessão. |
| Decisão de arquitetura ou troca de lib | Entrega o DECISIONS.md completo (nova DEC-N: contexto, decisão, alternativas, consequências). |
| Mudança de fase do projeto | Entrega o ROADMAP.md completo com a fase atualizada (concluída / em curso / próxima). |
| Termo técnico próprio do projeto usado | Entrega o GLOSSARY.md completo com o termo definido. |

> Se um arquivo da **camada universal** (STATUS, IDEAS, DECISIONS) referenciado acima ainda não existir, o assistente o CRIA na primeira necessidade, a partir do papel descrito. **Arquivo que NÃO faz parte do conjunto deste projeto não é criado por conta própria** — a ausência é intencional, não um erro. Neste projeto o conjunto é: CONTEXT, STATUS, DECISIONS, CHANGELOG, IDEAS, ROADMAP, GLOSSARY, HISTORY, LOG-TEMPLATE, README (em `meta/`) + `logs/` e `meta/workorders/`. `meta/SPEC.md` e `meta/analises/` nascem **no primeiro uso real**, não antes.
```

**Substituir por:**

```
## Tabela de gatilhos (evento → o que o assistente entrega)

| Evento | O assistente entrega |
|---|---|
| Início de turno | Lê CEREBRO.md → CONTEXT.md → STATUS.md → última entrada do CHANGELOG. **Todo turno**, não só ao abrir a conversa. |
| Decisão importante tomada | Entrega o DECISIONS.md completo e atualizado (nova entrada em formato ADR: contexto, decisão, alternativas, consequências). |
| Bug grave resolvido | Entrega o DECISIONS.md completo (nova entrada: sintoma, causa raiz, solução, lição). |
| Ideia mencionada (sua ou minha) | Entrega o IDEAS.md completo com a ideia capturada (na hora, sem pedir). |
| Feedback sobre o kit — dito OU feito (desvio estrutural: diretriz nova neste CEREBRO.md, template alterado/dispensado, arquivo novo criado) | Registra na hora no IDEAS.md, seção «Feedback para o Kit»: o que foi observado/mudado e por quê. É o material que volta para evoluir o kit — sem o registro, o aprendizado deste projeto se perde. |
| Fim de QUALQUER turno de trabalho | Emite o Bloco de fecho (formato fixo, secao propria). Nao espera fim de conversa: a maior parte do trabalho acontece em turnos que nao fecham nada. |
| Fim da conversa | Entrega os arquivos completos afetados: STATUS.md + CHANGELOG.md (se fechou algo) + log do dia. |
| Evento que MERECE log: cortar versao, registrar uma decisao ou um bug grave, virar o dia de trabalho | Escreve `logs/AAAA-MM-DD.md` na hora. O log nao espera o fim da conversa — numa conversa longa o fim nunca chega, e e assim que dias inteiros ficam sem registro. |
| Precisa de um numero sobre material grande demais para a conversa | Manda MEDIR (sonda) em vez de deduzir ou pedir upload. Se ninguem sabe ainda qual e a pergunta, manda EXPLORAR primeiro: exploracao produz hipotese, sonda produz evidencia. |
| Chega ou sai carta de outro projeto (negociacao de contrato entre frentes) | Extrai o durável AGORA — acordo vira decisao registrada, o que nao coube vira ideia com gatilho — e NAO versiona a carta. Se ela pede resposta do outro lado, cria o item de espera com prazo: espera sem gatilho trava o projeto sem ninguem perceber. |
| Uma conferencia deu VERDE — antes de relatar | Pergunte qual das duas perguntas esse verde responde: «esta la?» ou «presta?». Verde de existencia lido como verde de aptidao ja passou por 45 arquivos destruidos por dentro. Se o instrumento nao abre o conteudo, diga isso na MESMA linha do verde, nao no rodape. |
| Uma varredura ou conferencia nao achou NADA no lugar onde deveria achar algo | Confirme que o arquivo chegou ao mount antes de concluir que esta limpo. Cheque `.gitignore` e `.flatdropignore`: pasta excluida produz varredura muda, e silencio de ferramenta nao e ausencia de problema. |
| Vai sobrescrever, mover ou apagar algo que ja existe (arquivo, pasta, config, artefato baixado) | LE antes. E se o dono pediu para NAO apagar algo, pergunte do que ele tem medo: quase sempre a resposta e copiar para fora do espaco de trabalho e seguir — cumprir a letra e deixar o problema de pe e obedecer contra o interesse de quem pediu. |
| A tarefa criou algo FORA do repositorio (processo, porta, servidor de dev, arquivo temporario, download) | Quem abriu, fecha — a tarefa termina com a maquina como a encontrou. O que nao puder ser fechado e DECLARADO no relatorio, com o caminho: e o que ninguem lembra de limpar. |
| Decisão de arquitetura ou troca de lib | Entrega o DECISIONS.md completo (nova DEC-N: contexto, decisão, alternativas, consequências). |
| Mudança de fase do projeto | Entrega o ROADMAP.md completo com a fase atualizada (concluída / em curso / próxima). |
| Termo técnico próprio do projeto usado | Entrega o GLOSSARY.md completo com o termo definido. |

> Se um arquivo da **camada universal** (STATUS, IDEAS, DECISIONS) referenciado acima ainda não existir, o assistente o CRIA na primeira necessidade, a partir do papel descrito. **Arquivo que NÃO faz parte do conjunto deste projeto não é criado por conta própria** — a ausência é intencional, não um erro. Neste projeto o conjunto é: CONTEXT, STATUS, DECISIONS, CHANGELOG, IDEAS, ROADMAP, GLOSSARY, HISTORY, LOG-TEMPLATE, README (em `meta/`) + `logs/` e `meta/workorders/`. `meta/SPEC.md` e `meta/analises/` nascem **no primeiro uso real**, não antes.
```

> **Ancora multilinha, extraida por script.** Oito linhas novas entram na tabela; o paragrafo final e **o NOSSO**,
> preservado palavra por palavra — ele nomeia o conjunto de arquivos deste projeto («Neste projeto o conjunto
> e: ...»), que o template substitui por uma frase generica sobre nichos. Trocar seria perder informacao que so
> existe aqui.

## Edicao 6 — `meta/CEREBRO.md` · a secao de fim de sessao da lugar a de registro

**Ancora**:

```
## Ao final de cada sessão, o assistente entrega (como arquivos completos)

Cada arquivo abaixo vem INTEIRO e atualizado, pronto para você baixar e substituir o antigo. Aplicá-los é decisão sua:

1. STATUS.md — completo e atualizado (rolante: o resolvido sai)
2. CHANGELOG.md — completo, com nova entrada se algo foi concluído
3. DECISIONS.md — completo, com nova DEC/FIX se houve decisão ou bug grave
4. IDEAS.md — completo, com as ideias da sessão capturadas e reclassificadas
5. ROADMAP.md — completo, se alguma fase mudou de estado (quando o projeto usa roadmap)
6. GLOSSARY.md — completo, se surgiu termo novo (quando o projeto usa glossário)
7. logs/AAAA-MM-DD.md — log da sessão preenchido (formato em LOG-TEMPLATE.md)
8. **Fecho do turno** — as linhas que se aplicarem (formato abaixo)
```

**Substituir por:**

```
## Ao final da conversa, o assistente REGISTRA o que falta

**A regra geral — «entregue tudo inteiro» — foi escrita para projeto SEM executor, onde regenerar é a única saída. Aqui ela se inverte:** com um executor no repositório, o registro do fecho é **WO cirúrgica**, e reescrever um documento grande no fim de uma conversa pesada é justamente onde se perde conteúdo.

- **Registrar é o entregável; listar não é.** «O que ainda falta registrar» é o inventário da dívida, não o pagamento dela. Um fecho bom termina com essa lista **vazia** — e o que ficou de fora vira WO agora, nesta conversa, não recado para a próxima.
- **Regenerar ≠ criar.** «Não regenere os arquivos de contexto» existe para não haver dois escritores no mesmo documento. Um arquivo que **não existe** não tem escritor nenhum: escrevê-lo não é regenerar, é criar — e é obrigatório. O log do dia é o caso que mais se perde por essa confusão.
- **Qual canal para qual documento.** Documento grande e vivo → **WO** em `meta/workorders/`, com o texto exato de cada inserção e a linha `/apply-wo` junto. Arquivo **novo**, pequeno, ou que precise de curadoria que reescreve → **inteiro, para baixar**. Nunca os dois no mesmo ciclo para o mesmo documento.
- **Nunca empurre bloco para o usuário colar no executor.** A caixa de mensagem dele tem limite de caracteres — é a razão de a WO existir. **Isso inclui pedido de medição.** Medição não tem âncora nem commit, então não é ordem de trabalho — mas continua sendo um arquivo: um script de sonda, ou um `.md` curto com o que rodar e o formato do relatório. «Não é WO» quer dizer «outro artefato», nunca «vai colado na mensagem». Se o usuário precisou criar o arquivo à mão para caber, o pedido estava errado.

Os arquivos abaixo continuam sendo os afetados por este trabalho — o que muda é o canal de cada um, não a obrigação de registrar:

1. STATUS.md — completo e atualizado (rolante: o resolvido sai)
2. CHANGELOG.md — completo, com nova entrada se algo foi concluído
3. DECISIONS.md — completo, com nova DEC/FIX se houve decisão ou bug grave
4. IDEAS.md — completo, com as ideias da conversa capturadas e reclassificadas
5. ROADMAP.md — completo, se alguma fase mudou de estado (quando o projeto usa roadmap)
6. GLOSSARY.md — completo, se surgiu termo novo (quando o projeto usa glossário)
7. logs/AAAA-MM-DD.md — log do dia preenchido (formato em LOG-TEMPLATE.md)
```

> **Ancora multilinha, extraida por script.** Esta e a unica edicao da fase 2b que **troca a regra**, nao so o
> vocabulario: a nossa secao mandava entregar todo documento afetado INTEIRO; a nova diz que, **num projeto com
> executor, isso se inverte** — documento grande e vivo muda por WO cirurgica, e reescrever um documento grande
> no fim de uma conversa pesada e justamente onde se perde conteudo. E a mesma regra que a wo0054 ja pos nas
> Instrucoes do Projeto; aqui ela chega ao CEREBRO, que e onde mora a versao longa.

## Edicao 7 — `meta/CEREBRO.md` · o titulo da recomendacao de configuracao (uma linha)

**Ancora**:

```
## Recomendação de configuração (fim de sessão)
```

**Substituir por:**

```
## Recomendação de configuração (fim de turno)
```

## Edicao 8 — `meta/CEREBRO.md` · a primeira linha da mesma secao

**Ancora**:

```
No fim de cada sessão, junto do resumo e de qualquer dúvida, avalie o que a **próxima etapa** exige e recomende a configuração de forma **completa e explícita**. Os controles dependem de ONDE se trabalha:
```

**Substituir por:**

```
No fim de cada turno, junto do resumo e de qualquer dúvida, avalie o que a **próxima etapa** exige e recomende a configuração de forma **completa e explícita**. Os controles dependem de ONDE se trabalha:
```

## Edicao 9 — `meta/IDEAS.md` · o defeito do pacote, em «Feedback para o Kit»

**Ancora** (uma linha, primeiro item da secao):

```
- **Número de checklist é DERIVADO do texto da WO, nunca estimado antes dela.** Terceira
```

**Inserir IMEDIATAMENTE ANTES:**

```
- **O pacote v1.120.0 traz cinco bullets do «Refino das Instruções» dentro da seção «Bloco de fecho
  de turno» — e some com eles da seção a que pertencem.** Medido em 2026-08-26, comparando as duas
  versões do CEREBRO: os bullets «Sincronia com o CEREBRO», «Uma regra por linha», «Teto», «Teto por
  configuração» e «Registre» estão nas linhas 304-308 do template, dentro do fecho, e **não** estão
  na seção «Refino das Instruções do Projeto» (linhas 206-219), que é o lugar deles — e onde eles
  vivem no nosso arquivo desde a v1.95.0. Não é conteúdo novo nem reorganização: é bloco deslocado.
  Quem aplicasse o template ao pé da letra duplicaria os cinco no fecho e os perderia no Refino. A
  fase 2b os retirou do texto adotado, de propósito, e isto volta ao kit como defeito de pacote.
```

## Edicao 10 — `meta/STATUS.md` · o estado do merge

**Ancora** (uma linha):

```
   corpo). **Fase 2b e 2c (a fazer):** «Bloco de fecho de turno» (2.797 → 6.861), «Tabela de
```

**Substituir por:**

```
   corpo). **Fase 2b (wo0058, feita):** «Bloco de fecho de turno», «Tabela de gatilhos» (+8 linhas)
   e a seção «Ao final de cada sessão… entrega arquivos completos» substituída por «Ao final da
   conversa, o assistente REGISTRA o que falta» — mais os títulos do ritual e da recomendação de
   configuração. **As 4 ocorrências de «sessão» no CEREBRO foram a zero.** **Fase 2c (a fazer):**
   seções novas «Sonda e exploração» (4.882) e «Correspondência entre projetos» (2.126),
   «Técnicas específicas deste projeto» (765), e os deltas menores em «Análise antes do
   compromisso» (+1.146), «Ao receber um template-update» (+421) e «Princípios» (+391). **Fase 3:**
   os 12 modelos.
```

---

## Fora de escopo

- **Fase 2c:** «Sonda e exploração», «Correspondência entre projetos», «Técnicas específicas deste
  projeto» e os deltas menores («Análise antes do compromisso», «Ao receber um template-update»,
  «Princípios»). **Não encoste.**
- **Fase 3:** os 12 modelos.
- **Os cinco bullets do «Refino»** — ficam onde estão, no Refino. Não os mova, não os duplique.
- Nada de `.claude/`, nada de `flatdrop/`.

## Armadilhas desta WO

- **Três âncoras são seções inteiras** (4, 5 e 6). Foram extraídas do arquivo por script, então
  batem byte a byte com o que está em disco **no mount que eu li**. Se alguma não casar, alguém
  editou o `CEREBRO.md` depois de 26/08 15:21 — **PARE e reporte**, não aproxime nem case «o mais
  parecido».
- **A Edição 4 não é o texto do template inteiro.** Faltam os cinco bullets, de propósito. Se você
  comparar com o pacote e achar que faltou coisa: faltou mesmo, e a razão está em §1.
- A tabela de gatilhos passa de 9 para **17** linhas de dados. Conte depois de aplicar.
- **Ordem:** a Edição 7 troca o título da seção de configuração e a 8 troca a primeira linha dela.
  Se aplicar a 8 antes da 7, tanto faz — as âncoras não se sobrepõem.

---

## Depois de aplicar — conferência antes do commit

- [ ] `git diff` mostra exatamente: `meta/CEREBRO.md`, `meta/IDEAS.md`, `meta/STATUS.md`.
- [ ] **O número que fecha esta fase** — rode e reporte o cru:
      `grep -ncE "de cada sess|fim de sess|início de sess|toda sess" meta/CEREBRO.md` → **0**.
      *(Era 4 depois da fase 2a. Este é um «está lá?», não um «presta?»: ele prova que as
      ocorrências sumiram, não que o texto novo faz sentido.)*
- [ ] Linhas da tabela de gatilhos:
      `sed -n '/^## Tabela de gatilhos/,/^## /p' meta/CEREBRO.md | grep -c "^| "` → **18**
      (17 linhas de dados + o cabeçalho; a linha separadora começa com `|-` e **não** entra nesta
      contagem). Reporte o número cru que saiu. *(Número medido no texto final desta WO, não
      estimado — foi o que a wo0057 registrou como regra.)*
- [ ] Os cinco bullets do Refino continuam **um só de cada**:
      `grep -c "Sincronia com o CEREBRO" meta/CEREBRO.md` → **1**.
- [ ] `grep -c "REGISTRA o que falta" meta/CEREBRO.md` → **1**; e
      `grep -c "Ao final de cada sessão, o assistente entrega" meta/CEREBRO.md` → **0**.
- [ ] `python -m pytest -q` → **122**, sem mudança (WO só de doc).
- [ ] **Invariante DEC-020:** nada em `flatdrop/`.

## Relatório de aplicação *(quem aplica preenche ao terminar)*

O que foi feito · o que fugiu do texto literal · os números crus das quatro conferências · o
commit · **o push, com o resultado real**, escrito DEPOIS de o push estar resolvido. Grave o MESMO
relatório em `../AAMMDD-HHMM-code-flatdrop.txt`.

## Commit — blocos separados, mensagem SEM acento

```
git add meta\CEREBRO.md meta\IDEAS.md meta\STATUS.md meta\workorders\260826-wo0058-merge-kcm-fase2b.md
```

```
git commit -m "chore(kit): merge do KCM v1.120.0 fase 2b - cadencia do trabalho" -m "Bloco de fecho de turno ganha o carimbo Base, a regra de que o Proximo so pede o que o dono sabe produzir e a lista Arquivar/Manter exaustiva. Tabela de gatilhos passa de 9 para 17 linhas (fim de QUALQUER turno, log por evento, sonda, carta de outro projeto, verde de existencia vs de aptidao, varredura muda). A secao de fim de sessao da lugar a REGISTRA o que falta, que inverte a regra num projeto com executor: documento grande muda por WO. Zera as ocorrencias de sessao no CEREBRO. Os cinco bullets do Refino que o pacote deslocou nao foram copiados - o defeito volta ao kit pelo IDEAS."
```

```
git push
```
