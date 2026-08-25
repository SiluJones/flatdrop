# Changelog — FlatDrop

Todas as mudanças notáveis deste projeto são registradas aqui.
Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/);
versionamento conforme [SemVer](https://semver.org/lang/pt-BR/).

## [Não lançado]

_Itens de produto em aberto: multi-raiz na GUI (decisão A/B pendente), formato de nome
"caminho escrito" (raiz→pastas→stem), UI-2/UI-3 — todos com gatilho de retorno em `IDEAS.md` ›
Adiadas. A **saída da CLI ASCII-safe** saiu de «Adiadas» (gatilho disparado no smoke da wo0048) e
está em «Ativas». Decisões em aberto: `pasta/*` + `!mantido` no gerador do editor
(`meta/analises/260728-ANALISE-gerador-flatdropignore.md`) e o **formato do `_MANIFEST`**
(`meta/analises/260823-ANALISE-formato-do-manifesto.md`)._

### Adicionado
- **O `_MANIFEST` avisa quais nomes chegam diferentes ao Projeto (wo0051, DEC-030).** Quando algum
  arquivo plano tiver ponto inicial ou ponto interno, entra um bloco logo abaixo da tabela com o
  nome previsto no destino, a regra observada e o rótulo de **previsão**. Motivo: o Projeto do
  Claude sanitiza no upload, e a tabela apontava para um nome que **não existe** no mount — 3 de 38
  entradas aqui, 11 de 109 nos repos do KCM. A tabela continua intacta e continua descrevendo o
  disco; a exceção é que ficou visível.
- **A linha de git do `_MANIFEST` passa a dizer se o commit saiu daqui (wo0050).** Além do `ahead`
  que a wo0048 já emitia, a linha agora traz o **`behind`**, diz **«sem upstream»** quando o branch
  não rastreia nada e **«sincronizado com <upstream>»** quando está em dia — e nomeia o upstream
  real em vez do literal `origin`. Motivo: «limpo» descreve a árvore de trabalho e não distinguia
  *«o mount é o commit»* de *«o mount é o commit, e o commit não saiu daqui»*.

### Corrigido
- **O `behind` era descartado no parser (wo0050).** `[ahead 1, behind 2]` virava só «1 a frente»,
  porque o trecho era cortado num `.split(",")[0]`. A leitura da linha `##` virou a função pura
  `_divergence`, com **sete testes que rodam sem `git` instalado** — o trecho não tinha teste
  nenhum desde a wo0048.

## [0.15.0] — 2026-08-02

> Duas sessões num só corte de versão: a documentação e o ambiente de trabalho em 01/08, o código
> em 02/08. **92 testes verdes** (79 → 82 → 86 → 88 → 92, um degrau por WO). Fecha o único bug
> aberto do projeto.

### Documentação e ambiente de trabalho — 2026-08-01

> **Sem versão de propósito.** Nada do produto mudou: `flatdrop/` está intacto e a suíte não foi
> rodada nesta sessão (último número verificado: 79 verdes em 2026-07-29, relatados pelo Code na
> wo0043). Mesmo critério do merge de 2026-07-28, que também não cortou versão.

### Adicionado
- **O `_MANIFEST` passa a carregar o estado do repositório git (wo0048).** Duas linhas logo abaixo
  de «Gerado em»: o último commit (`%h %ad %s`, data curta) e um **resumo** do status (branch,
  contagem de modificados e não rastreados, commits à frente de `origin`). Rotuladas como **foto
  da geração**, porque é o que são. Motivo: o mount é uma cópia achatada e não leva o `.git`, então
  quem lê o mount não tinha como saber em que commit o projeto está — perguntava, ou respondia de
  memória. Resumo e nunca listagem: `git status` verboso é ruído e vazaria nome de arquivo pessoal
  não rastreado para dentro de uma conversa. Falha de git é silenciosa: nada impede o achatamento.
- **Rótulo `travada (manual)` na coluna «Arquivo novo» (wo0047).** A trava que vem de uma linha
  escrita à mão no `.flatdropignore` deixa de parecer trava do próprio autor. Ganhou importância
  com a wo0046: agora que destravar funciona de verdade sobre linha manual, é preciso saber que
  aquela trava não é sua antes de mexer. A sonda é de **arquivo inexistente**, não de diretório —
  `pasta/*` de propósito não casa a pasta como diretório (DEC-025/DEC-027).
- **Aviso de padrão com contrabarra (wo0047).** Ao abrir o editor, o FlatDrop denuncia toda linha
  de regra escrita com `\` e aponta arquivo e linha. Em sintaxe `.gitignore` a contrabarra é
  **escape**, não separador: o padrão não casa nada e o arquivo sobe achando que foi ignorado —
  falha silenciosa que custou ao autor arrastar arquivos à mão. Avisa e aponta; **não normaliza**,
  porque trocar `\` por `/` calado mudaria a semântica de um arquivo que o git também lê.
- **O Claude Code passa a gravar o relatório de trabalho em arquivo (DEC-028).** Ao fechar
  qualquer tarefa, o mesmo relatório que vai para o chat é escrito em
  `../AAMMDD-HHMM-code-flatdrop.txt`, na pasta-pai do repo. Motivo concreto: copiá-lo do console
  à mão trunca e duplica — foi o que aconteceu com o da wo0043 — e ele é a única fonte do que só
  quem aplicou viu. Exige `permissions.additionalDirectories` no `.claude/settings.json`.
- **`meta/SPEC.md`** — o modelo de spec de feature que a DEC-023 referenciava desde 28/07 e que
  nunca chegou a existir. Adaptado ao projeto: cada critério de aceite diz **onde** é verificado
  (`pytest`, smoke manual, inspeção do arquivo gerado) e há uma seção de invariantes com o DEC-020.
- **Seção «Adiadas» no `meta/IDEAS.md`**, com **gatilho de retorno obrigatório** em cada item —
  ideia adiada sem gatilho é ideia perdida. Seis itens migraram para lá; quatro que já estavam
  entregues foram para «Concluídas» com a versão em que saíram.

### Mudado
- **O bloco gerenciado do `.flatdropignore` virou um *diff* (wo0046, FIX-012).** A base de
  comparação deixou de ser o git puro e passou a ser *gitignore + curadoria manual, sem o próprio
  bloco*. Emite-se só o que diverge dessa baseline. **Consequência visível: num arquivo curado à
  mão, o bloco fica quase vazio — está certo, não "sumiu".**
- **O bloco é sempre reescrito no FIM do arquivo (wo0046).** Posição fixa, não caso-a-caso: vale a
  última regra que casa, então bloco no fim é o que dá ao editor a palavra final sobre o que ele
  mostra na tela. **Move-se o próprio bloco, nunca o texto do autor** — o que estava depois dele
  sobe, na ordem em que estava, e a GUI pergunta antes, porque isso inverte a precedência daquelas
  regras.
- **Merge do template-update do KCM v1.95.0 (DEC-028).** Treze novidades adotadas no `CEREBRO.md`,
  no `CLAUDE.md`, nas duas skills, no `.claude/settings.json` e no `.flatdropignore`; sete choques
  resolvidos a favor do arquivo vivo, quatro deles devolvidos como feedback ao kit. Boa parte das
  regras novas do kit nasceu do feedback deste repo (v1.89.0): é conteúdo próprio voltando
  generalizado, não novidade externa.
- **`.flatdropignore` reorganizado à mão:** cabeçalho explicando a anatomia do arquivo, tudo
  dentro do bloco gerenciado, nada depois do `# <<<` (elimina a duplicação que o bug da 0.13.0
  havia produzido) e o par que faltava — `meta/workorders/*` seguido de
  `!meta/workorders/_TEMPLATE.md`, para o modelo das WOs voltar a subir ao Projeto.
