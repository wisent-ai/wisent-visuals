"""Area chart implementation with Wisent brand styling."""

from typing import Optional, Union, List, Tuple
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import numpy as np

from wisent_plots.styles.style_config import get_style
from wisent_plots.charts.area.svg_area_chart import SVGAreaChart
from wisent_plots.charts.area.svg_area_chart_gradient import SVGAreaChartGradient
from wisent_plots.charts.area.svg_area_chart_pattern import SVGAreaChartPattern
from wisent_plots.charts.area.svg_area_chart_2patterns import SVGAreaChart2Patterns
from .matplotlib_backend.single import _plot_single
from .matplotlib_backend.multiple import _plot_multiple


class AreaChart:
    """Create area charts with Wisent brand styling.

    This class provides an easy-to-use interface for creating beautiful
    area charts that follow Wisent's brand guidelines.

    Example:
        >>> from wisent_plots import AreaChart
        >>> chart = AreaChart(style=1)
        >>> x = [1, 2, 3, 4, 5]
        >>> y = [2, 4, 3, 5, 4]
        >>> fig, ax = chart.plot(x, y, title="My Chart")
        >>> plt.show()
    """

    def __init__(
        self,
        style: Union[int, str] = 1,
        edge: bool = False,
        stacked: bool = True,
        figsize: Tuple[float, float] = (10, 6),
        dpi: int = 100
    ):
        """Initialize an AreaChart with specified styling.

        Args:
            style: Style number (1-5) or style name ("solid", "gradient", etc.).
                   Each style has different colors, fonts, and visual properties.
            edge: Whether to draw an edge around the filled area.
            stacked: Whether to stack areas on top of each other (True) or overlap (False).
            figsize: Figure size as (width, height) in inches.
            dpi: Dots per inch for the figure resolution.

        Raises:
            ValueError: If style is not between 1 and 5 or not a recognized style name.
        """
        # Map style names to numbers
        style_map = {
            "solid": 1,
            "gradient": 2,
            "pattern": 3,
            "2patterns": 4,
            "minimal": 5,
            "vibrant": 6,
            "dark": 7,
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

        self.style_config = get_style(self.style_number)
        self.edge = edge
        self.stacked = stacked
        self.figsize = figsize
        self.dpi = dpi

    def plot(
        self,
        x: Union[List, np.ndarray],
        y: Union[List, np.ndarray],
        title: Optional[str] = None,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        color: Optional[str] = None,
        label: Optional[str] = None,
        fig: Optional[Figure] = None,
        ax: Optional[Axes] = None,
    ) -> Tuple[Figure, Axes]:
        """Create an area chart.

        Args:
            x: X-axis data points.
            y: Y-axis data points.
            title: Chart title.
            xlabel: X-axis label.
            ylabel: Y-axis label.
            color: Custom color (hex or named color). If None, uses style's primary color.
            label: Legend label for the data series.
            fig: Existing figure to plot on. If None, creates new figure.
            ax: Existing axes to plot on. If None, creates new axes.

        Returns:
            Tuple of (figure, axes) objects.
        """
        return _plot_single(self, x, y, title, xlabel, ylabel, color, label, fig, ax)

    def plot_multiple(
        self,
        x: Union[List, np.ndarray],
        y_series: List[Union[List, np.ndarray]],
        labels: Optional[List[str]] = None,
        colors: Optional[List[str]] = None,
        title: Optional[str] = None,
        xlabel: Optional[str] = None,
        ylabel: Optional[str] = None,
        fig: Optional[Figure] = None,
        ax: Optional[Axes] = None,
        output_format: str = 'svg',
    ) -> Union[Tuple[Figure, Axes], str]:
        """Create an area chart with multiple data series.

        Args:
            x: X-axis data points.
            y_series: List of Y-axis data arrays.
            labels: List of legend labels for each series.
            colors: List of colors for each series. If None, uses style's color palette.
            title: Chart title.
            xlabel: X-axis label.
            ylabel: Y-axis label.
            fig: Existing figure to plot on. If None, creates new figure.
            ax: Existing axes to plot on. If None, creates new axes.
            output_format: Output format - 'svg' for SVG string (style 1 + edge only),
                          'matplotlib' for figure/axes tuple.

        Returns:
            Tuple of (figure, axes) objects or SVG string depending on output_format and style.
        """
        # Use SVG implementation for style=1 with edge=True
        if self.style_number == 1 and self.edge and output_format == 'svg':
            svg_chart = SVGAreaChart()
            svg_string = svg_chart.create_chart(x, y_series, labels or [], title or "Area Chart")
            return svg_string
        # Use SVG gradient implementation for style=2 with edge=True
        if self.style_number == 2 and self.edge and output_format == 'svg':
            svg_chart = SVGAreaChartGradient()
            svg_string = svg_chart.create_chart(x, y_series, labels or [], title or "Area Chart")
            return svg_string
        # Use SVG pattern implementation for style=3 with edge=True
        if self.style_number == 3 and self.edge and output_format == 'svg':
            svg_chart = SVGAreaChartPattern()
            svg_string = svg_chart.create_chart(x, y_series, labels or [], title or "Area Chart")
            return svg_string
        # Use SVG 2 patterns implementation for style=4 with edge=True
        if self.style_number == 4 and self.edge and output_format == 'svg':
            svg_chart = SVGAreaChart2Patterns()
            svg_string = svg_chart.create_chart(x, y_series, labels or [], title or "Area Chart")
            return svg_string
        # Use SVG solid colors implementation for style=5 with edge=True
        if self.style_number == 5 and output_format == 'svg':
            svg_chart = SVGAreaChart()
            # Update colors to use solid colors from style 5
            svg_chart.colors = {
                'background': self.style_config['colors']['background'],
                'title': self.style_config['colors']['text'],
                'legend_text': self.style_config['colors']['legend_text'],
                'grid': self.style_config['colors']['grid'],
                'area': self.style_config['colors']['primary'],  # Fallback for compatibility
                'primary': self.style_config['colors']['primary'],
                'secondary': self.style_config['colors']['secondary'],
                'accent': self.style_config['colors']['accent'],
            }
            svg_string = svg_chart.create_chart(x, y_series, labels or [], title or "Area Chart", self.style_config)
            return svg_string
        return _plot_multiple(self, x, y_series, labels, colors, title, xlabel, ylabel, fig, ax)

    def save(
        self,
        fig: Figure,
        filename: str,
        dpi: Optional[int] = None,
        transparent: bool = False,
    ) -> None:
        """Save the figure to a file.

        Args:
            fig: Figure object to save.
            filename: Output filename (with extension, e.g., 'chart.png').
            dpi: Resolution in dots per inch. If None, uses figure's dpi.
            transparent: Whether to save with transparent background.
        """
        save_dpi = dpi if dpi else self.dpi
        fig.savefig(
            filename,
            dpi=save_dpi,
            bbox_inches="tight",
            transparent=transparent,
        )
