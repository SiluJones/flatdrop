# IDEAS — FlatDrop

Banco de ideias. Não é compromisso nem prazo — é onde pensamentos ficam até
virarem item de `ROADMAP.md`, serem implementados ou descartados. Ideia adotada
vira item do roadmap; implementada vai para "Concluídas"; recusada vai para
"Descartadas" com o motivo. Nunca se perde nada — muda de status.

> **Mudanças nesta revisão (2026-08-23) — curadoria adiada desde 02/08, item a item:**
>
> 1. **«Saída da CLI ASCII-safe» saiu de Adiadas e voltou para Ativas** — o gatilho de retorno já
>    estava marcado como DISPARADO no próprio item desde 02/08 (terceira ocorrência, smoke da
>    wo0048); faltava só a curadoria do chat, prevista no handoff §3.3. Texto preservado inteiro.
> 2. **A Ativa «o editor e a curadoria manual não convivem» saiu** — descrevia como «bug aberto da
>    0.13.0» o que fechou na 0.15.0 (FIX-012). Nada se perdeu: o que ela tinha de único (o rótulo
>    `travada (manual)` e a origem do diagnóstico) foi somado à entrada correspondente em
>    **Concluídas**, que já existia.
> 3. **Duas frases obsoletas corrigidas dentro da Ativa do gerador `pasta/*`:** o contorno «não
>    salvar o `.flatdropignore` pela GUI» está **revogado** desde a 0.15.0 (DEC-029), e a trava por
>    pasta já grava a forma nova. O que segue aberto é só a pasta **parcialmente** curada.
> 4. **Dois resíduos truncados removidos** — a nota de Foco de 01/08 arrastava meia frase de uma
>    nota anterior («> foi ignorado\*\* e \*\*editor gravar `pasta/*`\*\*…»), e havia outro fragmento solto
>    antes do item da REGRA de ignore («> Concluídas). As frentes candidatas agora são…»). Ambos
>    eram sobra de reescrita, não conteúdo.
> 5. **Foco reescrito para a frente atual** (carta 01 do KCM sobre o formato do `_MANIFEST`).
> 6. **Duas ideias novas em Ativas:** o formato do `_MANIFEST` (nome plano que não existe no mount +
>    `mtime` por arquivo) e a linha de sincronia do git (`behind`/«sem upstream»).
> 7. **Uma corroboração** somada ao item «REGRA de ignore que casou»: a nota `260807-1324`, de
>    projeto irmão, com o custo real medido lá.
> 8. **Um item novo em «Feedback para o Kit»:** ausência de saída não é ausência de recurso.
>
> _Canal deste doc neste ciclo = **CHAT** (a wo0050 não toca o `IDEAS.md`)._

> **Mudanças nesta revisão (2026-08-01) — merge do template-update do KCM v1.95.0 (DEC-028):**
> criada a seção **Adiadas**, com gatilho de retorno obrigatório em cada item (formato adotado do
> kit). Para lá foram, sem perder texto: multi-raiz na GUI, `pasta/` como exclusão dura, UI-2/UI-3,
> saída da CLI ASCII-safe, formato «caminho escrito» e o arquivamento do `DECISIONS.md`. Quatro
> ideias que já estavam entregues e continuavam em «Ativas» foram para **Concluídas** com a versão
> em que saíram: `_TREE` nomear o conteúdo ignorado (0.12.0/0.14.0), force-include por caminho
> exato (0.7.0), botão «Gerar atalho da UI» (0.9.0) e ignores de pasta editáveis (0.4.0 + 0.13.0).
> Três ideias novas em Ativas (estado do repo no `_MANIFEST`, contrabarra em padrão, o limite da
> amostra do `_TREE`) e seis itens novos em «Feedback para o Kit». A nota de **Foco** foi reescrita
> para a frente atual. Nada foi apagado — só mudou de status.
>
> _A nota de foco de 2026-07-15 saiu: as frentes que ela citava estão em «Concluídas»._

> **Mudanças nesta revisão (2026-07-15):** specs 0017–0024 aplicadas. KCM, editor visual
> (Fase 2-D) e item C (persistência) movidos para **Concluídas**. Nova ideia ativa:
> **force-include por caminho exato** (correção do `.min.js`). Descartada: **remover a
> `DEFAULT_SUFFIX_IGNORES`** (motivo nas Descartadas). Próximas frentes: multi-raiz na GUI
> / force-include.

> **Mudanças nesta revisão (2026-07-05, transferência de conversa):** ciclo de
> release fechado — specs 0011–0016 todas aplicadas, `pytest` puro corrigido
> (FIX-005), versão 0.3.1, 41 testes. Sem ideia nova; as ideias foram **repriorizadas**
> para a próxima conversa: (1) trecho de KCM (ler `_TREE.md` → gerar
> `.flatdropignore`) e (2) editor de `.flatdropignore` na GUI (= Fase 2-D) sobem ao
> topo das Ativas; o item C (persistência) vem depois delas. A lista abaixo reflete
> essa ordem.

## Ativas


> **Foco (2026-08-26):** o merge do KCM **v1.120.0** consumiu a semana e está na última fatia — o
> `CEREBRO.md` fechou na wo0059; sobram os **12 modelos** do pacote (fase 3), que é a parte mais
> mecânica. Do ciclo anterior, a carta 01 do KCM está inteiramente respondida: item 1 entregue
> (DEC-030), item 3 entregue (wo0050) e item 2 **recusado com contraproposta entregue** (DEC-031).
> Seguem esperando **decisão do autor, sem prazo**: o gerador (`pasta/*` + `!mantido`) e a
> multi-raiz na GUI. E segue **sem resposta** a nossa carta 04 — ver o item com gatilho abaixo.

- **Carta 04 ao KCM, enviada em 26/08 e ainda sem resposta.** Ela devolve que a regra «o relatório
  lidera, sempre» só vale numa direção: quando o dono commita entre relatórios — o que aqui é
  rotina —, o manifesto fica com o commit mais novo, e a regra manda concluir que a cópia está
  atrasada justamente quando ela é a única em dia. A proposta é trocar a suposição por medição:
  **compare os dois carimbos, o mais recente vence**. **Gatilho:** se não vier resposta até
  **2026-09-09** (duas semanas), adotamos a regra por conta neste projeto, escrevemos a linha no
  `CEREBRO.md` e registramos a divergência como desvio — sem esperar mais. *(Registrado por causa
  da seção «Correspondência entre projetos», que entrou na wo0059: o que fica pendente do outro
  lado é nosso, não dele; carta esperando sem gatilho é como o projeto trava sem ninguém perceber.)*
