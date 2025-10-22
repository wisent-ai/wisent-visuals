"""SVG-based radar bubble chart for pixel-perfect Figma matching."""

from typing import List, Optional
import xml.etree.ElementTree as ET
import numpy as np
import math


class SVGRadarBubbleChart:
    """Generate pixel-perfect SVG radar/spider bubble charts matching Figma design."""

    def __init__(self, width: int = 456, height: int = 383):
        """Initialize SVG radar bubble chart with exact Figma dimensions.

        Args:
            width: Chart width in pixels (default from Figma: 456)
            height: Chart height in pixels (default from Figma: 383)
        """
        self.width = width
        self.height = height

        # Exact Figma colors
        self.colors = {
            'background': '#121212',
            'title': '#C5FFC8',
            'legend_text': '#769978',
            'grid': '#2D3130',
            'axis_text': '#769978',
            'axis_line': '#4A4A4A',
            # Bubble colors (brand color scheme)
            'bubble1': '#FA5A46',  # Red
            'bubble2': '#FF8C00',  # Orange
            'bubble3': '#FFD700',  # Yellow
            'bubble4': '#C5FFC8',  # Green
            'bubble5': '#00CED1',  # Cyan
            'bubble6': '#87CEEB',  # Sky blue
            'bubble7': '#B19ECC',  # Purple
            'bubble8': '#FFB6C1',  # Light pink
            'bubble9': '#A9A9A9',  # Gray
        }

        # Chart dimensions
        self.padding_x = 32
        self.padding_y = 16
        self.title_gap = 10
        self.legend_gap = 8
        self.chart_top_margin = 60

    def create_chart(
        self,
        angles: List[float],
        distances: List[float],
        sizes: List[float],
        categories: Optional[List[int]] = None,
        category_labels: Optional[List[str]] = None,
        title: str = "Bubble Radar chart",
        num_rings: int = 5,
        num_axes: int = 8,
        size_range: tuple = (5, 15)
    ) -> str:
        """Create SVG radar bubble chart matching Figma design.

        Args:
            angles: Angle for each bubble (in degrees, 0-360)
            distances: Distance from center for each bubble (0-100)
            sizes: Sizes for each bubble
            categories: Category index for each point (for coloring)
            category_labels: Labels for legend
            title: Chart title
            num_rings: Number of concentric rings
            num_axes: Number of radial axes
            size_range: Min and max bubble radius (min_r, max_r)

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
        bg_color = self.colors.get('background', '#121212')
        ET.SubElement(svg, 'rect', {
            'width': str(self.width),
            'height': str(self.height),
            'fill': bg_color,
            'rx': '20',
            'ry': '20'
        })

        # Render title
        title_y = self.padding_y + 20
        title_elem = ET.SubElement(svg, 'text', {
            'x': str(self.padding_x),
            'y': str(title_y),
            'fill': self.colors['title'],
            'font-size': '20',
            'font-weight': '400'
        })
        title_elem.text = title

        # Render legend if category labels provided
        # Only show labels for categories that are actually used in the data
        if category_labels and categories:
            unique_categories = sorted(set(categories))
            filtered_labels = [category_labels[i] for i in unique_categories if i < len(category_labels)]
            self._render_legend(svg, filtered_labels, unique_categories)
        elif category_labels:
            self._render_legend(svg, category_labels, None)

        # Calculate chart center and radius
        chart_center_x = self.width // 2
        chart_center_y = (self.height + self.chart_top_margin) // 2
        max_radius = min(self.width, self.height - self.chart_top_margin) // 2 - 60

        # Render radar grid
        self._render_radar_grid(svg, chart_center_x, chart_center_y, max_radius, num_rings, num_axes)

        # Render bubbles
        self._render_radar_bubbles(
            svg, angles, distances, sizes, categories,
            chart_center_x, chart_center_y, max_radius, size_range
        )

        # Convert to string
        return ET.tostring(svg, encoding='unicode', method='xml')

    def _render_legend(self, svg, labels: List[str], category_indices: Optional[List[int]] = None):
        """Render horizontal legend below title.

        Args:
            svg: SVG element to add legend to
            labels: Labels to display
            category_indices: Optional list of category indices (for proper color mapping)
        """
        legend_y = self.padding_y + 36
        legend_x = self.padding_x

        for i, label in enumerate(labels):
            # Color box - use category index if provided, otherwise use label index
            if category_indices and i < len(category_indices):
                cat_idx = category_indices[i]
            else:
                cat_idx = i
            color_key = f'bubble{cat_idx+1}'
            color = self.colors.get(color_key, self.colors['bubble9'])

            ET.SubElement(svg, 'rect', {
                'x': str(legend_x),
                'y': str(legend_y),
                'width': '20',
                'height': '10',
                'fill': color,
                'rx': '2',
                'ry': '2'
            })

            # Label text
            text_elem = ET.SubElement(svg, 'text', {
                'x': str(legend_x + 28),
                'y': str(legend_y + 9),
                'fill': self.colors['legend_text'],
                'font-size': '12',
                'font-weight': '400'
            })
            text_elem.text = label

            # Move to next position
            legend_x += 60

    def _render_radar_grid(self, svg, cx: float, cy: float, max_r: float, num_rings: int, num_axes: int):
        """Render concentric circles and radial axes."""
        # Draw concentric circles
        for i in range(1, num_rings + 1):
            radius = (i / num_rings) * max_r
            ET.SubElement(svg, 'circle', {
                'cx': str(cx),
                'cy': str(cy),
                'r': str(radius),
                'fill': 'none',
                'stroke': self.colors['grid'],
                'stroke-width': '1',
                'opacity': '0.3'
            })

            # Add ring labels at top (90 degrees)
            if i > 0:
                label_y = cy - radius - 5
                value = i * 20  # 0, 20, 40, 60, 80, 100
                text_elem = ET.SubElement(svg, 'text', {
                    'x': str(cx),
                    'y': str(label_y),
                    'fill': self.colors['axis_text'],
                    'font-size': '10',
                    'font-weight': '400',
                    'text-anchor': 'middle'
                })
                text_elem.text = f"{value:02d}"

        # Draw radial axes
        for i in range(num_axes):
            angle = (i * 360 / num_axes) - 90  # Start from top (90 degrees)
            angle_rad = math.radians(angle)

            # Calculate end point
            end_x = cx + max_r * math.cos(angle_rad)
            end_y = cy + max_r * math.sin(angle_rad)

            # Draw axis line
            ET.SubElement(svg, 'line', {
                'x1': str(cx),
                'y1': str(cy),
                'x2': str(end_x),
                'y2': str(end_y),
                'stroke': self.colors['axis_line'],
                'stroke-width': '1',
                'opacity': '0.5'
            })

            # Add axis labels
            label_distance = max_r + 20
            label_x = cx + label_distance * math.cos(angle_rad)
            label_y = cy + label_distance * math.sin(angle_rad) + 5

            # Calculate which quadrant for text anchor
            if -45 <= angle < 45 or angle >= 315:
                text_anchor = 'start'
            elif 135 <= angle < 225:
                text_anchor = 'end'
            else:
                text_anchor = 'middle'

            axis_label = f"{i * (360 // num_axes):02d}"
            text_elem = ET.SubElement(svg, 'text', {
                'x': str(label_x),
                'y': str(label_y),
                'fill': self.colors['axis_text'],
                'font-size': '12',
                'font-weight': '400',
                'text-anchor': text_anchor
            })
            text_elem.text = axis_label

    def _render_radar_bubbles(
        self,
        svg,
        angles: List[float],
        distances: List[float],
        sizes: List[float],
        categories: Optional[List[int]],
        cx: float,
        cy: float,
        max_radius: float,
        size_range: tuple
    ):
        """Render bubbles on the radar chart."""
        # Normalize sizes
        size_min, size_max = min(sizes), max(sizes)
        min_r, max_r = size_range

        for i, (angle, distance, size) in enumerate(zip(angles, distances, sizes)):
            # Convert angle to radians (0 degrees = top, clockwise)
            angle_rad = math.radians(angle - 90)

            # Calculate position
            radius = (distance / 100.0) * max_radius
            x_pos = cx + radius * math.cos(angle_rad)
            y_pos = cy + radius * math.sin(angle_rad)

            # Calculate bubble radius
            size_norm = (size - size_min) / (size_max - size_min) if size_max != size_min else 0.5
            bubble_radius = min_r + size_norm * (max_r - min_r)

            # Get color based on category
            if categories and i < len(categories):
                cat_idx = categories[i]
                color_key = f'bubble{cat_idx + 1}'
                color = self.colors.get(color_key, self.colors['bubble9'])
            else:
                color = self.colors['bubble1']

            # Draw bubble
            ET.SubElement(svg, 'circle', {
                'cx': str(x_pos),
                'cy': str(y_pos),
                'r': str(bubble_radius),
                'fill': color,
                'opacity': '0.7'
            })

    def save_svg(self, svg_string: str, filename: str):
        """Save SVG to file."""
        with open(filename, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(svg_string)
