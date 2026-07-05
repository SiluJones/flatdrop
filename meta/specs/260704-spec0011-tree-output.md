# spec0011 — `_TREE.md`: árvore da origem na saída (copiados, pulados, pastas colapsadas)

**Tipo:** código · **Alvos:** `flatdrop/config.py`, `flatdrop/core.py`, `flatdrop/cli.py`, `flatdrop/gui.py`, `tests/test_core.py`
**Autor:** chat · **Aplicador:** Claude Code
**Depende de:** nada novo. Estende o que o `_scan` já contabiliza (candidatos + `skipped`/`skipped_samples`). Casa com o FIX-001 (nada some em silêncio) e é o par visual do `.flatdropignore` (DEC-014).

## Objetivo

Gerar um segundo arquivo na pasta de saída — `_TREE.md` — com a **árvore da origem**: os arquivos **copiados** na sua estrutura real de pastas, os arquivos **pulados** com o **motivo**, e as **pastas ignoradas colapsadas em UMA linha, sem recursão** (padrão `tree --gitignore`/repomix — `node_modules/ [ignorada: embutido]`, jamais o interior). Não duplica o `_MANIFEST.md` (que mapeia nome-plano→origem); o `_TREE.md` cobre **estrutura + exclusões e o porquê**.

Serve a dois usos: (1) o autor vê de relance o que subiu, o que virou nome renomeado e o que nem entrou; (2) o Claude do Projeto lê o `_TREE.md` e consegue **ditar um `.flatdropignore`** para corrigir o que falta/sobra (por isso cada exclusão carrega o motivo).

## Decisões de projeto (já acordadas com o usuário)

1. **Desligado por padrão.** Checkbox desmarcada na GUI; flag **`--tree`** na CLI (default off). O gerador de `.bat` serializa `--tree` quando a checkbox está marcada (FIX-004: GUI e `.bat` dão o mesmo resultado).
2. **Nível de detalhe dos ARQUIVOS pulados soltos é configurável** por `tree_skipped`:
   - `"summary"` (**default**): arquivos pulados soltos **não** viram folha individual; cada pasta que os contém ganha um resumo agregado por motivo (ex.: `  [pulados: tipo ×3, sensível ×1]`). Enxuto.
   - `"full"`: cada arquivo pulado aparece como folha individual, com seu motivo (`.env  [pulado: sensível]`).
   - **As pastas ignoradas são SEMPRE uma linha colapsada** nas duas opções — o toggle só afeta arquivos soltos pulados, nunca reabre o interior de pasta podada.
3. **Sem recursão de verdade e sem risco de loop.** A árvore é montada a partir das listas que o `_scan` já devolveu (dados em memória, `followlinks=False` na varredura) — não há nova descida no disco. "Sem recursão" = não listar o interior de pasta colapsada, o que é grátis porque a poda in-place nunca varre esse interior.
4. **Custo do modo `full`:** o `_scan` hoje guarda no máximo 8 amostras por motivo (`note()` corta em 8). Para `full` ser fiel, o `_scan` precisa devolver a **lista completa** de itens pulados (path + motivo). É a única mudança de assinatura interna; são só strings de caminho (barato). As pastas colapsadas entram como **um item cada** (não recursam).

## Formato do `_TREE.md` (referência para o Code implementar)

Cabeçalho curto + a árvore indentada. Símbolos ASCII-safe (coerente com o item "saída ASCII-safe" do IDEAS; nada de `↳`/`•`). Legenda dos motivos no topo. Exemplo (modo `summary`):

```
<!-- flatdrop-tree v1 -->
# Arvore FlatDrop — meuprojeto

- Origem: `C:\...\meuprojeto`   (raiz comum, se multi-fonte)
- Gerado em: 2026-07-04 05:20
- Copiados: 43 · Pulados: 12 · Pastas ignoradas: 3
- Legenda: [copiado] · [renomeado: nome-plano] · [pulado: MOTIVO] · [ignorada: MOTIVO]

meuprojeto/
  app/
    routes/
      page.tsx            [renomeado: page__routes.tsx]
      users/
        page.tsx          [renomeado: page__users.tsx]
    .env                  [pulado: sensivel]        # (so aparece assim no modo full)
  logs/
    2026-07-03.md
    [pulados: tipo x2]                              # (modo summary: agregado por pasta)
  node_modules/           [ignorada: embutido]
  dist/                   [ignorada: gitignore]
  README.md
```

