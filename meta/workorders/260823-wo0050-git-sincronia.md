# WO 0050 — a linha de git do `_MANIFEST` diz se o commit saiu daqui

> **Tipo:** mista — CODIGO (`flatdrop/core.py`, `tests/test_core.py`) + REGISTRO (`meta/STATUS.md`,
> `meta/CHANGELOG.md`).
> **Config sugerida:** modelo intermediario, `/effort` medio. As ancoras sao curtas e o trecho de
> codigo e isolado; nao precisa de esforco alto.
> **Pre-requisito:** 0.15.0, commit `8913a39`, arvore limpa, 92 testes verdes (numero do relatorio
> da wo0049 em 02/08 — reconfira ao aplicar).
> **Base:** carta 01 do KCM (`260821-...-01-o-manifesto-e-o-que-chegou.md`), item 3; devolucao
> anterior de 02/08 na mensagem do KCM; nota `260802-2319`.
> **Ancora semantica:** se um trecho-ancora nao bater EXATAMENTE, **PARE e reporte** — nunca chute
> um lugar proximo.
> **Idempotencia:** antes de cada insercao, procure a frase-chave do texto NOVO (`_divergence`,
> `sem upstream`, `wo0050`). Se ja existir, **PULE** e diga no relatorio.

> **Canal dos meta neste ciclo:** `meta/STATUS.md` e `meta/CHANGELOG.md` = **CODE** (esta WO E o
> registro deles — nao espere doc do chat). `meta/IDEAS.md` = **CHAT** (o chat ja entregou o
> arquivo inteiro nesta sessao) — **nao toque no `IDEAS.md`.** `meta/DECISIONS.md` nao muda: isto
> completa a DEC/implementacao da wo0048, nao decide nada novo.

---

## 1. Por que

A linha `**Git (foto da geração) — status:** branch main · limpo` fala da **arvore de trabalho** e
cala sobre a relacao com o remoto. Um repo com tres commits locais nao empurrados le exatamente como
um repo em dia — e o mount, que e uma copia sem `.git`, e a unica coisa que a conversa seguinte tem.
O KCM devolveu isso duas vezes (02/08 e carta 01) e relata que quase produziu um relato errado numa
WO real do lado deles.

**O que ja existe, e por que ninguem viu:** o `ahead` **foi implementado na wo0048** (leia
`git_snapshot`). Ele so nao imprime quando `ahead=0`, que era o caso dos manifestos que os dois
lados olharam. Tres registros afirmaram o contrario a partir de ausencia de saida — a nota
`260802-2319`, a carta do KCM e o proprio backlog do `STATUS`. Esta WO **nao reimplementa** o
`ahead`: ela completa o que de fato falta.

**O que falta, medido lendo o codigo em 2026-08-23:**

1. **`behind` e descartado.** O parser faz `.split(",")[0]`, entao `[ahead 1, behind 2]` vira so
   «1 a frente» e o `behind` some.
2. **«sem upstream» sai calado.** Branch sem upstream nao tem `...origin/main` na linha `##`: o
   sufixo fica vazio e a linha le como se estivesse tudo em ordem. E o pior caso dos tres, porque
   ali os commits nao existem em lugar nenhum.
3. **Nenhum teste cobre o trecho.** Os quatro testes de git pulam sozinhos onde nao ha `git`, e o
   `ahead` nunca teve teste. A correcao entra como **funcao pura** (`_divergence`), justamente para
   ser testavel sem `git` instalado — fechando tambem a lacuna registrada no `STATUS`.

Fora de escopo, mas registrado: o `upstream` passa a sair pelo nome real (`origin/main`) em vez do
literal `origin`, porque a informacao esta na mesma linha e o remoto nem sempre se chama `origin`.

---

## Edicao 1 — `flatdrop/core.py` · funcao pura `_divergence`, antes de `git_snapshot`

**Ancora** (a linha `def` de `git_snapshot` e a primeira linha da sua docstring, logo depois do
helper `_git`):

```
def git_snapshot(root) -> tuple[str | None, str | None]:
    """(commit, resumo do status) da raiz — FOTO do momento, nao estado atual.
```

**Inserir IMEDIATAMENTE ANTES** da ancora (o texto novo termina com duas linhas em branco, como o
resto do arquivo):

