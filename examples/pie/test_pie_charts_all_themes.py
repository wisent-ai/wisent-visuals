"""Test all pie chart themes (brand, black, white)."""

from wisent_plots.charts.pie_chart import PieChart

# Sample data - 6 categories
values = [25, 20, 15, 15, 13, 12]
labels = ["One", "Two", "Three", "Four", "Five", "Six"]

# Create all three theme variations
themes = [
    (1, "brand", "Brand Colors"),
    (2, "black", "Black/Grayscale"),
    (3, "white", "White Theme")
]

for style_num, style_name, theme_name in themes:
    print(f"\nCreating {theme_name} pie chart...")

    # Create pie chart
    chart = PieChart(style=style_num)
    svg_string = chart.plot(
        values=values,
        labels=labels,
        title="Pie chart",
        center_label="Total",
        center_value="99999"
    )

    # Save to file
    filename = f'examples/pie/{style_name}/pie_chart_{style_name}.svg'
    chart.save_svg(svg_string, filename)
    print(f"✓ Created: {filename}")

print("\n" + "="*60)
print("All pie chart variations created successfully!")
print("="*60)
print("\nGenerated charts:")
print("  ✓ pie_chart_brand.svg - Brand colors (green, red, orange, etc.)")
print("  ✓ pie_chart_black.svg - Black theme with grayscale")
print("  ✓ pie_chart_white.svg - White theme with grayscale")
