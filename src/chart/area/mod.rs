//! Stacked area charts in the five Figma designs: 1 edge (one green at three
//! opacities), 2 gradient, 3 pattern, 4 two patterns, 5 solid colours.
//!
//! ```json
//! {"kind": "area", "style": "gradient", "width": 1002, "height": 499,
//!  "x": [1, 2, 3, 4], "y_series": [[5, 6, 7, 6], [3, 4, 3, 5], [2, 2, 3, 2]],
//!  "labels": ["One", "Two", "Three"], "title": "Area Chart"}
//! ```
//! Every design stacks exactly three bands, bottom to top in `y_series`
//! order. Each x value gets a dashed grid line and its own label.

use serde::Deserialize;

use super::parts::assets::{load_pattern, Pattern};
use super::parts::element::{chart_frame, Element};
use super::parts::legend::{render_title_and_legend, LegendFills};
use super::parts::{Colors, StyleChoice};
use crate::brand::brand_color;

/// The design's card padding, title gap and chart top margin.
const PADDING_X: f64 = 32.0;
const PADDING_Y: f64 = 16.0;
const TITLE_GAP: f64 = 10.0;
const CHART_TOP_MARGIN: f64 = 24.0;
/// The design's room under the bands for the x labels, and their baseline above the bottom.
const X_LABEL_ROOM: f64 = 40.0;
const X_LABEL_RISE: f64 = 10.0;
const TICK_SIZE: f64 = 14.0;
const GRID_DASH: &str = "4,4";
/// The design stacks three bands.
const BANDS: usize = 3;
/// The edge design's band opacities, bottom to top.
const EDGE_OPACITY: [f64; BANDS] = [1.0, 0.5, 0.4];
/// The gradient design's stops per band, bottom to top: (id, at the bottom, at the top).
const GRADIENTS: [(&str, &str, &str); BANDS] =
    [("grad-bottom", "#C5FFC8", "#7FA682"), ("grad-middle", "#90B892", "#5F7861"), ("grad-top", "#5A715B", "#3D4D3E")];
const CLIP_ID: &str = "chart-clip";

const STYLE_NAMES: [(&str, u32); 5] = [("solid", 1), ("gradient", 2), ("pattern", 3), ("2patterns", 4), ("minimal", 5)];

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Spec {
    pub style: StyleChoice,
    pub width: f64,
    pub height: f64,
    pub x: Vec<f64>,
    pub y_series: Vec<Vec<f64>>,
    #[serde(default)]
    pub labels: Option<Vec<String>>,
    #[serde(default)]
    pub title: Option<String>,
}

fn brand(role: &str) -> &'static str {
    brand_color(role).unwrap_or_default()
}

/// The card colours every design shares, with the legend palette `series`.
fn colors(series: &[&str]) -> Colors {
    Colors::new(
        &[("background", brand("surface")), ("title", brand("primary")), ("legend_text", brand("muted")), ("grid", brand("grid"))],
        series,
    )
}

/// A design: its colours, legend swatches, band fills and opacities, and
/// whether the top band is painted first.
struct Design {
    colors: Colors,
    legend: Vec<String>,
    fills: [String; BANDS],
    opacity: Option<[f64; BANDS]>,
    top_first: bool,
}

fn url(id: &str) -> String {
    format!("url(#{id})")
}

/// The design of `style`, its gradients and patterns added to `defs`.
fn design(style: u32, defs: &mut Element) -> Result<Design, String> {
    let greens = colors(&[brand("secondary"), brand("tertiary"), brand("deep")]);
    let area = brand("primary").to_string();
    Ok(match style {
        1 => {
            let legend = greens.series().to_vec();
            Design { legend, colors: greens, fills: [area.clone(), area.clone(), area], opacity: Some(EDGE_OPACITY), top_first: true }
        }
        2 => {
            for (id, bottom, top) in GRADIENTS {
                let gradient = defs.child(
                    Element::new("linearGradient").attr("id", id).attr("x1", "0%").attr("y1", "100%").attr("x2", "0%").attr("y2", "0%"),
                );
                gradient.child(Element::new("stop").attr("offset", "0%").attr("style", format!("stop-color:{bottom};stop-opacity:1")));
                gradient.child(Element::new("stop").attr("offset", "100%").attr("style", format!("stop-color:{top};stop-opacity:1")));
            }
            let fills = GRADIENTS.map(|(id, _, _)| url(id));
            Design { legend: fills.to_vec(), colors: greens, fills, opacity: None, top_first: true }
        }
        3 => {
            load_pattern(defs, "pattern-middle", Pattern::CrossingLines)?;
            load_pattern(defs, "pattern-top", Pattern::NoiseLarge)?;
            let fills = [area, url("pattern-middle"), url("pattern-top")];
            Design { legend: fills.to_vec(), colors: greens, fills, opacity: None, top_first: true }
        }
        4 => {
            load_pattern(defs, "pattern-bottom", Pattern::VerticalLines)?;
            load_pattern(defs, "pattern-middle", Pattern::DiagonalLines)?;
            load_pattern(defs, "pattern-top", Pattern::DitherLarge)?;
            let fills = [url("pattern-bottom"), url("pattern-middle"), url("pattern-top")];
            Design { legend: fills.to_vec(), colors: greens, fills, opacity: None, top_first: false }
        }
        5 => {
            let solid = colors(&[brand("primary"), "#FA5A46", "#B19ECC"]);
            let fills = [solid.series()[0].clone(), solid.series()[1].clone(), solid.series()[2].clone()];
            Design { legend: fills.to_vec(), colors: solid, fills, opacity: None, top_first: false }
        }
        other => return Err(format!("Area style must be between 1 and 5, got {other}")),
    })
}

