"""Radar chart configuration objects; public IDs stay in the registry."""

from typing import Any, Dict

BRAND: Dict[str, Any] = {
    "name": "Radar Chart - Brand Colors",
    "colors": {
        "background": "#121212",  # Dark background
        "title": "#C5FFC8",  # Brand accent green
        "legend_text": "#769978",  # Green-600
        "axis_text": "#A9A9A9",  # Gray for axis labels
        "grid": "#2D3130",  # Dark grid lines
        "axis": "#4A4A4A",  # Lighter axis lines
        "area1": "#90B892",  # Medium green with opacity
        "area1_stroke": "#5A715B",  # Dark green edge
        "area2": "#FA5A46",  # Error red-500
        "area2_stroke": "#D94435",  # Darker red edge
    },
    "font": {
        "family": "Hubot Sans",
        "size": {"title": 16, "label": 12, "axis": 10},
        "weight": {"title": 400, "label": 400, "axis": 400},
    },
    "radar": {
        "num_axes": 8,  # 8 axes (octagon)
        "num_rings": 5,  # 5 concentric circles
        "fill_opacity": 0.6,
    },
}

BLACK: Dict[str, Any] = {
    "name": "Radar Chart - Black/Grayscale Theme",
    "colors": {
        "background": "#121212",  # Dark background
        "title": "#FFFFFF",  # White title
        "legend_text": "#A9A9A9",  # Gray legend
        "axis_text": "#A9A9A9",  # Gray for axis labels
        "grid": "#2D3130",  # Dark grid lines
        "axis": "#4A4A4A",  # Lighter axis lines
        "area1": "#C8C8C8",  # Light gray
        "area1_stroke": "#909090",  # Medium gray edge
        "area2": "#606060",  # Medium-dark gray
        "area2_stroke": "#303030",  # Very dark gray edge
    },
    "font": {
        "family": "Hubot Sans",
        "size": {"title": 16, "label": 12, "axis": 10},
        "weight": {"title": 400, "label": 400, "axis": 400},
    },
    "radar": {
        "num_axes": 8,  # 8 axes (octagon)
        "num_rings": 5,  # 5 concentric circles
        "fill_opacity": 0.6,
    },
}

WHITE: Dict[str, Any] = {
    "name": "Radar Chart - White Theme",
    "colors": {
        "background": "#FFFFFF",  # White background
        "title": "#000000",  # Black title
        "legend_text": "#666666",  # Gray legend
        "axis_text": "#666666",  # Gray for axis labels
        "grid": "#E5E5E5",  # Light grid lines
        "axis": "#CCCCCC",  # Light axis lines
        "area1": "#484848",  # Dark gray
        "area1_stroke": "#303030",  # Very dark gray edge
        "area2": "#909090",  # Medium-light gray
        "area2_stroke": "#606060",  # Medium gray edge
    },
    "font": {
        "family": "Hubot Sans",
        "size": {"title": 16, "label": 12, "axis": 10},
        "weight": {"title": 400, "label": 400, "axis": 400},
    },
    "radar": {
        "num_axes": 8,  # 8 axes (octagon)
        "num_rings": 5,  # 5 concentric circles
        "fill_opacity": 0.6,
    },
}
