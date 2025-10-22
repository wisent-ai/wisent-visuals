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
    2: {
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
    },
    3: {
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
    },
    4: {
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
    },
    5: {
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
    },
    # Line Chart Styles
    10: {
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
    },
    11: {
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
    },
    12: {
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
    },
    # White/Light Theme Line Chart Styles
    20: {
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
    },
    21: {
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
    },
    22: {
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
    },
    # Bubble Chart Styles
    30: {
        "name": "Bubble Chart - Brand Colors (Dark Theme)",
        "colors": {
            "background": "#121212",
            "text": "#C5FFC8",
            "grid": "#2D3130",
            "legend_text": "#769978",
            "bubble1": "#FA5A46",  # Red
            "bubble2": "#FF8C00",  # Orange
            "bubble3": "#FFD700",  # Yellow
            "bubble4": "#C5FFC8",  # Green
            "bubble5": "#00CED1",  # Cyan
            "bubble6": "#87CEEB",  # Sky blue
            "bubble7": "#B19ECC",  # Purple
            "bubble8": "#FFB6C1",  # Light pink
            "bubble9": "#A9A9A9",  # Gray
        },
        "font": {
            "family": "Hubot Sans",
            "size": {"title": 20, "label": 14, "tick": 12},
            "weight": {"title": 400, "label": 400},
        },
    },
    31: {
        "name": "Bubble Chart - Black Theme (Grayscale)",
        "colors": {
            "background": "#121212",
            "text": "#FFFFFF",
            "grid": "#2D3130",
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
            "family": "Hubot Sans",
            "size": {"title": 20, "label": 14, "tick": 12},
            "weight": {"title": 400, "label": 400},
        },
    },
    32: {
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
            "family": "Hubot Sans",
            "size": {"title": 20, "label": 14, "tick": 12},
            "weight": {"title": 400, "label": 400},
        },
    },
    # Pie Chart Styles (40-42)
    40: {
        "name": "Pie Chart - Brand Colors",
        "colors": {
            "background": "#121212",  # Dark background
            "title": "#C5FFC8",  # Brand accent green
            "legend_text": "#769978",  # Green-600
            "center_text": "#FFFFFF",  # White for center label
            "separator": "#000000",  # Black lines between slices
            "slice1": "#C5FFC8",  # Brand accent green
            "slice2": "#FA5A46",  # Error red-500
            "slice3": "#FFB366",  # Warning orange-400
            "slice4": "#FFD699",  # Warning orange-300
            "slice5": "#B19ECC",  # Character purple-500
            "slice6": "#A4C2F4",  # Accent blue-400
        },
        "font": {
            "family": "Hubot Sans",
            "size": {"title": 16, "label": 12, "center": 12},
            "weight": {"title": 400, "label": 400, "center": 400},
        },
        "pie": {
            "inner_radius": 0.55,  # Donut chart (55% inner radius)
            "separator_width": 2,
        },
    },
    41: {
        "name": "Pie Chart - Black/Grayscale Theme",
        "colors": {
            "background": "#121212",  # Dark background
            "title": "#FFFFFF",  # White title
            "legend_text": "#A9A9A9",  # Gray legend
            "center_text": "#FFFFFF",  # White for center label
            "separator": "#000000",  # Black lines between slices
            "slice1": "#FFFFFF",  # White
            "slice2": "#E0E0E0",  # Light gray
            "slice3": "#C8C8C8",  # Medium-light gray
            "slice4": "#A9A9A9",  # Medium gray
            "slice5": "#909090",  # Medium-dark gray
            "slice6": "#787878",  # Dark gray
        },
        "font": {
            "family": "Hubot Sans",
            "size": {"title": 16, "label": 12, "center": 12},
            "weight": {"title": 400, "label": 400, "center": 400},
        },
        "pie": {
            "inner_radius": 0.55,  # Donut chart (55% inner radius)
            "separator_width": 2,
        },
    },
    42: {
        "name": "Pie Chart - White Theme",
        "colors": {
            "background": "#FFFFFF",  # White background
            "title": "#000000",  # Black title
            "legend_text": "#666666",  # Gray legend
            "center_text": "#000000",  # Black for center label
            "separator": "#FFFFFF",  # White lines between slices (inverted)
            "slice1": "#303030",  # Very dark gray
            "slice2": "#484848",  # Dark gray
            "slice3": "#606060",  # Medium-dark gray
            "slice4": "#787878",  # Medium gray
            "slice5": "#909090",  # Medium-light gray
            "slice6": "#C8C8C8",  # Light gray
        },
        "font": {
            "family": "Hubot Sans",
            "size": {"title": 16, "label": 12, "center": 12},
            "weight": {"title": 400, "label": 400, "center": 400},
        },
        "pie": {
            "inner_radius": 0.55,  # Donut chart (55% inner radius)
            "separator_width": 2,
        },
    },
    # Radar Chart Styles (50-52)
    50: {
        "name": "Radar Chart - Brand Colors",
        "colors": {
            "background": "#121212",  # Dark background
            "title": "#C5FFC8",  # Brand accent green
            "legend_text": "#769978",  # Green-600
            "axis_text": "#A9A9A9",  # Gray for axis labels
            "grid": "#2D3130",  # Dark grid lines
            "axis": "#4A4A4A",  # Lighter axis lines
            "area1": "#90B892",  # Medium green with opacity
            "area1_stroke": "#5A715B",  # Dark green edge
            "area2": "#FA5A46",  # Error red-500
            "area2_stroke": "#D94435",  # Darker red edge
        },
        "font": {
            "family": "Hubot Sans",
            "size": {"title": 16, "label": 12, "axis": 10},
            "weight": {"title": 400, "label": 400, "axis": 400},
        },
        "radar": {
            "num_axes": 8,  # 8 axes (octagon)
            "num_rings": 5,  # 5 concentric circles
            "fill_opacity": 0.6,
        },
    },
    51: {
        "name": "Radar Chart - Black/Grayscale Theme",
        "colors": {
            "background": "#121212",  # Dark background
            "title": "#FFFFFF",  # White title
            "legend_text": "#A9A9A9",  # Gray legend
            "axis_text": "#A9A9A9",  # Gray for axis labels
            "grid": "#2D3130",  # Dark grid lines
            "axis": "#4A4A4A",  # Lighter axis lines
            "area1": "#C8C8C8",  # Light gray
            "area1_stroke": "#909090",  # Medium gray edge
            "area2": "#606060",  # Medium-dark gray
            "area2_stroke": "#303030",  # Very dark gray edge
        },
        "font": {
            "family": "Hubot Sans",
            "size": {"title": 16, "label": 12, "axis": 10},
            "weight": {"title": 400, "label": 400, "axis": 400},
        },
        "radar": {
            "num_axes": 8,  # 8 axes (octagon)
            "num_rings": 5,  # 5 concentric circles
            "fill_opacity": 0.6,
        },
    },
    52: {
        "name": "Radar Chart - White Theme",
        "colors": {
            "background": "#FFFFFF",  # White background
            "title": "#000000",  # Black title
            "legend_text": "#666666",  # Gray legend
            "axis_text": "#666666",  # Gray for axis labels
            "grid": "#E5E5E5",  # Light grid lines
            "axis": "#CCCCCC",  # Light axis lines
            "area1": "#484848",  # Dark gray
            "area1_stroke": "#303030",  # Very dark gray edge
            "area2": "#909090",  # Medium-light gray
            "area2_stroke": "#606060",  # Medium gray edge
        },
        "font": {
            "family": "Hubot Sans",
            "size": {"title": 16, "label": 12, "axis": 10},
            "weight": {"title": 400, "label": 400, "axis": 400},
        },
        "radar": {
            "num_axes": 8,  # 8 axes (octagon)
            "num_rings": 5,  # 5 concentric circles
            "fill_opacity": 0.6,
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
