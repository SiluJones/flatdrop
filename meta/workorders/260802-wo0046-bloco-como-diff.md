# WO 0046 — o bloco gerenciado vira um *diff* contra tudo o que já existe, e vai sempre no fim

> **Tipo:** CÓDIGO (core + GUI + testes).
> **Config sugerida:** modelo mais capaz, `/effort` alto. É a mudança de fundo — a base de
> comparação do gerador muda.
> **Pré-requisito:** **a wo0045 aplicada e commitada** (as âncoras das edições 3 e 4 são o texto
> que ela deixou), suíte em 82 verdes.
> **Base:** `meta/specs/260802-spec-anatomia-flatdropignore.md`, critérios 3–7 · passos 1, 2 e 3
> de `meta/analises/260728-ANALISE-bloco-gerenciado-vs-manual.md` (medidos em protótipo).
> **Depende de:** wo0045.
> **Âncora semântica:** se um trecho-âncora não bater EXATAMENTE, **PARE e reporte**.
> **Idempotência:** se `build_flatdropignore` já tiver um parâmetro `skip_managed_root` na
> chamada a `_build_ignore_specs`, **PULE** a WO e diga no relatório.

> **Canal dos meta neste ciclo = CHAT.** Não faça append em `meta/*.md`.

---

## 1. Por que

O gerador compara o estado desejado com o **git puro** — herança de quando o bloco era o arquivo
inteiro. Ele é cego para a curadoria manual do próprio `.flatdropignore` e, sendo cego, não sabe
nem que existe algo a corrigir: **duplica** o que já está fora do bloco, e **não emite** o `!` que
precisaria vencer uma linha manual, então destravar uma pasta é desfeito em silêncio.

Trocando a base para *tudo o que já existe menos o próprio bloco*, o bloco passa a ser o que
sempre deveria ter sido: **um diff**. Emite só o que diverge; se a parte manual já faz o que a
tela mostra, o bloco fica vazio.

## 2. Contexto factual

Protótipo rodado em sandbox contra o código da 0.14.0 (2026-08-02). **Medido:**

| Gesto | Hoje | Com esta WO |
|---|---|---|
| salvar sem mexer em nada | `logs/*` · `meta/w/*` · `INSTRUCOES.md` | `# (sem alteracoes)` |
| destravar `logs` (fechada por linha manual) | `meta/w/*` · `INSTRUCOES.md` | `!logs/*` |
| marcar `logs/a.md` em pasta travada | as 3 duplicatas + `!logs/a.md` | `!logs/a.md` |

**Medido também:** o round-trip aguenta (salvar 2× dá o mesmo bloco) e o `.flatdropignore` deste
repo continua saindo com as quatro regras, `!meta/workorders/_TEMPLATE.md` inclusive — porque ali
tudo está *dentro* do bloco, então tudo diverge da baseline e tudo é re-emitido.

**Medido, e é o motivo do passo 3:** com um bloco mandando `!logs/*` e uma linha manual `logs/*`
**depois** do marcador de fechamento, o arquivo obedece à de fora e os passos 1+2 sozinhos escrevem
`# (sem alteracoes)` — o editor concorda com um estado que não é o que ele mostra na tela.

**Deduzido:** mover o bloco para o fim pode inverter a precedência de uma regra que estava depois
dele. Por isso a GUI avisa antes, em vez de a core decidir sozinha.

---

## Edição 1 — `flatdrop/core.py` · `_collect_ignore_lines` sabe pular o bloco

**Âncora:**

```
def _collect_ignore_lines(root: Path, cfg: ScanConfig) -> tuple[list[str], list[str]]:
    """Junta as linhas (rebaseadas) de todos os .gitignore e .flatdropignore da árvore.

    Devolve (gitignore_lines, flatdropignore_lines), cada um em ordem raso->fundo.
    """
```

**Substituir por:**

```
def _collect_ignore_lines(root: Path, cfg: ScanConfig,
                          skip_managed_root: bool = False) -> tuple[list[str], list[str]]:
    """Junta as linhas (rebaseadas) de todos os .gitignore e .flatdropignore da árvore.

    Devolve (gitignore_lines, flatdropignore_lines), cada um em ordem raso->fundo.

    ``skip_managed_root=True`` ignora o BLOCO GERENCIADO do .flatdropignore da RAIZ. E a
    baseline do editor: "tudo o que ja existe MENOS o que eu mesmo escrevi da ultima vez".
    Sem ela o gerador se compararia com o proprio resultado anterior e nunca saberia o que
    a curadoria manual ja faz (wo0046).
    """
```

