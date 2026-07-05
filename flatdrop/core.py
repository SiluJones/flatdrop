"""Lógica central do FlatDrop, sem nenhuma dependência de UI.

Pipeline (também é a ordem que a GUI usa):
    make_plan(root, cfg)            -> FlattenPlan   # "pré-visualizar"
    execute_plan(plan, dest, cfg)   -> ExecuteResult # "executar"

A separação entre PLANEJAR e EXECUTAR é deliberada: dá uma pré-visualização
segura (nada é escrito em disco) e torna a renomeação testável sem copiar nada.

Garantia central: os nomes finais na pasta de saída são ÚNICOS, comparados de
forma case-insensitive (porque o destino é Windows, que não diferencia maiúsc.).
"""

from __future__ import annotations

import hashlib
import os
import shutil
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path, PurePath

from . import config as C

# pathspec faz o casamento de .gitignore do jeito certo (negação, **, âncora).
# É opcional: sem ele a ferramenta ainda roda usando só os ignores embutidos.
try:
    import pathspec  # type: ignore

    HAS_PATHSPEC = True
except ImportError:  # pragma: no cover - depende do ambiente
    pathspec = None  # type: ignore
    HAS_PATHSPEC = False


# --------------------------------------------------------------------------- #
# Configuração de uma execução
# --------------------------------------------------------------------------- #
@dataclass
class ScanConfig:
    """Opções de uma varredura/achatamento. Tudo tem default sensato."""

    # "collisions"  -> só arquivos com nome repetido ganham sufixo (recomendado)
    # "all"         -> todo arquivo ganha sufixo (pasta-pai, estendido se colidir)
    # "fullpath"    -> todo arquivo carrega o caminho completo desde a raiz
    mode: str = "collisions"
    # Só no modo "fullpath" e em FONTE ÚNICA: inclui o nome da pasta-raiz como a
    # pasta mais externa do sufixo (arquivos da raiz passam a levar o nome do
    # projeto). Ignorado nos outros modos e em multi-fonte (spec0013). O limite de
    # nome (MAX_NAME_LEN) segue protegido pelo truncamento com hash já existente.
    root_in_name: bool = False
    sep: str = C.DEFAULT_SEP
    use_gitignore: bool = True
    include_sensitive: bool = False
    extensions: set[str] = field(default_factory=lambda: set(C.DEFAULT_EXTENSIONS))
    extensionless_allow: set[str] = field(
        default_factory=lambda: set(C.DEFAULT_EXTENSIONLESS_ALLOW)
    )
    dir_ignores: set[str] = field(default_factory=lambda: set(C.DEFAULT_DIR_IGNORES))
    file_ignores: set[str] = field(default_factory=lambda: set(C.DEFAULT_FILE_IGNORES))
    suffix_ignores: tuple[str, ...] = C.DEFAULT_SUFFIX_IGNORES
    write_manifest: bool = True
    write_tree: bool = False  # gera _TREE.md (arvore da origem); desligado por padrao (spec0011)
    # Nivel de detalhe dos ARQUIVOS pulados soltos no _TREE.md:
    #   "summary" -> agregado por pasta ([pulados: tipo x3]); "full" -> folha por arquivo.
    # Pastas ignoradas sao SEMPRE uma linha colapsada, independente disto.
    tree_skipped: str = "summary"  # "summary" | "full"
    clear_dest: bool = True  # só limpa pastas que SÃO nossas (ver safe_clear)

    # --- Filtros desta execução (todos opcionais; vazio/None = sem filtro) --- #
    # only_ext: se definido, RESTRINGE a só estas extensões (ex.: {"md"} = só .md).
    #   Quando ligado, ignora a allowlist ampla e os extensionless (corte duro).
    # exclude_ext: SUBTRAI estas extensões do que seria aceito (ex.: {"md"}).
    # Estes dois são o que o --also-md-from usa para montar "todos os .md" numa
    # fonte e "tudo menos .md" na outra, sem sobreposição.
    only_ext: set[str] | None = None
    exclude_ext: set[str] = field(default_factory=set)
    # Filtro de pasta: um arquivo só entra se algum componente de pasta do seu
    # caminho casar um dos termos (modo starts/contains/exact); um termo com "/"
    # é tratado como prefixo de caminho relativo à raiz da fonte.
    only_folders: list[str] = field(default_factory=list)
    folder_match: str = "starts"  # "starts" | "contains" | "exact"


@dataclass
class Source:
    """Uma fonte de coleta: uma raiz com seu próprio conjunto de filtros.

    Multi-fonte permite combinar coletas diferentes numa ÚNICA saída e um único
    manifesto — ex.: "todos os .md a partir da raiz do repositório" + "tudo menos
    .md a partir de uma subpasta". Os campos de NOMEAÇÃO/EXECUÇÃO (mode, sep,
    dest, clear_dest, write_manifest) são globais e vêm da fonte primária (a
    primeira da lista); só os campos de FILTRO variam por fonte (only_ext,
    exclude_ext, only_folders, use_gitignore, include_sensitive).
    """

    root: Path
    cfg: ScanConfig


# --------------------------------------------------------------------------- #
# Estruturas de resultado
# --------------------------------------------------------------------------- #
@dataclass
class PlannedFile:
    """Um arquivo que será copiado."""

    src: Path                 # caminho absoluto na origem
    rel: PurePath             # caminho relativo à raiz (POSIX, para exibir)
    target: str               # nome final (plano) na pasta de saída
    size: int                 # bytes
    renamed: bool             # ganhou sufixo de pasta?


