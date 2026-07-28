# 260711-spec0020 — Correção do gerador + checkbox + higiene

> **Tipo:** implementação (correção + higiene). Motivada pela análise dos prints e do
> mount desta sessão. Três problemas, os dois primeiros **verificados rodando o
> `make_plan` real**:
> 1. **Gerador deixa passar arquivo novo** — ao excluir uma pasta, o editor lista os
>    arquivos **um a um** em vez de bloquear a pasta; arquivos criados depois vazam.
>    (Evidência: `260711-spec0019-...md`, criado após a geração, entrou no mount mesmo
>    com `meta/specs` "excluído".)
> 2. **Round-trip perde exclusões** — o gerador usa `full` (git+flatdropignore) como
>    base, então regenerar sobre um `.flatdropignore` existente pode largar as exclusões
>    de pastas não expandidas.
> 3. **Checkbox de pasta não fica indeterminado ao abrir** uma raiz que já tem
>    `.flatdropignore` (cosmético — a gravação sai certa, mas confunde a leitura).
>
> **Bump:** 0.5.0 → **0.5.1** (correções).

## 0. Raiz das correções 1 e 2 (verificado)

O gerador precisava de **duas bases distintas**, não uma:
- **Base para gerar = git puro (`gi`)**, não `full`. Assim, uma exclusão feita só pelo
  `.flatdropignore` (não pelo git) é **re-emitida** ao regenerar, em vez de sumir.
- **Default de folha não-editada = estado EFETIVO atual (`full`)**, para o round-trip
  preservar o que já valia (exclusões e liberações) sem o usuário reafirmar item a item.
- **Colapso de pasta cheia:** quando **todas** as folhas de uma pasta versionada são
  excluídas, emitir `pasta/` (nível pasta) em vez de N linhas — **bloqueia arquivos
  novos**. Escolhe a pasta cheia mais alta; pastas parciais continuam por folha (preserva
  o irmão mantido).

Verificado no `make_plan` real: excluir `logs/` inteiro gera `logs/` e um `logs/NOVO.md`
criado depois **continua bloqueado**; regenerar mexendo só em `docs/a` **preserva**
`logs/`/`meta/specs/`; excluir `docs/a,b` mantendo `keep.md` sai por folha.

## 1. Edição A — core.py: substituir `build_flatdropignore`

**Âncora:** a função `build_flatdropignore` inteira (de `def build_flatdropignore(` até,
exclusive, `def flatdropignore_path(`). **Substituir por:**

```python
def build_flatdropignore(root, cfg: ScanConfig, wants: dict[str, bool],
                         existing_text: str | None = None) -> str:
    """Gera o texto do ``.flatdropignore`` (bloco gerenciado) a partir de ``wants``.

    ``wants``: ``{rel_arquivo: bool}`` — inclusao desejada por FOLHA; ausentes seguem o
    ESTADO EFETIVO atual (preserva o .flatdropignore existente no round-trip). Regras:
    - base de geracao = GIT PURO (uma exclusao so-do-flatdropignore e re-emitida);
    - LIBERAR pasta que o git esconde: ``!dir/`` + re-excluir os indesejados;
    - EXCLUIR do lado versionado: colapsa pasta CHEIA em ``dir/`` (a prova de arquivo
      novo); pasta parcial sai por folha (preserva o irmao mantido).
    Preserva linhas fora do bloco gerenciado (round-trip, DEC-016 opcao i).
    """
    root = Path(root)
    full, gi, _fd = _build_ignore_specs(root, cfg)

    def git_in(rel: str, is_dir: bool = False) -> bool:   # baseline SO do git
        if gi is None:
            return True
        return not gi.match_file(rel + "/" if is_dir else rel)

    def full_in(rel: str, is_dir: bool = False) -> bool:  # estado EFETIVO atual
        if full is None:
            return True
        return not full.match_file(rel + "/" if is_dir else rel)

    leaves, _gd, _b = _walk_leaves(root, cfg, _ignore_probes(root, cfg))
    all_dirs = {"/".join(l.split("/")[:i]) for l in leaves for i in range(1, len(l.split("/")))}
    gi_dirs = sorted(d for d in all_dirs if not git_in(d, True))  # pastas escondidas pelo GIT
    want_of = lambda rel: wants.get(rel, full_in(rel))            # default: efetivo atual

    def nearest_gi(rel: str):
        best = None
        for g in gi_dirs:
            if rel.startswith(g + "/") and (best is None or len(g) > len(best)):
                best = g
        return best

    # LIBERAR: pasta git-ignored com alguma folha desejada -> !dir/ + re-exclui indesejados
    liberate: list[str] = []
    reexclude: list[str] = []
    freed: set[str] = set()
    for g in gi_dirs:
        under = [l for l in leaves if l.startswith(g + "/")]
        if any(want_of(l) for l in under) and not any(g.startswith(o + "/") for o in freed):
            liberate.append(f"!{g}/")
            freed.add(g)
            for l in under:
                if not want_of(l):
                    reexclude.append(l)

    # EXCLUIR: base git puro; colapsa pasta CHEIA (a prova de arquivo novo)
    excluded = {l for l in leaves if git_in(l) and not want_of(l) and nearest_gi(l) is None}
    cand = {"/".join(l.split("/")[:i]) for l in excluded for i in range(1, len(l.split("/")))}

    def fully_excluded(d: str) -> bool:
        under = [l for l in leaves if l.startswith(d + "/")]
        return bool(under) and all(l in excluded for l in under)

    collapsible = {d for d in cand if fully_excluded(d)}
    maximal = {d for d in collapsible if not any(d != o and d.startswith(o + "/") for o in collapsible)}
    exclude = [f"{d}/" for d in sorted(maximal)]
    exclude += [l for l in sorted(excluded) if not any(l.startswith(d + "/") for d in maximal)]

    block = liberate + sorted(set(reexclude)) + exclude
    body = "\n".join(block) if block else "# (sem alteracoes)"
    managed = f"{FLATDROP_EDITOR_MARK_A}\n{body}\n{FLATDROP_EDITOR_MARK_B}"
    if existing_text and FLATDROP_EDITOR_MARK_A in existing_text and FLATDROP_EDITOR_MARK_B in existing_text:
        pre = existing_text.split(FLATDROP_EDITOR_MARK_A)[0].rstrip("\n")
        pos = existing_text.split(FLATDROP_EDITOR_MARK_B, 1)[1].lstrip("\n")
        return "\n".join(p for p in (pre, managed, pos) if p) + "\n"
    if existing_text and existing_text.strip():
        return existing_text.rstrip("\n") + "\n\n" + managed + "\n"
    return managed + "\n"
```