- **Instruções do Projeto refinadas** (5.514 → 6.143 caracteres): entram «análise antes do
  compromisso», «WO nunca vai sozinha» e o bloco de fecho de turno; sai o vocabulário
  **pré-DEC-023**, que ainda mandava escrever `meta/specs/AAMMDD-specNNNN-desc.md`.

### Corrigido
- **O editor não convivia com regra escrita fora do bloco (FIX-012, wo0045 + wo0046).** Três
  sintomas, uma causa: salvar duplicava dentro do bloco o que já estava fora; destravar uma pasta
  fechada à mão era desfeito em silêncio; e marcar um arquivo trazia as duplicatas junto. O
  gerador era cego para a curadoria manual e, sendo cego, não sabia que havia algo a corrigir.
- **Os marcadores do bloco eram procurados por substring (wo0045).** Um comentário que
  *mencionasse* o marcador — documentando a própria convenção — fazia o gerador cortar na menção:
  o bloco novo entrava no meio da frase, o antigo sobrava no fim, e a linha truncada perdia o `#`
  e virava padrão ativo. Agora o marcador é uma **linha inteira**, e arquivo com dois blocos
  **recusa salvar** em vez de adivinhar. Medido: 35 linhas viravam 42, com dois blocos.
- **O `.flatdropignore` crescia uma linha em branco a cada salvamento** (wo0045) — o `lstrip` do
  trecho final só limpava um lado.