- **Editor de `.flatdropignore` deve gravar `pasta/*`, não `pasta/`.** Causa raiz medida em
  DEC-025: `_scan` poda o diretório casado antes de descer, então um `!` dentro dele nunca é
  avaliado. Hoje o editor grava a forma `pasta/` e, ao salvar com um filho marcado, cai no
  fallback de listar arquivo por arquivo — frágil, porque arquivo novo na pasta passa a entrar
  sozinho. Proposta: o gerador emite `pasta/*` sempre que houver (ou puder haver) reinclusão,
  e o fallback por arquivo é aposentado. (Nasceu da nota de 2026-07-23 + medição de 28/07.)
  **Atualizado em 2026-08-23:** o contorno «não salvar o `.flatdropignore` pela GUI» está
  **revogado** — a 0.15.0 (FIX-012 + DEC-029) fez os dois conviverem, e a **trava** por pasta já
  grava a forma nova (`pasta/*` + `!` do que ficou). O que continua aberto é só a pasta
  **parcialmente curada e aberta**, que sai listada por folha. A decisão que trava está na análise
  `meta/analises/260728-ANALISE-gerador-flatdropignore.md`: *arquivo novo em pasta curada entra ou
  fica fora?*

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
  **Corroborado em 2026-08-07** pela nota `260807-1324`, com custo medido em projeto irmão: um
  `.xlsx` inteiro sumiu do achatamento por estar em pasta gitignorada, e a ausência só foi notada
  **sessões depois**. Reforça a prioridade sem mudar o escopo — a contagem já existia lá também;
  o que teria evitado o custo é a regra (ou o nome) na saída.
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

- **A amostra do `_TREE` não responde «o arquivo X existe?».** A faixa da 0.14.0 mostra as duas
  pontas e conta o meio — ótimo para ver até onde a coleção vai, inútil para confirmar a presença
  de um arquivo nomeado. Custou caro nesta sessão: `meta/workorders/_TEMPLATE.md` cairia
  exatamente nos 33 nomes ocultos do meio, e nem o `_MANIFEST` (que só lista o que subiu) nem o
  `_TREE` sabiam dizer se ele existe. Duas saídas possíveis, nenhuma decidida: (a) o `_TREE`
  sempre nomear os arquivos **resgatados por `!`** e os que casam um padrão `_*`/`_TEMPLATE`,
  porque são justamente os que existem para serem vistos; (b) aceitar o limite e tratar o editor
  da GUI como a resposta (foi a decisão da wo0043). (Assistente, 2026-08-01.)

## Adiadas

> Decisão consciente de não fazer agora. Cada item traz **o gatilho que o traz de volta** —
> ideia adiada sem gatilho é ideia perdida. Formato adotado do KCM v1.95.0 (DEC-028).

- **Acento na saída da CLI quebra em cp437.** A wo0052 resolveu os glifos decorativos e com isso
  cp1252 e cp850 — os dois consoles que este projeto usa. Sobra o cp437 (CMD em locale US), onde
  `ã`, `õ` e `Í` também não codificam: `PRÉ-VISUALIZAÇÃO`, `CONCLUÍDO` e `não` derrubariam o
  `print` do mesmo jeito. Não foi feito porque a correção certa aqui **não** é apagar os acentos
  (a saída ficaria feia em português para resolver um console que ninguém aqui usa) e sim uma rede
  de segurança no `print` — que é mudança de mecanismo, não de texto, e precisa de decisão própria
  por tocar `cli.py` (DEC-020). **Volta quando** alguém rodar o FlatDrop num Windows fora do
  locale pt-BR, ou quando a ferramenta for usada por outra pessoa. (Medido em 2026-08-24.)

- **Selecionar várias pastas de uma vez na GUI (multi-raiz).** Irmã do multi-fonte
  que já existe na core (`make_plan_sources`/`Source`): escolher N pastas na
  interface, prefixar cada arquivo com o nome da sua pasta-raiz e só cair na
  desambiguação atual se ainda colidir; a pasta de saída no Downloads vira uma
  genérica com numerador quando já existir uma de mesmo nome. A core já suporta
  multi-fonte; falta a UI de N raízes. (Ideia do usuário, nota `.txt` de 2026-07-03.)
  **Adiada** pelo autor em 2026-07-28: a decisão A/B (recomendação **B** — `.bat` desabilitado no
  modo multi-raiz) nunca foi tomada, e sem ela não há o que desenhar. **Volta quando** o autor
  responder A ou B, ou quando aparecer o segundo projeto que precise de N raízes no mesmo mount.

- **`pasta/` deveria voltar a ser exclusão DURA?** O FIX-011 tornou `pasta/` e `pasta/*`
  equivalentes no FlatDrop: os dois aceitam `!` por dentro. O autor prefere o contrário — `pasta/`
  significando "nunca entra, nem aparece na árvore" e só `pasta/*` aceitando resgate, que é o
  comportamento do git puro e dá duas ferramentas com dois usos. Em troca, reintroduz o caso que
  gerou a reclamação de 23/07, então só fecha se a GUI escrever `pasta/*` sozinha e o `_TREE`
  disser em qual forma cada pasta está. **Decisão separada da do gerador**; ver
  `meta/analises/260728-ANALISE-gerador-flatdropignore.md`. (2026-07-28.)
  **Adiada:** depende de duas mudanças que ainda não existem (a GUI escrever `pasta/*` sozinha e o
  `_TREE` dizer em qual forma cada pasta está). **Volta quando** o gerador do editor for corrigido —
  é o mesmo código, mas **decisão separada**: não misturar as duas na mesma WO.

- **UI-2 (polimento de layout) e UI-3 (presets/lembrar seleção).** UI-2: ordem das
  seções, 2 colunas nas opções, tema. UI-3: presets "só docs"/"só código", lembrar
  a última seleção do modal.
  **Adiada:** polimento, sem dor relatada. **Volta quando** o autor reclamar do layout duas vezes,
  ou quando um preset («só docs», «só código») for pedido em uso real.

