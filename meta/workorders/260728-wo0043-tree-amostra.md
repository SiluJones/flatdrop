# wo0043 — `_TREE`: mostrar a FAIXA em vez de so o comeco (+ registro do que ficou aberto)

**Data:** 2026-07-28 · **Autor:** chat · **Aplicar com:** `/apply-wo meta/workorders/260728-wo0043-tree-amostra.md`

> **Mexe em CODIGO** — rode `python -m pytest -q`.
> Fecha o item 4 do backlog. As Edicoes 6-9 sao registro do bug aberto do editor (nao corrigido
> aqui) e do feedback ao kit — o projeto entra em stand-by depois desta WO.

## Problema

Depois do wo0038 o `_TREE` nomeia o que foi ignorado, mas com **teto simples**: mostra os 10
primeiros e conta o resto (`+29 mais`). O autor apontou, com razao, que isso nao resolve o que a
feature prometia — nao da para escolher o que liberar sem saber quais sao os 29. Despejar tudo
tambem nao serve: uma pasta de 100 arquivos inunda a arvore.

## Decisao de desenho

**Primeiros N + ultimos N, com o meio contado.** Pelo mesmo orcamento de linha, ver as duas
pontas de uma lista ORDENADA entrega o que o teto simples escondia: a **faixa** e a **ordem**.
Numa pasta de arquivos datados (`workorders/`, `logs/`) o ultimo nome e justamente o que diz ate
onde a colecao vai — e era sempre ele que sumia.

**O `_TREE` orienta; nao indexa.** O indice completo de uma pasta grande e trabalho do editor da
GUI, que ja mostra tudo e ja deixa marcar. Fazer a arvore competir com ele so incharia o mount —
que e exatamente o problema que o FlatDrop existe para resolver. Fica registrado como escolha,
nao como omissao.

## Edicao 1 — `flatdrop/config.py`

**Ancora:**

```python
TREE_NAME_CAP = 10
```

**Substituir por:**

```python
TREE_NAME_CAP = 10

# Amostra de lista longa no _TREE.md (wo0043): quantos nomes das PRIMEIRAS e das ULTIMAS
# posicoes aparecem, com o meio contado entre eles. Ver so o comeco esconde a faixa — e numa
# pasta de arquivos datados e o ultimo nome que diz ate onde a colecao vai. A soma dos dois
# e o orcamento de nomes por pasta; nao vale subir sem medir o inchaco no mount.
TREE_NAME_HEAD = 6
TREE_NAME_TAIL = 4
```

## Edicao 2 — `flatdrop/core.py`: o amostrador

**Ancora:**

```python
def _peek_children(abs_dir: Path) -> list[str]:
```

**Inserir ANTES dela:**

```python
def _tree_amostra(nomes: list[str]) -> list[str]:
    """Amostra legivel de uma lista longa: as PRIMEIRAS e as ULTIMAS, com o meio contado.

    Recebe a lista JA ORDENADA. Ate ``HEAD + TAIL`` nomes devolve tudo; acima disso devolve
    as duas pontas e uma linha no meio com quantos ficaram de fora e o total. E o que permite
    a quem le o _TREE saber a FAIXA da colecao — o teto simples (wo0038) mostrava so o comeco,
    entao uma pasta de 39 workorders parecia parar no decimo.
    """
    n = len(nomes)
    if n <= C.TREE_NAME_HEAD + C.TREE_NAME_TAIL:
        return nomes
    meio = n - C.TREE_NAME_HEAD - C.TREE_NAME_TAIL
    return (nomes[:C.TREE_NAME_HEAD]
            + [f"... (+{meio} no meio, {n} no total) ..."]
            + nomes[-C.TREE_NAME_TAIL:])


def _peek_children(abs_dir: Path) -> list[str]:
```

## Edicao 3 — `flatdrop/core.py`: a espiada usa a amostra

**Ancora:**

```python
    out = [
        (e.name + "/" if e.is_dir(follow_symlinks=False) else e.name)
        for e in entries[:C.TREE_NAME_CAP]
    ]
    resto = len(entries) - C.TREE_NAME_CAP
    if resto > 0:
        out.append(f"(+{resto} mais)")
    return out
```

**Substituir por:**

```python
    nomes = [(e.name + "/" if e.is_dir(follow_symlinks=False) else e.name) for e in entries]
    return _tree_amostra(nomes)
```

## Edicao 4 — `flatdrop/core.py`: o resumo usa a amostra

**Ancora:**

