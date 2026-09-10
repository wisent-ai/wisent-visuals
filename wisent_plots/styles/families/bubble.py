"""Bubble chart color configurations; public IDs stay in the registry."""

from typing import Any, Dict

from wisent_plots.brand import BRAND_COLORS, FONT_FAMILY

BRAND: Dict[str, Any] = {
    "name": "Bubble Chart - Brand Colors (Dark Theme)",
    "colors": {
        "background": BRAND_COLORS["surface"],
        "text": BRAND_COLORS["primary"],
        "grid": BRAND_COLORS["grid"],
        "legend_text": BRAND_COLORS["muted"],
        "bubble1": "#FA5A46",  # Red
        "bubble2": "#FF8C00",  # Orange
        "bubble3": "#FFD700",  # Yellow
        "bubble4": BRAND_COLORS["primary"],  # Green
        "bubble5": "#00CED1",  # Cyan
        "bubble6": "#87CEEB",  # Sky blue
        "bubble7": "#B19ECC",  # Purple
        "bubble8": "#FFB6C1",  # Light pink
        "bubble9": "#A9A9A9",  # Gray
    },
    "font": {
        "family": FONT_FAMILY,
        "size": {"title": 20, "label": 14, "tick": 12},
        "weight": {"title": 400, "label": 400},
    },
}

BLACK: Dict[str, Any] = {
    "name": "Bubble Chart - Black Theme (Grayscale)",
    "colors": {
        "background": BRAND_COLORS["surface"],
        "text": "#FFFFFF",
        "grid": BRAND_COLORS["grid"],
        "legend_text": "#A9A9A9",
        "bubble1": "#FFFFFF",  # White
        "bubble2": "#E0E0E0",  # Light gray
        "bubble3": "#C8C8C8",  # Medium-light gray
        "bubble4": "#A9A9A9",  # Gray
        "bubble5": "#909090",  # Medium gray
        "bubble6": "#787878",  # Medium-dark gray
        "bubble7": "#606060",  # Dark gray
        "bubble8": "#484848",  # Darker gray
        "bubble9": "#303030",  # Very dark gray
    },
    "font": {
        "family": FONT_FAMILY,
        "size": {"title": 20, "label": 14, "tick": 12},
        "weight": {"title": 400, "label": 400},
    },
}

WHITE: Dict[str, Any] = {
    "name": "Bubble Chart - White Theme (Light Background)",
    "colors": {
        "background": "#FFFFFF",
        "text": "#000000",
        "grid": "#E5E5E5",
        "legend_text": "#666666",
        "bubble1": "#FA5A46",  # Red
        "bubble2": "#FF8C00",  # Orange
        "bubble3": "#FFD700",  # Yellow
        "bubble4": "#00C896",  # Teal
        "bubble5": "#00CED1",  # Cyan
        "bubble6": "#87CEEB",  # Sky blue
        "bubble7": "#B19ECC",  # Purple
        "bubble8": "#FFB6C1",  # Light pink
        "bubble9": "#666666",  # Medium gray
    },
    "font": {
        "family": FONT_FAMILY,
        "size": {"title": 20, "label": 14, "tick": 12},
        "weight": {"title": 400, "label": 400},
    },
}
