"""Banner publication plans and the files owned by automation."""

from dataclasses import dataclass

from ..identity import BannerIdentity

BANNER_START = "<!-- wisent-banner:start -->"
BANNER_END = "<!-- wisent-banner:end -->"
BANNER_PATH = "assets/readme-banner.webp"
SVG_PATH = "assets/readme-banner.svg"
CONFIG_PATH = ".github/banner.toml"
SIGNALS_START = "<!-- wisent-readme-signals:start -->"
LEGACY_BANNER_PATH = "banner.png"
SIGNALS_END = "<!-- wisent-readme-signals:end -->"


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
