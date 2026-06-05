# CONTEXT — FlatDrop

Documento de contexto principal. Leia este primeiro ao abrir uma nova conversa.
Para o estado atual, veja `STATUS.md`; para o porquê das escolhas, `DECISIONS.md`.

## O que é

FlatDrop é uma ferramenta de desktop (Windows em primeiro lugar) que **copia os
arquivos de uma pasta de projeto para uma única pasta plana** — por padrão no
`Downloads` —, achatando toda a árvore de subpastas em um nível só e renomeando
arquivos que colidiriam de nome, para que possam conviver soltos na mesma pasta.

O objetivo é prático: alimentar os **arquivos de um Projeto do Claude**. A
interface de upload aceita arquivos individuais, não pastas; então hoje o fluxo
manual é arrastar pasta por pasta e renomear duplicados (`page.tsx`,
`__init__.py`, `index.ts`…) à mão. O FlatDrop elimina esse trabalho: você roda,
ele organiza tudo numa pasta, e você arrasta uma vez só.

## Para quem é (e o que NÃO é)

- **Alvo:** o próprio autor do projeto, atualizando o conhecimento de um Projeto
  do Claude a partir de uma pasta local.
- **NÃO é um "repo-packer"/concatenador** (estilo Repomix/OneFile, que juntam o
  repositório inteiro num único arquivo XML/MD). O FlatDrop mantém arquivos
  **individuais** de propósito — assim o Claude indexa cada um e a atualização é
  granular (trocar um arquivo, não reenviar um blob gigante). Concatenar num só
  arquivo é uma ideia futura registrada, não o produto atual.
- **NÃO faz upload sozinho** para o Claude. Não existe API pública de upload para
  os arquivos de Projeto; a etapa de arrastar continua manual (e é só uma).
- **NÃO mexe na pasta de origem.** Apenas lê e copia.

## Stack

- **Python 3.11+** — tipagem moderna, `dataclasses`, `pathlib`.
- **tkinter** para a GUI — vem embutido no Python oficial de Windows/macOS, então
  o usuário final não instala nada além do Python (decisão DEC-008).
- **pathspec** — única dependência, e ainda assim **opcional**: serve para
  interpretar o `.gitignore` corretamente (negação, `**`, âncoras). Sem ela, o
  app cai num modo degradado que usa só os ignores embutidos (DEC-004).
- **pytest** — só para a suíte de testes; não é preciso para usar o app.

## Estrutura do repositório

```
flatdrop/
├── run.py                 # entrypoint: `python run.py` (ajusta sys.path, abre a GUI)
├── requirements.txt       # pathspec (opcional)
├── README.md              # uso e instalação para o usuário final
├── flatdrop/              # o pacote
│   ├── __init__.py        # __version__ = "0.1.0"
│   ├── config.py          # defaults: extensões, ignores de dir/arquivo, sensíveis, separador
│   ├── core.py            # LÓGICA PURA, sem UI — onde mora tudo que importa
│   └── gui.py             # interface tkinter; só coleta opções e chama a core
└── tests/
    └── test_core.py       # 13 testes (pytest) cobrindo o core
```

A separação **core × gui** é proposital (DEC-009): toda a lógica de varredura e
renomeação fica em `core.py`, sem importar tkinter, e é testável isoladamente. A
`gui.py` não contém regra de negócio — apenas amarra widgets à core e roda o
trabalho numa thread para não travar a janela.

## Como funciona (o pipeline)

O fluxo tem **duas fases**, espelhadas pelos botões "Pré-visualizar" e "Executar":

1. **`make_plan(root, cfg) -> FlattenPlan`** — varre a árvore a partir da raiz e
   calcula o nome final de cada arquivo, **sem escrever nada**. Devolve a lista de
   arquivos planejados, o que foi pulado (com motivo e amostras), o número de
   colisões e avisos. É uma pré-visualização segura.
2. **`execute_plan(plan, dest, cfg) -> ExecuteResult`** — resolve a pasta de
   destino, limpa-a se (e só se) for nossa, copia os arquivos com `shutil.copy2`
   e grava o `_MANIFEST.md`.

### A varredura (`_scan`)

Usa `os.walk(followlinks=False)` (não segue symlinks — evita loops, ver
armadilhas). Poda diretórios **in-place** (não desce em `node_modules`, `.git`,
`dist`, `.next`, etc.) para nem visitar lixo. Cada arquivo passa por uma sequência
de filtros e, se reprovado, é contabilizado por motivo (`gitignore`, `tipo`,
`sensível`, `ignore_padrão`):

