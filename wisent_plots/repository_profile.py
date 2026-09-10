"""Deterministic banner artwork with conversation-approved product copy."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

from .banner import BannerConfig

IDENTITY_SCHEMA_VERSION = 9


@dataclass(frozen=True)
class RepositoryProfile:
    """Repository facts used to choose artwork without inventing product copy."""

    name: str
    description: str = ""
    topics: Tuple[str, ...] = ()
    language: str = ""
    readme_excerpt: str = ""

    @property
    def display_name(self) -> str:
        acronyms = {"ai", "api", "cli", "gpu", "ios", "llm", "mlx", "sdk", "ugc", "ui", "ux"}
        words = self.name.replace("_", "-").split("-")
        return " ".join(
            word.upper() if word.lower() in acronyms else word.capitalize() for word in words
        )


@dataclass(frozen=True)
class BannerIdentity:
    """Approved copy and deterministic visual family for one repository."""

    category: str
    title: str
    description: str
    layout: str
    art_seed: str
    fingerprint: str
    copy_status: str
    approved_in: str

    def as_config(self) -> BannerConfig:
        return BannerConfig(
            title=self.title,
            description=self.description,
            layout=self.layout,
            art_seed=self.art_seed,
        )

    def to_toml(self) -> str:
        def quote(value: str) -> str:
            return json.dumps(value, ensure_ascii=False)

        return "\n".join(
            [
                "[automation]",
                "managed = true",
                f"source_fingerprint = {quote(self.fingerprint)}",
                f"category = {quote(self.category)}",
                f"copy_status = {quote(self.copy_status)}",
                f"approved_in = {quote(self.approved_in)}",
                "",
                "[banner]",
                f"title = {quote(self.title)}",
                f"description = {quote(self.description)}",
                'product = "Wisent"',
                'url = "wisent.com"',
                'theme = "dark"',
                f"layout = {quote(self.layout)}",
                f"art_seed = {quote(self.art_seed)}",
                "width = 1584",
                "height = 396",
                "",
            ]
        )


@dataclass(frozen=True)
class _Category:
    layout: str
    keywords: Tuple[str, ...]


_CATEGORIES: Dict[str, _Category] = {
    "gateway": _Category(
        "routes-left",
        ("gateway", "router", "routing", "provider", "fallback", "inference"),
    ),
    "benchmark": _Category(
        "benchmark-left",
        ("benchmark", "evaluation", "evaluator", "quality", "score", "compare", "test"),
    ),
    "agent": _Category(
        "orbit-left",
        ("agent", "autonomous", "toolkit", "service", "workflow", "assistant"),
    ),
    "audio": _Category(
        "waveform-left",
        ("audio", "codec", "speech", "voice", "sound", "music"),
    ),
    "data": _Category(
        "layers-left",
        ("storage", "database", "lake", "archive", "memory", "context", "transcript"),
    ),
    "visualization": _Category(
        "benchmark-left",
        ("visual", "plot", "chart", "analytics", "dashboard", "graph"),
    ),
    "model": _Category(
        "latent-field-left",
        ("model", "training", "finetuning", "fine-tuning", "mlx", "language", "lora"),
    ),
    "safety": _Category(
        "latent-field-left",
        ("safety", "steering", "censorship", "guardrail", "control", "harmful", "hallucination"),
    ),
    "developer": _Category(
        "signal-left",
        ("cli", "sdk", "client", "code", "developer", "framework", "library"),
    ),
}


def _approved_copy() -> Dict[str, Dict[str, str]]:
    document = json.loads(Path(__file__).with_name("approved_copy.json").read_text(encoding="utf-8"))
    if document.get("schema") != 1 or not isinstance(document.get("entries"), dict):
        raise ValueError("approved_copy.json must contain schema 1 and an entries object")
    return document["entries"]


def _fingerprint(
    profile: RepositoryProfile,
    category: str,
    layout: str,
    title: str,
    description: str,
    approved_in: str,
) -> str:
    payload = {
        "identity_schema_version": IDENTITY_SCHEMA_VERSION,
        "name": profile.name,
        "category": category,
        "layout": layout,
        "title": title,
        "description": description,
        "approved_in": approved_in,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def generate_identity(profile: RepositoryProfile) -> BannerIdentity:
    """Choose artwork from repository facts and copy only from the approval register."""
    weighted_text = (
        (" ".join(profile.topics).lower(), 3),
        (profile.description.lower(), 2),
        (profile.readme_excerpt.lower(), 1),
    )
    scores: Dict[str, int] = {}
    for category, definition in _CATEGORIES.items():
        scores[category] = sum(
            weight
            for source, weight in weighted_text
            for keyword in definition.keywords
            if keyword in source
        )

    category = max(scores, key=scores.get)
    if scores[category] == 0:
        category = "general"
        layout = "signal-left"
    else:
        layout = _CATEGORIES[category].layout

    approved = _approved_copy().get(profile.name.lower())
    if approved is None:
        title = profile.display_name
        description = ""
        approved_in = ""
        copy_status = "missing"
    else:
        title = approved["title"].strip()
        description = approved.get("description", "").strip()
        approved_in = approved["approved_in"].strip()
        if not title or not approved_in:
            raise ValueError(f"approved copy for {profile.name} lacks title or approved_in")
        copy_status = "approved"

    return BannerIdentity(
        category=category,
        title=title,
        description=description,
        layout=layout,
        art_seed=profile.name,
        fingerprint=_fingerprint(
            profile,
            category,
            layout,
            title,
            description,
            approved_in,
        ),
        copy_status=copy_status,
        approved_in=approved_in,
    )


__all__ = ["BannerIdentity", "RepositoryProfile", "generate_identity"]
