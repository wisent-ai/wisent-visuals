"""Organization-wide GitHub bot for personalized Wisent README banners."""

from __future__ import annotations

import argparse
import base64
import io
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

from .banner import Banner
from .repository_profile import BannerIdentity, RepositoryProfile, generate_identity

try:
    import tomllib
except ImportError:  # pragma: no cover - exercised on Python 3.8-3.10
    import tomli as tomllib


BANNER_START = "<!-- wisent-banner:start -->"
BANNER_END = "<!-- wisent-banner:end -->"
BANNER_PATH = "assets/readme-banner.webp"
SVG_PATH = "assets/readme-banner.svg"
CONFIG_PATH = ".github/banner.toml"


@dataclass(frozen=True)
class RepositoryPlan:
    """A banner update ready to render and submit."""

    owner: str
    name: str
    default_branch: str
    identity: BannerIdentity
    readme: str
    reason: str


class GitHubClient:
    """Small GitHub REST client with explicit read and mutation operations."""

    def __init__(self, token: str = "", api_url: str = "https://api.github.com"):
        self.token = token
        self.api_url = api_url.rstrip("/")

    def request(
        self,
        method: str,
        path: str,
        payload: Optional[Mapping[str, Any]] = None,
        allow_missing: bool = False,
    ) -> Any:
        url = f"{self.api_url}{path}"
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "wisent-banner-bot/0.2.0",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        request = urllib.request.Request(url, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read()
                return json.loads(body) if body else None
        except urllib.error.HTTPError as error:
            if allow_missing and error.code == 404:
                return None
            detail = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"GitHub {method} {path} failed ({error.code}): {detail}") from error

    def list_repositories(self, organization: str) -> Iterable[Mapping[str, Any]]:
        page = 1
        while True:
            query = urllib.parse.urlencode(
                {
                    "type": "all",
                    "sort": "created",
                    "direction": "desc",
                    "per_page": 100,
                    "page": page,
                }
            )
            repositories = self.request("GET", f"/orgs/{organization}/repos?{query}")
            yield from repositories
            if len(repositories) < 100:
                return
            page += 1

    def read_content(
        self, owner: str, repository: str, path: str, ref: str
    ) -> Optional[Tuple[bytes, str]]:
        encoded_path = urllib.parse.quote(path, safe="/")
        query = urllib.parse.urlencode({"ref": ref})
        result = self.request(
            "GET",
            f"/repos/{owner}/{repository}/contents/{encoded_path}?{query}",
            allow_missing=True,
        )
        if result is None:
            return None
        return base64.b64decode(result["content"]), result["sha"]

    def ensure_branch(self, owner: str, repository: str, default_branch: str, branch: str) -> None:
        encoded_branch = urllib.parse.quote(branch, safe="")
        existing = self.request(
            "GET",
            f"/repos/{owner}/{repository}/git/ref/heads/{encoded_branch}",
            allow_missing=True,
        )
        if existing is not None:
            return
        encoded_default = urllib.parse.quote(default_branch, safe="")
        source = self.request("GET", f"/repos/{owner}/{repository}/git/ref/heads/{encoded_default}")
        self.request(
            "POST",
            f"/repos/{owner}/{repository}/git/refs",
            {"ref": f"refs/heads/{branch}", "sha": source["object"]["sha"]},
        )

    def write_content(
        self,
        owner: str,
        repository: str,
        path: str,
        branch: str,
        content: bytes,
        message: str,
        current_sha: str = "",
    ) -> None:
        payload: Dict[str, Any] = {
            "message": message,
            "content": base64.b64encode(content).decode("ascii"),
            "branch": branch,
        }
        if current_sha:
            payload["sha"] = current_sha
        encoded_path = urllib.parse.quote(path, safe="/")
        self.request("PUT", f"/repos/{owner}/{repository}/contents/{encoded_path}", payload)

    def open_pull_request(
        self,
        owner: str,
        repository: str,
        branch: str,
        default_branch: str,
        identity: BannerIdentity,
    ) -> str:
        query = urllib.parse.urlencode(
            {"state": "open", "head": f"{owner}:{branch}", "base": default_branch}
        )
        existing = self.request("GET", f"/repos/{owner}/{repository}/pulls?{query}")
        if existing:
            return existing[0]["html_url"]
        result = self.request(
            "POST",
            f"/repos/{owner}/{repository}/pulls",
            {
                "title": "Add personalized Wisent README banner",
                "head": branch,
                "base": default_branch,
                "body": (
                    "Adds a banner generated from the repository description, topics, language, "
                    f"and README. Semantic family: `{identity.category}`.\n\n"
                    "The committed image is deterministic and remains editable through "
                    f"`{CONFIG_PATH}`."
                ),
            },
        )
        return result["html_url"]


def _readme_excerpt(readme: str) -> str:
    text = re.sub(r"```.*?```", " ", readme, flags=re.DOTALL)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    for paragraph in re.split(r"\n\s*\n", text):
        cleaned = re.sub(r"!?(?:\[[^]]*\])?\([^)]*\)", " ", paragraph)
        cleaned = re.sub(r"^[#>*\-\s]+", "", cleaned).strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        if len(cleaned) >= 24 and not cleaned.startswith("http"):
            return cleaned[:240]
    return ""


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


