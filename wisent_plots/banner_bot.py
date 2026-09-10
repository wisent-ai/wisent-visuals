"""Organization-wide GitHub bot for personalized Wisent README banners."""

from __future__ import annotations

import argparse
import base64
import io
import json
import os
import re
import sys
import time
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
        for attempt in range(3):
            request = urllib.request.Request(url, data=data, method=method, headers=headers)
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    body = response.read()
                    return json.loads(body) if body else None
            except urllib.error.HTTPError as error:
                if allow_missing and error.code == 404:
                    return None
                if error.code in {500, 502, 503, 504} and attempt < 2:
                    error.close()
                    time.sleep(2**attempt)
                    continue
                detail = error.read().decode("utf-8", errors="replace")
                raise RuntimeError(
                    f"GitHub {method} {path} failed ({error.code}): {detail}"
                ) from error

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

    def clear_description(self, owner: str, repository: str) -> bool:
        """Clear one description identified by the versioned provenance audit."""
        current = self.request("GET", f"/repos/{owner}/{repository}", allow_missing=True)
        if current is None or not (current.get("description") or "").strip():
            return False
        self.request("PATCH", f"/repos/{owner}/{repository}", {"description": ""})
        return True
    def set_description(self, owner: str, repository: str, description: str) -> bool:
        """Synchronize one GitHub description with approved copy."""
        current = self.request("GET", f"/repos/{owner}/{repository}", allow_missing=True)
        if current is None or (current.get("description") or "") == description:
            return False
        self.request("PATCH", f"/repos/{owner}/{repository}", {"description": description})
        return True


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

    def delete_content(
        self,
        owner: str,
        repository: str,
        path: str,
        branch: str,
        message: str,
        current_sha: str,
    ) -> None:
        encoded_path = urllib.parse.quote(path, safe="/")
        self.request(
            "DELETE",
            f"/repos/{owner}/{repository}/contents/{encoded_path}",
            {"message": message, "sha": current_sha, "branch": branch},
        )


    def create_initial_commit(
        self,
        owner: str,
        repository: str,
        default_branch: str,
        files: Mapping[str, bytes],
    ) -> str:
        readme = files["README.md"]
        self.request(
            "PUT",
            f"/repos/{owner}/{repository}/contents/README.md",
            {
                "message": "docs: initialize README presentation [skip ci]",
                "content": base64.b64encode(readme).decode("ascii"),
            },
        )
        for path, content in files.items():
            if path == "README.md":
                continue
            self.write_content(
                owner,
                repository,
                path,
                default_branch,
                content,
                "docs: add personalized README banner [skip ci]",
            )
        return f"https://github.com/{owner}/{repository}"

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
                "title": "Add personalized Wisent README banner and buttons",
                "head": branch,
                "base": default_branch,
                "body": (
                    "Adds a deterministic banner generated from repository facts and a compact "
                    f"button strip linking to `{owner}/{repository}`, its issues, Wisent, "
                    "Discord, LinkedIn, X, and the enterprise contact route.\n\n"
                    "Bot-owned README markup is bounded by explicit comments. Generated banner "
                    f"assets remain editable through `{CONFIG_PATH}`."
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


def _opening_legacy_banner(readme: str) -> bool:
    return (
        re.match(
            r'\A\s*<p\b[^>]*>\s*<img\b[^>]*\bsrc=["\']banner\.png["\'][^>]*>\s*</p>\s*',
            readme,
            re.IGNORECASE,
        )
        is not None
    )


def _remove_opening_legacy_banner(readme: str) -> str:
    return re.sub(
        r'\A\s*<p\b[^>]*>\s*<img\b[^>]*\bsrc=["\']banner\.png["\'][^>]*>\s*</p>\s*',
        "",
        readme,
        count=1,
        flags=re.IGNORECASE,
    )


def _has_manual_banner(readme: str) -> bool:
    if BANNER_START in readme or _opening_legacy_banner(readme):
        return False
    return (
        re.search(r"(?:src=|!\[[^]]*\]\()[^\n)]*banner\.(?:png|webp|svg)", readme, re.I) is not None
    )


def _signals_block(owner: str, repository: str) -> str:
    encoded = urllib.parse.quote(repository, safe="")
    repository_url = f"https://github.com/{owner}/{encoded}"
    buttons = [
        (
            "Source",
            "https://img.shields.io/badge/GitHub-Source-181717?logo=github",
            repository_url,
        ),
        (
            "Issues",
            "https://img.shields.io/badge/GitHub-Issues-181717?logo=github",
            f"{repository_url}/issues",
        ),
        (
            "Wisent",
            "https://img.shields.io/badge/Wisent-Website-0B0B0B",
            "https://wisent.com",
        ),
        (
            "Discord",
            "https://img.shields.io/badge/Discord-Join-5865F2?logo=discord&logoColor=white",
            "https://discord.gg/qRjpkthq54",
        ),
        (
            "LinkedIn",
            "https://img.shields.io/badge/LinkedIn-Follow-0A66C2?logo=linkedin&logoColor=white",
            "https://www.linkedin.com/company/wisent-ai/",
        ),
        (
            "X",
            "https://img.shields.io/badge/X-Follow-000000?logo=x&logoColor=white",
            "https://x.com/wisentai",
        ),
        (
            "Enterprise",
            "https://img.shields.io/badge/Enterprise-Book%20a%20call-0B0B0B?logo=calendly",
            "https://calendly.com/lbartoszcze",
        ),
    ]
    row = " ".join(f"[![{label}]({image})]({target})" for label, image, target in buttons)
    return "\n".join((SIGNALS_START, row, SIGNALS_END))


def _remove_signals(readme: str) -> str:
    pattern = re.compile(
        re.escape(SIGNALS_START) + r".*?" + re.escape(SIGNALS_END),
        re.DOTALL,
    )
    match = pattern.search(readme)
    if match is None:
        return readme
    prefix = readme[: match.start()].rstrip("\n")
    suffix = readme[match.end() :].lstrip("\n")
    if prefix and suffix:
        return f"{prefix}\n\n{suffix}"
    if prefix:
        return prefix + ("\n" if readme.endswith("\n") else "")
    return suffix


def _insert_signals(readme: str, block: str) -> str:
    if BANNER_END in readme:
        position = readme.index(BANNER_END) + len(BANNER_END)
        prefix = readme[:position].rstrip("\n")
        suffix = readme[position:].lstrip("\n")
        return f"{prefix}\n\n{block}\n\n{suffix}"

    manual_patterns = (
        (r"<p\b[^>]*>.*?banner\.(?:png|webp|svg).*?</p>", re.IGNORECASE | re.DOTALL),
        (
            r"<picture\b[^>]*>.*?banner\.(?:png|webp|svg).*?</picture>",
            re.IGNORECASE | re.DOTALL,
        ),
        (
            r"^.*!\[[^]]*\]\([^)\n]*banner\.(?:png|webp|svg)[^)\n]*\).*$",
            re.IGNORECASE | re.MULTILINE,
        ),
    )
    for pattern, flags in manual_patterns:
        match = re.search(pattern, readme, flags)
        if match is not None:
            prefix = readme[: match.end()].rstrip("\n")
            suffix = readme[match.end() :].lstrip("\n")
            return f"{prefix}\n\n{block}\n\n{suffix}"
    return f"{block}\n\n{readme.lstrip()}"


def update_readme(
    readme: str,
    repository_name: str,
    owner: str = "wisent-ai",
    approved_title: str = "",
) -> str:
    """Keep generated presentation first and preserve approved product copy."""
    body = _remove_signals(readme)
    body = _remove_opening_legacy_banner(body)
    if not _has_manual_banner(body):
        block = "\n".join(
            [
                BANNER_START,
                '<p align="center">',
                f'  <img src="{BANNER_PATH}" alt="{repository_name} by Wisent" width="100%">',
                "</p>",
                BANNER_END,
            ]
        )
        if BANNER_START in body and BANNER_END in body:
            pattern = re.compile(
                re.escape(BANNER_START) + r".*?" + re.escape(BANNER_END),
                re.DOTALL,
            )
            body = pattern.sub("", body, count=1)
        body = body.lstrip("\n")
        if not body.strip():
            body = f"# {approved_title or repository_name}\n"
        body = f"{block}\n\n{body}"
    body = _insert_signals(body, _signals_block(owner, repository_name))
    if approved_title:
        heading = re.compile(r"^# .+$", re.MULTILINE)
        if heading.search(body):
            body = heading.sub(f"# {approved_title}", body, count=1)
        else:
            body = f"{body.rstrip()}\n\n# {approved_title}\n"
    return body


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
            readme_current = update_readme(
                readme,
                name,
                organization,
                identity.title if identity.copy_status == "approved" else "",
            ) == readme
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
            files.update(
                {
                    CONFIG_PATH: plan.identity.to_toml().encode("utf-8"),
                    SVG_PATH: banner.render_svg().encode("utf-8"),
                    BANNER_PATH: raster.getvalue(),
                }
            )
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="wisent-banner-bot")
    parser.add_argument(
        "command",
        choices=(
            "plan",
            "sync",
            "clear-unapproved-descriptions",
            "sync-approved-descriptions",
        ),
    )
    parser.add_argument("--org", default="wisent-ai")
    parser.add_argument("--exclude", action="append", default=["wisent"])
    parser.add_argument("--include", action="append", default=[])
    parser.add_argument("--direct", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--token-env", default="WISENT_BANNER_GITHUB_TOKEN")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    token = os.environ.get(args.token_env, "")
    if args.command in {"sync", "clear-unapproved-descriptions", "sync-approved-descriptions"} and not token:
        print(f"{args.token_env} must contain a GitHub App token for mutation", file=sys.stderr)
        return 2
    if args.command == "clear-unapproved-descriptions":
        source = Path(__file__).with_name("unapproved_descriptions.json")
        document = json.loads(source.read_text(encoding="utf-8"))
        if document.get("schema") != 1 or not isinstance(document.get("repositories"), list):
            raise ValueError("unapproved_descriptions.json must contain schema 1 and repositories")
        client = GitHubClient(token)
        for repository in document["repositories"]:
            changed = client.clear_description(args.org, repository)
            print(
                json.dumps(
                    {
                        "repository": f"{args.org}/{repository}",
                        "description": "",
                        "changed": changed,
                    },
                    ensure_ascii=False,
                )
            )
        return 0

    if args.command == "sync-approved-descriptions":
        source = Path(__file__).with_name("approved_copy.json")
        document = json.loads(source.read_text(encoding="utf-8"))
        if document.get("schema") != 1 or not isinstance(document.get("entries"), dict):
            raise ValueError("approved_copy.json must contain schema 1 and entries")
        entries = document["entries"]
        client = GitHubClient(token)
        for repository in client.list_repositories(args.org):
            name = repository["name"]
            approved = entries.get(name.lower(), {})
            description = str(approved.get("description", "")).strip()
            changed = client.set_description(args.org, name, description)
            print(
                json.dumps(
                    {
                        "repository": f"{args.org}/{name}",
                        "description": description,
                        "changed": changed,
                    },
                    ensure_ascii=False,
                )
            )
        return 0

    included = set(args.include) or None
    bot = BannerBot(GitHubClient(token), set(args.exclude), included)
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
            result_key = "repository_url" if args.direct else "pull_request"
            summary[result_key] = bot.apply(plan, direct=args.direct)
            print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = ["BannerBot", "GitHubClient", "RepositoryPlan", "main", "update_readme"]
