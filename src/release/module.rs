//! One `wisent_plots` module read with tree-sitter: what it defines, what it
//! re-exports, and what it declares public in `__all__`.

use std::collections::BTreeMap;
use std::path::Path;

use tree_sitter::{Node, Parser};

const INIT: &str = "__init__.py";
pub(crate) const ALL: &str = "__all__";

/// What a module binds a name to, as far as the contract cares.
pub(crate) enum Binding {
    /// A class and its public method names.
    Class(Vec<String>),
    /// A literal mapping and its constant keys, written as Python writes them.
    Mapping(Vec<String>),
    /// Anything else: a function, a value.
    Other,
}

pub(crate) struct Module {
    pub(crate) defines: BTreeMap<String, Binding>,
    /// Local name → (absolute source module, name there).
    pub(crate) imports: BTreeMap<String, (String, String)>,
    pub(crate) exports: Option<Vec<String>>,
}

fn text<'s>(node: Node, source: &'s str) -> &'s str {
    &source[node.byte_range()]
}

/// The dotted name a caller would import this file as.
pub(crate) fn module_name(path: &Path, root: &Path) -> String {
    let relative = path.strip_prefix(root).unwrap_or(path);
    let mut parts: Vec<String> = relative.iter().map(|part| part.to_string_lossy().into_owned()).collect();
    if let (Some(last), Some(stem)) = (parts.last_mut(), path.file_stem()) {
        *last = stem.to_string_lossy().into_owned();
    }
    if path.file_name().is_some_and(|name| name == INIT) {
        parts.pop();
    }
    parts.join(".")
}

/// A Python string literal's value: no bytes or template prefix, no
/// interpolation or escape to decode.
fn string_literal(node: Node, source: &str) -> Option<String> {
    if node.kind() != "string" {
        return None;
    }
    let mut value = String::new();
    let mut cursor = node.walk();
    for child in node.children(&mut cursor) {
        match child.kind() {
            "string_start" => {
                let prefix = text(child, source).trim_end_matches(['"', '\'']).to_ascii_lowercase();
                if prefix.contains('b') || prefix.contains('f') || prefix.contains('t') {
                    return None;
                }
            }
            "string_content" => {
                let mut inner = child.walk();
                if child.children(&mut inner).next().is_some() {
                    return None;
                }
                value.push_str(text(child, source));
            }
            "string_end" => {}
            _ => return None,
        }
    }
    Some(value)
}

/// Python's `repr` of a constant dictionary key; `None` for a key that is not a constant.
fn key_repr(node: Node, source: &str) -> Option<String> {
    match node.kind() {
        "string" => string_literal(node, source).map(|value| {
            if value.contains('\'') && !value.contains('"') {
                format!("\"{value}\"")
            } else {
                format!("'{}'", value.replace('\'', "\\'"))
            }
        }),
        "integer" => {
            let digits = text(node, source).replace('_', "");
            Some(digits.parse::<i128>().map(|number| number.to_string()).unwrap_or(digits))
        }
        "float" => Some(text(node, source).to_string()),
        "true" => Some("True".to_string()),
        "false" => Some("False".to_string()),
        "none" => Some("None".to_string()),
        _ => None,
    }
}

fn definition_of(statement: Node) -> Node {
    match statement.kind() {
        "decorated_definition" => statement.child_by_field_name("definition").unwrap_or(statement),
        _ => statement,
    }
}

fn public_methods(class: Node, source: &str) -> Vec<String> {
    let Some(body) = class.child_by_field_name("body") else { return Vec::new() };
    let mut cursor = body.walk();
    body.named_children(&mut cursor)
        .map(definition_of)
        .filter(|member| member.kind() == "function_definition")
        .filter_map(|member| member.child_by_field_name("name"))
        .map(|name| text(name, source).to_string())
        .filter(|name| !name.starts_with('_'))
        .collect()
}

fn binding(value: Node, source: &str) -> Binding {
    if value.kind() != "dictionary" {
        return Binding::Other;
    }
    let mut cursor = value.walk();
    let keys = value
        .named_children(&mut cursor)
        .filter(|entry| entry.kind() == "pair")
        .filter_map(|pair| pair.child_by_field_name("key"))
        .filter_map(|key| key_repr(key, source))
        .collect();
    Binding::Mapping(keys)
}

