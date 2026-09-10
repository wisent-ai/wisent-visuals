"""Compose managed README presentation without replacing unrelated content."""

import re
import urllib.parse

from .model import BANNER_END, BANNER_PATH, BANNER_START, SIGNALS_END, SIGNALS_START


def _readme_excerpt(readme: str) -> str:
    text = re.sub(r"```.*?```", " ", readme, flags=re.DOTALL)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    for paragraph in re.split(r"\n\s*\n", text):
        cleaned = re.sub(r"!?(?:\[[^]]*\])?\([^)]*\)", " ", paragraph)
        cleaned = re.sub(r"^[#>*\-\s]+", "", cleaned).strip()
        cleaned = re.sub(r"\s+", " ", cleaned)
        if len(cleaned) >= 24 and not cleaned.startswith("http"):
            return cleaned[:240]
    return ""


def _opening_legacy_banner(readme: str) -> bool:
    return (
        re.match(
            r'\A\s*<p\b[^>]*>\s*<img\b[^>]*\bsrc=["\']banner\.png["\'][^>]*>\s*</p>\s*',
            readme,
            re.IGNORECASE,
        )
        is not None
    )


def _remove_opening_legacy_banner(readme: str) -> str:
    return re.sub(
        r'\A\s*<p\b[^>]*>\s*<img\b[^>]*\bsrc=["\']banner\.png["\'][^>]*>\s*</p>\s*',
        "",
        readme,
        count=1,
        flags=re.IGNORECASE,
    )


def _has_manual_banner(readme: str) -> bool:
    if BANNER_START in readme or _opening_legacy_banner(readme):
        return False
    return (
        re.search(r"(?:src=|!\[[^]]*\]\()[^\n)]*banner\.(?:png|webp|svg)", readme, re.I) is not None
    )


def _signals_block(owner: str, repository: str) -> str:
    encoded = urllib.parse.quote(repository, safe="")
    repository_url = f"https://github.com/{owner}/{encoded}"
    buttons = [
        (
            "Source",
            "https://img.shields.io/badge/GitHub-Source-181717?logo=github",
            repository_url,
        ),
        (
            "Issues",
            "https://img.shields.io/badge/GitHub-Issues-181717?logo=github",
            f"{repository_url}/issues",
        ),
        (
            "Wisent",
            "https://img.shields.io/badge/Wisent-Website-0B0B0B",
            "https://wisent.com",
        ),
        (
            "Discord",
            "https://img.shields.io/badge/Discord-Join-5865F2?logo=discord&logoColor=white",
            "https://discord.gg/qRjpkthq54",
        ),
        (
            "LinkedIn",
            "https://img.shields.io/badge/LinkedIn-Follow-0A66C2?logo=linkedin&logoColor=white",
            "https://www.linkedin.com/company/wisent-ai/",
        ),
        (
            "X",
            "https://img.shields.io/badge/X-Follow-000000?logo=x&logoColor=white",
            "https://x.com/wisentai",
        ),
        (
            "Enterprise",
            "https://img.shields.io/badge/Enterprise-Book%20a%20call-0B0B0B?logo=calendly",
            "https://calendly.com/lbartoszcze",
        ),
    ]
    row = " ".join(f"[![{label}]({image})]({target})" for label, image, target in buttons)
    return "\n".join((SIGNALS_START, row, SIGNALS_END))


def _remove_signals(readme: str) -> str:
    pattern = re.compile(
        re.escape(SIGNALS_START) + r".*?" + re.escape(SIGNALS_END),
        re.DOTALL,
    )
    match = pattern.search(readme)
    if match is None:
        return readme
    prefix = readme[: match.start()].rstrip("\n")
    suffix = readme[match.end() :].lstrip("\n")
    if prefix and suffix:
        return f"{prefix}\n\n{suffix}"
    if prefix:
        return prefix + ("\n" if readme.endswith("\n") else "")
    return suffix


def _insert_signals(readme: str, block: str) -> str:
    if BANNER_END in readme:
        position = readme.index(BANNER_END) + len(BANNER_END)
        prefix = readme[:position].rstrip("\n")
        suffix = readme[position:].lstrip("\n")
        return f"{prefix}\n\n{block}\n\n{suffix}"

    manual_patterns = (
        (r"<p\b[^>]*>.*?banner\.(?:png|webp|svg).*?</p>", re.IGNORECASE | re.DOTALL),
        (
            r"<picture\b[^>]*>.*?banner\.(?:png|webp|svg).*?</picture>",
            re.IGNORECASE | re.DOTALL,
        ),
        (
            r"^.*!\[[^]]*\]\([^)\n]*banner\.(?:png|webp|svg)[^)\n]*\).*$",
            re.IGNORECASE | re.MULTILINE,
        ),
    )
    for pattern, flags in manual_patterns:
        match = re.search(pattern, readme, flags)
        if match is not None:
            prefix = readme[: match.end()].rstrip("\n")
            suffix = readme[match.end() :].lstrip("\n")
            return f"{prefix}\n\n{block}\n\n{suffix}"
    return f"{block}\n\n{readme.lstrip()}"


def update_readme(
    readme: str,
    repository_name: str,
    owner: str = "wisent-ai",
    approved_title: str = "",
) -> str:
    """Keep generated presentation first and preserve approved product copy."""
    body = _remove_signals(readme)
    body = _remove_opening_legacy_banner(body)
    if not _has_manual_banner(body):
        block = "\n".join(
            [
                BANNER_START,
                '<p align="center">',
                f'  <img src="{BANNER_PATH}" alt="{repository_name} by Wisent" width="100%">',
                "</p>",
                BANNER_END,
            ]
        )
        if BANNER_START in body and BANNER_END in body:
            pattern = re.compile(
                re.escape(BANNER_START) + r".*?" + re.escape(BANNER_END),
                re.DOTALL,
            )
            body = pattern.sub("", body, count=1)
        body = body.lstrip("\n")
        if not body.strip():
            body = f"# {approved_title or repository_name}\n"
        body = f"{block}\n\n{body}"
    body = _insert_signals(body, _signals_block(owner, repository_name))
    if approved_title:
        heading = re.compile(r"^# .+$", re.MULTILINE)
        if heading.search(body):
            body = heading.sub(f"# {approved_title}", body, count=1)
        else:
            body = f"{body.rstrip()}\n\n# {approved_title}\n"
    return body
