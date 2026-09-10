"""Banner text measurement, wrapping and placement through the bundled fonts."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Sequence

from PIL import ImageFont

from ..brand import BRAND_COLORS

if TYPE_CHECKING:
    from ..banner import Banner


@dataclass(frozen=True)
class _TextLine:
    text: str
    x: float
    y: float
    size: int
    weight: str
    color: str


def _wrap(text: str, font: ImageFont.FreeTypeFont, max_width: float) -> List[str]:
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


def text_layout(banner: "Banner") -> Sequence[_TextLine]:
    cfg = banner.config
    scale = banner._scale()
    text_x = cfg.width * 0.518
    right = cfg.width - 50 * scale
    max_width = right - text_x

    title_size = max(24, round(48 * scale))
    while title_size > max(24, round(30 * scale)):
        if banner._font(title_size, "bold").getlength(cfg.title) <= max_width:
            break
        title_size -= 1

    description_size = max(16, round(32 * scale))
    description_font = banner._font(description_size)
    description_lines = _wrap(cfg.description, description_font, max_width)
    while len(description_lines) > 3 and description_size > max(14, round(20 * scale)):
        description_size -= 1
        description_font = banner._font(description_size)
        description_lines = _wrap(cfg.description, description_font, max_width)

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
