"""SVG area chart with 2 pattern fills matching Figma design."""

import xml.etree.ElementTree as ET
from typing import List

from wisent_plots.charts.area.svg.renderer import _generate_stacked_paths
from wisent_plots.charts.svg_assets import _asset_path, _load_pattern_from_file
from wisent_plots.charts.svg_components import render_title_and_legend


class SVGAreaChart2Patterns:
    """Create pixel-perfect SVG area charts with 2 pattern fills."""

    def __init__(self, width: int = 1002, height: int = 499):
        """Initialize SVG chart with Figma dimensions.

        Args:
            width: Chart width in pixels (default from Figma: 1002)
            height: Chart height in pixels (default from Figma: 499)
        """
        self.width = width
        self.height = height

        # Exact Figma colors
        self.colors = {
            "background": "#121212",
            "title": "#C5FFC8",
            "legend_text": "#769978",
            "grid": "#2D3130",
            "area": "#C5FFC8",
            "primary": "#B0E3B3",
            "secondary": "#90B892",
            "accent": "#5A715B",
        }

        # Exact Figma spacing
        self.padding_x = 32
        self.padding_y = 16
        self.title_gap = 10
        self.legend_gap = 4
        self.chart_top_margin = 24

        # Chart area dimensions (from Figma)
        self.chart_width = 938
        self.chart_height = 385

    def create_chart(
        self,
        x_data: List[float],
        y_series: List[List[float]],
        labels: List[str],
        title: str = "Area Chart",
    ) -> str:
        """Create SVG area chart with 2 pattern fills.

        Args:
            x_data: X-axis data points
            y_series: List of Y-axis data series
            labels: Legend labels
            title: Chart title

        Returns:
            SVG string
        """
        # Create root SVG element
        svg = ET.Element(
            "svg",
            {
                "width": str(self.width),
                "height": str(self.height),
                "xmlns": "http://www.w3.org/2000/svg",
                "viewBox": f"0 0 {self.width} {self.height}",
            },
        )

        # Add Google Fonts
        style = ET.SubElement(svg, "style")
        style.text = """
            @import url('https://fonts.googleapis.com/css2?family=Hubot+Sans:wght@400&display=swap');
            text { font-family: 'Hubot Sans', sans-serif; }
        """

        # Background rectangle
        ET.SubElement(
            svg,
            "rect",
            {
                "width": str(self.width),
                "height": str(self.height),
                "fill": self.colors["background"],
                "rx": "20",
                "ry": "20",
            },
        )

        # Define patterns FIRST (before rendering legend)
        self._create_patterns(svg)

        # Render title and legend with patterns
        chart_start_y = render_title_and_legend(
            svg,
            title,
            labels,
            self.colors,
            self.padding_x,
            self.padding_y,
            self.title_gap,
            self.chart_top_margin,
            fills=["url(#pattern-bottom)", "url(#pattern-middle)", "url(#pattern-top)"],
            extra_fill=self.colors["primary"],
        )

        # Chart area coordinates
        chart_x = self.padding_x
        chart_height = self.height - self.padding_y - chart_start_y

        # Render area chart with patterns
        self._render_pattern_areas(
            svg, x_data, y_series, chart_x, chart_start_y, self.chart_width, chart_height
        )

        # Convert to string
        return ET.tostring(svg, encoding="unicode", method="xml")

    def _create_patterns(self, svg):
        """Embed the three shipped pattern assets in their original order."""
        defs = svg.find("defs")
        if defs is None:
            defs = ET.SubElement(svg, "defs")
        _load_pattern_from_file(defs, "pattern-bottom", _asset_path("pattern_vertical_lines.svg"))
        _load_pattern_from_file(defs, "pattern-middle", _asset_path("pattern_diagonal_lines.svg"))
        _load_pattern_from_file(defs, "pattern-top", _asset_path("large", "dither_cross_large.svg"))

    def _render_pattern_areas(
        self,
        svg,
        x_data: List[float],
        y_series: List[List[float]],
        chart_x: int,
        chart_start_y: int,
        chart_width: int,
        chart_height: int,
    ):
        """Render 2 pattern-filled area chart."""
        # Create clipping path
        clip_id = "chart-clip-2patterns"
        defs = svg.find("defs")
        if defs is None:
            defs = ET.SubElement(svg, "defs")

        clipPath = ET.SubElement(defs, "clipPath", {"id": clip_id})
        ET.SubElement(
            clipPath,
            "rect",
            {
                "x": str(chart_x),
                "y": str(chart_start_y),
                "width": str(chart_width),
                "height": str(chart_height - 40),
            },
        )

        # Generate stacked paths
        paths = _generate_stacked_paths(
            x_data, y_series, chart_x, chart_start_y, chart_width, chart_height - 40
        )

        # Draw grid lines FIRST so area bands appear in front
        grid_spacing = 67
        for i in range(15):
            x = chart_x + (i * grid_spacing)
            if x <= chart_x + chart_width:
                # Dashed vertical line
                ET.SubElement(
                    svg,
                    "line",
                    {
                        "x1": str(x),
                        "y1": str(chart_start_y),
                        "x2": str(x),
                        "y2": str(chart_start_y + chart_height - 40),
                        "stroke": self.colors["grid"],
                        "stroke-width": "1",
                        "stroke-dasharray": "4,4",
                    },
                )

                # X-axis label
                if i < 14:
                    label_text = f"{i+1:02d}"
                    label_elem = ET.SubElement(
                        svg,
                        "text",
                        {
                            "x": str(x + 10),
                            "y": str(chart_start_y + chart_height - 10),
                            "fill": self.colors["legend_text"],
                            "font-size": "14",
                            "font-weight": "400",
                            "text-anchor": "middle",
                        },
                    )
                    label_elem.text = label_text

        # Draw bands matching screenshot exactly
        # Bottom band (largest) - light green with VERTICAL LINES
        ET.SubElement(
            svg,
            "path",
            {
                "d": paths[0][0],
                "fill": "url(#pattern-bottom)",
                "fill-rule": "evenodd",
                "clip-path": f"url(#{clip_id})",
            },
        )

        # Middle band - dark green with DIAGONAL LINES (one direction)
        ET.SubElement(
            svg,
            "path",
            {
                "d": paths[1][0],
                "fill": "url(#pattern-middle)",
                "fill-rule": "evenodd",
                "clip-path": f"url(#{clip_id})",
            },
        )

        # Top band (smallest) - darkest green with CROSSHATCH GRID
        ET.SubElement(
            svg,
            "path",
            {
                "d": paths[2][0],
                "fill": "url(#pattern-top)",
                "fill-rule": "evenodd",
                "clip-path": f"url(#{clip_id})",
            },
        )

    def save_svg(self, svg_string: str, filename: str) -> None:
        """Save SVG string to file."""
        with open(filename, "w") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(svg_string)
