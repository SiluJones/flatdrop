# ANALISE — o bloco gerenciado do `.flatdropignore` nao convive com edicao manual

- **Status:** Em discussão (bug aberto na 0.13.0)
- **Data:** 2026-07-28
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

## Correção desenhada

**Princípio: o bloco gerenciado é um *diff* contra tudo o que já existe — nunca uma cópia.**

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

**Tamanho estimado** (não medido — é estimativa): itens 1 e 2 são o núcleo, ~30 linhas em
`build_flatdropignore` mais um parâmetro em `_collect_ignore_lines`; item 3 é local à escrita
final; item 4 é GUI. Os 8 testes do editor precisam ganhar um caso com linha manual fora do bloco
— hoje **nenhum deles cobre isso**, e é por isso que a suíte passou verde com o bug presente.

## Riscos

- **Round-trip (DEC-016).** É o contrato que esta correção mais estica: o bloco passa a depender do
  que está fora dele. Um teste de estabilidade (salvar duas vezes seguidas dá o mesmo texto) tem
  de existir para o caso com parte manual.
- **Mover conteúdo do autor** (item 3) é a única parte que mexe em texto que não é da ferramenta.
  Se parecer arriscado, a alternativa é **avisar** em vez de mover — pior UX, risco zero.
- **A correção reduz o bloco.** Depois dela, o `.flatdropignore` deste repo teria o bloco quase
  vazio, porque tudo já está na parte manual. Isso é o certo, mas vai parecer que "sumiu" — vale
  dizer no CHANGELOG.

## Contorno enquanto não é corrigido

Num mesmo `.flatdropignore`, **use a curadoria manual OU o editor**, não os dois. Este repo está
no modo manual: a parte de cima está correta e o bloco tem duplicatas inofensivas (as linhas de
dentro repetem as de fora, sem mudar o resultado). Não use o editor aqui até a correção.

## Ponto de decisão

**Aprova o desenho (1–4)?** E o item 3 move o conteúdo ou só avisa? **A análise para aqui.**
