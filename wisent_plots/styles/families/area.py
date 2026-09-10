"""Area chart configuration objects; public IDs belong to style_config.STYLES."""

from typing import Any, Dict

from wisent_plots.brand import BRAND_COLORS, FONT_FAMILY

EDGE: Dict[str, Any] = {
    "name": "Area Chart - Edge - Style 1",
    "colors": {
        "primary": BRAND_COLORS["secondary"],  # Light green (One)
        "secondary": BRAND_COLORS["tertiary"],  # Medium green (Two)
        "accent": BRAND_COLORS["deep"],  # Dark green (Three)
        "background": BRAND_COLORS["surface"],  # Dark background (gray-950)
        "text": BRAND_COLORS["primary"],  # Brand accent green for title
        "grid": BRAND_COLORS["grid"],  # Grid lines (gray-800)
        "legend_text": BRAND_COLORS["muted"],  # Legend text (green-600)
    },
    "font": {
        "family": FONT_FAMILY,  # Hubot Sans from Figma
        "size": {
            "title": 20,  # Text xl (20px)
            "label": 14,  # Text sm (14px)
            "tick": 14,  # Text sm (14px)
        },
        "weight": {
            "title": 400,  # Regular weight
            "label": 400,  # Regular weight
        },
    },
    "line": {
        "width": 2.0,
        "style": "-",  # solid
        "alpha": 1.0,
    },
    "fill": {
        "alpha": 0.95,  # Nearly solid fill
    },
    "grid": {
        "alpha": 1.0,
        "linestyle": "--",  # Dashed grid lines
        "linewidth": 1.0,
    },
    "edge": {
        "width": 2.0,  # Edge enabled
        "color": "darker",  # Slightly darker edge
    },
    "spacing": {
        "title_pad": 10,
        "label_pad": 10,
    },
}

GRADIENT: Dict[str, Any] = {
    "name": "Area Chart - Edge - Style 2 (Gradient)",
    "colors": {
        "primary": BRAND_COLORS["secondary"],  # Light green (One)
        "secondary": BRAND_COLORS["tertiary"],  # Medium green (Two)
        "accent": BRAND_COLORS["deep"],  # Dark green (Three)
        "background": BRAND_COLORS["surface"],  # Dark background (gray-950)
        "text": BRAND_COLORS["primary"],  # Brand accent green for title
        "grid": BRAND_COLORS["grid"],  # Grid lines (gray-800)
        "legend_text": BRAND_COLORS["muted"],  # Legend text (green-600)
    },
    "font": {
        "family": FONT_FAMILY,  # Hubot Sans from Figma
        "size": {
            "title": 20,  # Text xl (20px)
            "label": 14,  # Text sm (14px)
            "tick": 14,  # Text sm (14px)
        },
        "weight": {
            "title": 400,  # Regular weight
            "label": 400,  # Regular weight
        },
    },
    "line": {
        "width": 2.0,
        "style": "-",  # solid
        "alpha": 1.0,
    },
    "fill": {
        "alpha": 0.95,  # Nearly solid fill
    },
    "grid": {
        "alpha": 1.0,
        "linestyle": "--",  # Dashed grid lines
        "linewidth": 1.0,
    },
    "edge": {
        "width": 2.0,  # Edge enabled
        "color": "darker",  # Slightly darker edge
    },
    "spacing": {
        "title_pad": 10,
        "label_pad": 10,
    },
}

