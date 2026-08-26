# WO 0055 — a contagem de nomes previstos sobe para o cabeçalho do `_MANIFEST`

> **Tipo:** mista — CODIGO (`flatdrop/core.py`, `tests/test_core.py`) + REGISTRO
> (`meta/CHANGELOG.md`, `meta/STATUS.md`).
> **Config sugerida:** modelo intermediario, `/effort` medio.
> **Pre-requisito:** wo0054 aplicada e empurrada, **118 testes verdes**.
> **Depende de:** wo0054 (so pela ordem do CHANGELOG; nao ha dependencia de codigo).
> **Base:** carta 03 do KCM (2026-08-25), secao 1 — resposta a pergunta unica da carta 02, com o
> teste real feito por eles. Aceita pelo autor no mesmo dia.
> **Ancoras lidas em:** *(trecho literal lido NESTE turno para escrever cada ancora)*
> - `flatdrop/core.py`, `write_manifest` — cabecalho:
>   `lines.append(f"- **Arquivos:** {len(plan.files)}")` seguido de `- **Tamanho total:**`.
> - `flatdrop/core.py`, fim de `write_manifest` — comentario `# Bloco de excecoes (DEC-030): ...`
>   seguido da compreensao `divergentes = [...]` e do `if divergentes:`.
> - `tests/test_core.py` — duas ultimas linhas, no teste `test_assinatura_continua_na_primeira_linha`.
> - `meta/CHANGELOG.md` — primeiro item de `### Adicionado` em `[Não lançado]`.
> - `meta/STATUS.md` — primeira linha da secao «Qualidade / testes».
> **Idempotencia:** procure `Nomes que chegam diferentes ao Projeto:` (com dois pontos, no
> cabecalho — nao confundir com o titulo do bloco, que diz `DIFERENTES ao Projeto (`). Se ja
> existir, **PULE**.

> **Canal dos meta neste ciclo = CODE** (`CHANGELOG`, `STATUS`).

---

## 1. Por que

O KCM respondeu a pergunta unica da carta 02 com o teste real, e a resposta desmentiu a nossa
hipotese sem derrubar o desenho. Na ordem em que aconteceu do lado deles:

1. abriram o turno lendo **as trinta primeiras linhas** do manifesto — que e o ritual deles;
2. **nao viram o bloco de excecoes**, que fica depois de uma tabela de 53 linhas;
3. so o acharam com `grep`, indo procura-lo de proposito para conferir a carta 02.

**O bloco chegou por busca, não por leitura.** E a causa **nao** e ele estar fora da tabela — o
argumento dos 8% x 92% que sustenta a DEC-030 continua de pe, e eles dizem explicitamente que nao
pedem mais a terceira coluna. **Quem falha e a posicao:** o dado existe num lugar onde o ritual de
leitura nao passa.

**A correcao e uma linha no cabecalho, com a CONTAGEM — nao a lista.** Contagem e dado de LOTE, e
lote e sobre o que o cabecalho fala; o detalhe continua na excecao, onde a DEC-030 o pos. O mesmo
criterio que separou as duas coisas la separa as duas aqui.

**E ela sai SEMPRE, inclusive `0`.** Pelo mesmo principio que nos aplicamos ao «sincronizado» na
wo0050: *ausencia de aviso nao deve ser lida como estado*. Um `0` diz que a previsao foi avaliada e
nao teve caso; a omissao nao diz nada — e foi justamente a omissao que fez o bloco se perder.

---

## Edicao 1 — `flatdrop/core.py` · a contagem entra no cabecalho

**Ancora** (dentro de `write_manifest`, no bloco de metadados):

```
    lines.append(f"- **Arquivos:** {len(plan.files)}")
    lines.append(f"- **Tamanho total:** {human_size(plan.total_bytes)}")
```

**Substituir por:**

```
    lines.append(f"- **Arquivos:** {len(plan.files)}")
    # Contagem no cabecalho (wo0055): o bloco de excecoes da DEC-030 vive no FIM do arquivo, depois
    # da tabela, e quem le so o cabecalho — que e o ritual — nao chega la. Medido pelo KCM em
    # 25/08: leram as 30 primeiras linhas, nao viram o bloco, e so o acharam com grep. A contagem e
    # dado de LOTE, que e do que o cabecalho fala; o detalhe continua na excecao. Sai SEMPRE,
    # inclusive `0`: zero diz que a previsao foi avaliada e nao teve caso, e a omissao nao diz nada
    # — mesmo principio do "sincronizado" da wo0050.
    divergentes = [(f.target, project_upload_name(f.target)) for f in plan.files
                   if project_upload_name(f.target) != f.target]
    lines.append(
        f"- **Nomes que chegam diferentes ao Projeto:** {len(divergentes)}"
        + (" (detalhe no fim deste arquivo)" if divergentes else "")
    )
    lines.append(f"- **Tamanho total:** {human_size(plan.total_bytes)}")
```

## Edicao 2 — `flatdrop/core.py` · o fim do arquivo reaproveita a lista

