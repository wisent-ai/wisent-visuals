"""Test all bar chart themes and styles."""

from wisent_plots.charts import BarChart

# Sample data - 3 series for stacked bar chart
categories = ['Q1', 'Q2', 'Q3', 'Q4']
series = [
    [85, 92, 78, 95],
    [65, 70, 82, 75],
    [45, 58, 52, 60]
]
labels = ["One", "Two", "Three"]

# All 5 style variations
styles = [
    (1, "style1"),
    (2, "style2"),
    (3, "style3"),
    (4, "style4"),
    (5, "style5"),
]

themes = [
    ("black", "Black Theme"),
    ("brand", "Brand Colors"),
    ("white", "White Theme"),
]

for theme_folder, theme_name in themes:
    print(f"\n{'='*60}")
    print(f"{theme_name}")
    print('='*60)

    for style_num, style_name in styles:
        print(f"\nCreating bar chart style {style_num}...")

        try:
            # Create bar chart
            chart = BarChart(style=style_num)
            svg_string = chart.plot(
                categories=categories,
                series=series,
                labels=labels,
                title="Bar Chart",
                output_format='svg'
            )

            # Save to file
            filename = f'examples/bar/{theme_folder}/bar_chart_{theme_folder}_{style_name}.svg'
            with open(filename, 'w') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write(svg_string)
            print(f"✓ Created: {filename}")
        except Exception as e:
            print(f"✗ Error creating {style_name}: {e}")

print("\n" + "="*60)
print("Bar chart generation complete!")
print("="*60)
