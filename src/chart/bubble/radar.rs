//! Bubbles on a radar: angle in degrees clockwise from twelve o'clock and
//! distance on a 0–100 scale from the centre.

use super::super::parts::element::Element;
use super::super::parts::Colors;
use super::{bounds, bubble, point_color, share, text, Spec};

/// The design's plot area: top margin and the margin around the outer ring.
const CHART_TOP_MARGIN: f64 = 60.0;
const RING_MARGIN: f64 = 60.0;
/// The design's grid: five rings at 30 % opacity, eight axes at 50 %.
const RINGS: u32 = 5;
const AXES: u32 = 8;
const RING_OPACITY: f64 = 0.3;
const AXIS_OPACITY: f64 = 0.5;
const RING_LABEL_GAP: f64 = 5.0;
const RING_LABEL_SIZE: f64 = 10.0;
const AXIS_LABEL_DISTANCE: f64 = 20.0;
const AXIS_LABEL_BASELINE: f64 = 5.0;
const AXIS_LABEL_SIZE: f64 = 12.0;
/// The design's bubble radii: 5 px for the smallest size, 15 px for the largest.
const MIN_RADIUS: f64 = 5.0;
const MAX_RADIUS: f64 = 15.0;
/// The scale a distance is read on.
const FULL_SCALE: f64 = 100.0;

/// The anchor of an axis label at `angle` degrees (−90 is twelve o'clock):
/// right of the centre starts, left of it ends, top and bottom centre.
fn anchor(angle: f64) -> &'static str {
    if (-45.0..45.0).contains(&angle) || angle >= 315.0 {
        "start"
    } else if (135.0..225.0).contains(&angle) {
        "end"
    } else {
        "middle"
    }
}

pub(super) fn draw(
    svg: &mut Element,
    spec: &Spec,
    colors: &Colors,
    angles: &[f64],
    distances: &[f64],
    categories: Option<&[usize]>,
) {
    let cx = (spec.width / 2.0).floor();
    let cy = ((spec.height + CHART_TOP_MARGIN) / 2.0).floor();
    let max_radius = (spec.width.min(spec.height - CHART_TOP_MARGIN) / 2.0).floor() - RING_MARGIN;
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
        let label = format!("{:02}", (share * FULL_SCALE).round() as u32);
        svg.child(text(
            cx,
            cy - radius - RING_LABEL_GAP,
            &colors["axis_text"],
            RING_LABEL_SIZE,
            "middle",
            &label,
        ));
    }
    for axis in 0..AXES {
        let degrees = f64::from(axis) * 360.0 / f64::from(AXES) - 90.0;
        let theta = degrees.to_radians();
        svg.child(
            Element::new("line")
                .attr("x1", cx)
                .attr("y1", cy)
                .attr("x2", cx + max_radius * theta.cos())
                .attr("y2", cy + max_radius * theta.sin())
                .attr("stroke", &colors["axis_line"])
                .attr("stroke-width", "1")
                .attr("opacity", AXIS_OPACITY),
        );
        let distance = max_radius + AXIS_LABEL_DISTANCE;
        let label = format!("{:02}", axis * (360 / AXES));
        svg.child(text(
            cx + distance * theta.cos(),
            cy + distance * theta.sin() + AXIS_LABEL_BASELINE,
            &colors["axis_text"],
            AXIS_LABEL_SIZE,
            anchor(degrees),
            &label,
        ));
    }
    let (size_min, size_max) = bounds(&spec.sizes);
    for (index, ((angle, distance), size)) in
        angles.iter().zip(distances).zip(&spec.sizes).enumerate()
    {
        let theta = (angle - 90.0).to_radians();
        let reach = distance / FULL_SCALE * max_radius;
        let radius = MIN_RADIUS + share(*size, size_min, size_max) * (MAX_RADIUS - MIN_RADIUS);
        svg.child(bubble(
            cx + reach * theta.cos(),
            cy + reach * theta.sin(),
            radius,
            point_color(colors, categories, index),
        ));
    }
}
