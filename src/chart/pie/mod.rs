//! Donut pie charts with a legend and a centre total.
//!
//! ```json
//! {"kind": "pie", "style": 1, "width": 328, "height": 328,
//!  "values": [25, 20, 15], "labels": ["One", "Two", "Three"],
//!  "title": "Pie chart", "center_label": "Total"}
//! ```
//! `center_value` defaults to the whole-number sum of `values`.

use serde::Deserialize;

use super::parts::element::{chart_frame, Element};
use super::parts::legend::text_width;
use super::parts::Colors;
use crate::brand::brand_color;

/// The design's padding, title and legend bands.
const PADDING: f64 = 16.0;
const TITLE_HEIGHT: f64 = 36.0;
const LEGEND_HEIGHT: f64 = 24.0;
const TITLE_SIZE: f64 = 16.0;
/// The design's legend: 8 px swatches, 1 px radius, 10 px labels 4 px after, 8 px apart.
const SWATCH: f64 = 8.0;
const SWATCH_RADIUS: f64 = 1.0;
const LABEL_SIZE: f64 = 10.0;
const LABEL_GAP: f64 = 4.0;
const ENTRY_GAP: f64 = 8.0;
const LEGEND_OFFSET: f64 = 20.0;
const LABEL_BASELINE: f64 = 7.0;
/// The design's donut: inner radius 55 % of the outer, 2 px separators.
const INNER_RADIUS_RATIO: f64 = 0.55;
const SEPARATOR_WIDTH: f64 = 2.0;
/// The design's centre text: a 12 px label above a 16 px value, 8 px from the centre.
const CENTER_LABEL_SIZE: f64 = 12.0;
const CENTER_VALUE_SIZE: f64 = 16.0;
const CENTER_OFFSET: f64 = 8.0;

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Spec {
    /// 1 brand colours, 2 black and grey, 3 white.
    pub style: u32,
    pub width: f64,
    pub height: f64,
    pub values: Vec<f64>,
    pub labels: Vec<String>,
    #[serde(default)]
    pub title: Option<String>,
    #[serde(default)]
    pub center_label: Option<String>,
    #[serde(default)]
    pub center_value: Option<String>,
}

fn brand(role: &str) -> &'static str {
    brand_color(role).unwrap_or_default()
}

/// The brand, black/grey and white designs.
fn colors(style: u32) -> Result<Colors, String> {
    let (background, title, legend, center, separator, slices) = match style {
        1 => (
            brand("surface"),
            brand("primary"),
            brand("muted"),
            "#FFFFFF",
            "#000000",
            [brand("primary"), "#FA5A46", "#FFB366", "#FFD699", "#B19ECC", "#A4C2F4"],
        ),
        2 => (
            brand("surface"),
            "#FFFFFF",
            "#A9A9A9",
            "#FFFFFF",
            "#000000",
            ["#FFFFFF", "#E0E0E0", "#C8C8C8", "#A9A9A9", "#909090", "#787878"],
        ),
        3 => (
            "#FFFFFF",
            "#000000",
            "#666666",
            "#000000",
            "#FFFFFF",
            ["#303030", "#484848", "#606060", "#787878", "#909090", "#C8C8C8"],
        ),
        other => return Err(format!("Pie style must be 1 (brand), 2 (black) or 3 (white), got {other}")),
    };
    Ok(Colors::new(
        &[
            ("background", background),
            ("title", title),
            ("legend_text", legend),
            ("center_text", center),
            ("separator", separator),
        ],
        &slices,
    ))
}

/// Slice `index`'s colour; a slice past the palette takes the first.
fn slice_color(colors: &Colors, index: usize) -> &str {
    colors.series().get(index).unwrap_or(&colors.series()[0])
}

fn text(x: f64, y: f64, fill: &str, size: f64, content: &str) -> Element {
    Element::new("text").attr("x", x).attr("y", y).attr("fill", fill).attr("font-size", size).attr("font-weight", "400").text(content)
}

