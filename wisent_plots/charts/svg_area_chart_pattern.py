"""SVG area chart with pattern fills matching Figma design."""

import xml.etree.ElementTree as ET
from typing import List
from wisent_plots.charts.area_chart_components import render_title_and_legend
from wisent_plots.charts.area_chart_renderer import _generate_stacked_paths


class SVGAreaChartPattern:
    """Create pixel-perfect SVG area charts with pattern fills."""

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
        """Create SVG area chart with pattern fills.

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
            self.colors['area'],  # Bottom band - solid light green
            'url(#pattern-middle)',  # Middle band - crossing lines pattern
            'url(#pattern-top)'  # Top band - noise pattern
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
        """Embed SVG pattern from asset file for top band."""
        import os

        defs = svg.find('defs')
        if defs is None:
            defs = ET.SubElement(svg, 'defs')

        # Get path to assets directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)), 'assets')

        # Pattern for bottom band (lightest) - solid light green
        # No pattern needed, will use solid color

        # Pattern for middle band - crossing diagonal lines
        pattern_middle_file = os.path.join(assets_dir, 'pattern_crossing_lines.svg')

        # Parse the checkered pattern SVG file
        pattern_middle_tree = ET.parse(pattern_middle_file)
        pattern_middle_root = pattern_middle_tree.getroot()

        # Extract width and height
        width_middle = pattern_middle_root.get('width')
        height_middle = pattern_middle_root.get('height')
        viewBox_middle = pattern_middle_root.get('viewBox')

        if viewBox_middle:
            viewBox_parts = viewBox_middle.split()
            if len(viewBox_parts) == 4:
                width_middle = viewBox_parts[2]
                height_middle = viewBox_parts[3]

        # Create pattern element for middle band
        pattern_middle = ET.SubElement(defs, 'pattern', {
            'id': 'pattern-middle',
            'patternUnits': 'userSpaceOnUse',
            'width': width_middle,
            'height': height_middle
        })

        # Copy all child elements from the checkered pattern SVG
        for child in pattern_middle_root:
            tag = child.tag
            if tag.startswith('{'):
                tag = tag.split('}')[1]
            if tag in ['title', 'desc', 'metadata']:
                continue
            self._copy_element(child, pattern_middle)

        # Top band (darkest) - load noise pattern from file
        pattern_file = os.path.join(assets_dir, 'large', 'noise_rectangle_large.svg')

        # Parse the pattern SVG file
        pattern_tree = ET.parse(pattern_file)
        pattern_root = pattern_tree.getroot()

        # Extract width and height from the original SVG
        width = pattern_root.get('width')
        height = pattern_root.get('height')
        viewBox = pattern_root.get('viewBox')

        # If viewBox exists, use those dimensions
        if viewBox:
            viewBox_parts = viewBox.split()
            if len(viewBox_parts) == 4:
                width = viewBox_parts[2]
                height = viewBox_parts[3]

        # Create pattern element for top band
        pattern_elem = ET.SubElement(defs, 'pattern', {
            'id': 'pattern-top',
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
        """Render pattern-filled area chart."""
        # Create clipping path
        clip_id = "chart-clip-pattern"
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

        # Draw bands with patterns
        # Top band (smallest) - noise pattern
        ET.SubElement(svg, 'path', {
            'd': paths[2][0],
            'fill': 'url(#pattern-top)',
            'fill-rule': 'evenodd',
            'clip-path': f'url(#{clip_id})'
        })

        # Middle band - diagonal line pattern
        ET.SubElement(svg, 'path', {
            'd': paths[1][0],
            'fill': 'url(#pattern-middle)',
            'fill-rule': 'evenodd',
            'clip-path': f'url(#{clip_id})'
        })

        # Bottom band (largest) - lightest (solid light green)
        ET.SubElement(svg, 'path', {
            'd': paths[0][0],
            'fill': self.colors['area'],  # Solid #C5FFC8
            'fill-rule': 'evenodd',
            'clip-path': f'url(#{clip_id})'
        })

    def save_svg(self, svg_string: str, filename: str) -> None:
        """Save SVG string to file."""
        with open(filename, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(svg_string)
