//! A small SVG element tree: the Rust counterpart of building a chart with
//! `xml.etree.ElementTree.SubElement`, serialised with escaped text and
//! attributes.

use std::fmt::{Display, Write};

/// One SVG element, its attributes in insertion order, its text and children.
#[derive(Clone, Debug, Default)]
pub struct Element {
    name: String,
    attributes: Vec<(String, String)>,
    text: Option<String>,
    children: Vec<Element>,
}

impl Element {
    pub fn new(name: &str) -> Self {
        Self {
            name: name.to_string(),
            ..Self::default()
        }
    }

    /// The element with `key` set to `value`, replacing an earlier value of `key`.
    pub fn attr(mut self, key: &str, value: impl Display) -> Self {
        self.set(key, value);
        self
    }

    pub fn set(&mut self, key: &str, value: impl Display) {
        let value = value.to_string();
        match self.attributes.iter_mut().find(|(name, _)| name == key) {
            Some(existing) => existing.1 = value,
            None => self.attributes.push((key.to_string(), value)),
        }
    }

    pub fn get(&self, key: &str) -> Option<&str> {
        self.attributes
            .iter()
            .find(|(name, _)| name == key)
            .map(|(_, value)| value.as_str())
    }

    pub fn name(&self) -> &str {
        &self.name
    }

    /// The element with its text content set.
    pub fn text(mut self, text: impl Display) -> Self {
        self.text = Some(text.to_string());
        self
    }

    /// Append `child` and return it for further building, like `ET.SubElement`.
    pub fn child(&mut self, child: Element) -> &mut Element {
        self.children.push(child);
        let last = self.children.len() - 1;
        &mut self.children[last]
    }

    /// The element with `child` appended.
    pub fn with(mut self, child: Element) -> Self {
        self.children.push(child);
        self
    }

    /// The first direct child named `name`, like `svg.find("defs")`.
    pub fn find_mut(&mut self, name: &str) -> Option<&mut Element> {
        self.children.iter_mut().find(|child| child.name == name)
    }

    /// The direct child named `name`, appended when there is none.
    pub fn find_or_insert(&mut self, name: &str) -> &mut Element {
        match self.children.iter().position(|child| child.name == name) {
            Some(index) => &mut self.children[index],
            None => self.child(Element::new(name)),
        }
    }

    /// The element serialised as XML.
    pub fn render(&self) -> String {
        let mut out = String::new();
        self.write(&mut out);
        out
    }

    fn write(&self, out: &mut String) {
        out.push('<');
        out.push_str(&self.name);
        for (key, value) in &self.attributes {
            let _ = write!(out, " {key}=\"{}\"", escape(value, true));
        }
        if self.text.is_none() && self.children.is_empty() {
            out.push_str(" />");
            return;
        }
        out.push('>');
        if let Some(text) = &self.text {
            out.push_str(&escape(text, false));
        }
        for child in &self.children {
            child.write(out);
        }
        let _ = write!(out, "</{}>", self.name);
    }
}

fn escape(raw: &str, attribute: bool) -> String {
    let mut out = String::with_capacity(raw.len());
    for character in raw.chars() {
        match character {
            '&' => out.push_str("&amp;"),
            '<' => out.push_str("&lt;"),
            '>' => out.push_str("&gt;"),
            '"' if attribute => out.push_str("&quot;"),
            '\n' if attribute => out.push_str("&#10;"),
            other => out.push(other),
        }
    }
    out
}

/// The root `<svg>` of a chart `width` by `height`, with the SVG namespace.
pub fn svg_root(width: f64, height: f64) -> Element {
    Element::new("svg")
        .attr("xmlns", "http://www.w3.org/2000/svg")
        .attr("width", width)
        .attr("height", height)
        .attr("viewBox", format!("0 0 {width} {height}"))
}

/// The font every chart's text asks for, loaded from Google Fonts by a viewer
/// and from the bundled files when the chart is rasterised.
const FONT_STYLE: &str = "\n            @import url('https://fonts.googleapis.com/css2?family=Hubot+Sans:wght@400&display=swap');\n            text { font-family: 'Hubot Sans', sans-serif; }\n        ";
/// The design's corner radius of a chart card.
const CARD_RADIUS: f64 = 20.0;

/// The root of a chart card: the SVG and XLink namespaces, the font style
/// and a rounded background of `background`.
pub fn chart_frame(width: f64, height: f64, background: &str) -> Element {
    svg_root(width, height)
        .attr("xmlns:xlink", "http://www.w3.org/1999/xlink")
        .with(Element::new("style").text(FONT_STYLE))
        .with(
            Element::new("rect")
                .attr("width", width)
                .attr("height", height)
                .attr("fill", background)
                .attr("rx", CARD_RADIUS)
                .attr("ry", CARD_RADIUS),
        )
}
