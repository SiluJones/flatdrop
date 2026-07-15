# IDEAS — FlatDrop

Banco de ideias. Não é compromisso nem prazo — é onde pensamentos ficam até
virarem item de `ROADMAP.md`, serem implementados ou descartados. Ideia adotada
vira item do roadmap; implementada vai para "Concluídas"; recusada vai para
"Descartadas" com o motivo. Nunca se perde nada — muda de status.

> **Mudanças nesta revisão (2026-07-15):** specs 0017–0024 aplicadas. KCM, editor visual
> (Fase 2-D) e item C (persistência) movidos para **Concluídas**. Nova ideia ativa:
> **force-include por caminho exato** (correção do `.min.js`). Descartada: **remover a
> `DEFAULT_SUFFIX_IGNORES`** (motivo nas Descartadas). Próximas frentes: multi-raiz na GUI
> / force-include.

> **Mudanças nesta revisão (2026-07-05, transferência de conversa):** ciclo de
> release fechado — specs 0011–0016 todas aplicadas, `pytest` puro corrigido
> (FIX-005), versão 0.3.1, 41 testes. Sem ideia nova; as ideias foram **repriorizadas**
> para a próxima conversa: (1) trecho de KCM (ler `_TREE.md` → gerar
> `.flatdropignore`) e (2) editor de `.flatdropignore` na GUI (= Fase 2-D) sobem ao
> topo das Ativas; o item C (persistência) vem depois delas. A lista abaixo reflete
> essa ordem.

## Ativas

> **Foco (2026-07-15):** as tarefas KCM, editor (Fase 2-D) e item C foram concluídas (ver
> Concluídas). As frentes candidatas agora são **multi-raiz na GUI** e o **force-include
> por caminho exato**; o restante segue por prioridade aproximada.

- **Formato de nome "caminho escrito" (`raiz__pastas__stem.ext`).** Um seletor de
  formato do nome, alternativo ao `root_in_name` atual. Em vez de stem na frente,
  escreveria o caminho na ordem natural de leitura com o **stem no fim**:
  `app/routes/page.tsx` (raiz `meuapp`) → `meuapp__app__routes__page.tsx`. O usuário
  reconhece que **não** ajuda o Claude a achar por nome (o stem deixa de liderar a
  ordenação alfabética), mas agrupa todos os arquivos de um projeto por raiz — útil
  para empilhar vários projetos numa mesma pasta/pilha mental. Implementação seria
  barata (a mecânica de nomeação já existe), mas fica em **espera**: só entra se o
  usuário quiser o seletor de formatos. Coexistiria com o `root_in_name`
  (stem-primeiro) como dois estilos opt-in. (Ideia do usuário, 2026-07-04.)
- **Force-include por caminho exato (resgatar um arquivo específico barrado por ignore
  embutido).** Uma lista de "sempre inclua exatamente este caminho", checada ANTES dos
  cortes embutidos (suffix-ignore, tipo, gitignore), ainda barrada por "sensível". Motiva:
  `htmx.min.js` (e afins) some porque `.min.js` está em `DEFAULT_SUFFIX_IGNORES`, e o `!`
  do `.flatdropignore` age numa camada abaixo (só o matcher), então não resgata. Marcador
  próprio no `.flatdropignore` (distinto do `!`, para não borrar a semântica gitignore do
  DEC-017). DEC-020-safe: vive no `_scan`, simétrica GUI×`.bat`, não toca o gerador de
  `.bat`. Mexe no `_scan` → pede spec de design. **Não urgente** (o autor adiou). (Ideia do
  usuário + assistente, nota 0827.)
- **Selecionar várias pastas de uma vez na GUI (multi-raiz).** Irmã do multi-fonte
  que já existe na core (`make_plan_sources`/`Source`): escolher N pastas na
  interface, prefixar cada arquivo com o nome da sua pasta-raiz e só cair na
  desambiguação atual se ainda colidir; a pasta de saída no Downloads vira uma
  genérica com numerador quando já existir uma de mesmo nome. A core já suporta
  multi-fonte; falta a UI de N raízes. (Ideia do usuário, nota `.txt` de 2026-07-03.)
