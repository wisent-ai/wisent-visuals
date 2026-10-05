//! `wisent-visuals-release`: the release-contract commands of the Python
//! package — `surface [root] [--tolerant]` prints what a caller can import and
//! call; `baseline [--print | --prefer-wheel | --cross-check]` rewrites
//! `released-surface.json` from the version PyPI serves.

mod baseline;
mod module;
mod surface;

use std::path::{Path, PathBuf};

use serde_json::json;

pub use surface::{surface, Surface, PACKAGE};

pub const USAGE: &str = "usage: wisent-visuals-release surface [root] [--tolerant] | baseline [--print | --prefer-wheel | --cross-check]";

/// How an invocation ended: answered, refused (exit 1), or written wrong (exit 2).
pub enum Outcome {
    Done,
    Refused(String),
    Usage,
}

fn print_surface(root: &Path, tolerant: bool) -> Result<(), String> {
    let found = surface(root, tolerant)?;
    let mut document = serde_json::Map::new();
    document.insert("surface".to_string(), json!(found.names));
    if !found.unparseable.is_empty() {
        document.insert("unparseable".to_string(), json!(found.unparseable));
    }
    if !found.unresolved.is_empty() {
        document.insert("unresolved".to_string(), json!(found.unresolved));
    }
    println!("{}", serde_json::to_string_pretty(&document).map_err(|error| error.to_string())?);
    Ok(())
}

/// Run one command; `repository` is the checkout the commands default to.
pub fn run(arguments: &[String], repository: &Path) -> Outcome {
    let Some((command, rest)) = arguments.split_first() else { return Outcome::Usage };
    let outcome = match command.as_str() {
        "surface" => {
            let root = rest
                .iter()
                .find(|argument| !argument.starts_with('-'))
                .map(PathBuf::from)
                .unwrap_or_else(|| repository.to_path_buf());
            print_surface(&root, rest.iter().any(|argument| argument == "--tolerant"))
        }
        "baseline" => baseline::run(repository, rest),
        _ => return Outcome::Usage,
    };
    match outcome {
        Ok(()) => Outcome::Done,
        Err(refusal) => Outcome::Refused(refusal),
    }
}
