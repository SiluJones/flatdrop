# WO 0052 — a saída da CLI para de quebrar no console do Windows

> **Tipo:** mista — CODIGO (`flatdrop/cli.py`, `tests/test_cli.py`) + REGISTRO (`meta/IDEAS.md`,
> `meta/CHANGELOG.md`).
> **Config sugerida:** modelo intermediario, `/effort` medio.
> **Pre-requisito:** wo0051 aplicada e empurrada (`9333363`), arvore limpa, **109 testes verdes**.
> **Base:** ideia «Saida da CLI ASCII-safe» (IDEAS › Ativas, gatilho disparado em 02/08 e de novo
> nos relatorios das wo0050 e wo0051) + medicao de code pages feita em 24/08 (abaixo).
> **Ordem:** aplique ANTES da wo0053. As duas ancoram no mesmo item do CHANGELOG, mas por
> *inserir antes*, entao a ordem inversa tambem funciona — so o resultado troca de lugar.
> **Ancora semantica:** se um trecho-ancora nao bater EXATAMENTE, **PARE e reporte**.
> **Idempotencia:** procure `  -> {reason}` e `isascii` antes de editar; se ja existirem, **PULE**.

> **Canal dos meta neste ciclo = CODE** (`IDEAS`, `CHANGELOG`). Nao toque em `STATUS`, `DECISIONS`
> nem em `meta/analises/` — sao da wo0053 ou do chat.

> **AUTORIZACAO EXPLICITA DA DEC-020.** Esta WO **toca `flatdrop/cli.py`**, que a DEC-020 protege.
> O autor autorizou por escrito em 2026-08-24, com escopo delimitado: **trocar glifos da saida**.
> Nada de argumento, nome de flag, ordem de parametro ou semantica muda — o contrato que a DEC-020
> defende (o caminho `gui -> .bat -> cli`) sai desta WO **mais** seguro, nao menos. Se alguma
> edicao parecer exigir mexer em argumento, **PARE e reporte como URGENTE**.

---

## 1. Por que

`python run.py ...` **quebra com `UnicodeEncodeError`** ao imprimir o resumo final, no `↳` de
`_summary`. Aconteceu no smoke da wo0048, no da wo0050 e no da wo0051 — quatro vezes, e a ultima
delas ja nao foi smoke: foi uso.

O dano e limitado (os arquivos ja estao gravados quando o traceback sai; so o `print` final falha),
mas o efeito pratico e pessimo: **a ferramenta termina com um traceback vermelho depois de ter dado
certo.** Quem roda pelo `.bat` — o caminho que a GUI gera — nao tem como saber que o resultado esta
correto.

**Medido em 2026-08-24** (`str.encode` contra cada code page):

| glifo | cp1252 (PowerShell / Git Bash) | cp850 (CMD pt-BR) | cp437 (CMD US) |
|---|---|---|---|
| `↳` U+21B3 | **falha** | **falha** | **falha** |
| `⚠` U+26A0 | **falha** | **falha** | **falha** |
| `•` U+2022 | ok | **falha** | **falha** |
| `…` U+2026 | ok | **falha** | **falha** |
| `ã`, `Í` (acentos) | ok | ok | **falha** |

Ou seja: o `↳` derruba **todos** os consoles do Windows, e no CMD pt-BR (cp850, o caminho do
`.bat`) o `•` e o `…` derrubam junto. Trocar os quatro glifos por ASCII resolve cp1252 **e** cp850
— os dois que este projeto realmente usa. O cp437 continuaria quebrando **nos acentos**, que sao
outra conversa: fica registrado no `IDEAS`, com gatilho, e **fora** desta WO.

Consequencia colateral boa: some a dependencia de `chcp 65001` nos `.bat`, que era a razao original
da ideia e o que o FIX-003 ja tinha ensinado sobre `.bat` em ASCII.

---

## Edicao 1 — `flatdrop/cli.py` · lista de fontes em `_summary`

**Ancora** (dentro de `_summary`, no ramo de multi-fonte):

```
        lines += [f"  • {d}" for d in plan.sources]
```

**Substituir por:**

```
        lines += [f"  * {d}" for d in plan.sources]
```

## Edicao 2 — `flatdrop/cli.py` · amostra dos pulados em `_summary`

**Ancora** (as duas linhas juntas — o `…` esta na primeira):

```
        extra = f" … (+{total - len(shown)})" if total > len(shown) else ""
        lines.append(f"  ↳ {reason}: " + ", ".join(shown) + extra)
```

**Substituir por:**

```
        extra = f" ... (+{total - len(shown)})" if total > len(shown) else ""
        lines.append(f"  -> {reason}: " + ", ".join(shown) + extra)
```

## Edicao 3 — `flatdrop/cli.py` · avisos do plano em `_summary`

**Ancora:**