## Edição 2 — `flatdrop/core.py` · aplicar o corte na leitura da raiz

**Âncora** *(dentro do laço de `_collect_ignore_lines`)*:

```
        for _fdname in C.FLATDROPIGNORE_NAMES:
            if _fdname in filenames:
                fd_by.append((depth, _rebase_all(_read_ignore_lines(cur / _fdname), base)))
                break  # precedencia: o primeiro nome encontrado no diretorio vence
```

**Substituir por:**

```
        for _fdname in C.FLATDROPIGNORE_NAMES:
            if _fdname in filenames:
                _linhas = _read_ignore_lines(cur / _fdname)
                if skip_managed_root and base == "":
                    _pre, _bloco, _pos = _split_managed("\n".join(_linhas))
                    if _bloco:
                        _linhas = (_pre + "\n" + _pos).splitlines()
                fd_by.append((depth, _rebase_all(_linhas, base)))
                break  # precedencia: o primeiro nome encontrado no diretorio vence
```

## Edição 3 — `flatdrop/core.py` · `_build_ignore_specs` repassa o parâmetro

**Âncora:**

```
    gi_lines, fd_lines = _collect_ignore_lines(root, cfg)
    if not gi_lines and not fd_lines:
```

**Substituir por:**

```
    gi_lines, fd_lines = _collect_ignore_lines(root, cfg, skip_managed_root)
    if not gi_lines and not fd_lines:
```

E, na mesma função, **âncora**:

```
def _build_ignore_specs(root: Path, cfg: ScanConfig):
```

**Substituir por:**

```
def _build_ignore_specs(root: Path, cfg: ScanConfig, skip_managed_root: bool = False):
```

## Edição 4 — `flatdrop/core.py` · função nova `rules_after_block`

**Âncora** *(primeira linha da definição de `build_flatdropignore`)*:

```
def build_flatdropignore(root, cfg: ScanConfig, wants: dict[str, bool],
```

**Inserir IMEDIATAMENTE ANTES:**

```
def rules_after_block(text: str) -> list[str]:
    """Linhas de REGRA escritas depois do bloco gerenciado (violam a anatomia normativa).

    Comentario e linha vazia nao contam — so o que o matcher leria como padrao. Existe
    porque o bloco passa a ser reescrito sempre no FIM (wo0046): se havia regra depois
    dele, a precedencia dessa regra se inverte, e isso e mudanca de comportamento que a
    ferramenta nao pode fazer calada. A core devolve a lista; quem avisa e a GUI.
    """
    _pre, bloco, pos = _split_managed(text)
    if not bloco:
        return []
    return [ln for ln in pos.splitlines()
            if ln.strip() and not ln.lstrip().startswith("#")]
```

## Edição 5 — `flatdrop/core.py` · a base de comparação deixa de ser o git puro

**Âncora** *(início do corpo de `build_flatdropignore`)*:

```
    root = Path(root)
    full, gi, _fd, _negated = _build_ignore_specs(root, cfg)

    def git_in(rel: str, is_dir: bool = False) -> bool:   # baseline SO do git
        if gi is None:
            return True
        return not gi.match_file(rel + "/" if is_dir else rel)

    def full_in(rel: str, is_dir: bool = False) -> bool:  # estado EFETIVO atual
        if full is None:
            return True
        return not full.match_file(rel + "/" if is_dir else rel)
```

**Substituir por:**

```
    root = Path(root)
    full, _gi, _fd, _negated = _build_ignore_specs(root, cfg)
    base, _bg, _bf, _bn = _build_ignore_specs(root, cfg, skip_managed_root=True)

    def _in(spec, rel: str, is_dir: bool = False) -> bool:
        if spec is None:
            return True
        return not spec.match_file(rel + "/" if is_dir else rel)

    def full_in(rel: str, is_dir: bool = False) -> bool:
        """Estado EFETIVO de hoje (com o bloco) — e o que preserva o round-trip."""
        return _in(full, rel, is_dir)

    def base_in(rel: str, is_dir: bool = False) -> bool:
        """BASELINE: gitignore + curadoria manual, SEM o bloco. E contra isto que o bloco
        e um diff. Era o git puro ate a wo0046, e por isso o gerador duplicava o que ja
        estava fora do bloco e nao emitia o "!" que venceria uma linha manual."""
        return _in(base, rel, is_dir)
```

## Edição 6 — `flatdrop/core.py` · emitir só o que diverge (pastas)

