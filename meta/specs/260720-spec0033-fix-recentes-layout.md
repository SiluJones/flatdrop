# spec0033 — FIX-009: Recentes compacto sem coluna morta (sub-frame na linha da Raiz)

- **Tipo:** implementação (GUI, correção de layout). Roda `python -m pytest -q` (segue verde;
  mudança só de widget). Versão-alvo: **0.9.2** (0.9.1 → 0.9.2).
- **Data:** 2026-07-20 · **Origem:** spec0032.
- **Sintoma.** O botão "Recentes ▾" ficou feio: em vez de encolher a linha da Raiz e colar o
  botão ao lado de "Procurar…" (como no ASU), a interface ganhou uma **coluna dedicada** que
  deixou um monte de espaço inútil à direita de todas as linhas e alargou a janela.
- **Causa raiz.** A spec0032 pôs o "Recentes ▾" em `column=3` do grid **principal**. Como o
  grid do tkinter tem **colunas globais** (compartilhadas por todas as linhas) e todo o resto
  da UI usa `columnspan=3` (colunas 0–2), a coluna 4 sobra **vazia em cada linha** e o
  `columnconfigure(1, weight=1)` faz o Entry empurrar tudo para a direita.
- **Correção.** Agrupar Entry + "Procurar…" + "Recentes ▾" num **sub-frame** que ocupa
  col1–col2 (a mesma faixa que as outras linhas usam para Entry+botão). A grade principal
  volta a ter **3 colunas**; o Entry encolhe só o necessário para os dois botões caberem,
  colados à direita — como no ASU. As demais linhas ficam intactas.
- **DEC-020:** só GUI; o `.bat` e seu gerador não são tocados.

---

## Edit 1 — `gui.py`: linha da Raiz num sub-frame (remove a coluna global)

**Âncora exata:**
```
        # Pasta raiz (+ Recentes compacto na mesma linha, à direita — spec0032).
        ttk.Label(self, text="Pasta raiz *").grid(row=r, column=0, sticky="w")
        ttk.Entry(self, textvariable=self.root_var).grid(row=r, column=1, sticky="ew", padx=6)
        ttk.Button(self, text="Procurar…", command=self._choose_root).grid(row=r, column=2)
        self.recent_menu = tk.Menu(self, tearoff=0)
        self.recent_btn = ttk.Menubutton(
            self, text="Recentes ▾", menu=self.recent_menu)
        self.recent_btn.grid(row=r, column=3, padx=(6, 0))
        self._refresh_recent_menu()
        r += 1
```
Trocar por:
```
        # Pasta raiz — Entry + "Procurar…" + "Recentes ▾" agrupados num sub-frame,
        # tight à direita (spec0033/FIX-009). Antes (spec0032) o "Recentes ▾" ia
        # para a coluna 3 do grid PRINCIPAL; como as colunas do tkinter são globais
        # e o resto da UI usa columnspan=3 (colunas 0–2), a coluna 4 sobrava vazia
        # em toda linha e alargava a janela. O sub-frame mantém a grade em 3 colunas:
        # o Entry encolhe só o necessário para os dois botões caberem, como no ASU.
        ttk.Label(self, text="Pasta raiz *").grid(row=r, column=0, sticky="w")
        raiz = ttk.Frame(self)
        raiz.grid(row=r, column=1, columnspan=2, sticky="ew", padx=(6, 0))
        raiz.columnconfigure(0, weight=1)  # só o Entry expande
        ttk.Entry(raiz, textvariable=self.root_var).grid(row=0, column=0, sticky="ew")
        ttk.Button(raiz, text="Procurar…", command=self._choose_root).grid(
            row=0, column=1, padx=(6, 0))
        self.recent_menu = tk.Menu(self, tearoff=0)
        self.recent_btn = ttk.Menubutton(
            raiz, text="Recentes ▾", menu=self.recent_menu)
        self.recent_btn.grid(row=0, column=2, padx=(6, 0))
        self._refresh_recent_menu()
        r += 1
```

## Edit 2 — `flatdrop/__init__.py`: bump

**Âncora exata:** `__version__ = "0.9.1"` → trocar por `__version__ = "0.9.2"`

## Edit 3 — `meta/DECISIONS.md`: registrar FIX-009 (lição de layout)

