# WO 0057 — corrigir os dois números que a wo0056 escreveu errado

> **Tipo:** REGISTRO — `meta/STATUS.md`, `meta/IDEAS.md`. Nao toca codigo nem `.claude/`.
> **Config sugerida:** modelo intermediario, `/effort` baixo. Duas ancoras de uma linha.
> **Pre-requisito:** wo0056 aplicada e empurrada (`a29fe57`), **122 testes verdes**, arvore limpa.
> **Base:** relatorio de aplicacao `260826-1242-code-flatdrop.txt`, secao «Achados / desvios» —
> dois achados do executor, **os dois contra a WO, e os dois procedentes**.
> **Ancoras lidas em:** *(trecho literal lido NESTE turno, no mount gerado 2026-08-26 13:28)*
> - `meta/STATUS.md`, linha 115: `**Fase 2a (wo0056, feita):** as «Regras de higiene» do CEREBRO
>   passaram de 8 para 16 bullets`.
> - `meta/IDEAS.md`, primeiro item de «Feedback para o Kit», que a wo0056 acabou de inserir:
>   `- **Edição em `.claude/` não vai por WO — vai pelo chat, como arquivo inteiro.**`
> - Contagem conferida no arquivo vivo: a secao de higiene tem **18** bullets.
> **Idempotencia:** procure `8 para 18 bullets` e `número de conferência`. Se ja existirem, **PULE**.
> **Proximo comando:** nao ha — a fase 2b depende de o pacote do KCM voltar ao mount (ver §1).

> **Canal dos meta neste ciclo = CODE** (`STATUS`, `IDEAS`).

---

## 1. Por que

O executor devolveu dois achados na aplicacao da wo0056, **os dois apontando erro na propria WO**,
e os dois estao certos:

1. **A WO previa 16 bullets na secao de higiene; o texto que ela mandava colar produz 18.** O
   executor contou 18, **recusou-se a adivinhar quais dois sobravam** e reportou — exatamente o
   comportamento que a regra «nao chute lugar proximo» pede. O arquivo esta **certo**; o numero
   estava errado em dois lugares da WO, e um deles foi copiado para dentro do `meta/STATUS.md`,
   onde virou afirmacao falsa versionada. **Esta WO conserta esse.**
2. **A WO mandava conferir `grep "wo0044" CLAUDE.md` → 0**, quando o proprio texto que ela mandava
   escrever **cita** `wo0044` dentro do exemplo («este dizia `wo0044` quando o repo ja ia na
   `wo0055`»). O executor aplicou o texto literal, nao editou a prosa por conta, e reportou. **Nada
   a consertar no arquivo** — a citacao e proposital, e e o proprio argumento do bullet. O que
   sobra e a licao, que vai para o `IDEAS`.

**Os dois erros sao da mesma familia, e ela ja tem nome neste projeto:** numero de conferencia
**produzido de memoria em vez de medido** — a mesma classe que a wo0055 cometeu com o `118` e que
a propria wo0056 registrou no `IDEAS`. A correcao de metodo esta na Edicao 2.

**Fase 2b nao entra nesta WO, e o motivo e material:** o pacote `template-update` **nao esta mais
no mount**. Conferido na listagem de 2026-08-26 13:28: nem `CEREBRO__template-update.md`, nem
`_UPDATE-MANIFEST.md`, nem `_UPDATE-PROMPT.md`. Sem o texto de origem, a fase 2b so poderia ser
escrita de memoria — que e precisamente o defeito que esta WO conserta.

---

## Edicao 1 — `meta/STATUS.md` · o numero medido

**Ancora** (uma linha):

```
   **Fase 2a (wo0056, feita):** as «Regras de higiene» do CEREBRO passaram de 8 para 16 bullets
```

**Substituir por:**

```
   **Fase 2a (wo0056, feita):** as «Regras de higiene» do CEREBRO passaram de 8 para **18** bullets
```

> **Por que 18 e nao 16:** os 8 originais foram mantidos em numero (6 deles com o texto ampliado)
> e entraram 10 novos. O `16` da wo0056 era estimativa da contagem do template, escrita antes de
> medir; a contagem real do arquivo depois de aplicado e 18, e foi o executor quem mediu. Se voce
> quiser reconferir:
> `sed -n '/^## Regras de higiene/,/^## Como o assistente entrega/p' meta/CEREBRO.md | grep -c "^- "`

