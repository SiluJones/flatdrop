# WO 0051 — o `_MANIFEST` avisa quais nomes chegam diferentes ao Projeto

> **Tipo:** mista — CODIGO (`flatdrop/core.py`, `tests/test_core.py`) + REGISTRO
> (`meta/DECISIONS.md`, `meta/STATUS.md`, `meta/CHANGELOG.md`).
> **Config sugerida:** modelo intermediario, `/effort` medio.
> **Pre-requisito:** wo0050 aplicada e commitada, arvore limpa, **100 testes verdes**. Se o numero
> for outro, diga qual no relatorio antes de seguir.
> **Base:** `meta/analises/260823-ANALISE-formato-do-manifesto.md` — opcoes **E + C**, decididas
> pelo autor em 2026-08-23. Item 1 da carta 01 do KCM.
> **Depende de:** wo0050 (as ancoras do STATUS e do CHANGELOG sao texto que ELA escreveu).
> **Ancora semantica:** se um trecho-ancora nao bater EXATAMENTE, **PARE e reporte**.
> **Idempotencia:** procure `project_upload_name` e `DEC-030` antes de inserir; se ja existirem,
> **PULE** e diga no relatorio.

> **Canal dos meta neste ciclo = CODE** para `DECISIONS`, `STATUS` e `CHANGELOG` — esta WO E o
> registro deles. **Nao toque** em `meta/IDEAS.md` nem em `meta/analises/` (canal CHAT; os dois
> chegam prontos no mesmo turno — ver a secao «Arquivos que o chat entregou junto», no fim).

---

## 1. Por que

O `_MANIFEST` abre prometendo que *«a tabela abaixo mapeia cada nome plano de volta ao seu caminho
original»*. Para dotfile e para nome com ponto interno, **a promessa e falsa no destino**: o Projeto
do Claude renomeia no upload, e o nome declarado nao existe na pasta que o assistente enxerga.

Medido em 2026-08-23, neste repositorio: **3 de 38** entradas (`.gitignore`, `.flatdropignore`,
`.claude/settings.local.json`). Medido pelo KCM em dois outros repos: **11 de 109**, nos dois modos
de renomeacao. Quem busca pelo nome declarado encontra ausencia — que e indistinguivel de «nao
subiu», ou seja, exatamente a duvida que o manifesto existe para eliminar.

**A solucao escolhida (analise 260823, opcao E com o aviso da opcao C embutido):** a tabela **nao
muda** — ela continua descrevendo o que a ferramenta escreveu em disco, que e a unica coisa sobre a
qual o FlatDrop tem autoridade. Logo abaixo dela entra um **bloco de excecoes**, presente so quando
houver caso, com o aviso e os nomes previstos. Assim a busca funciona **nas duas direcoes** (quem
procura `.gitignore` acha a linha da tabela e a excecao; quem procura `_gitignore` acha a excecao),
e a inferencia sobre software de terceiro fica rotulada como inferencia, num bloco datado e isolado
— se a regra do destino mudar, o que fica errado e o bloco, nunca a tabela.

**O que esta WO deliberadamente NAO faz:** `mtime` por arquivo (item 2 da carta) segue em
discussao, com contraproposta do chat em cima da mesa.

---

## Edicao 1 — `flatdrop/core.py` · funcao pura `project_upload_name`

**Ancora** (a linha `def` de `write_manifest` e a primeira linha da sua docstring):

```
def write_manifest(dest: Path, plan: FlattenPlan, cfg: ScanConfig) -> Path:
    """Escreve _MANIFEST.md: assinatura + metadados + mapa origem→nome plano.
```

**Inserir IMEDIATAMENTE ANTES** da ancora:

