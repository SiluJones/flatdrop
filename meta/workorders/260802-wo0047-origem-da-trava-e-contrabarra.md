# WO 0047 — dizer DE ONDE vem a trava, e denunciar padrão com contrabarra

> **Tipo:** CÓDIGO (core + GUI + testes).
> **Config sugerida:** modelo intermediário, `/effort` médio.
> **Pré-requisito:** wo0045 e wo0046 aplicadas e commitadas; suíte em 86 verdes.
> **Base:** `meta/specs/260802-spec-anatomia-flatdropignore.md`, critérios 8 e 9 · passo 4 da
> análise · nota do autor de 2026-08-01 (`260801-1835.txt`).
> **Depende de:** wo0046 (usa `_split_managed`, já criado na wo0045).
> **Âncora semântica:** se um trecho-âncora não bater EXATAMENTE, **PARE e reporte**.
> **Idempotência:** se `backslash_patterns` já existir em `flatdrop/core.py`, **PULE** a WO.

> **Canal dos meta neste ciclo = CHAT.** Não faça append em `meta/*.md`.

---

## 1. Por que

Duas falhas silenciosas do mesmo tipo: a pessoa olha para a tela, a tela não mente exatamente, mas
também não conta o que ela precisa saber.

**(a) Trava sem origem.** A coluna «Arquivo novo» mostra `travada (git)` quando a pasta está
escondida pelo `.gitignore` — para o autor não achar que o editor travou sozinho. Mas pasta
fechada por uma **linha manual do `.flatdropignore`** aparece igual a uma travada por ele mesmo.
Depois da wo0046 isso fica pior, não melhor: agora que destravar funciona de verdade sobre linha
manual, o autor precisa saber que aquela trava não é dele antes de mexer.

**(b) Contrabarra que não casa nada.** `!static\assets\...\_index.json` não ignora nem resgata
nada: em sintaxe `.gitignore` a contrabarra é caractere de **escape**, não separador. O arquivo
sobe achando que foi ignorado, e a pessoa descobre arrastando arquivo à mão. Aconteceu com o autor
em 2026-08-01, em outro projeto.

## 2. Contexto factual

