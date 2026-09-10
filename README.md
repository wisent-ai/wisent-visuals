# Wisent Plots

Create beautiful, brand-styled plots with ease. This package provides ready-to-use chart types that follow Wisent's visual identity guidelines.

## Features

- **5 Pre-configured Styles**: Choose from 5 professionally designed styles
- **Easy to Use**: Simple API that works with familiar data structures
- **Customizable**: Override colors and settings as needed
- **High Quality**: Publication-ready output with customizable DPI
- **Type Hints**: Full type annotation support

## Installation

```bash
pip install wisent-visuals
```

For development:

```bash
git clone https://github.com/wisent-ai/wisent-visuals
cd wisent-visuals
pip install -e ".[dev]"
```

## Quick Start

```python
from wisent_plots import AreaChart

# Create data
x = [1, 2, 3, 4, 5]
y = [2, 4, 3, 5, 4]

# Create chart with style 1 and edge enabled
chart = AreaChart(style=1, edge=True)

# Plot
fig, ax = chart.plot(
    x=x,
    y=y,
    title="My Chart",
    xlabel="Time",
    ylabel="Value"
)

# Save or show
chart.save(fig, "my_chart.png")
# Or: plt.show()
```

## Available Styles

Area charts provide five SVG styles: solid green bands (1), gradients (2),
patterns (3), two-pattern fills (4), and a solid multicolor palette (5).
Use `edge=True` for SVG area styles 1–4; style 5 also renders SVG without an edge.
`plot_multiple(..., output_format="matplotlib")` selects Matplotlib explicitly.

### Customizing Styles with Figma

To match your exact Figma design specifications:

1. Open the chart family's module under `wisent_plots/styles/families/`.
2. Update that family's colors, fonts, and spacing.
3. Keep public style identifiers in `wisent_plots/styles/style_config.py`.

The public `STYLES` mapping and `get_style()` keep their existing imports,
identifiers, and mutable configuration objects. The registry covers area, line,
bubble, pie, and radar presets; SVG bar and column palettes remain with those renderers.

Matplotlib drawing lives beside its chart facade in `matplotlib_backend`;
SVG title, legend, marker and pattern helpers are shared under `charts/`.

## Usage Examples

### Single Series Area Chart

```python
import numpy as np
from wisent_plots import AreaChart

x = np.linspace(0, 10, 50)
y = np.sin(x) * 3 + 5

chart = AreaChart(style=1, edge=True)
fig, ax = chart.plot(
    x=x,
    y=y,
    title="Sales Growth",
    xlabel="Month",
    ylabel="Revenue ($1000s)",
    label="Q1 Sales"
)
chart.save(fig, "sales_chart.png", dpi=300)
```

### Multiple Series

```python
chart = AreaChart(style=2, edge=False)

y1 = np.sin(x) * 3 + 5
y2 = np.cos(x) * 2 + 5
y3 = np.sin(x * 0.5) * 2 + 3

fig, ax = chart.plot_multiple(
    x=x,
    y_series=[y1, y2, y3],
    labels=["Product A", "Product B", "Product C"],
    title="Product Comparison",
    xlabel="Time (weeks)",
    ylabel="Units Sold",
    output_format="matplotlib",
)
chart.save(fig, "comparison.png")
```

### Custom Colors

```python
chart = AreaChart(style=1, edge=True)
fig, ax = chart.plot(
    x=x,
    y=y,
    title="Custom Colored Chart",
    color="#FF6B6B",  # Custom coral color
    label="Custom Series"
)
```

### Using with Existing Matplotlib Figures

```python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

chart1 = AreaChart(style=1)
chart1.plot(x, y1, title="Chart 1", fig=fig, ax=axes[0, 0])

chart2 = AreaChart(style=2)
chart2.plot(x, y2, title="Chart 2", fig=fig, ax=axes[0, 1])

plt.tight_layout()
plt.savefig("grid.png")
```

## API Reference

### AreaChart

**Constructor Parameters:**

- `style` (int, default=1): Style number (1-5)
- `edge` (bool, default=False): Whether to draw edge around filled area
- `figsize` (tuple, default=(10, 6)): Figure size as (width, height) in inches
- `dpi` (int, default=100): Resolution in dots per inch

**Methods:**

#### `plot(x, y, title=None, xlabel=None, ylabel=None, color=None, label=None, fig=None, ax=None)`

Create a single-series area chart.

**Parameters:**
- `x`: X-axis data (list or numpy array)
- `y`: Y-axis data (list or numpy array)
- `title`: Chart title (optional)
- `xlabel`: X-axis label (optional)
- `ylabel`: Y-axis label (optional)
- `color`: Custom color as hex string (optional)
- `label`: Legend label (optional)
- `fig`: Existing matplotlib Figure (optional)
- `ax`: Existing matplotlib Axes (optional)

**Returns:** `(fig, ax)` tuple

#### `plot_multiple(x, y_series, labels=None, colors=None, title=None, xlabel=None, ylabel=None, fig=None, ax=None, output_format="svg")`

Create a multi-series area chart.

**Parameters:**
- `x`: X-axis data (list or numpy array)
- `y_series`: List of Y-axis data arrays
- `labels`: List of legend labels (optional)
- `colors`: List of colors for each series (optional)
- `title`: Chart title (optional)
- `xlabel`: X-axis label (optional)
- `ylabel`: Y-axis label (optional)
- `fig`: Existing matplotlib Figure (optional)
- `ax`: Existing matplotlib Axes (optional)

**Returns:** an SVG string for styles 1–4 with `edge=True` and for style 5 when
`output_format="svg"`; otherwise `(fig, ax)`. Use `output_format="matplotlib"`
when supplying existing Matplotlib axes.

#### `save(fig, filename, dpi=None, transparent=False)`

Save the figure to a file.

**Parameters:**
- `fig`: Figure object to save
- `filename`: Output filename with extension (e.g., 'chart.png')
- `dpi`: Resolution in dots per inch (optional, uses figure dpi if not specified)
- `transparent`: Whether to save with transparent background (default=False)

## Development

### Running Examples

```bash
python examples/area/test_area_charts_all_themes.py
python examples/bubble/test_bubble_charts_all_themes.py
```

### Running Tests

```bash
python -m unittest discover -s tests/charts -p rendering.py -v
```

These tests render through the real SVG and Matplotlib backends without opening
a window. They check stacked geometry, missing-observation gaps, SVG paint and
clipping references, and unsupported output refusal. Set
`WISENT_VISUALS_ARTIFACT_DIR` to retain SVG, PNG and style-configuration evidence.

### Code Formatting

```bash
black wisent_plots/
isort wisent_plots/
```

## Building and Publishing

### Build the package

```bash
pip install build twine
python -m build
```

This creates distribution files in the `dist/` directory.

### Test with TestPyPI (recommended first)

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Install from TestPyPI to test
pip install --index-url https://test.pypi.org/simple/ wisent-visuals
```

### Publish to PyPI

```bash
python -m twine upload dist/*
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on the GitHub repository.