```python
        for label, names in sorted(named.items()):
            names = sorted(names)          # sem isto o teto guardaria um subconjunto aleatorio
            shown = names[:C.TREE_NAME_CAP]
            resto = len(names) - len(shown)
            sufixo = f" (+{resto} mais)" if resto else ""
            lines.append(f"{prefix}[pulados por {label}: {', '.join(shown)}{sufixo}]")
```

**Substituir por:**

```python
        for label, names in sorted(named.items()):
            # ordenar e obrigatorio: a amostra le as duas PONTAS, e ponta de lista
            # desordenada nao quer dizer nada.
            amostra = _tree_amostra(sorted(names))
            lines.append(f"{prefix}[pulados por {label}: {', '.join(amostra)}]")
```

## Edicao 5 — testes (`tests/test_core.py`)

Acrescente:

1. `test_tree_amostra_curta_devolve_tudo` — lista com `HEAD + TAIL` nomes sai inteira, sem a
   linha do meio.
2. `test_tree_amostra_longa_mostra_as_duas_pontas` — 39 nomes ordenados: o **primeiro** e o
   **ultimo** aparecem, o total aparece, e o numero de nomes e `HEAD + TAIL`.
3. `test_tree_pasta_grande_mostra_faixa` — ponta a ponta: pasta com 39 arquivos ignorada por
   `pasta/*`; o `_TREE.md` contem o primeiro e o ultimo nome e a marca `no total`.

Se algum teste do wo0038 quebrar pelo formato novo, **ajuste e registre no relatorio**.

## Edicao 6 — versao e CHANGELOG

`flatdrop/__init__.py`: `0.13.0` → `0.14.0`.

**Ancora** em `meta/CHANGELOG.md`:

```
## [0.13.0] — 2026-07-28
```

**Inserir ANTES dela:**

```
## [0.14.0] — 2026-07-28

### Mudado
- **O `_TREE.md` passa a mostrar a FAIXA de uma pasta grande, não só o começo (wo0043).** No
  lugar do teto simples (`10 nomes + "+29 mais"`), sai uma amostra com as primeiras e as
  últimas posições e o meio contado: `... (+29 no meio, 39 no total) ...`. Numa coleção
  ordenada por data é o último nome que diz até onde ela vai — e era exatamente ele que sumia.
  O `_TREE` orienta; o índice completo de uma pasta grande é trabalho do editor da GUI.
```

## Edicao 7 — `meta/STATUS.md`: fechar o item 4 e abrir o bug do editor

**Ancora:**

```
4. **Teto de nomes do `_TREE` (`+N mais`) esconde as pastas grandes.**
```

**Substituir a LINHA e as que a seguem ate o fim do item 4** por:

```
4. ~~Teto de nomes do `_TREE`.~~ **RESOLVIDO na 0.14.0 (wo0043)** — amostra com as duas pontas
   e o meio contado.
```

**Ancora** (primeiro item de «Riscos / pontos de atenção»):

```
- ~~O `!` não resgata arquivo dentro de pasta ignorada.~~
```

**Inserir ANTES dela:**

