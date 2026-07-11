# 260711-spec0019 — `.flatdropignore` no mount + nomes alternativos (implementação)

> **Tipo:** implementação. Dois ajustes no arquivo de controle do FlatDrop, motivados
> pela nota 2026-07-10 e **verificados rodando o `make_plan` real** nesta sessão:
> 1. **Fix** — o FlatDrop escondia o próprio `.flatdropignore` do mount; agora ele vai
>    para o Projeto, como o `.gitignore` (ambos são contexto importante).
> 2. **Feature** — aceitar nomes alternativos `.flatdropignore.txt` e `flatdropignore.txt`
>    (baixar um dotfile da internet às vezes falha), com precedência definida.
>
> **Bump:** 0.4.0 → **0.5.0** (adiciona funcionalidade — nome alternativo — logo, minor).

## Contexto verificado

- Hoje `.flatdropignore` está em `DEFAULT_FILE_IGNORES` (pulado) enquanto `.gitignore`
  está na allowlist (vai ao mount). Simulando o fix por `ScanConfig` (tirar do
  `file_ignores`, pôr no `extensionless_allow`), o `make_plan` passou a copiar
  `.flatdropignore` — e também `.flatdropignore.txt`/`flatdropignore.txt` (têm `.txt`).
- O nome é lido hardcoded em `_collect_ignore_lines` (`if ".flatdropignore" in filenames`).
  Protótipo com um laço de aliases fez `flatdropignore.txt` (contendo `logs/`) excluir
  `logs/` corretamente. A leitura reusa `_read_ignore_lines`/`_rebase_all` já provados,
  então o risco é baixo — muda só QUAIS nomes disparam a leitura.

## 1. Edição A — config.py: constante de nomes + mover `.flatdropignore` para a allowlist

**A.1 — Nova constante.** **Âncora:** inserir imediatamente ANTES de
`DEFAULT_FILE_IGNORES: set[str] = {`. **Inserir:**

```python
# Nomes aceitos para o arquivo de controle do FlatDrop, em ordem de PRECEDENCIA.
# Os aliases .txt existem porque baixar um dotfile da internet as vezes falha; num
# mesmo diretorio, o primeiro nome encontrado vence (spec0019).
FLATDROPIGNORE_NAMES: tuple[str, ...] = (
    ".flatdropignore", ".flatdropignore.txt", "flatdropignore.txt",
)


```

**A.2 — Tirar `.flatdropignore` do `DEFAULT_FILE_IGNORES`.** **Âncora (remover a linha):**

```python
    ".flatdropignore",  # arquivo de controle do FlatDrop — nao vai para o upload
```

(Deixar as linhas de `_manifest.md`/`_tree.md` como estão.)

**A.3 — Pôr `.flatdropignore` na allowlist (vai ao mount, como o `.gitignore`).**
**Âncora:** a linha

```python
    ".gitignore", ".gitattributes", ".dockerignore", ".editorconfig",
```

**Substituir por:**

```python
    ".gitignore", ".gitattributes", ".dockerignore", ".editorconfig",
    ".flatdropignore",  # controle do FlatDrop — importante no Projeto (spec0019)
```

> Os aliases `.flatdropignore.txt`/`flatdropignore.txt` já entram por serem `.txt` (tipo
> aceito por padrão). Se o autor filtrar `.txt`, eles não iriam ao mount — caso de borda
> aceitável; o canônico `.flatdropignore` está garantido pela allowlist.

## 2. Edição B — core.py: `_collect_ignore_lines` lê os aliases (com precedência)

**Âncora (substituir o bloco):**

```python
        if ".flatdropignore" in filenames:
            fd_by.append((depth, _rebase_all(_read_ignore_lines(cur / ".flatdropignore"), base)))
```

**Por:**

```python
        for _fdname in C.FLATDROPIGNORE_NAMES:
            if _fdname in filenames:
                fd_by.append((depth, _rebase_all(_read_ignore_lines(cur / _fdname), base)))
                break  # precedencia: o primeiro nome encontrado no diretorio vence
```

> `core.py` já importa o módulo de config como `C` (usado em `C.DEFAULT_SEP` etc.).

## 3. Edição C — core.py: helper de caminho + editor grava no alias existente

