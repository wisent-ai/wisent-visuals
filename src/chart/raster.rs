//! A chart's SVG written as is, or rasterised to PNG at its own size with the
//! bundled Hubot Sans, so a PNG does not depend on the fonts of the machine.

use std::fs;
use std::path::Path;
use std::sync::Arc;

use resvg::{tiny_skia, usvg};

use crate::brand::{BOLD_TTF, REGULAR_TTF};

/// `svg` rasterised to PNG bytes at the size the SVG declares.
pub fn png(svg: &str) -> Result<Vec<u8>, String> {
    let mut database = usvg::fontdb::Database::new();
    database.load_font_data(REGULAR_TTF.to_vec());
    database.load_font_data(BOLD_TTF.to_vec());
    let options = usvg::Options { fontdb: Arc::new(database), ..usvg::Options::default() };
    let tree = usvg::Tree::from_str(svg, &options).map_err(|error| format!("the chart SVG does not parse: {error}"))?;
    let size = tree.size().to_int_size();
    let mut pixmap = tiny_skia::Pixmap::new(size.width(), size.height())
        .ok_or_else(|| format!("the chart declares an empty size {}x{}", size.width(), size.height()))?;
    resvg::render(&tree, tiny_skia::Transform::identity(), &mut pixmap.as_mut());
    pixmap.encode_png().map_err(|error| format!("PNG encoding failed: {error}"))
}

/// Write `svg` to `path`, its format chosen by the `.svg` or `.png` suffix.
pub fn save(svg: &str, path: &Path) -> Result<(), String> {
    let shown = path.display();
    if let Some(parent) = path.parent().filter(|parent| !parent.as_os_str().is_empty()) {
        fs::create_dir_all(parent).map_err(|error| format!("{}: {error}", parent.display()))?;
    }
    match path.extension().and_then(|extension| extension.to_str()) {
        Some("svg") => fs::write(path, svg).map_err(|error| format!("{shown}: {error}")),
        Some("png") => fs::write(path, png(svg)?).map_err(|error| format!("{shown}: {error}")),
        _ => Err(format!("{shown}: output must use .svg or .png")),
    }
}
