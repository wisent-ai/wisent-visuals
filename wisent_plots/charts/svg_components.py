"""Components for rendering chart title, legend, and axes."""

import xml.etree.ElementTree as ET
from typing import List, Optional


def render_title(svg, title: str, colors: dict, padding_x: int, padding_y: int):
    title_elem = ET.SubElement(
        svg,
        "text",
        {
            "x": str(padding_x),
            "y": str(padding_y + 20),
            "fill": colors["title"],
            "font-size": "20",
            "font-weight": "400",
        },
    )
    title_elem.text = title


def render_title_and_legend(
    svg,
    title: str,
    labels: List[str],
    colors: dict,
    padding_x: int,
    padding_y: int,
    title_gap: int,
    chart_top_margin: int,
    fills: Optional[List[str]] = None,
    extra_fill: Optional[str] = None,
) -> int:
    """Render title, legend, and axes. Returns chart_start_y.

    Args:
        svg: SVG element tree root
        title: Chart title
        labels: List of legend labels
        colors: Color configuration dict
        padding_x: Horizontal padding
        padding_y: Vertical padding
        title_gap: Gap between title and legend
        chart_top_margin: Margin before chart area

    Returns:
        Y coordinate where chart area starts
    """
    # Title (20px, left-aligned at padding_x, padding_y)
    render_title(svg, title, colors, padding_x, padding_y)

    # Legend - horizontal layout below title
    legend_y = padding_y + 20 + title_gap + 4
    legend_x = padding_x

    # Get color palette (extend if needed)
    if fills is None:
        color_palette = [colors["primary"], colors["secondary"], colors["accent"]]
        if "quaternary" in colors:
            color_palette.append(colors["quaternary"])
        if "quinary" in colors:
            color_palette.append(colors["quinary"])
    else:
        color_palette = fills

    for i, label in enumerate(labels):
        # Color box (20x10px with 2px border radius)
        # Cycle through colors if we have more series than colors
        if fills is None:
            color = color_palette[i % len(color_palette)]
        else:
            color = color_palette[i] if i < len(color_palette) else extra_fill
        ET.SubElement(
            svg,
            "rect",
            {
                "x": str(legend_x),
                "y": str(legend_y),
                "width": "20",
                "height": "10",
                "fill": color,
                "rx": "2",
                "ry": "2",
            },
        )

        # Label text (14px, gap of 8px from box)
        text = ET.SubElement(
            svg,
            "text",
            {
                "x": str(legend_x + 28),
                "y": str(legend_y + 9),
                "fill": colors["legend_text"],
                "font-size": "14",
                "font-weight": "400",
            },
        )
        text.text = label

        # Move to next legend item (gap of 20px between items)
        legend_x += 20 + 8 + len(label) * 8 + 20

    # Return chart start Y position
    return padding_y + 20 + title_gap + 24 + chart_top_margin


def render_bubble_legend(
    svg,
    labels: List[str],
    colors: dict,
    padding_x: int,
    padding_y: int,
    category_indices: Optional[List[int]] = None,
):
    legend_y = padding_y + 36
    legend_x = padding_x

    for i, label in enumerate(labels):
        # Color box - use category index if provided, otherwise use label index
        if category_indices and i < len(category_indices):
            cat_idx = category_indices[i]
        else:
            cat_idx = i
        color_key = f"bubble{cat_idx+1}"
        color = colors.get(color_key, colors["bubble9"])

        ET.SubElement(
            svg,
            "rect",
            {
                "x": str(legend_x),
                "y": str(legend_y),
                "width": "20",
                "height": "10",
                "fill": color,
                "rx": "2",
                "ry": "2",
            },
        )

        # Label text
        text_elem = ET.SubElement(
            svg,
            "text",
            {
                "x": str(legend_x + 28),
                "y": str(legend_y + 9),
                "fill": colors["legend_text"],
                "font-size": "12",
                "font-weight": "400",
            },
        )
        text_elem.text = label

        # Move to next position
        legend_x += 60


def render_marker(svg, x: float, y: float, shape: str, color: str, size: float = 11):
    """Draw a marker at the specified position."""
    half_size = size / 2

    if shape == "circle":
        ET.SubElement(
            svg, "circle", {"cx": str(x), "cy": str(y), "r": str(half_size), "fill": color}
        )
    elif shape == "square":
        ET.SubElement(
            svg,
            "rect",
            {
                "x": str(x - half_size),
                "y": str(y - half_size),
                "width": str(size),
                "height": str(size),
                "fill": color,
                "rx": "2",
                "ry": "2",
            },
        )
    elif shape == "diamond":
        # Rotate square by 45 degrees
        points = f"{x},{y - half_size} {x + half_size},{y} {x},{y + half_size} {x - half_size},{y}"
        ET.SubElement(svg, "polygon", {"points": points, "fill": color})
    elif shape == "triangle":
        # Equilateral triangle pointing up
        h = half_size * 1.732  # sqrt(3) for equilateral
        points = f"{x},{y - h * 0.67} {x + half_size},{y + h * 0.33} {x - half_size},{y + h * 0.33}"
        ET.SubElement(svg, "polygon", {"points": points, "fill": color})
