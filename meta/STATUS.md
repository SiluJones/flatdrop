# STATUS — FlatDrop

Estado atual do projeto. Atualize ao fim de cada sessão de trabalho (rolante: o
resolvido sai daqui e vira `CHANGELOG`/`DECISIONS`).

> **Mudanças nesta revisão (2026-08-01) — meta apenas, nenhuma linha de produto tocada:**
> merge do template-update do KCM **v1.95.0** (**DEC-028**) e curadoria do registro. Higiene
> aplicada, item a item:
>
> - O **cabeçalho estava desatualizado**: declarava 0.11.0, 68 testes e data de 28/07, enquanto o
>   corpo já falava de 0.12.0–0.14.0. Corrigido — a divergência nasceu de o Code fazer *append* e
>   ninguém reescrever o topo. Agora **0.14.0**.
> - **Saíram por já estarem resolvidos** (o desfecho vive no CHANGELOG/DECISIONS): as seis notas
>   datadas de julho (spec0021, spec0024, spec0027, spec0028, specs 0031–0033), o item 1 do
>   backlog (*trecho de KCM* — o `ROADMAP` e o `IDEAS` já o davam por **entregue**; só o STATUS
>   ainda o chamava de «PRIMEIRA tarefa da próxima conversa»), os itens 2, 3 e 4, o risco do
>   backup (resolvido em 21/07) e a linha do FIX-011.
> - **Ficou o que ainda é o agora:** o bug do bloco gerenciado, o registro pendente da wo0044 e os
>   pontos de atenção que seguem valendo. O que era «adiado» virou item com **gatilho de retorno**
>   em `IDEAS.md` › Adiadas, em vez de morar aqui sem prazo.
> - **Suíte não rodada nesta sessão.** O número abaixo é o relatado pelo Claude Code em 29/07.

- **Versão:** **0.14.0** no `__init__.py` (amostra do `_TREE` — wo0043). `[Não lançado]` no
  CHANGELOG traz o registro desta sessão (documentação/ambiente, sem corte de versão) e os itens
  de produto em aberto.
- **Data:** 2026-08-01
- **Commit:** `e772d45` (wo0043) é o último **conhecido**, relatado pelo Code em 29/07 — o mount é
  uma cópia achatada e não tem `.git`, então o chat não consegue conferir. Quando o `_MANIFEST`
  passar a gravar `git log -1` (ideia ativa), este campo deixa de depender de relato.
- **Fase:** F1 (MVP) OK · F2 (robustez/conveniência) **quase concluída** — restam multi-raiz na
  GUI (adiada), UI-2/UI-3 e o bug abaixo · F3 (gerador de `.bat` + multi-fonte na GUI) OK · F4
  (distribuição) não iniciada — ver `ROADMAP.md`.
- **Situação geral:** em uso real, **estável**, em **stand-by** por decisão do autor. Fluxo do
  monorepo `cinzeiro` coberto de ponta a ponta (GUI, CLI e `.bat`). Modo Claude Code em operação;
  **WOs 0001–0043 aplicadas e commitadas** (as 0001–0037 mantêm o nome `spec00NN`, anteriores à
  DEC-023). **79 testes verdes** (relatado em 29/07, não reconferido). **Um bug aberto**, com
  contorno conhecido e correção já desenhada.

## 🔴 Bug aberto — o editor não convive com regras escritas FORA do bloco gerenciado

Aberto na 0.13.0. Reproduzido em sandbox e visível no `.flatdropignore` deste próprio repo.
Três sintomas, uma causa:

1. **Duplicação.** Salvar sem mexer em nada copia para dentro do bloco linhas que já existiam fora
   dele. A curadoria manual vira sombra de uma cópia gerada.
2. **Destravar não funciona** quando a trava vem de linha manual: o gerador só *omite* a linha do
   bloco; a de fora continua, a pasta segue travada, e ao reabrir o editor a trava voltou. O
   clique é desfeito em silêncio.
3. **Marcar arquivo excluído por linha manual** também não tem efeito, pela mesma razão.

**Causa raiz:** o gerador compara o estado desejado com o **git puro** e é cego para a curadoria
manual do próprio `.flatdropignore` — sendo cego, não sabe nem que existe algo a corrigir.
Agravante: nada garante que o bloco fique por **último**, e vale a última regra que casa.
**Por que a suíte não pegou:** nenhum dos 8 testes do editor tem linha manual fora do bloco.

**Contorno em vigor:** num mesmo arquivo, use a curadoria manual **ou** o editor, nunca os dois.
**Este repo está no modo manual — não use o editor aqui até a correção.**

**A correção está desenhada em 4 passos** em
`meta/analises/260728-ANALISE-bloco-gerenciado-vs-manual.md`, com riscos e estimativa. Não foi
implementada de propósito: mexe na coleta de ignores e estica o contrato de round-trip da DEC-016.
**Ela começa por duas perguntas ao autor, não por código:**

- **Aprova o desenho (passos 1–4)?**
- **O passo 3 (garantir que o bloco fique por último) MOVE o que estiver depois dele, ou só AVISA?**
  Mover é melhor UX e mexe em texto que não é da ferramenta; avisar é risco zero e pior de usar.
  **Terceira opção, aberta pela regra nova do CEREBRO (DEC-028):** mover **o próprio bloco** para
  o fim — a ferramenta mexendo no que é dela — sem tocar no texto da pessoa.

**Consequência que o autor precisa saber antes de aprovar:** depois da correção, o bloco gerenciado
**deste repo** fica quase vazio, porque tudo já está na parte manual. É o comportamento certo, mas
vai parecer que sumiu — tem de estar no CHANGELOG.