fn legend(svg: &mut Element, colors: &Colors, labels: &[String], values: &[f64]) -> Result<(), String> {
    let legend_y = PADDING + LEGEND_OFFSET;
    let mut legend_x = PADDING;
    for (index, label) in labels.iter().take(values.len()).enumerate() {
        svg.child(
            Element::new("rect")
                .attr("x", legend_x)
                .attr("y", legend_y)
                .attr("width", SWATCH)
                .attr("height", SWATCH)
                .attr("fill", slice_color(colors, index))
                .attr("rx", SWATCH_RADIUS)
                .attr("ry", SWATCH_RADIUS),
        );
        svg.child(text(legend_x + SWATCH + LABEL_GAP, legend_y + LABEL_BASELINE, &colors["legend_text"], LABEL_SIZE, label));
        legend_x += SWATCH + LABEL_GAP + text_width(label, LABEL_SIZE)? + ENTRY_GAP;
    }
    Ok(())
}

/// One donut slice from `start` sweeping `sweep` degrees clockwise.
fn slice(cx: f64, cy: f64, outer: f64, inner: f64, start: f64, sweep: f64) -> String {
    let (start_rad, end_rad) = (start.to_radians(), (start + sweep).to_radians());
    let point = |radius: f64, angle: f64| (cx + radius * angle.cos(), cy + radius * angle.sin());
    let (ox1, oy1) = point(outer, start_rad);
    let (ox2, oy2) = point(outer, end_rad);
    let (ix1, iy1) = point(inner, start_rad);
    let (ix2, iy2) = point(inner, end_rad);
    let large = u8::from(sweep > 180.0);
    format!(
        "M {ox1},{oy1}\n            A {outer},{outer} 0 {large} 1 {ox2},{oy2}\n            L {ix2},{iy2}\n            A {inner},{inner} 0 {large} 0 {ix1},{iy1}\n            Z"
    )
}

pub fn render(spec: &Spec) -> Result<String, String> {
    let colors = colors(spec.style)?;
    let mut svg = chart_frame(spec.width, spec.height, &colors["background"]);
    svg.child(text(PADDING, PADDING + TITLE_SIZE, &colors["title"], TITLE_SIZE, spec.title.as_deref().unwrap_or("Pie chart")));
    legend(&mut svg, &colors, &spec.labels, &spec.values)?;
    let center_y = TITLE_HEIGHT + LEGEND_HEIGHT + ((spec.height - TITLE_HEIGHT - LEGEND_HEIGHT) / 2.0).floor();
    let center_x = (spec.width / 2.0).floor();
    let total: f64 = spec.values.iter().sum();
    if total != 0.0 {
        let available_height = spec.height - TITLE_HEIGHT - LEGEND_HEIGHT - PADDING * 2.0;
        let outer = available_height.min(spec.width - PADDING * 2.0) / 2.0;
        let inner = outer * INNER_RADIUS_RATIO;
        // Clockwise from twelve o'clock.
        let mut start = -90.0;
        for (index, value) in spec.values.iter().enumerate().filter(|(_, value)| **value > 0.0) {
            let sweep = value / total * 360.0;
            svg.child(
                Element::new("path")
                    .attr("d", slice(center_x, center_y, outer, inner, start, sweep))
                    .attr("fill", slice_color(&colors, index))
                    .attr("stroke", &colors["separator"])
                    .attr("stroke-width", SEPARATOR_WIDTH),
            );
            start += sweep;
        }
    }
    let center_value = spec.center_value.clone().unwrap_or_else(|| total.trunc().to_string());
    let label = spec.center_label.as_deref().unwrap_or("Total");
    svg.child(text(center_x, center_y - CENTER_OFFSET, &colors["center_text"], CENTER_LABEL_SIZE, label).attr("text-anchor", "middle"));
    svg.child(text(center_x, center_y + CENTER_OFFSET, &colors["center_text"], CENTER_VALUE_SIZE, &center_value).attr("text-anchor", "middle"));
    Ok(svg.render())
}
