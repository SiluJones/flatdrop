# WO 0053 — o manifesto diz QUAIS arquivos do mount não são o commit

> **Tipo:** mista — CODIGO (`flatdrop/core.py`, `tests/test_core.py`) + REGISTRO
> (`meta/DECISIONS.md`, `meta/STATUS.md`, `meta/CHANGELOG.md`).
> **Config sugerida:** modelo intermediario, `/effort` medio.
> **Pre-requisito:** wo0052 aplicada, arvore limpa, **111 testes verdes**. Se aplicar esta antes da
> wo0052, o numero e 109 — diga qual no relatorio.
> **Base:** `meta/analises/260823-ANALISE-formato-do-manifesto.md` › Adendo › **Contraproposta 1**,
> aceita pelo autor em 2026-08-24. E a resposta ao item 2 da carta 01 do KCM — **no lugar** do
> `mtime` que eles pediram.
> **Ancora semantica:** se um trecho-ancora nao bater EXATAMENTE, **PARE e reporte**.
> **Idempotencia:** procure `git_modified_paths` e `DEC-031`; se ja existirem, **PULE**.

> **Canal dos meta neste ciclo = CODE** (`DECISIONS`, `STATUS`, `CHANGELOG`). **Nao toque no
> `IDEAS.md`** (e da wo0052) nem em `meta/analises/` (e do chat).

---

## 1. Por que

O manifesto **conta** os arquivos que divergem do commit (`1 modificado(s)`) e **não diz quais**.
Para quem lê o mount, a pergunta que sobra é a que mais importa: *o arquivo que estou lendo é o
commit, ou é trabalho por cima dele?* Hoje não há como saber sem perguntar ao autor — e perguntar é
exatamente o que o bloco de git da wo0048 existe para evitar.

**O KCM pediu `mtime` por arquivo para resolver isso. Não vamos fazer, e o motivo entra na carta
02:** `mtime` responde «quando foi tocado», não «mudou» — `git checkout` carimba a hora do checkout
em arquivo parado há meses, e cópia com preservação de timestamp mantém data velha em arquivo novo.
Pior: um dado que diz «velho» é uma **licença para não ler**, que é o gesto que produziu a falha que
o pedido tentava consertar. O `git status` **já sabe**, exatamente e de graça, quais arquivos não
são o commit. É dado de conteúdo, não proxy.

**A recusa que continua valendo.** A wo0048 decidiu «resumo, nunca listagem», por dois motivos:
ruído e vazamento de nome de arquivo pessoal não rastreado. O segundo motivo **continua inteiro
para os não rastreados** — e por isso eles seguem fora. Mas para os **rastreados que entraram no
achatamento** ele não protege nada: esses nomes já estão na tabela, duas linhas acima. É essa
distinção que a DEC-031 registra.

**Junto vai uma correção pedida pelo autor em 24/08:** ele aceitou o bloco de exceções da DEC-030
sabendo que ele afirma uma regra de sanitização não documentada, e pediu para «ficar esperto caso a
Anthropic corrija isso». A forma barata de ficar esperto não é vigilância — é o bloco **carregar o
próprio teste de falsificação**. Quem lê o manifesto dentro do Projeto está olhando para os nomes
reais: se eles baterem com a coluna 1, a previsão morreu. Uma frase resolve (Edição 3).

---

## Edicao 1 — `flatdrop/core.py` · parser puro + wrapper de git

**Ancora** (a linha `def` de `git_snapshot` e a primeira linha da sua docstring):

```
def git_snapshot(root) -> tuple[str | None, str | None]:
    """(commit, resumo do status) da raiz — FOTO do momento, nao estado atual.
```

**Inserir IMEDIATAMENTE ANTES** da ancora:

