#!/usr/bin/env python3
"""Turn a readout spec into one Google Doc per experiment.

    python3 build_docs.py <spec.json> --html-dir <scratch>/html          # preview only
    python3 build_docs.py <spec.json> --html-dir <scratch>/html --upload # + Drive

Each doc is written as HTML (chart = base64 PNG drawn with Pillow) and uploaded with Drive
multipart + Doc conversion, which keeps tables and images. Docs land in "My Drive /
Experiment Readouts <date>" (created if missing). A doc with "doc_id" in the spec is
overwritten in place instead (same link). Spec shape: see SKILL.md.
"""
import argparse
import base64
import html
import io
import json
import os
import sys
import urllib.parse
import urllib.request

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "weekly-volume-session", "scripts"))
from slides_lib import api, token  # noqa: E402

DOC_MIME = "application/vnd.google-apps.document"
FOLDER_MIME = "application/vnd.google-apps.folder"


def font(size, bold=False):
    for p in (["/System/Library/Fonts/Supplemental/Arial Bold.ttf"] if bold else []) + [
            "/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial.ttf"]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default(size=size)


def chart_png(c):
    """Horizontal bars + optional dashed benchmark line. c = {title, unit, bars:[{label,value}], reference:{label,value}}"""
    bars, ref, unit = c["bars"], c.get("reference"), c.get("unit", "%")
    W, row, left, top = 1200, 70, 300, 90
    H = top + row * len(bars) + 60
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)
    d.text((30, 25), c["title"], fill="#1f2937", font=font(30, True))
    vmax = max([b["value"] for b in bars] + [ref["value"] if ref else 0]) * 1.25 or 1
    span = W - left - 140
    for i, b in enumerate(bars):
        y = top + i * row
        d.text((30, y + 18), b["label"], fill="#374151", font=font(24))
        w = int(span * b["value"] / vmax)
        d.rectangle([left, y + 12, left + max(w, 2), y + row - 14], fill="#2563eb")
        d.text((left + w + 12, y + 18), f"{b['value']:g}{unit}", fill="#111827", font=font(24, True))
    if ref:
        x = left + int(span * ref["value"] / vmax)
        for y in range(top, H - 50, 14):
            d.line([x, y, x, y + 7], fill="#dc2626", width=3)
        d.text((x - 60, H - 45), f"{ref['label']} {ref['value']:g}{unit}", fill="#dc2626", font=font(22))
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode()


def e(s):
    return html.escape(str(s))


def table_html(t):
    th = "".join(f'<th style="background:#1f2937;color:#fff;padding:6px;text-align:left">{e(c)}</th>'
                 for c in t["columns"])
    rows = []
    for i, r in enumerate(t["rows"]):
        b = "font-weight:bold;" if i in t.get("bold_rows", []) else ""
        rows.append("<tr>" + "".join(f'<td style="{b}border:1px solid #d1d5db;padding:6px">{e(c)}</td>'
                                     for c in r) + "</tr>")
    return f'<table style="border-collapse:collapse;width:100%"><tr>{th}</tr>{"".join(rows)}</table>'


def doc_html(doc, date_label):
    p = [f'<p style="color:#6b7280;font-size:10pt">Near Outbound | {e(doc["id"])}</p>',
         f'<h1 style="font-size:18pt">{e(doc.get("kind", "WEEKLY READOUT"))} | {e(doc["subtitle"])}</h1>',
         f'<p style="color:#6b7280">Reporting date: {e(date_label)} · Data: cumulative since launch</p>',
         '<h2>TLDR</h2>',
         f'<p><b>DECISION: {e(doc["decision"].upper())}</b></p>',
         f'<p>{e(doc["tldr"])}</p>']
    for s in doc["sections"]:
        p.append(f'<h2>{e(s["heading"])}</h2>')
        if s.get("table"):
            p.append(table_html(s["table"]))
        if s.get("chart"):
            p.append(f'<p><img width="560" src="data:image/png;base64,{chart_png(s["chart"])}"></p>')
        p += [f"<p>{e(x)}</p>" for x in s.get("paragraphs", [])]
        if s.get("bullets"):
            p.append("<ul>" + "".join(f"<li>{e(x)}</li>" for x in s["bullets"]) + "</ul>")
    p.append("<h2>Sources</h2><ul>" + "".join(f"<li>{e(x)}</li>" for x in doc["sources"]) + "</ul>")
    return '<html><body style="font-family:Arial">' + "\n".join(p) + "</body></html>"


def folder_id(tok, name):
    q = urllib.parse.quote(f"name = '{name}' and mimeType = '{FOLDER_MIME}' and 'root' in parents and trashed = false")
    found = api(tok, "GET", f"https://www.googleapis.com/drive/v3/files?q={q}&fields=files(id)")["files"]
    if found:
        return found[0]["id"]
    return api(tok, "POST", "https://www.googleapis.com/drive/v3/files",
               {"name": name, "mimeType": FOLDER_MIME})["id"]


def upload(tok, name, parent, body):
    boundary = "readoutboundary"
    meta = json.dumps({"name": name, "mimeType": DOC_MIME, "parents": [parent]})
    data = (f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n{meta}\r\n"
            f"--{boundary}\r\nContent-Type: text/html; charset=UTF-8\r\n\r\n{body}\r\n--{boundary}--").encode()
    req = urllib.request.Request(
        "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id",
        data=data, method="POST", headers={"Authorization": "Bearer " + tok,
                                           "Content-Type": f"multipart/related; boundary={boundary}"})
    return json.load(urllib.request.urlopen(req))["id"]


def replace(tok, doc_id, body):
    """Overwrite an existing Doc's content with new HTML; the id and link stay the same."""
    req = urllib.request.Request(
        f"https://www.googleapis.com/upload/drive/v3/files/{doc_id}?uploadType=media&fields=id",
        data=body.encode(), method="PATCH",
        headers={"Authorization": "Bearer " + tok, "Content-Type": "text/html; charset=UTF-8"})
    return json.load(urllib.request.urlopen(req))["id"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--html-dir", required=True)
    ap.add_argument("--upload", action="store_true")
    a = ap.parse_args()
    spec = json.load(open(a.spec))
    os.makedirs(a.html_dir, exist_ok=True)
    tok = token() if a.upload else None
    new_docs = a.upload and any(not d.get("doc_id") for d in spec["docs"])
    parent = folder_id(tok, f"Experiment Readouts {spec['date']}") if new_docs else None
    for doc in spec["docs"]:
        body = doc_html(doc, spec["date_label"])
        path = os.path.join(a.html_dir, f"{doc['id']}.html")
        open(path, "w").write(body)
        if a.upload and doc.get("doc_id"):
            did = replace(tok, doc["doc_id"], body)
            print(f"{doc['id']} (updated): https://docs.google.com/document/d/{did}/edit")
        elif a.upload:
            did = upload(tok, f"{doc['id']}_Weekly_Readout_{spec['date']}", parent, body)
            print(f"{doc['id']}: https://docs.google.com/document/d/{did}/edit")
        else:
            print(f"{doc['id']}: {path}")
    if parent:
        print(f"folder: https://drive.google.com/drive/folders/{parent}")


if __name__ == "__main__":
    main()
