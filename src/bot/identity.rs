//! What a repository's banner says and draws.
//!
//! Copy comes only from the approval register (`identity/approved_copy.json`),
//! which records the conversation and time that approved each title. Artwork is
//! never guessed from words in a description: a repository whose banner the bot
//! already published keeps the layout written in its own `.github/banner.toml`,
//! and a repository without one gets the layout its name's SHA-256 selects, so
//! the same repository always receives the same artwork.

use std::collections::BTreeMap;

use serde::Deserialize;
use serde_json::Value;
use sha2::{Digest, Sha256};

use crate::banner::{BannerConfig, SUPPORTED_LAYOUTS};

/// Bumped when the fingerprint payload changes meaning, so every banner is redone.
const IDENTITY_SCHEMA_VERSION: u32 = 9;
/// The category written for a layout chosen from the repository name.
const SEEDED_CATEGORY: &str = "seeded";

const APPROVED_COPY: &str = include_str!("../../identity/approved_copy.json");

#[derive(Deserialize)]
pub struct ApprovedCopy {
    pub title: String,
    #[serde(default)]
    pub description: String,
    pub approved_in: String,
}

#[derive(Deserialize)]
struct Register {
    schema: u32,
    entries: BTreeMap<String, ApprovedCopy>,
}

/// The approval register, keyed by lower-case repository name.
pub fn approved_register() -> Result<BTreeMap<String, ApprovedCopy>, String> {
    let register: Register = serde_json::from_str(APPROVED_COPY)
        .map_err(|e| format!("identity/approved_copy.json: {e}"))?;
    if register.schema != 1 {
        return Err(format!(
            "identity/approved_copy.json declares schema {}, this bot reads schema 1",
            register.schema
        ));
    }
    Ok(register.entries)
}

/// What a bot-managed `.github/banner.toml` already says.
#[derive(Default)]
pub struct Published {
    pub fingerprint: String,
    pub category: String,
    pub copy_status: String,
    pub title: String,
    pub layout: String,
}

impl Published {
    /// The managed configuration's facts, or `None` for a missing, unreadable or
    /// hand-written one.
    pub fn read(config: &[u8]) -> Option<Self> {
        let document: toml::Table = std::str::from_utf8(config).ok()?.parse().ok()?;
        let automation = document.get("automation")?.as_table()?;
        if automation.get("managed")?.as_bool() != Some(true) {
            return None;
        }
        let banner = document.get("banner").and_then(toml::Value::as_table);
        let field = |table: Option<&toml::Table>, key: &str| {
            table
                .and_then(|t| t.get(key))
                .and_then(toml::Value::as_str)
                .unwrap_or_default()
                .to_owned()
        };
        Some(Self {
            fingerprint: field(Some(automation), "source_fingerprint"),
            category: field(Some(automation), "category"),
            copy_status: field(Some(automation), "copy_status"),
            title: field(banner, "title"),
            layout: field(banner, "layout"),
        })
    }
}

/// Approved copy and deterministic artwork for one repository.
pub struct BannerIdentity {
    pub category: String,
    pub title: String,
    pub description: String,
    pub layout: String,
    pub art_seed: String,
    pub fingerprint: String,
    pub copy_status: &'static str,
    pub approved_in: String,
}

