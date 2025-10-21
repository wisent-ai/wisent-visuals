"""Tests for AreaChart class."""

import pytest
import numpy as np
import matplotlib.pyplot as plt
from wisent_plots import AreaChart


class TestAreaChart:
    """Test cases for AreaChart."""

    def test_init_default(self):
        """Test initialization with default parameters."""
        chart = AreaChart()
        assert chart.style_number == 1
        assert chart.edge is False
        assert chart.figsize == (10, 6)
        assert chart.dpi == 100

    def test_init_custom(self):
        """Test initialization with custom parameters."""
        chart = AreaChart(style=3, edge=True, figsize=(12, 8), dpi=150)
        assert chart.style_number == 3
        assert chart.edge is True
        assert chart.figsize == (12, 8)
        assert chart.dpi == 150

    def test_init_invalid_style(self):
        """Test that invalid style raises ValueError."""
        with pytest.raises(ValueError, match="Style 6 not found"):
            AreaChart(style=6)

    def test_plot_basic(self):
        """Test basic plotting functionality."""
        chart = AreaChart(style=1)
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 3, 5, 4]

        fig, ax = chart.plot(x, y)

        assert fig is not None
        assert ax is not None
        plt.close(fig)

    def test_plot_with_labels(self):
        """Test plotting with labels and title."""
        chart = AreaChart(style=2)
        x = np.linspace(0, 10, 50)
        y = np.sin(x)

        fig, ax = chart.plot(
            x, y,
            title="Test Chart",
            xlabel="X Axis",
            ylabel="Y Axis",
            label="Sine Wave"
        )

        assert ax.get_title() == "Test Chart"
        assert ax.get_xlabel() == "X Axis"
        assert ax.get_ylabel() == "Y Axis"
        plt.close(fig)

    def test_plot_custom_color(self):
        """Test plotting with custom color."""
        chart = AreaChart(style=1)
        x = [1, 2, 3]
        y = [1, 2, 1]

        fig, ax = chart.plot(x, y, color="#FF5733")

        assert fig is not None
        plt.close(fig)

    def test_plot_multiple_basic(self):
        """Test multiple series plotting."""
        chart = AreaChart(style=1)
        x = [1, 2, 3, 4]
        y1 = [1, 2, 3, 4]
        y2 = [4, 3, 2, 1]

        fig, ax = chart.plot_multiple(x, [y1, y2])

        assert fig is not None
        assert ax is not None
        plt.close(fig)

    def test_plot_multiple_with_labels(self):
        """Test multiple series with labels."""
        chart = AreaChart(style=2)
        x = np.linspace(0, 5, 20)
        y1 = np.sin(x)
        y2 = np.cos(x)

        fig, ax = chart.plot_multiple(
            x, [y1, y2],
            labels=["Series 1", "Series 2"],
            title="Multiple Series"
        )

        assert ax.get_title() == "Multiple Series"
        assert ax.get_legend() is not None
        plt.close(fig)

    def test_plot_multiple_custom_colors(self):
        """Test multiple series with custom colors."""
        chart = AreaChart(style=1)
        x = [1, 2, 3]
        y1 = [1, 2, 3]
        y2 = [3, 2, 1]

        fig, ax = chart.plot_multiple(
            x, [y1, y2],
            colors=["#FF5733", "#33FF57"]
        )

        assert fig is not None
        plt.close(fig)

    def test_all_styles(self):
        """Test that all 5 styles work."""
        x = [1, 2, 3, 4, 5]
        y = [1, 3, 2, 4, 3]

        for style_num in range(1, 6):
            chart = AreaChart(style=style_num)
            fig, ax = chart.plot(x, y, title=f"Style {style_num}")
            assert fig is not None
            plt.close(fig)

    def test_edge_enabled(self):
        """Test plotting with edge enabled."""
        chart = AreaChart(style=1, edge=True)
        x = [1, 2, 3]
        y = [1, 2, 1]

        fig, ax = chart.plot(x, y)

        assert fig is not None
        plt.close(fig)

    def test_numpy_arrays(self):
        """Test that numpy arrays work as input."""
        chart = AreaChart(style=1)
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 4, 3, 5, 4])

        fig, ax = chart.plot(x, y)

        assert fig is not None
        plt.close(fig)

    def test_existing_fig_ax(self):
        """Test plotting on existing figure and axes."""
        fig, ax = plt.subplots()
        chart = AreaChart(style=1)
        x = [1, 2, 3]
        y = [1, 2, 1]

        result_fig, result_ax = chart.plot(x, y, fig=fig, ax=ax)

        assert result_fig is fig
        assert result_ax is ax
        plt.close(fig)

    def test_save(self, tmp_path):
        """Test saving figure to file."""
        chart = AreaChart(style=1)
        x = [1, 2, 3]
        y = [1, 2, 1]

        fig, ax = chart.plot(x, y)

        # Save to temporary file
        output_file = tmp_path / "test_chart.png"
        chart.save(fig, str(output_file))

        assert output_file.exists()
        plt.close(fig)

    def test_save_custom_dpi(self, tmp_path):
        """Test saving with custom DPI."""
        chart = AreaChart(style=1)
        x = [1, 2, 3]
        y = [1, 2, 1]

        fig, ax = chart.plot(x, y)

        output_file = tmp_path / "test_chart_dpi.png"
        chart.save(fig, str(output_file), dpi=300)

        assert output_file.exists()
        plt.close(fig)

    def test_save_transparent(self, tmp_path):
        """Test saving with transparent background."""
        chart = AreaChart(style=1)
        x = [1, 2, 3]
        y = [1, 2, 1]

        fig, ax = chart.plot(x, y)

        output_file = tmp_path / "test_chart_transparent.png"
        chart.save(fig, str(output_file), transparent=True)

        assert output_file.exists()
        plt.close(fig)
