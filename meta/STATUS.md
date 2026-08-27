# STATUS — FlatDrop

Estado atual do projeto. Atualize **a cada turno em que algo mudar** (rolante: o resolvido sai
daqui e vira `CHANGELOG`/`DECISIONS`). **Médio e longo prazo não ficam aqui — ficam no `ROADMAP`.**

> **Mudanças nesta revisão (2026-08-24) — quatro WOs e o fim do ciclo da carta 01:**
>
> - **wo0050 · wo0051 · wo0052 · wo0053 aplicadas e empurradas.** Os três itens da carta 01 do KCM
>   estão fechados no código; a **carta 02 foi escrita** e sai deste turno.
> - **Números lidos nesta revisão** (relatórios de aplicação de 22:23, 22:45 e 23:30 + manifesto
>   das 23:49): **118 testes verdes**, commit `03eeecf`, `main` limpo e sincronizado.
> - **Bug real encontrado pela suíte durante a wo0053:** o `.strip()` do helper `_git` comia o
>   espaço inicial de `" M caminho"` na primeira linha do `--porcelain`, e o caminho saía truncado.
>   Corrigido com `--branch` (a linha `## ramo…` blinda a borda). Está na carta 02, seção 2.6.
> - **A DEC-020 foi acionada e liberada uma vez**, com autorização escrita do autor e escopo
>   delimitado (glifos de saída em `cli.py`, wo0052). Nenhum argumento ou semântica mudou.
> - **Ficou o que ainda é o agora:** a validação visual pendente no Windows e a decisão em aberto
>   do gerador (`pasta/*` + `!mantido`).

> **Mudanças na revisão anterior (2026-08-02) — a sessão mais densa do projeto até aqui:**
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
- **Data:** 2026-08-24
- **Commit:** **leia no `_MANIFEST`** («Git (foto da geração)»), que desde a wo0048 traz
  `git log -1` e o resumo do `git status`. **Este campo não guarda mais hash:** guardar um aqui
  garante que ele nasça velho — a wo0049 se commitou DEPOIS de escrever esta linha, e ela passou
  20 dias apontando `9d8e62f` quando o repo estava em `8913a39`. Uma fonte de verdade por dado.
- **Fase:** F1 (MVP) OK · F2 (robustez/conveniência) **concluída no que estava em aberto** —
  restam apenas itens adiados com gatilho (multi-raiz na GUI, UI-2/UI-3) · F3 (gerador de `.bat` +
  multi-fonte na GUI) OK · F4 (distribuição) não iniciada — ver `ROADMAP.md`.
- **Situação geral:** em uso real, **estável**, em **stand-by** por decisão do autor. Fluxo do
  monorepo `cinzeiro` coberto de ponta a ponta (GUI, CLI e `.bat`). Modo Claude Code em operação;
  **WOs 0001–0057 aplicadas e commitadas** (as 0001–0037 mantêm o nome `spec00NN`, anteriores à
  DEC-023). **122 testes verdes.** **Nenhum bug aberto** — o da 0.13.0 fechou na 0.15.0.
- **Contorno revogado:** o «use a curadoria manual OU o editor, nunca os dois» **não vale mais**.
  Respeitada a anatomia normativa (DEC-029), os dois convivem no mesmo arquivo.

## ⏳ Validação visual no Windows — 2 de 3 conferidos em 27/08

**[relatado pelo dono, com print]** O dono rodou a GUI e o editor de `.flatdropignore` sobre **outro
repositório** (um projeto com `meta/`, `src/`, `.githooks/` — não o FlatDrop) e mandou três capturas.
O que elas mostram:

1. **`travada (manual)` — CONFIRMADO.** Na coluna «Arquivo novo», `logs`, `meta/analises` e
   `meta/workorders` aparecem com o rótulo `travada (manual)`, e `.claude`, `.githooks`, `meta` e
   `src` com `entra`. É a entrega da wo0047 funcionando na tela, com a trava por pasta (DEC-027)
   visível ao lado.
2. **`askyesno` de regra depois do bloco — NÃO exercitado.** Não havia regra escrita depois do
   marcador de fechamento no arquivo testado, então o diálogo não tinha por que aparecer.
3. **Aviso de contrabarra — NÃO exercitado**, pelo mesmo motivo: o `.flatdropignore` daquele projeto
   não tem nenhuma linha com `\`.

**O que falta, e é o gesto de cinco minutos:** num `.flatdropignore` de teste, pôr uma linha com `\`
e abrir o editor (o aviso deve trazer arquivo e linha; corrigir para `/` e reabrir: sem aviso), e
escrever uma regra depois do marcador de fechamento e salvar (deve perguntar antes de mover o bloco
para o fim). No mesmo passo, o smoke da wo0045: salvar sem mexer em nada e conferir que o arquivo
**não** ganhou linha em branco no fim; duplicar o bloco à mão e conferir que o salvamento **recusa**
com mensagem e não escreve nada.

> **Por que os dois que faltam não são «quase o mesmo teste»:** os três caminhos são independentes
> no código — o rótulo vem de `source()`, o aviso vem do parser de padrões e o `askyesno` vem do
> salvamento. Ver um funcionar não diz nada sobre os outros dois.

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

- **122 testes verdes** em 2026-08-25 (92 → 100 → 109 → 111 → 118 → 122, um degrau por WO). Rodar
  da raiz: `pytest -q` (o `conftest.py` resolve o import — FIX-005) ou `python -m pytest -q`.
- A distribuição por arquivo não é reconferida desde 21/07 (68 testes); os 24 posteriores estão em
  `test_core.py`.
- A GUI **não** é coberta pela suíte (tkinter fora do CI) → smoke manual no Windows.
- **A lacuna que deixou o bug passar foi fechada:** os testes do editor agora exercitam linha
  manual fora do bloco, destravar sobre linha manual, marcador citado em comentário e
  **estabilidade textual** (salvar 2× dá texto idêntico, não só regras equivalentes).
- **Lacuna que encolheu (wo0050, wo0053):** os testes que precisam de `git` continuam pulando
  sozinhos onde ele não existir, mas as duas partes que mais erravam — ler a linha `##` e ler os
  caminhos do `--porcelain` — viraram funções puras (`_divergence`, `_modified_paths`) com **doze
  testes que rodam sem `git` nenhum**. Sobra dependente de ambiente só o que exige repositório de
  verdade.
