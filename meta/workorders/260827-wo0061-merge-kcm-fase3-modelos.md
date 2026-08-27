# WO 0061 — merge do KCM v1.120.0, fase 3: os 11 modelos, e o merge fecha

> **Tipo:** REGISTRO — `meta/STATUS.md`, `meta/LOG-TEMPLATE.md`, `meta/DECISIONS.md`,
> `meta/ROADMAP.md`, `meta/analises/_TEMPLATE.md`, `meta/IDEAS.md`. Nao toca codigo nem `.claude/`.
> **Config sugerida:** modelo intermediario, `/effort` medio. Dez edicoes, seis arquivos, nenhuma
> exigindo julgamento — o julgamento ja foi feito ao comparar os 11 modelos.
> **Pre-requisito:** wo0060 aplicada e empurrada (`b47b652`), **122 testes verdes**, arvore limpa.
> **Base:** os 11 modelos restantes do pacote `template-update` v1.120.0, comparados um a um contra
> os arquivos vivos em 2026-08-27.
> **Ancoras lidas em:** *(as dez edicoes foram GERADAS por script a partir dos arquivos vivos do
> mount de 2026-08-27 07:44 — nenhum trecho de ancora foi digitado)*
> - `meta/STATUS.md` — linhas 3-4 (cabecalho), as tres ultimas linhas do arquivo, e o paragrafo da
>   fase 3 escrito pela wo0060.
> - `meta/LOG-TEMPLATE.md` — linhas 1-14 (cabecalho inteiro), a linha `## Objetivo da sessão` e a
>   linha do «Onde parei».
> - `meta/DECISIONS.md` — linhas 3-5 (cabecalho). `meta/ROADMAP.md` — linhas 3-4.
> - `meta/analises/_TEMPLATE.md` — a linha `- **Virou:** ...`.
> - `meta/IDEAS.md` — primeiro item de «Feedback para o Kit».
> **Idempotencia:** procure `## Última conversa`, `DECISIONS-archive.md` e `criterio de conclusao`.
> Se ja existirem, **PULE** e diga no relatorio.
> **Proximo comando:** nao ha — o merge fecha aqui.

> **Canal dos meta neste ciclo = CODE** (todos os seis).

---

## 1. Por que

Ultima fatia do merge. Os **11 modelos** que faltavam foram comparados um a um contra os arquivos
vivos, e o resultado e o esperado pela regra «template generico nunca substitui arquivo vivo
refinado»: **seis nao mudam nada** e **cinco rendem uma adocao pequena cada**.

**O que NAO muda, e por que** *(isto e resultado da comparacao, nao omissao)*:

| Modelo | Vivo | Veredito |
|---|---|---|
| `CONTEXT` | 16,3 KB × 3,0 KB | cobre tudo o que o modelo pede, com nomes proprios, e tem uma secao a mais («Modo de desenvolvimento — duas raias»). **Nada.** |
| `CHANGELOG` | 34,1 KB × 0,6 KB | so faltam `### Modificado` e `### Removido` em `[Nao lancado]` — e faltam porque nao ha o que registrar neles. **Nada.** |
| `IDEAS` | 47,3 KB × 1,8 KB | a unica diferenca estrutural e a separacao por autor, **recusada de proposito** — ver Edicao 9. A secao «Feedback para o ASU» nao se aplica (modo desligado no carimbo). **Nada.** |
| `GLOSSARY` | 15,9 KB × 0,6 KB | o agrupamento em quatro baldes e boa ideia e **nao e merge**: e reorganizar 40 termos nossos. Vira ideia com gatilho — Edicao 9. **Nada agora.** |
| `HISTORY` | 4,3 KB × 1,1 KB | o modelo sugere cinco tipos de conteudo; o nosso ja usa tres deles e nao tem material para os outros dois. **Nada.** |
| `SPEC` | 2,4 KB × 0,9 KB | o nosso e estritamente mais rico (distingue spec de WO pela DEC-023, diz ONDE cada criterio e verificado, e quando NAO escrever spec). **Nada.** |

**As cinco adocoes**, cada uma com o motivo:

1. **`STATUS` ganha «Ultima conversa»** (Edicao 2). O modelo tem uma secao que este projeto nunca
   teve: 2 a 4 linhas dizendo **onde parou** e **qual o proximo passo obvio**. A nossa nota
   «Mudancas nesta revisao» diz o que MUDOU — que e outra pergunta. E o modelo do log do dia ja
   tinha um «Onde parei» sem destino: agora ele tem.
