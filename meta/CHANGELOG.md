# Changelog — FlatDrop

Todas as mudanças notáveis deste projeto são registradas aqui.
Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/);
versionamento conforme [SemVer](https://semver.org/lang/pt-BR/).

## [Não lançado]

Sem mudanças ainda. Próximos candidatos em `ROADMAP.md` (Fase 2).

## [0.1.0] — 2026-06-05

Primeira versão funcional (MVP). Projeto, arquitetura, código e documentação de
contexto criados na sessão de gênese.

### Adicionado
- Pipeline de duas fases: `make_plan` (pré-visualização, não grava nada) e
  `execute_plan` (copia e gera manifesto).
- Varredura recursiva a partir de uma pasta raiz com `os.walk(followlinks=False)`
  e poda de diretórios in-place.
- Leitura do `.gitignore` da raiz via pathspec (dependência opcional, com modo
  degradado e aviso quando ausente).
- Ignores embutidos de diretórios (`node_modules`, `.git`, `dist`, `.next`…),
  arquivos (lockfiles, `.DS_Store`…) e sufixos (`.min.js`, `.map`, compilados).
- Allowlist de tipos de texto/código úteis ao Claude e lista de arquivos sem
  extensão permitidos (`Dockerfile`, `Makefile`, `.gitignore`…).
- Denylist de arquivos sensíveis (`.env` real, `*.pem`/`*.key`, `id_rsa`,
  `secrets.*`…) sempre pulada por padrão, com exceção para exemplos
  (`.env.example`/`.sample`/`.template`).
- Renomeação à prova de colisão com unicidade garantida (case-insensitive),
  desambiguação por profundidade uniforme dentro de cada grupo de nome,
  truncamento de nomes longos com hash e passe final de contador.
- Três modos de renomeação: `collisions` (padrão), `all` e `fullpath`.
- `safe_clear` / `is_our_folder` / `_resolve_dest`: limpa e reusa apenas pastas
  vazias ou comprovadamente do FlatDrop; pasta de terceiros vira variante `(2)`.
- `_MANIFEST.md` na saída: assinatura, metadados (origem, data, modo, contagem,
  tamanho, estimativa grosseira de tokens) e tabela `caminho original → nome plano`.
- Interface gráfica em tkinter amarrando tudo, com trabalho em thread separada.
- Entrypoint `run.py`, `requirements.txt` e `README.md`.
- Suíte de 13 testes em `tests/test_core.py` (pytest), todos passando.
