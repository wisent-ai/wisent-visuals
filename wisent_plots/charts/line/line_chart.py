"""Line chart implementation with Wisent brand styling."""

from typing import Optional, Union, List, Tuple
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import numpy as np

from wisent_plots.styles.style_config import get_style
from wisent_plots.charts.line.svg_line_chart import SVGLineChart


class LineChart:
    """Create line charts with Wisent brand styling.

    This class provides an easy-to-use interface for creating beautiful
    line charts that follow Wisent's brand guidelines.

    Example:
        >>> from wisent_plots import LineChart
        >>> chart = LineChart(style=1)
        >>> x = [1, 2, 3, 4, 5]
        >>> y = [2, 4, 3, 5, 4]
        >>> fig, ax = chart.plot(x, y, title="My Chart")
        >>> plt.show()
    """

    def __init__(
        self,
        style: Union[int, str] = 1,
        figsize: Tuple[float, float] = (10, 6),
        dpi: int = 100,
        line_width: float = 2.0,
        show_markers: bool = False
    ):
        """Initialize a LineChart with specified styling.

        Args:
            style: Style number (1-6) for line charts.
                   1: Solid color palette (dark theme)
                   2: Solid color with markers (dark theme)
                   3: Groups with different marker shapes (dark theme)
                   4: Solid color palette (white theme)
                   5: Solid color with markers (white theme)
                   6: Groups with different marker shapes (white theme)
            figsize: Figure size as (width, height) in inches.
            dpi: Dots per inch for the figure resolution.
            line_width: Width of the lines.
            show_markers: Whether to show markers at data points.

        Raises:
            ValueError: If style is not between 1 and 6.
        """
        # Map style names to numbers
        style_map = {
            "solid": 1,
            "markers": 2,
            "shapes": 3,
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

        # Map line chart styles to actual style numbers
        # Dark theme: Style 1 -> 10, Style 2 -> 11, Style 3 -> 12
        # White theme: Style 4 -> 20, Style 5 -> 21, Style 6 -> 22
        if self.style_number <= 3:
            actual_style = 9 + self.style_number
        else:
            actual_style = 16 + self.style_number

        # For line charts, use line chart specific styles
        try:
            self.style_config = get_style(actual_style)
        except ValueError:
            # Fallback if style doesn't exist
            self.style_config = {
                "colors": {
                    "primary": "#C5FFC8",
                    "secondary": "#FA5A46",
                    "accent": "#B19ECC",
                    "background": "#121212",
                    "text": "#C5FFC8",
                    "grid": "#2D3130",
                    "legend_text": "#769978",
                },
                "font": {
                    "family": "Hubot Sans",
                    "size": {"title": 20, "label": 14, "tick": 14},
                    "weight": {"title": 400, "label": 400},
                },
            }

        self.figsize = figsize
        self.dpi = dpi
        self.line_width = line_width
        # Styles 2, 3, 5, 6 have markers (second and third in each theme)
        self.show_markers = show_markers if self.style_number not in [1, 4] else False

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
        """Create a line chart.

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
        # Convert to numpy arrays
        x = np.asarray(x)
        y = np.asarray(y)

        # Create figure and axes if not provided
        if fig is None or ax is None:
            fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        # Apply style configuration
        self._apply_style(fig, ax)

        # Determine color
        line_color = color if color else self.style_config["colors"]["primary"]

        # Plot line
        line = ax.plot(
            x,
            y,
            color=line_color,
            linewidth=self.line_width,
            label=label,
            marker='o' if self.show_markers else None,
            markersize=5 if self.show_markers else 0,
        )

        # Set labels and title
        if title:
            ax.set_title(
                title,
                fontsize=self.style_config["font"]["size"]["title"],
                fontweight=self.style_config["font"]["weight"]["title"],
                pad=10,
                color=self.style_config["colors"]["text"],
                loc='left',
            )

        if xlabel:
            ax.set_xlabel(
                xlabel,
                fontsize=self.style_config["font"]["size"]["label"],
                fontweight=self.style_config["font"]["weight"]["label"],
                labelpad=10,
                color=self.style_config["colors"]["text"],
            )

        if ylabel:
            ax.set_ylabel(
                ylabel,
                fontsize=self.style_config["font"]["size"]["label"],
                fontweight=self.style_config["font"]["weight"]["label"],
                labelpad=10,
                color=self.style_config["colors"]["text"],
            )

        # Add legend if label provided
        if label:
            legend = ax.legend(
                fontsize=self.style_config["font"]["size"]["tick"],
                frameon=False,
            )
            legend_color = self.style_config["colors"].get("legend_text", self.style_config["colors"]["text"])
            for text in legend.get_texts():
                text.set_color(legend_color)

        # Tight layout
        fig.tight_layout()

        return fig, ax

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
        """Create a line chart with multiple data series.

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
            output_format: Output format - 'svg' for SVG string, 'matplotlib' for figure/axes tuple.

        Returns:
            Tuple of (figure, axes) objects or SVG string depending on output_format.
        """
        # Use SVG implementation for all line chart styles
        if output_format == 'svg':
            svg_chart = SVGLineChart()

            # Update colors - include all colors from style config
            svg_chart.colors['background'] = self.style_config['colors']['background']
            svg_chart.colors['title'] = self.style_config['colors']['text']
            svg_chart.colors['legend_text'] = self.style_config['colors']['legend_text']
            svg_chart.colors['grid_vertical'] = self.style_config['colors']['grid']
            svg_chart.colors['grid_horizontal'] = self.style_config['colors']['grid']
            svg_chart.colors['primary'] = self.style_config['colors']['primary']
            svg_chart.colors['secondary'] = self.style_config['colors']['secondary']
            svg_chart.colors['accent'] = self.style_config['colors']['accent']
            # Add additional colors if available
            if 'quaternary' in self.style_config['colors']:
                svg_chart.colors['quaternary'] = self.style_config['colors']['quaternary']
            if 'quinary' in self.style_config['colors']:
                svg_chart.colors['quinary'] = self.style_config['colors']['quinary']

            # Determine marker shapes based on style
            marker_shapes = None
            show_markers = False

            if self.style_number in [2, 5]:
                # Style 2 & 5: Same shape markers (dark & white themes)
                show_markers = True
                marker_shapes = ['circle', 'circle', 'circle']
            elif self.style_number in [3, 6]:
                # Style 3 & 6: Different shapes for each line (dark & white themes)
                show_markers = True
                marker_shapes = ['circle', 'triangle', 'square', 'diamond', 'triangle']

            svg_string = svg_chart.create_chart(
                x, y_series, labels or [], title or "Line Chart",
                line_width=self.line_width,
                show_markers=show_markers,
                marker_shapes=marker_shapes
            )
            return svg_string

        # Matplotlib fallback
        if fig is None or ax is None:
            fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        # Apply style configuration
        self._apply_style(fig, ax)

        # Convert x to numpy array
        x = np.asarray(x)

        # Determine colors
        if colors is None:
            colors = [
                self.style_config["colors"]["primary"],
                self.style_config["colors"]["secondary"],
                self.style_config["colors"]["accent"],
            ]
            # Extend colors if needed
            while len(colors) < len(y_series):
                colors.extend(colors)

        # Convert all y_series to numpy arrays and plot
        for i, y in enumerate(y_series):
            y_array = np.asarray(y)
            line_color = colors[i % len(colors)]
            label = labels[i] if labels and i < len(labels) else None

            ax.plot(
                x,
                y_array,
                color=line_color,
                linewidth=self.line_width,
                label=label,
                marker='o' if self.show_markers else None,
                markersize=5 if self.show_markers else 0,
            )

        # Set labels and title
        if title:
            ax.set_title(
                title,
                fontsize=self.style_config["font"]["size"]["title"],
                fontweight=self.style_config["font"]["weight"]["title"],
                pad=10,
                color=self.style_config["colors"]["text"],
                loc='left',
            )

        if xlabel:
            ax.set_xlabel(
                xlabel,
                fontsize=self.style_config["font"]["size"]["label"],
                fontweight=self.style_config["font"]["weight"]["label"],
                labelpad=10,
                color=self.style_config["colors"]["text"],
            )

        if ylabel:
            ax.set_ylabel(
                ylabel,
                fontsize=self.style_config["font"]["size"]["label"],
                fontweight=self.style_config["font"]["weight"]["label"],
                labelpad=10,
                color=self.style_config["colors"]["text"],
            )

        # Add legend if labels provided
        if labels:
            legend = ax.legend(
                fontsize=self.style_config["font"]["size"]["tick"],
                frameon=False,
            )
            legend_color = self.style_config["colors"].get("legend_text", self.style_config["colors"]["text"])
            for text in legend.get_texts():
                text.set_color(legend_color)

        # Tight layout
        fig.tight_layout()

        return fig, ax

    def _apply_style(self, fig: Figure, ax: Axes) -> None:
        """Apply style configuration to figure and axes."""
        # Set background colors
        fig.patch.set_facecolor(self.style_config["colors"]["background"])
        ax.set_facecolor(self.style_config["colors"]["background"])

        # Configure grid
        ax.grid(
            True,
            alpha=0.3,
            linestyle='-',
            linewidth=1.0,
            color=self.style_config["colors"]["grid"],
            zorder=0,
        )

        # Configure spines
        for spine in ax.spines.values():
            spine.set_visible(False)

        # Configure tick parameters
        ax.tick_params(
            axis="both",
            labelsize=self.style_config["font"]["size"]["tick"],
            colors=self.style_config["colors"]["legend_text"],
            length=0,
            pad=10,
        )

        # Set font family
        plt.rcParams["font.family"] = self.style_config["font"]["family"]

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
