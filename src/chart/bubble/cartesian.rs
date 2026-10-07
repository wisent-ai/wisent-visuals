//! Bubbles on x/y axes. The axis labels are the data's own range: the y axis
//! from its maximum at the top to its minimum at the bottom, the x axis at the
//! centre of each grid column, printed with the precision the data carries.

use super::super::parts::element::Element;
use super::super::parts::Colors;
use super::{bounds, bubble, point_color, share, text, Spec, PADDING_X};

/// The design's plot area: top margin, room for the y labels, right and bottom margins.
const CHART_TOP_MARGIN: f64 = 60.0;
const Y_LABEL_ROOM: f64 = 40.0;
const RIGHT_MARGIN: f64 = 50.0;
const BOTTOM_MARGIN: f64 = 50.0;
/// The design's grid: five bands each way at 30 % opacity.
const BANDS: u32 = 5;
const GRID_OPACITY: f64 = 0.3;
const TICK_SIZE: f64 = 12.0;
const Y_LABEL_GAP: f64 = 10.0;
const Y_LABEL_BASELINE: f64 = 5.0;
const X_LABEL_OFFSET: f64 = 20.0;
/// The design's bubble radii: 5 px for the smallest size, 20 px for the largest.
const MIN_RADIUS: f64 = 5.0;
const MAX_RADIUS: f64 = 20.0;

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

fn line(x1: f64, y1: f64, x2: f64, y2: f64, colors: &Colors) -> Element {
    Element::new("line")
        .attr("x1", x1)
        .attr("y1", y1)
        .attr("x2", x2)
        .attr("y2", y2)
        .attr("stroke", &colors["grid"])
        .attr("stroke-width", "1")
        .attr("opacity", GRID_OPACITY)
}

pub(super) fn draw(
    svg: &mut Element,
    spec: &Spec,
    colors: &Colors,
    xs: &[f64],
    ys: &[f64],
    categories: Option<&[usize]>,
) {
    let (x, y) = (PADDING_X + Y_LABEL_ROOM, CHART_TOP_MARGIN);
    let width = spec.width - PADDING_X * 2.0 - RIGHT_MARGIN;
    let height = spec.height - CHART_TOP_MARGIN - BOTTOM_MARGIN;
    let ((x_min, x_max), (y_min, y_max)) = (bounds(xs), bounds(ys));
    let (x_digits, y_digits) = (precision(xs), precision(ys));
    let bands = f64::from(BANDS);
    for band in 0..=BANDS {
        let step = f64::from(band);
        let y_pos = y + step * height / bands;
        svg.child(line(x, y_pos, x + width, y_pos, colors));
        let value = y_max - step * (y_max - y_min) / bands;
        svg.child(text(
            x - Y_LABEL_GAP,
            y_pos + Y_LABEL_BASELINE,
            &colors["axis_text"],
            TICK_SIZE,
            "end",
            &format!("{value:.y_digits$}"),
        ));
        let x_pos = x + step * width / bands;
        svg.child(line(x_pos, y, x_pos, y + height, colors));
        if band < BANDS {
            let value = x_min + (step + 0.5) * (x_max - x_min) / bands;
            let centre = x_pos + width / bands / 2.0;
            svg.child(text(
                centre,
                y + height + X_LABEL_OFFSET,
                &colors["axis_text"],
                TICK_SIZE,
                "middle",
                &format!("{value:.x_digits$}"),
            ));
        }
    }
    let (size_min, size_max) = bounds(&spec.sizes);
    for (index, ((px, py), size)) in xs.iter().zip(ys).zip(&spec.sizes).enumerate() {
        let cx = x + share(*px, x_min, x_max) * width;
        let cy = y + height - share(*py, y_min, y_max) * height;
        let radius = MIN_RADIUS + share(*size, size_min, size_max) * (MAX_RADIUS - MIN_RADIUS);
        svg.child(bubble(
            cx,
            cy,
            radius,
            point_color(colors, categories, index),
        ));
    }
}
