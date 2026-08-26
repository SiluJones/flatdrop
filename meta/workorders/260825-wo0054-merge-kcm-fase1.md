# WO 0054 — merge do KCM v1.120.0, fase 1: o que é conserto, não merge

> **Tipo:** mista — CONFIG (`.claude/settings.json`, `.claude/skills/wrap/SKILL.md`,
> `.flatdropignore`, `CLAUDE.md`) + REGISTRO (`meta/DECISIONS.md`, `meta/STATUS.md`).
> **Config sugerida:** modelo intermediario, `/effort` medio. Nenhuma edicao exige julgamento.
> **Pre-requisito:** commit `03eeecf`, **118 testes verdes**. A arvore NAO esta limpa: o
> `meta/STATUS.md` tem a entrega do turno anterior salva e nao commitada — **isso e esperado** e
> entra no mesmo commit desta WO.
> **Base:** pacote `template-update` v1.120.0 do KCM (`_UPDATE-MANIFEST.md`, secoes «Linhas
> revogadas» e «Correcoes obrigatorias») + carta 03, ambos de 2026-08-25. Autorizacao do autor no
> mesmo dia.
> **Ancoras lidas em:** *(campo novo, adotado do modelo v1.120.0 — declara o trecho literal lido
> NESTE turno para escrever cada ancora)*
> - `.claude/settings.json` — lido inteiro (12 linhas); `"allow": [` seguido de
>   `"Read", "Edit", "Grep", "Glob",`.
> - `.claude/skills/wrap/SKILL.md` — lido inteiro (13 linhas), incluindo a linha
>   `- Me mostre o \`git diff\` e o comando de commit (...)`.
> - `.flatdropignore` — lido inteiro (39 linhas), cabecalho e bloco gerenciado.
> - `CLAUDE.md` — lido inteiro (34 linhas); linha 3 comeca com `> Arquivo-raiz lido pelo Claude
>   Code em toda sessão.`
> - `meta/STATUS.md` — item 3 do backlog, na versao que a wo0053 deixou.
> - `meta/DECISIONS.md` — ultimas linhas, fim da DEC-031.
> **Idempotencia:** procure `"Write"`, `DEC-032` e `Resolva o push ANTES`; se ja existirem, **PULE**.
> **Proximo comando:** `/apply-wo meta/workorders/260825-wo0055-manifesto-linha-ponteiro.md`

> **Canal dos meta neste ciclo = CODE** para `STATUS` e `DECISIONS` (esta WO E o registro deles).
> **Nao toque** em `meta/IDEAS.md` nem em `meta/CEREBRO.md` — o CEREBRO e fase 2.

---

## 1. Por que

Este projeto esta **23 versoes atras** do kit (marca no `CEREBRO.md`: v1.95.0; pacote: v1.120.0).
Varredura feita em 2026-08-25 sobre o mount: **23 ocorrencias** de linha revogada, 18 propostas
para remocao, 5 classificadas como relato legitimo. Esta WO faz **so a parte que nao tem decisao
dentro** — conserto de defeito conhecido, com texto exato. A fusao do `CEREBRO.md` e das instrucoes
e a fase 2, e nao entra aqui.

**A varredura tambem achou coisa que nao estava na lista do kit.** O `.flatdropignore` carrega uma
instrucao viva mandando editar o arquivo A MAO «enquanto o bug do bloco gerenciado nao for
corrigido» — o bug fechou na 0.15.0 (FIX-012), o contorno esta revogado no `STATUS.md` e a DEC-029
descreve a anatomia que faz os dois conviverem. Nenhuma busca pelo texto do kit acharia essa linha,
porque a linha e nossa. Ela saiu porque o manifesto manda varrer **o proprio arquivo de exclusao**.

**E a superficie mais grave nao estava no mount.** O `INSTRUCOES-DO-PROJETO.md` — lido em TODO
turno — era excluido do achatamento por uma justificativa escrita no `.flatdropignore` («ja e lida
pelo painel do Projeto; subir seria a mesma coisa duas vezes»). **Cinco das 23 ocorrencias moravam
la**, entre elas a que mandava reler o mount so quando o autor sinalizasse upload — revogada pelo
kit na v1.90.0. Em 23/08 essa regra produziu a falha exata que ela descreve: o assistente abriu um
turno sem reler o mount e quase escreveu uma WO com ancoras de arquivos ja mudados. **O
`CEREBRO.md` mandava reler a cada turno; as instrucoes, lidas sempre, mandavam esperar o sinal.**

---