**Entra na mesma frente (não abrir outra):** detectar ou normalizar **contrabarra** em padrão
manual — sintaxe `.gitignore` usa só barra normal, então um padrão escrito com `\` não casa nada e
o arquivo sobe achando que foi ignorado. Medido: o gerador daqui só emite `/`, logo o caso veio de
edição manual. Só faz sentido depois que o gerador enxergar o que está fora do bloco.

## 📋 Registro pendente — wo0044 (primeira tarefa; canal dos meta neste ciclo = CHAT)

Nada disto está no repo. Âncoras e texto exato em
`meta/workorders/260801-wo0044-registro-pendente.md`.

1. **Logs.** `logs/2026-07-28.md` cobre só a primeira sessão do dia — acrescentar as sessões de
   wo0038 → wo0042 como `## Sessão N` (DEC-026) e criar `logs/2026-07-29.md` (wo0043 + handoff).
2. **Duas docstrings de `flatdrop/core.py`** (`_peek_children` e `write_tree`) ainda citam
   `C.TREE_NAME_CAP` como o limite, substituído na 0.14.0 por `TREE_NAME_HEAD`/`TREE_NAME_TAIL`.
3. **`meta/workorders/_TEMPLATE.md`:** conferir se existe — nem o `_MANIFEST` nem o `_TREE`
   respondem — e criar a partir do modelo do kit se faltar.
4. **`.flatdropignore` da raiz** está modificado e não commitado; a versão nova (DEC-028) entra
   junto.
5. `python -m pytest -q`, `git diff`, commit sem acento e **`git push`** — a conversa seguinte lê o
   repo, então o que não subiu não existe.

## ✅ O que funciona (além do MVP)

- **CLI** (`python run.py <opções>`) e **GUI** sobre a mesma core; sem args abre a GUI.
- **`_MANIFEST.md` + `_TREE.md`** na saída, opcionalmente nomeados com o nome da pasta (DEC-022).
  O `_TREE` diz o que foi pulado e por quê, com **amostra** nas pastas grandes (0.14.0).
- **`.flatdropignore` + `.gitignore` aninhado** (DEC-014), com `!` para liberar o que o git
  esconde — funcionando também **dentro de pasta ignorada** desde o FIX-011 (0.12.0).
- **Editor visual de `.flatdropignore`** na GUI, com **trava por pasta** (DEC-027) — sujeito ao
  bug acima.
- **Force-include por caminho exato** (`++caminho`, DEC-021), que resgata arquivo barrado por
  ignore embutido (vence tudo menos «sensível»).
- **Gerador de `.bat`** e **multi-fonte ao vivo** na GUI; **persistência** de config e recentes
  (só-GUI, DEC-020); `root_in_name`; filtros de execução; Downloads resolvido de verdade (FIX-002);
  poda de pastas visível (FIX-001).

## Qualidade / testes

- **79 testes** relatados verdes em 2026-07-29 (Code, wo0043). Rodar da raiz: `pytest -q` (o
  `conftest.py` resolve o import — FIX-005) ou `python -m pytest -q`.
- A distribuição por arquivo não é reconferida desde 21/07 (68 testes); os 11 novos vieram das
  wo0038 e wo0041–0043, em `test_core.py`.
- A GUI **não** é coberta pela suíte (tkinter fora do CI) → smoke manual no Windows.
- **Lacuna conhecida:** nenhum dos 8 testes do editor exercita linha manual fora do bloco
  gerenciado. É o que deixou o bug passar — a WO da correção precisa fechar essa lacuna.

## Em aberto (produto) — backlog curto, na ordem sugerida

1. **A correção do bug do bloco gerenciado**, começando pelas duas perguntas acima.
2. **Editor deve gravar `pasta/*` + `!mantido`** em vez de listar a pasta parcial por folha.
   Depois do FIX-011 deixou de ser bloqueio, mas a lista por folha continua não sendo à prova de
   arquivo novo. **Análise em discussão:** `meta/analises/260728-ANALISE-gerador-flatdropignore.md`
   — três opções (B, C, D); a decisão depende de responder *arquivo novo em pasta curada entra ou
   fica fora?*.
3. **FlatDrop grava o estado do repo no `_MANIFEST`** (`git log -1` + resumo de `git status`, como
   foto do momento da geração). Apaga uma ressalva inteira do lado do chat.
4. **Mostrar a REGRA de ignore que casou**, não só a contagem por motivo.
5. Aviso mais visível quando o `pathspec` está ausente.
6. Adiadas, com gatilho de retorno em `IDEAS.md`: multi-raiz na GUI, `pasta/` como exclusão dura,
   UI-2/UI-3, saída da CLI ASCII-safe, formato «caminho escrito».

## Riscos / pontos de atenção

- **`meta/DECISIONS.md` passou de 700 linhas** (864, 38 entradas). O arquivamento em
  `DECISIONS-archive.md` estava adiado **de propósito** durante a migração de vocabulário — o
  bloqueio caiu: fazer depois do commit da wo0044.
- **`.claude/settings.json` agora permite escrita fora do repo** (`additionalDirectories: ["../"]`)
  para o relatório do Code na pasta-pai (DEC-028). Concessão estreita e deliberada; se a escrita
  for negada, o Code diz e segue.
- O fix do Downloads e a GUI só são exercidos por estrutura/lógica no sandbox (sem Windows no
  ambiente do chat); a validação final é o smoke manual no PC.
- A estimativa de tokens segue grosseira (`bytes/4`) e não vale para binários.
- `.flatdropignore` faz uma passada extra na árvore para coletar os ignores (aceitável; fundível
  numa passada depois, se virar gargalo).
- **Hábito da pausa:** `git push` antes de fechar a sessão. O remoto
  (`github.com:SiluJones/flatdrop.git`) rastreia a `main` desde 21/07, então o `git status` avisa
  sozinho quando houver commit local não enviado.
