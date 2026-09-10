"""Style configuration definitions for Wisent plots.

This module contains style presets based on Wisent's Figma design system.
"""

from typing import Any, Dict

from .families import area, bubble, line, pie, radar

# Style definitions based on Figma Visual Identity
STYLES: Dict[int, Dict[str, Any]] = {
    1: area.EDGE,
    2: area.GRADIENT,
    3: area.PATTERN,
    4: area.TWO_PATTERNS,
    5: area.SOLID_COLORS,
    # Line Chart Styles
    10: line.DARK_PALETTE,
    11: line.DARK_MARKERS,
    12: line.DARK_SHAPES,
    # White/Light Theme Line Chart Styles
    20: line.LIGHT_PALETTE,
    21: line.LIGHT_MARKERS,
    22: line.LIGHT_SHAPES,
    # Bubble Chart Styles
    30: bubble.BRAND,
    31: bubble.BLACK,
    32: bubble.WHITE,
    # Pie Chart Styles (40-42)
    40: pie.BRAND,
    41: pie.BLACK,
    42: pie.WHITE,
    # Radar Chart Styles (50-52)
    50: radar.BRAND,
    51: radar.BLACK,
    52: radar.WHITE,
}


def get_style(style_number: int) -> Dict[str, Any]:
    """Get style configuration by number.

    Args:
        style_number: Numeric style identifier declared in STYLES.

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
