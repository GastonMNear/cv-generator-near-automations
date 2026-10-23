#!/usr/bin/env python3
"""Render slides to PNG so the agent can check visually that nothing shifted.

    python3 thumbnails.py --deck <id> [--slides 3,4,9] --out-dir <scratch dir>
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slides_lib import get_presentation, thumbnail, token

ap = argparse.ArgumentParser()
ap.add_argument("--deck", required=True)
ap.add_argument("--slides", help="1-based slide numbers, default all")
ap.add_argument("--out-dir", required=True)
a = ap.parse_args()
tok = token()
P = get_presentation(tok, a.deck)
os.makedirs(a.out_dir, exist_ok=True)
for n in ([int(x) for x in a.slides.split(",")] if a.slides else range(1, len(P["slides"]) + 1)):
    path = os.path.join(a.out_dir, f"slide{n:02d}.png")
    thumbnail(tok, a.deck, P["slides"][n - 1]["objectId"], path)
    print(path)
