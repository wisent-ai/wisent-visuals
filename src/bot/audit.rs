//! Declaring already-published banners to a repository audit, locally.
//!
//! The bot writes `.tama/violations-ignore` whenever it publishes a banner, so a
//! repository audit reads the rendered SVG as generated output. Banners published
//! before that behaviour existed carry no declaration, and the bot only revisits a
//! repository when its banner changes. This walks local checkouts instead of the
//! GitHub API (no token, no network) and writes the same declaration text the
//! publisher uses. It commits and pushes the file it wrote when asked, because a
//! declaration that lives only in a working tree is one the next clone lacks.

use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

use super::{audit_declaration, AUDIT_IGNORE_PATH, SVG_PATH};

const COMMIT_SUBJECT: &str = "docs: declare the published banner to the repository audit";
const COMMIT_BODY: &str = "The banner SVG is rendered from .github/banner.toml and replaced \
    whole on every run, so the audit reads it as generated output instead of asking somebody \
    to split a file nobody wrote by hand.";

/// What one checkout needed, and what was done about it.
pub struct Declaration {
    pub repository: PathBuf,
    pub wrote: bool,
    pub reason: String,
    pub revision: String,
}

impl Declaration {
    fn new(repository: &Path, wrote: bool, reason: impl Into<String>, revision: String) -> Self {
        Self {
            repository: repository.to_path_buf(),
            wrote,
            reason: reason.into(),
            revision,
        }
    }
}

/// Every checkout directly under `root`, plus `root` itself when it is one.
fn checkouts(root: &Path) -> Result<Vec<PathBuf>, String> {
    let mut found = Vec::new();
    if root.join(".git").exists() {
        found.push(root.to_path_buf());
    }
    if !root.is_dir() {
        return Ok(found);
    }
    let mut children: Vec<PathBuf> = fs::read_dir(root)
        .map_err(|e| format!("{}: {e}", root.display()))?
        .filter_map(|entry| entry.ok().map(|entry| entry.path()))
        .filter(|path| path.is_dir() && path.join(".git").exists())
        .collect();
    children.sort();
    found.extend(children);
    Ok(found)
}

/// Run git in `repository`: its trimmed output, or the first line of its complaint.
fn git(repository: &Path, arguments: &[&str]) -> Result<String, String> {
    let finished = Command::new("git")
        .arg("-C")
        .arg(repository)
        .args(arguments)
        .output()
        .map_err(|e| format!("git could not start: {e}"))?;
    let stdout = String::from_utf8_lossy(&finished.stdout).trim().to_owned();
    if finished.status.success() {
        return Ok(stdout);
    }
    let stderr = String::from_utf8_lossy(&finished.stderr).trim().to_owned();
    let detail = if stderr.is_empty() { stdout } else { stderr };
    Err(detail.lines().next().map_or_else(
        || format!("git exited with {}", finished.status),
        str::to_owned,
    ))
}

fn record(repository: &Path, push: bool) -> Declaration {
    if let Err(detail) = git(repository, &["add", AUDIT_IGNORE_PATH]) {
        return Declaration::new(
            repository,
            true,
            format!("written, not staged: {detail}"),
            String::new(),
        );
    }
    if let Err(detail) = git(
        repository,
        &["commit", "-q", "-m", COMMIT_SUBJECT, "-m", COMMIT_BODY],
    ) {
        return Declaration::new(
            repository,
            true,
            format!("written, not committed: {detail}"),
            String::new(),
        );
    }
    let revision = git(repository, &["rev-parse", "--short", "HEAD"]).unwrap_or_default();
    if !push {
        return Declaration::new(repository, true, "declared and committed", revision);
    }
    match git(repository, &["push", "-q", "origin", "HEAD"]) {
        Ok(_) => Declaration::new(repository, true, "declared, committed and pushed", revision),
        Err(detail) => Declaration::new(
            repository,
            true,
            format!("committed, not pushed: {detail}"),
            revision,
        ),
    }
}

/// Declare this checkout's published banner to its audit.
pub fn declare(repository: &Path, apply: bool, commit: bool, push: bool) -> Declaration {
    if !repository.join(SVG_PATH).is_file() {
        return Declaration::new(repository, false, "no published banner", String::new());
    }
    let target = repository.join(AUDIT_IGNORE_PATH);
    let existing = fs::read_to_string(&target).ok();
    let Some(declaration) = audit_declaration(existing.as_deref()) else {
        return Declaration::new(repository, false, "already declared", String::new());
    };
    if !apply {
        return Declaration::new(repository, false, "would declare the banner", String::new());
    }
    let written = target
        .parent()
        .map_or(Ok(()), fs::create_dir_all)
        .and_then(|()| fs::write(&target, declaration));
    if let Err(error) = written {
        return Declaration::new(
            repository,
            false,
            format!("not written: {error}"),
            String::new(),
        );
    }
    if !commit {
        return Declaration::new(repository, true, "declared the banner", String::new());
    }
    record(repository, push)
}

/// Declare every checkout under `root` that needs it.
pub fn declare_tree(
    root: &Path,
    apply: bool,
    commit: bool,
    push: bool,
) -> Result<Vec<Declaration>, String> {
    Ok(checkouts(root)?
        .iter()
        .map(|repository| declare(repository, apply, commit, push))
        .collect())
}
