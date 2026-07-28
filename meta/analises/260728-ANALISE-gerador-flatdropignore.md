# ANALISE — gerador do editor de `.flatdropignore`

- **Status:** Em discussão
- **Data:** 2026-07-28 (revisada no mesmo dia após crítica do autor)
- **Decisão registrada em:** — (pendente)
- **Virou:** — (pendente)

## Problema

O editor grava o bloco gerenciado enumerando **arquivos**, não declarando **intenção sobre a
pasta**. Um arquivo criado amanhã dentro de uma pasta já curada entra sozinho, sem decisão de
ninguém. Foi a reclamação da nota de 2026-07-23.

## O que foi medido

Rodando `core.build_flatdropignore` de verdade (código 0.12.0):

| Cenário | Bloco gerado hoje | Arquivo novo amanhã |
|---|---|---|
| pasta parcial: `docs/{a,b,c,d}.md`, quero só `a.md` | `docs/b.md` `docs/c.md` `docs/d.md` | **entra** |
| pasta escondida pelo git, quero um filho | `!legacy/` + `legacy/y.md` `legacy/z.md` | **entra** |
| pasta inteira fora | `docs/` | fica fora ✔ |

Os dois ramos que curam vazam para dentro. O único à prova de arquivo novo é o que não cura nada.

**Raio de impacto:** `core.build_flatdropignore` (~45 linhas) · **1** chamador (`gui.py:375`) ·
**5** testes em `tests/test_core.py` (`test_editor_liberate_only_one`,
`test_editor_exclude_keeps_sibling`, `test_editor_roundtrip_preserves_manual`,
`test_editor_collapse_blocks_new_files`, `test_editor_roundtrip_preserves_folder_exclusion`) ·
contrato na **DEC-016**. Invariante **DEC-020 não é tocado** (verificado por leitura).

## A pergunta que decide tudo

> **Arquivo novo numa pasta já curada: entra ou fica fora?**

Não há resposta única. Em `docs/` o autor quer "fica fora"; em `flatdrop/` quer "entra", senão um
módulo novo some do mount em silêncio. Logo, a forma do padrão tem de sair do **gesto** do autor
na GUI, não de uma regra fixa.

O gesto já diz tudo:

| O que o autor faz na UI | O que ele quis dizer | O que deve ser gravado |
|---|---|---|
| pasta **marcada**, desmarca 1 arquivo | "a pasta entra, menos este" | só `pasta/arquivo.md` — novo **entra** |
| pasta **desmarcada**, marca 1 arquivo | "a pasta não entra, menos este" | `pasta/*` + `!pasta/arquivo.md` — novo **fica fora** |
| pasta **desmarcada** inteira | "a pasta não entra" | `pasta/*` — novo **fica fora** |

## Opções

### B — usar sempre `pasta/*` + `!mantidos`
Uma troca localizada, sem mexer em assinatura nenhuma. Resolve o vazamento.
**Limite:** é a linha 2 da tabela aplicada aos três casos. No caso comum oposto — pasta com 20
arquivos, o autor desmarca **um** — obrigaria a escrever `pasta/*` e 19 negações para trazer o
resto de volta, e ainda inverteria o default de "novo entra" para "novo fica fora" numa pasta que
o autor deixou marcada. É a única objeção que existe a B; fora dela, B funciona.
**Quando escolher B:** se a prioridade for fechar isto sem mexer na fronteira GUI↔core.

### C — a forma sai do gesto (a tabela acima, os três casos)
Cobre B e mais os outros dois casos. O que falta **não é a regra, é o encanamento**: hoje a GUI
manda para o gerador só `{arquivo: sim/não}`; o estado da PASTA (o checkbox tri-estado, que a GUI
já calcula em `core.folder_effective_state`) é jogado fora antes de chegar lá. Preservá-lo é o
trabalho. Depois disso a regra são três `if`.
**Custo:** um parâmetro novo no gerador + a GUI preenchendo-o + os 5 testes declarando também a
intenção da pasta. Sem rede automática na GUI → smoke manual no Windows obrigatório.

### D — trocar `pasta/` por `pasta/*` no ramo que já funciona
Uma linha. Hoje o gerador escreve `docs/`, a forma que a DEC-025 desaconselha, dentro do arquivo
onde a regra está comentada. **Depois do FIX-011 é só cosmético** — no FlatDrop as duas formas se
comportam igual. Grátis, não conflita com B nem com C.

## Ponto em aberto que apareceu na revisão

O FIX-011 tornou `pasta/` e `pasta/*` **equivalentes no FlatDrop**: os dois aceitam `!` por dentro.
O autor manifestou preferência pelo contrário — que `pasta/` signifique "nunca entra, nem aparece
na árvore" (exclusão dura, fiel ao git) e só `pasta/*` aceite resgate. As duas posturas são
defensáveis:

- **Permissiva (é o estado atual):** faz o que o autor quis dizer; nunca perde arquivo que ele
  nomeou explicitamente. Custo: some a distinção entre as duas formas, e quem conhece git pode
  estranhar o comportamento diferente.
- **Estrita (a preferência declarada):** duas formas com dois significados úteis — uma dura, uma
  negociável; idêntica ao git, logo previsível para qualquer um. Custo: reintroduz exatamente o
  caso que gerou a reclamação de 23/07, então só é aceitável se a GUI escrever `pasta/*` sozinha e
  o `_TREE` disser em qual forma cada pasta está.

**Isto não é a mesma decisão do gerador** e não deve entrar na mesma WO. Fica registrado aqui e no
IDEAS.

## Recomendação

**D agora** (uma linha, tira a contradição do repo). **C em seguida**, porque é a única que
responde à pergunta em vez de escolher um lado dela. **B** se o autor quiser fechar hoje, com a
ressalva no CHANGELOG de que arquivo novo em pasta curada passa a não subir.

## Riscos

- **Round-trip (DEC-016).** O bloco é reescrito inteiro a cada salvamento. Se um dos dois testes de
  round-trip precisar mudar, isso é mudança de contrato e pede DEC — não é teste velho.
- **Perda silenciosa.** Qualquer forma que deixe arquivo novo fora precisa aparecer no `_TREE`.
  Depois do wo0038 aparece nomeado, mas veja o item do teto (`+N mais`) no IDEAS: pasta grande
  ainda esconde nomes.
- **Pasta vazia / só com subpastas.** `pasta/*` casa filhos diretos; é onde eu esperaria o primeiro
  caso de borda escapar. Teste explícito.

## Ponto de decisão

**B, C ou D-agora-C-depois?** E, separadamente, a forma `pasta/` continua permissiva ou volta a ser
estrita? **A análise para aqui.**
