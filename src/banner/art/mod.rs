//! The supported artwork registry and the seeded transformation every artwork shares.

mod forms;
mod signals;
mod structures;

use super::{Banner, Dot};

pub const SUPPORTED_LAYOUTS: [&str; 17] = [
    "benchmark-left",
    "flock-left",
    "focus-left",
    "forest-left",
    "fracture-left",
    "gate-left",
    "gauge-left",
    "latent-field-left",
    "layers-left",
    "orbit-left",
    "routes-left",
    "scan-left",
    "signal-left",
    "spark-left",
    "timeline-left",
    "vault-left",
    "waveform-left",
];

/// The configured layout's dots, stretched, sheared and re-weighted by the seed
/// around the artwork's design centre. The layout was validated by `Banner::new`.
pub(super) fn render(banner: &Banner) -> Vec<Dot> {
    let mut dots = Vec::new();
    let out = &mut dots;
    match banner.config.layout.as_str() {
        "benchmark-left" => structures::benchmark(banner, out),
        "flock-left" => forms::flock(banner, out),
        "focus-left" => signals::focus(banner, out),
        "forest-left" => structures::forest(banner, out),
        "fracture-left" => signals::fracture(banner, out),
        "gate-left" => signals::gate(banner, out),
        "gauge-left" => forms::gauge(banner, out),
        "latent-field-left" => signals::latent_field(banner, out),
        "layers-left" => structures::layers(banner, out),
        "orbit-left" => structures::orbit(banner, out),
        "routes-left" => structures::routes(banner, out),
        "scan-left" => forms::scan(banner, out),
        "signal-left" => signals::signal(banner, out),
        "spark-left" => signals::spark(banner, out),
        "timeline-left" => forms::timeline(banner, out),
        "vault-left" => forms::vault(banner, out),
        "waveform-left" => signals::waveform(banner, out),
        other => unreachable!("layout {other} passed validation but has no artwork"),
    }
    let scale = banner.scale();
    let center_x = 380.0 * scale;
    let center_y = 198.0 * scale;
    let stretch_x = banner.variant(0, 0.9, 1.1);
    let stretch_y = banner.variant(1, 0.88, 1.12);
    let shear = banner.variant(2, -0.06, 0.06);
    let radius_scale = banner.variant(3, 0.88, 1.16);
    let opacity_scale = banner.variant(4, 0.88, 1.08);
    dots.into_iter()
        .map(|(x, y, radius, opacity)| {
            let relative_x = x - center_x;
            let relative_y = y - center_y;
            (
                center_x + relative_x * stretch_x,
                center_y + relative_y * stretch_y + relative_x * shear,
                radius * radius_scale,
                (opacity * opacity_scale).min(1.0),
            )
        })
        .collect()
}
