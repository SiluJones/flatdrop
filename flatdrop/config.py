"""Valores padrão do FlatDrop.

Tudo aqui é configurável pela GUI; estes são apenas os defaults sensatos.
Mantido separado da lógica para ficar fácil de editar sem mexer na core.
"""

from __future__ import annotations

# Separador usado ao costurar o caminho da pasta dentro do nome do arquivo.
# Ex.: "page.tsx" em app/routes/users vira "page__routes__users.tsx".
# "__" é seguro em qualquer sistema de arquivos e visualmente distinto.
# Evite "." (parece extensão) e "/" "\" (inválidos no nome).
DEFAULT_SEP = "__"

# Nome do arquivo de manifesto gerado na pasta de saída.
# Serve a dois propósitos: (1) mapa de origem legível pelo Claude e por você;
# (2) marcador que prova que a pasta foi criada por esta ferramenta — só por
# isso o FlatDrop se permite limpá-la antes de regravar (ver core.safe_clear).
MANIFEST_NAME = "_MANIFEST.md"
MANIFEST_SIGNATURE = "<!-- flatdrop-manifest v1 -->"

# Limite de tamanho do nome de arquivo gerado. O Windows aceita até 255, mas
# deixamos folga para sufixos de contador e para não estourar caminhos longos.
MAX_NAME_LEN = 200

# Extensões de texto que o Claude lê e que são úteis num projeto de código.
# Imagens, binários, áudio, vídeo e PPTX ficam DE FORA de propósito: o Claude
# não os usa como conhecimento de texto do Projeto.
DEFAULT_EXTENSIONS: set[str] = {
    # Linguagens
    "py", "pyw", "pyi", "ipynb",
    "js", "mjs", "cjs", "jsx", "ts", "tsx", "vue", "svelte", "astro",
    "java", "kt", "kts", "scala", "groovy", "gradle",
    "go", "rs", "rb", "php", "pl", "lua", "r", "dart", "swift",
    "c", "h", "cpp", "cc", "cxx", "hpp", "hh", "cs", "m", "mm",
    "ex", "exs", "erl", "clj", "cljs", "elm", "hs", "ml", "fs",
    "sh", "bash", "zsh", "fish", "ps1", "bat", "cmd",
    "sql", "graphql", "gql", "proto",
    # Web / markup
    "html", "htm", "css", "scss", "sass", "less", "styl",
    "xml", "xsl", "vue",
    # Config / dados
    "json", "jsonc", "json5", "yaml", "yml", "toml", "ini", "cfg",
    "conf", "properties", "env_example",  # ".env.example" é tratado à parte
    "csv", "tsv",
    # Documentação
    "md", "markdown", "mdx", "rst", "adoc", "asciidoc", "txt", "tex",
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
}

# Arquivos SEM extensão (ou dotfiles) que ainda são texto útil.
# Comparados em minúsculas pelo nome exato.
DEFAULT_EXTENSIONLESS_ALLOW: set[str] = {
    "dockerfile", "containerfile", "makefile", "gnumakefile",
    "procfile", "rakefile", "gemfile", "brewfile", "jenkinsfile",
    "license", "licence", "readme", "changelog", "authors", "notice",
    "contributing", "codeowners", "vagrantfile",
    ".gitignore", ".gitattributes", ".dockerignore", ".editorconfig",
    ".npmrc", ".nvmrc", ".prettierrc", ".eslintrc", ".babelrc",
    ".env.example", ".env.sample", ".env.template",
}

# Diretórios pulados SEMPRE, mesmo sem .gitignore (ruído / binário / build).
# É uma rede de segurança; o .gitignore costuma cobrir a maioria.
DEFAULT_DIR_IGNORES: set[str] = {
    ".git", ".hg", ".svn", ".bzr",
    "node_modules", "bower_components", "jspm_packages",
    ".venv", "venv", "virtualenv", ".tox", ".nox",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".hypothesis",
    "dist", "build", "out", "target", "bin", "obj",
    ".next", ".nuxt", ".svelte-kit", ".astro", ".turbo", ".vercel",
    ".idea", ".gradle", ".cache", ".parcel-cache",
    "coverage", ".nyc_output", "htmlcov",
    ".terraform", ".serverless",
}

# Arquivos pulados por padrão mesmo quando versionados: ruído de baixo valor
# para contexto (lockfiles enormes, minificados, source maps).
DEFAULT_FILE_IGNORES: set[str] = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "npm-shrinkwrap.json",
    "poetry.lock", "pipfile.lock", "cargo.lock", "composer.lock", "gemfile.lock",
    ".ds_store", "thumbs.db", "desktop.ini",
    ".flatdropignore",  # arquivo de controle do FlatDrop — nao vai para o upload
}

# Sufixos pulados por padrão (minificados, mapas, compilados).
DEFAULT_SUFFIX_IGNORES: tuple[str, ...] = (
    ".min.js", ".min.css", ".map", ".lock",
    ".pyc", ".pyo", ".class", ".o", ".so", ".dll", ".exe",
)

# Padrões SENSÍVEIS — nunca copiados a menos que você marque "incluir sensíveis".
# Rede de segurança contra vazar segredo num upload (o .gitignore costuma pegar,
# mas confiar só nele é arriscado). Não é um scanner de conteúdo como o Secretlint.
SENSITIVE_EXACT: set[str] = {
    "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519",
    "secrets.json", "secrets.yaml", "secrets.yml", "credentials.json",
    ".netrc", ".pgpass", ".htpasswd",
}
SENSITIVE_SUFFIXES: tuple[str, ...] = (
    ".pem", ".key", ".pfx", ".p12", ".keystore", ".jks", ".ppk",
    ".secret", ".secrets",
)
# Considerados seguros mesmo casando ".env" (são exemplos sem valores reais).
SENSITIVE_ENV_SAFE_SUFFIXES: tuple[str, ...] = (
    ".example", ".sample", ".template", ".dist",
)