impl BannerIdentity {
    pub fn generate(
        name: &str,
        approved: Option<&ApprovedCopy>,
        published: Option<&Published>,
    ) -> Result<Self, String> {
        let kept = published.filter(|p| SUPPORTED_LAYOUTS.contains(&p.layout.as_str()));
        let (category, layout) = match kept {
            Some(p) => (p.category.clone(), p.layout.clone()),
            None => {
                let digest = Sha256::digest(name.as_bytes());
                let index = usize::from(digest[0]) % SUPPORTED_LAYOUTS.len();
                (
                    SEEDED_CATEGORY.to_owned(),
                    SUPPORTED_LAYOUTS[index].to_owned(),
                )
            }
        };
        let (title, description, approved_in, copy_status) = match approved {
            Some(copy) => {
                let title = copy.title.trim();
                let approved_in = copy.approved_in.trim();
                if title.is_empty() || approved_in.is_empty() {
                    return Err(format!(
                        "approved copy for {name} lacks title or approved_in"
                    ));
                }
                (
                    title.to_owned(),
                    copy.description.trim().to_owned(),
                    approved_in.to_owned(),
                    "approved",
                )
            }
            None => {
                // Without approval the banner names the repository. A title the bot
                // published earlier without approval is kept, so this rule alone
                // does not reopen a pull request on every such repository.
                let title = published
                    .filter(|p| p.copy_status == "missing" && !p.title.is_empty())
                    .map_or_else(|| name.to_owned(), |p| p.title.clone());
                (title, String::new(), String::new(), "missing")
            }
        };
        let fingerprint = fingerprint(name, &category, &layout, &title, &description, &approved_in);
        Ok(Self {
            category,
            title,
            description,
            layout,
            art_seed: name.to_owned(),
            fingerprint,
            copy_status,
            approved_in,
        })
    }

    pub fn approved_title(&self) -> Option<&str> {
        (self.copy_status == "approved").then_some(self.title.as_str())
    }

    pub fn as_config(&self) -> BannerConfig {
        BannerConfig {
            title: self.title.clone(),
            description: self.description.clone(),
            layout: self.layout.clone(),
            art_seed: self.art_seed.clone(),
            ..BannerConfig::default()
        }
    }

    pub fn to_toml(&self) -> String {
        let defaults = BannerConfig::default();
        let quote = |value: &str| Value::from(value).to_string();
        [
            "[automation]".to_owned(),
            "managed = true".to_owned(),
            format!("source_fingerprint = {}", quote(&self.fingerprint)),
            format!("category = {}", quote(&self.category)),
            format!("copy_status = {}", quote(self.copy_status)),
            format!("approved_in = {}", quote(&self.approved_in)),
            String::new(),
            "[banner]".to_owned(),
            format!("title = {}", quote(&self.title)),
            format!("description = {}", quote(&self.description)),
            format!("product = {}", quote(&defaults.product)),
            format!("url = {}", quote(&defaults.url)),
            format!("theme = {}", quote(&defaults.theme)),
            format!("layout = {}", quote(&self.layout)),
            format!("art_seed = {}", quote(&self.art_seed)),
            format!("width = {}", defaults.width),
            format!("height = {}", defaults.height),
            String::new(),
        ]
        .join("\n")
    }
}

/// The first 16 hex digits of the SHA-256 of the sorted, compact, ASCII-escaped
/// JSON payload, byte for byte what earlier bot runs wrote, so a repository whose
/// facts did not change is not offered another pull request.
fn fingerprint(
    name: &str,
    category: &str,
    layout: &str,
    title: &str,
    description: &str,
    approved_in: &str,
) -> String {
    let payload = serde_json::json!({
        "approved_in": approved_in,
        "category": category,
        "description": description,
        "identity_schema_version": IDENTITY_SCHEMA_VERSION,
        "layout": layout,
        "name": name,
        "title": title,
    });
    let digest = Sha256::digest(ascii_escaped(&payload.to_string()).as_bytes());
    digest[..8]
        .iter()
        .map(|byte| format!("{byte:02x}"))
        .collect()
}

/// JSON text with every non-ASCII character written as `\uXXXX` UTF-16 units.
fn ascii_escaped(json: &str) -> String {
    let mut out = String::with_capacity(json.len());
    for character in json.chars() {
        if character.is_ascii() {
            out.push(character);
        } else {
            let mut units = [0u16; 2];
            for unit in character.encode_utf16(&mut units) {
                out.push_str(&format!("\\u{unit:04x}"));
            }
        }
    }
    out
}
