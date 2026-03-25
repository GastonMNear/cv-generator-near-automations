import urllib.request
import json
import ssl

SESSION = "claysession=s%3AN0IwvD7t5LSWoQW6Wjc3vuCfFbjNsXDJ.ectFpxgbhtIRsqk%2B6kwaVh3VqaPiZG47pQg35bx%2BUzI"
TABLE_ID = "t_0t6ghvgCsvvvqAus4bp"
RECORD_ID = "r_0tav17yJvyEFDbBaSw2"
EMPLOYEE_COUNT_FIELD_ID = "f_0t062fr5fKsUy27nJhf"
BASE = "https://api.clay.com/v3"

ctx = ssl.create_default_context()

def api_post(path, data):
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(data).encode(),
        headers={"Cookie": SESSION, "Content-Type": "application/json"},
        method="POST"
    )
    resp = urllib.request.urlopen(req, context=ctx)
    return json.loads(resp.read().decode('utf-8'))

# Fetch the specific record
resp = api_post(f"/tables/{TABLE_ID}/bulk-fetch-records", {"recordIds": [RECORD_ID]})
record = resp["results"][0]
cells = record.get("cells", {})

# Extract employee count
employee_cell = cells.get(EMPLOYEE_COUNT_FIELD_ID, {})
employee_count = employee_cell.get("value") if isinstance(employee_cell, dict) else None

print(f"Company: Zamora Live")
print(f"Employee Count: {employee_count}")