**Âncora:**

```
    dirs_com_arquivo = {parent_of(l) for l in leaves if parent_of(l)}
    for d in sorted(all_dirs):
        fechada, git_fora = closed_of(d), not git_in(d, True)
        if fechada and not git_fora and d in dirs_com_arquivo:
            folder_lines.append(f"{d}/*")
        elif not fechada and git_fora:
            folder_lines.append(f"!{d}/*")
```

**Substituir por:**

```
    dirs_com_arquivo = {parent_of(l) for l in leaves if parent_of(l)}
    # "arquivo novo aqui entra?" perguntado dos DOIS lados: o que eu quero x o que a
    # baseline ja faz. Iguais -> nenhuma linha. E a definicao de diff.
    base_fechada = lambda d: not base_in(f"{d}/{FLATDROP_PROBE}")
    for d in sorted(all_dirs):
        quero, ja_e = closed_of(d), base_fechada(d)
        if quero == ja_e:
            continue
        if quero and d in dirs_com_arquivo:
            folder_lines.append(f"{d}/*")
        elif not quero:
            folder_lines.append(f"!{d}/*")   # abre o que a parte manual (ou o git) fechou
```

## Edição 7 — `flatdrop/core.py` · emitir só o que diverge (arquivos)

**Âncora:**

```
    for l in sorted(leaves):
        d = parent_of(l)
        if not d:                                   # raiz nao tem trava: regra antiga
            if git_in(l) and not want_of(l):
                file_lines.append(l)
            continue
        if closed_of(d):
            if want_of(l):
                file_lines.append(f"!{l}")
        else:
            if not want_of(l):
                file_lines.append(l)
```

**Substituir por:**

```
    for l in sorted(leaves):
        d = parent_of(l)
        quero = want_of(l)
        # o que a baseline JA faz com este arquivo, considerando as linhas de PASTA que
        # esta mesma geracao acabou de emitir (elas vem antes e valem para o que esta dentro)
        ja_e = base_in(l)
        if d and f"{d}/*" in folder_lines:
            ja_e = False
        elif d and f"!{d}/*" in folder_lines:
            ja_e = True
        if quero == ja_e:
            continue
        file_lines.append(f"!{l}" if quero else l)
```

## Edição 8 — `flatdrop/core.py` · o bloco vai sempre para o fim

**Âncora** *(trecho final de `build_flatdropignore`, como a wo0045 o deixou)*:

```
    if existing_text and existing_text.strip():
        pre, bloco, pos = _split_managed(existing_text)
        if bloco:
            pre, pos = pre.rstrip("\n"), pos.strip("\n")
            return "\n".join(p for p in (pre, managed, pos) if p) + "\n"
        return existing_text.rstrip("\n") + "\n\n" + managed + "\n"
    return managed + "\n"
```

**Substituir por:**

```
    if existing_text and existing_text.strip():
        pre, bloco, pos = _split_managed(existing_text)
        if bloco:
            # Posicao FIXA: o bloco e sempre o ultimo conteudo do arquivo. Vale a ultima
            # regra que casa, entao bloco no fim = o editor tem a palavra final sobre o que
            # ele mostra na tela. Move-se o PROPRIO bloco, nunca o texto do autor — o que
            # estava depois dele sobe, na ordem em que estava. Se isso inverter a
            # precedencia de alguma regra, quem avisa e a GUI (ver rules_after_block).
            antes = "\n".join(p for p in (pre.rstrip("\n"), pos.strip("\n")) if p)
            return (antes + "\n\n" + managed + "\n") if antes else managed + "\n"
        return existing_text.rstrip("\n") + "\n\n" + managed + "\n"
    return managed + "\n"
```

## Edição 9 — `flatdrop/core.py` · atualizar a tabela do docstring

**Âncora** *(no docstring de `build_flatdropignore`)*:

```
    Emissao (base de geracao = GIT PURO; exclusao so-do-flatdropignore e re-emitida):

    ==========  ==================  ====================  =========================
    trava       escondida pelo git  linha da PASTA        linhas dos ARQUIVOS
    ==========  ==================  ====================  =========================
    fechada     nao                 ``pasta/*``           ``!pasta/y`` p/ marcado
    fechada     sim                 (nada)                ``!pasta/y`` p/ marcado
    aberta      nao                 (nada)                ``pasta/x`` p/ desmarcado
    aberta      sim                 ``!pasta/*``           ``pasta/x`` p/ desmarcado
    ==========  ==================  ====================  =========================
```

