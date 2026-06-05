# IDEAS — FlatDrop

Banco de ideias. Não é compromisso nem prazo — é onde pensamentos ficam até
virarem item de `ROADMAP.md` ou serem descartados. Quando uma ideia for adotada,
mova-a para o roadmap; quando for recusada, mova para "Descartadas" com o motivo.

## Ativas

- **Modo single-file opcional (estilo Repomix).** Além de achatar para pasta,
  oferecer um botão que concatena tudo num único `.md`/`.xml` com cabeçalhos por
  arquivo. Útil quando se quer colar o projeto inteiro numa conversa avulsa em vez
  de nos arquivos de um Projeto. (Ver Fase 4 do roadmap.)
- **Empacotar como `.exe` (PyInstaller).** Para o PC sem Python instalado: um
  executável de duplo-clique. (Fase 3.)
- **CLI sem GUI.** Um comando `flatdrop <raiz> [opções]` reaproveitando o mesmo
  core, para automação e para terminais. (Fase 3.)
- **Persistir configurações.** Lembrar a última raiz, destino, modo, separador e
  extensões entre execuções (um pequeno JSON em `%APPDATA%`/`~/.config`).
- **`.gitignore` aninhado.** Hoje lê só o `.gitignore` da raiz; ler também os de
  subpastas, como o git de fato faz, para projetos com ignores por módulo.
- **Resync incremental por diff do manifesto.** Comparar com o `_MANIFEST.md`
  anterior e copiar/avisar só o que mudou, para atualizações rápidas.
- **Watch / resync automático.** Observar a pasta raiz e reachatá-la quando algo
  mudar, deixando a pasta de saída sempre fresca.
- **Drag-and-drop da pasta raiz na janela.** Arrastar a pasta para a janela em vez
  de navegar pelo seletor (exigiria tkinterdnd2 ou similar — pesar contra o
  princípio de zero dependências).
- **Contagem de tokens mais fiel.** Trocar a estimativa `bytes/4` por um
  tokenizador real (opcional), para quem quer mirar o teto de contexto com
  precisão.

## Descartadas

- **Ser só single-file (sem o modo pasta).** Descartado: o fluxo do usuário é de
  arquivos individuais nos arquivos do Projeto, com indexação e atualização
  granular. O single-file vira complemento, não substituto. (Ver DEC-001.)
- **Mover os arquivos em vez de copiar.** Descartado: destruiria a pasta de
  origem. (Ver DEC-002.)
- **Usar symlinks em vez de copiar.** Descartado: links não se resolvem no fluxo
  de arrastar para um app, e o Windows os trata de forma inconsistente.
  (Ver DEC-002.)
- **Fazer upload automático para o Claude.** Descartado: não há API pública para
  os arquivos de Projeto; a etapa de arrastar continua manual (e é só uma).
