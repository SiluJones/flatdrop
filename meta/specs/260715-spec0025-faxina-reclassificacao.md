# spec0025 — FAXINA: reclassificar ROADMAP/IDEAS (KCM, editor, item C) + capturar ideias

- **Tipo:** meta-only (docs). NÃO altera código, NÃO precisa de testes (a rede é o `git diff`).
- **Data:** 2026-07-15
- **Por quê.** STATUS e CHANGELOG já refletem o item C (o Code atualizou na spec0024), mas
  ROADMAP e IDEAS ainda marcam como abertos o **trecho de KCM**, o **editor visual (Fase
  2-D)** e o **item C** — os três já entregues. Esta faxina põe os docs em dia e captura
  duas coisas da nota `260715-0827`: a ideia do **force-include** e a **decisão de manter a
  `DEFAULT_SUFFIX_IGNORES`** (análise no §Análise abaixo).
- **Regra de segurança (como toda spec):** ache cada âncora EXATA; se alguma falhar, **PARE
  e reporte** — não chute lugar próximo. Blocos grandes são deletados por correspondência
  exata; se não bater, pare.

---

## ROADMAP.md

### Edit R1 — nota de revisão no topo
**Âncora exata:**
```
Itens em aberto vêm de `IDEAS.md`; ao concluir, registre em `CHANGELOG.md`.
```
Trocar por:
```
Itens em aberto vêm de `IDEAS.md`; ao concluir, registre em `CHANGELOG.md`.

> **Mudanças nesta revisão (2026-07-15):** specs 0017–0024 aplicadas. **KCM**, **editor
> visual de `.flatdropignore` (Fase 2-D)** e **item C (persistência + recentes)**
> concluídos; **0.6.0**, **58 testes**. O invariante **DEC-020** grava que o `.bat` não
> pode ser degradado por conveniência. Próximas frentes: **multi-raiz na GUI** e o
> **force-include por caminho exato** (correção do `.min.js`).
```

### Edit R2 — marcar KCM como feito
**Âncora exata:**
```
- [ ] **Trecho de KCM: ler `_TREE.md` → gerar `.flatdropignore`.** Conteúdo portável (não é código): ensina o Claude de qualquer Projeto que usa FlatDrop a ditar um `.flatdropignore` a partir do `_TREE.md`. **← PRÓXIMA 1.** (Não é fase formal, mas é o próximo trabalho.)
```
Trocar por:
```
- [x] **Trecho de KCM: ler `_TREE.md` → gerar `.flatdropignore`.** Entregue (bloco de KCM portável + exemplo no README; material externo, não é código do repo). Habilitado pela spec0011.
```

### Edit R3 — marcar editor (Fase 2-D) como feito
**Âncora exata:**
```
- [ ] **D — Editor de `.flatdropignore` na GUI** (consolida "ignores de pasta editáveis"): árvore navegável da raiz com checkbox por item, sinalizando o que o git ignora, gerando o `.flatdropignore`. Feature de UI não-trivial — provável spec de investigação antes da de implementação. **← PRÓXIMA 2.**
```
Trocar por:
```
- [x] **D — Editor de `.flatdropignore` na GUI** (Fase 2-D, specs 0017–0021). Modal com árvore lazy, checkbox binário, badges de tipo/sensível, bloco gerenciado no arquivo e glifo indeterminado correto na visão colapsada (FIX-007). Consolidou "ignores de pasta editáveis".
```

### Edit R4 — marcar item C como feito
**Âncora exata:**
```
- [ ] **C —** Persistir configurações + pastas recentes na GUI. **← depois das duas acima.**
```
Trocar por:
```
- [x] **C —** Persistir configurações + pastas recentes na GUI (specs 0022–0024, 0.6.0). `settings.json` por plataforma, Combobox de recentes, grava ao Executar; escopo só-GUI (DEC-020) para não tocar o `.bat`.
```

---

## IDEAS.md

### Edit I1 — nota de revisão no topo
**Âncora exata:**
```
> **Mudanças nesta revisão (2026-07-05, transferência de conversa):** ciclo de
```
Inserir ANTES dessa linha:
```
> **Mudanças nesta revisão (2026-07-15):** specs 0017–0024 aplicadas. KCM, editor visual
> (Fase 2-D) e item C (persistência) movidos para **Concluídas**. Nova ideia ativa:
> **force-include por caminho exato** (correção do `.min.js`). Descartada: **remover a
> `DEFAULT_SUFFIX_IGNORES`** (motivo nas Descartadas). Próximas frentes: multi-raiz na GUI
> / force-include.

```

