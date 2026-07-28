# ANALISE — gerador do editor de `.flatdropignore`

- **Status:** Em discussão — com recomendação fechada (rev. 3, após proposta do autor)
- **Data:** 2026-07-28
- **Decisão registrada em:** — (pendente)
- **Virou:** — (pendente)

## Onde o problema realmente está

**A linguagem já resolve tudo.** Quem escreve o `.flatdropignore` na mão — pessoa ou agente —
consegue expressar qualquer intenção, de forma curta, hoje. Verificado rodando `make_plan` de
verdade na 0.12.0:

| O que se quer | Como se escreve | Arquivo novo na pasta |
|---|---|---|
| pasta entra, menos um arquivo | `pasta/arquivo.md` | **entra** |
| pasta não entra, menos um arquivo | `pasta/*` + `!pasta/arquivo.md` | **fica fora** |
| pasta não entra, ponto | `pasta/*` | fica fora |
| abrir pasta que o `.gitignore` fechou | `!pasta/*` | entra |
| abrir pasta do git e tirar um | `!pasta/*` + `pasta/y.md` | entra |

Nenhuma dessas linhas precisa de código novo. **O defeito é só do editor da GUI** — ele é a
única peça incapaz de dizer o que a pessoa quis.

## Por que o editor não consegue

Ele tem **um** controle (o checkbox tri-estado) tentando expressar **duas** coisas independentes:

1. *este arquivo sobe?* — por arquivo;
2. *o que aparecer aqui depois sobe?* — por pasta.

E o checkbox da pasta não é uma escolha: é um **agregado** dos filhos. `folder_effective_state`
devolve `True`/`False`/`None` a partir das folhas — "indeterminado" quer dizer "os filhos estão
misturados", não "o autor decidiu algo sobre a pasta".

Correção de uma afirmação anterior desta análise: eu disse que a intenção da pasta "é jogada fora
no caminho até o gerador". Não é — **ela nunca existiu**. Não há o que plumbar; há um controle a
criar.

## Solução recomendada — trava por pasta (proposta do autor, refinada)

Uma coluna nova na árvore do editor, ao lado do nome da pasta: um **botão de trava**, que não é
checkbox e não se mistura com eles. A trava responde a uma única pergunta, e é literalmente a
frase do tooltip:

> **"Arquivo novo aqui: entra ou não entra?"**

| Trava | Significado | Gerador escreve |
|---|---|---|
| 🔓 **aberta** (padrão) | o que aparecer aqui entra | só os arquivos desmarcados: `pasta/x.md` |
| 🔒 **fechada** | o que aparecer aqui não entra | `pasta/*` + um `!pasta/y.md` por arquivo marcado |
| 🔒 **(git)** | fechada pelo `.gitignore`, herdada — não foi o autor | nada (já está fora) |
| 🔓 **(liberada)** | o autor abriu uma que o git fechava | `!pasta/*` + os desmarcados |

Os checkboxes dos arquivos continuam exatamente como são: dizem apenas *este* sobe ou não. A trava
cuida do futuro; o checkbox cuida do presente. Nenhuma negação é escrita sem necessidade — em
pasta aberta o gerador nunca emite `!`, e em pasta fechada nunca lista exclusão.

**Por que isto resolve de verdade:** a trava não é derivada de nada. É a única informação que
faltava, e ela chega ao gerador como um dado próprio, não como palpite sobre os filhos.

### Verificado antes de recomendar

As quatro formas que o gerador passaria a emitir foram medidas na 0.12.0, com varredura real:

- `!legacy/*` abre pasta fechada pelo git — e **arquivo novo entra**.
- `!legacy/*` + `legacy/y.md` abre e tira um — o resto entra.
- `legacy/*` + `!legacy/x.md` deixa só `x.md` — e **arquivo novo fica fora**. É a garantia central.
- `!legacy/` e `!legacy/*` se comportam igual; dá para padronizar em `/*` (DEC-025) sem perda.

## Custo e raio de impacto

- **GUI:** coluna nova + estado da trava por pasta + leitura do `.gitignore` para pintar a herdada.
  É o grosso do trabalho. **Não tem rede de testes** (a suíte não cobre tkinter) → smoke manual no
  Windows deixa de ser opcional.
- **core:** `build_flatdropignore` ganha a intenção da pasta e passa a ter três ramos claros no
  lugar da heurística atual. ~45 linhas reescritas.
- **Testes:** os 5 do editor precisam declarar também a trava. Um deles muda de resposta de
  propósito: `test_editor_collapse_blocks_new_files` hoje afirma que desmarcar todos os filhos
  vira `logs/` — isso era o palpite que a trava substitui. Passa a exigir trava fechada.
  **Essa é a mudança de contrato da DEC-016 e precisa de DEC própria.**
- **Invariante DEC-020:** não é tocado (`cli.py`, `_build_cli_args`, `_generate_bat`, `_sources`
  não participam deste caminho).

## Detalhes a decidir na WO (não bloqueiam a decisão)

- **Todos os filhos desmarcados com a trava aberta** gera N linhas em vez de um `pasta/*`. É a
  leitura honesta do gesto. Vale a GUI perguntar uma vez: *"desmarcou tudo — quer fechar a pasta?"*
- **Pasta aninhada:** a trava da filha vale sobre a da mãe. Caso de borda a testar explicitamente.
- **Forma:** emitir `pasta/*` e `!pasta/*` em tudo (DEC-025), já que se comportam igual.

## Riscos

- **Dois controles na mesma linha** podem confundir. Mitigação: coluna separada, ícone de cadeado,
  e o tooltip com a frase inteira — não abreviar para "ignorar pasta", que é justamente a
  ambiguidade de hoje.
- **Round-trip (DEC-016):** o bloco é reescrito inteiro a cada salvamento; o que está fora dele
  continua intocado. Os dois testes de round-trip são a rede.
- **Perda silenciosa:** trava fechada esconde arquivo novo. Só é aceitável porque o `_TREE` agora
  nomeia o que foi pulado — e é por isso que o teto `(+N mais)` virou frente aberta no IDEAS.

## Alternativas descartadas

- **Sempre `pasta/*` + `!mantidos`** (opção B das revisões anteriores): força trava fechada em toda
  pasta. Numa pasta de 20 arquivos com um desmarcado, viram 19 negações — e inverte o padrão de
  "novo entra" onde o autor não pediu isso.
- **Toggle global "à prova de arquivo novo"**: empurra a decisão para o usuário a cada salvamento,
  em vez de deixá-la registrada por pasta, que é onde ela varia.
- **Trocar só `pasta/` por `pasta/*` no gerador** (opção D): cosmético depois do FIX-011; entra de
  graça junto, mas não resolve nada sozinho.

## Ponto de decisão

**Aprova a trava por pasta como desenho?** Se sim, a WO sai em duas partes — core + testes
primeiro (tem rede), GUI depois (só smoke) — e a mudança de contrato do
`test_editor_collapse_blocks_new_files` vira DEC. **A análise para aqui.**
