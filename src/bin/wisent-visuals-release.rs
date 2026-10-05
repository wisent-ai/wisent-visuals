//! `wisent-visuals-release surface | baseline`: see `wisent_visuals::release`.
//! Run from the repository checkout, which both commands read by default.

use std::process::ExitCode;

use wisent_visuals::release::{run, Outcome, USAGE};

fn main() -> ExitCode {
    let arguments: Vec<String> = std::env::args().skip(1).collect();
    let repository = std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    match run(&arguments, &repository) {
        Outcome::Done => ExitCode::SUCCESS,
        Outcome::Refused(refusal) => {
            eprintln!("{refusal}");
            ExitCode::FAILURE
        }
        Outcome::Usage => {
            eprintln!("{USAGE}");
            ExitCode::from(2)
        }
    }
}
