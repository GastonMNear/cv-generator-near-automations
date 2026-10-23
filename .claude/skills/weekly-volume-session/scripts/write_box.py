#!/usr/bin/env python3
"""Write narrative text (a headline, an issue) into an existing, EMPTY text box with
the deck's own style. An emptied box falls back to its leftover paragraph style (23pt
on the issues box), so the style has to be copied from a reference run.

    python3 write_box.py --deck <id> --object <objectId> --text-file t.txt \
        --style-from <objectId> [--style-deck <id>] [--title-style-from <objectId>] \
        [--bold-labels] [--apply]

--style-from        box whose first text run gives the body style (e.g. a headline
                    Gaston already wrote, or the same box in last week's deck via
                    --style-deck)
--title-style-from  if set, line 1 gets the style of the first run of that box, and
                    the body style comes from its second run (the issues box layout:
                    bold title, plain lines)
--bold-labels       bold the "Label:" prefix of each body line (Today:, Proposal: …)

It refuses to write into a box that already has text: Gaston may have typed there.
Dry run by default.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from slides_lib import STYLE_FIELDS, batch, get_presentation, index, shape_text, token


def runs(el):
    return [x["textRun"]["style"] for x in el["shape"].get("text", {}).get("textElements", [])
            if "textRun" in x and x["textRun"]["content"].strip()]


def pick(st):
    return {k: st[k] for k in STYLE_FIELDS.split(",") if k in st}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deck", required=True)
    ap.add_argument("--object", required=True)
    ap.add_argument("--text-file", required=True)
    ap.add_argument("--style-from", required=True)
    ap.add_argument("--style-deck")
    ap.add_argument("--title-style-from", action="store_true")
    ap.add_argument("--bold-labels", action="store_true")
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    text = open(a.text_file).read().rstrip("\n")
    tok = token()
    E = index(get_presentation(tok, a.deck))
    SE = index(get_presentation(tok, a.style_deck)) if a.style_deck else E
    el = E[a.object]
    if shape_text(el):
        sys.exit(f"{a.object} already has text: {shape_text(el)[:80]!r}. Not overwriting.")
    ref = runs(SE[a.style_from])
    if not ref:
        sys.exit(f"{a.style_from} has no text to copy a style from")
    oid = a.object
    R = [{"insertText": {"objectId": oid, "insertionIndex": 0, "text": text}}]
    body_st = ref[1] if a.title_style_from and len(ref) > 1 else ref[0]
    R.append({"updateTextStyle": {"objectId": oid, "textRange": {"type": "ALL"},
                                  "style": pick(body_st), "fields": STYLE_FIELDS}})
    lines = text.split("\n")
    i = 0
    if a.title_style_from:
        R.append({"updateTextStyle": {"objectId": oid, "textRange": {
            "type": "FIXED_RANGE", "startIndex": 0, "endIndex": len(lines[0])},
            "style": pick(ref[0]), "fields": STYLE_FIELDS}})
        i = len(lines[0]) + 1
        lines = lines[1:]
    if a.bold_labels:
        for line in lines:
            if ":" in line[:40]:
                n = line.index(":") + 1
                R.append({"updateTextStyle": {"objectId": oid, "textRange": {
                    "type": "FIXED_RANGE", "startIndex": i, "endIndex": i + n},
                    "style": {"bold": True}, "fields": "bold"}})
            i += len(line) + 1
    print(text)
    if not a.apply:
        print("\nDry run, nothing written. Re-run with --apply.")
        return
    batch(tok, a.deck, R)
    print("\nApplied.")


if __name__ == "__main__":
    main()