```
def _divergence(header: str) -> str:
    """Sufixo de sincronia lido da linha ``##`` do ``git status --porcelain=v1 --branch``.

    Funcao PURA de proposito: e a unica parte do snapshot que da para testar SEM git instalado.
    Os testes de git existentes pulam sozinhos onde nao ha git, e verde num ambiente assim nao
    prova nada — lacuna registrada no STATUS desde a wo0048.

    Formas de entrada e o que sai::

        ## main                                    ->  · sem upstream
        ## main...origin/main                      ->  · sincronizado com origin/main
        ## main...origin/main [ahead 1]            ->  · 1 commit(s) a frente de origin/main
        ## main...origin/main [behind 2]           ->  · 2 commit(s) atras de origin/main
        ## main...origin/main [ahead 1, behind 2]  ->  · 1 a frente e 2 atras de origin/main
        ## HEAD (no branch)                        ->  · HEAD solto, sem branch

    Devolve string VAZIA so quando a linha nao e reconhecivel — nunca inventa estado: dizer
    "sincronizado" por engano e pior do que nao dizer nada.
    """
    corpo = header[2:].strip()
    if not corpo:
        return ""
    if corpo.startswith("HEAD (no branch)"):
        return " · HEAD solto, sem branch"
    trecho, _, resto = corpo.partition(" [")
    if "..." not in trecho:
        # Sem upstream configurado: o repo pode ter N commits que nao existem em lugar nenhum,
        # e nada no resto do status denuncia isso. E o caso em que calar engana mais.
        return " · sem upstream"
    upstream = trecho.split("...", 1)[1].strip()
    ahead = behind = 0
    for parte in resto.rstrip("]").split(","):
        chave, _, valor = parte.strip().partition(" ")
        if not valor.isdigit():
            continue
        if chave == "ahead":
            ahead = int(valor)
        elif chave == "behind":
            behind = int(valor)
    if ahead and behind:
        return f" · {ahead} a frente e {behind} atras de {upstream}"
    if ahead:
        return f" · {ahead} commit(s) a frente de {upstream}"
    if behind:
        return f" · {behind} commit(s) atras de {upstream}"
    return f" · sincronizado com {upstream}"


```

## Edicao 2 — `flatdrop/core.py` · terceiro item na docstring de `git_snapshot`

**Ancora** (fim da docstring de `git_snapshot`):

```
    - status: RESUMO numerico, nunca a listagem. ``git status`` verboso e ruido e vaza nome
      de arquivo pessoal nao rastreado — o mount vai para uma conversa.
    """
```

**Substituir por:**

```
    - status: RESUMO numerico, nunca a listagem. ``git status`` verboso e ruido e vaza nome
      de arquivo pessoal nao rastreado — o mount vai para uma conversa.
    - sincronia: ``ahead``/``behind``/"sem upstream" explicitos (ver ``_divergence``). "limpo"
      fala so da arvore de trabalho: um repo com tres commits locais nao empurrados lia como
      repo em dia. Devolvido pelo KCM em 2026-08-02 e de novo na carta 01 (wo0050).
    """
```

## Edicao 3a — `flatdrop/core.py` · o laco passa a usar `_divergence`

**Ancora** (dentro de `git_snapshot`, logo depois do `if porcelain is None:`) — **atencao a barra
invertida de continuacao de linha, que faz parte do texto**:

```
    modificados = nao_rastreados = 0
    frente = ""
    for ln in porcelain.splitlines():
        if ln.startswith("##"):
            if "[ahead " in ln:
                frente = " · " + ln.split("[ahead ", 1)[1].split("]")[0].split(",")[0] \
                    .strip() + " commit(s) a frente de origin"
            continue
```

**Substituir por:**

```
    modificados = nao_rastreados = 0
    sincronia = ""
    for ln in porcelain.splitlines():
        if ln.startswith("##"):
            sincronia = _divergence(ln)
            continue
```

## Edicao 3b — `flatdrop/core.py` · o `return` acompanha o nome novo

**Ancora** (ultima linha de `git_snapshot`):

```
    return commit, " · ".join(partes) + frente
```

**Substituir por:**

```
    return commit, " · ".join(partes) + sincronia
```

