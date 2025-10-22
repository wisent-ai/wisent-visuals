"""Bar chart implementation with Wisent brand styling."""

from typing import Optional, Union, List, Tuple
from wisent_plots.styles.style_config import get_style
from wisent_plots.charts.bar.svg_bar_chart import SVGBarChart


class BarChart:
    """Create bar charts with Wisent brand styling.

    This class provides an easy-to-use interface for creating beautiful
    horizontal stacked bar charts that follow Wisent's brand guidelines.

    Example:
        >>> from wisent_plots import BarChart
        >>> chart = BarChart(style=1, theme='brand')
        >>> categories = ["Day Time 1", "Day Time 2", "Day Time 3"]
        >>> series = [[30, 40, 30], [25, 35, 40], [20, 30, 35]]
        >>> labels = ["One", "Two", "Three"]
        >>> svg_output = chart.plot(categories, series, labels, title="Bar Chart")
    """

    def __init__(
        self,
        style: Union[int, str] = 1,
        theme: str = 'brand',
        width: int = 1002,
        height: int = 499
    ):
        """Initialize a BarChart with specified styling.

        Args:
            style: Style number (1-5) for different pattern combinations.
                   1 = solid colors
                   2 = solid + noise + solid
                   3 = solid + crossing lines + solid
                   4 = solid + noise + dither crosses
                   5 = multi-color (green, red, purple)
            theme: Color theme ('brand', 'black', or 'white')
            width: Chart width in pixels (default: 1002)
            height: Chart height in pixels (default: 499)
        """
        # Map style names to numbers
        style_map = {
            "solid": 1,
            "pattern1": 2,
            "pattern2": 3,
            "pattern3": 4,
            "multicolor": 5,
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

        if self.style_number < 1 or self.style_number > 5:
            raise ValueError(f"Style must be between 1 and 5, got {self.style_number}")

        self.theme = theme.lower()
        if self.theme not in ['brand', 'black', 'white']:
            raise ValueError(f"Theme must be 'brand', 'black', or 'white', got {theme}")

        self.width = width
        self.height = height

    def plot(
        self,
        categories: List[str],
        series: List[List[float]],
        labels: List[str],
        title: Optional[str] = None,
        output_format: str = 'svg'
    ) -> str:
        """Create a horizontal stacked bar chart.

        Args:
            categories: List of category labels (y-axis labels)
            series: List of data series, where each series is a list of values
                   Series are stacked from left to right in the order provided
            labels: Legend labels for each series
            title: Chart title
            output_format: Output format ('svg' only for now)

        Returns:
            SVG string

        Example:
            >>> categories = ["Day Time 1", "Day Time 2", "Day Time 3"]
            >>> series = [[30, 40, 30], [25, 35, 40], [20, 30, 35]]
            >>> labels = ["One", "Two", "Three"]
            >>> svg = chart.plot(categories, series, labels, title="Bar Chart")
        """
        if output_format != 'svg':
            raise ValueError("Only 'svg' output format is currently supported")

        # Create SVG bar chart
        svg_chart = SVGBarChart(
            style=self.style_number,
            theme=self.theme,
            width=self.width,
            height=self.height
        )

        return svg_chart.create_chart(
            categories,
            series,
            labels,
            title or "Bar Chart"
        )
