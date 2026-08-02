# WO 0048 — o `_MANIFEST` passa a carregar o estado do repositório git

> **Tipo:** CÓDIGO (core + testes).
> **Config sugerida:** modelo intermediário, `/effort` médio.
> **Pré-requisito:** 0.14.0 ou posterior, suíte verde. **Independente das wo0045–0047** — pode ser
> aplicada antes, depois ou entre elas; não toca nenhum arquivo em comum a não ser `core.py`, em
> região distante (aplique uma de cada vez para o `git diff` continuar legível).
> **Base:** notas do autor `260730-0432.txt` e `260801-1818.txt` (esta com os três refinos:
> formato do `log`, `status` resumido, rótulo de foto).
> **Âncora semântica:** se um trecho-âncora não bater EXATAMENTE, **PARE e reporte**.
> **Idempotência:** se `git_snapshot` já existir em `flatdrop/core.py`, **PULE** a WO.

> **Canal dos meta neste ciclo = CHAT.** Não faça append em `meta/*.md`.

---

## 1. Por que

O mount é uma cópia **achatada**: não tem `.git`. Toda conversa começa com o assistente sem saber
em que commit o projeto está, e o custo é recorrente — ou ele pede (um turno perdido), ou preenche
de memória (pior, e já aconteceu aqui em 28/07). Duas linhas no manifesto apagam o problema na
origem, e apagam junto uma regra inteira que hoje existe só para contornar a ausência.

O dado é **foto do momento da geração**, não estado atual — e é justamente por isso que ele
funciona: ao lado da hora de geração, que já está no manifesto, dá para saber o quanto envelheceu.

## 2. Contexto factual

- **Medido:** `write_manifest` (`core.py` ~1169) já imprime «Gerado em» com data e hora; é o
  vizinho natural das duas linhas novas.
- **Medido:** `core.py` **não** importa `subprocess` hoje (a edição 1 acrescenta). `gui.py` já
  importa, para abrir o explorador de arquivos.
- **Refinos do autor, a respeitar ao pé da letra** (`260801-1818.txt`): `--format=%h %ad %s` com
  `--date=short`, não `--oneline` — a data do commit ao lado da hora de geração diz de cara se o
  mount é do commit ou de trabalho posterior; do `status`, **o resumo**, não a listagem, porque
  verboso é ruído e **vaza nome de arquivo pessoal não rastreado**.

---

## Edição 1 — `flatdrop/core.py` · importar `subprocess`

**Âncora:**

```
import os
import shutil
```

**Substituir por:**

```
import os
import shutil
import subprocess
```

## Edição 2 — `flatdrop/core.py` · função nova `git_snapshot`

**Âncora** *(primeira linha da definição de `write_manifest`)*:

```
def write_manifest(dest: Path, plan: FlattenPlan, cfg: ScanConfig) -> Path:
```

**Inserir IMEDIATAMENTE ANTES:**

