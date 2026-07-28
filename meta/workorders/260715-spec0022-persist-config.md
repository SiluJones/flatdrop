# spec0022 — DESIGN: persistir configuração + pastas recentes (item C)

- **Tipo:** design (decisões + contrato). NÃO altera código. Gera **DEC-019** e prepara a
  spec de implementação (spec0023).
- **Data:** 2026-07-15
- **Versão-alvo:** 0.6.0 (funcionalidade nova, menor). A implementação (spec0023) faz o bump.
- **Escopo aprovado pelo autor:** os 4 pontos do item C, com **1 refinamento** no ponto de
  precedência (ver §4): a persistência é **só da GUI**; a CLI permanece pura.
- **Aplicação desta spec pelo Code:** apenas **um** edit em `meta/` — append de **DEC-019**
  ao fim de `meta/DECISIONS.md` (texto exato + âncora em §7). Sem tocar em código, sem testes
  (mudança só de doc; a rede é o `git diff`).

---

## 1. Onde gravar (aprovado)

Novo módulo `flatdrop/settings.py` com um resolvedor por plataforma, espelhando o padrão de
`core.default_downloads_dir()`:

- **Windows:** `%APPDATA%\FlatDrop\settings.json`
  (`os.environ.get("APPDATA")`; `%APPDATA%` está sempre no ambiente — **não** precisa de
  ctypes/Known Folder como o Downloads precisou). Fallback: `~/AppData/Roaming/FlatDrop`.
- **Linux/BSD:** `$XDG_CONFIG_HOME/flatdrop/settings.json` ou `~/.config/flatdrop/settings.json`.
- **macOS:** `~/Library/Application Support/FlatDrop/settings.json`.
- **Último recurso** (nada resolve): `~/.flatdrop/settings.json`.

Contrato do resolvedor: `settings_path() -> Path` (só devolve o caminho; **não** cria nada).

## 2. O que persistir (aprovado)

Exatamente o estado que hoje serializa no `.bat` (`_build_cli_args`), mais os recentes.
**A allowlist é gravada como DELTA vs `config.DEFAULT_EXTENSIONS`**, não como conjunto
inteiro — assim, se um default novo entrar numa versão futura, o usuário passa a recebê-lo
automaticamente (gravar o set congelado esconderia defaults novos). Isso reflete o
`added`/`removed` que o `_build_cli_args` já calcula.

Schema JSON (`version` para migração futura):

```json
{
  "version": 1,
  "last": {
    "root": "",
    "dest": "",
    "name": "",
    "mode": "collisions",
    "sep": "__",
    "ext_added": [],
    "ext_removed": [],
    "read_gitignore": true,
    "skip_sensitive": true,
    "write_manifest": true,
    "write_tree": false,
    "root_in_name": false,
    "clear_dest": true,
    "also_md": false,
    "also_md_root": ""
  },
  "recent_roots": []
}
```

Mapa campo → `tk.Var` da GUI (para o impl spec amarrar):
`root`→`root_var` · `dest`→`dest_var` · `name`→`name_var` · `mode`→`mode_var` ·
`sep`→`sep_var` · `ext_added`/`ext_removed`→`self._selected_exts` (reconstruído: defaults +
added − removed) · `read_gitignore`→`gitignore_var` · `skip_sensitive`→`skip_sensitive_var` ·
`write_manifest`→`manifest_var` · `write_tree`→`tree_var` · `root_in_name`→`root_in_name_var` ·
`clear_dest`→`clear_var` · `also_md`→`also_md_var` · `also_md_root`→`also_md_root_var`.

Fora de escopo (anotar como ideia, não implementar): geometria/posição da janela.

## 3. Recentes (aprovado)

- Lista `recent_roots`, **dedup**, **mais recente no topo**, **cap 8**.
- `Combobox` (readonly) ao lado do campo de raiz; escolher um item preenche `root_var`.
  Sem menu separado.
- Ao gravar: insere a raiz atual no topo, remove duplicata anterior, corta em 8.
- Ao carregar: **poda entradas cujo caminho não existe mais** (mantém a lista honesta).

## 4. Precedência — REFINAMENTO (persistência é só da GUI)

**Decisão:** a config salva é uma conveniência **exclusiva da GUI**. A **CLI não lê** o
`settings.json`.

Camadas (da mais fraca à mais forte):
`config.py` (defaults) → **config salva** (carregada nos widgets ao abrir a GUI) →
**edições ao vivo** do usuário na tela → **`.bat`/CLI** (não leem nem o settings nem os
recentes).

**Por quê (dois motivos de código, não estéticos):**
1. **Reprodutibilidade do `.bat`.** Um `.bat` é um snapshot fechado. Se a CLI absorvesse
   config do `%APPDATA%`, o mesmo `.bat` se comportaria diferente em outra máquina ou após
   o usuário mexer na GUI — quebra o propósito do gerador de `.bat`.
2. **Armadilha do argparse.** `_build_cli_args` só emite um flag quando difere do default
   (`--sep` só se `!= __`, `--dest` só se `!= default_downloads_dir()`, etc.). Sem trocar
   todos os defaults por sentinelas, a CLI não tem como distinguir "flag digitado" de
   "flag default" — logo "config salva sobrepõe só o não-especificado" não é implementável
   de forma limpa. Escopo só-GUI dispensa esse problema por inteiro.

Consequência: `flatdrop/cli.py` **não muda** nesta funcionalidade.

## 5. Contrato do módulo `flatdrop/settings.py` (para a spec0023)

Puro, testável sem tkinter. **Nunca** deixa uma falha de I/O quebrar o app.