```
        lines += [f"  ⚠ {w}" for w in plan.warnings]
```

**Substituir por:**

```
        lines += [f"  ! {w}" for w in plan.warnings]
```

## Edicao 4 — `flatdrop/cli.py` · avisos de execucao em `main`

**Ancora** (no fim de `main`, depois de «AVISOS de execução:»):

```
        for w in res.warnings:
            print(f"  ⚠ {w}")
```

**Substituir por:**

```
        for w in res.warnings:
            print(f"  ! {w}")
```

## Edicao 5a — `tests/test_cli.py` · import do `core`

**Ancora** (topo do arquivo):

```
from flatdrop import cli
```

**Substituir por:**

```
from flatdrop import cli, core
```

## Edicao 5b — `tests/test_cli.py` · dois testes que fixam o invariante

**Ancora** (as ultimas linhas do arquivo — o teste do `.bat`; case o `def` e o que vier depois
dele ate o fim do arquivo NAO precisa entrar na ancora, use so a linha do `def`):

```
def test_open_gui_bat_content_semeia_start_dir():
```

**Inserir IMEDIATAMENTE ANTES** dessa linha (o texto novo termina com duas linhas em branco):

```
def test_summary_e_ascii_puro(tmp_path):
    """O resumo nao pode ter glifo fora do ASCII: e ele que quebra o console do Windows.

    Quatro ocorrencias de UnicodeEncodeError (wo0048, wo0050, wo0051 e uso real) vinham do
    `↳` de `_summary`. Medido em 24/08: `↳` e `⚠` falham em cp1252, cp850 e cp437; `•` e `…`
    falham em cp850 e cp437 — o cp850 e justamente o CMD pt-BR, o caminho do `.bat`.
    """
    root = _mono(tmp_path)
    cfg = cli._primary_cfg(cli.build_parser().parse_args(["--root", str(root), "--no-gitignore"]))
    plan = core.make_plan(root, cfg)
    texto = cli._summary(plan)
    assert texto.isascii(), [c for c in texto if not c.isascii()]


def test_saida_do_preview_sobrevive_ao_cp850(tmp_path, capsys):
    """A saida INTEIRA (com acentos) tem de caber no cp850, que e o CMD pt-BR padrao.

    Acento cabe em cp850; o que nunca coube foram os glifos decorativos. Este teste falha se
    alguem reintroduzir um deles em qualquer print da CLI, nao so no `_summary`.
    """
    root = _mono(tmp_path)
    cli.main(["--root", str(root), "--only-ext", "md", "--no-gitignore", "--preview"])
    out = capsys.readouterr().out
    out.encode("cp850")  # levanta UnicodeEncodeError se alguem reintroduzir glifo


```

> **Conferido em 24/08:** os nomes reais sao `cli.build_parser()` e `cli._primary_cfg(args)` — a
> WO ja usa esses. O `test_cli.py` importa **so** `from flatdrop import cli`: acrescente
> `from flatdrop import core` na mesma altura do import existente, senao o teste novo nao resolve
> `core.make_plan`. Se ainda assim algo nao bater, nao invente: leia o arquivo, use o caminho real
> e **diga no relatorio** o que mudou.

## Edicao 6a — `meta/IDEAS.md` · sai de Ativas a ideia entregue por esta WO

**Ancora** (secao «Ativas»):

```
- **Saída da CLI ASCII-safe.** Trocar `↳`/`•`/`—` da saída por `->`/`*`/`-` para
  dispensar `chcp 65001` nos `.bat` e evitar de vez problemas de code page. Baixo custo.
  Ficou **Adiada** desde a Fase 2, com o gatilho «volta na terceira ocorrência num smoke»;
  **o gatilho disparou em 2026-08-02** (smoke da wo0048: `UnicodeEncodeError` no `↳` sob cp1252,
  com o traceback saindo DEPOIS de o manifesto já estar no disco — não corrompe o resultado, mas
  assusta). **Movida para Ativas em 2026-08-23**, na curadoria prevista pelo handoff §3.3.
```

**Remover o bloco inteiro** (as seis linhas; o item seguinte, da linha de git, continua onde está).

## Edicao 6b — `meta/IDEAS.md` · sai de Ativas a ideia entregue pela wo0050

**Ancora** (o item logo abaixo do anterior):

```
- **A linha de git do manifesto não distingue «commitado» de «empurrado».** «limpo» fala da
  árvore de trabalho e cala sobre o `ahead/behind`. Devolvida pelo KCM em 02/08 e de novo na carta
  01. **Estado verificado em 23/08, lendo `core.git_snapshot`:** o `ahead` **já existe** desde a
  wo0048 — a nota `260802-2319` que dizia o contrário está errada, e o KCM concluiu ausência de
  recurso a partir de ausência de saída (`ahead=0` não imprime nada). Falta o `behind`, o caso
  «sem upstream» e teste nenhum cobre o trecho. **Vira a wo0050.**
```

