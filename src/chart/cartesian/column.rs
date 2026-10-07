//! Grouped vertical column charts.
//!
//! ```json
//! {"kind": "column", "style": "pattern1", "theme": "black", "width": 1002, "height": 499,
//!  "categories": ["Q1", "Q2"], "series": [[800, 550], [500, 250]],
//!  "labels": ["One", "Two"], "title": "Group Column Chart"}
//! ```

use super::{self as cartesian, CHART_TOP_MARGIN, PADDING_X, PADDING_Y, TITLE_GAP};
use crate::chart::parts::assets::cartesian_patterns;
use crate::chart::parts::element::{chart_frame, Element};
use crate::chart::parts::legend::{render_title_and_legend, LegendFills};

/// The design's column width and the gap between columns of one group.
const COLUMN_WIDTH: f64 = 40.0;
const COLUMN_SPACING: f64 = 10.0;
/// The design's room under the columns for category labels, and their baseline.
const AXIS_LABEL_ROOM: f64 = 40.0;
const AXIS_LABEL_OFFSET: f64 = 20.0;
/// The design's value axis: five steps above zero, the top 10 % above the tallest column.
const Y_STEPS: u32 = 5;
const HEADROOM: f64 = 1.1;
const TICK_GAP: f64 = 10.0;
const TICK_BASELINE: f64 = 4.0;
const LABEL_SIZE: f64 = 14.0;
const TICK_SIZE: f64 = 12.0;

/// A column chart takes exactly the fields every cartesian chart takes.
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
        common.title.as_deref().unwrap_or("Group Column Chart"),
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
    let chart_height = common.height - PADDING_Y - chart_start_y - AXIS_LABEL_ROOM;
    let max_value = common
        .series
        .iter()
        .flatten()
        .copied()
        .fold(f64::MIN, f64::max);
    if max_value <= 0.0 {
        return Err(format!(
            "the largest value is {max_value}, so no column has a height to scale"
        ));
    }
    let y_max = max_value * HEADROOM;
    for step in 0..=Y_STEPS {
        let share = f64::from(step) / f64::from(Y_STEPS);
        let y = chart_start_y + chart_height - share * chart_height;
        svg.child(
            Element::new("text")
                .attr("x", chart_x - TICK_GAP)
                .attr("y", y + TICK_BASELINE)
                .attr("fill", &colors["legend_text"])
                .attr("font-size", TICK_SIZE)
                .attr("font-weight", "400")
                .attr("text-anchor", "end")
                .text((share * y_max).trunc()),
        );
    }
    let group_width = chart_width / common.categories.len() as f64;
    let series_count = common.series.len() as f64;
    let total_columns_width = series_count * COLUMN_WIDTH + (series_count - 1.0) * COLUMN_SPACING;
    for (index, category) in common.categories.iter().enumerate() {
        let group_center = chart_x + index as f64 * group_width + group_width / 2.0;
        let columns_start_x = group_center - total_columns_width / 2.0;
        for (series, values) in common.series.iter().enumerate() {
            let column_height = values[index] / y_max * chart_height;
            svg.child(
                Element::new("rect")
                    .attr(
                        "x",
                        columns_start_x + series as f64 * (COLUMN_WIDTH + COLUMN_SPACING),
                    )
                    .attr("y", chart_start_y + chart_height - column_height)
                    .attr("width", COLUMN_WIDTH)
                    .attr("height", column_height)
                    .attr("fill", fills.get(series).unwrap_or(&first)),
            );
        }
        svg.child(
            Element::new("text")
                .attr("x", group_center)
                .attr("y", chart_start_y + chart_height + AXIS_LABEL_OFFSET)
                .attr("fill", &colors["legend_text"])
                .attr("font-size", LABEL_SIZE)
                .attr("font-weight", "400")
                .attr("text-anchor", "middle")
                .text(category),
        );
    }
    Ok(svg.render())
}