@dataclass
class FlattenPlan:
    """O que make_plan produz: tudo que será feito, sem ter feito nada ainda."""

    root: Path
    files: list[PlannedFile]
    skipped: dict[str, int]              # motivo -> contagem
    skipped_samples: dict[str, list[str]]  # motivo -> alguns exemplos (rel paths)
    collisions: int                       # quantos nomes-base tinham repetição
    warnings: list[str]
    # Descrições legíveis de cada fonte (vazio/1 item = execução de fonte única).
    # Usado pelo manifesto para registrar de onde veio cada coleta em multi-fonte.
    sources: list[str] = field(default_factory=list)
    # Lista COMPLETA de (rel_posix, motivo) dos pulados — inclui pastas colapsadas
    # (rel terminando em "/"). Alimenta o _TREE.md; vazio quando o scan nao a produz.
    skipped_items: list[tuple[str, str]] = field(default_factory=list)

    @property
    def total_bytes(self) -> int:
        return sum(f.size for f in self.files)

    @property
    def est_tokens(self) -> int:
        # Estimativa GROSSEIRA (~4 bytes/token). Só para sentir a proximidade
        # do teto de contexto do Projeto; não é contagem real de tokens.
        return self.total_bytes // 4


@dataclass
class ExecuteResult:
    """O que execute_plan produz após escrever em disco."""

    dest: Path
    copied: int
    manifest_path: Path | None
    cleared: bool
    warnings: list[str]


# --------------------------------------------------------------------------- #
# Helpers de nome
# --------------------------------------------------------------------------- #
def split_name(name: str) -> tuple[str, str]:
    """Divide um nome em (stem, ext), tratando dotfiles corretamente.

    'page.tsx'        -> ('page', '.tsx')
    '.gitignore'      -> ('.gitignore', '')      # dotfile sem extensão real
    '.eslintrc.json'  -> ('.eslintrc', '.json')
    'Makefile'        -> ('Makefile', '')
    """
    if name.startswith("."):
        rest = name[1:]
        if "." in rest:
            i = name.rfind(".")
            return name[:i], name[i:]
        return name, ""
    i = name.rfind(".")
    if i <= 0:
        return name, ""
    return name[:i], name[i:]


def _sanitize(part: str) -> str:
    """Remove caracteres inválidos em nome de arquivo no Windows."""
    bad = '<>:"/\\|?*'
    out = "".join("-" if ch in bad else ch for ch in part)
    return out.strip(" .") or "_"


def _compose(stem: str, dir_parts: tuple[str, ...], k: int, sep: str, ext: str) -> str:
    """Monta o nome final como stem + sufixo-de-caminho + ext.

    k = quantas pastas (a partir da mais interna) entram no sufixo.
    k<=0 ou sem pastas -> mantém só stem+ext (sem sufixo).
    """
    if k <= 0 or not dir_parts:
        return f"{stem}{ext}"
    chosen = dir_parts[-k:] if k < len(dir_parts) else dir_parts
    suffix = sep.join(_sanitize(p) for p in chosen)
    return f"{stem}{sep}{suffix}{ext}"


def _truncate_if_long(name: str, rel_key: str) -> str:
    """Garante que o nome não estoure MAX_NAME_LEN, preservando unicidade.

    Trunca o meio e cola um hash curto do caminho relativo (estável e único).
    """
    if len(name) <= C.MAX_NAME_LEN:
        return name
    stem, ext = split_name(name)
    digest = hashlib.md5(rel_key.encode("utf-8")).hexdigest()[:8]
    keep = C.MAX_NAME_LEN - len(ext) - len(digest) - 2  # 2 = "~" + sep antes do hash
    keep = max(keep, 8)
    return f"{stem[:keep]}~{digest}{ext}"


# --------------------------------------------------------------------------- #
# Filtros
# --------------------------------------------------------------------------- #
def is_sensitive(name: str) -> bool:
    """True se o arquivo parece conter segredo (chave, .env real, credencial)."""
    low = name.lower()
    if low in C.SENSITIVE_EXACT:
        return True
    if any(low.endswith(sfx) for sfx in C.SENSITIVE_SUFFIXES):
        return True
    if low == ".env" or low.startswith(".env."):
        # .env.example / .sample / .template são seguros (sem valores reais).
        if low.endswith(C.SENSITIVE_ENV_SAFE_SUFFIXES):
            return False
        return True
    return False


def is_allowed_type(name: str, cfg: ScanConfig) -> bool:
    """True se a extensão (ou o nome, p/ extensionless) está na allowlist.

    Os filtros desta execução agem por cima da allowlist padrão:
    - exclude_ext SUBTRAI (um .md vira não-aceito se "md" estiver em exclude_ext);
    - only_ext RESTRINGE de forma dura: se definido, só passam as extensões
      listadas — nem extensionless (Dockerfile, .gitignore) nem o resto da
      allowlist ampla. É o que faz "--only-ext md" trazer apenas .md.
    """
    low = name.lower()
    _, ext = split_name(name)
    ext_nodot = ext[1:].lower() if ext else ""

    # exclude_ext: corte por subtração (não afeta extensionless, que tem ext "").
    if ext_nodot and ext_nodot in cfg.exclude_ext:
        return False
    # only_ext: corte por restrição (ignora extensionless e a allowlist ampla).
    if cfg.only_ext is not None:
        return ext_nodot in cfg.only_ext
    # comportamento padrão (sem filtro de tipo):
    if low in cfg.extensionless_allow:
        return True
    if not ext:
        return False
    return ext_nodot in cfg.extensions


