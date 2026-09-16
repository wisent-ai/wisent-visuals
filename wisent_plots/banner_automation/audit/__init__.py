"""Declaring already-published banners to a repository audit, locally.

The bot writes `.tama/violations-ignore` whenever it publishes a banner, so a
repository audit reads the rendered SVG as generated output. Banners published
before that behaviour existed carry no declaration, and the bot only revisits
a repository when its banner changes — so those repositories would keep
failing an audit over a file nobody wrote by hand.

This walks local checkouts instead of the GitHub API: no token, no network,
and the same declaration text the publisher uses. It commits and pushes the
file it wrote, because the publisher's own path commits: a declaration that
lives only in a working tree is a declaration the next clone does not have.
"""

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, List, Optional

from ..model import AUDIT_IGNORE_PATH, SVG_PATH, audit_declaration

GIT_DIR = ".git"
COMMIT_SUBJECT = "docs: declare the published banner to the repository audit"
COMMIT_BODY = (
    "The banner SVG is rendered from .github/banner.toml and replaced whole on "
    "every run, so the audit reads it as generated output instead of asking "
    "somebody to split a file nobody wrote by hand."
)


@dataclass(frozen=True)
class Declaration:
    """What one checkout needed, and what was done about it."""

    repository: Path
    wrote: bool
    reason: str
    revision: str = ""


def checkouts(root: Path) -> Iterator[Path]:
    """Every checkout directly under `root`, plus `root` itself when it is one."""
    if root.joinpath(GIT_DIR).exists():
        yield root
    if not root.is_dir():
        return
    for entry in sorted(root.iterdir()):
        if entry == root or not entry.is_dir():
            continue
        if entry.joinpath(GIT_DIR).exists():
            yield entry


def _existing(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def _git(repository: Path, *arguments: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(repository), *arguments],
        capture_output=True,
        text=True,
        check=False,
    )


def _revision(repository: Path) -> str:
    finished = _git(repository, "rev-parse", "--short", "HEAD")
    return finished.stdout.strip() if finished.returncode == 0 else ""


def _record(repository: Path, push: bool) -> Declaration:
    """Commit the declaration, and push it when asked."""
    staged = _git(repository, "add", AUDIT_IGNORE_PATH)
    if staged.returncode != 0:
        return Declaration(repository, True, f"written, not staged: {staged.stderr.strip()}")
    committed = _git(repository, "commit", "-q", "-m", COMMIT_SUBJECT, "-m", COMMIT_BODY)
    if committed.returncode != 0:
        detail = (committed.stderr or committed.stdout).strip().splitlines()
        return Declaration(
            repository,
            True,
            f"written, not committed: {detail[0] if detail else 'commit refused'}",
        )
    revision = _revision(repository)
    if not push:
        return Declaration(repository, True, "declared and committed", revision)
    pushed = _git(repository, "push", "-q", "origin", "HEAD")
    if pushed.returncode != 0:
        detail = (pushed.stderr or pushed.stdout).strip().splitlines()
        return Declaration(
            repository,
            True,
            f"committed, not pushed: {detail[0] if detail else 'push refused'}",
            revision,
        )
    return Declaration(repository, True, "declared, committed and pushed", revision)


def declare(repository: Path, apply: bool, commit: bool = False, push: bool = False) -> Declaration:
    """Declare this checkout's published banner to its audit."""
    banner = repository.joinpath(SVG_PATH)
    if not banner.is_file():
        return Declaration(repository, False, "no published banner")
    target = repository.joinpath(AUDIT_IGNORE_PATH)
    declaration = audit_declaration(_existing(target))
    if declaration is None:
        return Declaration(repository, False, "already declared")
    if not apply:
        return Declaration(repository, False, "would declare the banner")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(declaration, encoding="utf-8")
    if not commit:
        return Declaration(repository, True, "declared the banner")
    return _record(repository, push)


def declare_tree(
    root: Path,
    apply: bool,
    commit: bool = False,
    push: bool = False,
) -> List[Declaration]:
    """Declare every checkout under `root` that needs it."""
    return [declare(repository, apply, commit, push) for repository in checkouts(root)]
