#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

SKILLS=(
  compete-cron-builder
  execution-cron-builder
  learn-cron-builder
  optimization-cron-builder
  looper-cron-builder
)

DEPRECATED_SKILLS=(
  debate-cron-builder
  debating-cron-builder
  research-cron-builder
  migration-cron-builder
)

usage() {
  cat <<'USAGE'
Usage: scripts/install_skills.sh [--target codex|claude|cursor|grok|opencode|openclaw|hermes|both|all|grokbot] [--scope user|project] [--project-dir PATH] [--link] [--dry-run]

Installs b3ehive's five portable SKILL.md directories for Codex, Claude Code, Cursor, Grok Build, opencode, OpenClaw, Hermes, or all supported targets.

--target grokbot installs the grokbot-only set the way grokbot does:
`unzip grokbot/grokbot-<skill>-skill.zip -d ~/.claude/skills/`. Only grokbot
loads those skills; their subagents run only as
`claude --dangerously-skip-permissions`. `all` never includes grokbot.

--link symlinks each skill to this checkout so updates arrive with `git pull`.
Copies carry a .b3ehive-version stamp that `bin/b3ehive doctor` checks.

Defaults:
  --target all
  --scope user
  --project-dir .

Install roots:
  Codex user:        ~/.codex/skills
  Claude Code user:  ~/.claude/skills
  Cursor user:       ~/.cursor/skills
  Grok Build user:   ~/.grok/skills
  opencode user:     ~/.config/opencode/skills
  OpenClaw user:      ~/.openclaw/skills
  Hermes user:        ~/.hermes/skills
  Codex project:     <project-dir>/.codex/skills
  Claude project:    <project-dir>/.claude/skills
  Cursor project:    <project-dir>/.cursor/skills
  Grok project:      <project-dir>/.grok/skills
  opencode project:  <project-dir>/.opencode/skills
  OpenClaw project:   <project-dir>/skills
  Hermes project:     <project-dir>/skills
  grokbot user:       ~/.claude/skills (grokbot-* names only)
  grokbot project:    <project-dir>/.claude/skills (grokbot-* names only)
USAGE
}

target="all"
scope="user"
project_dir="."
dry_run=0
link=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --target)
      target="${2:?missing value for --target}"
      shift 2
      ;;
    --scope)
      scope="${2:?missing value for --scope}"
      shift 2
      ;;
    --project-dir)
      project_dir="${2:?missing value for --project-dir}"
      shift 2
      ;;
    --dry-run)
      dry_run=1
      shift
      ;;
    --link)
      link=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

case "$target" in
  codex|claude|cursor|grok|opencode|openclaw|hermes|both|all|grokbot) ;;
  *)
    echo "--target must be codex, claude, cursor, grok, opencode, openclaw, hermes, both, all, or grokbot" >&2
    exit 2
    ;;
esac

case "$scope" in
  user|project) ;;
  *)
    echo "--scope must be user or project" >&2
    exit 2
    ;;
esac

VERSION="$(cat "${ROOT_DIR}/VERSION")"

skill_digest() {
  (cd "$1" && find . -type f ! -name .b3ehive-version ! -name .DS_Store -print0 | LC_ALL=C sort -z \
    | xargs -0 shasum -a 256 | shasum -a 256 | cut -c1-16)
}

stamp_skill() {
  local skill="$1" dst="$2"
  printf 'version=%s\nskill=%s\ndigest=%s\n' "$VERSION" "$skill" "$(skill_digest "${ROOT_DIR}/${skill}")" \
    > "${dst}/.b3ehive-version"
}

