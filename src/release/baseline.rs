//! Regenerate `released-surface.json`: the public surface of the version PyPI
//! actually serves, never the version this repository declares, read from the
//! published artifact with the same extractor `surface` uses.
//!
//! The `source` field starts with a provenance marker — `pypi-sdist:<file>` or
//! `pypi-wheel:<file>` — so the version-check workflow can assert in both
//! directions that the registry serves what the baseline claims. Preference is
//! the best tier that exists: sdist, then a pure-Python wheel. A tier this does
//! not implement is a refusal, never a silent downgrade.

use std::io::Read;
use std::path::{Path, PathBuf};

use serde::Serialize;
use serde_json::Value;

use super::surface::{surface, PACKAGE};

const PROJECT: &str = "wisent-visuals";
const BASELINE: &str = "released-surface.json";
const SDIST_MARKER: &str = "pypi-sdist";
const WHEEL_MARKER: &str = "pypi-wheel";
const PURE_WHEEL: &str = "py3-none-any.whl";
const WORKSPACE: &str = ".baseline-artifact";

fn index() -> String {
    format!("https://pypi.org/pypi/{PROJECT}/json")
}

fn registry() -> Result<Value, String> {
    let url = index();
    let response = ureq::get(&url).call().map_err(|error| {
        format!("cannot reach {url}: {error}. Refusing to write a baseline without confirming what is actually published")
    })?;
    let body = response
        .into_string()
        .map_err(|error| format!("{url} could not be read: {error}"))?;
    serde_json::from_str(&body).map_err(|error| format!("{url} answered something that is not JSON: {error}"))
}

