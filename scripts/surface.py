"""Print this package's public surface: what a caller of wisent-visuals can import and call.

This is a library, not a script collection. It ships no console entry points — the
`tools/*.sh` helpers are not packaged, `pyproject.toml` declares no `[project.scripts]`,
and `[tool.setuptools.packages.find]` ships only `wisent_plots*`. So the contract is the
importable one, and `__all__` is where this package states it.

Three things make up that contract, because all three are things a user would notice
disappearing:

1.  **Exported names, qualified by the module that exports them** — `wisent_plots:AreaChart`.
    A module that declares `__all__` is making a promise; a module that does not is
    internal. `AreaChart` is promised twice, by `wisent_plots` and by
    `wisent_plots.charts`, and both import paths appear, because removing either one
    breaks the callers who used it.

2.  **Public methods of exported classes** — `wisent_plots:AreaChart.plot`. Class names
    alone would be a contract that cannot notice its most likely breakage. Every example
    in the README calls `chart.plot(...)` and `chart.save(...)`; dropping or renaming
    `plot` breaks every caller while the seven exported class names sit unchanged. A
    surface that called that "internal" would rubber-stamp the release that broke
    everyone. Methods are resolved through the re-export chain to the module that really
    defines the class.

3.  **Keys of exported mappings** — `wisent_plots.styles:STYLES[3]`. `STYLES` is a
    registry and callers index it by key, directly or through `get_style(3)` and
    `AreaChart(style=3)`. The keys are therefore selectable capabilities: style 22 is not
    an implementation detail to whoever passed 22 yesterday. Adding a style is a new
    capability; removing one is a break. This is the general rule — an exported name
    whose value is a literal dict contributes its keys — not a special case for `STYLES`.

Deliberately excluded: the per-class `style_map` aliases ("solid", "gradient", ...) that
each chart's `__init__` defines as a function-local. They read like a contract but are not
a trustworthy one — `AreaChart`'s map offers "vibrant" and "dark", which resolve to style
numbers 6 and 7 that `STYLES` does not contain, so `get_style` rejects those two aliases
with `ValueError: Style 6 not found` rather than drawing anything. Putting them in the
surface would promise capabilities that do not exist, and later deleting the broken
aliases would be scored as a breaking removal when it is a bugfix. The numeric keys above
are the honest form of the same promise.

Excluded for the same reason: the `theme` values ('brand', 'black', 'white') that
`BarChart` and `ColumnChart` check against a list literal inside their own `__init__`.
They are function-locals in a validation guard rather than a registry, only some chart
classes accept a theme at all, and harvesting them would mean either hardcoding which
local list in which method counts or treating every local list literal as contract. A
partial, heuristically-scraped theme set would misreport what the library offers; the
exported registry keys above are the part of this promise that is stated structurally.

Read with `ast`, never by importing. Importing pulls in `matplotlib` and `numpy`, and a
release decision must not depend on a machine having them. It also means this runs
unchanged against an unpacked sdist, so the surface of an already published version can be
recovered exactly rather than assumed.

A module that does not parse, or an `__all__` that is not a literal list of strings, is a
refusal and not a smaller answer. In both cases the surface is *unknown*, and the shared
versioning rule would read a short surface as removed capability and wave through a
breaking release.

Usage:
    python3 scripts/surface.py [root]     # root defaults to the repository
"""

from __future__ import annotations

import ast
import json
import pathlib
import sys

PACKAGE = "wisent_plots"
INIT = "__init__.py"
ALL = "__all__"
DEFINITIONS = (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef)


def module_name(path: pathlib.Path, root: pathlib.Path) -> str:
    """The dotted name a caller would import this file as."""
    parts = list(path.relative_to(root).parts)
    parts[-int(True)] = path.stem
    if path.name == INIT:
        parts.pop()
    return ".".join(parts)


def parse(path: pathlib.Path) -> ast.Module:
    """Parse one module, refusing rather than guessing when it cannot be read."""
    try:
        return ast.parse(path.read_text(), filename=str(path))
    except OSError as error:
        raise SystemExit(f"{path}: {error}") from error
    except SyntaxError as error:
        # Refuse rather than skip. A module that does not parse cannot be imported
        # either, so its names are unreachable at runtime; skipping it would report a
        # smaller surface, and the rule would read that as removed capability. The
        # surface is unknown here, not shrunk.
        raise SystemExit(
            f"{path}: does not parse, so the surface is unknown: {error}"
        ) from error


