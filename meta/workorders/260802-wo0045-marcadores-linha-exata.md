# WO 0045 — marcadores do bloco por LINHA EXATA, e recusa de arquivo ambíguo

> **Tipo:** CÓDIGO (core + GUI + testes).
> **Config sugerida:** modelo intermediário, `/effort` médio.
> **Pré-requisito:** 0.14.0, commit `6466578`, suíte verde (79), árvore limpa.
> **Base:** `meta/specs/260802-spec-anatomia-flatdropignore.md` (regras 3 e 5) e o passo 0 de
> `meta/analises/260728-ANALISE-bloco-gerenciado-vs-manual.md`.
> **Depende de:** nada. É deliberadamente **isolada** das wo0046/0047 — corrige perda de dado e
> pode ser aplicada e commitada sozinha.
> **Âncora semântica:** se um trecho-âncora não bater EXATAMENTE, **PARE e reporte**.
> **Idempotência:** se `_split_managed` já existir em `flatdrop/core.py`, **PULE** a WO inteira e
> diga no relatório.

> **Canal dos meta neste ciclo = CHAT.** Não faça append em `meta/*.md`.

---

## 1. Por que

`build_flatdropignore` localiza o bloco com `existing_text.split(MARK)` — **substring, primeira
ocorrência**. Um arquivo que *mencione* o marcador num comentário (documentando a própria
convenção, que é o uso mais natural do mundo) faz o gerador cortar na menção: o bloco novo é
injetado **no meio da linha de comentário**, o bloco antigo sobra no fim, e o resto da frase
truncada perde o `#` e **vira padrão ativo**.

**Medido em 2026-08-02** contra o código da 0.14.0, com o `.flatdropignore` deste repo entregue em
01/08: 35 linhas viraram 42, com dois blocos. O autor já havia disparado o mesmo defeito em outro
projeto, sem diagnóstico. É perda de dado silenciosa — a única operação irreversível do editor.

## 2. Contexto factual

- **Medido:** as únicas ocorrências dos marcadores no código são `FLATDROP_EDITOR_MARK_A/B`
  (`core.py` ~462) e o trecho final de `build_flatdropignore`. A GUI não localiza o bloco por
  conta própria: `gui._save` (linha ~417) só lê o arquivo e chama a core.
- **Medido:** `_read_ignore_lines` devolve as linhas cruas, comentários inclusive — então o corte
  por linha é possível sem tocar na leitura de ignores.
- **Deduzido:** nenhum teste atual cobre marcador citado em comentário (a suíte passa verde com o
  defeito presente).

---

## Edição 1 — `flatdrop/core.py` · função nova `_split_managed`

**Âncora** *(primeira linha da definição de `build_flatdropignore`)*:

```
def build_flatdropignore(root, cfg: ScanConfig, wants: dict[str, bool],
```

**Inserir IMEDIATAMENTE ANTES** *(mantendo uma linha em branco de separação depois do bloco novo)*:

```
class FlatdropIgnoreAmbiguo(ValueError):
    """O arquivo tem mais de um bloco gerenciado — reescrever destruiria conteudo.

    Levantado em vez de adivinhar qual bloco vale. A anatomia normativa (spec de
    2026-08-02) admite UM bloco: dois sao ambiguidade, e o editor recusa salvar.
    """


def _split_managed(text: str) -> tuple[str, str, str]:
    """(pre, bloco, pos) de um .flatdropignore, cortando pelos marcadores.

    O marcador e uma LINHA cujo conteudo, sem espacos, e igual ao marcador — nunca uma
    substring no meio de um texto. A versao antiga usava ``text.split(MARK)``, entao um
    comentario que CITASSE o marcador (documentando a propria convencao) fazia o corte
    acontecer no comentario: o bloco novo entrava no meio da frase, o bloco antigo sobrava
    no fim e o resto da linha truncada virava padrao ativo. Medido em 2026-08-02.

    Sem bloco: devolve (texto, "", ""). Mais de um marcador de abertura ou de fechamento:
    levanta ``FlatdropIgnoreAmbiguo`` — recusar e melhor que destruir.
    """
    linhas = text.splitlines()
    abre = [i for i, ln in enumerate(linhas) if ln.strip() == FLATDROP_EDITOR_MARK_A]
    fecha = [i for i, ln in enumerate(linhas) if ln.strip() == FLATDROP_EDITOR_MARK_B]
    if len(abre) > 1 or len(fecha) > 1:
        raise FlatdropIgnoreAmbiguo(
            f"{len(abre)} marcadores de abertura e {len(fecha)} de fechamento; "
            "esperado 1 de cada. Deixe um unico bloco no fim do arquivo e salve de novo."
        )
    if not abre or not fecha or fecha[0] < abre[0]:
        return text, "", ""
    pre = "\n".join(linhas[:abre[0]])
    bloco = "\n".join(linhas[abre[0]:fecha[0] + 1])
    pos = "\n".join(linhas[fecha[0] + 1:])
    return pre, bloco, pos
```