## Edicao 1 — `.claude/settings.json` · `Write` no `allow`

*(Correcao obrigatoria do pacote, item 2 de 3. Os outros dois ja estao certos aqui: nao ha linha
`//` depois do `}`, e o `additionalDirectories` esta presente.)*

**Ancora:**

```
      "Read", "Edit", "Grep", "Glob",
```

**Substituir por:**

```
      "Read", "Write", "Edit", "Grep", "Glob",
```

> Por que: as skills mandam CRIAR o log do dia e o relatorio de trabalho. Sem `Write` isso nao e
> negado em silencio — vira **pedido de aprovacao a cada arquivo novo**, e numa sequencia longa o
> passo que pede permissao e o primeiro a ser pulado. Este arquivo **nao** tem
> `defaultMode: acceptEdits`, entao a falta nao esta disfarcada: o relatorio da wo0052 registra o
> sintoma previsto (uma escrita fora da raiz negada pela permissao).

## Edicao 2 — `.claude/skills/wrap/SKILL.md` · as tres linhas revogadas e o que entra no lugar

**Ancora** (a linha do `git diff`, e so ela):

```
- Me mostre o `git diff` e o comando de commit (uma linha por comando, mensagem SEM acento, Conventional Commits).
```

**Substituir por:**

```
- ANTES de escrever qualquer coisa: abra o relatório mais recente em `../AAMMDD-HHMM-code-flatdrop.txt` e confira o que ele AFIRMA contra `git status` e `git log`. Relatório é escrito antes da última ação, então um push que saiu depois dele fica registrado como não feito — foi o que aconteceu com o da wo0051. Divergência vira uma linha de correção no log do dia; conferência que passa não vira linha.
- Confira o `git diff`: a forma esperada, nada além. Mensagem de commit SEM acento, Conventional Commits.
- Ao mudar um NÚMERO ou um ESTADO no `meta/STATUS.md` (contagem de testes, versão, commit, «funciona até X»), procure o valor ANTIGO no arquivo INTEIRO e atualize todas as ocorrências — o cabeçalho não é o único lugar onde ele aparece, e a cópia esquecida no meio do texto passa a mentir. Aconteceu aqui: o campo `Commit` ficou 20 dias apontando um hash que já não era o do repo.
- Escreva o log do dia em `logs/AAAA-MM-DD.md` (formato em `meta/LOG-TEMPLATE.md`). Se o arquivo do dia NÃO existe, CRIE — não regenerar é uma coisa, não criar é outra.
- **Verde:** `add` e `commit` sem perguntar. **Push:** peça confirmação — **DESVIO REGISTRADO** deste projeto em relação ao kit v1.104.0, que manda empurrar sem perguntar (motivo e revisão em DEC-032). **Resolva o push ANTES de escrever o relatório:** o relatório é o ÚLTIMO passo e diz o que de fato aconteceu — empurrado com o hash, ou não empurrado com o motivo. Se a confirmação chegar depois de o relatório existir, **reescreva o relatório**, não deixe a versão velha valendo.
- **Vermelho** (suíte falhou, âncora não encontrada, `git diff` com arquivo fora do previsto): não commite e não empurre. Feche com um MENU de saídas reais, a recomendada em primeiro lugar e marcada `(Recomendado)` — pela ferramenta `AskUserQuestion` se ela existir; sem ela, menu numerado em texto, **dizendo que caiu no fallback**. Nunca pergunte em prosa: pergunta escrita no meio do texto passa despercebida.
```

## Edicao 3a — `.flatdropignore` · a instrucao obsoleta sai

**Ancora** (duas linhas do cabecalho, fora do bloco gerenciado):

```
# - Enquanto o bug do bloco gerenciado nao for corrigido, este arquivo e editado A MAO (ver
#   meta/STATUS.md): o gerador e cego para linha manual e duplicaria dentro do bloco o que esta
#   fora dele.
```

**Substituir por:**

```
# - O editor e a curadoria manual CONVIVEM desde a 0.15.0 (FIX-012 + DEC-029): o bloco gerenciado
#   e um diff contra o que ja existe fora dele, e vai sempre para o fim do arquivo. O contorno
#   antigo ("edite este arquivo a mao") esta REVOGADO.
```

## Edicao 3b — `.flatdropignore` · a justificativa que sustentava a exclusao das instrucoes

**Ancora:**

```
# INSTRUCOES-DO-PROJETO.md ja e lida em todo turno pelo painel do Projeto: subir ao mount seria
# a mesma coisa duas vezes. Segue versionada no git, so nao vai aqui.
```

