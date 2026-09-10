"""Command-line selection and diagnostics for banner publication."""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional, Sequence

from .engine import BannerBot
from .github import GitHubClient


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
    if (
        args.command in {"sync", "clear-unapproved-descriptions", "sync-approved-descriptions"}
        and not token
    ):
        print(f"{args.token_env} must contain a GitHub token for mutation", file=sys.stderr)
        return 2
    if args.command == "clear-unapproved-descriptions":
        source = Path(__file__).parent.parent.joinpath("unapproved_descriptions.json")
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
        source = Path(__file__).parent.parent.joinpath("approved_copy.json")
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