2. **`LOG-TEMPLATE` passa a disparar por EVENTO** (Edicao 3). O nosso ainda mandava «copie ao
   iniciar uma sessao» e falava em «Sessao N». O gatilho por evento ja estava na tabela do CEREBRO
   desde a fase 2b — o molde do log era o ultimo lugar onde a regra velha sobrevivia.
3. **`DECISIONS` ganha as duas regras de manutencao no cabecalho** (Edicao 6): marcar a antiga como
   SUPERADA, e arquivar acima de ~700 linhas. **Este arquivo tem 69 KB e mais de 1.400 linhas** — a
   regra existia so no CEREBRO e no backlog, e nao no arquivo que ela governa.
4. **`ROADMAP` passa a exigir criterio de conclusao por fase** (Edicao 7). Nenhuma das nossas quatro
   fases tem um. A Fase 2 esta «quase concluida» ha dois meses, o que e exatamente o sintoma.
5. **O modelo de analise ganha uma frase** (Edicao 8): *se a leitura derrubar a premissa que
   disparou tudo, PARE*. O resto do nosso e mais rico e fica.

---

## Edicao 1 — `meta/STATUS.md` · o cabecalho, sem «sessao» e com o limite do ROADMAP

**Ancora**:

```
Estado atual do projeto. Atualize ao fim de cada sessão de trabalho (rolante: o
resolvido sai daqui e vira `CHANGELOG`/`DECISIONS`).
```

**Substituir por:**

```
Estado atual do projeto. Atualize **a cada turno em que algo mudar** (rolante: o resolvido sai
daqui e vira `CHANGELOG`/`DECISIONS`). **Médio e longo prazo não ficam aqui — ficam no `ROADMAP`.**
```

## Edicao 2 — `meta/STATUS.md` · secao nova «Ultima conversa», no fim do arquivo

**Ancora**:

```
- **Hábito da pausa:** `git push` antes de fechar a sessão. O remoto
  (`github.com:SiluJones/flatdrop.git`) rastreia a `main` desde 21/07, então o `git status` avisa
  sozinho quando houver commit local não enviado.
```

**Substituir por:**

```
- **Hábito da pausa:** `git push` antes de fechar a sessão. O remoto
  (`github.com:SiluJones/flatdrop.git`) rastreia a `main` desde 21/07, então o `git status` avisa
  sozinho quando houver commit local não enviado.

---

## Última conversa

**2026-08-27** — o merge do KCM v1.120.0 fechou nas quatro fases (wo0054 a wo0061); o `CEREBRO.md`,
o `CLAUDE.md`, as duas skills, as Instruções e os 12 modelos estão alinhados com o kit. **Onde
parou:** nada em curso. **Próximo passo óbvio:** a validação visual no Windows, que é o item 1 do
backlog e a única coisa entregue desde a 0.15.0 que ninguém viu na tela.

> **Como manter esta seção:** 2 a 4 linhas, reescritas por inteiro a cada turno que mexer no
> projeto — o que foi feito, **onde parou** e o **próximo passo óbvio**. É a primeira coisa que se
> lê para retomar o fio, e ela é alimentada pelo «Onde parei» do log do dia. Não vire lista: se
> precisar de mais de quatro linhas, o excesso pertence ao log ou ao backlog.
```

> Secao do modelo v1.120.0 que este projeto nao tinha. A nota «Mudancas nesta revisao», no topo,
> diz o que MUDOU; nenhuma das duas diz **onde parou e qual o proximo passo**, que e a pergunta de
> quem abre a conversa seguinte. O modelo do log do dia ja tem um «Onde parei» — esta secao e o
> destino dele.

## Edicao 3 — `meta/LOG-TEMPLATE.md` · o cabecalho: gatilho por evento, «Conversa N»

**Ancora**:

```
# LOG-TEMPLATE — FlatDrop

> Um arquivo por DIA (DEC-026). Segunda sessão no mesmo dia entra como
> `## Sessão N — <período>: <assunto>` neste mesmo arquivo — nunca um arquivo novo.

Este arquivo é o **molde** dos logs de sessão. NÃO é um log preenchido: copie-o
para `logs/AAAA-MM-DD.md` ao iniciar uma sessão e preencha os campos. Mantenha
este molde em branco como referência do formato.

Como usar:
1. Copie este arquivo para `logs/` com a data de hoje no nome (ex.: `logs/2026-06-05.md`).
2. Substitua os campos entre colchetes pelo conteúdo real.
3. Ao terminar, atualize também `STATUS.md` e, se houver mudança de versão,
   `CHANGELOG.md`.
```

**Substituir por:**

```
# LOG-TEMPLATE — FlatDrop

