# DECISIONS — FlatDrop

Registro de decisões de arquitetura (ADR enxuto). Cada entrada: contexto, decisão
e consequência. Decisões não se reescrevem — se mudarem, adicione uma nova que
supersede a anterior e marque a antiga como **SUPERADA por DEC-N**.
**Quando passar de ~700 linhas, mova as mais antigas para `DECISIONS-archive.md`** — este arquivo
já passou de 1.400, e o arquivamento está no backlog do `STATUS`.

---

## DEC-001 — Achatar para uma PASTA, não concatenar num único arquivo
**Data:** 2026-06-05 · **Status:** aceita

**Contexto.** As ferramentas dominantes do gênero (Repomix, OneFile) concatenam o
repositório inteiro em **um** arquivo XML/MD para colar num LLM. A pesquisa de
prior art não encontrou nenhuma ferramenta no nicho específico do usuário: achatar
para uma **pasta** com renomeação à prova de colisão, para arrastar de uma vez.

**Decisão.** Seguir com o achatamento para pasta (arquivos individuais), não com o
single-file. Combina com o fluxo real do usuário (upload de arquivos avulsos nos
arquivos do Projeto) e preserva granularidade: o Claude indexa cada arquivo e a
atualização é por arquivo, não um blob gigante reenviado a cada mudança.

**Consequência.** Precisamos resolver colisões de nome (o problema central). O
modo single-file fica registrado como ideia futura (DEC não-bloqueante; ver
`IDEAS.md` e Fase 4 do `ROADMAP.md`), aproveitando o que se aprendeu do Repomix
(respeitar `.gitignore`, pular sensíveis, header explicativo para a IA).

---

## DEC-002 — Copiar arquivos (não mover, não symlink); "desgaste" de SSD é não-problema
**Data:** 2026-06-05 · **Status:** aceita

**Contexto.** O usuário questionou se copiar arquivos que serão apagados logo
depois é eficiente, e citou preocupação com "desgaste" de SSD num dos PCs.

**Decisão.** Copiar com `shutil.copy2` (preserva metadados). Não mover (não
podemos destruir a origem) e não usar symlink (o destino é para arrastar para um
app; links não se resolvem nesse fluxo e o Windows trata symlink de forma
inconsistente).

**Consequência.** O desgaste de SSD é desprezível: os arquivos são de texto,
quase todos < 1 MB, e a gravação é ocasional. O TBW (terabytes-written) de
qualquer SSD moderno absorve isso sem significância — escrever alguns MB de vez em
quando não chega perto de qualquer limite relevante. Decisão fechada como
não-problema; copiar é o caminho simples e correto.

---

## DEC-003 — Unicidade GARANTIDA via desambiguação de profundidade uniforme
**Data:** 2026-06-05 · **Status:** aceita

**Contexto.** O pedido inicial era sufixar arquivos repetidos com "a pasta do
arquivo". Mas sufixar só com a pasta-pai **não garante** unicidade: dois
`index.tsx` em `app/users/` e `pages/users/` virariam ambos `index__users.tsx`.

**Decisão.** A garantia de saída é unicidade absoluta (comparada
case-insensitive). O algoritmo agrupa por nome original e, para cada grupo
repetido, escolhe o **menor `k`** (número de pastas no sufixo) que desempata
**todos** os membros, aplicando o **mesmo `k`** a todo o grupo (profundidade
uniforme — mais legível e previsível). Em seguida trunca nomes longos preservando
unicidade e faz um passe final de contador (`_2`, `_3`) para qualquer empate
residual.

**Consequência.** Nomes simétricos dentro de cada grupo de colisão; nunca há
sobrescrita silenciosa. É a parte mais delicada do core e a mais testada.

---

## DEC-004 — pathspec como dependência ÚNICA e OPCIONAL
**Data:** 2026-06-05 · **Status:** aceita

**Contexto.** Casar `.gitignore` corretamente (negação, `**`, âncoras) é difícil
de reimplementar à mão. A biblioteca pathspec faz isso bem. Mas queríamos manter a
barreira de instalação a mais baixa possível.

**Decisão.** Usar pathspec, importado em `try/except` com a flag `HAS_PATHSPEC`.
Sem ela, o app roda em modo degradado: usa apenas os ignores embutidos
(`node_modules`, `.git`, lockfiles, etc.) e **avisa** que o `.gitignore` foi
ignorado, sugerindo `pip install pathspec`. Tenta o factory novo `gitignore` e cai
no antigo `gitwildmatch` para compatibilidade entre versões (evitando o
DeprecationWarning).

**Consequência.** A ferramenta funciona "out of the box" só com Python; instalar
pathspec é um upgrade de qualidade, não um requisito rígido.

---

## DEC-005 — Allowlist de tipos + denylist de sensíveis (segurança não pedida, mas necessária)
**Data:** 2026-06-05 · **Status:** aceita

**Contexto.** O Claude só usa certos tipos como texto (código, markdown, dados);
imagens/binários/áudio/vídeo/PPTX não servem. E subir um repositório por engano
pode vazar segredos.

**Decisão.** (a) **Allowlist** de extensões de texto/código + uma lista de
arquivos sem extensão úteis (`Dockerfile`, `Makefile`, `.gitignore`…). Só o que
está na lista é copiado. (b) **Denylist** de sensíveis sempre pulada (`.env` real,
`*.pem`/`*.key`, `id_rsa`, `secrets.*`…), com exceção explícita para exemplos
(`.env.example`/`.sample`/`.template`). Há um toggle para incluir sensíveis, mas o
padrão é pular.

**Consequência.** A denylist é por nome/sufixo, não um scanner de conteúdo como o
Secretlint — é uma rede de segurança, e a pré-visualização continua sendo a
verdadeira revisão antes do upload.

---

## DEC-006 — Comparação case-insensitive + truncamento de nomes longos
**Data:** 2026-06-05 · **Status:** aceita

**Contexto.** O destino é Windows: case-insensitive e com limite prático de
tamanho de nome/caminho. Achatar caminhos profundos gera nomes muito longos.

**Decisão.** Toda checagem de unicidade é feita em minúsculas. Nomes que excedem
`MAX_NAME_LEN` (200) são truncados no meio e recebem um hash md5 curto (8 chars)
do caminho relativo — estável e único.

**Consequência.** Nada de colisão por diferença de maiúsculas no Windows, e nada
de nome estourado. O hash não é cosmético: é o que mantém a unicidade após o corte.

---

## DEC-007 — safe-clear por assinatura de manifesto (nunca apagar pasta de terceiros)
**Data:** 2026-06-05 · **Status:** aceita

**Contexto.** Para você arrastar sempre do mesmo lugar, é bom reusar e limpar a
mesma pasta de saída. Mas limpar a pasta errada (uma pasta sua de verdade dentro
do Downloads) seria desastroso.

**Decisão.** O FlatDrop só limpa uma pasta de destino se ela estiver **vazia** ou
contiver um `_MANIFEST.md` com a assinatura `<!-- flatdrop-manifest v1 -->` na
primeira linha (prova de que foi ele que a criou). Se a pasta existir, não for
vazia e não for nossa, ele **não toca** nela e cria uma variante numerada
`nome (2)`. Também recusa limpar se houver subpastas inesperadas (nossa saída é
sempre plana).

**Consequência.** Reexecução é segura e idempotente na nossa pasta; pastas de
terceiros ficam intocadas por construção.

---

## DEC-008 — GUI em tkinter (zero-install no Windows)
**Data:** 2026-06-05 · **Status:** aceita

**Contexto.** O usuário pediu uma interface simples. Alternativas (PySimpleGUI,
PyQt, web local) trariam dependências ou empacotamento extra.

**Decisão.** Usar tkinter, que acompanha o Python oficial de Windows/macOS. O
usuário final instala só o Python e roda `python run.py`.

**Consequência.** Interface modesta visualmente, porém suficiente e sem fricção de
instalação. Empacotar como `.exe` (PyInstaller) fica para a Fase 3, para quem não
tem Python.

---

## DEC-009 — Separar core (lógica pura) de gui (apresentação)
**Data:** 2026-06-05 · **Status:** aceita

**Contexto.** Misturar regra de negócio com código de UI dificulta testar e
evoluir (por exemplo, adicionar uma CLI depois).

**Decisão.** `core.py` não importa tkinter e concentra toda a varredura,
nomeação, planejamento e execução; `gui.py` apenas coleta opções, chama a core
numa thread e renderiza. O entrypoint `run.py` só ajusta o `sys.path`.