**Âncora exata** (última linha do bloco FIX-008):
```
sessões — comportamento desejado pelo autor. GUI não é coberta pela suíte → validação por
smoke manual.
```
Inserir DEPOIS (uma linha em branco antes):
```
## FIX-009 — "Recentes ▾" criava coluna global morta (layout)
**Data:** 2026-07-20 · **Origem:** spec0032 · **Correção:** spec0033

**Sintoma.** O botão compacto de Recentes deixou um bloco de espaço vazio à direita de
todas as linhas e alargou a janela, em vez de só encolher a linha da Raiz.

**Causa raiz.** As colunas do grid do tkinter são **globais** (compartilhadas por todas as
linhas). Pôr o "Recentes ▾" em `column=3` do grid principal criou uma 4ª coluna que sobrava
vazia em cada linha (o resto da UI usa `columnspan=3`), e o `columnconfigure(1, weight=1)`
empurrava tudo à direita.

**Correção.** Agrupar os controles da linha (Entry + "Procurar…" + "Recentes ▾") num
**sub-frame** que ocupa col1–col2; a grade principal volta a 3 colunas e o Entry encolhe só
o necessário. **Lição (não regredir):** um controle extra em UMA linha do grid NÃO vai numa
coluna nova do grid principal — vai num sub-frame daquela linha, senão vira coluna global
morta. GUI não é coberta pela suíte → validação por smoke manual.
```

## Edit 4 — `meta/CHANGELOG.md`: entrada [0.9.2]

**Âncora exata:** `## [0.9.1] — 2026-07-20`
Inserir ANTES dela:
```
## [0.9.2] — 2026-07-20

### Corrigido
- **Layout do "Recentes ▾" (FIX-009, spec0033).** O botão compacto (0.9.1) tinha ido para
  uma coluna do grid principal; como as colunas do tkinter são globais, isso deixava espaço
  morto à direita de toda a interface e alargava a janela. Agora Entry + "Procurar…" +
  "Recentes ▾" ficam num sub-frame na linha da Raiz: a grade volta a 3 colunas e o Entry
  encolhe só o necessário para os botões caberem colados, como no ASU. Só GUI.

```

## Edit 5 — `meta/STATUS.md`: refletir 0.9.2

**Âncora exata** (bloco da nota de revisão, inteiro):
```
> **Mudanças nesta revisão (2026-07-20):** **Recentes** virou um botão compacto
> **"Recentes ▾"** na linha da Raiz (spec0032, 0.9.1), liberando a linha inteira que o
> Combobox ocupava. Antes, nesta leva: menu **Ferramentas → "Gerar atalho da UI…"**
> (spec0031, 0.9.0). Versão **0.9.1**, **66 testes verdes**. RUN `.bat` intocado (DEC-020).
> Nada quebrado. **Frente candidata:** **multi-raiz na GUI** (exige decisão A/B do autor
> antes de desenhar, ver "Decisão pendente").
```
Trocar por:
```
> **Mudanças nesta revisão (2026-07-20):** leva de conveniências de GUI, agora com o layout
> do Recentes corrigido. Menu **Ferramentas → "Gerar atalho da UI…"** (spec0031, 0.9.0);
> **Recentes** compacto como botão **"Recentes ▾"** na linha da Raiz (spec0032, 0.9.1); e o
> **FIX-009** (spec0033, 0.9.2) que tirou a coluna morta que o botão criava — Entry +
> botões num sub-frame, grade de volta a 3 colunas, como no ASU. Versão **0.9.2**,
> **66 testes verdes**. RUN `.bat` intocado (DEC-020). Nada quebrado. **Frente candidata:**
> **multi-raiz na GUI** (exige decisão A/B do autor antes de desenhar, ver "Decisão
> pendente").
```

---

## O que testar

- **Automatizado:** segue **66 verdes** (só widget).
- **Smoke manual (Windows) — é o ponto:** a janela **não** tem mais o espaço morto à direita;
  na linha da Raiz, o Entry é um pouco mais curto e **"Procurar…" + "Recentes ▾"** ficam
  colados, à direita, sem coluna dedicada. As demais linhas (Destino, Multi-fonte) seguem
  iguais. Clicar "Recentes ▾" lista os recentes; escolher preenche a Raiz.
- **`git diff`:** só `gui.py` (linha da Raiz), `__init__.py` e os meta-docs. `.bat` e seu
  gerador intocados.

## Merece print no README

A linha da Raiz corrigida (Entry curto + "Procurar…"/"Recentes ▾" colados), no lugar do
print antigo com a coluna morta. Só sinalizar.

## Commit sugerido (sem acento)

```
git add flatdrop/gui.py flatdrop/__init__.py meta/DECISIONS.md meta/CHANGELOG.md meta/STATUS.md meta/specs/260720-spec0033-fix-recentes-layout.md & git commit -m "fix(gui): Recentes compacto sem coluna morta (FIX-009)" -m "O Recentes na coluna 3 do grid principal criava uma coluna global vazia em toda a UI (colunas do tkinter sao globais) e alargava a janela. Agrupa Entry + Procurar + Recentes num sub-frame na linha da Raiz; grade volta a 3 colunas e o Entry encolhe so o necessario, como no ASU. So GUI; .bat intocado. Bump 0.9.2."
```
