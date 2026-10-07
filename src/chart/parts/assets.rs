//! The fill patterns the chart designs use, embedded in the binary from
//! `assets/` and copied into a chart's `<defs>` as `<pattern>` elements.

use roxmltree::{Document, Node};

use super::element::Element;

/// A shipped pattern artwork.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Pattern {
    CheckMesh,
    CrossingLines,
    DiagonalLines,
    VerticalLines,
    NoiseLarge,
    DitherLarge,
}

impl Pattern {
    fn source(self) -> (&'static str, &'static str) {
        match self {
            Self::CheckMesh => (
                "check_mesh.svg",
                include_str!("../../../assets/patterns/check_mesh.svg"),
            ),
            Self::CrossingLines => (
                "crossing_lines.svg",
                include_str!("../../../assets/patterns/crossing_lines.svg"),
            ),
            Self::DiagonalLines => (
                "diagonal_lines.svg",
                include_str!("../../../assets/patterns/diagonal_lines.svg"),
            ),
            Self::VerticalLines => (
                "vertical_lines.svg",
                include_str!("../../../assets/patterns/vertical_lines.svg"),
            ),
            Self::NoiseLarge => (
                "noise_rectangle_large.svg",
                include_str!("../../../assets/large/noise_rectangle_large.svg"),
            ),
            Self::DitherLarge => (
                "dither_cross_large.svg",
                include_str!("../../../assets/large/dither_cross_large.svg"),
            ),
        }
    }
}

/// Copy `node` and its subtree, namespaces dropped, under `parent`.
fn copy(node: Node, parent: &mut Element) {
    let mut element = Element::new(node.tag_name().name());
    for attribute in node.attributes() {
        element.set(attribute.name(), attribute.value());
    }
    if let Some(text) = node
        .children()
        .find(Node::is_text)
        .and_then(|text| text.text())
    {
        element = element.text(text);
    }
    let copied = parent.child(element);
    for child in node.children().filter(Node::is_element) {
        copy(child, copied);
    }
}

/// Add `pattern` to `defs` as `<pattern id=…>` sized by its artwork's
/// viewBox (else its width and height), in user-space units.
pub fn load_pattern(defs: &mut Element, id: &str, pattern: Pattern) -> Result<(), String> {
    let (file, source) = pattern.source();
    let document =
        Document::parse(source).map_err(|error| format!("assets {file} is not SVG: {error}"))?;
    let root = document.root_element();
    let view_box: Vec<&str> = root
        .attribute("viewBox")
        .map(|value| value.split_whitespace().collect())
        .unwrap_or_default();
    let (width, height) = match view_box.as_slice() {
        [_, _, width, height] => (*width, *height),
        _ => (
            root.attribute("width")
                .ok_or_else(|| format!("assets {file} declares no width"))?,
            root.attribute("height")
                .ok_or_else(|| format!("assets {file} declares no height"))?,
        ),
    };
    let element = defs.child(
        Element::new("pattern")
            .attr("id", id)
            .attr("patternUnits", "userSpaceOnUse")
            .attr("width", width)
            .attr("height", height),
    );
    for child in root.children().filter(Node::is_element) {
        if matches!(child.tag_name().name(), "title" | "desc" | "metadata") {
            continue;
        }
        copy(child, element);
    }
    Ok(())
}

/// The patterns the bar and column designs fill their segments with:
/// style 2 noise, style 3 crossing lines, style 4 noise and dither crosses.
pub fn cartesian_patterns(svg: &mut Element, style: u32) -> Result<(), String> {
    let defs = svg.find_or_insert("defs");
    match style {
        2 => load_pattern(defs, "pattern-noise", Pattern::NoiseLarge),
        3 => load_pattern(defs, "pattern-crossing", Pattern::CrossingLines),
        4 => {
            load_pattern(defs, "pattern-noise", Pattern::NoiseLarge)?;
            load_pattern(defs, "pattern-dither", Pattern::DitherLarge)
        }
        _ => Ok(()),
    }
}
