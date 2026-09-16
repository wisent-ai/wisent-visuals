"""What the bot writes into a repository's audit declaration."""

import shutil
from pathlib import Path

from wisent_plots.banner_automation.audit import declare, declare_tree
from wisent_plots.banner_automation.model import (
    AUDIT_IGNORE_PATH,
    SVG_PATH,
    audit_declaration,
)

# Scratch checkouts live in this repository's ignored build directory:
# nothing here writes to the system temporary directory.
SCRATCH = Path(__file__).resolve().parents[2].joinpath("build", "test-declare")


def _checkout(name: str, banner: bool, declaration: str = "") -> Path:
    """A scratch checkout that starts empty, so a second run sees a first run."""
    repository = SCRATCH.joinpath(name)
    shutil.rmtree(repository, ignore_errors=True)
    repository.joinpath(".git").mkdir(parents=True, exist_ok=True)
    if banner:
        svg = repository.joinpath(SVG_PATH)
        svg.parent.mkdir(parents=True, exist_ok=True)
        svg.write_text("<svg/>\n", encoding="utf-8")
    if declaration:
        target = repository.joinpath(AUDIT_IGNORE_PATH)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(declaration, encoding="utf-8")
    return repository


def test_repository_without_a_declaration_receives_one_naming_the_banner():
    written = audit_declaration(None)

    assert written is not None
    assert SVG_PATH in written.splitlines()
    assert written.startswith("#")


def test_existing_declarations_survive_and_the_banner_is_added_once():
    existing = "# rendered by tools/build.py\ndist/bundle.js\n"

    written = audit_declaration(existing)

    assert written is not None
    assert written.startswith(existing)
    assert written.splitlines().count(SVG_PATH) == 1
    assert "dist/bundle.js" in written.splitlines()
    assert audit_declaration(written) is None


def test_a_repository_that_already_names_the_banner_is_left_alone():
    assert audit_declaration(f"{SVG_PATH}\n") is None
    assert audit_declaration(f"# generated\n  {SVG_PATH}  \n") is None


def test_a_published_banner_without_a_declaration_is_declared_locally():
    repository = _checkout("needs-one", banner=True)

    reported = declare(repository, apply=True)

    assert reported.wrote is True
    assert reported.reason == "declared the banner"
    written = repository.joinpath(AUDIT_IGNORE_PATH).read_text(encoding="utf-8")
    assert SVG_PATH in written.splitlines()


def test_a_report_only_run_changes_nothing():
    repository = _checkout("report-only", banner=True)

    reported = declare(repository, apply=False)

    assert reported.wrote is False
    assert reported.reason == "would declare the banner"
    assert not repository.joinpath(AUDIT_IGNORE_PATH).exists()


def test_a_checkout_without_a_banner_is_left_alone():
    repository = _checkout("no-banner", banner=False)

    assert declare(repository, apply=True).reason == "no published banner"
    assert not repository.joinpath(AUDIT_IGNORE_PATH).exists()


def test_a_checkout_that_already_declares_the_banner_is_untouched():
    existing = f"# generated\n{SVG_PATH}\n"
    repository = _checkout("already", banner=True, declaration=existing)

    assert declare(repository, apply=True).reason == "already declared"
    assert repository.joinpath(AUDIT_IGNORE_PATH).read_text(encoding="utf-8") == existing


def test_every_checkout_under_a_directory_is_visited():
    _checkout("tree/one", banner=True)
    _checkout("tree/two", banner=False)

    reported = declare_tree(SCRATCH.joinpath("tree"), apply=False)

    assert {found.repository.name for found in reported} == {"one", "two"}
    assert {found.reason for found in reported} == {
        "would declare the banner",
        "no published banner",
    }
