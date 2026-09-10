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

Synchronize every repository description with the same approved registry:

```bash
wisent-banner-bot sync-approved-descriptions --org wisent-ai
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

Use the same data for single-series, multiple-series, and custom-color charts:

```python
import numpy as np
from wisent_plots import AreaChart

x = np.linspace(0, 10, 50)
ys = [np.sin(x) * 3 + 5, np.cos(x) * 2 + 5, np.sin(x * 0.5) * 2 + 3]
chart = AreaChart(style=2, edge=False)
fig, ax = chart.plot(x, ys[0], color="#FF6B6B", label="Q1 Sales")
chart.save(fig, "sales_chart.png", dpi=300)
fig, ax = chart.plot_multiple(
    x, ys, labels=["Product A", "Product B", "Product C"], title="Product Comparison",
    xlabel="Time (weeks)", ylabel="Units Sold", output_format="matplotlib",
)
chart.save(fig, "comparison.png")
```

Existing figures and axes can be reused without replacing their contents:

```python
import matplotlib.pyplot as plt
fig, axes = plt.subplots(2, 2, figsize=(12, 10))
chart.plot(x, ys[0], title="Chart 1", fig=fig, ax=axes[0, 0])
chart.plot(x, ys[1], title="Chart 2", fig=fig, ax=axes[0, 1])
fig.tight_layout()
fig.savefig("grid.png")
```

## API Reference

`AreaChart(style=1, edge=False, stacked=True, figsize=(10, 6), dpi=100)` selects
area style 1–5, optional edges, stacked or overlapping areas, figure dimensions
in inches, and dots per inch.

`x` and `y` accept lists or NumPy arrays; `y_series` is a list of those arrays.
`title`, `xlabel`, and `ylabel` set text. `color`/`colors` override the palette;
`label`/`labels` set legend text. `fig` and `ax` reuse a caller's Matplotlib
figure and axes. These optional arguments default to `None`.

### `plot(x, y, title=None, xlabel=None, ylabel=None, color=None, label=None, fig=None, ax=None)`

Returns `(fig, ax)` for a single-series area chart.

### `plot_multiple(x, y_series, labels=None, colors=None, title=None, xlabel=None, ylabel=None, fig=None, ax=None, output_format="svg")`

Returns an SVG string for styles 1–4 with `edge=True` and for style 5 when
`output_format="svg"`; otherwise `(fig, ax)`. Use `output_format="matplotlib"`
when supplying existing Matplotlib axes.

### `save(fig, filename, dpi=None, transparent=False)`

The filename selects the image format. `dpi=None` uses the figure's resolution;
`transparent=True` saves a transparent background.

## Development

`banner_rendering/` owns artwork selection, seeded geometry, typography, and
the render CLI. `banner_automation/` owns GitHub requests, publication plans,
README updates, and bot command dispatch; public `Banner` and bot APIs remain intact.

### Running Examples

```bash
python examples/area/test_area_charts_all_themes.py
python examples/bubble/test_bubble_charts_all_themes.py
```

### Running Real Tests

```bash
python -m pytest tests --basetemp build/test-artifacts
```

Tests use real SVG, Matplotlib, Pillow, and CLI rendering without opening a
window. `WISENT_VISUALS_ARTIFACT_DIR` retains chart SVG, PNG, and style snapshots;
the pytest artifact directory retains banner images and command reports.

The live GitHub test requires `WISENT_BANNER_GITHUB_TOKEN` and
`WISENT_BANNER_TEST_REPOSITORY` set to an isolated `owner/repository`.
That initialized fixture must have the description
`Wisent Visuals publication test fixture`, only its default branch, and no open PR.
Use it exclusively for the test: the test creates and closes its PR, deletes its
branch, and restores the original fixture files. Missing prerequisites are
reported as skipped, never as a successful publication.

### Code Formatting

```bash
black wisent_plots/
isort wisent_plots/
```

## Building and Publishing

```bash
pip install build twine
python -m build
```

Distributions are written to `dist/`. TestPyPI can be used before publishing:

```bash
python -m twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ wisent-visuals
python -m twine upload dist/*  # Publish to PyPI
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on the GitHub repository.
