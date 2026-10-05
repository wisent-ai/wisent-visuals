//! `wisent-banner-bot` run as the workflow and an operator run it.
//!
//! `declare-local` works on real git checkouts made for the test and commits with
//! the git identity of whoever runs the suite, as the command itself does; `plan`
//! reads the real wisent-ai organization on GitHub and changes nothing there.

use std::fs;
use std::path::{Path, PathBuf};
use std::process::{Command, Output};

use serde_json::Value;

fn bot(arguments: &[&str]) -> Output {
    Command::new(env!("CARGO_BIN_EXE_wisent-banner-bot"))
        .args(arguments)
        .env_remove("WISENT_BANNER_GITHUB_TOKEN")
        .output()
        .expect("wisent-banner-bot runs")
}

fn rows(output: &Output) -> Vec<Value> {
    String::from_utf8_lossy(&output.stdout)
        .lines()
        .map(|line| serde_json::from_str(line).expect("one JSON object per line"))
        .collect()
}

fn git(repository: &Path, arguments: &[&str]) -> String {
    let output = Command::new("git")
        .arg("-C")
        .arg(repository)
        .args(arguments)
        .output()
        .expect("git runs");
    assert!(
        output.status.success(),
        "git {arguments:?}: {}",
        String::from_utf8_lossy(&output.stderr)
    );
    String::from_utf8_lossy(&output.stdout).trim().to_owned()
}

/// A fresh committed checkout at `repository`, carrying a published banner or not.
fn checkout(repository: &Path, banner: bool) {
    fs::create_dir_all(repository.join("assets")).unwrap();
    git(repository, &["init", "-q"]);
    fs::write(repository.join("README.md"), "# test\n").unwrap();
    if banner {
        fs::write(repository.join("assets/readme-banner.svg"), "<svg/>").unwrap();
    }
    git(repository, &["add", "-A"]);
    git(repository, &["commit", "-q", "-m", "start"]);
}

/// A directory holding `a-plain` (no banner) and `b-published` (a banner), in that order.
fn checkouts(name: &str) -> PathBuf {
    let root = Path::new(env!("CARGO_TARGET_TMPDIR"))
        .join("bot")
        .join(name);
    let _ = fs::remove_dir_all(&root);
    checkout(&root.join("a-plain"), false);
    checkout(&root.join("b-published"), true);
    root
}

#[test]
fn declare_local_reports_then_declares_then_leaves_a_declared_checkout_alone() {
    let root = checkouts("declare");
    let root_arg = root.to_str().unwrap();
    let published = root.join("b-published");
    let declaration = published.join(".tama/violations-ignore");

    let report = bot(&["declare-local", "--root", root_arg]);
    assert!(report.status.success());
    let reasons: Vec<String> = rows(&report)
        .iter()
        .map(|row| row["reason"].as_str().unwrap().to_owned())
        .collect();
    assert_eq!(reasons, ["no published banner", "would declare the banner"]);
    assert!(
        !declaration.exists(),
        "a report-only run wrote the declaration"
    );

    let applied = bot(&["declare-local", "--root", root_arg, "--apply", "--commit"]);
    assert!(applied.status.success());
    let row = &rows(&applied)[1];
    assert_eq!(row["reason"], "declared and committed");
    assert!(fs::read_to_string(&declaration)
        .unwrap()
        .lines()
        .any(|line| line == "assets/readme-banner.svg"));
    assert_eq!(
        row["revision"],
        git(&published, &["rev-parse", "--short", "HEAD"])
    );
    assert_eq!(git(&published, &["status", "--short"]), "");

    let again = bot(&["declare-local", "--root", root_arg, "--apply"]);
    assert_eq!(rows(&again)[1]["reason"], "already declared");
}

#[test]
fn an_existing_declaration_is_appended_to_not_replaced() {
    let root = checkouts("append");
    let published = root.join("b-published");
    fs::create_dir_all(published.join(".tama")).unwrap();
    fs::write(published.join(".tama/violations-ignore"), "Cargo.lock").unwrap();
    let applied = bot(&[
        "declare-local",
        "--root",
        published.to_str().unwrap(),
        "--apply",
    ]);
    assert_eq!(rows(&applied)[0]["reason"], "declared the banner");
    let text = fs::read_to_string(published.join(".tama/violations-ignore")).unwrap();
    assert!(text.starts_with("Cargo.lock\n"));
    assert!(text.ends_with("assets/readme-banner.svg\n"));
}

#[test]
fn mutations_without_a_token_are_refused_before_any_request() {
    let mutations = [
        "sync",
        "clear-unapproved-descriptions",
        "sync-approved-descriptions",
    ];
    for command in mutations {
        let output = bot(&[command]);
        assert_eq!(output.status.code(), Some(2), "{command}");
        assert!(String::from_utf8_lossy(&output.stderr)
            .contains("WISENT_BANNER_GITHUB_TOKEN must contain a GitHub token for mutation"));
    }
}

#[test]
fn plan_reads_the_organization_and_changes_nothing() {
    let output = bot(&[
        "plan",
        "--org",
        "wisent-ai",
        "--include",
        "wisent-visuals",
        "--include",
        "brama",
    ]);
    assert!(
        output.status.success(),
        "{}",
        String::from_utf8_lossy(&output.stderr)
    );
    for row in rows(&output) {
        let repository = row["repository"].as_str().unwrap();
        assert!(repository == "wisent-ai/wisent-visuals" || repository == "wisent-ai/brama");
        assert_eq!(row["fingerprint"].as_str().unwrap().len(), 16);
        assert!(row["layout"].as_str().unwrap().ends_with("-left"));
        assert!(
            row.get("pull_request").is_none(),
            "plan published something"
        );
    }
}

#[test]
fn an_unknown_organization_names_github_s_answer() {
    let output = bot(&["plan", "--org", "wisent-ai-no-such-organization"]);
    assert_eq!(output.status.code(), Some(1));
    assert!(String::from_utf8_lossy(&output.stderr).contains("failed (404)"));
}
