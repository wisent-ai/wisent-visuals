"""Area chart configuration objects; public IDs belong to style_config.STYLES."""

from typing import Any, Dict

EDGE: Dict[str, Any] = {
    "name": "Area Chart - Edge - Style 1",
    "colors": {
        "primary": "#B0E3B3",  # Light green (One)
        "secondary": "#90B892",  # Medium green (Two)
        "accent": "#5A715B",  # Dark green (Three)
        "background": "#121212",  # Dark background (gray-950)
        "text": "#C5FFC8",  # Brand accent green for title
        "grid": "#2D3130",  # Grid lines (gray-800)
        "legend_text": "#769978",  # Legend text (green-600)
    },
    "font": {
        "family": "Hubot Sans",  # Hubot Sans from Figma
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
        "primary": "#B0E3B3",  # Light green (One)
        "secondary": "#90B892",  # Medium green (Two)
        "accent": "#5A715B",  # Dark green (Three)
        "background": "#121212",  # Dark background (gray-950)
        "text": "#C5FFC8",  # Brand accent green for title
        "grid": "#2D3130",  # Grid lines (gray-800)
        "legend_text": "#769978",  # Legend text (green-600)
    },
    "font": {
        "family": "Hubot Sans",  # Hubot Sans from Figma
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
        "primary": "#B0E3B3",  # Light green (One)
        "secondary": "#90B892",  # Medium green (Two)
        "accent": "#5A715B",  # Dark green (Three)
        "background": "#121212",  # Dark background (gray-950)
        "text": "#C5FFC8",  # Brand accent green for title
        "grid": "#2D3130",  # Grid lines (gray-800)
        "legend_text": "#769978",  # Legend text (green-600)
    },
    "font": {
        "family": "Hubot Sans",  # Hubot Sans from Figma
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
        "primary": "#B0E3B3",  # Light green (One)
        "secondary": "#90B892",  # Medium green (Two)
        "accent": "#5A715B",  # Dark green (Three)
        "background": "#121212",  # Dark background (gray-950)
        "text": "#C5FFC8",  # Brand accent green for title
        "grid": "#2D3130",  # Grid lines (gray-800)
        "legend_text": "#769978",  # Legend text (green-600)
    },
    "font": {
        "family": "Hubot Sans",  # Hubot Sans from Figma
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
        "primary": "#C5FFC8",  # Brand accent green (One) from Figma
        "secondary": "#FA5A46",  # Error red-500 (Two) from Figma
        "accent": "#B19ECC",  # Character purple-500 (Three) from Figma
        "background": "#121212",  # Dark background (gray-950)
        "text": "#C5FFC8",  # Brand accent green for title
        "grid": "#2D3130",  # Grid lines (gray-800)
        "legend_text": "#769978",  # Legend text (green-600)
    },
    "font": {
        "family": "Hubot Sans",  # Hubot Sans from Figma
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
