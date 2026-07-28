# wo0042 — Trava por pasta: parte da GUI (coluna nova) + fecho da feature

**Data:** 2026-07-28 · **Autor:** chat · **Aplicar com:** `/apply-wo meta/workorders/260728-wo0042-trava-na-gui.md`

> **Parte 2 de 2** (a parte 1 e a wo0041, commit `d631230`, suite 75 verdes).
> Mexe em CODIGO e na GUI. Rode `python -m pytest -q` **e** peca o smoke manual: a suite
> nao cobre tkinter. Aqui a feature fica visivel — logo, e aqui que entram bump e CHANGELOG.

## O que esta WO faz

Poe na tela o unico dado que faltava. O editor ganha uma **segunda coluna**, so para pastas,
que responde: *arquivo novo aqui entra?* Os checkboxes continuam exatamente como sao — inclusive
o da pasta, que segue sendo o atalho de marcar/desmarcar todos os filhos e **nao mexe na trava**.

**Regra que NAO deve ser implementada:** nada de "marcar um filho abre a trava sozinho". Nao
precisa e seria inferencia — foi medido: numa pasta travada, marcar um filho ja gera o resgate
pontual (`!pasta/x.md`), o arquivo vem, e o arquivo novo continua fora. A trava decide **so** o
futuro; o checkbox decide **so** o presente. Se alguem sentir vontade de acoplar os dois, e sinal
de que a coluna esta mal rotulada — arrume o rotulo, nao a semantica.

## Fora de escopo

- Teto de nomes do `_TREE` (`+N mais`): proxima frente, WO propria.
- `flatdrop/cli.py`, `gui._build_cli_args`, `gui._generate_bat`, `gui._sources`: **intocados**
  (DEC-020). Se algo parecer exigir isso, **PARE e reporte**.

---

## Edicao 1 — `flatdrop/core.py`: expor a sonda da trava

**Ancora** (linha final de `folder_effective_state`, logo antes do `build_flatdropignore`):

```python
def build_flatdropignore(root, cfg: ScanConfig, wants: dict[str, bool],
```

**Inserir ANTES dela:**

```python
def folder_is_closed(root, cfg: ScanConfig, rel_dir: str, probes=None) -> bool:
    """A trava desta pasta esta FECHADA? — ou seja: um arquivo NOVO aqui deixaria de subir?

    Usa a MESMA sonda que o ``build_flatdropignore`` usa por dentro (DEC-027): pergunta aos
    ignores o que eles fariam com um arquivo que nao existe. E o unico jeito honesto de
    descobrir, porque ``pasta/*`` de proposito nao casa ``pasta/`` como diretorio — sondar a
    pasta devolveria "aberta" justamente para as que o proprio editor fechou.

    A GUI chama isto ao abrir o editor, para pintar a coluna da trava no estado atual.
    """
    base_in, _source = probes or _ignore_probes(Path(root), cfg)
    return not base_in(f"{rel_dir}/{FLATDROP_PROBE}" if rel_dir else FLATDROP_PROBE, False)


def build_flatdropignore(root, cfg: ScanConfig, wants: dict[str, bool],
```

## Edicao 2 — `flatdrop/gui.py`: glifos da trava

**Ancora:**

```python
_GLYPH = {True: "☑", False: "☐", None: "▣"}  # checked / unchecked / partial
```

**Substituir por:**

```python
_GLYPH = {True: "☑", False: "☐", None: "▣"}  # checked / unchecked / partial
# Rotulos da coluna da trava (wo0042). ASCII de proposito: o console do Windows em cp1252 ja
# nos mordeu uma vez, e este texto tambem aparece em mensagem de erro.
_LOCK_TXT = {False: "entra", True: "travada"}
```

## Edicao 3 — `flatdrop/gui.py`: a coluna

**Ancora:**

```python
        self.tree = ttk.Treeview(self, columns=("chk",), selectmode="browse")
        self.tree.heading("#0", text="Arquivo / pasta")
        self.tree.heading("chk", text="No Projeto")
        self.tree.column("chk", width=90, anchor="center", stretch=False)
```