**Substituir por:**

```
# INSTRUCOES-DO-PROJETO.md SOBE ao mount desde 2026-08-25 (DEC-032). A justificativa antiga era
# "o painel ja a entrega, subir seria a mesma coisa duas vezes" — e ela estava errada: o painel
# entrega um TEXTO, o arquivo em disco e outro OBJETO, e nao havia como conferir se batiam porque
# os dois nunca chegavam juntos. Enquanto ficou fora, foi a superficie com mais linha revogada
# viva do projeto, e e a mais lida de todas.
```

## Edicao 3c — `.flatdropignore` · a linha sai do bloco gerenciado

**Ancora** (dentro do bloco `# >>> flatdrop-editor`):

```
!meta/workorders/_TEMPLATE.md
INSTRUCOES-DO-PROJETO.md
# <<<
```

**Substituir por:**

```
!meta/workorders/_TEMPLATE.md
# <<<
```

> **Armadilha desta edicao, e ela e real:** essa linha esta DENTRO do bloco gerenciado, que o
> editor da GUI reescreve inteiro a cada salvamento a partir do estado das caixas. Tirar a linha
> aqui **nao** desmarca o arquivo na GUI. Registre no relatorio que **o autor precisa abrir o
> editor uma vez e conferir que `INSTRUCOES-DO-PROJETO.md` nao esta marcado para excluir** — senao
> o proximo salvamento pela GUI devolve a linha em silencio.

## Edicao 4 — `CLAUDE.md` · sessao vira turno

**Ancora:**

```
> Arquivo-raiz lido pelo Claude Code em toda sessão. Mantenha CURTO (< 200 linhas — custa token em todo turno).
```

**Substituir por:**

```
> Arquivo-raiz lido pelo Claude Code em todo TURNO. Mantenha CURTO (< 200 linhas — custa token em todo turno).
```

> Por que uma palavra vira edicao: o kit revogou o par «sessao/turno» na v1.106.0 porque o nome
> ensina a cadencia. «Lido em toda sessao» convida a ler uma vez e seguir de memoria — que e
> exatamente o defeito que esta WO conserta em outros tres lugares.

## Edicao 5 — `meta/DECISIONS.md` · DEC-032 no fim do arquivo

**Ancora** (ultimas linhas, fim da DEC-031):

```
`git_snapshot`, que já tem seis testes em cima. O parser (`_modified_paths`) é puro e roda sem git
instalado. Em multi-fonte, o `rel` pode não ser relativo a `plan.root`; a interseção então não casa
e a linha não sai — falso negativo, nunca falso positivo.
```

**Inserir IMEDIATAMENTE APOS:**

```

## DEC-032 — as instruções do projeto sobem ao mount; e o desvio registrado sobre o push

**Contexto.** Merge do template-update do KCM **v1.120.0** (o `CEREBRO.md` daqui carregava a marca
da v1.95.0 — 23 versões de distância). A seção «Linhas revogadas» do pacote aponta texto que foi
apagado do kit de propósito e que segue vivo nos arquivos deste projeto, invisível a qualquer
comparação. **Varredura de 2026-08-25: 23 ocorrências**, 18 para remoção e 5 classificadas como
relato legítimo (reescrever relato falsificaria registro). Desta WO saem 8; o restante é a fase 2.

**Decisão 1 — `INSTRUCOES-DO-PROJETO.md` passa a subir ao mount.** A regra antiga excluía o arquivo
com a justificativa de que o painel do Projeto já o entrega. Está errada: o painel entrega um
TEXTO, o arquivo em disco é outro OBJETO, e não havia como conferir se batiam — os dois nunca
chegavam juntos. **Conferido em 25/08, pela primeira vez desde que o projeto existe: batem, linha a
linha.** O custo de subir é ~7 KB por geração; o benefício é que a superfície mais lida do projeto
passa a ser auditável por quem a lê.

**O que sustenta:** enquanto ficou fora, foi onde mais linha revogada sobreviveu — 5 das 23,
inclusive a que mandava reler o mount só mediante sinal do autor (revogada na v1.90.0). Em
2026-08-23 essa regra produziu a falha que ela descreve: o assistente abriu um turno sem reler o
mount e quase escreveu uma WO com âncoras de arquivos já mudados. O `CEREBRO.md` mandava reler a
cada turno; as instruções, lidas sempre, mandavam esperar o sinal. **Entre uma regra correta lida
às vezes e uma regra errada lida sempre, venceu a errada** — e é por isso que a exclusão de uma
superfície de leitura não é economia de tokens, é ponto cego.

**Decisão 2 — desvio registrado: o executor continua pedindo confirmação antes do `push`.** O kit
revogou, na v1.104.0, o desenho em que o chat entrega o bloco de git ao dono, e o substituiu por
«verde: o executor roda `add`/`commit`/`push` sem perguntar». **Adotamos tudo menos o push
automático.** O resto entra inteiro — e a parte mais valiosa é *o push se resolve ANTES de escrever
o relatório, que é o último passo*, que é a nossa própria Devolução 2 ao KCM voltando pronta.

**Por que o desvio.** Empurrar muda o estado de um remoto, e o Code pediu confirmação nas quatro
últimas WOs sem que isso custasse nada além de uma linha. A troca é: um turno a mais contra um
push que ninguém pediu. **Fica em revisão** — o gatilho para reabrir é a primeira vez que a
confirmação atrasar um relatório correto, que é o defeito oposto e já aconteceu uma vez (wo0051).

**Consequências.** A `wrap/SKILL.md` passa a citar este desvio no próprio texto, para que ninguém o
leia como esquecimento. O `.flatdropignore` perde a linha das instruções e ganha a explicação do
porquê — mas a linha vive DENTRO do bloco gerenciado, então o editor da GUI pode devolvê-la no
próximo salvamento: conferir uma vez na tela faz parte desta decisão.
```