- **Registro pendente da leva 0.12.0–0.14.0 (wo0044).** Duas docstrings de `flatdrop/core.py`
  (`_peek_children` e `write_tree`) ainda citavam `C.TREE_NAME_CAP` como o limite, que a 0.14.0
  substituiu por `TREE_NAME_HEAD`/`TREE_NAME_TAIL`; o cabeçalho do `meta/STATUS.md` ainda declarava
  0.11.0 e 68 testes com o corpo já falando de 0.14.0; faltavam três termos no `meta/GLOSSARY.md`
  e os logs das sessões de 28 e 29/07.

## [0.14.0] — 2026-07-28

### Mudado
- **O `_TREE.md` passa a mostrar a FAIXA de uma pasta grande, não só o começo (wo0043).** No
  lugar do teto simples (`10 nomes + "+29 mais"`), sai uma amostra com as primeiras e as
  últimas posições e o meio contado: `... (+29 no meio, 39 no total) ...`. Numa coleção
  ordenada por data é o último nome que diz até onde ela vai — e era exatamente ele que sumia.
  O `_TREE` orienta; o índice completo de uma pasta grande é trabalho do editor da GUI.

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

## [0.12.0] — 2026-07-28

### Corrigido
- **A negação `!` volta a resgatar arquivo dentro de pasta ignorada (FIX-011, wo0038).**
  `_scan` podava o diretório antes de descer, então a negação nunca era avaliada — o motor
  de padrões já liberava o arquivo, mas a varredura não chegava até ele. Agora a poda
  consulta os prefixos alcançados por algum `!` e desce nesses casos; o custo extra só
  aparece quando o autor de fato escreveu uma negação.

### Adicionado
- **O `_TREE.md` passa a dizer O QUE foi ignorado (wo0038).** Arquivo pulado por ignore do
  autor sai **nomeado** (até `TREE_NAME_CAP`, depois `(+N mais)`) em vez de virar contagem;
  pasta ignorada pelo autor ganha uma **espiada rasa** nos filhos diretos. Ruído estrutural
  (`node_modules`, `.git`, tipo, sensível) segue colapsado/agregado.

## [0.11.0] — 2026-07-20

### Adicionado
- **Nomear _MANIFEST/_TREE com o nome da pasta no fim (DEC-022, spec0036).** Checkbox
  default-ON: os meta gerados viram `_MANIFEST_<pasta>.md`/`_TREE_<pasta>.md` (`<pasta>` = o
  campo "Nome da pasta", editável), mantendo o prefixo para busca e desambiguando no Projeto
  do Claude. Só para o que está marcado. Flag `--no-name-meta` na CLI (paridade `.bat`).
  `is_our_folder` reconhece o sufixo. 2 testes (66 → 68).

## [0.10.1] — 2026-07-20

### Corrigido
- **Preferências voltam a persistir abrindo pelo atalho (FIX-010, spec0035).** A semente de
  navegação (0.8.0) fazia a GUI começar 100% limpa quando aberta pelo atalho "abrir GUI",
  descartando renomeação/opções/tipos/separador salvos. Agora só a **localização**
  (raiz/nome/multi-fonte) reseta pelo atalho; as **preferências** são sempre restauradas.

### Adicionado
- **Menu Ferramentas → "Restaurar padrões de fábrica…" (spec0035).** Volta a config ao
  padrão e apaga o salvo (mantém os recentes). Só GUI; `.bat` intocado (DEC-020).

## [0.10.0] — 2026-07-20

### Alterado
- **Layout da GUI reorganizado em duas colunas (spec0034).** Raiz e "Nome da pasta" na mesma
  linha; Renomeação | Opções e Tipos | Ignore lado a lado; Multi-fonte numa linha fina; a
  descrição do topo foi removida (a barra de título já a diz). Isso encurta muito o
  formulário e **devolve espaço ao console de saída** (`Saída`), que antes sumia da vista, e
  encurta os campos (não mais "longos demais"). Só rearranjo: mesmos controles e
  comportamento; `.bat` intocado (DEC-020).

## [0.9.2] — 2026-07-20

