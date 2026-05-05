import urllib.request
import json
import numpy as np
from itertools import groupby
from pprint import pprint

# ── Configuration ──────────────────────────────────────────────────────────────
TOKEN      = "MUST REPLACE WITH YOUR TOKEN HERE"
PROJECT    = "Refactoring_LLM_Benchmark"
STATUSES   = "OPEN"
HOST       = "http://localhost:9000"
OUTPUT     = "sonar-report.json"
PAGE_SIZE  = 500
# ───────────────────────────────────────────────────────────────────────────────

def fetch_issues():
    page       = 1
    all_issues = []

    while True:
        url = f"{HOST}/api/issues/search?projectKeys={PROJECT}&ps={PAGE_SIZE}&p={page}&statuses={STATUSES}"
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {TOKEN}")

        try:
            with urllib.request.urlopen(req) as r:
                data = json.loads(r.read())
        except urllib.error.HTTPError as e:
            print("Status:", e.code)
            print("Body:", e.read().decode())
            raise



        issues = data["issues"]
        all_issues.extend(issues)
        print(f"Page {page}: {len(issues)} issues fetched (total so far: {len(all_issues)})")

        if page * PAGE_SIZE >= data["total"]:
            break
        page += 1

    return all_issues


def save_issues(issues):
    with open(OUTPUT, "w") as f:
        json.dump(issues, f, indent=2)
    print(f"\n✅ Done! {len(issues)} issues exported to '{OUTPUT}'")


def statistics_calculation():
    data = [(0, 0, 7, 1, 0), (0, 3, 13, 5, 0), (0, 1, 9, 2, 0), (0, 0, 11, 2, 0), (0, 1, 14, 3, 0)]
    arr = np.array(data)
    means = arr.mean(axis=0)
    stds  = arr.std(axis=0)

    for i, (m, s) in enumerate(zip(means, stds)):
        print(f"Col {i}: mean = {m:.2f}, std = {s:.2f}")


if __name__ == "__main__":
    print(f"🔍 Fetching issues for project: {PROJECT}")
    #issues = fetch_issues()
    #save_issues(issues)
    #statistics_calculation()