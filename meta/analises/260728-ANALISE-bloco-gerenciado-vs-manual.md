# ANALISE — o bloco gerenciado do `.flatdropignore` nao convive com edicao manual

- **Status:** Em discussão — **desenho revisado em 2026-08-02**, agora com protótipo medido
- **Data:** 2026-07-28 (revisão: 2026-08-02)
- **Decisão registrada em:** — (pendente; candidata a FIX-012)
- **Virou:** — (pendente)

## Problema

Um `.flatdropignore` com regras escritas à mão **fora** do bloco `# >>> flatdrop-editor` para de
funcionar corretamente com o editor: travar/destravar não tem efeito, e o arquivo acumula cópias.
Relatado pelo autor com o `.flatdropignore` deste próprio repo, que é exatamente assim — a parte
de cima é curadoria manual comentada, a de baixo é o bloco.

## Reproduzido

Sandbox, código da 0.13.0, arquivo montado como o real (parte manual + bloco vazio):

```
# comentario do autor
logs/*
meta/w/*
INSTRUCOES.md
# >>> flatdrop-editor
# (sem alteracoes)
# <<<
```

| Gesto na GUI | Bloco gerado | O que deveria acontecer |
|---|---|---|
| salvar **sem mexer em nada** | `logs/*` … não; sai `meta/w/*` + `INSTRUCOES.md` | bloco vazio — nada mudou |
| **destravar** `logs` | `meta/w/*` + `INSTRUCOES.md` (o `logs/*` só some do bloco) | `!logs/*`, para vencer a linha manual |
| marcar `logs/a.md` | `logs/*` + … + `!logs/a.md` | o `!` está certo, mas vem junto de duplicatas |

Ou seja: **destravar é desfeito em silêncio** (a linha manual continua lá; reabrir o editor mostra
a pasta travada de novo) e **o bloco duplica** o que já existia fora dele.

Observação lateral do mesmo teste: `source("logs/", is_dir=True)` devolve `""` para pasta fechada
por `logs/*`. É a mesma armadilha da DEC-027 — `pasta/*` não casa `pasta/` como diretório —, então
a GUI não consegue rotular `travada (manual)` como rotula `travada (git)`.

## Causa raiz

O gerador foi escrito com uma premissa que deixou de valer: **a base de comparação é o "git
puro"** (`git_in`), herdada de quando o bloco era o único conteúdo do `.flatdropignore`. Ele
compara o estado desejado com o que o `.gitignore` faria — e é cego para a curadoria manual do
próprio `.flatdropignore`. Sendo cego, ele nem sabe que existe algo a corrigir: não duplica de
propósito (não vê a linha de fora) e não emite o `!` de destravamento (não vê o que precisa
vencer).

Agravante estrutural: **nada garante que o bloco fique por último**. Vale a última regra que casa;
se o autor escrever qualquer coisa depois do `# <<<`, ela vence o bloco em silêncio.

## Medições de 2026-08-02 (protótipo, não implementação)

Tudo abaixo foi **medido** contra o código da **0.14.0** — a análise original media a 0.13.0 e
estimava o resto. O protótipo troca só a base de comparação (passos 1 e 2) e roda em sandbox.

**Os três sintomas continuam idênticos na 0.14.0**, e o protótipo corrige os três:

| Gesto | Hoje (0.14.0) | Protótipo (passos 1+2) |
|---|---|---|
| salvar sem mexer em nada | `logs/*` · `meta/w/*` · `INSTRUCOES.md` | `# (sem alteracoes)` |
| destravar `logs` | `meta/w/*` · `INSTRUCOES.md` *(o `logs/*` só some do bloco)* | `!logs/*` |
| marcar `logs/a.md` em pasta travada | as três duplicatas **+** `!logs/a.md` | `!logs/a.md` |

**O round-trip aguenta** (era o risco nº 1): salvar duas vezes seguidas devolve o mesmo bloco, e
o `.flatdropignore` real deste repo — onde hoje TUDO está dentro do bloco e só há comentário fora
— continua saindo com as quatro regras, `!meta/workorders/_TEMPLATE.md` inclusive. **Ressalva
medida:** o protótipo acrescenta uma linha em branco por salvamento; a implementação real precisa
de um teste de estabilidade **textual**, não só semântica.

**O passo 3 é necessário, não cosmético.** Montado o caso em que o bloco manda `!logs/*` e uma
linha manual **depois** do marcador de fechamento manda `logs/*`: o arquivo obedece à linha de
fora, e os passos 1+2 sozinhos escrevem `# (sem alteracoes)` — o editor concorda com um estado que
não é o que ele mostra na tela. Sem o passo 3, esse caso fica quebrado.

### Defeito NOVO, encontrado ao medir: os marcadores são procurados por substring

`build_flatdropignore` localiza o bloco com `existing_text.split(MARK)` — **substring, primeira
ocorrência**. Se o arquivo **mencionar** o marcador num comentário (documentando a própria
convenção, que é o uso mais natural do mundo), o gerador corta ali: injeta o bloco **no meio da
linha de comentário**, deixa o bloco antigo no fim, e o resto da frase truncada vira uma linha sem
`#` — ou seja, **vira padrão ativo**. Medido com o `.flatdropignore` deste repo entregue em 01/08,
que documentava a regra citando os dois marcadores: 35 linhas viraram 42, com dois blocos.