- **Botão "Gerar atalho da UI" na GUI.** UI-1 e o launcher `flatdrop-ui.bat` já
  existem; falta um botão que gere o launcher calculando o caminho do `run.py`
  sozinho (sem hardcode) — talvez um `.lnk` em vez de `.bat`.
- **UI-2 (polimento de layout) e UI-3 (presets/lembrar seleção).** UI-2: ordem das
  seções, 2 colunas nas opções, tema. UI-3: presets "só docs"/"só código", lembrar
  a última seleção do modal.
- **Saída da CLI ASCII-safe.** Trocar `↳`/`•`/`—` da saída por `->`/`*`/`-` para
  dispensar `chcp 65001` nos `.bat` e evitar de vez problemas de code page. Baixo custo.
- **Ignores de pasta editáveis na GUI** com núcleo imutável
  (`.git`/`node_modules`/`__pycache__`/VCS sempre reaplicados), para tirar/pôr
  pastas como `dist`/`build`/`.venv` caso a caso. (Fase 2 — item D.) **Consolidado
  na "[PRÓXIMA 2] Editor visual de `.flatdropignore`" no topo** — o editor cobre isto
  de forma declarativa e visual. O `.flatdropignore` já cobre boa parte hoje.
- **Resync incremental por diff do manifesto.** Comparar com o `_MANIFEST.md`
  anterior e copiar/avisar só o que mudou. Ganha valor com uso frequente. (Stand-by.)
- **Empacotar como `.exe` (PyInstaller).** Para o PC sem Python: duplo-clique sem
  instalar nada. (Fase 4.)
- **Modo single-file (estilo Repomix), com os mesmos filtros.** Botão que
  concatena tudo num único `.md`/`.xml` com cabeçalhos por arquivo — e respeitando
  os filtros de seleção (ex.: "fundir só os `.md`"). Complemento ao modo pasta,
  não substituto. (Fase 4.)
- **Contagem de tokens mais fiel.** Trocar `bytes/4` por um tokenizador real
  (opcional). (Fase 4.)
- **Drag-and-drop da pasta raiz na janela.** Arrastar a pasta em vez de navegar
  (exigiria tkinterdnd2 — pesar contra o princípio de zero dependências). (Stand-by.)

## Concluídas

- **[KCM — entregue] Claude lê o `_TREE.md` e dita o `.flatdropignore`.** Bloco de KCM
  portável (material externo, não é código do repo) + exemplo no README; habilitado pela
  spec0011. Fecha o ciclo `_TREE → flatdropignore → mount melhor`, sobretudo liberando via
  `!` o que o `.gitignore` esconde. (Ideia do usuário, notas 0704–0714.)
- **Editor visual de `.flatdropignore` na GUI (Fase 2-D, specs 0017–0021).** Modal com
  árvore lazy, checkbox binário ("quero no Projeto"), badges de tipo/sensível, bloco
  gerenciado no arquivo, e glifo indeterminado correto já na visão colapsada
  (`core.folder_effective_state`, FIX-007). Consolidou o antigo item D. (Ideia do usuário.)
- **Persistir config + pastas recentes na GUI (item C, specs 0022–0024, 0.6.0).**
  `settings.json` por plataforma (`%APPDATA%`/`~/.config`/App Support), Combobox de
  recentes, grava ao Executar; escopo **só-GUI (DEC-020)** para não tocar o `.bat`;
  allowlist salva como delta. `load` nunca lança, `save` atômico. (Fase 2 — item C.)
- **Fullpath com nome da pasta-raiz (spec0013 + ajuste de ordem na spec0014).** Flag
  `root_in_name`: no modo fullpath e em fonte única, inclui o nome do projeto no
  nome de cada arquivo (inclusive os da raiz: `README.md` → `README__meuapp.md`).
  Injeção só no NOME planejado (via `root_prefix` em `_plan_names`); o `rel` do
  manifesto/tree fica real. Ignorada com aviso fora do fullpath e em multi-fonte.
  Limite do Windows protegido pelo truncamento com hash. CLI `--root-in-name`;
  checkbox na GUI serializada no `.bat`. A **spec0013** deixou a raiz no meio do
  sufixo (efeito da implementação); a **spec0014** corrigiu para stem + caminho
  invertido + raiz no fim (`page__routes__app__meuapp.tsx`). (Ideia do usuário, nota
  `.txt` de 2026-07-03.)