> _**Saída da CLI ASCII-safe** saiu desta seção em 2026-08-23: o gatilho («terceira ocorrência num
> smoke») disparou em 02/08 e a curadoria do chat a moveu para **Ativas**, com o texto inteiro._

- **Formato de nome "caminho escrito" (`raiz__pastas__stem.ext`).** Um seletor de
  formato do nome, alternativo ao `root_in_name` atual. Em vez de stem na frente,
  escreveria o caminho na ordem natural de leitura com o **stem no fim**:
  `app/routes/page.tsx` (raiz `meuapp`) → `meuapp__app__routes__page.tsx`. O usuário
  reconhece que **não** ajuda o Claude a achar por nome (o stem deixa de liderar a
  ordenação alfabética), mas agrupa todos os arquivos de um projeto por raiz — útil
  para empilhar vários projetos numa mesma pasta/pilha mental. Implementação seria
  barata (a mecânica de nomeação já existe), mas fica em **espera**: só entra se o
  usuário quiser o seletor de formatos. Coexistiria com o `root_in_name`
  (stem-primeiro) como dois estilos opt-in. (Ideia do usuário, 2026-07-04.)
  **Adiada:** só entra se o autor quiser um **seletor de formatos** — sozinha ela não resolve nada que
  o `root_in_name` não resolva. **Volta quando** houver dois projetos empilhados na mesma pasta.

- **Arquivar o `meta/DECISIONS.md` em `DECISIONS-archive.md`.** O arquivo passou de 700 linhas (864
  hoje, 38 entradas). O CEREBRO manda arquivar as mais antigas nesse ponto. **Adiada de propósito**
  durante a migração de vocabulário (DEC-023), para não mexer nas mesmas referências duas vezes.
  **Volta quando** a wo0044 estiver commitada — a migração acabou, o bloqueio saiu. (2026-07-28.)

## Concluídas

- **Saída da CLI ASCII-safe.** **ENTREGUE (wo0052).** Os quatro glifos da saída (`↳`, `•`, `…`,
  `⚠`) viraram `->`, `*`, `...` e `!`. Nasceu como item de conforto («dispensar `chcp 65001` nos
  `.bat`») e terminou como correção de bug: era `UnicodeEncodeError` derrubando o `print` final
  depois de a ferramenta já ter dado certo. Quatro ocorrências até virar WO — a última já não era
  smoke, era uso. Medição de 24/08: `↳` e `⚠` falham nos três code pages do Windows; `•` e `…`
  falham em cp850, que é o CMD pt-BR, ou seja, o caminho do `.bat`. **Resíduo conhecido:** em
  cp437 (CMD em locale US) os **acentos** ainda quebram — outra conversa, ver «Adiadas».
- **A linha de git do manifesto não distingue «commitado» de «empurrado».** **ENTREGUE (wo0050).**
  O `ahead` já existia desde a wo0048; entraram o `behind`, o «sem upstream», o «sincronizado com
  <upstream>» e o nome real do upstream. Sete testes puros, que rodam sem `git` instalado. O
  registro que sobra é o da lição, e está em «Feedback para o Kit»: ausência de saída não é
  ausência de recurso.
- **O editor deve conviver com regra escrita à mão.** **ENTREGUE na 0.15.0** (FIX-012, wo0045 +
  wo0046): o bloco virou um diff contra a curadoria manual e vai sempre para o fim. Junto veio a
  **anatomia normativa** (DEC-029), que é o que de fato revoga o «ou um, ou outro».
  *(Absorve, em 2026-08-23, a Ativa gêmea de 28/07 que ainda descrevia isto como «bug aberto da
  0.13.0». O que ela tinha de próprio: o desenho nasceu do diagnóstico — bloco como **diff** e
  bloco **por último** —, e dele saiu também a exigência de a GUI **mostrar de onde vem cada
  trava herdada**, que virou o rótulo `travada (manual)` na wo0047. As três partes estão
  entregues.)*
- **O formato do `_MANIFEST` promete um nome que não existe no mount.** **ENTREGUE (DEC-030,
  wo0051 + wo0055).** A tabela não mudou — continua descrevendo o disco —, e a divergência saiu num
  bloco de exceções rotulado como **previsão**, com o próprio teste de falsificação dentro («se o
  arquivo aparecer no Projeto com o nome da coluna 1, a regra mudou»). Depois a carta 03 do KCM
  mediu que o bloco *chegava por busca, não por leitura*, e a wo0055 subiu a **contagem** para o
  cabeçalho, sempre presente, inclusive com `0`. Medido: 3 de 39 aqui, 11 de 109 nos repos do KCM.
