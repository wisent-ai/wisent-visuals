//! Deterministic README banners for Wisent projects.
//!
//! A banner is seeded artwork on the left and the project's words on the right,
//! drawn on a design canvas of `DESIGN_WIDTH` x `DESIGN_HEIGHT`; any other size
//! scales that design by its height. The same configuration always renders the
//! same banner: every variation is read from the SHA-256 of `art_seed` (or of the
//! layout name when no seed is given).

mod art;
mod render;
mod text;

use std::fs;
use std::path::Path;

use serde::Deserialize;
use sha2::{Digest, Sha256};

pub use art::SUPPORTED_LAYOUTS;

/// The canvas the artwork coordinates and text layout are designed on.
pub(crate) const DESIGN_WIDTH: u32 = 1584;
pub(crate) const DESIGN_HEIGHT: u32 = 396;

pub const SUPPORTED_THEMES: [&str; 1] = ["dark"];

/// One brand colour, in the form SVG writes and the form the raster fills.
#[derive(Clone, Copy)]
pub(crate) struct Color {
    pub hex: &'static str,
    pub rgb: [u8; 3],
}

pub(crate) const BACKGROUND: Color = Color {
    hex: "#050605",
    rgb: [0x05, 0x06, 0x05],
};
pub(crate) const PRIMARY: Color = Color {
    hex: "#C5FFC8",
    rgb: [0xC5, 0xFF, 0xC8],
};
pub(crate) const SECONDARY: Color = Color {
    hex: "#B0E3B3",
    rgb: [0xB0, 0xE3, 0xB3],
};
pub(crate) const FONT_FAMILY: &str = "Hubot Sans";

/// One artwork dot: centre x, centre y, radius, and opacity against the background.
pub(crate) type Dot = (f64, f64, f64, f64);

/// Validated content and dimensions for a README banner.
#[derive(Debug, Clone, Deserialize)]
#[serde(default, deny_unknown_fields)]
pub struct BannerConfig {
    pub title: String,
    pub description: String,
    pub product: String,
    pub url: String,
    pub theme: String,
    pub layout: String,
    pub art_seed: String,
    pub width: u32,
    pub height: u32,
}

impl Default for BannerConfig {
    fn default() -> Self {
        Self {
            title: String::new(),
            description: String::new(),
            product: "Wisent".into(),
            url: "wisent.com".into(),
            theme: "dark".into(),
            layout: "latent-field-left".into(),
            art_seed: String::new(),
            width: DESIGN_WIDTH,
            height: DESIGN_HEIGHT,
        }
    }
}

impl BannerConfig {
    /// Load a flat configuration, or the `[banner]` table of a bot-managed one
    /// (which may also hold `[automation]`). Unknown sections and settings are refused by name.
    pub fn from_toml(path: &Path) -> Result<Self, String> {
        let text = fs::read_to_string(path).map_err(|e| format!("{}: {e}", path.display()))?;
        let document: toml::Table = text
            .parse()
            .map_err(|e| format!("{} is not valid TOML: {e}", path.display()))?;
        let values = match document.get("banner") {
            Some(banner) => {
                let mut unknown: Vec<&str> = document
                    .keys()
                    .map(String::as_str)
                    .filter(|key| *key != "banner" && *key != "automation")
                    .collect();
                if !unknown.is_empty() {
                    unknown.sort_unstable();
                    return Err(format!("unknown banner section(s): {}", unknown.join(", ")));
                }
                banner.clone()
            }
            None => toml::Value::Table(document),
        };
        let config: Self = values
            .try_into()
            .map_err(|e| format!("{}: {e}", path.display()))?;
        config.validate()?;
        Ok(config)
    }

    fn validate(&self) -> Result<(), String> {
        if self.title.trim().is_empty() {
            return Err("title must not be empty".into());
        }
        if !SUPPORTED_LAYOUTS.contains(&self.layout.as_str()) {
            return Err(format!(
                "layout must be one of: {}",
                SUPPORTED_LAYOUTS.join(", ")
            ));
        }
        if !SUPPORTED_THEMES.contains(&self.theme.as_str()) {
            return Err(format!(
                "theme must be one of: {}",
                SUPPORTED_THEMES.join(", ")
            ));
        }
        if self.width == 0 || self.height == 0 {
            return Err("width and height must be positive pixel counts".into());
        }
        Ok(())
    }
}

/// A configuration ready to render, with its seed digest and the bundled fonts.
pub struct Banner {
    pub(crate) config: BannerConfig,
    digest: [u8; 32],
    pub(crate) fonts: text::Fonts,
}

impl Banner {
    pub fn new(config: BannerConfig) -> Result<Self, String> {
        config.validate()?;
        let seed = if config.art_seed.is_empty() {
            config.layout.as_str()
        } else {
            config.art_seed.as_str()
        };
        let digest: [u8; 32] = Sha256::digest(seed.as_bytes()).into();
        Ok(Self {
            config,
            digest,
            fonts: text::Fonts::load()?,
        })
    }

    /// How much the design canvas is scaled to reach the configured height.
    pub(crate) fn scale(&self) -> f64 {
        f64::from(self.config.height) / f64::from(DESIGN_HEIGHT)
    }

    /// A value between `low` and `high` read from byte `index` of the seed digest.
    pub(crate) fn variant(&self, index: usize, low: f64, high: f64) -> f64 {
        let unit = f64::from(self.digest[index % self.digest.len()]) / 255.0;
        low + (high - low) * unit
    }

    /// Evenly spaced dots from `start` to `end`, in design coordinates, scaled.
    pub(crate) fn line_dots(
        &self,
        out: &mut Vec<Dot>,
        start: (f64, f64),
        end: (f64, f64),
        spacing: f64,
        opacity: f64,
        radius: f64,
    ) {
        let scale = self.scale();
        let distance = (end.0 - start.0).hypot(end.1 - start.1);
        let steps = (distance / spacing).round_ties_even().max(1.0) as usize;
        for index in 0..=steps {
            let progress = index as f64 / steps as f64;
            let x = start.0 + (end.0 - start.0) * progress;
            let y = start.1 + (end.1 - start.1) * progress;
            out.push((x * scale, y * scale, radius * scale, opacity));
        }
    }
}
