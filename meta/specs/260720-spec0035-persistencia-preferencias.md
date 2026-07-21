# spec0035 — FIX-010: preferências persistem mesmo abrindo pelo atalho + padrões de fábrica

- **Tipo:** implementação (GUI + settings). Roda `python -m pytest -q` (segue verde; GUI →
  smoke manual). Versão-alvo: **0.10.1** (0.10.0 → 0.10.1).
- **Data:** 2026-07-20.
- **Sintoma.** Abrindo a GUI pelo atalho "abrir GUI", **nenhuma** config volta — renomeação,
  opções, tipos, separador, tudo reseta. O autor quer essas **preferências** persistentes
  entre projetos (independe do `.bat`/localização).
- **Causa raiz (confirmada).** A persistência (spec0024) salva/restaura tudo, mas a spec0030
  pôs no topo do `_apply_settings_to_vars` um `if self._start_dir: return` que começa **100%
  limpo** quando há `--start-dir` (o atalho passa isso). Foi longe demais: o certo é limpar
  só a **localização** (raiz/nome/multi-fonte, que é do projeto) e **manter as preferências**.
- **DEC-020:** só GUI/settings. Não toca `_build_cli_args`/`_generate_bat`/`_sources`/`cli.py`.

---

## Edit 1 — `gui.py`: separar preferências (sempre) de localização (sem --start-dir)

**Âncora exata** (o método `_apply_settings_to_vars` inteiro):
```
    def _apply_settings_to_vars(self) -> None:
        """Sobrescreve os valores iniciais dos widgets com a última config salva.

        Guardas: nenhum valor inválido do disco chega aos widgets — assim o .bat
        gerado a partir da tela sempre serializa uma config válida.
        """
        # Atalho "abrir GUI" (--start-dir presente): começa LIMPO — não restaura a
        # última sessão. O atalho é genérico e copiado para pastas variadas;
        # restaurar o projeto anterior faria "Procurar…" abrir no lugar errado
        # (a raiz restaurada venceria a semente). O Combobox de Recentes segue
        # disponível (nada se perde). Rodar a GUI sem --start-dir restaura como
        # antes. (spec0030 — espelha ASU spec0012.)
        if self._start_dir:
            return
        s = self._settings
        if s.root:
            self.root_var.set(s.root)
        if s.name:
            # Restaura o ultimo nome, mas NAO trava _name_edited: escolher outra raiz
            # (ou um recente) deve voltar a renomear automaticamente. Digitar no campo
            # ainda marca _name_edited (bind <Key>), entao um nome custom da sessao
            # persiste ao trocar de raiz. (FIX-008 — regressao da spec0024.)
            self.name_var.set(s.name)
        # dest só é aceito se for uma pasta real; senão fica o default (Downloads).
        if s.dest and Path(s.dest).is_dir():
            self.dest_var.set(s.dest)
        self.mode_var.set(s.mode)          # já saneado para {collisions,all,fullpath}
        self.sep_var.set(s.sep)            # já saneado para não-vazio
        self.gitignore_var.set(s.read_gitignore)
        self.skip_sensitive_var.set(s.skip_sensitive)
        self.manifest_var.set(s.write_manifest)
        self.tree_var.set(s.write_tree)
        self.root_in_name_var.set(s.root_in_name)
        self.clear_var.set(s.clear_dest)
        self.also_md_var.set(s.also_md)
        self.also_md_root_var.set(s.also_md_root)
        # allowlist reconstruída do delta contra os defaults ATUAIS.
        defaults = set(C.DEFAULT_EXTENSIONS)
        self._selected_exts = (defaults | set(s.ext_added)) - set(s.ext_removed)
```
Trocar por:
```
    def _apply_settings_to_vars(self) -> None:
        """Sobrescreve os valores iniciais dos widgets com a última config salva.

        PREFERÊNCIAS (renomeação, opções, tipos, separador, destino) são SEMPRE
        restauradas — inclusive abrindo pela GUI pelo atalho "abrir GUI" —, porque
        o autor quer a config montada persistente entre projetos (FIX-010). Só a
        LOCALIZAÇÃO (raiz, nome, multi-fonte, que é do projeto) NÃO é restaurada
        quando há --start-dir: o atalho é copiado para pastas variadas e restaurar
        o projeto anterior faria "Procurar…" abrir no lugar errado. Guardas: nenhum
        valor inválido do disco chega aos widgets.
        """
        s = self._settings
        # --- Preferências: sempre ---
        self.mode_var.set(s.mode)          # já saneado para {collisions,all,fullpath}
        self.sep_var.set(s.sep)            # já saneado para não-vazio
        self.gitignore_var.set(s.read_gitignore)
        self.skip_sensitive_var.set(s.skip_sensitive)
        self.clear_var.set(s.clear_dest)
        self.manifest_var.set(s.write_manifest)
        self.tree_var.set(s.write_tree)
        self.root_in_name_var.set(s.root_in_name)
        # allowlist reconstruída do delta contra os defaults ATUAIS.
        defaults = set(C.DEFAULT_EXTENSIONS)
        self._selected_exts = (defaults | set(s.ext_added)) - set(s.ext_removed)
        # destino é preferência (não é do projeto): só se for uma pasta real.
        if s.dest and Path(s.dest).is_dir():
            self.dest_var.set(s.dest)

        # --- Localização: só quando NÃO aberto pelo atalho "abrir GUI" ---
        if self._start_dir:
            return
        if s.root:
            self.root_var.set(s.root)
        if s.name:
            # NAO trava _name_edited: trocar de raiz deve voltar a renomear
            # (bind <Key> marca a flag quando o usuario digita). (FIX-008)
            self.name_var.set(s.name)
        self.also_md_var.set(s.also_md)
        self.also_md_root_var.set(s.also_md_root)
```

