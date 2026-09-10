import hashlib
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import wisent_plots
from wisent_plots.banner import SUPPORTED_LAYOUTS, Banner, BannerConfig
from wisent_plots.repository_profile import RepositoryProfile, generate_identity


def render_profile(profile, tmp_path):
    identity = generate_identity(profile)
    config = tmp_path / "banner.toml"
    svg = tmp_path / "banner.svg"
    config.write_text(identity.to_toml(), encoding="utf-8")
    command = [
        sys.executable,
        "-m",
        "wisent_plots.banner_rendering.cli",
        "--config",
        str(config),
        "--output",
        str(tmp_path / "banner.webp"),
        "--svg",
        str(svg),
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    (tmp_path / "command.json").write_text(
        json.dumps(
            {
                "command": command,
                "exitCode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    assert result.returncode == 0, result.stderr
    return [node.text for node in ET.parse(svg).getroot().findall("{*}text")]


def test_unapproved_metadata_does_not_become_published_copy(tmp_path):
    metadata = "Unapproved neural audio codec description"
    readme = "Unapproved README product claim"
    text = render_profile(
        RepositoryProfile("unapproved-rendering-example", metadata, readme_excerpt=readme),
        tmp_path,
    )
    assert text[0] == "Unapproved Rendering Example"
    assert metadata not in text
    assert readme not in text


def test_approved_copy_survives_different_repository_metadata(tmp_path):
    source = Path(wisent_plots.__file__).with_name("approved_copy.json")
    approved = json.loads(source.read_text(encoding="utf-8"))["entries"]["brama"]
    metadata = "This unapproved audio claim must not replace the approved title"
    text = render_profile(RepositoryProfile("brama", metadata, ("audio",)), tmp_path)
    assert text[0] == approved["title"].strip()
    assert metadata not in text


def test_every_layout_has_distinct_deterministic_artwork(tmp_path: Path) -> None:
    digests = set()
    for layout in SUPPORTED_LAYOUTS:
        config = BannerConfig(
            title="Project-specific heading",
            description="Repository description",
            layout=layout,
        )
        image = Banner(config).render_image()
        image.save(tmp_path / f"{layout}.png")
        first = image.tobytes()
        second = Banner(config).render_image().tobytes()
        assert first == second
        digests.add(hashlib.sha256(first).hexdigest())

    assert len(digests) == len(SUPPORTED_LAYOUTS)


def test_same_layout_uses_repository_seed_for_unique_artwork() -> None:
    grant = Banner(
        BannerConfig(
            title="Seed comparison",
            description="The content stays unchanged.",
            layout="signal-left",
            art_seed="grant-cli",
        )
    ).render_image()
    kronika = Banner(
        BannerConfig(
            title="Seed comparison",
            description="The content stays unchanged.",
            layout="signal-left",
            art_seed="kronika",
        )
    ).render_image()

    assert grant.tobytes() != kronika.tobytes()