**Consequência.** O core é coberto por testes sem precisar de display. Uma CLU/CLI
futura (Fase 3) reaproveita o mesmo core sem reescrever nada.

---

## DEC-010 — Coleta multi-fonte com manifesto único (não dois passos)
**Data:** 2026-06-14 · **Status:** aceita

**Contexto.** O usuário precisa montar uma saída que junte "todos os `.md` do
repositório (a partir da raiz)" com "os arquivos desenvolvidos de uma subpasta
(tudo menos `.md`)". Pensou em fazer em dois passos (duas execuções) e fundir,
mas isso geraria **dois** `_MANIFEST.md` e a segunda execução limparia/duplicaria
a pasta da primeira. Além disso, a garantia de unicidade (DEC-003) só vale dentro
de um único plano — dois passos independentes poderiam colidir entre si.

**Decisão.** Introduzir o conceito de **fonte de coleta** (`Source` = raiz +
filtros próprios) e `make_plan_sources([...])`, que varre várias fontes, **une**
os candidatos, **deduplica** por caminho real, roda a renomeação sobre o conjunto
unido e grava **um** manifesto. Os caminhos no manifesto passam a ser relativos à
**raiz comum** das fontes (para o cinzeiro, isso é a própria raiz do repo). Os
parâmetros de nomeação/execução (modo, separador, destino) são globais e vêm da
fonte primária; só os filtros variam por fonte. `make_plan(root, cfg)` continua
existindo como atalho de fonte única (delega a `make_plan_sources`).

**Consequência.** O caso "docs + área" sai numa execução só, com unicidade
garantida e sem sobreposição. A complexidade extra fica contida em
`make_plan_sources`; o resto da core não muda. O `--also-md-from` (DEC-011) é o
açúcar que expõe isso na CLI.

---

## DEC-011 — CLI reaproveitando a core; multi-fonte é CLI-first
**Data:** 2026-06-14 · **Status:** aceita

**Contexto.** O usuário quer `.bat` de duplo-clique para achatar pastas de
trabalho com configuração fixa (ex.: as 4 áreas do cinzeiro). Um `.bat` não tem
como dirigir uma GUI — então era preciso uma interface de linha de comando. A
separação core×gui (DEC-009) tornou isso barato.

**Decisão.** Criar `flatdrop/cli.py` e tornar `run.py` de modo duplo: **sem
argumentos abre a GUI** (duplo-clique como antes); **com argumentos roda a CLI** e
executa (com `--preview` para só simular — executar direto é seguro pelo
`safe_clear`, que nunca apaga pasta de terceiros). O atalho `--also-md-from`
implementa o padrão multi-fonte do DEC-010 numa linha legível. **Multi-fonte fica
só na CLI por enquanto** (CLI-first): a GUI segue fonte-única; expor multi-fonte
visualmente virá com o exportador de `.bat` (registrado em IDEAS/ROADMAP).
Imagens/áudio/vídeo seguem fora por construção (confirmado com o usuário) — não
há razão para movê-los, o Projeto do Claude não os usa como texto.

**Consequência.** O mesmo core serve GUI e CLI sem duplicação. Os 5 `.bat` do
cinzeiro nascem da CLI. O filtro `--add-ext` cobre arquivos de engine fora da
allowlist padrão (ex.: Godot `.gd`); como não se sabe o engine do usuário, não se
cravou extensão no padrão — o controle é por flag, com palpite ajustável nos
`.bat`.

---

## FIX-001 — Poda de pastas pelo .gitignore era silenciosa
**Data:** 2026-06-14 · **Status:** corrigido

**Sintoma.** Ao achatar o monorepo `cinzeiro`, arquivos de mesmo nome em pastas
`logs` "sumiam" da saída — sem erro, sem aviso, sem aparecer nos pulados.

**Causa raiz.** O `.gitignore` da raiz tinha `logs/`; a varredura poda diretórios
casados **in-place** para nem descer neles. A poda funcionava, mas **não era
contabilizada**: só arquivos pulados entravam nos contadores; pasta inteira podada
não deixava rastro. Como o conteúdo nem era varrido, a subárvore desaparecia da
pré-visualização. (A GUI ainda agravava ao exibir só contadores, nunca as
amostras que o plano já guardava.) Diagnóstico confirmado: com as pastas atuais
`logs-story`/`logs-art`/… o `.gitignore` `logs/` não casa (casa só `logs` exato),
por isso o manifesto real tinha os arquivos; o erro só apareceu quando foram
renomeadas para `logs`.

**Solução.** Contabilizar a poda com motivo (`gitignore (pasta)` /
`ignore_padrão (pasta)`) e amostras; emitir um **aviso de primeira classe** quando
o `.gitignore` engole pastas inteiras, sugerindo desativar a leitura do
`.gitignore` (os ignores embutidos seguem ativos). A GUI passou a listar amostras
de pulados por motivo. Dois testes de regressão reproduzem os cenários reais.

**Lição.** Filtragem que remove em silêncio é pior que ruído: o usuário precisa
**ver** o que não subiu. Toda exclusão (arquivo ou pasta) tem de deixar rastro.

---

## FIX-002 — Pasta de saída caía na raiz do perfil em vez do Downloads
**Data:** 2026-06-14 · **Status:** corrigido

