"""Seeded networks, grouped forms and measurements for banner artwork."""

import math
from typing import TYPE_CHECKING, Iterable, Tuple

if TYPE_CHECKING:
    from ..banner import Banner


def routes_dots(banner: "Banner") -> Iterable[Tuple[float, float, float, float]]:
    """Yield a seeded provider graph with repository-specific topology."""
    tier_counts = (
        round(banner._variant(5, 2, 5)),
        round(banner._variant(6, 2, 4)),
        round(banner._variant(7, 1, 4)),
        round(banner._variant(8, 1, 3)),
    )
    tier_x = (55, 255, 475, 705)
    tiers = []
    seed_index = 9
    for tier, count in enumerate(tier_counts):
        spacing = 250 / max(1, count - 1)
        points = []
        for node in range(count):
            y = 73 + node * spacing + banner._variant(seed_index, -24, 24)
            points.append((tier_x[tier], y))
            seed_index += 1
        tiers.append(points)
    for tier in range(len(tiers) - 1):
        destinations = tiers[tier + 1]
        for node_index, start in enumerate(tiers[tier]):
            target_index = round(
                banner._variant(seed_index + node_index + tier * 5, 0, len(destinations) - 1)
            )
            yield from banner._line_dots(
                start, destinations[target_index], opacity=0.38 + tier * 0.08
            )
            if len(destinations) > 1 and (node_index + tier) % 2 == 0:
                second = destinations[(target_index + 1) % len(destinations)]
                yield from banner._line_dots(start, second, opacity=0.2)
    scale = banner._scale()
    for tier_index, tier in enumerate(tiers):
        for x, y in tier:
            final = tier_index == len(tiers) - 1
            yield x * scale, y * scale, (5.2 if final else 3.5) * scale, 0.3
            yield x * scale, y * scale, (2.1 if final else 1.6) * scale, 0.98


def benchmark_dots(banner: "Banner") -> Iterable[Tuple[float, float, float, float]]:
    """Yield repository-seeded measurements and a target threshold."""
    scale = banner._scale()
    bar_count = round(banner._variant(5, 6, 11))
    values = tuple(banner._variant(6 + index, 75, 285) for index in range(bar_count))
    baseline = banner._variant(20, 310, 340)
    gap = 625 / max(1, bar_count - 1)
    for index, value in enumerate(values):
        x = 68 + index * gap
        rows = max(1, round(value / 8))
        for row in range(rows + 1):
            y = baseline - row * 8
            progress = row / rows
            opacity = 0.24 + progress * 0.62
            yield x * scale, y * scale, 1.55 * scale, opacity
            yield (x + 7) * scale, y * scale, 1.05 * scale, opacity * 0.6
    threshold = banner._variant(21, 105, 175)
    yield from banner._line_dots((45, threshold), (718, threshold), spacing=11, opacity=0.54)
    yield from banner._line_dots((45, baseline), (718, baseline), spacing=9, opacity=0.28)


def orbit_dots(banner: "Banner") -> Iterable[Tuple[float, float, float, float]]:
    """Yield a uniquely seeded multi-agent orbital system."""
    scale = banner._scale()
    center_x = banner._variant(5, 325, 410)
    center_y = banner._variant(6, 165, 225)
    orbit_count = round(banner._variant(7, 2, 6))
    for orbit_index in range(orbit_count):
        radius_x = banner._variant(8 + orbit_index * 3, 95, 285)
        radius_y = banner._variant(9 + orbit_index * 3, 42, 135)
        rotation = banner._variant(10 + orbit_index * 3, -0.85, 0.85)
        dot_count = round(banner._variant(22 + orbit_index, 64, 110))
        for index in range(dot_count):
            angle = index / dot_count * math.tau
            raw_x = radius_x * math.cos(angle)
            raw_y = radius_y * math.sin(angle)
            x = center_x + raw_x * math.cos(rotation) - raw_y * math.sin(rotation)
            y = center_y + raw_x * math.sin(rotation) + raw_y * math.cos(rotation)
            opacity = 0.17 + 0.38 * (math.sin(angle + orbit_index) + 1) / 2
            yield x * scale, y * scale, 1.05 * scale, opacity
        node_angle = banner._variant(27 + orbit_index, 0, math.tau)
        raw_x = radius_x * math.cos(node_angle)
        raw_y = radius_y * math.sin(node_angle)
        x = center_x + raw_x * math.cos(rotation) - raw_y * math.sin(rotation)
        y = center_y + raw_x * math.sin(rotation) + raw_y * math.cos(rotation)
        yield x * scale, y * scale, 4.5 * scale, 0.32
        yield x * scale, y * scale, 2 * scale, 0.96
    yield center_x * scale, center_y * scale, 7 * scale, 0.25
    yield center_x * scale, center_y * scale, 2.8 * scale, 1