- **Contrabarra em padrão deveria ser detectada.** **ENTREGUE na 0.15.0** (wo0047): o editor avisa
  na abertura e aponta arquivo e linha. Confirmado por medição que o gerador nunca emitiu `\` — as
  linhas vinham sempre de edição manual, e por isso a ferramenta **avisa em vez de normalizar**.
- **FlatDrop grava o estado do repo no `_MANIFEST`.** **ENTREGUE na 0.15.0** (wo0048), com os três
  refinos do autor: `%h %ad %s --date=short`, status **resumido** (nunca listagem, para não virar
  ruído nem vazar nome de arquivo não rastreado) e o rótulo «foto da geração».

- **`_TREE` deve nomear o conteúdo útil das pastas ignoradas.** Hoje a árvore colapsa a pasta
  numa linha (`meta/legacy/  [ignorada: flatdropignore]`) e não diz o que havia dentro — então
  o chat futuro não tem como saber qual arquivo pediria para liberar. Proposta: listar os
  filhos de pasta ignorada **por ignore do autor** (`.gitignore`/`.flatdropignore`), marcados
  como pulados, e seguir colapsando o lixo estrutural (`node_modules`, `.git`, `__pycache__` —
  a poda embutida de `cfg.dir_ignores`, que ninguém quer ver). Talvez com teto de N nomes por
  pasta para não inchar o `_TREE`. Insumo já existe: `_scan` produz `skipped_items` completo.
  (Ideia do usuário, nota de 2026-07-24.)
  **ENTREGUE na 0.12.0 (wo0038)** — arquivo pulado por ignore do autor sai nomeado e pasta ignorada
  ganha espiada rasa nos filhos; ruído estrutural segue colapsado. Refinado na 0.14.0 (wo0043), que
  trocou o teto simples pela amostra com as duas pontas.

- **Force-include por caminho exato (resgatar um arquivo específico barrado por ignore
  embutido).** Uma lista de "sempre inclua exatamente este caminho", checada ANTES dos
  cortes embutidos (suffix-ignore, tipo, gitignore), ainda barrada por "sensível". Motiva:
  `htmx.min.js` (e afins) some porque `.min.js` está em `DEFAULT_SUFFIX_IGNORES`, e o `!`
  do `.flatdropignore` age numa camada abaixo (só o matcher), então não resgata. Marcador
  próprio no `.flatdropignore` (distinto do `!`, para não borrar a semântica gitignore do
  DEC-017). DEC-020-safe: vive no `_scan`, simétrica GUI×`.bat`, não toca o gerador de
  `.bat`. Mexe no `_scan` → pede spec de design. **Não urgente** (o autor adiou). (Ideia do
  usuário + assistente, nota 0827.)
  **ENTREGUE na 0.7.0 (spec0027, DEC-021)** — marcador `++caminho` no `.flatdropignore`; vence tudo
  menos «sensível»; `.bat` intocado. 4 testes em `test_force_include.py`.

- **Botão "Gerar atalho da UI" na GUI.** UI-1 e o launcher `flatdrop-ui.bat` já
  existem; falta um botão que gere o launcher calculando o caminho do `run.py`
  sozinho (sem hardcode) — talvez um `.lnk` em vez de `.bat`.
  **ENTREGUE na 0.9.0 (spec0031)** — menu **Ferramentas → «Gerar atalho da UI…»**, gerador NOVO e
  separado (o RUN `.bat` ficou intocado, DEC-020).

- **Ignores de pasta editáveis na GUI** com núcleo imutável
  (`.git`/`node_modules`/`__pycache__`/VCS sempre reaplicados), para tirar/pôr
  pastas como `dist`/`build`/`.venv` caso a caso. (Fase 2 — item D.) **Consolidado
  na "[PRÓXIMA 2] Editor visual de `.flatdropignore`" no topo** — o editor cobre isto
  de forma declarativa e visual. O `.flatdropignore` já cobre boa parte hoje.
  **ENTREGUE** pelo editor visual (0.4.0–0.5.1) e completado pela **trava por pasta** (0.13.0,
  DEC-027), que é a forma declarativa de dizer «arquivo novo aqui não entra».


- **O teto de nomes do `_TREE` esconde justamente as pastas grandes.** **RESOLVIDO na 0.14.0
  (wo0043) — amostra com as duas pontas.** Depois do wo0038 a árvore nomeava até
  `TREE_NAME_CAP` (10) e agregava o resto: `meta/workorders/` saía com 10 nomes e
  `(+29 mais)` — e eram os 29 que a pessoa precisaria ver para escolher o que liberar. A
  0.14.0 troca o teto simples por uma amostra com as primeiras e as últimas posições e o
  meio contado (`... (+29 no meio, 39 no total) ...`). (Autor, 2026-07-28.)
- **[KCM — entregue] Claude lê o `_TREE.md` e dita o `.flatdropignore`.** Bloco de KCM
  portável (material externo, não é código do repo) + exemplo no README; habilitado pela
  spec0011. Fecha o ciclo `_TREE → flatdropignore → mount melhor`, sobretudo liberando via
  `!` o que o `.gitignore` esconde. (Ideia do usuário, notas 0704–0714.)
- **Editor visual de `.flatdropignore` na GUI (Fase 2-D, specs 0017–0021).** Modal com
  árvore lazy, checkbox binário ("quero no Projeto"), badges de tipo/sensível, bloco
  gerenciado no arquivo, e glifo indeterminado correto já na visão colapsada
  (`core.folder_effective_state`, FIX-007). Consolidou o antigo item D. (Ideia do usuário.)
- **Persistir config + pastas recentes na GUI (item C, specs 0022–0024, 0.6.0).**
  `settings.json` por plataforma (`%APPDATA%`/`~/.config`/App Support), Combobox de
  recentes, grava ao Executar; escopo **só-GUI (DEC-020)** para não tocar o `.bat`;
  allowlist salva como delta. `load` nunca lança, `save` atômico. (Fase 2 — item C.)
- **Fullpath com nome da pasta-raiz (spec0013 + ajuste de ordem na spec0014).** Flag
  `root_in_name`: no modo fullpath e em fonte única, inclui o nome do projeto no
  nome de cada arquivo (inclusive os da raiz: `README.md` → `README__meuapp.md`).
  Injeção só no NOME planejado (via `root_prefix` em `_plan_names`); o `rel` do
  manifesto/tree fica real. Ignorada com aviso fora do fullpath e em multi-fonte.
  Limite do Windows protegido pelo truncamento com hash. CLI `--root-in-name`;
  checkbox na GUI serializada no `.bat`. A **spec0013** deixou a raiz no meio do
  sufixo (efeito da implementação); a **spec0014** corrigiu para stem + caminho
  invertido + raiz no fim (`page__routes__app__meuapp.tsx`). (Ideia do usuário, nota
  `.txt` de 2026-07-03.)
- **`_TREE.md` opcional na saída (spec0011).** Árvore indentada da origem ao lado do
  `_MANIFEST.md`: copiados (renomeados marcados), pulados com o motivo, e pastas
  ignoradas colapsadas em UMA linha, sem recursão (`node_modules/ [ignorada:
  embutido]`). Desligado por padrão (checkbox GUI + `--tree` CLI, serializado no
  `.bat`). Detalhe dos pulados soltos via `--tree-detail summary|full`. O `_scan`
  passou a devolver a lista completa de pulados (`skipped_items`, sem o teto de 8).
  Verificado no mount (saiu correto). +8 testes (27->35). É o par visual do
  `.flatdropignore` e habilita o fluxo de KCM acima. (Fase 2 — item B.)
- **Redesign da UI por seleção (UI-1).** Modal "Escolher tipos…" (checklist
  categorizado + busca + marcar/limpar por grupo + adicionar custom); tela
  principal compacta. Subsumiu a caixa de extensões e os campos "Só estes/Exceto".
  (spec-0007.)
- **`.flatdropignore` + `.gitignore` aninhado.** Ignore próprio por projeto,
  aninhado, com negação `!` que libera o que o `.gitignore` bloqueia (até pasta
  podada). Lê os `.gitignore` de subpastas. (DEC-014, spec-0008.)
- **GUI: selecionar tipo na hora** (só-ext/exceto-ext) — feito pelo modal (UI-1).
- **GUI: liberar do `.gitignore`** — resolvido de forma declarativa pela negação
  `!` do `.flatdropignore` (spec-0008), em vez de um campo avulso na GUI.
- **Gerador de `.bat` pela interface.** Botão "Gerar .bat…" serializa a config da
  tela num `.bat` ASCII; reproduz a seleção do modal via `--add-ext`/`--exclude-ext`.
  (spec-0003, refinado na 0007. FIX-003 garantiu o ASCII.)
- **Multi-fonte também na GUI.** Toggle "incluir todos os `.md` a partir de [raiz]"
  ao vivo (Pré-visualizar/Executar), não só no `.bat`. (spec-0005; FIX-004.)
- **Launcher da UI.** `bat/flatdrop-ui.bat` abre a interface sem console (`pythonw`),
  copiável.
- **Expandir a allowlist de tipos** (Godot, PDF/DOCX/XLSX/ODT/RTF/EPUB, +linguagens).
  (DEC-013, spec-0001.)
- **Abrir a GUI maximizada.** (spec-0005.)
- **Selecionar por tipo na execução** (`--only-ext`/`--exclude-ext`/`--add-ext`) — 0.2.0.
- **Selecionar por pasta** (`--only-folder` + `--folder-match`) — 0.2.0.
- **Combinar "todos os `.md` do repo" + "conteúdo de uma área" num só manifesto**
  (multi-fonte `make_plan_sources`/`Source` + `--also-md-from`) — 0.2.0.
- **`.bat` para ativar em pastas de trabalho** (os 5 do cinzeiro) — 0.2.0.
- **CLI sem GUI** (`flatdrop/cli.py`) — 0.2.0 (antecipada da Fase 3).

## Descartadas

- **Remover a `DEFAULT_SUFFIX_IGNORES` (ou tirar `.min.js` dela), confiando em
  git/`.flatdropignore`.** Descartada (análise de 2026-07-15). A lista é **redundante** com
  o allowlist de tipos para `.map/.lock/.pyc/.pyo/.class/.o/.so/.dll/.exe` — essas
  extensões não são aceitas, então o filtro de tipo já as barra. Mas é **essencial** para
  `.min.js`/`.min.css`, cujas extensões (`js`/`css`) SÃO aceitas: sem a lista, todo
  minificado/bundle vazaria ao mount. Confiar no git não cobre committados (lockfiles, libs
  vendorizadas e source maps costumam ser versionados) e exigiria `.flatdropignore` por
  projeto para ruído binário — contra o zero-config. E tirar só `.min.js` liberaria TODOS
  os `.min.js`, contra o objetivo de liberar só um. O lever certo para exceções pontuais é
  o **force-include por caminho exato** (ver Ativas), não remover o default.
- **Flag CLI `--ext-set a,b,c` (allowlist exata).** Não foi preciso: o gerador de
  `.bat` reproduz qualquer seleção do modal com `--add-ext` (adições) +
  `--exclude-ext` (remoções), já que o `cli.py` reseta `exclude_ext` na fonte de `.md`.
- **Ser só single-file (sem o modo pasta).** O fluxo é de arquivos individuais no
  Projeto, com atualização granular. Single-file é complemento. (Ver DEC-001.)
- **Mover os arquivos em vez de copiar.** Destruiria a origem. (Ver DEC-002.)
- **Usar symlinks em vez de copiar.** Não se resolvem no fluxo de arrastar; Windows
  os trata de forma inconsistente. (Ver DEC-002.)
- **Upload automático para o Claude.** Não há API pública para os arquivos de
  Projeto; arrastar continua manual (e é só uma etapa).
- **Mover imagens/áudio/vídeo para a saída.** O Projeto do Claude não os usa como
  texto; ignorá-los é o certo. Reabrir via toggle explícito se algum dia precisar.
  (Confirmado com o usuário em 2026-06-14.)

## Feedback para o Kit

Registro do que ESTE projeto observou/mudou além do kit (material que volta para evoluí-lo).

- **Havendo WO no turno, o Code commita TUDO — inclusive o que o chat entregou junto.** Levantado
  pelo autor em 2026-08-24. Até a wo0050, o chat entregava a WO **e** um bloco `git add/commit`
  para os documentos que ele mesmo tinha escrito, obrigando o autor a um passo manual e criando
  risco de registro pendente (o defeito que a wo0044 existiu para consertar). A regra correta:
  **com WO, o bloco de commit é do Code e cobre a WO + os arquivos do chat + qualquer pendência;
  sem WO, o bloco é do chat.** A salvaguarda é conferir a presença no disco e, se faltar, commitar
  o resto e reportar — nunca inventar. Já em uso desde a wo0051; falta virar linha no
  `_TEMPLATE__workorders.md` e na skill `apply-wo`. *Guardado para o merge do próximo
  template-update do KCM, para não escrever convenção que o kit novo talvez já traga.*
- **O relatório de aplicação precisa ser gravado DEPOIS do push — ou corrigido depois dele.**
  Medido em 2026-08-24: o relatório da wo0051 diz «NÃO executei o push» porque o Code, com razão,
  pediu confirmação antes de mudar o remoto; o push saiu logo em seguida, e o `.txt` em disco ficou
  afirmando um estado falso, que é o que a sessão seguinte lê. **O que salvou:** o `_MANIFEST`
  gerado depois trazia «sincronizado com origin/main» — a linha da wo0050 desmentindo o relatório
  sozinha, um dia depois de existir. A correção: o campo `## Push` do relatório só é escrito com o
  resultado real, e se o push ficar pendente de confirmação o relatório é **reaberto e corrigido**
  quando ele sair. *Guardado para o mesmo merge.*