**Substituir por:**

```
    Emissao (wo0046) — o bloco e um DIFF contra a BASELINE, que e "gitignore + curadoria
    manual do proprio .flatdropignore, sem o bloco". Uma regra so, em vez da tabela de
    quatro casos que existia quando a base era o git puro:

        para cada pasta e cada arquivo, se o estado desejado e o que a baseline JA faz,
        nao se escreve nada; se diverge, escreve-se a linha que corrige — inclusive
        ``!pasta/*`` para ABRIR o que a parte manual ou o git fecharam.

    Consequencia visivel: num arquivo curado a mao, o bloco fica quase vazio. E o certo —
    nao ha nada a corrigir —, e nao "sumiu".
```

## Edição 10 — `flatdrop/gui.py` · avisar antes de mover o bloco

**Âncora** *(em `FlatDropIgnoreEditor._save`, como a wo0045 o deixou)*:

```
        existing = target.read_text(encoding="utf-8") if target.exists() else None
```

**Inserir IMEDIATAMENTE APÓS:**

```
        depois = core.rules_after_block(existing or "")
        if depois:
            # O bloco vai para o FIM (anatomia normativa). Regra que estava depois dele
            # passa a valer ANTES — inversao de precedencia, mudanca de comportamento que
            # o autor precisa autorizar.
            amostra = "\n".join(f"  {ln}" for ln in depois[:10])
            extra = f"\n  ... (+{len(depois) - 10})" if len(depois) > 10 else ""
            if not messagebox.askyesno(
                    "FlatDrop — regras depois do bloco",
                    f"{target}\n\nEstas regras estao DEPOIS do bloco gerenciado:\n"
                    f"{amostra}{extra}\n\nO bloco sera movido para o fim do arquivo, entao "
                    "elas passam a valer ANTES dele — o bloco ganha a palavra final.\n\n"
                    "Continuar?"):
                return
```

## Edição 11 — `tests/test_core.py` · quatro testes novos

**Inserir ao FIM do arquivo:**

```


def _repo_com_curadoria_manual(tmp_path):
    """Arvore minima com regra manual FORA do bloco — o caso que o gerador nao enxergava."""
    (tmp_path / "logs").mkdir()
    (tmp_path / "meta").mkdir()
    for rel in ("logs/a.md", "logs/b.md", "meta/x.md", "INSTRUCOES.md", "run.py"):
        (tmp_path / rel).write_text("x\n", encoding="utf-8")
    (tmp_path / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
    texto = ("# comentario do autor\n"
             "logs/*\nmeta/*\nINSTRUCOES.md\n"
             "# >>> flatdrop-editor\n# (sem alteracoes)\n# <<<\n")
    (tmp_path / ".flatdropignore").write_text(texto, encoding="utf-8")
    return texto


def _bloco(texto):
    _pre, bloco, _pos = core._split_managed(texto)
    return [ln for ln in bloco.splitlines()[1:-1]]


def test_bloco_nao_duplica_curadoria_manual(tmp_path):
    """Salvar sem mexer em nada nao copia para dentro o que ja esta fora (wo0046)."""
    texto = _repo_com_curadoria_manual(tmp_path)
    out = core.build_flatdropignore(tmp_path, core.ScanConfig(), {}, existing_text=texto)
    assert _bloco(out) == ["# (sem alteracoes)"]


def test_destravar_vence_linha_manual(tmp_path):
    """Destravar pasta fechada a mao emite o "!" que a vence — antes era desfeito calado."""
    texto = _repo_com_curadoria_manual(tmp_path)
    out = core.build_flatdropignore(tmp_path, core.ScanConfig(), {},
                                    existing_text=texto, locks={"logs": False})
    assert _bloco(out) == ["!logs/*"]


def test_marcar_arquivo_em_pasta_fechada_a_mao(tmp_path):
    """So o resgate do arquivo marcado, sem as duplicatas da pasta (wo0046)."""
    texto = _repo_com_curadoria_manual(tmp_path)
    out = core.build_flatdropignore(tmp_path, core.ScanConfig(), {"logs/a.md": True},
                                    existing_text=texto, locks={"logs": True})
    assert _bloco(out) == ["!logs/a.md"]


def test_bloco_vai_para_o_fim_e_avisa(tmp_path):
    """Regra depois do bloco: o bloco sobe para o fim e rules_after_block a denuncia."""
    (tmp_path / "logs").mkdir()
    (tmp_path / "logs" / "a.md").write_text("x\n", encoding="utf-8")
    (tmp_path / "run.py").write_text("x\n", encoding="utf-8")
    texto = "# >>> flatdrop-editor\n!logs/*\n# <<<\nlogs/*\n"
    (tmp_path / ".flatdropignore").write_text(texto, encoding="utf-8")
    assert core.rules_after_block(texto) == ["logs/*"]
    out = core.build_flatdropignore(tmp_path, core.ScanConfig(), {}, existing_text=texto)
    linhas = [ln for ln in out.splitlines() if ln.strip()]
    assert linhas[-1] == core.FLATDROP_EDITOR_MARK_B      # o bloco e o ultimo conteudo
    assert linhas[0] == "logs/*"                          # a regra do autor subiu, intacta
```

