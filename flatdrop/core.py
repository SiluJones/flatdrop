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


def _build_gitignore_spec(root: Path, cfg: ScanConfig):
    """Lê .gitignore da raiz e devolve um matcher pathspec (ou None)."""
    if not (cfg.use_gitignore and HAS_PATHSPEC):
        return None
    gi = root / ".gitignore"
    if not gi.is_file():
        return None
    try:
        lines = gi.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return None
    # "gitignore" é o factory novo; "gitwildmatch" o antigo (depreciado).
    # Tenta o novo primeiro p/ evitar warning; cai no antigo em versões velhas.
    for factory in ("gitignore", "gitwildmatch"):
        try:
            return pathspec.PathSpec.from_lines(factory, lines)
        except Exception:  # nome de factory não registrado nesta versão
            continue
    return None


# --------------------------------------------------------------------------- #
# Varredura
# --------------------------------------------------------------------------- #
def _scan(root: Path, cfg: ScanConfig) -> tuple[list[tuple[Path, PurePath, int]], dict, dict, list]:
    """Percorre a árvore e separa candidatos de pulados.

    Devolve (candidatos, skipped_counts, skipped_samples, warnings).
    candidato = (src_abs, rel_posix, size_bytes).
    """
    spec = _build_gitignore_spec(root, cfg)
    candidates: list[tuple[Path, PurePath, int]] = []
    skipped: dict[str, int] = {
        "gitignore": 0,
        "gitignore (pasta)": 0,
        "tipo": 0,
        "sensível": 0,
        "filtro (pasta)": 0,
        "ignore_padrão": 0,
        "ignore_padrão (pasta)": 0,
    }
    samples: dict[str, list[str]] = {k: [] for k in skipped}
    warnings: list[str] = []

    def note(reason: str, rel: str) -> None:
        skipped[reason] += 1
        if len(samples[reason]) < 8:
            samples[reason].append(rel)

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
            if spec is not None and spec.match_file(rel_sub + "/"):
                note("gitignore (pasta)", rel_sub + "/")
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
            if spec is not None and spec.match_file(rel_str):
                note("gitignore", rel_str)
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

    return candidates, skipped, samples, warnings


# --------------------------------------------------------------------------- #
# Renomeação à prova de colisão (o coração)
# --------------------------------------------------------------------------- #
def _plan_names(
    candidates: list[tuple[Path, PurePath, int]], cfg: ScanConfig
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

    for s, rp in zip(sources, roots):
        cands, skipped, samples, warns = _scan(rp, s.cfg)
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

    planned, collisions, name_warnings = _plan_names(all_candidates, primary_cfg)
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
