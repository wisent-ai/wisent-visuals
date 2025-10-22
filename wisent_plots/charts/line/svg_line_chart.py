"""SVG-based line chart for pixel-perfect Figma matching."""

from typing import List
import xml.etree.ElementTree as ET

from wisent_plots.charts.area.area_chart_components import render_title_and_legend


class SVGLineChart:
    """Generate pixel-perfect SVG line charts matching Figma design."""

    def __init__(self, width: int = 1002, height: int = 580):
        """Initialize SVG line chart with exact Figma dimensions.

        Args:
            width: Chart width in pixels (default from Figma: 1002)
            height: Chart height in pixels (default from Figma: 580)
        """
        self.width = width
        self.height = height

        # Exact Figma colors
        self.colors = {
            'background': '#121212',
            'title': '#C5FFC8',
            'legend_text': '#769978',
            'grid_vertical': '#2D3130',  # Vertical grid lines
            'grid_horizontal': '#4A4A4A',  # Horizontal grid lines (slightly lighter)
            'primary': '#C5FFC8',  # Green (One)
            'secondary': '#FA5A46',  # Red (Two)
            'accent': '#B19ECC',  # Purple (Three)
            'line1': '#C5FFC8',  # Alias for primary
            'line2': '#FA5A46',  # Alias for secondary
            'line3': '#B19ECC',  # Alias for accent
        }

        # Exact Figma spacing from design
        self.padding_x = 32
        self.padding_y = 16
        self.title_gap = 10
        self.legend_gap = 4
        self.chart_top_margin = 24

        # Chart area dimensions (from Figma)
        self.chart_width = 938
        self.chart_height = 466

    def create_chart(
        self,
        x_data: List[float],
        y_series: List[List[float]],
        labels: List[str],
        title: str = "Line Chart",
        line_width: float = 2.0,
        show_markers: bool = False,
        marker_shapes: List[str] = None
    ) -> str:
        """Create SVG line chart matching Figma design exactly.

        Args:
            x_data: X-axis data points
            y_series: List of Y-axis data series
            labels: Labels for each series
            title: Chart title
            line_width: Width of lines
            show_markers: Whether to show markers at data points
            marker_shapes: List of marker shapes ('circle', 'square', 'diamond', 'triangle')

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
        # Use background color from colors dict
        bg_color = self.colors.get('background', '#121212')
        bg = ET.SubElement(svg, 'rect', {
            'width': str(self.width),
            'height': str(self.height),
            'fill': bg_color,
            'rx': '20',
            'ry': '20'
        })

        # Render title and legend
        chart_start_y = render_title_and_legend(
            svg, title, labels, self.colors,
            self.padding_x, self.padding_y, self.title_gap, self.chart_top_margin
        )
        chart_x = self.padding_x

        # Render grid and lines
        self._render_grid(svg, chart_x, chart_start_y)
        self._render_lines(
            svg, x_data, y_series, chart_x, chart_start_y,
            line_width, show_markers, marker_shapes
        )

        # Convert to string
        return ET.tostring(svg, encoding='unicode', method='xml')

    def _render_grid(self, svg, chart_x: int, chart_y: int):
        """Render grid lines and axis labels."""
        # Vertical grid lines (every ~117px based on Figma)
        grid_spacing = 117
        num_lines = 9

        for i in range(num_lines):
            x = chart_x + (i * grid_spacing)
            if x <= chart_x + self.chart_width:
                # Vertical dashed line
                ET.SubElement(svg, 'line', {
                    'x1': str(x),
                    'y1': str(chart_y),
                    'x2': str(x),
                    'y2': str(chart_y + 430),
                    'stroke': self.colors['grid_vertical'],
                    'stroke-width': '1',
                    'stroke-dasharray': '4,4'
                })

                # X-axis label below chart
                if i < num_lines:
                    label_text = f"{i+1:02d}"
                    label_elem = ET.SubElement(svg, 'text', {
                        'x': str(x),
                        'y': str(chart_y + 453),
                        'fill': self.colors['legend_text'],
                        'font-size': '14',
                        'font-weight': '400',
                        'text-anchor': 'start'
                    })
                    label_elem.text = label_text

        # Horizontal grid lines (every ~110px based on Figma)
        horizontal_spacing = 110
        num_horizontal = 4

        for i in range(num_horizontal + 1):
            y = chart_y + (i * horizontal_spacing)
            if y <= chart_y + 440:
                # Horizontal line
                ET.SubElement(svg, 'line', {
                    'x1': str(chart_x),
                    'y1': str(y),
                    'x2': str(chart_x + self.chart_width),
                    'y2': str(y),
                    'stroke': self.colors['grid_horizontal'],
                    'stroke-width': '1'
                })

    def _render_lines(
        self,
        svg,
        x_data: List[float],
        y_series: List[List[float]],
        chart_x: int,
        chart_y: int,
        line_width: float,
        show_markers: bool,
        marker_shapes: List[str]
    ):
        """Render line series with optional markers."""
        import numpy as np

        # Calculate chart dimensions
        chart_width = self.chart_width
        chart_height = 430  # Actual chart area height

        # Find min and max values across all series
        all_values = []
        for series in y_series:
            all_values.extend(series)
        min_val = min(all_values)
        max_val = max(all_values)
        value_range = max_val - min_val if max_val != min_val else 1

        # Line colors - build from available color keys
        line_colors = [
            self.colors.get('primary', '#C5FFC8'),
            self.colors.get('secondary', '#FA5A46'),
            self.colors.get('accent', '#B19ECC'),
        ]
        # Add more colors if available
        if 'quaternary' in self.colors:
            line_colors.append(self.colors['quaternary'])
        if 'quinary' in self.colors:
            line_colors.append(self.colors['quinary'])

        # Default marker shapes
        if marker_shapes is None:
            marker_shapes = ['circle', 'square', 'diamond']

        # Render each line series
        for series_idx, series_data in enumerate(y_series):
            color = line_colors[series_idx % len(line_colors)]
            marker_shape = marker_shapes[series_idx % len(marker_shapes)]

            # Build path data
            path_d = ""
            points = []

            for i, (x_val, y_val) in enumerate(zip(x_data, series_data)):
                # Calculate position
                x_pos = chart_x + (i * (chart_width / (len(x_data) - 1)))
                # Invert Y axis (higher values at top)
                y_pos = chart_y + chart_height - ((y_val - min_val) / value_range * chart_height)

                points.append((x_pos, y_pos))

                if i == 0:
                    path_d = f"M {x_pos},{y_pos}"
                else:
                    path_d += f" L {x_pos},{y_pos}"

            # Draw line path
            ET.SubElement(svg, 'path', {
                'd': path_d,
                'stroke': color,
                'stroke-width': str(line_width),
                'fill': 'none',
                'stroke-linecap': 'round',
                'stroke-linejoin': 'round'
            })

            # Draw markers if requested
            if show_markers:
                for x_pos, y_pos in points:
                    self._draw_marker(svg, x_pos, y_pos, marker_shape, color)

    def _draw_marker(self, svg, x: float, y: float, shape: str, color: str, size: float = 11):
        """Draw a marker at the specified position."""
        half_size = size / 2

        if shape == 'circle':
            ET.SubElement(svg, 'circle', {
                'cx': str(x),
                'cy': str(y),
                'r': str(half_size),
                'fill': color
            })
        elif shape == 'square':
            ET.SubElement(svg, 'rect', {
                'x': str(x - half_size),
                'y': str(y - half_size),
                'width': str(size),
                'height': str(size),
                'fill': color,
                'rx': '2',
                'ry': '2'
            })
        elif shape == 'diamond':
            # Rotate square by 45 degrees
            points = f"{x},{y - half_size} {x + half_size},{y} {x},{y + half_size} {x - half_size},{y}"
            ET.SubElement(svg, 'polygon', {
                'points': points,
                'fill': color
            })
        elif shape == 'triangle':
            # Equilateral triangle pointing up
            h = half_size * 1.732  # sqrt(3) for equilateral
            points = f"{x},{y - h * 0.67} {x + half_size},{y + h * 0.33} {x - half_size},{y + h * 0.33}"
            ET.SubElement(svg, 'polygon', {
                'points': points,
                'fill': color
            })

    def save_svg(self, svg_string: str, filename: str):
        """Save SVG to file."""
        with open(filename, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(svg_string)
