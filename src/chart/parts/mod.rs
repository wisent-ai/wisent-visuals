//! What every chart family shares: the SVG element tree, title and legend,
//! markers, the embedded fill patterns, themes and colour palettes.

pub mod assets;
pub mod element;
pub mod legend;

use std::ops::Index;

use serde::Deserialize;

/// The background a chart is drawn for.
#[derive(Clone, Copy, Debug, PartialEq, Eq, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum Theme {
    Brand,
    Black,
    White,
}

/// A theme's colours: named roles (`title`, `legend_text`, `background`, …)
/// and the ordered series palette that fills data.
#[derive(Clone, Debug)]
pub struct Colors {
    roles: Vec<(&'static str, String)>,
    series: Vec<String>,
}

impl Colors {
    pub fn new(roles: &[(&'static str, &str)], series: &[&str]) -> Self {
        Self {
            roles: roles
                .iter()
                .map(|(role, value)| (*role, value.to_string()))
                .collect(),
            series: series.iter().map(|value| value.to_string()).collect(),
        }
    }

    pub fn get(&self, role: &str) -> Option<&String> {
        self.roles
            .iter()
            .find(|(name, _)| *name == role)
            .map(|(_, value)| value)
    }

    pub fn series(&self) -> &[String] {
        &self.series
    }

    /// Series colour `index`, cycling when there are more series than colours.
    pub fn series_color(&self, index: usize) -> &str {
        &self.series[index % self.series.len()]
    }

    /// Series colour `index`, the last colour for an index past the palette.
    pub fn series_or_last(&self, index: usize) -> &str {
        self.series
            .get(index)
            .or(self.series.last())
            .map(String::as_str)
            .unwrap_or_default()
    }
}

impl Index<&str> for Colors {
    type Output = String;

    /// The colour of `role`; a role the theme does not define is a defect in
    /// the family that asked for it, as a missing key was in the Python port.
    fn index(&self, role: &str) -> &String {
        self.get(role)
            .unwrap_or_else(|| panic!("the chart theme defines no colour for {role:?}"))
    }
}

/// A chart style selected by number or by its name, as the Python API took it.
#[derive(Clone, Debug, PartialEq, Eq, Deserialize)]
#[serde(untagged)]
pub enum StyleChoice {
    Number(u32),
    Name(String),
}

impl StyleChoice {
    /// The style number: `Number` as given, `Name` looked up case-insensitively in `names`.
    pub fn resolve(&self, names: &[(&str, u32)]) -> Result<u32, String> {
        match self {
            Self::Number(number) => Ok(*number),
            Self::Name(name) => names
                .iter()
                .find(|(known, _)| known.eq_ignore_ascii_case(name))
                .map(|(_, number)| *number)
                .ok_or_else(|| {
                    let valid: Vec<&str> = names.iter().map(|(known, _)| *known).collect();
                    format!(
                        "Unknown style name: {name}. Valid names are: {}",
                        valid.join(", ")
                    )
                }),
        }
    }
}
