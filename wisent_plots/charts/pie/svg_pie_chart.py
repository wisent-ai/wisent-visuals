"""SVG Pie Chart renderer matching Figma design exactly."""

import math
import xml.etree.ElementTree as ET
from typing import List, Optional


class SVGPieChart:
    """Render pie/donut charts as SVG matching Figma specifications."""

    def __init__(self, width: int = 328, height: int = 328):
        """Initialize SVG Pie Chart renderer.

        Args:
            width: Chart width in pixels
            height: Chart height in pixels
        """
        self.width = width
        self.height = height
        self.padding = 16
        self.title_height = 36
        self.legend_height = 24

        # Default colors (can be updated from style config)
        self.colors = {
            'background': '#121212',
            'title': '#C5FFC8',
            'legend_text': '#769978',
            'center_text': '#FFFFFF',
            'separator': '#000000',
            'slice1': '#C5FFC8',
            'slice2': '#FA5A46',
            'slice3': '#FFB366',
            'slice4': '#FFD699',
            'slice5': '#B19ECC',
            'slice6': '#A4C2F4',
        }

        self.inner_radius_ratio = 0.55  # For donut chart
        self.separator_width = 2

    def create_svg(
        self,
        values: List[float],
        labels: List[str],
        title: str = "Pie chart",
        center_label: str = "Total",
        center_value: str = "99999"
    ) -> str:
        """Create SVG pie chart.

        Args:
            values: List of values for each slice
            labels: List of labels for legend
            title: Chart title
            center_label: Label in center of donut
            center_value: Value in center of donut

        Returns:
            SVG string
        """
        # Create SVG root
        svg = ET.Element('svg', {
            'width': str(self.width),
            'height': str(self.height),
            'xmlns': 'http://www.w3.org/2000/svg',
            'viewBox': f'0 0 {self.width} {self.height}'
        })

        # Add Hubot Sans font
        style = ET.SubElement(svg, 'style')
        style.text = """
            @import url('https://fonts.googleapis.com/css2?family=Hubot+Sans:wght@400&display=swap');
            text { font-family: 'Hubot Sans', sans-serif; }
        """

        # Background with rounded corners
        ET.SubElement(svg, 'rect', {
            'width': str(self.width),
            'height': str(self.height),
            'fill': self.colors['background'],
            'rx': '20',
            'ry': '20'
        })

        # Render title
        self._render_title(svg, title)

        # Render legend
        self._render_legend(svg, labels, values)

        # Calculate chart area
        chart_center_y = self.title_height + self.legend_height + (self.height - self.title_height - self.legend_height) // 2
        chart_center_x = self.width // 2

        # Render pie slices
        self._render_pie(svg, values, chart_center_x, chart_center_y)

        # Render center text
        self._render_center_text(svg, center_label, center_value, chart_center_x, chart_center_y)

        # Convert to string
        return ET.tostring(svg, encoding='unicode', method='xml')

    def _render_title(self, svg, title: str):
        """Render chart title."""
        title_elem = ET.SubElement(svg, 'text', {
            'x': str(self.padding),
            'y': str(self.padding + 16),
            'fill': self.colors['title'],
            'font-size': '16',
            'font-weight': '400'
        })
        title_elem.text = title

    def _render_legend(self, svg, labels: List[str], values: List[float]):
        """Render horizontal legend below title."""
        legend_y = self.padding + 20
        legend_x = self.padding

        # Only show legend for labels that have corresponding values
        num_items = min(len(labels), len(values))

        for i in range(num_items):
            label = labels[i]

            # Color box
            color_key = f'slice{i+1}'
            color = self.colors.get(color_key, self.colors['slice1'])

            ET.SubElement(svg, 'rect', {
                'x': str(legend_x),
                'y': str(legend_y),
                'width': '8',
                'height': '8',
                'fill': color,
                'rx': '1',
                'ry': '1'
            })

            # Label text
            text_elem = ET.SubElement(svg, 'text', {
                'x': str(legend_x + 12),
                'y': str(legend_y + 7),
                'fill': self.colors['legend_text'],
                'font-size': '10',
                'font-weight': '400'
            })
            text_elem.text = label

            # Move to next legend item
            legend_x += 8 + 4 + len(label) * 6 + 8

    def _render_pie(self, svg, values: List[float], cx: float, cy: float):
        """Render pie chart slices.

        Args:
            svg: SVG element to add slices to
            values: List of values for each slice
            cx: Center X coordinate
            cy: Center Y coordinate
        """
        # Calculate total and percentages
        total = sum(values)
        if total == 0:
            return

        # Calculate radius based on available space
        available_height = self.height - self.title_height - self.legend_height - self.padding * 2
        available_width = self.width - self.padding * 2
        max_diameter = min(available_height, available_width)
        outer_radius = max_diameter / 2
        inner_radius = outer_radius * self.inner_radius_ratio

        # Draw slices
        start_angle = -90  # Start at top (12 o'clock position)

        for i, value in enumerate(values):
            if value <= 0:
                continue

            # Calculate sweep angle
            sweep_angle = (value / total) * 360

            # Get color for this slice
            color_key = f'slice{i+1}'
            color = self.colors.get(color_key, self.colors['slice1'])

            # Draw slice
            self._draw_donut_slice(
                svg, cx, cy,
                outer_radius, inner_radius,
                start_angle, sweep_angle,
                color
            )

            start_angle += sweep_angle

    def _draw_donut_slice(
        self, svg, cx: float, cy: float,
        outer_r: float, inner_r: float,
        start_angle: float, sweep_angle: float,
        color: str
    ):
        """Draw a donut slice using SVG path.

        Args:
            svg: SVG element
            cx, cy: Center coordinates
            outer_r: Outer radius
            inner_r: Inner radius
            start_angle: Starting angle in degrees
            sweep_angle: Sweep angle in degrees
            color: Fill color
        """
        # Convert angles to radians
        start_rad = math.radians(start_angle)
        end_rad = math.radians(start_angle + sweep_angle)

        # Calculate outer arc points
        outer_x1 = cx + outer_r * math.cos(start_rad)
        outer_y1 = cy + outer_r * math.sin(start_rad)
        outer_x2 = cx + outer_r * math.cos(end_rad)
        outer_y2 = cy + outer_r * math.sin(end_rad)

        # Calculate inner arc points
        inner_x1 = cx + inner_r * math.cos(start_rad)
        inner_y1 = cy + inner_r * math.sin(start_rad)
        inner_x2 = cx + inner_r * math.cos(end_rad)
        inner_y2 = cy + inner_r * math.sin(end_rad)

        # Determine if we need large arc flag
        large_arc = 1 if sweep_angle > 180 else 0

        # Create path for donut slice
        path_data = f"""
            M {outer_x1},{outer_y1}
            A {outer_r},{outer_r} 0 {large_arc} 1 {outer_x2},{outer_y2}
            L {inner_x2},{inner_y2}
            A {inner_r},{inner_r} 0 {large_arc} 0 {inner_x1},{inner_y1}
            Z
        """.strip()

        # Add slice path
        ET.SubElement(svg, 'path', {
            'd': path_data,
            'fill': color,
            'stroke': self.colors['separator'],
            'stroke-width': str(self.separator_width)
        })

    def _render_center_text(self, svg, label: str, value: str, cx: float, cy: float):
        """Render text in center of donut chart.

        Args:
            svg: SVG element
            label: Label text (e.g., "Total")
            value: Value text (e.g., "99999")
            cx, cy: Center coordinates
        """
        # Render label above value
        label_elem = ET.SubElement(svg, 'text', {
            'x': str(cx),
            'y': str(cy - 8),
            'fill': self.colors['center_text'],
            'font-size': '12',
            'font-weight': '400',
            'text-anchor': 'middle'
        })
        label_elem.text = label

        # Render value below label
        value_elem = ET.SubElement(svg, 'text', {
            'x': str(cx),
            'y': str(cy + 8),
            'fill': self.colors['center_text'],
            'font-size': '16',
            'font-weight': '400',
            'text-anchor': 'middle'
        })
        value_elem.text = value
