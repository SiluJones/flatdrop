# spec-0001 — Tipos de arquivo na allowlist (config.py)

**Tipo:** código · **Alvo:** `flatdrop/config.py` · **Autor:** chat · **Aplicador:** Claude Code
**Origem:** pedido em `260621-tipos_de_arquivos_a_adicionar.txt` + pesquisa dos tipos que o Projeto do Claude aceita.

## Objetivo
Acrescentar à allowlist padrão (`DEFAULT_EXTENSIONS`) os tipos pedidos e os que o Projeto do Claude
aceita mas estavam de fora, além de um conjunto curado de linguagens/configs comuns. **Não remover nada.**

## Contexto / decisões embutidas
- O Projeto do Claude aceita, além de texto/código: **PDF, DOCX, XLSX** (XLSX exige a ferramenta de
  análise/código ligada) e ainda **ODT, RTF, EPUB, DOC**. Imagens/áudio/vídeo seguem FORA (decisão do usuário).
- `.gd.uid` (Godot) tem extensão efetiva `uid` (o `split_name` parte `icon.gd.uid` em `icon.gd` + `.uid`),
  então adicionar `uid` já o cobre; `gd` cobre os scripts.
- **Atenção (binários):** `pdf/docx/xlsx/doc/odt/epub/rtf` são binários. Copiam normalmente, mas a
  estimativa de tokens (`bytes/4`) não vale para eles, e podem ser grandes (o Projeto tem teto de 30 MB/arquivo).
  Isso é aceitável; só não confie no número de tokens quando houver muitos binários.
- A lista de linguagens/configs abaixo é generosa de propósito; **se algum tipo não interessar a você,
  remova a string antes de aplicar** — é o seu projeto.

## Edição (append-only dentro do set)

**Âncora:** dentro de `DEFAULT_EXTENSIONS`, a última linha do grupo "Documentação":
```
    "md", "markdown", "mdx", "rst", "adoc", "asciidoc", "txt", "tex",
```
**Ação:** logo APÓS essa linha (e ANTES do `}` que fecha o set), inserir os blocos:
```
    # Documentos que o Projeto do Claude aceita (BINÁRIOS — copiam, mas a
    # estimativa de tokens não vale para eles; imagens/áudio/vídeo seguem fora).
    "pdf", "docx", "doc", "xlsx", "rtf", "odt", "epub",
    # Godot (projeto do usuário) — todos texto, exceto nada relevante de binário.
    "gd", "uid", "gdshader", "tscn", "tres", "godot", "import",
    # Linguagens comuns que faltavam (todas texto/código).
    "jl", "nim", "zig", "sol", "cu", "cuh", "hx", "coffee",
    "vb", "vbs", "pas", "pp", "f90", "f95", "for",
    "scm", "rkt", "lisp", "psm1", "psd1",
    # Infra / config como código.
    "hcl", "tf", "tfvars", "nix", "cmake", "bicep",
    # Markup / dados / templates que faltavam.
    "org", "rmd", "qmd", "bib", "sty", "cls", "plist",
    "jsonl", "ndjson", "hbs", "handlebars", "ejs", "pug",
    "liquid", "njk", "mustache", "twig",
```

## Validação
- `python -m pytest -q` (a allowlist é lida por `is_allowed_type`; os testes existentes não devem quebrar —
  nenhum deles depende da AUSÊNCIA desses tipos).
- Rápido manual (opcional): pré-visualizar uma pasta com um `.gd`, um `.pdf` e um `.docx` e conferir que
  aparecem nos "Arquivos a copiar" em vez de "Pulados: tipo".

## Fora do escopo desta spec
- O campo da GUI para SELECIONAR tipo na hora (só-md / exceto-md) e o `.flatdropignore` ficam para specs próprias.
