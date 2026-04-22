#!/usr/bin/env python3
"""
Usage: python3 parse_filename.py <filename_without_extension>

Parses a music filename into artist/title/track metadata and reports confidence.
Outputs JSON: {"artist": "...", "title": "...", "track": "...", "confidence": "high|medium|low"}

Patterns handled (in order of precedence):
  1. [Source] Artist - Song         strip bracketed prefix, then high-confidence split
  2. 074. Artist - Song             track number prefix, then high-confidence split
  3. 03 - Song                      leading digits only → track + title, unknown artist
  4. Artist - Song                  standard high-confidence split
  5. Artist_Song                    underscores → low confidence
  6. ArtistSong (fallback)          whole name as title, unknown artist
"""

import json
import re
import sys


def parse(raw):
    name = raw.strip()
    track = ''
    artist = ''
    title = ''
    confidence = 'low'

    # Strip bracketed/parenthesised source prefix: [NME] or (NME)
    name = re.sub(r'^[\[\(][^\]\)]+[\]\)]\s*', '', name)

    # Pattern 1+2: optional track prefix "074." or "074 -" or "74 -" before artist
    m = re.match(r'^(\d+)[.\s-]+\s*(.+)$', name)
    if m:
        candidate_track = m.group(1).lstrip('0') or '0'
        rest = m.group(2).strip()
        # If rest still contains " - ", it's "Artist - Song" with a track prefix
        parts = re.split(r'\s+-\s+', rest, maxsplit=1)
        if len(parts) == 2:
            artist, title, track, confidence = parts[0].strip(), parts[1].strip(), candidate_track, 'high'
        else:
            # Pattern 3: only a track number and title, no artist
            title, track, confidence = rest, candidate_track, 'medium'
    else:
        # Pattern 4: plain "Artist - Song"
        parts = re.split(r'\s+-\s+', name, maxsplit=1)
        if len(parts) == 2:
            artist, title, confidence = parts[0].strip(), parts[1].strip(), 'high'
        # Pattern 5: underscores as separators
        elif '_' in name:
            parts = name.split('_', 1)
            artist, title, confidence = parts[0].strip(), parts[1].replace('_', ' ').strip(), 'low'
        else:
            # Pattern 6: give up, use whole name as title
            title, confidence = name, 'low'

    return {'artist': artist, 'title': title, 'track': track, 'confidence': confidence}


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: parse_filename.py <filename_without_extension>', file=sys.stderr)
        sys.exit(1)
    print(json.dumps(parse(' '.join(sys.argv[1:]))))
