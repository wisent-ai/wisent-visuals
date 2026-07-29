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


def published(data: dict, prefer_wheel: bool = False) -> tuple:
    """The latest published version and the best artifact available for it.

    `info.version` is what PyPI itself calls the current release, so this cannot drift
    from the registry the way re-deriving an ordering locally could.

    `prefer_wheel` inverts the tier preference. It exists for one job, and not for
    producing a baseline: a wheel reader nobody has run is a liability, because a layout
    it mishandles yields a *shorter* surface and the rule reads a short surface as removed
    capability. This release publishes both an sdist and a pure-Python wheel, so the two
    readers can be made to disagree out loud instead of being trusted. See --cross-check.
    """
    version = data["info"]["version"]
    files = data["releases"].get(version, [])
    tiers = [(WHEEL_MARKER, PURE_WHEEL), (SDIST_MARKER, None)]
    if not prefer_wheel:
        tiers.reverse()
    for marker, suffix in tiers:
        for candidate in files:
            matched = (
                candidate["filename"].endswith(suffix)
                if suffix
                else candidate["packagetype"] == "sdist"
            )
            if matched:
                return version, marker, candidate
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


def recover(scripts: pathlib.Path, repository: pathlib.Path, prefer_wheel: bool) -> tuple:
    """Download the best published artifact and read its surface, leaving nothing behind."""
    version, marker, artifact = published(registry(), prefer_wheel)
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
    return version, marker, artifact, names


def cross_check(scripts: pathlib.Path, repository: pathlib.Path) -> int:
    """Make the sdist and wheel readers agree, or say exactly where they differ.

    An artifact reader is only trustworthy once it has been contradicted and survived.
    Both tiers describe the same release, so any difference is a bug in one reader, and
    the dangerous direction is a reader that returns *fewer* names: the shared rule scores
    a short surface as removed capability.
    """
    sdist_version, sdist_marker, _, from_sdist = recover(scripts, repository, False)
    wheel_version, wheel_marker, _, from_wheel = recover(scripts, repository, True)

    if sdist_marker == wheel_marker:
        raise SystemExit(
            f"only the {sdist_marker} tier exists for {PROJECT} {sdist_version}, so there "
            "is nothing to cross-check against"
        )
    if sdist_version != wheel_version:
        raise SystemExit(f"tiers disagree on the version: {sdist_version}, {wheel_version}")

    only_sdist = sorted(set(from_sdist) - set(from_wheel))
    only_wheel = sorted(set(from_wheel) - set(from_sdist))
    print(f"{sdist_marker}: {len(from_sdist)} names")
    print(f"{wheel_marker}: {len(from_wheel)} names")
    if only_sdist or only_wheel:
        for name in only_sdist:
            print(f"  only in {sdist_marker}: {name}")
        for name in only_wheel:
            print(f"  only in {wheel_marker}: {name}")
        raise SystemExit(
            "the two readers disagree about the same release, so at least one of them is "
            "wrong and neither can be trusted to produce a baseline"
        )
    print(f"both tiers agree on {PROJECT} {sdist_version}")
    return int(False)


def main(argv: list) -> int:
    scripts = pathlib.Path(__file__).resolve().parent
    repository = scripts.parent

    if "--cross-check" in argv:
        return cross_check(scripts, repository)

    version, marker, artifact, names = recover(
        scripts, repository, "--prefer-wheel" in argv
    )

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
