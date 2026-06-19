# IDEAS — FlatDrop

Banco de ideias. Não é compromisso nem prazo — é onde pensamentos ficam até
virarem item de `ROADMAP.md`, serem implementados ou descartados. Ideia adotada
vira item do roadmap; implementada vai para "Concluídas"; recusada vai para
"Descartadas" com o motivo. Nunca se perde nada — muda de status.

> **Mudanças nesta revisão (2026-06-14):** os filtros de seleção (por tipo, por
> pasta) e o multi-fonte "docs do repo + conteúdo de área num manifesto" saíram
> de "Ativas" para **Concluídas** (entregues na 0.2.0). Capturadas as ideias
> novas dos arquivos `ideia-260612`/`260613`: gerador de `.bat` pela interface,
> e single-file com os mesmos filtros.

## Ativas

- **`_TREE.md` na saída.** Gerar (opcional, ligado por padrão) uma árvore
  indentada da origem na pasta de saída: arquivos copiados limpos, pulados com o
  motivo, pastas podadas fechadas. Resolve o "Claude não acha `page.tsx` porque
  virou `page__users.tsx`" e dá visão do que nem subiu. Sem duplicar o manifesto
  (que mapeia nome→origem); o tree cobre estrutura e exclusões. (Fase 2 — item B.)
- **Pastas recentes + persistir configurações.** Lembrar últimas raízes, destino,
  modo, separador, toggles e extensões entre execuções (JSON em
  `%APPDATA%`/`~/.config`); Combobox de recentes na GUI. (Fase 2 — item C.)
- **Ignores de pasta editáveis na GUI** com núcleo imutável
  (`.git`/`node_modules`/`__pycache__`/VCS sempre reaplicados), para tirar/pôr
  pastas como `dist`/`build`/`.venv` caso a caso. (Fase 2 — item D.)
- **Gerador de `.bat` pela interface.** Botão "Exportar `.bat`…" que serializa a
  configuração atual da tela (raiz, modo, filtros, toggles) numa linha de comando
  e salva o arquivo — fecha o ciclo: configura visual, leva o `.bat`, sem decorar
  flag. A própria tela de config vira o editor do `.bat` (não precisa de página
  separada). Depende da CLI (feita) e dos filtros (feitos); expressar multi-fonte
  no exportador exige um pouco de UI. (Fase 3.)
- **Multi-fonte também na GUI.** Hoje multi-fonte é só CLI/`.bat` (CLI-first).
  Expor na GUI (ex.: um toggle "incluir todos os `.md` a partir de [raiz]") casa
  com o exportador de `.bat`. (Fase 3, junto do exportador.)
- **`.gitignore` aninhado.** Ler também os `.gitignore` de subpastas, como o git
  faz. Hoje lê só o da raiz da fonte — o que, no fluxo de área, joga a favor
  (a raiz da área não herda o `.gitignore` do pai). Útil em monorepos. (Stand-by.)
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

- **Selecionar por tipo na execução** ("quero só os `.md`", "tudo menos `.md`").
  Entregue na 0.2.0 como `--only-ext` / `--exclude-ext` / `--add-ext`.
- **Selecionar por pasta** ("só desta pasta e filhos", "pastas que começam com
  X"). Entregue como `--only-folder` + `--folder-match` (e raiz da fonte para o
  caso "só esta pasta").
- **Combinar "todos os `.md` do repo" + "conteúdo de uma área" num só manifesto.**
  Entregue via multi-fonte (`make_plan_sources`/`Source`) e o atalho
  `--also-md-from`. Resolve o impasse dos "dois manifestos" sem dois passos.
- **`.bat` para ativar em pastas de trabalho.** Entregues os 5 do cinzeiro em
  `bat/cinzeiro/` (um só-`.md`, um por área).
- **CLI sem GUI.** Entregue (`flatdrop/cli.py`); era item da Fase 3, antecipado
  porque destravava os `.bat`.

## Descartadas

- **Ser só single-file (sem o modo pasta).** O fluxo é de arquivos individuais no
  Projeto, com atualização granular. Single-file é complemento. (Ver DEC-001.)
- **Mover os arquivos em vez de copiar.** Destruiria a origem. (Ver DEC-002.)
- **Usar symlinks em vez de copiar.** Não se resolvem no fluxo de arrastar; Windows
  os trata de forma inconsistente. (Ver DEC-002.)
- **Upload automático para o Claude.** Não há API pública para os arquivos de
  Projeto; arrastar continua manual (e é só uma etapa).
- **Mover imagens/áudio/vídeo para a saída.** O Projeto do Claude não os usa como
  texto; ignorá-los é o certo. Se algum dia for preciso incluir, reabrir via um
  toggle explícito. (Confirmado com o usuário em 2026-06-14.)