```
def project_upload_name(flat: str) -> str:
    """Nome PREVISTO com que ``flat`` chega ao Projeto do Claude — inferencia, nao promessa.

    Regra observada em 2026-08 sobre 14 casos em tres repositorios: o upload troca o ponto
    INICIAL e os pontos INTERNOS por ``_``, preservando so a ultima extensao. Nao e documentada
    pela Anthropic e pode mudar — por isso o resultado sai rotulado como previsao e FORA da
    tabela, que continua descrevendo o que esta ferramenta escreveu em disco (analise 260823,
    DEC-030).

    Nao opina sobre nada alem de pontos: qualquer outro caractere passa intacto, porque nunca
    foi medido. Prever o que nao se mediu e como declarar estado sem ler.

        .gitignore           -> _gitignore
        settings.local.json  -> settings_local.json
        map.2.0-avowed.json  -> map_2_0-avowed.json
        core.py              -> core.py            (sem divergencia)
    """
    nome = ("_" + flat[1:]) if flat.startswith(".") else flat
    stem, ponto, ext = nome.rpartition(".")
    if not ponto:                      # sem ponto nenhum: nada a prever
        return nome
    return stem.replace(".", "_") + "." + ext


```

## Edicao 2 — `flatdrop/core.py` · o bloco de excecoes, no fim de `write_manifest`

**Ancora** (fim de `write_manifest`, depois do laco que escreve a tabela):

```
    for f in plan.files:
        lines.append(f"| `{f.rel.as_posix()}` | `{f.target}` |")
    lines.append("")
    mani = dest / meta_name(C.MANIFEST_NAME, dest, cfg)
```

**Substituir por:**

```
    for f in plan.files:
        lines.append(f"| `{f.rel.as_posix()}` | `{f.target}` |")
    lines.append("")
    # Bloco de excecoes (DEC-030): a tabela acima descreve o DISCO; o Projeto renomeia no upload
    # e a busca pelo nome declarado voltava vazia — ausencia indistinguivel de "nao subiu". Fica
    # FORA da tabela de proposito: vale para poucos arquivos (3 de 38 aqui) e e previsao sobre
    # software de terceiro. Coluna gastaria celula vazia em 92% das linhas para servir 8%.
    divergentes = [(f.target, project_upload_name(f.target)) for f in plan.files
                   if project_upload_name(f.target) != f.target]
    if divergentes:
        lines.append(
            f"> **Nomes que chegam DIFERENTES ao Projeto ({len(divergentes)}).** O upload troca "
            "ponto inicial e ponto interno por `_`, preservando só a última extensão. Regra "
            "observada em 2026-08 e **não documentada pela Anthropic**: é PREVISÃO, não promessa. "
            "A tabela acima continua valendo para a pasta em disco.\n"
        )
        lines.append("| Nome na pasta | Como chega ao Projeto (previsto) |")
        lines.append("|---|---|")
        for _flat, _previsto in divergentes:
            lines.append(f"| `{_flat}` | `{_previsto}` |")
        lines.append("")
    mani = dest / meta_name(C.MANIFEST_NAME, dest, cfg)
```

## Edicao 3 — `tests/test_core.py` · nove testes novos, no fim do arquivo

**Ancora** (as duas ultimas linhas do arquivo, no teste que a wo0050 acrescentou):

```
    _commit, status = core.git_snapshot(tmp_path)
    assert "limpo" in status and "sem upstream" in status
```

**Inserir IMEDIATAMENTE APOS:**

