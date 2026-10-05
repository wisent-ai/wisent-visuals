//! Seeded signal fields, waves and transitions for banner artwork.

use std::f64::consts::{PI, TAU};

use crate::banner::{Banner, Dot};

fn count(value: f64) -> usize {
    value.round_ties_even() as usize
}

/// A seeded activation field converging into controlled channels.
pub(super) fn latent_field(b: &Banner, out: &mut Vec<Dot>) {
    let scale = b.scale();
    let lane_count = count(b.variant(5, 13.0, 20.0));
    let column_count = count(b.variant(6, 58.0, 78.0));
    let gate_progress = b.variant(7, 0.42, 0.62);
    let center_frequency = b.variant(8, 1.25, 2.35);
    let center_phase = b.variant(9, -1.2, 0.5);
    let turbulence_a = b.variant(10, 0.17, 0.34);
    let turbulence_b = b.variant(11, 0.07, 0.16);
    for lane in 0..lane_count {
        let lane = lane as f64;
        let lane_offset = lane - (lane_count as f64 - 1.0) / 2.0;
        for column in 0..column_count {
            let column = column as f64;
            let progress = column / (column_count as f64 - 1.0);
            let x = (42.0 + progress * 660.0) * scale;
            let damping = 1.0 / (1.0 + ((progress - gate_progress) * 13.0).exp());
            let center = 198.0 + 32.0 * (progress * PI * center_frequency + center_phase).sin();
            let turbulence = (column * turbulence_a + lane * 0.79).sin() * 23.0
                + (column * turbulence_b + lane * 1.31).sin() * 13.0;
            let y = (center + lane_offset * 8.6 + turbulence * damping) * scale;
            let edge_fade = (progress / 0.12).min((1.0 - progress) / 0.12).min(1.0);
            let boundary_glow = (-((progress - gate_progress) / 0.13).powi(2)).exp();
            let opacity = (edge_fade * (0.34 + boundary_glow * 0.46)).max(0.12);
            out.push((x, y, (0.9 + boundary_glow * 0.65) * scale, opacity));
        }
    }

    let steering_phase = b.variant(12, 0.0, TAU);
    for column in 0..82 {
        let column = f64::from(column);
        let progress = column / 81.0;
        let x = (35.0 + progress * 680.0) * scale;
        let damping = 1.0 / (1.0 + ((progress - gate_progress) * 13.0).exp());
        let y = (205.0
            + 31.0 * (progress * PI * center_frequency + center_phase).sin()
            + (column * 0.27 + steering_phase).sin() * 24.0 * damping)
            * scale;
        let fade = (progress / 0.08).min((1.0 - progress) / 0.08).min(1.0);
        out.push((x, y, 1.8 * scale, (0.95 * fade).max(0.25)));
    }

    let gate_x = 42.0 + gate_progress * 660.0;
    for row in (0..23).filter(|row| !(9..=13).contains(row)) {
        let y = 67.0 + f64::from(row) * 11.5;
        out.push((gate_x * scale, y * scale, 1.25 * scale, 0.58));
    }
}

/// A repository-seeded layered neural waveform.
pub(super) fn waveform(b: &Banner, out: &mut Vec<Dot>) {
    let scale = b.scale();
    let frequency_a = b.variant(5, 0.2, 0.42);
    let frequency_b = b.variant(6, 0.52, 0.91);
    let frequency_c = b.variant(7, 1.05, 1.55);
    let phase = b.variant(8, 0.0, TAU);
    let strength = b.variant(9, 54.0, 86.0);
    let half_bands = count(b.variant(10, 3.0, 7.0)) as i64 / 2;
    let envelope_power = b.variant(11, 0.55, 1.1);
    let mirror_share = b.variant(12, 0.25, 0.58);
    for column in 0..112 {
        let column = f64::from(column);
        let progress = column / 111.0;
        let x = 34.0 + progress * 690.0;
        let envelope = (progress * PI).sin().powf(envelope_power);
        let signal = (column * frequency_a + phase).sin()
            + 0.55 * (column * frequency_b + 0.8).sin()
            + 0.25 * (column * frequency_c).sin();
        let amplitude = signal * strength * envelope;
        for band in -half_bands..=half_bands {
            let distance = band.abs() as f64;
            let y = 198.0 + amplitude + band as f64 * 7.0;
            let opacity = (0.9 - distance * 0.15).max(0.2);
            out.push((
                x * scale,
                y * scale,
                (1.65 - distance * 0.13).max(0.8) * scale,
                opacity,
            ));
        }
        let mirror = 198.0 - amplitude * mirror_share;
        out.push((x * scale, mirror * scale, 1.05 * scale, 0.28));
    }
    b.line_dots(out, (34.0, 198.0), (724.0, 198.0), 12.0, 0.22, 1.1);
}

