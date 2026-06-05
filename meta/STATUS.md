# STATUS — FlatDrop

Estado atual do projeto. Atualize ao fim de cada sessão de trabalho.

- **Versão:** 0.1.0
- **Data:** 2026-06-05
- **Fase:** F1 (MVP) concluída ✅ — ver `ROADMAP.md`.
- **Situação geral:** funcional e testado. Pronto para o primeiro teste em um
  projeto real do usuário, no Windows.

## O que já funciona

- GUI tkinter completa: seleção de pasta raiz (auto-preenche o nome da saída),
  destino (padrão `Downloads`), nome da pasta de saída, três modos de renomeação,
  toggles (ler `.gitignore`, pular sensíveis, limpar destino, gerar manifesto),
  campo de separador, editor de extensões com "Restaurar padrão", e os botões
  Pré-visualizar / Executar / Abrir pasta, com área de saída e status.
- Pipeline planejar→executar (`make_plan` / `execute_plan`) operante.
- Varredura com poda de diretórios, leitura de `.gitignore` (via pathspec),
  ignores embutidos, denylist de sensíveis e allowlist de tipos.
- Renomeação à prova de colisão com unicidade garantida (case-insensitive),
  profundidade uniforme por grupo, truncamento de nomes longos e contador final.
- Três modos verificados: `collisions`, `all`, `fullpath`.
- `safe_clear` que só limpa pasta vazia ou comprovadamente nossa; pasta de
  terceiros vira variante `nome (2)`. Reexecução reusa e limpa a mesma pasta.
- `_MANIFEST.md` gerado com metadados + mapa origem→nome + estimativa de tokens.

## Qualidade / testes

- **13 testes pytest passando** (`python -m pytest -q` a partir da raiz).
- Cobrem: unicidade nos três modos; `.gitignore` + ignores embutidos; `.env`
  pulado mas `.env.example` permitido; modo `collisions` deixa único intacto;
  modo `all` sufixa único em subpasta; grupo de colisão com profundidade
  uniforme; execução grava manifesto e marca a pasta; reexecução limpa a pasta
  própria; `safe_clear` recusa pasta de terceiros; destino de terceiros vira
  `(2)`; casos-limite de `split_name`.
- Smoke test manual executado com saída conferida (os quatro `index.tsx` viram
  nomes distintos; sensíveis e ruído pulados corretamente).

## Pendências imediatas (próxima sessão)

- **Testar em um projeto real** no Windows (um Next.js e um Python seriam ideais
  para exercitar `page.tsx`/`__init__.py`). É o próximo passo natural.
- Confirmar a experiência do `python run.py` no Windows com tkinter nativo
  (aqui no ambiente de desenvolvimento Linux o tkinter não está disponível, então
  a GUI não foi aberta de fato — só a core foi exercída).
- A partir do feedback do teste real, priorizar itens da Fase 2 (ver `ROADMAP.md`
  e `IDEAS.md`): persistir configurações, `.gitignore` aninhado, CLI sem GUI.

## Riscos / pontos de atenção

- Nenhum bug aberto.
- O modo degradado sem pathspec ignora o `.gitignore` silenciosamente, exceto por
  um aviso na saída — fácil de não perceber. Instalar pathspec é o recomendado.
- A estimativa de tokens é grosseira (`bytes/4`); serve só para sentir proximidade
  do teto de contexto, não como contagem real.
