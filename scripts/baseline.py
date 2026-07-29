"""Regenerate released-surface.json: the public surface of the version ACTUALLY PUBLISHED.

The baseline every later release is judged against must describe an artifact somebody can
install. Hand-editing it, or quietly falling back to the working tree, measures every
future comparison against something that was never shipped.

Two rules this script exists to enforce:

1.  **The baseline version is the latest version the registry serves, never the version
    this repository declares.** The moment someone bumps pyproject.toml ahead of a release,
    looking up the declared version 404s; a generator that then degraded to the working
    tree would throw away the real published baseline and silently start scoring changes
    against the wrong artifact. So the version is resolved from PyPI first, and the
    surface of *that* version is recovered.

2.  **The `source` field names its provenance with a marker, not prose.** The marker is the
    first whitespace-delimited token, so one `jq` call reads it and the workflow can assert
    in both directions: a baseline that claims a registry artifact must be served by that
    registry, and a baseline that claims none must not be served at all. Coupling the two
    files by a constant instead of by a sentence is the point.

    Marker grammar, shared fleet-wide:

        pypi-sdist:<filename>    recovered from a published sdist
        pypi-wheel:<filename>    recovered from a published pure-Python wheel
        head:<40-char sha>       LAST RESORT: nothing published

    Preference order is best-tier-that-exists: sdist, then pure-Python wheel, then HEAD.
    Never a lower tier because a higher one was inconvenient.

This repository is on PyPI as `wisent-visuals` with a published sdist, so it resolves to
the `pypi-sdist` tier. A tier this script does not implement is a loud refusal, never a
silent downgrade.

Usage:
    python3 scripts/baseline.py            # rewrite released-surface.json
    python3 scripts/baseline.py --print    # write nothing, show what it would produce
"""

from __future__ import annotations

import io
import json
import pathlib
import subprocess
import sys
import tarfile
import urllib.request
import zipfile

PROJECT = "wisent-visuals"
INDEX = f"https://pypi.org/pypi/{PROJECT}/json"
PACKAGE = "wisent_plots"
BASELINE = "released-surface.json"
EXTRACTOR = "surface.py"

SDIST_MARKER = "pypi-sdist"
WHEEL_MARKER = "pypi-wheel"
HEAD_MARKER = "head"

PURE_WHEEL = "py3-none-any.whl"
INDENT = int(True) + int(True)


def registry() -> dict:
    """What PyPI serves for this project."""
    try:
        with urllib.request.urlopen(INDEX) as response:
            return json.load(response)
    except OSError as error:
        raise SystemExit(
            f"cannot reach {INDEX}: {error}. Refusing to write a baseline without "
            "confirming what is actually published"
        ) from error


def published(data: dict) -> tuple:
    """The latest published version and the best artifact available for it.

    `info.version` is what PyPI itself calls the current release, so this cannot drift
    from the registry the way re-deriving an ordering locally could.
    """
    version = data["info"]["version"]
    files = data["releases"].get(version, [])
    for candidate in files:
        if candidate["packagetype"] == "sdist":
            return version, SDIST_MARKER, candidate
    for candidate in files:
        if candidate["filename"].endswith(PURE_WHEEL):
            return version, WHEEL_MARKER, candidate
    raise SystemExit(
        f"{PROJECT} {version} is published but offers neither an sdist nor a pure-Python "
        f"wheel: {[candidate['filename'] for candidate in files]}. The tier needed here "
        "is not implemented, and degrading to HEAD would claim an unpublished baseline "
        "is a published one"
    )


def fetch(url: str) -> bytes:
    try:
        with urllib.request.urlopen(url) as response:
            return response.read()
    except OSError as error:
        raise SystemExit(f"cannot download {url}: {error}") from error


def unpack(marker: str, payload: bytes, into: pathlib.Path) -> None:
    if marker == SDIST_MARKER:
        with tarfile.open(fileobj=io.BytesIO(payload)) as archive:
            # `data` filter where available: an artifact off the network should not be
            # able to write outside the directory we chose for it.
            if hasattr(tarfile, "data_filter"):
                archive.extractall(into, filter="data")
            else:
                archive.extractall(into)
        return
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        archive.extractall(into)


def root_of(unpacked: pathlib.Path) -> pathlib.Path:
    """The directory to run the extractor against: whatever holds the package."""
    if (unpacked / PACKAGE).is_dir():
        return unpacked
    for child in sorted(unpacked.iterdir()):
        if child.is_dir() and (child / PACKAGE).is_dir():
            return child
    raise SystemExit(f"no {PACKAGE}/ directory inside the downloaded artifact")


def extract(scripts: pathlib.Path, root: pathlib.Path) -> list:
    """Run this repository's own extractor against the unpacked artifact."""
    result = subprocess.run(
        [sys.executable, str(scripts / EXTRACTOR), str(root)],
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise SystemExit(
            f"{EXTRACTOR} refused to read the published artifact, so its surface is "
            f"unknown and no baseline can be written:\n{result.stderr.strip()}"
        )
    return json.loads(result.stdout)["surface"]


def main(argv: list) -> int:
    scripts = pathlib.Path(__file__).resolve().parent
    repository = scripts.parent

    version, marker, artifact = published(registry())
    payload = fetch(artifact["url"])

    workspace = repository / ".baseline-artifact"
    if workspace.exists():
        raise SystemExit(f"{workspace} already exists; remove it and rerun")
    workspace.mkdir()
    try:
        unpack(marker, payload, workspace)
        names = extract(scripts, root_of(workspace))
    finally:
        for path in sorted(workspace.rglob("*"), reverse=True):
            path.rmdir() if path.is_dir() else path.unlink()
        workspace.rmdir()

    document = {
        "version": version,
        "source": (
            f"{marker}:{artifact['filename']} "
            f"— latest version served by PyPI for {PROJECT}, downloaded and read with "
            f"scripts/{EXTRACTOR}; regenerate with scripts/baseline.py"
        ),
        "surface": names,
    }
    rendered = json.dumps(document, indent=INDENT, ensure_ascii=False) + "\n"

    if "--print" in argv:
        sys.stdout.write(rendered)
        return int(False)

    (repository / BASELINE).write_text(rendered)
    print(f"{BASELINE}: {marker} baseline {version}, {len(names)} names")
    return int(False)


if __name__ == "__main__":
    sys.exit(main(sys.argv[int(True) :]))