**C.1 — Novo helper.** **Âncora:** inserir logo após a função `build_flatdropignore`
(fim do bloco do editor). **Inserir:**

```python
def flatdropignore_path(root) -> Path:
    """Caminho do arquivo de controle na raiz: o primeiro alias EXISTENTE (por
    precedencia), ou o nome canonico se nenhum existir. Evita o editor criar um
    segundo arquivo quando o autor ja usa, ex., flatdropignore.txt (spec0019)."""
    root = Path(root)
    for name in C.FLATDROPIGNORE_NAMES:
        if (root / name).exists():
            return root / name
    return root / C.FLATDROPIGNORE_NAMES[0]
```

**C.2 — O editor grava no alias certo.** **Âncora:** em `FlatDropIgnoreEditor._save`, a
linha

```python
        target = self.root_dir / ".flatdropignore"
```

**Substituir por:**

```python
        target = core.flatdropignore_path(self.root_dir)
```

## 4. Edição D — test_core.py: dois testes (append no fim)

**Âncora:** fim do arquivo. **Inserir:**

```python
@pytest.mark.skipif(not core.HAS_PATHSPEC, reason="requer pathspec")
def test_flatdropignore_reaches_mount(tmp_path):
    (tmp_path / "keep.md").write_text("x", encoding="utf-8")
    (tmp_path / ".flatdropignore").write_text("# controle\n", encoding="utf-8")
    plan = core.make_plan(str(tmp_path), core.ScanConfig(mode="collisions"))
    names = {f.rel.as_posix() for f in plan.files}
    assert ".flatdropignore" in names  # agora vai ao Projeto (spec0019)


@pytest.mark.skipif(not core.HAS_PATHSPEC, reason="requer pathspec")
def test_flatdropignore_alias_txt_applies(tmp_path):
    (tmp_path / "logs").mkdir()
    (tmp_path / "logs" / "l.md").write_text("x", encoding="utf-8")
    (tmp_path / "keep.md").write_text("x", encoding="utf-8")
    # sem .flatdropignore canonico; so o alias sem ponto
    (tmp_path / "flatdropignore.txt").write_text("logs/\n", encoding="utf-8")
    plan = core.make_plan(str(tmp_path), core.ScanConfig(mode="collisions"))
    names = {f.rel.as_posix() for f in plan.files}
    assert "logs/l.md" not in names           # o alias foi aplicado
    assert "keep.md" in names
```

São 2 testes novos → 44 → **46**.

## 5. Validação

- `python -m pytest -q` → **46 verdes**.
- Sanidade manual (opcional): rodar o FlatDrop num repo com `.flatdropignore` e conferir
  que ele agora aparece no `_MANIFEST.md`/saída; renomear para `flatdropignore.txt` e
  confirmar que os padrões continuam valendo.

## 6. Fecho (docs + versão)

- **Bump 0.5.0** em `flatdrop/__init__.py`; entrada no `CHANGELOG.md`:
  *Added:* nomes alternativos `.flatdropignore.txt`/`flatdropignore.txt`; o
  `.flatdropignore` agora vai ao mount. *Fixed:* o FlatDrop escondia o próprio
  `.flatdropignore` do upload.
- **DEC nova (DEC-018):** reverter a decisão antiga de não enviar o `.flatdropignore` ao
  upload — os dois arquivos de ignore são contexto importante no Projeto e devem ir ao
  mount (e ser versionados no repo).
- **GLOSSARY / armadilha (nota curta):** ancoragem de padrões — um padrão **multi-segmento**
  (`meta/specs/`) ancora na **localização do `.flatdropignore`** (semântica gitignore),
  enquanto **um segmento** (`specs/`, `logs/`) casa em qualquer profundidade. Verificado:
  `.flatdropignore` **aninhado** em subpasta funciona (escopo por subárvore). Não é bug —
  é comportamento correto; documentar evita confusão como o caso relatado.

## 7. Commit (entregar pronto, sem acento)

```
git add -A && git commit -m "feat(ignore): flatdropignore vai ao mount e aceita nomes alternativos" -m "Tira .flatdropignore do file_ignores e poe na allowlist (vai ao Projeto como o .gitignore). Aceita aliases .flatdropignore.txt e flatdropignore.txt com precedencia; editor grava no alias existente. 2 testes novos (46 verdes). DEC-018. Bump 0.5.0."
```