- **Medido (2026-08-02):** o gerador do FlatDrop **não** produz contrabarra — `_walk_leaves` monta
  todo caminho com `as_posix()` e f-string com `/` (`core.py` ~526/530/536), e a GUI só escreve o
  arquivo por `core.build_flatdropignore` (`gui.py` ~421). As linhas com `\` são sempre de edição
  manual (humana ou de outra ferramenta). Logo: **a correção é avisar, não normalizar** — e é por
  isso que ela só faz sentido agora, depois de a wo0046 ensinar o gerador a enxergar o que está
  fora do bloco.
- **Medido, registrado na análise:** `source(rel, is_dir=True)` devolve `""` para pasta fechada por
  `pasta/*` — a forma `/*` de propósito não casa a pasta como diretório (DEC-025/DEC-027). Por
  isso o rótulo novo usa a sonda de **arquivo inexistente** (`FLATDROP_PROBE`), a mesma que a
  trava já usa, e não a sonda de diretório.
- **Deduzido:** normalizar `\` para `/` calado mudaria a semântica de um arquivo que o git também
  lê. Fora de escopo por decisão da spec.

---

## Edição 1 — `flatdrop/core.py` · função nova `backslash_patterns`

**Âncora** *(primeira linha da definição de `rules_after_block`, criada na wo0046)*:

```
def rules_after_block(text: str) -> list[str]:
```

**Inserir IMEDIATAMENTE ANTES:**

```
def backslash_patterns(root, cfg: ScanConfig) -> list[tuple[str, str]]:
    """(arquivo, linha) de todo padrao escrito com contrabarra nos .flatdropignore da arvore.

    Sintaxe .gitignore usa SO barra normal: a contrabarra e caractere de escape, nao
    separador de caminho. "pasta\\arquivo.json" nao casa nada — e o arquivo sobe ao mount
    achando que foi ignorado. E falha silenciosa: ninguem ve a regra deixar de valer.

    So linha de REGRA conta (comentario e linha vazia, nao), e so o .flatdropignore — o
    .gitignore e do git e nao cabe a esta ferramenta opinar sobre ele. A ferramenta AVISA e
    aponta a linha; corrigir e da pessoa, porque trocar "\\" por "/" caladamente mudaria a
    semantica de um arquivo que outras ferramentas tambem leem.
    """
    achados: list[tuple[str, str]] = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = [d for d in dirnames if d not in cfg.dir_ignores]
        for nome in C.FLATDROPIGNORE_NAMES:
            if nome not in filenames:
                continue
            alvo = Path(dirpath) / nome
            rel = alvo.relative_to(root).as_posix()
            for ln in _read_ignore_lines(alvo):
                if ln.strip() and not ln.lstrip().startswith("#") and "\\" in ln:
                    achados.append((rel, ln.strip()))
            break  # mesma precedencia de _collect_ignore_lines: o primeiro nome vence
    return achados
```

## Edição 2 — `flatdrop/gui.py` · rótulo `travada (manual)`

**Âncora** *(corpo de `FlatDropIgnoreEditor._lock_txt`)*:

```
        de_git = self.source(rel, True) == "gitignore"
        if fechada:
            return "travada (git)" if de_git and rel not in self.locks else _LOCK_TXT[True]
        return "liberada" if de_git else _LOCK_TXT[False]
```

**Substituir por:**

```
        # De onde veio a trava. A sonda e de ARQUIVO INEXISTENTE, nao de diretorio: a forma
        # "pasta/*" (DEC-025) nao casa a pasta como diretorio, entao source(rel, True)
        # devolve "" justamente nos casos que interessam aqui.
        origem = self.source(f"{rel}/{core.FLATDROP_PROBE}", False)
        if fechada:
            if rel in self.locks:                 # o autor acabou de fechar: e dele
                return _LOCK_TXT[True]
            if origem == "gitignore":
                return "travada (git)"
            if origem == "flatdropignore":
                return "travada (manual)"
            return _LOCK_TXT[True]
        return "liberada" if origem == "gitignore" else _LOCK_TXT[False]
```

> Depois da wo0046 o rótulo tem consequência prática: `travada (manual)` avisa que destravar vai
> emitir um `!pasta/*` para vencer uma linha que o autor escreveu — e não apagar essa linha.

## Edição 3 — `flatdrop/gui.py` · avisar sobre contrabarra ao abrir o editor

**Âncora** *(em `FlatDropIgnoreEditor.__init__`)*:

```
        self.base_in, self.source = self.probes
```

**Inserir IMEDIATAMENTE APÓS:**

```
        # Aviso na ABERTURA, nao no salvamento: a pessoa veio aqui justamente para decidir o
        # que sobe, e uma regra que nao casa nada torna a tela mentirosa antes de qualquer
        # clique. Nao bloqueia — o arquivo continua utilizavel.
        self._avisar_contrabarra()
```

E, **inserir IMEDIATAMENTE ANTES** da âncora *(definição de `FlatDropIgnoreEditor._save`)*:

```
    def _save(self):
```

o método novo:

```
    def _avisar_contrabarra(self) -> None:
        """Denuncia padrao com "\\" nos .flatdropignore da arvore — ele nao casa nada."""
        achados = core.backslash_patterns(self.root_dir, self.cfg)
        if not achados:
            return
        amostra = "\n".join(f"  {arq}: {ln}" for arq, ln in achados[:10])
        extra = f"\n  ... (+{len(achados) - 10})" if len(achados) > 10 else ""
        messagebox.showwarning(
            "FlatDrop — padrao com contrabarra",
            "Sintaxe .flatdropignore usa SO barra normal ('/'). A contrabarra e caractere "
            "de escape, entao estas linhas NAO casam nada e o arquivo sobe assim mesmo:\n\n"
            f"{amostra}{extra}\n\nTroque '\\' por '/' nessas linhas.")
```

## Edição 4 — `tests/test_core.py` · dois testes novos

**Inserir ao FIM do arquivo:**

```


def test_backslash_patterns_denuncia_linha_manual(tmp_path):
    """Padrao com contrabarra nao casa nada e precisa ser apontado (wo0047)."""
    (tmp_path / "static").mkdir()
    (tmp_path / "static" / "a.json").write_text("x\n", encoding="utf-8")
    (tmp_path / ".flatdropignore").write_text(
        "# comentario com \\ nao conta\n"
        "static/*\n"
        "!static\\a.json\n",
        encoding="utf-8")
    achados = core.backslash_patterns(tmp_path, core.ScanConfig())
    assert achados == [(".flatdropignore", "!static\\a.json")]


def test_backslash_patterns_vazio_quando_tudo_certo(tmp_path):
    """Arquivo bem escrito nao gera aviso — o aviso so aparece quando ha o que consertar."""
    (tmp_path / "static").mkdir()
    (tmp_path / "static" / "a.json").write_text("x\n", encoding="utf-8")
    (tmp_path / ".flatdropignore").write_text("static/*\n!static/a.json\n", encoding="utf-8")
    assert core.backslash_patterns(tmp_path, core.ScanConfig()) == []
```

---

## Fora de escopo

- **Normalizar `\` para `/`.** A ferramenta avisa e aponta; quem edita é a pessoa (decisão da spec).
- **Avisar fora do editor.** Levar o aviso ao fluxo principal (pré-visualizar/executar) esbarra em
  `flatdrop/cli.py`, que é **protegido pelo DEC-020**. Fica como decisão separada; hoje o editor é
  onde o autor vai justamente quando desconfia do arquivo.
- **Opinar sobre o `.gitignore`.** Só os `.flatdropignore` são varridos.

## Armadilhas desta WO

- **A edição 3 tem duas inserções**, uma em `__init__` e um método novo antes de `_save`. Aplicar
  só a chamada dá `AttributeError` no primeiro uso.
- **No teste, `"!static\\a.json"` em código Python é a string com UMA contrabarra** — é isso
  mesmo. Não "conserte" para barra normal.
- **`_LOCK_TXT[True]` continua sendo o rótulo padrão** (`"travada"`) para trava do próprio autor:
  o novo rótulo só entra quando a trava vem de fora.
- Não confunda `FLATDROP_PROBE` (arquivo inexistente) com sonda de diretório: usar a de diretório
  é exatamente o bug que a análise registrou.

---

## Depois de aplicar — conferência antes do commit

- [ ] `git diff` mostra só `flatdrop/core.py`, `flatdrop/gui.py`, `tests/test_core.py`.
- [ ] `python -m pytest -q`: **86 + 2 = 88**, 0 erros.
- [ ] **Invariante DEC-020:** `cli.py` e os três pontos da GUI intocados.
- [ ] **Smoke manual no Windows:** abrir o editor num projeto com `.flatdropignore` que tenha uma
      pasta fechada por linha manual → a coluna deve dizer `travada (manual)`; acrescentar uma
      linha com `\` e reabrir → o aviso aparece, com o arquivo e a linha; remover a linha e
      reabrir → nenhum aviso.

## Relatório de aplicação

O que foi feito · desvios · arquivos tocados · resultado da suíte · o commit · o resultado do
smoke. Grave o MESMO relatório em `../AAMMDD-HHMM-code-flatdrop.txt`.

## Commit — blocos separados, mensagem SEM acento

```
git add flatdrop/core.py flatdrop/gui.py tests/test_core.py
```

```
git commit -m "feat(ignore): rotular a origem da trava e avisar sobre contrabarra (wo0047)" -m "A coluna Arquivo novo passa a distinguir travada (manual) de travada (git), usando a sonda de arquivo inexistente porque pasta/* nao casa a pasta como diretorio. O editor avisa na abertura quando algum .flatdropignore tem padrao escrito com contrabarra: em sintaxe gitignore ela e escape e o padrao nao casa nada, entao o arquivo sobe achando que foi ignorado. Avisa e aponta a linha, sem normalizar. 2 testes novos."
```

```
git push
```
