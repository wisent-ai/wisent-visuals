"""Components for rendering chart title, legend, and axes."""

import xml.etree.ElementTree as ET
from typing import List


def render_title_and_legend(
    svg,
    title: str,
    labels: List[str],
    colors: dict,
    padding_x: int,
    padding_y: int,
    title_gap: int,
    chart_top_margin: int
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
    title_elem = ET.SubElement(svg, 'text', {
        'x': str(padding_x),
        'y': str(padding_y + 20),
        'fill': colors['title'],
        'font-size': '20',
        'font-weight': '400'
    })
    title_elem.text = title

    # Legend - horizontal layout below title
    legend_y = padding_y + 20 + title_gap + 4
    legend_x = padding_x

    # Get color palette (extend if needed)
    color_palette = [colors['primary'], colors['secondary'], colors['accent']]
    # Add more colors if available
    if 'quaternary' in colors:
        color_palette.append(colors['quaternary'])
    if 'quinary' in colors:
        color_palette.append(colors['quinary'])

    for i, label in enumerate(labels):
        # Color box (20x10px with 2px border radius)
        # Cycle through colors if we have more series than colors
        color = color_palette[i % len(color_palette)]
        ET.SubElement(svg, 'rect', {
            'x': str(legend_x),
            'y': str(legend_y),
            'width': '20',
            'height': '10',
            'fill': color,
            'rx': '2',
            'ry': '2'
        })

        # Label text (14px, gap of 8px from box)
        text = ET.SubElement(svg, 'text', {
            'x': str(legend_x + 28),
            'y': str(legend_y + 9),
            'fill': colors['legend_text'],
            'font-size': '14',
            'font-weight': '400'
        })
        text.text = label

        # Move to next legend item (gap of 20px between items)
        legend_x += 20 + 8 + len(label) * 8 + 20

    # Return chart start Y position
    return padding_y + 20 + title_gap + 24 + chart_top_margin