**Sintoma.** Em um dos PCs, a saída ia parar em `C:\Users\<user>\` em vez de
`...\Downloads`.

**Causa raiz.** `default_downloads_dir` fazia `home / "Downloads"` e, se esse
caminho não existisse, caía **silenciosamente na home**. No Windows, Downloads é
uma *Known Folder* que pode ter sido movida para outro disco (Propriedades →
Local), redirecionada por política ou pelo OneDrive — nesses casos
`home\Downloads` não existe e o fallback disparava cedo demais.

**Solução.** Resolver o local **real**: no Windows via `SHGetKnownFolderPath`
(GUID `FOLDERID_Downloads`) por `ctypes` (stdlib, sem dependência nova); no Linux
via `XDG_DOWNLOAD_DIR` e `~/.config/user-dirs.dirs`; no macOS `~/Downloads`. A
home permanece só como último recurso. Testável de fato só o ramo XDG aqui
(ambiente Linux); o ramo Windows é coberto por estrutura + confirmação no PC.

**Lição.** "Pasta conhecida" do SO não é um caminho fixo derivável do nome — tem
de ser perguntada ao sistema, ou o fallback mascara o problema.

---

## DEC-012 — Desenvolvimento em duas raias (chat autora, Claude Code implementa)
**Data:** 2026-06-22 · **Status:** aceita

**Contexto.** O kit passou a suportar o modo Claude Code. Antes, o chat planejava E
implementava o código no mesmo turno (via mount). Isso mistura curadoria com execução e
gasta contexto do chat com detalhe de implementação.

**Decisão.** Adotar duas raias: o **chat** autora documentos (arquivo inteiro para
novo/pequeno; **spec** em `meta/specs/` com texto exato + âncora semântica para delta em doc
grande) e specs de código; o **Claude Code** implementa o código, aplica as specs, roda
`pytest`, faz edições append-only nos meta e commita. "Um canal por doc por ciclo": se um doc
foi por spec, o chat não o entrega inteiro no mesmo ciclo. Criados os arquivos de arranque na
raiz (`CLAUDE.md`, `.claude/settings.json`, `.claude/commands/`). O antigo `meta/CLAUDE.md`
(comportamento) virou `meta/CEREBRO.md` — superconjunto exato do anterior (nada perdido); o
nome `CLAUDE.md` passou a ser o guia-raiz curto do Code.

**Alternativas.** Seguir implementando tudo no chat (mistura raias, gasta contexto);
implementar só no chat e usar o Code só para doc (subaproveita o Code em código).

**Consequência.** O chat fica mais enxuto e focado em decisão/arquitetura/curadoria; o código
é implementado e testado no Code com diff auditável. Custo: disciplina de manter specs com
âncoras exatas e de não duplicar canal por doc.

## DEC-013 — Expandir a allowlist de tipos (defaults), sem virar pega-tudo
**Data:** 2026-06-22 · **Status:** aceita

**Contexto.** Faltavam tipos que o Projeto do Claude aceita (PDF/DOCX/XLSX e ainda ODT/RTF/EPUB)
e os do engine do usuário (Godot: `.gd`, `.gd.uid`…), além de várias linguagens/config comuns.

**Decisão.** Acrescentar um conjunto curado à `DEFAULT_EXTENSIONS` (ver `spec-0001`), incluindo
os documentos binários aceitos pelo Projeto — mantendo imagens/áudio/vídeo FORA. Defaults
generosos cobrem o caso comum; o ajuste fino por projeto fica para o `.flatdropignore` (futuro),
em vez de inflar o config indefinidamente.

**Alternativas.** Só os 5 tipos pedidos (deixaria gaps óbvios de linguagem); só `.flatdropignore`
e nenhum default novo (todo projeto teria de reconfigurar do zero).

**Consequência.** Mais tipos chegam ao Projeto sem configuração. Ressalva: a estimativa de
tokens (`bytes/4`) não vale para binários, e binários grandes podem estourar o teto de 30 MB.

---

## FIX-003 — .bat gerado falhava no CMD por caracteres não-ASCII
**Data:** 2026-06-24 · **Status:** corrigido

**Sintoma.** Ao rodar os `.bat` do cinzeiro, o CMD imprimia `'FlatDrop'`/`'Use'`/`'m'` "não
reconhecido" ANTES do `CONCLUÍDO`. O Python rodava certo (multi-fonte OK, 86 arquivos), mas a
saída vinha poluída.

**Causa raiz.** Os `.bat` tinham caracteres não-ASCII no corpo (travessão "—" e acentos nos
comentários `rem`) e `chcp 65001`. Trocar o code page para UTF-8 no meio do batch faz o CMD
**desalinhar a leitura por bytes** das linhas seguintes (os multibyte deslocam o offset): o `rem`
é lido cortado ("em"/"m") e o resto da linha vira comando. Confirmado com `cat -A`: as linhas que
erravam eram exatamente as que tinham "—"/"só". O Python rodava porque a linha `python ...` é
ASCII e o CMD re-sincronizava até ela.

**Solução.** Corpo do `.bat` em **ASCII puro** (sem "—", sem acentos nos comentários), mantendo
`chcp 65001` só para a SAÍDA do Python (impressa, não parseada pelo CMD). Os 5 `.bat` do cinzeiro
foram reentregues em ASCII (e sem `--add-ext`, redundante após a spec-0001). O **gerador de `.bat`**
(spec-0003) emite sempre ASCII e avisa se um caminho tiver acento (frágil no CMD).

**Lição.** `.bat` no CMD é sensível a encoding: trate o corpo como ASCII. Acento só na SAÍDA
(via `chcp`), nunca no texto que o CMD parseia. Geradores de `.bat` devem garantir isso.

---

## FIX-004 — toggle multi-fonte não afetava a execução ao vivo na GUI
**Data:** 2026-06-24 · **Status:** corrigido (spec-0005)

**Sintoma.** Com "Também incluir todos os .md a partir de:" MARCADO, o `.bat` gerado fazia
área + todos os `.md` (2 fontes, correto), mas "Pré-visualizar"/"Executar" na própria GUI
faziam só a coleta normal da raiz (1 fonte).

**Causa raiz.** Omissão da spec-0003: o toggle (`also_md_var`/`also_md_root_var`) foi ligado
apenas ao `_build_cli_args` (gerador de `.bat`). Os handlers `_on_preview`/`_on_execute`
continuavam chamando `core.make_plan(root, cfg)` (fonte única), sem montar as fontes.

**Solução.** Helper `_sources(primary)` que espelha o `_build_cli_args` (raiz primária + fonte
"todos os .md" via `replace(primary, only_ext={'md'}, ...)`); `_on_preview`/`_on_execute` passam
a usar `core.make_plan_sources(...)`. Assim a execução ao vivo e o `.bat` dão o MESMO resultado.

**Lição.** Ao adicionar uma opção que o gerador de `.bat` serializa, ligar a MESMA opção ao
caminho de execução ao vivo no mesmo ciclo — senão a GUI e o `.bat` divergem.

---

## FIX-005 — `pytest` puro falhava ao coletar (`ModuleNotFoundError: flatdrop`)
**Data:** 2026-07-05 · **Status:** corrigido (spec0016)

**Sintoma.** No Windows, rodando `pytest` (puro) a partir da raiz do repo, a coleta era
interrompida com 2 erros: `tests/test_cli.py` e `tests/test_core.py` falhavam em
`from flatdrop import ...` com `ModuleNotFoundError: No module named 'flatdrop'`
(0 testes coletados). `python -m pytest` funcionava (41 verdes).

**Causa raiz.** Estrutura aninhada (raiz `FlatDrop\flatdrop\`, pacote `flatdrop\` dentro,
`tests\` ao lado). Os testes importam `flatdrop` como pacote de topo, mas nada inseria a
raiz do repo no `sys.path` durante a coleta, e o projeto não tinha `conftest.py`/
`pyproject.toml`/`pytest.ini`/`setup.*`. O `run.py` já fazia esse ajuste para a aplicação
(`sys.path.insert`), mas não havia equivalente para os testes. O `python -m pytest`
mascarava o problema porque o `-m` adiciona o diretório atual ao `sys.path`; o `pytest`
puro não faz isso. Ou seja: bug latente desde sempre, revelado só ao trocar a forma de
invocar.

**Solução.** `conftest.py` na raiz do repo com `sys.path.insert(0, Path(__file__).resolve().parent)`.
O pytest importa o `conftest.py` da rootdir antes de coletar, inserindo a raiz no path —
então `from flatdrop import ...` resolve com `pytest` puro, sem `python -m`, sem PYTHONPATH
e sem instalar o pacote. Espelha o que o `run.py` já faz. Alternativas mais invasivas
(`pyproject.toml` com `pythonpath`, `pip install -e .`) foram descartadas por exigirem
config de packaging/passo de ambiente, contra o princípio de zero-setup do repo.

**Lição.** Fixar a forma de rodar os testes na infra, não na memória de quem invoca: se o
comando documentado é `pytest -q`, garantir que `pytest` puro funcione (via `conftest.py`
na rootdir), em vez de depender de `python -m pytest`. Diferenças entre ambientes (o do
Code usava `-m`; o do usuário, puro) escondem esse tipo de defeito.

---

## DEC-014 — `.flatdropignore` (ignore próprio) + `.gitignore` aninhado
**Data:** 2026-06-24 · **Status:** aceita

**Contexto.** Faltava (a) respeitar `.gitignore` de subpastas (só o da raiz era lido) e (b) um jeito de
excluir o que vai para o git mas não para o Projeto, e de LIBERAR o que o `.gitignore` bloqueia — sem
desligar o `.gitignore` inteiro nem inflar o config.

**Decisão.** Um arquivo `.flatdropignore` por projeto, lido como o `.gitignore` e ANINHADO, com negação
`!` para re-incluir (até pasta inteira que seria podada). Tudo é unido num único matcher por "última regra
vence": todos os `.gitignore` (raso→fundo), depois todos os `.flatdropignore` (raso→fundo) — então o
**`.flatdropignore` tem sempre a palavra final** sobre o `.gitignore`, em qualquer profundidade. Padrões de
subpasta são reescritos para casar relativo à raiz. Três specs: `full` (decisão) + `gi`/`fd` (para atribuir
o motivo do skip e detectar liberação). A lógica foi VERIFICADA com o pathspec real antes de implementar.
O próprio `.flatdropignore` entra no ignore de arquivos (não vai para o upload).

**Alternativas.** Só campos avulsos na GUI (não cobre o aninhado nem "liberar do gitignore" de forma
declarativa); seguir só com `--no-gitignore` (tudo-ou-nada); inflar o config para sempre (não escala).

**Consequência.** Controle fino e declarativo por projeto, versionável, que também simplifica a config dos
`.bat`. Semântica deliberada: o `.flatdropignore` sobrepõe o `.gitignore` (≠ git puro, onde o mais fundo
vence) — bate com a intenção "`!` libera o que o gitignore bloqueia". Custo: uma passada extra na árvore
para coletar os arquivos de ignore (aceitável; fundível numa passada depois).

---

## DEC-015 — Integração da atualização do KCM (HUB omitido)
**Data:** 2026-06-24 · **Status:** aceita

**Contexto.** O Kit de Contexto (KCM) atualizou: dois princípios já tínhamos (12 higiene, 13 refutar);
novidades relevantes = seção "Recomendação de configuração", nova convenção de nome de spec
(`AAMMDD-specNNNN-desc.md`), renome `HISTORICO`→`HISTORY`, e uma seção "Projeto em grupo (HUB)".

**Decisão.** Adotar a padronização do KCM: acrescentar a seção de config ao CEREBRO, adotar o novo nome de
spec daqui pra frente (specs antigas mantidas), renomear `HISTORICO.md`→`HISTORY.md` (conteúdo preservado),
e atualizar as Instruções do Projeto. **Omitir a seção HUB** — o flatdrop é solo (sem outras frentes); o
usuário reconfigurará o HUB desativado numa próxima geração do KCM. Omitir também a regra ".gitignore/README
proativos" por não se aplicar (o repo já tem os dois, estáveis).

**Alternativas.** Regenerar todos os meta/ pelo template (o KCM manda preservar o conteúdo do projeto — não
sobrescrever com o template em branco); manter o HUB (não há grupo, seria peso morto).

**Consequência.** Comportamento alinhado ao KCM sem perder o específico do flatdrop. Desvios registrados
(HUB e .gitignore/README omitidos) conforme a "válvula de desvio registrado".

---

## DEC-016 — Editor de `.flatdropignore` (spec0017): 3 decisões fechadas
**Data:** 2026-07-06 · **Status:** aceita

**Contexto.** A `spec0017` (design/investigação, Fase 2-D) fechou o desenho do editor visual do
`.flatdropignore` e deixou três decisões em aberto para o usuário, necessárias antes de escrever a
spec0018 de implementação.

**Decisão.** (1) **Interação (§4):** Opção B — checkbox binário "quero no Projeto"; a ferramenta
deriva sozinha `!padrão` (liberar) ou `padrão` (excluir) a partir do `base_in` do git, expondo o
resultado como badge e com pré-visualização do texto do `.flatdropignore` antes de salvar. (2)
**Round-trip (§6):** opção (i) — bloco gerenciado entre marcadores (`# >>> flatdrop-editor` … `# <<<`),
preservando linhas manuais fora dele; a árvore é pré-marcada pelo estado atual via `fd`/`_ignore_status`.
(3) **Spike (§11):** sim — antes da spec0018, um spike de UI descartável (não commitado) valida no
Windows real o hit-testing do clique na coluna do glifo no `ttk.Treeview`, o lazy load e o comportamento
`!dir/` vs `!dir/**` na árvore real.