- **`_TREE.md` opcional na saída (spec0011).** Árvore indentada da origem ao lado do
  `_MANIFEST.md`: copiados (renomeados marcados), pulados com o motivo, e pastas
  ignoradas colapsadas em UMA linha, sem recursão (`node_modules/ [ignorada:
  embutido]`). Desligado por padrão (checkbox GUI + `--tree` CLI, serializado no
  `.bat`). Detalhe dos pulados soltos via `--tree-detail summary|full`. O `_scan`
  passou a devolver a lista completa de pulados (`skipped_items`, sem o teto de 8).
  Verificado no mount (saiu correto). +8 testes (27->35). É o par visual do
  `.flatdropignore` e habilita o fluxo de KCM acima. (Fase 2 — item B.)
- **Redesign da UI por seleção (UI-1).** Modal "Escolher tipos…" (checklist
  categorizado + busca + marcar/limpar por grupo + adicionar custom); tela
  principal compacta. Subsumiu a caixa de extensões e os campos "Só estes/Exceto".
  (spec-0007.)
- **`.flatdropignore` + `.gitignore` aninhado.** Ignore próprio por projeto,
  aninhado, com negação `!` que libera o que o `.gitignore` bloqueia (até pasta
  podada). Lê os `.gitignore` de subpastas. (DEC-014, spec-0008.)
- **GUI: selecionar tipo na hora** (só-ext/exceto-ext) — feito pelo modal (UI-1).
- **GUI: liberar do `.gitignore`** — resolvido de forma declarativa pela negação
  `!` do `.flatdropignore` (spec-0008), em vez de um campo avulso na GUI.
- **Gerador de `.bat` pela interface.** Botão "Gerar .bat…" serializa a config da
  tela num `.bat` ASCII; reproduz a seleção do modal via `--add-ext`/`--exclude-ext`.
  (spec-0003, refinado na 0007. FIX-003 garantiu o ASCII.)
- **Multi-fonte também na GUI.** Toggle "incluir todos os `.md` a partir de [raiz]"
  ao vivo (Pré-visualizar/Executar), não só no `.bat`. (spec-0005; FIX-004.)
- **Launcher da UI.** `bat/flatdrop-ui.bat` abre a interface sem console (`pythonw`),
  copiável.
- **Expandir a allowlist de tipos** (Godot, PDF/DOCX/XLSX/ODT/RTF/EPUB, +linguagens).
  (DEC-013, spec-0001.)
- **Abrir a GUI maximizada.** (spec-0005.)
- **Selecionar por tipo na execução** (`--only-ext`/`--exclude-ext`/`--add-ext`) — 0.2.0.
- **Selecionar por pasta** (`--only-folder` + `--folder-match`) — 0.2.0.
- **Combinar "todos os `.md` do repo" + "conteúdo de uma área" num só manifesto**
  (multi-fonte `make_plan_sources`/`Source` + `--also-md-from`) — 0.2.0.
- **`.bat` para ativar em pastas de trabalho** (os 5 do cinzeiro) — 0.2.0.
- **CLI sem GUI** (`flatdrop/cli.py`) — 0.2.0 (antecipada da Fase 3).

## Descartadas

- **Remover a `DEFAULT_SUFFIX_IGNORES` (ou tirar `.min.js` dela), confiando em
  git/`.flatdropignore`.** Descartada (análise de 2026-07-15). A lista é **redundante** com
  o allowlist de tipos para `.map/.lock/.pyc/.pyo/.class/.o/.so/.dll/.exe` — essas
  extensões não são aceitas, então o filtro de tipo já as barra. Mas é **essencial** para
  `.min.js`/`.min.css`, cujas extensões (`js`/`css`) SÃO aceitas: sem a lista, todo
  minificado/bundle vazaria ao mount. Confiar no git não cobre committados (lockfiles, libs
  vendorizadas e source maps costumam ser versionados) e exigiria `.flatdropignore` por
  projeto para ruído binário — contra o zero-config. E tirar só `.min.js` liberaria TODOS
  os `.min.js`, contra o objetivo de liberar só um. O lever certo para exceções pontuais é
  o **force-include por caminho exato** (ver Ativas), não remover o default.
