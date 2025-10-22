"""Test script for area chart style 3 (pattern with crossing lines and noise)."""

from wisent_plots import AreaChart

# Sample data
x_data = list(range(1, 15))
y1 = [20, 25, 30, 28, 35, 40, 38, 42, 45, 43, 48, 50, 52, 55]
y2 = [15, 18, 22, 20, 25, 28, 26, 30, 32, 30, 35, 37, 38, 40]
y3 = [10, 12, 15, 13, 18, 20, 18, 22, 24, 22, 26, 28, 29, 30]

y_series = [y1, y2, y3]
labels = ["One", "Two", "Three"]

# Create chart with style 3 (pattern)
chart = AreaChart(style=3, edge=True)

# Generate SVG
svg_output = chart.plot_multiple(
    x_data,
    y_series,
    labels=labels,
    title="Area Chart",
    output_format='svg'
)

# Save to file
with open('examples/area_chart_style3_noise.svg', 'w') as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write(svg_output)

print("✓ Chart saved to examples/area_chart_style3_noise.svg")
