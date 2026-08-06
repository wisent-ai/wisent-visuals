"""Wisent Plots - Create beautiful plots in Wisent brand styling."""

__version__ = "0.2.0"

from wisent_plots.banner import Banner, BannerConfig
from wisent_plots.brand import BRAND_COLORS, FONT_FAMILY

from wisent_plots.charts import (
    AreaChart,
    BarChart,
    BubbleChart,
    ColumnChart,
    LineChart,
    PieChart,
    RadarChart,
)

__all__ = [
    "Banner",
    "BannerConfig",
    "BRAND_COLORS",
    "FONT_FAMILY",
    "AreaChart",
    "BarChart",
    "BubbleChart",
    "ColumnChart",
    "LineChart",
    "PieChart",
    "RadarChart",
]
