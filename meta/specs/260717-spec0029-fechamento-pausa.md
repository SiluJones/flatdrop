# spec0029 — FECHAMENTO: higiene do STATUS, captura de ideia e marcação de pausa

- **Tipo:** meta-only (docs). NÃO altera código, NÃO precisa de testes (a rede é o `git diff`).
- **Data:** 2026-07-17 · **Versão:** permanece **0.7.1** (nada de código muda).
- **Por quê.** O projeto entra em **pausa planejada** (meses). Três problemas travam isso:
  1. **O cabeçalho do `STATUS.md` está defasado** e contradiz o próprio arquivo: o topo diz
     "revisão 2026-07-11, Versão 0.5.1, 48 testes, em aberto C e D", enquanto os bullets do
     fim já registram 0.7.1 / 62 testes / C e D **fechados**. Quem ler o STATUS primeiro (é
     o ritual) arranca com a informação errada. Fere "uma fonte de verdade por dado" e o
     caráter rolante do STATUS.
  2. **Uma ideia nova não está registrada** (nota `260717-1338`) — e ideia não capturada é
     ideia perdida numa pausa longa.
  3. **A pausa em si não está registrada** em lugar nenhum: sem isso, a próxima conversa não
     sabe se o silêncio foi planejado ou abandono.
- **Regra de segurança:** ache cada âncora EXATA; se alguma falhar, PARE e reporte.
- **DEC-020:** nada de código; o `.bat` não é tocado.

---

## Edit 1 — `meta/STATUS.md`: substituir a nota de revisão defasada

**Âncora exata** (bloco inteiro, linhas 6–13):
```
> **Mudanças nesta revisão (2026-07-11):** spec0019 (nomes alternativos +
> `.flatdropignore` vai ao mount, DEC-018) e spec0020 (gerador do editor corrigido:
> colapsa pasta cheia à prova de arquivo novo, base git-pura preserva exclusões no
> round-trip, checkbox indeterminado ao expandir; FIX-006) **aplicadas e
> commitadas**. Versão **0.5.1**, **48 testes verdes**. Higiene: `.gitignore` do
> Python + `__pycache__` destrastreado. **Próxima:** item C (persistência —
> configurações + pastas recentes na GUI). O trecho de KCM (`_TREE.md` →
> `.flatdropignore`) segue em aberto, ver backlog.
```
Trocar por:
```
> **Mudanças nesta revisão (2026-07-17):** specs 0021–0029 aplicadas e commitadas.
> Fechados nesta leva: **editor de `.flatdropignore` (Fase 2-D)**, **item C
> (persistência + recentes)**, **force-include `++`** e o **FIX-008** (nome voltando a
> renomear ao trocar de raiz). Versão **0.7.1**, **62 testes verdes**. Invariante
> **DEC-020** grava que o `.bat` não pode ser degradado por conveniência.
> **O projeto entra em PAUSA PLANEJADA a partir de 2026-07-17** — ferramenta estável e
> em uso real, sem bug aberto e sem fase grande pendente. **Ao retomar:** ler este
> STATUS, o `CHANGELOG` e as Ativas do `IDEAS.md`; a frente candidata é **multi-raiz na
> GUI**, que **exige decisão do autor antes de desenhar** (ver "Decisão pendente" abaixo).
```

## Edit 2 — `meta/STATUS.md`: atualizar Versão / Data / Fase / Situação

**Âncora exata** (bloco inteiro, linhas 15–25):
```
- **Versão:** 0.5.1 no `__init__.py` (spec0020: fix do gerador do editor de
  `.flatdropignore` + checkbox indeterminado, FIX-006). `[Não lançado]` no CHANGELOG
  só tem itens de produto em aberto.
- **Data:** 2026-07-11
- **Fase:** F1 (MVP) OK · F2 (robustez/conveniência): quase toda feita — em aberto C
  (persistência), D (editor de ignores = editor de `.flatdropignore`), multi-raiz na
  GUI, UI-2/UI-3 · F3 (gerador de `.bat` + multi-fonte na GUI) OK · F4 (distribuição
  + single-file) não iniciada — ver `ROADMAP.md`.
- **Situação geral:** em uso real e estável. Fluxo do monorepo `cinzeiro` coberto de
  ponta a ponta (GUI, CLI e `.bat`). Modo Claude Code em operação; specs 0001–0020
  aplicadas e commitadas.
```
Trocar por:
```
- **Versão:** 0.7.1 no `__init__.py` (spec0028: FIX-008, nome volta a renomear ao trocar
  de raiz). `[Não lançado]` no CHANGELOG só tem itens de produto em aberto.
- **Data:** 2026-07-17
- **Fase:** F1 (MVP) OK · F2 (robustez/conveniência) OK — **C (persistência) e D (editor
  de `.flatdropignore`) fechados**; em aberto só **multi-raiz na GUI** e **UI-2/UI-3**
  (polimento, opcionais) · F3 (gerador de `.bat` + multi-fonte na GUI) OK · F4
  (distribuição: `.exe`, single-file, contagem de tokens) não iniciada — ver `ROADMAP.md`.
- **Situação geral:** em uso real, **estável**, em **pausa planejada**. Fluxo do monorepo
  `cinzeiro` coberto de ponta a ponta (GUI, CLI e `.bat`). Modo Claude Code em operação;
  specs 0001–0029 aplicadas e commitadas. **62 testes verdes**; nenhum bug aberto.
- **Decisão pendente (bloqueia a próxima frente):** **multi-raiz na GUI** não tem versão
  "só-GUI, zero-toque" — a core já aceita N fontes, mas a CLI só tem `--root` + N
  `--also-md-from` (fontes só-`.md`). Ou (**B**) a GUI roda N raízes e o botão "Gerar
  .bat…" fica **desabilitado** no modo multi-raiz (o `.bat` nunca mente; caminho protegido
  intocado), ou (**A**) cria-se um flag aditivo `--add-root` e o `.bat` passa a codificar N
  raízes — o que **toca o caminho protegido** e, por DEC-020, exige aval consciente do
  autor + prova de que todo `.bat` de raiz única segue idêntico. **Recomendação: B.**
  Nada foi desenhado; a spec de design só começa depois dessa escolha.
```