1. Ignores embutidos de arquivo/sufixo (lockfiles, `.min.js`, `.map`, compilados).
2. `.gitignore` da raiz (via pathspec, se disponível).
3. Sensíveis (`.env` real, `*.pem`, `*.key`, `id_rsa`, `secrets.*`…), salvo se o
   usuário marcar "incluir sensíveis". Exemplos como `.env.example` passam.
4. Allowlist de tipos: só extensões de texto/código úteis ao Claude. Imagens,
   binários, áudio, vídeo e PPTX ficam de fora.

### A renomeação à prova de colisão (`_plan_names`) — o coração

A garantia central é: **os nomes finais são únicos**, comparados de forma
**case-insensitive** (porque o destino é Windows, que não diferencia maiúsculas).

A estratégia é de **profundidade uniforme por grupo de nome**, mais legível que o
ingênuo "sufixe com a pasta-pai":

1. Agrupa os candidatos pelo nome original (`stem+ext`, em minúsculas).
2. Para cada grupo com mais de um arquivo, escolhe **um único `k`** (quantas
   pastas, da mais interna para fora, entram no sufixo) que torna todos os membros
   distintos — e aplica o **mesmo `k` a todos**. Assim, todas as instâncias de
   `index.tsx` carregam a mesma profundidade de sufixo (fica simétrico e
   previsível), em vez de cada uma receber uma fatia diferente.
3. O "piso" de `k` depende do modo: `collisions` (piso 0 — quem não repete fica
   intacto), `all` (piso 1 — todo arquivo ganha ao menos a pasta-pai), `fullpath`
   (piso = profundidade total — caminho inteiro).
4. Trunca nomes que passem de `MAX_NAME_LEN` (200), preservando unicidade via um
   hash curto e estável do caminho relativo.
5. Passe final de **contador** (`_2`, `_3`…) para qualquer empate residual,
   inclusive a rara colisão entre grupos diferentes após truncamento.

O nome é montado como `stem + sep + pastas + ext`, ex.: `page__routes__users.tsx`.
O separador padrão é `__` (seguro em qualquer FS, visualmente distinto). Em
projetos Python, cheios de dunder, vale trocar para `-` na interface.

### O destino e o manifesto

`_resolve_dest` decide a pasta final com cuidado (DEC-007):

- Não existe ou está vazia → usa e cria.
- É **nossa** (tem o `_MANIFEST.md` com a assinatura `<!-- flatdrop-manifest v1 -->`)
  e "limpar" está ligado → `safe_clear` esvazia e reusa **a mesma pasta** (ideal
  para você sempre arrastar do mesmo lugar).
- É de **terceiros** (não-vazia, sem nossa assinatura) → **nunca** é apagada; o
  app cria uma variante numerada `nome (2)`.

`write_manifest` grava o `_MANIFEST.md`: assinatura + metadados (origem, data,
modo, contagem, tamanho, estimativa grosseira de ~`bytes/4` tokens) + a tabela
`caminho original → nome plano`. Ele cumpre dois papéis: devolve ao Claude a
estrutura que o achatamento desfez **e** é o marcador que prova que a pasta é
nossa (e portanto pode ser limpa).

## Armadilhas conhecidas (leia antes de mexer no core)

- **Windows é case-insensitive.** `Page.tsx` e `page.tsx` colidem no destino.
  Toda comparação de unicidade é feita em minúsculas. Não "otimize" isso para
  comparação sensível a maiúsculas.
- **Sufixo só de pasta-pai não garante unicidade.** Dois `index.tsx` em
  `app/users/` e `pages/users/` ambos virariam `index__users.tsx`. Por isso a
  profundidade é escolhida por grupo até desempatar — e ainda há o contador final.
- **Caminhos/nomes longos.** Achatar caminhos profundos gera nomes enormes; daí o
  truncamento com hash. Não remova o hash: é ele que mantém a unicidade após cortar.
- **Sensíveis vazam fácil.** Confiar só no `.gitignore` é arriscado (nem todo
  segredo está lá). A denylist embutida é uma rede de segurança — mas é por
  nome/sufixo, não por conteúdo. Sempre revise a pré-visualização.
- **Loops de symlink.** `os.walk` segue links por padrão e pode entrar em ciclo;
  por isso usamos `followlinks=False`. Mantenha assim.
- **tkinter não é thread-safe.** O trabalho pesado roda numa thread, mas todo
  toque em widget volta para a thread principal via `self.after`. Não chame
  widget direto de dentro da thread.
- **pathspec ausente = `.gitignore` ignorado.** O app avisa, mas não falha. Se a
  varredura trouxer coisa que o `.gitignore` deveria barrar, cheque se o pathspec
  está instalado.

## Convenções

- Documentação e comentários em **PT-BR**; identificadores de código em **inglês**.
- Mensagens de commit em **PT-BR**.
- Versionamento semântico; histórico em `CHANGELOG.md` (formato Keep a Changelog).