def _has_manual_banner(readme: str) -> bool:
    if BANNER_START in readme:
        return False
    return (
        re.search(r"(?:src=|!\[[^]]*\]\()[^\n)]*banner\.(?:png|webp|svg)", readme, re.I) is not None
    )


def update_readme(readme: str, repository_name: str) -> str:
    """Insert or replace only the bot-owned README banner block."""
    if _has_manual_banner(readme):
        return readme
    block = "\n".join(
        [
            BANNER_START,
            '<p align="center">',
            f'  <img src="{BANNER_PATH}" alt="{repository_name} by Wisent" width="100%">',
            "</p>",
            BANNER_END,
        ]
    )
    if BANNER_START in readme and BANNER_END in readme:
        pattern = re.compile(re.escape(BANNER_START) + r".*?" + re.escape(BANNER_END), re.DOTALL)
        return pattern.sub(block, readme)

    if not readme.strip():
        return f"# {repository_name}\n\n{block}\n"

    signals = "<!-- wisent-readme-signals:end -->"
    if signals in readme:
        return readme.replace(signals, f"{signals}\n\n{block}", 1)

    heading = re.search(r"^# .+$", readme, flags=re.MULTILINE)
    if heading:
        end = heading.end()
        return f"{readme[:end]}\n\n{block}{readme[end:]}"
    return f"{block}\n\n{readme}"


class BannerBot:
    """Discover unmanaged repositories and open personalized banner PRs."""

    def __init__(self, client: GitHubClient, excluded: Set[str]):
        self.client = client
        self.excluded = excluded

    def plans(self, organization: str, limit: int = 0) -> Iterable[RepositoryPlan]:
        emitted = 0
        for repository in self.client.list_repositories(organization):
            name = repository["name"]
            if (
                name in self.excluded
                or repository.get("archived")
                or repository.get("disabled")
                or repository.get("fork")
            ):
                continue

            default_branch = repository["default_branch"]
            readme_file = self.client.read_content(organization, name, "README.md", default_branch)
            readme = "" if readme_file is None else readme_file[0].decode("utf-8", errors="replace")
            config = self.client.read_content(organization, name, CONFIG_PATH, default_branch)

            profile = RepositoryProfile(
                name=name,
                description=repository.get("description") or "",
                topics=tuple(repository.get("topics") or ()),
                language=repository.get("language") or "",
                readme_excerpt=_readme_excerpt(readme),
            )
            identity = generate_identity(profile)
            managed_fingerprint = _managed_fingerprint(config)
            if managed_fingerprint == identity.fingerprint:
                continue
            if not managed_fingerprint and _has_manual_banner(readme):
                continue
            if limit and emitted >= limit:
                return
            emitted += 1
            reason = "new repository" if config is None else "repository identity changed"
            yield RepositoryPlan(
                owner=organization,
                name=name,
                default_branch=default_branch,
                identity=identity,
                readme=readme,
                reason=reason,
            )

    def apply(self, plan: RepositoryPlan) -> str:
        branch = f"wisent-banner-bot/{plan.identity.fingerprint}"
        self.client.ensure_branch(plan.owner, plan.name, plan.default_branch, branch)
        banner = Banner(plan.identity.as_config())
        raster = io.BytesIO()
        banner.render_image().save(raster, "WEBP", quality=90, method=6, exact=True)
        files = {
            CONFIG_PATH: plan.identity.to_toml().encode("utf-8"),
            SVG_PATH: banner.render_svg().encode("utf-8"),
            BANNER_PATH: raster.getvalue(),
            "README.md": update_readme(plan.readme, plan.name).encode("utf-8"),
        }
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
                "chore: generate personalized README banner",
                current_sha,
            )
        return self.client.open_pull_request(
            plan.owner,
            plan.name,
            branch,
            plan.default_branch,
            plan.identity,
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="wisent-banner-bot")
    parser.add_argument("command", choices=("plan", "sync"))
    parser.add_argument("--org", default="wisent-ai")
    parser.add_argument("--exclude", action="append", default=["wisent"])
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--token-env", default="WISENT_BANNER_GITHUB_TOKEN")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    token = os.environ.get(args.token_env, "")
    if args.command == "sync" and not token:
        print(f"{args.token_env} must contain a GitHub App token for sync", file=sys.stderr)
        return 2

    bot = BannerBot(GitHubClient(token), set(args.exclude))
    plans = list(bot.plans(args.org, args.limit))
    for plan in plans:
        summary = {
            "repository": f"{plan.owner}/{plan.name}",
            "reason": plan.reason,
            "category": plan.identity.category,
            "title": plan.identity.title,
            "description": plan.identity.description,
            "layout": plan.identity.layout,
            "fingerprint": plan.identity.fingerprint,
        }
        if args.command == "plan":
            print(json.dumps(summary, ensure_ascii=False))
        else:
            summary["pull_request"] = bot.apply(plan)
            print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = ["BannerBot", "GitHubClient", "RepositoryPlan", "main", "update_readme"]