> Depois de 3a e 3b, **nenhuma ocorrencia de `frente` deve sobrar** em `flatdrop/core.py`
> (`grep -n "frente" flatdrop/core.py` → so a que estiver dentro de string de mensagem nova).

## Edicao 4 — `tests/test_core.py` · oito testes novos, no fim do arquivo

**Ancora** (as duas ultimas linhas do arquivo, dentro de `test_manifesto_traz_as_duas_linhas`):

```
    assert "Git (foto da geração) — último commit:" in texto
    assert "Git (foto da geração) — status:" in texto
```

**Inserir IMEDIATAMENTE APOS** (duas linhas em branco antes do primeiro `def`):

```


# --- sincronia com o remoto (wo0050) — puros, rodam sem git instalado ---

def test_divergencia_sem_upstream():
    """Branch sem upstream nao pode ler como repo em dia — e o pior caso dos tres."""
    assert core._divergence("## main") == " · sem upstream"


def test_divergencia_sincronizado():
    """Com upstream e sem divergencia, a linha DIZ que esta sincronizado, em vez de calar."""
    assert core._divergence("## main...origin/main") == " · sincronizado com origin/main"


def test_divergencia_ahead():
    """O caso que a wo0048 ja resolvia — fica coberto para nao regredir."""
    assert core._divergence("## main...origin/main [ahead 1]") == \
        " · 1 commit(s) a frente de origin/main"


def test_divergencia_behind():
    assert core._divergence("## main...origin/main [behind 3]") == \
        " · 3 commit(s) atras de origin/main"


def test_divergencia_ahead_e_behind():
    """O defeito da wo0048: o `.split(",")[0]` jogava o behind fora."""
    s = core._divergence("## main...origin/main [ahead 1, behind 2]")
    assert "1 a frente" in s and "2 atras" in s


def test_divergencia_head_solto():
    assert "HEAD solto" in core._divergence("## HEAD (no branch)")


def test_divergencia_linha_estranha_nao_inventa():
    """Diante de linha irreconhecivel, silencio — nunca um estado inventado."""
    assert core._divergence("##") == ""


@pytest.mark.skipif(not _git_disponivel(), reason="git nao instalado no ambiente")
def test_git_snapshot_sem_upstream_no_status(tmp_path):
    """Ponta a ponta: repo local sem remoto sai como 'limpo' E 'sem upstream'."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True)
    (tmp_path / "a.md").write_text("x\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "primeiro"], cwd=tmp_path, check=True)
    _commit, status = core.git_snapshot(tmp_path)
    assert "limpo" in status and "sem upstream" in status
```

## Edicao 5a — `meta/STATUS.md` · o campo «Commit» para de guardar hash

**Ancora** (bloco de estado, no topo):

```
- **Data:** 2026-08-02
- **Commit:** `9d8e62f` (wo0048), branch `main`, **limpo** e com push feito. **Este campo deixou de
  depender de relato:** desde a wo0048 o `_MANIFEST` traz `git log -1` e o resumo do `git status`
  como foto do momento da geração — leia de lá, e só peça se o manifesto for de uma versão
  anterior.
```

**Substituir por:**

```
- **Data:** 2026-08-23 (a sessão anterior foi 2026-08-02; o repo ficou parado no intervalo)
- **Commit:** **leia no `_MANIFEST`** («Git (foto da geração)»), que desde a wo0048 traz
  `git log -1` e o resumo do `git status`. **Este campo não guarda mais hash:** guardar um aqui
  garante que ele nasça velho — a wo0049 se commitou DEPOIS de escrever esta linha, e ela passou
  20 dias apontando `9d8e62f` quando o repo estava em `8913a39`. Uma fonte de verdade por dado.
```

## Edicao 5b — `meta/STATUS.md` · a lacuna dos testes de git encolheu

**Ancora** (seção «Qualidade / testes», último item):

```
- **Lacuna que fica:** os quatro testes de git pulam sozinhos onde não houver `git` instalado —
  verde num ambiente sem git não prova nada sobre a wo0048.
```

**Substituir por:**