## Edição 2 — `flatdrop/core.py` · usar o corte por linha na escrita

**Âncora** *(trecho final de `build_flatdropignore`)*:

```
    if existing_text and FLATDROP_EDITOR_MARK_A in existing_text and FLATDROP_EDITOR_MARK_B in existing_text:
        pre = existing_text.split(FLATDROP_EDITOR_MARK_A)[0].rstrip("\n")
        pos = existing_text.split(FLATDROP_EDITOR_MARK_B, 1)[1].lstrip("\n")
        return "\n".join(p for p in (pre, managed, pos) if p) + "\n"
    if existing_text and existing_text.strip():
        return existing_text.rstrip("\n") + "\n\n" + managed + "\n"
    return managed + "\n"
```

**Substituir por:**

```
    if existing_text and existing_text.strip():
        pre, bloco, pos = _split_managed(existing_text)
        if bloco:
            pre, pos = pre.rstrip("\n"), pos.strip("\n")
            return "\n".join(p for p in (pre, managed, pos) if p) + "\n"
        return existing_text.rstrip("\n") + "\n\n" + managed + "\n"
    return managed + "\n"
```

> `pos` sai com `strip("\n")` nos dois lados de propósito: a versão antiga usava `lstrip` e
> deixava a quebra do fim acumular **uma linha em branco por salvamento** (medido). O bloco
> continua na posição em que estava — movê-lo para o fim é a wo0046, não esta.

## Edição 3 — `flatdrop/gui.py` · o editor recusa salvar arquivo ambíguo

**Âncora** *(corpo de `FlatDropIgnoreEditor._save`)*:

```
        text = core.build_flatdropignore(self.root_dir, self.cfg, wants,
                                         existing_text=existing, locks=self.locks)
        target.write_text(text, encoding="utf-8")
```

**Substituir por:**

```
        try:
            text = core.build_flatdropignore(self.root_dir, self.cfg, wants,
                                             existing_text=existing, locks=self.locks)
        except core.FlatdropIgnoreAmbiguo as err:
            # Recusa consciente: reescrever um arquivo com dois blocos apagaria conteudo do
            # autor. A janela fica aberta para ele corrigir o arquivo e tentar de novo.
            messagebox.showerror(
                "FlatDrop — .flatdropignore ambiguo",
                f"{target}\n\n{err}\n\nNada foi salvo.")
            return
        target.write_text(text, encoding="utf-8")
```

## Edição 4 — `tests/test_core.py` · três testes novos

**Inserir ao FIM do arquivo:**

