//! `wisent-banner` run as a user runs it: a TOML file in, banner files out.

use std::fs;
use std::path::{Path, PathBuf};
use std::process::{Command, Output};

fn workspace(name: &str) -> PathBuf {
    let dir = Path::new(env!("CARGO_TARGET_TMPDIR"))
        .join("banner")
        .join(name);
    let _ = fs::remove_dir_all(&dir);
    fs::create_dir_all(&dir).expect("test workspace");
    dir
}

fn render(dir: &Path, config: &str, outputs: &[&str]) -> Output {
    let path = dir.join("banner.toml");
    fs::write(&path, config).expect("config written");
    let mut command = Command::new(env!("CARGO_BIN_EXE_wisent-banner"));
    command
        .arg("--config")
        .arg(&path)
        .arg("--output")
        .arg(dir.join(outputs[0]));
    if let Some(svg) = outputs.get(1) {
        command.arg("--svg").arg(dir.join(svg));
    }
    command.output().expect("wisent-banner runs")
}

fn stderr(output: &Output) -> String {
    String::from_utf8_lossy(&output.stderr).into_owned()
}

const MANAGED: &str = r#"
[automation]
managed = true
source_fingerprint = "0123456789abcdef"

[banner]
title = "Brama: Keep All Your Models Accessible Through One Endpoint"
description = "One gateway in front of every provider."
layout = "routes-left"
art_seed = "brama"
"#;

#[test]
fn every_layout_renders_svg_and_lossless_webp() {
    for layout in [
        "benchmark-left",
        "flock-left",
        "focus-left",
        "forest-left",
        "fracture-left",
        "gate-left",
        "gauge-left",
        "latent-field-left",
        "layers-left",
        "orbit-left",
        "routes-left",
        "scan-left",
        "signal-left",
        "spark-left",
        "timeline-left",
        "vault-left",
        "waveform-left",
    ] {
        let dir = workspace(layout);
        let output = render(
            &dir,
            &format!("title = \"Wisent\"\nlayout = \"{layout}\"\n"),
            &["banner.webp", "banner.svg"],
        );
        assert!(output.status.success(), "{layout}: {}", stderr(&output));
        let webp = image::open(dir.join("banner.webp")).expect("a decodable WebP");
        assert_eq!((webp.width(), webp.height()), (1584, 396), "{layout}");
        let svg = fs::read_to_string(dir.join("banner.svg")).expect("svg written");
        assert!(
            svg.contains("<circle"),
            "{layout}: the SVG holds no artwork"
        );
        assert!(svg.contains("Wisent"), "{layout}: the SVG lacks the title");
    }
}

#[test]
fn the_same_configuration_renders_the_same_bytes() {
    let first = workspace("repeat-first");
    let second = workspace("repeat-second");
    for dir in [&first, &second] {
        let output = render(dir, MANAGED, &["banner.webp", "banner.svg"]);
        assert!(output.status.success(), "{}", stderr(&output));
    }
    for file in ["banner.webp", "banner.svg"] {
        assert_eq!(
            fs::read(first.join(file)).unwrap(),
            fs::read(second.join(file)).unwrap(),
            "{file} differs between two runs of one configuration"
        );
    }
}

#[test]
fn another_seed_draws_other_artwork() {
    let brama = workspace("seed-brama");
    let other = workspace("seed-other");
    assert!(render(&brama, MANAGED, &["banner.png"]).status.success());
    let changed = MANAGED.replace("art_seed = \"brama\"", "art_seed = \"skarbiec\"");
    assert!(render(&other, &changed, &["banner.png"]).status.success());
    assert_ne!(
        fs::read(brama.join("banner.png")).unwrap(),
        fs::read(other.join("banner.png")).unwrap()
    );
}

#[test]
fn any_positive_size_scales_the_design() {
    let dir = workspace("size");
    let output = render(
        &dir,
        "title = \"Wisent\"\nwidth = 400\nheight = 100\n",
        &["banner.png"],
    );
    assert!(output.status.success(), "{}", stderr(&output));
    let png = image::open(dir.join("banner.png")).expect("a decodable PNG");
    assert_eq!((png.width(), png.height()), (400, 100));
}

#[test]
fn refusals_name_what_is_wrong_and_write_nothing() {
    let cases = [
        (
            "unknown-layout",
            "title = \"Wisent\"\nlayout = \"spiral\"\n",
            "layout must be one of",
        ),
        ("empty-title", "title = \"  \"\n", "title must not be empty"),
        (
            "unknown-setting",
            "title = \"Wisent\"\nquality = 90\n",
            "quality",
        ),
        (
            "zero-size",
            "title = \"Wisent\"\nheight = 0\n",
            "width and height must be positive",
        ),
        (
            "unknown-section",
            "[banner]\ntitle = \"Wisent\"\n[extra]\n",
            "unknown banner section(s): extra",
        ),
    ];
    for (name, config, expected) in cases {
        let dir = workspace(name);
        let output = render(&dir, config, &["banner.webp"]);
        assert_eq!(output.status.code(), Some(1), "{name}");
        assert!(
            stderr(&output).contains(expected),
            "{name}: {}",
            stderr(&output)
        );
        assert!(
            !dir.join("banner.webp").exists(),
            "{name}: a refused banner was written"
        );
    }
}

#[test]
fn a_description_longer_than_three_lines_is_refused_not_cut() {
    let dir = workspace("long-description");
    let description = "A description that keeps going ".repeat(12);
    let output = render(
        &dir,
        &format!("title = \"Wisent\"\ndescription = \"{description}\"\n"),
        &["banner.webp"],
    );
    assert_eq!(output.status.code(), Some(1));
    assert!(
        stderr(&output).contains("description"),
        "{}",
        stderr(&output)
    );
    assert!(!dir.join("banner.webp").exists());
}

#[test]
fn an_unknown_output_suffix_is_refused() {
    let dir = workspace("suffix");
    let output = render(&dir, "title = \"Wisent\"\n", &["banner.gif"]);
    assert_eq!(output.status.code(), Some(1));
    assert!(stderr(&output).contains("output must use .svg, .webp, or .png"));
}
