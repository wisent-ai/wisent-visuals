//! The banner drawn as a self-contained SVG, or rasterised to WebP or PNG.

use std::fs;
use std::path::Path;

use base64::{engine::general_purpose::STANDARD, Engine as _};
use image::codecs::webp::WebPEncoder;
use image::{
    imageops, DynamicImage, ExtendedColorType, ImageEncoder, ImageFormat, Rgba, RgbaImage,
};

use super::text::{self, Fonts, Role, TextLine, Weight, BOLD_TTF, REGULAR_TTF};
use super::{art, Banner, BACKGROUND, FONT_FAMILY, PRIMARY};

use crate::brand::LOGO_PNG;

impl Banner {
    /// The logo's position and size, and the visible top of the product wordmark.
    fn footer_geometry(&self) -> (f64, f64, f64, f64) {
        let scale = self.scale();
        let size = 34.0 * scale;
        let footer_y = f64::from(self.config.height) - 65.0 * scale;
        let font_size = ((29.0 * scale).round_ties_even() as u32).max(16);
        let (top, bottom) = self
            .fonts
            .ink_bounds(&self.config.product, font_size, Weight::Regular);
        let text_top = footer_y + top;
        let logo_y = (text_top + footer_y + bottom - size) / 2.0;
        (f64::from(self.config.width) * 0.518, logo_y, size, text_top)
    }

