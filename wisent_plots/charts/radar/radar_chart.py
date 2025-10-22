"""Radar Chart implementation with matplotlib fallback and SVG output."""

from typing import List, Optional
import os

from wisent_plots.styles.style_config import get_style
from .svg_radar_chart import SVGRadarChart


class RadarChart:
    """Radar chart with style support."""

    def __init__(self, style: int = 1, width: int = 328, height: int = 328):
        """Initialize Radar Chart.

        Args:
            style: Style number (1=brand colors, 2=black/grayscale, 3=white)
            width: Chart width in pixels
            height: Chart height in pixels
        """
        self.style_number = style
        self.width = width
        self.height = height

        # Map radar chart styles: 1->50, 2->51, 3->52
        actual_style = 49 + self.style_number
        self.style_config = get_style(actual_style)

    def plot(
        self,
        data_series: List[List[float]],
        labels: List[str],
        axis_labels: Optional[List[str]] = None,
        title: str = "Radar chart",
        output_format: str = 'svg'
    ) -> str:
        """Create radar chart.

        Args:
            data_series: List of data series, each containing values for each axis (0-100)
            labels: Labels for legend (e.g., ["One", "Two"])
            axis_labels: Labels for each axis (e.g., ["0", "45", "90", ...])
                        If None, will generate default labels based on angles
            title: Chart title
            output_format: Output format ('svg' or 'matplotlib')

        Returns:
            SVG string if output_format='svg'
        """
        if output_format == 'svg':
            return self._create_svg(data_series, labels, axis_labels, title)
        else:
            raise NotImplementedError("Matplotlib output not yet implemented for radar charts")

    def _create_svg(
        self,
        data_series: List[List[float]],
        labels: List[str],
        axis_labels: Optional[List[str]],
        title: str
    ) -> str:
        """Create SVG radar chart."""
        # Create SVG chart
        svg_chart = SVGRadarChart(width=self.width, height=self.height)

        # Update colors from style config
        colors = self.style_config['colors']
        svg_chart.colors['background'] = colors['background']
        svg_chart.colors['title'] = colors['title']
        svg_chart.colors['legend_text'] = colors['legend_text']
        svg_chart.colors['axis_text'] = colors['axis_text']
        svg_chart.colors['grid'] = colors['grid']
        svg_chart.colors['axis'] = colors['axis']
        svg_chart.colors['area1'] = colors['area1']
        svg_chart.colors['area1_stroke'] = colors['area1_stroke']
        svg_chart.colors['area2'] = colors['area2']
        svg_chart.colors['area2_stroke'] = colors['area2_stroke']

        # Update radar configuration
        if 'radar' in self.style_config:
            radar_config = self.style_config['radar']
            svg_chart.num_axes = radar_config.get('num_axes', 8)
            svg_chart.num_rings = radar_config.get('num_rings', 5)
            svg_chart.fill_opacity = radar_config.get('fill_opacity', 0.6)

        # Generate default axis labels if not provided
        if axis_labels is None:
            axis_labels = [str(i * (360 // svg_chart.num_axes)) for i in range(svg_chart.num_axes)]

        # Generate SVG
        return svg_chart.create_svg(
            data_series=data_series,
            labels=labels,
            axis_labels=axis_labels,
            title=title
        )

    def save_svg(self, svg_string: str, filename: str):
        """Save SVG string to file.

        Args:
            svg_string: SVG content as string
            filename: Output filename
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)

        # Write SVG to file
        with open(filename, 'w', encoding='utf-8') as f:
            # Add XML declaration
            if not svg_string.startswith('<?xml'):
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(svg_string)

        print(f"Chart saved to {filename}")