Regras de render:
- Ordena por caminho (pastas e arquivos), estável e determinístico (o `plan.files` já vem ordenado por `rel` em `make_plan_sources`).
- Cada arquivo copiado que teve `renamed=True` mostra `[renomeado: <target>]`; sem rename, mostra o nome puro (opcional `[copiado]` — o Code decide o que fica mais limpo, mas o rename PRECISA aparecer, é o valor central).
- Pasta colapsada vem do `skipped_samples`/lista de pulados com motivos de pasta (`"* (pasta)"`), UMA linha, com o motivo mapeado para rótulo legível: `ignore_padrão (pasta)`→`embutido`, `gitignore (pasta)`→`gitignore`, `flatdropignore (pasta)`→`flatdropignore`.
- Motivos de arquivo mapeados: `tipo`→`tipo`, `sensível`→`sensivel` (ASCII no corpo), `gitignore`→`gitignore`, `flatdropignore`→`flatdropignore`, `filtro (pasta)`→`filtro`, `ignore_padrão`→`embutido`.

> Assinatura `<!-- flatdrop-tree v1 -->` na 1ª linha (paralela ao manifesto). NÃO reusar a assinatura do manifesto: `is_our_folder`/`safe_clear` só devem reconhecer a pasta pelo `_MANIFEST.md`. O `_TREE.md` é conteúdo, não marcador de propriedade.

---

## EDIÇÃO 1 — config.py: nome e assinatura do tree; não copiar o próprio `_TREE.md`

**Âncora:**
```
MANIFEST_NAME = "_MANIFEST.md"
MANIFEST_SIGNATURE = "<!-- flatdrop-manifest v1 -->"
```
**Ação:** SUBSTITUIR por:
```
MANIFEST_NAME = "_MANIFEST.md"
MANIFEST_SIGNATURE = "<!-- flatdrop-manifest v1 -->"

# Nome e assinatura da arvore opcional da origem (spec0011). A assinatura NAO
# marca propriedade da pasta (so o _MANIFEST.md faz isso, via is_our_folder);
# aqui e apenas um cabecalho de versao do formato do proprio _TREE.md.
TREE_NAME = "_TREE.md"
TREE_SIGNATURE = "<!-- flatdrop-tree v1 -->"
```

**Âncora (denylist de arquivos que não sobem — o Code deve localizar o conjunto `DEFAULT_FILE_IGNORES` e a linha do `.flatdropignore` já adicionada na spec-0008):**
```
    ".flatdropignore",  # arquivo de controle do FlatDrop — nao vai para o upload
```
**Ação:** SUBSTITUIR por:
```
    ".flatdropignore",  # arquivo de controle do FlatDrop — nao vai para o upload
    "_tree.md",         # a propria arvore gerada — nao reentra numa proxima varredura
```
> Nota: `_MANIFEST.md` já é filtrado hoje? Se NÃO houver `"_manifest.md"` em `DEFAULT_FILE_IGNORES`, o Code deve acrescentá-lo na mesma edição (mesma razão: não reabsorver a própria saída se a origem e o destino coincidirem). Se já houver, ignore esta nota. **Se a âncora do `.flatdropignore` não existir exatamente, PARE e reporte.**

## EDIÇÃO 2 — core.py: dois campos novos no ScanConfig

**Âncora:**
```
    write_manifest: bool = True
    clear_dest: bool = True  # só limpa pastas que SÃO nossas (ver safe_clear)
```
**Ação:** SUBSTITUIR por:
```
    write_manifest: bool = True
    write_tree: bool = False  # gera _TREE.md (arvore da origem); desligado por padrao (spec0011)
    # Nivel de detalhe dos ARQUIVOS pulados soltos no _TREE.md:
    #   "summary" -> agregado por pasta ([pulados: tipo x3]); "full" -> folha por arquivo.
    # Pastas ignoradas sao SEMPRE uma linha colapsada, independente disto.
    tree_skipped: str = "summary"  # "summary" | "full"
    clear_dest: bool = True  # só limpa pastas que SÃO nossas (ver safe_clear)
```