- `settings_path() -> Path` — resolve o caminho por plataforma (§1). Não cria nada.
- `load_settings() -> Settings` — **nunca lança**. Envolve `read_text` + `json.loads` em
  try/except (`FileNotFoundError`, `json.JSONDecodeError`, `OSError`) → devolve `Settings`
  com defaults. Chaves ausentes/desconhecidas toleradas (merge sobre defaults); campo com
  tipo estranho cai no default daquele campo. `version` diferente → tenta ler o que dá,
  senão defaults.
- `save_settings(s: Settings) -> bool` — cria o diretório (`mkdir(parents=True,
  exist_ok=True)`), grava em arquivo temporário no MESMO diretório e faz `os.replace`
  (**escrita atômica** — nunca deixa JSON meio-escrito). Em `OSError`
  (somente-leitura/travado): engole, loga UMA vez em `stderr`, devolve `False` — a
  persistência se desliga em silêncio e a GUI segue. Devolve `True` no sucesso.
- `Settings` = dataclass (ou dict tipado) com o schema de §2. Helpers:
  `push_recent(root: str)` (dedup + cap 8) e conversão delta↔set da allowlist.

## 6. Integração na GUI (nível de design; âncoras exatas ficam na spec0023)

- **Carregar ao abrir:** em `App.__init__`, DEPOIS de construir os `tk.Var` (âncora: bloco
  que começa em `self.root_var = tk.StringVar()`), chamar novo `self._load_settings()` que
  sobrescreve os valores iniciais a partir de `load_settings().last`, com guardas:
  - `dest` vazio OU inexistente → `str(core.default_downloads_dir())`.
  - `root` inexistente → carrega a string mesmo assim (a validação de execução já trata; não
    inventar novo modo de falha).
  - allowlist → `self._selected_exts = defaults ∪ added − removed`.
- **Combobox de recentes:** ao lado do campo de raiz (linha de `root_var`). `readonly`,
  populado de `recent_roots`; on-select preenche `root_var`.
- **Gravar ao executar:** no handler de "Executar", APÓS execução bem-sucedida, chamar
  `self._persist_settings()` (captura o estado da tela em `Settings.last` + `push_recent`).
  Só no Executar (não no Pré-visualizar) — é o sinal claro de "esta config prestou".
- **CLI:** nenhuma mudança (§4).

## 7. Edit em `meta/` desta spec (aplicar EXATO)

Append ao **fim** de `meta/DECISIONS.md`. **Âncora semântica:** o último parágrafo do bloco
**FIX-007**, que termina na linha exata:

> `"otimizar" de volta para a árvore.`

Inserir DEPOIS dessa linha (com uma linha em branco antes):

```
## DEC-019 — Persistir config + recentes num settings.json de escopo só-GUI
**Data:** 2026-07-15 · **Status:** aceita (design; implementação na spec0023)

**Contexto.** A GUI reconstruía toda a configuração a cada abertura (raiz, saída, tipos,
flags), e não havia atalho para as pastas usadas com frequência. O item C pede persistir a
última config e uma lista de raízes recentes.

**Decisão.** Novo módulo `flatdrop/settings.py` grava um `settings.json` por plataforma
(`%APPDATA%\FlatDrop` no Windows, `~/.config/flatdrop` no Linux, `~/Library/Application
Support/FlatDrop` no macOS), espelhando `core.default_downloads_dir()`. Persiste o mesmo
estado que já serializa no `.bat`, com a **allowlist gravada como delta** (added/removed vs
`DEFAULT_EXTENSIONS`) para não congelar defaults futuros, mais `recent_roots` (dedup, cap 8,
mais recente no topo). A persistência é **exclusiva da GUI**: a CLI NÃO lê o arquivo.

**Consequência.** O `.bat` continua sendo um snapshot reproduzível (não absorve estado de
`%APPDATA%`) e evita-se a armadilha do argparse de distinguir flag-digitado de flag-default.
`load_settings` nunca lança (arquivo corrompido/ausente → defaults) e `save_settings` é
atômico (temp + `os.replace`); falha de escrita desliga a persistência em silêncio sem
derrubar a GUI. Precedência: defaults < config salva (carregada nos widgets) < edições ao
vivo < `.bat`/CLI. Geometria de janela fica de fora (ideia futura).
```

## 8. O que testar (na spec0023, quando houver código)

`settings.py` é puro → cobre-se por pytest (a GUI fica no smoke manual):
- **round-trip:** `save_settings` → `load_settings` devolve o mesmo estado.
- **arquivo ausente** → defaults, sem lançar.
- **JSON corrompido** (texto lixo) → defaults, sem lançar.
- **delta da allowlist:** com `DEFAULT_EXTENSIONS` simulando um default novo, o load entrega
  defaults+added−removed (o default novo aparece).
- **cap/dedup de recentes:** `push_recent` mantém 8, sem duplicata, topo = mais recente.
- **escrita atômica:** não resta arquivo temporário; falha de escrita → `False` sem exceção.
- **Windows:** comparar caminhos com `.as_posix()`, nunca `str(path)`.
- **Smoke manual (GUI):** abrir → campos vêm da última sessão; escolher recente preenche a
  raiz; executar → reabrir confirma que gravou; `dest` inexistente cai no Downloads.

## 9. Merece print no README

Após a spec0023: a linha da raiz com o **Combobox de recentes** aberto (mostra o atalho
novo). Não gerar imagem — só sinalizar a captura.

## 10. Próxima spec

**spec0023 (implementação):** cria `flatdrop/settings.py`, fia na GUI (`_load_settings`,
Combobox, `_persist_settings`), testes de §8, bump 0.6.0, CHANGELOG [0.6.0], STATUS
(item C fechado, próxima = multi-raiz na GUI). Âncoras exatas de `gui.py` fecham lá.