```


# --- nome previsto no Projeto (wo0051, DEC-030) — puros ---

def test_previsao_dotfile():
    """Ponto inicial vira `_` — o caso dos tres dotfiles de configuracao."""
    assert core.project_upload_name(".gitignore") == "_gitignore"
    assert core.project_upload_name(".flatdropignore") == "_flatdropignore"
    assert core.project_upload_name(".gitattributes") == "_gitattributes"


def test_previsao_ponto_interno():
    """Ponto interno vira `_`; a ultima extensao sobrevive."""
    assert core.project_upload_name("settings.local.json") == "settings_local.json"
    assert core.project_upload_name("index.template.html") == "index_template.html"


def test_previsao_varios_pontos():
    """Todos os pontos internos caem, nao so o primeiro."""
    assert core.project_upload_name("map.2.0-avowed.json") == "map_2_0-avowed.json"


def test_previsao_nome_comum_nao_muda():
    """A esmagadora maioria nao diverge — e nao pode entrar no bloco de excecoes."""
    for nome in ("core.py", "README.md", "Dockerfile", "README__meta.md"):
        assert core.project_upload_name(nome) == nome


def test_previsao_nao_opina_alem_do_ponto():
    """Espaco e outros caracteres passam intactos: nunca foram medidos (DEC-030)."""
    assert core.project_upload_name("meu arquivo.md") == "meu arquivo.md"


def test_manifesto_traz_bloco_de_excecoes(tmp_path):
    """Nome com ponto interno gera o bloco, com o rotulo de PREVISAO."""
    origem = tmp_path / "src"
    origem.mkdir()
    (origem / "dados.v1.json").write_text("{}\n", encoding="utf-8")
    (origem / "a.md").write_text("x\n", encoding="utf-8")
    cfg = core.ScanConfig()
    plan = core.make_plan(origem, cfg)
    res = core.execute_plan(plan, tmp_path / "out", cfg)
    texto = list(res.dest.glob("_MANIFEST*.md"))[0].read_text(encoding="utf-8")
    assert "Nomes que chegam DIFERENTES ao Projeto (1)" in texto
    assert "`dados_v1.json`" in texto
    assert "PREVISÃO" in texto


def test_manifesto_sem_divergencia_nao_tem_bloco(tmp_path):
    """Sem caso, sem bloco — secao vazia e ruido em todo manifesto."""
    origem = tmp_path / "src"
    origem.mkdir()
    (origem / "a.md").write_text("x\n", encoding="utf-8")
    cfg = core.ScanConfig()
    plan = core.make_plan(origem, cfg)
    res = core.execute_plan(plan, tmp_path / "out", cfg)
    texto = list(res.dest.glob("_MANIFEST*.md"))[0].read_text(encoding="utf-8")
    assert "chegam DIFERENTES" not in texto


def test_manifesto_tabela_original_intacta(tmp_path):
    """A tabela continua declarando o nome EM DISCO — a excecao nao a reescreve."""
    origem = tmp_path / "src"
    origem.mkdir()
    (origem / "dados.v1.json").write_text("{}\n", encoding="utf-8")
    cfg = core.ScanConfig()
    plan = core.make_plan(origem, cfg)
    res = core.execute_plan(plan, tmp_path / "out", cfg)
    texto = list(res.dest.glob("_MANIFEST*.md"))[0].read_text(encoding="utf-8")
    assert "| `dados.v1.json` | `dados.v1.json` |" in texto
    assert (res.dest / "dados.v1.json").is_file()


def test_assinatura_continua_na_primeira_linha(tmp_path):
    """Invariante do DEC-007: e ela que autoriza o safe_clear. Nada pode empurra-la."""
    origem = tmp_path / "src"
    origem.mkdir()
    (origem / "dados.v1.json").write_text("{}\n", encoding="utf-8")
    cfg = core.ScanConfig()
    plan = core.make_plan(origem, cfg)
    res = core.execute_plan(plan, tmp_path / "out", cfg)
    texto = list(res.dest.glob("_MANIFEST*.md"))[0].read_text(encoding="utf-8")
    assert texto.splitlines()[0] == C.MANIFEST_SIGNATURE
    assert core.is_our_folder(res.dest)
```

## Edicao 4 — `meta/DECISIONS.md` · DEC-030 no fim do arquivo

**Ancora** (as ultimas linhas do arquivo, fim da DEC-029):

```
**Consequência.** As cinco regras foram enviadas ao KCM como acréscimo ao princípio «artefato
gerado que convive com edição humana», que a v1.89.0 já tinha levado deste projeto. Princípio sem
forma testável não impede o erro — este caso é a prova.
```

**Inserir IMEDIATAMENTE APOS:**

