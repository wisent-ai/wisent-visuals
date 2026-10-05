//! The organization-wide README banner bot: plan what each repository lacks,
//! then publish it as a pull request, or directly with `--direct`.

pub mod audit;
pub mod github;
pub mod identity;
pub mod readme;

use std::collections::{BTreeMap, BTreeSet};

use serde_json::Value;

use crate::banner::Banner;
use github::GitHubClient;
use identity::{ApprovedCopy, BannerIdentity, Published};

pub const BANNER_START: &str = "<!-- wisent-banner:start -->";
pub const BANNER_END: &str = "<!-- wisent-banner:end -->";
pub const BANNER_PATH: &str = "assets/readme-banner.webp";
pub const SVG_PATH: &str = "assets/readme-banner.svg";
pub const CONFIG_PATH: &str = ".github/banner.toml";
pub const SIGNALS_START: &str = "<!-- wisent-readme-signals:start -->";
pub const SIGNALS_END: &str = "<!-- wisent-readme-signals:end -->";
pub const LEGACY_BANNER_PATH: &str = "banner.png";
pub const AUDIT_IGNORE_PATH: &str = ".tama/violations-ignore";

fn audit_declaration_text() -> String {
    format!(
        "# Written by the wisent-visuals banner bot. The banner below is rendered\n\
         # from .github/banner.toml and replaced whole on every run, so a repository\n\
         # audit reads it as generated output instead of asking somebody to split it.\n\
         {SVG_PATH}\n"
    )
}

/// The declaration file to write, or `None` when the repository already says this.
/// A repository declares more than banners there, so an existing file is appended to.
pub fn audit_declaration(existing: Option<&str>) -> Option<String> {
    let Some(existing) = existing else {
        return Some(audit_declaration_text());
    };
    if existing.lines().any(|line| line.trim() == SVG_PATH) {
        return None;
    }
    let separator = if existing.ends_with('\n') { "" } else { "\n" };
    Some(format!("{existing}{separator}{}", audit_declaration_text()))
}

/// A banner update ready to render and submit.
pub struct RepositoryPlan {
    pub owner: String,
    pub name: String,
    pub default_branch: String,
    pub identity: BannerIdentity,
    pub readme: String,
    pub reason: &'static str,
    pub manage_banner: bool,
    pub empty: bool,
    pub remove_legacy_banner: bool,
    pub audit_ignore: Option<String>,
}

pub struct BannerBot {
    pub client: GitHubClient,
    pub excluded: BTreeSet<String>,
    pub included: Option<BTreeSet<String>>,
    pub approved: BTreeMap<String, ApprovedCopy>,
}

fn utf8(bytes: Vec<u8>, what: &str) -> Result<String, String> {
    String::from_utf8(bytes).map_err(|e| format!("{what} is not UTF-8: {e}"))
}

impl BannerBot {
    /// Every repository whose README buttons or managed banner are missing or stale.
    pub fn plans(
        &self,
        organization: &str,
        limit: Option<usize>,
    ) -> Result<Vec<RepositoryPlan>, String> {
        let mut plans = Vec::new();
        for repository in self.client.list_repositories(organization)? {
            if limit.is_some_and(|limit| plans.len() >= limit) {
                break;
            }
            let flag = |key: &str| repository.get(key).and_then(Value::as_bool) == Some(true);
            let field = |key: &str| repository.get(key).and_then(Value::as_str);
            let name = field("name").ok_or("GitHub listed a repository without a name")?;
            if self.excluded.contains(name)
                || self
                    .included
                    .as_ref()
                    .is_some_and(|set| !set.contains(name))
                || flag("archived")
                || flag("disabled")
                || flag("fork")
            {
                continue;
            }
            let default_branch = field("default_branch")
                .ok_or_else(|| format!("{organization}/{name} has no default branch"))?;
            let read = |path: &str| {
                self.client
                    .read_content(organization, name, path, default_branch)
            };
            let readme_file = read("README.md")?;
            let readme = readme_file
                .as_ref()
                .map(|file| String::from_utf8_lossy(&file.bytes).into_owned())
                .unwrap_or_default();
            let config = read(CONFIG_PATH)?;
            let declared = read(AUDIT_IGNORE_PATH)?
                .map(|file| utf8(file.bytes, &format!("{name}:{AUDIT_IGNORE_PATH}")))
                .transpose()?;

            let published = config
                .as_ref()
                .and_then(|file| Published::read(&file.bytes));
            let identity = BannerIdentity::generate(
                name,
                self.approved.get(&name.to_lowercase()),
                published.as_ref(),
            )?;
            let manage_banner = !readme::has_manual_banner(&readme);
            let banner_current = published.as_ref().map(|p| p.fingerprint.as_str())
                == Some(identity.fingerprint.as_str());
            let readme_current =
                readme::update_readme(&readme, name, organization, identity.approved_title())
                    == readme;
            if readme_current && (!manage_banner || banner_current) {
                continue;
            }
            let reason = if !readme_current && (!manage_banner || banner_current) {
                "README buttons missing or stale"
            } else if config.is_none() {
                "new repository"
            } else {
                "repository identity changed"
            };
            let size = repository.get("size").and_then(Value::as_u64);
            plans.push(RepositoryPlan {
                owner: organization.to_owned(),
                name: name.to_owned(),
                default_branch: default_branch.to_owned(),
                remove_legacy_banner: readme::opening_legacy_banner(&readme),
                identity,
                readme,
                reason,
                manage_banner,
                empty: readme_file.is_none() && size == Some(0),
                audit_ignore: declared,
            });
        }
        Ok(plans)
    }

