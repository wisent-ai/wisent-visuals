//! `wisent-banner`: render a deterministic Wisent README banner from a TOML configuration.

use std::path::PathBuf;
use std::process::ExitCode;

use clap::Parser;

use wisent_visuals::banner::{Banner, BannerConfig};

#[derive(Parser)]
#[command(
    name = "wisent-banner",
    version,
    about = "Generate a deterministic Wisent README banner."
)]
struct Args {
    /// TOML banner configuration: flat, or a `[banner]` table beside `[automation]`.
    #[arg(long)]
    config: PathBuf,
    /// Output path ending in .svg, .webp, or .png.
    #[arg(long)]
    output: PathBuf,
    /// An additional self-contained SVG source to write beside the output.
    #[arg(long)]
    svg: Option<PathBuf>,
}

fn run(args: &Args) -> Result<(), String> {
    let banner = Banner::new(BannerConfig::from_toml(&args.config)?)?;
    banner.save(&args.output)?;
    if let Some(svg) = &args.svg {
        banner.save(svg)?;
    }
    Ok(())
}

fn main() -> ExitCode {
    let args = Args::parse();
    match run(&args) {
        Ok(()) => ExitCode::SUCCESS,
        Err(error) => {
            eprintln!("wisent-banner: {error}");
            ExitCode::FAILURE
        }
    }
}
