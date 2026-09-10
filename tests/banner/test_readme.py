"""Defend the public README transformation and preservation of unmanaged content."""

from wisent_plots.banner_automation.model import BANNER_END, BANNER_START, SIGNALS_START
from wisent_plots.banner_bot import update_readme


def test_manual_banner_and_user_body_survive_repeated_updates():
    prefix = '# Project\n\n<p><img src="banner.png" width="100%"></p>'
    suffix = "\n\nKeep this documentation unchanged.\n"
    updated = update_readme(prefix + suffix, "project")
    assert updated.startswith(prefix)
    assert updated.endswith(suffix)
    assert "assets/readme-banner.webp" not in updated
    assert update_readme(updated, "project") == updated


def test_managed_banner_replacement_preserves_body_and_precedes_buttons():
    body = "# Project\n\nProject documentation stays untouched.\n"
    source = f"{BANNER_START}\nold generated markup\n{BANNER_END}\n\n{body}"
    updated = update_readme(source, "new-name")
    assert updated.startswith(BANNER_START)
    assert updated.endswith(body)
    assert "old generated markup" not in updated
    assert updated.count(BANNER_START) == 1
    assert updated.index(BANNER_END) < updated.index(SIGNALS_START) < updated.index("# Project")
    assert update_readme(updated, "new-name") == updated


def test_unbalanced_marker_in_user_body_is_not_deleted():
    body = "# Project\n\n<!-- wisent-readme-signals:end -->\n\nOverview\n"
    updated = update_readme(body, "project")
    assert updated.startswith(BANNER_START)
    assert updated.endswith(body)
    assert update_readme(updated, "project") == updated