## Edicao 6 — `meta/STATUS.md` · o item 3 do backlog vira o estado do merge

**Ancora** (item 3, texto escrito pela wo0053):

```
3. **Merge do template-update do KCM** — o autor avisou em 24/08 que sobe a versão nova depois
   deste ciclo. **Duas convenções nossas esperam esse merge** e estão registradas em `IDEAS.md` ›
   Feedback para o Kit, para não virarem texto local que o kit novo talvez reescreva: «com WO no
   turno, quem aplica commita tudo» e «o relatório só declara o push depois do push». Quando a
   v1.97.0 chegar, conferir também o P11 e o princípio de higiene, que o KCM pediu em 02/08.
   *(A carta 02 saiu em 24/08 e fechou o ciclo da carta 01: itens 1 e 3 entregues, item 2 recusado
   com a contraproposta entregue junto.)*
```

**Substituir por:**

```
3. **Merge do KCM v1.120.0 — em curso, 3 fases.** O pacote chegou em 25/08 com a carta 03 (o
   `CEREBRO.md` daqui marcava v1.95.0: 23 versões de distância). **Varredura de linhas revogadas:
   23 ocorrências, 18 para remoção, 5 relato legítimo.** Duas coberturas, que medem coisas
   diferentes e não se substituem:
   - **arquivos do pacote comparados: 8 de 20** — faltam os 2 de `fusao` e os 10 modelos de `meta/`;
   - **ocorrências corrigidas: 8 de 18** (esta WO) — e a varredura é **PARCIAL**: não alcançou
     `logs/` nem `meta/workorders/`, que o `.flatdropignore` mantém fora do mount.
   **Fase 1 (wo0054, feita):** `Write` no `settings.json`, as 3 linhas revogadas da `wrap/SKILL.md`,
   a instrução obsoleta do `.flatdropignore`, `sessão`→`turno` no `CLAUDE.md`, e as 4 das
   instruções — que passam a subir ao mount (DEC-032). **Fase 2 (a fazer):** fusão do
   `meta/CEREBRO.md` (10 ocorrências vivas) com o template de 83 KB, mais as duas seções novas do
   `CLAUDE.md` («Quando eu pedir medição» e «Push e relatório — nesta ordem»). **Fase 3:** os
   modelos (`_TEMPLATE.md` de WO e de análise, e os 10 de `meta/`).
   *(O raciocínio completo do merge está numa análise que o autor decidiu NÃO versionar — por isso
   os números que importam estão aqui e na DEC-032, e não numa referência a arquivo.)*
```

---

## Fora de escopo

- **`meta/CEREBRO.md`** — 10 ocorrências vivas, natureza `fusao`, 83 KB de template contra 54 KB
  vivos. É a fase 2 e pede leitura das duas versões inteiras. **Não encoste.**
- **`INSTRUCOES-DO-PROJETO.md`** — o chat entrega o arquivo inteiro neste mesmo turno (o autor
  precisa colá-lo também no painel do Projeto, que é a outra cópia). Esta WO **não edita** o
  arquivo; só o inclui no commit.