**Substituir por:**

```python
        self.tree = ttk.Treeview(self, columns=("chk", "lock"), selectmode="browse")
        self.tree.heading("#0", text="Arquivo / pasta")
        self.tree.heading("chk", text="No Projeto")
        self.tree.column("chk", width=90, anchor="center", stretch=False)
        # Coluna da trava (wo0042/DEC-027): so pastas. Responde "arquivo novo aqui entra?".
        # E deliberadamente separada do checkbox — sao duas perguntas diferentes.
        self.tree.heading("lock", text="Arquivo novo")
        self.tree.column("lock", width=110, anchor="center", stretch=False)
```

## Edicao 4 — `flatdrop/gui.py`: estado inicial da trava e legenda

**Ancora:**

```python
        self.probes = core._ignore_probes(self.root_dir, cfg)
        self.st: dict[str, dict] = {}
        self.folder_override: dict[str, bool] = {}
```

**Substituir por:**

```python
        self.probes = core._ignore_probes(self.root_dir, cfg)
        # A dupla (base_in, source): `source` diz DE ONDE veio o ignore, e e como a coluna da
        # trava distingue "travada por mim" de "travada (git)".
        self.base_in, self.source = self.probes
        self.st: dict[str, dict] = {}
        self.folder_override: dict[str, bool] = {}
        # Travas MEXIDAS nesta sessao do editor. O que nao foi tocado nao entra aqui: o core
        # deriva do estado atual dos ignores, e e assim que o round-trip se preserva.
        self.locks: dict[str, bool] = {}
```

**Ancora** (a legenda do rodape):

```python
        self.info = ttk.Label(bar, text="", foreground="#888")
```

**Substituir por:**

```python
        self.info = ttk.Label(bar, foreground="#888", text=(
            "Coluna 'No Projeto': este arquivo sobe.  |  Coluna 'Arquivo novo': clique para "
            "travar a pasta — travada, um arquivo criado depois NAO sobe."))
```

## Edicao 5 — `flatdrop/gui.py`: pintar a trava ao popular

**Ancora:**

```python
            name = rel.rsplit("/", 1)[-1] + note
            iid = self.tree.insert(parent_iid, "end", text=name, values=(_GLYPH[want],))
            self.st[iid] = dict(path=rel, is_dir=is_dir, base_in=base_in,
                                allowed=allowed, sens=sens, loaded=not is_dir, want=want)
```

**Substituir por:**

```python
            name = rel.rsplit("/", 1)[-1] + note
            # Arquivo nao tem trava — a coluna fica vazia na linha dele.
            fechada = core.folder_is_closed(self.root_dir, self.cfg, rel, self.probes) if is_dir else None
            if is_dir and rel in self.locks:
                fechada = self.locks[rel]
            iid = self.tree.insert(parent_iid, "end", text=name,
                                   values=(_GLYPH[want], self._lock_txt(rel, fechada, is_dir)))
            self.st[iid] = dict(path=rel, is_dir=is_dir, base_in=base_in,
                                allowed=allowed, sens=sens, loaded=not is_dir, want=want,
                                lock=fechada)
```

## Edicao 6 — `flatdrop/gui.py`: rotulo, clique e toggle da trava

**Ancora:**

```python
    def _on_click(self, e):
        region = self.tree.identify("region", e.x, e.y)
        col = self.tree.identify_column(e.x)
        row = self.tree.identify_row(e.y)
        if row and region == "cell" and col == "#1":
            self._toggle(row)
            return "break"
```

**Substituir por:**

