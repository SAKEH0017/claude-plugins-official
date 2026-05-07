# submit-skills

A Claude Code skill plugin that streamlines the process of packaging and submitting custom skills to the official plugin marketplace.

## Purpose

Automates the three-stage submission workflow for Claude Code skills:

- **Package**: Converts standalone skills into standard plugin format with proper directory structure
- **Host**: Guides GitHub hosting via fork of the official marketplace repository
- **Submit**: Generates all form field content for the official submission page

## Core Capabilities

1. **Name Compliance Check** — Detects and flags sensitive words (evade, bypass, detect, cheat, etc.) that would cause rejection, and suggests compliant alternatives
2. **Plugin Structure Generation** — Creates `.claude-plugin/plugin.json`, skills directory tree, README, and LICENSE automatically
3. **Chinese-to-English Translation** — Translates Chinese SKILL.md content to English for marketplace review compatibility
4. **GitHub Automation** — Handles fork creation, file placement, commit, and push via `gh` CLI
5. **Form Field Preparation** — Generates description, use cases, and privacy policy URL tailored to the specific skill

## Installation

```bash
# From the official marketplace (after approval)
/plugin install submit-skills@claude-plugins-official

# Manual install: copy skills/submit-skills/SKILL.md to ~/.claude/skills/
```

## Usage

Tell Claude you want to submit a skill:

> "Submit my xxx skill to the marketplace"

The skill triggers automatically and walks through the entire process — packaging, GitHub hosting, and form preparation.

## Privacy

This plugin does not collect, store, or transmit any user data. It operates entirely within Claude Code as a skill definition file (SKILL.md) that provides submission workflow instructions. No network requests, no analytics, no tracking.

## License

MIT License
