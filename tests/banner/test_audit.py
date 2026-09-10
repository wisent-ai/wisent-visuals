"""What the bot writes into a repository's audit declaration."""

from wisent_plots.banner_automation.model import SVG_PATH, audit_declaration


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