### Edit I2 — atualizar a nota "Próximas duas tarefas"
**Âncora exata:**
```
> **Próximas duas tarefas (ordem definida na transferência de 2026-07-05):** os dois
> primeiros itens abaixo são o foco imediato da próxima conversa; o restante segue
> por prioridade aproximada.
```
Trocar por:
```
> **Foco (2026-07-15):** as tarefas KCM, editor (Fase 2-D) e item C foram concluídas (ver
> Concluídas). As frentes candidatas agora são **multi-raiz na GUI** e o **force-include
> por caminho exato**; o restante segue por prioridade aproximada.
```

### Edit I3 — remover o bullet do KCM das Ativas
**Âncora exata** (bloco inteiro — deletar, substituir por vazio):
```
- **[PRÓXIMA 1] Trecho de KCM: "Claude lê o `_TREE.md` e dita o `.flatdropignore`"
  (refinada pela nota 0714).** Não é código do FlatDrop — é conteúdo de KCM, portável
  para todo Projeto que usa FlatDrop. O autor sobe o `_TREE.md`; o Claude vê o que
  sobrou/faltou (com o motivo de cada exclusão) e devolve o conteúdo do
  `.flatdropignore` pronto para salvar na raiz e rodar de novo. O tree é o
  diagnóstico; o `.flatdropignore` é a receita. Três ganhos: (1) o `.flatdropignore`
  fica **versionado** no repo (parte do projeto, não config solta); (2) o KCM torna
  o comportamento **portável** sem reensinar a cada projeto; (3) fecha o ciclo
  `_TREE -> flatdropignore -> mount melhor`. **Refino técnico importante:** o fluxo
  serve sobretudo para **liberar o que o `.gitignore` esconde** (via `!padrão`), pois
  arquivos que nem estão no Git não aparecem no mount para o Claude os enxergar; o
  `_TREE.md` mostra o que foi podado por `[ignorada: gitignore]` e o Claude sugere a
  reinclusão. Entregável: um bloco de KCM + um exemplo no README. Habilitado pela
  spec0011. (Ideia do usuário, notas 0704-0714.)
```
Substituir por (nada — remover o bloco e a linha em branco que o segue).

### Edit I4 — remover o bullet do editor das Ativas
**Âncora exata** (bloco inteiro — deletar):
```
- **[PRÓXIMA 2] Editor visual de `.flatdropignore` na GUI (= Fase 2-D).** Marcar
  visualmente o que excluir/re-incluir e a ferramenta grava o `.flatdropignore` por
  você — sem decorar a sintaxe. Como o usuário descreveu: uma **árvore navegável das
  pastas/arquivos percorridos da raiz, com checkbox por item**, sinalizando o que já
  é **ignorado pelo git**, prática/intuitiva/manipulável. Hoje o `.flatdropignore` é
  criado à mão; a ferramenta só o LÊ. **Feature de UI não-trivial:** precisa de árvore
  com estado tri-state (incluído / excluído / liberado via `!`), leitura do que o
  `.gitignore` já pega para sinalizar, e geração dos padrões do `.flatdropignore` a
  partir das marcações. Provavelmente pede uma **spec de investigação/design antes**
  da spec de implementação (o próprio usuário reconhece que exige pesquisa/estudo).
  Consolida o antigo item D "ignores de pasta editáveis na GUI". (Ideia do usuário.)
```
Substituir por (nada — remover o bloco e a linha em branco que o segue).

### Edit I5 — remover o bullet do item C das Ativas
**Âncora exata** (bloco inteiro — deletar):
```
- **Pastas recentes + persistir configurações.** Lembrar últimas raízes, destino,
  modo, separador, toggles e seleção de tipos entre execuções (JSON em
  `%APPDATA%`/`~/.config`); Combobox de recentes na GUI. (Fase 2 — item C.)
```
Substituir por (nada — remover o bloco e a linha em branco que o segue).

### Edit I6 — adicionar o force-include às Ativas
**Âncora exata** (o bullet de "Formato de nome", que permanece — inserir DEPOIS dele):
```
  (stem-primeiro) como dois estilos opt-in. (Ideia do usuário, 2026-07-04.)
```
Inserir DEPOIS:
```
- **Force-include por caminho exato (resgatar um arquivo específico barrado por ignore
  embutido).** Uma lista de "sempre inclua exatamente este caminho", checada ANTES dos
  cortes embutidos (suffix-ignore, tipo, gitignore), ainda barrada por "sensível". Motiva:
  `htmx.min.js` (e afins) some porque `.min.js` está em `DEFAULT_SUFFIX_IGNORES`, e o `!`
  do `.flatdropignore` age numa camada abaixo (só o matcher), então não resgata. Marcador
  próprio no `.flatdropignore` (distinto do `!`, para não borrar a semântica gitignore do
  DEC-017). DEC-020-safe: vive no `_scan`, simétrica GUI×`.bat`, não toca o gerador de
  `.bat`. Mexe no `_scan` → pede spec de design. **Não urgente** (o autor adiou). (Ideia do
  usuário + assistente, nota 0827.)
```