**Consequência.** A spec0018 (implementação) parte dessas 3 decisões já fechadas: `walk_annotated` +
`build_flatdropignore` no core (testáveis por pytest) + o modal em `gui.py`, entrando só depois do spike
de UI validar as armadilhas do §7/§9.

## DEC-017 — Assimetria do gitignore no gerador do `.flatdropignore` (spec0018)
**Data:** 2026-07-11 · **Status:** aceita

**Contexto.** A verificação em sandbox da spec0018 expôs uma assimetria do gitignore que a spec0017 §5
subestimava: quando a pasta-pai está excluída (`dir/`), **`!dir/arquivo` NÃO reinclui** o arquivo —
o git não reinclui uma folha se o diretório-pai está excluído.

**Decisão.** O `build_flatdropignore` implementa a assimetria: para **liberar** itens de uma pasta que
o git esconde, reinclui a **pasta** (`!dir/`, que já traz tudo em qualquer profundidade — `!dir/**` é
desnecessário) e depois **re-exclui por folha** (`dir/arquivo`) os indesejados sob ela; para **excluir**
do lado versionado (base incluída), sai **por folha** (`caminho`), em qualquer profundidade. Coberto por
`test_editor_liberate_only_one` / `test_editor_exclude_keeps_sibling` contra o `make_plan` real.

**Consequência.** Armadilha canônica registrada: não "otimizar" o gerador para `dir/` + `!dir/arquivo`
no futuro — não funciona. A geração passa por pasta liberada, não por folha reincluída.

---

## DEC-018 — `.flatdropignore` vai ao mount + nomes alternativos (spec0019)
**Data:** 2026-07-11 · **Status:** aceita (reverte parte da DEC-014)

**Contexto.** A DEC-014 mantinha o próprio `.flatdropignore` fora do upload (entrava em
`DEFAULT_FILE_IGNORES`), enquanto o `.gitignore` ia ao Projeto pela allowlist. Na prática os dois
arquivos de ignore são contexto igualmente importante para o Claude entender o projeto. Além disso,
baixar um dotfile da internet às vezes falha (o navegador/OS renomeia ou recusa arquivos sem stem),
o que dificultava começar um `.flatdropignore` a partir de um modelo baixado.

**Decisão.** (1) **Reverter** a decisão de esconder o `.flatdropignore`: tirá-lo de
`DEFAULT_FILE_IGNORES` e pô-lo na allowlist de arquivos sem extensão — vai ao mount como o
`.gitignore`. (2) Aceitar **nomes alternativos** via `FLATDROPIGNORE_NAMES`
(`.flatdropignore` → `.flatdropignore.txt` → `flatdropignore.txt`), nesta ordem de **precedência**:
num mesmo diretório, o primeiro nome encontrado vence. `_collect_ignore_lines` percorre a constante;
o editor da GUI grava no alias existente via o novo helper `core.flatdropignore_path` (não cria um
segundo arquivo). Verificado rodando o `make_plan` real; 2 testes novos (44 → 46). Bump 0.5.0.

**Alternativas.** Manter o `.flatdropignore` fora (mais "limpo", mas esconde contexto útil); só o nome
canônico (não resolve o download falho); aceitar qualquer `*.flatdropignore*` (frouxo demais, casaria
lixo). Os aliases `.txt` já vão ao mount por serem `.txt` (tipo aceito); se o autor filtrar `.txt`, o
canônico `.flatdropignore` continua garantido pela allowlist — borda aceitável.

**Consequência.** Os dois arquivos de ignore agora são versionáveis e visíveis no Projeto. Precedência
explícita evita ambiguidade quando há mais de um alias na mesma pasta.

---

## FIX-006 — Gerador do editor deixava passar arquivo novo + perdia exclusões no round-trip
**Data:** 2026-07-11 · **Status:** corrigido (spec0020)

**Sintoma.** Verificado rodando o `make_plan` real: (1) ao excluir uma pasta inteira no
editor, o `.flatdropignore` saía com os arquivos listados **um a um**, então um arquivo
criado DEPOIS da geração (ex.: `260711-spec0019-...md` em `meta/specs/`, criado após
"excluir" a pasta) não estava em nenhuma linha e **vazava** para o mount. (2) Regenerar o
arquivo sobre um `.flatdropignore` existente, mexendo só numa pasta, podia **largar** a
exclusão de outra pasta não expandida na tela — o gerador usava o estado efetivo atual
(`full` = git+flatdropignore) como base, então uma folha ausente de `wants` herdava o
estado JÁ CONSIDERANDO o próprio `.flatdropignore`, e ao reconstruir o bloco gerenciado do
zero essa herança não bastava para reafirmar a exclusão.

**Causa raiz.** `build_flatdropignore` tratava exclusão por FOLHA como suficiente e usava
uma base única (`full`) tanto para decidir o que emitir quanto para o default do que não
foi editado — mas esses dois papéis exigem bases diferentes: gerar por folha nunca
bloqueia arquivo novo (ele não existia na varredura), e usar o estado efetivo como base de
geração reemite só o que já está representado, não o que precisaria ser preservado.

**Solução.** Duas bases distintas: **base de geração = git puro (`gi`)** — uma exclusão
só do `.flatdropignore` é sempre re-emitida ao regenerar, não some; **default de folha não
editada = estado efetivo atual (`full`)** — preserva o round-trip sem o usuário reafirmar
item a item. E **colapso de pasta cheia**: quando todas as folhas versionadas de uma pasta
estão excluídas, emite `pasta/` (nível pasta) em vez de N linhas por arquivo — bloqueia
arquivo novo criado depois, porque a regra passa a valer para a pasta inteira, não para
nomes específicos. Escolhe a pasta cheia mais alta (maximal); pasta parcial continua saindo
por folha, preservando o irmão mantido. Verificado no `make_plan` real antes da spec: excluir
`logs/` inteiro gera `logs/` e um `logs/NOVO.md` criado depois continua bloqueado; regenerar
mexendo só em `docs/a` preserva `logs/`/`meta/specs/`; excluir `docs/a,b` mantendo `keep.md`
sai por folha. 2 testes novos (`test_editor_collapse_blocks_new_files`,
`test_editor_roundtrip_preserves_folder_exclusion`; 46 → 48).

**Lição.** "Gerar a partir do estado atual" e "preservar o que não foi tocado" são papéis
diferentes e podem exigir bases de dados diferentes (git puro vs. efetivo) — usar uma base
só para os dois criou um bug sutil que só aparece com o tempo (arquivo criado depois da
geração), não no teste ingênuo do dia da implementação.

