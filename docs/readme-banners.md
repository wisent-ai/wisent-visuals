# README banners

The banner bot renders a repository header from a small TOML file and keeps
every repository of the organization in step with it.

Keep banner content in a small TOML file:

```toml
title = "Deep control. Safer output."
description = "A Python package for latent space monitoring and guardrails."
product = "Wisent"
url = "wisent.com"
theme = "dark"
layout = "latent-field-left"
width = 1584
height = 396
```

Generate the committed README image and its editable, self-contained SVG source:

```bash
wisent-banner \
  --config .github/banner.toml \
  --output assets/readme-banner.webp \
  --svg assets/readme-banner.svg
```

The renderer bundles Hubot Sans, validates dimensions and supported layouts, and
produces byte-identical output for the same configuration. Commit both the TOML
configuration and generated assets; CI can rerun this command and use
`git diff --exit-code` to detect stale output.

### Automatic organization-wide presentation

`wisent-banner-bot` never writes product copy from repository metadata. Approved
titles and optional descriptions live in
`wisent_plots/identity/approved_copy.json`, with the conversation session and timestamp
that authorized each entry.

Repository descriptions, topics, languages, and README text select artwork only:

- routing graphs for gateways and model routers;
- measured bars for benchmarks and visualization;
- orbits for agent systems;
- waveforms for audio projects;
- stacked layers for storage and context;
- latent activation fields for models and safety;
- coordinated signals for SDKs, clients, and general developer tools.

A repository without approved copy receives only its display name and no
description. The generated TOML records `copy_status` and `approved_in`; changing
the approval register changes the source fingerprint and regenerates the assets.

Descriptions previously introduced by the removed copy table are listed in
`wisent_plots/identity/unapproved_descriptions.json`. Clear only those audited values
with:

```bash
wisent-banner-bot clear-unapproved-descriptions --org wisent-ai
```

Synchronize every repository description with the same approved registry:

```bash
wisent-banner-bot sync-approved-descriptions --org wisent-ai
```

Preview decisions without changing GitHub:

```bash
wisent-banner-bot plan --org wisent-ai --limit 10
```

The 15-minute `banner-bot.yml` workflow uses an organization-installed GitHub App
to create pull requests. Configure these repository secrets:

- `WISENT_BANNER_APP_ID`;
- `WISENT_BANNER_APP_PRIVATE_KEY`.

The app needs repository metadata read access plus Contents and Pull requests
read/write access. The bot skips forks and archived repositories and never
replaces an existing manually managed banner. Bot-owned README markup is the
first rendered block and is bounded by `wisent-banner:start` /
`wisent-banner:end` comments, so later runs replace only their own block. A source
fingerprint prevents unchanged repositories from receiving another pull request.

Every repository the bot writes to also receives `.tama/violations-ignore`
naming `assets/readme-banner.svg`. The vector banner is a rendered artifact of
`.github/banner.toml`, so a repository audit should read it as generated output
rather than ask somebody to split an 800-line file the next run overwrites.
Existing declarations are appended to, never replaced, and a repository that
already names the banner is left alone.

