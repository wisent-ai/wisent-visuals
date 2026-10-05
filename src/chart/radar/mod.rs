//! Radar charts: each series a filled polygon over one axis per value, on a
//! 0–100 scale.
//!
//! ```json
//! {"kind": "radar", "style": 1, "width": 328, "height": 328,
//!  "data_series": [[80, 60, 70, 90, 50, 65, 75, 85], [40, 70, 55, 60, 80, 45, 50, 65]],
//!  "labels": ["One", "Two"], "title": "Radar chart"}
//! ```
//! There are as many axes as each series has values; `axis_labels` defaults
//! to each axis's angle in degrees.

use serde::Deserialize;

use super::parts::element::{chart_frame, Element};
use super::parts::legend::text_width;
use super::parts::Colors;
use crate::brand::brand_color;

/// The design's padding and title band, title size and legend geometry.
const PADDING: f64 = 16.0;
const TITLE_HEIGHT: f64 = 36.0;
const TITLE_SIZE: f64 = 16.0;
const SWATCH: f64 = 8.0;
const SWATCH_RADIUS: f64 = 1.0;
const LABEL_SIZE: f64 = 10.0;
const LABEL_GAP: f64 = 4.0;
const ENTRY_GAP: f64 = 8.0;
const LEGEND_OFFSET: f64 = 20.0;
const LABEL_BASELINE: f64 = 7.0;
/// The design's grid: five rings at 30 % opacity, axes at 50 %, ring values 5 px above.
const RINGS: u32 = 5;
const RING_OPACITY: f64 = 0.3;
const AXIS_OPACITY: f64 = 0.5;
const RING_LABEL_GAP: f64 = 5.0;
/// The design's axis labels: 20 px past the axis end, centred within 10 px of the middle.
const AXIS_LABEL_DISTANCE: f64 = 20.0;
const AXIS_LABEL_CENTRE_BAND: f64 = 10.0;
const AXIS_LABEL_BASELINE: f64 = 4.0;
const AXIS_LABEL_SIZE: f64 = 12.0;
/// The design's series: 60 % fill, 2 px stroke at 80 %.
const FILL_OPACITY: f64 = 0.6;
const STROKE_WIDTH: f64 = 2.0;
const STROKE_OPACITY: f64 = 0.8;
/// The scale a value is read on.
const FULL_SCALE: f64 = 100.0;

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Spec {
    /// 1 brand colours, 2 black and grey, 3 white.
    pub style: u32,
    pub width: f64,
    pub height: f64,
    pub data_series: Vec<Vec<f64>>,
    pub labels: Vec<String>,
    #[serde(default)]
    pub axis_labels: Option<Vec<String>>,
    #[serde(default)]
    pub title: Option<String>,
}

fn brand(role: &str) -> &'static str {
    brand_color(role).unwrap_or_default()
}

