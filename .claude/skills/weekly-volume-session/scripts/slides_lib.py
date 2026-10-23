"""Google Slides / Sheets / Drive plumbing for the weekly volume session deck.

Text edits never touch shapes, sizes, colors or fonts. Replacing text works like this:
insert the new text at index 0, so it picks up the style of the first existing
character, then delete the old text after it. Each box or cell keeps its own
formatting instead of falling back to defaults.

Auth: the repo .env OAuth creds (GOOGLE_CLIENT_ID / _SECRET / _REFRESH_TOKEN). Their
`drive` scope covers Sheets, and the Slides API is enabled on project 1005567143564.
"""
import json
import os
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
STYLE_FIELDS = "fontSize,fontFamily,foregroundColor,bold,italic"


def _env():
    d = HERE
    while d != "/" and not os.path.exists(os.path.join(d, ".env")):
        d = os.path.dirname(d)
    path = os.environ.get("NEAR_ENV", os.path.join(d, ".env"))
    env = {}
    for line in open(path):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def token():
    e = _env()
    data = urllib.parse.urlencode({
        "client_id": e["GOOGLE_CLIENT_ID"], "client_secret": e["GOOGLE_CLIENT_SECRET"],
        "refresh_token": e["GOOGLE_REFRESH_TOKEN"], "grant_type": "refresh_token"}).encode()
    return json.load(urllib.request.urlopen("https://oauth2.googleapis.com/token", data))["access_token"]


def api(tok, method, url, body=None):
    req = urllib.request.Request(url, method=method, headers={
        "Authorization": "Bearer " + tok, "Content-Type": "application/json"},
        data=json.dumps(body).encode() if body is not None else None)
    try:
        return json.load(urllib.request.urlopen(req))
    except urllib.error.HTTPError as err:
        raise RuntimeError(f"{method} {url} -> {err.code}: {err.read().decode()[:800]}")


# ---- Sheets ---------------------------------------------------------------

def sheet_values(tok, sid, rng):
    u = f"https://sheets.googleapis.com/v4/spreadsheets/{sid}/values/{urllib.parse.quote(rng)}"
    return api(tok, "GET", u).get("values", [])


# ---- Slides ---------------------------------------------------------------

def get_presentation(tok, pid):
    return api(tok, "GET", f"https://slides.googleapis.com/v1/presentations/{pid}")


def batch(tok, pid, requests):
    """One atomic batchUpdate: if any request is invalid, nothing is applied."""
    if not requests:
        return {}
    return api(tok, "POST", f"https://slides.googleapis.com/v1/presentations/{pid}:batchUpdate",
               {"requests": requests})


def thumbnail(tok, pid, slide_id, out_path):
    t = api(tok, "GET", f"https://slides.googleapis.com/v1/presentations/{pid}/pages/{slide_id}"
                        "/thumbnail?thumbnailProperties.thumbnailSize=LARGE")
    open(out_path, "wb").write(urllib.request.urlopen(t["contentUrl"]).read())


def text_of(text_obj):
    return "".join(r.get("textRun", {}).get("content", "") for r in (text_obj or {}).get("textElements", []))


def index(pres):
    """objectId -> element, for every element on every slide (groups flattened)."""
    out = {}
    def walk(els):
        for e in els:
            out[e["objectId"]] = e
            if "elementGroup" in e:
                walk(e["elementGroup"]["children"])
    for s in pres["slides"]:
        walk(s.get("pageElements", []))
    return out


def shape_text(el):
    return text_of(el["shape"].get("text")).rstrip("\n")


def _cell(el, r, c):
    return el["table"]["tableRows"][r]["tableCells"][c]


def cell_text(el, r, c):
    return text_of(_cell(el, r, c).get("text")).rstrip("\n")


def _replace(old, new, base):
    """Requests that turn `old` into `new`. `base` = objectId (+ cellLocation)."""
    reqs = []
    if new:
        reqs.append({"insertText": {**base, "insertionIndex": 0, "text": new}})
    if old:  # the final paragraph mark can't be deleted, so `old` excludes it
        start = len(new)
        reqs.append({"deleteText": {**base, "textRange": {
            "type": "FIXED_RANGE", "startIndex": start, "endIndex": start + len(old)}}})
    return reqs


def set_shape(el, new):
    old = shape_text(el)
    return [] if old == new else _replace(old, new, {"objectId": el["objectId"]})


def clear_shape(el):
    return set_shape(el, "")


def run_style(el, r, c):
    """Style of the first text run in a cell (or None if the cell is empty)."""
    for x in _cell(el, r, c).get("text", {}).get("textElements", []):
        if "textRun" in x and x["textRun"]["content"].strip():
            return x["textRun"].get("style", {})
    return None


def set_cell(el, r, c, new, style_from=None):
    """Replace a cell's text. `style_from=(r, c)` names a sibling cell whose font
    (size, family, color, bold, italic) the written text should match. Use it for
    data cells, so a cell that was empty or drifted gets the same style as its neighbors."""
    base = {"objectId": el["objectId"], "cellLocation": {"rowIndex": r, "columnIndex": c}}
    reqs = _replace(cell_text(el, r, c), new, base)
    if new and style_from:
        st = run_style(el, *style_from)
        if st:
            reqs.append({"updateTextStyle": {**base, "textRange": {"type": "ALL"},
                         "style": {k: st[k] for k in STYLE_FIELDS.split(",") if k in st},
                         "fields": STYLE_FIELDS}})
    return reqs
