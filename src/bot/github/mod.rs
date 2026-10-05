//! GitHub repository reads and explicit banner publication operations.
//!
//! A failed request ends the run with GitHub's own status and body. Nothing is
//! retried here: the workflow runs again on its schedule, and a run that stops on
//! a 5xx leaves every repository either untouched or carrying a partial branch the
//! next run completes, because each write first compares what is already there.

mod content;

use std::io::Read;

use percent_encoding::{utf8_percent_encode, AsciiSet, NON_ALPHANUMERIC};
use serde_json::Value;

pub use content::Content;

const API_URL: &str = "https://api.github.com";
const API_VERSION: &str = "2022-11-28";

/// RFC 3986 unreserved characters stay literal; everything else is escaped.
const COMPONENT: &AsciiSet = &NON_ALPHANUMERIC
    .remove(b'-')
    .remove(b'.')
    .remove(b'_')
    .remove(b'~');
/// A repository path keeps its separators.
const PATH: &AsciiSet = &COMPONENT.remove(b'/');

pub fn component(value: &str) -> String {
    utf8_percent_encode(value, COMPONENT).to_string()
}

fn path_component(value: &str) -> String {
    utf8_percent_encode(value, PATH).to_string()
}

pub struct GitHubClient {
    agent: ureq::Agent,
    token: String,
}

impl GitHubClient {
    pub fn new(token: String) -> Self {
        Self {
            agent: ureq::AgentBuilder::new().build(),
            token,
        }
    }

    /// Send one request. `Ok(None)` is an empty body, or a 404 when `allow_missing`;
    /// otherwise the JSON answer and its `rel="next"` page, if any.
    fn send(
        &self,
        method: &str,
        url: &str,
        payload: Option<&Value>,
        allow_missing: bool,
    ) -> Result<Option<(Value, Option<String>)>, String> {
        let mut request = self
            .agent
            .request(method, url)
            .set("Accept", "application/vnd.github+json")
            .set(
                "User-Agent",
                concat!("wisent-banner-bot/", env!("CARGO_PKG_VERSION")),
            )
            .set("X-GitHub-Api-Version", API_VERSION);
        if !self.token.is_empty() {
            request = request.set("Authorization", &format!("Bearer {}", self.token));
        }
        let shown = url.strip_prefix(API_URL).unwrap_or(url);
        let outcome = match payload {
            Some(body) => request
                .set("Content-Type", "application/json")
                .send_string(&body.to_string()),
            None => request.call(),
        };
        let response = match outcome {
            Ok(response) => response,
            Err(ureq::Error::Status(404, _)) if allow_missing => return Ok(None),
            Err(ureq::Error::Status(code, response)) => {
                let detail = response.into_string().unwrap_or_default();
                return Err(format!("GitHub {method} {shown} failed ({code}): {detail}"));
            }
            Err(ureq::Error::Transport(error)) => {
                return Err(format!("GitHub {method} {shown} did not complete: {error}"));
            }
        };
        let next = response.header("link").and_then(next_page);
        let mut body = Vec::new();
        response
            .into_reader()
            .read_to_end(&mut body)
            .map_err(|e| format!("GitHub {method} {shown}: reading the answer failed: {e}"))?;
        if body.is_empty() {
            return Ok(None);
        }
        let value = serde_json::from_slice(&body)
            .map_err(|e| format!("GitHub {method} {shown} answered non-JSON: {e}"))?;
        Ok(Some((value, next)))
    }

    fn request(
        &self,
        method: &str,
        path: &str,
        payload: Option<&Value>,
        allow_missing: bool,
    ) -> Result<Option<Value>, String> {
        Ok(self
            .send(method, &format!("{API_URL}{path}"), payload, allow_missing)?
            .map(|(value, _)| value))
    }

    fn expect(&self, method: &str, path: &str, payload: Option<&Value>) -> Result<Value, String> {
        self.request(method, path, payload, false)?
            .ok_or_else(|| format!("GitHub {method} {path} answered an empty body"))
    }

    /// Every repository of the organization, newest first, following GitHub's
    /// own `Link: rel="next"` pages until it names none.
    pub fn list_repositories(&self, organization: &str) -> Result<Vec<Value>, String> {
        let mut url = Some(format!(
            "{API_URL}/orgs/{}/repos?type=all&sort=created&direction=desc",
            component(organization)
        ));
        let mut repositories = Vec::new();
        while let Some(current) = url.take() {
            let Some((page, next)) = self.send("GET", &current, None, false)? else {
                break;
            };
            match page {
                Value::Array(items) => repositories.extend(items),
                other => return Err(format!("GitHub listed repositories as {other}")),
            }
            url = next;
        }
        Ok(repositories)
    }
}

fn text<'a>(value: &'a Value, field: &str) -> Result<&'a str, String> {
    value
        .get(field)
        .and_then(Value::as_str)
        .ok_or_else(|| format!("GitHub answer has no {field}"))
}

/// The `rel="next"` target of an RFC 8288 `Link` header.
fn next_page(link: &str) -> Option<String> {
    link.split(',').find_map(|entry| {
        let (target, params) = entry.split_once(';')?;
        params
            .split(';')
            .any(|param| param.trim() == "rel=\"next\"")
            .then(|| {
                target
                    .trim()
                    .trim_start_matches('<')
                    .trim_end_matches('>')
                    .to_owned()
            })
    })
}