- **O teste puro não substitui o ponta a ponta, e a wo0053 provou:** o parser passava nos cinco
  testes puros e mesmo assim o manifesto saía errado, porque o defeito estava no `.strip()` do
  helper que entregava a string ao parser. Só o teste que gerou um manifesto de verdade viu.

## Em aberto (produto) — backlog curto, na ordem sugerida

1. **Fechar a validação visual** — 2 dos 3 comportamentos foram confirmados em 27/08 (ver a seção
   «Validação visual no Windows»). Faltam o **aviso de contrabarra** e o **`askyesno` de regra depois
   do bloco**, que precisam de um `.flatdropignore` de teste montado de propósito.
2. **Editor deve gravar `pasta/*` + `!mantido`** em vez de listar a pasta parcial por folha.
   Depois do FIX-011 deixou de ser bloqueio, mas a lista por folha continua não sendo à prova de
   arquivo novo. **Análise em discussão:** `meta/analises/260728-ANALISE-gerador-flatdropignore.md`
   — três opções (B, C, D); a decisão depende de responder *arquivo novo em pasta curada entra ou
   fica fora?*.
3. **Arquivar o `meta/DECISIONS.md`** em `DECISIONS-archive.md`. O arquivo tem **69 KB e 1.124
   linhas** (medido em 27/08, `wc -l`), contra o teto de ~700 que agora está escrito no cabeçalho dele (wo0061). Precisa
   de um critério de corte antes de virar WO — por data ou por fase encerrada —, e o critério é
   decisão do autor.
   *(O item que estava neste lugar, o **merge do KCM v1.120.0**, saiu: fechou em 27/08 nas quatro
   fases, wo0054 a wo0061. 20 de 20 arquivos do pacote comparados, 18 de 18 ocorrências de linha
   revogada tratadas. O porquê vive na **DEC-032** e na **DEC-033**; o que sobrou de pendência está
   aqui como itens 7 e 8.)*
4. **Mostrar a REGRA de ignore que casou**, não só a contagem por motivo. **Reforçado em 07/08**
   pela nota `260807-1324`: em projeto irmão, um `.xlsx` inteiro sumiu do achatamento por estar em
   pasta gitignorada e a ausência só foi notada sessões depois. A contagem por motivo já existe na
   saída — o que falta é a regra.
5. Aviso mais visível quando o `pathspec` está ausente.
6. Adiadas, com gatilho de retorno em `IDEAS.md`: multi-raiz na GUI, `pasta/` como exclusão dura,
   UI-2/UI-3, formato «caminho escrito». *(A **saída da CLI ASCII-safe** deixou de ser adiada — o
   gatilho disparou em 02/08 e a curadoria de 23/08 a moveu para «Ativas».)*
7. **Critérios de conclusão das quatro fases do `ROADMAP`.** A regra entrou no cabeçalho (wo0061);
   os critérios em si precisam ser decididos com o autor — a Fase 2 está «quase concluída» há dois
   meses, que é o sintoma de fase sem critério.
8. **~~Passada de diff sobre o `meta/workorders/_TEMPLATE.md`~~ — FEITA em 27/08 (wo0063).** O
   pacote voltou ao mount e a comparação rendeu três adoções: as seções **«Inventário»** e
   **«Medição prévia»**, e o parágrafo *«afirmação sobre artefato legível não é opinião, é
   leitura»*. Os dois blocos que este projeto escreveu sozinho (extrair âncora por script; a âncora
   cobre o que o texto novo torna redundante) **não existem no kit** e ficaram — voltam ao KCM na
   próxima carta.

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

---

## Última conversa

**2026-08-27** — o merge do KCM v1.120.0 fechou (wo0054–wo0061), o desvio do push foi revogado
(DEC-033, wo0062) e a última pendência do merge — a passada de diff no modelo de WO — fechou na
wo0063. **Onde parou:** nada em curso; o kit está inteiro e o produto não anda desde 25/08.
**Próximo passo óbvio:** decidir *arquivo novo em pasta curada entra ou fica fora?* — é a análise
mais antiga em aberto (28/07) e destrava o item 2 do backlog e a Fase 2 do ROADMAP.

> **Como manter esta seção:** 2 a 4 linhas, reescritas por inteiro a cada turno que mexer no
> projeto — o que foi feito, **onde parou** e o **próximo passo óbvio**. É a primeira coisa que se
> lê para retomar o fio, e ela é alimentada pelo «Onde parei» do log do dia. Não vire lista: se
> precisar de mais de quatro linhas, o excesso pertence ao log ou ao backlog.