    fn files(plan: &RepositoryPlan) -> Result<Vec<(&'static str, Vec<u8>)>, String> {
        let readme = readme::update_readme(
            &plan.readme,
            &plan.name,
            &plan.owner,
            plan.identity.approved_title(),
        );
        let mut files = vec![("README.md", readme.into_bytes())];
        if plan.manage_banner {
            let banner = Banner::new(plan.identity.as_config())?;
            files.push((CONFIG_PATH, plan.identity.to_toml().into_bytes()));
            files.push((SVG_PATH, banner.render_svg()?.into_bytes()));
            files.push((BANNER_PATH, banner.render_webp()?));
            if let Some(declaration) = audit_declaration(plan.audit_ignore.as_deref()) {
                files.push((AUDIT_IGNORE_PATH, declaration.into_bytes()));
            }
        }
        Ok(files)
    }

    /// Write the plan's files to `branch`, skipping any already identical, and
    /// remove the superseded `banner.png` when the plan says so.
    fn write_branch(
        &self,
        plan: &RepositoryPlan,
        branch: &str,
        files: &[(&'static str, Vec<u8>)],
        suffix: &str,
    ) -> Result<(), String> {
        let (owner, name) = (plan.owner.as_str(), plan.name.as_str());
        for (path, content) in files {
            let existing = self.client.read_content(owner, name, path, branch)?;
            if existing.as_ref().is_some_and(|file| &file.bytes == content) {
                continue;
            }
            self.client.write_content(
                owner,
                name,
                path,
                Some(branch),
                content,
                &format!("docs: add personalized README banner and buttons{suffix}"),
                existing.as_ref().map(|file| file.sha.as_str()),
            )?;
        }
        if plan.remove_legacy_banner {
            if let Some(legacy) =
                self.client
                    .read_content(owner, name, LEGACY_BANNER_PATH, branch)?
            {
                self.client.delete_content(
                    owner,
                    name,
                    LEGACY_BANNER_PATH,
                    branch,
                    &format!("docs: remove superseded README banner{suffix}"),
                    &legacy.sha,
                )?;
            }
        }
        Ok(())
    }

    /// Publish one plan; the answer is the repository or pull request URL.
    pub fn apply(&self, plan: &RepositoryPlan, direct: bool) -> Result<String, String> {
        let files = Self::files(plan)?;
        let (owner, name) = (plan.owner.as_str(), plan.name.as_str());
        let repository_url = format!("https://github.com/{owner}/{name}");
        if plan.empty {
            // The README commit creates the default branch; the rest follow on it.
            for (index, (path, content)) in files.iter().enumerate() {
                let (branch, message) = if index == 0 {
                    (None, "docs: initialize README presentation [skip ci]")
                } else {
                    (
                        Some(plan.default_branch.as_str()),
                        "docs: add personalized README banner [skip ci]",
                    )
                };
                self.client
                    .write_content(owner, name, path, branch, content, message, None)?;
            }
            return Ok(repository_url);
        }
        if direct {
            self.write_branch(plan, &plan.default_branch, &files, " [skip ci]")?;
            return Ok(repository_url);
        }
        let branch = format!("wisent-readme-bot/{}", plan.identity.fingerprint);
        self.client
            .ensure_branch(owner, name, &plan.default_branch, &branch)?;
        self.write_branch(plan, &branch, &files, "")?;
        let body = format!(
            "Adds a deterministic banner generated from repository facts and a compact \
             button strip linking to `{owner}/{name}`, its issues, Wisent, Discord, \
             LinkedIn, X, and the enterprise contact route.\n\n\
             Bot-owned README markup is bounded by explicit comments. Generated banner \
             assets remain editable through `{CONFIG_PATH}`."
        );
        self.client
            .open_pull_request(owner, name, &branch, &plan.default_branch, &body)
    }
}
