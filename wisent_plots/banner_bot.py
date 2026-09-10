"""Organization-wide GitHub bot for personalized Wisent README banners."""

from __future__ import annotations

from .banner_automation.cli import main
from .banner_automation.engine import BannerBot
from .banner_automation.github import GitHubClient
from .banner_automation.model import RepositoryPlan
from .banner_automation.readme import update_readme

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = ["BannerBot", "GitHubClient", "RepositoryPlan", "main", "update_readme"]
