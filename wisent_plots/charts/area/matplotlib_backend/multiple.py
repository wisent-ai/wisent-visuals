"""Stacked and overlapping area rendering through Matplotlib."""

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import numpy as np

from .appearance import _add_horizontal_legend, _apply_style, _get_edge_color

if TYPE_CHECKING:
    from ..area_chart import AreaChart


def _plot_multiple(chart: "AreaChart", x, y_series, labels, colors, title, xlabel, ylabel, fig, ax):
    # Create figure and axes if not provided
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=chart.figsize, dpi=chart.dpi)

    # Apply style configuration
    _apply_style(chart, fig, ax)

    # Convert x to numpy array
    x = np.asarray(x)

    # Determine colors
    if colors is None:
        colors = [
            chart.style_config["colors"]["primary"],
            chart.style_config["colors"]["secondary"],
            chart.style_config["colors"]["accent"],
        ]
        # Extend colors if needed
        while len(colors) < len(y_series):
            colors.extend(colors)

    # Convert all y_series to numpy arrays
    y_arrays = [np.asarray(y) for y in y_series]

    # If stacked, plot using stackplot for proper stacking
    if chart.stacked:
        # Reverse the order for bottom-to-top stacking (darkest at bottom)
        y_arrays_reversed = list(reversed(y_arrays))
        colors_reversed = list(reversed(colors[: len(y_arrays)]))
        labels_reversed = list(reversed(labels)) if labels else None

        # Create stacked areas
        ax.stackplot(
            x,
            *y_arrays_reversed,
            colors=colors_reversed,
            labels=labels_reversed,
            alpha=chart.style_config["fill"]["alpha"],
            edgecolor="none",
        )

        # Add edges if requested
        if chart.edge:
            # Draw edge lines between stacked areas
            cumulative = np.zeros_like(x, dtype=float)
            for i, y in enumerate(y_arrays_reversed):
                cumulative += y
                edge_color = _get_edge_color(chart, colors_reversed[i])
                ax.plot(
                    x,
                    cumulative,
                    color=edge_color,
                    linewidth=chart.style_config["edge"]["width"],
                    alpha=1.0,
                    zorder=10,
                )
    else:
        # Overlapping mode (original behavior)
        for i, y in enumerate(y_arrays):
            fill_color = colors[i % len(colors)]
            edge_color = _get_edge_color(chart, fill_color)
            label = labels[i] if labels and i < len(labels) else None

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

            # Plot line
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

    # Add horizontal legend with color boxes if labels provided
    if labels:
        _add_horizontal_legend(chart, ax, labels, colors[: len(labels)])

    # Tight layout
    fig.tight_layout()

    return fig, ax
