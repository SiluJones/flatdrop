# GLOSSARY — FlatDrop

Vocabulário do projeto. Mantém os termos consistentes entre conversas.

**FlatDrop.** A ferramenta deste repositório. Nome ainda tratável como provisório;
trocar aqui e no `README`/código se mudar.

**Achatar (flatten).** Copiar todos os arquivos de uma árvore de pastas para um
único nível (uma pasta só), desfazendo a hierarquia de diretórios.

**Raiz (root).** A pasta de projeto escolhida como ponto de partida da varredura.
Tudo abaixo dela é considerado; ela própria não é copiada, só lida.

**Destino (dest).** A pasta onde os arquivos achatados são gravados. Padrão: o
`Downloads` do usuário, numa subpasta com o nome da raiz (personalizável).

**Colisão.** Dois ou mais arquivos com o mesmo nome em pastas diferentes (ex.:
vários `page.tsx` num Next.js, vários `__init__.py` em Python). Achatados na mesma
pasta, colidiriam — daí a renomeação.

**Modos de renomeação.** Como os sufixos de pasta são aplicados:
- `collisions` (padrão): só arquivos que colidem ganham sufixo; o resto fica intacto.
- `all`: todo arquivo ganha ao menos o nome da pasta-pai.
- `fullpath`: cada arquivo carrega o caminho completo desde a raiz no nome.

**Desambiguação de profundidade uniforme.** A estratégia de renomeação: dentro de
um grupo de arquivos de mesmo nome, escolhe-se um único `k` (quantas pastas entram
no sufixo) que torna todos distintos, e aplica-se o **mesmo `k`** a todos do grupo.
Resultado simétrico e legível.

**Separador (sep).** O texto que cola o nome do arquivo às pastas no sufixo. Padrão
`__`. Em projetos Python (cheios de dunder) costuma-se preferir `-`.

**Allowlist (de tipos).** Conjunto de extensões e nomes de arquivos sem extensão
que o FlatDrop copia — texto e código úteis ao Claude. O que não está na lista é
pulado (imagens, binários, áudio, vídeo, PPTX).

**Denylist de sensíveis.** Padrões de arquivos com segredo (`.env` real, `*.pem`,
`*.key`, `id_rsa`, `secrets.*`…) que são sempre pulados, salvo se o usuário marcar
"incluir sensíveis". Exemplos como `.env.example` são permitidos. É filtro por
nome/sufixo, não scanner de conteúdo.

**Ignores embutidos.** Listas internas de diretórios (`node_modules`, `.git`,
`dist`, `.next`…), arquivos (lockfiles, `.DS_Store`…) e sufixos (`.min.js`, `.map`,
compilados) pulados mesmo sem `.gitignore`. Rede de segurança contra ruído.

**Manifesto (`_MANIFEST.md`).** Arquivo gerado na pasta de saída com metadados e a
tabela `caminho original → nome plano`. Devolve ao Claude a estrutura que o
achatamento desfez.

**Assinatura / marcador de pasta segura.** A primeira linha do manifesto,
`<!-- flatdrop-manifest v1 -->`. É como o FlatDrop reconhece que uma pasta foi
criada por ele e, só por isso, pode limpá-la antes de regravar. Pasta sem essa
assinatura nunca é apagada.

**`safe_clear`.** A função que esvazia a pasta de destino apenas se ela for vazia
ou comprovadamente nossa (tem a assinatura). Caso contrário, recusa-se a apagar.

**Plano (`FlattenPlan`).** O resultado de `make_plan`: a lista do que seria
copiado e renomeado, mais o que foi pulado e por quê — tudo **sem** gravar em
disco. É a base da pré-visualização.

**pathspec.** Biblioteca Python que interpreta padrões de `.gitignore`
corretamente (negação, `**`, âncoras). Dependência única e opcional do FlatDrop.

**TBW (terabytes written).** Métrica de durabilidade de SSD. Citada para concluir
que copiar poucos MB de texto ocasionalmente é irrelevante para o desgaste do
disco (ver DEC-002).

---

*Termos acrescentados na 0.2.0 (multi-fonte, filtros, CLI):*

**Fonte (`Source`).** Uma coleta: uma raiz com seu próprio conjunto de filtros.
Várias fontes podem ser combinadas numa única saída/manifesto (ver Multi-fonte).

**Multi-fonte.** Combinar mais de uma `Source` numa execução só, fundindo os
candidatos, deduplicando por caminho real e gravando **um** `_MANIFEST.md`. É o
que permite "todos os `.md` do repo + conteúdo de uma área" sem dois manifestos.
Implementado por `make_plan_sources`.

**Raiz comum.** Em multi-fonte, a pasta ancestral comum a todas as raízes das
fontes. Os caminhos no manifesto ficam relativos a ela, para a tabela ser coerente
entre coletas de raízes diferentes.

**Filtro de tipo.** `only_ext` (restringe a saída a certas extensões — corte
duro, ignora a allowlist ampla e os extensionless), `exclude_ext` (subtrai
extensões do que seria aceito) e `add_ext` (acrescenta extensões à allowlist
padrão, ex.: `gd`/`tscn` para Godot).

**Filtro de pasta.** `only_folders` + `folder_match` (`starts`/`contains`/
`exact`): um arquivo só entra se algum componente de pasta do seu caminho casar um
termo; um termo com `/` é tratado como prefixo de caminho relativo à raiz da fonte.

**CLI.** Interface de linha de comando (`flatdrop/cli.py`), acionada por
`python run.py <opções>`. Sem argumentos, `run.py` abre a GUI; com argumentos,
roda a CLI. Reaproveita a mesma core (sem regra de negócio duplicada).

**`--also-md-from <raiz>`.** Flag da CLI que adiciona a coleta "todos os `.md` a
partir de `<raiz>`" à mesma saída. Açúcar sobre o multi-fonte para o padrão "docs
do repositório + conteúdo de uma subpasta".

**Pacote de área.** No contexto do cinzeiro: a saída de um `.bat` de área — os
arquivos desenvolvidos (não-`.md`) daquela área **mais** todos os `.md` do grupo,
num só manifesto.
