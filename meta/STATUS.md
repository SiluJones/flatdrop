# STATUS — FlatDrop

Estado atual do projeto. Atualize ao fim de cada sessão de trabalho (rolante: o
resolvido sai daqui e vira `CHANGELOG`/`DECISIONS`).

> **Mudanças nesta revisão (2026-07-28) — atualização de meta, sem tocar em código:**
> merge do **template-update do KCM v1.87.0**. Três decisões novas: **DEC-023** (vocabulário —
> `meta/specs/` vira `meta/workorders/`, o delta aplicável passa a se chamar **WO**, a próxima
> é `wo0038`; os 37 arquivos existentes mudam de pasta e **mantêm o nome**, e nenhuma
> referência histórica é reescrita), **DEC-024** (comandos do Code viram **Skills** em
> `.claude/skills/`; o apêndice de arranque sai do `CEREBRO.md`) e **DEC-025** (no
> `.flatdropignore`, pasta se escreve `pasta/*`, nunca `pasta/` — causa raiz medida: `_scan`
> poda o diretório antes de descer, então o `!` dentro dele nunca é avaliado). Atualizados:
> `CEREBRO.md`, `CLAUDE.md`, as duas skills, `.gitignore`, `.flatdropignore`, `meta/README.md`,
> GLOSSARY, IDEAS, DECISIONS e as Instruções do Projeto. **Nada de código mudou** — a suíte não
> foi rodada nesta sessão (último número verificado: 68 verdes em 2026-07-21).
>
> _Notas de revisão anteriores (DEC-022/spec0036 em 20/07 e a higiene de 21/07 — backup,
> contagem de testes, backlog) foram absorvidas: o desfecho vive no `CHANGELOG` 0.11.0/0.10.1,
> em DEC-022/FIX-010 e nas seções abaixo._

- **Versão:** 0.11.0 no `__init__.py` (spec0036/DEC-022: nomear `_MANIFEST`/`_TREE` com o
  nome da pasta). `[Não lançado]` no CHANGELOG só tem itens de produto em aberto.
- **Data:** 2026-07-28
- **Fase:** F1 (MVP) OK · F2 (robustez/conveniência) OK — **C (persistência) e D (editor
  de `.flatdropignore`) fechados**; em aberto só **multi-raiz na GUI** e **UI-2/UI-3**
  (polimento, opcionais) · F3 (gerador de `.bat` + multi-fonte na GUI) OK · F4
  (distribuição: `.exe`, single-file, contagem de tokens) não iniciada — ver `ROADMAP.md`.
- **Situação geral:** em uso real, **estável**, em **pausa** (2026-07-21). Fluxo do monorepo
  `cinzeiro` coberto de ponta a ponta (GUI, CLI e `.bat`). Modo Claude Code em operação;
  **WOs 0001–0037 aplicadas e commitadas** (nomeadas `spec00NN`, anteriores à DEC-023; agora em `meta/workorders/`). **68 testes verdes**; nenhum bug aberto. Esta
  leva (0.8.0–0.11.0): atalho "abrir GUI" semeia navegação (0.8.0), gerar atalho da UI +
  Recentes compacto + layout em duas colunas (0.9.0–0.10.0), FIX-010 persistência de
  preferências + padrões de fábrica (0.10.1), e nomeação dos meta com o nome da pasta
  (0.11.0).
- **Decisão pendente (bloqueia a próxima frente):** **multi-raiz na GUI** não tem versão
  "só-GUI, zero-toque" — a core já aceita N fontes, mas a CLI só tem `--root` + N
  `--also-md-from` (fontes só-`.md`). Ou (**B**) a GUI roda N raízes e o botão "Gerar
  .bat…" fica **desabilitado** no modo multi-raiz (o `.bat` nunca mente; caminho protegido
  intocado), ou (**A**) cria-se um flag aditivo `--add-root` e o `.bat` passa a codificar N
  raízes — o que **toca o caminho protegido** e, por DEC-020, exige aval consciente do
  autor + prova de que todo `.bat` de raiz única segue idêntico. **Recomendação: B.**
  Nada foi desenhado; a spec de design só começa depois dessa escolha.
- **(2026-07-15, spec0021 aplicada) Editor de `.flatdropignore` (Fase 2-D) fechado:**
  glifo da pasta correto já na visão colapsada (`core.folder_effective_state`, FIX-007).
