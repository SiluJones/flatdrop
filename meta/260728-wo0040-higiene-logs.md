# wo0040 — Fusao dos logs colididos + higiene pendente

**Data:** 2026-07-28 · **Autor:** chat · **Aplicar com:** `/apply-wo meta/workorders/260728-wo0040-higiene-logs.md`

> **So doc** — sem suite; a rede e o `git diff`.

## Edicao 1 — substituir os quatro logs por dois

Dois arquivos NOVOS (entregues pelo chat, ja fundidos) substituem quatro:

- `logs/2026-06-24.md` (novo) substitui `logs/2026-06-24.md` + `logs/2026-06-24 (2).md`
- `logs/2026-07-05.md` (novo) substitui `logs/2026-07-05.md` + `logs/2026-07-05 (novo menor, analisar e fazer merge com outro).md`

Passos:

```
git rm "logs/2026-06-24 (2).md" "logs/2026-07-05 (novo menor, analisar e fazer merge com outro).md"
```

e sobrescreva `logs/2026-06-24.md` e `logs/2026-07-05.md` com os arquivos que o autor baixou.
**Confira antes de commitar** que os dois novos comecam com o bloco `>` explicando a fusao — se
nao comecarem, o autor colocou o arquivo errado: PARE e reporte.

## Edicao 2 — `meta/DECISIONS.md`: regra do log

Acrescente ao FIM do arquivo:

```
## DEC-026 — Um log por DIA, sessões concatenadas
**Data:** 2026-07-28 · **Status:** aceita

**Contexto.** A convenção `logs/AAAA-MM-DD.md` não previu duas sessões no mesmo dia. Aconteceu
duas vezes (24/06 e 05/07) e foi resolvido na mão, com sufixos: `2026-06-24 (2).md` e
`2026-07-05 (novo menor, analisar e fazer merge com outro).md`. O resultado foi pior que o
problema — em 24/06 os dois arquivos diziam "cobre o dia inteiro" e **nenhum dos dois cobria**:
um tinha o teste real do usuário e o modal da UI-1, o outro tinha a spec-0008 e a DEC-014.
Informação perdida em ambos, e ninguém sabia qual ler.

**Decisão.** Um arquivo por dia. Segunda sessão no mesmo dia **concatena** no arquivo existente,
como seção `## Sessão N — <período>: <assunto>`, nunca como arquivo novo. Se um log já foi
entregue e a sessão continua, o chat reentrega o arquivo do dia INTEIRO, com a seção nova ao fim.

**Consequência.** Os quatro arquivos viraram dois (wo0040), com nota de fusão no topo e nada
descartado. A regra entrou no `meta/CEREBRO.md` e no `meta/LOG-TEMPLATE.md`.
```

## Edicao 3 — `meta/LOG-TEMPLATE.md`: dizer a regra no molde

**Ancora:** a primeira linha do arquivo (`# Log — AAAA-MM-DD` ou equivalente). **Inserir logo
abaixo dela**, antes do resto:

```
> Um arquivo por DIA (DEC-026). Segunda sessão no mesmo dia entra como
> `## Sessão N — <período>: <assunto>` neste mesmo arquivo — nunca um arquivo novo.
```

## Edicao 4 — `meta/CEREBRO.md`: a mesma regra na tabela de documentos

**Ancora:**

```
| `logs/AAAA-MM-DD.md` | Histórico | Ao final de cada sessão (formato em LOG-TEMPLATE). |
```

**Substituir por:**

```
| `logs/AAAA-MM-DD.md` | Histórico | Ao final de cada sessão (formato em LOG-TEMPLATE). **Um arquivo por DIA** (DEC-026): segunda sessão no mesmo dia vira `## Sessão N` no mesmo arquivo, nunca arquivo novo. |
```

## Edicao 5 — `meta/IDEAS.md`: dois itens novos nas Ativas

**Ancora:**

```
- **`_TREE` deve nomear o conteúdo útil das pastas ignoradas.**
```

**Inserir ANTES dela:**

```
- **O teto de nomes do `_TREE` esconde justamente as pastas grandes.** Depois do wo0038 a árvore
  nomeia até `TREE_NAME_CAP` (10) e agrega o resto: `meta/workorders/` sai com 10 nomes e
  `(+29 mais)` — e são os 29 que a pessoa precisaria ver para escolher o que liberar. Despejar
  tudo também não serve (uma pasta de 100 arquivos inunda o `_TREE`). Caminhos a considerar:
  primeiros N + últimos N (dá a faixa e a ordem); teto por pasta em vez de global; teto maior
  quando a pasta é o alvo de um `!`; ou uma lista completa fora do `_TREE`, num arquivo à parte
  que só a pasta grande gera. Vale também levar isso à GUI, para o editor mostrar a pasta inteira
  quando ela vier de um ignore do autor. **Ainda sem forma decidida — o teto atual não serve.**
  (Autor, 2026-07-28.)
