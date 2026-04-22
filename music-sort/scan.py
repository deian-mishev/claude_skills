#!/usr/bin/env python3
"""
Usage: python3 scan.py <folder>

Recursively finds all music files under <folder>, reads metadata via ffprobe,
and prints a single JSON array to stdout. Falls back to empty tags if ffprobe
fails or is unavailable for a file.
"""

import json
import os
import shutil
import subprocess
import sys

MUSIC_EXTS = {'.mp3', '.flac', '.wav', '.aac', '.ogg', '.m4a', '.wma', '.aiff'}


def ffprobe_tags(path):
    try:
        raw = subprocess.check_output(
            ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', path],
            stderr=subprocess.DEVNULL,
        )
        tags = {k.lower(): v for k, v in json.loads(raw).get('format', {}).get('tags', {}).items()}
        return tags
    except Exception:
        return {}


def scan(folder):
    results = []
    for root, _dirs, files in os.walk(folder):
        for name in sorted(files):
            ext = os.path.splitext(name)[1].lower()
            if ext not in MUSIC_EXTS:
                continue
            path = os.path.join(root, name)
            tags = ffprobe_tags(path)
            track = tags.get('track', '').split('/')[0].lstrip('0') or ''
            results.append({
                'path':         path,
                'size':         os.path.getsize(path),
                'artist':       tags.get('artist') or tags.get('album_artist') or '',
                'album_artist': tags.get('album_artist') or '',
                'album':        tags.get('album') or '',
                'title':        tags.get('title') or '',
                'track':        track,
                'year':         tags.get('date') or tags.get('year') or '',
            })
    return results


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: scan.py <folder>', file=sys.stderr)
        sys.exit(1)

    if not shutil.which('ffprobe'):
        print('Warning: ffprobe not found. Install with: brew install ffmpeg', file=sys.stderr)
        print('Falling back to filename-only metadata.', file=sys.stderr)

    folder = os.path.expanduser(sys.argv[1])
    print(json.dumps(scan(folder), indent=2))