## EDIÇÃO 3 — core.py: `_scan` devolve também a lista completa de pulados

O `_scan` hoje retorna `(candidates, skipped, samples, warnings)`. Para o modo `full` do tree ser fiel (sem o teto de 8 amostras), acrescenta-se uma 5ª saída: `skipped_items`, lista de `(rel_posix, reason)` — inclusive as pastas colapsadas (uma entrada cada, com o `reason` de pasta e o `rel` terminando em `/`).

**Âncora (a assinatura e a docstring do `_scan`):**
```
def _scan(root: Path, cfg: ScanConfig) -> tuple[list[tuple[Path, PurePath, int]], dict, dict, list]:
    """Percorre a árvore e separa candidatos de pulados.

    Devolve (candidatos, skipped_counts, skipped_samples, warnings).
    candidato = (src_abs, rel_posix, size_bytes).
    """
```
**Ação:** SUBSTITUIR por:
```
def _scan(
    root: Path, cfg: ScanConfig
) -> tuple[list[tuple[Path, PurePath, int]], dict, dict, list, list[tuple[str, str]]]:
    """Percorre a árvore e separa candidatos de pulados.

    Devolve (candidatos, skipped_counts, skipped_samples, warnings, skipped_items).
    candidato = (src_abs, rel_posix, size_bytes).
    skipped_items = lista COMPLETA de (rel_posix, motivo) dos pulados — inclui as
    pastas colapsadas (uma entrada cada, rel terminando em "/"). Alimenta o _TREE.md
    no modo "full"; independe do teto de 8 amostras de skipped_samples.
    """
```

**Âncora (o helper `note` interno):**
```
    def note(reason: str, rel: str) -> None:
        skipped[reason] += 1
        if len(samples[reason]) < 8:
            samples[reason].append(rel)
```
**Ação:** SUBSTITUIR por:
```
    skipped_items: list[tuple[str, str]] = []

    def note(reason: str, rel: str) -> None:
        skipped[reason] += 1
        if len(samples[reason]) < 8:
            samples[reason].append(rel)
        # Lista completa (sem teto) para a arvore fiel do _TREE.md modo "full".
        skipped_items.append((rel, reason))
```

**Âncora (o return do `_scan`):**
```
    return candidates, skipped, samples, warnings
```
**Ação:** SUBSTITUIR por:
```
    return candidates, skipped, samples, warnings, skipped_items
```

## EDIÇÃO 4 — core.py: `make_plan_sources` agrega `skipped_items` e o guarda no plano

**Âncora (o desempacotamento da chamada a `_scan` no laço de fontes):**
```
    for s, rp in zip(sources, roots):
        cands, skipped, samples, warns = _scan(rp, s.cfg)
```
**Ação:** SUBSTITUIR por:
```
    skipped_items_total: list[tuple[str, str]] = []
    for s, rp in zip(sources, roots):
        cands, skipped, samples, warns, skipped_items = _scan(rp, s.cfg)
        skipped_items_total += skipped_items
```

**Âncora (a construção do FlattenPlan no final da função):**
```
    return FlattenPlan(
        root=common,
        files=planned,
        skipped=skipped_total,
        skipped_samples=samples_total,
        collisions=collisions,
        warnings=warnings,
        sources=descs,
    )
```
**Ação:** SUBSTITUIR por:
```
    return FlattenPlan(
        root=common,
        files=planned,
        skipped=skipped_total,
        skipped_samples=samples_total,
        collisions=collisions,
        warnings=warnings,
        sources=descs,
        skipped_items=skipped_items_total,
    )
```

## EDIÇÃO 5 — core.py: campo `skipped_items` no FlattenPlan

**Âncora:**
```
    # Descrições legíveis de cada fonte (vazio/1 item = execução de fonte única).
    # Usado pelo manifesto para registrar de onde veio cada coleta em multi-fonte.
    sources: list[str] = field(default_factory=list)
```
**Ação:** SUBSTITUIR por:
```
    # Descrições legíveis de cada fonte (vazio/1 item = execução de fonte única).
    # Usado pelo manifesto para registrar de onde veio cada coleta em multi-fonte.
    sources: list[str] = field(default_factory=list)
    # Lista COMPLETA de (rel_posix, motivo) dos pulados — inclui pastas colapsadas
    # (rel terminando em "/"). Alimenta o _TREE.md; vazio quando o scan nao a produz.
    skipped_items: list[tuple[str, str]] = field(default_factory=list)
```

