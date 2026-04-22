#!/usr/bin/env python3
"""
Usage: python3 scan.py <folder>

Recursively finds all music files under <folder>, reads metadata via mutagen
(auto-installed on first run), and prints a single JSON array to stdout.
Falls back to empty tags if a file's tags cannot be read.
"""

import json
import os
import sys

try:
    from mutagen import File as MutagenFile
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'mutagen', '-q'])
    from mutagen import File as MutagenFile

MUSIC_EXTS = {'.mp3', '.flac', '.wav', '.aac', '.ogg', '.m4a', '.wma', '.aiff'}


def read_tags(path):
    try:
        audio = MutagenFile(path, easy=True)
        if not audio or not audio.tags:
            return {}
        # mutagen easy=True normalises keys to lowercase across all formats
        return {k: str(v[0]) if isinstance(v, list) else str(v) for k, v in audio.tags.items()}
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
            tags = read_tags(path)
            track = tags.get('tracknumber', '').split('/')[0].lstrip('0') or ''
            results.append({
                'path':         path,
                'size':         os.path.getsize(path),
                'artist':       tags.get('artist') or tags.get('albumartist') or '',
                'album_artist': tags.get('albumartist') or '',
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

    folder = os.path.expanduser(sys.argv[1])
    print(json.dumps(scan(folder), indent=2))
