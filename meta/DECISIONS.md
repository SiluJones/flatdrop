# DECISIONS — FlatDrop

Registro de decisões de arquitetura (ADR enxuto). Cada entrada: contexto, decisão
e consequência. Decisões não se reescrevem — se mudarem, adicione uma nova que
supersede a anterior.

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
