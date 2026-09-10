"""Dark and light line-chart configurations; public IDs stay in the registry."""

from typing import Any, Dict

DARK_PALETTE: Dict[str, Any] = {
    "name": "Line Chart - Solid Palette",
    "colors": {
        "primary": "#C5FFC8",  # Brand accent green
        "secondary": "#FA5A46",  # Error red-500
        "accent": "#B19ECC",  # Character purple-500
        "background": "#121212",  # Dark background
        "text": "#C5FFC8",  # Brand accent green for title
        "grid": "#2D3130",  # Grid lines
        "legend_text": "#769978",  # Legend text
    },
    "font": {
        "family": "Hubot Sans",
        "size": {
            "title": 20,
            "label": 14,
            "tick": 14,
        },
        "weight": {
            "title": 400,
            "label": 400,
        },
    },
    "line": {
        "width": 2.0,
        "style": "-",
        "alpha": 1.0,
    },
    "markers": {
        "show": False,
        "size": 11,
    },
    "grid": {
        "alpha": 1.0,
        "linestyle": "--",
        "linewidth": 1.0,
    },
    "spacing": {
        "title_pad": 10,
        "label_pad": 10,
    },
}

DARK_MARKERS: Dict[str, Any] = {
    "name": "Line Chart - Solid Color (with markers)",
    "colors": {
        "primary": "#C5FFC8",  # Brand accent green
        "secondary": "#FA5A46",  # Error red-500
        "accent": "#B19ECC",  # Character purple-500
        "background": "#121212",  # Dark background
        "text": "#C5FFC8",  # Brand accent green for title
        "grid": "#2D3130",  # Grid lines
        "legend_text": "#769978",  # Legend text
    },
    "font": {
        "family": "Hubot Sans",
        "size": {
            "title": 20,
            "label": 14,
            "tick": 14,
        },
        "weight": {
            "title": 400,
            "label": 400,
        },
    },
    "line": {
        "width": 2.0,
        "style": "-",
        "alpha": 1.0,
    },
    "markers": {
        "show": True,
        "size": 11,
        "shapes": ["circle", "circle", "circle"],  # Same shape for all
    },
    "grid": {
        "alpha": 1.0,
        "linestyle": "--",
        "linewidth": 1.0,
    },
    "spacing": {
        "title_pad": 10,
        "label_pad": 10,
    },
}

DARK_SHAPES: Dict[str, Any] = {
    "name": "Line Chart - Solid Shapes (different markers)",
    "colors": {
        "primary": "#FFFFFF",  # White for better contrast
        "secondary": "#FA5A46",  # Error red-500
        "accent": "#FF8C00",  # Orange
        "quaternary": "#90EE90",  # Light green
        "quinary": "#87CEEB",  # Sky blue
        "background": "#121212",  # Dark background
        "text": "#C5FFC8",  # Brand accent green for title
        "grid": "#2D3130",  # Grid lines
        "legend_text": "#769978",  # Legend text
    },
    "font": {
        "family": "Hubot Sans",
        "size": {
            "title": 20,
            "label": 14,
            "tick": 14,
        },
        "weight": {
            "title": 400,
            "label": 400,
        },
    },
    "line": {
        "width": 2.0,
        "style": "-",
        "alpha": 1.0,
    },
    "markers": {
        "show": True,
        "size": 11,
        "shapes": ["circle", "triangle", "square", "diamond", "triangle"],  # Different shapes
    },
    "grid": {
        "alpha": 1.0,
        "linestyle": "-",
        "linewidth": 1.0,
    },
    "spacing": {
        "title_pad": 10,
        "label_pad": 10,
    },
}

LIGHT_PALETTE: Dict[str, Any] = {
    "name": "Line Chart - Solid Palette (White Theme)",
    "colors": {
        "primary": "#333333",  # Dark gray/black for lines
        "secondary": "#666666",  # Medium gray
        "accent": "#999999",  # Light gray
        "background": "#FFFFFF",  # White background
        "text": "#000000",  # Black text for title
        "grid": "#E5E5E5",  # Light gray grid lines
        "legend_text": "#666666",  # Medium gray legend text
    },
    "font": {
        "family": "Hubot Sans",
        "size": {
            "title": 20,
            "label": 14,
            "tick": 14,
        },
        "weight": {
            "title": 400,
            "label": 400,
        },
    },
    "line": {
        "width": 2.0,
        "style": "-",
        "alpha": 1.0,
    },
    "markers": {
        "show": False,
        "size": 11,
    },
    "grid": {
        "alpha": 1.0,
        "linestyle": "-",
        "linewidth": 1.0,
    },
    "spacing": {
        "title_pad": 10,
        "label_pad": 10,
    },
}

LIGHT_MARKERS: Dict[str, Any] = {
    "name": "Line Chart - Solid Color (White Theme, with markers)",
    "colors": {
        "primary": "#00C896",  # Teal/green
        "secondary": "#FF6B6B",  # Coral red
        "accent": "#C8C8C8",  # Light gray
        "background": "#FFFFFF",  # White background
        "text": "#000000",  # Black text for title
        "grid": "#E5E5E5",  # Light gray grid lines
        "legend_text": "#666666",  # Medium gray legend text
    },
    "font": {
        "family": "Hubot Sans",
        "size": {
            "title": 20,
            "label": 14,
            "tick": 14,
        },
        "weight": {
            "title": 400,
            "label": 400,
        },
    },
    "line": {
        "width": 2.0,
        "style": "-",
        "alpha": 1.0,
    },
    "markers": {
        "show": True,
        "size": 11,
        "shapes": ["circle", "circle", "circle"],  # Same shape for all
    },
    "grid": {
        "alpha": 1.0,
        "linestyle": "-",
        "linewidth": 1.0,
    },
    "spacing": {
        "title_pad": 10,
        "label_pad": 10,
    },
}

LIGHT_SHAPES: Dict[str, Any] = {
    "name": "Line Chart - Solid Shapes (White Theme, different markers)",
    "colors": {
        "primary": "#000000",  # Black
        "secondary": "#FF6B6B",  # Coral red
        "accent": "#FF8C00",  # Orange
        "quaternary": "#C8C8FF",  # Light purple
        "quinary": "#C8C8C8",  # Light gray
        "background": "#FFFFFF",  # White background
        "text": "#000000",  # Black text for title
        "grid": "#E5E5E5",  # Light gray grid lines
        "legend_text": "#666666",  # Medium gray legend text
    },
    "font": {
        "family": "Hubot Sans",
        "size": {
            "title": 20,
            "label": 14,
            "tick": 14,
        },
        "weight": {
            "title": 400,
            "label": 400,
        },
    },
    "line": {
        "width": 2.0,
        "style": "-",
        "alpha": 1.0,
    },
    "markers": {
        "show": True,
        "size": 11,
        "shapes": ["circle", "triangle", "square", "diamond", "triangle"],  # Different shapes
    },
    "grid": {
        "alpha": 1.0,
        "linestyle": "-",
        "linewidth": 1.0,
    },
    "spacing": {
        "title_pad": 10,
        "label_pad": 10,
    },
}