> Nota: o editor (`_save`) lê o `.flatdropignore` existente ANTES de gravar (não trunca
> antes de ler) — condição necessária para o round-trip acima. Isso já é o caso no código
> atual; não mexer.

## 2. Edição B — gui.py: checkbox de pasta fica indeterminado ao abrir

Ao expandir uma pasta, os filhos carregam mas o glifo da **própria pasta** não era
recomputado — então uma pasta com filho excluído continuava marcada (☑) em vez de
indeterminada (▣). **Âncora:** em `FlatDropIgnoreEditor._on_open`, a linha final

```python
        s["loaded"] = True
        self._refresh_chain(iid)
```

**Substituir por:**

```python
        s["loaded"] = True
        self._set_glyph(iid, self._folder_state(iid))  # recomputa a propria pasta
        self._refresh_chain(iid)
```

> Escopo: corrige a exibição **ao expandir**. Na visão colapsada inicial (filhos ainda não
> carregados, lazy), a pasta ainda aparece pelo seu próprio estado — limitação aceitável do
> lazy load; a gravação nunca dependeu do glifo da pasta (usa o `want` por folha), então
> **não havia risco de gerar arquivo errado** — era cosmético.

## 3. Edição C — test_core.py: colapso à prova de arquivo novo + round-trip (append)

**Âncora:** fim do arquivo. **Inserir:**

