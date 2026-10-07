//! Horizontal stacked bar charts.
//!
//! ```json
//! {"kind": "bar", "style": 1, "theme": "brand", "width": 1002, "height": 499,
//!  "categories": ["Day Time 1", "Day Time 2"], "series": [[30, 40], [25, 35]],
//!  "labels": ["One", "Two"], "title": "Bar Chart"}
//! ```

use super::{self as cartesian, CHART_TOP_MARGIN, PADDING_X, PADDING_Y, TITLE_GAP};
use crate::chart::parts::assets::cartesian_patterns;
use crate::chart::parts::element::{chart_frame, Element};
use crate::chart::parts::legend::{render_title_and_legend, LegendFills};

/// The design's bar thickness, gap between bars and category label column.
const BAR_HEIGHT: f64 = 30.0;
const BAR_SPACING: f64 = 20.0;
const LABEL_COLUMN: f64 = 120.0;
/// The design's scale: nine ticks under the bars, 10 px below the last bar.
const TICKS: u32 = 9;
const AXIS_OFFSET: f64 = 10.0;
const LABEL_SIZE: f64 = 14.0;
const TICK_SIZE: f64 = 12.0;
const LABEL_BASELINE: f64 = 5.0;

/// A bar chart takes exactly the fields every cartesian chart takes.
pub type Spec = cartesian::Common;

pub fn render(common: &Spec) -> Result<String, String> {
    let style = cartesian::style_number(&common.style)?;
    cartesian::check_shape(common)?;
    let colors = cartesian::colors(common.theme);
    let fills = cartesian::fills(&colors, style);
    let mut svg = chart_frame(common.width, common.height, &colors["background"]);
    cartesian_patterns(&mut svg, style)?;
    let first = colors.series()[0].clone();
    let chart_start_y = render_title_and_legend(
        &mut svg,
        common.title.as_deref().unwrap_or("Bar Chart"),
        &common.labels,
        &colors,
        PADDING_X,
        PADDING_Y,
        TITLE_GAP,
        CHART_TOP_MARGIN,
        LegendFills::Given {
            fills: &fills,
            extra: Some(&first),
        },
    )?;
    let chart_x = PADDING_X;
    let chart_width = common.width - 2.0 * PADDING_X;
    let available_width = chart_width - LABEL_COLUMN;
    let max_value = (0..common.categories.len())
        .map(|category| {
            common
                .series
                .iter()
                .map(|values| values[category])
                .sum::<f64>()
        })
        .fold(f64::MIN, f64::max);
    if max_value <= 0.0 {
        return Err(format!(
            "the largest stacked total is {max_value}, so no bar has a length to scale"
        ));
    }
    for (index, category) in common.categories.iter().enumerate() {
        let y = chart_start_y + index as f64 * (BAR_HEIGHT + BAR_SPACING);
        svg.child(
            Element::new("text")
                .attr("x", chart_x)
                .attr("y", y + (BAR_HEIGHT / 2.0).floor() + LABEL_BASELINE)
                .attr("fill", &colors["legend_text"])
                .attr("font-size", LABEL_SIZE)
                .attr("font-weight", "400")
                .text(category),
        );
        let mut current_x = chart_x + LABEL_COLUMN;
        for (segment, values) in common.series.iter().enumerate() {
            let width = values[index] / max_value * available_width;
            svg.child(
                Element::new("rect")
                    .attr("x", current_x)
                    .attr("y", y)
                    .attr("width", width)
                    .attr("height", BAR_HEIGHT)
                    .attr("fill", fills.get(segment).unwrap_or(&first)),
            );
            current_x += width;
        }
    }
    let axis_y =
        chart_start_y + common.categories.len() as f64 * (BAR_HEIGHT + BAR_SPACING) + AXIS_OFFSET;
    let last = f64::from(TICKS - 1);
    for tick in 0..TICKS {
        let share = f64::from(tick) / last;
        svg.child(
            Element::new("text")
                .attr("x", chart_x + LABEL_COLUMN + share * available_width)
                .attr("y", axis_y)
                .attr("fill", &colors["legend_text"])
                .attr("font-size", TICK_SIZE)
                .attr("font-weight", "400")
                .attr("text-anchor", "middle")
                .text((share * max_value).trunc()),
        );
    }
    Ok(svg.render())
}