## EDIÇÃO 6 — core.py: função `write_tree` (nova) + rótulos de motivo

Inserir a função **logo após** `write_manifest` (antes de `execute_plan`). O Code decide a estética fina, respeitando o formato acima. Requisitos duros:
- 1ª linha = `C.TREE_SIGNATURE`.
- Pastas ignoradas: UMA linha colapsada, sem interior, mesmo em ambos os modos.
- `tree_skipped == "summary"`: arquivos pulados soltos agregados por pasta e motivo; `"full"`: folha por arquivo (usa `plan.skipped_items`).
- Arquivo copiado com `renamed=True` mostra `[renomeado: <target>]`.
- Corpo ASCII no texto fixo (rótulos), embora nomes de arquivo possam ter acento (são nomes reais).

**Âncora (o início de `execute_plan`, para inserir a nova função ANTES dela):**
```
def execute_plan(plan: FlattenPlan, dest: str | os.PathLike, cfg: ScanConfig) -> ExecuteResult:
    """Escreve em disco: resolve destino, (limpa se nosso), copia, gera manifesto."""
```
**Ação:** INSERIR, imediatamente antes dessa linha:
```
# Mapa motivo-interno -> rotulo curto ASCII exibido no _TREE.md.
_TREE_REASON_LABEL = {
    "gitignore": "gitignore",
    "gitignore (pasta)": "gitignore",
    "flatdropignore": "flatdropignore",
    "flatdropignore (pasta)": "flatdropignore",
    "ignore_padrão": "embutido",
    "ignore_padrão (pasta)": "embutido",
    "tipo": "tipo",
    "sensível": "sensivel",
    "filtro (pasta)": "filtro",
}


def _tree_label(reason: str) -> str:
    """Rotulo ASCII curto do motivo, para a arvore. Desconhecido cai em si mesmo."""
    return _TREE_REASON_LABEL.get(reason, reason)


def write_tree(dest: Path, plan: FlattenPlan, cfg: ScanConfig) -> Path:
    """Escreve _TREE.md: arvore indentada da origem (copiados + pulados + pastas
    colapsadas), com o motivo de cada exclusao. Par visual do .flatdropignore.

    Nao lista o interior de pasta ignorada (colapso em uma linha, sem recursao).
    O nivel de detalhe dos arquivos pulados soltos segue cfg.tree_skipped
    ("summary" agrega por pasta; "full" mostra folha a folha).

    A arvore e montada a partir de plan.files (copiados) e plan.skipped_items
    (pulados, ja em memoria) — nenhuma nova varredura de disco.
    """
    # (Implementacao a cargo do Code, seguindo o formato da spec. Esqueleto:
    #  1) separar plan.skipped_items em pastas (rel termina em "/") e arquivos;
    #  2) construir um dict de nos {parte_de_caminho: subarvore} a partir dos
    #     rel de copiados + pastas colapsadas; anexar pulados-arquivo conforme o modo;
    #  3) render indentado por 2 espacos por nivel, ordenado, determinístico;
    #  4) 1a linha = C.TREE_SIGNATURE, depois cabecalho e legenda.)
    lines: list[str] = [C.TREE_SIGNATURE]
    # ... (o Code preenche o corpo) ...
    tree = dest / C.TREE_NAME
    tree.write_text("\n".join(lines), encoding="utf-8")
    return tree
```
> O corpo detalhado (montagem da árvore + render) fica a cargo do Code — a spec fixa o CONTRATO (nome, assinatura, colapso sem recursão, os dois modos, rótulos), não a estética linha a linha. Se o Code preferir montar a árvore com um helper recursivo sobre o dict EM MEMÓRIA, tudo bem — isso não é varredura de disco e não tem loop (não confundir com o "sem recursão" do enunciado, que é sobre não expandir pasta colapsada).

## EDIÇÃO 7 — core.py: `execute_plan` grava o `_TREE.md` quando ligado

