//! Chart title, legends and markers, shared by every chart family.
//!
//! Sizes are the Figma design's: a 20 px title, 20 x 10 px legend swatches
//! with a 2 px corner radius, 14 px legend labels 8 px after the swatch and
//! 20 px between entries. A legend entry's width is its label measured in
//! the bundled Hubot Sans at the size it is drawn, not a per-character guess.

use std::sync::LazyLock;

use fontdue::{Font, FontSettings};

use super::element::Element;
use super::Colors;
use crate::brand::REGULAR_TTF;

const TITLE_SIZE: f64 = 20.0;
const SWATCH_WIDTH: f64 = 20.0;
const SWATCH_HEIGHT: f64 = 10.0;
const SWATCH_RADIUS: f64 = 2.0;
const LABEL_SIZE: f64 = 14.0;
const BUBBLE_LABEL_SIZE: f64 = 12.0;
const LABEL_GAP: f64 = 8.0;
const ENTRY_GAP: f64 = 20.0;
const LEGEND_GAP: f64 = 4.0;
const LEGEND_HEIGHT: f64 = 24.0;
const LABEL_BASELINE: f64 = 9.0;
const BUBBLE_LEGEND_OFFSET: f64 = 36.0;

static REGULAR: LazyLock<Result<Font, String>> = LazyLock::new(|| {
    Font::from_bytes(REGULAR_TTF, FontSettings::default())
        .map_err(|error| format!("the bundled HubotSans-Regular.ttf does not load: {error}"))
});

/// The advance width of `text` set in Hubot Sans Regular at `size` px.
pub fn text_width(text: &str, size: f64) -> Result<f64, String> {
    let font = REGULAR.as_ref().map_err(Clone::clone)?;
    Ok(text
        .chars()
        .map(|character| f64::from(font.metrics(character, size as f32).advance_width))
        .sum())
}

pub fn render_title(
    svg: &mut Element,
    title: &str,
    colors: &Colors,
    padding_x: f64,
    padding_y: f64,
) {
    svg.child(
        Element::new("text")
            .attr("x", padding_x)
            .attr("y", padding_y + TITLE_SIZE)
            .attr("fill", &colors["title"])
            .attr("font-size", TITLE_SIZE)
            .attr("font-weight", "400")
            .text(title),
    );
}

fn swatch(svg: &mut Element, x: f64, y: f64, fill: &str) {
    svg.child(
        Element::new("rect")
            .attr("x", x)
            .attr("y", y)
            .attr("width", SWATCH_WIDTH)
            .attr("height", SWATCH_HEIGHT)
            .attr("fill", fill)
            .attr("rx", SWATCH_RADIUS)
            .attr("ry", SWATCH_RADIUS),
    );
}

fn label(svg: &mut Element, x: f64, y: f64, colors: &Colors, size: f64, text: &str) {
    svg.child(
        Element::new("text")
            .attr("x", x + SWATCH_WIDTH + LABEL_GAP)
            .attr("y", y + LABEL_BASELINE)
            .attr("fill", &colors["legend_text"])
            .attr("font-size", size)
            .attr("font-weight", "400")
            .text(text),
    );
}

/// Where the legend's fills come from.
pub enum LegendFills<'a> {
    /// The theme's series colours, cycled.
    Theme,
    /// One fill per series (a colour or a `url(#pattern)`); a series past the end uses `extra`.
    Given {
        fills: &'a [String],
        extra: Option<&'a str>,
    },
}

/// Title, then a one-line legend under it; returns the y where the chart area starts.
#[allow(clippy::too_many_arguments)]
pub fn render_title_and_legend(
    svg: &mut Element,
    title: &str,
    labels: &[String],
    colors: &Colors,
    padding_x: f64,
    padding_y: f64,
    title_gap: f64,
    chart_top_margin: f64,
    fills: LegendFills,
) -> Result<f64, String> {
    render_title(svg, title, colors, padding_x, padding_y);
    let legend_y = padding_y + TITLE_SIZE + title_gap + LEGEND_GAP;
    let mut legend_x = padding_x;
    for (index, text) in labels.iter().enumerate() {
        let fill = match &fills {
            LegendFills::Theme => colors.series_color(index),
            LegendFills::Given { fills, extra } => fills
                .get(index)
                .map(String::as_str)
                .or(*extra)
                .unwrap_or_default(),
        };
        swatch(svg, legend_x, legend_y, fill);
        label(svg, legend_x, legend_y, colors, LABEL_SIZE, text);
        legend_x += SWATCH_WIDTH + LABEL_GAP + text_width(text, LABEL_SIZE)? + ENTRY_GAP;
    }
    Ok(padding_y + TITLE_SIZE + title_gap + LEGEND_HEIGHT + chart_top_margin)
}

/// The bubble legend: entry `i` takes the series colour of its category (from
/// `category_indices`, else its own position), the last one past the palette.
pub fn render_bubble_legend(
    svg: &mut Element,
    labels: &[String],
    colors: &Colors,
    padding_x: f64,
    padding_y: f64,
    category_indices: Option<&[usize]>,
) -> Result<(), String> {
    let legend_y = padding_y + BUBBLE_LEGEND_OFFSET;
    let mut legend_x = padding_x;
    for (index, text) in labels.iter().enumerate() {
        let category = category_indices
            .and_then(|indices| indices.get(index).copied())
            .unwrap_or(index);
        swatch(svg, legend_x, legend_y, colors.series_or_last(category));
        label(svg, legend_x, legend_y, colors, BUBBLE_LABEL_SIZE, text);
        legend_x += SWATCH_WIDTH + LABEL_GAP + text_width(text, BUBBLE_LABEL_SIZE)? + ENTRY_GAP;
    }
    Ok(())
}

/// A marker shape the line and radar charts draw at data points.
#[derive(Clone, Copy, Debug, PartialEq, Eq, serde::Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Marker {
    Circle,
    Square,
    Diamond,
    Triangle,
}

/// Draw `marker` of side `size` centred on (`x`, `y`).
pub fn render_marker(svg: &mut Element, x: f64, y: f64, marker: Marker, color: &str, size: f64) {
    let half = size / 2.0;
    match marker {
        Marker::Circle => {
            svg.child(
                Element::new("circle")
                    .attr("cx", x)
                    .attr("cy", y)
                    .attr("r", half)
                    .attr("fill", color),
            );
        }
        Marker::Square => {
            svg.child(
                Element::new("rect")
                    .attr("x", x - half)
                    .attr("y", y - half)
                    .attr("width", size)
                    .attr("height", size)
                    .attr("fill", color)
                    .attr("rx", SWATCH_RADIUS)
                    .attr("ry", SWATCH_RADIUS),
            );
        }
        Marker::Diamond => {
            let points = format!(
                "{x},{} {},{y} {x},{} {},{y}",
                y - half,
                x + half,
                y + half,
                x - half
            );
            svg.child(
                Element::new("polygon")
                    .attr("points", points)
                    .attr("fill", color),
            );
        }
        Marker::Triangle => {
            // Equilateral, side `size`, pointing up, centred on its centroid.
            let height = half * 3f64.sqrt();
            let points = format!(
                "{x},{} {},{} {},{}",
                y - height * 2.0 / 3.0,
                x + half,
                y + height / 3.0,
                x - half,
                y + height / 3.0
            );
            svg.child(
                Element::new("polygon")
                    .attr("points", points)
                    .attr("fill", color),
            );
        }
    }
}
