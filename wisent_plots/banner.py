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
from typing import Dict, Iterable, List, Sequence, Tuple, Union

from PIL import Image, ImageDraw, ImageFont

from .brand import BRAND_COLORS, FONT_FAMILY

try:
    import tomllib
except ImportError:  # pragma: no cover - exercised on Python 3.8-3.10
    import tomli as tomllib


SUPPORTED_LAYOUTS = (
    "benchmark-left",
    "flock-left",
    "focus-left",
    "forest-left",
    "fracture-left",
    "gate-left",
    "gauge-left",
    "latent-field-left",
    "layers-left",
    "orbit-left",
    "routes-left",
    "scan-left",
    "signal-left",
    "spark-left",
    "timeline-left",
    "vault-left",
    "waveform-left",
)
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


@dataclass(frozen=True)
class _TextLine:
    text: str
    x: float
    y: float
    size: int
    weight: str
    color: str


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

    def _wrap(self, text: str, font: ImageFont.FreeTypeFont, max_width: float) -> List[str]:
        measure = font.getlength
        lines: List[str] = []
        for paragraph in text.strip().splitlines():
            words = paragraph.split()
            if not words:
                continue
            current = words[0]
            for word in words[1:]:
                candidate = f"{current} {word}"
                if measure(candidate) <= max_width:
                    current = candidate
                else:
                    lines.append(current)
                    current = word
            lines.append(current)
        return lines

    def _text_layout(self) -> Sequence[_TextLine]:
        cfg = self.config
        scale = self._scale()
        text_x = cfg.width * 0.518
        right = cfg.width - 50 * scale
        max_width = right - text_x

        title_size = max(24, round(48 * scale))
        while title_size > max(24, round(30 * scale)):
            if self._font(title_size, "bold").getlength(cfg.title) <= max_width:
                break
            title_size -= 1

        description_size = max(16, round(32 * scale))
        description_font = self._font(description_size)
        description_lines = self._wrap(cfg.description, description_font, max_width)
        while len(description_lines) > 3 and description_size > max(14, round(20 * scale)):
            description_size -= 1
            description_font = self._font(description_size)
            description_lines = self._wrap(cfg.description, description_font, max_width)

        lines: List[_TextLine] = [
            _TextLine(
                cfg.title,
                text_x,
                43 * scale,
                title_size,
                "bold",
                BRAND_COLORS["primary"],
            )
        ]
        description_y = 116 * scale
        line_height = description_size * 1.12
        for index, text in enumerate(description_lines[:3]):
            lines.append(
                _TextLine(
                    text,
                    text_x,
                    description_y + index * line_height,
                    description_size,
                    "regular",
                    BRAND_COLORS["secondary"],
                )
            )

        footer_y = cfg.height - 65 * scale
        lines.extend(
            [
                _TextLine(
                    cfg.product,
                    text_x + 44 * scale,
                    footer_y,
                    max(16, round(29 * scale)),
                    "regular",
                    BRAND_COLORS["primary"],
                ),
                _TextLine(
                    cfg.url,
                    right,
                    footer_y + 8 * scale,
                    max(12, round(20 * scale)),
                    "regular",
                    BRAND_COLORS["secondary"],
                ),
            ]
        )
        return lines

    def _latent_field_dots(self) -> Iterable[Tuple[float, float, float, float]]:
        """Yield a seeded activation field converging into controlled channels."""
        scale = self._scale()
        lane_count = round(self._variant(5, 13, 20))
        column_count = round(self._variant(6, 58, 78))
        gate_progress = self._variant(7, 0.42, 0.62)
        center_frequency = self._variant(8, 1.25, 2.35)
        center_phase = self._variant(9, -1.2, 0.5)
        turbulence_a = self._variant(10, 0.17, 0.34)
        turbulence_b = self._variant(11, 0.07, 0.16)

        for lane in range(lane_count):
            lane_offset = lane - (lane_count - 1) / 2
            for column in range(column_count):
                progress = column / (column_count - 1)
                x = (42 + progress * 660) * scale
                damping = 1 / (1 + math.exp((progress - gate_progress) * 13))
                center = 198 + 32 * math.sin(progress * math.pi * center_frequency + center_phase)
                turbulence = (
                    math.sin(column * turbulence_a + lane * 0.79) * 23
                    + math.sin(column * turbulence_b + lane * 1.31) * 13
                )
                y = (center + lane_offset * 8.6 + turbulence * damping) * scale
                edge_fade = min(progress / 0.12, (1 - progress) / 0.12, 1)
                boundary_glow = math.exp(-(((progress - gate_progress) / 0.13) ** 2))
                opacity = max(0.12, edge_fade * (0.34 + boundary_glow * 0.46))
                radius = (0.9 + boundary_glow * 0.65) * scale
                yield x, y, radius, opacity

        steering_phase = self._variant(12, 0, math.tau)
        for column in range(82):
            progress = column / 81
            x = (35 + progress * 680) * scale
            damping = 1 / (1 + math.exp((progress - gate_progress) * 13))
            y = (
                205
                + 31 * math.sin(progress * math.pi * center_frequency + center_phase)
                + math.sin(column * 0.27 + steering_phase) * 24 * damping
            ) * scale
            fade = min(progress / 0.08, (1 - progress) / 0.08, 1)
            yield x, y, 1.8 * scale, max(0.25, 0.95 * fade)

        gate_x = 42 + gate_progress * 660
        for row in range(23):
            if 9 <= row <= 13:
                continue
            y = 67 + row * 11.5
            yield gate_x * scale, y * scale, 1.25 * scale, 0.58

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

    def _routes_dots(self) -> Iterable[Tuple[float, float, float, float]]:
        """Yield a seeded provider graph with repository-specific topology."""
        tier_counts = (
            round(self._variant(5, 2, 5)),
            round(self._variant(6, 2, 4)),
            round(self._variant(7, 1, 4)),
            round(self._variant(8, 1, 3)),
        )
        tier_x = (55, 255, 475, 705)
        tiers = []
        seed_index = 9
        for tier, count in enumerate(tier_counts):
            spacing = 250 / max(1, count - 1)
            points = []
            for node in range(count):
                y = 73 + node * spacing + self._variant(seed_index, -24, 24)
                points.append((tier_x[tier], y))
                seed_index += 1
            tiers.append(points)
        for tier in range(len(tiers) - 1):
            destinations = tiers[tier + 1]
            for node_index, start in enumerate(tiers[tier]):
                target_index = round(
                    self._variant(seed_index + node_index + tier * 5, 0, len(destinations) - 1)
                )
                yield from self._line_dots(
                    start, destinations[target_index], opacity=0.38 + tier * 0.08
                )
                if len(destinations) > 1 and (node_index + tier) % 2 == 0:
                    second = destinations[(target_index + 1) % len(destinations)]
                    yield from self._line_dots(start, second, opacity=0.2)
        scale = self._scale()
        for tier_index, tier in enumerate(tiers):
            for x, y in tier:
                final = tier_index == len(tiers) - 1
                yield x * scale, y * scale, (5.2 if final else 3.5) * scale, 0.3
                yield x * scale, y * scale, (2.1 if final else 1.6) * scale, 0.98

    def _benchmark_dots(self) -> Iterable[Tuple[float, float, float, float]]:
        """Yield repository-seeded measurements and a target threshold."""
        scale = self._scale()
        bar_count = round(self._variant(5, 6, 11))
        values = tuple(self._variant(6 + index, 75, 285) for index in range(bar_count))
        baseline = self._variant(20, 310, 340)
        gap = 625 / max(1, bar_count - 1)
        for index, value in enumerate(values):
            x = 68 + index * gap
            rows = max(1, round(value / 8))
            for row in range(rows + 1):
                y = baseline - row * 8
                progress = row / rows
                opacity = 0.24 + progress * 0.62
                yield x * scale, y * scale, 1.55 * scale, opacity
                yield (x + 7) * scale, y * scale, 1.05 * scale, opacity * 0.6
        threshold = self._variant(21, 105, 175)
        yield from self._line_dots((45, threshold), (718, threshold), spacing=11, opacity=0.54)
        yield from self._line_dots((45, baseline), (718, baseline), spacing=9, opacity=0.28)

    def _waveform_dots(self) -> Iterable[Tuple[float, float, float, float]]:
        """Yield a repository-seeded layered neural waveform."""
        scale = self._scale()
        frequency_a = self._variant(5, 0.2, 0.42)
        frequency_b = self._variant(6, 0.52, 0.91)
        frequency_c = self._variant(7, 1.05, 1.55)
        phase = self._variant(8, 0, math.tau)
        strength = self._variant(9, 54, 86)
        band_count = round(self._variant(10, 3, 7))
        half_bands = band_count // 2
        for column in range(112):
            progress = column / 111
            x = 34 + progress * 690
            envelope = math.sin(progress * math.pi) ** self._variant(11, 0.55, 1.1)
            signal = (
                math.sin(column * frequency_a + phase)
                + 0.55 * math.sin(column * frequency_b + 0.8)
                + 0.25 * math.sin(column * frequency_c)
            )
            amplitude = signal * strength * envelope
            for band in range(-half_bands, half_bands + 1):
                y = 198 + amplitude + band * 7
                opacity = max(0.2, 0.9 - abs(band) * 0.15)
                yield x * scale, y * scale, max(0.8, 1.65 - abs(band) * 0.13) * scale, opacity
            mirror = 198 - amplitude * self._variant(12, 0.25, 0.58)
            yield x * scale, mirror * scale, 1.05 * scale, 0.28
        yield from self._line_dots((34, 198), (724, 198), spacing=12, opacity=0.22)

    def _orbit_dots(self) -> Iterable[Tuple[float, float, float, float]]:
        """Yield a uniquely seeded multi-agent orbital system."""
        scale = self._scale()
        center_x = self._variant(5, 325, 410)
        center_y = self._variant(6, 165, 225)
        orbit_count = round(self._variant(7, 2, 6))
        for orbit_index in range(orbit_count):
            radius_x = self._variant(8 + orbit_index * 3, 95, 285)
            radius_y = self._variant(9 + orbit_index * 3, 42, 135)
            rotation = self._variant(10 + orbit_index * 3, -0.85, 0.85)
            dot_count = round(self._variant(22 + orbit_index, 64, 110))
            for index in range(dot_count):
                angle = index / dot_count * math.tau
                raw_x = radius_x * math.cos(angle)
                raw_y = radius_y * math.sin(angle)
                x = center_x + raw_x * math.cos(rotation) - raw_y * math.sin(rotation)
                y = center_y + raw_x * math.sin(rotation) + raw_y * math.cos(rotation)
                opacity = 0.17 + 0.38 * (math.sin(angle + orbit_index) + 1) / 2
                yield x * scale, y * scale, 1.05 * scale, opacity
            node_angle = self._variant(27 + orbit_index, 0, math.tau)
            raw_x = radius_x * math.cos(node_angle)
            raw_y = radius_y * math.sin(node_angle)
            x = center_x + raw_x * math.cos(rotation) - raw_y * math.sin(rotation)
            y = center_y + raw_x * math.sin(rotation) + raw_y * math.cos(rotation)
            yield x * scale, y * scale, 4.5 * scale, 0.32
            yield x * scale, y * scale, 2 * scale, 0.96
        yield center_x * scale, center_y * scale, 7 * scale, 0.25
        yield center_x * scale, center_y * scale, 2.8 * scale, 1

    def _layers_dots(self) -> Iterable[Tuple[float, float, float, float]]:
        """Yield repository-seeded data layers linked by a retrieval spine."""
        scale = self._scale()
        layer_count = round(self._variant(5, 3, 6))
        start_y = self._variant(6, 72, 105)
        spacing_y = 250 / max(1, layer_count - 1)
        spine_x = self._variant(7, 335, 430)
        event_ys = []
        for layer in range(layer_count):
            center_y = start_y + layer * spacing_y
            inset = layer * self._variant(8, 10, 22)
            left = 78 + inset + self._variant(9 + layer, -12, 12)
            right = 690 - inset + self._variant(15 + layer, -12, 12)
            height = self._variant(21 + layer, 21, 38)
            corners = (
                (left, center_y),
                (spine_x, center_y - height),
                (right, center_y),
                (spine_x, center_y + height),
            )
            opacity = 0.26 + layer / max(1, layer_count - 1) * 0.4
            for index in range(4):
                yield from self._line_dots(
                    corners[index], corners[(index + 1) % 4], spacing=7, opacity=opacity
                )
            event_ys.append(center_y)
        yield from self._line_dots(
            (spine_x, 45), (spine_x, 350), spacing=10, opacity=0.72, radius=1.4
        )
        for y in event_ys:
            yield spine_x * scale, y * scale, 3.1 * scale, 0.95

    def _signal_dots(self) -> Iterable[Tuple[float, float, float, float]]:
        """Yield repository-seeded coordinated software signals."""
        scale = self._scale()
        lane_count = round(self._variant(5, 6, 12))
        frequency = self._variant(6, 1.4, 3.4)
        phase = self._variant(7, 0, math.tau)
        amplitude = self._variant(8, 11, 31)
        lane_spacing = 270 / max(1, lane_count - 1)
        for lane in range(lane_count):
            for column in range(76):
                progress = column / 75
                x = 34 + progress * 690
                y = (
                    63
                    + lane * lane_spacing
                    + math.sin(progress * math.pi * frequency + lane * 0.72 + phase) * amplitude
                    + math.sin(progress * math.pi) * (lane - (lane_count - 1) / 2) * 4
                )
                fade = min(progress / 0.1, (1 - progress) / 0.1, 1)
                yield x * scale, y * scale, 1.2 * scale, max(0.12, fade * 0.58)
        node_count = round(self._variant(9, 3, 7))
        for node in range(node_count):
            x = self._variant(10 + node * 2, 90, 680)
            y = self._variant(11 + node * 2, 75, 320)
            yield x * scale, y * scale, 4.2 * scale, 0.3
            yield x * scale, y * scale, 1.8 * scale, 0.95

    def _spark_dots(self) -> Iterable[Tuple[float, float, float, float]]:
        """Yield an asymmetric spark expanding into model activations."""
        scale = self._scale()
        center = (355 + self._variant(1, -28, 28), 198 + self._variant(2, -18, 18))
        ray_count = round(self._variant(3, 11, 17))
        phase = self._variant(4, 0, math.tau)
        for ray in range(ray_count):
            angle = phase + ray / ray_count * math.tau
            length = self._variant(5 + ray, 85, 275)
            for step in range(4, round(length / 7)):
                progress = step * 7 / length
                wobble = math.sin(step * 0.47 + ray) * 7 * progress
                x = center[0] + math.cos(angle) * step * 7 - math.sin(angle) * wobble
                y = center[1] + math.sin(angle) * step * 7 + math.cos(angle) * wobble
                opacity = max(0.12, (1 - progress) * 0.82)
                yield x * scale, y * scale, (1.7 - progress * 0.65) * scale, opacity
        yield center[0] * scale, center[1] * scale, 7 * scale, 0.25
        yield center[0] * scale, center[1] * scale, 2.8 * scale, 1

    def _forest_dots(self) -> Iterable[Tuple[float, float, float, float]]:
        """Yield a layered forest suggested by the Polish name Las."""
        scale = self._scale()
        for tree in range(11):
            x = 55 + tree * 64 + self._variant(tree, -12, 12)
            height = self._variant(tree + 11, 100, 245)
            base_y = 335
            top_y = base_y - height
            opacity = self._variant(tree + 22, 0.3, 0.75)
            yield from self._line_dots((x, base_y), (x, top_y), spacing=7, opacity=opacity)
            branch_count = max(4, round(height / 28))
            for branch in range(branch_count):
                progress = (branch + 1) / (branch_count + 1)
                y = base_y - height * progress
                width = (1 - progress) * self._variant(tree + 4, 38, 62)
                yield from self._line_dots((x, y), (x - width, y + 24), spacing=7, opacity=opacity)
                yield from self._line_dots((x, y), (x + width, y + 24), spacing=7, opacity=opacity)

    def _flock_dots(self) -> Iterable[Tuple[float, float, float, float]]:
        """Yield coordinated V formations for Stado and creator communities."""
        scale = self._scale()
        phase = self._variant(3, -0.3, 0.3)
        for flock in range(4):
            anchor_x = 110 + flock * 150 + self._variant(flock, -20, 20)
            anchor_y = 95 + flock * 66 + self._variant(flock + 8, -22, 22)
            wing = self._variant(flock + 16, 55, 95)
            for side in (-1, 1):
                for bird in range(9):
                    progress = bird / 8
                    x = anchor_x + progress * wing * 1.6
                    y = anchor_y + side * progress * wing * 0.48 + math.sin(bird + phase) * 3
                    yield x * scale, y * scale, 1.5 * scale, 0.4 + progress * 0.5
            yield anchor_x * scale, anchor_y * scale, 2.8 * scale, 0.95

    def _timeline_dots(self) -> Iterable[Tuple[float, float, float, float]]:
        """Yield a chronicle of events and documentary branches."""
        scale = self._scale()
        center_y = self._variant(2, 175, 225)
        yield from self._line_dots((45, center_y), (720, center_y), spacing=7, opacity=0.62)
        event_count = round(self._variant(3, 7, 11))
        for event in range(event_count):
            progress = (event + 1) / (event_count + 1)
            x = 45 + progress * 675
            direction = -1 if event % 2 == 0 else 1
            height = self._variant(event + 8, 45, 135)
            end_y = center_y + direction * height
            yield from self._line_dots((x, center_y), (x, end_y), spacing=8, opacity=0.48)
            yield x * scale, center_y * scale, 3 * scale, 0.95
            yield x * scale, end_y * scale, 2 * scale, 0.72

    def _gauge_dots(self) -> Iterable[Tuple[float, float, float, float]]:
        """Yield a calibrated gauge for Probierz and quality-control systems."""
        scale = self._scale()
        center_x, center_y = 370, 292
        radius = self._variant(1, 220, 275)
        for ring in range(3):
            adjusted = radius - ring * 20
            for index in range(86):
                angle = math.pi + index / 85 * math.pi
                x = center_x + adjusted * math.cos(angle)
                y = center_y + adjusted * math.sin(angle)
                yield x * scale, y * scale, (1.3 - ring * 0.12) * scale, 0.28 + ring * 0.12
        needle_angle = math.pi + self._variant(4, 0.18, 0.82) * math.pi
        target = (
            center_x + radius * 0.82 * math.cos(needle_angle),
            center_y + radius * 0.82 * math.sin(needle_angle),
        )
        yield from self._line_dots((center_x, center_y), target, spacing=6, opacity=0.9, radius=1.6)
        yield center_x * scale, center_y * scale, 6 * scale, 0.3
        yield center_x * scale, center_y * scale, 2.5 * scale, 1

    def _vault_dots(self) -> Iterable[Tuple[float, float, float, float]]:
        """Yield a secure layered vault and signed center."""
        scale = self._scale()
        center_x, center_y = 370, 198
        for layer in range(5):
            half_width = 285 - layer * 42
            half_height = 145 - layer * 21
            corners = (
                (center_x - half_width, center_y - half_height),
                (center_x + half_width, center_y - half_height),
                (center_x + half_width, center_y + half_height),
                (center_x - half_width, center_y + half_height),
            )
            for index in range(4):
                yield from self._line_dots(
                    corners[index],
                    corners[(index + 1) % 4],
                    spacing=8 + layer,
                    opacity=0.22 + layer * 0.1,
                )
        for index in range(48):
            angle = index / 48 * math.tau
            radius = 40 + math.sin(index * 0.7) * 3
            yield (
                (center_x + math.cos(angle) * radius) * scale,
                (center_y + math.sin(angle) * radius) * scale,
                1.4 * scale,
                0.72,
            )
        yield center_x * scale, center_y * scale, 3.2 * scale, 1

    def _focus_dots(self) -> Iterable[Tuple[float, float, float, float]]:
        """Yield many signals collapsing into one focal point."""
        scale = self._scale()
        target_x = self._variant(1, 315, 430)
        target_y = self._variant(2, 155, 240)
        for source in range(16):
            edge = source % 4
            progress = source / 15
            if edge == 0:
                start = (35, 45 + progress * 300)
            elif edge == 1:
                start = (720, 45 + progress * 300)
            elif edge == 2:
                start = (55 + progress * 640, 45)
            else:
                start = (55 + progress * 640, 350)
            yield from self._line_dots(start, (target_x, target_y), spacing=10, opacity=0.34)
        yield target_x * scale, target_y * scale, 11 * scale, 0.17
        yield target_x * scale, target_y * scale, 4.5 * scale, 1

    def _scan_dots(self) -> Iterable[Tuple[float, float, float, float]]:
        """Yield a code-analysis grid with a moving scan line and finding."""
        scale = self._scale()
        scan_x = self._variant(3, 210, 585)
        finding_y = self._variant(4, 95, 295)
        for column in range(28):
            x = 48 + column * 24
            for row in range(13):
                y = 54 + row * 24
                distance = abs(x - scan_x)
                opacity = 0.18 + max(0, 1 - distance / 95) * 0.55
                yield x * scale, y * scale, 1.1 * scale, opacity
        yield from self._line_dots((scan_x, 42), (scan_x, 350), spacing=6, opacity=0.88, radius=1.5)
        for index in range(36):
            angle = index / 36 * math.tau
            radius = 26
            yield (
                (scan_x + math.cos(angle) * radius) * scale,
                (finding_y + math.sin(angle) * radius) * scale,
                1.5 * scale,
                0.85,
            )

    def _fracture_dots(self) -> Iterable[Tuple[float, float, float, float]]:
        """Yield broken constraints and diverging response paths."""
        center_x = self._variant(1, 330, 420)
        crack = (
            (center_x - 45, 35),
            (center_x + 18, 105),
            (center_x - 26, 166),
            (center_x + 34, 231),
            (center_x - 12, 292),
            (center_x + 48, 360),
        )
        for index in range(len(crack) - 1):
            yield from self._line_dots(crack[index], crack[index + 1], spacing=5, opacity=0.92)
        for shard in range(13):
            origin = crack[shard % len(crack)]
            direction = -1 if shard % 2 == 0 else 1
            length = self._variant(shard + 8, 65, 245)
            end = (
                origin[0] + direction * length,
                origin[1] + self._variant(shard + 20, -55, 55),
            )
            yield from self._line_dots(origin, end, spacing=8, opacity=0.28 + shard % 3 * 0.1)

    def _gate_dots(self) -> Iterable[Tuple[float, float, float, float]]:
        """Yield routed signals crossing a controlled gate."""
        scale = self._scale()
        gate_x = self._variant(2, 330, 430)
        gap_center = self._variant(3, 150, 245)
        for pillar_x in (gate_x - 28, gate_x + 28):
            for row in range(34):
                y = 30 + row * 10
                if abs(y - gap_center) < 42:
                    continue
                yield pillar_x * scale, y * scale, 1.6 * scale, 0.7
        for route in range(9):
            source_y = 58 + route * 34
            target_y = gap_center + (route - 4) * 10
            exit_y = 78 + route * 29 + self._variant(route + 7, -14, 14)
            yield from self._line_dots(
                (40, source_y), (gate_x - 32, target_y), spacing=8, opacity=0.3
            )
            yield from self._line_dots(
                (gate_x + 32, target_y), (720, exit_y), spacing=8, opacity=0.52
            )

    def _art_dots(self) -> Iterable[Tuple[float, float, float, float]]:
        renderers = {
            "benchmark-left": self._benchmark_dots,
            "flock-left": self._flock_dots,
            "focus-left": self._focus_dots,
            "forest-left": self._forest_dots,
            "fracture-left": self._fracture_dots,
            "gate-left": self._gate_dots,
            "gauge-left": self._gauge_dots,
            "latent-field-left": self._latent_field_dots,
            "layers-left": self._layers_dots,
            "orbit-left": self._orbit_dots,
            "routes-left": self._routes_dots,
            "scan-left": self._scan_dots,
            "signal-left": self._signal_dots,
            "spark-left": self._spark_dots,
            "timeline-left": self._timeline_dots,
            "vault-left": self._vault_dots,
            "waveform-left": self._waveform_dots,
        }
        center_x = 380 * self._scale()
        center_y = 198 * self._scale()
        stretch_x = self._variant(0, 0.9, 1.1)
        stretch_y = self._variant(1, 0.88, 1.12)
        shear = self._variant(2, -0.06, 0.06)
        radius_scale = self._variant(3, 0.88, 1.16)
        opacity_scale = self._variant(4, 0.88, 1.08)
        for x, y, radius, opacity in renderers[self.config.layout]():
            relative_x = x - center_x
            relative_y = y - center_y
            yield (
                center_x + relative_x * stretch_x,
                center_y + relative_y * stretch_y + relative_x * shear,
                radius * radius_scale,
                min(1, opacity * opacity_scale),
            )

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
        for x, y, radius, opacity in self._art_dots():
            base = tuple(int(BRAND_COLORS["primary"][i : i + 2], 16) for i in (1, 3, 5))
            color = tuple(round(channel * opacity) for channel in base)
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)

        self._draw_logo(image)
        for line in self._text_layout():
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
        for x, y, radius, opacity in self._art_dots():
            parts.append(
                f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{radius:.2f}" fill="{BRAND_COLORS["primary"]}" opacity="{opacity:.3f}"/>'
            )

        logo_x, logo_y, logo_size, product_top = self._footer_geometry()
        logo = base64.b64encode(self._logo_bytes).decode("ascii")
        parts.append(
            f'<image x="{logo_x:.2f}" y="{logo_y:.2f}" width="{logo_size:.2f}" height="{logo_size:.2f}" href="data:image/png;base64,{logo}"/>'
        )
        for line in self._text_layout():
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
