# FlatDrop

Achata uma pasta de projeto do Windows numa **única pasta plana** (por padrão no
seu `Downloads`), renomeando arquivos de mesmo nome para nunca colidirem, de modo
que você possa **arrastar tudo de uma vez** para os arquivos de um Projeto do Claude.

Hoje, para atualizar o conhecimento de um Projeto, é preciso arrastar pasta por
pasta e renomear duplicados (`page.tsx`, `__init__.py`, `index.ts`…) na mão. O
FlatDrop faz isso por você: percorre a árvore a partir de uma raiz, ignora o que
não interessa (lendo o `.gitignore` + uma lista embutida de ruído), pega só os
tipos de arquivo que o Claude usa como texto, resolve as colisões de nome e
deposita tudo numa pasta só, junto de um `_MANIFEST.md` que mapeia cada arquivo
de volta ao seu lugar original.

## Requisitos

- **Python 3.11+** (no Windows, baixe em python.org — o `tkinter` já vem junto).
- **pathspec** (opcional, recomendado) para interpretar o `.gitignore` do projeto.

## Instalação

```bash
pip install -r requirements.txt
```

Se você pular esta etapa, o FlatDrop ainda funciona — apenas não lê o `.gitignore`
(continua ignorando `node_modules`, `.git`, lockfiles e afins pela lista embutida).

## Como usar

```bash
python run.py
```

A janela abre. Então:

1. **Escolha a pasta raiz** do projeto. O nome da pasta de saída é preenchido
   automaticamente com o nome dela (você pode editar).
2. **Destino** já vem como seu `Downloads` (pode trocar).
3. Escolha o **modo de renomeação** (veja abaixo).
4. Clique em **Pré-visualizar** para ver o que será copiado, o que foi pulado e
   uma estimativa grosseira de tokens — **sem gravar nada**.
5. Clique em **Executar** para copiar de fato. Depois, **Abrir pasta** e arraste
   tudo para o seu Projeto do Claude.

### Modos de renomeação

- **Só duplicados** (padrão): apenas arquivos com nome repetido em pastas
  diferentes ganham sufixo. O resto fica com o nome original. *Mais limpo.*
- **Todos**: todo arquivo ganha pelo menos o nome da pasta-pai como sufixo.
- **Caminho completo**: cada arquivo carrega o caminho inteiro desde a raiz.

Exemplo (modo "só duplicados"), quatro `index.tsx` viram:
`index__app__admin.tsx`, `index__app__users.tsx`, `index__pages__users.tsx`,
`index__src__users.tsx`. (Em projetos Python, com muitos `__init__.py`, vale
trocar o separador `__` por `-` na interface para ler melhor.)

## O manifesto

Cada execução grava um `_MANIFEST.md` na pasta de saída com: a origem, data,
modo, contagem/tamanho/estimativa de tokens e uma tabela
`caminho original → nome plano`. Suba esse arquivo junto: ele devolve ao Claude a
estrutura de pastas que o achatamento desfez. Ele também é o **marcador** que
permite ao FlatDrop limpar e reusar a mesma pasta com segurança (uma pasta que
não tenha esse marcador nunca é apagada — o app cria uma variante `nome (2)`).

## Estrutura do repositório

```
flatdrop/
├── run.py                 # entrypoint: python run.py
├── requirements.txt       # pathspec (opcional)
├── flatdrop/
│   ├── __init__.py        # versão do pacote
│   ├── config.py          # defaults: extensões, ignores, sensíveis, separador
│   ├── core.py            # lógica pura (planejar/executar), sem UI — testável
│   └── gui.py             # interface tkinter (só amarra a core)
└── tests/
    └── test_core.py       # 13 testes (pytest)
```

Rodar os testes:

```bash
pip install pytest
python -m pytest -q       # rode a partir da raiz do repositório
```

## Privacidade

Arquivos sensíveis (`.env` real, `*.pem`, `*.key`, `id_rsa`, `secrets.*`…) são
**sempre pulados**, a menos que você marque explicitamente "incluir sensíveis".
Variantes de exemplo como `.env.example` são permitidas. Ainda assim, **confira a
pré-visualização** antes de subir qualquer coisa: a lista é uma rede de segurança,
não um scanner de conteúdo.

---

Documentação de contexto do projeto (para continuar entre conversas) em
`CONTEXT.md`, `STATUS.md`, `DECISIONS.md`, `ROADMAP.md` e nos demais `.md` da raiz.
