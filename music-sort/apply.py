#!/usr/bin/env python3
"""
Usage: python3 apply.py <plan.json> <root_folder> [--dry-run] [--to-mp3]

Applies a music sort plan, strips all metadata tags and embedded artwork
from every output file via ffmpeg, optionally converts non-MP3 files to MP3
in the same ffmpeg pass.

Requires ffmpeg: brew install ffmpeg

Plan format — a JSON array of objects, each with an "action" field:
  {"action": "MOVE",   "src": "/abs/src.mp3", "dst": "/abs/dst.mp3"}
  {"action": "DELETE", "src": "/abs/dup.mp3"}
  {"action": "SKIP",   "src": "/abs/file.mp3", "reason": "..."}

Exits non-zero if any errors occurred. Prints a summary to stdout.
"""

import json
import os
import shutil
import subprocess
import sys


def check_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print('ERROR: ffmpeg not found. Install with: brew install ffmpeg', file=sys.stderr)
        sys.exit(1)


def strip_tags(path):
    """Re-mux the file in place using ffmpeg, dropping all metadata and embedded artwork."""
    base, ext = os.path.splitext(path)
    tmp = base + '.notags' + ext  # keep extension so ffmpeg auto-detects format
    try:
        result = subprocess.run(
            ['ffmpeg', '-i', path, '-map', '0:a', '-map_metadata', '-1',
             '-map_chapters', '-1', '-c:a', 'copy', tmp, '-y', '-loglevel', 'error'],
            capture_output=True,
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.decode().strip())
        os.replace(tmp, path)
    except Exception as e:
        print(f'WARNING: could not strip tags from {path}: {e}', file=sys.stderr)
        if os.path.exists(tmp):
            os.remove(tmp)


def main():
    if len(sys.argv) < 2:
        print('Usage: apply.py <plan.json> <root_folder> [--dry-run] [--to-mp3]', file=sys.stderr)
        sys.exit(1)

    plan_path   = sys.argv[1]
    dry_run     = '--dry-run' in sys.argv
    to_mp3      = '--to-mp3' in sys.argv

    check_ffmpeg()

    with open(plan_path) as f:
        plan = json.load(f)

    moves   = [p for p in plan if p['action'] == 'MOVE']
    deletes = [p for p in plan if p['action'] == 'DELETE']
    skips   = [p for p in plan if p['action'] == 'SKIP']

    if dry_run:
        print(f'[dry-run] Would move {len(moves)} file(s), delete {len(deletes)}, skip {len(skips)}.')
        print(f'[dry-run] Tags would be stripped from all output files.')
        if to_mp3:
            non_mp3 = sum(1 for m in moves if os.path.splitext(m['src'])[1].lower() != '.mp3')
            print(f'[dry-run] {non_mp3} file(s) would be converted to MP3.')
        return

    moved = deleted = errors = converted = 0

    for entry in moves:
        src, dst = entry['src'], entry['dst']
        try:
            if to_mp3:
                dst = os.path.splitext(dst)[0] + '.mp3'

            dst_dir = os.path.dirname(dst)
            os.makedirs(dst_dir, exist_ok=True)

            src_ext = os.path.splitext(src)[1].lower()
            if to_mp3 and src_ext != '.mp3':
                # Convert + strip tags in one ffmpeg pass
                result = subprocess.run(
                    ['ffmpeg', '-i', src, '-map', '0:a', '-map_metadata', '-1',
                     '-map_chapters', '-1', '-q:a', '0', dst, '-y', '-loglevel', 'error'],
                    capture_output=True,
                )
                if result.returncode != 0:
                    raise RuntimeError(result.stderr.decode().strip())
                os.remove(src)
                converted += 1
            else:
                shutil.move(src, dst)
                strip_tags(dst)

            moved += 1
        except Exception as e:
            print(f'ERROR processing {src} → {dst}: {e}', file=sys.stderr)
            errors += 1

    for entry in deletes:
        src = entry['src']
        try:
            os.remove(src)
            deleted += 1
        except Exception as e:
            print(f'ERROR deleting {src}: {e}', file=sys.stderr)
            errors += 1

    try:
        os.remove(plan_path)
    except OSError:
        pass

    extras = f', Converted to MP3: {converted}' if converted else ''
    print(f'Done. Moved: {moved}, Deleted: {deleted}, Skipped: {len(skips)}, Errors: {errors}{extras}')
    if moved:
        print('Tags stripped from all output files.' if not errors else 'Tags stripped from successfully processed files.')

    if errors:
        sys.exit(1)


if __name__ == '__main__':
    main()