- **Âncora de uma linha só é segura quando o texto novo fala só daquela linha.** Medido em
  2026-08-26, na wo0058: a edição de registro tinha âncora de uma linha, mas o texto substituto
  reescrevia o parágrafo inteiro — cinco linhas. Aplicada ao pé da letra, ela deixaria quatro
  linhas órfãs, dizendo em versão velha o que a nova já dizia. Quem aplicou percebeu, removeu as
  quatro e reportou; a decisão foi dele, não da WO, e é decisão que uma WO não deveria delegar.
  **A regra é de escopo, não de tamanho:** a âncora precisa cobrir tudo o que o substituto torna
  redundante. A pergunta antes de fechar qualquer edição: *o que estou escrevendo faz alguma linha
  vizinha virar repetição?* O modelo de WO poderia dizer isso ao lado do conselho de preferir
  âncora de uma linha — os dois são verdadeiros e um limita o outro.
- **O pacote v1.120.0 traz cinco bullets do «Refino das Instruções» dentro da seção «Bloco de fecho
  de turno» — e some com eles da seção a que pertencem.** Medido em 2026-08-26, comparando as duas
  versões do CEREBRO: os bullets «Sincronia com o CEREBRO», «Uma regra por linha», «Teto», «Teto por
  configuração» e «Registre» estão nas linhas 304-308 do template, dentro do fecho, e **não** estão
  na seção «Refino das Instruções do Projeto» (linhas 206-219), que é o lugar deles — e onde eles
  vivem no nosso arquivo desde a v1.95.0. Não é conteúdo novo nem reorganização: é bloco deslocado.
  Quem aplicasse o template ao pé da letra duplicaria os cinco no fecho e os perderia no Refino. A
  fase 2b os retirou do texto adotado, de propósito, e isto volta ao kit como defeito de pacote.
