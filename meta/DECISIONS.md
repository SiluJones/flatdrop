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