/// The brand, black and white designs: the theme's colours, the series fills
/// as its palette, and the matching strokes.
fn theme(style: u32) -> Result<(Colors, [&'static str; 2]), String> {
    let (background, title, legend, axis_text, grid, axis, fills, strokes) = match style {
        1 => (brand("surface"), brand("primary"), brand("muted"), "#A9A9A9", brand("grid"), "#4A4A4A", [brand("tertiary"), "#FA5A46"], [brand("deep"), "#D94435"]),
        2 => (brand("surface"), "#FFFFFF", "#A9A9A9", "#A9A9A9", brand("grid"), "#4A4A4A", ["#C8C8C8", "#606060"], ["#909090", "#303030"]),
        3 => ("#FFFFFF", "#000000", "#666666", "#666666", "#E5E5E5", "#CCCCCC", ["#484848", "#909090"], ["#303030", "#606060"]),
        other => return Err(format!("Radar style must be 1 (brand), 2 (black) or 3 (white), got {other}")),
    };
    let colors = Colors::new(
        &[("background", background), ("title", title), ("legend_text", legend), ("axis_text", axis_text), ("grid", grid), ("axis", axis)],
        &fills,
    );
    Ok((colors, strokes))
}

fn text(x: f64, y: f64, fill: &str, size: f64, content: &str) -> Element {
    Element::new("text").attr("x", x).attr("y", y).attr("fill", fill).attr("font-size", size).attr("font-weight", "400").text(content)
}

/// The angle of axis `index` of `axes`, clockwise from twelve o'clock.
fn angle(index: usize, axes: usize) -> f64 {
    (index as f64 * 360.0 / axes as f64 - 90.0).to_radians()
}

pub fn render(spec: &Spec) -> Result<String, String> {
    let (colors, strokes) = theme(spec.style)?;
    let axes = spec.data_series.first().map(Vec::len).unwrap_or_default();
    if axes == 0 {
        return Err("a radar chart needs at least one series with at least one value".to_string());
    }
    if let Some(index) = spec.data_series.iter().position(|series| series.len() != axes) {
        return Err(format!("series {index} has {} values but series 0 has {axes}", spec.data_series[index].len()));
    }
    let mut svg = chart_frame(spec.width, spec.height, &colors["background"]);
    svg.child(text(PADDING, PADDING + TITLE_SIZE, &colors["title"], TITLE_SIZE, spec.title.as_deref().unwrap_or("Radar chart")));
    let legend_y = PADDING + LEGEND_OFFSET;
    let mut legend_x = PADDING;
    for (index, label) in spec.labels.iter().enumerate() {
        svg.child(
            Element::new("rect")
                .attr("x", legend_x)
                .attr("y", legend_y)
                .attr("width", SWATCH)
                .attr("height", SWATCH)
                .attr("fill", colors.series_or_last(index))
                .attr("opacity", FILL_OPACITY)
                .attr("rx", SWATCH_RADIUS)
                .attr("ry", SWATCH_RADIUS),
        );
        svg.child(text(legend_x + SWATCH + LABEL_GAP, legend_y + LABEL_BASELINE, &colors["legend_text"], LABEL_SIZE, label));
        legend_x += SWATCH + LABEL_GAP + text_width(label, LABEL_SIZE)? + ENTRY_GAP;
    }
    let available_height = spec.height - TITLE_HEIGHT - PADDING * 2.0;
    let max_radius = available_height.min(spec.width - PADDING * 2.0) / 2.0;
    let (cx, cy) = (spec.width / 2.0, TITLE_HEIGHT + available_height / 2.0);
    for ring in 1..=RINGS {
        let share = f64::from(ring) / f64::from(RINGS);
        let radius = share * max_radius;
        svg.child(
            Element::new("circle")
                .attr("cx", cx)
                .attr("cy", cy)
                .attr("r", radius)
                .attr("fill", "none")
                .attr("stroke", &colors["grid"])
                .attr("stroke-width", "1")
                .attr("opacity", RING_OPACITY),
        );
        svg.child(text(cx, cy - radius - RING_LABEL_GAP, &colors["axis_text"], LABEL_SIZE, &(share * FULL_SCALE).trunc().to_string()).attr("text-anchor", "middle"));
    }
    let default_labels: Vec<String> = (0..axes).map(|index| (index * 360 / axes).to_string()).collect();
    let axis_labels = spec.axis_labels.as_ref().unwrap_or(&default_labels);
    for index in 0..axes {
        let theta = angle(index, axes);
        svg.child(
            Element::new("line")
                .attr("x1", cx)
                .attr("y1", cy)
                .attr("x2", cx + max_radius * theta.cos())
                .attr("y2", cy + max_radius * theta.sin())
                .attr("stroke", &colors["axis"])
                .attr("stroke-width", "1")
                .attr("opacity", AXIS_OPACITY),
        );
        if let Some(label) = axis_labels.get(index) {
            let distance = max_radius + AXIS_LABEL_DISTANCE;
            let (x, y) = (cx + distance * theta.cos(), cy + distance * theta.sin());
            let anchor = if x < cx - AXIS_LABEL_CENTRE_BAND {
                "end"
            } else if x > cx + AXIS_LABEL_CENTRE_BAND {
                "start"
            } else {
                "middle"
            };
            svg.child(text(x, y + AXIS_LABEL_BASELINE, &colors["axis_text"], AXIS_LABEL_SIZE, label).attr("text-anchor", anchor));
        }
    }
    for (index, series) in spec.data_series.iter().enumerate() {
        let points: Vec<String> = series
            .iter()
            .enumerate()
            .map(|(axis, value)| {
                let (theta, distance) = (angle(axis, axes), value / FULL_SCALE * max_radius);
                format!("{},{}", cx + distance * theta.cos(), cy + distance * theta.sin())
            })
            .collect();
        svg.child(
            Element::new("polygon")
                .attr("points", points.join(" "))
                .attr("fill", colors.series_or_last(index))
                .attr("fill-opacity", FILL_OPACITY)
                .attr("stroke", strokes[index.min(strokes.len() - 1)])
                .attr("stroke-width", STROKE_WIDTH)
                .attr("stroke-opacity", STROKE_OPACITY),
        );
    }
    Ok(svg.render())
}