def layers_dots(banner: "Banner") -> Iterable[Tuple[float, float, float, float]]:
    """Yield repository-seeded data layers linked by a retrieval spine."""
    scale = banner._scale()
    layer_count = round(banner._variant(5, 3, 6))
    start_y = banner._variant(6, 72, 105)
    spacing_y = 250 / max(1, layer_count - 1)
    spine_x = banner._variant(7, 335, 430)
    event_ys = []
    for layer in range(layer_count):
        center_y = start_y + layer * spacing_y
        inset = layer * banner._variant(8, 10, 22)
        left = 78 + inset + banner._variant(9 + layer, -12, 12)
        right = 690 - inset + banner._variant(15 + layer, -12, 12)
        height = banner._variant(21 + layer, 21, 38)
        corners = (
            (left, center_y),
            (spine_x, center_y - height),
            (right, center_y),
            (spine_x, center_y + height),
        )
        opacity = 0.26 + layer / max(1, layer_count - 1) * 0.4
        for index in range(4):
            yield from banner._line_dots(
                corners[index], corners[(index + 1) % 4], spacing=7, opacity=opacity
            )
        event_ys.append(center_y)
    yield from banner._line_dots(
        (spine_x, 45), (spine_x, 350), spacing=10, opacity=0.72, radius=1.4
    )
    for y in event_ys:
        yield spine_x * scale, y * scale, 3.1 * scale, 0.95


def forest_dots(banner: "Banner") -> Iterable[Tuple[float, float, float, float]]:
    """Yield a layered forest suggested by the Polish name Las."""
    scale = banner._scale()
    for tree in range(11):
        x = 55 + tree * 64 + banner._variant(tree, -12, 12)
        height = banner._variant(tree + 11, 100, 245)
        base_y = 335
        top_y = base_y - height
        opacity = banner._variant(tree + 22, 0.3, 0.75)
        yield from banner._line_dots((x, base_y), (x, top_y), spacing=7, opacity=opacity)
        branch_count = max(4, round(height / 28))
        for branch in range(branch_count):
            progress = (branch + 1) / (branch_count + 1)
            y = base_y - height * progress
            width = (1 - progress) * banner._variant(tree + 4, 38, 62)
            yield from banner._line_dots((x, y), (x - width, y + 24), spacing=7, opacity=opacity)
            yield from banner._line_dots((x, y), (x + width, y + 24), spacing=7, opacity=opacity)


def flock_dots(banner: "Banner") -> Iterable[Tuple[float, float, float, float]]:
    """Yield coordinated V formations for Stado and creator communities."""
    scale = banner._scale()
    phase = banner._variant(3, -0.3, 0.3)
    for flock in range(4):
        anchor_x = 110 + flock * 150 + banner._variant(flock, -20, 20)
        anchor_y = 95 + flock * 66 + banner._variant(flock + 8, -22, 22)
        wing = banner._variant(flock + 16, 55, 95)
        for side in (-1, 1):
            for bird in range(9):
                progress = bird / 8
                x = anchor_x + progress * wing * 1.6
                y = anchor_y + side * progress * wing * 0.48 + math.sin(bird + phase) * 3
                yield x * scale, y * scale, 1.5 * scale, 0.4 + progress * 0.5
        yield anchor_x * scale, anchor_y * scale, 2.8 * scale, 0.95


