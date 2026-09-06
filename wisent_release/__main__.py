"""Release-contract commands for wisent-visuals."""

from __future__ import annotations

import sys

from . import baseline, surface


def entrypoint() -> int:
    argv = sys.argv[1:]
    if not argv or argv[0] not in {"surface", "baseline"}:
        print("Usage: wisent-visuals-release surface [root] | baseline [options]", file=sys.stderr)
        return 2
    command, arguments = argv[0], argv[1:]
    return surface.main(arguments) if command == "surface" else baseline.main(arguments)


if __name__ == "__main__":
    sys.exit(entrypoint())