```python
    def _lock_txt(self, rel: str, fechada, is_dir: bool) -> str:
        """Rotulo da coluna da trava. Diz tambem DE ONDE veio, quando nao foi o autor:
        pasta escondida pelo .gitignore abre travada, e isso precisa ficar visivel — senao
        parece que o editor travou sozinho."""
        if not is_dir:
            return ""
        de_git = self.source(rel, True) == "gitignore"
        if fechada:
            return "travada (git)" if de_git and rel not in self.locks else _LOCK_TXT[True]
        return "liberada" if de_git else _LOCK_TXT[False]

    def _on_click(self, e):
        region = self.tree.identify("region", e.x, e.y)
        col = self.tree.identify_column(e.x)
        row = self.tree.identify_row(e.y)
        if row and region == "cell" and col == "#1":
            self._toggle(row)
            return "break"
        if row and region == "cell" and col == "#2":
            self._toggle_lock(row)
            return "break"

    def _toggle_lock(self, iid):
        """Vira a trava da pasta. NAO mexe nos checkboxes dos filhos, de proposito: a trava
        decide o futuro, o checkbox decide o presente (DEC-027)."""
        s = self.st.get(iid)
        if not s or not s["is_dir"]:
            return
        nova = not bool(s["lock"])
        s["lock"] = nova
        self.locks[s["path"]] = nova
        self.tree.set(iid, "lock", self._lock_txt(s["path"], nova, True))
```

> `self.source` vem do desempacotamento feito na Edicao 4. Conferido: hoje o editor guarda so
> `self.probes` e nunca usa `source` — por isso o desempacotamento entra junto.

## Edicao 7 — `flatdrop/gui.py`: mandar as travas ao salvar

**Ancora:**

```python
        text = core.build_flatdropignore(self.root_dir, self.cfg, wants, existing_text=existing)
```

**Substituir por:**

```python
        text = core.build_flatdropignore(self.root_dir, self.cfg, wants,
                                         existing_text=existing, locks=self.locks)
```

## Edicao 8 — teste do helper (`tests/test_core.py`)

Acrescente ao fim:

- `test_folder_is_closed_le_o_estado_atual` — pasta normal devolve `False`; com `pasta/*` no
  `.flatdropignore` devolve `True`; com `pasta/*` + `!pasta/x.md` **continua** `True` (o resgate
  de um arquivo nao abre a pasta); pasta escondida pelo `.gitignore` devolve `True`.

## Edicao 9 — versao e CHANGELOG

`flatdrop/__init__.py`: `0.12.0` → `0.13.0`.

**Ancora** em `meta/CHANGELOG.md`:

```
## [0.12.0] — 2026-07-28
```

**Inserir ANTES dela:**

