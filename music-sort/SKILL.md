---
name: music-sort
description: "A music file organizer"
---

Music-file organizer. CLI tools only. Scripts in `~/.claude/skills/music-sort/`:
- `scan.py <folder>` → JSON array: `path, size, artist, album_artist, album, title, track, year`
- `parse_filename.py "<stem>"` → `{artist, title, track, confidence}`
- `apply.py <plan.json> <folder> [--dry-run] [--to-mp3]` → executes plan, strips tags, deletes plan file

Requires ffmpeg (`brew install ffmpeg`).

## Step 1: Folder + flags
Use path from user message or ask with `AskUserQuestion`. Check for `--dry-run` and `--to-mp3`.

## Step 2: Scan
```bash
python3 ~/.claude/skills/music-sort/scan.py <folder>
```

## Step 3: Fill gaps
For entries missing `artist` or `title`, batch-parse filename stems:
```bash
for f in "074. Billy Idol - Mony Mony" "Unknown - track01"; do
  echo "$f"; python3 ~/.claude/skills/music-sort/parse_filename.py "$f"
done
```
`confidence: low` → flag row with `?`.

## Step 4: Build plan (no tool calls)
Target: `{folder}/{Artist}/{Artist} - {Title}.ext`  
Unknown artist: `{folder}/Unknown Artist/Unknown Artist - {Title}.ext`

- No track numbers; album ignored for structure
- `--to-mp3`: always use `.mp3` extension
- Sanitize: strip `/ : * ? " < > |`, collapse spaces
- Duplicates (same lowercase artist+title): keep largest, DELETE rest
- Conflicts (target exists): keep larger, SKIP smaller
- No-op (src == dst): mark OK, exclude from plan

## Step 5: Proposal table
```
| Original Path | New Path | Action |
```
Flag uncertain rows with `?`.

## Step 6: Confirm and execute
Ask user to confirm. `--dry-run` stops here.

Write plan JSON, then run:
```bash
python3 ~/.claude/skills/music-sort/apply.py <folder>/music_sort_plan.json <folder>
# append --to-mp3 if needed
```
apply.py handles mkdir, mv, tag-strip, artwork removal, optional conversion and deletes the plan JSON.

## Step 7: Summary
Print apply.py summary line + uncertain-row count + conversion count if `--to-mp3`.

## Step 8: CLAUDE.md
Write/update `CLAUDE.md` in the folder: date, folder tree, naming conventions, flagged files.
