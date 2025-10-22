"""SVG area chart with gradient fills matching Figma design."""

import xml.etree.ElementTree as ET
from typing import List
from wisent_plots.charts.area_chart_components import render_title_and_legend
from wisent_plots.charts.area_chart_renderer import _generate_stacked_paths


class SVGAreaChartGradient:
    """Create pixel-perfect SVG area charts with gradient fills."""

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
            'background': '#121212',
            'title': '#C5FFC8',
            'legend_text': '#769978',
            'grid': '#2D3130',
            'area': '#C5FFC8',
            'primary': '#B0E3B3',
            'secondary': '#90B892',
            'accent': '#5A715B',
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
        title: str = "Area Chart"
    ) -> str:
        """Create SVG area chart with gradient fills.

        Args:
            x_data: X-axis data points
            y_series: List of Y-axis data series
            labels: Legend labels
            title: Chart title

        Returns:
            SVG string
        """
        # Create root SVG element
        svg = ET.Element('svg', {
            'width': str(self.width),
            'height': str(self.height),
            'xmlns': 'http://www.w3.org/2000/svg',
            'viewBox': f'0 0 {self.width} {self.height}'
        })

        # Add Google Fonts
        style = ET.SubElement(svg, 'style')
        style.text = """
            @import url('https://fonts.googleapis.com/css2?family=Hubot+Sans:wght@400&display=swap');
            text { font-family: 'Hubot Sans', sans-serif; }
        """

        # Background rectangle
        ET.SubElement(svg, 'rect', {
            'width': str(self.width),
            'height': str(self.height),
            'fill': self.colors['background'],
            'rx': '20',
            'ry': '20'
        })

        # Define gradients FIRST (before rendering legend)
        # Use a temporary chart_start_y for gradient positioning
        temp_chart_start_y = self.padding_y + 20 + self.title_gap + 24 + self.chart_top_margin
        self._create_gradients(svg, temp_chart_start_y)

        # Render title and legend with gradients
        chart_start_y = self._render_title_and_legend_with_gradients(
            svg, title, labels
        )

        # Chart area coordinates
        chart_x = self.padding_x
        chart_height = self.height - self.padding_y - chart_start_y

        # Update gradients with actual chart position
        self._create_gradients(svg, chart_start_y)

        # Render area chart with gradients
        self._render_gradient_areas(
            svg, x_data, y_series,
            chart_x, chart_start_y,
            self.chart_width, chart_height
        )

        # Convert to string
        return ET.tostring(svg, encoding='unicode', method='xml')

    def _render_title_and_legend_with_gradients(self, svg, title: str, labels: List[str]) -> int:
        """Render title and legend with gradient fills matching the chart."""
        # Title (20px, left-aligned at padding_x, padding_y)
        title_elem = ET.SubElement(svg, 'text', {
            'x': str(self.padding_x),
            'y': str(self.padding_y + 20),
            'fill': self.colors['title'],
            'font-size': '20',
            'font-weight': '400'
        })
        title_elem.text = title

        # Legend - horizontal layout below title
        legend_y = self.padding_y + 20 + self.title_gap + 4
        legend_x = self.padding_x

        # Gradient/fill mapping for each series (bottom to top in stacking order)
        fills = [
            'url(#grad-bottom)',  # Bottom band - lightest gradient
            'url(#grad-middle)',  # Middle band - medium gradient
            'url(#grad-top)'  # Top band - darkest gradient
        ]

        for i, label in enumerate(labels):
            # Get fill (gradient or color) for this series
            fill = fills[i] if i < len(fills) else self.colors['primary']

            # Color box (20x10px with 2px border radius)
            ET.SubElement(svg, 'rect', {
                'x': str(legend_x),
                'y': str(legend_y),
                'width': '20',
                'height': '10',
                'fill': fill,
                'rx': '2',
                'ry': '2'
            })

            # Label text (14px, gap of 8px from box)
            text = ET.SubElement(svg, 'text', {
                'x': str(legend_x + 28),
                'y': str(legend_y + 9),
                'fill': self.colors['legend_text'],
                'font-size': '14',
                'font-weight': '400'
            })
            text.text = label

            # Move to next legend item (gap of 20px between items)
            legend_x += 20 + 8 + len(label) * 8 + 20

        # Return chart start Y position
        return self.padding_y + 20 + self.title_gap + 24 + self.chart_top_margin

    def _create_gradients(self, svg, chart_start_y):
        """Create SVG gradient definitions."""
        defs = svg.find('defs')
        if defs is None:
            defs = ET.SubElement(svg, 'defs')

        # Gradient for bottom band (lightest) - from light to lighter
        grad1 = ET.SubElement(defs, 'linearGradient', {
            'id': 'grad-bottom',
            'x1': '0%',
            'y1': '100%',  # Start at bottom
            'x2': '0%',
            'y2': '0%'  # End at top
        })
        ET.SubElement(grad1, 'stop', {
            'offset': '0%',
            'style': 'stop-color:#C5FFC8;stop-opacity:1'  # Light at bottom
        })
        ET.SubElement(grad1, 'stop', {
            'offset': '100%',
            'style': 'stop-color:#7FA682;stop-opacity:1'  # Darker at top
        })

        # Gradient for middle band
        grad2 = ET.SubElement(defs, 'linearGradient', {
            'id': 'grad-middle',
            'x1': '0%',
            'y1': '100%',
            'x2': '0%',
            'y2': '0%'
        })
        ET.SubElement(grad2, 'stop', {
            'offset': '0%',
            'style': 'stop-color:#90B892;stop-opacity:1'
        })
        ET.SubElement(grad2, 'stop', {
            'offset': '100%',
            'style': 'stop-color:#5F7861;stop-opacity:1'
        })

        # Gradient for top band (darkest)
        grad3 = ET.SubElement(defs, 'linearGradient', {
            'id': 'grad-top',
            'x1': '0%',
            'y1': '100%',
            'x2': '0%',
            'y2': '0%'
        })
        ET.SubElement(grad3, 'stop', {
            'offset': '0%',
            'style': 'stop-color:#5A715B;stop-opacity:1'
        })
        ET.SubElement(grad3, 'stop', {
            'offset': '100%',
            'style': 'stop-color:#3D4D3E;stop-opacity:1'
        })

    def _render_gradient_areas(
        self,
        svg,
        x_data: List[float],
        y_series: List[List[float]],
        chart_x: int,
        chart_start_y: int,
        chart_width: int,
        chart_height: int
    ):
        """Render gradient-filled area chart."""
        # Create clipping path
        clip_id = "chart-clip-gradient"
        defs = svg.find('defs')
        if defs is None:
            defs = ET.SubElement(svg, 'defs')

        clipPath = ET.SubElement(defs, 'clipPath', {'id': clip_id})
        ET.SubElement(clipPath, 'rect', {
            'x': str(chart_x),
            'y': str(chart_start_y),
            'width': str(chart_width),
            'height': str(chart_height - 40)
        })

        # Generate stacked paths
        paths = _generate_stacked_paths(
            x_data, y_series,
            chart_x, chart_start_y,
            chart_width, chart_height - 40
        )

        # Draw grid lines FIRST so area bands appear in front
        grid_spacing = 67
        for i in range(15):
            x = chart_x + (i * grid_spacing)
            if x <= chart_x + chart_width:
                # Dashed vertical line
                ET.SubElement(svg, 'line', {
                    'x1': str(x),
                    'y1': str(chart_start_y),
                    'x2': str(x),
                    'y2': str(chart_start_y + chart_height - 40),
                    'stroke': self.colors['grid'],
                    'stroke-width': '1',
                    'stroke-dasharray': '4,4'
                })

                # X-axis label
                if i < 14:
                    label_text = f"{i+1:02d}"
                    label_elem = ET.SubElement(svg, 'text', {
                        'x': str(x + 10),
                        'y': str(chart_start_y + chart_height - 10),
                        'fill': self.colors['legend_text'],
                        'font-size': '14',
                        'font-weight': '400',
                        'text-anchor': 'middle'
                    })
                    label_elem.text = label_text

        # Draw bands with gradients
        # Top band (smallest) - darkest gradient
        ET.SubElement(svg, 'path', {
            'd': paths[2][0],
            'fill': 'url(#grad-top)',
            'fill-rule': 'evenodd',
            'clip-path': f'url(#{clip_id})'
        })

        # Middle band - medium gradient
        ET.SubElement(svg, 'path', {
            'd': paths[1][0],
            'fill': 'url(#grad-middle)',
            'fill-rule': 'evenodd',
            'clip-path': f'url(#{clip_id})'
        })

        # Bottom band (largest) - lightest gradient
        ET.SubElement(svg, 'path', {
            'd': paths[0][0],
            'fill': 'url(#grad-bottom)',
            'fill-rule': 'evenodd',
            'clip-path': f'url(#{clip_id})'
        })

    def save_svg(self, svg_string: str, filename: str) -> None:
        """Save SVG string to file."""
        with open(filename, 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(svg_string)
