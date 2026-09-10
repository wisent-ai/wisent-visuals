"""Deterministic README banner generation for Wisent projects."""

from __future__ import annotations

import base64
import hashlib
import html
import io
import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, Tuple, Union

from PIL import Image, ImageDraw, ImageFont

from .banner_rendering.artwork import SUPPORTED_LAYOUTS, render_artwork
from .banner_rendering.typography import text_layout
from .brand import BRAND_COLORS, FONT_FAMILY

try:
    import tomllib
except ImportError:  # pragma: no cover - exercised on Python 3.8-3.10
    import tomli as tomllib


SUPPORTED_THEMES = ("dark",)


@dataclass(frozen=True)
class BannerConfig:
    """Validated content and dimensions for a README banner."""

    title: str
    description: str
    product: str = "Wisent"
    url: str = "wisent.com"
    theme: str = "dark"
    layout: str = "latent-field-left"
    art_seed: str = ""
    width: int = 1584
    height: int = 396

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("title must not be empty")
        if self.layout not in SUPPORTED_LAYOUTS:
            raise ValueError(f"layout must be one of: {', '.join(SUPPORTED_LAYOUTS)}")
        if self.theme not in SUPPORTED_THEMES:
            raise ValueError(f"theme must be one of: {', '.join(SUPPORTED_THEMES)}")
        if not 800 <= self.width <= 3200:
            raise ValueError("width must be between 800 and 3200 pixels")
        if not 200 <= self.height <= 1000:
            raise ValueError("height must be between 200 and 1000 pixels")

    @classmethod
    def from_toml(cls, path: Union[Path, str]) -> "BannerConfig":
        """Load flat or bot-managed banner configuration from a TOML file."""
        with Path(path).open("rb") as stream:
            document = tomllib.load(stream)
        if "banner" in document:
            unknown_sections = set(document) - {"automation", "banner"}
            if unknown_sections:
                names = ", ".join(sorted(unknown_sections))
                raise ValueError(f"unknown banner section(s): {names}")
            values = document["banner"]
        else:
            values = document
        unknown = set(values) - set(cls.__dataclass_fields__)
        if unknown:
            names = ", ".join(sorted(unknown))
            raise ValueError(f"unknown banner setting(s): {names}")
        return cls(**values)