### Corrigido
- **Layout do "Recentes ▾" (FIX-009, spec0033).** O botão compacto (0.9.1) tinha ido para
  uma coluna do grid principal; como as colunas do tkinter são globais, isso deixava espaço
  morto à direita de toda a interface e alargava a janela. Agora Entry + "Procurar…" +
  "Recentes ▾" ficam num sub-frame na linha da Raiz: a grade volta a 3 colunas e o Entry
  encolhe só o necessário para os botões caberem colados, como no ASU. Só GUI.

## [0.9.1] — 2026-07-20

### Alterado
- **Recentes compacto (spec0032).** O Combobox de Recentes (que ocupava uma linha inteira)
  virou um botão **"Recentes ▾"** na própria linha da Raiz, ao lado de "Procurar…" — libera
  a linha e deixa a feature discreta. Comportamento igual: escolher um recente preenche a
  raiz (e o nome, se não editado). Só GUI; o `.bat` não é afetado.

## [0.9.0] — 2026-07-20

### Adicionado
- **Menu "Ferramentas → Gerar atalho da UI…" (spec0031).** A GUI passa a gerar o `.bat` que
  abre a interface (antes mantido à mão), já com `--start-dir "%~dp0."` (o "Procurar…" abre
  na pasta do atalho, spec0030). Salva por padrão **uma pasta acima da raiz do repo** — onde
  os `.bat` do FlatDrop já vivem, fora do worktree (não são achatados nem versionados). É um
  gerador **novo e separado**; o RUN `.bat` (`_generate_bat`/`_build_cli_args`) fica
  **intocado** (DEC-020). Colocado num menu (ação de setup, uma vez), não na barra de ações
  por-execução. 1 teste novo (65 → 66).

## [0.8.0] — 2026-07-20

### Adicionado
- **Atalho "abrir GUI" semeia a navegação (`--start-dir`, spec0030).** O `flatdrop-ui.bat`
  passa a mandar `--start-dir "%~dp0."`, então o "Procurar…" da Raiz abre **na pasta onde o
  `.bat` está** — que é para onde o atalho é copiado, junto dos projetos. O argumento apenas
  SEMEIA a navegação; **não define a raiz**. E, quando presente, a GUI **abre limpa** (não
  restaura a última sessão) — senão a raiz salva sobrescreveria a semente e o diálogo abriria
  no projeto anterior. O Combobox de **Recentes** segue disponível. Rodar `run.py` sem
  `--start-dir` restaura a sessão como antes. **Só-GUI/launcher: o gerador do RUN `.bat` e a
  CLI de flatten ficam intocados (DEC-020), com teste de guarda.** 3 testes novos (62 → 65).

## [0.7.1] — 2026-07-16

### Corrigido
- **Nome volta a renomear ao trocar de raiz** (FIX-008). A persistência (0.6.0) travava o
  campo de nome ao restaurar a config, confundindo "nome restaurado" com "nome editado à
  mão"; escolher outra raiz não atualizava mais o nome. Agora o nome salvo é restaurado sem
  travar a flag `_name_edited`, então trocar de raiz renomeia de novo — e um nome digitado
  na sessão ainda é preservado.

## [0.7.0] — 2026-07-16

### Adicionado
- **Force-include por caminho exato no `.flatdropignore`** (DEC-021, spec0027). Uma linha
  `++caminho/exato` resgata um arquivo barrado por um ignore embutido (ex.: `.min.js` da
  `DEFAULT_SUFFIX_IGNORES`) sem liberar todos do tipo. Vence suffix/file-ignore, poda de
  pasta, matcher gitignore/`.flatdropignore` e tipo — **exceto "sensível"**, que segue
  barrado (com aviso). Resgate por `stat` direto: alcança dentro de pastas podadas sem
  varrê-las. Caminho inexistente vira aviso. Independe do `pathspec`. **Só-core/scan: a CLI
  e o gerador de `.bat` seguem intocados (DEC-020).** 4 testes novos (58 → 62).

## [0.6.0] — 2026-07-15

### Adicionado
- **Persistência de config + pastas recentes na GUI** (item C, spec0024, DEC-019). A GUI
  reabre com a última config usada e um Combobox de raízes recentes (dedup, até 8). Grava só
  após um Executar bem-sucedido, num `settings.json` por plataforma (`%APPDATA%\FlatDrop` no
  Windows, `~/.config/flatdrop` no Linux, `~/Library/Application Support/FlatDrop` no macOS).
  A allowlist é salva como delta (não congela defaults futuros). `load` nunca lança (arquivo
  ausente/corrompido → defaults) e `save` é atômico; falha de escrita desliga a persistência
  sem derrubar a GUI. **Escopo só-GUI (DEC-020): a CLI e o gerador de `.bat` não leem nada
  disto — o `.bat` segue snapshot reproduzível.** Guarda `test_cli_has_no_settings`.