PATTERN: Dict[str, Any] = {
    "name": "Area Chart - Edge - Style 3 (Pattern)",
    "colors": {
        "primary": BRAND_COLORS["secondary"],  # Light green (One)
        "secondary": BRAND_COLORS["tertiary"],  # Medium green (Two)
        "accent": BRAND_COLORS["deep"],  # Dark green (Three)
        "background": BRAND_COLORS["surface"],  # Dark background (gray-950)
        "text": BRAND_COLORS["primary"],  # Brand accent green for title
        "grid": BRAND_COLORS["grid"],  # Grid lines (gray-800)
        "legend_text": BRAND_COLORS["muted"],  # Legend text (green-600)
    },
    "font": {
        "family": FONT_FAMILY,  # Hubot Sans from Figma
        "size": {
            "title": 20,  # Text xl (20px)
            "label": 14,  # Text sm (14px)
            "tick": 14,  # Text sm (14px)
        },
        "weight": {
            "title": 400,  # Regular weight
            "label": 400,  # Regular weight
        },
    },
    "line": {
        "width": 2.0,
        "style": "-",  # solid
        "alpha": 1.0,
    },
    "fill": {
        "alpha": 0.95,  # Nearly solid fill
    },
    "grid": {
        "alpha": 1.0,
        "linestyle": "--",  # Dashed grid lines
        "linewidth": 1.0,
    },
    "edge": {
        "width": 2.0,  # Edge enabled
        "color": "darker",  # Slightly darker edge
    },
    "spacing": {
        "title_pad": 10,
        "label_pad": 10,
    },
}

TWO_PATTERNS: Dict[str, Any] = {
    "name": "Area Chart - Edge - Style 4 (2 Patterns)",
    "colors": {
        "primary": BRAND_COLORS["secondary"],  # Light green (One)
        "secondary": BRAND_COLORS["tertiary"],  # Medium green (Two)
        "accent": BRAND_COLORS["deep"],  # Dark green (Three)
        "background": BRAND_COLORS["surface"],  # Dark background (gray-950)
        "text": BRAND_COLORS["primary"],  # Brand accent green for title
        "grid": BRAND_COLORS["grid"],  # Grid lines (gray-800)
        "legend_text": BRAND_COLORS["muted"],  # Legend text (green-600)
    },
    "font": {
        "family": FONT_FAMILY,  # Hubot Sans from Figma
        "size": {
            "title": 20,  # Text xl (20px)
            "label": 14,  # Text sm (14px)
            "tick": 14,  # Text sm (14px)
        },
        "weight": {
            "title": 400,  # Regular weight
            "label": 400,  # Regular weight
        },
    },
    "line": {
        "width": 2.0,
        "style": "-",  # solid
        "alpha": 1.0,
    },
    "fill": {
        "alpha": 0.95,  # Nearly solid fill
    },
    "grid": {
        "alpha": 1.0,
        "linestyle": "--",  # Dashed grid lines
        "linewidth": 1.0,
    },
    "edge": {
        "width": 2.0,  # Edge enabled
        "color": "darker",  # Slightly darker edge
    },
    "spacing": {
        "title_pad": 10,
        "label_pad": 10,
    },
}

SOLID_COLORS: Dict[str, Any] = {
    "name": "Area Chart - Edge - Solid Colors",
    "colors": {
        "primary": BRAND_COLORS["primary"],  # Brand accent green (One) from Figma
        "secondary": "#FA5A46",  # Error red-500 (Two) from Figma
        "accent": "#B19ECC",  # Character purple-500 (Three) from Figma
        "background": BRAND_COLORS["surface"],  # Dark background (gray-950)
        "text": BRAND_COLORS["primary"],  # Brand accent green for title
        "grid": BRAND_COLORS["grid"],  # Grid lines (gray-800)
        "legend_text": BRAND_COLORS["muted"],  # Legend text (green-600)
    },
    "font": {
        "family": FONT_FAMILY,  # Hubot Sans from Figma
        "size": {
            "title": 20,  # Text xl (20px)
            "label": 14,  # Text sm (14px)
            "tick": 14,  # Text sm (14px)
        },
        "weight": {
            "title": 400,  # Regular weight
            "label": 400,  # Regular weight
        },
    },
    "line": {
        "width": 0,  # No edge lines for solid color style
        "style": "-",
        "alpha": 0,
    },
    "fill": {
        "alpha": 1.0,  # Fully solid colors
        "type": "solid",  # Use solid colors instead of opacity variations
    },
    "grid": {
        "alpha": 1.0,
        "linestyle": "--",  # Dashed grid lines
        "linewidth": 1.0,
    },
    "edge": {
        "width": 0,  # No edge for solid color style
        "color": None,
    },
    "spacing": {
        "title_pad": 10,
        "label_pad": 10,
    },
}
