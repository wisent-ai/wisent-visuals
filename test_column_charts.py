"""Test column charts for all themes and styles."""

from wisent_plots import ColumnChart

# Sample data - 5 categories (Q1-Q5) with 3 data series each
categories = ["Q1", "Q2", "Q3", "Q4", "Q5"]

# Three data series (One, Two, Three)
series = [
    [800, 550, 1000, 350, 400],  # One
    [500, 250, 750, 550, 500],   # Two
    [250, 350, 300, 600, 600]    # Three
]

labels = ["One", "Two", "Three"]

# Test all combinations of themes and styles
themes = ['brand', 'black', 'white']
styles = [1, 2, 3, 4, 5]

for theme in themes:
    for style in styles:
        print(f"Generating {theme} theme, style {style}...")

        chart = ColumnChart(style=style, theme=theme)

        svg_output = chart.plot(
            categories,
            series,
            labels,
            title="Group Column Chart"
        )

        filename = f'examples/column_chart_{theme}_style{style}.svg'
        with open(filename, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(svg_output)

        print(f"  ✓ Saved to {filename}")

print("\n✓ All column charts generated!")