**Ancora** (fim de `write_manifest`, o comentario e a compreensao):

```
    # Bloco de excecoes (DEC-030): a tabela acima descreve o DISCO; o Projeto renomeia no upload
    # e a busca pelo nome declarado voltava vazia — ausencia indistinguivel de "nao subiu". Fica
    # FORA da tabela de proposito: vale para poucos arquivos (3 de 38 aqui) e e previsao sobre
    # software de terceiro. Coluna gastaria celula vazia em 92% das linhas para servir 8%.
    divergentes = [(f.target, project_upload_name(f.target)) for f in plan.files
                   if project_upload_name(f.target) != f.target]
    if divergentes:
```

**Substituir por:**

```
    # Bloco de excecoes (DEC-030): a tabela acima descreve o DISCO; o Projeto renomeia no upload
    # e a busca pelo nome declarado voltava vazia — ausencia indistinguivel de "nao subiu". Fica
    # FORA da tabela de proposito: vale para poucos arquivos (3 de 39 aqui) e e previsao sobre
    # software de terceiro. Coluna gastaria celula vazia em 92% das linhas para servir 8%.
    # `divergentes` ja foi montado la em cima, para a contagem do cabecalho (wo0055) — uma passada
    # so, e os dois lugares nunca discordam.
    if divergentes:
```

## Edicao 3 — `tests/test_core.py` · quatro testes novos, no fim do arquivo

**Ancora** (as duas ultimas linhas do arquivo):

```
    assert texto.splitlines()[0] == C.MANIFEST_SIGNATURE
    assert core.is_our_folder(res.dest)
```

**Inserir IMEDIATAMENTE APOS:**

```


# --- contagem de nomes previstos no cabecalho (wo0055) ---

def _manifesto_de(tmp_path, arquivos: dict[str, str]) -> str:
    """Gera um manifesto a partir de {nome: conteudo} e devolve o texto."""
    origem = tmp_path / "src"
    origem.mkdir()
    for nome, conteudo in arquivos.items():
        (origem / nome).write_text(conteudo, encoding="utf-8")
    cfg = core.ScanConfig()
    plan = core.make_plan(origem, cfg)
    res = core.execute_plan(plan, tmp_path / "out", cfg)
    return list(res.dest.glob("_MANIFEST*.md"))[0].read_text(encoding="utf-8")


def test_cabecalho_conta_os_nomes_previstos(tmp_path):
    """Havendo caso, o cabecalho traz a contagem e aponta para o fim do arquivo."""
    texto = _manifesto_de(tmp_path, {"dados.v1.json": "{}\n", "a.md": "x\n"})
    assert "- **Nomes que chegam diferentes ao Projeto:** 1 (detalhe no fim deste arquivo)" in texto


def test_cabecalho_diz_zero_em_voz_alta(tmp_path):
    """Sem caso, a linha SAI MESMO ASSIM, com 0 — omissao nao e estado (wo0050, wo0055)."""
    texto = _manifesto_de(tmp_path, {"a.md": "x\n"})
    assert "- **Nomes que chegam diferentes ao Projeto:** 0" in texto
    assert "detalhe no fim" not in texto      # nao aponta para um bloco que nao existe
    assert "chegam DIFERENTES" not in texto   # e o bloco continua ausente


def test_contagem_do_cabecalho_bate_com_o_bloco(tmp_path):
    """A contagem e a minitabela saem da MESMA lista: nunca podem discordar."""
    texto = _manifesto_de(tmp_path, {"a.b.json": "{}\n", "c.d.json": "{}\n", "e.md": "x\n"})
    assert "Nomes que chegam diferentes ao Projeto:** 2" in texto
    assert "Nomes que chegam DIFERENTES ao Projeto (2)" in texto


def test_contagem_vem_antes_da_tabela(tmp_path):
    """A linha tem de estar no CABECALHO — o ponto inteiro da wo0055 e o alcance."""
    texto = _manifesto_de(tmp_path, {"dados.v1.json": "{}\n"})
    assert texto.index("Nomes que chegam diferentes ao Projeto:") < texto.index("| Caminho original |")
```

## Edicao 4 — `meta/CHANGELOG.md` · entrada em `[Não lançado]`

**Ancora** (primeiro item de `### Adicionado`, escrito pela wo0053):

```
- **O `_MANIFEST` diz QUAIS arquivos do mount não são o commit (wo0053, DEC-031).** Além da
```

**Inserir IMEDIATAMENTE ANTES** dessa linha:

```
- **O cabeçalho do `_MANIFEST` conta os nomes que chegam diferentes ao Projeto (wo0055).** Uma
  linha, sempre presente — inclusive com `0` —, apontando para o bloco de exceções quando houver
  caso. Motivo, medido pelo KCM em 25/08: o bloco da DEC-030 fica depois da tabela, e quem lê só o
  cabeçalho não chega lá — eles só o encontraram com `grep`, procurando de propósito. **O bloco
  chegou por busca, não por leitura.** A tabela e o bloco não mudam: o que subiu foi a contagem,
  que é dado de lote. O `0` sai em voz alta pelo mesmo princípio do «sincronizado» da wo0050 —
  ausência de aviso não deve ser lida como estado.
```

