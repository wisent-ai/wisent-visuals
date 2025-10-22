"""SVG grouped column chart with pattern fills matching Figma designs."""

import xml.etree.ElementTree as ET
from typing import List
import os


class SVGColumnChart:
    """Create pixel-perfect SVG grouped column charts with patterns."""

    def __init__(self, style: int = 1, theme: str = 'brand', width: int = 1002, height: int = 499):
        """Initialize SVG column chart.

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
                'column_one': '#C5FFC8',      # Lightest green
                'column_two': '#90B892',      # Medium green
                'column_three': '#5A715B',    # Dark green
                # Multi-color style
                'column_multi_one': '#C5FFC8',   # Green
                'column_multi_two': '#FF4444',    # Red
                'column_multi_three': '#B19CD9',  # Purple
            }
        elif self.theme == 'black':
            self.colors = {
                'background': '#121212',
                'title': '#FFFFFF',
                'legend_text': '#999999',
                'grid': '#2D3130',
                'column_one': '#FFFFFF',      # White
                'column_two': '#808080',      # Medium gray
                'column_three': '#4D4D4D',    # Dark gray
                # Multi-color style
                'column_multi_one': '#C5FFC8',   # Green
                'column_multi_two': '#FF4444',    # Red
                'column_multi_three': '#B19CD9',  # Purple
            }
        else:  # white theme
            self.colors = {
                'background': '#FFFFFF',
                'title': '#000000',
                'legend_text': '#666666',
                'grid': '#E0E0E0',
                'column_one': '#000000',      # Black
                'column_two': '#808080',      # Medium gray
                'column_three': '#CCCCCC',    # Light gray
                # Multi-color style
                'column_multi_one': '#C5FFC8',   # Green
                'column_multi_two': '#FF4444',    # Red
                'column_multi_three': '#B19CD9',  # Purple
            }

    def create_chart(
        self,
        categories: List[str],
        series: List[List[float]],
        labels: List[str],
        title: str = "Group Column Chart"
    ) -> str:
        """Create SVG column chart.

        Args:
            categories: Category labels (x-axis)
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
        chart_height = self.height - self.padding_y - chart_start_y - 40  # Reserve space for x-axis labels

        # Render column chart
        self._render_columns(
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

        # Style 2: noise pattern for middle column
        if self.style == 2:
            self._load_pattern_from_file(
                defs,
                'pattern-noise',
                os.path.join(assets_dir, 'large', 'noise_rectangle_large.svg')
            )

        # Style 3: crossing lines for middle column
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
        fills = self._get_column_fills()

        for i, label in enumerate(labels):
            fill = fills[i] if i < len(fills) else self.colors['column_one']

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

    def _get_column_fills(self) -> List[str]:
        """Get fill patterns/colors for each column based on style."""
        if self.style == 1:
            # Solid colors
            return [
                self.colors['column_one'],
                self.colors['column_two'],
                self.colors['column_three']
            ]
        elif self.style == 2:
            # Solid + noise + solid
            return [
                self.colors['column_one'],
                'url(#pattern-noise)',
                self.colors['column_three']
            ]
        elif self.style == 3:
            # Solid + crossing lines + solid
            return [
                self.colors['column_one'],
                'url(#pattern-crossing)',
                self.colors['column_three']
            ]
        elif self.style == 4:
            # Solid + noise + dither
            return [
                self.colors['column_one'],
                'url(#pattern-noise)',
                'url(#pattern-dither)'
            ]
        elif self.style == 5:
            # Multi-color
            return [
                self.colors['column_multi_one'],
                self.colors['column_multi_two'],
                self.colors['column_multi_three']
            ]

    def _render_columns(
        self,
        svg,
        categories: List[str],
        series: List[List[float]],
        chart_x: int,
        chart_start_y: int,
        chart_width: int,
        chart_height: int
    ):
        """Render grouped vertical columns."""
        num_categories = len(categories)
        num_series = len(series)

        # Calculate column dimensions
        group_width = chart_width / num_categories
        column_width = 40  # Fixed column width
        column_spacing = 10  # Space between columns in a group

        # Calculate max value for scaling
        max_value = max(max(s) for s in series)

        # Add some padding to max value for better visualization
        y_max = max_value * 1.1

        # Get fills
        fills = self._get_column_fills()

        # Render y-axis labels
        num_y_ticks = 5
        for i in range(num_y_ticks + 1):
            tick_value = int((i / num_y_ticks) * y_max)
            y = chart_start_y + chart_height - (i / num_y_ticks) * chart_height

            tick_elem = ET.SubElement(svg, 'text', {
                'x': str(chart_x - 10),
                'y': str(y + 4),
                'fill': self.colors['legend_text'],
                'font-size': '12',
                'font-weight': '400',
                'text-anchor': 'end'
            })
            tick_elem.text = str(tick_value)

        # Render each group (category)
        for cat_idx, category in enumerate(categories):
            group_x = chart_x + cat_idx * group_width
            group_center = group_x + group_width / 2

            # Calculate starting x for columns (centered in group)
            total_columns_width = num_series * column_width + (num_series - 1) * column_spacing
            columns_start_x = group_center - total_columns_width / 2

            # Render columns in this group
            for series_idx, data_series in enumerate(series):
                value = data_series[cat_idx]
                column_height = (value / y_max) * chart_height

                column_x = columns_start_x + series_idx * (column_width + column_spacing)
                column_y = chart_start_y + chart_height - column_height

                fill = fills[series_idx] if series_idx < len(fills) else self.colors['column_one']

                # Draw column
                ET.SubElement(svg, 'rect', {
                    'x': str(column_x),
                    'y': str(column_y),
                    'width': str(column_width),
                    'height': str(column_height),
                    'fill': fill
                })

            # Category label
            label_elem = ET.SubElement(svg, 'text', {
                'x': str(group_center),
                'y': str(chart_start_y + chart_height + 20),
                'fill': self.colors['legend_text'],
                'font-size': '14',
                'font-weight': '400',
                'text-anchor': 'middle'
            })
            label_elem.text = category
