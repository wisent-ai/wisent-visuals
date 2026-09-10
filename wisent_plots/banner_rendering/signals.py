"""Seeded signal fields, waves and transitions for banner artwork."""

import math
from typing import TYPE_CHECKING, Iterable, Tuple

if TYPE_CHECKING:
    from ..banner import Banner


def latent_field_dots(banner: "Banner") -> Iterable[Tuple[float, float, float, float]]:
    """Yield a seeded activation field converging into controlled channels."""
    scale = banner._scale()
    lane_count = round(banner._variant(5, 13, 20))
    column_count = round(banner._variant(6, 58, 78))
    gate_progress = banner._variant(7, 0.42, 0.62)
    center_frequency = banner._variant(8, 1.25, 2.35)
    center_phase = banner._variant(9, -1.2, 0.5)
    turbulence_a = banner._variant(10, 0.17, 0.34)
    turbulence_b = banner._variant(11, 0.07, 0.16)

    for lane in range(lane_count):
        lane_offset = lane - (lane_count - 1) / 2
        for column in range(column_count):
            progress = column / (column_count - 1)
            x = (42 + progress * 660) * scale
            damping = 1 / (1 + math.exp((progress - gate_progress) * 13))
            center = 198 + 32 * math.sin(progress * math.pi * center_frequency + center_phase)
            turbulence = (
                math.sin(column * turbulence_a + lane * 0.79) * 23
                + math.sin(column * turbulence_b + lane * 1.31) * 13
            )
            y = (center + lane_offset * 8.6 + turbulence * damping) * scale
            edge_fade = min(progress / 0.12, (1 - progress) / 0.12, 1)
            boundary_glow = math.exp(-(((progress - gate_progress) / 0.13) ** 2))
            opacity = max(0.12, edge_fade * (0.34 + boundary_glow * 0.46))
            radius = (0.9 + boundary_glow * 0.65) * scale
            yield x, y, radius, opacity

    steering_phase = banner._variant(12, 0, math.tau)
    for column in range(82):
        progress = column / 81
        x = (35 + progress * 680) * scale
        damping = 1 / (1 + math.exp((progress - gate_progress) * 13))
        y = (
            205
            + 31 * math.sin(progress * math.pi * center_frequency + center_phase)
            + math.sin(column * 0.27 + steering_phase) * 24 * damping
        ) * scale
        fade = min(progress / 0.08, (1 - progress) / 0.08, 1)
        yield x, y, 1.8 * scale, max(0.25, 0.95 * fade)

    gate_x = 42 + gate_progress * 660
    for row in range(23):
        if 9 <= row <= 13:
            continue
        y = 67 + row * 11.5
        yield gate_x * scale, y * scale, 1.25 * scale, 0.58


def waveform_dots(banner: "Banner") -> Iterable[Tuple[float, float, float, float]]:
    """Yield a repository-seeded layered neural waveform."""
    scale = banner._scale()
    frequency_a = banner._variant(5, 0.2, 0.42)
    frequency_b = banner._variant(6, 0.52, 0.91)
    frequency_c = banner._variant(7, 1.05, 1.55)
    phase = banner._variant(8, 0, math.tau)
    strength = banner._variant(9, 54, 86)
    band_count = round(banner._variant(10, 3, 7))
    half_bands = band_count // 2
    for column in range(112):
        progress = column / 111
        x = 34 + progress * 690
        envelope = math.sin(progress * math.pi) ** banner._variant(11, 0.55, 1.1)
        signal = (
            math.sin(column * frequency_a + phase)
            + 0.55 * math.sin(column * frequency_b + 0.8)
            + 0.25 * math.sin(column * frequency_c)
        )
        amplitude = signal * strength * envelope
        for band in range(-half_bands, half_bands + 1):
            y = 198 + amplitude + band * 7
            opacity = max(0.2, 0.9 - abs(band) * 0.15)
            yield x * scale, y * scale, max(0.8, 1.65 - abs(band) * 0.13) * scale, opacity
        mirror = 198 - amplitude * banner._variant(12, 0.25, 0.58)
        yield x * scale, mirror * scale, 1.05 * scale, 0.28
    yield from banner._line_dots((34, 198), (724, 198), spacing=12, opacity=0.22)