## Edicao 5 — `meta/STATUS.md` · a contagem de testes

**Ancora** (primeira linha da secao «Qualidade / testes»):

```
- **118 testes verdes** em 2026-08-24 (92 → 100 → 109 → 111 → 118, um degrau por WO). Rodar da
  raiz: `pytest -q` (o `conftest.py` resolve o import — FIX-005) ou `python -m pytest -q`.
```

**Substituir por:**

```
- **122 testes verdes** em 2026-08-25 (92 → 100 → 109 → 111 → 118 → 122, um degrau por WO). Rodar
  da raiz: `pytest -q` (o `conftest.py` resolve o import — FIX-005) ou `python -m pytest -q`.
```

> **`118` aparece TRÊS vezes neste arquivo** — medido em 25/08: linha 11 (nota de revisão), linha
> 45 (situação geral) e linha 83 (esta edição). Troque as três; a edição acima cobre só a terceira.
> **Declare o número que você trocou no relatório** — se não forem 3, a divergência é o achado.
> *(Regra que a wo0054 acabou de acrescentar à `wrap/SKILL.md`: número mudado se procura no arquivo
> inteiro, porque a cópia esquecida passa a mentir. O campo `Commit` deste mesmo arquivo já ficou 20
> dias apontando hash errado por isso.)*

---

## Fora de escopo

- **A tabela e o bloco de exceções não mudam** — nem a forma, nem a posição, nem o texto. A DEC-030
  continua valendo inteira; esta WO só resolve o **alcance**.
- **Nada do merge do KCM** (fases 2 e 3) entra aqui.
- Nenhum caminho da DEC-020.

## Armadilhas desta WO

- **Duas variáveis com o mesmo nome, agora numa só.** Se a Edição 1 entrar e a Edição 2 não, o
  `divergentes` será montado duas vezes — funciona, mas é a metade errada do trabalho. Se a Edição
  2 entrar e a 1 não, `write_manifest` quebra com `NameError` no primeiro achatamento com caso, e
  a suíte pega. **Aplique as duas ou nenhuma.**
- A âncora da Edição 2 tem **quatro linhas de comentário + duas de compreensão + o `if`**. Copie o
  bloco inteiro; o texto novo muda «3 de 38» para «3 de 39» dentro do comentário, de propósito.
- `test_core.py` já tem um helper por perto para montar plano; o novo `_manifesto_de` é local desta
  seção. Se colidir com nome existente, **PARE e reporte** — não renomeie por conta.

---

## Depois de aplicar — conferência antes do commit

- [ ] `git diff` mostra exatamente: `flatdrop/core.py`, `tests/test_core.py`, `meta/CHANGELOG.md`,
      `meta/STATUS.md`.
- [ ] `python -m pytest -q` → **0 erros**, **122 testes** (118 + 4).
- [ ] `grep -c "divergentes = \[" flatdrop/core.py` → **1**. Dois significa que a Edição 2 não
      pegou. *(Este termo é citado por duas edições desta WO, mas só uma o deixa no arquivo final —
      esperado = 1.)*
- [ ] **Smoke real, e é o teste que importa:** achate este próprio repositório e leia **só as 12
      primeiras linhas** do `_MANIFEST` gerado. A linha tem de estar lá, com **3**. Depois achate
      uma pasta sem dotfile nem ponto interno e confirme que sai **0**, sem o «detalhe no fim».
      **Prova de vida:** o caso `0` só significa alguma coisa depois de você ter visto o caso `3`.
- [ ] Quantas ocorrências de `118` você trocou no `meta/STATUS.md`? Diga o número no relatório.
- [ ] **Invariante DEC-020:** nada dos quatro caminhos protegidos.

## Relatório de aplicação *(quem aplica preenche ao terminar)*

O que foi feito · o que fugiu do texto literal · arquivos tocados · resultado da suíte · o commit ·
**o push, com o resultado real** — escrito DEPOIS de o push estar resolvido. Grave o MESMO
relatório em `../AAMMDD-HHMM-code-flatdrop.txt`.

## Commit — blocos separados, mensagem SEM acento

```
git add flatdrop\core.py tests\test_core.py meta\CHANGELOG.md meta\STATUS.md meta\workorders\260825-wo0055-manifesto-linha-ponteiro.md
```

```
git commit -m "feat(manifest): contar no cabecalho os nomes que chegam diferentes" -m "O bloco de excecoes fica depois da tabela e quem le so o cabecalho nao chega la: o KCM mediu isso e so achou o bloco com grep. Sobe a CONTAGEM, que e dado de lote; o detalhe continua na excecao. A linha sai sempre, inclusive com zero, pelo mesmo principio do sincronizado da wo0050."
```

```
git push
```