class Module:
    """One parsed module: what it defines, what it re-exports, what it declares public."""

    def __init__(self, name: str, path: pathlib.Path, tree: ast.Module) -> None:
        self.name = name
        self.path = path
        self.defines = {}
        self.imports = {}
        self.exports = None
        for node in tree.body:
            self._absorb(node)

    def _absorb(self, node: ast.stmt) -> None:
        if isinstance(node, DEFINITIONS):
            self.defines[node.name] = node
        elif isinstance(node, ast.ImportFrom):
            self._absorb_import(node)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                self._absorb_binding(target, node.value)
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            self._absorb_binding(node.target, node.value)

    def _absorb_import(self, node: ast.ImportFrom) -> None:
        source = self._source_of(node)
        for alias in node.names:
            if alias.name == "*":
                # `import *` makes __all__ unverifiable: the names it promises may come
                # from anywhere, so their methods and keys cannot be resolved.
                raise SystemExit(
                    f"{self.path}: star import from {source}, so what this module "
                    "exports cannot be determined without importing it"
                )
            self.imports[alias.asname or alias.name] = (source, alias.name)

    def _source_of(self, node: ast.ImportFrom) -> str:
        """The absolute module an ImportFrom reads from, resolving relative imports."""
        if not node.level:
            return node.module or ""
        parts = self.name.split(".")
        if self.path.name != INIT:
            # A plain module is not a package: `from . import x` means its parent.
            parts.pop()
        upward = node.level - int(True)
        if upward:
            parts = parts[: len(parts) - upward]
        if node.module:
            parts.append(node.module)
        return ".".join(parts)

    def _absorb_binding(self, target: ast.expr, value: ast.expr) -> None:
        if not isinstance(target, ast.Name):
            return
        if target.id == ALL:
            self.exports = self._read_all(value)
        else:
            # The value, not the statement: an exported mapping's keys are contract.
            self.defines[target.id] = value

    def _read_all(self, value: ast.expr) -> list:
        if not isinstance(value, (ast.List, ast.Tuple)):
            raise SystemExit(
                f"{self.path}: {ALL} is not a literal list, so the public surface is "
                "unknown; refusing rather than reporting a shorter one"
            )
        names = []
        for element in value.elts:
            if not (isinstance(element, ast.Constant) and isinstance(element.value, str)):
                raise SystemExit(
                    f"{self.path}: {ALL} holds a non-literal entry, so the public "
                    "surface is unknown; refusing rather than reporting a shorter one"
                )
            names.append(element.value)
        return names


def collect(package: pathlib.Path, root: pathlib.Path, tolerant: bool) -> tuple:
    """Every module in the package, and the ones tolerance had to skip."""
    modules = {}
    skipped = []
    for path in sorted(package.rglob("*.py")):
        try:
            module = Module(module_name(path, root), path, parse(path))
        except SystemExit:
            if not tolerant:
                raise
            skipped.append(str(path.relative_to(root)))
            continue
        modules[module.name] = module
    return modules, skipped


def definition(modules: dict, module: str, name: str):
    """Follow re-exports to the node that actually defines `name`, or None."""
    seen = set()
    while (module, name) not in seen:
        seen.add((module, name))
        owner = modules.get(module)
        if owner is None:
            return None
        if name in owner.defines:
            return owner.defines[name]
        origin = owner.imports.get(name)
        if origin is None:
            return None
        module, name = origin
    return None


def detail(node, qualified: str) -> list:
    """What an exported object promises beyond its own name."""
    if isinstance(node, ast.ClassDef):
        return [
            f"{qualified}.{member.name}"
            for member in node.body
            if isinstance(member, FUNCTIONS) and not member.name.startswith("_")
        ]
    if isinstance(node, ast.Dict):
        return [
            f"{qualified}[{key.value!r}]"
            for key in node.keys
            if isinstance(key, ast.Constant)
        ]
    return []


def surface(root: pathlib.Path, tolerant: bool = False) -> tuple:
    """The public surface, plus whatever had to be skipped or could not be resolved."""
    package = root / PACKAGE
    if not package.is_dir():
        raise SystemExit(f"{package} is not a directory; is {root} the repository root?")

    modules, skipped = collect(package, root, tolerant)
    names = set()
    unresolved = []
    for module in modules.values():
        if module.exports is None:
            continue
        for exported in module.exports:
            qualified = f"{module.name}:{exported}"
            names.add(qualified)
            node = definition(modules, module.name, exported)
            if node is None:
                # The name is still promised, so it stays in the surface; we just
                # cannot see what it carries. Reported, never swallowed.
                unresolved.append(qualified)
                continue
            names.update(detail(node, qualified))

    if not names:
        raise SystemExit(
            f"no {ALL} declarations found under {package}. Either the package stopped "
            f"stating its public API, or it moved — both change what this library "
            "promises, so refusing rather than reporting an empty surface"
        )
    return sorted(names), skipped, unresolved


def main(argv: list) -> int:
    tolerant = "--tolerant" in argv
    positional = [arg for arg in argv if not arg.startswith("-")]
    root = (
        pathlib.Path(positional[int(False)])
        if positional
        else pathlib.Path(__file__).resolve().parent.parent
    )
    names, skipped, unresolved = surface(root, tolerant)
    document = {"surface": names}
    if skipped:
        document["unparseable"] = skipped
    if unresolved:
        document["unresolved"] = unresolved
    print(json.dumps(document, indent=int(True) + int(True)))
    return int(False)


if __name__ == "__main__":
    sys.exit(main(sys.argv[int(True) :]))
