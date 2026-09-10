"""Area-specific axes, edges, tick formatting and legends."""

from typing import TYPE_CHECKING, List

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

if TYPE_CHECKING:
    from ..area_chart import AreaChart


def _apply_style(chart: "AreaChart", fig: Figure, ax: Axes) -> None:
    """Apply style configuration to figure and axes."""
    # Set background colors
    fig.patch.set_facecolor(chart.style_config["colors"]["background"])
    ax.set_facecolor(chart.style_config["colors"]["background"])

    # Configure grid - only vertical lines for Figma style
    ax.grid(
        True,
        axis="x",  # Only vertical grid lines
        alpha=chart.style_config["grid"]["alpha"],
        linestyle=chart.style_config["grid"]["linestyle"],
        linewidth=chart.style_config["grid"]["linewidth"],
        color=chart.style_config["colors"]["grid"],
        zorder=0,
    )
    ax.grid(False, axis="y")  # No horizontal grid lines

    # Hide Y-axis spine and ticks (Figma design has no Y-axis)
    ax.spines["left"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["bottom"].set_visible(False)

    # Hide Y-axis ticks and labels
    ax.yaxis.set_visible(False)

    # Configure X-axis tick parameters
    ax.tick_params(
        axis="x",
        labelsize=chart.style_config["font"]["size"]["tick"],
        colors=chart.style_config["colors"]["legend_text"],
        length=0,  # No tick marks
        pad=10,
    )

    # Format x-axis labels with leading zeros
    _format_xaxis_labels(ax)

    # Set font family
    plt.rcParams["font.family"] = chart.style_config["font"]["family"]


def _get_edge_color(chart: "AreaChart", fill_color: str) -> str:
    """Get edge color based on fill color.

    If style specifies 'auto', returns a darker version of the fill color.
    Otherwise returns the specified edge color.
    """
    edge_config = chart.style_config["edge"]["color"]

    if edge_config == "auto" or edge_config == "darker":
        # Convert hex to RGB, darken, and convert back
        if fill_color.startswith("#"):
            # Remove '#' and convert to RGB
            rgb = tuple(int(fill_color[i : i + 2], 16) / 255.0 for i in (1, 3, 5))
            # Darken by 30%
            darkened = tuple(max(0, c * 0.7) for c in rgb)
            # Convert back to hex
            return "#{:02x}{:02x}{:02x}".format(
                int(darkened[0] * 255), int(darkened[1] * 255), int(darkened[2] * 255)
            )
        else:
            return fill_color
    elif edge_config:
        return edge_config
    else:
        return fill_color


def _add_horizontal_legend(
    chart: "AreaChart", ax: Axes, labels: List[str], colors: List[str]
) -> None:
    """Add horizontal legend with color boxes at the top."""
    from matplotlib.patches import Rectangle

    legend_color = chart.style_config["colors"].get(
        "legend_text", chart.style_config["colors"]["text"]
    )
    font_size = chart.style_config["font"]["size"]["tick"]

    # Create legend elements manually
    legend_elements = []
    for i, (label, color) in enumerate(zip(labels, colors)):
        # Add small rectangle for color box (20x10 px as in Figma)
        rect = Rectangle((0, 0), 1, 1, facecolor=color, edgecolor="none")
        legend_elements.append((rect, label))

    # Create legend with horizontal layout
    legend = ax.legend(
        [elem[0] for elem in legend_elements],
        [elem[1] for elem in legend_elements],
        loc="upper left",
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


def _format_xaxis_labels(ax: Axes) -> None:
    """Format x-axis labels with leading zeros (01, 02, etc)."""
    from matplotlib.ticker import FuncFormatter

    def format_with_leading_zero(x, pos):
        """Format tick labels with leading zeros."""
        return f"{int(x):02d}" if x >= 0 else str(int(x))

    ax.xaxis.set_major_formatter(FuncFormatter(format_with_leading_zero))
