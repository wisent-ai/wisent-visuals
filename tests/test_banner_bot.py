from typing import Dict, Iterable, Mapping, Optional, Tuple

from wisent_plots.banner_bot import (
    BANNER_END,
    BANNER_START,
    BannerBot,
    RepositoryPlan,
    update_readme,
)
from wisent_plots.repository_profile import RepositoryProfile, generate_identity


def test_update_readme_preserves_manual_banner() -> None:
    readme = '# Project\n\n<p><img src="banner.png" width="100%"></p>\n\nKeep me.\n'

    assert update_readme(readme, "project") == readme


def test_update_readme_replaces_only_managed_block() -> None:
    readme = (
        "# Project\n\n"
        f"{BANNER_START}\nold generated markup\n{BANNER_END}\n\n"
        "Project documentation stays untouched.\n"
    )

    updated = update_readme(readme, "new-name")

    assert "old generated markup" not in updated
    assert 'alt="new-name by Wisent"' in updated
    assert "Project documentation stays untouched." in updated
    assert updated.count(BANNER_START) == 1


def test_update_readme_inserts_after_signal_badges() -> None:
    readme = "# Project\n\n<!-- wisent-readme-signals:end -->\n\nOverview\n"

    updated = update_readme(readme, "project")

    assert updated.index("wisent-readme-signals:end") < updated.index(BANNER_START)
    assert updated.endswith("Overview\n")


class FakeReadClient:
    def __init__(self) -> None:
        self.files: Dict[Tuple[str, str], bytes] = {
            (
                "new-router",
                "README.md",
            ): b"# New Router\n\nRoutes requests across model providers.\n",
            ("manual", "README.md"): b'# Manual\n\n<img src="banner.svg">\n',
        }

    def list_repositories(self, organization: str) -> Iterable[Mapping[str, object]]:
        return [
            {
                "name": "wisent",
                "description": "Reference repository",
                "topics": [],
                "language": "Python",
                "default_branch": "main",
                "archived": False,
                "disabled": False,
                "fork": False,
            },
            {
                "name": "new-router",
                "description": "Multi-provider gateway and fallback router",
                "topics": ["gateway"],
                "language": "Rust",
                "default_branch": "main",
                "archived": False,
                "disabled": False,
                "fork": False,
            },
            {
                "name": "manual",
                "description": "A manually branded repository",
                "topics": [],
                "language": "Python",
                "default_branch": "main",
                "archived": False,
                "disabled": False,
                "fork": False,
            },
        ]

    def read_content(
        self, owner: str, repository: str, path: str, ref: str
    ) -> Optional[Tuple[bytes, str]]:
        content = self.files.get((repository, path))
        return None if content is None else (content, "sha")


def test_bot_plans_new_repo_but_skips_reference_and_manual_banners() -> None:
    bot = BannerBot(FakeReadClient(), {"wisent"})

    plans = list(bot.plans("wisent-ai"))

    assert len(plans) == 1
    assert plans[0].name == "new-router"
    assert plans[0].identity.category == "gateway"
    assert plans[0].identity.title == "New Router routes. You stay in control."


class LimitClient:
    def __init__(self) -> None:
        managed = generate_identity(
            RepositoryProfile("managed-cli", "CLI for managed work", language="Python")
        )
        self.managed_config = managed.to_toml().encode()

    def list_repositories(self, organization: str):
        common = {
            "topics": [],
            "language": "Python",
            "default_branch": "main",
            "archived": False,
            "disabled": False,
            "fork": False,
        }
        return [
            {"name": "managed-cli", "description": "CLI for managed work", **common},
            {"name": "waiting-cli", "description": "CLI still waiting for a banner", **common},
        ]

    def read_content(self, owner: str, repository: str, path: str, ref: str):
        if repository == "managed-cli" and path == ".github/banner.toml":
            return self.managed_config, "sha"
        return None


def test_plan_limit_counts_emitted_plans_not_already_managed_repositories() -> None:
    plans = list(BannerBot(LimitClient(), set()).plans("wisent-ai", limit=1))

    assert [plan.name for plan in plans] == ["waiting-cli"]


class FakeWriteClient:
    def __init__(self) -> None:
        self.branch = ""
        self.files: Dict[str, bytes] = {}
        self.pull_requests = []

    def ensure_branch(self, owner: str, repository: str, default_branch: str, branch: str) -> None:
        self.branch = branch

    def read_content(
        self, owner: str, repository: str, path: str, ref: str
    ) -> Optional[Tuple[bytes, str]]:
        content = self.files.get(path)
        return None if content is None else (content, "sha")

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
        self.files[path] = content

    def open_pull_request(self, owner, repository, branch, default_branch, identity) -> str:
        self.pull_requests.append((repository, branch, identity.category))
        return "https://github.com/wisent-ai/new-router/pull/1"


def test_apply_writes_managed_config_assets_and_readme() -> None:
    client = FakeWriteClient()
    identity = generate_identity(
        RepositoryProfile("new-router", "Multi-provider gateway", ("gateway",), "Rust")
    )
    plan = RepositoryPlan("wisent-ai", "new-router", "main", identity, "# New Router\n", "new")

    url = BannerBot(client, {"wisent"}).apply(plan)

    assert url.endswith("/pull/1")
    assert set(client.files) == {
        ".github/banner.toml",
        "assets/readme-banner.svg",
        "assets/readme-banner.webp",
        "README.md",
    }
    assert client.files["assets/readme-banner.webp"].startswith(b"RIFF")
    assert b"[automation]" in client.files[".github/banner.toml"]
    assert BANNER_START.encode() in client.files["README.md"]
