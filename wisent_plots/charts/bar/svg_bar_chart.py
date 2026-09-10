"""SVG bar chart with pattern fills matching Figma designs."""

import xml.etree.ElementTree as ET
from typing import List
from wisent_plots.charts.svg_assets import _create_cartesian_patterns
from wisent_plots.charts.svg_components import render_title_and_legend


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
        _create_cartesian_patterns(svg, self.style)

        # Render title and legend with patterns/colors
        chart_start_y = render_title_and_legend(
            svg, title, labels, self.colors, self.padding_x, self.padding_y,
            self.title_gap, self.chart_top_margin, fills=self._get_segment_fills(),
            extra_fill=self.colors['bar_one'],
        )

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
