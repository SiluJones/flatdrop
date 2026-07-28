# 260705-spec0017 — Editor visual de `.flatdropignore` na GUI (design/investigação)

> **Tipo:** spec de **design/investigação** — NÃO tem edições ancoradas em código. O
> objetivo é fechar o desenho e as decisões antes de a spec de **implementação**
> (spec0018) escrever os diffs. Nada aqui é aplicado pelo Code ainda.
>
> **Contexto:** Fase 2-D. Hoje o `.flatdropignore` é escrito à mão; a ferramenta só o LÊ.
> Queremos uma tela que gere o arquivo por marcação visual, sem o autor decorar sintaxe.
> Fundamentado por leitura do core no mount e por verificação em sandbox (o `!` libera a
> camada de ignore, mas não vence tipo/sensível — spec0016/nota da sessão 2026-07-05).

## 1. Objetivo e não-objetivos

**Objetivo:** uma janela (modal a partir da GUI principal) com a **árvore navegável** das
pastas/arquivos da raiz, um **controle por item** para decidir se ele vai ou não ao
Projeto, **sinalizando o que o `.gitignore` já esconde** e o que não entra por **tipo** ou
por ser **sensível**, e um botão que **grava o `.flatdropignore` na raiz** a partir das
marcações.

**Não-objetivos (v1):**
- Não editar os ignores **embutidos imutáveis** (`.git`, `node_modules`, `dist`… — a
  lista `DEFAULT_DIR_IGNORES`/`DEFAULT_FILE_IGNORES`). Ficam podados/ocultos. (Expor
  alguns caso a caso é a antiga ideia "ignores de pasta editáveis" — fica para depois.)
- Não editar a allowlist de **tipos** aqui — isso já é o modal "Escolher tipos…". O editor
  só **sinaliza** quando um item não viria por tipo e aponta para lá.
- Não mexer na precedência do core: **o `.flatdropignore` continua com a palavra final
  sobre o `.gitignore`** (DEC-014). O editor só gera o arquivo.

## 2. O que o core já oferece (reaproveitável)

Tudo isto já existe em `core.py`/`config.py` e o editor deve reusar, não reimplementar:

- `_build_ignore_specs(root, cfg) -> (full, gi, fd)` — os três matchers pathspec.
- `_ignore_status(rel, full, gi, fd) -> (ignored, source, liberated)` — por item: está
  ignorado? por `gitignore` ou `flatdropignore`? ou **liberado** (o git pegaria, mas um
  `!` soltou)? É exatamente o sinal que a árvore precisa exibir.
