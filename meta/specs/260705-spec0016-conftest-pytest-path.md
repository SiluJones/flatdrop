# spec0016 — `conftest.py` na raiz: fazer `pytest` puro encontrar o pacote

**Tipo:** código/infra de teste · **Alvos:** `conftest.py` (novo, na RAIZ do repo)
**Autor:** chat · **Aplicador:** Claude Code
**Depende de:** nada. Corrige um problema latente de path de teste (não é regressão da 0.3.1).

## Sintoma

Rodando `pytest` (puro) a partir da raiz do repo no Windows, a coleta falha:

```
collected 0 items / 2 errors
ERROR tests/test_cli.py  -> from flatdrop import cli  -> ModuleNotFoundError: No module named 'flatdrop'
ERROR tests/test_core.py -> from flatdrop import config as C -> ModuleNotFoundError: No module named 'flatdrop'
Interrupted: 2 errors during collection
```

## Causa raiz

Estrutura aninhada do repo (raiz `FlatDrop\flatdrop\`, pacote `flatdrop\` dentro,
`tests\` ao lado):

```
<raiz-do-repo>/
  flatdrop/            <- o pacote (core.py, cli.py, config.py, gui.py, __init__.py)
  tests/               <- test_core.py, test_cli.py  (fazem `from flatdrop import ...`)
  run.py               <- ajusta sys.path para a aplicação; os testes NÃO têm equivalente
```

Os testes importam `flatdrop` como pacote de topo, mas **nada insere a raiz do repo
no `sys.path`** durante a coleta do pytest. O `run.py` resolve isso para a aplicação
(`sys.path.insert(0, Path(__file__).resolve().parent)`), mas não há nada análogo para
os testes, e o projeto **não tem** `conftest.py`, `pyproject.toml`, `setup.py`,
`setup.cfg` nem `pytest.ini` (verificado no mount).

Por que "41 verdes" antes e erro agora: `python -m pytest` adiciona o diretório atual
ao `sys.path` (comportamento do `-m`), mascarando o problema. `pytest` puro **não**
faz isso. O docstring dos testes diz "rode com `pytest -q` a partir da raiz" — a
correção faz essa promessa valer para `pytest` puro também.

Reproduzido e curado em sandbox: sem o `conftest.py`, `from flatdrop import config`
lançava o mesmo `ModuleNotFoundError`; com ele na raiz, importa OK.

## Correção (mínima, canônica)

Um `conftest.py` na **raiz do repo**. O pytest importa o `conftest.py` da rootdir
automaticamente **antes** de coletar os testes; ao importá-lo, a rootdir entra no
`sys.path`, e `from flatdrop import ...` passa a resolver — independente de o usuário
chamar `pytest`, `pytest -q`, `python -m pytest`, ou de qual subdiretório. Não instala
nada, não toca os testes, não altera o código de produção. Espelha exatamente o que o
`run.py` já faz para a aplicação.

> Alternativas consideradas e descartadas por serem mais invasivas para o objetivo:
> - `pyproject.toml` com `[tool.pytest.ini_options] pythonpath = ["."]` — funciona
>   (pytest >= 7), mas introduz um arquivo de config de projeto inteiro só para uma
>   linha de path; maior superfície. Pode vir depois se o projeto adotar packaging.
> - Instalar em modo editável (`pip install -e .`) — exige `pyproject/setup` e um
>   passo de ambiente; contraria o princípio de "zero setup" do repo (o `run.py`
>   roda por duplo-clique). Descartado.
> O `conftest.py` é o menor diff que resolve para sempre.

---

## EDIÇÃO 1 — criar `conftest.py` na RAIZ do repo

**Ação:** CRIAR o arquivo `conftest.py` na raiz do repositório (mesmo nível de
`run.py`, `tests/` e do pacote `flatdrop/`), com o conteúdo:

```python
"""Configuração de teste do pytest — raiz do repositório.

Único propósito: garantir que a raiz do repo esteja no sys.path ANTES da coleta,
para que os testes possam fazer `from flatdrop import ...` com `pytest` puro, sem
depender de `python -m pytest`, de variável PYTHONPATH, nem de instalar o pacote.

O pytest importa o conftest.py da rootdir automaticamente antes de coletar os
testes; este insert espelha o ajuste que o run.py já faz para a aplicação (DEC-009:
a raiz cuida do PYTHONPATH; GUI/CLI/testes só amarram a core).
"""

import sys
from pathlib import Path

# Raiz do repo = pasta deste arquivo. Colocada à frente do sys.path para que
# `import flatdrop` resolva o pacote local, não um homônimo instalado.
sys.path.insert(0, str(Path(__file__).resolve().parent))
```

> Se já existir um `conftest.py` na raiz (não existia no mount), NÃO sobrescrever:
> apenas garantir que o `sys.path.insert` acima esteja presente e PARAR para reportar.

---

## Sinais de teste / regressão

- **O caso do bug:** a partir da raiz do repo, rodar **`pytest`** (puro, sem `-m`) —
  deve coletar os 41 testes e passar, sem `ModuleNotFoundError`.
- **Continua valendo:** `python -m pytest -q` também segue verde (o insert é
  idempotente; se a raiz já estiver no path, o import só a acha mais cedo).
- **De subdiretório:** rodar `pytest` de dentro de `tests/` deve funcionar também
  (o pytest sobe até a rootdir para achar o `conftest.py`).
- **Sem efeito no código de produção:** `conftest.py` só é carregado pelo pytest;
  `run.py`, GUI e CLI não são afetados.
- Nenhum teste novo; nenhuma mudança em `flatdrop/` nem em `tests/`.

## Nota para o README (não é código)

Vale alinhar o texto de "como rodar os testes" no README/docstring para `pytest -q`
(agora que o puro funciona) — mas isso é doc, fora desta spec de código. Aponto para
o chat cuidar do README num ciclo próprio se você quiser.

## Após aplicar (Code)

1. Da raiz do repo: `pytest -q` → 41 verdes (este é o teste que valida a correção).
2. Conferir `git status` — só o novo `conftest.py` aparece; nada em `flatdrop/` nem `tests/`.
3. Commit:

```
git add conftest.py
git commit -m "test: adiciona conftest.py na raiz para pytest puro achar o pacote" -m "Os testes fazem 'from flatdrop import ...' mas nada punha a raiz do repo no sys.path na coleta, entao 'pytest' puro falhava com ModuleNotFoundError (so 'python -m pytest' funcionava). O conftest.py na rootdir e carregado antes da coleta e insere a raiz no path, espelhando o que o run.py ja faz para a aplicacao. Sem mudanca de codigo de producao nem de testes."
```