## [0.5.2] — 2026-07-15

### Corrigido
- **Glifo da pasta correto na visão colapsada** (FIX-007): uma pasta com conteúdo
  parcialmente excluído (ex.: `meta/` com `meta/specs/` excluído) aparecia ☑ marcada em
  vez de ▣ indeterminada, e só se corrigia depois de expandir. O estado do checkbox de
  pasta derivava dos filhos já carregados na `Treeview`, e o lazy load só carrega ao
  expandir. Agora o glifo vem do core (`folder_effective_state`), que agrega a subárvore
  (todas/nenhuma/misto) independente da árvore da GUI. spec0021. 1 teste novo (48 → 49).

## [0.5.1] — 2026-07-11

Correção do gerador do editor de `.flatdropignore`: deixava passar arquivo novo criado
depois da geração e podia perder exclusões no round-trip. spec0020 / FIX-006. Suíte de
48 testes verde.

### Corrigido
- **Gerador deixava passar arquivo novo** (FIX-006): ao excluir uma pasta inteira, o
  editor listava os arquivos um a um em vez de bloquear a pasta — um arquivo criado
  depois da geração vazava para o mount. `build_flatdropignore` agora **colapsa pasta
  cheia** (todas as folhas versionadas excluídas) em `dir/` (nível pasta) em vez de N
  linhas por arquivo; pasta parcial continua saindo por folha (preserva o irmão mantido).
- **Round-trip perdia exclusões**: o gerador usava o estado efetivo (`full`,
  git+flatdropignore) como base, então regenerar sobre um `.flatdropignore` existente
  podia largar exclusões de pastas não expandidas na tela. Agora a **base de geração é
  git puro** (uma exclusão só do `.flatdropignore` é re-emitida) e o **default de folha
  não editada é o estado efetivo atual** (preserva o que já valia sem reafirmar item a
  item). 2 testes novos (46 → 48).
- **Checkbox de pasta não ficava indeterminado ao abrir** uma raiz que já tem
  `.flatdropignore`: ao expandir uma pasta, os filhos recarregavam mas o glifo da
  própria pasta não era recomputado. Cosmético — a gravação sempre usou o `want` por
  folha, nunca dependeu do glifo da pasta.

### Chore
- `.gitignore` na raiz com bloco Python (`__pycache__/`, `*.py[cod]`, `*.egg-info/`,
  `.pytest_cache/`) e destrastreamento do `__pycache__` que estava versionado.

## [0.5.0] — 2026-07-11

O `.flatdropignore` deixa de ser escondido do upload e passa a ir ao Projeto (como o
`.gitignore` — ambos são contexto importante). Além disso, o arquivo de controle passa a
aceitar nomes alternativos, para o caso de baixar um dotfile da internet falhar. spec0019
/ DEC-018. Suíte de 46 testes verde.

### Adicionado
- **Nomes alternativos para o arquivo de controle** (spec0019): além de
  `.flatdropignore`, agora valem `.flatdropignore.txt` e `flatdropignore.txt`, nesta
  ordem de precedência (num mesmo diretório, o primeiro encontrado vence). A leitura em
  `_collect_ignore_lines` percorre a constante `FLATDROPIGNORE_NAMES`; o editor da GUI
  grava no alias já existente (novo helper `core.flatdropignore_path`), evitando criar um
  segundo arquivo. 2 testes novos (44 → 46).
- **O `.flatdropignore` agora vai ao mount**: saiu de `DEFAULT_FILE_IGNORES` e entrou na
  allowlist de arquivos sem extensão, como o `.gitignore`.

### Corrigido
- **O FlatDrop escondia o próprio `.flatdropignore` do upload** (spec0019): o arquivo de
  controle é contexto importante e deve ir ao Projeto (e ser versionado no repo). Reverte
  a decisão antiga de mantê-lo fora do upload (DEC-018).

## [0.4.0] — 2026-07-11

Editor visual de `.flatdropignore` na GUI (Fase 2-D): marca-se "quero no Projeto" e a
ferramenta deriva os padrões, respeitando a assimetria do gitignore. Fecha o item do
ROADMAP e a spec0018 / DEC-016. Suíte de 44 testes verde.

