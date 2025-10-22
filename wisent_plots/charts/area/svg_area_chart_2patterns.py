"""SVG area chart with 2 pattern fills matching Figma design."""

import xml.etree.ElementTree as ET
from typing import List
from wisent_plots.charts.area.area_chart_components import render_title_and_legend
from wisent_plots.charts.area.area_chart_renderer import _generate_stacked_paths

# Base64-encoded pattern images
# Seamless rotated squares pattern for middle band
PATTERN_SQUARES_B64 = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAAABmJLR0QA/wD/AP+gvaeTAAABCUlEQVQokY2RwU6DQBRFXwETWoMwgpiof8CbdtUCfkG70+jStSu/03Tqys7jD9zUNKGujN3gYpBAZ9r6lmdyk3Pn9h5eHnnGg4jB323WpZxLANA5CbKG+YhEUX6Win6tNyQKnHAjT8Zo3z3f+6FPC/ICb/v9IwUl44TFzB24Ru4AgB/6POPL13cAwJSzuNYwcqsWrCoAqKAHO6dxS/lJQZjy0e2weOt469zOp/lR7za3w6uQZ8guam/1JufL1ccKJ9j0cQfu2blXLMgC/fb0CSKGKRp2MPZpMv/aoX/abzL29Gl2wFvPHNlBbdd2O7SDMbN3h7Z3Z4foOsK0s4P67/jm0jlx2hnFfwHQ4s4tc7v0bgAAAABJRU5ErkJggg=="

PATTERN_TOP_B64 = "data:image/png;base64,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"


