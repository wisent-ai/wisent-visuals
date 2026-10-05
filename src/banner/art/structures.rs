//! Seeded networks, measurements, orbits, layers and forests for banner artwork.

use std::f64::consts::TAU;

use crate::banner::{Banner, Dot};

fn count(value: f64) -> usize {
    value.round_ties_even() as usize
}

/// A seeded provider graph with repository-specific topology.
pub(super) fn routes(b: &Banner, out: &mut Vec<Dot>) {
    let tier_counts = [
        count(b.variant(5, 2.0, 5.0)),
        count(b.variant(6, 2.0, 4.0)),
        count(b.variant(7, 1.0, 4.0)),
        count(b.variant(8, 1.0, 3.0)),
    ];
    let tier_x = [55.0, 255.0, 475.0, 705.0];
    let mut tiers: Vec<Vec<(f64, f64)>> = Vec::with_capacity(tier_counts.len());
    let mut seed_index = 9;
    for (tier, &nodes) in tier_counts.iter().enumerate() {
        let spacing = 250.0 / (nodes.max(2) - 1) as f64;
        let mut points = Vec::with_capacity(nodes);
        for node in 0..nodes {
            let y = 73.0 + node as f64 * spacing + b.variant(seed_index, -24.0, 24.0);
            points.push((tier_x[tier], y));
            seed_index += 1;
        }
        tiers.push(points);
    }
    for tier in 0..tiers.len() - 1 {
        let destinations = &tiers[tier + 1];
        if destinations.is_empty() {
            continue;
        }
        for (node_index, &start) in tiers[tier].iter().enumerate() {
            let last = (destinations.len() - 1) as f64;
            let target_index = count(b.variant(seed_index + node_index + tier * 5, 0.0, last));
            let opacity = 0.38 + tier as f64 * 0.08;
            b.line_dots(out, start, destinations[target_index], 8.0, opacity, 1.1);
            if destinations.len() > 1 && (node_index + tier) % 2 == 0 {
                let second = destinations[(target_index + 1) % destinations.len()];
                b.line_dots(out, start, second, 8.0, 0.2, 1.1);
            }
        }
    }
    let scale = b.scale();
    let final_tier = tiers.len() - 1;
    for (tier_index, tier) in tiers.iter().enumerate() {
        let (halo, core) = if tier_index == final_tier {
            (5.2, 2.1)
        } else {
            (3.5, 1.6)
        };
        for &(x, y) in tier {
            out.push((x * scale, y * scale, halo * scale, 0.3));
            out.push((x * scale, y * scale, core * scale, 0.98));
        }
    }
}

/// Repository-seeded measurements and a target threshold.
pub(super) fn benchmark(b: &Banner, out: &mut Vec<Dot>) {
    let scale = b.scale();
    let bar_count = count(b.variant(5, 6.0, 11.0));
    let baseline = b.variant(20, 310.0, 340.0);
    let gap = 625.0 / (bar_count.max(2) - 1) as f64;
    for index in 0..bar_count {
        let value = b.variant(6 + index, 75.0, 285.0);
        let x = 68.0 + index as f64 * gap;
        let rows = count(value / 8.0).max(1);
        for row in 0..=rows {
            let y = baseline - row as f64 * 8.0;
            let opacity = 0.24 + row as f64 / rows as f64 * 0.62;
            out.push((x * scale, y * scale, 1.55 * scale, opacity));
            out.push(((x + 7.0) * scale, y * scale, 1.05 * scale, opacity * 0.6));
        }
    }
    let threshold = b.variant(21, 105.0, 175.0);
    b.line_dots(out, (45.0, threshold), (718.0, threshold), 11.0, 0.54, 1.1);
    b.line_dots(out, (45.0, baseline), (718.0, baseline), 9.0, 0.28, 1.1);
}

