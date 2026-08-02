# WO 0049 — registro de fecho da sessão de 2026-08-02 (0.15.0)

> **Tipo:** REGISTRO (meta + um bump de versão). Nenhuma linha de lógica muda.
> **Config sugerida:** modelo intermediário, `/effort` médio. São muitas edições, todas ancoradas.
> **Pré-requisito:** wo0045–wo0048 aplicadas e commitadas (commit `9d8e62f`), **92 testes verdes**,
> árvore limpa.
> **Base:** os quatro relatórios de aplicação de 2026-08-02 (12:44, 13:14, 16:20, 16:26) e a
> sessão de chat do mesmo dia.
> **Âncora semântica:** se um trecho-âncora não bater EXATAMENTE, **PARE e reporte**.
> **Idempotência:** se `meta/CHANGELOG.md` já tiver a linha `## [0.15.0]`, **PULE a WO inteira**.

> **Canal dos meta neste ciclo = CODE.** É esta WO que registra tudo; o chat não vai entregar
> documento nenhum depois dela. Faça os appends abaixo e mais nada.

---

## 1. Por que

Quatro WOs de produto entraram no mesmo dia (o bug aberto na 0.13.0 fechou, o `_MANIFEST` passou a
carregar o estado do git, o editor ganhou dois avisos) e **nenhuma delas registrou nada nos
`meta/`** — todas rodaram com «canal = CHAT», porque o plano era o chat fechar a sessão. A conversa
ficou pesada antes disso. Sem esta WO, o repositório tem o código novo e uma documentação que ainda
descreve o bug como aberto e a versão como 0.14.0 — e o repositório é o que a próxima conversa vai
ler.

## 2. Contexto factual

Tudo abaixo é **medido**, vindo dos relatórios e do manifesto gerado às 16:50:

- Commits, em ordem: `9c296ce` (wo0045) → `373a904` (wo0046) → `8f8dff8` (wo0047) → `9d8e62f`
  (wo0048). Todos com push feito; `git status` no manifesto das 16:50 diz **branch main · limpo**.
- Suíte: 79 → **82** → **86** → **88** → **92** verdes. Nenhum teste antigo precisou de ajuste em
  nenhuma das quatro — a armadilha prevista na wo0046 (testes escritos contra a base git-pura) não
  se confirmou, porque nenhum deles tinha curadoria manual fora do bloco.
- Um desvio, na wo0048: as assinaturas reais são `make_plan(root, cfg)` e
  `execute_plan(plan, dest, cfg)`, e o manifesto pode sair com sufixo do nome da pasta — o teste
  foi corrigido para a forma real, copiada dos testes de manifesto já existentes.
- **Pendente de validação visual pelo autor** (o ambiente do Code não tem display Windows): a
  coluna `travada (manual)`, o popup de contrabarra e o `askyesno` de regra depois do bloco. A
  lógica por baixo dos três foi exercitada e passou.
- O `UnicodeEncodeError` do `↳` sob cp1252 reapareceu no smoke da wo0048 — **terceira ocorrência**.

---

## Edição 1 — `flatdrop/__init__.py` · versão 0.15.0

**Âncora:**

```
__version__ = "0.14.0"
```

**Substituir por:**

```
__version__ = "0.15.0"
```

> MINOR, não PATCH: além da correção do bug, entraram três comportamentos novos (estado do git no
> manifesto, rótulo `travada (manual)`, aviso de contrabarra).

## Edição 2 — `meta/CHANGELOG.md` · abrir a versão 0.15.0

**Âncora 2a:**

```
_Itens de produto em aberto: multi-raiz na GUI (decisão A/B pendente), formato de nome
"caminho escrito" (raiz→pastas→stem), UI-2/UI-3, saída da CLI ASCII-safe — todos com gatilho
de retorno em `IDEAS.md` › Adiadas. Frente aberta: a correção do editor × curadoria manual._

### Documentação e ambiente de trabalho — 2026-08-01

> **Sem versão de propósito.** Nada do produto mudou: `flatdrop/` está intacto e a suíte não foi
> rodada nesta sessão (último número verificado: 79 verdes em 2026-07-29, relatados pelo Code na
> wo0043). Mesmo critério do merge de 2026-07-28, que também não cortou versão.
```

