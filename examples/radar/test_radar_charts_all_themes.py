"""Test all radar chart themes (brand, black, white)."""

from wisent_plots.charts.radar_chart import RadarChart

# Sample data - 2 series with 8 axes each (octagon)
# Values are 0-100 representing distance from center
series1 = [85, 70, 90, 65, 80, 75, 70, 85]  # "One"
series2 = [60, 80, 55, 75, 65, 70, 85, 60]  # "Two"

data_series = [series1, series2]
labels = ["One", "Two"]

# Axis labels for 8-axis octagon (angles at 45° intervals)
axis_labels = ["0", "45", "90", "135", "180", "225", "270", "315"]

# Create all three theme variations
themes = [
    (1, "brand", "Brand Colors"),
    (2, "black", "Black/Grayscale"),
    (3, "white", "White Theme")
]

for style_num, style_name, theme_name in themes:
    print(f"\nCreating {theme_name} radar chart...")

    # Create radar chart
    chart = RadarChart(style=style_num)
    svg_string = chart.plot(
        data_series=data_series,
        labels=labels,
        axis_labels=axis_labels,
        title="Radar chart"
    )

    # Save to file
    filename = f'examples/radar/{style_name}/radar_chart_{style_name}.svg'
    chart.save_svg(svg_string, filename)
    print(f"✓ Created: {filename}")

print("\n" + "="*60)
print("All radar chart variations created successfully!")
print("="*60)
print("\nGenerated charts:")
print("  ✓ radar_chart_brand.svg - Brand colors (green and red)")
print("  ✓ radar_chart_black.svg - Black theme with grayscale")
print("  ✓ radar_chart_white.svg - White theme with grayscale")