### Adicionado
- **Editor visual de `.flatdropignore` na GUI** (spec0018): modal
  `FlatDropIgnoreEditor` com árvore navegável (lazy load), checkbox binário por item
  (Opção B), tri-state por pasta e sinalização do que o `.gitignore` já esconde. No
  core, `annotate_children` (anota os filhos diretos de um diretório: `base_in`, fonte
  do ignore, tipo permitido, sensível) e `build_flatdropignore` (gera o **bloco
  gerenciado** entre marcadores, preservando linhas manuais no round-trip). O gerador
  respeita a **assimetria do gitignore** (spec0018 §0): para liberar itens de uma
  pasta escondida usa `!dir/` + re-exclusão por folha das indesejadas; para excluir do
  lado versionado sai por folha. Botão "Editar .flatdropignore…" na tela principal. 3
  testes novos exercitam o gerador contra o `make_plan` real (41 → 44).

### Corrigido
- **FIX-005 — `pytest` puro falhava ao coletar (`ModuleNotFoundError: flatdrop`)**
  (spec0016): adicionado `conftest.py` na raiz do repo com
  `sys.path.insert(0, Path(__file__).resolve().parent)`. O pytest o importa antes de
  coletar, inserindo a raiz no `sys.path` — então `from flatdrop import ...` resolve
  com `pytest` puro, sem depender de `python -m pytest`. Espelha o que o `run.py` já
  faz para a aplicação. Sem mudança de código de produção.

## [0.3.1] — 2026-07-05

Acabamento do modo fullpath: opção de incluir o nome da pasta-raiz no nome de cada
arquivo. Recurso pequeno e opt-in que entrou logo após o corte da 0.3.0; a mesma
sessão ajustou a ordem do sufixo antes de qualquer uso real. Suíte de 41 testes verde.

### Adicionado
- **`root_in_name` — pasta-raiz no nome (modo fullpath)** (spec0013): flag opcional
  (desligada por padrão) que, no modo `fullpath` e em **fonte única**, inclui o nome
  da pasta-raiz do projeto no nome de cada arquivo — inclusive os da raiz
  (`README.md` → `README__meuapp.md`). A injeção acontece só no **nome planejado**
  (via `root_prefix` em `_plan_names`); o `rel` de exibição do `_MANIFEST.md` e do
  `_TREE.md` permanece o caminho real. Ignorada com aviso fora do `fullpath` e em
  multi-fonte (lá o caminho já parte da raiz comum). Exposta como `--root-in-name`
  na CLI e como checkbox na GUI (serializada no `.bat`, FIX-004). O limite de nome do
  Windows segue protegido pelo truncamento com hash já existente.

### Corrigido
- **Ordem do sufixo do `root_in_name`** (spec0014): o formato passou a ser
  **stem + caminho da pasta mais interna à mais externa + nome da pasta-raiz por
  último** (ex.: `app/routes/page.tsx` sob `meuapp` → `page__routes__app__meuapp.tsx`),
  em vez da raiz logo após o stem que a primeira implementação produzia. Ajuste de
  uma linha em `_plan_names` (`(*reversed(dir_parts), root_prefix)`), sem tocar
  `_compose`; o `fullpath` sem a flag permanece idêntico.

## [0.3.0] — 2026-07-04

CLI completa, coleta multi-fonte com manifesto único, expansão de tipos aceitos,
seleção de tipos por modal na GUI, gerador de `.bat`, `.flatdropignore` (+ `.gitignore`
aninhado), `_TREE.md` opcional, adoção do modo Claude Code (duas raias) e integração
do KCM. Duas correções de peso (FIX-003 ASCII no `.bat`, FIX-004 multi-fonte ao vivo).
Suíte de 35 testes verde. A separação core×gui seguiu pagando: CLI e GUI compartilham
a mesma lógica sem duplicação.

### Adicionado
- **Allowlist de tipos expandida** (DEC-013, spec-0001): documentos que o Projeto
  do Claude aceita (`pdf`, `docx`, `doc`, `xlsx`, `rtf`, `odt`, `epub`); Godot
  (`gd`, `uid` para `.gd.uid`, `gdshader`, `tscn`, `tres`, `godot`, `import`); e um
  conjunto curado de linguagens/config (Julia, Nim, Zig, Solidity, CUDA, Terraform/
  HCL, Nix, templates, etc.). Imagens/áudio/vídeo seguem fora.
