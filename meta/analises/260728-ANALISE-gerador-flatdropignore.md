# ANALISE — gerador do editor de `.flatdropignore` (`pasta/*` + `!mantido`)

- **Status:** Em discussão
- **Data:** 2026-07-28
- **Decisão registrada em:** — (pendente)
- **Virou:** — (pendente; candidata a wo0040)

## Problema

O editor de `.flatdropignore` da GUI grava o bloco gerenciado enumerando **arquivos**, não
declarando **intenção sobre a pasta**. Consequência: um arquivo criado amanhã dentro de uma
pasta que o autor já curou entra sozinho, sem ninguém decidir nada.

Foi a reclamação da nota de 2026-07-23 ("se adicionasse um novo arquivo a pasta, teria que
ignorar ele também manualmente") e o motivo de o autor achar o fallback frágil na captura de
tela: a caixa da pasta aparecia indeterminada, sugerindo que o editor entendia "pasta fora,
este filho dentro", mas o que ele gravava era outra coisa.

Depois do **FIX-011** (0.12.0) isto deixou de ser bloqueio — a negação `!` funciona nas duas
formas, então nada fica inacessível. Virou dívida de **durabilidade**: o arquivo gerado hoje
descreve corretamente o estado de hoje e não sobrevive ao amanhã.

## Restrições / o que foi medido

Medido no sandbox, chamando `core.build_flatdropignore` de verdade (código da 0.12.0):

| Cenário | `wants` | Bloco gerado hoje | Arquivo novo na pasta amanhã |
|---|---|---|---|
| **Pasta parcial** — `docs/{a,b,c,d}.md`, quero só `a.md` | 3 folhas `False` | `docs/b.md`<br>`docs/c.md`<br>`docs/d.md` | **entra** (não está listado) |
| **Pasta inteira fora** — `docs/{a,b}.md` | 2 folhas `False` | `docs/` | fica fora ✔ (é o que o `test_editor_collapse_blocks_new_files` garante) |
| **Pasta escondida pelo git, quero um filho** — `.gitignore` com `legacy/`, quero `legacy/x.md` | 1 folha `True` | `!legacy/`<br>`legacy/y.md`<br>`legacy/z.md` | **entra** (o `!legacy/` liberou a pasta toda) |

Ou seja: **os dois ramos vazam para dentro**. O ramo que colapsa a pasta cheia é o único
à prova de arquivo novo — e é justamente o caso em que não há nada a curar.

Achado lateral da mesma rodada: o ramo do colapso emite `docs/` (forma pasta), a forma que a
**DEC-025** desaconselha. Não quebra mais nada depois do FIX-011, mas contradiz por escrito a
convenção do próprio projeto — e é o `.flatdropignore` que o editor grava por cima.

**Raio de impacto** (contado no repo, não estimado):
- `core.build_flatdropignore` — 1 função, ~45 linhas.
- **1** chamador na GUI (`gui.py:375`), dentro do salvamento do editor.
- **6** referências em `tests/test_core.py`, em **5** testes: `test_editor_liberate_only_one`,
  `test_editor_exclude_keeps_sibling`, `test_editor_roundtrip_preserves_manual`,
  `test_editor_collapse_blocks_new_files`, `test_editor_roundtrip_preserves_folder_exclusion`.
- Contrato escrito na **DEC-016** (round-trip, preservar linhas fora do bloco) e na spec0018.
- **Invariante DEC-020 não é tocado:** `cli.py`, `_build_cli_args`, `_generate_bat` e `_sources`
  não participam deste caminho. Verificado por leitura.

**Limite que a solução tem de respeitar:** o round-trip da DEC-016 (o que o autor escreveu fora
do bloco gerenciado continua intocado) e o comportamento do colapso de pasta cheia, que já é
correto e tem teste.

## A pergunta que estava escondida

O defeito parece um detalhe de sintaxe, mas embaixo dele há uma pergunta de produto que o
projeto nunca respondeu por escrito:

> **Um arquivo criado amanhã dentro de uma pasta parcialmente curada — entra ou fica fora?**

Hoje a resposta é sempre **entra**. Trocar para `pasta/*` + `!mantido` torna a resposta sempre
**fica fora**. Nenhuma das duas está certa para toda pasta: em `docs/` o autor provavelmente
quer "fica fora"; em `flatdrop/` (código) quer "entra", senão um módulo novo some do mount sem
aviso — e some silenciosamente, que é o pior tipo de perda para esta ferramenta.

Por isso a opção mais óbvia (trocar a forma em todo lugar) não é a recomendada.

## Opções consideradas

### A — Não mexer
Custo zero. O `.flatdropignore` continua correto no dia em que é gravado e vai apodrecendo;
o autor descobre o vazamento quando um arquivo indesejado aparece no mount — ou não descobre.
**Descartada:** a reclamação é real e o custo de arrumar é baixo.

### B — Sempre `pasta/*` + `!mantido` nas pastas parciais
Uma troca localizada nos dois ramos de `build_flatdropignore`. Resolve o vazamento em todas as
pastas de uma vez.
**Descartada como padrão:** inverte o default para "arquivo novo fica de fora" **em toda pasta**,
inclusive nas de código, onde some sem aviso. Também fica verboso no caso comum oposto (pasta com
20 arquivos e 1 excluído viraria `pasta/*` + 19 negações).

### C — A intenção da PASTA decide a forma
O editor já sabe o que o autor quis: a caixa da pasta é tri-estado
(`core.folder_effective_state` devolve `True`/`False`/`None`). O que se perde é o caminho até o
gerador — `wants` só carrega folhas (`{rel_arquivo: bool}`), então a intenção da pasta é jogada
fora antes de chegar em `build_flatdropignore`.

Com ela preservada:
- pasta **desmarcada** com filhos remarcados → `pasta/*` + `!filho` (novo fica **fora**);
- pasta **marcada** com filhos desmarcados → lista os desmarcados (novo **entra**);
- pasta cheia fora → `pasta/*` (hoje `pasta/`), alinhando com a DEC-025.

Cada `.flatdropignore` passa a descrever a intenção real, pasta por pasta. Custo: `wants` ganha
entradas de pasta (ou um segundo dicionário), a GUI passa a mandá-las, e os 5 testes do editor
precisam declarar a intenção da pasta além das folhas.
**É a opção que responde à pergunta escondida em vez de escolher um lado dela.**

### D — Só trocar `pasta/` por `pasta/*` no ramo do colapso
Uma linha. Alinha o gerador com a DEC-025 e não muda semântica nenhuma (com FIX-011, as duas
formas se comportam igual; a forma nova é a que o projeto documenta).
**Não resolve o problema**, mas é grátis e não conflita com C.

### E — Tornar configurável (toggle "à prova de arquivo novo")
**Descartada:** superfície de UI nova para uma pergunta que o gesto do autor já responde. Se C
funcionar, o toggle vira redundante; se não funcionar, o toggle empurra a decisão para o usuário
toda vez, que é o oposto de curar uma vez.

## Recomendação

**D agora, C em seguida** — e nesta ordem, porque são independentes.

**D** é um ajuste de uma linha no ramo que já está correto, cabe em qualquer WO de passagem e
tira do repo a contradição de o gerador escrever a forma que a DEC-025 desaconselha.

**C** é a resposta certa ao problema, e o trabalho real está no *plumbing*, não na regra: levar
a intenção da pasta da GUI até o gerador. A regra em si são três ramos claros. Vale escrever a
WO com os 5 testes existentes reescritos junto, porque é neles que a mudança de contrato aparece.

**B** é o que eu faria se o autor quisesse fechar isso hoje sem mexer na assinatura de `wants` —
com uma ressalva que precisa estar no CHANGELOG: a partir daí, arquivo novo em pasta curada
**não sobe** até alguém liberar.

## Riscos

- **Round-trip (DEC-016).** É o contrato mais fácil de quebrar sem perceber: o bloco gerenciado
  é reescrito inteiro a cada salvamento. `test_editor_roundtrip_preserves_manual` e
  `test_editor_roundtrip_preserves_folder_exclusion` são a rede — se algum deles precisar mudar,
  isso é sinal de mudança de contrato, não de teste velho, e pede DEC.
- **Silêncio na direção errada.** Qualquer opção que faça arquivo novo ficar de fora precisa
  aparecer no `_TREE.md` — e depois do wo0038 aparece: sai nomeado em
  `[pulados por flatdropignore: ...]`. Vale conferir isso no smoke, porque é a única coisa que
  separa "curadoria" de "arquivo sumiu".
- **Pasta vazia e pasta só com subpastas.** `pasta/*` casa filhos diretos; a lógica de
  `fully_excluded`/`maximal` já lida com aninhamento, mas é onde eu esperaria o primeiro caso
  de borda escapar. Teste explícito.
- **Custo de rodada:** C mexe na fronteira GUI↔core, e a GUI **não é coberta pela suíte**. O
  smoke manual no Windows deixa de ser opcional.

## Ponto de decisão

**Qual opção?** Se for **C**, uma pergunta a mais antes da WO: a intenção da pasta viaja como
entradas dentro do próprio `wants` (`{"docs": False}` ao lado das folhas) ou como um segundo
parâmetro (`folder_wants`)? A primeira é menos código e mais fácil de esquecer; a segunda é
explícita e muda a assinatura pública do gerador.

**A análise para aqui.**
