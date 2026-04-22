# CLAUDE-SKILLS

## Description

A collection of custom skills for [Claude Code] — Anthropic's CLI for Claude.

Skills extend Claude Code with reusable, domain-specific workflows triggered via `/skill-name` in the prompt. Each skill lives in its own subfolder and consists of a `SKILL.md` instruction file plus optional helper scripts that Claude calls during execution to minimise tool-call overhead.

## Skills

| Skill | Trigger | Description |
|-------|---------|-------------|
| [music-sort] | `/music-sort` | Organizes a local music folder: reads ID3/Vorbis tags via `mutagen` (auto-installed), parses filenames for missing metadata, sorts files into `Artist/` subfolders, detects duplicates, and generates an `undo.sh` rollback script. |

## Usage

Skills are picked up automatically by Claude Code from `~/.claude/skills/`. Invoke any skill by typing its name as a slash command:

## Installation

```sh
# Clone into your Claude skills directory
git clone https://github.com/deian-mishev/claude_skills.git ~/.claude/skills
```

## Requirements

* [CLAUDE_CODE] - Anthropic CLI for Claude
* [PYTHON] - Python 3.8+ (bundled on macOS 12+; system 3.11.4)

## Adding a Skill

1. Create a subfolder: `~/.claude/skills/<skill-name>/`
2. Add `SKILL.md` with frontmatter (`name`, `description`) and instructions for Claude
3. Optionally add helper scripts for batch operations to reduce tool-call overhead

[CLAUDE_CODE]: https://claude.ai/code
[PYTHON]: https://www.python.org/downloads/

[music-sort]: ./music-sort/SKILL.md