É defeito **independente** do bug principal, mais barato de corrigir e mais destrutivo quando
dispara. Vira o **passo 0**.

## Correção desenhada

**Princípio: o bloco gerenciado é um *diff* contra tudo o que já existe — nunca uma cópia.**

0. **Marcadores por LINHA EXATA, não por substring.** Localizar o bloco procurando a linha cujo
   `strip()` é igual ao marcador. Se houver mais de uma linha-marcador de abertura (ou de
   fechamento), **não salvar** e avisar: o arquivo está ambíguo e reescrevê-lo destruiria conteúdo.
   Independente dos demais passos, e o único que corrige perda de dado.
1. **Baseline correta.** Além do estado efetivo (que já é calculado), calcular um segundo spec a
   partir de `gitignore + flatdropignore SEM o bloco gerenciado`. `_collect_ignore_lines` ganha um
   parâmetro para pular o bloco ao ler o arquivo da raiz — os marcadores sobrevivem à leitura
   (`_read_ignore_lines` devolve as linhas cruas, comentários inclusive), então o corte é direto.
2. **Emitir só o que diverge.** Para cada pasta e cada arquivo: se o estado desejado já é o que a
   baseline produz, **não escrever nada**; se diverge, escrever a linha que corrige — inclusive
   `!pasta/*` para abrir o que a parte manual fechou. Isso mata a duplicação e faz o destravar
   funcionar, com a mesma regra.
3. **Garantir a posição.** O bloco passa a ser sempre reescrito no **fim** do arquivo. Se havia
   conteúdo depois dele, ele sobe para antes do bloco — com um comentário dizendo que foi movido.
4. **Rotular a origem na GUI.** `travada (manual)` ao lado de `travada (git)`, usando a sonda de
   arquivo inexistente em vez da sonda de diretório (que não funciona com a forma `/*`).

**Tamanho — agora medido para os itens 1 e 2**, estimado para o resto. O protótipo que corrige
os três sintomas tem **~35 linhas** de emissão (a tabela de 4 casos do docstring vira uma
comparação só: *o desejado difere do que a baseline já faz?*) mais um parâmetro em
`_collect_ignore_lines` para pular o bloco na leitura. O passo 0 é ~10 linhas na localização do
bloco; o passo 3 é local à escrita final; o passo 4 é GUI. Os 8 testes do editor precisam ganhar
**quatro** casos: linha manual fora do bloco, destravar sobre linha manual, estabilidade textual
em dois salvamentos e marcador citado em comentário — hoje **nenhum deles cobre nada disso**, e é
por isso que a suíte passou verde com o bug presente.

## Riscos

- **Round-trip (DEC-016).** É o contrato que esta correção mais estica: o bloco passa a depender do
  que está fora dele. Um teste de estabilidade (salvar duas vezes seguidas dá o mesmo texto) tem
  de existir para o caso com parte manual.
- **Mover conteúdo do autor** (item 3) é a única parte que mexe em texto que não é da ferramenta.
  Se parecer arriscado, a alternativa é **avisar** em vez de mover — pior UX, risco zero.
- **Deriva de espaço em branco.** Medida no protótipo: uma linha em branco a mais por salvamento.
  Bug pequeno, mas é exatamente o tipo que passa por teste semântico e some do radar até o arquivo
  ficar feio. O teste de estabilidade tem de comparar **texto**, não só o conjunto de regras.
- **A correção reduz o bloco.** Depois dela, o `.flatdropignore` deste repo teria o bloco quase
  vazio, porque tudo já está na parte manual. Isso é o certo, mas vai parecer que "sumiu" — vale
  dizer no CHANGELOG.

## Contorno enquanto não é corrigido

Num mesmo `.flatdropignore`, **use a curadoria manual OU o editor**, não os dois. Este repo está
no modo manual: a parte de cima está correta e o bloco tem duplicatas inofensivas (as linhas de
dentro repetem as de fora, sem mudar o resultado). Não use o editor aqui até a correção.

## Ponto de decisão

Três perguntas, na ordem em que travam o trabalho:

1. **O passo 0 sai na frente, sozinho?** É um bug de perda de dado, isolado dos demais, e o
   arquivo deste repo já pisou nele. Recomendação: **sim** — WO própria, aplicável hoje.
2. **Aprova o desenho dos passos 1–4?** Os passos 1 e 2 estão medidos (tabela acima); 3 e 4
   seguem como desenho.
3. **O passo 3 MOVE o conteúdo que estiver depois do bloco, ou só AVISA?** A regra de higiene
   adotada na DEC-028 («nunca apagar nem desfazer o que não é seu», e o bloco gerado fica no FIM)
   abre uma **terceira opção que esta análise não tinha**: mover **o próprio bloco** para o fim,
   em vez de mover o texto da pessoa. É a ferramenta mexendo no que é dela — sem o risco do
   item 3 original e sem a UX ruim de só avisar. Recomendação: **mover o próprio bloco**, e avisar
   apenas quando isso mudar o resultado efetivo de alguma regra.

**A análise para aqui.**
