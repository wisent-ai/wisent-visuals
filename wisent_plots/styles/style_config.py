"""Style configuration definitions for Wisent plots.

This module contains style presets based on Wisent's Figma design system.
"""

from typing import Dict, Any

# Style definitions based on Figma Visual Identity
STYLES: Dict[int, Dict[str, Any]] = {
    1: {
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
    },
}


def get_style(style_number: int) -> Dict[str, Any]:
    """Get style configuration by number.

    Args:
        style_number: Style number (currently only 1 is available)

    Returns:
        Style configuration dictionary

    Raises:
        ValueError: If style_number is not available
    """
    if style_number not in STYLES:
        available = ", ".join(str(k) for k in STYLES.keys())
        raise ValueError(f"Style {style_number} not found. Available styles: {available}")
    return STYLES[style_number]


def list_styles() -> None:
    """Print available styles with their names."""
    print("Available Wisent plot styles:")
    for num, style in STYLES.items():
        print(f"  {num}: {style['name']}")
