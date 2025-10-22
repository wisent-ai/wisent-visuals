"""Test all bubble chart themes and styles."""

from wisent_plots.charts import BubbleChart
import numpy as np

# Sample data for regular bubble chart
np.random.seed(42)
x_data = [10, 20, 30, 40, 50, 60, 70, 80]
y_data = [100, 200, 150, 300, 250, 350, 400, 320]
sizes = [15, 25, 20, 30, 22, 28, 35, 26]
categories = [0, 1, 2, 0, 1, 2, 0, 1]
category_labels = ["Category A", "Category B", "Category C"]

# Sample data for radar bubble chart
angles = [0, 45, 90, 135, 180, 225, 270, 315]
distances = [70, 85, 60, 95, 75, 80, 90, 65]
radar_sizes = [20, 25, 18, 30, 22, 24, 28, 19]

# All 3 themes
themes = [
    (1, "brand", "Brand Colors"),
    (2, "black", "Black/Grayscale Theme"),
    (3, "white", "White/Light Theme"),
]

chart_types = [
    ("bubble", "Regular Bubble Chart"),
    ("radar", "Radar Bubble Chart"),
]

for style_num, theme_folder, theme_name in themes:
    print(f"\n{'='*60}")
    print(f"{theme_name}")
    print('='*60)

    for chart_type, chart_desc in chart_types:
        print(f"\nCreating {chart_desc}...")

        try:
            # Create bubble chart
            chart = BubbleChart(style=style_num, chart_type=chart_type)

            if chart_type == 'bubble':
                svg_string = chart.plot(
                    x_data=x_data,
                    y_data=y_data,
                    sizes=sizes,
                    categories=categories,
                    category_labels=category_labels,
                    title="Bubble chart"
                )
                filename = f'examples/bubble/{theme_folder}/bubble_chart_{theme_folder}.svg'
            else:  # radar
                svg_string = chart.plot(
                    angles=angles,
                    distances=distances,
                    sizes=radar_sizes,
                    categories=categories,
                    category_labels=category_labels,
                    title="Bubble chart"
                )
                filename = f'examples/bubble/{theme_folder}/radar_bubble_chart_{theme_folder}.svg'

            # Save to file
            chart.save_svg(svg_string, filename)
            print(f"✓ Created: {filename}")
        except Exception as e:
            print(f"✗ Error creating {chart_desc}: {e}")

print("\n" + "="*60)
print("Bubble chart generation complete!")
print("="*60)
