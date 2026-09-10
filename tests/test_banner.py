import base64
import io
from pathlib import Path

import pytest
from PIL import Image, ImageChops

from wisent_plots.banner import Banner, BannerConfig
from wisent_plots.banner_cli import main


@pytest.fixture
def config() -> BannerConfig:
    return BannerConfig(
        title="Deep control. Safer output.",
        description="A Python package for latent space monitoring and guardrails.",
    )


def test_loads_toml_and_rejects_unknown_settings(tmp_path: Path) -> None:
    source = tmp_path / "banner.toml"
    source.write_text(
        'title = "A title"\ndescription = "A description"\nwidth = 1200\n',
        encoding="utf-8",
    )
    assert BannerConfig.from_toml(source).width == 1200

    source.write_text(
        'title = "A title"\ndescription = "A description"\ncolour = "green"\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="unknown banner setting.*colour"):
        BannerConfig.from_toml(source)


def test_webp_has_requested_dimensions_and_real_format(
    tmp_path: Path, config: BannerConfig
) -> None:
    output = tmp_path / "banner.webp"
    Banner(config).save(output)

    with Image.open(output) as image:
        assert image.format == "WEBP"
        assert image.size == (1584, 396)


def test_render_is_byte_deterministic(tmp_path: Path, config: BannerConfig) -> None:
    first = tmp_path / "first.webp"
    second = tmp_path / "second.webp"

    Banner(config).save(first)
    Banner(config).save(second)

    assert first.read_bytes() == second.read_bytes()


def test_svg_is_self_contained_and_escapes_content(config: BannerConfig) -> None:
    svg = Banner(
        BannerConfig(title="Control & safety", description=config.description)
    ).render_svg()

    assert "data:font/ttf;base64," in svg
    assert "data:image/png;base64," in svg
    encoded_logo = svg.split("data:image/png;base64,", 1)[1].split('"', 1)[0]
    with Image.open(io.BytesIO(base64.b64decode(encoded_logo))) as logo:
        assert logo.mode == "RGBA"
        assert logo.getchannel("A").getextrema() == (0, 255)
    assert "Control &amp; safety" in svg
    assert "fonts.googleapis.com" not in svg


def test_footer_logo_and_wordmark_share_visual_center(config: BannerConfig) -> None:
    image = Banner(config).render_image()
    background = Image.new("RGB", image.size, image.getpixel((0, 0)))
    foreground = ImageChops.difference(image, background)
    logo_bounds = foreground.crop((820, 300, 860, 380)).getbbox()
    wordmark_bounds = foreground.crop((860, 300, 970, 380)).getbbox()

    assert logo_bounds is not None
    assert wordmark_bounds is not None
    logo_center = (logo_bounds[1] + logo_bounds[3]) / 2
    wordmark_center = (wordmark_bounds[1] + wordmark_bounds[3]) / 2
    assert abs(logo_center - wordmark_center) <= 1


def test_cli_generates_raster_and_svg(tmp_path: Path) -> None:
    source = tmp_path / "banner.toml"
    raster = tmp_path / "banner.webp"
    svg = tmp_path / "banner.svg"
    source.write_text(
        'title = "Deep control."\ndescription = "Safer model output."\n',
        encoding="utf-8",
    )

    assert main(["--config", str(source), "--output", str(raster), "--svg", str(svg)]) == 0
    assert raster.is_file()
    assert svg.read_text(encoding="utf-8").startswith("<?xml")
