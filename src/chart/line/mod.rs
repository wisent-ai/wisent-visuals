//! Line charts: one or more series over shared x values.
//!
//! ```json
//! {"kind": "line", "style": 3, "width": 1002, "height": 580, "line_width": 2,
//!  "x": [1, 2, 3, 4], "y_series": [[2, 4, 3, 5], [1, 3, 2, 4]],
//!  "labels": ["One", "Two"], "title": "Line Chart"}
//! ```
//! `colors` replaces the style's series colours, one per series. Each x value
//! gets a dashed grid line and its own label; the y axis spans the data.

mod style;

use serde::Deserialize;

use super::parts::element::{chart_frame, Element};
use super::parts::legend::{render_marker, render_title_and_legend, LegendFills};
use super::parts::StyleChoice;

/// The design's card padding, title gap and chart top margin.
const PADDING_X: f64 = 32.0;
const PADDING_Y: f64 = 16.0;
const TITLE_GAP: f64 = 10.0;
const CHART_TOP_MARGIN: f64 = 24.0;
/// The design's room under the plot for the x labels, and their baseline below it.
const X_LABEL_ROOM: f64 = 56.0;
const X_LABEL_OFFSET: f64 = 23.0;
const TICK_SIZE: f64 = 14.0;
/// The design's grid: dashed verticals, four horizontal bands.
const VERTICAL_DASH: &str = "4,4";
const HORIZONTAL_BANDS: u32 = 4;
/// The design's marker side.
const MARKER_SIZE: f64 = 11.0;

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Spec {
    /// 1–3 dark (solid, markers, shapes), 4–6 the same on white; or a dark style's name.
    pub style: StyleChoice,
    pub width: f64,
    pub height: f64,
    pub line_width: f64,
    pub x: Vec<f64>,
    pub y_series: Vec<Vec<f64>>,
    #[serde(default)]
    pub labels: Option<Vec<String>>,
    #[serde(default)]
    pub colors: Option<Vec<String>>,
    #[serde(default)]
    pub title: Option<String>,
}

/// The most fractional digits any of `values` is written with.
fn precision(values: &[f64]) -> usize {
    values
        .iter()
        .map(|value| {
            value
                .to_string()
                .split_once('.')
                .map(|(_, fraction)| fraction.len())
                .unwrap_or(0)
        })
        .max()
        .unwrap_or(0)
}

pub fn render(spec: &Spec) -> Result<String, String> {
    let style = style::line_style(&spec.style)?;
    let colors = &style.colors;
    if spec.x.len() < 2 {
        return Err(format!(
            "a line chart needs at least two x values, got {}",
            spec.x.len()
        ));
    }
    if let Some(index) = spec
        .y_series
        .iter()
        .position(|series| series.len() != spec.x.len())
    {
        return Err(format!(
            "series {index} has {} values but there are {} x values",
            spec.y_series[index].len(),
            spec.x.len()
        ));
    }
    let series_colors: Vec<String> = match &spec.colors {
        Some(given) if given.len() < spec.y_series.len() => {
            return Err(format!(
                "{} colors given for {} series",
                given.len(),
                spec.y_series.len()
            ));
        }
        Some(given) => given.clone(),
        None => (0..spec.y_series.len())
            .map(|index| colors.series_color(index).to_string())
            .collect(),
    };
    let labels = spec.labels.clone().unwrap_or_default();
    let mut svg = chart_frame(spec.width, spec.height, &colors["background"]);
    let chart_y = render_title_and_legend(
        &mut svg,
        spec.title.as_deref().unwrap_or("Line Chart"),
        &labels,
        colors,
        PADDING_X,
        PADDING_Y,
        TITLE_GAP,
        CHART_TOP_MARGIN,
        LegendFills::Given {
            fills: &series_colors,
            extra: None,
        },
    )?;
    let chart_x = PADDING_X;
    let chart_width = spec.width - 2.0 * PADDING_X;
    let chart_height = spec.height - chart_y - X_LABEL_ROOM;
    let step = chart_width / (spec.x.len() - 1) as f64;
    let digits = precision(&spec.x);
    for (index, value) in spec.x.iter().enumerate() {
        let x = chart_x + index as f64 * step;
        svg.child(
            Element::new("line")
                .attr("x1", x)
                .attr("y1", chart_y)
                .attr("x2", x)
                .attr("y2", chart_y + chart_height)
                .attr("stroke", &colors["grid"])
                .attr("stroke-width", "1")
                .attr("stroke-dasharray", VERTICAL_DASH),
        );
        svg.child(
            Element::new("text")
                .attr("x", x)
                .attr("y", chart_y + chart_height + X_LABEL_OFFSET)
                .attr("fill", &colors["legend_text"])
                .attr("font-size", TICK_SIZE)
                .attr("font-weight", "400")
                .attr("text-anchor", "start")
                .text(format!("{value:.digits$}")),
        );
    }
    for band in 0..=HORIZONTAL_BANDS {
        let y = chart_y + f64::from(band) * chart_height / f64::from(HORIZONTAL_BANDS);
        svg.child(
            Element::new("line")
                .attr("x1", chart_x)
                .attr("y1", y)
                .attr("x2", chart_x + chart_width)
                .attr("y2", y)
                .attr("stroke", &colors["grid"])
                .attr("stroke-width", "1"),
        );
    }
    let (low, high) = spec
        .y_series
        .iter()
        .flatten()
        .fold((f64::MAX, f64::MIN), |(low, high), value| {
            (low.min(*value), high.max(*value))
        });
    let range = if high == low { 1.0 } else { high - low };
    for (index, series) in spec.y_series.iter().enumerate() {
        let color = &series_colors[index];
        let points: Vec<(f64, f64)> = series
            .iter()
            .enumerate()
            .map(|(position, value)| {
                (
                    chart_x + position as f64 * step,
                    chart_y + chart_height - (value - low) / range * chart_height,
                )
            })
            .collect();
        let path: Vec<String> = points
            .iter()
            .enumerate()
            .map(|(position, (x, y))| format!("{} {x},{y}", if position == 0 { "M" } else { "L" }))
            .collect();
        svg.child(
            Element::new("path")
                .attr("d", path.join(" "))
                .attr("stroke", color)
                .attr("stroke-width", spec.line_width)
                .attr("fill", "none")
                .attr("stroke-linecap", "round")
                .attr("stroke-linejoin", "round"),
        );
        if let Some(marker) = style.markers.get(index % style.markers.len().max(1)) {
            for (x, y) in &points {
                render_marker(&mut svg, *x, *y, *marker, color, MARKER_SIZE);
            }
        }
    }
    Ok(svg.render())
}