/// The latest published version, its tier marker, and the artifact for it.
fn published(data: &Value, prefer_wheel: bool) -> Result<(String, &'static str, Value), String> {
    let version = data["info"]["version"]
        .as_str()
        .ok_or_else(|| format!("{} names no info.version", index()))?
        .to_string();
    let files = data["releases"][&version].as_array().cloned().unwrap_or_default();
    let is_wheel = |file: &Value| file["filename"].as_str().is_some_and(|name| name.ends_with(PURE_WHEEL));
    let is_sdist = |file: &Value| file["packagetype"].as_str() == Some("sdist");
    let mut tiers: Vec<(&'static str, &dyn Fn(&Value) -> bool)> =
        vec![(SDIST_MARKER, &is_sdist), (WHEEL_MARKER, &is_wheel)];
    if prefer_wheel {
        tiers.reverse();
    }
    for (marker, matches) in tiers {
        if let Some(file) = files.iter().find(|file| matches(file)) {
            return Ok((version, marker, file.clone()));
        }
    }
    let names: Vec<&str> = files.iter().filter_map(|file| file["filename"].as_str()).collect();
    Err(format!(
        "{PROJECT} {version} is published but offers neither an sdist nor a pure-Python wheel: {names:?}. \
         The tier needed here is not implemented, and degrading to HEAD would claim an unpublished baseline \
         is a published one"
    ))
}

fn fetch(url: &str) -> Result<Vec<u8>, String> {
    let response = ureq::get(url).call().map_err(|error| format!("cannot download {url}: {error}"))?;
    let mut payload = Vec::new();
    response
        .into_reader()
        .read_to_end(&mut payload)
        .map_err(|error| format!("cannot download {url}: {error}"))?;
    Ok(payload)
}

/// Unpack an artifact off the network into `into`; neither archive reader
/// writes outside it.
fn unpack(marker: &str, payload: &[u8], into: &Path) -> Result<(), String> {
    if marker == SDIST_MARKER {
        let mut archive = tar::Archive::new(flate2::read::GzDecoder::new(payload));
        return archive.unpack(into).map_err(|error| format!("the sdist does not unpack: {error}"));
    }
    zip::ZipArchive::new(std::io::Cursor::new(payload))
        .and_then(|mut archive| archive.extract(into))
        .map_err(|error| format!("the wheel does not unpack: {error}"))
}

/// The directory that holds the package inside an unpacked artifact.
fn root_of(unpacked: &Path) -> Result<PathBuf, String> {
    if unpacked.join(PACKAGE).is_dir() {
        return Ok(unpacked.to_path_buf());
    }
    let mut children: Vec<PathBuf> = std::fs::read_dir(unpacked)
        .map_err(|error| format!("{}: {error}", unpacked.display()))?
        .filter_map(|entry| entry.ok().map(|entry| entry.path()))
        .collect();
    children.sort();
    children
        .into_iter()
        .find(|child| child.join(PACKAGE).is_dir())
        .ok_or_else(|| format!("no {PACKAGE}/ directory inside the downloaded artifact"))
}

/// Download the best published artifact and read its surface, leaving nothing behind.
fn recover(repository: &Path, prefer_wheel: bool) -> Result<(String, &'static str, String, Vec<String>), String> {
    let (version, marker, artifact) = published(&registry()?, prefer_wheel)?;
    let url = artifact["url"].as_str().ok_or("the published artifact names no url")?;
    let filename = artifact["filename"].as_str().unwrap_or_default().to_string();
    let payload = fetch(url)?;
    let workspace = repository.join(WORKSPACE);
    if workspace.exists() {
        return Err(format!("{} already exists; remove it and rerun", workspace.display()));
    }
    std::fs::create_dir(&workspace).map_err(|error| format!("{}: {error}", workspace.display()))?;
    let read = unpack(marker, &payload, &workspace)
        .and_then(|()| root_of(&workspace))
        .and_then(|root| surface(&root, false))
        .map_err(|refusal| {
            format!("the published artifact's surface is unknown, so no baseline can be written: {refusal}")
        });
    let cleaned = std::fs::remove_dir_all(&workspace);
    let names = read?.names;
    cleaned.map_err(|error| format!("{} was not removed: {error}", workspace.display()))?;
    Ok((version, marker, filename, names))
}

/// Make the sdist and wheel readers agree, or say exactly where they differ.
fn cross_check(repository: &Path) -> Result<(), String> {
    let (sdist_version, sdist_marker, _, from_sdist) = recover(repository, false)?;
    let (wheel_version, wheel_marker, _, from_wheel) = recover(repository, true)?;
    if sdist_marker == wheel_marker {
        return Err(format!(
            "only the {sdist_marker} tier exists for {PROJECT} {sdist_version}, so there is nothing to cross-check against"
        ));
    }
    if sdist_version != wheel_version {
        return Err(format!("tiers disagree on the version: {sdist_version}, {wheel_version}"));
    }
    println!("{sdist_marker}: {} names", from_sdist.len());
    println!("{wheel_marker}: {} names", from_wheel.len());
    let only_sdist: Vec<&String> = from_sdist.iter().filter(|name| !from_wheel.contains(name)).collect();
    let only_wheel: Vec<&String> = from_wheel.iter().filter(|name| !from_sdist.contains(name)).collect();
    if only_sdist.is_empty() && only_wheel.is_empty() {
        println!("both tiers agree on {PROJECT} {sdist_version}");
        return Ok(());
    }
    for name in only_sdist {
        println!("  only in {sdist_marker}: {name}");
    }
    for name in only_wheel {
        println!("  only in {wheel_marker}: {name}");
    }
    Err("the two readers disagree about the same release, so at least one of them is wrong and neither can be \
         trusted to produce a baseline"
        .to_string())
}

#[derive(Serialize)]
struct Baseline {
    version: String,
    source: String,
    surface: Vec<String>,
}

/// `baseline [--print | --prefer-wheel | --cross-check]` against the repository at `repository`.
pub fn run(repository: &Path, flags: &[String]) -> Result<(), String> {
    let has = |flag: &str| flags.iter().any(|given| given == flag);
    if has("--cross-check") {
        return cross_check(repository);
    }
    let (version, marker, filename, names) = recover(repository, has("--prefer-wheel"))?;
    let count = names.len();
    let document = Baseline {
        version: version.clone(),
        source: format!(
            "{marker}:{filename} — latest version served by PyPI for {PROJECT}, downloaded and read with \
             wisent-visuals-release surface; regenerate with wisent-visuals-release baseline"
        ),
        surface: names,
    };
    let rendered = serde_json::to_string_pretty(&document).map_err(|error| error.to_string())? + "\n";
    if has("--print") {
        print!("{rendered}");
        return Ok(());
    }
    let path = repository.join(BASELINE);
    std::fs::write(&path, rendered).map_err(|error| format!("{}: {error}", path.display()))?;
    println!("{BASELINE}: {marker} baseline {version}, {count} names");
    Ok(())
}
