//! The public surface of the `wisent_plots` Python package: what a caller can
//! import and call, read from the source and never by importing it (importing
//! needs matplotlib and numpy, and a release decision must not).
//!
//! Three things make up the contract, because all three are things a user would
//! notice disappearing: exported names qualified by the module that exports
//! them (`wisent_plots:AreaChart`); public methods of exported classes
//! (`wisent_plots:AreaChart.plot`), resolved through the re-export chain; and
//! keys of exported literal mappings (`wisent_plots.styles:STYLES[3]`), because
//! a registry's keys are selectable capabilities.
//!
//! A module that does not parse, an `__all__` that is not a literal list of
//! strings, or a star import is a refusal, not a smaller answer: the surface is
//! unknown, and the versioning rule would read a short surface as removed
//! capability.

use std::collections::{BTreeMap, BTreeSet};
use std::path::{Path, PathBuf};

use super::module::{module_name, Binding, Module, ALL};

pub const PACKAGE: &str = "wisent_plots";

/// The surface of the package under a root, what `tolerant` let it skip, and
/// the promised names whose definition could not be found.
pub struct Surface {
    pub names: Vec<String>,
    pub unparseable: Vec<String>,
    pub unresolved: Vec<String>,
}

fn python_files(directory: &Path, found: &mut Vec<PathBuf>) -> Result<(), String> {
    let entries = std::fs::read_dir(directory).map_err(|error| format!("{}: {error}", directory.display()))?;
    for entry in entries {
        let path = entry.map_err(|error| format!("{}: {error}", directory.display()))?.path();
        if path.is_dir() {
            python_files(&path, found)?;
        } else if path.extension().is_some_and(|extension| extension == "py") {
            found.push(path);
        }
    }
    Ok(())
}

/// Follow re-exports to the binding that actually defines `name`.
fn definition<'m>(modules: &'m BTreeMap<String, Module>, module: &str, name: &str) -> Option<&'m Binding> {
    let mut seen = BTreeSet::new();
    let (mut module, mut name) = (module.to_string(), name.to_string());
    while seen.insert((module.clone(), name.clone())) {
        let owner = modules.get(&module)?;
        if let Some(bound) = owner.defines.get(&name) {
            return Some(bound);
        }
        let (source, original) = owner.imports.get(&name)?;
        module = source.clone();
        name = original.clone();
    }
    None
}

pub fn surface(root: &Path, tolerant: bool) -> Result<Surface, String> {
    let package = root.join(PACKAGE);
    if !package.is_dir() {
        return Err(format!(
            "{} is not a directory; is {} the repository root?",
            package.display(),
            root.display()
        ));
    }
    let mut files = Vec::new();
    python_files(&package, &mut files)?;
    files.sort();
    let mut modules = BTreeMap::new();
    let mut unparseable = Vec::new();
    for path in files {
        let name = module_name(&path, root);
        match Module::parse(&name, &path) {
            Ok(module) => {
                modules.insert(name, module);
            }
            Err(_) if tolerant => unparseable.push(path.strip_prefix(root).unwrap_or(&path).display().to_string()),
            Err(refusal) => return Err(refusal),
        }
    }
    let mut names = BTreeSet::new();
    let mut unresolved = Vec::new();
    for (owner, module) in &modules {
        for exported in module.exports.iter().flatten() {
            let qualified = format!("{owner}:{exported}");
            names.insert(qualified.clone());
            match definition(&modules, owner, exported) {
                None => unresolved.push(qualified),
                Some(Binding::Class(methods)) => {
                    names.extend(methods.iter().map(|method| format!("{qualified}.{method}")));
                }
                Some(Binding::Mapping(keys)) => {
                    names.extend(keys.iter().map(|key| format!("{qualified}[{key}]")));
                }
                Some(Binding::Other) => {}
            }
        }
    }
    if names.is_empty() {
        return Err(format!(
            "no {ALL} declarations found under {}. Either the package stopped stating its public API, or it \
             moved — both change what this library promises, so refusing rather than reporting an empty surface",
            package.display()
        ));
    }
    Ok(Surface { names: names.into_iter().collect(), unparseable, unresolved })
}