```

## DEC-030 — o manifesto declara o disco; o que o Projeto renomeia vai num bloco à parte

**Contexto.** O `_MANIFEST` promete, no cabeçalho, mapear cada nome plano de volta ao caminho
original. Para dotfile e nome com ponto interno a promessa é falsa **no destino**: o Projeto do
Claude sanitiza no upload (ponto inicial e ponto interno viram `_`; só a última extensão
sobrevive). Medido em 2026-08-23: 3 de 38 entradas neste repo; 11 de 109 nos dois repos do KCM,
nos dois modos de renomeação. Quem busca pelo nome declarado encontra **ausência**, que é
indistinguível de «não subiu» — a dúvida que o manifesto existe para eliminar.

**Decisão.** A tabela **não muda**: ela descreve o que esta ferramenta escreveu em disco, que é a
única coisa sobre a qual ela tem autoridade. Quando houver divergência prevista, o manifesto ganha
logo abaixo da tabela um **bloco de exceções** — aviso com a regra observada, a data, o rótulo
**PREVISÃO** e uma minitabela `nome na pasta → como chega`. Sem caso, sem bloco.

**Alternativas descartadas.** *(a) A coluna «Nome na pasta» passar a declarar o nome sanitizado* —
a tabela deixaria de descrever o disco, e é frágil na direção mais provável: se a sanitização
afrouxar, o nome declarado volta a não existir, agora por culpa nossa. *(b) Terceira coluna na
tabela* (pedido do KCM) — paga a quebra de forma em 100% das linhas para carregar informação que
vale para 8% delas; célula vazia no resto. *(c) Só uma linha no cabeçalho* — resolve a leitura, não
a busca, que é onde dói; adotada **dentro** do bloco, não sozinha. *(d) Gravar o arquivo já
sanitizado* — é a única imune a mudança do destino, mas exigiria sanitizar **dentro** de
`_plan_names`, antes da checagem de unicidade (senão `settings.local.json` e `settings_local.json`
colidem em silêncio): risco no coração da ferramenta para resolver um problema de relato. Fica
registrada como a saída correta **se** o problema deixar de ser de relato — por exemplo, se o
upload passar a falhar em vez de renomear.

**Consequências.** O manifesto passa a afirmar uma regra de software de terceiro, não documentada:
por isso o rótulo de previsão, a data da observação e o isolamento fora da tabela — se a regra
mudar, o que fica errado é um bloco datado, e a tabela segue verdadeira. `project_upload_name` só
opina sobre pontos; qualquer outro caractere passa intacto, porque nunca foi medido. A assinatura
`<!-- flatdrop-manifest v1 -->` continua na primeira linha (DEC-007) — há teste fixando isso.
```

## Edicao 5 — `meta/STATUS.md` · o item 3 do backlog vira decidido

**Ancora** (seção «Em aberto (produto)», item 3 — texto escrito pela wo0050):

```
3. **Decidir o formato do `_MANIFEST`** — análise em
   `meta/analises/260823-ANALISE-formato-do-manifesto.md`, «Em discussão», parada num ponto de
   decisão do autor. O nome plano declarado na tabela **não existe** no mount para dotfile e nome
   com ponto interno (medido: 3 de 38 aqui; 11 de 109 pelo KCM), e falta `mtime` por arquivo.
   *(O item que estava neste lugar — «FlatDrop grava o estado do repo no `_MANIFEST`» — saiu: foi
   ENTREGUE na 0.15.0 pela wo0048 e continuava listado como pendente.)*
```

**Substituir por:**

```
3. **Responder a carta 01 do KCM** — falta só a carta 02, que o chat escreve depois desta WO
   aplicada. Item 1 **decidido e implementado** (DEC-030, wo0051: bloco de exceções). Item 3
   **entregue** (wo0050). Item 2 (`mtime` por arquivo) **em discussão**: o autor questionou a
   utilidade e o chat contrapôs uma coluna de **hash curto** — hash igual ao que já se leu
   *justifica* pular a releitura; `mtime` antigo só *sugere*. Decisão pendente na análise
   `meta/analises/260823-ANALISE-formato-do-manifesto.md`.
```

## Edicao 6 — `meta/CHANGELOG.md` · entrada em `[Não lançado]`

**Ancora** (primeiro item de `### Adicionado` em `[Não lançado]`, escrito pela wo0050 — a primeira
linha basta para localizar, mas case o bloco inteiro):

```
- **A linha de git do `_MANIFEST` passa a dizer se o commit saiu daqui (wo0050).** Além do `ahead`
```

**Inserir IMEDIATAMENTE ANTES** dessa linha (o item novo entra no topo da seção):

```
- **O `_MANIFEST` avisa quais nomes chegam diferentes ao Projeto (wo0051, DEC-030).** Quando algum
  arquivo plano tiver ponto inicial ou ponto interno, entra um bloco logo abaixo da tabela com o
  nome previsto no destino, a regra observada e o rótulo de **previsão**. Motivo: o Projeto do
  Claude sanitiza no upload, e a tabela apontava para um nome que **não existe** no mount — 3 de 38
  entradas aqui, 11 de 109 nos repos do KCM. A tabela continua intacta e continua descrevendo o
  disco; a exceção é que ficou visível.
```