- **Desvio registrado: o `IDEAS.md` deste projeto NÃO separa «Ativas — Usuário» de «Ativas —
  Assistente».** O modelo v1.120.0 propõe as duas seções, com o argumento de que ajuda a lembrar de
  onde veio cada coisa. Aqui a origem viaja **dentro do item** («Ideia do usuário, nota
  `260717-1338`», «nasceu do diagnóstico»), e isso funciona melhor para o caso comum deste projeto,
  que é ideia de autoria mista — o usuário levanta o atrito, o assistente propõe a forma. Com duas
  seções, esse item teria de escolher um lado ou ser duplicado, e mudaria de seção conforme quem
  falou por último. **Mantido como está, de propósito, e registrado aqui para que o próximo merge
  não proponha isto como lacuna.**
- **Agrupar o `GLOSSARY.md` em seções.** O arquivo tem 15,8 KB e **nenhum `##`**: achar um termo é
  varrer o texto inteiro. O modelo v1.120.0 sugere quatro baldes (conceitos · arquiteturas e
  módulos · comandos e artefatos · identificadores) e eles cabem bem no nosso vocabulário. Não
  entrou no merge porque **reorganizar 40 e poucos termos é edição do nosso conteúdo, não adoção de
  modelo** — e edição desse tamanho merece uma passada própria, não um item no fim de uma WO de
  fechamento. **Volta quando** alguém não achar um termo que sabe que está lá, ou na próxima vez que
  o arquivo crescer.
- **Número de checklist é DERIVADO do texto da WO, nunca estimado antes dela.** Terceira
  ocorrência da mesma falha em três WOs seguidas, o que já a qualifica como padrão e não como
  descuido: a wo0055 mandou trocar `118` em três lugares quando dois eram estado e um era registro
  datado; a wo0056 previu «16 bullets» onde o texto que ela mesma mandava colar produz **18**, e
  mandou conferir `grep "wo0044" → 0` num arquivo onde o próprio texto novo cita `wo0044` de
  propósito. **Nas três, o executor mediu, discordou e reportou sem consertar por conta — e nas
  três ele estava certo.** A causa é sempre a mesma: o número foi escrito na fase de *raciocínio*
  sobre o merge e não foi recalculado depois que o texto final da edição ficou pronto. **A regra:**
  onde as âncoras já são extraídas do arquivo vivo por script, as contagens do checklist saem do
  mesmo script, sobre o texto final — e aí param de poder divergir do que a WO manda escrever.
  Enquanto não for automático, vale a pergunta antes de escrever qualquer número de conferência:
  *«isto eu medi agora, ou lembrei?»*. O kit poderia dizer isso no campo do checklist do modelo de
  WO, ao lado dos três campos por passo de verificação.
- **Edição em `.claude/` não vai por WO — vai pelo chat, como arquivo inteiro.** Medido em
  2026-08-26, na wo0054: o classificador de permissão do Claude Code **bloqueou** as duas edições
  que tocavam `.claude/settings.json` e `.claude/skills/wrap/SKILL.md`, e o executor fez certo em
  não contornar (a barreira existe para impedir que o Code se autoconceda permissão, e «eu
  autorizo» dito no chat não muda isso). O erro foi do **chat**, ao montar a WO: deveria ter
  previsto que edição na configuração do próprio executor não é aplicável por ele. **Regra:**
  arquivo sob `.claude/` o chat entrega INTEIRO, para download e substituição; a WO só o menciona
  no `git add`. O kit poderia marcar essas edições como «risco de bloqueio do classificador».
- **A distinção «MANDA × RELATA» vale para o próprio texto da WO, não só para a varredura.** Medido
  em 2026-08-26, na wo0055: a WO mandou trocar as **três** ocorrências de `118` no `STATUS.md`, e
  o executor trocou **duas** — deixando de pé a que estava dentro de um bloco datado («números
  lidos nesta revisão», 24/08), porque ali `118` era o número **medido naquele dia**. Ele estava
  certo e a WO estava errada: trocar teria falsificado o registro. Quem escreve a instrução de
  varredura precisa classificar as ocorrências ANTES de mandar trocar todas — é a mesma regra que
  o kit aplica às linhas revogadas, virada para dentro.
- **Ausência de saída não é ausência de recurso — leia o código antes de devolver a outra frente
  que algo não foi feito.** Medido em 2026-08-23, num caso com três participantes errando junto: o
  `ahead` da linha de git do manifesto **existe** desde a wo0048, mas só imprime quando há commit
  não empurrado. A nota `260802-2319` afirmou, no mesmo dia da implementação, que «a parte do à
  frente não entrou»; o KCM repetiu a devolução na carta 01 citando um manifesto sem o trecho; e
  o STATUS deste repo listava como pendente («backlog 3») algo que o CHANGELOG da mesma versão
  declarava entregue. Nenhum dos três abriu a função. O kit já tem «verifica antes de AFIRMAR»
  para o estado do repo — falta a variante para **capacidade do próprio produto**: antes de
  registrar «a ferramenta não faz X», abra o código de X; ausência na saída é compatível com
  recurso presente e condição não satisfeita.