**Remover o bloco inteiro.**

## Edicao 6c — `meta/IDEAS.md` · as duas entram em Concluídas

**Ancora** (primeira entrada da secao «Concluídas»):

```
- **O editor deve conviver com regra escrita à mão.** **ENTREGUE na 0.15.0** (FIX-012, wo0045 +
```

**Inserir IMEDIATAMENTE ANTES** dessa linha:

```
- **Saída da CLI ASCII-safe.** **ENTREGUE (wo0052).** Os quatro glifos da saída (`↳`, `•`, `…`,
  `⚠`) viraram `->`, `*`, `...` e `!`. Nasceu como item de conforto («dispensar `chcp 65001` nos
  `.bat`») e terminou como correção de bug: era `UnicodeEncodeError` derrubando o `print` final
  depois de a ferramenta já ter dado certo. Quatro ocorrências até virar WO — a última já não era
  smoke, era uso. Medição de 24/08: `↳` e `⚠` falham nos três code pages do Windows; `•` e `…`
  falham em cp850, que é o CMD pt-BR, ou seja, o caminho do `.bat`. **Resíduo conhecido:** em
  cp437 (CMD em locale US) os **acentos** ainda quebram — outra conversa, ver «Adiadas».
- **A linha de git do manifesto não distingue «commitado» de «empurrado».** **ENTREGUE (wo0050).**
  O `ahead` já existia desde a wo0048; entraram o `behind`, o «sem upstream», o «sincronizado com
  <upstream>» e o nome real do upstream. Sete testes puros, que rodam sem `git` instalado. O
  registro que sobra é o da lição, e está em «Feedback para o Kit»: ausência de saída não é
  ausência de recurso.
```

## Edicao 6d — `meta/IDEAS.md` · resíduo do cp437 vai para Adiadas, com gatilho

**Ancora** (cabecalho da secao «Adiadas», incluindo a nota explicativa que vem logo abaixo):

```
> Decisão consciente de não fazer agora. Cada item traz **o gatilho que o traz de volta** —
> ideia adiada sem gatilho é ideia perdida. Formato adotado do KCM v1.95.0 (DEC-028).
```

**Inserir IMEDIATAMENTE APOS:**

```

- **Acento na saída da CLI quebra em cp437.** A wo0052 resolveu os glifos decorativos e com isso
  cp1252 e cp850 — os dois consoles que este projeto usa. Sobra o cp437 (CMD em locale US), onde
  `ã`, `õ` e `Í` também não codificam: `PRÉ-VISUALIZAÇÃO`, `CONCLUÍDO` e `não` derrubariam o
  `print` do mesmo jeito. Não foi feito porque a correção certa aqui **não** é apagar os acentos
  (a saída ficaria feia em português para resolver um console que ninguém aqui usa) e sim uma rede
  de segurança no `print` — que é mudança de mecanismo, não de texto, e precisa de decisão própria
  por tocar `cli.py` (DEC-020). **Volta quando** alguém rodar o FlatDrop num Windows fora do
  locale pt-BR, ou quando a ferramenta for usada por outra pessoa. (Medido em 2026-08-24.)
```

## Edicao 6e — `meta/IDEAS.md` · duas convenções de processo, esperando o merge do kit

**Ancora** (primeiro item de «Feedback para o Kit»):

```
- **Ausência de saída não é ausência de recurso — leia o código antes de devolver a outra frente
```

**Inserir IMEDIATAMENTE ANTES** dessa linha:

```
- **Havendo WO no turno, o Code commita TUDO — inclusive o que o chat entregou junto.** Levantado
  pelo autor em 2026-08-24. Até a wo0050, o chat entregava a WO **e** um bloco `git add/commit`
  para os documentos que ele mesmo tinha escrito, obrigando o autor a um passo manual e criando
  risco de registro pendente (o defeito que a wo0044 existiu para consertar). A regra correta:
  **com WO, o bloco de commit é do Code e cobre a WO + os arquivos do chat + qualquer pendência;
  sem WO, o bloco é do chat.** A salvaguarda é conferir a presença no disco e, se faltar, commitar
  o resto e reportar — nunca inventar. Já em uso desde a wo0051; falta virar linha no
  `_TEMPLATE__workorders.md` e na skill `apply-wo`. *Guardado para o merge do próximo
  template-update do KCM, para não escrever convenção que o kit novo talvez já traga.*
- **O relatório de aplicação precisa ser gravado DEPOIS do push — ou corrigido depois dele.**
  Medido em 2026-08-24: o relatório da wo0051 diz «NÃO executei o push» porque o Code, com razão,
  pediu confirmação antes de mudar o remoto; o push saiu logo em seguida, e o `.txt` em disco ficou
  afirmando um estado falso, que é o que a sessão seguinte lê. **O que salvou:** o `_MANIFEST`
  gerado depois trazia «sincronizado com origin/main» — a linha da wo0050 desmentindo o relatório
  sozinha, um dia depois de existir. A correção: o campo `## Push` do relatório só é escrito com o
  resultado real, e se o push ficar pendente de confirmação o relatório é **reaberto e corrigido**
  quando ele sair. *Guardado para o mesmo merge.*