/// Each band's outline: along its baseline left to right, back along its top.
fn band_paths(x_count: usize, series: &[Vec<f64>], left: f64, top: f64, width: f64, height: f64) -> Result<Vec<String>, String> {
    let max = (0..x_count).map(|index| series.iter().map(|values| values[index]).sum::<f64>()).fold(f64::MIN, f64::max);
    if max <= 0.0 {
        return Err(format!("the largest stacked total is {max}, so no band has a height to scale"));
    }
    let bottom = top + height;
    let x_at = |index: usize| left + index as f64 * width / (x_count - 1) as f64;
    let y_at = |value: f64| bottom - value / max * height;
    let mut baseline = vec![0.0; x_count];
    let mut paths = Vec::new();
    for values in series {
        let mut path = format!("M {left},{}", y_at(baseline[0]));
        for (index, base) in baseline.iter().enumerate() {
            path.push_str(&format!(" L {},{}", x_at(index), y_at(*base)));
        }
        for index in (0..x_count).rev() {
            path.push_str(&format!(" L {},{}", x_at(index), y_at(baseline[index] + values[index])));
        }
        path.push_str(" Z");
        paths.push(path);
        for (base, value) in baseline.iter_mut().zip(values) {
            *base += value;
        }
    }
    Ok(paths)
}

/// The most fractional digits any of `values` is written with.
fn precision(values: &[f64]) -> usize {
    values.iter().map(|value| value.to_string().split_once('.').map(|(_, fraction)| fraction.len()).unwrap_or(0)).max().unwrap_or(0)
}

pub fn render(spec: &Spec) -> Result<String, String> {
    let style = spec.style.resolve(&STYLE_NAMES)?;
    if spec.y_series.len() != BANDS {
        return Err(format!("the area designs stack {BANDS} series, got {}", spec.y_series.len()));
    }
    if spec.x.len() < 2 {
        return Err(format!("an area chart needs at least two x values, got {}", spec.x.len()));
    }
    if let Some(index) = spec.y_series.iter().position(|series| series.len() != spec.x.len()) {
        return Err(format!("series {index} has {} values but there are {} x values", spec.y_series[index].len(), spec.x.len()));
    }
    let mut svg = chart_frame(spec.width, spec.height, brand("surface"));
    let design = design(style, svg.find_or_insert("defs"))?;
    let colors = &design.colors;
    let labels = spec.labels.clone().unwrap_or_default();
    let chart_y = render_title_and_legend(
        &mut svg,
        spec.title.as_deref().unwrap_or("Area Chart"),
        &labels,
        colors,
        PADDING_X,
        PADDING_Y,
        TITLE_GAP,
        CHART_TOP_MARGIN,
        LegendFills::Given { fills: &design.legend, extra: Some(&colors.series()[0]) },
    )?;
    let chart_x = PADDING_X;
    let chart_width = spec.width - 2.0 * PADDING_X;
    let chart_height = spec.height - PADDING_Y - chart_y;
    let plot_height = chart_height - X_LABEL_ROOM;
    svg.find_or_insert("defs")
        .child(Element::new("clipPath").attr("id", CLIP_ID))
        .child(Element::new("rect").attr("x", chart_x).attr("y", chart_y).attr("width", chart_width).attr("height", plot_height));
    let paths = band_paths(spec.x.len(), &spec.y_series, chart_x, chart_y, chart_width, plot_height)?;
    let digits = precision(&spec.x);
    for (index, value) in spec.x.iter().enumerate() {
        let x = chart_x + index as f64 * chart_width / (spec.x.len() - 1) as f64;
        svg.child(
            Element::new("line")
                .attr("x1", x)
                .attr("y1", chart_y)
                .attr("x2", x)
                .attr("y2", chart_y + plot_height)
                .attr("stroke", &colors["grid"])
                .attr("stroke-width", "1")
                .attr("stroke-dasharray", GRID_DASH),
        );
        svg.child(
            Element::new("text")
                .attr("x", x)
                .attr("y", chart_y + chart_height - X_LABEL_RISE)
                .attr("fill", &colors["legend_text"])
                .attr("font-size", TICK_SIZE)
                .attr("font-weight", "400")
                .attr("text-anchor", "middle")
                .text(format!("{value:.digits$}")),
        );
    }
    let order: Vec<usize> = if design.top_first { (0..BANDS).rev().collect() } else { (0..BANDS).collect() };
    for band in order {
        let mut path = Element::new("path").attr("d", &paths[band]).attr("fill", &design.fills[band]);
        if let Some(opacity) = design.opacity.filter(|opacity| opacity[band] < 1.0) {
            path.set("opacity", opacity[band]);
        }
        svg.child(path.attr("fill-rule", "evenodd").attr("clip-path", url(CLIP_ID)));
    }
    Ok(svg.render())
}