> **Referência fixa.** Este arquivo é o MOLDE — nunca é substituído pelo conteúdo preenchido.
> Um arquivo por DIA (DEC-026). Segunda conversa no mesmo dia entra como
> `## Conversa N — <período>: <assunto>` neste mesmo arquivo — nunca um arquivo novo, porque o
> nome é da data e não da conversa.

O log entra **ao bater um gatilho de evento** — cortar versão, registrar decisão ou bug grave,
virar o dia — e **não «no fim»**, que numa conversa longa nunca chega: é assim que dias inteiros
ficam sem registro. Os logs vivem em `logs/` no Git (NÃO no Projeto) e são lidos sob demanda.

Como usar:
1. Copie este arquivo para `logs/` com a data de hoje no nome (ex.: `logs/2026-06-05.md`).
   Se o arquivo do dia já existe, acrescente `## Conversa N` nele — não crie outro.
2. Substitua os campos entre colchetes pelo conteúdo real.
3. Ao terminar, atualize também `STATUS.md` (inclusive a seção «Última conversa») e, se houver
   mudança de versão, `CHANGELOG.md`.
```

## Edicao 4 — `meta/LOG-TEMPLATE.md` · «Objetivo da sessao» vira «do dia»

**Ancora**:

```
## Objetivo da sessão
```

**Substituir por:**

```
## Objetivo do dia
```

## Edicao 5 — `meta/LOG-TEMPLATE.md` · o «Onde parei» aponta para onde ele vai

**Ancora**:

```
[Estado exato ao encerrar: o que está pronto, o que ficou no meio.]
```

**Substituir por:**

```
[Estado exato ao encerrar: o que está pronto, o que ficou no meio, e o próximo passo óbvio.
Este campo alimenta a seção «Última conversa» do `STATUS.md` — escreva-o pensando em quem abre
a conversa seguinte sem ter lido esta.]
```

## Edicao 5b — `meta/LOG-TEMPLATE.md` · a ultima «sessao» do arquivo

**Ancora**:

```
- [O primeiro passo concreto para a próxima sessão.]
```

**Substituir por:**

```
- [O primeiro passo concreto para o próximo turno.]
```

> Sexta e ultima ocorrencia de «sess» neste arquivo. As outras cinco saem nas Edicoes 3 e 4.

## Edicao 6 — `meta/DECISIONS.md` · as duas regras de manutencao que faltavam no cabecalho

**Ancora**:

```
Registro de decisões de arquitetura (ADR enxuto). Cada entrada: contexto, decisão
e consequência. Decisões não se reescrevem — se mudarem, adicione uma nova que
supersede a anterior.
```

**Substituir por:**

```
Registro de decisões de arquitetura (ADR enxuto). Cada entrada: contexto, decisão
e consequência. Decisões não se reescrevem — se mudarem, adicione uma nova que
supersede a anterior e marque a antiga como **SUPERADA por DEC-N**.
**Quando passar de ~700 linhas, mova as mais antigas para `DECISIONS-archive.md`** — este arquivo
já passou de 1.400, e o arquivamento está no backlog do `STATUS`.
```

## Edicao 7 — `meta/ROADMAP.md` · criterio de conclusao por fase

**Ancora**:

```
Direção do projeto por fases. Sem datas: a ordem importa mais que o calendário.
Itens em aberto vêm de `IDEAS.md`; ao concluir, registre em `CHANGELOG.md`.
```

**Substituir por:**

```
Direção do projeto por fases. Sem datas: a ordem importa mais que o calendário.
Itens em aberto vêm de `IDEAS.md`; ao concluir, registre em `CHANGELOG.md`.
**Cada fase declara um objetivo e um critério de conclusão** — fase sem critério não fecha, só
envelhece. Marque o estado no título: ✅ concluída · 🟡 em curso/próxima · 🔵 futura · 🚫 descartada.
```

## Edicao 8 — `meta/analises/_TEMPLATE.md` · a frase que o modelo do kit tem e o nosso nao

**Ancora**:

```
- **Virou:** wo00NN / spec de feature / nada (preencher depois)
```

**Substituir por:**

```
- **Virou:** wo00NN / spec de feature / nada (preencher depois)

