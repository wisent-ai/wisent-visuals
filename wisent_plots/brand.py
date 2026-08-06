"""Canonical Wisent visual identity tokens."""

from types import MappingProxyType

BRAND_COLORS = MappingProxyType(
    {
        "background": "#050605",
        "surface": "#121212",
        "primary": "#C5FFC8",
        "secondary": "#B0E3B3",
        "tertiary": "#90B892",
        "deep": "#5A715B",
        "muted": "#769978",
        "grid": "#2D3130",
    }
)

FONT_FAMILY = "Hubot Sans"

__all__ = ["BRAND_COLORS", "FONT_FAMILY"]
