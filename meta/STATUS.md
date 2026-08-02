# STATUS — FlatDrop

Estado atual do projeto. Atualize ao fim de cada sessão de trabalho (rolante: o
resolvido sai daqui e vira `CHANGELOG`/`DECISIONS`).

> **Mudanças nesta revisão (2026-08-02) — a sessão mais densa do projeto até aqui:**
>
> - **O único bug aberto fechou** (FIX-012, wo0045 + wo0046). A seção «🔴 Bug aberto» saiu daqui:
>   o desfecho vive no `CHANGELOG` 0.15.0 e no `DECISIONS`.
> - **Saiu também a seção «Registro pendente — wo0044»**, aplicada em 02/08 às 11:26.
> - **Entraram três comportamentos novos** (git no manifesto, `travada (manual)`, aviso de
>   contrabarra) e **uma convenção**: a anatomia normativa do `.flatdropignore` (DEC-029).
> - **Ficou o que ainda é o agora:** a validação visual pendente no Windows, a decisão em aberto
>   do gerador (`pasta/*` + `!mantido`) e os pontos de atenção que seguem valendo.
> - **Números lidos nesta revisão**, não previstos: 92 verdes e commit `9d8e62f`, dos quatro
>   relatórios de aplicação e do manifesto das 16:50.

- **Versão:** **0.15.0** no `__init__.py` — fecha o bug do bloco gerenciado e abre o estado do git
  no manifesto.
- **Data:** 2026-08-02
- **Commit:** `9d8e62f` (wo0048), branch `main`, **limpo** e com push feito. **Este campo deixou de
  depender de relato:** desde a wo0048 o `_MANIFEST` traz `git log -1` e o resumo do `git status`
  como foto do momento da geração — leia de lá, e só peça se o manifesto for de uma versão
  anterior.
- **Fase:** F1 (MVP) OK · F2 (robustez/conveniência) **concluída no que estava em aberto** —
  restam apenas itens adiados com gatilho (multi-raiz na GUI, UI-2/UI-3) · F3 (gerador de `.bat` +
  multi-fonte na GUI) OK · F4 (distribuição) não iniciada — ver `ROADMAP.md`.
- **Situação geral:** em uso real, **estável**, em **stand-by** por decisão do autor. Fluxo do
  monorepo `cinzeiro` coberto de ponta a ponta (GUI, CLI e `.bat`). Modo Claude Code em operação;
  **WOs 0001–0049 aplicadas e commitadas** (as 0001–0037 mantêm o nome `spec00NN`, anteriores à
  DEC-023). **92 testes verdes.** **Nenhum bug aberto** — o da 0.13.0 fechou na 0.15.0.
- **Contorno revogado:** o «use a curadoria manual OU o editor, nunca os dois» **não vale mais**.
  Respeitada a anatomia normativa (DEC-029), os dois convivem no mesmo arquivo.

## ⏳ Pendente de validação visual no Windows

O ambiente do Claude Code não tem display do Windows, então a **lógica** dos três foi exercitada e
passou, mas **ninguém viu a tela**. É o primeiro gesto de quem retomar, e leva cinco minutos:

1. **`travada (manual)`** — abrir o editor num projeto com pasta fechada por linha manual e
   conferir a coluna «Arquivo novo». (`source(pasta/__flatdrop_arquivo_novo__)` já devolve
   `flatdropignore` corretamente — o que falta é ver o rótulo.)
2. **Aviso de contrabarra** — pôr uma linha com `\` num `.flatdropignore`, abrir o editor: o
   aviso deve aparecer com arquivo e linha; corrigir para `/` e reabrir: sem aviso.
3. **`askyesno` de regra depois do bloco** — escrever uma regra depois do marcador de fechamento
   e salvar: deve perguntar antes de mover o bloco para o fim.

E, no mesmo passo, o smoke da wo0045: salvar sem mexer em nada e conferir que o arquivo **não**
ganhou linha em branco no fim; duplicar o bloco à mão e conferir que o salvamento **recusa** com
mensagem e não escreve nada.

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

- **92 testes verdes** em 2026-08-02 (79 → 82 → 86 → 88 → 92, um degrau por WO). Rodar da raiz:
  `pytest -q` (o `conftest.py` resolve o import — FIX-005) ou `python -m pytest -q`.
- A distribuição por arquivo não é reconferida desde 21/07 (68 testes); os 24 posteriores estão em
  `test_core.py`.
- A GUI **não** é coberta pela suíte (tkinter fora do CI) → smoke manual no Windows.
- **A lacuna que deixou o bug passar foi fechada:** os testes do editor agora exercitam linha
  manual fora do bloco, destravar sobre linha manual, marcador citado em comentário e
  **estabilidade textual** (salvar 2× dá texto idêntico, não só regras equivalentes).
- **Lacuna que fica:** os quatro testes de git pulam sozinhos onde não houver `git` instalado —
  verde num ambiente sem git não prova nada sobre a wo0048.

## Em aberto (produto) — backlog curto, na ordem sugerida

1. **Validar na tela os três comportamentos novos** (seção «Pendente de validação visual»).
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
