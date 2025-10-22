"""Test all area chart themes and styles."""

from wisent_plots.charts import AreaChart
import numpy as np

# Sample data - 3 series
np.random.seed(42)
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
series1 = [100, 120, 115, 134, 145, 150]
series2 = [80, 95, 100, 110, 120, 125]
series3 = [60, 70, 75, 85, 95, 100]

labels = ["One", "Two", "Three"]

# Create all theme and style variations
# Style 1: Gradient with lighter edges
# Style 2: Gradient
# Style 3: Pattern/texture
# Style 4: Solid colors with opacity
# Style 5: Solid colors (no opacity)

styles = [
    (1, "style1", "Gradient with lighter edges"),
    (2, "style2", "Gradient"),
    (3, "style3", "Pattern/Texture"),
    (4, "style4", "Solid with opacity"),
]

themes = [
    ("black", "Black/Dark Theme"),
    ("brand", "Brand Colors"),
    ("white", "White/Light Theme"),
]

for theme_folder, theme_name in themes:
    print(f"\n{'='*60}")
    print(f"{theme_name}")
    print('='*60)

    for style_num, style_name, style_desc in styles:
        print(f"\nCreating {style_desc} area chart...")

        # Create area chart
        chart = AreaChart(style=style_num, output_format='svg')

        try:
            svg_string = chart.plot_multiple(
                x=months,
                y_series=[series1, series2, series3],
                labels=labels,
                title="Area Chart"
            )

            # Save to file
            filename = f'examples/area/{theme_folder}/area_chart_{theme_folder}_{style_name}.svg'
            chart.save_svg(svg_string, filename)
            print(f"✓ Created: {filename}")
        except Exception as e:
            print(f"✗ Error creating {style_name}: {e}")

print("\n" + "="*60)
print("Area chart generation complete!")
print("="*60)
