# 260624-spec0010 — Integração da atualização do KCM

**Tipo:** doc · **Alvos:** `meta/CEREBRO.md`, `meta/DECISIONS.md`, `meta/IDEAS.md`
**Autor:** chat · **Aplicador:** Claude Code · Sem build.
**Regra:** achar cada âncora EXATAMENTE; se faltar, PARAR e reportar.
**Nota:** primeira spec no novo padrão de nome do KCM — `AAMMDD-specNNNN-desc.md`.

## Contexto
O KCM atualizou. O nosso `CEREBRO.md` já estava quase todo no formato novo (princípios 1-19, higiene,
transferência, apêndice). Faltavam só: (1) a seção "Recomendação de configuração"; (2) a convenção nova de
nome de spec; (3) a referência `HISTORICO`→`HISTORY`. O HUB (projeto em grupo) foi **omitido** de propósito
(flatdrop é solo). O `.gitignore`/README proativo foi omitido por não se aplicar (o repo já tem os dois,
estáveis). Instruções do Projeto entregues à parte (arquivo inteiro).

---

## 1) CEREBRO.md — `HISTORICO` → `HISTORY` na tabela de docs

**Âncora:**
```
| `HISTORICO.md` | Cresce (histórico) | OPCIONAL — conhecimento consolidado de fases antigas (guias, análises que não cabem no CONTEXT enxuto). Lido sob demanda. |
```
**Ação:** SUBSTITUIR por:
```
| `HISTORY.md` | Cresce (histórico) | OPCIONAL — conhecimento consolidado de fases antigas (guias, análises que não cabem no CONTEXT enxuto). Lido sob demanda. |
```

## 2) CEREBRO.md — acrescentar a seção "Recomendação de configuração"

**Âncora:**
```
## Idioma

Respostas em pt-BR, incluindo comentários quando houver código.

## Desenvolvimento no Claude Code (raias chat ↔ Code)
```
**Ação:** SUBSTITUIR por (insere a seção de config ENTRE Idioma e Desenvolvimento):
```
## Idioma

Respostas em pt-BR, incluindo comentários quando houver código.

## Recomendação de configuração (fim de sessão)

No fim de cada sessão, junto do resumo e de qualquer dúvida, avalie o que a **próxima etapa** exige e recomende a configuração de forma **completa e explícita**. Os controles dependem de ONDE se trabalha:
- **No chat (claude.ai):** **modelo** (recomende pela capacidade — o mais capaz vs. um mais leve —, não pelo nome/versão, que muda), **esforço** (Baixo→Máximo) e **pensamento** (ligado/desligado): três controles independentes.
- **No Claude Code (CLI/desktop):** **modelo** + **nível de esforço** (`/effort` baixo→máximo, ou `xhigh`/`ultracode` onde houver). **Não há toggle de pensamento** no Code — ele é acoplado ao esforço; para um turno difícil pontual, use `ultrathink` no prompt. Nunca recomende "ligar o pensamento" no Code.
- **Nunca afirme saber a configuração atual** — ela não é legível de forma confiável. Recomende pela TAREFA e pela config que o usuário declarou.
- Próxima etapa **pesada** + config provável fraca → **pare e peça o aumento, nomeando os níveis exatos**.
- Etapa atual **leve** mas config **alta** → **não pare no meio**; termine e, no fim, sinalize "pode baixar para X na próxima".
- É um **default recomendado**, não proibição — cabe sob a válvula de desvio registrado.

## Desenvolvimento no Claude Code (raias chat ↔ Code)
```

## 3) CEREBRO.md — convenção nova de nome de spec (seção do Claude Code)

**Âncora:**
```
- **Claude Code (execução):** implementa código e faz edições **append-only** nos meta/ (linha no STATUS, `DEC-`/`FIX-` em DECISOES, marcar estado de fase). Aplica as specs de doc. Roda build/validação. Commita.
```
**Ação:** SUBSTITUIR por (acrescenta o bullet "Nomes padronizados"):
```
- **Claude Code (execução):** implementa código e faz edições **append-only** nos meta/ (linha no STATUS, `DEC-`/`FIX-` em DECISIONS, marcar estado de fase). Aplica as specs de doc. Roda build/validação. Commita.
- **Nomes padronizados:** specs em `meta/specs/` seguem `AAMMDD-specNNNN-desc.md` (ex.: `260624-spec0010-kit-update.md`). Numeração sequencial e estável; a data é a de criação. As specs antigas (`spec-0001…0009`, já aplicadas) ficam como estão; o padrão novo vale daqui pra frente. O chat nomeia; o Code aplica.
```

## 4) DECISIONS.md — DEC-015 (integração do KCM) ao FINAL

**Âncora (fim do arquivo):**
```
para coletar os arquivos de ignore (aceitável; fundível numa passada depois).
```
**Ação:** após essa linha, acrescentar:
```

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
```

## 5) IDEAS.md — Feedback para o Kit (ao FINAL)

**Âncora (último item do arquivo):**
```
- **Verificar lógica sutil no sandbox antes de virar spec.** O `.flatdropignore` (negação + aninhamento)
  foi testado com o pathspec real ANTES de escrever a spec — pegou uma expectativa minha errada e deu
  confiança no algoritmo. Vale como prática para qualquer regra não-óbvia.
```
**Ação:** acrescentar, logo após esse item:
```
- **Atualização do KCM integrada (DEC-015).** Adotados: seção de config, novo nome de spec
  (`AAMMDD-specNNNN-desc.md`), `HISTORICO`→`HISTORY`. Omitidos com registro: HUB (projeto solo) e a regra
  `.gitignore`/README proativa (o repo já tem os dois). Preservado o conteúdo específico do flatdrop —
  nada de sobrescrever meta/ com template em branco.
```