```
def _modified_paths(porcelain: str) -> list[str]:
    """Caminhos RASTREADOS que divergem do commit, lidos do ``git status --porcelain=v1``.

    Funcao PURA, pelo mesmo motivo do ``_divergence``: e testavel sem git instalado.

    Le so o que e rastreado — linhas ``??`` (nao rastreado) e ``!!`` (ignorado) ficam de fora **de
    proposito**. A wo0048 decidiu que o manifesto nao lista nome de arquivo, e para o nao rastreado
    essa recusa continua inteira: e ali que mora o arquivo pessoal que ninguem quer ver numa
    conversa. Rastreado que entrou no achatamento e outra coisa: o nome ja esta na tabela do
    proprio manifesto (DEC-031).

    Renomeado (``R  velho -> novo``) devolve o caminho NOVO, que e o que foi copiado.
    """
    fora: list[str] = []
    for ln in porcelain.splitlines():
        if len(ln) < 4 or ln.startswith(("##", "??", "!!")):
            continue
        caminho = ln[3:].strip()          # porcelain v1: dois codigos, espaco, caminho
        if " -> " in caminho:
            caminho = caminho.split(" -> ", 1)[1].strip()
        fora.append(caminho.strip('"'))
    return fora


def git_modified_paths(root) -> list[str]:
    """Wrapper fino do ``_modified_paths``; devolve [] quando nao ha git, repo ou saida.

    ``core.quotepath=false`` para caminho com acento vir legivel — o padrao do git escapa em
    octal (``"meta/an\\303\\241lise.md"``), e o manifesto e para leitura humana.

    Chama o git uma segunda vez de proposito, em vez de mudar o retorno de ``git_snapshot``:
    aquela assinatura ja tem seis testes em cima, e o custo aqui e um processo de 5 ms num
    caminho que ja roda tres.
    """
    porcelain = _git(root, "-c", "core.quotepath=false", "status", "--porcelain=v1")
    return _modified_paths(porcelain) if porcelain else []


```

## Edicao 2 — `flatdrop/core.py` · a linha nova no cabecalho do manifesto

**Ancora** (dentro de `write_manifest`, o bloco do git):

```
    if _status:
        lines.append(f"- **Git (foto da geração) — status:** {_status}")
    lines.append(f"- **Modo de renomeação:** {cfg.mode} · separador `{cfg.sep}`")
```

**Substituir por:**

```
    if _status:
        lines.append(f"- **Git (foto da geração) — status:** {_status}")
    # Nomear os divergentes que ENTRARAM no achatamento (DEC-031). O resumo acima conta e nao
    # diz quais; quem le o mount precisa saber se o arquivo que esta lendo e o commit ou trabalho
    # por cima dele. Nao rastreado continua sem aparecer — a recusa da wo0048 vale inteira la.
    # Em multi-fonte o `rel` pode nao ser relativo a plan.root: a intersecao entao nao casa e a
    # linha simplesmente nao sai. Falso negativo, nunca falso positivo.
    if _commit:
        _no_mount = {f.rel.as_posix() for f in plan.files}
        _fora_do_commit = [p for p in git_modified_paths(plan.root) if p in _no_mount]
        if _fora_do_commit:
            _nomes = ", ".join(f"`{p}`" for p in _fora_do_commit)
            lines.append(
                f"- **Git — arquivos deste mount que NÃO são o commit ({len(_fora_do_commit)}):** "
                f"{_nomes}"
            )
        elif "modificado" in (_status or ""):
            lines.append(
                "- **Git — arquivos deste mount que NÃO são o commit:** nenhum (o que está "
                "modificado na árvore não entrou no achatamento)"
            )
    lines.append(f"- **Modo de renomeação:** {cfg.mode} · separador `{cfg.sep}`")
```

## Edicao 3 — `flatdrop/core.py` · o bloco de excecoes ganha seu teste de falsificacao

**Ancora** (dentro do bloco condicional da DEC-030, no fim de `write_manifest`):

```
            "observada em 2026-08 e **não documentada pela Anthropic**: é PREVISÃO, não promessa. "
            "A tabela acima continua valendo para a pasta em disco.\n"
```

**Substituir por:**

```
            "observada em 2026-08 e **não documentada pela Anthropic**: é PREVISÃO, não promessa. "
            "A tabela acima continua valendo para a pasta em disco. **Se você está lendo isto "
            "DENTRO do Projeto e o arquivo aparece com o nome da coluna 1, a regra mudou — diga "
            "ao autor, porque esta previsão morreu.**\n"
```

## Edicao 4 — `tests/test_core.py` · sete testes novos, no fim do arquivo

**Ancora** (as ultimas linhas do arquivo, no teste que a wo0051 acrescentou):