/// Repository-seeded coordinated software signals.
pub(super) fn signal(b: &Banner, out: &mut Vec<Dot>) {
    let scale = b.scale();
    let lane_count = count(b.variant(5, 6.0, 12.0));
    let frequency = b.variant(6, 1.4, 3.4);
    let phase = b.variant(7, 0.0, TAU);
    let amplitude = b.variant(8, 11.0, 31.0);
    let lane_spacing = 270.0 / (lane_count.max(2) - 1) as f64;
    for lane in 0..lane_count {
        let lane = lane as f64;
        for column in 0..76 {
            let progress = f64::from(column) / 75.0;
            let x = 34.0 + progress * 690.0;
            let y = 63.0
                + lane * lane_spacing
                + (progress * PI * frequency + lane * 0.72 + phase).sin() * amplitude
                + (progress * PI).sin() * (lane - (lane_count as f64 - 1.0) / 2.0) * 4.0;
            let fade = (progress / 0.1).min((1.0 - progress) / 0.1).min(1.0);
            out.push((x * scale, y * scale, 1.2 * scale, (fade * 0.58).max(0.12)));
        }
    }
    for node in 0..count(b.variant(9, 3.0, 7.0)) {
        let x = b.variant(10 + node * 2, 90.0, 680.0);
        let y = b.variant(11 + node * 2, 75.0, 320.0);
        out.push((x * scale, y * scale, 4.2 * scale, 0.3));
        out.push((x * scale, y * scale, 1.8 * scale, 0.95));
    }
}

/// An asymmetric spark expanding into model activations.
pub(super) fn spark(b: &Banner, out: &mut Vec<Dot>) {
    let scale = b.scale();
    let center = (
        355.0 + b.variant(1, -28.0, 28.0),
        198.0 + b.variant(2, -18.0, 18.0),
    );
    let ray_count = count(b.variant(3, 11.0, 17.0));
    let phase = b.variant(4, 0.0, TAU);
    for ray in 0..ray_count {
        let angle = phase + ray as f64 / ray_count as f64 * TAU;
        let length = b.variant(5 + ray, 85.0, 275.0);
        for step in 4..count(length / 7.0) {
            let step = step as f64;
            let progress = step * 7.0 / length;
            let wobble = (step * 0.47 + ray as f64).sin() * 7.0 * progress;
            let x = center.0 + angle.cos() * step * 7.0 - angle.sin() * wobble;
            let y = center.1 + angle.sin() * step * 7.0 + angle.cos() * wobble;
            let opacity = ((1.0 - progress) * 0.82).max(0.12);
            out.push((
                x * scale,
                y * scale,
                (1.7 - progress * 0.65) * scale,
                opacity,
            ));
        }
    }
    out.push((center.0 * scale, center.1 * scale, 7.0 * scale, 0.25));
    out.push((center.0 * scale, center.1 * scale, 2.8 * scale, 1.0));
}

/// Many signals collapsing into one focal point.
pub(super) fn focus(b: &Banner, out: &mut Vec<Dot>) {
    let scale = b.scale();
    let target = (b.variant(1, 315.0, 430.0), b.variant(2, 155.0, 240.0));
    for source in 0..16 {
        let progress = f64::from(source) / 15.0;
        let start = match source % 4 {
            0 => (35.0, 45.0 + progress * 300.0),
            1 => (720.0, 45.0 + progress * 300.0),
            2 => (55.0 + progress * 640.0, 45.0),
            _ => (55.0 + progress * 640.0, 350.0),
        };
        b.line_dots(out, start, target, 10.0, 0.34, 1.1);
    }
    out.push((target.0 * scale, target.1 * scale, 11.0 * scale, 0.17));
    out.push((target.0 * scale, target.1 * scale, 4.5 * scale, 1.0));
}

/// Broken constraints and diverging response paths.
pub(super) fn fracture(b: &Banner, out: &mut Vec<Dot>) {
    let center_x = b.variant(1, 330.0, 420.0);
    let crack = [
        (center_x - 45.0, 35.0),
        (center_x + 18.0, 105.0),
        (center_x - 26.0, 166.0),
        (center_x + 34.0, 231.0),
        (center_x - 12.0, 292.0),
        (center_x + 48.0, 360.0),
    ];
    for pair in crack.windows(2) {
        b.line_dots(out, pair[0], pair[1], 5.0, 0.92, 1.1);
    }
    for shard in 0..13 {
        let origin = crack[shard % crack.len()];
        let direction = if shard % 2 == 0 { -1.0 } else { 1.0 };
        let length = b.variant(shard + 8, 65.0, 245.0);
        let end = (
            origin.0 + direction * length,
            origin.1 + b.variant(shard + 20, -55.0, 55.0),
        );
        b.line_dots(out, origin, end, 8.0, 0.28 + (shard % 3) as f64 * 0.1, 1.1);
    }
}

/// Routed signals crossing a controlled gate.
pub(super) fn gate(b: &Banner, out: &mut Vec<Dot>) {
    let scale = b.scale();
    let gate_x = b.variant(2, 330.0, 430.0);
    let gap_center = b.variant(3, 150.0, 245.0);
    for pillar_x in [gate_x - 28.0, gate_x + 28.0] {
        for row in 0..34 {
            let y = 30.0 + f64::from(row) * 10.0;
            if (y - gap_center).abs() < 42.0 {
                continue;
            }
            out.push((pillar_x * scale, y * scale, 1.6 * scale, 0.7));
        }
    }
    for route in 0..9 {
        let source_y = 58.0 + route as f64 * 34.0;
        let target_y = gap_center + (route as f64 - 4.0) * 10.0;
        let exit_y = 78.0 + route as f64 * 29.0 + b.variant(route + 7, -14.0, 14.0);
        b.line_dots(
            out,
            (40.0, source_y),
            (gate_x - 32.0, target_y),
            8.0,
            0.3,
            1.1,
        );
        b.line_dots(
            out,
            (gate_x + 32.0, target_y),
            (720.0, exit_y),
            8.0,
            0.52,
            1.1,
        );
    }
}
