"""The supported artwork registry and shared seeded geometry transformation."""

from typing import TYPE_CHECKING, Iterable, Tuple

from . import signals, structures

if TYPE_CHECKING:
    from ..banner import Banner


_RENDERERS = {
    "benchmark-left": structures.benchmark_dots,
    "flock-left": structures.flock_dots,
    "focus-left": signals.focus_dots,
    "forest-left": structures.forest_dots,
    "fracture-left": signals.fracture_dots,
    "gate-left": signals.gate_dots,
    "gauge-left": structures.gauge_dots,
    "latent-field-left": signals.latent_field_dots,
    "layers-left": structures.layers_dots,
    "orbit-left": structures.orbit_dots,
    "routes-left": structures.routes_dots,
    "scan-left": structures.scan_dots,
    "signal-left": signals.signal_dots,
    "spark-left": signals.spark_dots,
    "timeline-left": structures.timeline_dots,
    "vault-left": structures.vault_dots,
    "waveform-left": signals.waveform_dots,
}
SUPPORTED_LAYOUTS = tuple(_RENDERERS)


def render_artwork(banner: "Banner") -> Iterable[Tuple[float, float, float, float]]:
    center_x = 380 * banner._scale()
    center_y = 198 * banner._scale()
    stretch_x = banner._variant(0, 0.9, 1.1)
    stretch_y = banner._variant(1, 0.88, 1.12)
    shear = banner._variant(2, -0.06, 0.06)
    radius_scale = banner._variant(3, 0.88, 1.16)
    opacity_scale = banner._variant(4, 0.88, 1.08)
    for x, y, radius, opacity in _RENDERERS[banner.config.layout](banner):
        relative_x = x - center_x
        relative_y = y - center_y
        yield (
            center_x + relative_x * stretch_x,
            center_y + relative_y * stretch_y + relative_x * shear,
            radius * radius_scale,
            min(1, opacity * opacity_scale),
        )
