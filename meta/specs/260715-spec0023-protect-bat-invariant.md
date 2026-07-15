# spec0023 — Invariante permanente: proteger o `.bat` e o núcleo comprovado

- **Tipo:** meta-only (docs). NÃO altera código, NÃO precisa de testes (a rede é o `git diff`).
- **Data:** 2026-07-15
- **Por que existe / por que separada da implementação.** O autor determinou que o gerador
  e o uso de `.bat` são a peça mais valiosa da ferramenta e não podem ser degradados por
  conveniências (ex.: persistência). Esta spec grava esse freio como **invariante
  permanente**, aplicada e commitada **ANTES** da implementação (spec0024). Assim, se um dia
  a persistência precisar ser revertida, o invariante e a lição **sobrevivem** ao revert —
  não ficam acoplados ao código que pode sumir.
- **Ordem:** aplicar e commitar ESTA spec primeiro; só depois a spec0024.

Três edições de doc, todas por âncora exata. Nada de código.

---

## Edit 1 — Append DEC-020 ao fim de `meta/DECISIONS.md`

**Âncora semântica:** a última linha do bloco **DEC-019**, que é exatamente:

> `vivo < `.bat`/CLI. Geometria de janela fica de fora (ideia futura).`

Inserir DEPOIS dessa linha (uma linha em branco antes):

```
## DEC-020 — Invariante: proteger o `.bat` e o núcleo comprovado acima de features novas
**Data:** 2026-07-15 · **Status:** aceita (invariante permanente)

**Contexto.** O gerador e o uso de `.bat` são, até aqui, a funcionalidade mais útil e
prática do FlatDrop (snapshot reproduzível da config, roda sem abrir a GUI). O autor
determinou explicitamente que estragar isso por causa de uma conveniência (ex.: persistência
de config) seria a pior das decisões — pior do que não ter a conveniência.

**Decisão.** Fica registrado como invariante permanente do projeto: nenhuma funcionalidade
nova pode degradar o `.bat`, nem outra função de valor já comprovada (a paridade GUI×`.bat`
do FIX-004, a renomeação à prova de colisão, a poda visível do FIX-001, o `.flatdropignore`
correto). Concretamente: (1) a CLI e o gerador de `.bat` (`flatdrop/cli.py`,
`gui._build_cli_args`, `gui._generate_bat`, `gui._sources`) são **intocáveis** por features
de conveniência — persistência/estado de GUI NUNCA os alcança nem é lido pela CLI; (2) se
alguma tarefa futura só puder avançar mexendo nesse caminho, o assistente **PARA e reporta
ao autor**, de forma clara, **MAIS DE UMA VEZ** e marcada como **URGENTE**, ANTES de
priorizar a feature — nunca segue no automático; (3) se ainda assim o `.bat` for quebrado,
aplica-se a doutrina do autor: **regredir** para antes da feature, **limpar todo o vestígio**
e registrar aqui um **FIX** proibindo repetir o erro.

**Consequência.** Toda conversa futura (chat e Code) herda esse freio: conveniência jamais
tem precedência sobre o núcleo comprovado sem aprovação explícita e consciente do autor. Uma
guarda automatizada (`test_cli_has_no_settings`, spec0024) falha alto se a persistência
vazar para a CLI. Este DEC é apontado no `meta/CONTEXT.md` (armadilhas) e no `CLAUDE.md`
para ser lido no ritual de início das duas raias.
```

## Edit 2 — Bullet em `meta/CONTEXT.md` (seção "Armadilhas conhecidas")

**Âncora semântica:** o último bullet da seção, que termina nas linhas:

> `- **Multi-fonte e raiz comum.** Caminhos do manifesto relativos à raiz comum;`
> `  raízes em drives diferentes (Windows) caem em modo degradado. Dedup por caminho real.`

Inserir DEPOIS desse bullet (ainda dentro da seção, antes de `## Convenções`):

```
- **O `.bat` é intocável por conveniência (DEC-020).** O gerador/uso de `.bat` é a peça
  mais valiosa da ferramenta. Nenhuma feature nova pode degradá-lo; a CLI nunca lê estado de
  GUI/persistência. Se uma tarefa só avançar mexendo nesse caminho, PARE e reporte ao autor,
  claro e mais de uma vez, como URGENTE, antes de priorizar a feature.
```

## Edit 3 — Bullet em `CLAUDE.md` (raiz; seção "Convenções")

**Âncora semântica:** o último bullet de Convenções, exatamente:

> `- Ao aplicar uma spec de `meta/specs/`: ache cada âncora EXATAMENTE; se não achar, PARE e reporte — não chute lugar próximo. Não mexa fora das edições nomeadas. `git diff` antes do commit.`

Inserir DEPOIS dessa linha:

```
- **Invariante — proteger o `.bat` (DEC-020).** O gerador/uso de `.bat` é o núcleo mais
  valioso; NÃO o quebre por conveniência. `flatdrop/cli.py`, `gui._build_cli_args`,
  `gui._generate_bat` e `gui._sources` são intocáveis por features de estado/persistência.
  Se algo só avançar mexendo neles, PARE e reporte ao autor — claro, mais de uma vez, como
  URGENTE — antes de priorizar a feature.
```

## Commit sugerido (sem acento)

```
git add meta/DECISIONS.md meta/CONTEXT.md CLAUDE.md meta/specs/260715-spec0023-protect-bat-invariant.md & git commit -m "docs(guardrail): DEC-020 invariante de protecao ao .bat" -m "Registra que o gerador/uso de .bat e outras funcoes comprovadas nao podem ser degradados por conveniencia; a CLI nunca le estado de GUI. Se uma tarefa exigir mexer nesse caminho, parar e reportar ao autor mais de uma vez como urgente antes de priorizar. Aponta o invariante no CONTEXT e no CLAUDE.md."
```