**Substituir por:**

```
_Itens de produto em aberto: multi-raiz na GUI (decisão A/B pendente), formato de nome
"caminho escrito" (raiz→pastas→stem), UI-2/UI-3, saída da CLI ASCII-safe — todos com gatilho
de retorno em `IDEAS.md` › Adiadas. Decisão em aberto: `pasta/*` + `!mantido` no gerador do
editor (`meta/analises/260728-ANALISE-gerador-flatdropignore.md`)._

## [0.15.0] — 2026-08-02

> Duas sessões num só corte de versão: a documentação e o ambiente de trabalho em 01/08, o código
> em 02/08. **92 testes verdes** (79 → 82 → 86 → 88 → 92, um degrau por WO). Fecha o único bug
> aberto do projeto.
```

**Âncora 2b:**

```
#### Adicionado
- **O Claude Code passa a gravar o relatório de trabalho em arquivo (DEC-028).**
```

**Substituir por:**

```
### Adicionado
- **O `_MANIFEST` passa a carregar o estado do repositório git (wo0048).** Duas linhas logo abaixo
  de «Gerado em»: o último commit (`%h %ad %s`, data curta) e um **resumo** do status (branch,
  contagem de modificados e não rastreados, commits à frente de `origin`). Rotuladas como **foto
  da geração**, porque é o que são. Motivo: o mount é uma cópia achatada e não leva o `.git`, então
  quem lê o mount não tinha como saber em que commit o projeto está — perguntava, ou respondia de
  memória. Resumo e nunca listagem: `git status` verboso é ruído e vazaria nome de arquivo pessoal
  não rastreado para dentro de uma conversa. Falha de git é silenciosa: nada impede o achatamento.
- **Rótulo `travada (manual)` na coluna «Arquivo novo» (wo0047).** A trava que vem de uma linha
  escrita à mão no `.flatdropignore` deixa de parecer trava do próprio autor. Ganhou importância
  com a wo0046: agora que destravar funciona de verdade sobre linha manual, é preciso saber que
  aquela trava não é sua antes de mexer. A sonda é de **arquivo inexistente**, não de diretório —
  `pasta/*` de propósito não casa a pasta como diretório (DEC-025/DEC-027).
- **Aviso de padrão com contrabarra (wo0047).** Ao abrir o editor, o FlatDrop denuncia toda linha
  de regra escrita com `\` e aponta arquivo e linha. Em sintaxe `.gitignore` a contrabarra é
  **escape**, não separador: o padrão não casa nada e o arquivo sobe achando que foi ignorado —
  falha silenciosa que custou ao autor arrastar arquivos à mão. Avisa e aponta; **não normaliza**,
  porque trocar `\` por `/` calado mudaria a semântica de um arquivo que o git também lê.
- **O Claude Code passa a gravar o relatório de trabalho em arquivo (DEC-028).**
```

**Âncora 2c:**

```
#### Mudado
- **Merge do template-update do KCM v1.95.0 (DEC-028).**
```

**Substituir por:**

```
### Mudado
- **O bloco gerenciado do `.flatdropignore` virou um *diff* (wo0046, FIX-012).** A base de
  comparação deixou de ser o git puro e passou a ser *gitignore + curadoria manual, sem o próprio
  bloco*. Emite-se só o que diverge dessa baseline. **Consequência visível: num arquivo curado à
  mão, o bloco fica quase vazio — está certo, não "sumiu".**
- **O bloco é sempre reescrito no FIM do arquivo (wo0046).** Posição fixa, não caso-a-caso: vale a
  última regra que casa, então bloco no fim é o que dá ao editor a palavra final sobre o que ele
  mostra na tela. **Move-se o próprio bloco, nunca o texto do autor** — o que estava depois dele
  sobe, na ordem em que estava, e a GUI pergunta antes, porque isso inverte a precedência daquelas
  regras.
- **Merge do template-update do KCM v1.95.0 (DEC-028).**
```

**Âncora 2d:**

```
#### Corrigido
- **Registro pendente da leva 0.12.0–0.14.0 (wo0044).**
```

**Substituir por:**

```
### Corrigido
- **O editor não convivia com regra escrita fora do bloco (FIX-012, wo0045 + wo0046).** Três
  sintomas, uma causa: salvar duplicava dentro do bloco o que já estava fora; destravar uma pasta
  fechada à mão era desfeito em silêncio; e marcar um arquivo trazia as duplicatas junto. O
  gerador era cego para a curadoria manual e, sendo cego, não sabia que havia algo a corrigir.
- **Os marcadores do bloco eram procurados por substring (wo0045).** Um comentário que
  *mencionasse* o marcador — documentando a própria convenção — fazia o gerador cortar na menção:
  o bloco novo entrava no meio da frase, o antigo sobrava no fim, e a linha truncada perdia o `#`
  e virava padrão ativo. Agora o marcador é uma **linha inteira**, e arquivo com dois blocos
  **recusa salvar** em vez de adivinhar. Medido: 35 linhas viravam 42, com dois blocos.
- **O `.flatdropignore` crescia uma linha em branco a cada salvamento** (wo0045) — o `lstrip` do
  trecho final só limpava um lado.
- **Registro pendente da leva 0.12.0–0.14.0 (wo0044).**
```

## Edição 3 — `meta/STATUS.md` · o resolvido sai

**Âncora 3a** — **remova o bloco de citação inteiro**, da linha:

```
> **Mudanças nesta revisão (2026-08-01) — meta apenas, nenhuma linha de produto tocada:**
```

até a linha (inclusive):

```
> - **Suíte não rodada nesta sessão.** O número abaixo é o relatado pelo Claude Code em 29/07.
```

**e ponha no lugar:**

```
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
```

**Âncora 3b** — do cabeçalho de estado:

```
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
```

**Substituir por:**

```
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
```

**Âncora 3c** — **remova as duas seções inteiras**, da linha:

```
## 🔴 Bug aberto — o editor não convive com regras escritas FORA do bloco gerenciado
```

até a linha **anterior** a:

```
## ✅ O que funciona (além do MVP)
```

**e ponha no lugar** (antes do `## ✅`):

```
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
```

**Âncora 3d** — na seção «Qualidade / testes»:

```
- **79 testes** relatados verdes em 2026-07-29 (Code, wo0043). Rodar da raiz: `pytest -q` (o
  `conftest.py` resolve o import — FIX-005) ou `python -m pytest -q`.
- A distribuição por arquivo não é reconferida desde 21/07 (68 testes); os 11 novos vieram das
  wo0038 e wo0041–0043, em `test_core.py`.
- A GUI **não** é coberta pela suíte (tkinter fora do CI) → smoke manual no Windows.
- **Lacuna conhecida:** nenhum dos 8 testes do editor exercita linha manual fora do bloco
  gerenciado. É o que deixou o bug passar — a WO da correção precisa fechar essa lacuna.
```

**Substituir por:**

```
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
```

**Âncora 3e** — o item 1 do backlog:

```
1. **A correção do bug do bloco gerenciado**, começando pelas duas perguntas acima.
```

**Substituir por:**

```
1. **Validar na tela os três comportamentos novos** (seção «Pendente de validação visual»).
```

## Edição 4 — `meta/DECISIONS.md` · FIX-012 e DEC-029

**Inserir ao FIM do arquivo:**

```

## FIX-012 — o editor não convivia com regra escrita fora do bloco gerenciado
**Data:** 2026-08-02 · **Aberto em:** 0.13.0 · **Corrigido em:** 0.15.0 (wo0045 + wo0046)

**Sintomas.** Três, num `.flatdropignore` com curadoria manual fora do bloco: (1) salvar sem mexer
em nada copiava para dentro do bloco linhas que já existiam fora; (2) destravar uma pasta fechada
por linha manual não tinha efeito — o gerador só omitia a linha do bloco, a de fora continuava, e
ao reabrir a trava estava lá; (3) marcar um arquivo dentro dessa pasta trazia as duplicatas junto.

**Causa raiz.** A base de comparação era o **git puro**, herança de quando o bloco era o arquivo
inteiro. O gerador comparava o estado desejado com o que o `.gitignore` faria e era cego para a
curadoria manual do próprio `.flatdropignore`. **Sendo cego, não sabia que havia algo a corrigir:**
não duplicava de propósito (não via a linha de fora) e não emitia o `!` de destravamento (não via
o que precisava vencer).

**Correção.** A baseline passou a ser *gitignore + flatdropignore **sem** o bloco*
(`_collect_ignore_lines(..., skip_managed_root=True)`), e a emissão passou a escrever **apenas o
que diverge** dela — a tabela de quatro casos virou uma regra só. O bloco é um *diff*, nunca uma
cópia. Junto veio a posição fixa: o bloco é sempre reescrito no fim do arquivo.

**Defeito irmão, encontrado ao medir (wo0045).** Os marcadores eram procurados por **substring**:
um comentário que citasse o marcador fazia o corte acontecer na citação — bloco injetado no meio da
frase, bloco antigo sobrando no fim, linha truncada virando padrão ativo. Medido com o
`.flatdropignore` deste repo, escrito no dia anterior pelo próprio assistente: 35 linhas viravam
42. Corrigido junto: marcador é linha inteira, e arquivo ambíguo **recusa salvar**.

**Por que a suíte não pegou.** Nenhum dos 8 testes do editor tinha linha manual fora do bloco.
Fechado: os testes novos cobrem os três sintomas, o marcador citado e a estabilidade textual.

**Consequência a não estranhar.** Num arquivo curado à mão, o bloco gerenciado fica quase vazio.
É o comportamento certo — não há nada a corrigir —, mas parece que sumiu.

## DEC-029 — a anatomia normativa do `.flatdropignore`
**Data:** 2026-08-02 · **Status:** aceita · **Spec:**
`meta/specs/260802-spec-anatomia-flatdropignore.md`

**Contexto.** O FIX-012 tratou o problema como bug de algoritmo. Era metade: **o arquivo nunca teve
uma anatomia declarada**, então cada lado inventou a sua — o gerador supôs que o bloco era o
arquivo inteiro, o autor escreveu regra fora do bloco, e o assistente chegou a citar os marcadores
dentro de um comentário *para documentar a convenção*. A convenção existia na cabeça do autor (ele
já a usava no KCM); não existia escrita em lugar nenhum, e o que não está escrito não pode ser
garantido.

**Decisão — cinco regras.** (1) Comentário fica FORA do bloco. (2) Regra fica DENTRO. (3) Existe
UM bloco, e só um. (4) O bloco é sempre o ÚLTIMO conteúdo do arquivo. (5) Os marcadores não se
citam em comentário.

**O corolário é o objetivo, não um detalhe:** respeitadas as cinco, **editor visual e edição
manual podem ser usados livremente no mesmo arquivo**. A convenção não é restrição a mais — é o
que revoga o contorno «ou um, ou outro» que vigorava desde a 0.13.0.

**Duas obrigações que ela impõe à ferramenta**, e que valem para qualquer gerador do gênero:
**recusar, não adivinhar** (ambiguidade para o salvamento, porque reescrever é a única operação
irreversível) e **normalizar só o que é seu** (mover o próprio bloco é legítimo; mover o texto da
pessoa, não — e quando a normalização mudar o resultado efetivo de alguma regra dela, avisar).

**Alternativas descartadas.** *Deixar a convenção implícita e só corrigir o algoritmo* — foi o que
se tentou em 28/07, e o resultado foi o assistente violando a convenção ao documentá-la.
*Normalizar tudo automaticamente* (mover texto do autor, trocar `\` por `/`) — descartada: muda
semântica de um arquivo que outras ferramentas também leem.

**Consequência.** As cinco regras foram enviadas ao KCM como acréscimo ao princípio «artefato
gerado que convive com edição humana», que a v1.89.0 já tinha levado deste projeto. Princípio sem
forma testável não impede o erro — este caso é a prova.
```

## Edição 5 — `meta/GLOSSARY.md` · três termos

**Inserir ao FIM do arquivo:**

```

**Anatomia normativa.** As cinco regras que tornam o `.flatdropignore` editável pelas duas mãos
(DEC-029): comentário fora do bloco · regra dentro · um bloco só · bloco sempre no fim · marcador
não se cita em comentário. Não é estilo: é o que revoga o contorno «ou o editor, ou a mão». Quem
as respeita pode alternar à vontade entre a GUI e o editor de texto.

**Baseline (do gerador).** O que o `.flatdropignore` faria **sem o próprio bloco gerenciado** —
`gitignore` + a curadoria manual do autor. É contra ela que o bloco é um *diff* desde a 0.15.0
(FIX-012). Antes a base era o **git puro**, e era essa cegueira que fazia o bloco duplicar o que já
estava fora e falhar em destravar o que uma linha manual tinha fechado.

**Foto da geração.** Rótulo dos dados de git que o `_MANIFEST` passou a carregar na 0.15.0
(wo0048): último commit e resumo do `git status` **no instante em que o mount foi gerado** — não o
estado atual. O rótulo é parte do dado: ao lado da hora de geração, que já estava no manifesto, ele
diz o quanto envelheceu.
```

## Edição 6 — `meta/ROADMAP.md` · o bug fechou

**Âncora** *(a linha inteira, é longa — copie-a do arquivo)*:

```
- [ ] 🔴 **Bug do bloco gerenciado × curadoria manual** (aberto na 0.13.0).
```

*(a âncora é o início da linha; substitua a **linha inteira**)*

**Substituir por:**

```
- [x] **Bug do bloco gerenciado × curadoria manual** (aberto na 0.13.0, **fechado na 0.15.0** —
      FIX-012, wo0045 + wo0046). A base de comparação virou a curadoria manual em vez do git puro,
      o bloco passou a ser um diff e vai sempre para o fim do arquivo. A convenção que faltava
      virou a DEC-029. Com isso, editor e edição manual convivem no mesmo `.flatdropignore`.
```

## Edição 7 — `meta/IDEAS.md` · o que saiu e o gatilho que disparou

**Âncora 7a** *(dentro da seção «Adiadas», a linha que fecha o item da CLI)*:

```
  (`UnicodeEncodeError` no `↳` sob cp1252, na wo0043 e antes). O custo é baixo; o que falta é a vez.
```

**Substituir por:**

```
  (`UnicodeEncodeError` no `↳` sob cp1252, na wo0043 e antes). O custo é baixo; o que falta é a vez.
  **GATILHO DISPARADO em 2026-08-02:** terceira ocorrência, no smoke da wo0048 — o traceback saiu
  DEPOIS de o manifesto já estar no disco, então não corrompe resultado, mas assusta. Esta ideia
  volta para «Ativas» na próxima curadoria do chat.
```

**Âncora 7b** *(o início da seção «Concluídas»)*:

```
## Concluídas
```

**Inserir IMEDIATAMENTE APÓS** *(deixando uma linha em branco antes e depois)*:

```
- **O editor deve conviver com regra escrita à mão.** **ENTREGUE na 0.15.0** (FIX-012, wo0045 +
  wo0046): o bloco virou um diff contra a curadoria manual e vai sempre para o fim. Junto veio a
  **anatomia normativa** (DEC-029), que é o que de fato revoga o «ou um, ou outro».
- **Contrabarra em padrão deveria ser detectada.** **ENTREGUE na 0.15.0** (wo0047): o editor avisa
  na abertura e aponta arquivo e linha. Confirmado por medição que o gerador nunca emitiu `\` — as
  linhas vinham sempre de edição manual, e por isso a ferramenta **avisa em vez de normalizar**.
- **FlatDrop grava o estado do repo no `_MANIFEST`.** **ENTREGUE na 0.15.0** (wo0048), com os três
  refinos do autor: `%h %ad %s --date=short`, status **resumido** (nunca listagem, para não virar
  ruído nem vazar nome de arquivo não rastreado) e o rótulo «foto da geração».
```

## Edição 8 — `logs/2026-08-02.md` · criar

**Criar arquivo novo.** Se já existir, **PARE e reporte** em vez de sobrescrever.

```
# Log — 2026-08-02

## Objetivo da sessão

Fechar o registro pendente da leva 0.12–0.14 (wo0044), abrir a frente do bug do bloco gerenciado e
resolver as ideias e bugs que o autor tinha deixado nas notas do mount. Terminou entregando a
0.15.0 inteira.

## O que foi feito

**wo0044 — registro pendente.** Duas docstrings de `core.py` que citavam `TREE_NAME_CAP` (morto
desde a wo0043), a constante removida do `config.py`, o modelo das WOs criado, e os logs de 28 e
29/07 reconstruídos a partir do `git log`.

**A frente do bug foi aberta com medição, não com opinião.** O código da 0.14.0 foi rodado em
sandbox: os três sintomas reproduzidos, um protótipo dos passos 1 e 2 escrito, e o resultado
tabelado antes de devolver qualquer pergunta ao autor. Foi essa medição que converteu «estimativa»
em número — e que descobriu dois defeitos que ninguém procurava.

**Defeito 1, o mais caro: os marcadores eram procurados por substring.** O `.flatdropignore`
entregue no dia anterior pelo próprio assistente **citava os marcadores num comentário**, para
documentar a convenção. Rodando o gerador de produção contra ele: 35 linhas viraram 42, com dois
blocos, e uma frase truncada virou padrão ativo. O autor já havia disparado o mesmo defeito noutro
projeto, à mão, sem diagnóstico.

**Defeito 2: o `.flatdropignore` crescia uma linha em branco por salvamento** — `lstrip` num lado
só, no trecho final da escrita.

**A convenção virou o eixo do trabalho.** O autor apontou que o problema não era falta de
algoritmo: a convenção que ele já usava no KCM (comentário fora, regra dentro, um bloco só, sempre
no fim, nada depois) resolvia tudo — e o exemplo de bloco dentro do comentário nunca deveria ter
existido. Isso virou a spec da **anatomia normativa** e, dela, quatro WOs.

**wo0045–wo0048, aplicadas no mesmo dia**, cada uma com seu commit e push: marcadores por linha
exata e recusa de arquivo ambíguo · o bloco virando um diff e indo para o fim · `travada (manual)`
e aviso de contrabarra · estado do git no manifesto. 79 → 92 testes verdes, nenhum teste antigo
precisou de ajuste.

## Decisões

- **FIX-012** — a base de comparação do gerador deixa de ser o git puro.
- **DEC-029** — a anatomia normativa do `.flatdropignore`, com as duas obrigações que ela impõe:
  *recusar, não adivinhar* e *normalizar só o que é seu*.
- **Passo 3 fixo, não reativo:** o bloco vai para o fim sempre, e o que se move é o **próprio
  bloco** — a terceira opção, que a análise de 28/07 não tinha e que a regra de higiene adotada na
  DEC-028 tornou visível.
- **Contrabarra: avisar, não normalizar.** Medido que o gerador nunca emitiu `\`; trocar
  caladamente mudaria a semântica de um arquivo que o git também lê.
- **Versão cortada como MINOR (0.15.0)** — houve correção, mas também três comportamentos novos.

## Bugs

- **FIX-012 fechado.** Aberto na 0.13.0, corrigido na 0.15.0.
- **Marcador por substring** — corrigido na wo0045.
- **Linha em branco acumulando** — corrigido na wo0045.
- **`UnicodeEncodeError` do `↳` sob cp1252: terceira ocorrência**, no smoke da wo0048. Sai depois
  de o manifesto já estar no disco. É o gatilho de retorno da ideia adiada da CLI ASCII-safe.

## Aprendizados / armadilhas

- **Documentar uma convenção violando-a.** Foi o erro do dia, e do assistente: escrever um exemplo
  de bloco dentro do comentário do próprio arquivo que a ferramenta reescreve. Era previsível. A
  lição não é «tomar mais cuidado» — é que **convenção não escrita não pode ser garantida**, e a
  correção certa foi declará-la e fazer a ferramenta recusar o que a viola.
- **Medir antes de perguntar.** Rodar o código em sandbox antes de devolver perguntas ao autor
  transformou duas incertezas em tabela e revelou dois defeitos que nenhuma leitura de código teria
  encontrado. Custou minutos.
- **Suíte verde não é cobertura.** Os 8 testes do editor passavam há semanas com o bug presente,
  porque nenhum deles tinha linha manual fora do bloco. O que não está no teste não está protegido.
- **A ferramenta que informa o próprio estado apaga uma regra do assistente.** Com o `git log` e o
  `git status` no manifesto, a ressalva «commit não legível pelo mount» virou dado. Vale procurar
  outros lugares onde uma linha de código apaga um parágrafo de protocolo.
- **Gatilho de retorno funciona.** A ideia da CLI ASCII-safe foi adiada de manhã com o gatilho
  «volta na terceira ocorrência num smoke» e disparou à tarde, sozinha.

## Onde parei

0.15.0 fechada, 92 testes verdes, commit `9d8e62f`, branch `main` limpa e com push feito. Falta a
**validação visual no Windows** de três comportamentos que o Code não consegue ver (a coluna
`travada (manual)`, o popup de contrabarra e o `askyesno` de regra depois do bloco) — a lógica dos
três foi exercitada e passou.

## Próximos passos

1. Validar na tela os três comportamentos (cinco minutos, `meta/STATUS.md` tem o roteiro).
2. Responder a pergunta que trava a outra análise: *arquivo novo em pasta curada entra ou fica
   fora?* (`meta/analises/260728-ANALISE-gerador-flatdropignore.md`).
3. Arquivar o `meta/DECISIONS.md` — passou de 900 linhas.
```

---

## Fora de escopo

- **Não mexa em código de produto.** Só o `__version__` muda em `flatdrop/`.
- **Não arquive o `meta/DECISIONS.md`** — é trabalho próprio, com decisão de corte a tomar.
- **Não faça curadoria do `meta/IDEAS.md`** além dos dois appends da edição 7: mover a ideia da CLI
  de «Adiadas» para «Ativas» é curadoria do chat, e está anotada para a próxima sessão.

## Armadilhas desta WO

- **A edição 3 tem duas remoções por faixa** (3a e 3c). Confira que o que ficou antes e depois da
  faixa continua fazendo sentido — e **não remova o `## ✅ O que funciona (além do MVP)`**, que é o
  limite de baixo da faixa 3c.
- **As âncoras 2b/2c/2d incluem o nível do cabeçalho** (`####` → `###`): a mudança de nível é
  proposital, porque a seção deixou de estar aninhada em `[Não lançado]` e virou o corpo da 0.15.0.
- **A edição 6 substitui uma linha muito longa.** Copie-a do arquivo em vez de digitá-la.
- **A edição 8 cria o log do dia** — `logs/2026-08-01.md` já existe e é de outra sessão; não os
  funda (DEC-026: um arquivo por DIA).
- Os `.md` estão em **LF**.

---

## Depois de aplicar — conferência antes do commit

- [ ] `git diff` mostra: `flatdrop/__init__.py`, `meta/CHANGELOG.md`, `meta/STATUS.md`,
      `meta/DECISIONS.md`, `meta/GLOSSARY.md`, `meta/ROADMAP.md`, `meta/IDEAS.md` e
      `logs/2026-08-02.md` (novo) — nada além.
- [ ] `python -m pytest -q`: **92 verdes**. Nenhuma edição toca lógica; se cair, **PARE**.
- [ ] `grep -n "0.14.0" flatdrop/__init__.py` não devolve nada.
- [ ] O `meta/STATUS.md` não contém mais a string `Bug aberto` nem `Registro pendente — wo0044`.
- [ ] O `meta/CHANGELOG.md` tem `## [0.15.0] — 2026-08-02` e o `[Não lançado]` ficou só com o
      parágrafo dos itens em aberto.

## Relatório de aplicação

O que foi feito · desvios · arquivos tocados · resultado da suíte · o commit. Grave o MESMO
relatório em `../AAMMDD-HHMM-code-flatdrop.txt`. **Diga explicitamente** se alguma das duas faixas
da edição 3 pegou mais ou menos linhas do que o previsto — é a parte mais frágil desta WO.

## Commit — blocos separados, mensagem SEM acento

```
git add flatdrop/__init__.py meta/CHANGELOG.md meta/STATUS.md meta/DECISIONS.md meta/GLOSSARY.md meta/ROADMAP.md meta/IDEAS.md logs/2026-08-02.md
```

```
git commit -m "docs(meta): fechar a sessao de 02-08 e cortar a 0.15.0 (wo0049)" -m "Versao 0.15.0: fecha o FIX-012 (o bloco gerenciado virou um diff contra a curadoria manual e vai sempre para o fim do arquivo), registra a DEC-029 (anatomia normativa do flatdropignore, que revoga o contorno de usar editor OU edicao manual) e os tres comportamentos novos: estado do git no manifesto, rotulo travada (manual) e aviso de contrabarra. STATUS perde a secao do bug e a do registro pendente, e ganha o roteiro da validacao visual que falta no Windows. 92 testes verdes."
```

```
git push
```