```
    assert texto.splitlines()[0] == C.MANIFEST_SIGNATURE
    assert core.is_our_folder(res.dest)
```

**Inserir IMEDIATAMENTE APOS:**

```


# --- quais arquivos do mount nao sao o commit (wo0053, DEC-031) ---

def test_modificados_le_rastreado():
    """Modificado e adicionado no indice contam: os dois divergem do commit."""
    porcelain = " M meta/IDEAS.md\nA  meta/novo.md\n"
    assert core._modified_paths(porcelain) == ["meta/IDEAS.md", "meta/novo.md"]


def test_modificados_ignora_nao_rastreado():
    """`??` fica de fora — e ali que mora arquivo pessoal (recusa da wo0048, mantida)."""
    porcelain = " M a.md\n?? segredo-pessoal.txt\n!! build/\n"
    assert core._modified_paths(porcelain) == ["a.md"]


def test_modificados_ignora_cabecalho():
    """A linha `##` e do branch, nao e caminho."""
    assert core._modified_paths("## main...origin/main [ahead 1]\n") == []


def test_modificados_renomeado_vale_o_destino():
    """`R  velho -> novo`: o que foi copiado e o novo."""
    assert core._modified_paths("R  velho.md -> novo.md\n") == ["novo.md"]


def test_modificados_saida_vazia():
    assert core._modified_paths("") == []


