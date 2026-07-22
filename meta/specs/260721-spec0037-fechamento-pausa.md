# spec0037 — FECHAMENTO: higiene do STATUS e marcação de pausa (0.11.0)

- **Tipo:** meta-only (docs). NÃO altera código, NÃO precisa de testes. Versão permanece
  **0.11.0**.
- **Data:** 2026-07-21.
- **Por quê.** A **nota de revisão** do STATUS está em dia (0.11.0), mas o **bloco fixo
  abaixo** (Versão, Data, Situação geral) envelheceu — ainda diz **0.7.1**, **specs
  0001–0029**, **62 testes**, data 2026-07-17. Quem lê o STATUS no ritual arranca errado. E o
  projeto entra de novo em **pausa**, que precisa estar marcada.
- **Regra:** ache cada âncora EXATA; se falhar, PARE e reporte. DEC-020: nada de código.

---

## Edit 1 — `meta/STATUS.md`: marcar a pausa na nota de revisão

**Âncora exata:**
```
> Versão **0.11.0**, **68 testes verdes**. **Frente maior:** multi-raiz (decisão A/B pendente).
```
Trocar por:
```
> Versão **0.11.0**, **68 testes verdes**. **O projeto entra de novo em PAUSA a partir de
> 2026-07-21** — uso real, estável, sem bug aberto. **Ao retomar:** ler este STATUS, o
> `CHANGELOG` e as Ativas do `IDEAS.md`. **Frente candidata maior:** multi-raiz (decisão A/B
> pendente, ver abaixo). **Antes de tudo:** conferir o backup do repo (ver Riscos).
```

## Edit 2 — `meta/STATUS.md`: atualizar Versão

**Âncora exata:**
```
- **Versão:** 0.7.1 no `__init__.py` (spec0028: FIX-008, nome volta a renomear ao trocar
  de raiz). `[Não lançado]` no CHANGELOG só tem itens de produto em aberto.
```
Trocar por:
```
- **Versão:** 0.11.0 no `__init__.py` (spec0036/DEC-022: nomear `_MANIFEST`/`_TREE` com o
  nome da pasta). `[Não lançado]` no CHANGELOG só tem itens de produto em aberto.
```

## Edit 3 — `meta/STATUS.md`: atualizar Data

**Âncora exata:**
```
- **Data:** 2026-07-17
```
Trocar por:
```
- **Data:** 2026-07-21
```

## Edit 4 — `meta/STATUS.md`: atualizar Situação geral

**Âncora exata:**
```
- **Situação geral:** em uso real, **estável**, em **pausa planejada**. Fluxo do monorepo
  `cinzeiro` coberto de ponta a ponta (GUI, CLI e `.bat`). Modo Claude Code em operação;
  specs 0001–0029 aplicadas e commitadas. **62 testes verdes**; nenhum bug aberto.
```
Trocar por:
```
- **Situação geral:** em uso real, **estável**, em **pausa** (2026-07-21). Fluxo do monorepo
  `cinzeiro` coberto de ponta a ponta (GUI, CLI e `.bat`). Modo Claude Code em operação;
  **specs 0001–0037 aplicadas e commitadas**. **68 testes verdes**; nenhum bug aberto. Esta
  leva (0.8.0–0.11.0): atalho "abrir GUI" semeia navegação (0.8.0), gerar atalho da UI +
  Recentes compacto + layout em duas colunas (0.9.0–0.10.0), FIX-010 persistência de
  preferências + padrões de fábrica (0.10.1), e nomeação dos meta com o nome da pasta
  (0.11.0).
```

---

## Depois de aplicar (checklist do autor)

1. **Backup do repo — o mais crítico antes de meses de pausa.** Conferir se há remoto
   configurado e `git push` (ver seção Riscos do STATUS). O repositório É a memória.
2. Smoke manual pendente da leva (se ainda não fez): nomeação ON/OFF, portão do `.bat`,
   preferências pelo atalho, "Restaurar padrões de fábrica…".

## Commit sugerido (sem acento)

```
git add meta/STATUS.md meta/specs/260721-spec0037-fechamento-pausa.md & git commit -m "docs(status): higiene do bloco fixo e marcacao de pausa (0.11.0)" -m "O bloco fixo do STATUS (Versao/Data/Situacao) dizia 0.7.1/specs 0001-0029/62 testes; atualiza para 0.11.0/specs 0001-0037/68 testes, data 2026-07-21, e marca a pausa. Nota de revisao ganha o marcador de pausa e o lembrete de backup do repo."
```
