"""Build repository-specific plans and publish through the GitHub client."""

import io
from typing import Iterable, Optional, Set, Tuple

from ..banner import Banner
from ..identity import RepositoryProfile, generate_identity
from .github import GitHubClient
from .model import (
    AUDIT_IGNORE_PATH,
    BANNER_PATH,
    CONFIG_PATH,
    LEGACY_BANNER_PATH,
    SVG_PATH,
    RepositoryPlan,
    audit_declaration,
)
from .readme import _has_manual_banner, _opening_legacy_banner, _readme_excerpt, update_readme

try:
    import tomllib
except ImportError:  # Python 3.8-3.10
    import tomli as tomllib


def _managed_fingerprint(config: Optional[Tuple[bytes, str]]) -> str:
    if config is None:
        return ""
    try:
        document = tomllib.loads(config[0].decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError):
        return ""
    automation = document.get("automation", {})
    if automation.get("managed") is not True:
        return ""
    return str(automation.get("source_fingerprint", ""))


class BannerBot:
    """Discover repositories and publish personalized README presentation."""

    def __init__(
        self,
        client: GitHubClient,
        excluded: Set[str],
        included: Optional[Set[str]] = None,
    ):
        self.client = client
        self.excluded = excluded
        self.included = included

    def plans(self, organization: str, limit: int = 0) -> Iterable[RepositoryPlan]:
        emitted = 0
        for repository in self.client.list_repositories(organization):
            name = repository["name"]
            if (
                name in self.excluded
                or (self.included is not None and name not in self.included)
                or repository.get("archived")
                or repository.get("disabled")
                or repository.get("fork")
            ):
                continue

            default_branch = repository["default_branch"]
            readme_file = self.client.read_content(organization, name, "README.md", default_branch)
            readme = "" if readme_file is None else readme_file[0].decode("utf-8", errors="replace")
            config = self.client.read_content(organization, name, CONFIG_PATH, default_branch)
            declared = self.client.read_content(
                organization, name, AUDIT_IGNORE_PATH, default_branch
            )

            profile = RepositoryProfile(
                name=name,
                description=repository.get("description") or "",
                topics=tuple(repository.get("topics") or ()),
                language=repository.get("language") or "",
                readme_excerpt=_readme_excerpt(readme),
            )
            identity = generate_identity(profile)
            manage_banner = not _has_manual_banner(readme)
            remove_legacy_banner = _opening_legacy_banner(readme)
            managed_fingerprint = _managed_fingerprint(config)
            banner_current = managed_fingerprint == identity.fingerprint
            readme_current = (
                update_readme(
                    readme,
                    name,
                    organization,
                    identity.title if identity.copy_status == "approved" else "",
                )
                == readme
            )
            if readme_current and (not manage_banner or banner_current):
                continue
            if limit and emitted >= limit:
                return
            emitted += 1
            if not readme_current and (not manage_banner or banner_current):
                reason = "README buttons missing or stale"
            elif config is None:
                reason = "new repository"
            else:
                reason = "repository identity changed"
            yield RepositoryPlan(
                owner=organization,
                name=name,
                default_branch=default_branch,
                identity=identity,
                readme=readme,
                reason=reason,
                manage_banner=manage_banner,
                remove_legacy_banner=remove_legacy_banner,
                empty=readme_file is None and repository.get("size", 0) == 0,
                audit_ignore=None if declared is None else declared[0].decode("utf-8"),
            )

    def apply(self, plan: RepositoryPlan, direct: bool = False) -> str:
        files = {
            "README.md": update_readme(
                plan.readme,
                plan.name,
                plan.owner,
                plan.identity.title if plan.identity.copy_status == "approved" else "",
            ).encode("utf-8"),
        }
        if plan.manage_banner:
            banner = Banner(plan.identity.as_config())
            raster = io.BytesIO()
            banner.render_image().save(raster, "WEBP", quality=90, method=6, exact=True)
            declaration = audit_declaration(plan.audit_ignore)
            files.update(
                {
                    CONFIG_PATH: plan.identity.to_toml().encode("utf-8"),
                    SVG_PATH: banner.render_svg().encode("utf-8"),
                    BANNER_PATH: raster.getvalue(),
                }
            )
            if declaration is not None:
                files[AUDIT_IGNORE_PATH] = declaration.encode("utf-8")
        if plan.empty:
            return self.client.create_initial_commit(
                plan.owner,
                plan.name,
                plan.default_branch,
                files,
            )
        if direct:
            for path, content in files.items():
                existing = self.client.read_content(
                    plan.owner,
                    plan.name,
                    path,
                    plan.default_branch,
                )
                if existing is not None and existing[0] == content:
                    continue
                current_sha = "" if existing is None else existing[1]
                self.client.write_content(
                    plan.owner,
                    plan.name,
                    path,
                    plan.default_branch,
                    content,
                    "docs: add personalized README banner and buttons [skip ci]",
                    current_sha,
                )
            if plan.remove_legacy_banner:
                legacy = self.client.read_content(
                    plan.owner,
                    plan.name,
                    LEGACY_BANNER_PATH,
                    plan.default_branch,
                )
                if legacy is not None:
                    self.client.delete_content(
                        plan.owner,
                        plan.name,
                        LEGACY_BANNER_PATH,
                        plan.default_branch,
                        "docs: remove superseded README banner [skip ci]",
                        legacy[1],
                    )
            return f"https://github.com/{plan.owner}/{plan.name}"

        branch = f"wisent-readme-bot/{plan.identity.fingerprint}"
        self.client.ensure_branch(plan.owner, plan.name, plan.default_branch, branch)
        for path, content in files.items():
            existing = self.client.read_content(plan.owner, plan.name, path, branch)
            if existing is not None and existing[0] == content:
                continue
            current_sha = "" if existing is None else existing[1]
            self.client.write_content(
                plan.owner,
                plan.name,
                path,
                branch,
                content,
                "docs: add personalized README banner and buttons",
                current_sha,
            )
        if plan.remove_legacy_banner:
            legacy = self.client.read_content(
                plan.owner,
                plan.name,
                LEGACY_BANNER_PATH,
                branch,
            )
            if legacy is not None:
                self.client.delete_content(
                    plan.owner,
                    plan.name,
                    LEGACY_BANNER_PATH,
                    branch,
                    "docs: remove superseded README banner",
                    legacy[1],
                )
        return self.client.open_pull_request(
            plan.owner,
            plan.name,
            branch,
            plan.default_branch,
            plan.identity,
        )