**Âncora:**
```
    mani_path = write_manifest(dest_path, plan, cfg) if cfg.write_manifest else None
    return ExecuteResult(
        dest=dest_path,
        copied=copied,
        manifest_path=mani_path,
        cleared=cleared,
        warnings=warnings,
    )
```
**Ação:** SUBSTITUIR por:
```
    mani_path = write_manifest(dest_path, plan, cfg) if cfg.write_manifest else None
    if cfg.write_tree:
        try:
            write_tree(dest_path, plan, cfg)
        except OSError as exc:
            warnings.append(f"Falha ao gravar _TREE.md: {exc}")
    return ExecuteResult(
        dest=dest_path,
        copied=copied,
        manifest_path=mani_path,
        cleared=cleared,
        warnings=warnings,
    )
```
> `ExecuteResult` não ganha campo novo (mantém a superfície mínima). Se quiser expor o caminho do tree no futuro, vira outra spec. Basta o arquivo em disco e, em falha, o warning.

## EDIÇÃO 8 — cli.py: flag `--tree` e `--tree-detail`

**Âncora:**
```
    p.add_argument("--no-manifest", action="store_false", dest="write_manifest", help="não gerar _MANIFEST.md")
```
**Ação:** SUBSTITUIR por:
```
    p.add_argument("--no-manifest", action="store_false", dest="write_manifest", help="não gerar _MANIFEST.md")
    p.add_argument("--tree", action="store_true", dest="write_tree",
                   help="gerar _TREE.md (arvore da origem: copiados, pulados com motivo, pastas colapsadas)")
    p.add_argument("--tree-detail", choices=["summary", "full"], default="summary",
                   help="detalhe dos arquivos pulados no _TREE.md (summary=agregado; full=um por arquivo)")
```

**Âncora (o `ScanConfig(...)` de `_primary_cfg` — o Code localiza a chamada e insere os dois kwargs junto a `write_manifest=`):**
```
        write_manifest=args.write_manifest,
```
**Ação:** SUBSTITUIR por:
```
        write_manifest=args.write_manifest,
        write_tree=args.write_tree,
        tree_skipped=args.tree_detail,
```

## EDIÇÃO 9 — gui.py: checkbox "Gerar _TREE.md" + var + serialização no .bat

**Âncora (criação das BooleanVar de opções):**
```
        self.manifest_var = tk.BooleanVar(value=True)
```
**Ação:** SUBSTITUIR por:
```
        self.manifest_var = tk.BooleanVar(value=True)
        self.tree_var = tk.BooleanVar(value=False)  # _TREE.md desligado por padrao (spec0011)
```

**Âncora (o checkbutton do manifesto na área de opções):**
```
        ttk.Checkbutton(opts, text="Gerar _MANIFEST.md (mapa origem → nome plano)",
                        variable=self.manifest_var).grid(row=3, column=0, sticky="w")
```
**Ação:** SUBSTITUIR por:
```
        ttk.Checkbutton(opts, text="Gerar _MANIFEST.md (mapa origem → nome plano)",
                        variable=self.manifest_var).grid(row=3, column=0, sticky="w")
        ttk.Checkbutton(opts, text="Gerar _TREE.md (árvore: copiados, pulados c/ motivo, pastas colapsadas)",
                        variable=self.tree_var).grid(row=4, column=0, sticky="w")
```
> Se `row=4` já estiver ocupada nessa grade, o Code ajusta a linha/coluna livre mais próxima — a intenção é a checkbox aparecer junto das outras opções de saída. Não mexer no layout além disso.

**Âncora (o `_gather_cfg`, para o toggle valer na execução ao vivo):**
```
            clear_dest=self.clear_var.get(),
            write_manifest=self.manifest_var.get(),
        )
```
**Ação:** SUBSTITUIR por:
```
            clear_dest=self.clear_var.get(),
            write_manifest=self.manifest_var.get(),
            write_tree=self.tree_var.get(),
        )
```

**Âncora (o `_build_cli_args`, para o `.bat` reproduzir o toggle — FIX-004):**
```
        if not self.manifest_var.get():
            args += ["--no-manifest"]
```
**Ação:** SUBSTITUIR por:
```
        if not self.manifest_var.get():
            args += ["--no-manifest"]
        if self.tree_var.get():
            args += ["--tree"]
```
> `tree_skipped` fica no default `summary` na GUI por ora (sem controle de UI nesta spec — o modo `full` é exercitável pela CLI `--tree-detail full`). Expor um seletor na GUI é melhoria de UX futura (UI-3); não incluir aqui para manter a mudança mínima.