## Edicao 2 — `meta/IDEAS.md` · a licao de metodo, em «Feedback para o Kit»

**Ancora** (uma linha, primeiro item da secao — inserido pela wo0056):

```
- **Edição em `.claude/` não vai por WO — vai pelo chat, como arquivo inteiro.** Medido em
```

**Inserir IMEDIATAMENTE ANTES:**

```
- **Número de checklist é DERIVADO do texto da WO, nunca estimado antes dela.** Terceira
  ocorrência da mesma falha em três WOs seguidas, o que já a qualifica como padrão e não como
  descuido: a wo0055 mandou trocar `118` em três lugares quando dois eram estado e um era registro
  datado; a wo0056 previu «16 bullets» onde o texto que ela mesma mandava colar produz **18**, e
  mandou conferir `grep "wo0044" → 0` num arquivo onde o próprio texto novo cita `wo0044` de
  propósito. **Nas três, o executor mediu, discordou e reportou sem consertar por conta — e nas
  três ele estava certo.** A causa é sempre a mesma: o número foi escrito na fase de *raciocínio*
  sobre o merge e não foi recalculado depois que o texto final da edição ficou pronto. **A regra:**
  onde as âncoras já são extraídas do arquivo vivo por script, as contagens do checklist saem do
  mesmo script, sobre o texto final — e aí param de poder divergir do que a WO manda escrever.
  Enquanto não for automático, vale a pergunta antes de escrever qualquer número de conferência:
  *«isto eu medi agora, ou lembrei?»*. O kit poderia dizer isso no campo do checklist do modelo de
  WO, ao lado dos três campos por passo de verificação.
```

---

## Fora de escopo

- **O `CLAUDE.md` não muda.** A citação de `wo0044` dentro do exemplo é proposital e fica.
- **Fase 2b/2c do merge** — bloqueadas até o pacote voltar ao mount.
- **Nada de `.claude/`, nada de `flatdrop/`.**

## Armadilhas desta WO

- A âncora da Edição 1 **termina no meio da frase** (a linha continua na seguinte, com o `(3.443 →
  12.922 bytes...)`). É de propósito: a linha física é a unidade da âncora. Não estenda para a
  linha seguinte, e não reescreva o resto do parágrafo.
- Se a contagem de bullets no seu arquivo **não** for 18, **PARE e reporte o número real** — a
  Edição 1 existe justamente para o documento parar de afirmar um número que ninguém mediu.

---

## Depois de aplicar — conferência antes do commit

- [ ] `git diff` mostra exatamente: `meta/STATUS.md`, `meta/IDEAS.md`.
- [ ] **Medido, não estimado:**
      `sed -n '/^## Regras de higiene/,/^## Como o assistente entrega/p' meta/CEREBRO.md | grep -c "^- "`
      → e o `meta/STATUS.md` tem de dizer **esse mesmo número**. Reporte o número que saiu.
- [ ] `grep -c "16 bullets" meta/STATUS.md` → **0**.
- [ ] `python -m pytest -q` → **122**, sem mudança (WO só de doc).
- [ ] **Invariante DEC-020:** nada em `flatdrop/`.

## Relatório de aplicação *(quem aplica preenche ao terminar)*

O que foi feito · o número medido de bullets · o commit · **o push, com o resultado real**, escrito
DEPOIS de o push estar resolvido. Grave o MESMO relatório em `../AAMMDD-HHMM-code-flatdrop.txt`.

## Commit — blocos separados, mensagem SEM acento

```
git add meta\STATUS.md meta\IDEAS.md meta\workorders\260826-wo0057-corrigir-numeros-da-wo0056.md
```

```
git commit -m "docs(meta): corrigir a contagem de bullets da fase 2a" -m "O STATUS afirmava 16 bullets na secao de higiene; o numero medido no arquivo e 18. O 16 era estimativa escrita antes do texto final da edicao. Vai junto a licao de metodo no IDEAS: numero de checklist e derivado do texto da WO, nunca estimado antes - terceira ocorrencia em tres WOs, e nas tres o executor mediu e estava certo."
```

```
git push
```