- **GUI — seleção de tipos por modal (UI-1, spec-0007):** botão "Escolher tipos…"
  abre um `TypePickerDialog` (checklist categorizado — Godot, Linguagens, Web,
  Config, Documentos, Templates, Outros — com busca, marcar/limpar por grupo,
  adicionar tipo custom). A tela principal ficou compacta (só o resumo "Tipos: N de
  M"); a caixa de extensões e os campos "Só estes/Exceto" saíram (o modal os subsume).
- **GUI — gerador de `.bat`** (spec-0003, refinado na 0007): botão "Gerar .bat…"
  serializa a config da tela (`_build_cli_args`) num `.bat` ASCII e salva (abre na
  pasta-pai da raiz). Reproduz a seleção do modal via `--add-ext` (adições) +
  `--exclude-ext` (remoções). Avisa em caminho com acento.
- **GUI — multi-fonte ao vivo** (spec-0005): toggle "Também incluir todos os `.md`
  a partir de [raiz]" passou a valer no Pré-visualizar/Executar (helper `_sources`
  + `make_plan_sources`), não só no `.bat` gerado. "Procurar…" do multi-fonte abre
  na pasta-pai da raiz. A janela abre **maximizada**.
- **`.flatdropignore` + `.gitignore` aninhado** (DEC-014, spec-0008): lê os
  `.gitignore` de subpastas (aninhado) e adiciona um `.flatdropignore` por projeto
  (sintaxe do gitignore, aninhado) que exclui a mais e, com `!`, **libera** o que o
  `.gitignore` bloqueia — até pasta que seria podada. Modelo de "última regra vence"
  com rebasing dos padrões de subpasta; o `.flatdropignore` tem a palavra final
  sobre o `.gitignore`. Atribui o motivo do skip (`gitignore`/`flatdropignore`).
  Verificado com o pathspec real antes de implementar. +3 testes.
- **Launcher `bat/flatdrop-ui.bat`:** abre a UI sem janela de console (`pythonw`),
  copiável para qualquer lugar (acesso rápido à interface).
- **Modo Claude Code** (DEC-012): arranque `CLAUDE.md` (raiz) + `.claude/`
  (`settings.json`, `commands/apply-spec.md`, `commands/wrap.md`); specs em
  `meta/specs/`. `meta/CLAUDE.md` (comportamento) → `meta/CEREBRO.md`.
- **Integração da atualização do KCM** (DEC-015, spec0010): seção "Recomendação de
  configuração" no CEREBRO, convenção nova de nome de spec `AAMMDD-specNNNN-desc.md`,
  `HISTORICO.md` → `HISTORY.md`. HUB omitido (projeto solo).
- **`_TREE.md` opcional na saída** (spec0011, Fase 2-B): árvore indentada da origem
  ao lado do `_MANIFEST.md` — arquivos copiados (renomeados marcados com o nome
  plano), pulados com o motivo, e **pastas ignoradas colapsadas em UMA linha, sem
  recursão** (padrão `tree --gitignore`/repomix; `node_modules/ [ignorada: embutido]`
  nunca expande). Desligado por padrão: checkbox na GUI + `--tree` na CLI (serializado
  no `.bat`, FIX-004). Detalhe dos pulados soltos via `--tree-detail summary|full`
  (default `summary`); o `_scan` passou a devolver a lista completa de pulados
  (`skipped_items`, sem o teto de 8 amostras). +8 testes (27 → 35).

### Corrigido
- **FIX-003 — `.bat` falhava no CMD por caracteres não-ASCII.** Travessão/acentos no
  corpo do `.bat` + `chcp 65001` desalinhavam a leitura do CMD (fragmentos viravam
  comando: `'FlatDrop'`/`'m'`/`'Use'`). Corpo dos `.bat` passou a ser ASCII puro
  (`chcp` só para a saída do Python); os 5 `.bat` do cinzeiro reentregues em ASCII
  e sem `--add-ext` redundante; o gerador emite sempre ASCII.
- **FIX-004 — toggle multi-fonte não afetava a execução ao vivo na GUI.** O toggle
  só estava ligado ao gerador de `.bat`; `_on_preview`/`_on_execute` chamavam
  `make_plan` (fonte única). Corrigido com o helper `_sources` + `make_plan_sources`.

## [0.2.0] — 2026-06-14

Linha de comando, coleta multi-fonte com manifesto único, filtros de seleção e
duas correções. Tudo reaproveitando a core existente (a separação core×gui pagou
a aposta: a CLI não duplicou regra de negócio).

### Adicionado
- **CLI** (`flatdrop/cli.py`): `python run.py` sem argumentos abre a GUI; com
  argumentos roda no terminal. Flags: `--root`, `--dest`, `--name`, `--mode`,
  `--sep`, `--only-ext`, `--exclude-ext`, `--add-ext`, `--only-folder`,
  `--folder-match`, `--no-gitignore`, `--include-sensitive`, `--no-manifest`,
  `--no-clear`, `--also-md-from`, `--preview`.
