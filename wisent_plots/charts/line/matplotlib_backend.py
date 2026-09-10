"""Single and multiple line rendering through the real Matplotlib backend."""

from typing import TYPE_CHECKING
import matplotlib.pyplot as plt
import numpy as np

if TYPE_CHECKING:
    from .line_chart import LineChart

def _plot_single(chart: "LineChart", x, y, title, xlabel, ylabel, color, label, fig, ax):
        # Convert to numpy arrays
        x = np.asarray(x)
        y = np.asarray(y)

        # Create figure and axes if not provided
        if fig is None or ax is None:
            fig, ax = plt.subplots(figsize=chart.figsize, dpi=chart.dpi)

        # Apply style configuration
        _apply_style(chart, fig, ax)

        # Determine color
        line_color = color if color else chart.style_config["colors"]["primary"]

        # Plot line
        line = ax.plot(
            x,
            y,
            color=line_color,
            linewidth=chart.line_width,
            label=label,
            marker='o' if chart.show_markers else None,
            markersize=5 if chart.show_markers else 0,
        )

        # Set labels and title
        if title:
            ax.set_title(
                title,
                fontsize=chart.style_config["font"]["size"]["title"],
                fontweight=chart.style_config["font"]["weight"]["title"],
                pad=10,
                color=chart.style_config["colors"]["text"],
                loc='left',
            )

        if xlabel:
            ax.set_xlabel(
                xlabel,
                fontsize=chart.style_config["font"]["size"]["label"],
                fontweight=chart.style_config["font"]["weight"]["label"],
                labelpad=10,
                color=chart.style_config["colors"]["text"],
            )

        if ylabel:
            ax.set_ylabel(
                ylabel,
                fontsize=chart.style_config["font"]["size"]["label"],
                fontweight=chart.style_config["font"]["weight"]["label"],
                labelpad=10,
                color=chart.style_config["colors"]["text"],
            )

        # Add legend if label provided
        if label:
            legend = ax.legend(
                fontsize=chart.style_config["font"]["size"]["tick"],
                frameon=False,
            )
            legend_color = chart.style_config["colors"].get("legend_text", chart.style_config["colors"]["text"])
            for text in legend.get_texts():
                text.set_color(legend_color)

        # Tight layout
        fig.tight_layout()

        return fig, ax


def _plot_multiple(chart: "LineChart", x, y_series, labels, colors, title, xlabel, ylabel, fig, ax):
        # Matplotlib fallback
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

        # Convert all y_series to numpy arrays and plot
        for i, y in enumerate(y_series):
            y_array = np.asarray(y)
            line_color = colors[i % len(colors)]
            label = labels[i] if labels and i < len(labels) else None

            ax.plot(
                x,
                y_array,
                color=line_color,
                linewidth=chart.line_width,
                label=label,
                marker='o' if chart.show_markers else None,
                markersize=5 if chart.show_markers else 0,
            )

        # Set labels and title
        if title:
            ax.set_title(
                title,
                fontsize=chart.style_config["font"]["size"]["title"],
                fontweight=chart.style_config["font"]["weight"]["title"],
                pad=10,
                color=chart.style_config["colors"]["text"],
                loc='left',
            )

        if xlabel:
            ax.set_xlabel(
                xlabel,
                fontsize=chart.style_config["font"]["size"]["label"],
                fontweight=chart.style_config["font"]["weight"]["label"],
                labelpad=10,
                color=chart.style_config["colors"]["text"],
            )

        if ylabel:
            ax.set_ylabel(
                ylabel,
                fontsize=chart.style_config["font"]["size"]["label"],
                fontweight=chart.style_config["font"]["weight"]["label"],
                labelpad=10,
                color=chart.style_config["colors"]["text"],
            )

        # Add legend if labels provided
        if labels:
            legend = ax.legend(
                fontsize=chart.style_config["font"]["size"]["tick"],
                frameon=False,
            )
            legend_color = chart.style_config["colors"].get("legend_text", chart.style_config["colors"]["text"])
            for text in legend.get_texts():
                text.set_color(legend_color)

        # Tight layout
        fig.tight_layout()

        return fig, ax


def _apply_style(chart: "LineChart", fig, ax):
        """Apply style configuration to figure and axes."""
        # Set background colors
        fig.patch.set_facecolor(chart.style_config["colors"]["background"])
        ax.set_facecolor(chart.style_config["colors"]["background"])

        # Configure grid
        ax.grid(
            True,
            alpha=0.3,
            linestyle='-',
            linewidth=1.0,
            color=chart.style_config["colors"]["grid"],
            zorder=0,
        )

        # Configure spines
        for spine in ax.spines.values():
            spine.set_visible(False)

        # Configure tick parameters
        ax.tick_params(
            axis="both",
            labelsize=chart.style_config["font"]["size"]["tick"],
            colors=chart.style_config["colors"]["legend_text"],
            length=0,
            pad=10,
        )

        # Set font family
        plt.rcParams["font.family"] = chart.style_config["font"]["family"]

