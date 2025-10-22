"""Bubble chart implementation with Wisent brand styling."""

from typing import Optional, Union, List, Tuple
import numpy as np

from wisent_plots.styles.style_config import get_style
from wisent_plots.charts.svg_bubble_chart import SVGBubbleChart
from wisent_plots.charts.svg_radar_bubble_chart import SVGRadarBubbleChart


class BubbleChart:
    """Create bubble charts with Wisent brand styling.

    Supports both regular bubble charts and radar bubble charts.

    Example:
        >>> from wisent_plots import BubbleChart
        >>> chart = BubbleChart(style=1, chart_type='bubble')
        >>> x = [10, 20, 30, 40, 50]
        >>> y = [100, 200, 300, 400, 500]
        >>> sizes = [10, 20, 30, 20, 10]
        >>> svg = chart.plot(x, y, sizes, title="My Bubble Chart")
    """

    def __init__(
        self,
        style: Union[int, str] = 1,
        chart_type: str = 'bubble',
        width: int = 456,
        height: int = 383
    ):
        """Initialize a BubbleChart with specified styling.

        Args:
            style: Style number (1-3) for bubble charts.
                   1: Brand colors (dark theme)
                   2: Black theme (grayscale)
                   3: White theme (light background)
            chart_type: Type of chart - 'bubble' or 'radar'
            width: Chart width in pixels
            height: Chart height in pixels

        Raises:
            ValueError: If style is not between 1 and 3 or chart_type is invalid.
        """
        # Map style names to numbers
        style_map = {
            "brand": 1,
            "black": 2,
            "white": 3,
        }

        # Convert style name to number if needed
        if isinstance(style, str):
            style_lower = style.lower()
            if style_lower in style_map:
                self.style_number = style_map[style_lower]
            else:
                raise ValueError(f"Unknown style name: {style}. Valid names are: {', '.join(style_map.keys())}")
        else:
            self.style_number = style

        if chart_type not in ['bubble', 'radar']:
            raise ValueError("chart_type must be 'bubble' or 'radar'")

        self.chart_type = chart_type
        self.width = width
        self.height = height

        # Map bubble chart styles to actual style numbers (30, 31, 32)
        actual_style = 29 + self.style_number

        # Load style configuration
        try:
            self.style_config = get_style(actual_style)
        except ValueError:
            # Fallback if style doesn't exist
            self.style_config = {
                "colors": {
                    "primary": "#FA5A46",
                    "secondary": "#FF8C00",
                    "accent": "#FFD700",
                    "background": "#121212",
                    "text": "#C5FFC8",
                    "grid": "#2D3130",
                    "legend_text": "#769978",
                },
                "font": {
                    "family": "Hubot Sans",
                    "size": {"title": 20, "label": 14, "tick": 12},
                    "weight": {"title": 400, "label": 400},
                },
            }

    def plot(
        self,
        x_data: Optional[List[float]] = None,
        y_data: Optional[List[float]] = None,
        sizes: List[float] = None,
        categories: Optional[List[int]] = None,
        category_labels: Optional[List[str]] = None,
        title: str = "Bubble Chart",
        angles: Optional[List[float]] = None,
        distances: Optional[List[float]] = None,
        output_format: str = 'svg'
    ) -> str:
        """Create a bubble chart.

        For regular bubble charts, provide x_data, y_data, sizes.
        For radar charts, provide angles, distances, sizes.

        Args:
            x_data: X-axis data points (for regular bubble chart)
            y_data: Y-axis data points (for regular bubble chart)
            sizes: Sizes for each bubble
            categories: Category index for each point (for coloring)
            category_labels: Labels for legend
            title: Chart title
            angles: Angles for radar chart (0-360 degrees)
            distances: Distances from center for radar chart (0-100)
            output_format: Output format - 'svg' for SVG string

        Returns:
            SVG string
        """
        if output_format == 'svg':
            if self.chart_type == 'radar':
                return self._create_radar_svg(
                    angles, distances, sizes, categories, category_labels, title
                )
            else:
                return self._create_bubble_svg(
                    x_data, y_data, sizes, categories, category_labels, title
                )

        raise ValueError("Only 'svg' output format is currently supported")

    def _create_bubble_svg(
        self,
        x_data: List[float],
        y_data: List[float],
        sizes: List[float],
        categories: Optional[List[int]],
        category_labels: Optional[List[str]],
        title: str
    ) -> str:
        """Create regular bubble chart SVG."""
        svg_chart = SVGBubbleChart(width=self.width, height=self.height)

        # Update colors from style config
        self._update_chart_colors(svg_chart)

        svg_string = svg_chart.create_chart(
            x_data=x_data,
            y_data=y_data,
            sizes=sizes,
            categories=categories,
            category_labels=category_labels,
            title=title
        )

        return svg_string

    def _create_radar_svg(
        self,
        angles: List[float],
        distances: List[float],
        sizes: List[float],
        categories: Optional[List[int]],
        category_labels: Optional[List[str]],
        title: str
    ) -> str:
        """Create radar bubble chart SVG."""
        svg_chart = SVGRadarBubbleChart(width=self.width, height=self.height)

        # Update colors from style config
        self._update_chart_colors(svg_chart)

        svg_string = svg_chart.create_chart(
            angles=angles,
            distances=distances,
            sizes=sizes,
            categories=categories,
            category_labels=category_labels,
            title=title
        )

        return svg_string

    def _update_chart_colors(self, svg_chart):
        """Update chart colors from style configuration."""
        svg_chart.colors['background'] = self.style_config['colors']['background']
        svg_chart.colors['title'] = self.style_config['colors']['text']
        svg_chart.colors['legend_text'] = self.style_config['colors']['legend_text']
        svg_chart.colors['grid'] = self.style_config['colors']['grid']
        svg_chart.colors['axis_text'] = self.style_config['colors']['legend_text']

        # Update bubble colors if specified in style
        for i in range(1, 10):
            color_key = f'bubble{i}'
            if color_key in self.style_config['colors']:
                svg_chart.colors[color_key] = self.style_config['colors'][color_key]

    def save_svg(self, svg_string: str, filename: str):
        """Save SVG to file."""
        with open(filename, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(svg_string)