/// A uniquely seeded multi-agent orbital system.
pub(super) fn orbit(b: &Banner, out: &mut Vec<Dot>) {
    let scale = b.scale();
    let center_x = b.variant(5, 325.0, 410.0);
    let center_y = b.variant(6, 165.0, 225.0);
    for orbit_index in 0..count(b.variant(7, 2.0, 6.0)) {
        let radius_x = b.variant(8 + orbit_index * 3, 95.0, 285.0);
        let radius_y = b.variant(9 + orbit_index * 3, 42.0, 135.0);
        let rotation = b.variant(10 + orbit_index * 3, -0.85, 0.85);
        let place = |angle: f64| {
            let raw_x = radius_x * angle.cos();
            let raw_y = radius_y * angle.sin();
            (
                center_x + raw_x * rotation.cos() - raw_y * rotation.sin(),
                center_y + raw_x * rotation.sin() + raw_y * rotation.cos(),
            )
        };
        let dot_count = count(b.variant(22 + orbit_index, 64.0, 110.0));
        for index in 0..dot_count {
            let angle = index as f64 / dot_count as f64 * TAU;
            let (x, y) = place(angle);
            let opacity = 0.17 + 0.38 * ((angle + orbit_index as f64).sin() + 1.0) / 2.0;
            out.push((x * scale, y * scale, 1.05 * scale, opacity));
        }
        let (x, y) = place(b.variant(27 + orbit_index, 0.0, TAU));
        out.push((x * scale, y * scale, 4.5 * scale, 0.32));
        out.push((x * scale, y * scale, 2.0 * scale, 0.96));
    }
    out.push((center_x * scale, center_y * scale, 7.0 * scale, 0.25));
    out.push((center_x * scale, center_y * scale, 2.8 * scale, 1.0));
}

/// Repository-seeded data layers linked by a retrieval spine.
pub(super) fn layers(b: &Banner, out: &mut Vec<Dot>) {
    let scale = b.scale();
    let layer_count = count(b.variant(5, 3.0, 6.0));
    let start_y = b.variant(6, 72.0, 105.0);
    let spacing_y = 250.0 / (layer_count.max(2) - 1) as f64;
    let spine_x = b.variant(7, 335.0, 430.0);
    let mut event_ys = Vec::with_capacity(layer_count);
    for layer in 0..layer_count {
        let center_y = start_y + layer as f64 * spacing_y;
        let inset = layer as f64 * b.variant(8, 10.0, 22.0);
        let left = 78.0 + inset + b.variant(9 + layer, -12.0, 12.0);
        let right = 690.0 - inset + b.variant(15 + layer, -12.0, 12.0);
        let height = b.variant(21 + layer, 21.0, 38.0);
        let corners = [
            (left, center_y),
            (spine_x, center_y - height),
            (right, center_y),
            (spine_x, center_y + height),
        ];
        let opacity = 0.26 + layer as f64 / (layer_count.max(2) - 1) as f64 * 0.4;
        for index in 0..4 {
            b.line_dots(
                out,
                corners[index],
                corners[(index + 1) % 4],
                7.0,
                opacity,
                1.1,
            );
        }
        event_ys.push(center_y);
    }
    b.line_dots(out, (spine_x, 45.0), (spine_x, 350.0), 10.0, 0.72, 1.4);
    for y in event_ys {
        out.push((spine_x * scale, y * scale, 3.1 * scale, 0.95));
    }
}

/// A layered forest suggested by the Polish name Las.
pub(super) fn forest(b: &Banner, out: &mut Vec<Dot>) {
    for tree in 0..11 {
        let x = 55.0 + tree as f64 * 64.0 + b.variant(tree, -12.0, 12.0);
        let height = b.variant(tree + 11, 100.0, 245.0);
        let base_y = 335.0;
        let opacity = b.variant(tree + 22, 0.3, 0.75);
        b.line_dots(out, (x, base_y), (x, base_y - height), 7.0, opacity, 1.1);
        let branch_count = count(height / 28.0).max(4);
        let reach = b.variant(tree + 4, 38.0, 62.0);
        for branch in 0..branch_count {
            let progress = (branch + 1) as f64 / (branch_count + 1) as f64;
            let y = base_y - height * progress;
            let width = (1.0 - progress) * reach;
            b.line_dots(out, (x, y), (x - width, y + 24.0), 7.0, opacity, 1.1);
            b.line_dots(out, (x, y), (x + width, y + 24.0), 7.0, opacity, 1.1);
        }
    }
}