def _folder_matches(rel: PurePath, cfg: ScanConfig) -> bool:
    """True se o arquivo passa o filtro de pasta (vazio = passa tudo).

    Casa se QUALQUER componente de pasta do caminho satisfaz um termo no modo
    escolhido (starts/contains/exact). Um termo contendo "/" é tratado como
    prefixo de caminho relativo à raiz da fonte (ex.: "Cinzeiro-Story/docs").
    """
    if not cfg.only_folders:
        return True
    parent_posix = rel.parent.as_posix().lower()
    parts = [p.lower() for p in rel.parent.parts]
    for term in cfg.only_folders:
        t = term.strip().strip("/").lower()
        if not t:
            continue
        if "/" in t:  # prefixo de caminho
            if parent_posix == t or parent_posix.startswith(t + "/"):
                return True
            continue
        for p in parts:  # casa um componente de pasta
            if cfg.folder_match == "exact" and p == t:
                return True
            if cfg.folder_match == "contains" and t in p:
                return True
            if cfg.folder_match == "starts" and p.startswith(t):
                return True
    return False


def _read_ignore_lines(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return []


def _rebase_ignore(line: str, base: str) -> list[str]:
    """Reescreve um padrão de ignore de um arquivo em ``base`` (rel posix, sem barra
    final) para casar contra caminhos relativos à RAIZ. Devolve [] p/ vazio/comentário.

    - âncora (`/inicio` ou com `/` no meio): casa só dentro de ``base``;
    - sem âncora (ex.: ``*.log``): casa direto em ``base`` E em qualquer profundidade abaixo.
    """
    s = line.strip()
    if not s or s.startswith("#"):
        return []
    neg = ""
    if s.startswith("!"):
        neg, s = "!", s[1:]
    if not base:  # arquivo na raiz: sem rebase
        return [neg + s]
    trailing = ""
    if s.endswith("/"):
        trailing, s = "/", s[:-1]
    anchored = s.startswith("/") or ("/" in s)
    if s.startswith("/"):
        s = s[1:]
    if anchored:
        return [f"{neg}{base}/{s}{trailing}"]
    return [f"{neg}{base}/{s}{trailing}", f"{neg}{base}/**/{s}{trailing}"]


def _rebase_all(lines: list[str], base: str) -> list[str]:
    out: list[str] = []
    for ln in lines:
        out += _rebase_ignore(ln, base)
    return out


def _collect_ignore_lines(root: Path, cfg: ScanConfig) -> tuple[list[str], list[str]]:
    """Junta as linhas (rebaseadas) de todos os .gitignore e .flatdropignore da árvore.

    Devolve (gitignore_lines, flatdropignore_lines), cada um em ordem raso->fundo.
    """
    gi_by: list[tuple[int, list[str]]] = []
    fd_by: list[tuple[int, list[str]]] = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        cur = Path(dirpath)
        rel = cur.relative_to(root).as_posix()
        base = "" if rel == "." else rel
        depth = 0 if base == "" else base.count("/") + 1
        # não desce nos ignores embutidos (evita varrer node_modules atrás de ignores)
        dirnames[:] = [d for d in dirnames if d not in cfg.dir_ignores]
        if cfg.use_gitignore and ".gitignore" in filenames:
            gi_by.append((depth, _rebase_all(_read_ignore_lines(cur / ".gitignore"), base)))
        if ".flatdropignore" in filenames:
            fd_by.append((depth, _rebase_all(_read_ignore_lines(cur / ".flatdropignore"), base)))
    gi_lines: list[str] = []
    for _, lines in sorted(gi_by, key=lambda t: t[0]):
        gi_lines += lines
    fd_lines: list[str] = []
    for _, lines in sorted(fd_by, key=lambda t: t[0]):
        fd_lines += lines
    return gi_lines, fd_lines


def _make_spec(lines: list[str]):
    if not lines:
        return None
    # "gitignore" é o factory novo; "gitwildmatch" o antigo (depreciado).
    for factory in ("gitignore", "gitwildmatch"):
        try:
            return pathspec.PathSpec.from_lines(factory, lines)
        except Exception:
            continue
    return None


def _build_ignore_specs(root: Path, cfg: ScanConfig):
    """(full, gi, fd): ``full`` = decisão (gitignore + flatdropignore, este por último
    p/ ter a palavra final); ``gi``/``fd`` = só p/ atribuir o motivo e detectar liberação."""
    if not HAS_PATHSPEC:
        return None, None, None
    gi_lines, fd_lines = _collect_ignore_lines(root, cfg)
    if not gi_lines and not fd_lines:
        return None, None, None
    return _make_spec(gi_lines + fd_lines), _make_spec(gi_lines), _make_spec(fd_lines)


def _ignore_status(rel: str, full, gi, fd) -> tuple[bool, str, bool]:
    """(ignored, source, liberated). source ∈ {'gitignore','flatdropignore',''}.
    liberated = o .gitignore pegaria, mas o .flatdropignore liberou (negação)."""
    if full is None:
        return False, "", False
    if full.match_file(rel):
        if fd is not None and fd.match_file(rel):
            return True, "flatdropignore", False
        return True, "gitignore", False
    if gi is not None and gi.match_file(rel):
        return False, "", True
    return False, "", False


# --------------------------------------------------------------------------- #
# Varredura
# --------------------------------------------------------------------------- #
def _scan(
    root: Path, cfg: ScanConfig
) -> tuple[list[tuple[Path, PurePath, int]], dict, dict, list, list[tuple[str, str]]]:
    """Percorre a árvore e separa candidatos de pulados.

    Devolve (candidatos, skipped_counts, skipped_samples, warnings, skipped_items).
    candidato = (src_abs, rel_posix, size_bytes).
    skipped_items = lista COMPLETA de (rel_posix, motivo) dos pulados — inclui as
    pastas colapsadas (uma entrada cada, rel terminando em "/"). Alimenta o _TREE.md
    no modo "full"; independe do teto de 8 amostras de skipped_samples.
    """
    full_spec, gi_spec, fd_spec = _build_ignore_specs(root, cfg)
    candidates: list[tuple[Path, PurePath, int]] = []
    skipped: dict[str, int] = {
        "gitignore": 0,
        "gitignore (pasta)": 0,
        "flatdropignore": 0,
        "flatdropignore (pasta)": 0,
        "tipo": 0,
        "sensível": 0,
        "filtro (pasta)": 0,
        "ignore_padrão": 0,
        "ignore_padrão (pasta)": 0,
    }
    samples: dict[str, list[str]] = {k: [] for k in skipped}
    warnings: list[str] = []

    skipped_items: list[tuple[str, str]] = []

    def note(reason: str, rel: str) -> None:
        skipped[reason] += 1
        if len(samples[reason]) < 8:
            samples[reason].append(rel)
        # Lista completa (sem teto) para a arvore fiel do _TREE.md modo "full".
        skipped_items.append((rel, reason))

    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        cur = Path(dirpath)
        rel_dir = cur.relative_to(root)

        # Poda de diretórios IN-PLACE (evita descer em node_modules etc.).
        # IMPORTANTE: cada poda é CONTABILIZADA com motivo e amostra. Antes era
        # silenciosa: uma pasta casada pelo .gitignore sumia com a subárvore
        # inteira sem deixar rastro na pré-visualização (FIX-001 — caso real:
        # pastas "logs" engolidas pelo .gitignore do monorepo do usuário).
        kept = []
        for d in dirnames:
            rel_sub = (rel_dir / d).as_posix()
            if d in cfg.dir_ignores:
                note("ignore_padrão (pasta)", rel_sub + "/")
                continue
            ign, src, _ = _ignore_status(rel_sub + "/", full_spec, gi_spec, fd_spec)
            if ign:
                note(f"{src} (pasta)", rel_sub + "/")
                continue
            kept.append(d)
        dirnames[:] = kept

        for fn in filenames:
            rel = PurePath((rel_dir / fn).as_posix())
            rel_str = rel.as_posix()
            low = fn.lower()

            # 1) ignores embutidos (arquivo/sufixo) e .gitignore
            if low in cfg.file_ignores or low.endswith(cfg.suffix_ignores):
                note("ignore_padrão", rel_str)
                continue
            ign, src, _ = _ignore_status(rel_str, full_spec, gi_spec, fd_spec)
            if ign:
                note(src, rel_str)
                continue
            # 2) sensíveis
            if not cfg.include_sensitive and is_sensitive(fn):
                note("sensível", rel_str)
                continue
            # 3) tipo aceito? (inclui only_ext/exclude_ext desta execução)
            if not is_allowed_type(fn, cfg):
                note("tipo", rel_str)
                continue
            # 3b) filtro de pasta (se houver): só certas pastas desta fonte
            if not _folder_matches(rel, cfg):
                note("filtro (pasta)", rel_str)
                continue
            # 4) candidato
            try:
                size = (cur / fn).stat().st_size
            except OSError:
                size = 0
            candidates.append((cur / fn, rel, size))

    return candidates, skipped, samples, warnings, skipped_items


# --------------------------------------------------------------------------- #
# Renomeação à prova de colisão (o coração)
# --------------------------------------------------------------------------- #
def _plan_names(
    candidates: list[tuple[Path, PurePath, int]],
    cfg: ScanConfig,
    root_prefix: str | None = None,
) -> tuple[list[PlannedFile], int, list[str]]:
    """Atribui um nome final único a cada candidato segundo o modo escolhido.

    Estratégia (profundidade UNIFORME por grupo de nome — mais legível):
      1. Agrupa candidatos pelo nome de arquivo original (stem+ext).
      2. Para cada grupo com mais de um arquivo, escolhe UM k (nº de pastas no
         sufixo) que desempata todos os membros — e aplica o MESMO k a todos.
         Assim todas as instâncias de "index.tsx" carregam a mesma profundidade.
      3. fullpath: cada arquivo carrega seu caminho completo.
         all: arquivos sem repetição ganham a pasta-pai (k=1); repetidos sobem
         até desempatar. collisions: arquivos sem repetição ficam intactos.
      4. Trunca nomes longos demais (com hash, mantendo unicidade).
      5. Passe final de contador (_2, _3...) para qualquer empate residual
         (inclusive colisões raras entre grupos diferentes).
    """
    n = len(candidates)
    warnings: list[str] = []
    # pré-computa stem, ext, partes de pasta
    meta = []
    for src, rel, _size in candidates:
        stem, ext = split_name(rel.name)
        dir_parts = rel.parent.parts if rel.parent.as_posix() != "." else ()
        # spec0013/0014: com root_in_name, o sufixo de caminho é montado só no NOME
        # (o rel de exibição do manifesto/tree permanece o real, sem a raiz).
        # Ordem do sufixo (spec0014): pastas da mais INTERNA para a mais externa,
        # com o nome da pasta-raiz por ÚLTIMO. Ex.: app/routes/page.tsx (raiz meuapp)
        # -> stem "page" + "routes__app__meuapp". O _compose junta dir_parts na
        # ordem dada, então a inversão é feita aqui e o _compose fica intocado.
        if root_prefix:
            dir_parts = (*reversed(dir_parts), root_prefix)
        meta.append((stem, ext, dir_parts))

    ks = [0] * n

    def compose(i: int, k: int) -> str:
        return _compose(meta[i][0], meta[i][2], k, cfg.sep, meta[i][1])

    # piso de k por modo (quanto cada arquivo ganha mesmo sem colidir)
    if cfg.mode == "fullpath":
        floor = [len(m[2]) for m in meta]
    elif cfg.mode == "all":
        floor = [min(1, len(m[2])) for m in meta]
    else:  # collisions
        floor = [0] * n

    # agrupa por nome original (stem+ext), case-insensitive
    by_base: dict[str, list[int]] = {}
    for i, (stem, ext, _dp) in enumerate(meta):
        by_base.setdefault(f"{stem}{ext}".lower(), []).append(i)
    collisions = sum(1 for idxs in by_base.values() if len(idxs) > 1)

    for idxs in by_base.values():
        if len(idxs) == 1:
            ks[idxs[0]] = floor[idxs[0]]
            continue
        # grupo repetido: acha k uniforme que torna todos distintos
        maxdepth = max(len(meta[i][2]) for i in idxs)
        start = max(1, max(floor[i] for i in idxs))
        chosen = maxdepth  # fallback; contador resolve se nem isto bastar
        for k in range(start, maxdepth + 1):
            names = {compose(i, k).lower() for i in idxs}
            if len(names) == len(idxs):
                chosen = k
                break
        for i in idxs:
            ks[i] = chosen

    names = [compose(i, ks[i]) for i in range(n)]

    # 3) trunca longos
    for i in range(n):
        names[i] = _truncate_if_long(names[i], candidates[i][1].as_posix())

    # 4) passe final de contador (garante unicidade absoluta)
    seen: dict[str, int] = {}
    finals: list[str] = []
    for nm in names:
        low = nm.lower()
        if low not in seen:
            seen[low] = 1
            finals.append(nm)
        else:
            stem, ext = split_name(nm)
            c = seen[low]
            while True:
                c += 1
                cand = f"{stem}{cfg.sep}{c}{ext}"
                if cand.lower() not in seen:
                    break
            seen[low] = c
            seen[cand.lower()] = 1
            finals.append(cand)
            warnings.append(f"Colisão residual resolvida com contador: {cand}")

    planned: list[PlannedFile] = []
    for i, (src, rel, size) in enumerate(candidates):
        renamed = finals[i].lower() != rel.name.lower()
        planned.append(PlannedFile(src=src, rel=rel, target=finals[i], size=size, renamed=renamed))
    return planned, collisions, warnings


# --------------------------------------------------------------------------- #
# API pública: planejar e executar
# --------------------------------------------------------------------------- #
def make_plan(root: str | os.PathLike, cfg: ScanConfig) -> FlattenPlan:
    """Pré-visualização de FONTE ÚNICA: varre a raiz e calcula nomes, sem gravar.

    É um atalho para o caso comum. Internamente delega a make_plan_sources com
    uma única fonte, então todo o comportamento (e os testes) seguem idênticos.
    """
    root_path = Path(root).resolve()
    if not root_path.is_dir():
        raise NotADirectoryError(f"Pasta raiz não encontrada: {root_path}")
    return make_plan_sources([Source(root_path, cfg)])


def _describe_source(root: Path, cfg: ScanConfig) -> str:
    """Resumo legível de uma fonte para registrar no manifesto/saída."""
    bits: list[str] = []
    if cfg.only_ext is not None:
        bits.append("só: " + ", ".join(sorted(cfg.only_ext)) if cfg.only_ext else "só: (nenhuma)")
    if cfg.exclude_ext:
        bits.append("exceto: " + ", ".join(sorted(cfg.exclude_ext)))
    if cfg.only_folders:
        bits.append(f"pastas[{cfg.folder_match}]: " + ", ".join(cfg.only_folders))
    if not cfg.use_gitignore:
        bits.append("sem .gitignore")
    suffix = f"  ({'; '.join(bits)})" if bits else ""
    return f"`{root}`{suffix}"


def make_plan_sources(sources: list["Source"]) -> FlattenPlan:
    """Pré-visualização MULTI-FONTE: varre várias raízes/filtros e funde tudo
    numa única lista plana com unicidade garantida e UM manifesto.

    Passos:
      1. Resolve e valida cada raiz; calcula a RAIZ COMUM (para os caminhos do
         manifesto e para a desambiguação serem coerentes entre fontes).
      2. Varre cada fonte com seus próprios filtros; rebaseia o caminho relativo
         à raiz comum; UNE os candidatos e DEDUPLICA por caminho real (nenhum
         arquivo entra duas vezes, mesmo que duas fontes o aceitem).
      3. Roda a renomeação à prova de colisão sobre o conjunto unido, usando os
         parâmetros de nomeação da fonte PRIMÁRIA (mode/sep globais).
      4. Agrega pulados/avisos de todas as fontes.
    """
    if not sources:
        raise ValueError("Nenhuma fonte fornecida.")

    roots: list[Path] = []
    for s in sources:
        rp = Path(s.root).resolve()
        if not rp.is_dir():
            raise NotADirectoryError(f"Pasta raiz não encontrada: {rp}")
        roots.append(rp)

    # Raiz comum: base dos caminhos relativos no manifesto. Em fonte única é a
    # própria raiz (comportamento idêntico ao de antes).
    if len(roots) == 1:
        common = roots[0]
    else:
        try:
            common = Path(os.path.commonpath([str(r) for r in roots]))
            if not common.is_dir():
                common = roots[0]
        except ValueError:  # drives diferentes no Windows (C: vs D:)
            common = roots[0]

    primary_cfg = sources[0].cfg
    all_candidates: list[tuple[Path, PurePath, int]] = []
    seen_src: set[str] = set()  # dedup por caminho real (case-insensitive no Win)
    skipped_total: dict[str, int] = {}
    samples_total: dict[str, list[str]] = {}
    warnings: list[str] = []

    skipped_items_total: list[tuple[str, str]] = []
    for s, rp in zip(sources, roots):
        cands, skipped, samples, warns, skipped_items = _scan(rp, s.cfg)
        skipped_items_total += skipped_items
        for src, rel_src, size in cands:
            key = os.path.normcase(str(src))
            if key in seen_src:
                continue
            seen_src.add(key)
            # rebaseia o relativo para a raiz comum (cai no relativo da fonte se
            # o arquivo não estiver sob a comum — ex.: cross-drive degradado).
            try:
                rel_common = PurePath(src.relative_to(common).as_posix())
            except ValueError:
                rel_common = rel_src
            all_candidates.append((src, rel_common, size))
        for k, v in skipped.items():
            skipped_total[k] = skipped_total.get(k, 0) + v
            bucket = samples_total.setdefault(k, [])
            for ex in samples.get(k, []):
                if len(bucket) < 8:
                    bucket.append(ex)
        warnings += warns

    # spec0013: incluir o nome da pasta-raiz no sufixo (só fullpath + fonte única).
    root_prefix: str | None = None
    if primary_cfg.root_in_name:
        if primary_cfg.mode != "fullpath":
            warnings.append(
                "Opção 'incluir pasta-raiz no nome' só vale no modo fullpath — "
                "ignorada neste modo."
            )
        elif len(sources) > 1:
            warnings.append(
                "Opção 'incluir pasta-raiz no nome' foi ignorada: com múltiplas "
                "fontes o caminho já parte da raiz comum. (Multi-raiz é tarefa futura.)"
            )
        elif common.name:
            root_prefix = common.name

    planned, collisions, name_warnings = _plan_names(
        all_candidates, primary_cfg, root_prefix=root_prefix
    )
    warnings += name_warnings

    # FIX-001: pasta inteira engolida pelo .gitignore é fácil de não perceber
    # (o conteúdo nem é varrido) — então vira um aviso de primeira classe.
    pruned_gi = skipped_total.get("gitignore (pasta)", 0)
    if pruned_gi:
        ex = ", ".join(samples_total.get("gitignore (pasta)", [])[:4])
        more = " …" if pruned_gi > 4 else ""
        warnings.append(
            f".gitignore pulou {pruned_gi} pasta(s) INTEIRA(s): {ex}{more} — "
            "o conteúdo delas nem foi varrido. Se você precisa desses arquivos, "
            "desative a leitura do .gitignore (os ignores embutidos continuam ativos)."
        )
    if any(s.cfg.use_gitignore for s in sources) and not HAS_PATHSPEC:
        warnings.append(
            "pathspec não instalado: .gitignore ignorado nesta execução "
            "(usando só os ignores embutidos). Instale com: pip install pathspec"
        )

    planned.sort(key=lambda f: f.rel.as_posix().lower())
    descs = [_describe_source(rp, s.cfg) for s, rp in zip(sources, roots)]
    return FlattenPlan(
        root=common,
        files=planned,
        skipped=skipped_total,
        skipped_samples=samples_total,
        collisions=collisions,
        warnings=warnings,
        sources=descs,
        skipped_items=skipped_items_total,
    )


def is_our_folder(dest: Path) -> bool:
    """True se a pasta de destino foi criada pelo FlatDrop (tem manifesto nosso)."""
    mani = dest / C.MANIFEST_NAME
    if not mani.is_file():
        return False
    try:
        first = mani.read_text(encoding="utf-8", errors="ignore").splitlines()[:1]
    except OSError:
        return False
    return bool(first) and first[0].strip() == C.MANIFEST_SIGNATURE


def safe_clear(dest: Path) -> bool:
    """Limpa a pasta de destino SOMENTE se for vazia ou comprovadamente nossa.

    Nunca apaga uma pasta de terceiros. Devolve True se limpou de fato.
    Recusa-se a limpar se houver subpastas inesperadas (saída nossa é plana).
    """
    if not dest.exists():
        return False
    entries = list(dest.iterdir())
    if not entries:
        return False
    if any(e.is_dir() for e in entries):
        raise RuntimeError(
            "Destino tem subpastas inesperadas; não vou limpar por segurança."
        )
    if not is_our_folder(dest):
        raise RuntimeError(
            "Destino não-vazio e não foi criado pelo FlatDrop; não vou limpar."
        )
    for e in entries:
        e.unlink()
    return True


def _resolve_dest(dest: Path, cfg: ScanConfig) -> tuple[Path, bool, list[str]]:
    """Decide a pasta de destino final e se ela foi (ou será) limpa.

    - Não existe -> usa, cria.
    - Nossa + clear_dest -> limpa e reusa (mesma pasta sempre; ideal p/ arrastar).
    - Nossa + sem clear  -> mescla (arquivos antigos podem sobrar).
    - De terceiros (não-vazia) -> NUNCA mexe; cria variante numerada.
    """
    warnings: list[str] = []
    if not dest.exists() or not any(dest.iterdir()):
        return dest, False, warnings
    if is_our_folder(dest):
        if cfg.clear_dest:
            cleared = safe_clear(dest)
            return dest, cleared, warnings
        warnings.append("Reusando pasta existente sem limpar; arquivos antigos podem sobrar.")
        return dest, False, warnings
    # pasta de terceiros: não clobberar
    base = dest
    i = 2
    while dest.exists() and any(dest.iterdir()):
        dest = base.with_name(f"{base.name} ({i})")
        i += 1
    warnings.append(
        f"Destino original já existia e não é do FlatDrop; usando '{dest.name}'."
    )
    return dest, False, warnings


def write_manifest(dest: Path, plan: FlattenPlan, cfg: ScanConfig) -> Path:
    """Escreve _MANIFEST.md: assinatura + metadados + mapa origem→nome plano.

    O manifesto devolve ao Claude a estrutura que o achatamento desfez.
    """
    lines: list[str] = [C.MANIFEST_SIGNATURE]
    lines.append(f"# Manifesto FlatDrop — {plan.root.name}\n")
    # Origem: uma linha simples para fonte única; lista quando há multi-fonte.
    if len(plan.sources) <= 1:
        origem = plan.sources[0] if plan.sources else f"`{plan.root}`"
        lines.append(f"- **Origem:** {origem}")
    else:
        lines.append(f"- **Raiz comum:** `{plan.root}`")
        lines.append(f"- **Fontes ({len(plan.sources)}):**")
        for d in plan.sources:
            lines.append(f"  - {d}")
    lines.append(f"- **Gerado em:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"- **Modo de renomeação:** {cfg.mode} · separador `{cfg.sep}`")
    lines.append(f"- **Arquivos:** {len(plan.files)}")
    lines.append(f"- **Tamanho total:** {human_size(plan.total_bytes)}")
    lines.append(f"- **Tokens (estimativa grosseira ~4 B/token):** ~{plan.est_tokens:,}")
    lines.append("")
    lines.append("> Os arquivos foram achatados nesta pasta para upload no Projeto do Claude.")
    lines.append("> A tabela abaixo mapeia cada nome plano de volta ao seu caminho original.\n")
    lines.append("| Caminho original | Nome na pasta |")
    lines.append("|---|---|")
    for f in plan.files:
        lines.append(f"| `{f.rel.as_posix()}` | `{f.target}` |")
    lines.append("")
    mani = dest / C.MANIFEST_NAME
    mani.write_text("\n".join(lines), encoding="utf-8")
    return mani


# Mapa motivo-interno -> rotulo curto ASCII exibido no _TREE.md.
_TREE_REASON_LABEL = {
    "gitignore": "gitignore",
    "gitignore (pasta)": "gitignore",
    "flatdropignore": "flatdropignore",
    "flatdropignore (pasta)": "flatdropignore",
    "ignore_padrão": "embutido",
    "ignore_padrão (pasta)": "embutido",
    "tipo": "tipo",
    "sensível": "sensivel",
    "filtro (pasta)": "filtro",
}


def _tree_label(reason: str) -> str:
    """Rotulo ASCII curto do motivo, para a arvore. Desconhecido cai em si mesmo."""
    return _TREE_REASON_LABEL.get(reason, reason)


def _tree_node() -> dict:
    return {"children": {}, "files": [], "collapsed": None, "skipped": []}


def _tree_get_node(root_node: dict, parts: tuple[str, ...]) -> dict:
    node = root_node
    for p in parts:
        node = node["children"].setdefault(p, _tree_node())
    return node


def _tree_render(node: dict, indent: int, mode: str, lines: list[str]) -> None:
    """Renderiza um nó da árvore em memória (sem tocar disco), ordenado e estável."""
    entries: list[tuple[str, str, str, object]] = []
    for name, child in node["children"].items():
        entries.append((name.lower(), "dir", name, child))
    for name, target in node["files"]:
        entries.append((name.lower(), "file", name, target))
    if mode == "full":
        for name, label in node["skipped"]:
            entries.append((name.lower(), "skipped", name, label))
    entries.sort(key=lambda e: e[0])

    prefix = "  " * indent
    for _, kind, name, data in entries:
        if kind == "dir":
            if data["collapsed"]:
                lines.append(f"{prefix}{name}/  [ignorada: {data['collapsed']}]")
            else:
                lines.append(f"{prefix}{name}/")
                _tree_render(data, indent + 1, mode, lines)
        elif kind == "file":
            if data:
                lines.append(f"{prefix}{name}  [renomeado: {data}]")
            else:
                lines.append(f"{prefix}{name}")
        else:  # "skipped" — só aparece no modo full (folha por arquivo)
            lines.append(f"{prefix}{name}  [pulado: {data}]")

    if mode == "summary" and node["skipped"]:
        counts: dict[str, int] = {}
        for _, label in node["skipped"]:
            counts[label] = counts.get(label, 0) + 1
        agg = ", ".join(f"{label} x{n}" for label, n in sorted(counts.items()))
        lines.append(f"{prefix}[pulados: {agg}]")


def write_tree(dest: Path, plan: FlattenPlan, cfg: ScanConfig) -> Path:
    """Escreve _TREE.md: arvore indentada da origem (copiados + pulados + pastas
    colapsadas), com o motivo de cada exclusao. Par visual do .flatdropignore.

    Nao lista o interior de pasta ignorada (colapso em uma linha, sem recursao).
    O nivel de detalhe dos arquivos pulados soltos segue cfg.tree_skipped
    ("summary" agrega por pasta; "full" mostra folha a folha).

    A arvore e montada a partir de plan.files (copiados) e plan.skipped_items
    (pulados, ja em memoria) — nenhuma nova varredura de disco.
    """
    folder_items = [(rel, reason) for rel, reason in plan.skipped_items if rel.endswith("/")]
    file_items = [(rel, reason) for rel, reason in plan.skipped_items if not rel.endswith("/")]

    root_node = _tree_node()

    # Pastas colapsadas: uma entrada cada, sem interior.
    for rel, reason in folder_items:
        parts = rel[:-1].split("/")
        parent = _tree_get_node(root_node, tuple(parts[:-1]))
        parent["children"][parts[-1]] = {
            "children": {},
            "files": [],
            "collapsed": _tree_label(reason),
            "skipped": [],
        }

    # Arquivos copiados (com rename, se houve).
    for f in plan.files:
        parts = f.rel.parent.parts if f.rel.parent.as_posix() != "." else ()
        node = _tree_get_node(root_node, parts)
        node["files"].append((f.rel.name, f.target if f.renamed else None))

    # Arquivos pulados soltos (fora de pasta colapsada, que nunca é varrida).
    for rel, reason in file_items:
        p = PurePath(rel)
        parts = p.parent.parts if p.parent.as_posix() != "." else ()
        node = _tree_get_node(root_node, parts)
        node["skipped"].append((p.name, _tree_label(reason)))

    n_copied = len(plan.files)
    n_skipped = len(file_items)
    n_ignored_dirs = len(folder_items)

    lines: list[str] = [C.TREE_SIGNATURE]
    lines.append(f"# Arvore FlatDrop — {plan.root.name}\n")
    if len(plan.sources) <= 1:
        origem = plan.sources[0] if plan.sources else f"`{plan.root}`"
        lines.append(f"- Origem: {origem}")
    else:
        lines.append(f"- Raiz comum: `{plan.root}`")
    lines.append(f"- Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"- Copiados: {n_copied} · Pulados: {n_skipped} · Pastas ignoradas: {n_ignored_dirs}")
    lines.append("- Legenda: [copiado] · [renomeado: nome-plano] · [pulado: MOTIVO] · [ignorada: MOTIVO]")
    lines.append("")
    lines.append(f"{plan.root.name}/")
    _tree_render(root_node, 1, cfg.tree_skipped, lines)
    lines.append("")

    tree = dest / C.TREE_NAME
    tree.write_text("\n".join(lines), encoding="utf-8")
    return tree


def execute_plan(plan: FlattenPlan, dest: str | os.PathLike, cfg: ScanConfig) -> ExecuteResult:
    """Escreve em disco: resolve destino, (limpa se nosso), copia, gera manifesto."""
    dest_path = Path(dest)
    dest_path, cleared, warnings = _resolve_dest(dest_path, cfg)
    dest_path.mkdir(parents=True, exist_ok=True)

    copied = 0
    for f in plan.files:
        try:
            shutil.copy2(f.src, dest_path / f.target)
            copied += 1
        except OSError as exc:
            warnings.append(f"Falha ao copiar {f.rel.as_posix()}: {exc}")

    mani_path = write_manifest(dest_path, plan, cfg) if cfg.write_manifest else None
    if cfg.write_tree:
        try:
            write_tree(dest_path, plan, cfg)
        except OSError as exc:
            warnings.append(f"Falha ao gravar _TREE.md: {exc}")
    return ExecuteResult(
        dest=dest_path,
        copied=copied,
        manifest_path=mani_path,
        cleared=cleared,
        warnings=warnings,
    )


# --------------------------------------------------------------------------- #
# Utilidades
# --------------------------------------------------------------------------- #
def human_size(num: int) -> str:
    """Formata bytes em unidade legível (KB/MB...)."""
    size = float(num)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


def _windows_downloads() -> Path | None:  # pragma: no cover - só roda no Windows
    """Local REAL da pasta Downloads no Windows via Known Folder API.

    Necessário porque Downloads é uma 'Known Folder' que o usuário pode ter
    movido para outro disco (Propriedades → Local), redirecionado por política
    ou pelo OneDrive. Nesses casos `home/Downloads` não existe e o fallback
    ingênuo caía na home (bug observado). Usa ctypes (stdlib), sem dependência.
    """
    try:
        import ctypes
        from ctypes import wintypes

        class GUID(ctypes.Structure):
            _fields_ = [
                ("Data1", wintypes.DWORD),
                ("Data2", wintypes.WORD),
                ("Data3", wintypes.WORD),
                ("Data4", ctypes.c_ubyte * 8),
            ]

        # FOLDERID_Downloads = {374DE290-123F-4565-9164-39C4925E467B}
        folderid = GUID(
            0x374DE290, 0x123F, 0x4565,
            (ctypes.c_ubyte * 8)(0x91, 0x64, 0x39, 0xC4, 0x92, 0x5E, 0x46, 0x7B),
        )
        ptr = ctypes.c_wchar_p()
        res = ctypes.windll.shell32.SHGetKnownFolderPath(
            ctypes.byref(folderid), 0, None, ctypes.byref(ptr)
        )
        try:
            if res != 0 or not ptr.value:
                return None
            p = Path(ptr.value)
        finally:
            ctypes.windll.ole32.CoTaskMemFree(ptr)
        return p if p.is_dir() else None
    except Exception:
        return None


def _xdg_downloads() -> Path | None:
    """Local da pasta Downloads no Linux/BSD respeitando o XDG user-dirs."""
    env = os.environ.get("XDG_DOWNLOAD_DIR")
    if env:
        p = Path(os.path.expandvars(env))
        if p.is_dir():
            return p
    cfg = Path.home() / ".config" / "user-dirs.dirs"
    if cfg.is_file():
        try:
            for line in cfg.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = line.strip()
                if line.startswith("XDG_DOWNLOAD_DIR"):
                    val = line.split("=", 1)[1].strip().strip('"')
                    val = val.replace("$HOME", str(Path.home()))
                    p = Path(val)
                    if p.is_dir():
                        return p
        except OSError:
            return None
    return None


def default_downloads_dir() -> Path:
    """Pasta Downloads do usuário (multiplataforma), resolvendo o local REAL.

    No Windows consulta a Known Folder (pode estar movida de disco); no Linux
    respeita o XDG; no macOS usa ~/Downloads. Só cai na home como último recurso
    quando nada disso resolve — antes o fallback disparava cedo demais e a saída
    ia parar na raiz do perfil em vez do Downloads (bug corrigido).
    """
    if sys.platform.startswith("win"):
        p = _windows_downloads()
        if p:
            return p
    elif sys.platform != "darwin":  # Linux/BSD
        p = _xdg_downloads()
        if p:
            return p
    home = Path.home()
    dl = home / "Downloads"
    return dl if dl.is_dir() else home
