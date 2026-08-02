# SPEC — anatomia normativa do `.flatdropignore`

> **Status:** aprovada pelo autor em 2026-08-02 · **Origem:** convenção que o autor já adotou no
> KCM · **Análise:** `meta/analises/260728-ANALISE-bloco-gerenciado-vs-manual.md`
> **Vira:** wo0045 (passo 0), wo0046 (passos 1–3), wo0047 (passo 4 + contrabarra).

## Problema

O editor visual e a curadoria manual não convivem no mesmo arquivo. O diagnóstico de 28/07 tratou
isso como bug de algoritmo — o gerador compara com o git puro e é cego para o que está fora do
bloco. É verdade, mas é metade: **o arquivo nunca teve uma anatomia declarada**, então cada lado
inventou a sua. O gerador supôs que o bloco era o arquivo inteiro; o autor escreveu regra fora do
bloco; e o cabeçalho entregue em 01/08 chegou a **citar os marcadores dentro de um comentário**, o
que fez o gerador injetar o bloco no meio da linha e deixar dois blocos no arquivo — defeito real,
disparado em outro projeto do autor antes de ser diagnosticado aqui.

A causa comum é a mesma: **nada define a forma do arquivo, então nada pode garanti-la.**

## A convenção (o contrato)

Cinco regras. Não são preferência de estilo — são o que torna a convivência possível, e cada uma
existe porque a sua violação já quebrou alguma coisa.

1. **Comentário fica FORA do bloco.** Dentro, o editor reescreve tudo a cada salvamento e o
   comentário some.
2. **Regra fica DENTRO do bloco.** É o território da ferramenta, e o único lugar que ela reescreve.
3. **Existe UM bloco, e só um.** Dois blocos são ambiguidade: nem a pessoa nem a ferramenta sabem
   qual manda.
4. **O bloco é sempre o ÚLTIMO conteúdo do arquivo.** Vale a última regra que casa; qualquer coisa
   depois dele vence em silêncio. Bloco no fim = o editor tem a palavra final sobre o que ele
   mostra na tela, e o que está fora é a base sobre a qual ele decide.
5. **Os marcadores não se citam em comentário.** Exemplo de bloco dentro de comentário é
   indistinguível de um segundo bloco. A regra 3 já implica isto; a ferramenta precisa dizê-lo em
   voz alta, porque é o erro mais fácil de cometer justamente ao documentar a convenção.

**Corolário — e é o objetivo desta feature:** respeitadas as cinco, **editor e edição manual
podem ser usados livremente no mesmo arquivo**, alternando à vontade. O contorno atual («ou um, ou
outro») deixa de existir.

## O que a ferramenta passa a garantir

- **Reconhecer** a anatomia: marcador é uma **linha** cujo conteúdo, sem espaços, é o marcador —
  nunca uma substring no meio de um texto.
- **Recusar** o que é ambíguo: dois ou mais marcadores de abertura (ou de fechamento) fazem o
  salvamento parar com mensagem clara. Recusar é obrigatório; adivinhar destrói conteúdo.
- **Normalizar** o que é seguro normalizar: o bloco é sempre reescrito no fim do arquivo. Mover o
  **próprio bloco** é a ferramenta mexendo no que é dela; mover o texto da pessoa, não.
- **Enxergar** o que está fora do bloco e emitir **apenas o que diverge** disso — o bloco é um
  *diff* contra tudo o que já existe, nunca uma cópia.
- **Avisar** sobre o que ela não pode consertar sozinha: regra escrita depois do bloco cuja
  precedência muda quando o bloco vai para o fim; e padrão escrito com contrabarra, que não casa
  nada em sintaxe `.gitignore` e falha em silêncio.

## Critérios de aceite (verificáveis)