- **Coleta multi-fonte** (`make_plan_sources`, tipo `Source`): combina várias
  raízes/filtros numa única saída e **um** `_MANIFEST.md`, com caminhos relativos
  à raiz comum e deduplicação por caminho real (nenhum arquivo entra duas vezes).
- **`--also-md-from <raiz>`**: atalho que adiciona a coleta "todos os `.md` a
  partir de `<raiz>`" à mesma saída — monta o padrão "docs do repo + conteúdo de
  uma área" sem dois manifestos.
- **Filtros de execução** no `ScanConfig` e na GUI/CLI: `only_ext` (restringe),
  `exclude_ext` (subtrai), filtro de pasta `only_folders` + `folder_match`
  (starts/contains/exact; termo com `/` vira prefixo de caminho); e `--add-ext`
  para acrescentar extensões à allowlist (ex.: `gd,tscn,tres` para Godot).
- **5 `.bat` do cinzeiro** em `bat/cinzeiro/`: `00-todos-md.bat` (só os `.md` do
  grupo) e `story/art/game/ost-pack.bat` (não-`.md` da área + todos os `.md`).
- **Testes**: `tests/test_cli.py` (3) e novos casos no core (filtros, multi-fonte,
  Downloads).

### Corrigido
- **FIX-001 — poda de pastas era silenciosa.** Pasta inteira engolida pelo
  `.gitignore` (ou pelos ignores embutidos) sumia com a subárvore sem deixar
  rastro na pré-visualização. Agora é contabilizada (`gitignore (pasta)` /
  `ignore_padrão (pasta)`), com amostras, e o `.gitignore` que engole pastas vira
  aviso de primeira classe. A GUI passou a exibir as amostras de pulados por
  motivo. Caso real: pastas renomeadas para `logs` no monorepo `cinzeiro`.
- **FIX-002 — Downloads caía na raiz do perfil.** `default_downloads_dir` agora
  resolve o local REAL: no Windows via Known Folder (`SHGetKnownFolderPath`,
  ctypes, sem dependência nova); no Linux via `XDG_DOWNLOAD_DIR`/`user-dirs.dirs`.
  A home só é usada como último recurso.

## [0.1.0] — 2026-06-05

Primeira versão funcional (MVP). Projeto, arquitetura, código e documentação de
contexto criados na sessão de gênese.

### Adicionado
- Pipeline de duas fases: `make_plan` (pré-visualização, não grava nada) e
  `execute_plan` (copia e gera manifesto).
- Varredura recursiva a partir de uma pasta raiz com `os.walk(followlinks=False)`
  e poda de diretórios in-place.
- Leitura do `.gitignore` da raiz via pathspec (dependência opcional, com modo
  degradado e aviso quando ausente).
- Ignores embutidos de diretórios (`node_modules`, `.git`, `dist`, `.next`…),
  arquivos (lockfiles, `.DS_Store`…) e sufixos (`.min.js`, `.map`, compilados).
- Allowlist de tipos de texto/código úteis ao Claude e lista de arquivos sem
  extensão permitidos (`Dockerfile`, `Makefile`, `.gitignore`…).
- Denylist de arquivos sensíveis (`.env` real, `*.pem`/`*.key`, `id_rsa`,
  `secrets.*`…) sempre pulada por padrão, com exceção para exemplos
  (`.env.example`/`.sample`/`.template`).
- Renomeação à prova de colisão com unicidade garantida (case-insensitive),
  desambiguação por profundidade uniforme dentro de cada grupo de nome,
  truncamento de nomes longos com hash e passe final de contador.
- Três modos de renomeação: `collisions` (padrão), `all` e `fullpath`.
- `safe_clear` / `is_our_folder` / `_resolve_dest`: limpa e reusa apenas pastas
  vazias ou comprovadamente do FlatDrop; pasta de terceiros vira variante `(2)`.
- `_MANIFEST.md` na saída: assinatura, metadados (origem, data, modo, contagem,
  tamanho, estimativa grosseira de tokens) e tabela `caminho original → nome plano`.
- Interface gráfica em tkinter amarrando tudo, com trabalho em thread separada.
- Entrypoint `run.py`, `requirements.txt` e `README.md`.
- Suíte de 13 testes em `tests/test_core.py` (pytest), todos passando.
