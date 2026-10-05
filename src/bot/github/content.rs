//! Reads and writes of repository files, branches, descriptions and pull requests.

use base64::{engine::general_purpose::STANDARD, Engine as _};
use serde_json::{json, Value};

use super::{component, path_component, text, GitHubClient};

/// One file read from a branch: its bytes and the blob sha GitHub needs to replace it.
pub struct Content {
    pub bytes: Vec<u8>,
    pub sha: String,
}

impl GitHubClient {
    /// One file on `reference`, or `None` when the branch has no such file.
    /// A file GitHub's contents answer omits (`encoding: none`, past its inline
    /// size) is read whole from the git blob it names.
    pub fn read_content(
        &self,
        owner: &str,
        repository: &str,
        path: &str,
        reference: &str,
    ) -> Result<Option<Content>, String> {
        let Some(result) = self.request(
            "GET",
            &format!(
                "/repos/{owner}/{repository}/contents/{}?ref={}",
                path_component(path),
                component(reference)
            ),
            None,
            true,
        )?
        else {
            return Ok(None);
        };
        let sha = text(&result, "sha")?.to_owned();
        let encoded = if result.get("encoding").and_then(Value::as_str) == Some("none") {
            let blob = self.expect(
                "GET",
                &format!("/repos/{owner}/{repository}/git/blobs/{sha}"),
                None,
            )?;
            text(&blob, "content")?.to_owned()
        } else {
            text(&result, "content")?.to_owned()
        };
        let compact: String = encoded.split_whitespace().collect();
        let bytes = STANDARD
            .decode(compact)
            .map_err(|e| format!("{owner}/{repository}:{path} is not base64 content: {e}"))?;
        Ok(Some(Content { bytes, sha }))
    }

    pub fn ensure_branch(
        &self,
        owner: &str,
        repository: &str,
        default_branch: &str,
        branch: &str,
    ) -> Result<(), String> {
        let existing = self.request(
            "GET",
            &format!(
                "/repos/{owner}/{repository}/git/ref/heads/{}",
                component(branch)
            ),
            None,
            true,
        )?;
        if existing.is_some() {
            return Ok(());
        }
        let source = self.expect(
            "GET",
            &format!(
                "/repos/{owner}/{repository}/git/ref/heads/{}",
                component(default_branch)
            ),
            None,
        )?;
        let sha = source
            .pointer("/object/sha")
            .and_then(Value::as_str)
            .ok_or_else(|| format!("{owner}/{repository}: {default_branch} names no commit"))?;
        self.expect(
            "POST",
            &format!("/repos/{owner}/{repository}/git/refs"),
            Some(&json!({"ref": format!("refs/heads/{branch}"), "sha": sha})),
        )?;
        Ok(())
    }

    /// Set the repository description to `description`; `false` when it already was.
    pub fn set_description(
        &self,
        owner: &str,
        repository: &str,
        description: &str,
    ) -> Result<bool, String> {
        let path = format!("/repos/{owner}/{repository}");
        let Some(current) = self.request("GET", &path, None, true)? else {
            return Ok(false);
        };
        let present = current
            .get("description")
            .and_then(Value::as_str)
            .unwrap_or("");
        if present == description {
            return Ok(false);
        }
        self.expect("PATCH", &path, Some(&json!({ "description": description })))?;
        Ok(true)
    }

    /// Create or replace one file; `current_sha` names the blob being replaced.
    pub fn write_content(
        &self,
        owner: &str,
        repository: &str,
        path: &str,
        branch: Option<&str>,
        content: &[u8],
        message: &str,
        current_sha: Option<&str>,
    ) -> Result<(), String> {
        let mut payload = json!({
            "message": message,
            "content": STANDARD.encode(content),
        });
        if let Some(branch) = branch {
            payload["branch"] = Value::from(branch);
        }
        if let Some(sha) = current_sha {
            payload["sha"] = Value::from(sha);
        }
        self.expect(
            "PUT",
            &format!(
                "/repos/{owner}/{repository}/contents/{}",
                path_component(path)
            ),
            Some(&payload),
        )?;
        Ok(())
    }

    pub fn delete_content(
        &self,
        owner: &str,
        repository: &str,
        path: &str,
        branch: &str,
        message: &str,
        current_sha: &str,
    ) -> Result<(), String> {
        self.expect(
            "DELETE",
            &format!(
                "/repos/{owner}/{repository}/contents/{}",
                path_component(path)
            ),
            Some(&json!({"message": message, "sha": current_sha, "branch": branch})),
        )?;
        Ok(())
    }

    /// The pull request already open from `branch`, or a new one with `body`.
    pub fn open_pull_request(
        &self,
        owner: &str,
        repository: &str,
        branch: &str,
        default_branch: &str,
        body: &str,
    ) -> Result<String, String> {
        let existing = self.expect(
            "GET",
            &format!(
                "/repos/{owner}/{repository}/pulls?state=open&head={}&base={}",
                component(&format!("{owner}:{branch}")),
                component(default_branch)
            ),
            None,
        )?;
        if let Some(url) = existing
            .as_array()
            .and_then(|pulls| pulls.first())
            .and_then(|pull| pull.get("html_url"))
            .and_then(Value::as_str)
        {
            return Ok(url.to_owned());
        }
        let created = self.expect(
            "POST",
            &format!("/repos/{owner}/{repository}/pulls"),
            Some(&json!({
                "title": "Add personalized Wisent README banner and buttons",
                "head": branch,
                "base": default_branch,
                "body": body,
            })),
        )?;
        Ok(text(&created, "html_url")?.to_owned())
    }
}