```
## [0.13.0] — 2026-07-28

### Adicionado
- **Trava por pasta no editor de `.flatdropignore` (DEC-027, wo0041 + wo0042).** Uma coluna
  nova, só para pastas, responde a única pergunta que a interface não sabia fazer: *arquivo
  novo aqui entra?* Travada, o gerador escreve `pasta/*` e resgata por `!` o que estiver
  marcado; aberta, escreve só a exclusão do que foi desmarcado. Pasta escondida pelo
  `.gitignore` abre como `travada (git)`, e liberá-la escreve `!pasta/*`.

### Mudado
- **O editor não adivinha mais a intenção da pasta.** Desmarcar todos os filhos de uma pasta
  aberta agora escreve uma linha por arquivo, e não mais `pasta/`. Fechar a pasta virou um gesto
  próprio — o da trava. O checkbox da pasta continua sendo o atalho de marcar/desmarcar todos.
```

## Edicao 10 — `meta/CEREBRO.md`: fechar o buraco que deixou passar o erro de 28/07

**Ancora** (na secao do bloco de fecho de turno):

```
2. **Estado** — uma linha: versão/fase, resultado da suíte (`python -m pytest -q`) quando houve mexida em código, e o commit, quando existir.
```

**Substituir por:**

```
2. **Estado** — uma linha: versão/fase, resultado da suíte (`python -m pytest -q`) quando houve mexida em código, e o commit, quando existir. **Todo dado desta linha vem de leitura FEITA NESTE TURNO.** Se algo não foi verificado agora, ou se verifica antes de escrever, ou se escreve "não verificado nesta rodada" — nunca se completa a linha de memória. Campo obrigatório é convite a preencher com o que se lembra, e o que se lembra é a expectativa do próprio turno anterior, não o repo.
```

**Ancora** (o titulo do principio 8, linha 42 — o da secao de principios, NAO o `## Verifica
antes de pedir um arquivo` que aparece mais abaixo; confira que casa 1x com o `###`):

```
### 8. Verifica antes de pedir arquivo
```

**Substituir por:**

```
### 8. Verifica antes de pedir arquivo — e antes de AFIRMAR

> Antes de dizer que algo está aplicado, pendente, quebrado ou verde, **leia a fonte nesta rodada**. Vale principalmente para o que você mesmo entregou no turno anterior: a expectativa de que o trabalho foi aplicado é uma previsão, não uma observação, e por dentro as duas se parecem. Se não deu para ler, diga que não verificou.
```

## Edicao 11 — `meta/IDEAS.md`: feedback ao kit

**Ancora** (primeiro item de «Feedback para o Kit»):

```
- **O kit ensina a regra `pasta/*` e não a segue.**
```

**Inserir ANTES dela:**

```
- **A regra "sua cópia não é a fonte da verdade" está longe do lugar onde ela é quebrada.** No
  template ela vive em «Regras de higiene»; o erro acontece ao preencher a linha **Estado** do
  bloco de fecho de turno, dezenas de linhas depois, e nada ali lembra de verificar. Aconteceu
  aqui em 28/07: o assistente afirmou que uma WO estava pendente **duas horas depois de trazer
  essa mesma regra do kit** — e havia dois `.txt` no mount dizendo o contrário, não lidos.
  Sugestão ao KCM: a regra pertence ao **campo**, não ao apêndice. Todo campo do bloco de fecho
  que afirme estado deveria trazer, na própria descrição, "vem de leitura feita neste turno".
  Regra sem gatilho no ponto de uso é decoração. (2026-07-28.)
- **Campo obrigatório em formulário induz confabulação.** O bloco de fecho pede **Estado** em
  todo turno. Quando não há leitura fresca, a saída de menor atrito é preencher com a memória —
  e a memória, logo depois de entregar um trabalho, é a *expectativa* de que ele foi aplicado.
  O formato deveria admitir "não verificado nesta rodada" como resposta de primeira classe, em
  vez de tratar o campo como sempre-preenchível. (2026-07-28.)
```

## Checklist de fecho

- [ ] `python -m pytest -q` verde (75 antes; diga o final).
- [ ] `git diff` conferido: `core.py` (1 funcao nova), `gui.py` (6 pontos), testes, versao,
      CHANGELOG, CEREBRO, IDEAS. `cli.py` / `_build_cli_args` / `_generate_bat` / `_sources`
      **intocados**.
- [ ] **Commit tambem** `meta/analises/260728-ANALISE-gerador-flatdropignore.md`, que ficou
      fora dos dois commits anteriores por estar fora do escopo deles. Agora e o escopo.
- [ ] **Smoke manual no Windows** (a suite nao cobre tkinter) — roteiro no fim desta WO.
- [ ] Commit sem acento, Conventional Commits.
- [ ] **Relatorio**: o que fez, desvios, arquivos tocados, suite, commit.

## Roteiro do smoke manual

1. `python run.py` → abrir o editor de `.flatdropignore`.
2. Uma pasta comum deve abrir com **`entra`**; uma pasta do `.gitignore`, com **`travada (git)`**.
3. Clicar na coluna «Arquivo novo» de uma pasta comum → vira `travada`. Salvar → o arquivo
   ganha `pasta/*`. Criar um arquivo novo dentro dela e pre-visualizar → **nao sobe**.
4. Reabrir o editor → a pasta deve voltar **travada** (e a sonda funcionando; se voltar `entra`,
   o round-trip quebrou: PARE e reporte).
5. Numa pasta travada, marcar um arquivo → salvar → sai `!pasta/arquivo.md` e ele sobe, mas o
   arquivo novo do passo 3 continua fora.
6. Numa pasta **aberta** com varios filhos, desmarcar pelo checkbox da PASTA → salvar → devem
   sair N linhas, **uma por arquivo**, e nenhum `pasta/*`. (E o pedido explicito do autor.)
7. Conferir que o que estava fora do bloco `# >>> flatdrop-editor` continua intacto.
