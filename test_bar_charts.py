"""Test bar charts for all themes and styles."""

from wisent_plots import BarChart

# Sample data - 7 categories with 3 data series each
categories = [
    "Day Time 1",
    "Day Time 2",
    "Day Time 3",
    "Day Time 4",
    "Day Time 5",
    "Day Time 6",
    "Day Time 7"
]

# Three data series (One, Two, Three)
series = [
    [30, 35, 25, 20, 35, 30, 25],  # One
    [25, 30, 35, 40, 30, 25, 40],  # Two
    [20, 25, 25, 30, 25, 30, 30]   # Three
]

labels = ["One", "Two", "Three"]

# Test all combinations of themes and styles
themes = ['brand', 'black', 'white']
styles = [1, 2, 3, 4, 5]

for theme in themes:
    for style in styles:
        print(f"Generating {theme} theme, style {style}...")

        chart = BarChart(style=style, theme=theme)

        svg_output = chart.plot(
            categories,
            series,
            labels,
            title="Bar Chart"
        )

        filename = f'examples/bar_chart_{theme}_style{style}.svg'
        with open(filename, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(svg_output)

        print(f"  ✓ Saved to {filename}")

print("\n✓ All bar charts generated!")