class Banner:
    """Render a :class:`BannerConfig` to SVG, WebP, or PNG."""

    def __init__(self, config: BannerConfig):
        self.config = config
        self._font_bytes: Dict[str, bytes] = {
            "regular": self._read_asset("HubotSans-Regular.ttf"),
            "bold": self._read_asset("HubotSans-Bold.ttf"),
        }
        self._logo_bytes = (
            Path(__file__).with_name("assets").joinpath("wisent-logo.png").read_bytes()
        )
        self._art_digest = hashlib.sha256(
            (config.art_seed or config.layout).encode("utf-8")
        ).digest()

    @staticmethod
    def _read_asset(name: str) -> bytes:
        asset = Path(__file__).with_name("assets") / "fonts" / name
        return asset.read_bytes()

    @lru_cache(maxsize=32)
    def _font(self, size: int, weight: str = "regular") -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(io.BytesIO(self._font_bytes[weight]), size=size)

    def _scale(self) -> float:
        return self.config.height / 396

    def _variant(self, index: int, low: float = 0, high: float = 1) -> float:
        unit = self._art_digest[index % len(self._art_digest)] / 255
        return low + (high - low) * unit

    def _line_dots(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        spacing: float = 8,
        opacity: float = 0.5,
        radius: float = 1.1,
    ) -> Iterable[Tuple[float, float, float, float]]:
        scale = self._scale()
        distance = math.hypot(end[0] - start[0], end[1] - start[1])
        steps = max(1, round(distance / spacing))
        for index in range(steps + 1):
            progress = index / steps
            x = start[0] + (end[0] - start[0]) * progress
            y = start[1] + (end[1] - start[1]) * progress
            yield x * scale, y * scale, radius * scale, opacity

    def _footer_geometry(self) -> Tuple[float, float, float, float]:
        """Return logo position, size, and the visible top of the product wordmark."""
        scale = self._scale()
        size = 34 * scale
        footer_y = self.config.height - 65 * scale
        font_size = max(16, round(29 * scale))
        bounds = self._font(font_size).getbbox(self.config.product, anchor="la")
        text_top = footer_y + bounds[1]
        text_bottom = footer_y + bounds[3]
        logo_y = (text_top + text_bottom - size) / 2
        return self.config.width * 0.518, logo_y, size, text_top

    def _draw_logo(self, image: Image.Image) -> None:
        logo_x, logo_y, logo_size, _ = self._footer_geometry()
        size = max(1, round(logo_size))
        logo = Image.open(io.BytesIO(self._logo_bytes)).convert("RGBA")
        logo = logo.resize((size, size), Image.Resampling.LANCZOS)
        image.paste(logo, (round(logo_x), round(logo_y)), logo)

    def render_image(self) -> Image.Image:
        """Render the banner into an RGB Pillow image."""
        cfg = self.config
        image = Image.new("RGB", (cfg.width, cfg.height), BRAND_COLORS["background"])
        draw = ImageDraw.Draw(image)
        base = tuple(int(BRAND_COLORS["primary"][i : i + 2], 16) for i in (1, 3, 5))
        for x, y, radius, opacity in render_artwork(self):
            color = tuple(round(channel * opacity) for channel in base)
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)

        self._draw_logo(image)
        for line in text_layout(self):
            font = self._font(line.size, line.weight)
            anchor = "ra" if line.text == cfg.url else "la"
            draw.text((line.x, line.y), line.text, font=font, fill=line.color, anchor=anchor)
        return image

    def render_svg(self) -> str:
        """Render a self-contained SVG with embedded Hubot Sans fonts."""
        cfg = self.config
        regular = base64.b64encode(self._font_bytes["regular"]).decode("ascii")
        bold = base64.b64encode(self._font_bytes["bold"]).decode("ascii")
        parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{cfg.width}" height="{cfg.height}" viewBox="0 0 {cfg.width} {cfg.height}">',
            "<defs><style>",
            f"@font-face{{font-family:'{FONT_FAMILY}';src:url(data:font/ttf;base64,{regular}) format('truetype');font-weight:400}}",
            f"@font-face{{font-family:'{FONT_FAMILY}';src:url(data:font/ttf;base64,{bold}) format('truetype');font-weight:700}}",
            f"text{{font-family:'{FONT_FAMILY}',sans-serif}}",
            "</style></defs>",
            f'<rect width="{cfg.width}" height="{cfg.height}" fill="{BRAND_COLORS["background"]}"/>',
        ]
        for x, y, radius, opacity in render_artwork(self):
            parts.append(
                f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{radius:.2f}" fill="{BRAND_COLORS["primary"]}" opacity="{opacity:.3f}"/>'
            )

        logo_x, logo_y, logo_size, product_top = self._footer_geometry()
        logo = base64.b64encode(self._logo_bytes).decode("ascii")
        parts.append(
            f'<image x="{logo_x:.2f}" y="{logo_y:.2f}" width="{logo_size:.2f}" height="{logo_size:.2f}" href="data:image/png;base64,{logo}"/>'
        )
        for line in text_layout(self):
            anchor = "end" if line.text == cfg.url else "start"
            escaped = html.escape(line.text)
            text_y = product_top if line.text == cfg.product else line.y
            parts.append(
                f'<text x="{line.x:.2f}" y="{text_y:.2f}" dominant-baseline="hanging" text-anchor="{anchor}" font-size="{line.size}" font-weight="{700 if line.weight == "bold" else 400}" fill="{line.color}">{escaped}</text>'
            )
        parts.append("</svg>")
        return "\n".join(parts) + "\n"

    def save(self, path: Union[Path, str]) -> Path:
        """Render to a file selected by its .svg, .webp, or .png suffix."""
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        suffix = output.suffix.lower()
        if suffix == ".svg":
            output.write_text(self.render_svg(), encoding="utf-8", newline="\n")
        elif suffix == ".webp":
            self.render_image().save(output, "WEBP", quality=90, method=6, exact=True)
        elif suffix == ".png":
            self.render_image().save(output, "PNG", optimize=True)
        else:
            raise ValueError("output must use .svg, .webp, or .png")
        return output


__all__ = ["Banner", "BannerConfig", "SUPPORTED_LAYOUTS", "SUPPORTED_THEMES"]
