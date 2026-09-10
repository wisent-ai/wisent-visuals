"""Command-line entry point for Wisent README banners."""

import argparse
from pathlib import Path
from typing import Optional, Sequence

from .banner import Banner, BannerConfig


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wisent-banner",
        description="Generate a deterministic Wisent README banner.",
    )
    parser.add_argument("--config", required=True, type=Path, help="TOML banner configuration")
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Output path ending in .svg, .webp, or .png",
    )
    parser.add_argument(
        "--svg",
        type=Path,
        help="Optional additional self-contained SVG source",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    banner = Banner(BannerConfig.from_toml(args.config))
    banner.save(args.output)
    if args.svg is not None:
        banner.save(args.svg)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
