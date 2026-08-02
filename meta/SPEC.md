# SPEC — [nome da feature]

> **Este arquivo é o MODELO — não o preencha aqui.** Copie para `meta/specs/AAMMDD-nome-da-feature.md`
> e preencha a cópia ANTES de codar. A pasta `meta/specs/` nasce no primeiro uso.
>
> **Spec ≠ WO (DEC-023).** A spec diz **o que** construir e **quando está pronto**; a **WO**
> (`meta/workorders/AAMMDD-woNNNN-desc.md`) diz **como aplicar** — âncora + texto exato. Se você ainda
> não sabe o que construir, não é hora nem de spec nem de WO: é hora de análise (`meta/analises/`).
>
> **Quando usar:** só quando uma feature justifica — nunca por rotina. Mudança pequena vai direto para
> a WO. Feature que mexe no core de ignores, na nomeação ou no contrato do `.bat` justifica.

## Problema

[Que dor real isto resolve? Para quem? O que acontece hoje sem isto? Sintoma observado, não teoria.]

## Critérios de aceite (verificáveis)

> Cada linha precisa ser conferível — se não dá para dizer «passou/não passou», reescreva.
> Diga também **onde** cada um é verificado: `pytest`, smoke manual no Windows, ou inspeção do arquivo gerado.

- [ ] [ex.: `pasta/*` com `!pasta/arquivo.md` deixa o arquivo subir — `tests/test_core.py`]
- [ ] [ex.: o `_TREE.md` mostra a faixa da pasta grande — smoke manual, `python run.py --tree`]

## Decisões de design

[O que foi escolhido e por quê; o que foi descartado e por quê. Decisão estrutural também vira DEC no
`meta/DECISIONS.md` — aqui fica o raciocínio, lá fica a decisão.]

## Fora de escopo

[O que esta feature deliberadamente NÃO vai fazer — o limite que impede o escopo de crescer sozinho.]

## Invariantes que esta feature NÃO pode quebrar

> Sempre confira o **DEC-020**: `flatdrop/cli.py`, `gui._build_cli_args`, `gui._generate_bat` e
> `gui._sources` são intocáveis por feature de estado/persistência. Se a feature só avançar mexendo
> neles, PARE e reporte como URGENTE antes de priorizá-la.

- [Invariante · DEC/FIX de referência]

## Passos

[Quebra em passos pequenos, ordenados, cada um entregável e testável. Cada passo vira uma WO — ou
todos viram uma WO só, se forem pequenos e do mesmo arquivo.]

1. [Passo — arquivo(s) tocado(s) — como se verifica.]

## Riscos e regressão possível

[O que vigiar depois de aplicar: que teste existente pode quebrar, que comportamento antigo depende
disto, o que só aparece em uso real no Windows.]
