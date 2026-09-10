"""GitHub repository reads and explicit banner publication operations."""

import base64
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple

from ..identity import BannerIdentity
from .model import CONFIG_PATH


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