> Análise é para quando a pergunta ainda é do dono. Se ele já decidiu o QUÊ, isto não é análise: é
> decisão registrada + ordem de trabalho. E **se a leitura derrubar a premissa que disparou tudo,
> PARE** — o achado técnico vai para as armadilhas da WO, não volta como pergunta.
```

## Edicao 9 — `meta/IDEAS.md` · dois registros que fecham a fase 3

**Ancora** (uma linha, primeiro item de «Feedback para o Kit»):

```
- **Número de checklist é DERIVADO do texto da WO, nunca estimado antes dela.** Terceira
```

**Inserir IMEDIATAMENTE ANTES:**

```
- **Desvio registrado: o `IDEAS.md` deste projeto NÃO separa «Ativas — Usuário» de «Ativas —
  Assistente».** O modelo v1.120.0 propõe as duas seções, com o argumento de que ajuda a lembrar de
  onde veio cada coisa. Aqui a origem viaja **dentro do item** («Ideia do usuário, nota
  `260717-1338`», «nasceu do diagnóstico»), e isso funciona melhor para o caso comum deste projeto,
  que é ideia de autoria mista — o usuário levanta o atrito, o assistente propõe a forma. Com duas
  seções, esse item teria de escolher um lado ou ser duplicado, e mudaria de seção conforme quem
  falou por último. **Mantido como está, de propósito, e registrado aqui para que o próximo merge
  não proponha isto como lacuna.**
- **Agrupar o `GLOSSARY.md` em seções.** O arquivo tem 15,8 KB e **nenhum `##`**: achar um termo é
  varrer o texto inteiro. O modelo v1.120.0 sugere quatro baldes (conceitos · arquiteturas e
  módulos · comandos e artefatos · identificadores) e eles cabem bem no nosso vocabulário. Não
  entrou no merge porque **reorganizar 40 e poucos termos é edição do nosso conteúdo, não adoção de
  modelo** — e edição desse tamanho merece uma passada própria, não um item no fim de uma WO de
  fechamento. **Volta quando** alguém não achar um termo que sabe que está lá, ou na próxima vez que
  o arquivo crescer.
```

> O primeiro e um **desvio registrado** (a valvula que o proprio kit prevê): decisao consciente de
> nao adotar, com o motivo, para que o proximo merge nao a leia como lacuna. O segundo e ideia com
> gatilho, pelo mesmo criterio das «Adiadas» — so que o lugar dela e aqui, junto do resto do que o
> merge produziu.

## Edicao 10 — `meta/STATUS.md` · o merge fecha

**Ancora** (o paragrafo da fase 3 inteiro, extraido do arquivo):

```
   **O merge do CEREBRO está fechado. Fase 3 (parcial, wo0060):** o `meta/workorders/_TEMPLATE.md`
   absorveu o que sete WOs seguidas ensinaram — campos «Âncoras lidas em» e «Próximo comando», a
   regra de extrair âncora por script e de a âncora cobrir o que o texto novo torna redundante, e
   os três campos de todo passo de conferência. **Escrito daqui, não copiado:** o pacote saiu do
   mount antes desta fase, então a redação é nossa e os nomes dos campos vieram do que ficou
   registrado na comparação de 25/08. **Falta:** os 11 modelos restantes e uma passada de diff
   sobre o `_TEMPLATE.md` de WO quando o pacote voltar.
```

**Substituir por:**

```
   **O merge do KCM v1.120.0 está FECHADO (wo0054 a wo0061).** Coberturas finais: **20 de 20
   arquivos do pacote comparados**; **18 de 18 ocorrências de linha revogada** tratadas (as 5 que
   restam no repo são relato legítimo, não instrução). Fase 3: o `_TEMPLATE.md` de WO absorveu o
   que sete WOs ensinaram (wo0060); os 11 modelos restantes foram comparados um a um na wo0061 e
   renderam quatro adoções — «Última conversa» no `STATUS`, gatilho por evento no `LOG-TEMPLATE`,
   as duas regras de manutenção no cabeçalho do `DECISIONS` e o critério de conclusão por fase no
   `ROADMAP` — mais uma frase no modelo de análise. **CONTEXT, CHANGELOG, IDEAS, GLOSSARY, HISTORY
   e SPEC não mudaram:** os nossos são mais ricos que os modelos, e a regra é que genérico não
   substitui vivo. Dois desvios ficam registrados no `IDEAS`: o `IDEAS` não separa ideias por autor,
   e o agrupamento do `GLOSSARY` ficou como ideia com gatilho. **Pendência:** uma passada de diff
   sobre o `meta/workorders/_TEMPLATE.md`, cuja redação foi escrita daqui enquanto o pacote estava
   fora do mount.