## FIX-007 — Glifo da pasta mentia na visão colapsada do editor
**Data:** 2026-07-15 · **Status:** corrigido (spec0021)

**Sintoma.** Ao abrir o editor numa raiz com `.flatdropignore`, uma pasta com conteúdo
parcialmente excluído (ex.: `meta/` com `meta/specs/` excluído) aparecia ☑ marcada em vez
de ▣ indeterminada. O estado só se corrigia depois de expandir a pasta.

**Causa raiz.** `_folder_state` calcula o estado a partir dos filhos carregados na
`Treeview`, e o lazy load só os carrega ao expandir. Sem filhos, a função caía no
`return self.st[iid]["want"]` — o `want` da própria pasta (que não está ignorada) — e
devolvia ☑. O fix da spec0020 (recompor o glifo ao expandir) agia só ao expandir; a visão
inicial continuava mentindo. O dado necessário já existe no core e não depende da UI.

**Solução.** Novo `core.folder_effective_state(root, cfg, rel_dir, probes)` agrega a
subárvore via `_walk_leaves` e devolve `True`/`False`/`None` (todas/nenhuma/misto). A GUI
passa a pintar o checkbox de pasta a partir dele (em `_populate`), em vez de olhar os
filhos carregados. `_GLYPH` já mapeia `None` → ▣ e `_style`/`_eff_want` já tratam `None`
como "vai". 1 teste novo (`test_folder_effective_state`; 48 → 49).

**Lição.** O estado de checkbox de pasta não pode derivar dos filhos carregados na árvore
(o lazy load faz a visão colapsada mentir) — deriva do core. Impede a regressão de
"otimizar" de volta para a árvore.

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

## DEC-020 — Invariante: proteger o `.bat` e o núcleo comprovado acima de features novas
**Data:** 2026-07-15 · **Status:** aceita (invariante permanente)

**Contexto.** O gerador e o uso de `.bat` são, até aqui, a funcionalidade mais útil e
prática do FlatDrop (snapshot reproduzível da config, roda sem abrir a GUI). O autor
determinou explicitamente que estragar isso por causa de uma conveniência (ex.: persistência
de config) seria a pior das decisões — pior do que não ter a conveniência.

**Decisão.** Fica registrado como invariante permanente do projeto: nenhuma funcionalidade
nova pode degradar o `.bat`, nem outra função de valor já comprovada (a paridade GUI×`.bat`
do FIX-004, a renomeação à prova de colisão, a poda visível do FIX-001, o `.flatdropignore`
correto). Concretamente: (1) a CLI e o gerador de `.bat` (`flatdrop/cli.py`,
`gui._build_cli_args`, `gui._generate_bat`, `gui._sources`) são **intocáveis** por features
de conveniência — persistência/estado de GUI NUNCA os alcança nem é lido pela CLI; (2) se
alguma tarefa futura só puder avançar mexendo nesse caminho, o assistente **PARA e reporta
ao autor**, de forma clara, **MAIS DE UMA VEZ** e marcada como **URGENTE**, ANTES de
priorizar a feature — nunca segue no automático; (3) se ainda assim o `.bat` for quebrado,
aplica-se a doutrina do autor: **regredir** para antes da feature, **limpar todo o vestígio**
e registrar aqui um **FIX** proibindo repetir o erro.

**Consequência.** Toda conversa futura (chat e Code) herda esse freio: conveniência jamais
tem precedência sobre o núcleo comprovado sem aprovação explícita e consciente do autor. Uma
guarda automatizada (`test_cli_has_no_settings`, spec0024) falha alto se a persistência
vazar para a CLI. Este DEC é apontado no `meta/CONTEXT.md` (armadilhas) e no `CLAUDE.md`
para ser lido no ritual de início das duas raias.

## DEC-021 — Force-include por caminho exato (`++path` no `.flatdropignore`)
**Data:** 2026-07-15 · **Status:** aceita (design; implementação na spec0027)

**Contexto.** Arquivos barrados por um ignore embutido (ex.: `.min.js` em
`DEFAULT_SUFFIX_IGNORES`) não podem ser resgatados pelo `!` do `.flatdropignore`: o corte
embutido roda antes do matcher onde o `!` age, e pastas podadas nem são visitadas. Faltava
liberar UM arquivo específico sem liberar todos os de um tipo.

**Decisão.** Novo mecanismo **force-include**: linhas `++caminho/exato` no `.flatdropignore`
(marcador distinto do `!`, extraídas antes do `pathspec`). Caminho EXATO, ancorado onde é
declarado. O arquivo é resgatado por `stat` direto (alcança dentro de pastas podadas sem
varrê-las) e **vence todos os cortes embutidos** (suffix/file-ignore, poda de pasta, matcher,
tipo) — **exceto "sensível"**, que permanece barrado (com aviso), coerente com "`!` não vence
sensível". Caminho inexistente vira aviso. Independe do `pathspec` (é pertinência de conjunto,
não glob).

**Consequência.** Resolve o caso `htmx.min.js` e afins de forma cirúrgica, sem reinundar o
mount. Vive na core/scan, lido do `.flatdropignore` que GUI e CLI consomem igual (paridade
FIX-004 preservada); não toca o gerador de `.bat` (DEC-020-safe). O arquivo forçado sai dos
pulados do `_TREE.md`/`_MANIFEST.md`. O editor visual poderá, no futuro, expor um terceiro
estado ("forçar mesmo assim"). Lógica verificada no sandbox contra a core real antes de virar
spec.

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

## DEC-022 — Nomear _MANIFEST/_TREE com o nome da pasta no fim
**Data:** 2026-07-20 · **Status:** aceita (spec0036)

**Contexto.** Vários projetos achatados no Claude têm `_MANIFEST.md`/`_TREE.md` homônimos —
ambíguos. O autor quer desambiguar com o nome da pasta de saída, mas no FIM (os projetos
buscam pelo prefixo `_MANIFEST`/`_TREE` no começo).

**Decisão.** Checkbox **default-ON** "Nomear _MANIFEST/_TREE com o nome da pasta": os meta
gerados viram `_MANIFEST_<pasta>.md`/`_TREE_<pasta>.md`, onde `<pasta>` = `dest.name` (o
campo "Nome da pasta", editável — não a raiz). Aplica-se só ao que está marcado. O flag
`--no-name-meta` leva o desligamento à CLI (paridade GUI×`.bat`, FIX-004). `is_our_folder`
passou a reconhecer `_MANIFEST*.md` para o "limpar destino" seguir funcionando.

**Consequência.** Muda o nome PADRÃO dos meta (default-ON) — `.bat` antigos passam a gerar
os nomes com sufixo (comportamento desejado). Só-core/CLI/GUI; o gerador do `.bat`
(`_generate_bat`) não muda, só ganha um flag aditivo em `_build_cli_args` (DEC-020,
autorizado). É preferência persistida (settings).

## DEC-023 — Vocabulário: `wo` para o delta aplicável, `spec` reservado para feature
**Data:** 2026-07-28 · **Status:** aceita

**Contexto.** Desde a criação do modo Claude Code (DEC-012), o delta estruturado que o chat
autora e o Code aplica se chamava **spec** e vivia em `meta/specs/` (`AAMMDD-specNNNN-desc.md`,
0001–0037 aplicadas). O template-update do KCM (v1.87.0) trouxe **duas** coisas de uma vez: o
mesmo artefato com outro nome (**WO**, *work order*, em `meta/workorders/`) **e** um `SPEC.md`
que é outra coisa — a **spec de feature** no espírito do Spec-Driven Development (GitHub
spec-kit): o problema, os critérios de aceite verificáveis, as decisões, o fora-de-escopo.
Manter "spec" com os dois sentidos garantiria confusão permanente.

**Decisão.** Separar os dois sentidos por nome:
- **WO** = **como aplicar**. Pasta `meta/workorders/`, nome `AAMMDD-woNNNN-desc.md`, comando
  `/apply-wo`. É o herdeiro direto das specs 0001–0037.
- **spec** = **o quê construir e quando está pronto**. Spec de feature, modelo em `meta/SPEC.md`,
  escrita em `meta/specs/` **só quando uma feature justifica** — nunca por rotina.

**Migração (deliberadamente parcial).** Os 37 arquivos existentes **mudam de pasta e mantêm o
nome** (`git mv meta\specs meta\workorders`). Nenhuma referência histórica é reescrita —
STATUS, CHANGELOG, DECISIONS e os logs continuam dizendo "spec0021", "spec0036", e isso está
certo: são as WOs de antes do nome mudar. A numeração **continua**: a próxima é `wo0038`.
`meta/specs/` fica vazia e renasce no primeiro uso real como casa das specs de feature.

