<!-- wisent-banner:start -->
<p align="center">
  <img src="assets/readme-banner.webp" alt="wisent-visuals by Wisent" width="100%">
</p>
<!-- wisent-banner:end -->

<!-- wisent-readme-signals:start -->
[![Source](https://img.shields.io/badge/GitHub-Source-181717?logo=github)](https://github.com/wisent-ai/wisent-visuals) [![Issues](https://img.shields.io/badge/GitHub-Issues-181717?logo=github)](https://github.com/wisent-ai/wisent-visuals/issues) [![Wisent](https://img.shields.io/badge/Wisent-Website-0B0B0B)](https://wisent.com) [![Discord](https://img.shields.io/badge/Discord-Join-5865F2?logo=discord&logoColor=white)](https://discord.gg/qRjpkthq54) [![LinkedIn](https://img.shields.io/badge/LinkedIn-Follow-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/company/wisent-ai/) [![X](https://img.shields.io/badge/X-Follow-000000?logo=x&logoColor=white)](https://x.com/wisentai) [![Enterprise](https://img.shields.io/badge/Enterprise-Book%20a%20call-0B0B0B?logo=calendly)](https://calendly.com/lbartoszcze)
<!-- wisent-readme-signals:end -->

# Wisent Visuals

Charts That Already Look Like Your Company.

Every deck ends the same way: someone re-colours a matplotlib default at midnight
so the chart does not look like a lab report. Wisent Visuals gives you the chart
types you actually use, already carrying the brand — colours, type, spacing and
the small decisions nobody wants to make twice. Call one function and get a
figure you can put in front of a customer. Your plots stop being the weakest
slide in the room.

Brand-Ready Plots, One Import Away.

## Features

- **5 Pre-configured Styles**: Choose from 5 professionally designed styles
- **Easy to Use**: Simple API that works with familiar data structures
- **Customizable**: Override colors and settings as needed
- **High Quality**: Publication-ready output with customizable DPI
- **Type Hints**: Full type annotation support
- **README banners**: Deterministic, brand-safe SVG, WebP, and PNG generation

## Installation

```bash
pip install wisent-plots
```

For development:

```bash
git clone https://github.com/wisent/wisent-plots
cd wisent-plots
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

## README Banners

Keep banner content in a small TOML file:

```toml
title = "Deep control. Safer output."
description = "A Python package for latent space monitoring and guardrails."
product = "Wisent"
url = "wisent.com"
theme = "dark"
layout = "latent-field-left"
width = 1584
height = 396
```

Generate the committed README image and its editable, self-contained SVG source:

```bash
wisent-banner \
  --config .github/banner.toml \
  --output assets/readme-banner.webp \
  --svg assets/readme-banner.svg
```

The renderer bundles Hubot Sans, validates dimensions and supported layouts, and
produces byte-identical output for the same configuration. Commit both the TOML
configuration and generated assets; CI can rerun this command and use
`git diff --exit-code` to detect stale output.

### Automatic organization-wide presentation

`wisent-banner-bot` never writes product copy from repository metadata. Approved
titles and optional descriptions live in
`wisent_plots/approved_copy.json`, with the conversation session and timestamp
that authorized each entry.

Repository descriptions, topics, languages, and README text select artwork only:

- routing graphs for gateways and model routers;
- measured bars for benchmarks and visualization;
- orbits for agent systems;
- waveforms for audio projects;
- stacked layers for storage and context;
- latent activation fields for models and safety;
- coordinated signals for SDKs, clients, and general developer tools.

A repository without approved copy receives only its display name and no
description. The generated TOML records `copy_status` and `approved_in`; changing
the approval register changes the source fingerprint and regenerates the assets.

Descriptions previously introduced by the removed copy table are listed in
`wisent_plots/unapproved_descriptions.json`. Clear only those audited values
with:

```bash
wisent-banner-bot clear-unapproved-descriptions --org wisent-ai
```

Preview decisions without changing GitHub:

```bash
wisent-banner-bot plan --org wisent-ai --limit 10
```

The 15-minute `banner-bot.yml` workflow uses an organization-installed GitHub App
to create pull requests. Configure these repository secrets:

- `WISENT_BANNER_APP_ID`;
- `WISENT_BANNER_APP_PRIVATE_KEY`.

The app needs repository metadata read access plus Contents and Pull requests
read/write access. The bot skips forks and archived repositories and never
replaces an existing manually managed banner. Bot-owned README markup is the
first rendered block and is bounded by `wisent-banner:start` /
`wisent-banner:end` comments, so later runs replace only their own block. A source
fingerprint prevents unchanged repositories from receiving another pull request.

## Available Styles

The package includes 5 distinct styles, each with unique color palettes and typography:

1. **Corporate** (style=1): Professional deep blue theme
2. **Minimal** (style=2): Clean, understated design
3. **Bold** (style=3): High-contrast, vibrant colors
4. **Academic** (style=4): Classic, publication-ready style
5. **Modern** (style=5): Contemporary gradient colors

### Customizing Styles with Figma

To match your exact Figma design specifications:

1. Open `wisent_plots/styles/style_config.py`
2. Update the color values, fonts, and spacing for each style
3. The comments marked with `# UPDATE with Figma` show where to add your brand colors

Example of what to update:

```python
"colors": {
    "primary": "#1E3A8A",  # UPDATE: Replace with your primary brand color
    "secondary": "#3B82F6",  # UPDATE: Replace with your secondary color
    # ... etc
},
"font": {
    "family": "Arial",  # UPDATE: Replace with your brand font
    # ...
}
```

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
    ylabel="Units Sold"
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

#### `plot_multiple(x, y_series, labels=None, colors=None, title=None, xlabel=None, ylabel=None, fig=None, ax=None)`

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

**Returns:** `(fig, ax)` tuple

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
cd examples
python quick_start.py
python area_chart_demo.py
```

### Running Tests

```bash
pytest tests/
```

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
pip install --index-url https://test.pypi.org/simple/ wisent-plots
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