```

## Edicao 7 — `meta/CHANGELOG.md` · entrada em `[Não lançado]`

**Ancora** (primeiro item de `### Adicionado`, escrito pela wo0051):

```
- **O `_MANIFEST` avisa quais nomes chegam diferentes ao Projeto (wo0051, DEC-030).** Quando algum
```

**Inserir IMEDIATAMENTE ANTES** dessa linha:

```
- **A saída da CLI virou ASCII puro (wo0052).** `↳`, `•`, `…` e `⚠` viraram `->`, `*`, `...` e
  `!`. Era `UnicodeEncodeError` derrubando o `print` final **depois** de o achatamento ter dado
  certo — quatro ocorrências, a última em uso real. Medido: `↳` e `⚠` não codificam em nenhum dos
  três code pages do Windows, e `•`/`…` não codificam em cp850, que é o CMD pt-BR — o caminho do
  `.bat` gerado pela GUI. Some junto a dependência de `chcp 65001`. Um teste fixa o invariante
  (`_summary(...).isascii()`) e outro passa a saída inteira por `cp850`.
```

---

## Fora de escopo

- **Acentos e cp437** — ver o item novo em `IDEAS` › Adiadas, com gatilho.
- **Rede de segurança no `print`** (tentar imprimir e degradar em vez de estourar): é mudança de
  mecanismo, não de texto, e a autorização do autor foi para **glifos**. Fica para decisão própria.
- **A GUI não muda.** Ela escreve num widget Tk, que aceita qualquer glifo; trocar lá seria piorar
  a leitura sem motivo.
- **Nenhum argumento, flag ou semântica da CLI muda** (DEC-020).

## Armadilhas desta WO

- Os quatro glifos são **invisíveis à leitura rápida**. Confira com busca, não com o olho:
  depois de aplicar, `python -c "print([c for c in open('flatdrop/cli.py',encoding='utf-8').read()
  if ord(c)>127])"` deve devolver **só letras acentuadas** — nenhum `↳`, `•`, `…` ou `⚠`.
- A Edição 2 tem **duas** linhas na âncora, e o `…` está na primeira. Copie o bloco inteiro.
- `flatdrop/cli.py` é LF e UTF-8 (conferido em 24/08). Não converta o arquivo.

---

## Depois de aplicar — conferência antes do commit

- [ ] `git diff` mostra exatamente: `flatdrop/cli.py`, `tests/test_cli.py`, `meta/IDEAS.md`,
      `meta/CHANGELOG.md`.
- [ ] A busca por não-ASCII em `flatdrop/cli.py` devolve só acentos (comando acima).
- [ ] `python -m pytest -q` → **0 erros**, **111 testes** (109 + 2).
- [ ] **Smoke real, o motivo desta WO:** rode `python run.py --root . --dest <scratch> --only-ext
      md` num console **sem** `chcp 65001` (CMD normal). Esperado: termina imprimindo o resumo,
      **sem traceback**. Se ainda quebrar, copie o glifo culpado no relatório — sobrou um.
- [ ] **Invariante DEC-020:** `cli.py` foi tocado **com autorização escrita do autor**, e só em
      literais de saída. Confirme no relatório que nenhum argumento mudou.

## Relatório de aplicação *(quem aplica preenche ao terminar)*

O que foi feito · o que fugiu do texto literal · arquivos tocados · resultado da suíte · o commit ·
**o push** (com o resultado real; se ficar pendente de confirmação, volte e corrija este campo
depois que ele sair). Grave o MESMO relatório em `../AAMMDD-HHMM-code-flatdrop.txt`.

## Commit — blocos separados, mensagem SEM acento

```
git add flatdrop\cli.py tests\test_cli.py meta\IDEAS.md meta\CHANGELOG.md meta\workorders\260824-wo0052-cli-ascii-safe.md
```

```
git commit -m "fix(cli): trocar glifos da saida por ASCII" -m "O print final estourava UnicodeEncodeError depois de o achatamento ter dado certo. Medido: seta e alerta nao codificam em cp1252, cp850 nem cp437; bullet e reticencias nao codificam em cp850, o CMD pt-BR do .bat. Dois testes fixam o invariante. Autorizacao explicita do autor para tocar cli.py sob a DEC-020."
```

```
git push
```