```
def _git(root: Path, *args: str) -> str | None:
    """Roda um comando git na raiz e devolve a saida limpa, ou None se nao der.

    Silencioso de proposito: sem git instalado, fora de repositorio, timeout ou erro, o
    manifesto simplesmente nao ganha as linhas. Nada aqui pode impedir um achatamento.
    """
    try:
        p = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                           text=True, timeout=5, encoding="utf-8", errors="replace")
    except (OSError, subprocess.SubprocessError):
        return None
    return p.stdout.strip() if p.returncode == 0 else None


def git_snapshot(root) -> tuple[str | None, str | None]:
    """(commit, resumo do status) da raiz — FOTO do momento, nao estado atual.

    Existe porque o mount e uma copia achatada e nao leva o ``.git`` junto: sem estas duas
    linhas, quem le o mount nao tem como saber em que commit o projeto esta, e acaba
    perguntando ou — pior — respondendo de memoria.

    - commit: ``%h %ad %s`` com ``--date=short``. A data do COMMIT ao lado da hora de
      geracao do manifesto diz de cara se o mount e o commit ou trabalho posterior a ele.
    - status: RESUMO numerico, nunca a listagem. ``git status`` verboso e ruido e vaza nome
      de arquivo pessoal nao rastreado — o mount vai para uma conversa.
    """
    root = Path(root)
    if not (root / ".git").exists():
        return None, None
    commit = _git(root, "log", "-1", "--format=%h %ad %s", "--date=short")
    branch = _git(root, "rev-parse", "--abbrev-ref", "HEAD")
    porcelain = _git(root, "status", "--porcelain=v1", "--branch")
    if porcelain is None:
        return commit, None
    modificados = nao_rastreados = 0
    frente = ""
    for ln in porcelain.splitlines():
        if ln.startswith("##"):
            if "[ahead " in ln:
                frente = " · " + ln.split("[ahead ", 1)[1].split("]")[0].split(",")[0] \
                    .strip() + " commit(s) a frente de origin"
            continue
        if ln.startswith("??"):
            nao_rastreados += 1
        else:
            modificados += 1
    partes = [f"branch {branch or '?'}"]
    if modificados or nao_rastreados:
        if modificados:
            partes.append(f"{modificados} modificado(s)")
        if nao_rastreados:
            partes.append(f"{nao_rastreados} nao rastreado(s)")
    else:
        partes.append("limpo")
    return commit, " · ".join(partes) + frente
```

## Edição 3 — `flatdrop/core.py` · imprimir as duas linhas no manifesto

**Âncora** *(em `write_manifest`)*:

```
    lines.append(f"- **Gerado em:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"- **Modo de renomeação:** {cfg.mode} · separador `{cfg.sep}`")
```

**Substituir por:**

```
    lines.append(f"- **Gerado em:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    # Estado do repo: FOTO da hora acima, nao estado atual. Rotulado assim de proposito —
    # quem le o mount precisa saber que o dado envelhece como todo o resto (wo0048).
    _commit, _status = git_snapshot(plan.root)
    if _commit:
        lines.append(f"- **Git (foto da geração) — último commit:** `{_commit}`")
    if _status:
        lines.append(f"- **Git (foto da geração) — status:** {_status}")
    lines.append(f"- **Modo de renomeação:** {cfg.mode} · separador `{cfg.sep}`")
```

## Edição 4 — `tests/test_core.py` · quatro testes novos

**Inserir ao FIM do arquivo:**

```


def _git_disponivel():
    try:
        return subprocess.run(["git", "--version"], capture_output=True, timeout=5).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def test_git_snapshot_sem_repositorio(tmp_path):
    """Pasta que nao e repo nao ganha as linhas — e nao quebra nada (wo0048)."""
    assert core.git_snapshot(tmp_path) == (None, None)


@pytest.mark.skipif(not _git_disponivel(), reason="git nao instalado no ambiente")
def test_git_snapshot_repo_limpo(tmp_path):
    """Repo sem alteracao pendente sai como 'limpo', e o commit traz hash, data e assunto."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True)
    (tmp_path / "a.md").write_text("x\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "primeiro"], cwd=tmp_path, check=True)
    commit, status = core.git_snapshot(tmp_path)
    assert commit and commit.endswith("primeiro")
    assert len(commit.split()) >= 3          # hash + data + assunto
    assert status and "limpo" in status


@pytest.mark.skipif(not _git_disponivel(), reason="git nao instalado no ambiente")
def test_git_snapshot_conta_sem_listar(tmp_path):
    """O status e RESUMO: conta, e nao expoe nome de arquivo nao rastreado."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=tmp_path, check=True)
    (tmp_path / "a.md").write_text("x\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-qm", "primeiro"], cwd=tmp_path, check=True)
    (tmp_path / "a.md").write_text("y\n", encoding="utf-8")
    (tmp_path / "segredo-pessoal.txt").write_text("z\n", encoding="utf-8")
    _commit, status = core.git_snapshot(tmp_path)
    assert "1 modificado(s)" in status and "1 nao rastreado(s)" in status
    assert "segredo-pessoal" not in status


@pytest.mark.skipif(not _git_disponivel(), reason="git nao instalado no ambiente")
def test_manifesto_traz_as_duas_linhas(tmp_path):
    """As linhas aparecem no _MANIFEST.md, rotuladas como foto (wo0048)."""
    origem = tmp_path / "src"
    origem.mkdir()
    (origem / "a.md").write_text("x\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=origem, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=origem, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=origem, check=True)
    subprocess.run(["git", "add", "."], cwd=origem, check=True)
    subprocess.run(["git", "commit", "-qm", "primeiro"], cwd=origem, check=True)
    dest = tmp_path / "out"
    cfg = core.ScanConfig()
    plan = core.make_plan(origem, dest, cfg)
    core.execute_plan(plan, cfg)
    texto = (dest / core.C.MANIFEST_NAME).read_text(encoding="utf-8")
    assert "Git (foto da geração) — último commit:" in texto
    assert "Git (foto da geração) — status:" in texto
```