### Edit I7 — três entradas em Concluídas
**Âncora exata:**
```
## Concluídas
```
Inserir DEPOIS (com uma linha em branco antes das entradas):
```

- **[KCM — entregue] Claude lê o `_TREE.md` e dita o `.flatdropignore`.** Bloco de KCM
  portável (material externo, não é código do repo) + exemplo no README; habilitado pela
  spec0011. Fecha o ciclo `_TREE → flatdropignore → mount melhor`, sobretudo liberando via
  `!` o que o `.gitignore` esconde. (Ideia do usuário, notas 0704–0714.)
- **Editor visual de `.flatdropignore` na GUI (Fase 2-D, specs 0017–0021).** Modal com
  árvore lazy, checkbox binário ("quero no Projeto"), badges de tipo/sensível, bloco
  gerenciado no arquivo, e glifo indeterminado correto já na visão colapsada
  (`core.folder_effective_state`, FIX-007). Consolidou o antigo item D. (Ideia do usuário.)
- **Persistir config + pastas recentes na GUI (item C, specs 0022–0024, 0.6.0).**
  `settings.json` por plataforma (`%APPDATA%`/`~/.config`/App Support), Combobox de
  recentes, grava ao Executar; escopo **só-GUI (DEC-020)** para não tocar o `.bat`;
  allowlist salva como delta. `load` nunca lança, `save` atômico. (Fase 2 — item C.)
```

### Edit I8 — registrar a ideia descartada da suffix-list
**Âncora exata:**
```
## Descartadas
```
Inserir DEPOIS (com uma linha em branco antes da entrada):
```

- **Remover a `DEFAULT_SUFFIX_IGNORES` (ou tirar `.min.js` dela), confiando em
  git/`.flatdropignore`.** Descartada (análise de 2026-07-15). A lista é **redundante** com
  o allowlist de tipos para `.map/.lock/.pyc/.pyo/.class/.o/.so/.dll/.exe` — essas
  extensões não são aceitas, então o filtro de tipo já as barra. Mas é **essencial** para
  `.min.js`/`.min.css`, cujas extensões (`js`/`css`) SÃO aceitas: sem a lista, todo
  minificado/bundle vazaria ao mount. Confiar no git não cobre committados (lockfiles, libs
  vendorizadas e source maps costumam ser versionados) e exigiria `.flatdropignore` por
  projeto para ruído binário — contra o zero-config. E tirar só `.min.js` liberaria TODOS
  os `.min.js`, contra o objetivo de liberar só um. O lever certo para exceções pontuais é
  o **force-include por caminho exato** (ver Ativas), não remover o default.
```

---

## Análise (o "porquê" da decisão I8, para referência)

`.min.js` é barrado no passo 1 do `_scan` (`endswith(DEFAULT_SUFFIX_IGNORES)`, rótulo
`ignore_padrão`), ANTES do matcher do `.flatdropignore`. Cruzando cada sufixo com o
allowlist de tipos:
- **`.min.js`/`.min.css`** → extensões `js`/`css` **são aceitas** → a suffix-list é a ÚNICA
  coisa que os separa do código escrito à mão. **Load-bearing.**
- **`.map .lock .pyc .pyo .class .o .so .dll .exe`** → extensões **não aceitas** → o filtro
  de tipo já os barra → a suffix-list é **redundante** (rede de segurança barata + guarda
  se alguém adicionar, p.ex., `map` ao allowlist). Poderiam ser enxugados, mas sem ganho
  real e com pequeno risco — não vale mexer.

Conclusão: **manter a lista**; o resgate pontual de um arquivo útil é trabalho do
force-include, não da remoção do default.

## Commit sugerido (sem acento)

```
git add ROADMAP.md IDEAS.md meta/specs/260715-spec0025-faxina-reclassificacao.md & git commit -m "docs(faxina): reclassificar ROADMAP/IDEAS e capturar ideias" -m "KCM, editor visual (Fase 2-D) e item C marcados como concluidos e movidos para Concluidas. Nova ideia ativa: force-include por caminho exato (fix do .min.js). Descartada com motivo: remover a DEFAULT_SUFFIX_IGNORES (redundante para binarios/maps/locks, mas essencial para .min.js/.min.css)."
```
