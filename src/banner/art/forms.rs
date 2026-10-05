//! Flocks, timelines, gauges, vaults and scans for banner artwork.

use std::f64::consts::{PI, TAU};

use crate::banner::{Banner, Dot};

/// Coordinated V formations for Stado and creator communities.
pub(super) fn flock(b: &Banner, out: &mut Vec<Dot>) {
    let scale = b.scale();
    let phase = b.variant(3, -0.3, 0.3);
    for flock in 0..4 {
        let anchor_x = 110.0 + flock as f64 * 150.0 + b.variant(flock, -20.0, 20.0);
        let anchor_y = 95.0 + flock as f64 * 66.0 + b.variant(flock + 8, -22.0, 22.0);
        let wing = b.variant(flock + 16, 55.0, 95.0);
        for side in [-1.0, 1.0] {
            for bird in 0..9 {
                let progress = f64::from(bird) / 8.0;
                let x = anchor_x + progress * wing * 1.6;
                let y = anchor_y
                    + side * progress * wing * 0.48
                    + (f64::from(bird) + phase).sin() * 3.0;
                out.push((x * scale, y * scale, 1.5 * scale, 0.4 + progress * 0.5));
            }
        }
        out.push((anchor_x * scale, anchor_y * scale, 2.8 * scale, 0.95));
    }
}

/// A chronicle of events and documentary branches.
pub(super) fn timeline(b: &Banner, out: &mut Vec<Dot>) {
    let scale = b.scale();
    let center_y = b.variant(2, 175.0, 225.0);
    b.line_dots(out, (45.0, center_y), (720.0, center_y), 7.0, 0.62, 1.1);
    let event_count = b.variant(3, 7.0, 11.0).round_ties_even() as usize;
    for event in 0..event_count {
        let progress = (event + 1) as f64 / (event_count + 1) as f64;
        let x = 45.0 + progress * 675.0;
        let direction = if event % 2 == 0 { -1.0 } else { 1.0 };
        let end_y = center_y + direction * b.variant(event + 8, 45.0, 135.0);
        b.line_dots(out, (x, center_y), (x, end_y), 8.0, 0.48, 1.1);
        out.push((x * scale, center_y * scale, 3.0 * scale, 0.95));
        out.push((x * scale, end_y * scale, 2.0 * scale, 0.72));
    }
}

/// A calibrated gauge for Probierz and quality-control systems.
pub(super) fn gauge(b: &Banner, out: &mut Vec<Dot>) {
    let scale = b.scale();
    let (center_x, center_y) = (370.0, 292.0);
    let radius = b.variant(1, 220.0, 275.0);
    for ring in 0..3 {
        let ring = f64::from(ring);
        let adjusted = radius - ring * 20.0;
        for index in 0..86 {
            let angle = PI + f64::from(index) / 85.0 * PI;
            let x = center_x + adjusted * angle.cos();
            let y = center_y + adjusted * angle.sin();
            out.push((
                x * scale,
                y * scale,
                (1.3 - ring * 0.12) * scale,
                0.28 + ring * 0.12,
            ));
        }
    }
    let needle_angle = PI + b.variant(4, 0.18, 0.82) * PI;
    let target = (
        center_x + radius * 0.82 * needle_angle.cos(),
        center_y + radius * 0.82 * needle_angle.sin(),
    );
    b.line_dots(out, (center_x, center_y), target, 6.0, 0.9, 1.6);
    out.push((center_x * scale, center_y * scale, 6.0 * scale, 0.3));
    out.push((center_x * scale, center_y * scale, 2.5 * scale, 1.0));
}

/// A secure layered vault and signed centre.
pub(super) fn vault(b: &Banner, out: &mut Vec<Dot>) {
    let scale = b.scale();
    let (center_x, center_y) = (370.0, 198.0);
    for layer in 0..5 {
        let layer = f64::from(layer);
        let half_width = 285.0 - layer * 42.0;
        let half_height = 145.0 - layer * 21.0;
        let corners = [
            (center_x - half_width, center_y - half_height),
            (center_x + half_width, center_y - half_height),
            (center_x + half_width, center_y + half_height),
            (center_x - half_width, center_y + half_height),
        ];
        for index in 0..4 {
            b.line_dots(
                out,
                corners[index],
                corners[(index + 1) % 4],
                8.0 + layer,
                0.22 + layer * 0.1,
                1.1,
            );
        }
    }
    for index in 0..48 {
        let index = f64::from(index);
        let angle = index / 48.0 * TAU;
        let radius = 40.0 + (index * 0.7).sin() * 3.0;
        out.push((
            (center_x + angle.cos() * radius) * scale,
            (center_y + angle.sin() * radius) * scale,
            1.4 * scale,
            0.72,
        ));
    }
    out.push((center_x * scale, center_y * scale, 3.2 * scale, 1.0));
}

/// A code-analysis grid with a moving scan line and a finding.
pub(super) fn scan(b: &Banner, out: &mut Vec<Dot>) {
    let scale = b.scale();
    let scan_x = b.variant(3, 210.0, 585.0);
    let finding_y = b.variant(4, 95.0, 295.0);
    for column in 0..28 {
        let x = 48.0 + f64::from(column) * 24.0;
        for row in 0..13 {
            let y = 54.0 + f64::from(row) * 24.0;
            let opacity = 0.18 + (1.0 - (x - scan_x).abs() / 95.0).max(0.0) * 0.55;
            out.push((x * scale, y * scale, 1.1 * scale, opacity));
        }
    }
    b.line_dots(out, (scan_x, 42.0), (scan_x, 350.0), 6.0, 0.88, 1.5);
    for index in 0..36 {
        let angle = f64::from(index) / 36.0 * TAU;
        out.push((
            (scan_x + angle.cos() * 26.0) * scale,
            (finding_y + angle.sin() * 26.0) * scale,
            1.5 * scale,
            0.85,
        ));
    }
}
