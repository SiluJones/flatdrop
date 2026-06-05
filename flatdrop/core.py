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
    """True se a extensão (ou o nome, p/ extensionless) está na allowlist."""
    low = name.lower()
    if low in cfg.extensionless_allow:
        return True
    _, ext = split_name(name)
    if not ext:
        return False
    return ext[1:].lower() in cfg.extensions


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
    skipped: dict[str, int] = {"gitignore": 0, "tipo": 0, "sensível": 0, "ignore_padrão": 0}
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
        kept = []
        for d in dirnames:
            if d in cfg.dir_ignores:
                continue
            rel_sub = (rel_dir / d).as_posix()
            if spec is not None and spec.match_file(rel_sub + "/"):
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
            # 3) tipo aceito?
            if not is_allowed_type(fn, cfg):
                note("tipo", rel_str)
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
    """Pré-visualização: varre a raiz e calcula nomes, SEM escrever nada."""
    root_path = Path(root).resolve()
    if not root_path.is_dir():
        raise NotADirectoryError(f"Pasta raiz não encontrada: {root_path}")

    candidates, skipped, samples, warnings = _scan(root_path, cfg)
    planned, collisions, name_warnings = _plan_names(candidates, cfg)
    warnings += name_warnings
    if cfg.use_gitignore and not HAS_PATHSPEC:
        warnings.append(
            "pathspec não instalado: .gitignore ignorado nesta execução "
            "(usando só os ignores embutidos). Instale com: pip install pathspec"
        )
    # ordena por caminho de origem (leitura natural)
    planned.sort(key=lambda f: f.rel.as_posix().lower())
    return FlattenPlan(
        root=root_path,
        files=planned,
        skipped=skipped,
        skipped_samples=samples,
        collisions=collisions,
        warnings=warnings,
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
    lines.append(f"- **Origem:** `{plan.root}`")
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


def default_downloads_dir() -> Path:
    """Pasta Downloads do usuário (multiplataforma, com fallback)."""
    home = Path.home()
    dl = home / "Downloads"
    return dl if dl.is_dir() else home