**Alternativas consideradas.**
- **Não adotar WO** (manter tudo como "spec") — rejeitada: o `SPEC.md` do kit ficaria ambíguo,
  e a ambiguidade custaria uma explicação por sessão.
- **Migração total** (renomear os 37 arquivos e todas as referências) — rejeitada: reescreveria
  histórico em 4 documentos e nos logs, com custo alto e ganho cosmético. Registro histórico não
  se reescreve (mesma regra que rege este arquivo).

**Consequência.** Existe, de propósito, um período de coexistência: dentro de `meta/workorders/`
convivem nomes `spec00NN` (antigos) e `wo00NN` (novos). Quem ler os docs precisa saber disto —
por isso está no `CLAUDE.md`, no `CEREBRO.md` e no `GLOSSARY.md`. As WOs seguem ignoradas no
`.flatdropignore`; as specs de feature sobem ao Projeto (são poucas e dizem o que se constrói).

## DEC-024 — Comandos do Code viram Skills; o CEREBRO deixa de carregar apêndice
**Data:** 2026-07-28 · **Status:** aceita (supera a parte de arranque da DEC-012)

**Contexto.** Dois débitos herdados da montagem do modo Code: (1) os comandos `/` viviam em
`.claude/commands/*.md`, formato **legado** — o formato atual é **Skill** em
`.claude/skills/<nome>/SKILL.md`, com front-matter (`name`, `description`,
`disable-model-invocation`); (2) o `meta/CEREBRO.md` carregava um **apêndice** com o conteúdo de
`CLAUDE.md`, `settings.json` e dos comandos, "para criar no repo e depois apagar o apêndice".
O apêndice nunca foi apagado, divergiu do original (apontava para um `meta/DECISOES.md` que não
existe) e criava fonte de verdade dupla — contra a própria regra de higiene do CEREBRO.

**Decisão.** (1) `/apply-spec` e `/wrap` migram para `.claude/skills/apply-wo/SKILL.md` e
`.claude/skills/wrap/SKILL.md`, com front-matter e `disable-model-invocation: true` (impede o
Code de disparar o comando por conta própria). O conteúdo **vivo** é preservado — a versão do
projeto roda `python -m pytest -q` e usa Conventional Commits, coisas que o template genérico
não tem — e ganha do template a linha do **relatório de trabalho**. `.claude/commands/` é
removida. (2) O apêndice sai do CEREBRO, substituído por uma tabela que aponta para os arquivos
reais da raiz.

