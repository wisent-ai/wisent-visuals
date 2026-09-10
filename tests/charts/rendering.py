"""Exercise real chart output; optional artifacts retain before/after render evidence."""

import json
import os
import re
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.path import Path as PlotPath

from wisent_plots import AreaChart, BarChart, BubbleChart, ColumnChart, LineChart
from wisent_plots.styles import STYLES, get_style


class RenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = None
        configured = os.environ.get("WISENT_VISUALS_ARTIFACT_DIR")
        if configured:
            cls.artifacts = Path(configured)
        else:
            work = Path.home() / ".stado" / "work"
            work.mkdir(parents=True, exist_ok=True)
            cls.temporary = tempfile.TemporaryDirectory(prefix="chart-tests-", dir=work)
            cls.artifacts = Path(cls.temporary.name)
        cls.artifacts.mkdir(parents=True, exist_ok=True)
        (cls.artifacts / "styles.json").write_text(
            json.dumps({number: get_style(number) for number in STYLES}, sort_keys=True, indent=2),
            encoding="utf-8",
        )

    @classmethod
    def tearDownClass(cls):
        if cls.temporary is not None:
            cls.temporary.cleanup()

    def save_svg(self, relative, svg):
        root = ET.fromstring(svg)
        self.assertEqual(root.tag, "{http://www.w3.org/2000/svg}svg")
        definitions = {node.attrib["id"] for node in root.iter() if "id" in node.attrib}
        references = {
            match
            for node in root.iter()
            for value in node.attrib.values()
            for match in re.findall(r"url\(#([^)]*)\)", value)
        }
        self.assertFalse(
            references - definitions, "SVG paint or clipping references are unresolved"
        )
        target = self.artifacts / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(svg, encoding="utf-8")
        return root

    def test_area_stack_preserves_caller_axes_and_cumulative_geometry(self):
        with matplotlib.rc_context():
            fig, ax = plt.subplots()
            original = ax.plot([1, 2, 3], [-1, -1, -1])[0]
            chart = AreaChart(style=5, edge=True, stacked=True)
            returned = chart.plot_multiple(
                [1, 2, 3],
                [[1, 2, 3], [4, 4, 4]],
                labels=["A", "B"],
                title="Stacked area",
                fig=fig,
                ax=ax,
                output_format="matplotlib",
            )
            self.assertIs(returned[0], fig)
            self.assertIs(returned[1], ax)
            self.assertIn(original, ax.lines)
            vertices = ax.collections[-1].get_paths()[0].vertices
            tops = [vertices[vertices[:, 0] == x, 1].max() for x in [1, 2, 3]]
            np.testing.assert_allclose(tops, [5, 6, 7])
            target = self.artifacts / "area" / "stacked.png"
            target.parent.mkdir(parents=True, exist_ok=True)
            chart.save(fig, str(target))
            plt.close(fig)

    def test_line_keeps_a_gap_where_observations_are_missing(self):
        with matplotlib.rc_context():
            chart = LineChart(style=2, show_markers=True, line_width=3)
            fig, ax = chart.plot(
                [1, 2, 3, 4, 5],
                [1, 2, np.nan, 4, 3],
                color="#E63946",
                label="Observed",
            )
            segments = ax.lines[-1].get_path().iter_segments()
            starts = [vertices.tolist() for vertices, code in segments if code == PlotPath.MOVETO]
            self.assertEqual(starts, [[1.0, 1.0], [4.0, 4.0]])
            target = self.artifacts / "line" / "gaps.png"
            target.parent.mkdir(parents=True, exist_ok=True)
            chart.save(fig, str(target))
            plt.close(fig)

    def test_svg_backends_embed_their_real_paint_and_clipping_resources(self):
        categories = ["A", "B", "C"]
        series = [[3, 5, 4], [2, 3, 5], [1, 4, 2]]
        labels = ["First", "Second", "Third"]
        for style in range(1, 6):
            with self.subTest(kind="area", style=style):
                svg = AreaChart(style=style, edge=True).plot_multiple(categories, series, labels)
                self.save_svg(f"area/svg/style-{style}.svg", svg)
        for kind, chart_type in [("bar", BarChart), ("column", ColumnChart)]:
            for style in range(1, 6):
                with self.subTest(kind=kind, style=style):
                    svg = chart_type(style=style, theme="brand").plot(categories, series, labels)
                    self.save_svg(f"{kind}/style-{style}.svg", svg)
        svg = LineChart(style=3).plot_multiple([1, 2, 3], series, labels)
        self.save_svg("line/shapes.svg", svg)
        svg = BubbleChart(chart_type="radar").plot(
            angles=[0, 90, 180],
            distances=[0, 50, 100],
            sizes=[2, 4, 8],
            categories=[0, 1, 2],
            category_labels=labels,
        )
        self.save_svg("bubble/radar.svg", svg)
        with self.assertRaisesRegex(ValueError, "Only 'svg' output format is currently supported"):
            BarChart().plot(categories, series, labels, output_format="unsupported")


if __name__ == "__main__":
    unittest.main()
