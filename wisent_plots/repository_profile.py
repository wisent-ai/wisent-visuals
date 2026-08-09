"""Deterministic repository analysis for personalized Wisent banners."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Dict, Sequence, Tuple

from .banner import BannerConfig

IDENTITY_SCHEMA_VERSION = 7


@dataclass(frozen=True)
class RepositoryProfile:
    """Repository facts used to derive banner copy and artwork."""

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

    @property
    def fingerprint(self) -> str:
        payload = {
            "identity_schema_version": IDENTITY_SCHEMA_VERSION,
            "name": self.name,
            "description": self.description,
            "topics": sorted(self.topics),
            "language": self.language,
            "readme_excerpt": self.readme_excerpt,
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()[:16]


@dataclass(frozen=True)
class BannerIdentity:
    """Generated copy and visual family for one repository."""

    category: str
    title: str
    description: str
    layout: str
    art_seed: str
    fingerprint: str

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
                "",
                "[banner]",
                f"title = {quote(self.title)}",
                f"description = {quote(self.description)}",
                'product = "Wisent"',
                'url = "wisent.ai"',
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
    title: str
    layout: str
    keywords: Tuple[str, ...]


_CATEGORIES: Dict[str, _Category] = {
    "gateway": _Category(
        "{name} routes. You stay in control.",
        "routes-left",
        ("gateway", "router", "routing", "provider", "fallback", "inference"),
    ),
    "benchmark": _Category(
        "{name} measures. Progress proven.",
        "benchmark-left",
        ("benchmark", "evaluation", "evaluator", "quality", "score", "compare", "test"),
    ),
    "agent": _Category(
        "{name} acts. Work keeps moving.",
        "orbit-left",
        ("agent", "autonomous", "toolkit", "service", "workflow", "assistant"),
    ),
    "audio": _Category(
        "{name} decodes. Native speed.",
        "waveform-left",
        ("audio", "codec", "speech", "voice", "sound", "music"),
    ),
    "data": _Category(
        "{name} remembers. Context stays useful.",
        "layers-left",
        ("storage", "database", "lake", "archive", "memory", "context", "transcript"),
    ),
    "visualization": _Category(
        "{name} visualizes. Wisent style.",
        "benchmark-left",
        ("visual", "plot", "chart", "analytics", "dashboard", "graph"),
    ),
    "model": _Category(
        "{name} trains. Models improve.",
        "latent-field-left",
        ("model", "training", "finetuning", "fine-tuning", "mlx", "language", "lora"),
    ),
    "safety": _Category(
        "{name} steers. Outputs stay safer.",
        "latent-field-left",
        ("safety", "steering", "censorship", "guardrail", "control", "harmful", "hallucination"),
    ),
    "developer": _Category(
        "{name} builds. You ship faster.",
        "signal-left",
        ("cli", "sdk", "client", "code", "developer", "framework", "library"),
    ),
}


_PROJECT_COPY: Dict[str, Tuple[str, str]] = {
    "wisent-python": (
        "Control models from Python.",
        "Python client for Wisent model steering and activation-engineering services.",
    ),
    "wisent-node": (
        "Control models from TypeScript.",
        "JavaScript and TypeScript client for the Wisent backend.",
    ),
    "iskra": (
        "Representation fine-tuning for Polish.",
        "Research prototype for improving Polish generation with representation fine-tuning.",
    ),
    "wisent-visuals": (
        "Wisent charts. Ready to publish.",
        "Python package for producing charts and README banners in the Wisent visual system.",
    ),
    "heretic": (
        "Remove model censorship automatically.",
        "Automated representation-engineering pipeline for removing censorship from language models.",
    ),
    "uncensorbench": (
        "Measure censorship removal.",
        "Offline benchmark with versioned prompts and evaluators for model compliance.",
    ),
    "neucodec-mlx-swift": (
        "Decode neural audio on Apple Silicon.",
        "Swift MLX implementation of the NeuCodec neural audio decoder.",
    ),
    "singularity": (
        "Run autonomous agents within bounds.",
        "Auditable Rust runtime controlling agent loops, cost, state, tools, and external effects.",
    ),
    "adam-agent-toolkit": (
        "Give agents economic judgment.",
        "Python toolkit for agent cost tracking, decisions, dynamic pricing, and survival management.",
    ),
    "adam-services": (
        "Eight developer tools. One service.",
        "Zero-dependency service for code review, summaries, audits, analysis, docs, diffs, and regex.",
    ),
    "codespy": (
        "Scan code offline. Catch real risks.",
        "Zero-dependency static scanner for security, secrets, quality, performance, and supply-chain issues.",
    ),
    "eve-services": (
        "Sixteen utilities. Zero dependencies.",
        "Developer service for validation, hashing, text, cron, JWT, diff, templates, regex, and more.",
    ),
    "agent-gateway": (
        "One gateway for Adam and Eve.",
        "Unified API for service discovery, developer tools, and cross-agent pipelines.",
    ),
    "adam-docs": (
        "Turn codebases into usable documentation.",
        "Generates API references, architecture diagrams, complexity reports, and onboarding guides.",
    ),
    "eve-analytics": (
        "See the agent economy in real time.",
        "Analytics for agent health, token markets, chat activity, and platform reporting.",
    ),
    "eve-toolkit": (
        "Everyday developer tools from one CLI.",
        "Zero-dependency CLI for hashes, UUIDs, Base64, JWT, JSON, CSV, regex, diffs, and more.",
    ),
    "eve-portfolio": (
        "Developer utilities, live in the browser.",
        "Interactive browser tools for UUIDs, hashing, passwords, Base64, JSON, and colors.",
    ),
    "adam-monitor": (
        "Track agent health, cost, and runway.",
        "Real-time dashboard for agent finances, activity, spam, and platform economics.",
    ),
    "mlx-swift": (
        "Use MLX natively from Swift.",
        "Swift API for GPU-accelerated MLX workloads on Apple Silicon.",
    ),
    "swift-jinja": (
        "Render ML chat templates in Swift.",
        "Minimal Swift implementation of Jinja for parsing and rendering model chat templates.",
    ),
    "easyskeleton": (
        "Fast skeleton loading for SwiftUI.",
        "Lightweight SwiftUI framework for responsive skeleton loading states.",
    ),
    "openenv": (
        "Train strategic reasoning through games.",
        "Game-theory environment for training and evaluating LLM agents on strategic decisions.",
    ),
    "stado": (
        "Run governed workloads on any compute.",
        "Durable orchestration for policy-controlled AI jobs across local, cloud, and owned machines.",
    ),
    "brama": (
        "Route every model through one gateway.",
        "Authenticated multi-provider LLM routing with fallback chains and local inference.",
    ),
    "wisent-extractors": (
        "Extract benchmark signals consistently.",
        "Shared benchmark extractors split from the Wisent monorepo.",
    ),
    "wisent-evaluators": (
        "Evaluate benchmarks with shared methods.",
        "Evaluator registry, benchmark-specific evaluators, and methodology configurations for Wisent.",
    ),
    "wisent-optimizer": (
        "Tune steering methods automatically.",
        "Optuna and Hyperopt optimization for Wisent representation-steering parameters.",
    ),
    "wisent-tools": (
        "Operate the complete Wisent pipeline.",
        "Runners for activation extraction, benchmark evaluation, quality sweeps, and private inputs.",
    ),
    "wisent-gradio": (
        "Operate Wisent through a visual interface.",
        "Gradio application package for interactive Wisent workflows.",
    ),
    "wisent-cost-tracker": (
        "Track agent spend. Enforce every budget.",
        "Shared TypeScript and Python clients with a Supabase backend for per-agent cost control.",
    ),
    "wisent-1b": (
        "Language modeling with an explicit concept stream.",
        "Reference implementation of Rej-1B, a representation-native language model.",
    ),
    "turbot-ios": (
        "Turbot, built for iOS.",
        "Archived SwiftUI implementation of the Turbot mobile application.",
    ),
    "trading-ios": (
        "Wisent trading tools for iOS.",
        "Native Swift application for using Wisent trading workflows on iPhone.",
    ),
    "quality-control": (
        "Make repository policy executable.",
        "Dependency-free checks and reusable GitHub workflows for enforcing organization quality gates.",
    ),
    "probierz": (
        "Test every product surface from one CLI.",
        "Cross-platform automation for web, Electron, iOS, Android, macOS, and Windows.",
    ),
    "jeden": (
        "Run coding agents locally, under your policy.",
        "Rust coding-agent harness with controlled tools, durable sessions, memory, and model freedom.",
    ),
    "las": (
        "Federate every Wisent tool through one MCP.",
        "Local catalogue that verifies and exposes approved sibling MCP servers through one CLI.",
    ),
    "wisent-desktop-auth": (
        "One secure identity layer for Wisent macOS apps.",
        "Swift package for Supabase sign-in, organizations, entitlements, sessions, and Keychain storage.",
    ),
    "tama-desktop": (
        "Enforce coding-agent policy across Mac fleets.",
        "Native control plane for inspecting, enforcing, recovering, and auditing local agent hooks.",
    ),
    "probierz-desktop": (
        "Inspect test runs and evidence on macOS.",
        "Native viewer for Probierz contracts, run status, manifests, and artifact metadata.",
    ),
    "kronika": (
        "Write documentation from repository evidence.",
        "Local writer that selects bounded source evidence and uses Brama to produce Markdown.",
    ),
    "ugc-cli": (
        "Run creator campaigns from one local ledger.",
        "System of record for briefs, creators, assets, rights, payments, publication, and audit.",
    ),
    "grant-cli": (
        "Research and write grants with evidence attached.",
        "Local workspace for discovery, eligibility, source-backed applications, and submission export.",
    ),
    "skarbiec": (
        "Issue credentials without exposing secrets.",
        "Local broker for short-lived capabilities, encrypted vault state, recovery, and audit.",
    ),
    "transcript-lake": (
        "Archive agent conversations privately.",
        "Privacy-masked local transcript store with incremental updates, SQL inspection, and Oko import.",
    ),
    "weles-client": (
        "Authorize browser work. Verify every receipt.",
        "Node.js client for submitting bounded browser workflows and verifying signed receipts.",
    ),
}


def _normalized_copy(profile: RepositoryProfile) -> str:
    copy = profile.description.strip() or profile.readme_excerpt.strip()
    copy = re.sub(r"\s+", " ", copy)
    copy = re.sub(r"^#+\s*", "", copy)
    if copy:
        return copy[:180].rstrip()
    if profile.language:
        return f"A {profile.language} project from Wisent."
    return f"A project from Wisent for {profile.display_name}."


def generate_identity(profile: RepositoryProfile) -> BannerIdentity:
    """Classify repository facts and generate stable, project-specific copy."""
    weighted_text: Sequence[Tuple[str, int]] = (
        (" ".join(profile.topics).lower(), 3),
        (profile.description.lower(), 2),
        (profile.readme_excerpt.lower(), 1),
    )
    scores: Dict[str, int] = {}
    for category, definition in _CATEGORIES.items():
        score = 0
        for source, weight in weighted_text:
            score += sum(weight for keyword in definition.keywords if keyword in source)
        scores[category] = score

    category = max(scores, key=scores.get)
    if scores[category] == 0:
        title = f"{profile.display_name}. Built for what comes next."
        layout = "signal-left"
        category = "general"
    else:
        definition = _CATEGORIES[category]
        title = definition.title.format(name=profile.display_name)
        layout = definition.layout

    project_copy = _PROJECT_COPY.get(profile.name.lower())
    if project_copy is not None:
        title, description = project_copy
    else:
        description = _normalized_copy(profile)

    return BannerIdentity(
        category=category,
        title=title,
        description=description,
        layout=layout,
        art_seed=profile.name,
        fingerprint=profile.fingerprint,
    )


__all__ = ["BannerIdentity", "RepositoryProfile", "generate_identity"]
