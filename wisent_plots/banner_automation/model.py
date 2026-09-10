"""Banner publication plans and the files owned by automation."""

from dataclasses import dataclass
from typing import Optional

from ..identity import BannerIdentity

BANNER_START = "<!-- wisent-banner:start -->"
BANNER_END = "<!-- wisent-banner:end -->"
BANNER_PATH = "assets/readme-banner.webp"
SVG_PATH = "assets/readme-banner.svg"
CONFIG_PATH = ".github/banner.toml"
SIGNALS_START = "<!-- wisent-readme-signals:start -->"
LEGACY_BANNER_PATH = "banner.png"
SIGNALS_END = "<!-- wisent-readme-signals:end -->"
AUDIT_IGNORE_PATH = ".tama/violations-ignore"
AUDIT_DECLARATION = (
    "# Written by the wisent-visuals banner bot. The banner below is rendered\n"
    "# from .github/banner.toml and replaced whole on every run, so a repository\n"
    "# audit reads it as generated output instead of asking somebody to split it.\n"
    f"{SVG_PATH}\n"
)


def audit_declaration(existing: Optional[str]) -> Optional[str]:
    """The declaration file to write, or None when the repository already says this.

    A repository declares more than banners here — generated distributions, a
    root whose files are fixed by a packager — so an existing file is appended
    to, never replaced.
    """
    if existing is None:
        return AUDIT_DECLARATION
    if any(line.strip() == SVG_PATH for line in existing.splitlines()):
        return None
    body = existing if existing.endswith("\n") else f"{existing}\n"
    return body + AUDIT_DECLARATION


@dataclass(frozen=True)
class RepositoryPlan:
    """A banner update ready to render and submit."""

    owner: str
    name: str
    default_branch: str
    identity: BannerIdentity
    readme: str
    reason: str
    manage_banner: bool
    empty: bool
    remove_legacy_banner: bool = False
    audit_ignore: Optional[str] = None
