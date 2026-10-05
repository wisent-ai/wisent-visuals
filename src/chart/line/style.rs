//! Line styles 1–6: dark solid palette, dark with markers, dark with marker
//! shapes, and the same three on white (registry styles 10–12 and 20–22).

use super::super::parts::legend::Marker;
use super::super::parts::{Colors, StyleChoice};
use crate::brand::brand_color;

/// The style names; they name the dark styles.
const STYLE_NAMES: [(&str, u32); 3] = [("solid", 1), ("markers", 2), ("shapes", 3)];

/// Every series of a marker style draws circles.
const CIRCLES: [Marker; 1] = [Marker::Circle];
/// A shapes style gives each series its own marker, in this order.
const SHAPES: [Marker; 5] = [Marker::Circle, Marker::Triangle, Marker::Square, Marker::Diamond, Marker::Triangle];

/// What a line style decides: its colours and the markers each series draws.
pub struct LineStyle {
    pub colors: Colors,
    pub markers: &'static [Marker],
}

fn brand(role: &str) -> &'static str {
    brand_color(role).unwrap_or_default()
}

pub fn line_style(choice: &StyleChoice) -> Result<LineStyle, String> {
    let number = choice.resolve(&STYLE_NAMES)?;
    let dark = |series: &[&str], markers: &'static [Marker]| LineStyle {
        colors: Colors::new(
            &[("background", brand("surface")), ("title", brand("primary")), ("grid", brand("grid")), ("legend_text", brand("muted"))],
            series,
        ),
        markers,
    };
    let light = |series: &[&str], markers: &'static [Marker]| LineStyle {
        colors: Colors::new(&[("background", "#FFFFFF"), ("title", "#000000"), ("grid", "#E5E5E5"), ("legend_text", "#666666")], series),
        markers,
    };
    match number {
        1 => Ok(dark(&[brand("primary"), "#FA5A46", "#B19ECC"], &[])),
        2 => Ok(dark(&[brand("primary"), "#FA5A46", "#B19ECC"], &CIRCLES)),
        3 => Ok(dark(&["#FFFFFF", "#FA5A46", "#FF8C00", "#90EE90", "#87CEEB"], &SHAPES)),
        4 => Ok(light(&["#333333", "#666666", "#999999"], &[])),
        5 => Ok(light(&["#00C896", "#FF6B6B", "#C8C8C8"], &CIRCLES)),
        6 => Ok(light(&["#000000", "#FF6B6B", "#FF8C00", "#C8C8FF", "#C8C8C8"], &SHAPES)),
        other => Err(format!("Line style must be between 1 and 6, got {other}")),
    }
}