class SVGAreaChart2Patterns:
    """Create pixel-perfect SVG area charts with 2 pattern fills."""

    def __init__(self, width: int = 1002, height: int = 499):
        """Initialize SVG chart with Figma dimensions.

        Args:
            width: Chart width in pixels (default from Figma: 1002)
            height: Chart height in pixels (default from Figma: 499)
        """
        self.width = width
        self.height = height

        # Exact Figma colors
        self.colors = {
            'background': '#121212',
            'title': '#C5FFC8',
            'legend_text': '#769978',
            'grid': '#2D3130',
            'area': '#C5FFC8',
            'primary': '#B0E3B3',
            'secondary': '#90B892',
            'accent': '#5A715B',
        }

        # Exact Figma spacing
        self.padding_x = 32
        self.padding_y = 16
        self.title_gap = 10
        self.legend_gap = 4
        self.chart_top_margin = 24

        # Chart area dimensions (from Figma)
        self.chart_width = 938
        self.chart_height = 385

    def create_chart(
        self,
        x_data: List[float],
        y_series: List[List[float]],
        labels: List[str],
        title: str = "Area Chart"
    ) -> str:
        """Create SVG area chart with 2 pattern fills.

        Args:
            x_data: X-axis data points
            y_series: List of Y-axis data series
            labels: Legend labels
            title: Chart title

        Returns:
            SVG string
        """
        # Create root SVG element
        svg = ET.Element('svg', {
            'width': str(self.width),
            'height': str(self.height),
            'xmlns': 'http://www.w3.org/2000/svg',
            'viewBox': f'0 0 {self.width} {self.height}'
        })

        # Add Google Fonts
        style = ET.SubElement(svg, 'style')
        style.text = """
            @import url('https://fonts.googleapis.com/css2?family=Hubot+Sans:wght@400&display=swap');
            text { font-family: 'Hubot Sans', sans-serif; }
        """

        # Background rectangle
        ET.SubElement(svg, 'rect', {
            'width': str(self.width),
            'height': str(self.height),
            'fill': self.colors['background'],
            'rx': '20',
            'ry': '20'
        })

        # Define patterns FIRST (before rendering legend)
        self._create_patterns(svg)

        # Render title and legend with patterns
        chart_start_y = self._render_title_and_legend_with_patterns(
            svg, title, labels
        )

        # Chart area coordinates
        chart_x = self.padding_x
        chart_height = self.height - self.padding_y - chart_start_y

        # Render area chart with patterns
        self._render_pattern_areas(
            svg, x_data, y_series,
            chart_x, chart_start_y,
            self.chart_width, chart_height
        )

        # Convert to string
        return ET.tostring(svg, encoding='unicode', method='xml')

    def _render_title_and_legend_with_patterns(self, svg, title: str, labels: List[str]) -> int:
        """Render title and legend with pattern fills matching the chart."""
        # Title (20px, left-aligned at padding_x, padding_y)
        title_elem = ET.SubElement(svg, 'text', {
            'x': str(self.padding_x),
            'y': str(self.padding_y + 20),
            'fill': self.colors['title'],
            'font-size': '20',
            'font-weight': '400'
        })
        title_elem.text = title

        # Legend - horizontal layout below title
        legend_y = self.padding_y + 20 + self.title_gap + 4
        legend_x = self.padding_x

        # Pattern/fill mapping for each series (bottom to top in stacking order)
        fills = [
            'url(#pattern-bottom)',  # Bottom band - vertical lines
            'url(#pattern-middle)',  # Middle band - diagonal lines
            'url(#pattern-top)'  # Top band - dither crosses
        ]

        for i, label in enumerate(labels):
            # Get fill (pattern or color) for this series
            fill = fills[i] if i < len(fills) else self.colors['primary']

            # Color box (20x10px with 2px border radius)
            ET.SubElement(svg, 'rect', {
                'x': str(legend_x),
                'y': str(legend_y),
                'width': '20',
                'height': '10',
                'fill': fill,
                'rx': '2',
                'ry': '2'
            })

            # Label text (14px, gap of 8px from box)
            text = ET.SubElement(svg, 'text', {
                'x': str(legend_x + 28),
                'y': str(legend_y + 9),
                'fill': self.colors['legend_text'],
                'font-size': '14',
                'font-weight': '400'
            })
            text.text = label

            # Move to next legend item (gap of 20px between items)
            legend_x += 20 + 8 + len(label) * 8 + 20

        # Return chart start Y position
        return self.padding_y + 20 + self.title_gap + 24 + self.chart_top_margin

    def _create_patterns(self, svg):
        """Embed SVG patterns from asset files:
        - Bottom: vertical lines from pattern_vertical_lines.svg
        - Middle: diagonal lines from pattern_diagonal_lines.svg
        - Top: dither cross from dither_cross.svg (with larger seamless tile)
        """
        import os

        defs = svg.find('defs')
        if defs is None:
            defs = ET.SubElement(svg, 'defs')

        # Get path to assets directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)), 'assets')

        # Pattern definitions from asset files
        patterns = {
            'pattern-bottom': os.path.join(assets_dir, 'pattern_vertical_lines.svg'),
            'pattern-middle': os.path.join(assets_dir, 'pattern_diagonal_lines.svg'),
            'pattern-top': os.path.join(assets_dir, 'large', 'dither_cross_large.svg')
        }

        # Embed each pattern
        for pattern_id, svg_file in patterns.items():
            # Parse the pattern SVG file
            pattern_tree = ET.parse(svg_file)
            pattern_root = pattern_tree.getroot()

            # Extract width and height from the original SVG
            width = pattern_root.get('width')
            height = pattern_root.get('height')
            viewBox = pattern_root.get('viewBox')

            # If viewBox exists, use those dimensions for seamless tiling
            if viewBox:
                viewBox_parts = viewBox.split()
                if len(viewBox_parts) == 4:
                    width = viewBox_parts[2]
                    height = viewBox_parts[3]

            # Standard pattern embedding for all patterns
            pattern_elem = ET.SubElement(defs, 'pattern', {
                'id': pattern_id,
                'patternUnits': 'userSpaceOnUse',
                'width': width,
                'height': height
            })

            # Copy all child elements from the pattern SVG
            for child in pattern_root:
                tag = child.tag
                if tag.startswith('{'):
                    tag = tag.split('}')[1]
                if tag in ['title', 'desc', 'metadata']:
                    continue
                self._copy_element(child, pattern_elem)

    def _copy_element(self, source, parent):
        """Recursively copy an element and its children, removing namespaces."""
        # Get tag without namespace
        tag = source.tag
        if tag.startswith('{'):
            tag = tag.split('}')[1]

        # Copy attributes without namespace prefixes
        attribs = {}
        for key, value in source.attrib.items():
            if key.startswith('{'):
                key = key.split('}')[1]
            attribs[key] = value

        # Create new element
        new_elem = ET.SubElement(parent, tag, attribs)
        new_elem.text = source.text
        new_elem.tail = source.tail

        # Recursively copy children
        for child in source:
            self._copy_element(child, new_elem)

    def _render_pattern_areas(
        self,
        svg,
        x_data: List[float],
        y_series: List[List[float]],
        chart_x: int,
        chart_start_y: int,
        chart_width: int,
        chart_height: int
    ):
        """Render 2 pattern-filled area chart."""
        # Create clipping path
        clip_id = "chart-clip-2patterns"
        defs = svg.find('defs')
        if defs is None:
            defs = ET.SubElement(svg, 'defs')

        clipPath = ET.SubElement(defs, 'clipPath', {'id': clip_id})
        ET.SubElement(clipPath, 'rect', {
            'x': str(chart_x),
            'y': str(chart_start_y),
            'width': str(chart_width),
            'height': str(chart_height - 40)
        })

        # Generate stacked paths
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
                    'stroke': self.colors['grid'],
                    'stroke-width': '1',
                    'stroke-dasharray': '4,4'
                })

                # X-axis label
                if i < 14:
                    label_text = f"{i+1:02d}"
                    label_elem = ET.SubElement(svg, 'text', {
                        'x': str(x + 10),
                        'y': str(chart_start_y + chart_height - 10),
                        'fill': self.colors['legend_text'],
                        'font-size': '14',
                        'font-weight': '400',
                        'text-anchor': 'middle'
                    })
                    label_elem.text = label_text

        # Draw bands matching screenshot exactly
        # Bottom band (largest) - light green with VERTICAL LINES
        ET.SubElement(svg, 'path', {
            'd': paths[0][0],
            'fill': 'url(#pattern-bottom)',
            'fill-rule': 'evenodd',
            'clip-path': f'url(#{clip_id})'
        })

        # Middle band - dark green with DIAGONAL LINES (one direction)
        ET.SubElement(svg, 'path', {
            'd': paths[1][0],
            'fill': 'url(#pattern-middle)',
            'fill-rule': 'evenodd',
            'clip-path': f'url(#{clip_id})'
        })

        # Top band (smallest) - darkest green with CROSSHATCH GRID
        ET.SubElement(svg, 'path', {
            'd': paths[2][0],
            'fill': 'url(#pattern-top)',
            'fill-rule': 'evenodd',
            'clip-path': f'url(#{clip_id})'
        })

    def save_svg(self, svg_string: str, filename: str) -> None:
        """Save SVG string to file."""
        with open(filename, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(svg_string)