## Edit 2 — `gui.py`: método `_reset_defaults` (padrões de fábrica)

**Âncora exata** (fim do `_apply_settings_to_vars` recém-trocado — a última linha nova):
```
        self.also_md_var.set(s.also_md)
        self.also_md_root_var.set(s.also_md_root)
```
Inserir DEPOIS (novo método):
```

    def _reset_defaults(self) -> None:
        """Volta a config ao padrão de fábrica e apaga o salvo (menu Ferramentas).
        Repinta só as PREFERÊNCIAS; a localização atual na tela (raiz/nome/multi-
        fonte) fica como está. Os recentes são mantidos (histórico, não config).
        (spec0035)"""
        if not messagebox.askyesno(
            "FlatDrop",
            "Restaurar as configurações ao padrão de fábrica? A config salva será "
            "apagada (os recentes são mantidos)."):
            return
        self._settings = settings_store.Settings(
            recent_roots=self._settings.recent_roots)
        settings_store.save_settings(self._settings)
        s = self._settings
        self.mode_var.set(s.mode)
        self.sep_var.set(s.sep)
        self.gitignore_var.set(s.read_gitignore)
        self.skip_sensitive_var.set(s.skip_sensitive)
        self.clear_var.set(s.clear_dest)
        self.manifest_var.set(s.write_manifest)
        self.tree_var.set(s.write_tree)
        self.root_in_name_var.set(s.root_in_name)
        self._selected_exts = set(C.DEFAULT_EXTENSIONS)
        self._update_types_summary()
        self.status.config(text="Configurações restauradas ao padrão de fábrica.")
```

## Edit 3 — `gui.py`: item no menu Ferramentas

**Âncora exata:**
```
        tools.add_command(label="Gerar atalho da UI…",
                          command=self._generate_open_gui_bat)
        menubar.add_cascade(label="Ferramentas", menu=tools)
```
Trocar por:
```
        tools.add_command(label="Gerar atalho da UI…",
                          command=self._generate_open_gui_bat)
        tools.add_command(label="Restaurar padrões de fábrica…",
                          command=self._reset_defaults)
        menubar.add_cascade(label="Ferramentas", menu=tools)
```

## Edit 4 — `flatdrop/__init__.py`: bump

**Âncora exata:** `__version__ = "0.10.0"` → trocar por `__version__ = "0.10.1"`

## Edit 5 — `meta/DECISIONS.md`: registrar FIX-010

**Âncora exata** (última linha do bloco FIX-009):
```
coluna global morta. GUI não é coberta pela suíte → validação por smoke manual.
```
Inserir DEPOIS (uma linha em branco antes):
```
## FIX-010 — Atalho "abrir GUI" descartava as preferências salvas
**Data:** 2026-07-20 · **Origem:** spec0030 · **Correção:** spec0035

**Sintoma.** Abrindo a GUI pelo atalho "abrir GUI", nenhuma config voltava (renomeação,
opções, tipos, separador) — tudo resetava.

**Causa raiz.** A spec0030, para semear a navegação, pôs `if self._start_dir: return` no
topo de `_apply_settings_to_vars` — começava 100% limpo com `--start-dir`, jogando fora
também as preferências.

**Correção.** Separar **preferências** (renomeação/opções/tipos/separador/destino), que são
SEMPRE restauradas, da **localização** (raiz/nome/multi-fonte), que só é restaurada sem
`--start-dir`. Assim a config montada persiste entre projetos e o atalho ainda abre no lugar
certo. Adicionado um "Restaurar padrões de fábrica…" no menu Ferramentas (apaga o salvo,
mantém os recentes). **Lição:** "começar limpo" pelo atalho vale para a LOCALIZAÇÃO, não
para as preferências. Persistência é só-GUI (DEC-020); nada disto toca o `.bat`.
```

