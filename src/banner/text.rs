//! Banner text measurement, wrapping and placement through the bundled Hubot Sans fonts.

use fontdue::{Font, FontSettings};

use super::{Banner, Color, PRIMARY, SECONDARY};

pub(super) use crate::brand::{BOLD_TTF, REGULAR_TTF};

/// The description area of the layout holds this many lines.
const DESCRIPTION_LINES: usize = 3;

#[derive(Clone, Copy, PartialEq, Eq)]
pub(super) enum Weight {
    Regular,
    Bold,
}

/// What a line is, which decides its anchor: the URL is right-aligned, the rest left.
#[derive(Clone, Copy, PartialEq, Eq)]
pub(super) enum Role {
    Title,
    Description,
    Product,
    Url,
}

/// One placed line; `y` is the top of the font's ascender.
pub(super) struct TextLine {
    pub text: String,
    pub x: f64,
    pub y: f64,
    pub size: u32,
    pub weight: Weight,
    pub color: Color,
    pub role: Role,
}

struct Face {
    font: Font,
    ascent_per_px: f64,
}

pub(crate) struct Fonts {
    regular: Face,
    bold: Face,
}

impl Fonts {
    pub(super) fn load() -> Result<Self, String> {
        let face = |bytes: &'static [u8], name: &str| -> Result<Face, String> {
            let font = Font::from_bytes(bytes, FontSettings::default())
                .map_err(|e| format!("bundled font {name} is unreadable: {e}"))?;
            let ascent_per_px = font
                .horizontal_line_metrics(1.0)
                .ok_or_else(|| format!("bundled font {name} declares no horizontal metrics"))?
                .ascent;
            Ok(Face {
                font,
                ascent_per_px: f64::from(ascent_per_px),
            })
        };
        Ok(Self {
            regular: face(REGULAR_TTF, "HubotSans-Regular.ttf")?,
            bold: face(BOLD_TTF, "HubotSans-Bold.ttf")?,
        })
    }

    pub(super) fn font(&self, weight: Weight) -> &Font {
        match weight {
            Weight::Regular => &self.regular.font,
            Weight::Bold => &self.bold.font,
        }
    }

    pub(super) fn ascent(&self, size: u32, weight: Weight) -> f64 {
        let face = match weight {
            Weight::Regular => &self.regular,
            Weight::Bold => &self.bold,
        };
        face.ascent_per_px * f64::from(size)
    }

    /// The advance width of `text`, kerning included.
    pub(super) fn measure(&self, text: &str, size: u32, weight: Weight) -> f64 {
        let font = self.font(weight);
        let px = size as f32;
        let mut width = 0.0_f64;
        let mut previous = None;
        for ch in text.chars() {
            if let Some(prev) = previous {
                width += f64::from(font.horizontal_kern(prev, ch, px).unwrap_or(0.0));
            }
            width += f64::from(font.metrics(ch, px).advance_width);
            previous = Some(ch);
        }
        width
    }

    /// The top and bottom of the ink of `text`, measured down from the ascender line.
    pub(super) fn ink_bounds(&self, text: &str, size: u32, weight: Weight) -> (f64, f64) {
        let font = self.font(weight);
        let ascent = self.ascent(size, weight);
        let mut bounds: Option<(f64, f64)> = None;
        for ch in text.chars() {
            let metrics = font.metrics(ch, size as f32);
            if metrics.height == 0 {
                continue;
            }
            let top = ascent - f64::from(metrics.ymin + metrics.height as i32);
            let bottom = ascent - f64::from(metrics.ymin);
            bounds = Some(match bounds {
                Some((t, b)) => (t.min(top), b.max(bottom)),
                None => (top, bottom),
            });
        }
        bounds.unwrap_or((0.0, 0.0))
    }
}

fn wrap(fonts: &Fonts, text: &str, size: u32, max_width: f64) -> Vec<String> {
    let mut lines = Vec::new();
    for paragraph in text.trim().lines() {
        let mut words = paragraph.split_whitespace();
        let Some(first) = words.next() else { continue };
        let mut current = first.to_string();
        for word in words {
            let candidate = format!("{current} {word}");
            if fonts.measure(&candidate, size, Weight::Regular) <= max_width {
                current = candidate;
            } else {
                lines.push(std::mem::replace(&mut current, word.to_string()));
            }
        }
        lines.push(current);
    }
    lines
}

fn scaled(value: f64, scale: f64, floor: u32) -> u32 {
    ((value * scale).round_ties_even() as u32).max(floor)
}

/// Place the title, description, product and URL. The title and description
/// shrink to fit the text column; a description that still needs more than the
/// layout's lines at its smallest size is refused rather than cut.
pub(super) fn layout(banner: &Banner) -> Result<Vec<TextLine>, String> {
    let cfg = &banner.config;
    let fonts = &banner.fonts;
    let scale = banner.scale();
    let width = f64::from(cfg.width);
    let text_x = width * 0.518;
    let right = width - 50.0 * scale;
    let max_width = right - text_x;

    let mut title_size = scaled(48.0, scale, 24);
    while title_size > scaled(30.0, scale, 24)
        && fonts.measure(&cfg.title, title_size, Weight::Bold) > max_width
    {
        title_size -= 1;
    }

    let smallest_description = scaled(20.0, scale, 14);
    let mut description_size = scaled(32.0, scale, 16);
    let mut description = wrap(fonts, &cfg.description, description_size, max_width);
    while description.len() > DESCRIPTION_LINES && description_size > smallest_description {
        description_size -= 1;
        description = wrap(fonts, &cfg.description, description_size, max_width);
    }
    if description.len() > DESCRIPTION_LINES {
        return Err(format!(
            "the description needs {} lines at the smallest size ({description_size} px); the banner holds {DESCRIPTION_LINES}: shorten it",
            description.len()
        ));
    }

    let mut lines = vec![TextLine {
        text: cfg.title.clone(),
        x: text_x,
        y: 43.0 * scale,
        size: title_size,
        weight: Weight::Bold,
        color: PRIMARY,
        role: Role::Title,
    }];
    let line_height = f64::from(description_size) * 1.12;
    for (index, text) in description.into_iter().enumerate() {
        lines.push(TextLine {
            text,
            x: text_x,
            y: 116.0 * scale + index as f64 * line_height,
            size: description_size,
            weight: Weight::Regular,
            color: SECONDARY,
            role: Role::Description,
        });
    }
    let footer_y = f64::from(cfg.height) - 65.0 * scale;
    lines.push(TextLine {
        text: cfg.product.clone(),
        x: text_x + 44.0 * scale,
        y: footer_y,
        size: scaled(29.0, scale, 16),
        weight: Weight::Regular,
        color: PRIMARY,
        role: Role::Product,
    });
    lines.push(TextLine {
        text: cfg.url.clone(),
        x: right,
        y: footer_y + 8.0 * scale,
        size: scaled(20.0, scale, 12),
        weight: Weight::Regular,
        color: SECONDARY,
        role: Role::Url,
    });
    Ok(lines)
}