```
- **Lacuna que encolheu (wo0050):** os testes que precisam de `git` continuam pulando sozinhos onde
  ele não existir, mas a parte que mais errava — ler a linha `##` do `--porcelain` — virou função
  pura (`_divergence`) e ganhou **sete testes que rodam sem `git` nenhum**. Sobra dependente de
  ambiente: só o que exige repositório de verdade.
```

## Edicao 5c — `meta/STATUS.md` · backlog: sai item entregue, entra a frente real

**Ancora** (seção «Em aberto (produto)», itens 3 a 6 — bloco inteiro):

```
3. **FlatDrop grava o estado do repo no `_MANIFEST`** (`git log -1` + resumo de `git status`, como
   foto do momento da geração). Apaga uma ressalva inteira do lado do chat.
4. **Mostrar a REGRA de ignore que casou**, não só a contagem por motivo.
5. Aviso mais visível quando o `pathspec` está ausente.
6. Adiadas, com gatilho de retorno em `IDEAS.md`: multi-raiz na GUI, `pasta/` como exclusão dura,
   UI-2/UI-3, saída da CLI ASCII-safe, formato «caminho escrito».
```

**Substituir por:**

```
3. **Decidir o formato do `_MANIFEST`** — análise em
   `meta/analises/260823-ANALISE-formato-do-manifesto.md`, «Em discussão», parada num ponto de
   decisão do autor. O nome plano declarado na tabela **não existe** no mount para dotfile e nome
   com ponto interno (medido: 3 de 38 aqui; 11 de 109 pelo KCM), e falta `mtime` por arquivo.
   *(O item que estava neste lugar — «FlatDrop grava o estado do repo no `_MANIFEST`» — saiu: foi
   ENTREGUE na 0.15.0 pela wo0048 e continuava listado como pendente.)*
4. **Mostrar a REGRA de ignore que casou**, não só a contagem por motivo. **Reforçado em 07/08**
   pela nota `260807-1324`: em projeto irmão, um `.xlsx` inteiro sumiu do achatamento por estar em
   pasta gitignorada e a ausência só foi notada sessões depois. A contagem por motivo já existe na
   saída — o que falta é a regra.
5. Aviso mais visível quando o `pathspec` está ausente.
6. Adiadas, com gatilho de retorno em `IDEAS.md`: multi-raiz na GUI, `pasta/` como exclusão dura,
   UI-2/UI-3, formato «caminho escrito». *(A **saída da CLI ASCII-safe** deixou de ser adiada — o
   gatilho disparou em 02/08 e a curadoria de 23/08 a moveu para «Ativas».)*
```

## Edicao 6 — `meta/CHANGELOG.md` · registro em `[Não lançado]` (sem cortar versão)

**Ancora** (o parágrafo em itálico logo abaixo de `## [Não lançado]`):