def signal_dots(banner: "Banner") -> Iterable[Tuple[float, float, float, float]]:
    """Yield repository-seeded coordinated software signals."""
    scale = banner._scale()
    lane_count = round(banner._variant(5, 6, 12))
    frequency = banner._variant(6, 1.4, 3.4)
    phase = banner._variant(7, 0, math.tau)
    amplitude = banner._variant(8, 11, 31)
    lane_spacing = 270 / max(1, lane_count - 1)
    for lane in range(lane_count):
        for column in range(76):
            progress = column / 75
            x = 34 + progress * 690
            y = (
                63
                + lane * lane_spacing
                + math.sin(progress * math.pi * frequency + lane * 0.72 + phase) * amplitude
                + math.sin(progress * math.pi) * (lane - (lane_count - 1) / 2) * 4
            )
            fade = min(progress / 0.1, (1 - progress) / 0.1, 1)
            yield x * scale, y * scale, 1.2 * scale, max(0.12, fade * 0.58)
    node_count = round(banner._variant(9, 3, 7))
    for node in range(node_count):
        x = banner._variant(10 + node * 2, 90, 680)
        y = banner._variant(11 + node * 2, 75, 320)
        yield x * scale, y * scale, 4.2 * scale, 0.3
        yield x * scale, y * scale, 1.8 * scale, 0.95


def spark_dots(banner: "Banner") -> Iterable[Tuple[float, float, float, float]]:
    """Yield an asymmetric spark expanding into model activations."""
    scale = banner._scale()
    center = (355 + banner._variant(1, -28, 28), 198 + banner._variant(2, -18, 18))
    ray_count = round(banner._variant(3, 11, 17))
    phase = banner._variant(4, 0, math.tau)
    for ray in range(ray_count):
        angle = phase + ray / ray_count * math.tau
        length = banner._variant(5 + ray, 85, 275)
        for step in range(4, round(length / 7)):
            progress = step * 7 / length
            wobble = math.sin(step * 0.47 + ray) * 7 * progress
            x = center[0] + math.cos(angle) * step * 7 - math.sin(angle) * wobble
            y = center[1] + math.sin(angle) * step * 7 + math.cos(angle) * wobble
            opacity = max(0.12, (1 - progress) * 0.82)
            yield x * scale, y * scale, (1.7 - progress * 0.65) * scale, opacity
    yield center[0] * scale, center[1] * scale, 7 * scale, 0.25
    yield center[0] * scale, center[1] * scale, 2.8 * scale, 1


def focus_dots(banner: "Banner") -> Iterable[Tuple[float, float, float, float]]:
    """Yield many signals collapsing into one focal point."""
    scale = banner._scale()
    target_x = banner._variant(1, 315, 430)
    target_y = banner._variant(2, 155, 240)
    for source in range(16):
        edge = source % 4
        progress = source / 15
        if edge == 0:
            start = (35, 45 + progress * 300)
        elif edge == 1:
            start = (720, 45 + progress * 300)
        elif edge == 2:
            start = (55 + progress * 640, 45)
        else:
            start = (55 + progress * 640, 350)
        yield from banner._line_dots(start, (target_x, target_y), spacing=10, opacity=0.34)
    yield target_x * scale, target_y * scale, 11 * scale, 0.17
    yield target_x * scale, target_y * scale, 4.5 * scale, 1


def fracture_dots(banner: "Banner") -> Iterable[Tuple[float, float, float, float]]:
    """Yield broken constraints and diverging response paths."""
    center_x = banner._variant(1, 330, 420)
    crack = (
        (center_x - 45, 35),
        (center_x + 18, 105),
        (center_x - 26, 166),
        (center_x + 34, 231),
        (center_x - 12, 292),
        (center_x + 48, 360),
    )
    for index in range(len(crack) - 1):
        yield from banner._line_dots(crack[index], crack[index + 1], spacing=5, opacity=0.92)
    for shard in range(13):
        origin = crack[shard % len(crack)]
        direction = -1 if shard % 2 == 0 else 1
        length = banner._variant(shard + 8, 65, 245)
        end = (
            origin[0] + direction * length,
            origin[1] + banner._variant(shard + 20, -55, 55),
        )
        yield from banner._line_dots(origin, end, spacing=8, opacity=0.28 + shard % 3 * 0.1)


def gate_dots(banner: "Banner") -> Iterable[Tuple[float, float, float, float]]:
    """Yield routed signals crossing a controlled gate."""
    scale = banner._scale()
    gate_x = banner._variant(2, 330, 430)
    gap_center = banner._variant(3, 150, 245)
    for pillar_x in (gate_x - 28, gate_x + 28):
        for row in range(34):
            y = 30 + row * 10
            if abs(y - gap_center) < 42:
                continue
            yield pillar_x * scale, y * scale, 1.6 * scale, 0.7
    for route in range(9):
        source_y = 58 + route * 34
        target_y = gap_center + (route - 4) * 10
        exit_y = 78 + route * 29 + banner._variant(route + 7, -14, 14)
        yield from banner._line_dots(
            (40, source_y), (gate_x - 32, target_y), spacing=8, opacity=0.3
        )
        yield from banner._line_dots(
            (gate_x + 32, target_y), (720, exit_y), spacing=8, opacity=0.52
        )