**Consequência.** O CEREBRO encolhe ~55 linhas e some uma referência errada. Fica registrado o
princípio que gerou o atrito: **template genérico nunca substitui arquivo vivo refinado** — a
comparação existe para colher o que há de novo, não para nivelar por baixo; a única exceção é
formato descontinuado, que sempre migra. Isso virou seção própria no CEREBRO ("Ao receber um
template-update do KCM") e crítica ao kit no IDEAS.

## DEC-025 — No `.flatdropignore`, ignorar `pasta/*` e nunca `pasta/`
**Data:** 2026-07-28 · **Status:** aceita

**Contexto.** O autor tentou liberar um único arquivo dentro de uma pasta ignorada
(`meta/legacy/` + `!meta/legacy/GOT_Build_-_Joker.md`) e o `!` não teve efeito: o `_TREE`
mostrava só `meta/legacy/  [ignorada: flatdropignore]`, e o editor da GUI, ao salvar, caiu no
fallback de ignorar arquivo a arquivo — frágil, porque arquivo novo na pasta entra sozinho.

**Causa raiz (medida, não suposta).** Não é o motor de padrões: `core._scan` **poda diretórios
in-place** antes de descer (`dirnames[:] = kept`, herança do FIX-001) e a poda sonda a pasta com
barra final. Com `meta/legacy/`, a sonda casa → a subárvore inteira é descartada → o arquivo
negado nunca é visitado. Verificado com `pathspec.PathSpec.from_lines("gitignore", ...)`, o
mesmo motor de `core._make_spec`:

| padrões | `meta/legacy/` casa (= poda)? | `GOT.md` ignorado? | `outro.md` ignorado? |
|---|---|---|---|
| `meta/legacy/` + `!…/GOT.md` | **True** (poda: o `!` nunca é avaliado) | False | True |
| `meta/legacy/*` + `!…/GOT.md` | False | False | True |

Ou seja: o motor **já libera** o arquivo (`match_file` devolve False para ele); quem o perde é a
poda. `PathSpec` (não `GitIgnoreSpec`) usa "a última regra que casa vence", então a negação
funciona — desde que a varredura chegue lá.

**Decisão.** Convenção do projeto: no `.flatdropignore`, pasta se escreve **`pasta/*`** (o
conteúdo), nunca **`pasta/`** (a pasta). O `.flatdropignore` da raiz foi reescrito nessa forma
(`logs/*`, `meta/workorders/*`) com a regra em comentário.

**Consequência.** É **contorno de convenção, não correção de produto**. O gerador do editor da
GUI continua escrevendo a forma `pasta/` (e caindo no fallback por arquivo), e o `_TREE` continua
colapsando a pasta podada sem dizer o que havia dentro. Os dois viraram item ativo no IDEAS e
são a próxima frente de trabalho — na frente do multi-raiz. Enquanto isso: **não salvar o
`.flatdropignore` pelo editor da GUI**, sob pena de o bloco `# >>> flatdrop-editor` reescrever
os padrões na forma antiga.

## FIX-011 — A negação `!` não resgatava arquivo dentro de pasta ignorada
**Data:** 2026-07-28

- **Sintoma:** `meta/legacy/` + `!meta/legacy/GOT.md` no `.flatdropignore` não trazia o
  arquivo; o `_TREE` mostrava só `meta/legacy/  [ignorada: flatdropignore]`, e o editor da
  GUI, ao salvar, caía no fallback de listar arquivo a arquivo.
- **Causa raiz:** não era o motor de padrões. `core._scan` **poda diretórios in-place**
  antes de descer (`dirnames[:] = kept`, herança do FIX-001); com a pasta podada, o `!`
  nunca chega a ser avaliado. Medido em DEC-025: `match_file` devolve *não ignorado* para o
  arquivo negado — quem o perde é a poda.
- **Solução:** `_negated_dir_prefixes` calcula, dos ignores coletados, as pastas alcançadas
  por alguma negação; a poda só descarta a pasta se ela **não** estiver nesse conjunto.
  Conservador com curinga: na dúvida, desce. O custo extra só existe quando há `!`.
- **Lição:** poda ≠ filtro. Otimização que corta a árvore antes de decidir muda a semântica,
  não só a performance — e o sintoma aparece longe da causa. A convenção `pasta/*` (DEC-025)
  continua valendo como cinto e suspensório, mas deixou de ser obrigatória.

## DEC-026 — Um log por DIA, sessões concatenadas
**Data:** 2026-07-28 · **Status:** aceita

**Contexto.** A convenção `logs/AAAA-MM-DD.md` não previu duas sessões no mesmo dia. Aconteceu
duas vezes (24/06 e 05/07) e foi resolvido na mão, com sufixos: `2026-06-24 (2).md` e
`2026-07-05 (novo menor, analisar e fazer merge com outro).md`. O resultado foi pior que o
problema — em 24/06 os dois arquivos diziam "cobre o dia inteiro" e **nenhum dos dois cobria**:
um tinha o teste real do usuário e o modal da UI-1, o outro tinha a spec-0008 e a DEC-014.
Informação perdida em ambos, e ninguém sabia qual ler.

**Decisão.** Um arquivo por dia. Segunda sessão no mesmo dia **concatena** no arquivo existente,
como seção `## Sessão N — <período>: <assunto>`, nunca como arquivo novo. Se um log já foi
entregue e a sessão continua, o chat reentrega o arquivo do dia INTEIRO, com a seção nova ao fim.

**Consequência.** Os quatro arquivos viraram dois (wo0040), com nota de fusão no topo e nada
descartado. A regra entrou no `meta/CEREBRO.md` e no `meta/LOG-TEMPLATE.md`.

## DEC-027 — A trava da pasta decide o futuro; o checkbox decide o presente
**Data:** 2026-07-28 · **Status:** aceita (altera o contrato da DEC-016)

**Contexto.** O editor de `.flatdropignore` tinha **um** controle (o checkbox tri-estado)
tentando responder **duas** perguntas independentes: *este arquivo sobe?* e *o que aparecer
aqui depois sobe?*. Pior: o checkbox da pasta nem é uma escolha — `folder_effective_state`
o **deriva** dos filhos, então "indeterminado" significa "os filhos estão misturados", nunca
"o autor decidiu algo sobre a pasta". A intenção da pasta não estava perdida no caminho:
**nunca existiu**. O gerador então adivinhava — colapsava a pasta em `pasta/` quando todos os
filhos estavam desmarcados — e o palpite errava nos dois sentidos: arquivo novo entrava numa
pasta parcialmente curada, e uma pasta esvaziada à mão virava exclusão dura sem ninguém pedir.

**Decisão.** Separar os dois controles.

- **Checkbox de arquivo:** *este arquivo sobe?* — como sempre foi.
- **Checkbox de pasta:** atalho para marcar/desmarcar todos os filhos. **Não influencia a
  trava** e continua sendo um agregado.
- **Trava da pasta (controle novo):** *arquivo novo aqui sobe?* — 🔓 aberta (padrão) ou
  🔒 fechada. É a única informação nova, e não é derivada de nada.

No core, `build_flatdropignore` ganha `locks: {rel_pasta: bool}` ao lado de `wants`, e a
heurística de colapso é **removida**. Trava ausente = estado efetivo de hoje, o que preserva o
round-trip sem palpite.

**Consequência (quebra de contrato assumida).** Pasta aberta com todos os filhos desmarcados
passa a escrever **uma linha por arquivo**, não `pasta/`. É o que o autor pediu explicitamente:
desmarcar 20 arquivos é desmarcar 20 arquivos; fechar a pasta é outro gesto. O teste
`test_editor_collapse_blocks_new_files` afirmava o contrário e foi reescrito — o comportamento
que ele protegia agora se obtém fechando a trava.

**Medido antes de decidir** (0.12.0, varredura real): `pasta/*` + `!pasta/x.md` deixa entrar só
`x.md` **e mantém arquivo novo fora**; `!pasta/*` abre pasta escondida pelo git e deixa arquivo
novo entrar; `!pasta/` e `!pasta/*` se comportam igual (padronizado em `/*`, DEC-025). E a
armadilha do aninhamento: `pasta/*` **não** casa `pasta/sub/arquivo.md` — só `pasta/sub/` como
diretório. Enquanto ninguém resgata nada lá dentro, a poda resolve; assim que um `!` desce, a
subpasta precisa da linha dela. Por isso o gerador emite uma linha por nível fechado.
## DEC-028 — Merge do template-update do KCM v1.95.0: o kit devolve o que este projeto ensinou
**Data:** 2026-08-01 · **Status:** aceita

**Contexto.** Chegou ao mount o pacote `__template-update` do KCM **v1.95.0** (19 arquivos +
`_UPDATE-MANIFEST.md`), o terceiro depois do v1.87.0/v1.88.0 (DEC-023 a DEC-025). Diferença
importante em relação aos anteriores, conferida na mensagem do KCM de 2026-07-29: **boa parte das
regras novas nasceu do «Feedback para o Kit» DESTE repo** (v1.89.0) — artefato gerado que convive
com edição humana, «não verificado nesta rodada» como resposta de primeira classe, a regra da
cópia que não é fonte da verdade colada ao campo **Estado**, e o gatilho testável de análise. Não
era novidade externa a avaliar: era conteúdo próprio voltando generalizado.

**Decisão.** Merge seletivo, em duas fases, com três critérios fixos:

1. **Novidade (a) entra** — 13 itens adotados. No `meta/CEREBRO.md`: artefato gerado × edição
   humana; os quatro modos de falha da releitura do mount; «não verifiquei» × «não é legível por
   este canal»; a contrapartida do carimbo de emissão; as três exigências novas do protocolo de
   update; o gatilho concreto e o abandono legítimo na análise; o teto por configuração; a linha
   de `analises/` na tabela. No Claude Code: o **relatório gravado em arquivo** na pasta-pai
   (`../AAMMDD-HHMM-code-flatdrop.txt`) com `additionalDirectories`. No `.flatdropignore`: o
   cabeçalho que explica a anatomia e o par `meta/workorders/*` + `!meta/workorders/_TEMPLATE.md`.
   Criado o `meta/SPEC.md`, que a DEC-023 já referenciava e nunca existiu. No `IDEAS.md`: a seção
   **Adiadas** com gatilho de retorno.
2. **Choque (b): o vivo fica** — sete confrontos, todos resolvidos a favor do arquivo vivo
   (princípios 8 e 11, tabela dos documentos, kit de arranque do Code, commit/artefatos de repo,
   rodapé dos gatilhos, LOG-TEMPLATE). Os quatro mais graves viraram feedback ao kit.
3. **(c) não se toca.** Nenhuma migração obrigatória: `.claude/commands/` já virou Skills na
   DEC-024, e era o único formato descontinuado da lista.

**Alternativas consideradas.**
- **Adotar o template inteiro** — descartada: apagaria o princípio 8 refinado, a DEC-026 e a
  proibição de voltar a `.claude/commands/`. É exatamente o que a regra «template genérico nunca
  substitui arquivo vivo refinado» existe para impedir.
- **Não adotar nada** («já temos tudo») — descartada: treze itens não existiam aqui, e um deles
  (o relatório em arquivo) automatiza um gesto manual que já tinha corrompido um relatório.
- **Fazer o merge num turno só** — descartada por tamanho: oito arquivos de comportamento numa
  fase, sete documentos de estado na outra, cada fase completa e commitável.

**Consequências.**
- O `.claude/settings.json` passa a permitir escrita **fora do repo** (`../`). É concessão
  deliberada e estreita: só a pasta-pai, e o Code diz e segue se a escrita for negada.
- O `.flatdropignore` foi reescrito **à mão** (o repo está no modo manual até o bug do bloco
  gerenciado ser corrigido) com tudo dentro do bloco e nada depois do `# <<<` — o que já elimina
  a duplicação que o próprio bug havia produzido.
- **Achado colateral que virou trabalho:** faltava a reinclusão do modelo das WOs, então
  `meta/workorders/_TEMPLATE.md` nunca chegou ao mount e não pôde ser comparado neste update. Nem
  o `_MANIFEST` (só lista o que subiu) nem o `_TREE` (a amostra da 0.14.0 esconde o meio) sabiam
  dizer se o arquivo existe. Conferir e, se faltar, criar — wo0044.
- As Instruções do Projeto ganharam 629 caracteres (5.514 → 6.143), dentro do teto novo (6.900 +
  550 do Modo Code). Na mesma passada corrigiu-se um resto **pré-DEC-023**: a seção do Modo Code
  ainda dizia `meta/specs/` e `AAMMDD-specNNNN-desc.md`.

## FIX-012 — o editor não convivia com regra escrita fora do bloco gerenciado
**Data:** 2026-08-02 · **Aberto em:** 0.13.0 · **Corrigido em:** 0.15.0 (wo0045 + wo0046)

**Sintomas.** Três, num `.flatdropignore` com curadoria manual fora do bloco: (1) salvar sem mexer
em nada copiava para dentro do bloco linhas que já existiam fora; (2) destravar uma pasta fechada
por linha manual não tinha efeito — o gerador só omitia a linha do bloco, a de fora continuava, e
ao reabrir a trava estava lá; (3) marcar um arquivo dentro dessa pasta trazia as duplicatas junto.

**Causa raiz.** A base de comparação era o **git puro**, herança de quando o bloco era o arquivo
inteiro. O gerador comparava o estado desejado com o que o `.gitignore` faria e era cego para a
curadoria manual do próprio `.flatdropignore`. **Sendo cego, não sabia que havia algo a corrigir:**
não duplicava de propósito (não via a linha de fora) e não emitia o `!` de destravamento (não via
o que precisava vencer).

**Correção.** A baseline passou a ser *gitignore + flatdropignore **sem** o bloco*
(`_collect_ignore_lines(..., skip_managed_root=True)`), e a emissão passou a escrever **apenas o
que diverge** dela — a tabela de quatro casos virou uma regra só. O bloco é um *diff*, nunca uma
cópia. Junto veio a posição fixa: o bloco é sempre reescrito no fim do arquivo.

**Defeito irmão, encontrado ao medir (wo0045).** Os marcadores eram procurados por **substring**:
um comentário que citasse o marcador fazia o corte acontecer na citação — bloco injetado no meio da
frase, bloco antigo sobrando no fim, linha truncada virando padrão ativo. Medido com o
`.flatdropignore` deste repo, escrito no dia anterior pelo próprio assistente: 35 linhas viravam
42. Corrigido junto: marcador é linha inteira, e arquivo ambíguo **recusa salvar**.

**Por que a suíte não pegou.** Nenhum dos 8 testes do editor tinha linha manual fora do bloco.
Fechado: os testes novos cobrem os três sintomas, o marcador citado e a estabilidade textual.

**Consequência a não estranhar.** Num arquivo curado à mão, o bloco gerenciado fica quase vazio.
É o comportamento certo — não há nada a corrigir —, mas parece que sumiu.

## DEC-029 — a anatomia normativa do `.flatdropignore`
**Data:** 2026-08-02 · **Status:** aceita · **Spec:**
`meta/specs/260802-spec-anatomia-flatdropignore.md`

**Contexto.** O FIX-012 tratou o problema como bug de algoritmo. Era metade: **o arquivo nunca teve
uma anatomia declarada**, então cada lado inventou a sua — o gerador supôs que o bloco era o
arquivo inteiro, o autor escreveu regra fora do bloco, e o assistente chegou a citar os marcadores
dentro de um comentário *para documentar a convenção*. A convenção existia na cabeça do autor (ele
já a usava no KCM); não existia escrita em lugar nenhum, e o que não está escrito não pode ser
garantido.

**Decisão — cinco regras.** (1) Comentário fica FORA do bloco. (2) Regra fica DENTRO. (3) Existe
UM bloco, e só um. (4) O bloco é sempre o ÚLTIMO conteúdo do arquivo. (5) Os marcadores não se
citam em comentário.

**O corolário é o objetivo, não um detalhe:** respeitadas as cinco, **editor visual e edição
manual podem ser usados livremente no mesmo arquivo**. A convenção não é restrição a mais — é o
que revoga o contorno «ou um, ou outro» que vigorava desde a 0.13.0.

**Duas obrigações que ela impõe à ferramenta**, e que valem para qualquer gerador do gênero:
**recusar, não adivinhar** (ambiguidade para o salvamento, porque reescrever é a única operação
irreversível) e **normalizar só o que é seu** (mover o próprio bloco é legítimo; mover o texto da
pessoa, não — e quando a normalização mudar o resultado efetivo de alguma regra dela, avisar).

**Alternativas descartadas.** *Deixar a convenção implícita e só corrigir o algoritmo* — foi o que
se tentou em 28/07, e o resultado foi o assistente violando a convenção ao documentá-la.
*Normalizar tudo automaticamente* (mover texto do autor, trocar `\` por `/`) — descartada: muda
semântica de um arquivo que outras ferramentas também leem.

**Consequência.** As cinco regras foram enviadas ao KCM como acréscimo ao princípio «artefato
gerado que convive com edição humana», que a v1.89.0 já tinha levado deste projeto. Princípio sem
forma testável não impede o erro — este caso é a prova.

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

## DEC-031 — o manifesto nomeia o rastreado divergente; o não rastreado continua anônimo

**Contexto.** A wo0048 decidiu «resumo, nunca listagem» no bloco de git, por dois motivos: ruído e
vazamento de nome de arquivo pessoal não rastreado. A regra funcionou, mas deixou sem resposta a
pergunta que o leitor do mount mais faz: *o arquivo que estou lendo é o commit, ou trabalho por
cima dele?* `1 modificado(s)` não diz qual.

**Decisão.** Nomear **apenas** os arquivos rastreados que (a) divergem do commit e (b) entraram no
achatamento. Não rastreado (`??`) e ignorado (`!!`) seguem fora, sem exceção.

**O que sustenta o corte.** Dos dois motivos da wo0048, o do vazamento **só vale para o não
rastreado** — e ali continua valendo inteiro. Para o rastreado que foi achatado ele não protege
coisa alguma: o nome já está na tabela do mesmo arquivo, poucas linhas acima. O motivo do ruído
some pela ordem de grandeza: são tipicamente 1 a 3 nomes, contra os 39 da tabela.

**Alternativa descartada — `mtime` por arquivo** (pedido do KCM na carta 01, item 2). Responde
«quando foi tocado», não «mudou»: `git checkout` carimba a hora do checkout em arquivo parado há
meses, e cópia com preservação de timestamp mantém data velha em arquivo recém-chegado. E cria um
dado que **autoriza a não ler** — que é o gesto que produziu a falha que o pedido tentava
consertar. O `git status` já sabe a resposta certa, de graça, e é dado de conteúdo. A recusa vai
argumentada na carta 02.

**Alternativa guardada — hash curto por arquivo.** Responde a pergunta vizinha («mudou desde a
geração anterior?»), que esta decisão só cobre em parte: arquivo alterado **e commitado** entre
duas gerações não aparece aqui, porque deixou de divergir. Fica com gatilho: volta quando uma
sessão precisar comparar duas gerações e esta linha não bastar. A regra que separa os dois
instrumentos, e que vale para qualquer um deles: **hash igual ao que já se leu JUSTIFICA pular a
releitura; data antiga apenas SUGERE.**

**Consequências.** `git_modified_paths` chama o git uma segunda vez em vez de alterar o retorno de
`git_snapshot`, que já tem seis testes em cima. O parser (`_modified_paths`) é puro e roda sem git
instalado. Em multi-fonte, o `rel` pode não ser relativo a `plan.root`; a interseção então não casa
e a linha não sai — falso negativo, nunca falso positivo.

## DEC-032 — as instruções do projeto sobem ao mount; e o desvio registrado sobre o push

**Contexto.** Merge do template-update do KCM **v1.120.0** (o `CEREBRO.md` daqui carregava a marca
da v1.95.0 — 23 versões de distância). A seção «Linhas revogadas» do pacote aponta texto que foi
apagado do kit de propósito e que segue vivo nos arquivos deste projeto, invisível a qualquer
comparação. **Varredura de 2026-08-25: 23 ocorrências**, 18 para remoção e 5 classificadas como
relato legítimo (reescrever relato falsificaria registro). Desta WO saem 8; o restante é a fase 2.

**Decisão 1 — `INSTRUCOES-DO-PROJETO.md` passa a subir ao mount.** A regra antiga excluía o arquivo
com a justificativa de que o painel do Projeto já o entrega. Está errada: o painel entrega um
TEXTO, o arquivo em disco é outro OBJETO, e não havia como conferir se batiam — os dois nunca
chegavam juntos. **Conferido em 25/08, pela primeira vez desde que o projeto existe: batem, linha a
linha.** O custo de subir é ~7 KB por geração; o benefício é que a superfície mais lida do projeto
passa a ser auditável por quem a lê.

**O que sustenta:** enquanto ficou fora, foi onde mais linha revogada sobreviveu — 5 das 23,
inclusive a que mandava reler o mount só mediante sinal do autor (revogada na v1.90.0). Em
2026-08-23 essa regra produziu a falha que ela descreve: o assistente abriu um turno sem reler o
mount e quase escreveu uma WO com âncoras de arquivos já mudados. O `CEREBRO.md` mandava reler a
cada turno; as instruções, lidas sempre, mandavam esperar o sinal. **Entre uma regra correta lida
às vezes e uma regra errada lida sempre, venceu a errada** — e é por isso que a exclusão de uma
superfície de leitura não é economia de tokens, é ponto cego.

**Decisão 2 — desvio registrado: o executor continua pedindo confirmação antes do `push`.** O kit
revogou, na v1.104.0, o desenho em que o chat entrega o bloco de git ao dono, e o substituiu por
«verde: o executor roda `add`/`commit`/`push` sem perguntar». **Adotamos tudo menos o push
automático.** O resto entra inteiro — e a parte mais valiosa é *o push se resolve ANTES de escrever
o relatório, que é o último passo*, que é a nossa própria Devolução 2 ao KCM voltando pronta.

**Por que o desvio.** Empurrar muda o estado de um remoto, e o Code pediu confirmação nas quatro
últimas WOs sem que isso custasse nada além de uma linha. A troca é: um turno a mais contra um
push que ninguém pediu. **Fica em revisão** — o gatilho para reabrir é a primeira vez que a
confirmação atrasar um relatório correto, que é o defeito oposto e já aconteceu uma vez (wo0051).

**Consequências.** A `wrap/SKILL.md` passa a citar este desvio no próprio texto, para que ninguém o
leia como esquecimento. O `.flatdropignore` perde a linha das instruções e ganha a explicação do
porquê — mas a linha vive DENTRO do bloco gerenciado, então o editor da GUI pode devolvê-la no
próximo salvamento: conferir uma vez na tela faz parte desta decisão.