---

## Fora de escopo

- **`mtime`/hash por arquivo** (item 2 da carta): em discussão, fora desta WO.
- **Não corta versão** — nada em `flatdrop/__init__.py`.
- **Não toca `meta/IDEAS.md` nem `meta/analises/`** (canal CHAT neste ciclo).
- **Não mexe na assinatura, no cabeçalho nem na tabela** do manifesto. Se qualquer edição parecer
  exigir isso, **PARE**: a decisão inteira depende de a tabela ficar como está.

## Armadilhas desta WO

- **As âncoras do STATUS e do CHANGELOG são texto que a wo0050 escreveu.** Se você aplicou a wo0050
  com desvio, elas não vão casar — **PARE e reporte o texto real**, não force.
- `### Adicionado` **não** é âncora: aparece em toda versão do CHANGELOG. Ancore no item da wo0050.
- O bloco de exceções usa **acentos** (o manifesto já os usa: «Modo de renomeação», «Tokens
  (estimativa grosseira…)»). Não converta para ASCII — isto não é `.bat` (FIX-003).
- `project_upload_name` roda **duas vezes por arquivo** na *list comprehension*. É de propósito
  (legibilidade); a função é pura e barata. Não "otimize" para um laço — o coração da ferramenta é
  `_plan_names`, e nada aqui deve encostar nele.

---

## Depois de aplicar — conferência antes do commit

- [ ] `git diff` mostra **exatamente**: `flatdrop/core.py`, `tests/test_core.py`,
      `meta/DECISIONS.md`, `meta/STATUS.md`, `meta/CHANGELOG.md`.
- [ ] `python -m pytest -q` → **0 erros**, **109 testes** (100 + 9). Outro número: diga qual antes
      de commitar.
- [ ] **Smoke real:** achate este próprio repositório e abra o `_MANIFEST` gerado. Esperado: a
      tabela inalterada, e logo abaixo dela o bloco com **3** linhas — `.flatdropignore`,
      `.gitignore` e `settings.local.json`. Se vierem mais ou menos que três, reporte quais.
- [ ] `head -1` do manifesto gerado ainda é `<!-- flatdrop-manifest v1 -->`.
- [ ] **Invariante DEC-020:** esta WO não toca `flatdrop/cli.py`, `gui._build_cli_args`,
      `gui._generate_bat` nem `gui._sources`.

## Arquivos que o chat entregou junto — commite-os no mesmo commit

Estes dois vêm prontos do chat neste turno e **são parte desta entrega**. Confira que existem no
disco e inclua-os no `git add`. **Se algum não estiver lá, não invente:** commite o resto e diga no
relatório qual faltou.

- `meta/analises/260823-ANALISE-formato-do-manifesto.md` (atualizada: Status → Decidida em parte)
- `meta/IDEAS.md` (curadoria de 23/08 — se ainda não tiver sido commitado no turno anterior)

## Relatório de aplicação *(quem aplica preenche ao terminar)*

O que foi feito · o que fugiu do texto literal da WO · arquivos tocados · resultado da suíte · o
commit. Grave o MESMO relatório em `../AAMMDD-HHMM-code-flatdrop.txt` (pasta-pai do repo).

## Commit — blocos separados, mensagem SEM acento

```
git add flatdrop\core.py tests\test_core.py meta\DECISIONS.md meta\STATUS.md meta\CHANGELOG.md meta\IDEAS.md meta\analises\260823-ANALISE-formato-do-manifesto.md meta\workorders\260823-wo0051-manifesto-nomes-previstos.md
```

```
git commit -m "feat(manifest): avisar quais nomes chegam diferentes ao Projeto" -m "A tabela prometia mapear o nome plano de volta e apontava para um nome inexistente no mount: o upload troca ponto inicial e interno por _. Medido 3 de 38 aqui e 11 de 109 nos repos do KCM. A tabela fica intacta (descreve o disco) e a divergencia sai num bloco rotulado como previsao, logo abaixo dela. DEC-030."
```

```
git push
```
