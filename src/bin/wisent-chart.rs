//! `wisent-chart`: draw a Wisent brand chart from a JSON spec.

use std::path::PathBuf;
use std::process::ExitCode;

use clap::Parser;

use wisent_visuals::chart::ChartSpec;

#[derive(Parser)]
#[command(name = "wisent-chart", version, about = "Draw a Wisent brand chart from a JSON spec.")]
struct Args {
    /// JSON chart spec: `kind` (area, bar, bubble, column, line, pie or radar)
    /// and that family's fields. `-` reads it from standard input.
    #[arg(long)]
    spec: PathBuf,
    /// Output path ending in .svg or .png.
    #[arg(long)]
    output: PathBuf,
}

fn run(args: &Args) -> Result<(), String> {
    let origin = args.spec.display().to_string();
    let text = if origin == "-" {
        std::io::read_to_string(std::io::stdin()).map_err(|error| format!("standard input: {error}"))?
    } else {
        std::fs::read_to_string(&args.spec).map_err(|error| format!("{origin}: {error}"))?
    };
    ChartSpec::from_json(&text, &origin)?.save(&args.output)
}

fn main() -> ExitCode {
    let args = Args::parse();
    match run(&args) {
        Ok(()) => ExitCode::SUCCESS,
        Err(error) => {
            eprintln!("wisent-chart: {error}");
            ExitCode::FAILURE
        }
    }
}