- **Adotado o modo Claude Code (duas raias).** Chat autora docs/specs; Code implementa e commita.
  Criados os arquivos de arranque (`CLAUDE.md` raiz, `.claude/`). Ver DEC-012.
- **`meta/CLAUDE.md` → `meta/CEREBRO.md`.** Confirmado como superconjunto exato do anterior
  (nada perdido) — não houve merge a fazer.
- **Método "doc por spec" exercitado** em muitos ciclos (specs 0001–0010): âncora semântica,
  um canal por doc por ciclo, "PARE e reporte" se a âncora falhar. Funcionou bem.
- **`.bat` no CMD exige ASCII (FIX-003).** Encoding de `.bat` é armadilha: corpo ASCII, acento só na
  saída via `chcp`. O gerador de `.bat` passou a garantir isso.
- **Verificar lógica sutil no sandbox antes de virar spec.** O `.flatdropignore` (negação +
  aninhamento) foi testado com o pathspec real ANTES de escrever a spec — pegou uma expectativa
  errada e deu confiança no algoritmo. Vale como prática para qualquer regra não-óbvia.
- **Atualização do KCM integrada (DEC-015).** Adotados: seção de config, novo nome de spec
  (`AAMMDD-specNNNN-desc.md`), `HISTORICO`→`HISTORY`. Omitidos com registro: HUB (projeto solo) e a
  regra `.gitignore`/README proativa (o repo já tem os dois). Preservado o conteúdo específico do
  flatdrop — nada de sobrescrever meta/ com template em branco.
- **Higiene em transferência.** Ao transferir conversa, regenerar os meta/ completos e detalhados
  (não resumir), reclassificar IDEAS (implementadas → Concluídas) e limpar o STATUS. Um "prompt de
  início" com ordem de leitura + estado exato faz a nova conversa continuar sem perda.
- **Descompasso de versão por corte cedo (2026-07-05).** Cortar a 0.3.0 antes de a spec seguinte
  (root_in_name) entrar deixou código à frente do CHANGELOG; resolvido com um patch de acerto (0.3.1).
  Lição: datar a versão só quando o lote de specs do ciclo estiver todo aplicado, ou assumir o patch.
- **Faltou no kit uma regra sobre artefato gerado que convive com edição humana.** Este projeto
  tropeçou duas vezes no mesmo padrão — um bloco gerado dentro de um arquivo que a pessoa também
  edita à mão (o `.flatdropignore`; antes, o apêndice do CEREBRO). É um padrão comum o bastante
  para virar princípio: **o artefato gerado precisa (i) saber o que existe fora dele, (ii) ter
  precedência definida por posição, e (iii) nunca duplicar o que já está lá.** Nenhuma dessas
  três aparece no kit hoje, e as três foram violadas de uma vez. (2026-07-28.)
- **Sugestão de fluxo: a análise devia ser oferecida ANTES da WO, não depois do erro.** As três
  correções desta sessão que exigiram redesenho (gerador, trava, este bug) tinham em comum uma
  pergunta de produto não formulada. O CEREBRO já traz «Análise antes do compromisso», mas o
  gatilho é subjetivo («mudança não-trivial»). Um gatilho mais afiado, que teria pegado os três:
  **mudar o formato de um artefato que outra pessoa (ou o futuro você) vai ler ou editar pede
  análise, mesmo quando o diff é pequeno.** (2026-07-28.)
- **O `_UPDATE-PROMPT` deveria pedir o estado do repo, não só o pacote.** Em todo update o
  assistente precisa saber o que está aplicado, e a única fonte confiável é o repo — que ele só
  vê pelo mount. Se o prompt do kit terminasse com uma linha do tipo «antes de comparar, liste o
  mount e diga em que versão/commit o projeto está», o erro de 28/07 (afirmar que uma WO estava
  pendente) teria sido impossível de cometer em silêncio. (2026-07-28.)
- **A regra "sua cópia não é a fonte da verdade" está longe do lugar onde ela é quebrada.** No
  template ela vive em «Regras de higiene»; o erro acontece ao preencher a linha **Estado** do
  bloco de fecho de turno, dezenas de linhas depois, e nada ali lembra de verificar. Aconteceu
  aqui em 28/07: o assistente afirmou que uma WO estava pendente **duas horas depois de trazer
  essa mesma regra do kit** — e havia dois `.txt` no mount dizendo o contrário, não lidos.
  Sugestão ao KCM: a regra pertence ao **campo**, não ao apêndice. Todo campo do bloco de fecho
  que afirme estado deveria trazer, na própria descrição, "vem de leitura feita neste turno".
  Regra sem gatilho no ponto de uso é decoração. (2026-07-28.)
- **Campo obrigatório em formulário induz confabulação.** O bloco de fecho pede **Estado** em
  todo turno. Quando não há leitura fresca, a saída de menor atrito é preencher com a memória —
  e a memória, logo depois de entregar um trabalho, é a *expectativa* de que ele foi aplicado.
  O formato deveria admitir "não verificado nesta rodada" como resposta de primeira classe, em
  vez de tratar o campo como sempre-preenchível. (2026-07-28.)
- **O kit ensina a regra `pasta/*` e não a segue.** O `flatdropignore__template-update` traz o
  comentário certo («use `pasta/*` (o conteudo), nao `pasta/` (a pasta): sob pasta excluida por
  inteiro o `!` NAO reinclui») e aplica a forma nova em `meta/workorders/*` — mas escreve
  `logs/` na forma antiga, duas linhas acima. E o `CEREBRO` manda reincluir com
  `!analises/_TEMPLATE.md` sem exigir que a pasta esteja como `analises/*`, o que não
  funcionaria. Sugestão: o kit deveria aplicar a própria regra em TODAS as pastas que emite, e
  a linha do modelo de análise deveria vir com o par completo (`meta/analises/*` +
  `!meta/analises/_TEMPLATE.md`). (2026-07-28.)
