//! What the bar and column designs share: styles 1–5, the three themes'
//! colours, the fill each series takes in each style, and the Figma spacing.

pub mod bar;
pub mod column;

use serde::Deserialize;

use super::parts::{Colors, StyleChoice, Theme};

/// The design's card padding, title gap and chart top margin.
pub const PADDING_X: f64 = 32.0;
pub const PADDING_Y: f64 = 16.0;
pub const TITLE_GAP: f64 = 10.0;
pub const CHART_TOP_MARGIN: f64 = 24.0;

/// The bar and column style names.
const STYLE_NAMES: [(&str, u32); 5] = [
    ("solid", 1),
    ("pattern1", 2),
    ("pattern2", 3),
    ("pattern3", 4),
    ("multicolor", 5),
];

/// A bar or column chart: the fields both take.
#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Common {
    /// 1 solid, 2 solid + noise + solid, 3 solid + crossing lines + solid,
    /// 4 solid + noise + dither crosses, 5 green, red and purple; or a style name.
    pub style: StyleChoice,
    pub theme: Theme,
    pub width: f64,
    pub height: f64,
    pub categories: Vec<String>,
    pub series: Vec<Vec<f64>>,
    pub labels: Vec<String>,
    #[serde(default)]
    pub title: Option<String>,
}

/// The validated style number.
pub fn style_number(choice: &StyleChoice) -> Result<u32, String> {
    let number = choice.resolve(&STYLE_NAMES)?;
    if !(1..=5).contains(&number) {
        return Err(format!("Style must be between 1 and 5, got {number}"));
    }
    Ok(number)
}

/// Every series must give one value per category, or a segment would read past its data.
pub fn check_shape(common: &Common) -> Result<(), String> {
    if common.categories.is_empty() || common.series.is_empty() {
        return Err("a chart needs at least one category and one series".to_string());
    }
    match common
        .series
        .iter()
        .position(|values| values.len() != common.categories.len())
    {
        Some(index) => Err(format!(
            "series {index} has {} values but there are {} categories",
            common.series[index].len(),
            common.categories.len()
        )),
        None => Ok(()),
    }
}

/// The theme's colours; the series palette is the three tones, then the multi-colour three.
pub fn colors(theme: Theme) -> Colors {
    let (background, title, legend_text, grid, tones) = match theme {
        Theme::Brand => (
            "#121212",
            "#C5FFC8",
            "#769978",
            "#2D3130",
            ["#C5FFC8", "#90B892", "#5A715B"],
        ),
        Theme::Black => (
            "#121212",
            "#FFFFFF",
            "#999999",
            "#2D3130",
            ["#FFFFFF", "#808080", "#4D4D4D"],
        ),
        Theme::White => (
            "#FFFFFF",
            "#000000",
            "#666666",
            "#E0E0E0",
            ["#000000", "#808080", "#CCCCCC"],
        ),
    };
    let [one, two, three] = tones;
    Colors::new(
        &[
            ("background", background),
            ("title", title),
            ("legend_text", legend_text),
            ("grid", grid),
        ],
        &[one, two, three, "#C5FFC8", "#FF4444", "#B19CD9"],
    )
}

/// The fill of each series in `style`; a series past the third takes the first tone.
pub fn fills(colors: &Colors, style: u32) -> Vec<String> {
    let tone = |index: usize| colors.series()[index].clone();
    match style {
        2 => vec![tone(0), "url(#pattern-noise)".to_string(), tone(2)],
        3 => vec![tone(0), "url(#pattern-crossing)".to_string(), tone(2)],
        4 => vec![
            tone(0),
            "url(#pattern-noise)".to_string(),
            "url(#pattern-dither)".to_string(),
        ],
        5 => vec![tone(3), tone(4), tone(5)],
        _ => vec![tone(0), tone(1), tone(2)],
    }
}