| # | Critério | Onde se verifica |
|---|---|---|
| 1 | Arquivo com o marcador citado em comentário: o bloco é encontrado pela linha-marcador real, o comentário fica intacto e o arquivo continua com **um** bloco | `pytest` |
| 2 | Dois marcadores de abertura: salvar **falha** com erro nomeado, sem escrever nada no disco | `pytest` |
| 3 | Arquivo com regra manual fora do bloco, salvar sem mexer em nada → bloco sai `# (sem alteracoes)` | `pytest` |
| 4 | Destravar pasta fechada por regra manual → bloco emite `!pasta/*` | `pytest` |
| 5 | Marcar arquivo dentro de pasta fechada por regra manual → bloco emite só `!pasta/arquivo` | `pytest` |
| 6 | Salvar duas vezes seguidas produz **texto idêntico** (não só regras equivalentes) | `pytest` |
| 7 | Conteúdo depois do bloco: o bloco vai para o fim; se a precedência de alguma regra mudar com isso, a GUI avisa antes de salvar | `pytest` (core) + smoke manual (aviso) |
| 8 | Pasta fechada por regra manual aparece como `travada (manual)`, distinta de `travada (git)` | smoke manual no Windows |
| 9 | Padrão com contrabarra em linha manual gera aviso identificando a linha | `pytest` |
| 10 | O `.flatdropignore` deste repo sobrevive a um salvamento: cabeçalho intacto, um bloco, `!meta/workorders/_TEMPLATE.md` preservado | smoke manual |

## Decisões de design

- **A base de comparação passa a ser `gitignore + flatdropignore SEM o bloco`**, não o git puro.
  Medido em protótipo (2026-08-02): corrige os três sintomas e mantém o round-trip.
- **Bloco sempre no fim, como regra fixa** — não como reação a ter encontrado algo depois dele.
  Regra fixa é previsível; reação caso-a-caso é o que produziu o comportamento atual.
- **Recusar, não adivinhar.** Em ambiguidade (regra 3), o salvamento para. É a única operação
  irreversível do editor.
- **Avisar sem bloquear** nos casos em que a pessoa pode estar certa: precedência alterada pela
  mudança de posição, e contrabarra em padrão.

## Fora de escopo

- **Corrigir a contrabarra sozinho.** A ferramenta avisa e aponta a linha; quem edita é a pessoa.
  Normalizar `\` para `/` calado mudaria a semântica de um arquivo que também é lido pelo git.
- **Migrar arquivos existentes** que violem a convenção. Nada é reescrito sem um salvamento
  explícito na GUI.
- **Mexer no `pasta/` × `pasta/*`** (DEC-025) e na pergunta «arquivo novo em pasta curada entra?»
  (`meta/analises/260728-ANALISE-gerador-flatdropignore.md`). Decisões separadas, de propósito.

## Invariantes que esta feature NÃO pode quebrar

- **DEC-020** — `flatdrop/cli.py`, `gui._build_cli_args`, `gui._generate_bat` e `gui._sources`
  não são tocados. Esta feature vive em `core.build_flatdropignore`, na leitura de ignores e no
  modal do editor.
- **DEC-016** (round-trip) — é o contrato que esta feature mais estica: o bloco passa a depender
  do que está fora dele. O critério 6 é a rede.
- **DEC-027** — a trava continua sendo a única informação não-derivada do editor; nada aqui
  reintroduz colapso automático de pasta.
- **FIX-011 / DEC-025** — a forma `pasta/*` continua sendo a emitida.

## Riscos

- **A correção reduz o bloco.** Num arquivo curado à mão, o bloco fica quase vazio — está certo,
  mas parece que sumiu. Tem de estar no CHANGELOG.
- **Deriva de espaço em branco** — medida no protótipo: uma linha em branco por salvamento. É o
  motivo do critério 6 comparar texto, não regras.
- **Ambiguidade herdada:** arquivos antigos de outros projetos podem ter dois blocos e passarão a
  falhar ao salvar. É o comportamento desejado (recusar > destruir), mas a mensagem precisa dizer
  o que fazer.
