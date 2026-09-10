"""Embed shipped SVG patterns without duplicating parsing and namespace handling."""

import os
import xml.etree.ElementTree as ET


def _asset_path(*parts):
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", *parts)

def _create_cartesian_patterns(svg, style: int):
        """Create SVG pattern definitions based on style."""
        defs = svg.find('defs')
        if defs is None:
            defs = ET.SubElement(svg, 'defs')

        # Get path to assets directory
        assets_dir = _asset_path()

        # Style 2: noise pattern for middle column
        if style == 2:
            _load_pattern_from_file(defs, 'pattern-noise', os.path.join(assets_dir, 'large', 'noise_rectangle_large.svg'))

        # Style 3: crossing lines for middle column
        elif style == 3:
            _load_pattern_from_file(defs, 'pattern-crossing', os.path.join(assets_dir, 'pattern_crossing_lines.svg'))

        # Style 4: noise + dither crosses
        elif style == 4:
            _load_pattern_from_file(defs, 'pattern-noise', os.path.join(assets_dir, 'large', 'noise_rectangle_large.svg'))
            _load_pattern_from_file(defs, 'pattern-dither', os.path.join(assets_dir, 'large', 'dither_cross_large.svg'))

def _load_pattern_from_file(defs, pattern_id: str, svg_file: str):
        """Load and embed an SVG pattern from a file."""
        pattern_tree = ET.parse(svg_file)
        pattern_root = pattern_tree.getroot()

        # Extract width and height
        width = pattern_root.get('width')
        height = pattern_root.get('height')
        viewBox = pattern_root.get('viewBox')

        if viewBox:
            viewBox_parts = viewBox.split()
            if len(viewBox_parts) == 4:
                width = viewBox_parts[2]
                height = viewBox_parts[3]

        # Create pattern element
        pattern_elem = ET.SubElement(defs, 'pattern', {
            'id': pattern_id,
            'patternUnits': 'userSpaceOnUse',
            'width': width,
            'height': height
        })

        # Copy all child elements from the pattern SVG
        for child in pattern_root:
            tag = child.tag
            if tag.startswith('{'):
                tag = tag.split('}')[1]
            if tag in ['title', 'desc', 'metadata']:
                continue
            _copy_element(child, pattern_elem)

def _copy_element(source, parent):
        """Recursively copy an element and its children."""
        tag = source.tag
        if tag.startswith('{'):
            tag = tag.split('}')[1]

        attribs = {}
        for key, value in source.attrib.items():
            if key.startswith('{'):
                key = key.split('}')[1]
            attribs[key] = value

        new_elem = ET.SubElement(parent, tag, attribs)
        new_elem.text = source.text
        new_elem.tail = source.tail

        for child in source:
            _copy_element(child, new_elem)

