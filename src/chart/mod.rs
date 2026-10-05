//! Wisent brand charts drawn as SVG: area, bar, column, line, pie, radar and
//! bubble. A chart is described by a JSON spec whose `kind` names the family;
//! every other field is that family's, and a field the family does not take
//! is refused.

pub mod area;
pub mod bubble;
pub mod cartesian;
pub mod line;
pub mod parts;
pub mod pie;
pub mod radar;
pub mod raster;

use cartesian::{bar, column};

use std::path::Path;

use serde::Deserialize;

/// One chart, by family.
#[derive(Debug, Deserialize)]
#[serde(tag = "kind", rename_all = "lowercase")]
pub enum ChartSpec {
    Area(area::Spec),
    Bar(bar::Spec),
    Bubble(bubble::Spec),
    Column(column::Spec),
    Line(line::Spec),
    Pie(pie::Spec),
    Radar(radar::Spec),
}

impl ChartSpec {
    /// Read a spec from JSON text; `origin` names it in a refusal.
    pub fn from_json(text: &str, origin: &str) -> Result<Self, String> {
        serde_json::from_str(text).map_err(|error| format!("{origin} is not a chart spec: {error}"))
    }

    /// The chart as SVG text.
    pub fn render(&self) -> Result<String, String> {
        match self {
            Self::Area(spec) => area::render(spec),
            Self::Bar(spec) => bar::render(spec),
            Self::Bubble(spec) => bubble::render(spec),
            Self::Column(spec) => column::render(spec),
            Self::Line(spec) => line::render(spec),
            Self::Pie(spec) => pie::render(spec),
            Self::Radar(spec) => radar::render(spec),
        }
    }

    /// Render to `path`: `.svg` writes the SVG, `.png` rasterises it.
    pub fn save(&self, path: &Path) -> Result<(), String> {
        raster::save(&self.render()?, path)
    }
}
