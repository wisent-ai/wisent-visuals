"""Test all column chart themes and styles."""

from wisent_plots.charts import ColumnChart

# Sample data - 3 series
categories = ["Q1", "Q2", "Q3", "Q4", "Q5"]
series = [
    [800, 550, 1000, 350, 400],
    [500, 250, 750, 550, 500],
    [250, 350, 300, 600, 600]
]
labels = ["One", "Two", "Three"]

# All 5 style variations
# Style 1: Solid colors
# Style 2: Solid + noise + solid
# Style 3: Solid + crossing lines + solid
# Style 4: Solid + noise + dither crosses
# Style 5: Multi-color (green, red, purple)
styles = [
    (1, "style1", "Solid colors"),
    (2, "style2", "Solid + noise + solid"),
    (3, "style3", "Solid + crossing lines + solid"),
    (4, "style4", "Solid + noise + dither crosses"),
    (5, "style5", "Multi-color"),
]

themes = [
    ("black", "Black Theme"),
    ("brand", "Brand Colors"),
    ("white", "White Theme"),
]

for theme_name, theme_desc in themes:
    print(f"\n{'='*60}")
    print(f"{theme_desc}")
    print('='*60)

    for style_num, style_name, style_desc in styles:
        print(f"\nCreating {style_desc} column chart...")

        try:
            # Create column chart
            chart = ColumnChart(style=style_num, theme=theme_name)
            svg_string = chart.plot(
                categories=categories,
                series=series,
                labels=labels,
                title="Group Column Chart"
            )

            # Save to file
            filename = f'examples/column/{theme_name}/column_chart_{theme_name}_{style_name}.svg'
            with open(filename, 'w') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write(svg_string)
            print(f"✓ Created: {filename}")
        except Exception as e:
            print(f"✗ Error creating {style_name}: {e}")

print("\n" + "="*60)
print("Column chart generation complete!")
print("="*60)