---

## EDIÇÃO 10 — tests/test_core.py: cobertura do `_TREE.md`

Acrescentar testes (o Code posiciona junto aos demais de `execute_plan`/manifesto). Casos:

1. **Desligado por padrão:** `ScanConfig()` → `execute_plan` NÃO cria `_TREE.md`; `is_our_folder` continua True (só o `_MANIFEST.md` marca propriedade).
2. **Ligado gera o arquivo:** `write_tree=True` → existe `_TREE.md`, 1ª linha == `C.TREE_SIGNATURE`.
3. **Pasta ignorada colapsa em uma linha:** com um `node_modules/` (ou `.git/`) na origem, o `_TREE.md` cita a pasta UMA vez com rótulo `[ignorada: embutido]` e **não** contém nenhum caminho de dentro dela (nenhuma linha com `node_modules/<algo>`).
4. **Renomeado aparece:** dois `page.tsx` em pastas diferentes → o tree mostra `[renomeado: ...]` para pelo menos um (casa com o `_plan_names`).
5. **Modo summary × full:** um `.env` (pulado por sensível) + arquivos pulados por tipo → no `full` cada um é folha com `[pulado: ...]`; no `summary` aparece um agregado por pasta (ex.: contém `pulados:` e não a folha individual do `.env`). Verificar a diferença de conteúdo entre os dois modos.
6. **`skipped_items` completo:** montar origem com > 8 arquivos pulados pelo MESMO motivo → `plan.skipped_items` tem todos (sem o teto de 8 de `skipped_samples`), e o tree `full` lista todos.
7. **Regressão do `_scan`:** garantir que o novo 5º retorno não quebrou chamadas — se algum teste existente desempacota `_scan` em 4, ajustar para 5 (o Code localiza; provavelmente só `make_plan_sources` chama `_scan`).

Meta: **suíte sobe de 27 → ~33 testes**, todos verdes com `python -m pytest -q`.

---

## Sinais de teste / regressão a conferir (além da suíte)

- **Smoke GUI (Windows):** marcar a checkbox, Executar, abrir a pasta e conferir que `_TREE.md` saiu ao lado do `_MANIFEST.md`; gerar `.bat` com a checkbox marcada e confirmar que o corpo tem `--tree`.
- **FIX-004:** o resultado ao vivo e o do `.bat` gerado devem bater (checkbox marcada ⇒ ambos geram o tree).
- **Origem == destino improvável, mas cobrir:** `_TREE.md`/`_MANIFEST.md` não devem reentrar numa nova varredura (Edição 1).
- **`.flatdropignore`:** rodar com um `.flatdropignore` que faz `!logs/` e conferir no `_TREE.md` que `logs/` aparece como copiada (liberada), não colapsada — é o teste visual de que o par tree×flatdropignore funciona.

## Fora de escopo (vira IDEAS / spec futura)

- Seletor `summary/full` na GUI (UI-3).
- Editor visual de `.flatdropignore` na GUI (aba/painel) — ideia nova do usuário, capturada no IDEAS.
- Fluxo "Claude do Projeto lê `_TREE.md` e dita o `.flatdropignore`" — não é código; é uso que esta spec habilita.
- Expor o caminho do tree em `ExecuteResult`.

## Após aplicar (Code)

1. `python -m pytest -q` — tudo verde (~33).
2. `git diff` — conferir que só os 4 arquivos de código + o teste mudaram; nada fora das âncoras.
3. Commit (bloco pronto, sem acento):

```
git add flatdrop/config.py flatdrop/core.py flatdrop/cli.py flatdrop/gui.py tests/test_core.py
git commit -m "feat(tree): gera _TREE.md opcional com arvore da origem" -m "Arvore indentada dos copiados, pulados com motivo e pastas ignoradas colapsadas em uma linha sem recursao (padrao tree --gitignore/repomix). Desligado por padrao: flag --tree na CLI e checkbox na GUI; o gerador de .bat serializa --tree (FIX-004). Modo de detalhe dos pulados via --tree-detail summary|full (default summary); _scan passa a devolver a lista completa de pulados. +testes."
git push
```