def timeline_dots(banner: "Banner") -> Iterable[Tuple[float, float, float, float]]:
    """Yield a chronicle of events and documentary branches."""
    scale = banner._scale()
    center_y = banner._variant(2, 175, 225)
    yield from banner._line_dots((45, center_y), (720, center_y), spacing=7, opacity=0.62)
    event_count = round(banner._variant(3, 7, 11))
    for event in range(event_count):
        progress = (event + 1) / (event_count + 1)
        x = 45 + progress * 675
        direction = -1 if event % 2 == 0 else 1
        height = banner._variant(event + 8, 45, 135)
        end_y = center_y + direction * height
        yield from banner._line_dots((x, center_y), (x, end_y), spacing=8, opacity=0.48)
        yield x * scale, center_y * scale, 3 * scale, 0.95
        yield x * scale, end_y * scale, 2 * scale, 0.72


def gauge_dots(banner: "Banner") -> Iterable[Tuple[float, float, float, float]]:
    """Yield a calibrated gauge for Probierz and quality-control systems."""
    scale = banner._scale()
    center_x, center_y = 370, 292
    radius = banner._variant(1, 220, 275)
    for ring in range(3):
        adjusted = radius - ring * 20
        for index in range(86):
            angle = math.pi + index / 85 * math.pi
            x = center_x + adjusted * math.cos(angle)
            y = center_y + adjusted * math.sin(angle)
            yield x * scale, y * scale, (1.3 - ring * 0.12) * scale, 0.28 + ring * 0.12
    needle_angle = math.pi + banner._variant(4, 0.18, 0.82) * math.pi
    target = (
        center_x + radius * 0.82 * math.cos(needle_angle),
        center_y + radius * 0.82 * math.sin(needle_angle),
    )
    yield from banner._line_dots((center_x, center_y), target, spacing=6, opacity=0.9, radius=1.6)
    yield center_x * scale, center_y * scale, 6 * scale, 0.3
    yield center_x * scale, center_y * scale, 2.5 * scale, 1


def vault_dots(banner: "Banner") -> Iterable[Tuple[float, float, float, float]]:
    """Yield a secure layered vault and signed center."""
    scale = banner._scale()
    center_x, center_y = 370, 198
    for layer in range(5):
        half_width = 285 - layer * 42
        half_height = 145 - layer * 21
        corners = (
            (center_x - half_width, center_y - half_height),
            (center_x + half_width, center_y - half_height),
            (center_x + half_width, center_y + half_height),
            (center_x - half_width, center_y + half_height),
        )
        for index in range(4):
            yield from banner._line_dots(
                corners[index],
                corners[(index + 1) % 4],
                spacing=8 + layer,
                opacity=0.22 + layer * 0.1,
            )
    for index in range(48):
        angle = index / 48 * math.tau
        radius = 40 + math.sin(index * 0.7) * 3
        yield (
            (center_x + math.cos(angle) * radius) * scale,
            (center_y + math.sin(angle) * radius) * scale,
            1.4 * scale,
            0.72,
        )
    yield center_x * scale, center_y * scale, 3.2 * scale, 1


def scan_dots(banner: "Banner") -> Iterable[Tuple[float, float, float, float]]:
    """Yield a code-analysis grid with a moving scan line and finding."""
    scale = banner._scale()
    scan_x = banner._variant(3, 210, 585)
    finding_y = banner._variant(4, 95, 295)
    for column in range(28):
        x = 48 + column * 24
        for row in range(13):
            y = 54 + row * 24
            distance = abs(x - scan_x)
            opacity = 0.18 + max(0, 1 - distance / 95) * 0.55
            yield x * scale, y * scale, 1.1 * scale, opacity
    yield from banner._line_dots((scan_x, 42), (scan_x, 350), spacing=6, opacity=0.88, radius=1.5)
    for index in range(36):
        angle = index / 36 * math.tau
        radius = 26
        yield (
            (scan_x + math.cos(angle) * radius) * scale,
            (finding_y + math.sin(angle) * radius) * scale,
            1.5 * scale,
            0.85,
        )
