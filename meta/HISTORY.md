# HISTÓRICO — FlatDrop

Referência densa, para ler sob demanda. Reúne a pesquisa que fundamentou as
decisões: o que existe lá fora, como o Claude lida com upload e por que o
achatamento para pasta é o caminho. As decisões em si estão em `DECISIONS.md`;
aqui fica o "porquê por trás do porquê".

> Nota: os números abaixo vêm de pesquisa feita na sessão de gênese (fontes
> públicas de fev–abr/2026). Limites de produto mudam; reconfirme antes de
> depender deles.

## Como o Claude lida com upload de arquivos

- A interface de upload aceita **arquivos**, não **pastas**. Não há, em nenhuma
  das plataformas pesquisadas, upload de uma pasta inteira de uma vez — o usuário
  sobe arquivo a arquivo, ou usa uma ferramenta para juntar/preparar antes. É
  exatamente essa lacuna que o FlatDrop ataca.
- Nos arquivos de um **Projeto** do Claude (planos pagos), o limite observado era
  de cerca de 30 MB por arquivo, com número de arquivos efetivamente ilimitado.
- Tipos aceitos como conhecimento de **texto**: TXT, MD, CSV, JSON, HTML,
  código-fonte em geral, além de DOCX e PDF. **Não** entram como texto útil:
  vídeo, áudio, PPTX e binários em geral — e imagens não servem como conhecimento
  textual de Projeto. Por isso a allowlist do FlatDrop foca em texto/código.
- Há um teto **suave** de contexto na casa das centenas de milhares de tokens
  (~200K como referência); acima disso o material tende a ser recuperado por
  busca (RAG) em vez de caber inteiro de uma vez. Daí a estimativa grosseira de
  tokens no manifesto: serve para "sentir" a proximidade desse teto, não para
  contabilizar com exatidão.

## Prior art (ferramentas semelhantes)

- **Repomix** (github.com/yamadashy/repomix) é o nome dominante do gênero
  "empacotar repositório para LLM". Ele **concatena** o repositório inteiro em
  **um** arquivo (XML ou Markdown) pensado para colar num modelo. Respeita o
  `.gitignore` e usa Secretlint para evitar vazar segredos.
- **OneFile** e similares fazem a mesma ideia central: reduzir o projeto a um
  único artefato textual.
- **Nenhuma** das ferramentas pesquisadas faz o nicho específico do usuário:
  **achatar para uma pasta** (mantendo arquivos individuais) com **renomeação à
  prova de colisão** para então arrastar tudo de uma vez. Esse é o espaço que o
  FlatDrop ocupa.

### O que herdamos do estado da arte

Mesmo seguindo por outro caminho (pasta, não single-file), valem as boas práticas
consolidadas por essas ferramentas:
- respeitar o `.gitignore`;
- pular arquivos sensíveis por padrão;
- dar à IA um mapa/manifesto explicando o material;
- oferecer uma estimativa de tamanho/tokens.

## Por que achatar para PASTA, e não concatenar num arquivo único

A escolha (DEC-001) parte do fluxo real do usuário:

- O destino é os **arquivos de um Projeto** do Claude, que lidam bem com muitos
  arquivos individuais e os indexam separadamente.
- Manter arquivos separados dá **atualização granular**: ao mexer em um arquivo,
  troca-se aquele arquivo, sem reenviar um blob gigante a cada alteração.
- Arrastar uma pasta de arquivos avulsos casa com o hábito atual do usuário (que
  hoje arrasta pasta por pasta e renomeia duplicados na mão) — o FlatDrop só
  remove o atrito de organizar e renomear.

O modo single-file não foi rejeitado como inútil — ele é ótimo para colar um
projeto numa conversa avulsa. Ficou como **complemento** futuro (Fase 4), não
como o produto principal.

## Sobre copiar arquivos e o "desgaste" de SSD

A dúvida do usuário (copiar arquivos que serão apagados logo depois é
desperdício? desgasta o SSD?) foi analisada e fechada como **não-problema**
(DEC-002):

- Os arquivos são de texto/código, quase todos abaixo de 1 MB.
- A gravação é ocasional (quando se quer atualizar o Projeto), não contínua.
- A durabilidade de um SSD é medida em TBW (terabytes escritos ao longo da vida);
  escrever alguns megabytes esporadicamente é ordens de grandeza distante de
  qualquer limite relevante.

Copiar (em vez de mover ou usar symlink) é, portanto, a opção simples e correta:
não destrói a origem e funciona no fluxo de arrastar para um aplicativo, onde
links simbólicos não se resolveriam.