```python
@pytest.mark.skipif(not core.HAS_PATHSPEC, reason="requer pathspec")
def test_editor_collapse_blocks_new_files(tmp_path):
    for p in ("logs/a.md", "logs/b.md", "keep.md"):
        f = tmp_path / p
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("x", encoding="utf-8")
    (tmp_path / ".gitignore").write_text("", encoding="utf-8")
    cfg = core.ScanConfig(mode="collisions")
    txt = core.build_flatdropignore(str(tmp_path), cfg, {"logs/a.md": False, "logs/b.md": False})
    assert "logs/" in txt and "logs/a.md" not in txt  # colapsou em pasta, nao por arquivo
    (tmp_path / ".flatdropignore").write_text(txt, encoding="utf-8")
    (tmp_path / "logs" / "NOVO.md").write_text("x", encoding="utf-8")  # arquivo novo
    names = {f.rel.as_posix() for f in core.make_plan(str(tmp_path), cfg).files}
    assert "logs/NOVO.md" not in names  # bloqueado pela regra de pasta


@pytest.mark.skipif(not core.HAS_PATHSPEC, reason="requer pathspec")
def test_editor_roundtrip_preserves_folder_exclusion(tmp_path):
    for p in ("logs/a.md", "docs/a.md", "docs/keep.md"):
        f = tmp_path / p
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("x", encoding="utf-8")
    (tmp_path / ".gitignore").write_text("", encoding="utf-8")
    cfg = core.ScanConfig(mode="collisions")
    first = core.build_flatdropignore(str(tmp_path), cfg, {"logs/a.md": False})
    (tmp_path / ".flatdropignore").write_text(first, encoding="utf-8")
    existing = (tmp_path / ".flatdropignore").read_text(encoding="utf-8")
    # usuario mexe SO em docs/a; logs nao entra em wants (nao expandido)
    second = core.build_flatdropignore(str(tmp_path), cfg, {"docs/a.md": False}, existing_text=existing)
    (tmp_path / ".flatdropignore").write_text(second, encoding="utf-8")
    names = {f.rel.as_posix() for f in core.make_plan(str(tmp_path), cfg).files}
    assert "logs/a.md" not in names   # exclusao preservada no round-trip
    assert "docs/a.md" not in names   # nova exclusao aplicada
    assert "docs/keep.md" in names    # irmao preservado
```

2 testes novos → 46 → **48**.

## 4. Edição D — higiene: `__pycache__`/`.pyc` versionados

O Code notou `.pyc` entrando no `git add -A`; `__pycache__` está **rastreado** no repo e
não está no `.gitignore`. **Duas partes:**

**D.1 — `.gitignore`:** acrescentar (se ainda não houver bloco Python):

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
.pytest_cache/
```

**D.2 — destrastrear** (comando no commit, §6): `git rm -r --cached` do que já entrou.

## 5. Validação

- `python -m pytest -q` → **48 verdes**.
- Smoke manual (Windows): abrir o editor numa raiz **com** `.flatdropignore`, expandir uma
  pasta de estado misto e conferir o glifo **indeterminado**; excluir uma pasta inteira,
  salvar, e conferir no arquivo que saiu `pasta/` (não a lista de arquivos); criar um
  arquivo novo na pasta e rodar o FlatDrop para ver que **não** vai ao mount.
- Fica ainda pendente (herdado da spec0018) o **smoke geral da GUI** do editor no Windows.

## 6. Fecho (docs + versão + commit)

- **Bump 0.5.1**; `CHANGELOG.md` *Fixed:* gerador colapsa pasta cheia (bloqueia arquivos
  novos) e preserva exclusões no round-trip (base git-pura); checkbox de pasta fica
  indeterminado ao expandir. *Chore:* `.gitignore` do Python + destrastrear `__pycache__`.
- **FIX novo (FIX-006):** o gerador precisa de base **git-pura** + default **efetivo** +
  **colapso de pasta**; documenta por que exclusão por folha era insuficiente (arquivo
  novo vaza) — evita regressão.
- **STATUS.md:** atualizar (o cabeçalho ainda menciona 0.4.0/0.3.1); marcar spec0019 e
  0020 como aplicadas; próxima = item C (persistência).
- **IDEAS.md:** registrar, se ainda não, a decisão de conteúdo dos ignores coexistentes
  (abaixo) e a limitação do glifo colapsado inicial.

## 7. Commit (entregar pronto, sem acento)

```
git rm -r --cached __pycache__ flatdrop/__pycache__ tests/__pycache__ 2>NUL & git add -A && git commit -m "fix(ignore): gerador colapsa pasta cheia e preserva round-trip; checkbox indeterminado" -m "build_flatdropignore usa base git-pura + default efetivo (round-trip preserva exclusoes de pasta nao expandida) e colapsa pasta cheia em dir/ (bloqueia arquivos novos). Editor recomputa o glifo da pasta ao expandir. Higiene: .gitignore do Python e destrastrear __pycache__. 2 testes novos (48). FIX-006. Bump 0.5.1."
```

## 8. Decisão de conteúdo pendente (não é código)

O repo tem **dois** arquivos de ignore na raiz: `.flatdropignore` (gerado pelo editor,
por-arquivo) e `flatdropignore.txt` (à mão, nível-pasta). Pela precedência da spec0019, o
`.flatdropignore` **vence** e o `.txt` fica **inerte**. Recomendo: aplicar esta spec, abrir
o editor, excluir `meta/specs/` e `logs/` inteiros (agora sai nível-pasta), salvar — e
**apagar o `flatdropignore.txt`** para não ter dois. Ou, se preferir manter só o à mão
(nível-pasta, já correto), **apagar o `.flatdropignore`**. Ter os dois só confunde.
