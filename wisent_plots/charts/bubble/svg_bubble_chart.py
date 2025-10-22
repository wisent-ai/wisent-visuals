"""SVG-based bubble chart for pixel-perfect Figma matching."""

from typing import List, Optional
import xml.etree.ElementTree as ET
import numpy as np


class SVGBubbleChart:
    """Generate pixel-perfect SVG bubble charts matching Figma design."""

    def __init__(self, width: int = 456, height: int = 383):
        """Initialize SVG bubble chart with exact Figma dimensions.

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
        x_data: List[float],
        y_data: List[float],
        sizes: List[float],
        categories: Optional[List[str]] = None,
        category_labels: Optional[List[str]] = None,
        title: str = "Bubble Chart",
        x_label: str = "",
        y_label: str = "",
        size_range: tuple = (5, 20)
    ) -> str:
        """Create SVG bubble chart matching Figma design exactly.

        Args:
            x_data: X-axis data points
            y_data: Y-axis data points
            sizes: Sizes for each bubble
            categories: Category index for each point (for coloring)
            category_labels: Labels for legend
            title: Chart title
            x_label: X-axis label
            y_label: Y-axis label
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

        # Calculate chart area
        chart_x = self.padding_x + 40
        chart_y = self.chart_top_margin
        chart_width = self.width - self.padding_x * 2 - 50
        chart_height = self.height - self.chart_top_margin - 50

        # Render grid and axes
        self._render_grid(svg, chart_x, chart_y, chart_width, chart_height)

        # Render bubbles
        self._render_bubbles(
            svg, x_data, y_data, sizes, categories,
            chart_x, chart_y, chart_width, chart_height, size_range
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

    def _render_grid(self, svg, x: int, y: int, width: int, height: int):
        """Render grid lines and axis labels."""
        # Horizontal grid lines
        num_h_lines = 5
        for i in range(num_h_lines + 1):
            y_pos = y + (i * height / num_h_lines)
            ET.SubElement(svg, 'line', {
                'x1': str(x),
                'y1': str(y_pos),
                'x2': str(x + width),
                'y2': str(y_pos),
                'stroke': self.colors['grid'],
                'stroke-width': '1',
                'opacity': '0.3'
            })

            # Y-axis labels
            value = 1000 - (i * 200)
            text_elem = ET.SubElement(svg, 'text', {
                'x': str(x - 10),
                'y': str(y_pos + 5),
                'fill': self.colors['axis_text'],
                'font-size': '12',
                'font-weight': '400',
                'text-anchor': 'end'
            })
            text_elem.text = str(value)

        # Vertical grid lines
        num_v_lines = 5
        for i in range(num_v_lines + 1):
            x_pos = x + (i * width / num_v_lines)
            ET.SubElement(svg, 'line', {
                'x1': str(x_pos),
                'y1': str(y),
                'x2': str(x_pos),
                'y2': str(y + height),
                'stroke': self.colors['grid'],
                'stroke-width': '1',
                'opacity': '0.3'
            })

            # X-axis labels
            if i < num_v_lines:
                value = i * 20 + 10
                text_elem = ET.SubElement(svg, 'text', {
                    'x': str(x_pos + width / num_v_lines / 2),
                    'y': str(y + height + 20),
                    'fill': self.colors['axis_text'],
                    'font-size': '12',
                    'font-weight': '400',
                    'text-anchor': 'middle'
                })
                text_elem.text = f"{value:02d}"

    def _render_bubbles(
        self,
        svg,
        x_data: List[float],
        y_data: List[float],
        sizes: List[float],
        categories: Optional[List[str]],
        chart_x: int,
        chart_y: int,
        chart_width: int,
        chart_height: int,
        size_range: tuple
    ):
        """Render bubbles on the chart."""
        # Normalize data
        x_min, x_max = min(x_data), max(x_data)
        y_min, y_max = min(y_data), max(y_data)
        size_min, size_max = min(sizes), max(sizes)

        min_r, max_r = size_range

        for i, (x, y, size) in enumerate(zip(x_data, y_data, sizes)):
            # Normalize positions
            x_norm = (x - x_min) / (x_max - x_min) if x_max != x_min else 0.5
            y_norm = (y - y_min) / (y_max - y_min) if y_max != y_min else 0.5

            # Calculate pixel positions (invert Y axis)
            x_pos = chart_x + x_norm * chart_width
            y_pos = chart_y + chart_height - (y_norm * chart_height)

            # Calculate radius
            size_norm = (size - size_min) / (size_max - size_min) if size_max != size_min else 0.5
            radius = min_r + size_norm * (max_r - min_r)

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
                'r': str(radius),
                'fill': color,
                'opacity': '0.7'
            })

    def save_svg(self, svg_string: str, filename: str):
        """Save SVG to file."""
        with open(filename, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(svg_string)
