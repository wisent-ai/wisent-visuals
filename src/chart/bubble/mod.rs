//! Bubble charts: points sized by a third value and coloured by category,
//! on cartesian axes or on a radar of angles and distances.
//!
//! ```json
//! {"kind": "bubble", "style": "brand", "width": 456, "height": 383,
//!  "chart": {"type": "bubble", "x_data": [10, 20, 30], "y_data": [100, 200, 300]},
//!  "sizes": [10, 20, 30], "categories": [0, 1, 0], "category_labels": ["A", "B"],
//!  "title": "Bubble Chart"}
//! ```
//! A radar bubble chart takes `"chart": {"type": "radar", "angles": [0, 90],
//! "distances": [40, 80]}` (degrees clockwise from twelve o'clock, 0–100).

mod cartesian;
mod radar;

use std::collections::BTreeSet;

use serde::Deserialize;

use super::parts::element::{chart_frame, Element};
use super::parts::legend::{render_bubble_legend, render_title};
use super::parts::{Colors, StyleChoice};
use crate::brand::brand_color;

/// The design's card padding.
const PADDING_X: f64 = 32.0;
const PADDING_Y: f64 = 16.0;
/// The design's bubbles: 70 % opaque.
const BUBBLE_OPACITY: f64 = 0.7;

const STYLE_NAMES: [(&str, u32); 3] = [("brand", 1), ("black", 2), ("white", 3)];

#[derive(Debug, Deserialize)]
#[serde(tag = "type", rename_all = "lowercase", deny_unknown_fields)]
pub enum Layout {
    Bubble { x_data: Vec<f64>, y_data: Vec<f64> },
    Radar { angles: Vec<f64>, distances: Vec<f64> },
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Spec {
    /// 1 brand colours (dark), 2 black (greyscale), 3 white; or the style's name.
    pub style: StyleChoice,
    pub width: f64,
    pub height: f64,
    pub chart: Layout,
    pub sizes: Vec<f64>,
    /// Each point's category, an index into `category_labels` and the palette.
    #[serde(default)]
    pub categories: Option<Vec<usize>>,
    #[serde(default)]
    pub category_labels: Option<Vec<String>>,
    #[serde(default)]
    pub title: Option<String>,
}

fn brand(role: &str) -> &'static str {
    brand_color(role).unwrap_or_default()
}

/// The brand, black and white designs; the series palette is the nine bubble colours.
fn colors(style: u32) -> Result<Colors, String> {
    let (background, title, grid, legend, bubbles) = match style {
        1 => (brand("surface"), brand("primary"), brand("grid"), brand("muted"), ["#FA5A46", "#FF8C00", "#FFD700", brand("primary"), "#00CED1", "#87CEEB", "#B19ECC", "#FFB6C1", "#A9A9A9"]),
        2 => (brand("surface"), "#FFFFFF", brand("grid"), "#A9A9A9", ["#FFFFFF", "#E0E0E0", "#C8C8C8", "#A9A9A9", "#909090", "#787878", "#606060", "#484848", "#303030"]),
        3 => ("#FFFFFF", "#000000", "#E5E5E5", "#666666", ["#FA5A46", "#FF8C00", "#FFD700", "#00C896", "#00CED1", "#87CEEB", "#B19ECC", "#FFB6C1", "#666666"]),
        other => return Err(format!("Bubble style must be 1 (brand), 2 (black) or 3 (white), got {other}")),
    };
    Ok(Colors::new(
        &[("background", background), ("title", title), ("legend_text", legend), ("grid", grid), ("axis_text", legend), ("axis_line", "#4A4A4A")],
        &bubbles,
    ))
}

/// A point's fill: its category's colour, the first colour without categories.
fn point_color<'a>(colors: &'a Colors, categories: Option<&[usize]>, index: usize) -> &'a str {
    match categories.and_then(|categories| categories.get(index)) {
        Some(category) => colors.series_or_last(*category),
        None => colors.series_or_last(0),
    }
}

/// `value`'s place between `low` and `high`, the middle when they are equal.
fn share(value: f64, low: f64, high: f64) -> f64 {
    if high == low { 0.5 } else { (value - low) / (high - low) }
}

/// The bounds of `values`.
fn bounds(values: &[f64]) -> (f64, f64) {
    values.iter().fold((f64::MAX, f64::MIN), |(low, high), value| (low.min(*value), high.max(*value)))
}

fn bubble(x: f64, y: f64, radius: f64, fill: &str) -> Element {
    Element::new("circle").attr("cx", x).attr("cy", y).attr("r", radius).attr("fill", fill).attr("opacity", BUBBLE_OPACITY)
}

fn text(x: f64, y: f64, fill: &str, size: f64, anchor: &str, content: &str) -> Element {
    Element::new("text")
        .attr("x", x)
        .attr("y", y)
        .attr("fill", fill)
        .attr("font-size", size)
        .attr("font-weight", "400")
        .attr("text-anchor", anchor)
        .text(content)
}

/// The legend lists only the categories the points use, in category order.
fn legend(svg: &mut Element, spec: &Spec, colors: &Colors) -> Result<(), String> {
    let Some(labels) = spec.category_labels.as_ref().filter(|labels| !labels.is_empty()) else { return Ok(()) };
    match spec.categories.as_ref().filter(|categories| !categories.is_empty()) {
        Some(categories) => {
            let used: Vec<usize> = categories.iter().copied().collect::<BTreeSet<_>>().into_iter().collect();
            let shown: Vec<String> = used.iter().filter_map(|category| labels.get(*category).cloned()).collect();
            render_bubble_legend(svg, &shown, colors, PADDING_X, PADDING_Y, Some(&used))
        }
        None => render_bubble_legend(svg, labels, colors, PADDING_X, PADDING_Y, None),
    }
}

pub fn render(spec: &Spec) -> Result<String, String> {
    let colors = colors(spec.style.resolve(&STYLE_NAMES)?)?;
    let points = match &spec.chart {
        Layout::Bubble { x_data, y_data } => (x_data.len(), y_data.len()),
        Layout::Radar { angles, distances } => (angles.len(), distances.len()),
    };
    if points.0 != points.1 || points.0 != spec.sizes.len() || spec.sizes.is_empty() {
        return Err(format!(
            "a bubble chart needs one position pair and one size per point, got {} and {} positions and {} sizes",
            points.0,
            points.1,
            spec.sizes.len()
        ));
    }
    let mut svg = chart_frame(spec.width, spec.height, &colors["background"]);
    let default_title = match spec.chart {
        Layout::Bubble { .. } => "Bubble Chart",
        Layout::Radar { .. } => "Bubble Radar chart",
    };
    render_title(&mut svg, spec.title.as_deref().unwrap_or(default_title), &colors, PADDING_X, PADDING_Y);
    legend(&mut svg, spec, &colors)?;
    let categories = spec.categories.as_deref();
    match &spec.chart {
        Layout::Bubble { x_data, y_data } => cartesian::draw(&mut svg, spec, &colors, x_data, y_data, categories),
        Layout::Radar { angles, distances } => radar::draw(&mut svg, spec, &colors, angles, distances, categories),
    }
    Ok(svg.render())
}
