"""Area chart implementation with Wisent brand styling."""

from typing import Optional, Union, List, Tuple
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import numpy as np

from wisent_plots.styles.style_config import get_style
from wisent_plots.charts.area.svg_area_chart import SVGAreaChart
from wisent_plots.charts.area.svg_area_chart_gradient import SVGAreaChartGradient
from wisent_plots.charts.area.svg_area_chart_pattern import SVGAreaChartPattern
from wisent_plots.charts.area.svg_area_chart_2patterns import SVGAreaChart2Patterns


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
        # Convert to numpy arrays
        x = np.asarray(x)
        y = np.asarray(y)

        # Create figure and axes if not provided
        if fig is None or ax is None:
            fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        # Apply style configuration
        self._apply_style(fig, ax)

        # Determine colors
        fill_color = color if color else self.style_config["colors"]["primary"]
        edge_color = self._get_edge_color(fill_color)

        # Plot area
        edge_width = self.style_config["edge"]["width"] if self.edge else 0
        edge_line_color = edge_color if self.edge else None

        # Fill area
        ax.fill_between(
            x,
            y,
            alpha=self.style_config["fill"]["alpha"],
            color=fill_color,
            label=label,
            edgecolor=edge_line_color,
            linewidth=edge_width,
        )

        # Plot line on top
        ax.plot(
            x,
            y,
            color=fill_color,
            linewidth=self.style_config["line"]["width"],
            linestyle=self.style_config["line"]["style"],
            alpha=self.style_config["line"]["alpha"],
        )

        # Set labels and title
        if title:
            ax.set_title(
                title,
                fontsize=self.style_config["font"]["size"]["title"],
                fontweight=self.style_config["font"]["weight"]["title"],
                pad=self.style_config["spacing"]["title_pad"],
                color=self.style_config["colors"]["text"],
                loc='left',  # Left-align title like in Figma
            )

        if xlabel:
            ax.set_xlabel(
                xlabel,
                fontsize=self.style_config["font"]["size"]["label"],
                fontweight=self.style_config["font"]["weight"]["label"],
                labelpad=self.style_config["spacing"]["label_pad"],
                color=self.style_config["colors"]["text"],
            )

        if ylabel:
            ax.set_ylabel(
                ylabel,
                fontsize=self.style_config["font"]["size"]["label"],
                fontweight=self.style_config["font"]["weight"]["label"],
                labelpad=self.style_config["spacing"]["label_pad"],
                color=self.style_config["colors"]["text"],
            )

        # Add legend if label provided
        if label:
            legend = ax.legend(
                fontsize=self.style_config["font"]["size"]["tick"],
                frameon=False,
            )
            # Set legend text color
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
        # Create figure and axes if not provided
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

        # Convert all y_series to numpy arrays
        y_arrays = [np.asarray(y) for y in y_series]

        # If stacked, plot using stackplot for proper stacking
        if self.stacked:
            # Reverse the order for bottom-to-top stacking (darkest at bottom)
            y_arrays_reversed = list(reversed(y_arrays))
            colors_reversed = list(reversed(colors[:len(y_arrays)]))
            labels_reversed = list(reversed(labels)) if labels else None

            # Create stacked areas
            ax.stackplot(
                x,
                *y_arrays_reversed,
                colors=colors_reversed,
                labels=labels_reversed,
                alpha=self.style_config["fill"]["alpha"],
                edgecolor='none',
            )

            # Add edges if requested
            if self.edge:
                # Draw edge lines between stacked areas
                cumulative = np.zeros_like(x, dtype=float)
                for i, y in enumerate(y_arrays_reversed):
                    cumulative += y
                    edge_color = self._get_edge_color(colors_reversed[i])
                    ax.plot(
                        x,
                        cumulative,
                        color=edge_color,
                        linewidth=self.style_config["edge"]["width"],
                        alpha=1.0,
                        zorder=10,
                    )
        else:
            # Overlapping mode (original behavior)
            for i, y in enumerate(y_arrays):
                fill_color = colors[i % len(colors)]
                edge_color = self._get_edge_color(fill_color)
                label = labels[i] if labels and i < len(labels) else None

                edge_width = self.style_config["edge"]["width"] if self.edge else 0
                edge_line_color = edge_color if self.edge else None

                # Fill area
                ax.fill_between(
                    x,
                    y,
                    alpha=self.style_config["fill"]["alpha"],
                    color=fill_color,
                    label=label,
                    edgecolor=edge_line_color,
                    linewidth=edge_width,
                )

                # Plot line
                ax.plot(
                    x,
                    y,
                    color=fill_color,
                    linewidth=self.style_config["line"]["width"],
                    linestyle=self.style_config["line"]["style"],
                    alpha=self.style_config["line"]["alpha"],
                )

        # Set labels and title
        if title:
            ax.set_title(
                title,
                fontsize=self.style_config["font"]["size"]["title"],
                fontweight=self.style_config["font"]["weight"]["title"],
                pad=self.style_config["spacing"]["title_pad"],
                color=self.style_config["colors"]["text"],
                loc='left',  # Left-align title like in Figma
            )

        if xlabel:
            ax.set_xlabel(
                xlabel,
                fontsize=self.style_config["font"]["size"]["label"],
                fontweight=self.style_config["font"]["weight"]["label"],
                labelpad=self.style_config["spacing"]["label_pad"],
                color=self.style_config["colors"]["text"],
            )

        if ylabel:
            ax.set_ylabel(
                ylabel,
                fontsize=self.style_config["font"]["size"]["label"],
                fontweight=self.style_config["font"]["weight"]["label"],
                labelpad=self.style_config["spacing"]["label_pad"],
                color=self.style_config["colors"]["text"],
            )

        # Add horizontal legend with color boxes if labels provided
        if labels:
            self._add_horizontal_legend(fig, ax, labels, colors[:len(labels)])

        # Tight layout
        fig.tight_layout()

        return fig, ax

    def _apply_style(self, fig: Figure, ax: Axes) -> None:
        """Apply style configuration to figure and axes."""
        # Set background colors
        fig.patch.set_facecolor(self.style_config["colors"]["background"])
        ax.set_facecolor(self.style_config["colors"]["background"])

        # Configure grid - only vertical lines for Figma style
        ax.grid(
            True,
            axis='x',  # Only vertical grid lines
            alpha=self.style_config["grid"]["alpha"],
            linestyle=self.style_config["grid"]["linestyle"],
            linewidth=self.style_config["grid"]["linewidth"],
            color=self.style_config["colors"]["grid"],
            zorder=0,
        )
        ax.grid(False, axis='y')  # No horizontal grid lines

        # Hide Y-axis spine and ticks (Figma design has no Y-axis)
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)

        # Hide Y-axis ticks and labels
        ax.yaxis.set_visible(False)

        # Configure X-axis tick parameters
        ax.tick_params(
            axis="x",
            labelsize=self.style_config["font"]["size"]["tick"],
            colors=self.style_config["colors"]["legend_text"],
            length=0,  # No tick marks
            pad=10,
        )

        # Format x-axis labels with leading zeros
        self._format_xaxis_labels(ax)

        # Set font family
        plt.rcParams["font.family"] = self.style_config["font"]["family"]

    def _get_edge_color(self, fill_color: str) -> str:
        """Get edge color based on fill color.

        If style specifies 'auto', returns a darker version of the fill color.
        Otherwise returns the specified edge color.
        """
        edge_config = self.style_config["edge"]["color"]

        if edge_config == "auto" or edge_config == "darker":
            # Convert hex to RGB, darken, and convert back
            if fill_color.startswith("#"):
                # Remove '#' and convert to RGB
                rgb = tuple(int(fill_color[i:i+2], 16) / 255.0 for i in (1, 3, 5))
                # Darken by 30%
                darkened = tuple(max(0, c * 0.7) for c in rgb)
                # Convert back to hex
                return "#{:02x}{:02x}{:02x}".format(
                    int(darkened[0] * 255),
                    int(darkened[1] * 255),
                    int(darkened[2] * 255)
                )
            else:
                return fill_color
        elif edge_config:
            return edge_config
        else:
            return fill_color

    def _add_horizontal_legend(self, fig: Figure, ax: Axes, labels: List[str], colors: List[str]) -> None:
        """Add horizontal legend with color boxes at the top."""
        from matplotlib.patches import Rectangle

        legend_color = self.style_config["colors"].get("legend_text", self.style_config["colors"]["text"])
        font_size = self.style_config["font"]["size"]["tick"]

        # Create legend elements manually
        legend_elements = []
        for i, (label, color) in enumerate(zip(labels, colors)):
            # Add small rectangle for color box (20x10 px as in Figma)
            rect = Rectangle((0, 0), 1, 1, facecolor=color, edgecolor='none')
            legend_elements.append((rect, label))

        # Create legend with horizontal layout
        legend = ax.legend(
            [elem[0] for elem in legend_elements],
            [elem[1] for elem in legend_elements],
            loc='upper left',
            bbox_to_anchor=(0.02, 0.98),
            ncol=len(labels),  # All items in one row
            frameon=False,
            fontsize=font_size,
            handlelength=1.2,
            handleheight=0.6,
            columnspacing=1.5,
        )

        # Set legend text color
        for text in legend.get_texts():
            text.set_color(legend_color)

    def _format_xaxis_labels(self, ax: Axes) -> None:
        """Format x-axis labels with leading zeros (01, 02, etc)."""
        from matplotlib.ticker import FuncFormatter

        def format_with_leading_zero(x, pos):
            """Format tick labels with leading zeros."""
            return f"{int(x):02d}" if x >= 0 else str(int(x))

        ax.xaxis.set_major_formatter(FuncFormatter(format_with_leading_zero))

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