@pytest.mark.skipif(not _git_disponivel(), reason="git nao instalado no ambiente")
def test_manifesto_nomeia_modificado_rastreado(tmp_path):
    """Ponta a ponta: o rastreado divergente e NOMEADO; o nao rastreado, nunca."""
    origem = tmp_path / "src"
    origem.mkdir()
    (origem / "a.md").write_text("x\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=origem, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=origem, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=origem, check=True)
    subprocess.run(["git", "add", "."], cwd=origem, check=True)
    subprocess.run(["git", "commit", "-qm", "primeiro"], cwd=origem, check=True)
    (origem / "a.md").write_text("x\ny\n", encoding="utf-8")   # rastreado, divergente
    (origem / "b.md").write_text("z\n", encoding="utf-8")      # NAO rastreado
    cfg = core.ScanConfig()
    plan = core.make_plan(origem, cfg)
    res = core.execute_plan(plan, tmp_path / "out", cfg)
    texto = list(res.dest.glob("_MANIFEST*.md"))[0].read_text(encoding="utf-8")
    linha = [ln for ln in texto.splitlines() if "NÃO são o commit" in ln][0]
    assert "`a.md`" in linha
    assert "b.md" not in linha
    assert "`b.md`" in texto          # o nao rastreado esta na TABELA, so nao nesta linha


@pytest.mark.skipif(not _git_disponivel(), reason="git nao instalado no ambiente")
def test_manifesto_repo_limpo_nao_tem_a_linha(tmp_path):
    """Sem divergencia, sem linha — o cabecalho ja diz `limpo`."""
    origem = tmp_path / "src"
    origem.mkdir()
    (origem / "a.md").write_text("x\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=origem, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=origem, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=origem, check=True)
    subprocess.run(["git", "add", "."], cwd=origem, check=True)
    subprocess.run(["git", "commit", "-qm", "primeiro"], cwd=origem, check=True)
    cfg = core.ScanConfig()
    plan = core.make_plan(origem, cfg)
    res = core.execute_plan(plan, tmp_path / "out", cfg)
    texto = list(res.dest.glob("_MANIFEST*.md"))[0].read_text(encoding="utf-8")
    assert "NÃO são o commit" not in texto
```

## Edicao 5 — `meta/DECISIONS.md` · DEC-031 no fim do arquivo

**Ancora** (as ultimas linhas do arquivo, fim da DEC-030):

```
`<!-- flatdrop-manifest v1 -->` continua na primeira linha (DEC-007) — há teste fixando isso.
```

**Inserir IMEDIATAMENTE APOS:**

```

## DEC-031 — o manifesto nomeia o rastreado divergente; o não rastreado continua anônimo

**Contexto.** A wo0048 decidiu «resumo, nunca listagem» no bloco de git, por dois motivos: ruído e
vazamento de nome de arquivo pessoal não rastreado. A regra funcionou, mas deixou sem resposta a
pergunta que o leitor do mount mais faz: *o arquivo que estou lendo é o commit, ou trabalho por
cima dele?* `1 modificado(s)` não diz qual.

**Decisão.** Nomear **apenas** os arquivos rastreados que (a) divergem do commit e (b) entraram no
achatamento. Não rastreado (`??`) e ignorado (`!!`) seguem fora, sem exceção.

**O que sustenta o corte.** Dos dois motivos da wo0048, o do vazamento **só vale para o não
rastreado** — e ali continua valendo inteiro. Para o rastreado que foi achatado ele não protege
coisa alguma: o nome já está na tabela do mesmo arquivo, poucas linhas acima. O motivo do ruído
some pela ordem de grandeza: são tipicamente 1 a 3 nomes, contra os 39 da tabela.

**Alternativa descartada — `mtime` por arquivo** (pedido do KCM na carta 01, item 2). Responde
«quando foi tocado», não «mudou»: `git checkout` carimba a hora do checkout em arquivo parado há
meses, e cópia com preservação de timestamp mantém data velha em arquivo recém-chegado. E cria um
dado que **autoriza a não ler** — que é o gesto que produziu a falha que o pedido tentava
consertar. O `git status` já sabe a resposta certa, de graça, e é dado de conteúdo. A recusa vai
argumentada na carta 02.

**Alternativa guardada — hash curto por arquivo.** Responde a pergunta vizinha («mudou desde a
geração anterior?»), que esta decisão só cobre em parte: arquivo alterado **e commitado** entre
duas gerações não aparece aqui, porque deixou de divergir. Fica com gatilho: volta quando uma
sessão precisar comparar duas gerações e esta linha não bastar. A regra que separa os dois
instrumentos, e que vale para qualquer um deles: **hash igual ao que já se leu JUSTIFICA pular a
releitura; data antiga apenas SUGERE.**

**Consequências.** `git_modified_paths` chama o git uma segunda vez em vez de alterar o retorno de
`git_snapshot`, que já tem seis testes em cima. O parser (`_modified_paths`) é puro e roda sem git
instalado. Em multi-fonte, o `rel` pode não ser relativo a `plan.root`; a interseção então não casa
e a linha não sai — falso negativo, nunca falso positivo.
```

## Edicao 6 — `meta/STATUS.md` · item 3 do backlog

**Ancora** (secao «Em aberto (produto)», item 3 inteiro — texto escrito pela wo0051):

```
3. **Responder a carta 01 do KCM** — falta só a carta 02, que o chat escreve depois desta WO
   aplicada. Item 1 **decidido e implementado** (DEC-030, wo0051: bloco de exceções). Item 3
   **entregue** (wo0050). Item 2 (`mtime` por arquivo) **em discussão**: o autor questionou a
   utilidade e o chat contrapôs uma coluna de **hash curto** — hash igual ao que já se leu
   *justifica* pular a releitura; `mtime` antigo só *sugere*. Decisão pendente na análise
   `meta/analises/260823-ANALISE-formato-do-manifesto.md`.
```

**Substituir por:**

```
3. **Escrever a carta 02 ao KCM** — os três itens da carta 01 estão fechados no código: item 1
   entregue (DEC-030, wo0051), item 3 entregue (wo0050) e item 2 **recusado com contraproposta
   entregue** (DEC-031, wo0053: nomear os rastreados divergentes, em vez do `mtime` pedido). A
   carta precisa levar a lógica inteira da recusa, não só o «não» — pedido explícito do autor em
   24/08. O hash curto ficou guardado com gatilho na DEC-031.
```

## Edicao 7 — `meta/CHANGELOG.md` · entrada em `[Não lançado]`

**Ancora** (primeiro item de `### Adicionado`, seja o da wo0052 ou o da wo0051, dependendo da
ordem — case o da **wo0051**, que existe nos dois casos):

```
- **O `_MANIFEST` avisa quais nomes chegam diferentes ao Projeto (wo0051, DEC-030).** Quando algum
```

**Inserir IMEDIATAMENTE ANTES** dessa linha:

```
- **O `_MANIFEST` diz QUAIS arquivos do mount não são o commit (wo0053, DEC-031).** Além da
  contagem, o cabeçalho passa a nomear os arquivos rastreados que divergem do commit **e** entraram
  no achatamento — a pergunta que quem lê o mount faz o tempo todo. Não rastreado continua sem
  aparecer: é ali que mora arquivo pessoal, e a recusa da wo0048 vale inteira. É a resposta ao item
  2 da carta 01 do KCM **no lugar** do `mtime` pedido: data diz «quando foi tocado», o `git status`
  diz «mudou».
- **O bloco de nomes previstos passa a carregar seu teste de falsificação (wo0053).** Uma frase diz
  ao leitor que, se o arquivo aparecer no Projeto com o nome da coluna 1, a regra de sanitização
  mudou e a previsão morreu. Pedido do autor ao aceitar a DEC-030: ficar esperto sem depender de
  vigilância.
```

---

## Fora de escopo

- **Hash por arquivo** (contraproposta 2): guardado com gatilho na DEC-031.
- **Listar não rastreados** — nunca, e a DEC-031 diz por quê.
- **`meta/IDEAS.md`** (wo0052) e **`meta/analises/`** (chat).
- **Nada de `flatdrop/cli.py`, `gui._build_cli_args`, `gui._generate_bat`, `gui._sources`**
  (DEC-020). A autorização que o autor deu para `cli.py` era da wo0052 e **não** se estende a esta.

## Armadilhas desta WO

- A Edição 2 substitui um bloco que **começa e termina em linhas que continuam existindo**
  (`if _status:` e `- **Modo de renomeação:**`). Confira que a linha do «Modo de renomeação» não
  ficou duplicada depois de aplicar.
- `_git` monta `git -C <root> <args>`; o `-c core.quotepath=false` da Edição 1 entra **como
  argumento**, antes do `status`. Se a saída vier com escapes octais (`\303\241`), o `-c` não pegou
  — reporte em vez de tratar o escape na mão.
- O teste `test_manifesto_nomeia_modificado_rastreado` depende de `b.md` **não** estar
  gitignorado. O `tmp_path` não tem `.gitignore` — se por algum motivo tiver, o teste vira falso
  verde.

---

## Depois de aplicar — conferência antes do commit

- [ ] `git diff` mostra exatamente: `flatdrop/core.py`, `tests/test_core.py`, `meta/DECISIONS.md`,
      `meta/STATUS.md`, `meta/CHANGELOG.md`.
- [ ] `python -m pytest -q` → **0 erros**, **118 testes** (111 + 7). Se a wo0052 ainda não tiver
      sido aplicada, são 116 — diga qual número saiu.
- [ ] **Smoke real, e é o melhor teste desta WO:** com a árvore suja (ela vai estar — você acabou
      de editar cinco arquivos), achate este próprio repositório e leia o cabeçalho do
      `_MANIFEST`. Esperado: a linha nova nomeando os arquivos que você acabou de mexer. Confira
      que **nenhum arquivo não rastreado** aparece nela.
- [ ] O bloco de exceções agora termina com a frase da falsificação.
- [ ] **Invariante DEC-020:** nenhum dos quatro caminhos protegidos foi tocado.

## Relatório de aplicação *(quem aplica preenche ao terminar)*

O que foi feito · o que fugiu do texto literal · arquivos tocados · resultado da suíte · o commit ·
**o push** (com o resultado real; se ficar pendente de confirmação, **volte e corrija este campo**
depois que ele sair — o relatório da wo0051 ficou afirmando «não empurrei» depois do push, e é ele
que a sessão seguinte lê). Grave o MESMO relatório em `../AAMMDD-HHMM-code-flatdrop.txt`.

## Commit — blocos separados, mensagem SEM acento

```
git add flatdrop\core.py tests\test_core.py meta\DECISIONS.md meta\STATUS.md meta\CHANGELOG.md meta\workorders\260824-wo0053-manifesto-fora-do-commit.md
```

```
git commit -m "feat(manifest): nomear os arquivos do mount que nao sao o commit" -m "A contagem dizia 1 modificado e nao dizia qual, entao quem le o mount nao sabia se o arquivo era o commit ou trabalho por cima. Passa a nomear so o rastreado que entrou no achatamento; nao rastreado continua anonimo, que e onde a recusa da wo0048 protege de fato. Resposta ao item 2 da carta 01 do KCM no lugar do mtime pedido. DEC-031."
```

```
git push
```