- **A regra do `!` depende da ferramenta que consome o arquivo, não só do padrão.** Medido
  aqui: com `PathSpec` (última regra que casa vence), a negação FUNCIONA mesmo em pasta
  excluída — quem a mata é a poda de diretório na varredura, que nunca chega a avaliar o `!`.
  Vale para qualquer ferramenta que faça `os.walk` com poda (é o padrão). O kit poderia dizer
  «`pasta/*` porque a maioria das ferramentas poda o diretório antes de olhar dentro», que é o
  motivo real e ensina a generalizar. Ver FIX-011/DEC-025. (2026-07-28.)
- **Template genérico não deve ser candidato a substituir arquivo vivo refinado — e o protocolo
  de update precisa dizer isso.** A cada template-update, o mesmo atrito: o kit apresenta
  `CLAUDE.md`, `.claude/settings.json`, skills (e, em outros projetos, as skills de nicho — o
  caso do *narrative*, com 4) como se coubesse escolher entre o genérico e o vivo. Não cabe: o
  genérico ensina estrutura e base; o projeto já especializou. Sugestão ao KCM: o
  `_UPDATE-PROMPT.md` e a seção de update do `CEREBRO.md` devem afirmar de saída que (i)
  template nunca substitui vivo, (ii) esses arquivos entram por padrão na seção «(c) o projeto
  tem e o template não cobre», e (iii) a **única** exceção é formato descontinuado, que sempre
  migra. Adotado localmente na seção «Ao receber um template-update do KCM» do CEREBRO
  (DEC-024). (2026-07-28.)
- **`.claude/commands/` está descontinuado — o kit deveria entregar Skills e dizer isso.** O
  formato atual é `.claude/skills/<nome>/SKILL.md` com front-matter e
  `disable-model-invocation`. O kit já entrega assim no v1.87.0, mas sem marcar que o antigo é
  legado; sem essa marca, um projeto montado antes fica no formato velho sem saber. (DEC-024.)
- **`meta/SPEC.md` chegou sem contexto e colidiu com um termo em uso.** O template não diz que
  é spec de **feature** (Spec-Driven Development / GitHub spec-kit) nem que é **sob demanda** —
  e neste projeto "spec" já significava o delta aplicável. Custou um mal-entendido que o autor
  teve de desfazer à mão. Sugestão: o manifesto deveria trazer a origem (SDD) e a nota "não é o
  modelo das WOs" na própria linha do arquivo. Resolvido aqui pela DEC-023. (2026-07-28.)
- **Apêndice dentro do CEREBRO foi um erro de kit — já corrigido no template atual.** A versão
  que montou este projeto punha os arquivos de arranque do Code como apêndice do `CEREBRO.md`,
  com a instrução de apagá-lo depois de usar. Documento que manda apagar parte de si vira
  dívida: nunca foi apagado e a cópia divergiu do original (`meta/DECISOES.md`, que não existe).
  O template v1.87.0 já resolve remetendo ao `claude-code-kit.zip`. Registrado como resolvido —
  a reclamação original era deste projeto. (DEC-024.)
- **Diferença de ambiente esconde bug de teste (FIX-005).** O Code rodava `python -m pytest` (resolvia
  o path); o usuário roda `pytest` puro (não resolvia). Fixar a forma de rodar na infra (`conftest.py`
  na rootdir), não na memória de quem invoca. Vale como recomendação para o Kit em projetos com pacote
  aninhado.
- **O template regride quatro trechos que este projeto já refinou** (v1.95.0, todos mantidos no
  vivo, DEC-028): (1) o **princípio 8** volta ao título antigo e apaga a citação «previsão ×
  observação» — regra que nasceu de erro real aqui; (2) o **princípio 11** troca o exemplo real
  (renomear «spec» para «WO» arrasta `/apply-spec` e `meta/specs/`) por um exemplo de outro nicho;
  (3) a **tabela dos documentos** apaga as linhas `logs/` (perdendo a DEC-026, um arquivo por DIA)
  e `workorders/`; (4) o **«Kit de arranque do Code»** volta ao `claude-code-kit.zip` e diz que
  `.claude/commands/*.md` «também funcionaria» — afrouxando a DEC-024, que o próprio kit mandou
  aplicar. Sugestão ao KCM: quando uma regra sobe de um projeto para o template, o texto que a
  originou deveria subir junto — regra generalizada sem o caso que a gerou perde os dentes.
  (2026-08-01.)
- **O template do `IDEAS.md` não tem a seção «Feedback para o Kit», que o CEREBRO manda usar.** O
  kit prescreve um endereço que ele próprio não cria; quem monta um projeto novo não tem onde
  escrever o primeiro feedback. (2026-08-01.)
- **O template do `STATUS.md` cria «📁 Arquivos Críticos», que duplica o CONTEXT.** Aqui esse papel
  é do `CONTEXT.md` (Armadilhas) e do `CLAUDE.md` (Mapa rápido). Duas fontes para o mesmo dado
  contraria a própria regra de higiene do kit. Não adotado. (2026-08-01.)
- **`_TEMPLATE.md` de pasta ignorada precisa do par completo — e o kit acertou onde este projeto
  errava.** O `flatdropignore__template-update` traz `meta/workorders/*` seguido de
  `!meta/workorders/_TEMPLATE.md`; o arquivo vivo daqui não tinha a reinclusão, e o efeito foi
  concreto: o modelo das WOs não chegou ao mount e não pôde ser comparado no update. Adotado.
  (2026-08-01.)
- **A regra do «pacote fica até o merge fechar» valeu na prática.** O protocolo novo diz que os
  `__template-update` seguem no mount enquanto o merge estiver em curso e que o assistente deve
  declarar a cobertura de leitura (verbatim × por estrutura). As duas coisas foram usadas nesta
  sessão e evitaram refazer o merge quando ele foi entregue em duas fases. (2026-08-01.)
- **O KCM aposentou o `meta/HUB.md` e devolveu o feedback deste projeto (v1.89.0).** Cinco itens
  daqui viraram regra no kit; um foi aceito com refino (a limitação do `!` é normativa no git puro
  e prática no FlatDrop — o texto novo diz as duas coisas). Os contratos de formato continuam de
  pé: se o cabeçalho `<!-- flatdrop-manifest v1 -->` ou a tabela do manifesto mudarem, avisar o
  KCM por uma linha aqui nesta seção. (Mensagem de 2026-07-29.)
