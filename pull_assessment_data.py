import csv
import sys
import time
import urllib.parse
import urllib.request
import json

RESOURCE_ID = "65855e14-549e-4992-b5be-d629afc676fa"
API_BASE = "https://data.wprdc.org/api/3/action/datastore_search"


def fetch_all(zip_list):
    offset = 0
    limit = 1000
    all_records = []
    while True:
        filters = json.dumps({"PROPERTYZIP": zip_list, "CLASS": "R"})
        params = {
            "resource_id": RESOURCE_ID,
            "filters": filters,
            "limit": limit,
            "offset": offset,
        }
        url = API_BASE + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        if not data.get("success"):
            raise RuntimeError("API returned an error: " + str(data))
        records = data["result"]["records"]
        all_records.extend(records)
        print(f"fetched {len(all_records)} records so far...")
        if len(records) < limit:
            break
        offset += limit
        time.sleep(0.5)
    return all_records


def main():
    if len(sys.argv) < 2:
        print("usage: python pull_assessment_data.py 15217,15218 [output.csv]")
        sys.exit(1)
    zip_list = [z.strip() for z in sys.argv[1].split(",") if z.strip()]
    out_path = sys.argv[2] if len(sys.argv) > 2 else "assessment_sales.csv"

    records = fetch_all(zip_list)
    if not records:
        print("no records found")
        return

    fields = [
        "PARID", "PROPERTYHOUSENUM", "PROPERTYADDRESS", "PROPERTYCITY",
        "PROPERTYZIP", "MUNIDESC", "SCHOOLDESC", "SALEDATE", "SALEPRICE",
        "PREVSALEDATE", "PREVSALEPRICE", "COUNTYTOTAL", "FAIRMARKETTOTAL",
        "HOMESTEADFLAG",
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for r in records:
            writer.writerow(r)

    print(f"wrote {len(records)} records to {out_path}")


if __name__ == "__main__":
    main()
