"""Turn a cb.dump() output (saved to a file by the harness) into real files.

  python3 save_dump.py <harness file> <out.json>                 # whole object → one JSON file
  python3 save_dump.py <harness file> <dir> --backups             # cb.backup() list → one file per field:
                                                                  #   <dir>/<tableId>__<fieldId>.json
Backups live next to the build log in `Near Work Partner/logs/backups/<log name>/`; the log links them.
"""
import json, os, sys
from sl import read_dump

src, out = sys.argv[1], sys.argv[2]
obj = json.loads(read_dump(src))
if "--backups" in sys.argv:
    os.makedirs(out, exist_ok=True)
    for b in obj:
        p = os.path.join(out, f"{b['tableId']}__{b['fieldId']}.json")
        json.dump(b, open(p, "w"), indent=1, ensure_ascii=False)
        print(p, b["name"], b.get("configRevision"))
else:
    json.dump(obj, open(out, "w"), indent=1, ensure_ascii=False)
    print(out)