- `is_allowed_type(name, cfg) -> bool` — se a extensão é aceita (para o badge "não vem por
  tipo").
- `is_sensitive(name) -> bool` — para o badge "sensível, barrado".
- `DEFAULT_DIR_IGNORES` / `DEFAULT_FILE_IGNORES` — o núcleo imutável a podar da visão.
- `_collect_ignore_lines` / `_rebase_ignore` — já leem os `.gitignore`/`.flatdropignore`
  aninhados e rebaseiam padrões de subpasta para a raiz.

Ponto de atenção: `_build_ignore_specs` **já inclui** um `.flatdropignore` existente no
`full`/`fd`. Para o editor, isso é bom para **pré-marcar** o estado atual (ver §6), mas a
geração precisa distinguir "o que o git faz sozinho" de "o que o flatdropignore já mudou".

## 3. Modelo de dados do editor

O `_scan` **poda** (não desce em pasta ignorada), então não serve para a árvore do editor,
que precisa mostrar **tudo o que é editável**, inclusive o que o git esconde. Proposta: um
**novo helper puro no core** (testável por pytest, sem tkinter):

```
walk_annotated(root, cfg) -> Iterator[Item]
  Item = (rel: str, is_dir: bool, base_in: bool, source: str,
          allowed_type: bool, sensitive: bool)
```

Regras do walk:
- Poda os imutáveis (`DEFAULT_DIR_IGNORES`; arquivos em `DEFAULT_FILE_IGNORES`, incluindo
  o próprio `.flatdropignore`/`_MANIFEST.md`/`_TREE.md`) — não aparecem.
- Desce em pasta **gitignored** (ao contrário do `_scan`), para o autor poder liberá-la.
- `base_in` = "iria ao Projeto se o `.flatdropignore` estivesse vazio?" — calculado do
  `.gitignore` + embutidos, **sem** considerar tipo/sensível (esses são badges à parte).
- `source` vem do `_ignore_status` (`gitignore`/`flatdropignore`/``).
- Lazy: em repo grande, popular filhos só ao expandir a pasta (ver §9).

A GUI monta a árvore a partir desse iterador; nenhuma regra de negócio mora na GUI (DEC-009).

## 4. Decisão-chave 1 — modelo de interação

**Opção A — tri-state literal** (o que o IDEAS registrou: incluído/excluído/liberado). O
autor clica e o item cicla `neutro → excluir → liberar`. Fiel ao arquivo, mas exige que ele
entenda a diferença entre "excluir" e "liberar" — ou seja, meio que decorar a semântica.

**Opção B — checkbox binário "quero no Projeto" + a ferramenta deriva o padrão
(recomendada).** O autor só marca/desmarca "vai ao Projeto"; a ferramenta olha o estado do
git (`base_in`) e escolhe sozinha se precisa de `!padrão` (liberar) ou de `padrão`
(excluir). "Liberado" e "excluído" viram **resultado exibido** (um badge), não algo que o
autor seleciona. Casa com o objetivo "sem decorar sintaxe".

Em ambas, **pasta com filhos divergentes** mostra o estado **indeterminado** (parcial) —
comportamento clássico de árvore com checkbox; marcar/desmarcar a pasta propaga aos filhos.

**Recomendo a Opção B.** Trade-off: B esconde o `!` do autor (bom para usabilidade, menos
"transparente"); mitigo com um badge visível "liberado via !" e a **pré-visualização do
`.flatdropignore`** antes de salvar (ele vê o texto que sairá).

## 5. Decisão-chave 2 — geração dos padrões (o coração, no core e testável)

Uma função **pura** `build_flatdropignore(selections, walk) -> str`, em `core.py`, coberta
por pytest (a parte não-trivial não pode morar na GUI). Regra por item-folha, cruzando o
desejo do autor (`want ∈ {in, out}`) com o baseline do git (`base_in`):

| `want` | `base_in` | Linha gerada |
|---|---|---|
| in | in | *(nenhuma — já entra)* |
| in | out | `!caminho` **(liberar)** |
| out | in | `caminho` **(excluir)** |
| out | out | *(nenhuma — já está fora; deixa com o git)* |

Otimização de legibilidade (o que exige teste): quando **todos** os descendentes de uma
pasta compartilham o mesmo `want` e ele difere do `base`, emitir **uma** regra de pasta
(`dir/` ou `!dir/`) em vez de N regras de arquivo; pastas mistas → regra da maioria +
exceções por filho. O gerador escolhe o conjunto **mínimo e legível**.

**A verificar no spike (parcialmente testado):** no sandbox, `!docs/api/` sozinho trouxe
`docs/api/schema.json` (um nível). Para arquivos mais fundos, a semântica gitignore pode
exigir também `!dir/**`. O gerador deve, ao liberar uma pasta, decidir entre `!dir/` e
`!dir/` + `!dir/**` — confirmar com a árvore real antes de fixar.

## 6. Decisão-chave 3 — round-trip de um `.flatdropignore` existente

O autor pode já ter um `.flatdropignore` escrito à mão (com comentários). O editor **não
pode destruí-lo em silêncio**. Opções:
- **(i)** Ler o arquivo, pré-marcar a árvore pelo efeito dele (via `fd`/`_ignore_status`) e,
  ao salvar, **regenerar só um bloco gerenciado** entre marcadores
  (`# >>> flatdrop-editor` … `# <<<`), preservando o que estiver fora do bloco. **Recomendo.**
- (ii) Regenerar o arquivo inteiro, avisando que linhas manuais serão perdidas (mais
  simples, mais destrutivo).

Recomendo **(i)**: pré-marca pelo estado atual e preserva linhas manuais fora do bloco
gerenciado. Requer parse leve dos padrões que o editor "entende"; padrões avançados que ele
não sabe mapear ficam fora do bloco, intactos, e a árvore os reflete pelo efeito (via o
matcher `fd`), mesmo sem editá-los.

## 7. Widget tkinter (zero-dep) e armadilhas

`ttk.Treeview` **não tem checkbox nativo**. Mantendo o princípio de zero dependências
(nada de `ttkwidgets`), a abordagem padrão é: uma **coluna de glifo** (`☐`/`☑`/`▣` para
parcial; talvez um distinto p/ "liberado") + bind de `<Button-1>` que alterna quando o
clique cai naquela coluna (`identify_region`/`identify_column`), e **tags** para colorir a
linha por efeito (verde = vai / cinza = não vai / azul = liberado). Alternativa visual:
`PhotoImage` 16×16 por estado (mais bonito, exige embutir imagens base64).

**Armadilhas a validar no spike (é onde some tempo):**
- Hit-testing do clique exatamente na coluna do glifo; e alternar por teclado (Espaço).
- Propagação pai→filhos e recomputar o estado **indeterminado** dos ancestrais.
- **Performance/lazy load** em repositório grande (ver §9): popular filhos só ao expandir.
- Reconciliar a marcação com o efeito real (um `!` de pasta muda vários filhos).

## 8. Interação com tipo e sensível (badges não-editáveis)

Um item pode estar "quero no Projeto" e **ainda assim não vir**:
- **tipo não aceito** (`is_allowed_type` falso): badge "não vem — tipo; ajuste em Escolher
  tipos…". É o caso do `logs/*.log` do exemplo: liberar a pasta não basta; a extensão tem
  de ser aceita. O editor **não** resolve isso (é o modal de tipos), só avisa e oferece
  abrir o modal.
- **sensível** (`is_sensitive`): badge "barrado — sensível". Não sugerir liberar por
  reflexo; se o autor insistir, aí sim expor um caminho explícito (fora do v1).

Esses badges são **informativos**, ortogonais ao checkbox de ignore.

## 9. Escopo da árvore e performance

- Poda os imutáveis (§3) — nunca mostra `node_modules` etc.
- Mostra o resto, **inclusive gitignored**, para permitir liberar.
- **Lazy load**: em raiz grande, montar só o primeiro nível e popular filhos no evento de
  expandir (`<<TreeviewOpen>>`), calculando o `walk_annotated` por subpasta sob demanda.
- Recalcular ignore status é barato (pathspec em memória), mas evitar recomputar a árvore
  inteira a cada clique — atualizar só o ramo afetado.

## 10. Arquitetura (core × gui)

- **core.py (novo, testável):**
  - `walk_annotated(root, cfg)` — o iterador anotado (§3).
  - `build_flatdropignore(selections, walk, existing_text=None) -> str` — o gerador puro
    (§5) + o round-trip do bloco gerenciado (§6).
  - Testes pytest cobrindo a tabela do §5, a otimização pasta-vs-arquivo, `!dir/` vs
    `!dir/**`, e o round-trip (preserva linhas fora do bloco).
- **gui.py (só UI):** o modal, a árvore, os binds de checkbox, a pré-visualização do texto,
  e a gravação do `.flatdropignore` na raiz. Nenhuma regra de geração aqui.
- Botão de entrada na tela principal: "Editar .flatdropignore…" (abre o modal para a raiz
  selecionada). Como a GUI não é testada pela suíte → **smoke manual no Windows**.

## 11. Plano em fases e o que testar

1. **spec0017 (esta)** — fechar as 3 decisões abaixo.
2. **Spike (descartável, não commitado ou sob `scratch/`)** — validar no Windows a
   interação de checkbox no `ttk.Treeview` + lazy load + o comportamento `!dir/` vs
   `!dir/**` na árvore real. Só a mecânica arriscada, sem integrar.
3. **spec0018 (implementação)** — diffs ancorados: `walk_annotated` + `build_flatdropignore`
   + testes no core; o modal e a fiação na `gui.py`. Entra com bump de versão (Fase 2-D
   fecha um item do ROADMAP).

**O que testar (core, pytest):** a tabela want×base; pasta uniforme → regra única; pasta
mista → regra + exceções; liberação profunda (`!dir/**`); round-trip preservando linhas
manuais; item sensível/tipo não vira linha de ignore (são estágios à parte).

## 12. Decisões que preciso de você (para eu escrever a spec0018)

1. **Interação (§4):** vou de **Opção B** (checkbox binário "quero no Projeto", a
   ferramenta deriva `!`/exclusão) com badge de resultado + pré-visualização do texto?
   Ou você prefere a **Opção A** (tri-state literal incluído/excluído/liberado)?
2. **Round-trip (§6):** **bloco gerenciado** preservando linhas manuais fora dele (i), ou
   **regenerar tudo com aviso** (ii)?
3. **Spike (§11):** topa uma etapa de spike de UI descartável antes da implementação, ou
   quer ir direto para a spec0018 assumindo a abordagem de glifo do §7?