---

## Fora de escopo

- **Rótulo `travada (manual)` na GUI** e **aviso de contrabarra** — são a wo0047.
- **Colapso automático de pasta.** A DEC-027 removeu o palpite; nada aqui o traz de volta.
- **Reescrever `.flatdropignore` de outros projetos.** Nada muda sem um salvamento explícito.

## Armadilhas desta WO

- **A edição 3 tem duas âncoras na mesma função** — aplique as duas; trocar só a assinatura
  quebra a chamada, e trocar só a chamada é `NameError`.
- **`closed_of` continua sondando o estado EFETIVO** (`full_in`), não a baseline: é ele que
  preserva o round-trip quando a trava não foi mexida nesta chamada. Só a comparação (`base_fechada`)
  usa a baseline. Trocar os dois é o erro fácil aqui.
- **A ordem `folder_lines + file_lines` continua importando** — vale a última regra que casa, e o
  resgate precisa vir depois da exclusão que o pegaria.
- **Os testes antigos do editor foram escritos contra a base git-pura.** Alguns podem passar a
  esperar bloco vazio onde antes esperavam linhas. Se um deles quebrar, **leia-o antes de mexer**:
  se ele afirmava a duplicação, corrija-o e **diga qual e por quê** no relatório; se afirmava outra
  coisa, **PARE e reporte**.
- Arquivos em **LF**; cole os blocos sem reindentar.

---

## Depois de aplicar — conferência antes do commit

- [ ] `git diff` mostra só `flatdrop/core.py`, `flatdrop/gui.py`, `tests/test_core.py`.
- [ ] `python -m pytest -q`: **82 + 4 = 86**, 0 erros (menos eventuais ajustes justificados nos
      testes antigos do editor — reporte cada um).
- [ ] **Invariante DEC-020:** nenhum dos quatro pontos protegidos foi tocado.
- [ ] **Smoke manual no Windows** — é onde esta WO se prova, porque a suíte não cobre tkinter:
      1. abrir o editor **neste repo**, salvar sem mexer em nada → o bloco deve encolher para
         `# (sem alteracoes)`? **Não**: aqui tudo está *dentro* do bloco, então as quatro regras
         devem ser re-emitidas, com `!meta/workorders/_TEMPLATE.md` presente. Confira isso.
      2. mover à mão uma das quatro regras para fora do bloco, salvar → ela deve **sumir** do
         bloco (a baseline já a faz) e continuar valendo.
      3. destravar `logs` → o bloco deve emitir `!logs/*`.
      4. escrever uma regra depois do bloco e salvar → o aviso aparece; ao aceitar, o bloco fica
         no fim e a regra sobe.

## Relatório de aplicação

O que foi feito · desvios · arquivos tocados · resultado da suíte · o commit · **o resultado dos
quatro passos do smoke manual**. Grave o MESMO relatório em `../AAMMDD-HHMM-code-flatdrop.txt`.
Diga também **quais testes antigos precisaram de ajuste e por quê** — é o dado que diz se o
contrato da DEC-016 esticou como previsto.

## Commit — blocos separados, mensagem SEM acento

```
git add flatdrop/core.py flatdrop/gui.py tests/test_core.py
```

```
git commit -m "fix(ignore): bloco gerenciado vira diff contra a curadoria manual (wo0046)" -m "A base de comparacao deixa de ser o git puro e passa a ser gitignore + flatdropignore sem o bloco. O gerador para de duplicar o que ja esta fora, passa a emitir o ! que vence linha manual, e o bloco e sempre reescrito no fim do arquivo (move-se o proprio bloco, nunca o texto do autor). A GUI avisa quando isso inverte a precedencia de uma regra. Fecha o bug aberto na 0.13.0. 4 testes novos."
```

```
git push
```
