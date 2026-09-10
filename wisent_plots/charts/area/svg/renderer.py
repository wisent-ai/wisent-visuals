"""Main area chart rendering with paths and grid lines."""

import numpy as np
import xml.etree.ElementTree as ET
from typing import List, Tuple


def render_area_chart(
    svg,
    x_data: List[float],
    y_series: List[List[float]],
    chart_x: int,
    chart_start_y: int,
    chart_width: int,
    chart_height: int,
    colors: dict,
    style_config: dict = None
):
    """Render the main area chart with grid lines and x-axis labels.

    Args:
        svg: SVG element tree root
        x_data: X-axis data points
        y_series: List of Y-axis data series (will be stacked)
        chart_x: X coordinate where chart starts
        chart_start_y: Y coordinate where chart starts
        chart_width: Width of chart area
        chart_height: Height of chart area
        colors: Color configuration dict
        style_config: Optional style configuration dict (for solid colors, etc.)
    """
    # Create clipping path for chart area
    clip_id = "chart-clip"
    defs = ET.SubElement(svg, 'defs')
    clipPath = ET.SubElement(defs, 'clipPath', {'id': clip_id})
    ET.SubElement(clipPath, 'rect', {
        'x': str(chart_x),
        'y': str(chart_start_y),
        'width': str(chart_width),
        'height': str(chart_height - 40)
    })

    # Generate stacked area paths
    paths = _generate_stacked_paths(
        x_data, y_series,
        chart_x, chart_start_y,
        chart_width, chart_height - 40
    )

    # Draw grid lines FIRST so area bands appear in front
    grid_spacing = 67
    for i in range(15):
        x = chart_x + (i * grid_spacing)
        if x <= chart_x + chart_width:
            # Dashed vertical line
            ET.SubElement(svg, 'line', {
                'x1': str(x),
                'y1': str(chart_start_y),
                'x2': str(x),
                'y2': str(chart_start_y + chart_height - 40),
                'stroke': colors['grid'],
                'stroke-width': '1',
                'stroke-dasharray': '4,4'
            })

            # X-axis label below chart
            if i < 14:
                label_text = f"{i+1:02d}"
                label_elem = ET.SubElement(svg, 'text', {
                    'x': str(x + 10),
                    'y': str(chart_start_y + chart_height - 10),
                    'fill': colors['legend_text'],
                    'font-size': '14',
                    'font-weight': '400',
                    'text-anchor': 'middle'
                })
                label_elem.text = label_text

    # Draw area bands AFTER grid lines so they appear in front
    # Check if we're using solid colors (style 5) or opacity-based colors
    use_solid_colors = style_config and style_config.get('fill', {}).get('type') == 'solid'

    if use_solid_colors:
        # Style 5: Use distinct solid colors for each band
        # Bottom (largest) - primary color (green)
        ET.SubElement(svg, 'path', {
            'd': paths[0][0],
            'fill': colors['primary'],  # #C5FFC8
            'fill-rule': 'evenodd',
            'clip-path': f'url(#{clip_id})'
        })

        # Middle band - secondary color (red)
        ET.SubElement(svg, 'path', {
            'd': paths[1][0],
            'fill': colors['secondary'],  # #FA5A46
            'fill-rule': 'evenodd',
            'clip-path': f'url(#{clip_id})'
        })

        # Top band (smallest) - accent color (purple)
        ET.SubElement(svg, 'path', {
            'd': paths[2][0],
            'fill': colors['accent'],  # #B19ECC
            'fill-rule': 'evenodd',
            'clip-path': f'url(#{clip_id})'
        })
    else:
        # Original opacity-based rendering
        # Bottom should be lightest, top should be darkest
        # Assign opacities to match: bottom=1.0 (lightest), top=0.4 (darkest)

        # Top band (smallest) - opacity 0.4 (darkest)
        ET.SubElement(svg, 'path', {
            'd': paths[2][0],
            'fill': colors['area'],  # #C5FFC8
            'opacity': '0.4',
            'fill-rule': 'evenodd',
            'clip-path': f'url(#{clip_id})'
        })

        # Middle band - opacity 0.5
        ET.SubElement(svg, 'path', {
            'd': paths[1][0],
            'fill': colors['area'],  # #C5FFC8
            'opacity': '0.5',
            'fill-rule': 'evenodd',
            'clip-path': f'url(#{clip_id})'
        })

        # Bottom band (largest) - opacity 1.0 (lightest, fully opaque)
        ET.SubElement(svg, 'path', {
            'd': paths[0][0],
            'fill': colors['area'],  # #C5FFC8
            'fill-rule': 'evenodd',
            'clip-path': f'url(#{clip_id})'
        })


def _generate_stacked_paths(
    x_data, y_series, chart_x, chart_y, chart_w, chart_h
) -> List[Tuple[str, str]]:
    """Generate SVG path data for stacked band areas.

    Creates band paths where each band shows only its own contribution,
    stacked on top of previous bands, creating distinct visible bands.

    Args:
        x_data: X-axis data points
        y_series: List of Y-axis data series
        chart_x: X coordinate of chart area
        chart_y: Y coordinate of chart area
        chart_w: Width of chart area
        chart_h: Height of chart area

    Returns:
        List of (path_string, color) tuples
    """
    paths = []

    # Chart bottom
    chart_bottom = chart_y + chart_h

    # Calculate cumulative sum to find the true max (for stacked charts)
    cumulative_sum = np.zeros(len(x_data))
    for series in y_series:
        cumulative_sum += np.array(series)

    # Max value is the max of the cumulative total
    max_val = np.max(cumulative_sum)

    # Cumulative sum to know where each band starts
    cumulative = np.zeros(len(x_data))

    # Generate band paths (not cumulative areas, but bands between baselines)
    for series_data in y_series:
        y_array = np.array(series_data)

        # This band's baseline is the previous cumulative
        baseline = cumulative.copy()

        # Add current series to cumulative for next band
        cumulative += y_array

        # Create a band path from baseline to baseline+series
        # Start at left edge, at the baseline
        baseline_y_start = chart_bottom - (baseline[0] / max_val * chart_h)
        path_d = f"M {chart_x},{baseline_y_start}"

        # Draw along the baseline (left to right)
        for i in range(len(x_data)):
            x_pos = chart_x + i * (chart_w / (len(x_data) - 1))
            y_pos = chart_bottom - (baseline[i] / max_val * chart_h)
            path_d += f" L {x_pos},{y_pos}"

        # Now draw the top edge (right to left) at baseline + series
        for i in range(len(x_data) - 1, -1, -1):
            x_pos = chart_x + i * (chart_w / (len(x_data) - 1))
            y_pos = chart_bottom - ((baseline[i] + y_array[i]) / max_val * chart_h)
            path_d += f" L {x_pos},{y_pos}"

        # Close path
        path_d += " Z"

        paths.append((path_d, None))

    return paths