```
- 🔴 **BUG ABERTO (0.13.0): o editor não convive com regras escritas FORA do bloco gerenciado.**
  Reproduzido em sandbox e no `.flatdropignore` real deste repo. Três defeitos, uma causa:
  1. **Duplicação.** Salvar sem mexer em nada copia para dentro do bloco as linhas que já
     existiam fora dele (aqui: `meta/workorders/*` e `INSTRUCOES-DO-PROJETO.md` aparecem duas
     vezes). A curadoria manual vira sombra de uma cópia gerada.
  2. **Destravar não funciona.** Se a trava vem de uma linha manual fora do bloco, destravar na
     GUI só faz o gerador *omitir* a linha do bloco — a de fora continua lá, a pasta segue
     travada, e ao reabrir o editor a trava volta. O clique é desfeito em silêncio.
  3. **Marcar um arquivo excluído por linha manual também não tem efeito**, pela mesma razão:
     o bloco não emite o `!` que precisaria vencer a linha de fora.
  **Causa raiz:** o gerador usa como referência o **git puro**, não "tudo o que já existe menos
  o meu bloco". Quem só lê o `.gitignore` não enxerga a curadoria manual do próprio
  `.flatdropignore`, então não sabe nem que precisa corrigi-la. Agravado por não haver garantia
  de que o bloco fique por ÚLTIMO no arquivo (vale a última regra que casa).
  **Contorno até a correção:** manter a curadoria manual OU usar o editor, não os dois no mesmo
  arquivo. **Análise com o desenho da correção:**
  `meta/analises/260728-ANALISE-bloco-gerenciado-vs-manual.md`.
```

## Edicao 8 — `meta/IDEAS.md`

**Ancora:**

```
- **O teto de nomes do `_TREE` esconde justamente as pastas grandes.**
```

**Inserir ANTES dela** (e deixe o item antigo onde está, para o Code mover para «Concluídas»
com a nota `RESOLVIDO na 0.14.0 (wo0043) — amostra com as duas pontas`):

```
- **O editor e a curadoria manual do `.flatdropignore` não convivem.** Bug aberto da 0.13.0,
  detalhado no STATUS e na análise. Fica aqui a ideia que nasceu do diagnóstico: o bloco
  gerenciado deveria ser tratado como um **diff contra tudo o que já existe** — emite linha
  só quando o estado desejado diverge do que os outros arquivos e a parte manual já fazem —,
  e o gerador deveria **garantir que o bloco fique por último** no arquivo, senão uma linha
  manual abaixo dele vence em silêncio. Também vale a GUI **mostrar de onde vem** cada trava
  herdada (`travada (git)` já existe; falta `travada (manual)`), porque hoje o autor não tem
  como saber que aquela trava não é dele. (2026-07-28.)
```

## Edicao 9 — `meta/IDEAS.md`: feedback ao kit

**Ancora:**

```
- **A regra "sua cópia não é a fonte da verdade" está longe do lugar onde ela é quebrada.**
```

**Inserir ANTES dela:**

```
- **Faltou no kit uma regra sobre artefato gerado que convive com edição humana.** Este projeto
  tropeçou duas vezes no mesmo padrão — um bloco gerado dentro de um arquivo que a pessoa também
  edita à mão (o `.flatdropignore`; antes, o apêndice do CEREBRO). É um padrão comum o bastante
  para virar princípio: **o artefato gerado precisa (i) saber o que existe fora dele, (ii) ter
  precedência definida por posição, e (iii) nunca duplicar o que já está lá.** Nenhuma dessas
  três aparece no kit hoje, e as três foram violadas de uma vez. (2026-07-28.)
- **Sugestão de fluxo: a análise devia ser oferecida ANTES da WO, não depois do erro.** As três
  correções desta sessão que exigiram redesenho (gerador, trava, este bug) tinham em comum uma
  pergunta de produto não formulada. O CEREBRO já traz «Análise antes do compromisso», mas o
  gatilho é subjetivo («mudança não-trivial»). Um gatilho mais afiado, que teria pegado os três:
  **mudar o formato de um artefato que outra pessoa (ou o futuro você) vai ler ou editar pede
  análise, mesmo quando o diff é pequeno.** (2026-07-28.)
- **O `_UPDATE-PROMPT` deveria pedir o estado do repo, não só o pacote.** Em todo update o
  assistente precisa saber o que está aplicado, e a única fonte confiável é o repo — que ele só
  vê pelo mount. Se o prompt do kit terminasse com uma linha do tipo «antes de comparar, liste o
  mount e diga em que versão/commit o projeto está», o erro de 28/07 (afirmar que uma WO estava
  pendente) teria sido impossível de cometer em silêncio. (2026-07-28.)
```

## Checklist de fecho

- [ ] `python -m pytest -q` verde (76 antes; diga o final).
- [ ] `git diff` conferido: `config.py`, `core.py` (3 pontos), testes, versao, CHANGELOG,
      STATUS, IDEAS. `cli.py` / `_build_cli_args` / `_generate_bat` / `_sources` **intocados**.
- [ ] Coloque tambem `meta/analises/260728-ANALISE-bloco-gerenciado-vs-manual.md` (o autor baixa
      junto desta WO) e inclua no commit.
- [ ] Rode `python run.py` uma vez e confira o `_TREE.md` gerado num projeto com pasta grande —
      a faixa (primeiro e ultimo nome) deve aparecer.
- [ ] Commit sem acento, Conventional Commits.
- [ ] **Relatorio**: o que fez, desvios, arquivos tocados, suite, commit.

---

## Validado em sandbox antes de virar WO

As edicoes 1-4 foram aplicadas numa copia de `core.py`/`config.py` (0.13.0) e a arvore foi
gerada de verdade, com 39 arquivos numa pasta ignorada por `wo/*` e 15 numa pasta ignorada
por `assets/`:

```
  assets/  [ignorada: flatdropignore]
    img00.png ... img05.png
    ... (+5 no meio, 15 no total) ...
    img11.png ... img14.png
  wo/
    [pulados por flatdropignore: 260600-wo0000-x.md, ..., ... (+29 no meio, 39 no total) ...,
     260637-wo0037-x.md, 260638-wo0038-x.md]
```

Antes desta WO a mesma pasta parava em `260609-wo0009-x.md (+29 mais)` — dava o tamanho, nao
dava a faixa.