```
_Itens de produto em aberto: multi-raiz na GUI (decisão A/B pendente), formato de nome
"caminho escrito" (raiz→pastas→stem), UI-2/UI-3, saída da CLI ASCII-safe — todos com gatilho
de retorno em `IDEAS.md` › Adiadas. Decisão em aberto: `pasta/*` + `!mantido` no gerador do
editor (`meta/analises/260728-ANALISE-gerador-flatdropignore.md`)._
```

**Substituir por:**

```
_Itens de produto em aberto: multi-raiz na GUI (decisão A/B pendente), formato de nome
"caminho escrito" (raiz→pastas→stem), UI-2/UI-3 — todos com gatilho de retorno em `IDEAS.md` ›
Adiadas. A **saída da CLI ASCII-safe** saiu de «Adiadas» (gatilho disparado no smoke da wo0048) e
está em «Ativas». Decisões em aberto: `pasta/*` + `!mantido` no gerador do editor
(`meta/analises/260728-ANALISE-gerador-flatdropignore.md`) e o **formato do `_MANIFEST`**
(`meta/analises/260823-ANALISE-formato-do-manifesto.md`)._

### Adicionado
- **A linha de git do `_MANIFEST` passa a dizer se o commit saiu daqui (wo0050).** Além do `ahead`
  que a wo0048 já emitia, a linha agora traz o **`behind`**, diz **«sem upstream»** quando o branch
  não rastreia nada e **«sincronizado com <upstream>»** quando está em dia — e nomeia o upstream
  real em vez do literal `origin`. Motivo: «limpo» descreve a árvore de trabalho e não distinguia
  *«o mount é o commit»* de *«o mount é o commit, e o commit não saiu daqui»*.

### Corrigido
- **O `behind` era descartado no parser (wo0050).** `[ahead 1, behind 2]` virava só «1 a frente»,
  porque o trecho era cortado num `.split(",")[0]`. A leitura da linha `##` virou a função pura
  `_divergence`, com **sete testes que rodam sem `git` instalado** — o trecho não tinha teste
  nenhum desde a wo0048.
```

---

## Fora de escopo

- **Não corta versão.** Nada de mexer em `flatdrop/__init__.py`: o corte é do próximo registro de
  fecho, quando houver mais coisa na leva.
- **Não toca `meta/IDEAS.md`** (canal CHAT neste ciclo) nem `meta/DECISIONS.md`.
- **Não implementa nada da carta 01 itens 1 e 2** (nome sanitizado, `mtime`): estão na análise, que
  para num ponto de decisão do autor.
- **Não responde ao KCM.** A carta 02 é da raia do chat, e sai depois desta WO aplicada — declarar
  «vai sair» é o erro que o próprio KCM pediu desculpas por ter cometido na errata da carta 01.

## Armadilhas desta WO

- **A âncora da Edição 3a contém uma barra invertida de continuação de linha** (` \` no fim) e o
  caractere `·`. Copie o bloco como está; se o casamento falhar por causa dela, **PARE e reporte**
  em vez de reconstruir o trecho à mão.
- **`git_snapshot` já tem `ahead` funcionando.** Se ao ler o código você achar que ele não tem, você
  está lendo outra coisa — pare e diga o que encontrou. Esta WO **completa**, não reescreve.
- Os arquivos tocados são **LF** (conferido em 23/08). Âncora multi-linha colada com CRLF não casa.
- `flatdrop/core.py` tem acentos em comentários de outras seções, mas o trecho de git é escrito
  **sem acento** — mantenha o padrão local ao inserir.

---

## Depois de aplicar — conferência antes do commit

- [ ] `git diff` mostra **exatamente** quatro arquivos: `flatdrop/core.py`, `tests/test_core.py`,
      `meta/STATUS.md`, `meta/CHANGELOG.md` — e nada além (o `meta/IDEAS.md` e a análise chegam pelo
      chat; se aparecerem como *untracked*, é isso mesmo).
- [ ] `grep -n "frente" flatdrop/core.py` não devolve mais o parser antigo.
- [ ] `python -m pytest -q` passa com **0 erros**. Esperado: **100 testes** (92 + 8). Se der outro
      número, diga qual no relatório antes de commitar.
- [ ] Rode `python -m pytest -q -k divergencia` e confirme que **7 testes rodam** mesmo se o `git`
      não estiver instalado — é o ponto da mudança.
- [ ] **Smoke real, que a suíte não alcança:** achate este próprio repo com um commit local **não
      empurrado** e confira que o `_MANIFEST` sai com `· N commit(s) a frente de origin/main`.
      Depois, `git push`, achate de novo: deve sair `· sincronizado com origin/main`.
- [ ] **Invariante DEC-020:** esta WO não toca `flatdrop/cli.py`, `gui._build_cli_args`,
      `gui._generate_bat` nem `gui._sources`. Se precisar tocar, **PARE e reporte como URGENTE**.

## Relatório de aplicação *(quem aplica preenche ao terminar)*

O que foi feito · o que fugiu do texto literal da WO · arquivos tocados · resultado da suíte · o
commit. Grave o MESMO relatório em `../AAMMDD-HHMM-code-flatdrop.txt` (pasta-pai do repo).

## Commit — blocos separados, mensagem SEM acento

```
git add flatdrop\core.py tests\test_core.py meta\STATUS.md meta\CHANGELOG.md meta\workorders\260823-wo0050-git-sincronia.md
```

```
git commit -m "feat(manifest): dizer ahead, behind e sem upstream no estado do git" -m "A linha de status falava so da arvore de trabalho: repo com commit nao empurrado lia como repo em dia. A leitura da linha ## virou a funcao pura _divergence, com sete testes que rodam sem git instalado. Devolucao do KCM em 02-08 e na carta 01 (wo0050)."
```

```
git push
```