- **`pasta/` deveria voltar a ser exclusão DURA?** O FIX-011 tornou `pasta/` e `pasta/*`
  equivalentes no FlatDrop: os dois aceitam `!` por dentro. O autor prefere o contrário — `pasta/`
  significando "nunca entra, nem aparece na árvore" e só `pasta/*` aceitando resgate, que é o
  comportamento do git puro e dá duas ferramentas com dois usos. Em troca, reintroduz o caso que
  gerou a reclamação de 23/07, então só fecha se a GUI escrever `pasta/*` sozinha e o `_TREE`
  disser em qual forma cada pasta está. **Decisão separada da do gerador**; ver
  `meta/analises/260728-ANALISE-gerador-flatdropignore.md`. (2026-07-28.)
```

## Edicao 6 — `meta/STATUS.md`: apontar para a análise e ajustar o backlog

**Ancora** (item 4 do backlog):

```
4. **`_TREE` deve nomear o conteúdo útil das pastas ignoradas** (nota do autor,
   2026-07-24). Hoje a pasta ignorada vira uma linha só e o chat futuro não descobre o que
   liberar. Listar os filhos de pasta ignorada **por ignore do autor**, seguindo a colapsar o
   lixo estrutural (`node_modules`, `.git`, `__pycache__`). Insumo pronto: `skipped_items`.
   **PRÓXIMA frente, à frente do multi-raiz (decisão do autor, 2026-07-28).**
```

**Substituir por:**

```
4. **Teto de nomes do `_TREE` (`+N mais`) esconde as pastas grandes.** A parte de nomear o que
   foi ignorado saiu na 0.12.0 (wo0038), mas com teto global de 10: `meta/workorders/` mostra 10
   e esconde 29 — e são os 29 que interessam para escolher o que liberar. Despejar tudo inunda o
   `_TREE`. Forma ainda não decidida (ver IDEAS). Vale para a GUI também. **Próxima frente.**
```

**Ancora** (item 5):

```
   maquinaria de round-trip (DEC-016/spec0020): **pede análise antes da WO**.
```

**Substituir por:**

```
   maquinaria de round-trip (DEC-016/spec0020). **Análise escrita e em discussão:**
   `meta/analises/260728-ANALISE-gerador-flatdropignore.md` — três opções (B, C, D), a decisão
   depende de responder "arquivo novo em pasta curada entra ou fica fora?". Aguarda o autor.
```

## Edicao 7 — `meta/GLOSSARY.md`

Acrescente ao FIM:

```
**`pasta/` × `pasta/*`.** Duas formas de ignorar uma pasta. `pasta/` nomeia **a pasta**;
`pasta/*` nomeia **o conteúdo direto** dela. No git puro a diferença é decisiva: com `pasta/`
o walker poda o diretório e um `!pasta/arquivo` posterior nunca chega a ser avaliado; com
`pasta/*` a pasta não casa, a varredura desce e o resgate funciona. No FlatDrop, **desde o
FIX-011 (0.12.0) as duas formas aceitam resgate** — a poda passou a consultar as negações antes
de descartar a pasta. A convenção `pasta/*` (DEC-025) segue recomendada por ser explícita e
compatível com quem lê o arquivo como se fosse `.gitignore`.
```

## Checklist de fecho

- [ ] `git rm` dos dois logs colididos + os dois novos no lugar; `git log` continua legivel.
- [ ] `git diff` conferido: 6 edicoes de doc, nada de codigo.
- [ ] Commit sem acento, Conventional Commits.
- [ ] **Relatorio** curto.