- **Os 10 modelos de `meta/`** e os dois `_TEMPLATE.md` — fase 3.
- **Push automático no verde** — desvio registrado na DEC-032, decisão consciente.

## Armadilhas desta WO

- **A árvore já está suja antes de você começar** (`meta/STATUS.md` modificado, do turno anterior).
  Isso é esperado e entra no mesmo commit. O que **não** é esperado é qualquer outro arquivo
  aparecendo no `git diff`.
- A Edição 3c mexe **dentro do bloco gerenciado** do `.flatdropignore` — leia a nota da edição.
- `.claude/settings.json` é JSON: uma vírgula a mais e o arquivo INTEIRO é descartado em silêncio,
  com todas as permissões junto. Depois de editar, valide:
  `python -c "import json;json.load(open('.claude/settings.json'));print('json ok')"`.
- O texto novo da Edição 2 **tem acentos** — é markdown de skill, não `.bat` (FIX-003) e não
  mensagem de commit. Mantenha.

---

## Depois de aplicar — conferência antes do commit

- [ ] `git diff` mostra exatamente: `.claude/settings.json`, `.claude/skills/wrap/SKILL.md`,
      `.flatdropignore`, `CLAUDE.md`, `meta/DECISIONS.md`, `meta/STATUS.md` — mais o
      `INSTRUCOES-DO-PROJETO.md` que o chat entregou (modificado, não editado por você).
- [ ] `python -c "import json;json.load(open('.claude/settings.json'));print('json ok')"` imprime
      `json ok`.
- [ ] **Varredura de conferência** — rode e reporte o número cru com o comando:
      `grep -rniE "de cada sess|fim de sess|inicio de sess|toda sess" CLAUDE.md .claude/ INSTRUCOES-DO-PROJETO.md`
      **Esperado: 0.** *(Não inclua `meta/` — o `CEREBRO.md` é fase 2 e vai devolver 7.)*
- [ ] `grep -n "INSTRUCOES-DO-PROJETO" .flatdropignore` → só a linha de **comentário**, nenhuma
      regra ativa.
- [ ] **Prova de vida da mudança que importa** — achate este repositório
      (`python run.py . --dest <scratch> --only-ext md`) e confirme que
      **`INSTRUCOES-DO-PROJETO.md` agora aparece na tabela do `_MANIFEST`**. Antes desta WO ele não
      aparecia; se continuar sem aparecer, a Edição 3c não pegou.
- [ ] **WO só de config/doc:** não há suíte a rodar aqui, mas rode `python -m pytest -q` mesmo
      assim e confirme **118** — se mudou, alguma edição saiu do lugar previsto.
- [ ] **Invariante DEC-020:** nada de `flatdrop/cli.py`, `gui._build_cli_args`,
      `gui._generate_bat`, `gui._sources`.
- [ ] **Passo do AUTOR, não seu** (toca a GUI, que a suíte não cobre): abrir o editor de
      `.flatdropignore` na GUI e conferir que `INSTRUCOES-DO-PROJETO.md` **não** está marcado para
      excluir. Se estiver, desmarcar e salvar. **Esta é a pergunta «está lá?», não «presta?»** — ela
      não diz se o bloco foi regravado corretamente, só se a linha voltou.

## Relatório de aplicação *(quem aplica preenche ao terminar)*

O que foi feito · o que fugiu do texto literal · arquivos tocados · resultado da suíte · o commit ·
**o push, com o resultado real** — e o relatório é escrito DEPOIS de o push estar resolvido.
Registre também o passo pendente do autor (o editor na GUI). Grave o MESMO relatório em
`../AAMMDD-HHMM-code-flatdrop.txt`.

## Commit — blocos separados, mensagem SEM acento

```
git add .claude\settings.json .claude\skills\wrap\SKILL.md .flatdropignore CLAUDE.md INSTRUCOES-DO-PROJETO.md meta\DECISIONS.md meta\STATUS.md meta\workorders\260825-wo0054-merge-kcm-fase1.md
```

```
git commit -m "chore(kit): merge do KCM v1.120.0 fase 1 - consertos e linhas revogadas" -m "Write no settings (log e relatorio deixam de pedir aprovacao a cada arquivo). wrap/SKILL: o relatorio vira o ultimo passo, depois do push resolvido; menu no caso vermelho. flatdropignore: sai a instrucao de editar a mao (revogada pelo FIX-012) e as instrucoes do projeto passam a subir ao mount. CLAUDE.md: sessao vira turno. DEC-032 registra as duas decisoes e o desvio do push."
```

```
git push
```