- **(2026-07-15, spec0024 aplicada) Item C — persistência entregue:** `flatdrop/settings.py`
  grava config + recentes (só-GUI; DEC-020 blinda o `.bat`). Versão **0.6.0**,
  **58 testes verdes**. Próxima = multi-raiz na GUI.
- **(2026-07-16, spec0027 aplicada) Force-include por caminho exato entregue (DEC-021):**
  `++caminho` no `.flatdropignore` resgata arquivo barrado por ignore embutido (vence tudo
  menos sensível); `.bat` intocado. Versão **0.7.0**, **62 testes**.
- **(2026-07-16, spec0028 aplicada) FIX-008:** o nome volta a renomear ao trocar de raiz
  (regressão da persistência corrigida). Versão **0.7.1**. Próxima = multi-raiz na GUI.
- **(2026-07-20, specs 0031–0033 aplicadas) Leva de conveniências de GUI, 0.9.0 → 0.9.2,
  66 testes verdes.** spec0031: menu **Ferramentas → "Gerar atalho da UI…"** gera o `.bat`
  que abre a interface (gerador NOVO e separado; RUN `.bat` intocado, DEC-020) — 1 teste
  novo (65 → 66). spec0032: **Recentes** compacto como botão **"Recentes ▾"** na linha da
  Raiz. spec0033/**FIX-009**: sub-frame na linha da Raiz tira a coluna global morta que o
  botão criava (grade de volta a 3 colunas). Pendências de smoke manual no Windows e dois
  prints candidatos a README (menu Ferramentas; linha da Raiz corrigida). Próxima = multi-
  raiz na GUI (decisão A/B do autor antes de desenhar).

## O que funciona (além do MVP)

- **CLI** (`python run.py <opções>`): mesma core da GUI. Sem args abre a GUI.
- **GUI repaginada (UI-1):** modal "Escolher tipos…" (checklist categorizado +
  busca + marcar/limpar por grupo + adicionar custom); tela compacta (resumo
  "Tipos: N de M"); abre **maximizada**.
- **`_TREE.md` opcional na saída (spec0011):** árvore da origem ao lado do
  `_MANIFEST.md` — copiados (renomeados marcados), pulados com o motivo, e pastas
  ignoradas colapsadas em UMA linha, sem recursão. Desligado por padrão (checkbox
  GUI + `--tree` CLI, serializado no `.bat`). Detalhe dos pulados via
  `--tree-detail summary|full`. É o par visual do `.flatdropignore`.
- **`root_in_name` (spec0013 + spec0014):** flag opcional — no modo fullpath e em
  fonte única, inclui o nome do projeto no nome de cada arquivo. Formato final:
  stem + caminho invertido + raiz no fim (`app/routes/page.tsx` sob `meuapp` →
  `page__routes__app__meuapp.tsx`; `README.md` → `README__meuapp.md`). Só no nome
  planejado; `rel` do manifesto/tree fica real. CLI `--root-in-name`; checkbox na
  GUI serializada no `.bat`.
- **Gerador de `.bat` na GUI:** "Gerar .bat…" serializa a config da tela num `.bat`
  ASCII (reproduz a seleção do modal via `--add-ext`/`--exclude-ext`).
- **Multi-fonte ao vivo na GUI:** toggle "Também incluir todos os `.md` a partir de
  [raiz]" vale no Pré-visualizar/Executar (FIX-004).
- **`.flatdropignore` + `.gitignore` aninhado (DEC-014):** ignore próprio por
  projeto, aninhado, com `!` para liberar o que o `.gitignore` bloqueia. Palavra
  final sobre o `.gitignore`. **Criável à mão ou pelo editor visual da GUI** (Fase 2-D,
  entregue na 0.4.0 — spec0018; gerador corrigido na 0.5.1 — spec0020, FIX-006).
  Aceita nomes alternativos (`.flatdropignore.txt`, `flatdropignore.txt`) e vai ao
  mount como o `.gitignore` (spec0019, DEC-018).
- **Allowlist expandida (DEC-013):** documentos aceitos pelo Projeto, Godot e várias
  linguagens/config. Imagens/áudio/vídeo fora.
- **Multi-fonte com manifesto único** (`make_plan_sources`) + `--also-md-from`.
- **Filtros de execução:** `only_ext`/`exclude_ext`/`add_ext`, `only_folder`/`folder_match`.
- **5 `.bat` do cinzeiro** (ASCII) + **launcher `flatdrop-ui.bat`**.
- **Downloads resolvido de verdade** (Known Folder / XDG) — FIX-002.
- Poda de pastas **visível** (contador + amostra + aviso) na GUI e CLI — FIX-001.

## Qualidade / testes

- **68 testes pytest passando** (conferido em 2026-07-21). Rodar da raiz:
  **`pytest -q`** (o `conftest.py` na raiz resolve o import — FIX-005) ou
  `python -m pytest -q`.
- Distribuição: `test_core.py` 48 (MVP + FIX-001 + filtros/multi-fonte/Downloads +
  `.flatdropignore` + `_TREE.md` + `root_in_name` + editor/spec0018 + aliases/spec0019 +
  gerador corrigido/spec0020 + nomeação dos meta/spec0036) · `test_settings.py` 9
  (persistência, spec0024 + FIX-010) · `test_cli.py` 7 · `test_force_include.py` 4
  (force-include `++`, DEC-021).
- A GUI **não** é coberta pela suíte (tkinter fora do CI) → smoke manual no Windows.

## Em aberto (produto) — backlog curto, na ordem sugerida

1. **Trecho de KCM: "Claude lê o `_TREE.md` → dita o `.flatdropignore`".** Conteúdo
   portável (não é código do FlatDrop): ensina o Claude de qualquer Projeto que usa
   FlatDrop a ler o `_TREE.md` (que mostra o motivo de cada exclusão) e devolver um
   `.flatdropignore` pronto — sobretudo para **liberar via `!` o que o `.gitignore`
   esconde**. Entregável: um bloco de KCM + exemplo no README. Rápido; destrava o
   fluxo que o `_TREE.md` já habilita. **PRIMEIRA tarefa da próxima conversa.**
2. ~~**Editor de `.flatdropignore` na GUI (= Fase 2-D).**~~ **ENTREGUE (0.4.0,
   spec0018; nomes alternativos + vai ao mount na 0.5.0, spec0019; gerador corrigido —
   colapso de pasta cheia, base git-pura no round-trip, checkbox indeterminado ao
   expandir — na 0.5.1, spec0020, FIX-006).** Modal `FlatDropIgnoreEditor` (árvore lazy,
   checkbox binário Opção B, tri-state por pasta, sinaliza o que o `.gitignore` esconde)
   + `annotate_children` / `build_flatdropignore` no core. Bloco gerenciado no
   round-trip. 3 testes (spec0018) + 2 (spec0019) + 2 (spec0020) novos. Falta só o
   smoke manual da GUI no Windows (a suíte não cobre tkinter).
3. ~~**C — Persistir configurações + pastas recentes** na GUI.~~ **ENTREGUE (0.6.0,
   spec0024):** `flatdrop/settings.py` grava config + recentes (JSON em
   `%APPDATA%`/`~/.config`); só-GUI, DEC-020 blinda o `.bat`. Depois: Recentes virou botão
   compacto (0.9.1, spec0032) e **FIX-010** devolveu as preferências ao abrir pelo atalho
   (0.10.1, spec0035). 9 testes em `test_settings.py`.
4. ~~Teto de nomes do `_TREE`.~~ **RESOLVIDO na 0.14.0 (wo0043)** — amostra com as duas pontas
   e o meio contado.
5. **Editor de `.flatdropignore` deveria gravar `pasta/*` + `!mantido`** em vez de listar a
   pasta parcial por folha. Depois do FIX-011 (0.12.0) deixou de ser bloqueio — o `!` funciona
   nas duas formas —, mas a lista por folha continua não sendo à prova de arquivo novo. Mexe na
   maquinaria de round-trip (DEC-016/spec0020). **Análise escrita e em discussão:**
   `meta/analises/260728-ANALISE-gerador-flatdropignore.md` — três opções (B, C, D), a decisão
   depende de responder "arquivo novo em pasta curada entra ou fica fora?". Aguarda o autor.
6. **Multi-raiz na GUI** (selecionar N pastas, prefixar cada uma com sua raiz). Decisão A/B
   ainda pendente (recomendação: B). **Adiada por decisão do autor (2026-07-28).**
7. **UI-2** (polimento de layout) e **UI-3** (presets "só docs"/"só código", lembrar
   última seleção).
8. **Formato "caminho escrito"** (`raiz__pastas__stem.ext`) como seletor de formato
   do nome — útil para empilhar por raiz, não para o Claude achar por nome. Espera.
9. Aviso mais visível quando o pathspec está ausente (destaque na GUI).
10. Saída da CLI ASCII-safe (`->`/`*`). ~~Botão "Gerar atalho da UI".~~ **ENTREGUE (0.9.0,
   spec0031):** menu **Ferramentas → "Gerar atalho da UI…"** (gerador NOVO e separado; o
   RUN `.bat` ficou intocado, DEC-020).

## Riscos / pontos de atenção

- 🔴 **BUG ABERTO (0.13.0): o editor não convive com regras escritas FORA do bloco gerenciado.**
  Reproduzido em sandbox e no `.flatdropignore` real deste repo. Três defeitos, uma causa:
  1. **Duplicação.** Salvar sem mexer em nada copia para dentro do bloco as linhas que já
     existiam fora dele (aqui: `meta/workorders/*` e `INSTRUCOES-DO-PROJETO.md` aparecem duas
     vezes). A curadoria manual vira sombra de uma cópia gerada.
  2. **Destravar não funciona.** Se a trava vem de uma linha manual fora do bloco, destravar na
     GUI só faz o gerador *omitir* a linha do bloco — a de fora continua lá, a pasta segue
     travada, e ao reabrir o editor a trava volta. O clique é desfeito em silêncio.
  3. **Marcar um arquivo excluído por linha manual também não tem efeito**, pela mesma razão:
     o bloco não emite o `!` que precisaria vencer a linha de fora.
  **Causa raiz:** o gerador usa como referência o **git puro**, não "tudo o que já existe menos
  o meu bloco". Quem só lê o `.gitignore` não enxerga a curadoria manual do próprio
  `.flatdropignore`, então não sabe nem que precisa corrigi-la. Agravado por não haver garantia
  de que o bloco fique por ÚLTIMO no arquivo (vale a última regra que casa).
  **Contorno até a correção:** manter a curadoria manual OU usar o editor, não os dois no mesmo
  arquivo. **Análise com o desenho da correção:**
  `meta/analises/260728-ANALISE-bloco-gerenciado-vs-manual.md`.
- ~~O `!` não resgata arquivo dentro de pasta ignorada.~~ **RESOLVIDO na 0.12.0 (FIX-011,
  wo0038).** A poda passou a consultar as pastas alcançadas por negação. A convenção `pasta/*`
  (DEC-025) segue recomendada, mas deixou de ser obrigatória.
- **`meta/DECISIONS.md` passou de 700 linhas** (793 com DEC-023/024/025). O arquivamento em
  `DECISIONS-archive.md` está pendente **de propósito**: fazer agora, no meio da mudança de
  vocabulário, mexeria nas mesmas referências duas vezes. Fazer depois do commit da migração.
- Nenhum bug de código aberto. (FIX-005 resolvido pelo `conftest.py`; FIX-008 corrigido na
  spec0028 — falta só o smoke manual de confirmação no Windows.)
- **Backup do repositório — RESOLVIDO em 2026-07-21 (era o risco nº 1 da pausa).** O remoto
  já existia (`origin` → `github.com:SiluJones/flatdrop.git`, SSH), mas a `main` local **não
  o rastreava** e estava **3 commits à frente** (layout em duas colunas, DEC-022/FIX-010 e o
  fechamento da spec0037) — a leva 0.10.0–0.11.0 só existia no disco. `git push -u origin
  main` enviou tudo e amarrou o tracking, então daqui em diante o `git status` avisa sozinho
  quando houver commit local não enviado. O repositório é a memória do projeto (specs,
  DECISIONS, CHANGELOG, logs). **Hábito para o retorno: `git push` antes de fechar a
  sessão.**
- O `_TREE.md` deste projeto mostra `Pulados: 0` (sem `.flatdropignore` nem arquivos
  pulados por tipo aqui) — a diferença `summary`×`full` e as linhas `[pulado: …]` só
  aparecem "ao vivo" num projeto com `.env`/`.flatdropignore`. Coberto por testes.
- O fix do Downloads e a GUI só foram exercidos por estrutura/lógica no sandbox (sem
  Windows no ambiente do chat); a validação final é o smoke manual no PC.
- A estimativa de tokens segue grosseira (`bytes/4`) e não vale para binários.
- `.flatdropignore` faz uma passada extra na árvore para coletar os ignores
  (aceitável; fundível numa passada depois, se virar gargalo).
