# Codex Plugin

[中文](codex-plugin.zh-CN.md)

b3ehive is packaged as a Codex plugin in `plugins/b3ehive` and exposed through
the repository marketplace catalog at `.agents/plugins/marketplace.json`.

The plugin is the preferred Codex distribution path. It bundles the same five
portable `SKILL.md` directories that live at the repository root, but lets Codex
install and load them as one named package.

## What The Plugin Includes

The plugin exposes five Codex skills:

- `compete-cron-builder`
- `execution-cron-builder`
- `learn-cron-builder`
- `optimization-cron-builder`
- `looper-cron-builder`

Each skill keeps its own `SKILL.md`, `agents/`, `references/`, and optional
`scripts/` files under `plugins/b3ehive/skills/<skill>/`.

The root skill directories remain the source of truth. The plugin copy is a
release package generated from those root directories.

## When To Use It

Use the Codex plugin when the consumer is Codex and wants one package install
that loads all five b3ehive skills.

Use the portable skill installer when the consumer is Claude Code, opencode,
OpenClaw, Hermes, or a project-local `SKILL.md` layout:

```bash
scripts/install_skills.sh --target all --scope user
```

## Install From This Repository

```bash
codex plugin marketplace add .
codex plugin add b3ehive@b3ehive
```

## Install From GitHub

```bash
codex plugin marketplace add weiyangzen/b3ehive
codex plugin add b3ehive@b3ehive
```

Start a new Codex thread after installation so Codex can load the plugin skills.

## Usage

After installation, mention `b3ehive` or one bundled skill by name:

```text
Use b3ehive to create an execution blueprint.
Use compete-cron-builder to compare local proposals and synthesize a blueprint.
Use execution-cron-builder for this repo and this blueprint.
Use learn-cron-builder to learn this source scope into validated docs.
Use optimization-cron-builder with this design philosophy.
Use looper-cron-builder to add bounded ROI control around these bridge surfaces.
```

Codex loads plugin skills for new sessions. If a session was already open before
installation or update, start a fresh thread before testing discovery.

## Package Layout

```text
.agents/plugins/marketplace.json
plugins/b3ehive/
  README.md
  README.zh-CN.md
  .codex-plugin/plugin.json
  skills/
    compete-cron-builder/
    execution-cron-builder/
    learn-cron-builder/
    optimization-cron-builder/
    looper-cron-builder/
```

`.agents/plugins/marketplace.json` is the repository marketplace catalog. It
points the `b3ehive` marketplace entry at `./plugins/b3ehive`.

`plugins/b3ehive/.codex-plugin/plugin.json` is the plugin manifest. Keep its
version, description, URLs, capabilities, and skill path aligned with
`package.json` and the public README.

`plugins/b3ehive/skills/` contains the package copy of the five source skills.
Before a plugin release, sync the root skill directories into the Codex plugin
package:

```bash
scripts/sync_codex_plugin.sh
```

## Maintenance Workflow

1. Edit the root skill directory, for example
   `execution-cron-builder/SKILL.md`.
2. Run `scripts/sync_codex_plugin.sh`.
3. Review the generated diff under `plugins/b3ehive/skills/`.
4. Update `plugins/b3ehive/.codex-plugin/plugin.json`, `package.json`,
   `README.md`, `PRIVACY.md`, and `TERMS.md` when package metadata, user-facing
   behavior, policy, or legal surface changes.
5. Run validation before tagging or publishing.

Do not edit generated plugin skill copies as the primary source. Changes made
only under `plugins/b3ehive/skills/` can be overwritten by the next sync.

## Validation

Run these checks before release:

```bash
jq empty package.json .agents/plugins/marketplace.json plugins/b3ehive/.codex-plugin/plugin.json
scripts/validate_agent_platforms.sh
scripts/validate_learn_upgrade.sh
```

For plugin packaging changes, also inspect that the marketplace catalog points
at the package directory:

```bash
jq '.plugins[] | select(.name == "b3ehive").source.path' .agents/plugins/marketplace.json
```

## Current Public Directory Status

This repository marketplace is a public Git-backed distribution path. It is not
an OpenAI official Plugin Directory listing. OpenAI's self-serve public Plugin
Directory publishing flow should be used when that program is available.

## Release Checklist

- Run `scripts/sync_codex_plugin.sh`.
- Validate `plugins/b3ehive/.codex-plugin/plugin.json`.
- Verify `.agents/plugins/marketplace.json` points to `./plugins/b3ehive`.
- Start a fresh Codex thread and confirm the five bundled skills are discoverable.
- Keep `PRIVACY.md`, `TERMS.md`, `LICENSE`, and README install instructions
  current.
- Tag the repository release after plugin metadata and root package metadata
  agree on version.
