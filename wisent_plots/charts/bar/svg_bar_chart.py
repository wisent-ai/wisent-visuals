"""SVG bar chart with pattern fills matching Figma designs."""

import xml.etree.ElementTree as ET
from typing import List
import os


class SVGBarChart:
    """Create pixel-perfect SVG horizontal stacked bar charts with patterns."""

    def __init__(self, style: int = 1, theme: str = 'brand', width: int = 1002, height: int = 499):
        """Initialize SVG bar chart.

        Args:
            style: Style number (1-5)
            theme: Color theme ('brand', 'black', or 'white')
            width: Chart width in pixels
            height: Chart height in pixels
        """
        self.style = style
        self.theme = theme
        self.width = width
        self.height = height

        # Exact Figma spacing
        self.padding_x = 32
        self.padding_y = 16
        self.title_gap = 10
        self.legend_gap = 4
        self.chart_top_margin = 24

        # Set colors based on theme
        self._set_theme_colors()

    def _set_theme_colors(self):
        """Set color scheme based on theme."""
        if self.theme == 'brand':
            self.colors = {
                'background': '#121212',
                'title': '#C5FFC8',
                'legend_text': '#769978',
                'grid': '#2D3130',
                'bar_one': '#C5FFC8',      # Lightest green
                'bar_two': '#90B892',      # Medium green
                'bar_three': '#5A715B',    # Dark green
                # Multi-color style
                'bar_multi_one': '#C5FFC8',   # Green
                'bar_multi_two': '#FF4444',    # Red
                'bar_multi_three': '#B19CD9',  # Purple
            }
        elif self.theme == 'black':
            self.colors = {
                'background': '#121212',
                'title': '#FFFFFF',
                'legend_text': '#999999',
                'grid': '#2D3130',
                'bar_one': '#FFFFFF',      # White
                'bar_two': '#808080',      # Medium gray
                'bar_three': '#4D4D4D',    # Dark gray
                # Multi-color style
                'bar_multi_one': '#C5FFC8',   # Green
                'bar_multi_two': '#FF4444',    # Red
                'bar_multi_three': '#B19CD9',  # Purple
            }
        else:  # white theme
            self.colors = {
                'background': '#FFFFFF',
                'title': '#000000',
                'legend_text': '#666666',
                'grid': '#E0E0E0',
                'bar_one': '#000000',      # Black
                'bar_two': '#808080',      # Medium gray
                'bar_three': '#CCCCCC',    # Light gray
                # Multi-color style
                'bar_multi_one': '#C5FFC8',   # Green
                'bar_multi_two': '#FF4444',    # Red
                'bar_multi_three': '#B19CD9',  # Purple
            }

    def create_chart(
        self,
        categories: List[str],
        series: List[List[float]],
        labels: List[str],
        title: str = "Bar Chart"
    ) -> str:
        """Create SVG bar chart.

        Args:
            categories: Category labels (y-axis)
            series: List of data series
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
            'xmlns:xlink': 'http://www.w3.org/1999/xlink',
            'viewBox': f'0 0 {self.width} {self.height}'
        })

        # Add Google Fonts
        style_elem = ET.SubElement(svg, 'style')
        style_elem.text = """
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

        # Render title and legend with patterns/colors
        chart_start_y = self._render_title_and_legend(svg, title, labels)

        # Chart area coordinates
        chart_x = self.padding_x
        chart_height = self.height - self.padding_y - chart_start_y

        # Render bar chart
        self._render_bars(
            svg, categories, series,
            chart_x, chart_start_y,
            self.width - 2 * self.padding_x, chart_height
        )

        # Convert to string
        return ET.tostring(svg, encoding='unicode', method='xml')

    def _create_patterns(self, svg):
        """Create SVG pattern definitions based on style."""
        defs = svg.find('defs')
        if defs is None:
            defs = ET.SubElement(svg, 'defs')

        # Get path to assets directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)), 'assets')

        # Style 2: noise pattern for middle segment
        if self.style == 2:
            self._load_pattern_from_file(
                defs,
                'pattern-noise',
                os.path.join(assets_dir, 'large', 'noise_rectangle_large.svg')
            )

        # Style 3: crossing lines for middle segment
        elif self.style == 3:
            self._load_pattern_from_file(
                defs,
                'pattern-crossing',
                os.path.join(assets_dir, 'pattern_crossing_lines.svg')
            )

        # Style 4: noise + dither crosses
        elif self.style == 4:
            self._load_pattern_from_file(
                defs,
                'pattern-noise',
                os.path.join(assets_dir, 'large', 'noise_rectangle_large.svg')
            )
            self._load_pattern_from_file(
                defs,
                'pattern-dither',
                os.path.join(assets_dir, 'large', 'dither_cross_large.svg')
            )

    def _load_pattern_from_file(self, defs, pattern_id: str, svg_file: str):
        """Load and embed an SVG pattern from a file."""
        pattern_tree = ET.parse(svg_file)
        pattern_root = pattern_tree.getroot()

        # Extract width and height
        width = pattern_root.get('width')
        height = pattern_root.get('height')
        viewBox = pattern_root.get('viewBox')

        if viewBox:
            viewBox_parts = viewBox.split()
            if len(viewBox_parts) == 4:
                width = viewBox_parts[2]
                height = viewBox_parts[3]

        # Create pattern element
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
        """Recursively copy an element and its children."""
        tag = source.tag
        if tag.startswith('{'):
            tag = tag.split('}')[1]

        attribs = {}
        for key, value in source.attrib.items():
            if key.startswith('{'):
                key = key.split('}')[1]
            attribs[key] = value

        new_elem = ET.SubElement(parent, tag, attribs)
        new_elem.text = source.text
        new_elem.tail = source.tail

        for child in source:
            self._copy_element(child, new_elem)

    def _render_title_and_legend(self, svg, title: str, labels: List[str]) -> int:
        """Render title and legend with appropriate fills."""
        # Title
        title_elem = ET.SubElement(svg, 'text', {
            'x': str(self.padding_x),
            'y': str(self.padding_y + 20),
            'fill': self.colors['title'],
            'font-size': '20',
            'font-weight': '400'
        })
        title_elem.text = title

        # Legend
        legend_y = self.padding_y + 20 + self.title_gap + 4
        legend_x = self.padding_x

        # Get fills based on style
        fills = self._get_segment_fills()

        for i, label in enumerate(labels):
            fill = fills[i] if i < len(fills) else self.colors['bar_one']

            # Legend box
            ET.SubElement(svg, 'rect', {
                'x': str(legend_x),
                'y': str(legend_y),
                'width': '20',
                'height': '10',
                'fill': fill,
                'rx': '2',
                'ry': '2'
            })

            # Legend text
            text = ET.SubElement(svg, 'text', {
                'x': str(legend_x + 28),
                'y': str(legend_y + 9),
                'fill': self.colors['legend_text'],
                'font-size': '14',
                'font-weight': '400'
            })
            text.text = label

            legend_x += 20 + 8 + len(label) * 8 + 20

        return self.padding_y + 20 + self.title_gap + 24 + self.chart_top_margin

    def _get_segment_fills(self) -> List[str]:
        """Get fill patterns/colors for each segment based on style."""
        if self.style == 1:
            # Solid colors
            return [
                self.colors['bar_one'],
                self.colors['bar_two'],
                self.colors['bar_three']
            ]
        elif self.style == 2:
            # Solid + noise + solid
            return [
                self.colors['bar_one'],
                'url(#pattern-noise)',
                self.colors['bar_three']
            ]
        elif self.style == 3:
            # Solid + crossing lines + solid
            return [
                self.colors['bar_one'],
                'url(#pattern-crossing)',
                self.colors['bar_three']
            ]
        elif self.style == 4:
            # Solid + noise + dither
            return [
                self.colors['bar_one'],
                'url(#pattern-noise)',
                'url(#pattern-dither)'
            ]
        elif self.style == 5:
            # Multi-color
            return [
                self.colors['bar_multi_one'],
                self.colors['bar_multi_two'],
                self.colors['bar_multi_three']
            ]

    def _render_bars(
        self,
        svg,
        categories: List[str],
        series: List[List[float]],
        chart_x: int,
        chart_start_y: int,
        chart_width: int,
        chart_height: int
    ):
        """Render horizontal stacked bars."""
        num_categories = len(categories)
        bar_height = 30
        bar_spacing = 20

        # Calculate max value for scaling
        max_value = max(sum(values) for values in zip(*series))

        # Get fills
        fills = self._get_segment_fills()

        # Render each category (row)
        for cat_idx, category in enumerate(categories):
            y = chart_start_y + cat_idx * (bar_height + bar_spacing)

            # Category label
            label_elem = ET.SubElement(svg, 'text', {
                'x': str(chart_x),
                'y': str(y + bar_height // 2 + 5),
                'fill': self.colors['legend_text'],
                'font-size': '14',
                'font-weight': '400'
            })
            label_elem.text = category

            # Start x position for bars (after label)
            bar_start_x = chart_x + 120
            available_width = chart_width - 120

            # Render stacked segments
            current_x = bar_start_x
            for seg_idx, segment_series in enumerate(series):
                value = segment_series[cat_idx]
                segment_width = (value / max_value) * available_width

                fill = fills[seg_idx] if seg_idx < len(fills) else self.colors['bar_one']

                # Draw segment
                ET.SubElement(svg, 'rect', {
                    'x': str(current_x),
                    'y': str(y),
                    'width': str(segment_width),
                    'height': str(bar_height),
                    'fill': fill
                })

                current_x += segment_width

        # X-axis labels (scale)
        axis_y = chart_start_y + num_categories * (bar_height + bar_spacing) + 10
        num_ticks = 9
        for i in range(num_ticks):
            tick_x = chart_x + 120 + i * (chart_width - 120) / (num_ticks - 1)
            tick_value = int((i / (num_ticks - 1)) * max_value)

            tick_elem = ET.SubElement(svg, 'text', {
                'x': str(tick_x),
                'y': str(axis_y),
                'fill': self.colors['legend_text'],
                'font-size': '12',
                'font-weight': '400',
                'text-anchor': 'middle'
            })
            tick_elem.text = str(tick_value)