```


def test_marcador_citado_em_comentario_nao_corta_o_bloco(tmp_path):
    """Marcador mencionado num comentario nao pode ser confundido com o bloco (wo0045)."""
    (tmp_path / "logs").mkdir()
    (tmp_path / "logs" / "a.md").write_text("x\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("x\n", encoding="utf-8")
    texto = (
        '# Regra vai DENTRO do bloco "# >>> flatdrop-editor" e nada depois do "# <<<".\n'
        "logs/*\n"
        "# >>> flatdrop-editor\n"
        "# (sem alteracoes)\n"
        "# <<<\n"
    )
    (tmp_path / ".flatdropignore").write_text(texto, encoding="utf-8")
    out = core.build_flatdropignore(tmp_path, core.ScanConfig(), {}, existing_text=texto)
    assert out.count(core.FLATDROP_EDITOR_MARK_A) == 2   # o do comentario + o bloco real
    assert out.splitlines()[0] == texto.splitlines()[0]  # comentario intacto, nao cortado
    assert out.splitlines()[1] == "logs/*"


def test_dois_blocos_recusa_salvar(tmp_path):
    """Arquivo ambiguo para o salvamento em vez de adivinhar qual bloco vale (wo0045)."""
    (tmp_path / "README.md").write_text("x\n", encoding="utf-8")
    texto = ("# >>> flatdrop-editor\n# (sem alteracoes)\n# <<<\n"
             "# >>> flatdrop-editor\n# (sem alteracoes)\n# <<<\n")
    (tmp_path / ".flatdropignore").write_text(texto, encoding="utf-8")
    with pytest.raises(core.FlatdropIgnoreAmbiguo):
        core.build_flatdropignore(tmp_path, core.ScanConfig(), {}, existing_text=texto)


def test_salvar_duas_vezes_nao_acumula_linha_em_branco(tmp_path):
    """Estabilidade TEXTUAL, nao so das regras: o lstrip antigo deixava o arquivo crescer."""
    (tmp_path / "logs").mkdir()
    (tmp_path / "logs" / "a.md").write_text("x\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("x\n", encoding="utf-8")
    texto = "# cabecalho\nlogs/*\n# >>> flatdrop-editor\n# (sem alteracoes)\n# <<<\n"
    (tmp_path / ".flatdropignore").write_text(texto, encoding="utf-8")
    cfg = core.ScanConfig()
    t1 = core.build_flatdropignore(tmp_path, cfg, {}, existing_text=texto)
    (tmp_path / ".flatdropignore").write_text(t1, encoding="utf-8")
    t2 = core.build_flatdropignore(tmp_path, cfg, {}, existing_text=t1)
    assert t1 == t2
```

> **Medido:** `tests/test_core.py` já importa `pytest` — nenhum import novo é necessário aqui.

---

## Fora de escopo

- **Não mova o bloco para o fim** e **não mude a base de comparação** — é a wo0046, e misturar as
  duas torna impossível saber qual delas quebrou um teste.
- **Não corrija o `.flatdropignore` da raiz por código.** O autor aplica a versão nova à mão.
- **Não mexa na leitura de ignores** (`_collect_ignore_lines`): a wo0046 é que ganha o parâmetro.

## Armadilhas desta WO

- **`FLATDROP_EDITOR_MARK_B` é `"# <<<"`** — curto e comum. Por isso a comparação é por linha
  inteira (`ln.strip() == MARK`), nunca `in`.
- **O primeiro teste espera DOIS marcadores de abertura no resultado** — está certo: um é a
  citação no comentário, o outro é o bloco. É exatamente o caso que o código antigo destruía.
- **Não "conserte" o teste de ambiguidade** para aceitar o arquivo: recusar é o comportamento
  pedido.
- Os arquivos estão em **LF**; cole os blocos como estão, sem reindentar.

---

## Depois de aplicar — conferência antes do commit

- [ ] `git diff` mostra só `flatdrop/core.py`, `flatdrop/gui.py`, `tests/test_core.py`.
- [ ] `python -m pytest -q` passa: **79 + 3 = 82**. Se algum teste ANTIGO do editor quebrar,
      **PARE e reporte** — significa que algum deles dependia do corte por substring.
- [ ] **Invariante DEC-020:** nenhum dos quatro pontos protegidos foi tocado.
- [ ] **Smoke manual (a suíte não cobre tkinter):** abrir o editor num projeto qualquer, salvar
      sem mexer em nada, conferir que o arquivo não ganhou linha em branco no fim; depois,
      duplicar o bloco à mão e conferir que o salvamento mostra o erro e **não escreve nada**.

## Relatório de aplicação

O que foi feito · desvios · arquivos tocados · resultado da suíte · o commit. Grave o MESMO
relatório em `../AAMMDD-HHMM-code-flatdrop.txt`. Diga também se precisou acrescentar `import
pytest` e se algum teste antigo do editor precisou de ajuste.

## Commit — blocos separados, mensagem SEM acento

```
git add flatdrop/core.py flatdrop/gui.py tests/test_core.py
```

```
git commit -m "fix(ignore): localizar o bloco gerenciado por linha exata (wo0045)" -m "O corte por substring confundia uma mencao ao marcador num comentario com o proprio bloco: injetava o bloco no meio da frase, deixava o antigo no fim e a linha truncada virava padrao ativo. Agora o marcador e uma linha inteira, arquivo com dois blocos recusa salvar em vez de adivinhar, e o pos deixou de acumular linha em branco a cada salvamento. 3 testes novos."
```

```
git push
```
