"""SVG Radar Chart renderer matching Figma design exactly."""

import math
import xml.etree.ElementTree as ET
from typing import List, Optional


class SVGRadarChart:
    """Render radar charts as SVG matching Figma specifications."""

    def __init__(self, width: int = 328, height: int = 328):
        """Initialize SVG Radar Chart renderer.

        Args:
            width: Chart width in pixels
            height: Chart height in pixels
        """
        self.width = width
        self.height = height
        self.padding = 16
        self.title_height = 36

        # Default colors (can be updated from style config)
        self.colors = {
            'background': '#121212',
            'title': '#C5FFC8',
            'legend_text': '#769978',
            'axis_text': '#A9A9A9',
            'grid': '#2D3130',
            'axis': '#4A4A4A',
            'area1': '#90B892',
            'area1_stroke': '#5A715B',
            'area2': '#FA5A46',
            'area2_stroke': '#D94435',
        }

        self.num_axes = 8
        self.num_rings = 5
        self.fill_opacity = 0.6

    def create_svg(
        self,
        data_series: List[List[float]],
        labels: List[str],
        axis_labels: List[str],
        title: str = "Radar chart"
    ) -> str:
        """Create SVG radar chart.

        Args:
            data_series: List of data series, each containing values for each axis (0-100)
            labels: Labels for legend (e.g., ["One", "Two"])
            axis_labels: Labels for each axis (e.g., ["0", "45", "90", ...])
            title: Chart title

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
        self._render_legend(svg, labels)

        # Calculate chart center and radius
        available_height = self.height - self.title_height - self.padding * 2
        available_width = self.width - self.padding * 2
        max_radius = min(available_height, available_width) / 2
        center_x = self.width / 2
        center_y = self.title_height + available_height / 2

        # Render radar grid
        self._render_grid(svg, center_x, center_y, max_radius, axis_labels)

        # Render data series
        self._render_data_series(svg, data_series, center_x, center_y, max_radius)

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

    def _render_legend(self, svg, labels: List[str]):
        """Render horizontal legend below title."""
        legend_y = self.padding + 20
        legend_x = self.padding

        for i, label in enumerate(labels):
            # Color box
            if i == 0:
                color = self.colors['area1']
            else:
                color = self.colors.get(f'area{i+1}', self.colors['area2'])

            ET.SubElement(svg, 'rect', {
                'x': str(legend_x),
                'y': str(legend_y),
                'width': '8',
                'height': '8',
                'fill': color,
                'opacity': str(self.fill_opacity),
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

    def _render_grid(
        self, svg, cx: float, cy: float, max_radius: float, axis_labels: List[str]
    ):
        """Render radar chart grid (concentric circles and axes).

        Args:
            svg: SVG element
            cx, cy: Center coordinates
            max_radius: Maximum radius
            axis_labels: Labels for each axis
        """
        # Draw concentric circles
        for i in range(1, self.num_rings + 1):
            radius = (i / self.num_rings) * max_radius
            ET.SubElement(svg, 'circle', {
                'cx': str(cx),
                'cy': str(cy),
                'r': str(radius),
                'fill': 'none',
                'stroke': self.colors['grid'],
                'stroke-width': '1',
                'opacity': '0.3'
            })

            # Add value labels at top of each ring
            value = int((i / self.num_rings) * 100)
            text_elem = ET.SubElement(svg, 'text', {
                'x': str(cx),
                'y': str(cy - radius - 5),
                'fill': self.colors['axis_text'],
                'font-size': '10',
                'font-weight': '400',
                'text-anchor': 'middle'
            })
            text_elem.text = str(value)

        # Draw axes and labels
        for i in range(self.num_axes):
            angle_deg = (i * 360 / self.num_axes) - 90  # Start at top (270°)
            angle_rad = math.radians(angle_deg)

            # End point of axis
            end_x = cx + max_radius * math.cos(angle_rad)
            end_y = cy + max_radius * math.sin(angle_rad)

            # Draw axis line
            ET.SubElement(svg, 'line', {
                'x1': str(cx),
                'y1': str(cy),
                'x2': str(end_x),
                'y2': str(end_y),
                'stroke': self.colors['axis'],
                'stroke-width': '1',
                'opacity': '0.5'
            })

            # Add axis label if provided
            if i < len(axis_labels):
                # Position label slightly beyond the axis end
                label_distance = max_radius + 20
                label_x = cx + label_distance * math.cos(angle_rad)
                label_y = cy + label_distance * math.sin(angle_rad)

                # Determine text anchor based on position
                if label_x < cx - 10:
                    anchor = 'end'
                elif label_x > cx + 10:
                    anchor = 'start'
                else:
                    anchor = 'middle'

                text_elem = ET.SubElement(svg, 'text', {
                    'x': str(label_x),
                    'y': str(label_y + 4),  # Adjust for vertical centering
                    'fill': self.colors['axis_text'],
                    'font-size': '12',
                    'font-weight': '400',
                    'text-anchor': anchor
                })
                text_elem.text = axis_labels[i]

    def _render_data_series(
        self, svg, data_series: List[List[float]], cx: float, cy: float, max_radius: float
    ):
        """Render data series as filled polygons.

        Args:
            svg: SVG element
            data_series: List of data series
            cx, cy: Center coordinates
            max_radius: Maximum radius
        """
        for series_idx, data in enumerate(data_series):
            # Get colors for this series
            if series_idx == 0:
                fill_color = self.colors['area1']
                stroke_color = self.colors['area1_stroke']
            else:
                fill_color = self.colors.get(f'area{series_idx+1}', self.colors['area2'])
                stroke_color = self.colors.get(f'area{series_idx+1}_stroke', self.colors['area2_stroke'])

            # Build polygon points
            points = []
            for i, value in enumerate(data):
                angle_deg = (i * 360 / self.num_axes) - 90  # Start at top
                angle_rad = math.radians(angle_deg)

                # Calculate distance from center (value is 0-100)
                distance = (value / 100.0) * max_radius

                # Calculate point coordinates
                point_x = cx + distance * math.cos(angle_rad)
                point_y = cy + distance * math.sin(angle_rad)

                points.append(f"{point_x},{point_y}")

            # Create polygon
            ET.SubElement(svg, 'polygon', {
                'points': ' '.join(points),
                'fill': fill_color,
                'fill-opacity': str(self.fill_opacity),
                'stroke': stroke_color,
                'stroke-width': '2',
                'stroke-opacity': '0.8'
            })