- **Flag CLI `--ext-set a,b,c` (allowlist exata).** Não foi preciso: o gerador de
  `.bat` reproduz qualquer seleção do modal com `--add-ext` (adições) +
  `--exclude-ext` (remoções), já que o `cli.py` reseta `exclude_ext` na fonte de `.md`.
- **Ser só single-file (sem o modo pasta).** O fluxo é de arquivos individuais no
  Projeto, com atualização granular. Single-file é complemento. (Ver DEC-001.)
- **Mover os arquivos em vez de copiar.** Destruiria a origem. (Ver DEC-002.)
- **Usar symlinks em vez de copiar.** Não se resolvem no fluxo de arrastar; Windows
  os trata de forma inconsistente. (Ver DEC-002.)
- **Upload automático para o Claude.** Não há API pública para os arquivos de
  Projeto; arrastar continua manual (e é só uma etapa).
- **Mover imagens/áudio/vídeo para a saída.** O Projeto do Claude não os usa como
  texto; ignorá-los é o certo. Reabrir via toggle explícito se algum dia precisar.
  (Confirmado com o usuário em 2026-06-14.)

## Feedback para o Kit

Registro do que ESTE projeto observou/mudou além do kit (material que volta para evoluí-lo).

- **Adotado o modo Claude Code (duas raias).** Chat autora docs/specs; Code implementa e commita.
  Criados os arquivos de arranque (`CLAUDE.md` raiz, `.claude/`). Ver DEC-012.
- **`meta/CLAUDE.md` → `meta/CEREBRO.md`.** Confirmado como superconjunto exato do anterior
  (nada perdido) — não houve merge a fazer.
- **Método "doc por spec" exercitado** em muitos ciclos (specs 0001–0010): âncora semântica,
  um canal por doc por ciclo, "PARE e reporte" se a âncora falhar. Funcionou bem.
- **`.bat` no CMD exige ASCII (FIX-003).** Encoding de `.bat` é armadilha: corpo ASCII, acento só na
  saída via `chcp`. O gerador de `.bat` passou a garantir isso.
- **Verificar lógica sutil no sandbox antes de virar spec.** O `.flatdropignore` (negação +
  aninhamento) foi testado com o pathspec real ANTES de escrever a spec — pegou uma expectativa
  errada e deu confiança no algoritmo. Vale como prática para qualquer regra não-óbvia.
- **Atualização do KCM integrada (DEC-015).** Adotados: seção de config, novo nome de spec
  (`AAMMDD-specNNNN-desc.md`), `HISTORICO`→`HISTORY`. Omitidos com registro: HUB (projeto solo) e a
  regra `.gitignore`/README proativa (o repo já tem os dois). Preservado o conteúdo específico do
  flatdrop — nada de sobrescrever meta/ com template em branco.
- **Higiene em transferência.** Ao transferir conversa, regenerar os meta/ completos e detalhados
  (não resumir), reclassificar IDEAS (implementadas → Concluídas) e limpar o STATUS. Um "prompt de
  início" com ordem de leitura + estado exato faz a nova conversa continuar sem perda.
- **Descompasso de versão por corte cedo (2026-07-05).** Cortar a 0.3.0 antes de a spec seguinte
  (root_in_name) entrar deixou código à frente do CHANGELOG; resolvido com um patch de acerto (0.3.1).
  Lição: datar a versão só quando o lote de specs do ciclo estiver todo aplicado, ou assumir o patch.
- **Diferença de ambiente esconde bug de teste (FIX-005).** O Code rodava `python -m pytest` (resolvia
  o path); o usuário roda `pytest` puro (não resolvia). Fixar a forma de rodar na infra (`conftest.py`
  na rootdir), não na memória de quem invoca. Vale como recomendação para o Kit em projetos com pacote
  aninhado.