    /// A self-contained SVG with the Hubot Sans fonts and the logo embedded.
    pub fn render_svg(&self) -> Result<String, String> {
        let cfg = &self.config;
        let (width, height) = (cfg.width, cfg.height);
        let regular = STANDARD.encode(REGULAR_TTF);
        let bold = STANDARD.encode(BOLD_TTF);
        let mut parts = vec![
            r#"<?xml version="1.0" encoding="UTF-8"?>"#.to_string(),
            format!(r#"<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">"#),
            "<defs><style>".to_string(),
            format!("@font-face{{font-family:'{FONT_FAMILY}';src:url(data:font/ttf;base64,{regular}) format('truetype');font-weight:400}}"),
            format!("@font-face{{font-family:'{FONT_FAMILY}';src:url(data:font/ttf;base64,{bold}) format('truetype');font-weight:700}}"),
            format!("text{{font-family:'{FONT_FAMILY}',sans-serif}}"),
            "</style></defs>".to_string(),
            format!(r#"<rect width="{width}" height="{height}" fill="{}"/>"#, BACKGROUND.hex),
        ];
        for (x, y, radius, opacity) in art::render(self) {
            parts.push(format!(
                r#"<circle cx="{x:.2}" cy="{y:.2}" r="{radius:.2}" fill="{}" opacity="{opacity:.3}"/>"#,
                PRIMARY.hex
            ));
        }
        let (logo_x, logo_y, logo_size, product_top) = self.footer_geometry();
        parts.push(format!(
            r#"<image x="{logo_x:.2}" y="{logo_y:.2}" width="{logo_size:.2}" height="{logo_size:.2}" href="data:image/png;base64,{}"/>"#,
            STANDARD.encode(LOGO_PNG)
        ));
        for line in text::layout(self)? {
            let anchor = if line.role == Role::Url {
                "end"
            } else {
                "start"
            };
            let y = if line.role == Role::Product {
                product_top
            } else {
                line.y
            };
            let weight = if line.weight == Weight::Bold {
                700
            } else {
                400
            };
            parts.push(format!(
                r#"<text x="{:.2}" y="{y:.2}" dominant-baseline="hanging" text-anchor="{anchor}" font-size="{}" font-weight="{weight}" fill="{}">{}</text>"#,
                line.x,
                line.size,
                line.color.hex,
                escape(&line.text)
            ));
        }
        parts.push("</svg>".to_string());
        Ok(parts.join("\n") + "\n")
    }

    /// The banner as pixels: artwork dots, the logo, then the text.
    pub fn render_image(&self) -> Result<RgbaImage, String> {
        let cfg = &self.config;
        let [r, g, b] = BACKGROUND.rgb;
        let mut image = RgbaImage::from_pixel(cfg.width, cfg.height, Rgba([r, g, b, 255]));
        for (x, y, radius, opacity) in art::render(self) {
            let shade = |channel: u8| (f64::from(channel) * opacity).round_ties_even() as u8;
            let [pr, pg, pb] = PRIMARY.rgb;
            fill_circle(
                &mut image,
                x,
                y,
                radius,
                Rgba([shade(pr), shade(pg), shade(pb), 255]),
            );
        }
        let (logo_x, logo_y, logo_size, _) = self.footer_geometry();
        let side = (logo_size.round_ties_even() as u32).max(1);
        let logo = image::load_from_memory(LOGO_PNG)
            .map_err(|e| format!("bundled logo is unreadable: {e}"))?
            .to_rgba8();
        let logo = imageops::resize(&logo, side, side, imageops::FilterType::Lanczos3);
        imageops::overlay(
            &mut image,
            &logo,
            logo_x.round_ties_even() as i64,
            logo_y.round_ties_even() as i64,
        );
        for line in text::layout(self)? {
            draw_text(&mut image, &self.fonts, &line);
        }
        Ok(image)
    }

    /// The banner as lossless WebP bytes, so no quality setting is involved.
    pub fn render_webp(&self) -> Result<Vec<u8>, String> {
        let rgb = DynamicImage::ImageRgba8(self.render_image()?).to_rgb8();
        let mut bytes = Vec::new();
        WebPEncoder::new_lossless(&mut bytes)
            .write_image(
                rgb.as_raw(),
                rgb.width(),
                rgb.height(),
                ExtendedColorType::Rgb8,
            )
            .map_err(|e| format!("WebP encoding failed: {e}"))?;
        Ok(bytes)
    }

    /// Render to `path`, the format chosen by its .svg, .webp, or .png suffix.
    pub fn save(&self, path: &Path) -> Result<(), String> {
        let shown = path.display();
        if let Some(parent) = path.parent().filter(|p| !p.as_os_str().is_empty()) {
            fs::create_dir_all(parent).map_err(|e| format!("{}: {e}", parent.display()))?;
        }
        let suffix = path
            .extension()
            .and_then(|ext| ext.to_str())
            .map(str::to_ascii_lowercase);
        match suffix.as_deref() {
            Some("svg") => fs::write(path, self.render_svg()?).map_err(|e| format!("{shown}: {e}")),
            Some("webp") => {
                fs::write(path, self.render_webp()?).map_err(|e| format!("{shown}: {e}"))
            }
            Some("png") => DynamicImage::ImageRgba8(self.render_image()?)
                .to_rgb8()
                .save_with_format(path, ImageFormat::Png)
                .map_err(|e| format!("{shown}: {e}")),
            _ => Err(format!("{shown}: output must use .svg, .webp, or .png")),
        }
    }
}

/// Fill every pixel whose centre lies inside the circle.
fn fill_circle(image: &mut RgbaImage, x: f64, y: f64, radius: f64, color: Rgba<u8>) {
    let (width, height) = (i64::from(image.width()), i64::from(image.height()));
    let left = ((x - radius).floor() as i64).max(0);
    let right = ((x + radius).ceil() as i64).min(width - 1);
    let top = ((y - radius).floor() as i64).max(0);
    let bottom = ((y + radius).ceil() as i64).min(height - 1);
    for row in top..=bottom {
        for column in left..=right {
            let dx = column as f64 + 0.5 - x;
            let dy = row as f64 + 0.5 - y;
            if dx * dx + dy * dy <= radius * radius {
                image.put_pixel(column as u32, row as u32, color);
            }
        }
    }
}

/// Draw one line with anti-aliased glyph coverage blended over what is beneath.
fn draw_text(image: &mut RgbaImage, fonts: &Fonts, line: &TextLine) {
    let font = fonts.font(line.weight);
    let px = line.size as f32;
    let (width, height) = (i64::from(image.width()), i64::from(image.height()));
    let mut pen = match line.role {
        Role::Url => line.x - fonts.measure(&line.text, line.size, line.weight),
        Role::Title | Role::Description | Role::Product => line.x,
    };
    let baseline = (line.y + fonts.ascent(line.size, line.weight)).round_ties_even() as i64;
    let mut previous = None;
    for ch in line.text.chars() {
        if let Some(prev) = previous {
            pen += f64::from(font.horizontal_kern(prev, ch, px).unwrap_or(0.0));
        }
        let (metrics, coverage) = font.rasterize(ch, px);
        let left = pen.round_ties_even() as i64 + i64::from(metrics.xmin);
        let top = baseline - (i64::from(metrics.ymin) + metrics.height as i64);
        for row in 0..metrics.height {
            for column in 0..metrics.width {
                let alpha = f64::from(coverage[row * metrics.width + column]) / 255.0;
                let (x, y) = (left + column as i64, top + row as i64);
                if alpha == 0.0 || x < 0 || y < 0 || x >= width || y >= height {
                    continue;
                }
                let pixel = image.get_pixel_mut(x as u32, y as u32);
                for channel in 0..3 {
                    let under = f64::from(pixel.0[channel]);
                    let over = f64::from(line.color.rgb[channel]);
                    pixel.0[channel] =
                        (under * (1.0 - alpha) + over * alpha).round_ties_even() as u8;
                }
            }
        }
        pen += f64::from(metrics.advance_width);
        previous = Some(ch);
    }
}

/// HTML escaping of text content, quotes included.
fn escape(text: &str) -> String {
    let mut out = String::with_capacity(text.len());
    for ch in text.chars() {
        match ch {
            '&' => out.push_str("&amp;"),
            '<' => out.push_str("&lt;"),
            '>' => out.push_str("&gt;"),
            '"' => out.push_str("&quot;"),
            '\'' => out.push_str("&#x27;"),
            other => out.push(other),
        }
    }
    out
}
