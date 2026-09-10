"""Single-series area rendering through the real Matplotlib backend."""

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np

from .appearance import _apply_style, _get_edge_color

if TYPE_CHECKING:
    from ..area_chart import AreaChart


def _plot_single(chart: "AreaChart", x, y, title, xlabel, ylabel, color, label, fig, ax):
    # Convert to numpy arrays
    x = np.asarray(x)
    y = np.asarray(y)

    # Create figure and axes if not provided
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=chart.figsize, dpi=chart.dpi)

    # Apply style configuration
    _apply_style(chart, fig, ax)

    # Determine colors
    fill_color = color if color else chart.style_config["colors"]["primary"]
    edge_color = _get_edge_color(chart, fill_color)

    # Plot area
    edge_width = chart.style_config["edge"]["width"] if chart.edge else 0
    edge_line_color = edge_color if chart.edge else None

    # Fill area
    ax.fill_between(
        x,
        y,
        alpha=chart.style_config["fill"]["alpha"],
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
        linewidth=chart.style_config["line"]["width"],
        linestyle=chart.style_config["line"]["style"],
        alpha=chart.style_config["line"]["alpha"],
    )

    # Set labels and title
    if title:
        ax.set_title(
            title,
            fontsize=chart.style_config["font"]["size"]["title"],
            fontweight=chart.style_config["font"]["weight"]["title"],
            pad=chart.style_config["spacing"]["title_pad"],
            color=chart.style_config["colors"]["text"],
            loc="left",  # Left-align title like in Figma
        )

    if xlabel:
        ax.set_xlabel(
            xlabel,
            fontsize=chart.style_config["font"]["size"]["label"],
            fontweight=chart.style_config["font"]["weight"]["label"],
            labelpad=chart.style_config["spacing"]["label_pad"],
            color=chart.style_config["colors"]["text"],
        )

    if ylabel:
        ax.set_ylabel(
            ylabel,
            fontsize=chart.style_config["font"]["size"]["label"],
            fontweight=chart.style_config["font"]["weight"]["label"],
            labelpad=chart.style_config["spacing"]["label_pad"],
            color=chart.style_config["colors"]["text"],
        )

    # Add legend if label provided
    if label:
        legend = ax.legend(
            fontsize=chart.style_config["font"]["size"]["tick"],
            frameon=False,
        )
        # Set legend text color
        legend_color = chart.style_config["colors"].get(
            "legend_text", chart.style_config["colors"]["text"]
        )
        for text in legend.get_texts():
            text.set_color(legend_color)

    # Tight layout
    fig.tight_layout()

    return fig, ax
