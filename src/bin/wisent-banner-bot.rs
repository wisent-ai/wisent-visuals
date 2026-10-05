//! `wisent-banner-bot`: keep every repository of an organization presenting its
//! approved banner and README buttons.

use std::collections::BTreeSet;
use std::env;
use std::path::PathBuf;
use std::process::ExitCode;

use clap::{Parser, ValueEnum};
use serde::Deserialize;
use serde_json::json;

use wisent_visuals::bot::audit::declare_tree;
use wisent_visuals::bot::github::GitHubClient;
use wisent_visuals::bot::identity::approved_register;
use wisent_visuals::bot::BannerBot;

const UNAPPROVED_DESCRIPTIONS: &str = include_str!("../../identity/unapproved_descriptions.json");

#[derive(Clone, Copy, PartialEq, Eq, ValueEnum)]
enum Command {
    /// Print what each repository would receive, changing nothing.
    Plan,
    /// Publish every plan as a pull request (or directly with --direct).
    Sync,
    /// Write the audit declaration into local checkouts under --root.
    DeclareLocal,
    /// Clear the descriptions listed in identity/unapproved_descriptions.json.
    ClearUnapprovedDescriptions,
    /// Set every repository description to its approved one, or empty.
    SyncApprovedDescriptions,
}

#[derive(Parser)]
#[command(
    name = "wisent-banner-bot",
    version,
    about = "Keep organization READMEs presenting approved Wisent banners."
)]
struct Args {
    command: Command,
    #[arg(long, default_value = "wisent-ai")]
    org: String,
    /// Repository to leave alone; repeat for more. Without it, `wisent` is left alone.
    #[arg(long, default_value = "wisent")]
    exclude: Vec<String>,
    /// Only these repositories; repeat for more.
    #[arg(long)]
    include: Vec<String>,
    /// Commit to the default branch instead of opening pull requests.
    #[arg(long)]
    direct: bool,
    /// Stop after this many plans; without it every repository is planned.
    #[arg(long)]
    limit: Option<usize>,
    /// Environment variable holding the GitHub token.
    #[arg(long, default_value = "WISENT_BANNER_GITHUB_TOKEN")]
    token_env: String,
    /// Checkout, or directory of checkouts, for declare-local.
    #[arg(long, default_value = ".")]
    root: PathBuf,
    /// declare-local writes the files; without it the run only reports.
    #[arg(long)]
    apply: bool,
    /// declare-local commits the file it wrote in that checkout.
    #[arg(long)]
    commit: bool,
    /// declare-local pushes the commit it made.
    #[arg(long)]
    push: bool,
}

#[derive(Deserialize)]
struct Unapproved {
    schema: u32,
    repositories: Vec<String>,
}

fn print(value: serde_json::Value) {
    println!("{value}");
}

fn run(args: &Args, token: String) -> Result<(), String> {
    let client = GitHubClient::new(token);
    match args.command {
        Command::DeclareLocal => {
            for declaration in declare_tree(&args.root, args.apply, args.commit, args.push)? {
                print(json!({
                    "repository": declaration.repository.display().to_string(),
                    "wrote": declaration.wrote,
                    "reason": declaration.reason,
                    "revision": declaration.revision,
                }));
            }
        }
        Command::ClearUnapprovedDescriptions => {
            let document: Unapproved = serde_json::from_str(UNAPPROVED_DESCRIPTIONS)
                .map_err(|e| format!("identity/unapproved_descriptions.json: {e}"))?;
            if document.schema != 1 {
                return Err(format!(
                    "identity/unapproved_descriptions.json declares schema {}, this bot reads schema 1",
                    document.schema
                ));
            }
            for repository in &document.repositories {
                let changed = client.set_description(&args.org, repository, "")?;
                print(
                    json!({"repository": format!("{}/{repository}", args.org), "description": "", "changed": changed}),
                );
            }
        }
        Command::SyncApprovedDescriptions => {
            let register = approved_register()?;
            for repository in client.list_repositories(&args.org)? {
                let Some(name) = repository.get("name").and_then(|n| n.as_str()) else {
                    return Err("GitHub listed a repository without a name".into());
                };
                let description = register
                    .get(&name.to_lowercase())
                    .map_or("", |copy| copy.description.trim());
                let changed = client.set_description(&args.org, name, description)?;
                print(
                    json!({"repository": format!("{}/{name}", args.org), "description": description, "changed": changed}),
                );
            }
        }
        Command::Plan | Command::Sync => {
            let bot = BannerBot {
                client,
                excluded: args.exclude.iter().cloned().collect(),
                included: (!args.include.is_empty())
                    .then(|| args.include.iter().cloned().collect::<BTreeSet<_>>()),
                approved: approved_register()?,
            };
            for plan in bot.plans(&args.org, args.limit)? {
                let mut summary = json!({
                    "repository": format!("{}/{}", plan.owner, plan.name),
                    "reason": plan.reason,
                    "category": plan.identity.category,
                    "title": plan.identity.title,
                    "description": plan.identity.description,
                    "layout": plan.identity.layout,
                    "fingerprint": plan.identity.fingerprint,
                });
                if args.command == Command::Sync {
                    let key = if args.direct {
                        "repository_url"
                    } else {
                        "pull_request"
                    };
                    summary[key] = json!(bot.apply(&plan, args.direct)?);
                }
                print(summary);
            }
        }
    }
    Ok(())
}

fn main() -> ExitCode {
    let args = Args::parse();
    let token = env::var(&args.token_env).unwrap_or_default();
    let mutates = matches!(
        args.command,
        Command::Sync | Command::ClearUnapprovedDescriptions | Command::SyncApprovedDescriptions
    );
    if mutates && token.is_empty() {
        eprintln!(
            "wisent-banner-bot: {} must contain a GitHub token for mutation",
            args.token_env
        );
        return ExitCode::from(2);
    }
    match run(&args, token) {
        Ok(()) => ExitCode::SUCCESS,
        Err(error) => {
            eprintln!("wisent-banner-bot: {error}");
            ExitCode::FAILURE
        }
    }
}
