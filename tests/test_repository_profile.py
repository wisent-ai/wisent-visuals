import hashlib
from pathlib import Path

import pytest

from wisent_plots.banner import SUPPORTED_LAYOUTS, Banner, BannerConfig
from wisent_plots.repository_profile import RepositoryProfile, generate_identity


@pytest.mark.parametrize(
    ("profile", "category", "layout"),
    [
        (
            RepositoryProfile(
                "brama",
                "Multi-provider LLM router with fallback chains",
                ("gateway", "inference"),
                "Rust",
            ),
            "gateway",
            "gate-left",
        ),
        (
            RepositoryProfile(
                "uncensorbench", "Benchmark model censorship removal", language="Python"
            ),
            "benchmark",
            "fracture-left",
        ),
        (
            RepositoryProfile("neucodec-mlx-swift", "Neural audio codec decoder", language="Swift"),
            "audio",
            "waveform-left",
        ),
        (
            RepositoryProfile("eve-toolkit", "Toolkit for autonomous AI agents", language="Python"),
            "agent",
            "orbit-left",
        ),
        (
            RepositoryProfile(
                "transcript-lake", "Storage for searchable transcripts", language="Rust"
            ),
            "data",
            "layers-left",
        ),
        (
            RepositoryProfile("wisent-visuals", "Brand-styled plots and charts", language="Python"),
            "visualization",
            "benchmark-left",
        ),
    ],
)
def test_generates_semantic_identity(profile, category, layout) -> None:
    identity = generate_identity(profile)

    assert identity.category == category
    assert identity.layout == layout
    assert identity.description


def test_unknown_repository_gets_named_heading() -> None:
    identity = generate_identity(RepositoryProfile("nowy-projekt", language="Rust"))

    assert identity.category == "general"
    assert identity.title == "Nowy Projekt. Built for what comes next."
    assert identity.description == "A Rust project from Wisent."
    assert identity.layout == "signal-left"
    assert identity.art_seed == "nowy-projekt"


@pytest.mark.parametrize(
    ("name", "title", "description_fragment"),
    [
        (
            "heretic",
            "Remove model censorship automatically.",
            "representation-engineering",
        ),
        (
            "brama",
            "Route every model through one gateway.",
            "multi-provider LLM routing",
        ),
        (
            "jeden",
            "Run coding agents locally, under your policy.",
            "coding-agent harness",
        ),
        (
            "kronika",
            "Write documentation from repository evidence.",
            "bounded source evidence",
        ),
        (
            "grant-cli",
            "Research and write grants with evidence attached.",
            "source-backed applications",
        ),
        (
            "ugc-cli",
            "Run creator campaigns from one local ledger.",
            "creator",
        ),
    ],
)
def test_known_repository_gets_specific_package_copy(
    name: str, title: str, description_fragment: str
) -> None:
    identity = generate_identity(RepositoryProfile(name))

    assert identity.title == title
    assert description_fragment in identity.description


def test_identity_toml_is_accepted_by_renderer(tmp_path: Path) -> None:
    identity = generate_identity(
        RepositoryProfile("brama", "Multi-provider model router", ("gateway",), "Rust")
    )
    config_path = tmp_path / "banner.toml"
    config_path.write_text(identity.to_toml(), encoding="utf-8")

    config = BannerConfig.from_toml(config_path)

    assert config.title == identity.title
    assert config.layout == "gate-left"
    assert config.art_seed == "brama"


def test_every_layout_has_distinct_deterministic_artwork() -> None:
    digests = set()
    for layout in SUPPORTED_LAYOUTS:
        config = BannerConfig(
            title="Project-specific heading",
            description="Repository description",
            layout=layout,
        )
        first = Banner(config).render_image().tobytes()
        second = Banner(config).render_image().tobytes()
        assert first == second
        digests.add(hashlib.sha256(first).hexdigest())

    assert len(digests) == len(SUPPORTED_LAYOUTS)


def test_same_layout_uses_repository_seed_for_unique_artwork() -> None:
    grant = Banner(
        BannerConfig(
            title="Grant CLI",
            description="Grant research",
            layout="signal-left",
            art_seed="grant-cli",
        )
    ).render_image()
    kronika = Banner(
        BannerConfig(
            title="Kronika",
            description="Documentation writer",
            layout="signal-left",
            art_seed="kronika",
        )
    ).render_image()

    assert grant.tobytes() != kronika.tobytes()
