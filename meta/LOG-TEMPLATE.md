# LOG-TEMPLATE — FlatDrop

> **Referência fixa.** Este arquivo é o MOLDE — nunca é substituído pelo conteúdo preenchido.
> Um arquivo por DIA (DEC-026). Segunda conversa no mesmo dia entra como
> `## Conversa N — <período>: <assunto>` neste mesmo arquivo — nunca um arquivo novo, porque o
> nome é da data e não da conversa.

O log entra **ao bater um gatilho de evento** — cortar versão, registrar decisão ou bug grave,
virar o dia — e **não «no fim»**, que numa conversa longa nunca chega: é assim que dias inteiros
ficam sem registro. Os logs vivem em `logs/` no Git (NÃO no Projeto) e são lidos sob demanda.

Como usar:
1. Copie este arquivo para `logs/` com a data de hoje no nome (ex.: `logs/2026-06-05.md`).
   Se o arquivo do dia já existe, acrescente `## Conversa N` nele — não crie outro.
2. Substitua os campos entre colchetes pelo conteúdo real.
3. Ao terminar, atualize também `STATUS.md` (inclusive a seção «Última conversa») e, se houver
   mudança de versão, `CHANGELOG.md`.

---

# Log — [AAAA-MM-DD]

## Objetivo do dia
[O que se pretendia fazer hoje, em uma ou duas frases.]

## O que foi feito
- [Item concluído.]
- [Item concluído.]

## Decisões
- [Nova decisão tomada e seu número, se aplicável — registre em `DECISIONS.md`.]
- [Ou: "Nenhuma decisão nova."]

## Bugs / problemas
- [Bug encontrado e estado: aberto / corrigido / contornado.]
- [Ou: "Nenhum."]

## Aprendizados / armadilhas
- [Algo que se descobriu e que vale lembrar na próxima.]

## Onde parei
[Estado exato ao encerrar: o que está pronto, o que ficou no meio, e o próximo passo óbvio.
Este campo alimenta a seção «Última conversa» do `STATUS.md` — escreva-o pensando em quem abre
a conversa seguinte sem ter lido esta.]

## Próximos passos
- [O primeiro passo concreto para o próximo turno.]
- [Outros passos.]
