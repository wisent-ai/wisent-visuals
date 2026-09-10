"""Exercise the real publication CLI; mutation requires a dedicated GitHub fixture."""

import io
import json
import os
import subprocess
import sys
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
from PIL import Image

from wisent_plots.banner_bot import GitHubClient

ROOT = Path(__file__).resolve().parents[2]


def run_cli(arguments, commands, environment=None):
    command = [sys.executable, "-m", "wisent_plots.banner_bot", *arguments]
    result = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True, text=True)
    commands.append(
        {
            "command": command,
            "exitCode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    )
    return result


def report_for_source():
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return {"sourceRevision": revision, "commands": []}


def test_sync_refuses_missing_credentials_before_publication(tmp_path):
    report = report_for_source()
    environment = dict(os.environ)
    environment.pop("WISENT_BANNER_TEST_MISSING_TOKEN", None)
    result = run_cli(
        ["sync", "--token-env", "WISENT_BANNER_TEST_MISSING_TOKEN"],
        report["commands"],
        environment,
    )
    (tmp_path / "refusal.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    assert result.returncode == 2
    assert result.stderr.strip() == (
        "WISENT_BANNER_TEST_MISSING_TOKEN must contain a GitHub App token for mutation"
    )
    assert result.stdout == ""


def test_sync_publishes_real_artifacts_and_reuses_unchanged_pull_request(tmp_path):
    report = report_for_source()
    target = os.environ.get("WISENT_BANNER_TEST_REPOSITORY", "")
    token = os.environ.get("WISENT_BANNER_GITHUB_TOKEN", "")
    if not target or not token:
        report.update(
            status="blocked",
            reason=(
                "Real GitHub publication requires WISENT_BANNER_GITHUB_TOKEN and "
                "WISENT_BANNER_TEST_REPOSITORY naming an isolated publication fixture."
            ),
        )
        (tmp_path / "publication.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        pytest.skip(report["reason"])

    owner, repository = target.split("/")
    client = GitHubClient(token)
    resource = f"/repos/{owner}/{repository}"
    metadata = client.request("GET", resource)
    assert (
        metadata.get("description") == "Wisent Visuals publication test fixture"
    ), "Refusing to mutate a repository that is not explicitly designated as a test fixture."
    assert not metadata.get("archived") and not metadata.get("fork")
    branch = metadata["default_branch"]
    assert (
        client.request("GET", f"{resource}/pulls?state=open") == []
    ), "The fixture must have no active pull request."
    branches = client.request("GET", f"{resource}/branches?per_page=100")
    assert {item["name"] for item in branches} == {
        branch
    }, "The fixture must have only its default branch and be used exclusively by this test."
    originals = {
        path: client.read_content(owner, repository, path, branch)
        for path in ("README.md", ".github/banner.toml")
    }
    assert originals["README.md"] is not None, "The fixture must already be initialized."
    report["fixture"] = target
    cleanup_errors = []
    try:
        client.write_content(
            owner,
            repository,
            "README.md",
            branch,
            b"# Publication fixture\n\nThis body belongs to the fixture.\n",
            "test: seed isolated banner publication",
            originals["README.md"][1],
        )
        previous_config = originals[".github/banner.toml"]
        if previous_config is not None:
            client.delete_content(
                owner,
                repository,
                ".github/banner.toml",
                branch,
                "test: exercise initial banner publication",
                previous_config[1],
            )
        arguments = ["sync", "--org", owner, "--include", repository, "--limit", "1"]
        first = run_cli(arguments, report["commands"])
        assert first.returncode == 0, first.stderr
        published = json.loads(first.stdout)
        number = int(published["pull_request"].rsplit("/", 1)[1])
        pull = client.request("GET", f"{resource}/pulls/{number}")
        assert pull["state"] == "open" and pull["base"]["ref"] == branch
        head = pull["head"]["ref"]
        head_revision = pull["head"]["sha"]
        report.update(pullRequest=published["pull_request"], publishedRevision=head_revision)
        artifacts = {}
        for path in (
            "README.md",
            ".github/banner.toml",
            "assets/readme-banner.svg",
            "assets/readme-banner.webp",
        ):
            stored = client.read_content(owner, repository, path, head)
            assert stored is not None, f"GitHub does not contain the promised artifact: {path}"
            destination = tmp_path / "published" / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(stored[0])
            artifacts[path] = stored[0]
        readme = artifacts["README.md"].decode("utf-8")
        assert readme.startswith("<!-- wisent-banner:start -->")
        assert "This body belongs to the fixture." in readme
        assert 'src="assets/readme-banner.webp"' in readme
        svg = ET.fromstring(artifacts["assets/readme-banner.svg"])
        assert svg.tag == "{http://www.w3.org/2000/svg}svg"
        with Image.open(io.BytesIO(artifacts["assets/readme-banner.webp"])) as image:
            assert image.format == "WEBP"
            assert image.size == (int(svg.attrib["width"]), int(svg.attrib["height"]))
            assert any(low != high for low, high in image.getextrema())
        second = run_cli(arguments, report["commands"])
        assert second.returncode == 0, second.stderr
        assert json.loads(second.stdout)["pull_request"] == published["pull_request"]
        repeated = client.request("GET", f"{resource}/pulls/{number}")
        assert repeated["head"]["sha"] == head_revision
        report["status"] = "passed"
    finally:
        # This explicitly isolated fixture had no PR or non-default branch before the test.
        try:
            for pull in client.request("GET", f"{resource}/pulls?state=open"):
                if pull["head"]["ref"].startswith("wisent-readme-bot/"):
                    client.request(
                        "PATCH", f"{resource}/pulls/{pull['number']}", {"state": "closed"}
                    )
        except Exception as error:
            cleanup_errors.append(f"close test pull request: {error}")
        try:
            for item in client.request("GET", f"{resource}/branches?per_page=100"):
                if item["name"].startswith("wisent-readme-bot/"):
                    ref = urllib.parse.quote(item["name"], safe="")
                    client.request("DELETE", f"{resource}/git/refs/heads/{ref}")
        except Exception as error:
            cleanup_errors.append(f"delete test branch: {error}")
        for path, original in originals.items():
            try:
                current = client.read_content(owner, repository, path, branch)
                if original is None:
                    if current is not None:
                        client.delete_content(
                            owner, repository, path, branch, "test: restore fixture", current[1]
                        )
                elif current is None or current[0] != original[0]:
                    client.write_content(
                        owner,
                        repository,
                        path,
                        branch,
                        original[0],
                        "test: restore fixture",
                        "" if current is None else current[1],
                    )
            except Exception as error:
                cleanup_errors.append(f"restore {path}: {error}")
        report["cleanupErrors"] = cleanup_errors
        report.setdefault("status", "failed")
        if cleanup_errors:
            report["status"] = "failed"
        (tmp_path / "publication.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        assert not cleanup_errors, cleanup_errors
