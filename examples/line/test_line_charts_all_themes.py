"""Test all line chart themes and styles."""

from wisent_plots.charts import LineChart
import numpy as np

# Sample data - 3 series
np.random.seed(42)
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
series1 = [100, 120, 115, 134, 145, 150]
series2 = [80, 95, 100, 110, 120, 125]
series3 = [60, 70, 75, 85, 95, 100]

labels = ["One", "Two", "Three"]

# Line chart styles
# Style 1: Solid color palette (dark theme)
# Style 2: Solid color with markers (dark theme)
# Style 3: Groups with different marker shapes (dark theme)
# Style 4: Solid color palette (white theme)
# Style 5: Solid color with markers (white theme)
# Style 6: Groups with different marker shapes (white theme)

styles_dark = [
    (1, "style1", "Solid colors (dark)"),
    (2, "style2", "With markers (dark)"),
    (3, "style3", "Different shapes (dark)"),
]

styles_white = [
    (4, "style4", "Solid colors (white)"),
    (5, "style5", "With markers (white)"),
    (6, "style6", "Different shapes (white)"),
]

# Map styles to appropriate themes
theme_styles = [
    ("black", "Black Theme", styles_dark),
    ("brand", "Brand Colors", styles_dark),
    ("white", "White Theme", styles_white),
]

for theme_folder, theme_name, styles in theme_styles:
    print(f"\n{'='*60}")
    print(f"{theme_name}")
    print('='*60)

    for style_num, style_name, style_desc in styles:
        print(f"\nCreating {style_desc} line chart...")

        try:
            # Create line chart
            chart = LineChart(style=style_num)
            svg_string = chart.plot_multiple(
                x=months,
                y_series=[series1, series2, series3],
                labels=labels,
                title="Line chart",
                output_format='svg'
            )

            # Save to file
            filename = f'examples/line/{theme_folder}/line_chart_{theme_folder}_{style_name}.svg'
            with open(filename, 'w') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write(svg_string)
            print(f"✓ Created: {filename}")
        except Exception as e:
            print(f"✗ Error creating {style_name}: {e}")

print("\n" + "="*60)
print("Line chart generation complete!")
print("="*60)