install_root() {
  local platform="$1"
  if [[ "$scope" == "user" ]]; then
    case "$platform" in
      codex) printf '%s\n' "${HOME}/.codex/skills" ;;
      claude|grokbot) printf '%s\n' "${HOME}/.claude/skills" ;;
      cursor) printf '%s\n' "${HOME}/.cursor/skills" ;;
      grok) printf '%s\n' "${GROK_SKILLS_HOME:-${HOME}/.grok/skills}" ;;
      opencode) printf '%s\n' "${XDG_CONFIG_HOME:-${HOME}/.config}/opencode/skills" ;;
      openclaw) printf '%s\n' "${OPENCLAW_SKILLS_HOME:-${HOME}/.openclaw/skills}" ;;
      hermes) printf '%s\n' "${HERMES_SKILLS_HOME:-${HOME}/.hermes/skills}" ;;
    esac
  else
    case "$platform" in
      codex) printf '%s\n' "${project_dir}/.codex/skills" ;;
      claude|grokbot) printf '%s\n' "${project_dir}/.claude/skills" ;;
      cursor) printf '%s\n' "${project_dir}/.cursor/skills" ;;
      grok) printf '%s\n' "${project_dir}/.grok/skills" ;;
      opencode) printf '%s\n' "${project_dir}/.opencode/skills" ;;
      openclaw) printf '%s\n' "${project_dir}/skills" ;;
      hermes) printf '%s\n' "${project_dir}/skills" ;;
    esac
  fi
}

install_grokbot() {
  local root
  root="$(install_root grokbot)"
  if [[ "$dry_run" -eq 0 ]]; then
    command -v unzip >/dev/null || { echo "Missing dependency: unzip" >&2; exit 2; }
    mkdir -p "$root"
  fi
  for skill in "${SKILLS[@]}"; do
    local name="grokbot-${skill}"
    local zip="${ROOT_DIR}/grokbot/${name}-skill.zip" dst="${root}/${name}"
    if [[ ! -f "$zip" ]]; then
      echo "Missing grokbot package: ${zip}; run scripts/build_grokbot.py" >&2
      exit 1
    fi
    if [[ "$dry_run" -eq 1 ]]; then
      echo "[dry-run] unzip ${zip} -d ${root}/ (link=${link})"
    elif [[ "$link" -eq 1 ]]; then
      rm -rf "$dst"
      ln -s "${ROOT_DIR}/grokbot/skills/${name}" "$dst"
      echo "Linked grokbot: ${dst} -> ${ROOT_DIR}/grokbot/skills/${name}"
    else
      rm -rf "$dst"
      unzip -q "$zip" -d "${root}/"
      echo "Installed grokbot: ${dst} (${VERSION})"
    fi
  done
}

install_for_platform() {
  local platform="$1"
  local root
  root="$(install_root "$platform")"

  if [[ "$dry_run" -eq 1 ]]; then
    echo "[dry-run] mkdir -p ${root}"
  else
    mkdir -p "$root"
  fi

  for skill in "${DEPRECATED_SKILLS[@]}"; do
    local dst="${root}/${skill}"
    if [[ "$dry_run" -eq 1 ]]; then
      echo "[dry-run] remove deprecated ${dst}"
    else
      rm -rf "$dst"
      echo "Removed deprecated ${platform}: ${dst}"
    fi
  done

  for skill in "${SKILLS[@]}"; do
    local src="${ROOT_DIR}/${skill}"
    local dst="${root}/${skill}"
    if [[ ! -f "${src}/SKILL.md" ]]; then
      echo "Missing skill source: ${src}/SKILL.md" >&2
      exit 1
    fi
    if [[ "$dry_run" -eq 1 ]]; then
      echo "[dry-run] install ${src} -> ${dst} (link=${link})"
    elif [[ "$link" -eq 1 ]]; then
      rm -rf "$dst"
      ln -s "$src" "$dst"
      echo "Linked ${platform}: ${dst} -> ${src}"
    else
      rm -rf "$dst"
      cp -a "$src" "$dst"
      stamp_skill "$skill" "$dst"
      echo "Installed ${platform}: ${dst} (${VERSION})"
    fi
  done
}

platforms=()
case "$target" in
  codex) platforms=(codex) ;;
  claude) platforms=(claude) ;;
  cursor) platforms=(cursor) ;;
  grok) platforms=(grok) ;;
  opencode) platforms=(opencode) ;;
  openclaw) platforms=(openclaw) ;;
  hermes) platforms=(hermes) ;;
  both) platforms=(codex claude) ;;
  all) platforms=(codex claude cursor grok opencode openclaw hermes) ;;
  grokbot) install_grokbot; exit 0 ;;
esac

installed_roots=":"
for platform in "${platforms[@]}"; do
  root="$(install_root "$platform")"
  case "$installed_roots" in
    *":${root}:"*)
      echo "Skipping ${platform}: install root already handled (${root})"
      ;;
    *)
      install_for_platform "$platform"
      installed_roots="${installed_roots}${root}:"
      ;;
  esac
done
