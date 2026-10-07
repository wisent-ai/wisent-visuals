//! Canonical Wisent visual identity: the brand colours, the typeface and the
//! logo every banner and chart is drawn with.

/// Brand colours by role, as declared in Wisent's visual identity.
pub const BRAND_COLORS: [(&str, &str); 8] = [
    ("background", "#050605"),
    ("surface", "#121212"),
    ("primary", "#C5FFC8"),
    ("secondary", "#B0E3B3"),
    ("tertiary", "#90B892"),
    ("deep", "#5A715B"),
    ("muted", "#769978"),
    ("grid", "#2D3130"),
];

/// The brand colour for `role`; `None` for a role the identity does not declare.
pub fn brand_color(role: &str) -> Option<&'static str> {
    BRAND_COLORS
        .iter()
        .find(|(name, _)| *name == role)
        .map(|(_, value)| *value)
}

/// The family name every SVG asks for; the font files below carry it.
pub const FONT_FAMILY: &str = "Hubot Sans";

pub const REGULAR_TTF: &[u8] = include_bytes!("../assets/fonts/HubotSans-Regular.ttf");
pub const BOLD_TTF: &[u8] = include_bytes!("../assets/fonts/HubotSans-Bold.ttf");
pub const LOGO_PNG: &[u8] = include_bytes!("../assets/brand/wisent-logo.png");