## Edit 3 — `meta/STATUS.md`: risco de backup na seção "Riscos / pontos de atenção"

**Âncora exata:**
```
- **Nenhum bug aberto.** (FIX-005 resolvido pelo `conftest.py`.)
```
Trocar por:
```
- **Nenhum bug aberto.** (FIX-005 resolvido pelo `conftest.py`; FIX-008 corrigido na
  spec0028 — falta só o smoke manual de confirmação no Windows.)
- **Backup do repositório (atenção numa pausa longa).** Os commits recentes foram feitos
  na `main` **sem `git push`** e o repo não parecia ter remoto configurado. O repositório é
  a memória do projeto (specs, DECISIONS, CHANGELOG, logs) — se ficar só no disco local
  durante meses, uma falha de máquina apaga tudo. **Configurar um remoto (mesmo privado) e
  enviar antes de pausar.**
```

## Edit 4 — `meta/IDEAS.md`: capturar a ideia nova nas Ativas

**Âncora exata** (fim do bullet do force-include, nas Ativas):
```
  `.bat`. Mexe no `_scan` → pede spec de design. **Não urgente** (o autor adiou). (Ideia do
  usuário + assistente, nota 0827.)
```
Inserir DEPOIS:
```
- **Mostrar a REGRA de ignore que casou (não só a contagem).** Ao achatar, informar quais
  arquivos ficaram de fora por `.gitignore` **e por qual padrão** — para o autor perceber na
  hora se algo relevante foi podado. **Estado atual (verificado):** a contagem por motivo e
  uma amostra de nomes **já existem** (`Pulados: gitignore: N ↳ a.py, b.py…` na CLI/GUI e no
  `_TREE.md`); o que **falta** é a **regra que casou** — `_ignore_status` devolve só
  `(True, "gitignore", False)`, sem o padrão. Implementação exigiria o `pathspec` reportando
  o padrão vencedor (a API expõe isso por `match_file` com detalhes / iterar os patterns), o
  que encarece o scan. Valor real: quem lê o `_TREE.md` (inclusive o KCM) descobre *por que*
  o arquivo sumiu sem abrir o `.gitignore`. Escopo pequeno-médio, sem risco ao `.bat`
  (relato apenas). (Ideia do usuário, nota `260717-1338`.)
```

---

## Depois de aplicar (checklist do autor, fora do Code)

1. **Smoke manual do FIX-008** (Windows): abrir a GUI, trocar de raiz → nome renomeia;
   digitar um nome → trocar de raiz → nome digitado permanece.
2. **Confirmar o force-include no projeto real:** linha `++webapp/static/vendor/htmx.min.js`
   no `.flatdropignore`, gerar o mount e ver o arquivo aparecer.
3. **Backup do repo:** configurar remoto e `git push` (ver Edit 3) — é o passo mais
   importante antes de meses de pausa.

## Commit sugerido (sem acento)

```
git add meta/STATUS.md meta/IDEAS.md meta/specs/260717-spec0029-fechamento-pausa.md & git commit -m "docs(status): higiene do STATUS, captura de ideia e marcacao de pausa" -m "Cabecalho do STATUS estava defasado (dizia 0.5.1 e itens C/D em aberto) e contradizia os proprios bullets (0.7.1, C e D fechados); atualiza revisao, versao, data, fase e situacao. Registra a pausa planejada e a decisao pendente de multi-raiz (opcoes A/B sob DEC-020). Adiciona risco de backup: commits na main sem remoto configurado. Captura a ideia de mostrar a regra de ignore que casou, com o estado atual verificado."
```
