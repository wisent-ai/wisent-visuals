"""SVG-based area chart for pixel-perfect Figma matching."""

from typing import List
import xml.etree.ElementTree as ET

from .area_chart_components import render_title_and_legend
from .area_chart_renderer import render_area_chart


class SVGAreaChart:
    """Generate pixel-perfect SVG area charts matching Figma design."""

    def __init__(self, width: int = 1002, height: int = 499):
        """Initialize SVG chart with exact Figma dimensions.

        Args:
            width: Chart width in pixels (default from Figma: 1002)
            height: Chart height in pixels (default from Figma: 499)
        """
        self.width = width
        self.height = height

        # Exact Figma colors
        self.colors = {
            'background': '#121212',
            'title': '#C5FFC8',
            'legend_text': '#769978',
            'grid': '#2D3130',  # Grey grid lines
            'area': '#C5FFC8',  # All areas use same color with different opacity
            'primary': '#B0E3B3',  # Legend colors
            'secondary': '#90B892',
            'accent': '#5A715B',
        }

        # Exact Figma spacing from design
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
        title: str = "Area Chart"
    ) -> str:
        """Create SVG chart matching Figma design exactly.

        Args:
            x_data: X-axis data points
            y_series: List of Y-axis data series (will be stacked)
            labels: Labels for each series
            title: Chart title

        Returns:
            SVG string
        """
        # Create SVG root with exact Figma dimensions
        svg = ET.Element('svg', {
            'width': str(self.width),
            'height': str(self.height),
            'xmlns': 'http://www.w3.org/2000/svg',
            'viewBox': f'0 0 {self.width} {self.height}'
        })

        # Add Hubot Sans font definition
        style = ET.SubElement(svg, 'style')
        style.text = """
            @import url('https://fonts.googleapis.com/css2?family=Hubot+Sans:wght@400&display=swap');
            text { font-family: 'Hubot Sans', sans-serif; }
        """

        # Background with rounded corners (20px radius from Figma)
        bg = ET.SubElement(svg, 'rect', {
            'width': str(self.width),
            'height': str(self.height),
            'fill': self.colors['background'],
            'rx': '20',
            'ry': '20'
        })

        # Render title, legend, axes
        chart_start_y = render_title_and_legend(
            svg, title, labels, self.colors,
            self.padding_x, self.padding_y, self.title_gap, self.chart_top_margin
        )
        chart_x = self.padding_x

        # Render main area chart
        render_area_chart(
            svg, x_data, y_series, chart_x, chart_start_y,
            self.chart_width, self.chart_height, self.colors
        )

        # Convert to string
        return ET.tostring(svg, encoding='unicode', method='xml')

    def _darken_color(self, hex_color: str, factor: float = 0.7) -> str:
        """Darken a hex color."""
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))
        darkened = tuple(int(c * factor) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"

    def save_svg(self, svg_string: str, filename: str):
        """Save SVG to file."""
        with open(filename, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(svg_string)

    def save_png(self, svg_string: str, filename: str, dpi: int = 150):
        """Convert SVG to PNG using cairosvg."""
        try:
            import cairosvg
            cairosvg.svg2png(
                bytestring=svg_string.encode('utf-8'),
                write_to=filename,
                dpi=dpi
            )
        except ImportError:
            print("⚠ cairosvg not installed. Install with: pip install cairosvg")
            print("  Saving as SVG instead...")
            self.save_svg(svg_string, filename.replace('.png', '.svg'))