## Edit 6 — `meta/CHANGELOG.md`: entrada [0.10.1]

**Âncora exata:** `## [0.10.0] — 2026-07-20`
Inserir ANTES dela:
```
## [0.10.1] — 2026-07-20

### Corrigido
- **Preferências voltam a persistir abrindo pelo atalho (FIX-010, spec0035).** A semente de
  navegação (0.8.0) fazia a GUI começar 100% limpa quando aberta pelo atalho "abrir GUI",
  descartando renomeação/opções/tipos/separador salvos. Agora só a **localização**
  (raiz/nome/multi-fonte) reseta pelo atalho; as **preferências** são sempre restauradas.

### Adicionado
- **Menu Ferramentas → "Restaurar padrões de fábrica…" (spec0035).** Volta a config ao
  padrão e apaga o salvo (mantém os recentes). Só GUI; `.bat` intocado (DEC-020).

```

## Edit 7 — `meta/STATUS.md`: refletir 0.10.1

**Âncora exata** (bloco da nota de revisão, inteiro):
```
> **Mudanças nesta revisão (2026-07-20):** **layout da GUI reorganizado em duas colunas**
> (spec0034, 0.10.0) — Raiz+Nome na mesma linha, Renomeação|Opções e Tipos|Ignore lado a
> lado, e o **console de saída de volta à vista**. Antes, nesta leva: menu Ferramentas →
> "Gerar atalho da UI…" (0.9.0), Recentes compacto (0.9.1) e FIX-009 do layout (0.9.2).
> Versão **0.10.0**, **66 testes verdes**. Só rearranjo de UI; RUN `.bat` intocado
> (DEC-020). **Pendente (autorizado, a desenhar):** checkbox para nomear `_MANIFEST`/`_TREE`
> com o nome da pasta no fim (default-ON; toca `cli.py`/`_build_cli_args` para paridade —
> DEC-020). **Frente candidata maior:** multi-raiz na GUI (decisão A/B pendente).
```
Trocar por:
```
> **Mudanças nesta revisão (2026-07-20):** **FIX-010** (spec0035, 0.10.1) — preferências
> (renomeação/opções/tipos/separador) voltam a persistir mesmo abrindo pela GUI pelo atalho;
> só a localização reseta. Novo "Restaurar padrões de fábrica…" no menu Ferramentas. Antes,
> nesta leva: layout em duas colunas (0.10.0), gerar atalho da UI (0.9.0), Recentes compacto
> (0.9.1), FIX-009 do layout (0.9.2). Versão **0.10.1**. Só GUI/settings; RUN `.bat`
> intocado (DEC-020). **Pendente (autorizado):** spec0036 — nomear `_MANIFEST`/`_TREE` com
> o nome da pasta (default-ON; toca `cli.py`/`_build_cli_args`). **Frente maior:** multi-raiz
> (decisão A/B pendente).
```

---

## O que testar

- **Automatizado:** segue **66 verdes** (só GUI/settings).
- **Smoke manual (Windows):** (1) montar config (renomeação/opções/tipos), Executar, fechar,
  abrir **pelo atalho "abrir GUI"** → as preferências voltam, mas Raiz vem vazia (semente
  ainda funciona). (2) Menu Ferramentas → "Restaurar padrões de fábrica…" → volta ao padrão
  natural, recentes mantidos. (3) Rodar `run.py` sem `--start-dir` → raiz/nome também voltam.
- **`git diff`:** só `gui.py` + `__init__` + meta-docs. `.bat` e seu gerador intocados.

## Commit sugerido (sem acento)

```
git add flatdrop/gui.py flatdrop/__init__.py meta/DECISIONS.md meta/CHANGELOG.md meta/STATUS.md meta/specs/260720-spec0035-persistencia-preferencias.md & git commit -m "fix(gui): preferencias persistem mesmo pelo atalho (FIX-010) + padroes de fabrica" -m "spec0030 comecava 100% limpo com --start-dir, jogando fora renomeacao/opcoes/tipos salvos. Agora so a localizacao (raiz/nome/multi-fonte) reseta pelo atalho; preferencias sempre restauradas. Novo menu Ferramentas > Restaurar padroes de fabrica (apaga salvo, mantem recentes). So GUI/settings; .bat intocado. Bump 0.10.1."
```