> **Medido:** `tests/test_core.py` já importa `pytest`, mas **não** importa `subprocess` —
> acrescente `import subprocess` junto dos imports existentes.
>
> **Se `core.make_plan` / `core.execute_plan` / `core.C.MANIFEST_NAME` tiverem outra assinatura
> ou outro nome**, use no último teste a mesma forma que os testes existentes de manifesto já
> usam — copie deles em vez de inventar, e diga no relatório o que precisou trocar.

---

## Fora de escopo

- **Não mexa no `_TREE.md`.** A árvore descreve a varredura, não o repositório.
- **Não liste arquivos.** Se um dia o autor quiser a lista, será `--porcelain` com teto e decisão
  própria — hoje, resumo.
- **Não faça o achatamento depender do git.** Qualquer falha do subprocesso é silenciosa.
- **`flatdrop/cli.py` e o gerador de `.bat` continuam intocados** (DEC-020): não há flag nova; a
  informação entra sempre que houver `.git`.

## Armadilhas desta WO

- **`plan.root` é a raiz do plano, não `dest`.** Passar `dest` mediria o repositório errado (a
  pasta de saída costuma estar em `Downloads`).
- **Multi-fonte:** o snapshot é da **raiz comum** (`plan.root`). É a escolha certa por ora — dizer
  isso no relatório se a árvore tiver várias fontes com repositórios diferentes.
- **Timeout obrigatório.** Um `git` travado não pode segurar a GUI.
- **Não use `check=True`** no `_git`: repositório sem nenhum commit devolve código de erro no
  `log -1`, e isso é normal — o manifesto simplesmente sai sem a linha do commit.

---

## Depois de aplicar — conferência antes do commit

- [ ] `git diff` mostra só `flatdrop/core.py` e `tests/test_core.py`.
- [ ] `python -m pytest -q`: os 4 testes novos passam (ou pulam, se não houver `git` no ambiente).
- [ ] **Rede real:** rodar o FlatDrop **neste próprio repo** e abrir o `_MANIFEST` gerado — as duas
      linhas devem aparecer logo abaixo de «Gerado em», com o commit do dia e o status batendo com
      o `git status` que você acabou de rodar. **Cole as duas linhas no relatório.**
- [ ] Rodar numa pasta **sem** `.git` e confirmar que o manifesto sai normal, sem as linhas.

## Relatório de aplicação

O que foi feito · desvios · arquivos tocados · resultado da suíte · o commit · **as duas linhas
geradas no manifesto deste repo**. Grave o MESMO relatório em `../AAMMDD-HHMM-code-flatdrop.txt`.

## Commit — blocos separados, mensagem SEM acento

```
git add flatdrop/core.py tests/test_core.py
```

```
git commit -m "feat(manifest): gravar o estado do repo git como foto da geracao (wo0048)" -m "O mount e uma copia achatada e nao leva o .git, entao quem le o manifesto nao sabia em que commit o projeto esta. Passam a sair duas linhas: ultimo commit no formato hash + data curta + assunto, e um RESUMO do status (branch, contagem de modificados e nao rastreados, commits a frente de origin). Resumo e nao listagem, para nao virar ruido nem vazar nome de arquivo nao rastreado. Falha de git e silenciosa: nada impede o achatamento. 4 testes novos."
```

```
git push
```
