"""Pie chart configuration objects; public IDs stay in the registry."""

from typing import Any, Dict

BRAND: Dict[str, Any] = {
        "name": "Pie Chart - Brand Colors",
        "colors": {
            "background": "#121212",  # Dark background
            "title": "#C5FFC8",  # Brand accent green
            "legend_text": "#769978",  # Green-600
            "center_text": "#FFFFFF",  # White for center label
            "separator": "#000000",  # Black lines between slices
            "slice1": "#C5FFC8",  # Brand accent green
            "slice2": "#FA5A46",  # Error red-500
            "slice3": "#FFB366",  # Warning orange-400
            "slice4": "#FFD699",  # Warning orange-300
            "slice5": "#B19ECC",  # Character purple-500
            "slice6": "#A4C2F4",  # Accent blue-400
        },
        "font": {
            "family": "Hubot Sans",
            "size": {"title": 16, "label": 12, "center": 12},
            "weight": {"title": 400, "label": 400, "center": 400},
        },
        "pie": {
            "inner_radius": 0.55,  # Donut chart (55% inner radius)
            "separator_width": 2,
        },
}

BLACK: Dict[str, Any] = {
        "name": "Pie Chart - Black/Grayscale Theme",
        "colors": {
            "background": "#121212",  # Dark background
            "title": "#FFFFFF",  # White title
            "legend_text": "#A9A9A9",  # Gray legend
            "center_text": "#FFFFFF",  # White for center label
            "separator": "#000000",  # Black lines between slices
            "slice1": "#FFFFFF",  # White
            "slice2": "#E0E0E0",  # Light gray
            "slice3": "#C8C8C8",  # Medium-light gray
            "slice4": "#A9A9A9",  # Medium gray
            "slice5": "#909090",  # Medium-dark gray
            "slice6": "#787878",  # Dark gray
        },
        "font": {
            "family": "Hubot Sans",
            "size": {"title": 16, "label": 12, "center": 12},
            "weight": {"title": 400, "label": 400, "center": 400},
        },
        "pie": {
            "inner_radius": 0.55,  # Donut chart (55% inner radius)
            "separator_width": 2,
        },
}

WHITE: Dict[str, Any] = {
        "name": "Pie Chart - White Theme",
        "colors": {
            "background": "#FFFFFF",  # White background
            "title": "#000000",  # Black title
            "legend_text": "#666666",  # Gray legend
            "center_text": "#000000",  # Black for center label
            "separator": "#FFFFFF",  # White lines between slices (inverted)
            "slice1": "#303030",  # Very dark gray
            "slice2": "#484848",  # Dark gray
            "slice3": "#606060",  # Medium-dark gray
            "slice4": "#787878",  # Medium gray
            "slice5": "#909090",  # Medium-light gray
            "slice6": "#C8C8C8",  # Light gray
        },
        "font": {
            "family": "Hubot Sans",
            "size": {"title": 16, "label": 12, "center": 12},
            "weight": {"title": 400, "label": 400, "center": 400},
        },
        "pie": {
            "inner_radius": 0.55,  # Donut chart (55% inner radius)
            "separator_width": 2,
        },
}
