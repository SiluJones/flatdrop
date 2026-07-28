# spec0028 — FIX-008: nome para de renomear ao trocar de raiz (regressão da persistência)

- **Tipo:** implementação (correção de bug de GUI). Roda `python -m pytest -q` (deve seguir
  verde; a GUI é validada por smoke manual). Versão-alvo: **0.7.1** (0.7.0 → 0.7.1).
- **Ordem:** aplicar DEPOIS da spec0027 (assume 0.7.0). Fix pequeno e independente.
- **Sintoma.** Após a persistência (spec0024), ao abrir a GUI o nome vem preenchido
  (correto). Mas ao **escolher outra pasta raiz** (ou um recente), o nome **não** é mais
  renomeado automaticamente para o nome da nova pasta, como acontecia antes.
- **Causa raiz (confirmada no código).** `_choose_root` e `_on_recent_selected` só
  auto-renomeiam `if not self._name_edited`. A flag `_name_edited` deve significar "o
  usuário digitou um nome à mão" (setada pelo bind `<Key>` do campo, `gui.py:469`). Mas em
  `_apply_settings_to_vars` (spec0024) eu também a marquei `True` ao **restaurar** o nome
  salvo — confundindo "nome restaurado" com "nome editado à mão". Resultado: a flag nasce
  `True` e o auto-rename nunca dispara.

## GUARDAS (DEC-020)

Fix isolado no `_apply_settings_to_vars`. `_build_cli_args`, `_generate_bat`, `_sources`,
`cli.py`: intocados. `git diff` confirma.

---

## Edit 1 — `flatdrop/gui.py`: não travar `_name_edited` ao restaurar

**Âncora exata:**
```
        if s.name:
            self.name_var.set(s.name)
            self._name_edited = True  # não deixar o _choose_root sobrescrever
```
Trocar por:
```
        if s.name:
            # Restaura o ultimo nome, mas NAO trava _name_edited: escolher outra raiz
            # (ou um recente) deve voltar a renomear automaticamente. Digitar no campo
            # ainda marca _name_edited (bind <Key>), entao um nome custom da sessao
            # persiste ao trocar de raiz. (FIX-008 — regressao da spec0024.)
            self.name_var.set(s.name)
```

## Edit 2 — `flatdrop/__init__.py`: bump

**Âncora exata:** `__version__ = "0.7.0"` → trocar por `__version__ = "0.7.1"`

## Edit 3 — `meta/DECISIONS.md`: registrar FIX-008

**Âncora exata** (última linha do bloco DEC-021):
```
Lógica verificada no sandbox contra a core real antes de virar spec.
```
Inserir DEPOIS (uma linha em branco antes):
```
## FIX-008 — Nome parava de renomear ao trocar de raiz (regressão da persistência)
**Data:** 2026-07-16 · **Origem:** spec0024 (persistência) · **Correção:** spec0028

**Sintoma.** Com a config restaurada ao abrir a GUI, escolher outra pasta raiz não
atualizava mais o campo de nome para o nome da nova pasta (antes atualizava).

**Causa raiz.** `_choose_root`/`_on_recent_selected` só auto-renomeiam quando
`_name_edited` é `False` (flag que significa "usuário digitou um nome"; setada pelo bind
`<Key>`). Em `_apply_settings_to_vars` a flag foi marcada `True` ao **restaurar** o nome
salvo, confundindo "restaurado" com "editado à mão" — então a flag nascia `True` e o
auto-rename nunca disparava.

**Correção.** Restaurar o nome salvo SEM tocar em `_name_edited`. Consequência: trocar de
raiz volta a renomear; um nome digitado na sessão (que marca a flag via `<Key>`) ainda
persiste ao trocar de raiz. Um nome custom restaurado deixa de ficar "travado" entre
sessões — comportamento desejado pelo autor. GUI não é coberta pela suíte → validação por
smoke manual.
```

## Edit 4 — `meta/CHANGELOG.md`: entrada [0.7.1]

**Âncora exata:** `## [0.7.0] — 2026-07-16`
Inserir ANTES dela:
```
## [0.7.1] — 2026-07-16

### Corrigido
- **Nome volta a renomear ao trocar de raiz** (FIX-008). A persistência (0.6.0) travava o
  campo de nome ao restaurar a config, confundindo "nome restaurado" com "nome editado à
  mão"; escolher outra raiz não atualizava mais o nome. Agora o nome salvo é restaurado sem
  travar a flag `_name_edited`, então trocar de raiz renomeia de novo — e um nome digitado
  na sessão ainda é preservado.

```

## Edit 5 — `meta/STATUS.md`: refletir 0.7.1

**Âncora exata:**
```
  menos sensível); `.bat` intocado. Versão **0.7.0**, **62 testes**. Próxima = corrigir o
  nome ao trocar de raiz (FIX-008, spec0028) e multi-raiz na GUI.
```
Trocar por:
```
  menos sensível); `.bat` intocado. Versão **0.7.0**, **62 testes**.
- **(2026-07-16, spec0028 aplicada) FIX-008:** o nome volta a renomear ao trocar de raiz
  (regressão da persistência corrigida). Versão **0.7.1**. Próxima = multi-raiz na GUI.
```

---

## O que testar

- **Automatizado** (`python -m pytest -q`): segue **62 verdes** (mudança só de GUI, não
  toca a core).
- **Smoke manual (Windows) — o que importa:**
  1. Rodar a GUI (com uma config já salva de antes). O nome vem preenchido.
  2. Clicar "Procurar…" e escolher **outra** pasta raiz → o nome **atualiza** para o nome
     da nova pasta. Idem ao escolher um **recente** no Combobox.
  3. Digitar um nome à mão, depois trocar de raiz → o nome **digitado permanece** (não é
     sobrescrito).
- **`git diff`:** só `_apply_settings_to_vars` mudou; caminho do `.bat` intocado.

## Commit sugerido (sem acento)

```
git add flatdrop/gui.py flatdrop/__init__.py meta/DECISIONS.md meta/CHANGELOG.md meta/STATUS.md meta/specs/260715-spec0028-fix-name-rename.md & git commit -m "fix(gui): nome volta a renomear ao trocar de raiz (FIX-008)" -m "A persistencia (spec0024) travava _name_edited ao restaurar o nome salvo, confundindo restaurado com editado a mao; trocar de raiz nao renomeava mais. Restaura o nome sem travar a flag; digitar no campo ainda marca a flag e preserva o nome custom da sessao. Bump 0.7.1."
```
