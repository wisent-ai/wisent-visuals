//! Compose managed README presentation without replacing unrelated content.
//!
//! A hand-placed banner is any image whose file is named `banner`, whatever its
//! extension: the README's own markup says which picture is the banner.

use regex::{NoExpand, Regex};

use super::github::component;
use super::{BANNER_END, BANNER_PATH, BANNER_START, SIGNALS_END, SIGNALS_START};

const LEGACY_OPENING: &str =
    r#"(?i)\A\s*<p\b[^>]*>\s*<img\b[^>]*\bsrc=["']banner\.png["'][^>]*>\s*</p>\s*"#;

fn pattern(source: &str) -> Regex {
    Regex::new(source).unwrap_or_else(|e| panic!("README pattern {source} is invalid: {e}"))
}

fn block(start: &str, end: &str) -> Regex {
    pattern(&format!(
        "(?s){}.*?{}",
        regex::escape(start),
        regex::escape(end)
    ))
}

/// The README opens with the hand-placed `banner.png` paragraph the bot supersedes.
pub fn opening_legacy_banner(readme: &str) -> bool {
    pattern(LEGACY_OPENING).is_match(readme)
}

fn remove_opening_legacy_banner(readme: &str) -> String {
    pattern(LEGACY_OPENING).replacen(readme, 1, "").into_owned()
}

/// A banner somebody placed by hand, which the bot never replaces.
pub fn has_manual_banner(readme: &str) -> bool {
    if readme.contains(BANNER_START) || opening_legacy_banner(readme) {
        return false;
    }
    pattern(r"(?i)(?:src=|!\[[^\]]*\]\()[^\n)]*banner\.[a-z]+").is_match(readme)
}

fn signals_block(owner: &str, repository: &str) -> String {
    let repository_url = format!("https://github.com/{owner}/{}", component(repository));
    let issues = format!("{repository_url}/issues");
    let buttons = [
        (
            "Source",
            "https://img.shields.io/badge/GitHub-Source-181717?logo=github",
            repository_url.as_str(),
        ),
        (
            "Issues",
            "https://img.shields.io/badge/GitHub-Issues-181717?logo=github",
            issues.as_str(),
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
    ];
    let row: Vec<String> = buttons
        .iter()
        .map(|(label, image, target)| format!("[![{label}]({image})]({target})"))
        .collect();
    [SIGNALS_START, &row.join(" "), SIGNALS_END].join("\n")
}

/// Join two halves around an inserted block with one blank line on each side.
fn join(prefix: &str, middle: &str, suffix: &str) -> String {
    let prefix = prefix.trim_end_matches('\n');
    let suffix = suffix.trim_start_matches('\n');
    format!("{prefix}\n\n{middle}\n\n{suffix}")
}

fn remove_signals(readme: &str) -> String {
    let Some(found) = block(SIGNALS_START, SIGNALS_END).find(readme) else {
        return readme.to_owned();
    };
    let prefix = readme[..found.start()].trim_end_matches('\n');
    let suffix = readme[found.end()..].trim_start_matches('\n');
    match (prefix.is_empty(), suffix.is_empty()) {
        (false, false) => format!("{prefix}\n\n{suffix}"),
        (false, true) if readme.ends_with('\n') => format!("{prefix}\n"),
        (false, true) => prefix.to_owned(),
        _ => suffix.to_owned(),
    }
}

fn insert_signals(readme: &str, signals: &str) -> String {
    if let Some(position) = readme.find(BANNER_END) {
        let position = position + BANNER_END.len();
        return join(&readme[..position], signals, &readme[position..]);
    }
    let manual = [
        r"(?is)<p\b[^>]*>.*?banner\.[a-z]+.*?</p>",
        r"(?is)<picture\b[^>]*>.*?banner\.[a-z]+.*?</picture>",
        r"(?im)^.*!\[[^\]]*\]\([^)\n]*banner\.[a-z]+[^)\n]*\).*$",
    ];
    for source in manual {
        if let Some(found) = pattern(source).find(readme) {
            return join(&readme[..found.end()], signals, &readme[found.end()..]);
        }
    }
    format!("{signals}\n\n{}", readme.trim_start())
}

/// Keep generated presentation first and preserve approved product copy.
pub fn update_readme(
    readme: &str,
    repository_name: &str,
    owner: &str,
    approved_title: Option<&str>,
) -> String {
    let mut body = remove_opening_legacy_banner(&remove_signals(readme));
    if !has_manual_banner(&body) {
        let image = format!(
            "  <img src=\"{BANNER_PATH}\" alt=\"{repository_name} by Wisent\" width=\"100%\">"
        );
        let banner = [
            BANNER_START,
            "<p align=\"center\">",
            &image,
            "</p>",
            BANNER_END,
        ]
        .join("\n");
        if body.contains(BANNER_START) && body.contains(BANNER_END) {
            body = block(BANNER_START, BANNER_END)
                .replacen(&body, 1, "")
                .into_owned();
        }
        let mut rest = body.trim_start_matches('\n').to_owned();
        if rest.trim().is_empty() {
            rest = format!("# {}\n", approved_title.unwrap_or(repository_name));
        }
        body = format!("{banner}\n\n{rest}");
    }
    body = insert_signals(&body, &signals_block(owner, repository_name));
    if let Some(title) = approved_title {
        let heading = pattern(r"(?m)^# .+$");
        let replacement = format!("# {title}");
        body = if heading.is_match(&body) {
            heading
                .replacen(&body, 1, NoExpand(&replacement))
                .into_owned()
        } else {
            format!("{}\n\n{replacement}\n", body.trim_end())
        };
    }
    body
}
