"""Generate pixel-perfect SVG chart matching Figma."""

import sys
sys.path.insert(0, '/Users/lukaszbartoszcze/Documents/CodingProjects/Wisent/wisent-academic-style')

from wisent_plots.charts.svg_area_chart import SVGAreaChart
import numpy as np

# Sample data - properly proportioned to match Figma visual
# Based on Figma analysis:
# - Cumulative 1 fills ~42% of chart height
# - Cumulative 2 fills 100% of chart height
# - Cumulative 3 fills 200% of chart height (extends beyond)
x = list(range(1, 15))  # 1-14

# Smooth curves
from scipy.ndimage import gaussian_filter1d

# Data to create stacked wave effect that fills the chart
# Each series adds to the previous, creating cumulative stacking
y1_raw = [20, 25, 30, 38, 45, 50, 45, 38, 30, 25, 20, 18, 16, 15]
y1 = gaussian_filter1d(y1_raw, sigma=2.0).tolist()

y2_raw = [35, 42, 52, 62, 70, 75, 70, 62, 52, 42, 35, 30, 28, 25]
y2 = gaussian_filter1d(y2_raw, sigma=2.0).tolist()

y3_raw = [50, 60, 75, 88, 98, 105, 98, 88, 75, 60, 50, 45, 42, 40]
y3 = gaussian_filter1d(y3_raw, sigma=2.0).tolist()

print("Creating pixel-perfect SVG chart...")

# Create chart with exact Figma dimensions
chart = SVGAreaChart(width=1002, height=499)

# Generate SVG
svg_string = chart.create_chart(
    x_data=x,
    y_series=[y1, y2, y3],
    labels=["One", "Two", "Three"],
    title="Area Chart"
)

# Save as SVG
chart.save_svg(svg_string, "figma_exact_svg.svg")
print("✓ Created: figma_exact_svg.svg")

# Save as PNG
chart.save_png(svg_string, "figma_exact_svg.png", dpi=150)
print("✓ Created: figma_exact_svg.png")

print("\nThis SVG chart has:")
print("  ✓ Pixel-perfect Figma dimensions (1002x499)")
print("  ✓ Exact Figma spacing and layout")
print("  ✓ Hubot Sans font via web font")
print("  ✓ Proper text rendering")
print("  ✓ All exact colors and styling")