```

> **Ancora multilinha de proposito** — o texto novo reescreve o paragrafo todo (licao da wo0058).

---

## Fora de escopo

- **Reorganizar o `GLOSSARY.md`** — vira ideia com gatilho na Edição 9, não edição desta WO.
- **Separar o `IDEAS.md` por autor** — desvio registrado, também na Edição 9.
- **Reescrever as quatro fases do `ROADMAP`** para acrescentar critério de conclusão a cada uma: a
  Edição 7 põe a **regra** no cabeçalho; preencher os critérios é trabalho de conteúdo, com o dono,
  e cada critério precisa ser decidido, não inventado por quem aplica.
- **Arquivar o `DECISIONS.md`** — a Edição 6 escreve a regra no lugar certo; executá-la é outra WO,
  e continua no backlog do `STATUS`.
- **`CONTEXT`, `CHANGELOG`, `IDEAS`, `GLOSSARY`, `HISTORY`, `SPEC`** — comparados e mantidos.
- Nada de `.claude/`, nada de `flatdrop/`.

## Armadilhas desta WO

- **A Edição 2 insere no FIM do arquivo**, ancorando nas três últimas linhas. Se o `STATUS.md`
  tiver ganhado conteúdo no fim depois de 27/08 07:44, a âncora não casa — **PARE e reporte**.
- **A Edição 3 substitui as 14 primeiras linhas do `LOG-TEMPLATE.md`**, incluindo o `# título`.
  Confira depois que o arquivo continua começando por `# LOG-TEMPLATE — FlatDrop` e que o `---` e
  o `# Log — [AAAA-MM-DD]` que vêm depois não foram tocados.
- **A Edição 10 tem âncora multilinha** (o parágrafo da fase 3 inteiro), de propósito.
- Os textos novos usam acento normalmente — nenhum destes arquivos é ASCII-only (só o
  `workorders/_TEMPLATE.md` é, e esta WO não o toca).

---

## Depois de aplicar — conferência antes do commit

- [ ] `git diff` mostra exatamente seis arquivos: `meta/STATUS.md`, `meta/LOG-TEMPLATE.md`,
      `meta/DECISIONS.md`, `meta/ROADMAP.md`, `meta/analises/_TEMPLATE.md`, `meta/IDEAS.md`.
      *(Quem executa: você. Responde «está lá?».)*
- [ ] `grep -c "^## Última conversa" meta/STATUS.md` → **1**. *(«está lá?»)*
- [ ] `grep -c "DECISIONS-archive.md" meta/DECISIONS.md` → **1**. *(«está lá?»)*
- [ ] `grep -ci "sess" meta/LOG-TEMPLATE.md` → **0**. *(«está lá?» — eram **6 linhas** antes desta
      WO, medidas em 27/08: quatro no cabeçalho, uma no «Objetivo da sessão» e uma nos «Próximos
      passos». As Edições 3, 4 e 5b fecham as seis. Se der mais que zero, reporte a linha crua.)*
- [ ] **Este responde «presta?», não «está lá?»:** abra o `meta/LOG-TEMPLATE.md` e confirme que o
      molde continua **em branco** — nenhum campo entre colchetes foi preenchido por engano com
      conteúdo real. Molde preenchido deixa de ser molde, e o erro só aparece no dia em que alguém
      copiar o arquivo.
- [ ] `python -m pytest -q` → **122**, sem mudança (WO só de doc).
- [ ] **Invariante DEC-020:** nada em `flatdrop/`.

## Relatório de aplicação *(quem aplica preenche ao terminar)*

O que foi feito · o que fugiu do texto literal · os números crus das conferências · o commit ·
**o push, com o resultado real**, escrito DEPOIS de o push estar resolvido. Grave o MESMO relatório
em `../AAMMDD-HHMM-code-flatdrop.txt`.

## Commit — blocos separados, mensagem SEM acento

```
git add meta\STATUS.md meta\LOG-TEMPLATE.md meta\DECISIONS.md meta\ROADMAP.md meta\analises\_TEMPLATE.md meta\IDEAS.md meta\workorders\260827-wo0061-merge-kcm-fase3-modelos.md
```

```
git commit -m "chore(kit): merge do KCM v1.120.0 fase 3 - fecha o merge" -m "Os 11 modelos restantes comparados um a um. Seis nao mudam (o vivo e mais rico que o generico). Cinco adocoes: STATUS ganha a secao Ultima conversa; LOG-TEMPLATE passa a disparar por evento e fala em Conversa N; DECISIONS ganha no cabecalho as regras de marcar SUPERADA e arquivar acima de 700 linhas, num arquivo que ja passou de 1400; ROADMAP passa a exigir criterio de conclusao por fase; o modelo de analise ganha a regra de parar quando a leitura derruba a premissa. Dois desvios registrados: IDEAS nao separa por autor, e agrupar o GLOSSARY fica como ideia com gatilho. Merge fechado: 20 de 20 arquivos comparados."
```

```
git push
```
