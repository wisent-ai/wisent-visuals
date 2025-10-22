"""Pie Chart implementation with matplotlib fallback and SVG output."""

from typing import List, Optional
import os

from wisent_plots.styles.style_config import get_style
from wisent_plots.charts.pie.svg_pie_chart import SVGPieChart


class PieChart:
    """Pie/Donut chart with style support."""

    def __init__(self, style: int = 1, width: int = 328, height: int = 328):
        """Initialize Pie Chart.

        Args:
            style: Style number (1=brand colors, 2=black/grayscale, 3=white)
            width: Chart width in pixels
            height: Chart height in pixels
        """
        self.style_number = style
        self.width = width
        self.height = height

        # Map pie chart styles: 1->40, 2->41, 3->42
        actual_style = 39 + self.style_number
        self.style_config = get_style(actual_style)

    def plot(
        self,
        values: List[float],
        labels: List[str],
        title: str = "Pie chart",
        center_label: str = "Total",
        center_value: Optional[str] = None,
        output_format: str = 'svg'
    ) -> str:
        """Create pie chart.

        Args:
            values: List of values for each slice
            labels: List of labels for legend
            title: Chart title
            center_label: Label in center of donut (e.g., "Total")
            center_value: Value in center of donut (e.g., "99999"), if None will calculate sum
            output_format: Output format ('svg' or 'matplotlib')

        Returns:
            SVG string if output_format='svg'
        """
        if output_format == 'svg':
            return self._create_svg(values, labels, title, center_label, center_value)
        else:
            raise NotImplementedError("Matplotlib output not yet implemented for pie charts")

    def _create_svg(
        self,
        values: List[float],
        labels: List[str],
        title: str,
        center_label: str,
        center_value: Optional[str]
    ) -> str:
        """Create SVG pie chart."""
        # Create SVG chart
        svg_chart = SVGPieChart(width=self.width, height=self.height)

        # Update colors from style config
        colors = self.style_config['colors']
        svg_chart.colors['background'] = colors['background']
        svg_chart.colors['title'] = colors['title']
        svg_chart.colors['legend_text'] = colors['legend_text']
        svg_chart.colors['center_text'] = colors['center_text']
        svg_chart.colors['separator'] = colors['separator']

        # Update slice colors
        for i in range(1, 7):
            slice_key = f'slice{i}'
            if slice_key in colors:
                svg_chart.colors[slice_key] = colors[slice_key]

        # Update pie configuration
        if 'pie' in self.style_config:
            pie_config = self.style_config['pie']
            svg_chart.inner_radius_ratio = pie_config.get('inner_radius', 0.55)
            svg_chart.separator_width = pie_config.get('separator_width', 2)

        # Calculate center value if not provided
        if center_value is None:
            total = sum(values)
            center_value = str(int(total))

        # Generate SVG
        return svg_chart.create_svg(
            values=values,
            labels=labels,
            title=title,
            center_label=center_label,
            center_value=center_value
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