fn read_all(value: Node, source: &str, path: &Path) -> Result<Vec<String>, String> {
    if !matches!(value.kind(), "list" | "tuple" | "expression_list") {
        return Err(format!(
            "{}: {ALL} is not a literal list, so the public surface is unknown; refusing rather than reporting a shorter one",
            path.display()
        ));
    }
    let mut cursor = value.walk();
    value
        .named_children(&mut cursor)
        .filter(|element| element.kind() != "comment")
        .map(|element| {
            string_literal(element, source).ok_or_else(|| {
                format!(
                    "{}: {ALL} holds a non-literal entry, so the public surface is unknown; refusing rather than reporting a shorter one",
                    path.display()
                )
            })
        })
        .collect()
}

impl Module {
    /// Read one module; a module that does not parse is a refusal, because its
    /// names are unknown rather than absent.
    pub(crate) fn parse(name: &str, path: &Path) -> Result<Module, String> {
        let source = std::fs::read_to_string(path).map_err(|error| format!("{}: {error}", path.display()))?;
        let mut parser = Parser::new();
        parser
            .set_language(&tree_sitter_python::LANGUAGE.into())
            .map_err(|error| format!("the Python grammar did not load: {error}"))?;
        let tree = parser
            .parse(&source, None)
            .filter(|tree| !tree.root_node().has_error())
            .ok_or_else(|| format!("{}: does not parse, so the surface is unknown", path.display()))?;
        let mut module = Module { defines: BTreeMap::new(), imports: BTreeMap::new(), exports: None };
        let root = tree.root_node();
        let mut cursor = root.walk();
        for statement in root.named_children(&mut cursor) {
            let statement = definition_of(statement);
            match statement.kind() {
                "class_definition" | "function_definition" => {
                    let Some(name_node) = statement.child_by_field_name("name") else { continue };
                    let bound = if statement.kind() == "class_definition" {
                        Binding::Class(public_methods(statement, &source))
                    } else {
                        Binding::Other
                    };
                    module.defines.insert(text(name_node, &source).to_string(), bound);
                }
                "import_from_statement" => module.absorb_import(statement, &source, name, path)?,
                "expression_statement" => {
                    let mut inner = statement.walk();
                    for expression in statement.named_children(&mut inner) {
                        module.absorb_assignment(expression, &source, path)?;
                    }
                }
                _ => {}
            }
        }
        Ok(module)
    }

    fn absorb_import(&mut self, statement: Node, source: &str, name: &str, path: &Path) -> Result<(), String> {
        let from = match statement.child_by_field_name("module_name") {
            Some(module) if module.kind() == "relative_import" => {
                let raw = text(module, source);
                let level = raw.chars().take_while(|c| *c == '.').count();
                let rest = raw[level..].trim();
                let mut parts: Vec<&str> = name.split('.').collect();
                if path.file_name().is_none_or(|file| file != INIT) {
                    parts.pop();
                }
                let keep = parts.len().saturating_sub(level.saturating_sub(1));
                parts.truncate(keep);
                if !rest.is_empty() {
                    parts.push(rest);
                }
                parts.join(".")
            }
            Some(module) => text(module, source).to_string(),
            None => String::new(),
        };
        let mut cursor = statement.walk();
        if statement.named_children(&mut cursor).any(|child| child.kind() == "wildcard_import") {
            return Err(format!(
                "{}: star import from {from}, so what this module exports cannot be determined without importing it",
                path.display()
            ));
        }
        let mut cursor = statement.walk();
        for imported in statement.children_by_field_name("name", &mut cursor) {
            let (original, local) = match imported.kind() {
                "aliased_import" => (
                    imported.child_by_field_name("name").map(|n| text(n, source)).unwrap_or_default(),
                    imported.child_by_field_name("alias").map(|n| text(n, source)).unwrap_or_default(),
                ),
                _ => (text(imported, source), text(imported, source)),
            };
            self.imports.insert(local.to_string(), (from.clone(), original.to_string()));
        }
        Ok(())
    }

    fn absorb_assignment(&mut self, expression: Node, source: &str, path: &Path) -> Result<(), String> {
        let mut assignment = Some(expression);
        while let Some(node) = assignment.filter(|node| node.kind() == "assignment") {
            let value = node.child_by_field_name("right");
            if let (Some(left), Some(value)) = (node.child_by_field_name("left"), value) {
                if left.kind() == "identifier" {
                    let target = text(left, source);
                    if target == ALL {
                        self.exports = Some(read_all(value, source, path)?);
                    } else {
                        self.defines.insert(target.to_string(), binding(value, source));
                    }
                }
            }
            assignment = value;
        }
        Ok(())
    }
}
